"""
私有API密钥管理模块
管理用户的私人API密钥，包括OpenAI、Claude、Google等第三方服务
提供加密存储、权限控制和使用统计功能
"""

import os
import json
import hashlib
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from cryptography.fernet import Fernet
import base64

class APIProvider(Enum):
    """API提供商枚举"""
    OPENAI = "openai"
    CLAUDE = "claude"
    GOOGLE = "google"
    BAIDU = "baidu"
    ALIBABA = "alibaba"
    CUSTOM = "custom"

class APIKeyStatus(Enum):
    """API密钥状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    SUSPENDED = "suspended"

@dataclass
class APIKeyInfo:
    """API密钥信息"""
    key_id: str
    user_id: str
    provider: APIProvider
    key_name: str
    encrypted_key: str
    status: APIKeyStatus
    usage_count: int = 0
    daily_limit: int = 1000
    monthly_limit: int = 30000
    created_at: float = None
    last_used: float = None
    expires_at: float = None
    description: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

class PrivateAPIManager:
    """私有API管理器"""
    
    def __init__(self, config_file: str = "private_apis.json", key_file: str = "api_encryption.key"):
        self.config_file = os.path.join(os.path.dirname(__file__), "config", config_file)
        self.key_file = os.path.join(os.path.dirname(__file__), "config", key_file)
        self.api_keys: Dict[str, APIKeyInfo] = {}
        self.usage_stats: Dict[str, Dict[str, int]] = {}
        
        # 初始化加密密钥
        self.encryption_key = self._load_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # 加载配置
        self.load_config()
    
    def _load_or_create_encryption_key(self) -> bytes:
        """加载或创建加密密钥"""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    return f.read()
            else:
                # 创建新的加密密钥
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                # 设置文件权限为只有所有者可读写
                os.chmod(self.key_file, 0o600)
                return key
        except Exception as e:
            print(f"加密密钥处理失败: {e}")
            return Fernet.generate_key()
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """加密API密钥"""
        try:
            encrypted = self.cipher.encrypt(api_key.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            print(f"API密钥加密失败: {e}")
            return ""
    
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """解密API密钥"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_key.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            print(f"API密钥解密失败: {e}")
            return ""
    
    def _generate_key_id(self, user_id: str, provider: str, key_name: str) -> str:
        """生成密钥ID"""
        data = f"{user_id}_{provider}_{key_name}_{time.time()}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    def load_config(self):
        """加载API配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 加载API密钥
                    if 'api_keys' in data:
                        for key_id, config in data['api_keys'].items():
                            config['provider'] = APIProvider(config['provider'])
                            config['status'] = APIKeyStatus(config['status'])
                            self.api_keys[key_id] = APIKeyInfo(**config)
                    
                    # 加载使用统计
                    if 'usage_stats' in data:
                        self.usage_stats = data['usage_stats']
        except Exception as e:
            print(f"加载私有API配置失败: {e}")
            self.api_keys = {}
            self.usage_stats = {}
    
    def save_config(self):
        """保存API配置"""
        try:
            data = {
                'api_keys': {},
                'usage_stats': self.usage_stats
            }
            
            # 保存API密钥
            for key_id, key_info in self.api_keys.items():
                config = asdict(key_info)
                config['provider'] = key_info.provider.value
                config['status'] = key_info.status.value
                data['api_keys'][key_id] = config
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # 设置文件权限
            os.chmod(self.config_file, 0o600)
        except Exception as e:
            print(f"保存私有API配置失败: {e}")
    
    def add_api_key(self, user_id: str, provider: APIProvider, key_name: str, 
                   api_key: str, daily_limit: int = 1000, monthly_limit: int = 30000,
                   description: str = "") -> Optional[str]:
        """添加API密钥"""
        try:
            # 检查是否已存在相同名称的密钥
            existing_keys = self.get_user_api_keys(user_id)
            for existing_key in existing_keys:
                if existing_key.key_name == key_name and existing_key.provider == provider:
                    return None  # 已存在相同名称的密钥
            
            # 生成密钥ID
            key_id = self._generate_key_id(user_id, provider.value, key_name)
            
            # 加密API密钥
            encrypted_key = self._encrypt_api_key(api_key)
            if not encrypted_key:
                return None
            
            # 创建密钥信息
            key_info = APIKeyInfo(
                key_id=key_id,
                user_id=user_id,
                provider=provider,
                key_name=key_name,
                encrypted_key=encrypted_key,
                status=APIKeyStatus.ACTIVE,
                daily_limit=daily_limit,
                monthly_limit=monthly_limit,
                description=description
            )
            
            self.api_keys[key_id] = key_info
            self.save_config()
            
            return key_id
        except Exception as e:
            print(f"添加API密钥失败: {e}")
            return None
    
    def remove_api_key(self, user_id: str, key_id: str) -> bool:
        """删除API密钥"""
        try:
            if key_id in self.api_keys and self.api_keys[key_id].user_id == user_id:
                del self.api_keys[key_id]
                self.save_config()
                return True
            return False
        except Exception as e:
            print(f"删除API密钥失败: {e}")
            return False
    
    def get_api_key(self, user_id: str, key_id: str) -> Optional[str]:
        """获取解密后的API密钥"""
        try:
            if key_id in self.api_keys:
                key_info = self.api_keys[key_id]
                if key_info.user_id == user_id and key_info.status == APIKeyStatus.ACTIVE:
                    return self._decrypt_api_key(key_info.encrypted_key)
            return None
        except Exception as e:
            print(f"获取API密钥失败: {e}")
            return None
    
    def get_user_api_keys(self, user_id: str) -> List[APIKeyInfo]:
        """获取用户的所有API密钥信息（不包含实际密钥）"""
        user_keys = []
        for key_info in self.api_keys.values():
            if key_info.user_id == user_id:
                # 创建副本，不包含加密的密钥
                safe_key_info = APIKeyInfo(
                    key_id=key_info.key_id,
                    user_id=key_info.user_id,
                    provider=key_info.provider,
                    key_name=key_info.key_name,
                    encrypted_key="***",  # 隐藏实际密钥
                    status=key_info.status,
                    usage_count=key_info.usage_count,
                    daily_limit=key_info.daily_limit,
                    monthly_limit=key_info.monthly_limit,
                    created_at=key_info.created_at,
                    last_used=key_info.last_used,
                    expires_at=key_info.expires_at,
                    description=key_info.description
                )
                user_keys.append(safe_key_info)
        return user_keys
    
    def update_api_key_status(self, user_id: str, key_id: str, status: APIKeyStatus) -> bool:
        """更新API密钥状态"""
        try:
            if key_id in self.api_keys and self.api_keys[key_id].user_id == user_id:
                self.api_keys[key_id].status = status
                self.save_config()
                return True
            return False
        except Exception as e:
            print(f"更新API密钥状态失败: {e}")
            return False
    
    def record_api_usage(self, user_id: str, key_id: str) -> bool:
        """记录API使用"""
        try:
            if key_id in self.api_keys and self.api_keys[key_id].user_id == user_id:
                key_info = self.api_keys[key_id]
                key_info.usage_count += 1
                key_info.last_used = time.time()
                
                # 更新使用统计
                today = time.strftime("%Y-%m-%d")
                if key_id not in self.usage_stats:
                    self.usage_stats[key_id] = {}
                if today not in self.usage_stats[key_id]:
                    self.usage_stats[key_id][today] = 0
                self.usage_stats[key_id][today] += 1
                
                self.save_config()
                return True
            return False
        except Exception as e:
            print(f"记录API使用失败: {e}")
            return False
    
    def check_usage_limit(self, user_id: str, key_id: str) -> Tuple[bool, Dict[str, Any]]:
        """检查使用限制"""
        try:
            if key_id not in self.api_keys or self.api_keys[key_id].user_id != user_id:
                return False, {"error": "密钥不存在"}
            
            key_info = self.api_keys[key_id]
            if key_info.status != APIKeyStatus.ACTIVE:
                return False, {"error": "密钥未激活"}
            
            # 检查日限制
            today = time.strftime("%Y-%m-%d")
            daily_usage = 0
            if key_id in self.usage_stats and today in self.usage_stats[key_id]:
                daily_usage = self.usage_stats[key_id][today]
            
            if daily_usage >= key_info.daily_limit:
                return False, {"error": "已达到日使用限制", "daily_usage": daily_usage, "daily_limit": key_info.daily_limit}
            
            # 检查月限制
            current_month = time.strftime("%Y-%m")
            monthly_usage = 0
            if key_id in self.usage_stats:
                for date, usage in self.usage_stats[key_id].items():
                    if date.startswith(current_month):
                        monthly_usage += usage
            
            if monthly_usage >= key_info.monthly_limit:
                return False, {"error": "已达到月使用限制", "monthly_usage": monthly_usage, "monthly_limit": key_info.monthly_limit}
            
            return True, {
                "daily_usage": daily_usage,
                "daily_limit": key_info.daily_limit,
                "monthly_usage": monthly_usage,
                "monthly_limit": key_info.monthly_limit
            }
        except Exception as e:
            print(f"检查使用限制失败: {e}")
            return False, {"error": str(e)}
    
    def get_usage_statistics(self, user_id: str, key_id: Optional[str] = None) -> Dict[str, Any]:
        """获取使用统计"""
        try:
            stats = {}
            
            if key_id:
                # 获取特定密钥的统计
                if key_id in self.api_keys and self.api_keys[key_id].user_id == user_id:
                    key_info = self.api_keys[key_id]
                    stats[key_id] = {
                        "key_name": key_info.key_name,
                        "provider": key_info.provider.value,
                        "total_usage": key_info.usage_count,
                        "daily_usage": self.usage_stats.get(key_id, {}),
                        "last_used": key_info.last_used
                    }
            else:
                # 获取用户所有密钥的统计
                for kid, key_info in self.api_keys.items():
                    if key_info.user_id == user_id:
                        stats[kid] = {
                            "key_name": key_info.key_name,
                            "provider": key_info.provider.value,
                            "total_usage": key_info.usage_count,
                            "daily_usage": self.usage_stats.get(kid, {}),
                            "last_used": key_info.last_used
                        }
            
            return stats
        except Exception as e:
            print(f"获取使用统计失败: {e}")
            return {}
    
    def get_available_key(self, user_id: str, provider: APIProvider) -> Optional[Tuple[str, str]]:
        """获取用户可用的API密钥"""
        try:
            user_keys = [k for k in self.api_keys.values() 
                        if k.user_id == user_id and k.provider == provider and k.status == APIKeyStatus.ACTIVE]
            
            # 按使用次数排序，优先使用使用次数少的
            user_keys.sort(key=lambda x: x.usage_count)
            
            for key_info in user_keys:
                can_use, _ = self.check_usage_limit(user_id, key_info.key_id)
                if can_use:
                    api_key = self._decrypt_api_key(key_info.encrypted_key)
                    if api_key:
                        return key_info.key_id, api_key
            
            return None
        except Exception as e:
            print(f"获取可用密钥失败: {e}")
            return None
    
    def cleanup_expired_keys(self):
        """清理过期的密钥"""
        try:
            current_time = time.time()
            expired_keys = []
            
            for key_id, key_info in self.api_keys.items():
                if key_info.expires_at and current_time > key_info.expires_at:
                    key_info.status = APIKeyStatus.EXPIRED
                    expired_keys.append(key_id)
            
            if expired_keys:
                self.save_config()
                print(f"已标记 {len(expired_keys)} 个密钥为过期状态")
        except Exception as e:
            print(f"清理过期密钥失败: {e}")

# 全局私有API管理器实例
private_api_manager = PrivateAPIManager()

# 便捷函数
def get_private_api_manager() -> PrivateAPIManager:
    """获取私有API管理器实例"""
    return private_api_manager

def add_user_api_key(user_id: str, provider: str, key_name: str, api_key: str, **kwargs) -> Optional[str]:
    """添加用户API密钥的便捷函数"""
    try:
        provider_enum = APIProvider(provider)
        return private_api_manager.add_api_key(user_id, provider_enum, key_name, api_key, **kwargs)
    except ValueError:
        return None

def get_user_api_key(user_id: str, provider: str) -> Optional[Tuple[str, str]]:
    """获取用户API密钥的便捷函数"""
    try:
        provider_enum = APIProvider(provider)
        return private_api_manager.get_available_key(user_id, provider_enum)
    except ValueError:
        return None

if __name__ == "__main__":
    # 测试代码
    manager = PrivateAPIManager()
    
    # 测试添加API密钥
    test_user = "test_user_123"
    key_id = manager.add_api_key(
        user_id=test_user,
        provider=APIProvider.OPENAI,
        key_name="我的OpenAI密钥",
        api_key="sk-test123456789",
        daily_limit=100,
        description="测试用的OpenAI API密钥"
    )
    
    if key_id:
        print(f"成功添加API密钥，ID: {key_id}")
        
        # 测试获取密钥
        retrieved_key = manager.get_api_key(test_user, key_id)
        print(f"获取到的密钥: {retrieved_key}")
        
        # 测试使用限制检查
        can_use, info = manager.check_usage_limit(test_user, key_id)
        print(f"可以使用: {can_use}, 信息: {info}")
        
        # 测试记录使用
        manager.record_api_usage(test_user, key_id)
        print("已记录一次使用")
        
        # 获取用户密钥列表
        user_keys = manager.get_user_api_keys(test_user)
        print(f"用户密钥数量: {len(user_keys)}")
        for key in user_keys:
            print(f"- {key.key_name} ({key.provider.value}): {key.usage_count} 次使用")
    else:
        print("添加API密钥失败")