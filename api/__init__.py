"""
通用API管理系统
为整个研究工作站项目提供统一的API配置和私有密钥管理服务

支持的子系统：
- RAG智能问答系统
- ML牛模型系统  
- 桌面宠物系统
- 其他未来扩展的系统

主要功能：
1. 公共API端点配置和权限管理
2. 私有API密钥安全存储和管理
3. 用户角色权限控制
4. API使用统计和监控
5. Web管理界面
"""

from .api_config import (
    APIConfigManager,
    UserRole,
    APIType,
    APIEndpoint,
    get_api_config,
    check_api_access,
    get_user_apis
)

from .private_api_manager import (
    PrivateAPIManager,
    APIProvider,
    APIKeyStatus,
    APIKeyInfo,
    get_private_api_manager,
    add_user_api_key,
    get_user_api_key
)

__version__ = "1.0.0"
__author__ = "Research Workstation Team"
__description__ = "通用API管理系统 - 为研究工作站项目提供统一的API管理服务"

# 全局管理器实例
_api_manager = None
_private_manager = None

def get_global_api_manager():
    """获取全局API配置管理器"""
    global _api_manager
    if _api_manager is None:
        _api_manager = APIConfigManager()
    return _api_manager

def get_global_private_manager():
    """获取全局私有API管理器"""
    global _private_manager
    if _private_manager is None:
        _private_manager = PrivateAPIManager()
    return _private_manager

# 便捷函数
def init_api_system():
    """初始化API管理系统"""
    api_manager = get_global_api_manager()
    private_manager = get_global_private_manager()
    
    print("🔧 API管理系统初始化完成")
    print(f"📊 API端点数量: {len(api_manager.get_all_endpoints())}")
    print(f"🔐 私有密钥数量: {len(private_manager.api_keys)}")
    
    return api_manager, private_manager

def validate_api_request(user_id: str, user_role: str, api_endpoint: str, provider: str = None):
    """
    验证API请求的完整流程
    
    Args:
        user_id: 用户ID
        user_role: 用户角色
        api_endpoint: API端点名称
        provider: API提供商（如果需要私有密钥）
    
    Returns:
        dict: 验证结果
    """
    result = {
        "success": False,
        "message": "",
        "api_key": None,
        "key_id": None,
        "usage_info": None
    }
    
    try:
        # 1. 检查API访问权限
        if not check_api_access(api_endpoint, user_role):
            result["message"] = "用户没有权限访问此API"
            return result
        
        # 2. 如果需要私有密钥，获取并验证
        if provider:
            private_manager = get_global_private_manager()
            key_result = get_user_api_key(user_id, provider)
            
            if not key_result:
                result["message"] = f"用户没有可用的{provider} API密钥"
                return result
            
            key_id, api_key = key_result
            
            # 3. 检查使用限制
            can_use, limit_info = private_manager.check_usage_limit(user_id, key_id)
            if not can_use:
                result["message"] = f"已达到使用限制: {limit_info.get('error', '未知错误')}"
                result["usage_info"] = limit_info
                return result
            
            result["api_key"] = api_key
            result["key_id"] = key_id
            result["usage_info"] = limit_info
        
        result["success"] = True
        result["message"] = "验证通过"
        return result
        
    except Exception as e:
        result["message"] = f"验证过程出错: {str(e)}"
        return result

def record_api_usage(user_id: str, key_id: str = None):
    """记录API使用"""
    if key_id:
        private_manager = get_global_private_manager()
        return private_manager.record_api_usage(user_id, key_id)
    return True

# 导出主要类和函数
__all__ = [
    # 类
    'APIConfigManager',
    'PrivateAPIManager', 
    'UserRole',
    'APIType',
    'APIProvider',
    'APIKeyStatus',
    'APIEndpoint',
    'APIKeyInfo',
    
    # 管理器获取函数
    'get_api_config',
    'get_private_api_manager',
    'get_global_api_manager',
    'get_global_private_manager',
    
    # 便捷函数
    'check_api_access',
    'get_user_apis',
    'add_user_api_key',
    'get_user_api_key',
    'init_api_system',
    'validate_api_request',
    'record_api_usage'
]