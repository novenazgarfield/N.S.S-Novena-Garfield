# NEXUS远程访问配置指南

## 🌟 概述

本指南将帮助您配置NEXUS系统的远程访问功能，实现真正的"多设备协同"和"远程指挥控制"。通过内网穿透技术，您可以在任何地方使用手机、平板或其他设备，安全地连接到您家中或实验室的NEXUS系统。

## 🏗️ 架构原理

```
[手机/平板] ←→ [公网服务器(FRP)] ←→ [本地NEXUS系统]
    远程设备        星际之门           指挥中心
```

### 核心组件

1. **FRP服务端 (frps)** - 部署在有公网IP的云服务器上
2. **FRP客户端 (frpc)** - 运行在您的本地NEXUS系统上
3. **WebSocket隧道** - 实现实时双向通信
4. **安全认证** - 确保只有授权用户可以访问

## 📋 准备工作

### 1. 云服务器要求
- 拥有公网IP地址
- 操作系统：Linux (推荐Ubuntu 20.04+)
- 内存：至少512MB
- 带宽：建议1Mbps以上
- 开放端口：7000 (FRP控制端口), 8080 (Web访问端口), 8765 (WebSocket端口)

### 2. 本地系统要求
- NEXUS系统正常运行
- 网络连接稳定
- 防火墙允许出站连接

## 🚀 配置步骤

### 步骤1：在云服务器上安装FRP服务端

```bash
# 1. 下载FRP
cd /opt
wget https://github.com/fatedier/frp/releases/download/v0.52.3/frp_0.52.3_linux_amd64.tar.gz
tar -xzf frp_0.52.3_linux_amd64.tar.gz
mv frp_0.52.3_linux_amd64 frp
cd frp

# 2. 创建服务端配置文件
cat > frps.ini << EOF
[common]
# FRP服务端监听端口
bind_port = 7000

# Web管理界面
dashboard_port = 7500
dashboard_user = admin
dashboard_pwd = your_secure_password_here

# 认证token (请修改为您自己的密钥)
token = your_secret_token_here

# 日志配置
log_file = ./frps.log
log_level = info
log_max_days = 3
EOF

# 3. 创建systemd服务
cat > /etc/systemd/system/frps.service << EOF
[Unit]
Description=FRP Server
After=network.target

[Service]
Type=simple
User=root
Restart=on-failure
RestartSec=5s
ExecStart=/opt/frp/frps -c /opt/frp/frps.ini

[Install]
WantedBy=multi-user.target
EOF

# 4. 启动服务
systemctl daemon-reload
systemctl enable frps
systemctl start frps

# 5. 检查状态
systemctl status frps
```

### 步骤2：在本地NEXUS系统上安装FRP客户端

```bash
# 1. 下载FRP (在NEXUS系统目录下)
cd /workspace/systems/nexus
wget https://github.com/fatedier/frp/releases/download/v0.52.3/frp_0.52.3_linux_amd64.tar.gz
tar -xzf frp_0.52.3_linux_amd64.tar.gz
mv frp_0.52.3_linux_amd64 frp
cd frp

# 2. 创建客户端配置文件
cat > frpc.ini << EOF
[common]
# 云服务器地址和端口
server_addr = YOUR_SERVER_IP
server_port = 7000

# 认证token (必须与服务端一致)
token = your_secret_token_here

[nexus-web]
type = http
local_ip = 127.0.0.1
local_port = 52308
custom_domains = your-domain.com

[nexus-websocket]
type = tcp
local_ip = 127.0.0.1
local_port = 8765
remote_port = 8765

[nexus-api]
type = http
local_ip = 127.0.0.1
local_port = 8000
subdomain = nexus-api
EOF

# 3. 创建启动脚本
cat > start_frpc.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./frpc -c frpc.ini
EOF

chmod +x start_frpc.sh
```

### 步骤3：配置NEXUS系统环境变量

```bash
# 在NEXUS项目根目录创建.env文件
cat > .env << EOF
# 远程访问配置
VITE_WS_URL=ws://your-domain.com:8765
VITE_API_BASE_URL=https://nexus-api.your-domain.com

# 本地开发配置
VITE_WS_URL_LOCAL=ws://localhost:8765
VITE_API_BASE_URL_LOCAL=http://localhost:8000
EOF
```

### 步骤4：启动完整的NEXUS远程指挥系统

```bash
# 1. 启动WebSocket服务器
cd /workspace/systems/nexus/backend
python websocket_server.py &

# 2. 启动FRP客户端
cd /workspace/systems/nexus/frp
./start_frpc.sh &

# 3. 启动NEXUS前端
cd /workspace/systems/nexus
npm run dev

# 4. 检查所有服务状态
ps aux | grep -E "(websocket_server|frpc|vite)"
```

