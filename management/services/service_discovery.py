#!/usr/bin/env python3
"""
🌐 N.S.S 动态服务发现系统
自动端口分配、服务注册、隧道管理
"""

import socket
import json
import subprocess
import threading
import time
import requests
import os
from pathlib import Path
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceDiscovery:
    def __init__(self):
        # 动态发现项目根目录
        self.script_dir = Path(__file__).resolve().parent
        self.project_root = self.script_dir.parent.parent
        
        # 服务注册表文件
        self.registry_file = self.project_root / "management" / "config" / "service_registry.json"
        self.registry_file.parent.mkdir(exist_ok=True)
        
        # 端口范围配置
        self.port_ranges = {
            'rag_api': (5000, 5100),
            'nexus_frontend': (52300, 52400),
            'api_gateway': (8000, 8100),
            'energy_api': (56400, 56500),
            'websocket': (9000, 9100),
            'tunnel_manager': (7000, 7100)
        }
        
        # 服务注册表
        self.services = {}
        self.tunnels = {}
        
        # 加载现有注册表
        self.load_registry()
    
    def find_free_port(self, start_port=5000, end_port=6000):
        """查找可用端口"""
        for port in range(start_port, end_port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise RuntimeError(f"无法在 {start_port}-{end_port} 范围内找到可用端口")
    
    def register_service(self, service_name, service_type='api', custom_port=None):
        """注册服务并分配端口"""
        try:
            # 获取端口范围
            port_range = self.port_ranges.get(service_type, (5000, 6000))
            
            # 分配端口
            if custom_port and self.is_port_available(custom_port):
                port = custom_port
            else:
                port = self.find_free_port(port_range[0], port_range[1])
            
            # 注册服务
            service_info = {
                'name': service_name,
                'type': service_type,
                'port': port,
                'local_url': f'http://localhost:{port}',
                'status': 'registered',
                'registered_at': datetime.now().isoformat(),
                'pid': None,
                'tunnel_url': None
            }
            
            self.services[service_name] = service_info
            self.save_registry()
            
            logger.info(f"✅ 服务注册成功: {service_name} -> {service_info['local_url']}")
            return service_info
            
        except Exception as e:
            logger.error(f"❌ 服务注册失败 {service_name}: {e}")
            return None
    
    def is_port_available(self, port):
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def get_service_config(self):
        """获取所有服务配置（供前端使用）"""
        config = {
            'services': {},
            'updated_at': datetime.now().isoformat()
        }
        
        for name, info in self.services.items():
            config['services'][name] = {
                'local_url': info['local_url'],
                'tunnel_url': info.get('tunnel_url'),
                'status': info['status'],
                'port': info['port']
            }
        
        return config
    
    def save_registry(self):
        """保存服务注册表"""
        try:
            registry_data = {
                'services': self.services,
                'tunnels': self.tunnels,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"❌ 保存注册表失败: {e}")
    
    def load_registry(self):
        """加载服务注册表"""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.services = data.get('services', {})
                    self.tunnels = data.get('tunnels', {})
                    logger.info(f"✅ 加载注册表成功，共 {len(self.services)} 个服务")
        except Exception as e:
            logger.error(f"❌ 加载注册表失败: {e}")

if __name__ == '__main__':
    # 创建服务发现实例
    sd = ServiceDiscovery()
    
    print("🌐 N.S.S 动态服务发现系统")
    print("=" * 40)
    
    # 注册核心服务
    services_to_register = [
        ('rag_api', 'rag_api'),
        ('nexus_frontend', 'nexus_frontend'),
        ('api_gateway', 'api_gateway')
    ]
    
    for service_name, service_type in services_to_register:
        result = sd.register_service(service_name, service_type)
        if result:
            print(f"📝 {service_name}: {result['local_url']}")
    
    print(f"\n📋 配置文件: {sd.registry_file}")
    print("🎯 服务注册完成！")