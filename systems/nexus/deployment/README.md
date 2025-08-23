# 🚀 NEXUS Research Workstation 部署指南

## 📋 概述

NEXUS Research Workstation 提供多种部署方案，满足不同用户的需求：

1. **🎯 专业安装包** - 适合最终用户的图形化安装体验
2. **⚡ 一键部署脚本** - 适合开发者的快速部署方案
3. **🔧 手动部署** - 适合高级用户的自定义部署

---

## 🎯 方案一：专业安装包 (推荐)

### 特性
- ✅ 跨平台支持 (Windows/macOS/Linux)
- ✅ 图形化安装界面
- ✅ 用户自定义安装路径
- ✅ 自动依赖检查和安装
- ✅ 桌面快捷方式和开始菜单
- ✅ 自动更新检查

### 下载安装包

访问 [官方门户网站](../landing_page/index.html) 或 [GitHub Releases](https://github.com/novenazgarfield/research-workstation/releases) 下载对应平台的安装包：

| 平台 | 文件格式 | 大小 | 说明 |
|------|----------|------|------|
| Windows | `.exe` | ~150MB | NSIS安装包，支持自定义路径 |
| macOS | `.dmg` | ~160MB | DMG磁盘映像，支持Intel和Apple Silicon |
| Linux | `.AppImage` | ~140MB | 免安装可执行文件 |
| Linux | `.deb` | ~140MB | Debian/Ubuntu软件包 |

### 安装步骤

#### Windows
1. 下载 `NEXUS-Setup.exe`
2. 右键选择"以管理员身份运行"
3. 按照安装向导提示操作
4. 选择安装路径（可自定义）
5. 等待安装完成
6. 从桌面或开始菜单启动NEXUS

#### macOS
1. 下载 `NEXUS-Research-Workstation.dmg`
2. 双击打开DMG文件
3. 将NEXUS拖拽到Applications文件夹
4. 从Launchpad或Applications启动NEXUS
5. 首次运行可能需要在"安全性与隐私"中允许

#### Linux
1. 下载 `.AppImage` 或 `.deb` 文件
2. **AppImage方式**：
   ```bash
   chmod +x NEXUS-Research-Workstation.AppImage
   ./NEXUS-Research-Workstation.AppImage
   ```
3. **DEB方式**：
   ```bash
   sudo dpkg -i nexus-research-workstation.deb
   sudo apt-get install -f  # 解决依赖问题
   ```

---

## ⚡ 方案二：一键部署脚本 (开发者推荐)

### 特性
- ✅ 完全自动化部署
- ✅ 智能依赖检查和安装
- ✅ 支持私有仓库访问
- ✅ 用户交互式配置
- ✅ 跨平台脚本支持

### Windows PowerShell 部署

```powershell
# 下载并运行部署脚本
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/novenazgarfield/research-workstation/main/systems/nexus/deployment/deploy_nexus.ps1" -OutFile "deploy_nexus.ps1"

# 交互式安装
.\deploy_nexus.ps1

# 或指定参数安装
.\deploy_nexus.ps1 -InstallPath "D:\NEXUS" -GitHubToken "ghp_xxxx"

# 静默安装
.\deploy_nexus.ps1 -Silent
```

### Linux/macOS Bash 部署

```bash
# 下载并运行部署脚本
curl -fsSL https://raw.githubusercontent.com/novenazgarfield/research-workstation/main/systems/nexus/deployment/deploy_nexus.sh -o deploy_nexus.sh
chmod +x deploy_nexus.sh

# 交互式安装
./deploy_nexus.sh

# 或指定参数安装
./deploy_nexus.sh --path "/opt/nexus" --token "ghp_xxxx"

# 静默安装
./deploy_nexus.sh --silent
```

### 脚本参数说明

#### Windows PowerShell
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-InstallPath` | 安装路径 | `C:\NEXUS` |
| `-GitHubToken` | GitHub访问令牌 | 无 |
| `-Silent` | 静默模式 | `false` |
| `-Help` | 显示帮助 | `false` |

#### Linux/macOS Bash
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-p, --path` | 安装路径 | `~/nexus` |
| `-t, --token` | GitHub访问令牌 | 无 |
| `-s, --silent` | 静默模式 | `false` |
| `-h, --help` | 显示帮助 | `false` |

---

## 🔧 方案三：手动部署

### 系统要求

#### 基础要求
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **内存**: 4GB+ (推荐8GB+)
- **存储**: 2GB+ 可用空间
- **网络**: 稳定的互联网连接

#### 依赖项
- **Git**: 2.0+
- **Node.js**: 16.0+
- **Python**: 3.8+
- **npm**: 8.0+
- **pip**: 20.0+

### 手动安装步骤

#### 1. 克隆代码库
```bash
git clone https://github.com/novenazgarfield/research-workstation.git
cd research-workstation/systems/nexus
```

#### 2. 安装Node.js依赖
```bash
npm install
```

#### 3. 安装Python依赖
```bash
pip install -r backend/requirements.txt
```

#### 4. 启动服务

**方式一：分别启动**
```bash
# 终端1：启动后端WebSocket服务器
cd backend
python websocket_server.py

# 终端2：启动前端开发服务器
npm run dev
```

**方式二：使用启动脚本**
```bash
# Windows
.\scripts\start.bat

# Linux/macOS
./scripts/start.sh
```

#### 5. 访问应用
- 主界面: http://localhost:5173
- 测试页面: http://localhost:52333/test_remote_center.html
- WebSocket: ws://localhost:8765

---

## 🌐 部署到生产环境

### Docker 部署

```bash
# 构建镜像
docker build -t nexus-research-workstation .

# 运行容器
docker run -d \
  --name nexus \
  -p 5173:5173 \
  -p 8765:8765 \
  -p 52333:52333 \
  nexus-research-workstation
```

### 云服务器部署

#### 1. 准备服务器
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y git nodejs npm python3 python3-pip nginx
```

#### 2. 克隆和配置
```bash
# 克隆代码
git clone https://github.com/novenazgarfield/research-workstation.git
cd research-workstation/systems/nexus

# 安装依赖
npm install
pip3 install -r backend/requirements.txt

# 构建生产版本
npm run build
```

#### 3. 配置Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    location /ws {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

#### 4. 配置系统服务
```bash
# 创建systemd服务文件
sudo tee /etc/systemd/system/nexus.service > /dev/null <<EOF
[Unit]
Description=NEXUS Research Workstation
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/nexus
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
sudo systemctl enable nexus
sudo systemctl start nexus
```

---

## 🔍 故障排除

### 常见问题

#### 1. 端口冲突
**问题**: 端口5173、8765或52333被占用
**解决**: 
```bash
# 查找占用端口的进程
netstat -tulpn | grep :5173
# 或
lsof -i :5173

# 终止进程
kill -9 <PID>
```

#### 2. 依赖安装失败
**问题**: npm install 或 pip install 失败
**解决**:
```bash
# 清除npm缓存
npm cache clean --force

# 使用国内镜像
npm config set registry https://registry.npmmirror.com/
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 3. WebSocket连接失败
**问题**: 前端无法连接到WebSocket服务器
**解决**:
- 检查防火墙设置
- 确认WebSocket服务器正在运行
- 检查端口8765是否开放

#### 4. 权限问题
**问题**: 文件权限不足或需要管理员权限
**解决**:
```bash
# Linux/macOS
sudo chown -R $USER:$USER /path/to/nexus
chmod +x scripts/*.sh

# Windows (以管理员身份运行PowerShell)
icacls "C:\NEXUS" /grant Users:F /T
```

### 日志查看

#### 应用日志
```bash
# 前端日志
npm run dev  # 直接在终端查看

# 后端日志
cd backend
python websocket_server.py  # 直接在终端查看
```

#### 系统日志
```bash
# Linux
journalctl -u nexus -f

# macOS
tail -f /var/log/system.log | grep nexus

# Windows
Get-EventLog -LogName Application -Source "NEXUS" -Newest 50
```

---

## 📞 技术支持

### 获取帮助
- **GitHub Issues**: [提交问题](https://github.com/novenazgarfield/research-workstation/issues)
- **讨论区**: [GitHub Discussions](https://github.com/novenazgarfield/research-workstation/discussions)
- **文档**: [项目文档](../README.md)

### 贡献代码
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 发起 Pull Request

---

## 📄 许可证

本项目采用 [MIT License](../../../LICENSE) 开源协议。

---

<div align="center">

**🎉 感谢使用 NEXUS Research Workstation！**

让远程控制变得简单而强大 🚀

</div>