## 🔒 安全配置

### 1. 防火墙配置

**云服务器防火墙：**
```bash
# Ubuntu/Debian
ufw allow 7000/tcp  # FRP控制端口
ufw allow 8080/tcp  # Web访问端口
ufw allow 8765/tcp  # WebSocket端口
ufw enable

# CentOS/RHEL
firewall-cmd --permanent --add-port=7000/tcp
firewall-cmd --permanent --add-port=8080/tcp
firewall-cmd --permanent --add-port=8765/tcp
firewall-cmd --reload
```

### 2. SSL/TLS加密

```bash
# 使用Let's Encrypt获取免费SSL证书
certbot --nginx -d your-domain.com
```

### 3. 访问控制

在FRP配置中添加IP白名单：
```ini
[nexus-web]
type = http
local_ip = 127.0.0.1
local_port = 52308
custom_domains = your-domain.com
# 只允许特定IP访问
http_user = your_username
http_pwd = your_password
```

## 📱 移动端访问

### 1. 浏览器访问
直接在手机浏览器中访问：`https://your-domain.com`

### 2. PWA安装
NEXUS支持PWA（渐进式Web应用），可以像原生应用一样安装到手机桌面。

### 3. 响应式界面
NEXUS界面完全响应式，自动适配手机、平板等不同屏幕尺寸。

## 🛠️ 故障排除

### 常见问题

1. **连接超时**
   ```bash
   # 检查FRP服务状态
   systemctl status frps  # 服务端
   ps aux | grep frpc     # 客户端
   
   # 检查端口占用
   netstat -tlnp | grep :7000
   ```

2. **WebSocket连接失败**
   ```bash
   # 检查WebSocket服务
   ps aux | grep websocket_server
   
   # 测试本地连接
   curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
        -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" \
        http://localhost:8765
   ```

3. **权限问题**
   ```bash
   # 确保脚本有执行权限
   chmod +x scripts/*.sh
   chmod +x frp/start_frpc.sh
   ```

### 日志查看

```bash
# FRP服务端日志
tail -f /opt/frp/frps.log

# FRP客户端日志
tail -f /workspace/systems/nexus/frp/frpc.log

# WebSocket服务日志
tail -f /workspace/systems/nexus/backend/websocket.log
```

## 🎯 使用场景

### 1. 远程实验监控
在家中启动长时间的基因组分析任务，在实验室用手机实时监控进度。

### 2. 多地协作
团队成员在不同地点，同时连接到同一个NEXUS系统，协同进行数据分析。

### 3. 移动办公
出差时用平板电脑远程启动分子动力学模拟，随时查看结果。

### 4. 紧急响应
系统异常时，立即通过手机远程诊断和处理问题。

## 📊 性能优化

### 1. 带宽优化
```bash
# 在frpc.ini中添加压缩
[common]
server_addr = YOUR_SERVER_IP
server_port = 7000
token = your_secret_token_here

# 启用压缩
use_compression = true
```

### 2. 连接池优化
```bash
# 增加连接池大小
pool_count = 5
```

### 3. 心跳检测
```bash
# 设置心跳间隔
heartbeat_interval = 30
heartbeat_timeout = 90
```

## 🔄 自动化部署

创建一键部署脚本：

```bash
#!/bin/bash
# deploy_remote_access.sh

echo "🚀 部署NEXUS远程访问系统..."

# 检查依赖
command -v python3 >/dev/null 2>&1 || { echo "需要Python3"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "需要Node.js"; exit 1; }

# 启动所有服务
echo "📡 启动WebSocket服务器..."
cd backend && python websocket_server.py &

echo "🌐 启动FRP客户端..."
cd frp && ./start_frpc.sh &

echo "💻 启动前端服务..."
npm run dev &

echo "✅ NEXUS远程指挥中心已启动！"
echo "🔗 本地访问: http://localhost:52308"
echo "🌍 远程访问: https://your-domain.com"
```

## 📞 技术支持

如果在配置过程中遇到问题，请：

1. 查看相关日志文件
2. 检查网络连接和防火墙设置
3. 确认所有端口正确开放
4. 验证配置文件语法正确

---

**🎉 恭喜！您现在拥有了一个真正的"星际指挥中心"！**

无论您身在何处，只要有网络连接，就能随时随地指挥您的NEXUS系统进行各种生物信息学分析任务。这就是现代"星舰工程学"的魅力所在！