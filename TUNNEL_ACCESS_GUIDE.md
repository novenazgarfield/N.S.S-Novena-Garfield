# 🌐 隧道访问解决方案

## 📋 问题描述

当您通过 Cloudflare 隧道访问前端页面时（如 `https://xxx.trycloudflare.com`），会遇到RAG系统连接失败的问题。这是因为：

1. **跨域问题**: 前端通过HTTPS访问，但RAG服务器在本地HTTP
2. **网络隔离**: 隧道只暴露了前端服务，RAG服务器仍在本地
3. **协议不匹配**: HTTPS页面无法访问HTTP API

## 🚀 解决方案

### 方案1: 使用统一启动脚本 (推荐)

```bash
cd /workspace/N.S.S-Novena-Garfield
python start_with_tunnel.py
```

这个脚本会：
- ✅ 启动RAG API服务器 (端口5000)
- ✅ 启动HTTP服务器 (端口52943)  
- ✅ 自动创建隧道暴露两个服务
- ✅ 前端自动检测并连接到正确的RAG服务器

### 方案2: 手动启动隧道

#### 步骤1: 启动服务器
```bash
# 终端1: 启动RAG服务器
python simple_rag_api.py --host 0.0.0.0 --port 5000

# 终端2: 启动HTTP服务器
python3 -m http.server 52943 --bind 0.0.0.0
```

#### 步骤2: 创建隧道
```bash
# 终端3: RAG API隧道
cloudflared tunnel --url http://localhost:5000

# 终端4: 前端隧道
cloudflared tunnel --url http://localhost:52943
```

#### 步骤3: 访问系统
访问前端隧道URL，系统会自动尝试连接RAG API隧道。

### 方案3: 本地访问 (最简单)

如果不需要远程访问，直接使用本地地址：

```bash
# 启动服务器
python simple_rag_api.py
python3 -m http.server 52943 --bind 0.0.0.0

# 访问本地地址
http://localhost:52943/systems/nexus/nexus-dashboard-restored.html
```

## 🔧 系统特性

### 智能连接检测
系统会自动尝试以下地址：
1. 当前域名的5000端口 (隧道环境)
2. `http://localhost:5000` (本地环境)
3. `http://127.0.0.1:5000` (备用本地地址)

### 可视化状态监控
- 🔄 **连接中**: 黄色状态框，显示尝试进度
- ✅ **已连接**: 绿色状态框，3秒后自动隐藏
- ❌ **连接失败**: 红色状态框，需手动关闭

### 错误处理
- 详细的错误信息和解决建议
- 自动重试机制
- 一键重新连接功能

## 📊 状态检查

### 查看连接状态
右上角会显示悬浮状态框，包含：
- 连接状态指示器
- 详细错误信息
- 服务器地址信息
- 故障排除建议

### 手动重新连接
1. 点击聊天界面的 ⚡ 功能按钮
2. 选择 🔄 **重新连接**
3. 系统会重新测试所有可能的服务器地址

### 调试信息
打开浏览器开发者工具 (F12)，查看Console标签：
- 连接尝试日志
- 成功/失败的URL
- 详细错误信息

## 🎯 最佳实践

### 开发环境
```bash
# 本地开发，使用localhost
python simple_rag_api.py
python3 -m http.server 52943
```

### 演示环境
```bash
# 需要远程访问，使用隧道
python start_with_tunnel.py
```

### 生产环境
```bash
# 使用反向代理 (nginx/apache)
# 配置HTTPS和域名
# 设置防火墙规则
```

## 🔍 故障排除

### 问题1: 状态框显示"连接失败"
**原因**: RAG服务器未启动或端口被占用
**解决**: 
```bash
# 检查RAG服务器
ps aux | grep simple_rag_api
# 重启服务器
python simple_rag_api.py
```

### 问题2: 隧道无法创建
**原因**: cloudflared未安装或网络问题
**解决**:
```bash
# 安装cloudflared
# 或使用本地访问方案
```

### 问题3: 跨域错误
**原因**: CORS配置问题
**解决**: RAG服务器已配置CORS，确保服务器正常启动

### 问题4: 连接超时
**原因**: 网络延迟或服务器响应慢
**解决**: 
- 检查网络连接
- 重启RAG服务器
- 使用重新连接功能

## 📈 监控和日志

### 实时监控
访问系统状态页面：
```
http://localhost:52943/system_status.html
```

### 自动检查
运行状态检查脚本：
```bash
python check_rag_status.py
```

### 日志查看
```bash
# 查看服务器日志
tail -f rag_server.log

# 查看连接诊断
python diagnose_connection.py
```

## 💡 提示

1. **首次访问**: 系统会自动测试连接，请等待状态框显示结果
2. **网络切换**: 从隧道切换到本地访问时，点击重新连接
3. **错误持续**: 如果问题持续存在，查看浏览器控制台获取详细信息
4. **性能优化**: 本地访问速度最快，隧道访问会有一定延迟

---

**🎉 现在您可以通过任何方式访问RAG系统，系统会自动处理连接问题！**