# 🚀 NEXUS - 远程指挥与控制系统

一个革命性的远程电源管理和控制系统，让您能够从世界任何地方控制您的电脑！支持远程开机、关机、重启以及完整的生物信息学工作站管理功能。

## ✨ 核心特性

### 🌍 全球远程访问
- **广域网支持**: 突破局域网限制，真正的全球远程控制
- **云服务器中转**: 通过云端中转实现稳定的远程访问
- **多网络管理**: 统一管理家庭、办公室等多个网络环境
- **移动端优化**: 手机、平板完美支持，随时随地控制

### ⚡ 完整电源管理
- **远程唤醒 (WOL)**: Wake-on-LAN技术远程开机
- **远程关机**: 安全关闭远程电脑，支持延迟执行
- **系统重启**: 远程重启功能，维护更便捷
- **跨平台支持**: Windows/Linux/macOS全平台兼容

### 🛡️ 企业级安全
- **令牌认证**: 256位安全令牌保护
- **MAC白名单**: 设备级访问控制
- **操作审计**: 完整的操作日志记录
- **SSL加密**: 数据传输全程加密保护

### 🧬 生物信息学集成
- **基因组分析**: 基因组拼图分析流水线
- **分子模拟**: GROMACS分子动力学模拟
- **蛋白质预测**: AlphaFold蛋白质折叠预测
- **实时监控**: 任务状态实时跟踪

## 🎯 使用场景

### 📱 出差远程办公
```
在酒店用手机:
1. 远程唤醒家里的工作站
2. VPN连接家庭网络  
3. 远程桌面访问电脑
4. 完成工作后远程关机
```

### 💡 智能节能管理
```
每日自动化:
1. 下班时远程关机节省电费
2. 第二天早上远程唤醒
3. 到达办公室时电脑就绪
4. 年节省电费数百元
```

### 🚨 紧急故障处理
```
半夜服务器故障:
1. 收到监控告警
2. 手机远程唤醒备用服务器
3. 5分钟内恢复服务
4. 避免重大业务损失
```

## 🛠️ 技术架构

### 前端技术栈
- **React 18** + **TypeScript**: 现代化前端框架
- **Material-UI**: 精美的用户界面组件
- **WebSocket**: 实时双向通信
- **PWA**: 支持安装为原生应用
- **响应式设计**: 完美适配各种设备

### 后端技术栈
- **Python**: 高性能WebSocket服务器
- **Wake-on-LAN**: 标准WOL协议实现
- **跨平台命令**: 支持多操作系统
- **云端中转**: 突破网络限制
- **安全认证**: 多层安全防护

## 🚀 快速开始

### 环境要求
- Node.js 18+
- Python 3.8+
- 现代浏览器

### 一键启动
```bash
# 克隆项目
git clone https://github.com/novenazgarfield/research-workstation.git
cd research-workstation/systems/nexus

# 安装依赖
npm install

# 启动系统
npm run dev

# 启动后端服务
cd backend && python3 websocket_server.py
```

### 访问系统
- **主界面**: http://localhost:5173
- **测试页面**: http://localhost:52333/test_remote_center.html
- **WebSocket**: ws://localhost:8765

## 📱 移动端使用

### PWA安装
1. 手机浏览器访问NEXUS系统
2. 点击"添加到主屏幕"
3. 创建桌面图标
4. 像原生App一样使用

### 移动端功能
- ✅ 触摸友好的大按钮设计
- ✅ 响应式布局完美适配
- ✅ 离线缓存支持
- ✅ 推送通知提醒

## 🌐 广域网部署

### 方案1: 云服务器中转（推荐）
```bash
# 部署到云服务器
scp cloud_wol_relay.py user@your-server:/opt/nexus/
ssh user@your-server "cd /opt/nexus && python3 cloud_wol_relay.py"

# 配置网络信息
vim wol_networks.json
```

### 方案2: FRP内网穿透
```ini
# frpc.ini
[nexus_ws]
type = tcp
local_port = 8765
remote_port = 8765
```

### 方案3: VPN访问
```bash
# WireGuard配置
[Interface]
PrivateKey = YOUR_PRIVATE_KEY
Address = 10.0.0.2/24
```

