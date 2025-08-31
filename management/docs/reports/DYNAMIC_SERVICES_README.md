# 🌐 N.S.S 动态服务系统

## 🎯 概述

N.S.S-Novena-Garfield 现在配备了智能动态服务发现系统，彻底解决了端口冲突和硬编码地址问题。

## ✨ 核心特性

### 🔧 自动端口分配
- **智能检测**: 自动扫描可用端口，避免冲突
- **范围管理**: 不同服务类型使用不同端口范围
- **动态分配**: 每次启动自动分配最佳端口

### 🌐 服务发现机制
- **自动注册**: 服务启动时自动注册到发现系统
- **实时更新**: 配置变更实时同步到所有组件
- **健康检查**: 持续监控服务状态

### 🚀 一键启动
- **智能启动器**: 自动启动所有必需服务
- **隧道管理**: 自动创建公网访问隧道
- **配置同步**: 前后端配置自动同步

## 📋 服务端口范围

| 服务类型 | 端口范围 | 说明 |
|---------|---------|------|
| RAG API | 5000-5100 | 智能问答后端服务 |
| Nexus前端 | 52300-52400 | Web界面服务 |
| API网关 | 8000-8100 | 服务发现和配置中心 |
| WebSocket | 9000-9100 | 实时通信服务 |
| 隧道管理 | 7000-7100 | 隧道控制服务 |

## 🚀 快速启动

### 方法1: 一键启动（推荐）
```bash
cd /workspace
python start_nss.py
```

### 方法2: 手动启动
```bash
cd /workspace/management/services
python smart_launcher.py
```

## 📁 文件结构

```
/workspace/
├── start_nss.py                           # 一键启动脚本
├── management/
│   ├── services/
│   │   ├── service_discovery.py           # 服务发现核心
│   │   └── smart_launcher.py              # 智能启动器
│   └── config/
│       └── service_registry.json          # 服务注册表
├── systems/
│   └── nexus/
│       └── public/
│           ├── dynamic_config.js           # 前端动态配置
│           └── api_config.json            # API配置文件
└── simple_rag_api.py                      # 简化RAG API服务
```

## 🔧 配置系统

### 服务注册表 (`service_registry.json`)
```json
{
  "services": {
    "rag_api": {
      "name": "rag_api",
      "type": "rag_api",
      "port": 5001,
      "local_url": "http://localhost:5001",
      "tunnel_url": "https://xxx.trycloudflare.com",
      "status": "running"
    }
  }
}
```

### 前端配置 (`api_config.json`)
```json
{
  "api_endpoints": {
    "rag_api": "http://localhost:5001",
    "health_check": "http://localhost:5001/api/health",
    "chat": "http://localhost:5001/api/chat",
    "upload": "http://localhost:5001/api/upload"
  }
}
```

## 🌐 动态配置工作流程

1. **服务启动**: 智能启动器启动所有服务
2. **端口分配**: 自动检测并分配可用端口
3. **服务注册**: 将服务信息注册到发现系统
4. **配置生成**: 生成前端配置文件
5. **隧道创建**: 自动创建公网访问隧道
6. **配置同步**: 前端自动加载最新配置

## 🔍 服务监控

### 健康检查端点
- RAG API: `http://localhost:{port}/api/health`
- 服务发现: `http://localhost:{port}/api/services/config`

### 状态查询
```bash
# 查看服务注册表
cat /workspace/management/config/service_registry.json

# 查看前端配置
cat /workspace/systems/nexus/public/api_config.json
```

## 🛠️ 故障排除

### 端口被占用
系统会自动检测并分配新端口，无需手动干预。

### 服务连接失败
前端配置了自动重连机制，会尝试重新连接服务。

### 隧道创建失败
检查 `cloudflared` 是否存在于 `/workspace/systems/nexus/` 目录。

## 🎯 使用示例

### 启动系统
```bash
cd /workspace
python start_nss.py
```

### 访问服务
启动完成后，系统会显示：
```
🌟 N.S.S 服务状态报告
==================================================
📋 rag_api:
   🔗 本地地址: http://localhost:5001
   🌐 公网地址: https://xxx.trycloudflare.com

📋 nexus_frontend:
   🔗 本地地址: http://localhost:52300
   🌐 公网地址: https://yyy.trycloudflare.com
```

### 停止服务
按 `Ctrl+C` 即可优雅停止所有服务。

## 🔄 版本历史

- **v2.0**: 引入动态服务发现系统
- **v1.0**: 基础静态配置系统

## 📞 技术支持

如遇问题，请检查：
1. 服务注册表文件是否正常生成
2. 端口是否被其他程序占用
3. 网络连接是否正常

---

🌟 **N.S.S-Novena-Garfield 动态服务系统** - 让部署更智能，让开发更高效！