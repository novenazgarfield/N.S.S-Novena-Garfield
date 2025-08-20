#!/usr/bin/env python3
"""
NEXUS远程指挥中心 - WebSocket实时通信服务器
支持多设备协同、实时状态同步和命令执行监控
"""

import asyncio
import json
import logging
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import websockets
from websockets.server import WebSocketServerProtocol
import threading
import queue
import os
import signal

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NexusWebSocketServer:
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.active_tasks: Dict[str, Dict] = {}
        self.command_whitelist = {
            "genome_jigsaw": {
                "script": "./scripts/run_genome_jigsaw.sh",
                "description": "基因组拼图分析流水线"
            },
            "gromacs_simulation": {
                "script": "./scripts/run_gromacs.sh", 
                "description": "GROMACS分子动力学模拟"
            },
            "protein_folding": {
                "script": "./scripts/run_alphafold.sh",
                "description": "蛋白质折叠预测"
            },
            "system_status": {
                "script": "./scripts/get_system_status.sh",
                "description": "系统状态检查"
            },
            "wake_computer": {
                "script": "./scripts/wake_computer.sh",
                "description": "远程唤醒电脑 (Wake-on-LAN)",
                "parameters": ["mac_address", "ip_address"]
            },
            "shutdown_computer": {
                "script": "./scripts/shutdown_computer.sh",
                "description": "远程关机 (本地电脑)",
                "parameters": ["shutdown_type", "delay_seconds", "message"]
            }
        }
        
    async def register_client(self, websocket: WebSocketServerProtocol):
        """注册新的客户端连接"""
        self.clients.add(websocket)
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"🔗 新客户端连接: {client_info} (总连接数: {len(self.clients)})")
        
        # 发送欢迎消息和当前状态
        welcome_msg = {
            "type": "welcome",
            "message": "欢迎连接到NEXUS远程指挥中心！",
            "timestamp": datetime.now().isoformat(),
            "active_tasks": list(self.active_tasks.keys()),
            "available_commands": list(self.command_whitelist.keys())
        }
        await websocket.send(json.dumps(welcome_msg))

    async def unregister_client(self, websocket: WebSocketServerProtocol):
        """注销客户端连接"""
        self.clients.discard(websocket)
        logger.info(f"❌ 客户端断开连接 (剩余连接数: {len(self.clients)})")

    async def broadcast_message(self, message: Dict, exclude_client=None):
        """向所有连接的客户端广播消息"""
        if not self.clients:
            return
            
        message_json = json.dumps(message)
        disconnected_clients = set()
        
        for client in self.clients:
            if client == exclude_client:
                continue
                
            try:
                await client.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                disconnected_clients.add(client)
        
        # 清理断开的连接
        for client in disconnected_clients:
            self.clients.discard(client)

    async def handle_command_execution(self, websocket: WebSocketServerProtocol, data: Dict):
        """处理远程命令执行请求"""
        command_name = data.get("command")
        parameters = data.get("parameters", {})
        
        if command_name not in self.command_whitelist:
            error_msg = {
                "type": "error",
                "message": f"未授权的命令: {command_name}",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(error_msg))
            return
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        command_info = self.command_whitelist[command_name]
        
        # 记录任务信息
        self.active_tasks[task_id] = {
            "command": command_name,
            "script": command_info["script"],
            "description": command_info["description"],
            "parameters": parameters,
            "status": "starting",
            "start_time": datetime.now().isoformat(),
            "client": f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        }
        
        # 通知所有客户端任务开始
        start_msg = {
            "type": "task_started",
            "task_id": task_id,
            "command": command_name,
            "description": command_info["description"],
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_message(start_msg)
        
        # 在后台执行命令
        asyncio.create_task(self.execute_command_async(task_id, command_info["script"], parameters))
        
        # 返回任务ID给请求客户端
        response_msg = {
            "type": "task_created",
            "task_id": task_id,
            "message": f"任务 {command_name} 已启动",
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send(json.dumps(response_msg))

    async def execute_command_async(self, task_id: str, script_path: str, parameters: Dict):
        """异步执行命令并实时广播输出"""
        try:
            # 构建命令参数
            cmd_args = [script_path]
            
            # 特殊处理不同命令的参数
            if "wake_computer" in script_path:
                if "mac_address" in parameters:
                    cmd_args.append(parameters["mac_address"])
                if "ip_address" in parameters:
                    cmd_args.append(parameters["ip_address"])
            elif "shutdown_computer" in script_path:
                # 关机命令参数：类型 延迟 消息
                if "shutdown_type" in parameters:
                    cmd_args.append(parameters["shutdown_type"])
                if "delay_seconds" in parameters:
                    cmd_args.append(str(parameters["delay_seconds"]))
                if "message" in parameters:
                    cmd_args.append(f'"{parameters["message"]}"')
            else:
                # 其他命令使用标准参数格式
                for key, value in parameters.items():
                    cmd_args.extend([f"--{key}", str(value)])
            
            # 更新任务状态
            self.active_tasks[task_id]["status"] = "running"
            
            # 启动进程
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=Path(__file__).parent
            )
            
            self.active_tasks[task_id]["process"] = process
            
            # 实时读取输出并广播
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                output = line.decode().strip()
                if output:
                    log_msg = {
                        "type": "task_log",
                        "task_id": task_id,
                        "output": output,
                        "timestamp": datetime.now().isoformat()
                    }
                    await self.broadcast_message(log_msg)
            
            # 等待进程完成
            return_code = await process.wait()
            
            # 更新任务状态
            self.active_tasks[task_id]["status"] = "completed" if return_code == 0 else "failed"
            self.active_tasks[task_id]["return_code"] = return_code
            self.active_tasks[task_id]["end_time"] = datetime.now().isoformat()
            
            # 广播任务完成消息
            completion_msg = {
                "type": "task_completed",
                "task_id": task_id,
                "status": self.active_tasks[task_id]["status"],
                "return_code": return_code,
                "timestamp": datetime.now().isoformat()
            }
            await self.broadcast_message(completion_msg)
            
        except Exception as e:
            logger.error(f"执行任务 {task_id} 时出错: {e}")
            
            # 更新任务状态为失败
            self.active_tasks[task_id]["status"] = "error"
            self.active_tasks[task_id]["error"] = str(e)
            self.active_tasks[task_id]["end_time"] = datetime.now().isoformat()
            
            # 广播错误消息
            error_msg = {
                "type": "task_error",
                "task_id": task_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            await self.broadcast_message(error_msg)

    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """处理客户端消息"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "execute_command":
                await self.handle_command_execution(websocket, data)
            elif message_type == "get_task_status":
                task_id = data.get("task_id")
                if task_id in self.active_tasks:
                    status_msg = {
                        "type": "task_status",
                        "task_id": task_id,
                        "task_info": self.active_tasks[task_id],
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send(json.dumps(status_msg))
            elif message_type == "get_system_info":
                # 发送系统信息
                system_msg = {
                    "type": "system_info",
                    "connected_clients": len(self.clients),
                    "active_tasks": len([t for t in self.active_tasks.values() if t["status"] == "running"]),
                    "available_commands": self.command_whitelist,
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(system_msg))
            else:
                logger.warning(f"未知消息类型: {message_type}")
                
        except json.JSONDecodeError:
            error_msg = {
                "type": "error",
                "message": "无效的JSON格式",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(error_msg))
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")

    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """处理客户端连接"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"客户端处理出错: {e}")
        finally:
            await self.unregister_client(websocket)

    async def start_server(self):
        """启动WebSocket服务器"""
        logger.info(f"🚀 NEXUS远程指挥中心启动中...")
        logger.info(f"📡 WebSocket服务器地址: ws://{self.host}:{self.port}")
        logger.info(f"🔐 支持的命令: {list(self.command_whitelist.keys())}")
        
        server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            ping_interval=30,
            ping_timeout=10
        )
        
        logger.info("✅ NEXUS远程指挥中心已启动！等待客户端连接...")
        return server

def main():
    """主函数"""
    server = NexusWebSocketServer()
    
    async def run_server():
        websocket_server = await server.start_server()
        await websocket_server.wait_closed()
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("🛑 服务器正在关闭...")
    except Exception as e:
        logger.error(f"服务器运行出错: {e}")

if __name__ == "__main__":
    main()