## 🔧 配置指南

### Wake-on-LAN设置
```bash
# Linux启用WOL
sudo ethtool -s eth0 wol g

# Windows设备管理器
# 网络适配器 → 属性 → 电源管理 → 允许此设备唤醒计算机

# macOS系统偏好设置
# 节能 → 网络访问唤醒
```

### 安全配置
```json
{
  "networks": [
    {
      "name": "home_network",
      "broadcast_ip": "192.168.1.255",
      "auth_token": "your_secure_token_here",
      "allowed_macs": ["00:1B:21:3A:4C:5D"]
    }
  ]
}
```

## 📊 功能对比

| 功能 | 传统方案 | NEXUS系统 |
|------|----------|-----------|
| **访问范围** | 仅局域网 | 全球访问 |
| **电源控制** | 仅开机 | 开机+关机+重启 |
| **设备支持** | 仅电脑 | 电脑+手机+平板 |
| **安全性** | 基础 | 企业级 |
| **易用性** | 命令行 | 图形化一键操作 |

## 🎮 操作演示

### 远程唤醒
```
1. 点击绿色🌅"远程唤醒电脑"按钮
2. 输入MAC地址: 00:1B:21:3A:4C:5D
3. 选择网络: 家庭网络
4. 点击"发送唤醒信号"
5. 等待30-60秒电脑启动
```

### 远程关机
```
1. 点击红色🔴"远程关机/重启"按钮
2. 选择操作类型: 正常关机
3. 设置延迟时间: 60秒
4. 输入关机消息: "NEXUS远程关机"
5. 确认执行
```

## 📚 完整文档

- 📖 [Wake-on-LAN使用指南](WAKE_ON_LAN_GUIDE.md)
- 🌐 [广域网远程访问指南](WAN_REMOTE_ACCESS_GUIDE.md)
- 🔧 [远程访问配置指南](REMOTE_ACCESS_GUIDE.md)
- 🎉 [功能完成报告](POWER_MANAGEMENT_COMPLETE.md)

## 🚨 故障排除

### 常见问题
| 问题 | 解决方案 |
|------|----------|
| 连接超时 | 检查防火墙，开放8765端口 |
| 唤醒失败 | 检查BIOS WOL设置 |
| 关机失败 | 使用管理员权限运行 |
| 认证失败 | 检查令牌配置 |

### 调试工具
```bash
# 网络连通性测试
ping 192.168.1.255

# WOL包测试
wakeonlan -i 192.168.1.255 00:1B:21:3A:4C:5D

# 服务状态检查
netstat -tlnp | grep 8765
```

## 🎯 未来规划

### 短期计划
- [ ] 设备管理界面
- [ ] 批量操作功能
- [ ] 定时任务支持
- [ ] 状态监控优化

### 中期计划
- [ ] AI智能管理
- [ ] 语音控制支持
- [ ] IoT设备集成
- [ ] 企业版功能

### 长期计划
- [ ] 云端设备管理
- [ ] 原生移动应用
- [ ] 开放API接口
- [ ] 商业化产品

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 开源许可

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- 🏠 **项目主页**: [GitHub Repository](https://github.com/novenazgarfield/research-workstation)
- 🐛 **问题反馈**: [Issues](https://github.com/novenazgarfield/research-workstation/issues)
- 💬 **讨论交流**: [Discussions](https://github.com/novenazgarfield/research-workstation/discussions)
- 📧 **邮箱联系**: novenazgarfield@example.com

## 🌟 Star History

如果这个项目对您有帮助，请给我们一个 ⭐ Star！

[![Star History Chart](https://api.star-history.com/svg?repos=novenazgarfield/research-workstation&type=Date)](https://star-history.com/#novenazgarfield/research-workstation&Date)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！特别感谢：

- Wake-on-LAN 技术社区
- React 和 Material-UI 团队
- Python WebSocket 生态系统
- 所有测试用户和反馈者

---

**让NEXUS成为您的远程控制利器！从此告别距离限制，享受真正的远程自由！** 🚀✨