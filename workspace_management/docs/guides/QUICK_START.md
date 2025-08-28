# 🚀 RAG系统快速启动指南

## 📋 系统概述

这是一个增强的RAG (Retrieval-Augmented Generation) 智能问答系统，具有完整的连接诊断和错误处理功能。

## ⚡ 快速启动

### 1. 启动RAG服务器
```bash
cd /workspace/N.S.S-Novena-Garfield
python simple_rag_api.py
```

### 2. 启动前端服务器
```bash
python3 -m http.server 52943 --bind 0.0.0.0
```

### 3. 访问系统
打开浏览器访问: `http://localhost:52943/systems/nexus/nexus-dashboard-restored.html`

## 🔍 系统状态检查

### 自动检查工具
```bash
python check_rag_status.py
```

### 手动检查
```bash
# 检查RAG服务器
curl http://localhost:5000/api/health

# 检查前端服务器
curl http://localhost:52943
```

## 🎯 主要功能

### ✅ 连接状态监控
- **实时状态栏**: 页面顶部显示连接状态
- **状态指示器**: 🔄 连接中 | ✅ 已连接 | ❌ 连接失败
- **详细信息**: 鼠标悬停查看详细状态信息

### 🔧 智能错误处理
- **自动诊断**: 识别不同类型的连接错误
- **具体建议**: 根据错误类型提供解决方案
- **一键重连**: 功能菜单中的重新连接按钮

### 📊 系统监控
- **健康检查**: 定期检查系统状态
- **性能监控**: 显示响应时间和成功率
- **历史记录**: 跟踪聊天记录和文档数量

## 🛠️ 故障排除

### 常见问题

#### 问题1: "❌ 连接RAG系统失败"
**解决方案**:
1. 检查RAG服务器是否运行: `ps aux | grep simple_rag_api`
2. 重启RAG服务器: `python simple_rag_api.py`
3. 使用重新连接功能: 点击 ⚡ → 🔄 重新连接

#### 问题2: 页面无法加载
**解决方案**:
1. 检查前端服务器: `curl http://localhost:52943`
2. 重启前端服务器: `python3 -m http.server 52943 --bind 0.0.0.0`
3. 清除浏览器缓存: Ctrl+F5

#### 问题3: 功能异常
**解决方案**:
1. 打开开发者工具 (F12) 查看错误
2. 运行状态检查: `python check_rag_status.py`
3. 查看详细指南: `RAG_CONNECTION_GUIDE.md`

### 诊断工具

#### 1. 状态检查脚本
```bash
python check_rag_status.py
```
- 检查所有系统组件
- 提供详细的诊断信息
- 给出具体的修复建议

#### 2. 连接诊断脚本
```bash
python diagnose_connection.py
```
- 测试所有API端点
- 验证CORS配置
- 检查网络连接

#### 3. 系统状态页面
访问: `http://localhost:52943/system_status.html`
- 实时系统监控
- 可视化状态显示
- 交互式诊断工具

## 📈 系统监控

### 状态指标
- **连接状态**: 实时显示RAG系统连接状态
- **响应时间**: 监控API响应性能
- **成功率**: 跟踪请求成功率
- **资源使用**: 显示内存和存储使用情况

### 日志监控
```bash
# 查看RAG服务器日志
tail -f rag_server.log

# 查看HTTP服务器日志
tail -f http_server.log
```

## 🔒 安全注意事项

### API密钥管理
- 确保OpenAI API密钥安全存储
- 不要在日志中暴露敏感信息
- 定期轮换API密钥

### 网络安全
- 仅在可信网络环境中运行
- 考虑使用HTTPS (生产环境)
- 限制API访问权限

## 📚 进阶功能

### 文档上传
- 支持多种格式: PDF, DOCX, TXT, MD等
- 自动文本提取和向量化
- 智能文档检索

### 记忆管理
- 永久记忆: 长期保存重要信息
- 临时记忆: 会话级别的上下文
- 智能记忆检索

### 多轮对话
- 上下文理解
- 对话历史管理
- 智能回复生成

## 🎉 成功验证

当系统正常工作时，您应该看到:

1. **状态栏显示**: ✅ RAG系统已就绪 (X条历史, Y个文档)
2. **欢迎消息**: 🎉 RAG系统已就绪
3. **功能正常**: 可以发送消息并收到AI回复
4. **文件上传**: 可以上传文档并进行问答

## 📞 获取帮助

### 查看日志
```bash
# 系统状态
python check_rag_status.py

# 详细诊断
python diagnose_connection.py

# 服务器日志
tail -20 rag_server.log
```

### 重置系统
```bash
# 停止所有服务
pkill -f simple_rag_api
pkill -f "python.*server"

# 清除缓存 (可选)
rm -f chat_history.json

# 重新启动
python simple_rag_api.py &
python3 -m http.server 52943 --bind 0.0.0.0 &
```

## 📋 检查清单

启动前请确认:
- [ ] Python环境已配置
- [ ] 依赖包已安装 (`pip install -r requirements.txt`)
- [ ] OpenAI API密钥已设置
- [ ] 端口5000和52943未被占用
- [ ] 防火墙允许本地连接

运行时检查:
- [ ] RAG服务器正在运行
- [ ] 前端服务器可访问
- [ ] 状态栏显示绿色 ✅
- [ ] 可以发送和接收消息
- [ ] 文件上传功能正常

---

**💡 提示**: 如果遇到任何问题，请先运行 `python check_rag_status.py` 进行自动诊断，然后查看 `RAG_CONNECTION_GUIDE.md` 获取详细的解决方案。