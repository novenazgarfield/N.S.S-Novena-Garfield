# 🤖 RAG智能问答系统

基于DeepSeek + multilingual-e5 + FAISS的模块化RAG系统，支持多种文档格式的智能问答。

## 🏗️ 系统架构

```
rag-system/
├── config.py                   # 配置管理
├── app.py                      # Streamlit前端
├── run.py                      # 启动脚本
├── requirements.txt            # 依赖列表
├── core/                       # 核心系统
│   └── rag_system.py          #   主要业务逻辑
├── utils/                      # 工具模块
│   └── logger.py              #   日志系统
├── database/                   # 数据库模块
│   └── chat_db.py             #   聊天记录管理
├── memory/                     # 记忆系统
│   └── memory_manager.py      #   记忆管理
├── document/                   # 文档处理
│   └── document_processor.py  #   文档解析器
├── retrieval/                  # 检索系统
│   └── vector_store.py        #   向量存储
└── llm/                        # LLM管理
    └── llm_manager.py         #   模型管理
```

## ✨ 主要功能

### 📚 文档处理
- **多格式支持**: PDF, DOCX, PPTX, Excel, CSV, TXT, HTML, Markdown
- **智能分块**: 自动文本分块，支持重叠处理
- **批量处理**: 支持同时处理多个文档

### 🔍 智能检索
- **向量检索**: 基于FAISS的高效向量搜索
- **语义理解**: 使用multilingual-e5模型进行语义嵌入
- **相似度匹配**: 智能匹配最相关的文档片段

### 🧠 记忆系统
- **永久记忆**: 长期保存重要信息
- **临时记忆**: 按任务分类的会话记忆
- **历史对话**: 基于向量相似度的对话历史检索

### 💬 智能问答
- **上下文理解**: 结合文档内容和历史对话
- **多轮对话**: 支持连续对话和上下文保持
- **任务分类**: 不同任务的独立对话空间

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd /workspace/systems/rag-system

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置模型路径

编辑 `config.py` 文件，修改模型路径：

```python
class ModelConfig:
    # 嵌入模型路径
    EMBEDDING_MODEL_PATH = "/path/to/multilingual-e5-large"
    
    # LLM模型路径  
    LLM_MODEL_PATH = "/path/to/deepseek-llm-7b-chat.Q5_K_M.gguf"
```

### 3. 启动系统

```bash
# 方式1：使用启动脚本
python run.py

# 方式2：直接启动Streamlit
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### 4. 访问界面

打开浏览器访问：http://localhost:8501

## 📁 数据存储结构

系统会在 `../../data/` 目录下创建以下结构：

```
data/
├── raw/rag/
│   └── library/               # 本地文献库
├── processed/rag/
│   ├── memory/               # 记忆文件
│   │   ├── permanent/        # 永久记忆
│   │   └── temporary/        # 临时记忆
│   ├── database/             # 数据库文件
│   └── logs/                 # 日志文件
└── models/rag/
    ├── faiss_index.pkl       # FAISS索引
    └── chunks.pkl            # 文本块
```

## 🔧 配置说明

### 模型配置
- `EMBEDDING_MODEL_PATH`: 嵌入模型路径
- `LLM_MODEL_PATH`: 大语言模型路径
- `LLM_N_CTX`: 上下文窗口大小
- `AUTO_GPU_LAYERS`: 是否自动检测GPU层数

### 文档配置
- `CHUNK_SIZE`: 文本分块大小（默认300词）
- `CHUNK_OVERLAP`: 分块重叠大小（默认50词）
- `MAX_RETRIEVED_CHUNKS`: 最大检索文档数（默认15）

### 系统配置
- `DEBUG`: 调试模式
- `LOG_LEVEL`: 日志级别
- `PAGE_TITLE`: 页面标题

## 🐛 故障排除

### 常见问题

1. **模型加载失败**
   - 检查模型路径是否正确
   - 确认模型文件存在且可读
   - 检查内存是否足够

2. **FAISS索引错误**
   - 删除 `data/models/rag/` 下的索引文件重新构建
   - 检查向量维度是否一致

3. **文档处理失败**
   - 确认文件格式在支持列表中
   - 检查文件是否损坏
   - 查看日志文件获取详细错误信息

4. **内存不足**
   - 减少 `CHUNK_SIZE` 和 `MAX_RETRIEVED_CHUNKS`
   - 使用CPU模式运行
   - 分批处理大量文档

### 日志查看

日志文件位置：`../../data/processed/rag/logs/rag_system.log`

```bash
# 查看最新日志
tail -f ../../data/processed/rag/logs/rag_system.log
```

## 🔄 系统维护

### 清理数据
```python
# 清除特定任务数据
rag_system.clear_task_data("任务名")

# 清空向量索引
rag_system.vector_store.clear_index()
```

### 备份数据
重要数据文件：
- `data/processed/rag/database/chat_logs.db` - 聊天记录
- `data/models/rag/faiss_index.pkl` - 向量索引
- `data/models/rag/chunks.pkl` - 文本块
- `data/processed/rag/memory/` - 记忆文件

## 🤝 开发指南

### 添加新的文档类型
1. 在 `document/document_processor.py` 中添加解析器
2. 更新 `config.py` 中的 `SUPPORTED_EXTENSIONS`
3. 测试新格式的文档处理

### 自定义LLM模型
1. 修改 `llm/llm_manager.py` 中的模型加载逻辑
2. 调整 `config.py` 中的模型配置
3. 更新prompt模板

### 扩展记忆系统
1. 在 `memory/memory_manager.py` 中添加新的记忆类型
2. 更新数据库schema（如需要）
3. 修改前端界面支持新功能

## 📄 许可证

本项目基于MIT许可证开源。

## 🙏 致谢

- [DeepSeek](https://github.com/deepseek-ai) - 大语言模型
- [sentence-transformers](https://github.com/UKPLab/sentence-transformers) - 嵌入模型
- [FAISS](https://github.com/facebookresearch/faiss) - 向量检索
- [Streamlit](https://streamlit.io/) - Web界面框架