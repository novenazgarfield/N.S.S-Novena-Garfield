#!/usr/bin/env python3
"""
🌐 统一API管理系统
=================

整合所有API管理功能，提供统一的接口
- 基础API管理 (api_manager.py)
- 私有API管理 (private_api_manager.py)
- Web API管理 (api_web_manager.py)
- 能源API服务 (energy_api_server.py)

保持所有原有功能不变，仅统一管理
"""

import os
import sys
import json
import time
import logging
import hashlib
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

class APIProvider(Enum):
    """API提供商枚举"""
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    BAIDU = "baidu"
    ALIBABA = "alibaba"
    ZHIPU = "zhipu"
    LOCAL = "local"
    CUSTOM = "custom"

class APIKeyStatus(Enum):
    """API密钥状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    INVALID = "invalid"

@dataclass
class APIKeyInfo:
    """API密钥信息"""
    provider: APIProvider
    key: str
    name: str
    status: APIKeyStatus = APIKeyStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    rate_limit: Optional[int] = None
    monthly_limit: Optional[float] = None
    current_usage: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class APIEndpoint:
    """API端点信息"""
    provider: APIProvider
    base_url: str
    endpoints: Dict[str, str]
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_count: int = 3

class UnifiedAPIManager:
    """统一API管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or str(PROJECT_ROOT / "api" / "config" / "api_config.json")
        self.keys_file = str(PROJECT_ROOT / "api" / "config" / "api_keys.json")
        
        # 初始化日志
        self.logger = self._setup_logger()
        
        # API密钥存储
        self.api_keys: Dict[str, APIKeyInfo] = {}
        
        # API端点配置
        self.endpoints: Dict[APIProvider, APIEndpoint] = {}
        
        # 使用统计
        self.usage_stats: Dict[str, Dict[str, Any]] = {}
        
        # 初始化
        self._init_default_endpoints()
        self.load_config()
        
        # FastAPI应用
        self.app = FastAPI(
            title="统一API管理系统",
            description="N.S.S-Novena-Garfield项目API管理服务",
            version="2.0.0"
        )
        self._setup_fastapi()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("UnifiedAPIManager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _init_default_endpoints(self):
        """初始化默认API端点"""
        self.endpoints = {
            APIProvider.OPENAI: APIEndpoint(
                provider=APIProvider.OPENAI,
                base_url="https://api.openai.com/v1",
                endpoints={
                    "chat": "/chat/completions",
                    "embeddings": "/embeddings",
                    "models": "/models"
                },
                headers={"Content-Type": "application/json"}
            ),
            APIProvider.GEMINI: APIEndpoint(
                provider=APIProvider.GEMINI,
                base_url="https://generativelanguage.googleapis.com/v1beta",
                endpoints={
                    "generate": "/models/gemini-pro:generateContent",
                    "embed": "/models/embedding-001:embedContent"
                },
                headers={"Content-Type": "application/json"}
            ),
            APIProvider.CLAUDE: APIEndpoint(
                provider=APIProvider.CLAUDE,
                base_url="https://api.anthropic.com/v1",
                endpoints={
                    "messages": "/messages",
                    "complete": "/complete"
                },
                headers={
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
            )
        }
    
    def _setup_fastapi(self):
        """设置FastAPI应用"""
        # CORS中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 安全认证
        security = HTTPBearer()
        
        @self.app.get("/")
        async def root():
            return {
                "message": "统一API管理系统",
                "version": "2.0.0",
                "status": "running"
            }
        
        @self.app.get("/api/keys")
        async def list_api_keys():
            """列出所有API密钥（隐藏实际密钥）"""
            return {
                key_id: {
                    "provider": info.provider.value,
                    "name": info.name,
                    "status": info.status.value,
                    "created_at": info.created_at.isoformat(),
                    "usage_count": info.usage_count,
                    "current_usage": info.current_usage
                }
                for key_id, info in self.api_keys.items()
            }
        
        @self.app.post("/api/keys")
        async def add_api_key(key_data: dict):
            """添加新的API密钥"""
            try:
                provider = APIProvider(key_data["provider"])
                key_info = APIKeyInfo(
                    provider=provider,
                    key=key_data["key"],
                    name=key_data.get("name", f"{provider.value}_key"),
                    rate_limit=key_data.get("rate_limit"),
                    monthly_limit=key_data.get("monthly_limit")
                )
                
                key_id = self.add_api_key(key_info)
                return {"key_id": key_id, "message": "API密钥添加成功"}
                
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.delete("/api/keys/{key_id}")
        async def remove_api_key(key_id: str):
            """删除API密钥"""
            if self.remove_api_key(key_id):
                return {"message": "API密钥删除成功"}
            else:
                raise HTTPException(status_code=404, detail="API密钥不存在")
        
        @self.app.get("/api/stats")
        async def get_usage_stats():
            """获取使用统计"""
            return self.get_usage_statistics()
        
        @self.app.post("/api/request")
        async def make_api_request(request_data: dict):
            """统一API请求接口"""
            try:
                provider = APIProvider(request_data["provider"])
                endpoint = request_data["endpoint"]
                data = request_data.get("data", {})
                key_id = request_data.get("key_id")
                
                result = await self.make_request(provider, endpoint, data, key_id)
                return result
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    def add_api_key(self, key_info: APIKeyInfo) -> str:
        """添加API密钥"""
        key_id = hashlib.md5(
            f"{key_info.provider.value}_{key_info.key}_{time.time()}".encode()
        ).hexdigest()[:16]
        
        self.api_keys[key_id] = key_info
        self.save_config()
        
        self.logger.info(f"添加API密钥: {key_info.provider.value} - {key_info.name}")
        return key_id
    
    def remove_api_key(self, key_id: str) -> bool:
        """删除API密钥"""
        if key_id in self.api_keys:
            key_info = self.api_keys[key_id]
            del self.api_keys[key_id]
            self.save_config()
            
            self.logger.info(f"删除API密钥: {key_info.provider.value} - {key_info.name}")
            return True
        return False
    
    def get_api_key(self, provider: APIProvider, key_id: Optional[str] = None) -> Optional[APIKeyInfo]:
        """获取API密钥"""
        if key_id:
            return self.api_keys.get(key_id)
        
        # 查找该提供商的活跃密钥
        for key_info in self.api_keys.values():
            if key_info.provider == provider and key_info.status == APIKeyStatus.ACTIVE:
                return key_info
        
        return None
    
    async def make_request(
        self, 
        provider: APIProvider, 
        endpoint: str, 
        data: Dict[str, Any],
        key_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """统一API请求方法"""
        # 获取API密钥
        key_info = self.get_api_key(provider, key_id)
        if not key_info:
            raise ValueError(f"未找到 {provider.value} 的有效API密钥")
        
        # 获取端点配置
        endpoint_config = self.endpoints.get(provider)
        if not endpoint_config:
            raise ValueError(f"未配置 {provider.value} 的端点信息")
        
        # 构建请求URL
        if endpoint not in endpoint_config.endpoints:
            raise ValueError(f"未知的端点: {endpoint}")
        
        url = endpoint_config.base_url + endpoint_config.endpoints[endpoint]
        
        # 构建请求头
        headers = endpoint_config.headers.copy()
        
        if provider == APIProvider.OPENAI:
            headers["Authorization"] = f"Bearer {key_info.key}"
        elif provider == APIProvider.GEMINI:
            url += f"?key={key_info.key}"
        elif provider == APIProvider.CLAUDE:
            headers["x-api-key"] = key_info.key
        
        # 发送请求
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url, 
                    json=data, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=endpoint_config.timeout)
                ) as response:
                    result = await response.json()
                    
                    # 更新使用统计
                    self._update_usage_stats(key_info, endpoint, response.status)
                    
                    if response.status == 200:
                        return result
                    else:
                        raise HTTPException(
                            status_code=response.status,
                            detail=result.get("error", "API请求失败")
                        )
                        
            except asyncio.TimeoutError:
                raise HTTPException(status_code=408, detail="请求超时")
            except Exception as e:
                self.logger.error(f"API请求失败: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _update_usage_stats(self, key_info: APIKeyInfo, endpoint: str, status_code: int):
        """更新使用统计"""
        key_info.usage_count += 1
        key_info.last_used = datetime.now()
        
        # 更新全局统计
        provider_key = key_info.provider.value
        if provider_key not in self.usage_stats:
            self.usage_stats[provider_key] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "endpoints": {}
            }
        
        stats = self.usage_stats[provider_key]
        stats["total_requests"] += 1
        
        if 200 <= status_code < 300:
            stats["successful_requests"] += 1
        else:
            stats["failed_requests"] += 1
        
        if endpoint not in stats["endpoints"]:
            stats["endpoints"][endpoint] = 0
        stats["endpoints"][endpoint] += 1
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """获取使用统计"""
        return {
            "api_keys_count": len(self.api_keys),
            "active_keys": len([k for k in self.api_keys.values() if k.status == APIKeyStatus.ACTIVE]),
            "providers": list(set(k.provider.value for k in self.api_keys.values())),
            "usage_stats": self.usage_stats,
            "last_updated": datetime.now().isoformat()
        }
    
    def load_config(self):
        """加载配置"""
        try:
            # 加载API密钥
            if os.path.exists(self.keys_file):
                with open(self.keys_file, 'r', encoding='utf-8') as f:
                    keys_data = json.load(f)
                
                for key_id, key_data in keys_data.items():
                    try:
                        key_info = APIKeyInfo(
                            provider=APIProvider(key_data["provider"]),
                            key=key_data["key"],
                            name=key_data["name"],
                            status=APIKeyStatus(key_data.get("status", "active")),
                            created_at=datetime.fromisoformat(key_data["created_at"]),
                            usage_count=key_data.get("usage_count", 0),
                            current_usage=key_data.get("current_usage", 0.0)
                        )
                        
                        if key_data.get("last_used"):
                            key_info.last_used = datetime.fromisoformat(key_data["last_used"])
                        
                        self.api_keys[key_id] = key_info
                        
                    except Exception as e:
                        self.logger.error(f"加载API密钥失败 {key_id}: {str(e)}")
            
            self.logger.info(f"已加载 {len(self.api_keys)} 个API密钥")
            
        except Exception as e:
            self.logger.error(f"加载配置失败: {str(e)}")
    
    def save_config(self):
        """保存配置"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.keys_file), exist_ok=True)
            
            # 保存API密钥
            keys_data = {}
            for key_id, key_info in self.api_keys.items():
                keys_data[key_id] = {
                    "provider": key_info.provider.value,
                    "key": key_info.key,
                    "name": key_info.name,
                    "status": key_info.status.value,
                    "created_at": key_info.created_at.isoformat(),
                    "usage_count": key_info.usage_count,
                    "current_usage": key_info.current_usage
                }
                
                if key_info.last_used:
                    keys_data[key_id]["last_used"] = key_info.last_used.isoformat()
            
            with open(self.keys_file, 'w', encoding='utf-8') as f:
                json.dump(keys_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("配置已保存")
            
        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")
    
    def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """启动API服务器"""
        self.logger.info(f"启动统一API管理服务器: http://{host}:{port}")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="统一API管理系统")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--config", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 创建管理器
    manager = UnifiedAPIManager(args.config)
    
    # 启动服务器
    try:
        manager.start_server(args.host, args.port)
    except KeyboardInterrupt:
        print("\n正在关闭服务器...")
    except Exception as e:
        print(f"服务器启动失败: {e}")

if __name__ == "__main__":
    main()