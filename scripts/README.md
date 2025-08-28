# 📁 Scripts 目录说明

这个目录包含了NEXUS AI系统的所有脚本文件，按功能分类整理。

## 📂 目录结构

```
scripts/
├── deployment/          # 部署相关脚本
├── management/          # 管理和监控脚本
├── testing/            # 测试脚本
└── README.md           # 本说明文件
```

## 🚀 deployment/ - 部署脚本

| 脚本文件 | 功能描述 | 使用方法 |
|---------|---------|---------|
| `simple_api.py` | 简化版RAG API服务器 | `python simple_api.py` |
| `online_rag_api.py` | 完整版RAG API服务器 | `python online_rag_api.py` |
| `start_services.py` | Python版服务启动器 | `python start_services.py` |
| `start_tunnels.sh` | 完整隧道启动脚本 | `./start_tunnels.sh` |
| `quick_start.sh` | 快速启动脚本 | `./quick_start.sh` |
| `start_ai_system.py` | AI系统启动器 | `python start_ai_system.py` |

## 🔧 management/ - 管理脚本

| 脚本文件 | 功能描述 | 使用方法 |
|---------|---------|---------|
| `service_status.py` | 服务状态检查器 | `python service_status.py` |
| `check_status.sh` | 系统状态检查 | `./check_status.sh` |
| `cleanup.sh` | 系统清理脚本 | `./cleanup.sh` |

## 🧪 testing/ - 测试脚本

| 脚本文件 | 功能描述 | 使用方法 |
|---------|---------|---------|
| `test_api.py` | API功能测试 | `python test_api.py` |

## 🎯 快速开始

### 1. 启动完整系统
```bash
cd /workspace/scripts/deployment
./start_tunnels.sh
```

### 2. 启动简化版本
```bash
cd /workspace/scripts/deployment
python simple_api.py &
python -m http.server 53870 --bind 0.0.0.0 &
```

### 3. 检查系统状态
```bash
cd /workspace/scripts/management
python service_status.py
```

### 4. 测试API功能
```bash
cd /workspace/scripts/testing
python test_api.py
```

## 📋 脚本依赖

### Python依赖
- flask
- flask-cors
- requests
- google-generativeai (完整版API)

### 系统依赖
- cloudflared (隧道功能)
- curl (测试功能)
- python3 (所有Python脚本)

## ⚠️ 注意事项

1. **权限设置**: 确保shell脚本有执行权限
   ```bash
   chmod +x *.sh
   ```

2. **路径问题**: 脚本中的路径已更新为新的目录结构

3. **端口冲突**: 默认使用端口5000(API)和53870(前端)

4. **隧道限制**: Cloudflare免费隧道有使用限制

## 🔄 更新日志

- **2025-08-28**: 初始整理，创建分类目录结构
- **2025-08-28**: 更新所有脚本路径引用