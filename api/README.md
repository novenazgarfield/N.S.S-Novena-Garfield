# 🔧 通用API管理系统

为研究工作站项目提供统一的API配置管理和私有密钥管理服务。

## 🎯 系统概述

这是一个独立的API管理系统，为整个研究工作站项目的所有子系统提供：

- **统一的API端点配置管理**
- **安全的私有API密钥存储**
- **基于角色的权限控制**
- **API使用统计和监控**
- **可视化Web管理界面**

### 支持的子系统

- 🤖 **RAG智能问答系统**
- 🐄 **ML牛模型系统**
- 🐱 **桌面宠物系统**
- 🔬 **其他研究工具**

## 🚀 快速开始

### 1. 启动API管理系统

```bash
# 启动完整的API管理服务（包含Web界面）
python start_api_manager.py start

# 仅初始化系统
python start_api_manager.py init

# 测试系统功能
python start_api_manager.py test

# 查看系统状态
python start_api_manager.py status
```

### 2. 访问Web管理界面

- **本地访问**: http://localhost:56336
- **公网访问**: http://13.57.59.89:56336

### 3. 在子系统中集成

```python
# 导入API管理功能
from api_management import validate_api_request, record_api_usage

# 验证API请求
def handle_user_request(user_id, user_role, api_name, provider=None):
    # 完整的权限验证和密钥获取
    result = validate_api_request(user_id, user_role, api_name, provider)
    
    if result["success"]:
        # 使用返回的API密钥调用外部服务
        api_key = result["api_key"]
        # ... 调用外部API
        
        # 记录使用
        record_api_usage(user_id, result["key_id"])
        
        return "API调用成功"
    else:
        return f"权限验证失败: {result['message']}"
```

## 📁 项目结构

```
api_management/
├── __init__.py                 # 主模块入口
├── api_config.py              # 公共API配置管理
├── private_api_manager.py     # 私有API密钥管理
├── api_web_manager.py         # Web管理界面
├── start_api_manager.py       # 启动脚本
├── config/                    # 配置文件目录
│   ├── api_endpoints.json     # API端点配置
│   ├── private_apis.json      # 私有API配置（加密）
│   └── api_encryption.key     # 加密密钥文件
├── integrations/              # 子系统集成示例
│   └── rag_integration.py     # RAG系统集成示例
├── docs/                      # 文档目录
│   ├── API_MANAGEMENT_README.md
│   └── API_SYSTEM_SUMMARY.md
└── logs/                      # 日志目录
```

## 🔐 安全特性

### 1. 加密存储
- 使用Fernet对称加密算法
- 独立的加密密钥文件
- 配置文件权限自动设置为600

### 2. 权限控制
- 4种用户角色：Guest、User、VIP、Admin
- 4种API类型：Public、Private、Protected、Internal
- 细粒度的访问控制

### 3. 使用监控
- 实时使用统计
- 日/月使用限制
- 异常使用检测

## 👥 用户角色权限

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

## 🌐 Web管理界面功能

### 📊 系统概览
- API端点统计
- 私有密钥统计
- 使用情况图表
- 系统状态监控

### 🔗 API端点管理
- 查看所有API端点
- 添加新的API端点
- 编辑端点配置
- 启用/禁用端点

### 🔐 私有密钥管理
- 用户密钥列表
- 添加新密钥
- 密钥状态管理
- 使用限制设置

### 📈 使用统计
- 详细使用报告
- 按用户统计
- 按时间统计
- 可视化图表

### 🔒 权限测试
- 权限验证测试
- 角色功能预览
- API访问测试

## 🔌 子系统集成示例

### RAG系统集成

```python
from api_management.integrations.rag_integration import RAGAPIIntegration

rag = RAGAPIIntegration()

# 带权限检查的聊天
result = rag.chat_with_permission(
    user_id="user123",
    user_role="vip", 
    message="什么是人工智能？",
    model_provider="openai"
)

if result["success"]:
    print(f"AI回复: {result['response']}")
else:
    print(f"错误: {result['message']}")
```

### 其他系统集成

```python
# 通用集成模式
from api_management import validate_api_request, record_api_usage

def your_system_api_call(user_id, user_role, feature_name):
    # 1. 验证权限和获取密钥
    validation = validate_api_request(user_id, user_role, feature_name, "openai")
    
    if not validation["success"]:
        return {"error": validation["message"]}
    
    # 2. 使用API密钥调用外部服务
    api_key = validation["api_key"]
    # ... 你的API调用逻辑
    
    # 3. 记录使用
    record_api_usage(user_id, validation["key_id"])
    
    return {"success": True, "data": "..."}
```

## 📊 系统监控

### 实时状态检查
```bash
# 检查系统状态
python start_api_manager.py status
```

### 日志监控
```bash
# 查看Web界面日志
tail -f logs/api_manager.log

# 查看系统日志
tail -f logs/system.log
```

## 🛠️ 配置管理

### 添加新的API提供商
```python
# 在 private_api_manager.py 中添加
class APIProvider(Enum):
    # ... 现有提供商
    NEW_PROVIDER = "new_provider"
```

### 添加新的用户角色
```python
# 在 api_config.py 中添加
class UserRole(Enum):
    # ... 现有角色
    SUPER_ADMIN = "super_admin"
```

### 自定义API端点
```python
from api_management import get_global_api_manager
from api_management.api_config import APIEndpoint, APIType, UserRole

manager = get_global_api_manager()

# 添加新端点
endpoint = APIEndpoint(
    name="custom_api",
    url="/api/custom",
    api_type=APIType.PRIVATE,
    required_roles=[UserRole.USER, UserRole.VIP],
    rate_limit=200,
    description="自定义API端点"
)

manager.add_endpoint(endpoint)
```

## 🚨 重要注意事项

1. **加密密钥安全**: `config/api_encryption.key` 文件非常重要，丢失将无法解密已存储的API密钥
2. **文件权限**: 确保配置文件权限设置正确（600）
3. **定期备份**: 定期备份整个 `config` 目录
4. **密钥轮换**: 定期更换API密钥以提高安全性

## 📞 技术支持

### 常见问题
- 查看 `docs/` 目录中的详细文档
- 运行测试脚本诊断问题
- 检查日志文件获取错误信息

### 系统要求
- Python 3.8+
- Streamlit
- Cryptography
- Plotly
- Pandas

## 🎉 部署状态

✅ **API管理系统已完全部署**

- **Web界面**: http://localhost:56336
- **配置文件**: 已生成并加密存储
- **权限系统**: 已配置并测试
- **集成示例**: 已提供完整示例

---

**版本**: 1.0.0  
**更新时间**: 2025-08-18  
**状态**: ✅ 生产就绪