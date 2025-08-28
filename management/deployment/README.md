# 🚀 N.S.S-Novena-Garfield 部署指南

## 📁 部署文件说明

本目录包含N.S.S-Novena-Garfield项目的所有部署相关文件：

- `docker-compose.yml` - Docker容器编排配置
- `.env.template` - 环境变量配置模板
- `start.sh` - 快速启动脚本
- `README.md` - 本说明文件

## 🚀 快速启动

### 方法1: 使用启动脚本 (推荐)
```bash
cd management/deployment
./start.sh
```

### 方法2: 直接使用Docker Compose
```bash
# 1. 复制环境配置
cp management/deployment/.env.template .env

# 2. 启动所有服务
docker compose -f management/deployment/docker-compose.yml up -d

# 3. 查看状态
docker compose -f management/deployment/docker-compose.yml ps

# 4. 停止服务
docker compose -f management/deployment/docker-compose.yml down
```

### 方法3: 本地开发模式
```bash
python management/scripts/unified_launcher.py --interactive
```

## 🌐 服务访问地址

启动成功后，可通过以下地址访问各服务：

- **RAG智能系统**: http://localhost:8501
- **Changlee音乐播放器**: http://localhost:8082
- **Chronicle时间管理**: http://localhost:3000
- **Nexus集成管理**: http://localhost:8080
- **API管理器**: http://localhost:8000

## 🔧 配置说明

### 环境变量配置
复制 `.env.template` 为 `.env` 并根据需要修改：

```bash
# 核心服务端口
RAG_PORT=8501
CHANGLEE_WEB_PORT=8082
CHRONICLE_PORT=3000
NEXUS_PORT=8080

# API密钥
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

# 数据库配置
DB_NAME=nss_db
DB_USER=nss_user
DB_PASSWORD=nss_password
```

### Docker网络配置
- 网络名称: `nss-network`
- 网络范围: `172.20.0.0/16`
- 网关: `172.20.0.1`

### 数据持久化
- `nss-data`: 应用数据
- `nss-logs`: 日志文件
- `nss-models`: AI模型文件

## 🛠️ 故障排除

### 端口冲突
如果遇到端口冲突，修改 `.env` 文件中的端口配置。

### Docker权限问题
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### 服务启动失败
```bash
# 查看日志
docker compose -f management/deployment/docker-compose.yml logs [service-name]

# 重启服务
docker compose -f management/deployment/docker-compose.yml restart [service-name]
```

## 📊 监控和维护

### 查看服务状态
```bash
docker compose -f management/deployment/docker-compose.yml ps
```

### 查看资源使用
```bash
docker stats
```

### 清理未使用的资源
```bash
docker system prune -f
```

## 🔒 安全注意事项

1. **生产环境**请修改默认密码
2. **API密钥**请妥善保管，不要提交到版本控制
3. **防火墙**请根据需要开放相应端口
4. **SSL证书**生产环境建议启用HTTPS

---

📝 **注意**: 本部署配置遵循DEVELOPMENT_GUIDE.md的项目结构规范，所有部署文件统一存放在 `management/deployment/` 目录下。