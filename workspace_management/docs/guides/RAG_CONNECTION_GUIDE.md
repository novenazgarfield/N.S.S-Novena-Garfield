# 🔧 RAG系统连接问题解决指南

## 📋 问题概述

如果您看到"❌ 连接RAG系统失败，请确保后端服务正在运行"的错误消息，请按照以下步骤进行排查和解决。

## 🔍 快速诊断

### 1. 检查连接状态栏
页面顶部有一个连接状态栏，显示当前RAG系统的连接状态：
- 🔄 **正在连接**: 系统正在尝试连接RAG服务器
- ✅ **已连接**: RAG系统工作正常，显示历史记录和文档数量
- ❌ **连接失败**: 无法连接到RAG服务器
- ⚠️ **连接异常**: 连接不稳定或部分功能不可用

### 2. 使用重新连接功能
1. 点击聊天界面右下角的 ⚡ 功能按钮
2. 选择 🔄 **重新连接**
3. 系统会自动重新测试RAG连接

## 🛠️ 详细排查步骤

### 步骤1: 检查RAG服务器状态

```bash
# 检查RAG服务器是否运行
ps aux | grep simple_rag_api

# 检查端口5000是否被占用
curl http://localhost:5000/api/health
```

**预期结果**: 应该看到JSON响应，包含`"status": "ok"`

### 步骤2: 启动RAG服务器

如果服务器没有运行，请启动它：

```bash
cd /workspace/N.S.S-Novena-Garfield
python simple_rag_api.py
```

**预期输出**:
```
🚀 RAG API服务器启动成功！
📊 聊天历史已加载: X 条记录
* Running on http://127.0.0.1:5000
```

### 步骤3: 检查网络连接

在浏览器开发者工具中检查网络请求：

1. 按 F12 打开开发者工具
2. 切换到 Network 标签
3. 刷新页面或发送消息
4. 查看是否有失败的请求到 `localhost:5000`

### 步骤4: 检查CORS配置

确认RAG服务器的CORS配置正确：

```bash
# 测试CORS预检请求
curl -H "Origin: http://localhost:52943" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS http://localhost:5000/api/chat -v
```

**预期结果**: 应该看到 `Access-Control-Allow-Origin: http://localhost:52943`

## 🔧 常见问题解决方案

### 问题1: 端口冲突
**症状**: 服务器启动失败，提示端口被占用
**解决方案**:
```bash
# 查找占用端口5000的进程
lsof -i :5000
# 或者使用其他端口启动
python simple_rag_api.py --port 5001
```

### 问题2: 防火墙阻止
**症状**: 连接超时或网络错误
**解决方案**:
- 检查系统防火墙设置
- 确认localhost访问没有被阻止
- 尝试使用127.0.0.1替代localhost

### 问题3: 浏览器缓存问题
**症状**: 页面显示旧的错误信息
**解决方案**:
- 按 Ctrl+F5 强制刷新页面
- 清除浏览器缓存
- 使用无痕模式测试

### 问题4: JavaScript错误
**症状**: 页面功能异常，控制台有错误
**解决方案**:
1. 打开浏览器开发者工具 (F12)
2. 查看Console标签中的错误信息
3. 刷新页面重新加载JavaScript

## 📊 系统状态检查工具

### 使用内置诊断工具

访问系统状态页面进行全面检查：
```
http://localhost:52943/system_status.html
```

### 使用Python诊断脚本

运行自动诊断脚本：
```bash
cd /workspace/N.S.S-Novena-Garfield
python diagnose_connection.py
```

## 🎯 最佳实践

### 1. 定期检查系统状态
- 使用功能菜单中的"存储状态"查看系统信息
- 定期点击"重新连接"确保连接稳定

### 2. 监控错误日志
```bash
# 查看RAG服务器日志
tail -f /workspace/N.S.S-Novena-Garfield/rag_server.log
```

### 3. 备份重要数据
- 聊天记录自动保存到 `chat_history.json`
- 定期备份重要文档和配置

## 🚨 紧急恢复步骤

如果系统完全无法连接，请按以下步骤恢复：

### 1. 完全重启服务
```bash
# 停止所有相关进程
pkill -f simple_rag_api
pkill -f "python.*server"

# 重新启动RAG服务器
cd /workspace/N.S.S-Novena-Garfield
python simple_rag_api.py > rag_server.log 2>&1 &

# 重新启动HTTP服务器
python3 -m http.server 52943 --bind 0.0.0.0 > http_server.log 2>&1 &
```

### 2. 清除缓存和重置
```bash
# 清除聊天历史（如果需要）
rm -f chat_history.json

# 重新启动服务
python simple_rag_api.py
```

### 3. 验证恢复
1. 访问 `http://localhost:52943/systems/nexus/nexus-dashboard-restored.html`
2. 检查顶部状态栏是否显示 ✅ **已连接**
3. 发送测试消息验证功能

## 📞 获取帮助

### 查看详细错误信息
1. 打开浏览器开发者工具 (F12)
2. 查看Console标签中的错误详情
3. 查看Network标签中的失败请求

### 收集诊断信息
运行以下命令收集系统信息：
```bash
# 系统状态
curl -s http://localhost:5000/api/health | jq .

# 服务器进程
ps aux | grep -E "(simple_rag_api|python.*server)"

# 端口状态
netstat -tlnp 2>/dev/null | grep -E ":5000|:52943" || echo "netstat不可用"

# 最近的错误日志
tail -20 rag_server.log 2>/dev/null || echo "日志文件不存在"
```

## ✅ 验证清单

在报告问题之前，请确认已完成以下检查：

- [ ] RAG服务器正在运行 (`ps aux | grep simple_rag_api`)
- [ ] 端口5000可以访问 (`curl http://localhost:5000/api/health`)
- [ ] 浏览器控制台没有JavaScript错误
- [ ] 网络请求没有被阻止（检查Network标签）
- [ ] 已尝试重新连接功能
- [ ] 已尝试刷新页面
- [ ] 状态栏显示具体的错误信息

## 🎉 成功标志

当系统正常工作时，您应该看到：

1. **状态栏**: ✅ RAG系统已就绪 (X条历史, Y个文档)
2. **欢迎消息**: 🎉 RAG系统已就绪
3. **功能正常**: 可以发送消息并收到回复
4. **存储状态**: 显示正确的消息数量和存储大小

---

**💡 提示**: 大多数连接问题都可以通过重启RAG服务器和刷新页面来解决。如果问题持续存在，请检查系统日志获取更多详细信息。