# NEXUS + RAG 系统集成指南

## 📋 概述

本文档介绍如何将你的RAG系统与NEXUS仪表板前端进行集成，实现完整的文档问答功能。

## 🏗️ 系统架构

```
┌─────────────────┐    HTTP请求    ┌─────────────────┐
│   NEXUS前端     │ ──────────────→ │   RAG API服务器  │
│  (HTML/JS)      │                │   (Flask)       │
└─────────────────┘                └─────────────────┘
                                           │
                                           ▼
                                   ┌─────────────────┐
                                   │   RAG核心系统    │
                                   │  (Python)       │
                                   └─────────────────┘
```

## 🔧 集成组件

### 1. 前端修改 (`nexus-dashboard-restored.html`)
- ✅ **异步聊天功能**: `sendMessage()` 连接RAG API
- ✅ **文件上传功能**: `uploadFile()` 支持多文件上传到RAG系统
- ✅ **聊天记录清空**: `clearChat()` 清空RAG系统数据
- ✅ **加载状态显示**: 显示处理进度和错误信息

### 2. RAG API服务器 (`api_server.py`)
- ✅ **聊天接口**: `POST /api/chat` - 处理用户问题
- ✅ **文档上传**: `POST /api/upload` - 上传并处理文档
- ✅ **聊天历史**: `GET /api/history` - 获取聊天记录
- ✅ **清空数据**: `POST /api/clear` - 清空聊天记录
- ✅ **系统状态**: `GET /api/health` - 健康检查
- ✅ **跨域支持**: CORS配置允许前端访问

### 3. 启动脚本 (`start_nexus_with_rag.py`)
- ✅ **一键启动**: 同时启动前端和RAG服务
- ✅ **进程管理**: 自动管理多个服务进程
- ✅ **优雅关闭**: Ctrl+C安全停止所有服务

## 🚀 快速开始

### 1. 安装依赖
```bash
cd /workspace/N.S.S-Novena-Garfield/systems/rag-system
pip install -r requirements.txt
```

### 2. 启动集成系统
```bash
cd /workspace/N.S.S-Novena-Garfield
python start_nexus_with_rag.py
```

### 3. 访问系统
- 🌐 **前端界面**: http://localhost:52943/systems/nexus/nexus-dashboard-restored.html
- 🤖 **RAG API**: http://localhost:5000
- 📊 **健康检查**: http://localhost:5000/api/health

## 🧪 测试集成

运行集成测试：
```bash
cd /workspace/N.S.S-Novena-Garfield
python test_rag_integration.py
```

## 📡 API接口详情

### 聊天接口
```http
POST /api/chat
Content-Type: application/json

{
    "message": "用户问题",
    "task_name": "nexus_chat"
}
```

**响应**:
```json
{
    "success": true,
    "response": "AI回答",
    "timestamp": "2025-08-26T11:20:00"
}
```

### 文档上传接口
```http
POST /api/upload
Content-Type: multipart/form-data

files: [文件1, 文件2, ...]
```

**响应**:
```json
{
    "success": true,
    "message": "成功处理 2 个文档",
    "processed_count": 2,
    "total_chunks": 150,
    "total_vectors": 150
}
```

### 清空聊天接口
```http
POST /api/clear
Content-Type: application/json

{
    "task_name": "nexus_chat"
}
```

## 🎯 功能特性

### 前端功能
- ✅ **智能聊天**: 与RAG系统实时对话
- ✅ **文件上传**: 支持PDF、Word、图片等多种格式
- ✅ **多文件处理**: 一次上传多个文档
- ✅ **状态反馈**: 实时显示处理状态和错误信息
- ✅ **聊天记录**: 保持对话上下文
- ✅ **一键清空**: 清空聊天记录和RAG数据

### RAG系统功能
- ✅ **文档理解**: 支持多种文档格式解析
- ✅ **向量检索**: 基于语义相似度的文档检索
- ✅ **上下文记忆**: 保持对话上下文和历史记录
- ✅ **智能回答**: 基于文档内容生成准确回答

## 🔧 配置说明

### 端口配置
- **前端服务器**: 52943 (HTTP)
- **RAG API服务器**: 5000 (Flask)

### 数据存储
- **RAG数据目录**: `/workspace/N.S.S-Novena-Garfield/data/processed/rag/`
- **聊天记录**: SQLite数据库
- **向量存储**: FAISS索引
- **临时文件**: `/workspace/N.S.S-Novena-Garfield/data/raw/rag/temp_uploads/`

## 🐛 故障排除

### 常见问题

1. **RAG系统初始化失败**
   - 检查依赖是否完整安装
   - 确认Python路径配置正确

2. **API连接失败**
   - 确认RAG API服务器正在运行 (端口5000)
   - 检查防火墙设置

3. **文件上传失败**
   - 检查文件格式是否支持
   - 确认磁盘空间充足

4. **聊天无响应**
   - 检查RAG系统日志
   - 确认模型文件存在

### 调试命令

```bash
# 检查API服务器状态
curl http://localhost:5000/api/health

# 测试聊天功能
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "task_name": "test"}'

# 查看RAG系统日志
tail -f /workspace/N.S.S-Novena-Garfield/systems/rag-system/logs/rag_system.log
```

## 📈 性能优化

### 建议配置
- **内存**: 建议8GB以上
- **存储**: SSD硬盘提升文档处理速度
- **网络**: 稳定的网络连接用于模型下载

### 优化选项
- 使用GPU加速向量计算 (安装faiss-gpu)
- 调整向量维度和检索参数
- 启用文档缓存机制

## 🔄 更新日志

### v1.0.0 (2025-08-26)
- ✅ 完成NEXUS前端与RAG系统集成
- ✅ 实现完整的API接口
- ✅ 添加文件上传和处理功能
- ✅ 支持多文件批量上传
- ✅ 实现聊天记录管理
- ✅ 添加错误处理和状态反馈

## 📞 技术支持

如有问题，请检查：
1. 系统日志文件
2. API响应状态
3. 网络连接状态
4. 依赖包版本

---

🎉 **恭喜！你的RAG系统已成功集成到NEXUS仪表板中！**