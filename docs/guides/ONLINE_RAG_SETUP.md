# 🤖 在线RAG系统设置指南

## 🎯 概述
这是一个基于Gemini AI的在线RAG系统，无需本地部署大模型，只需要Google的API密钥即可使用。

## 🔑 获取Gemini API密钥

### 步骤1: 访问Google AI Studio
1. 打开浏览器，访问: https://makersuite.google.com/app/apikey
2. 使用您的Google账号登录

### 步骤2: 创建API密钥
1. 点击 "Create API Key" 按钮
2. 选择一个Google Cloud项目（或创建新项目）
3. 复制生成的API密钥

### 步骤3: 配置API密钥
编辑文件 `/workspace/N.S.S-Novena-Garfield/online_rag_api.py`，找到这一行：
```python
GEMINI_API_KEY = "AIzaSyBJmXRJmXRJmXRJmXRJmXRJmXRJmXRJmXR"  # 请替换为您的实际API密钥
```

将引号中的内容替换为您的真实API密钥。

## 🚀 启动系统

### 自动启动（推荐）
```bash
cd /workspace/N.S.S-Novena-Garfield
python online_rag_api.py
```

### 手动启动
```bash
# 1. 启动RAG API服务器
cd /workspace/N.S.S-Novena-Garfield
python online_rag_api.py &

# 2. 启动前端服务器
cd /workspace/N.S.S-Novena-Garfield/systems/nexus
python -m http.server 52943 &

# 3. 创建隧道（如果需要）
cloudflared tunnel --url http://localhost:5000 &
cloudflared tunnel --url http://localhost:52943 &
```

## 🌐 访问地址

### 当前可用地址
- **前端界面**: https://preview-gamma-believed-leader.trycloudflare.com
- **RAG API**: https://webmasters-soup-pack-safer.trycloudflare.com

### 本地地址
- **前端界面**: http://localhost:52943
- **RAG API**: http://localhost:5000

## 🔧 API端点说明

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/chat` | POST | 智能对话 |
| `/api/upload` | POST | 文档上传 |
| `/api/history` | GET | 聊天历史 |
| `/api/clear` | POST | 清空记录 |
| `/api/stats` | GET | 系统统计 |

## 💬 使用示例

### 测试聊天功能
```bash
curl -X POST https://webmasters-soup-pack-safer.trycloudflare.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，请介绍一下自己"}'
```

### 检查系统状态
```bash
curl https://webmasters-soup-pack-safer.trycloudflare.com/api/health
```

## 🎨 功能特点

### ✅ 优势
- **无需本地部署**: 使用Google Gemini云服务
- **高质量回答**: 基于最新的Gemini 2.0 Flash模型
- **中文支持**: 完美支持中文对话
- **快速响应**: 云端处理，响应迅速
- **易于配置**: 只需要一个API密钥

### 🔧 技术架构
```
用户浏览器 → Cloudflare隧道 → Nexus前端 → RAG API → Gemini AI
```

## 🛠️ 故障排除

### 问题1: API密钥错误
**症状**: 聊天功能返回错误
**解决**: 检查API密钥是否正确配置

### 问题2: 服务无法访问
**症状**: 前端显示"API端点不存在"
**解决**: 确保RAG API服务器正在运行

### 问题3: 隧道连接失败
**症状**: 隧道地址无法访问
**解决**: 重新启动cloudflared隧道

## 📞 支持

如果遇到问题，请检查：
1. Gemini API密钥是否有效
2. 网络连接是否正常
3. 服务进程是否在运行
4. 隧道是否正常工作

## 🔄 重启服务

如果需要重启整个系统：
```bash
# 停止所有服务
pkill -f "online_rag_api"
pkill -f "http.server.*52943"
pkill -f "cloudflared"

# 重新启动
cd /workspace/N.S.S-Novena-Garfield
python online_rag_api.py &
cd systems/nexus && python -m http.server 52943 &
cloudflared tunnel --url http://localhost:5000 &
cloudflared tunnel --url http://localhost:52943 &
```

---

🎉 **现在您可以享受完全在线的RAG智能问答服务了！**