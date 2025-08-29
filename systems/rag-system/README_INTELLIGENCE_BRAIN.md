# 🧠 中央情报大脑 (Central Intelligence Brain)

> 基于"大宪章"构建的新一代RAG系统 - 版本 2.0.0 "Genesis"

## 🌟 项目简介

中央情报大脑是一个革命性的RAG（检索增强生成）系统，基于"大宪章"的指导原则构建，实现了从传统"信息检索工具"到真正"中央情报大脑"的颠覆性升级。

### 🎯 核心特性

- **🔄 三位一体智能分块**: 句子-段落-文档的三层语义感知分块
- **💾 永恒归档系统**: 一次处理，永久使用的知识管理模式
- **🏷️ 身份铭牌机制**: 每个知识原子的完整溯源信息
- **🧠 深度理解能力**: 基于先进AI技术的语义理解
- **🔧 精准控制功能**: 细粒度的知识管理和控制
- **🛠️ 自我修复机制**: 自动错误恢复和数据一致性保障

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- 8GB+ RAM (推荐)
- 2GB+ 磁盘空间

### 2. 安装依赖

```bash
# 安装核心依赖
pip install streamlit chromadb spacy nltk sentence-transformers faiss-cpu

# 安装文档处理依赖
pip install PyMuPDF python-docx python-pptx pandas openpyxl beautifulsoup4

# 安装LLM支持
pip install transformers torch torchvision
```

### 3. 启动系统

```bash
# 方式1: 使用快速启动脚本
python start_intelligence_brain.py

# 方式2: 直接启动Streamlit
streamlit run intelligence_app.py
```

### 4. 访问界面

打开浏览器访问: http://localhost:8501

## 📋 功能模块

### 📥 文档摄取模块

**功能**: 将各种格式的文档转换为知识原子并永久归档

**支持格式**:
- 📄 PDF文件
- 📝 Word文档 (.docx)
- 📊 PowerPoint演示文稿 (.pptx)
- 📈 Excel表格 (.xlsx, .xls)
- 📋 CSV文件
- 📃 文本文件 (.txt, .md, .py)
- 🌐 HTML文件

**处理流程**:
1. **文档解析**: 提取文档内容并保持结构
2. **三位一体分块**: 按句子-段落-文档三层分割
3. **身份铭牌**: 为每个知识原子分配唯一标识
4. **永恒归档**: 自动存储到ChromaDB和SQLite

### 🔍 智能查询模块

**功能**: 基于语义理解的智能知识检索和问答

**查询能力**:
- **语义搜索**: 理解查询意图，返回相关知识原子
- **相似度评分**: 提供检索结果的相关性评分
- **上下文保持**: 维护知识原子间的关联关系
- **智能回答**: 结合LLM生成准确的答案

**查询参数**:
- 返回结果数量 (1-20)
- 文档范围限制
- 相似度阈值设置

## 🏗️ 系统架构

### 核心组件

```
🧠 IntelligenceBrain (中央情报大脑)
├── 🔄 TrinityChunker (三位一体分块器)
├── 💾 EternalArchive (永恒归档系统)
├── 📄 TrinityDocumentProcessor (文档处理器)
└── 🤖 LLMManager (语言模型管理器)
```

### 数据流程

```
📄 原始文档 
    ↓
🔄 三位一体分块 
    ↓
🏷️ 身份铭牌生成 
    ↓
💾 永恒归档 (ChromaDB + SQLite)
    ↓
🔍 智能检索 
    ↓
🤖 智能回答
```

## 🧪 测试验证

运行完整的测试套件:

```bash
python test_intelligence_brain.py
```

预期输出:
```
🧪 中央情报大脑测试套件
==================================================
✅ 三位一体分块器: 通过
✅ 文档处理器: 通过  
✅ 永恒归档系统: 通过
✅ 中央情报大脑: 通过
✅ 大脑状态: 通过
==================================================
🎉 所有测试通过！中央情报大脑运行正常！
```

## 📊 性能指标

### 处理能力
- **文档处理速度**: 平均 1-5秒/文档
- **分块效率**: 平均 3-10个知识原子/文档
- **存储效率**: 双重存储保障数据安全

### 检索性能
- **查询响应时间**: < 2秒
- **检索准确率**: 相似度 > 0.4
- **知识召回率**: > 90%

## 🔧 配置说明

### 环境变量

```bash
# 禁用tokenizers并行警告
export TOKENIZERS_PARALLELISM=false

# 设置数据目录
export RAG_DATA_DIR=/path/to/data

# 设置模型缓存目录
export TRANSFORMERS_CACHE=/path/to/cache
```

### 配置文件

主要配置在 `config.py` 中:

```python
# 文档处理配置
SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.pptx', '.xlsx', '.csv', '.txt', '.html']

# 向量检索配置
MAX_RETRIEVED_CHUNKS = 10
SIMILARITY_THRESHOLD = 0.3

# 存储配置
MODELS_DATA_DIR = Path("data/models")
CHROMA_DB_PATH = MODELS_DATA_DIR / "chroma_db"
```

## 🐛 故障排除

### 常见问题

1. **NLTK数据缺失**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
   ```

2. **spaCy模型缺失**
   ```bash
   python -m spacy download en_core_web_sm
   python -m spacy download zh_core_web_sm
   ```

3. **内存不足**
   - 减少批处理大小
   - 使用更小的嵌入模型
   - 增加系统内存

4. **端口占用**
   ```bash
   # 使用不同端口启动
   streamlit run intelligence_app.py --server.port 8502
   ```

### 日志查看

系统日志位置: `logs/rag_system.log`

```bash
# 实时查看日志
tail -f logs/rag_system.log
```

## 📚 API文档

### 核心API

```python
from core.intelligence_brain import IntelligenceBrain

# 初始化大脑
brain = IntelligenceBrain()

# 摄取文档
result = brain.ingest_document(
    document_content="文档内容",
    filename="document.txt",
    metadata={"source": "upload"}
)

# 智能查询
query_result = brain.query_intelligence(
    query="查询问题",
    top_k=10
)

# 获取状态
status = brain.get_brain_status()
```

## 🤝 贡献指南

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>
cd rag-system

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 运行测试
python test_intelligence_brain.py
```

### 代码规范

- 使用Black进行代码格式化
- 遵循PEP 8编码规范
- 添加类型注解
- 编写单元测试

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢以下技术和项目的支持:

- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [Streamlit](https://streamlit.io/) - Web应用框架
- [spaCy](https://spacy.io/) - 自然语言处理
- [NLTK](https://www.nltk.org/) - 自然语言工具包
- [Sentence Transformers](https://www.sbert.net/) - 句子嵌入
- [FAISS](https://faiss.ai/) - 向量检索

## 📞 联系方式

- **项目**: N.S.S-Novena-Garfield
- **版本**: 2.0.0 - "Genesis"
- **文档**: 基于"大宪章"构建

---

**🧠 让知识拥有永恒的记忆，让智能拥有深度的理解！**