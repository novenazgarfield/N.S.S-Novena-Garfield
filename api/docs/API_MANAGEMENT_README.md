# API管理系统使用指南

本系统提供了完整的API管理解决方案，包括公共API配置管理和私有API密钥管理。

## 📁 文件结构

```
rag_system/config/
├── api_config.py              # 公共API配置管理
├── private_api_manager.py     # 私有API密钥管理
├── api_usage_example.py       # 使用示例
├── api_endpoints.json         # API端点配置文件
├── private_apis.json          # 私有API配置文件（加密存储）
├── api_encryption.key         # 加密密钥文件
└── API_MANAGEMENT_README.md   # 本说明文件
```

## 🔧 功能特性

### 1. 公共API配置管理 (`api_config.py`)

- **权限控制**: 支持4种用户角色（Guest、User、VIP、Admin）
- **API类型**: 公共、私有、受保护、内部API
- **访问控制**: 基于角色的API访问权限验证
- **速率限制**: 每个API端点可设置访问频率限制
- **动态配置**: 支持运行时添加、删除、修改API端点

### 2. 私有API密钥管理 (`private_api_manager.py`)

- **安全存储**: 使用Fernet加密算法加密存储API密钥
- **多提供商支持**: OpenAI、Claude、Google、百度、阿里云等
- **使用限制**: 支持日限制和月限制
- **使用统计**: 详细的API使用记录和统计
- **自动过期**: 支持密钥过期时间设置

## 🚀 快速开始

### 1. 基本使用

```python
from api_config import check_api_access, get_user_apis
from private_api_manager import add_user_api_key, get_user_api_key

# 检查用户是否有权限访问API
has_permission = check_api_access('user_chat', 'user')

# 获取用户可访问的API列表
user_apis = get_user_apis('vip')

# 添加用户的私有API密钥
key_id = add_user_api_key(
    user_id="user123",
    provider="openai",
    key_name="我的OpenAI密钥",
    api_key="sk-proj-...",
    daily_limit=100
)

# 获取用户的API密钥
key_result = get_user_api_key("user123", "openai")
if key_result:
    key_id, api_key = key_result
    print(f"获取到API密钥: {api_key}")
```

### 2. 完整的API调用流程

```python
def handle_api_request(user_id, user_role, api_endpoint, provider):
    """处理API请求的完整流程"""
    
    # 1. 检查API访问权限
    if not check_api_access(api_endpoint, user_role):
        return {"error": "没有权限访问此API"}
    
    # 2. 获取用户的私有API密钥
    key_result = get_user_api_key(user_id, provider)
    if not key_result:
        return {"error": "没有可用的API密钥"}
    
    key_id, api_key = key_result
    
    # 3. 检查使用限制
    private_manager = PrivateAPIManager()
    can_use, limit_info = private_manager.check_usage_limit(user_id, key_id)
    if not can_use:
        return {"error": f"使用限制: {limit_info['error']}"}
    
    # 4. 调用实际API
    try:
        # 这里调用实际的API
        result = call_external_api(api_key, user_request)
        
        # 5. 记录使用
        private_manager.record_api_usage(user_id, key_id)
        
        return {"success": True, "data": result}
    except Exception as e:
        return {"error": str(e)}
```

## 🔐 安全特性

### 1. 加密存储
- 所有私有API密钥使用Fernet对称加密
- 加密密钥单独存储，权限设置为600（仅所有者可读写）
- 配置文件权限自动设置为600

### 2. 权限控制
- 基于角色的访问控制（RBAC）
- 多层次权限验证
- API类型分级管理

### 3. 使用监控
- 详细的使用记录和统计
- 日/月使用限制
- 异常使用检测

## 📊 用户角色权限

| 角色 | 权限描述 | 可访问API类型 |
|------|----------|---------------|
| Guest | 访客用户 | Public |
| User | 普通用户 | Public + Private |
| VIP | VIP用户 | Public + Private + Protected (VIP) |
| Admin | 管理员 | Public + Private + Protected (All) |

## 🔧 API类型说明

| 类型 | 描述 | 访问要求 |
|------|------|----------|
| Public | 公共API | 无需认证 |
| Private | 私有API | 需要用户认证 |
| Protected | 受保护API | 需要特殊权限 |
| Internal | 内部API | 仅系统内部使用 |

## 📈 使用统计

系统自动记录以下统计信息：
- 每个API密钥的使用次数
- 每日/每月使用量
- 最后使用时间
- 使用趋势分析

## 🛠️ 管理员功能

### 1. 系统概览
```python
from api_config import APIConfigManager

manager = APIConfigManager()
summary = manager.get_api_summary()
print(f"总API数: {summary['total_endpoints']}")
print(f"活跃API数: {summary['active_endpoints']}")
```

### 2. 用户管理
```python
from private_api_manager import PrivateAPIManager

private_manager = PrivateAPIManager()

# 获取所有用户的API使用统计
for user_id in get_all_users():
    stats = private_manager.get_usage_statistics(user_id)
    print(f"用户 {user_id} 的使用统计: {stats}")
```

## 🔄 配置文件格式

### API端点配置 (`api_endpoints.json`)
```json
{
  "user_chat": {
    "name": "user_chat",
    "url": "/api/chat",
    "api_type": "private",
    "required_roles": ["user", "vip", "admin"],
    "rate_limit": 50,
    "description": "用户聊天接口",
    "is_active": true,
    "created_at": 1755489443.626
  }
}
```

### 私有API配置 (`private_apis.json`)
```json
{
  "api_keys": {
    "key_id_123": {
      "key_id": "key_id_123",
      "user_id": "user123",
      "provider": "openai",
      "key_name": "我的OpenAI密钥",
      "encrypted_key": "gAAAAABh...",
      "status": "active",
      "usage_count": 42,
      "daily_limit": 100,
      "monthly_limit": 3000
    }
  },
  "usage_stats": {
    "key_id_123": {
      "2025-08-18": 5,
      "2025-08-17": 12
    }
  }
}
```

## 🚨 注意事项

1. **加密密钥安全**: `api_encryption.key` 文件非常重要，丢失将无法解密已存储的API密钥
2. **文件权限**: 确保配置文件权限设置正确（600）
3. **备份**: 定期备份配置文件和加密密钥
4. **密钥轮换**: 定期更换API密钥以提高安全性
5. **监控**: 定期检查API使用统计，发现异常使用

## 🔧 扩展开发

### 添加新的API提供商
```python
# 在 private_api_manager.py 中的 APIProvider 枚举中添加
class APIProvider(Enum):
    # ... 现有提供商
    NEW_PROVIDER = "new_provider"
```

### 添加新的用户角色
```python
# 在 api_config.py 中的 UserRole 枚举中添加
class UserRole(Enum):
    # ... 现有角色
    SUPER_ADMIN = "super_admin"
```

### 自定义权限验证
```python
def custom_permission_check(user_id, api_endpoint):
    """自定义权限验证逻辑"""
    # 实现您的自定义逻辑
    return True
```

## 📞 技术支持

如果您在使用过程中遇到问题，请：
1. 查看日志文件中的错误信息
2. 检查配置文件格式是否正确
3. 确认文件权限设置
4. 验证API密钥是否有效

---

**版本**: 1.0.0  
**更新时间**: 2025-08-18  
**兼容性**: Python 3.8+