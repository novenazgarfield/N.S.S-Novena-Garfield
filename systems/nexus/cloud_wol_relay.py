#!/usr/bin/env python3
"""
NEXUS云端WOL中转服务
用于实现广域网远程唤醒功能

部署在云服务器上，接收远程唤醒请求并转发到目标网络
支持多网络、多设备管理

作者: NEXUS Team
版本: 1.0.0
"""

import asyncio
import json
import logging
import socket
import struct
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

import websockets
from websockets.server import WebSocketServerProtocol
from wakeonlan import send_magic_packet

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class NetworkConfig:
    """网络配置"""
    name: str
    broadcast_ip: str
    description: str
    auth_token: str  # 认证令牌
    allowed_macs: List[str]  # 允许的MAC地址列表

@dataclass
class WakeRequest:
    """唤醒请求"""
    network_name: str
    mac_address: str
    auth_token: str
    client_ip: str
    timestamp: datetime

class CloudWOLRelay:
    """云端WOL中转服务"""
    
    def __init__(self, config_file: str = "wol_networks.json"):
        self.config_file = config_file
        self.networks: Dict[str, NetworkConfig] = {}
        self.wake_history: List[WakeRequest] = []
        self.clients: set = set()
        
        # 加载网络配置
        self.load_networks()
        
    def load_networks(self):
        """加载网络配置"""
        config_path = Path(self.config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                for net_data in config_data.get('networks', []):
                    network = NetworkConfig(
                        name=net_data['name'],
                        broadcast_ip=net_data['broadcast_ip'],
                        description=net_data['description'],
                        auth_token=net_data['auth_token'],
                        allowed_macs=net_data.get('allowed_macs', [])
                    )
                    self.networks[network.name] = network
                    
                logger.info(f"✅ 加载了 {len(self.networks)} 个网络配置")
                
            except Exception as e:
                logger.error(f"❌ 加载网络配置失败: {e}")
        else:
            # 创建示例配置
            self.create_example_config()
    
    def create_example_config(self):
        """创建示例配置文件"""
        example_config = {
            "networks": [
                {
                    "name": "home_network",
                    "broadcast_ip": "192.168.1.255",
                    "description": "家庭网络",
                    "auth_token": "your_home_token_here",
                    "allowed_macs": [
                        "00:1B:21:3A:4C:5D",
                        "AA:BB:CC:DD:EE:FF"
                    ]
                },
                {
                    "name": "office_network", 
                    "broadcast_ip": "10.0.0.255",
                    "description": "办公室网络",
                    "auth_token": "your_office_token_here",
                    "allowed_macs": [
                        "11:22:33:44:55:66"
                    ]
                }
            ]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, indent=2, ensure_ascii=False)
            
        logger.info(f"📝 创建了示例配置文件: {self.config_file}")
        logger.info("⚠️  请编辑配置文件并设置正确的网络信息和认证令牌")

    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """处理客户端连接"""
        client_ip = websocket.remote_address[0]
        logger.info(f"🔗 新客户端连接: {client_ip}")
        
        self.clients.add(websocket)
        
        try:
            # 发送欢迎消息
            welcome_msg = {
                "type": "welcome",
                "message": "欢迎连接到NEXUS云端WOL中转服务",
                "networks": list(self.networks.keys()),
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(welcome_msg))
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, data, client_ip)
                except json.JSONDecodeError:
                    await self.send_error(websocket, "无效的JSON格式")
                except Exception as e:
                    logger.error(f"处理消息失败: {e}")
                    await self.send_error(websocket, f"处理失败: {str(e)}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 客户端断开连接: {client_ip}")
        finally:
            self.clients.discard(websocket)

    async def handle_message(self, websocket: WebSocketServerProtocol, data: dict, client_ip: str):
        """处理客户端消息"""
        msg_type = data.get('type')
        
        if msg_type == 'wake_request':
            await self.handle_wake_request(websocket, data, client_ip)
        elif msg_type == 'list_networks':
            await self.handle_list_networks(websocket)
        elif msg_type == 'wake_history':
            await self.handle_wake_history(websocket)
        else:
            await self.send_error(websocket, f"未知的消息类型: {msg_type}")

    async def handle_wake_request(self, websocket: WebSocketServerProtocol, data: dict, client_ip: str):
        """处理唤醒请求"""
        try:
            network_name = data.get('network_name')
            mac_address = data.get('mac_address')
            auth_token = data.get('auth_token')
            
            # 验证参数
            if not all([network_name, mac_address, auth_token]):
                await self.send_error(websocket, "缺少必要参数")
                return
                
            # 验证网络配置
            if network_name not in self.networks:
                await self.send_error(websocket, f"未知的网络: {network_name}")
                return
                
            network = self.networks[network_name]
            
            # 验证认证令牌
            if network.auth_token != auth_token:
                await self.send_error(websocket, "认证失败")
                logger.warning(f"⚠️  认证失败: {client_ip} 尝试访问 {network_name}")
                return
                
            # 验证MAC地址
            if network.allowed_macs and mac_address not in network.allowed_macs:
                await self.send_error(websocket, "MAC地址未授权")
                logger.warning(f"⚠️  未授权MAC: {mac_address} from {client_ip}")
                return
                
            # 记录唤醒请求
            wake_req = WakeRequest(
                network_name=network_name,
                mac_address=mac_address,
                auth_token=auth_token,
                client_ip=client_ip,
                timestamp=datetime.now()
            )
            self.wake_history.append(wake_req)
            
            # 发送魔术包
            logger.info(f"🌅 发送WOL包: {mac_address} -> {network.broadcast_ip}")
            send_magic_packet(mac_address, ip_address=network.broadcast_ip, port=9)
            
            # 发送成功响应
            response = {
                "type": "wake_success",
                "message": f"魔术包已发送到 {network.description}",
                "network": network_name,
                "mac_address": mac_address,
                "broadcast_ip": network.broadcast_ip,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(response))
            
            # 广播给所有客户端
            await self.broadcast_wake_notification(wake_req, network)
            
        except Exception as e:
            logger.error(f"❌ 唤醒请求处理失败: {e}")
            await self.send_error(websocket, f"唤醒失败: {str(e)}")

    async def handle_list_networks(self, websocket: WebSocketServerProtocol):
        """处理网络列表请求"""
        networks_info = []
        for name, network in self.networks.items():
            networks_info.append({
                "name": name,
                "description": network.description,
                "broadcast_ip": network.broadcast_ip,
                "allowed_devices": len(network.allowed_macs)
            })
            
        response = {
            "type": "networks_list",
            "networks": networks_info,
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send(json.dumps(response))

    async def handle_wake_history(self, websocket: WebSocketServerProtocol):
        """处理唤醒历史请求"""
        # 只返回最近100条记录
        recent_history = self.wake_history[-100:]
        
        history_data = []
        for req in recent_history:
            history_data.append({
                "network_name": req.network_name,
                "mac_address": req.mac_address,
                "client_ip": req.client_ip,
                "timestamp": req.timestamp.isoformat()
            })
            
        response = {
            "type": "wake_history",
            "history": history_data,
            "total_count": len(self.wake_history),
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send(json.dumps(response))

    async def broadcast_wake_notification(self, wake_req: WakeRequest, network: NetworkConfig):
        """广播唤醒通知"""
        notification = {
            "type": "wake_notification",
            "message": f"设备 {wake_req.mac_address} 在网络 {network.description} 中被唤醒",
            "network": wake_req.network_name,
            "mac_address": wake_req.mac_address,
            "client_ip": wake_req.client_ip,
            "timestamp": wake_req.timestamp.isoformat()
        }
        
        # 发送给所有连接的客户端
        disconnected_clients = set()
        for client in self.clients:
            try:
                await client.send(json.dumps(notification))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
                
        # 清理断开的连接
        self.clients -= disconnected_clients

    async def send_error(self, websocket: WebSocketServerProtocol, error_msg: str):
        """发送错误消息"""
        error_response = {
            "type": "error",
            "message": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send(json.dumps(error_response))

    def start_server(self, host: str = "0.0.0.0", port: int = 8766):
        """启动服务器"""
        logger.info("🚀 启动NEXUS云端WOL中转服务...")
        logger.info(f"📡 服务器地址: ws://{host}:{port}")
        logger.info(f"🌐 支持的网络: {list(self.networks.keys())}")
        
        start_server = websockets.serve(
            self.handle_client,
            host,
            port,
            ping_interval=30,
            ping_timeout=10
        )
        
        logger.info("✅ 云端WOL中转服务已启动！")
        return start_server

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='NEXUS云端WOL中转服务')
    parser.add_argument('--host', default='0.0.0.0', help='服务器地址')
    parser.add_argument('--port', type=int, default=8766, help='服务器端口')
    parser.add_argument('--config', default='wol_networks.json', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 创建中转服务
    relay = CloudWOLRelay(args.config)
    
    # 启动服务器
    start_server = relay.start_server(args.host, args.port)
    
    # 运行事件循环
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()