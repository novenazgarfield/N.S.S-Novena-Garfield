"""
API配置管理模块
管理项目中所有API的配置、权限和访问控制
"""

import os
import json
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib
import time

class UserRole(Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    VIP = "vip"
    USER = "user"
    GUEST = "guest"

class APIType(Enum):
    """API类型枚举"""
    PUBLIC = "public"          # 公共API，无需认证
    PRIVATE = "private"        # 私有API，需要用户认证
    PROTECTED = "protected"    # 受保护API，需要特殊权限
    INTERNAL = "internal"      # 内部API，仅系统内部使用

@dataclass
class APIEndpoint:
    """API端点配置"""
    name: str
    url: str
    api_type: APIType
    required_roles: List[UserRole]
    rate_limit: int = 100  # 每小时请求限制
    description: str = ""
    is_active: bool = True
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

class APIConfigManager:
    """API配置管理器"""
    
    def __init__(self, config_file: str = "api_endpoints.json"):
        self.config_file = os.path.join(os.path.dirname(__file__), "config", config_file)
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.load_config()
        self._init_default_apis()
    
    def _init_default_apis(self):
        """初始化默认API配置"""
        default_apis = [
            # 公共API
            APIEndpoint(
                name="health_check",
                url="/api/health",
                api_type=APIType.PUBLIC,
                required_roles=[],
                rate_limit=1000,
                description="系统健康检查"
            ),
            APIEndpoint(
                name="system_info",
                url="/api/system/info",
                api_type=APIType.PUBLIC,
                required_roles=[],
                rate_limit=100,
                description="获取系统基本信息"
            ),
            
            # 用户API
            APIEndpoint(
                name="user_chat",
                url="/api/chat",
                api_type=APIType.PRIVATE,
                required_roles=[UserRole.USER, UserRole.VIP, UserRole.ADMIN],
                rate_limit=50,
                description="用户聊天接口"
            ),
            APIEndpoint(
                name="document_upload",
                url="/api/documents/upload",
                api_type=APIType.PRIVATE,
                required_roles=[UserRole.USER, UserRole.VIP, UserRole.ADMIN],
                rate_limit=20,
                description="文档上传接口"
            ),
            
            # VIP API
            APIEndpoint(
                name="advanced_chat",
                url="/api/chat/advanced",
                api_type=APIType.PROTECTED,
                required_roles=[UserRole.VIP, UserRole.ADMIN],
                rate_limit=100,
                description="高级聊天功能"
            ),
            APIEndpoint(
                name="batch_processing",
                url="/api/batch/process",
                api_type=APIType.PROTECTED,
                required_roles=[UserRole.VIP, UserRole.ADMIN],
                rate_limit=10,
                description="批量处理接口"
            ),
            
            # 管理员API
            APIEndpoint(
                name="user_management",
                url="/api/admin/users",
                api_type=APIType.PROTECTED,
                required_roles=[UserRole.ADMIN],
                rate_limit=200,
                description="用户管理接口"
            ),
            APIEndpoint(
                name="system_config",
                url="/api/admin/config",
                api_type=APIType.PROTECTED,
                required_roles=[UserRole.ADMIN],
                rate_limit=50,
                description="系统配置管理"
            ),
            APIEndpoint(
                name="system_logs",
                url="/api/admin/logs",
                api_type=APIType.PROTECTED,
                required_roles=[UserRole.ADMIN],
                rate_limit=100,
                description="系统日志查看"
            ),
            
            # 内部API
            APIEndpoint(
                name="internal_metrics",
                url="/api/internal/metrics",
                api_type=APIType.INTERNAL,
                required_roles=[],
                rate_limit=1000,
                description="内部指标收集"
            )
        ]
        
        for api in default_apis:
            if api.name not in self.endpoints:
                self.endpoints[api.name] = api
        
        self.save_config()
    
    def load_config(self):
        """加载API配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, config in data.items():
                        # 转换枚举类型
                        config['api_type'] = APIType(config['api_type'])
                        config['required_roles'] = [UserRole(role) for role in config['required_roles']]
                        self.endpoints[name] = APIEndpoint(**config)
        except Exception as e:
            print(f"加载API配置失败: {e}")
            self.endpoints = {}
    
    def save_config(self):
        """保存API配置"""
        try:
            data = {}
            for name, endpoint in self.endpoints.items():
                config = asdict(endpoint)
                # 转换枚举为字符串
                config['api_type'] = endpoint.api_type.value
                config['required_roles'] = [role.value for role in endpoint.required_roles]
                data[name] = config
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存API配置失败: {e}")
    
    def add_endpoint(self, endpoint: APIEndpoint) -> bool:
        """添加API端点"""
        try:
            self.endpoints[endpoint.name] = endpoint
            self.save_config()
            return True
        except Exception as e:
            print(f"添加API端点失败: {e}")
            return False
    
    def remove_endpoint(self, name: str) -> bool:
        """删除API端点"""
        try:
            if name in self.endpoints:
                del self.endpoints[name]
                self.save_config()
                return True
            return False
        except Exception as e:
            print(f"删除API端点失败: {e}")
            return False
    
    def get_endpoint(self, name: str) -> Optional[APIEndpoint]:
        """获取API端点"""
        return self.endpoints.get(name)
    
    def get_endpoints_by_role(self, user_role: UserRole) -> List[APIEndpoint]:
        """根据用户角色获取可访问的API端点"""
        accessible_endpoints = []
        for endpoint in self.endpoints.values():
            if not endpoint.is_active:
                continue
            
            # 公共API所有人都可以访问
            if endpoint.api_type == APIType.PUBLIC:
                accessible_endpoints.append(endpoint)
            # 内部API只有系统可以访问
            elif endpoint.api_type == APIType.INTERNAL:
                continue
            # 检查角色权限
            elif not endpoint.required_roles or user_role in endpoint.required_roles:
                accessible_endpoints.append(endpoint)
        
        return accessible_endpoints
    
    def get_endpoints_by_type(self, api_type: APIType) -> List[APIEndpoint]:
        """根据API类型获取端点"""
        return [ep for ep in self.endpoints.values() if ep.api_type == api_type and ep.is_active]
    
    def check_access_permission(self, endpoint_name: str, user_role: UserRole) -> bool:
        """检查用户是否有权限访问指定API"""
        endpoint = self.get_endpoint(endpoint_name)
        if not endpoint or not endpoint.is_active:
            return False
        
        # 公共API允许所有人访问
        if endpoint.api_type == APIType.PUBLIC:
            return True
        
        # 内部API只允许系统访问
        if endpoint.api_type == APIType.INTERNAL:
            return False
        
        # 检查角色权限
        return not endpoint.required_roles or user_role in endpoint.required_roles
    
    def update_endpoint(self, name: str, **kwargs) -> bool:
        """更新API端点配置"""
        try:
            if name not in self.endpoints:
                return False
            
            endpoint = self.endpoints[name]
            for key, value in kwargs.items():
                if hasattr(endpoint, key):
                    setattr(endpoint, key, value)
            
            self.save_config()
            return True
        except Exception as e:
            print(f"更新API端点失败: {e}")
            return False
    
    def get_all_endpoints(self) -> Dict[str, APIEndpoint]:
        """获取所有API端点"""
        return self.endpoints.copy()
    
    def get_api_summary(self) -> Dict[str, Any]:
        """获取API概览信息"""
        total = len(self.endpoints)
        active = sum(1 for ep in self.endpoints.values() if ep.is_active)
        by_type = {}
        by_role = {}
        
        for endpoint in self.endpoints.values():
            # 按类型统计
            type_name = endpoint.api_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
            
            # 按角色统计
            for role in endpoint.required_roles:
                role_name = role.value
                by_role[role_name] = by_role.get(role_name, 0) + 1
        
        return {
            "total_endpoints": total,
            "active_endpoints": active,
            "inactive_endpoints": total - active,
            "by_type": by_type,
            "by_role": by_role
        }

# 全局API配置管理器实例
api_config = APIConfigManager()

# 便捷函数
def get_api_config() -> APIConfigManager:
    """获取API配置管理器实例"""
    return api_config

def check_api_access(endpoint_name: str, user_role: str) -> bool:
    """检查API访问权限的便捷函数"""
    try:
        role = UserRole(user_role)
        return api_config.check_access_permission(endpoint_name, role)
    except ValueError:
        return False

def get_user_apis(user_role: str) -> List[Dict[str, Any]]:
    """获取用户可访问的API列表"""
    try:
        role = UserRole(user_role)
        endpoints = api_config.get_endpoints_by_role(role)
        return [
            {
                "name": ep.name,
                "url": ep.url,
                "type": ep.api_type.value,
                "description": ep.description,
                "rate_limit": ep.rate_limit
            }
            for ep in endpoints
        ]
    except ValueError:
        return []

if __name__ == "__main__":
    # 测试代码
    manager = APIConfigManager()
    
    # 打印API概览
    summary = manager.get_api_summary()
    print("API概览:")
    print(f"总端点数: {summary['total_endpoints']}")
    print(f"活跃端点数: {summary['active_endpoints']}")
    print(f"按类型分布: {summary['by_type']}")
    print(f"按角色分布: {summary['by_role']}")
    
    # 测试权限检查
    print(f"\n权限测试:")
    print(f"普通用户访问聊天API: {check_api_access('user_chat', 'user')}")
    print(f"普通用户访问管理API: {check_api_access('user_management', 'user')}")
    print(f"管理员访问管理API: {check_api_access('user_management', 'admin')}")