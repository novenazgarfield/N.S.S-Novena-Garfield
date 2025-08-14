# 🚀 增强版RAG系统部署指南

## 📋 系统概述

这是一个支持多API和分布式计算的增强版RAG系统，专为您的3090+4060双GPU环境设计。

### 🎯 核心特性

- **多API支持**: 本地模型、魔搭API、OpenAI API、智谱API等
- **分布式计算**: 3090负责LLM推理，4060负责嵌入计算
- **智能记忆**: 永久记忆 + 临时记忆，支持向量检索
- **多格式文档**: PDF、DOCX、PPTX、Excel等
- **Web界面**: 现代化的Streamlit界面
- **配置管理**: 图形化配置工具

## 🛠️ 环境要求

### 硬件要求
- **GPU**: NVIDIA RTX 3090 (24GB) + RTX 4060 (8GB)
- **内存**: 建议32GB以上
- **存储**: 建议100GB以上可用空间

### 软件要求
- **Python**: 3.8+
- **CUDA**: 11.8+ (支持PyTorch)
- **Git**: 用于代码管理

## 📦 安装步骤

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd research-workstation/systems/rag-system
```

### 2. 创建虚拟环境

```bash
# 使用conda (推荐)
conda create -n rag-system python=3.10
conda activate rag-system

# 或使用venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 如果需要GPU支持
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 安装FAISS GPU版本 (可选)
pip uninstall faiss-cpu
pip install faiss-gpu
```

### 4. 验证安装

```bash
python run_enhanced.py --mode cli --skip-check
```

## ⚙️ 配置指南

### 方式1: 使用配置管理器 (推荐)

```bash
python config_manager.py
```

选择"快速设置向导"，按提示配置您的首选API。

### 方式2: 手动配置

#### 配置本地模型 (DeepSeek 7B Q5)

```bash
# 1. 下载模型文件到本地
# 2. 编辑配置
python -c "
from config_advanced import APIConfig
config = APIConfig.get_config('local')
config['model_path'] = '/path/to/deepseek-7b-chat-q5.gguf'
config['device'] = 'cuda:0'  # 3090
config['n_gpu_layers'] = 35
APIConfig.set_config('local', config)
"
```

#### 配置魔搭API

```bash
export MODELSCOPE_API_KEY="your-api-key"
```

或在配置管理器中设置。

#### 配置OpenAI API

```bash
export OPENAI_API_KEY="your-api-key"
```

### 方式3: 环境变量配置

创建 `.env` 文件：

```bash
# API密钥
MODELSCOPE_API_KEY=your-modelscope-key
OPENAI_API_KEY=your-openai-key
ZHIPU_API_KEY=your-zhipu-key

# 默认API类型
RAG_API_TYPE=modelscope

# 模型路径
LOCAL_MODEL_PATH=/path/to/your/model.gguf
```

## 🚀 启动系统

### Web界面 (推荐)

```bash
# 启动增强版Web界面
python run_enhanced.py --mode web --app enhanced --port 8501

# 启动简化版Web界面
python run_enhanced.py --mode web --app simple --port 8502
```

访问: http://localhost:8501

### 命令行界面

```bash
python run_enhanced.py --mode cli
```

### 配置管理

```bash
python run_enhanced.py --mode config
```

## 🔧 分布式计算配置

系统会自动检测您的GPU配置并分配任务：

- **RTX 3090 (cuda:0)**: LLM推理
- **RTX 4060 (cuda:1)**: 嵌入计算、向量搜索
- **CPU**: 文档处理、记忆管理

### 手动调整设备分配

编辑 `config_advanced.py`:

```python
DEVICES = {
    "gpu_3090": {
        "device": "cuda:0",
        "role": "llm_inference"
    },
    "gpu_4060": {
        "device": "cuda:1", 
        "role": "embedding_processing"
    }
}
```

## 📚 使用指南

### 1. 上传文档

- 支持格式: PDF, DOCX, PPTX, Excel, CSV, TXT, HTML
- 批量上传: 可同时上传多个文件
- 自动处理: 文档会自动分块并向量化

### 2. 智能问答

- 输入问题后点击"获取答案"
- 系统会检索相关文档并生成回答
- 支持多轮对话和上下文记忆

### 3. API切换

在侧边栏选择不同的API提供者：
- 本地模型: 完全离线，速度快
- 魔搭API: 支持Qwen2.5等模型
- OpenAI API: GPT-4等模型
- 智谱API: GLM-4等模型

### 4. 任务管理

- 使用任务关键词区分不同的对话
- 每个任务有独立的记忆和历史
- 可以清除特定任务的数据

## 🔍 故障排除

### 常见问题

#### 1. GPU内存不足

```bash
# 减少批次大小
export CUDA_VISIBLE_DEVICES=0,1
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

#### 2. 模型加载失败

- 检查模型文件路径是否正确
- 确认模型文件完整性
- 检查GPU显存是否足够

#### 3. API调用失败

- 检查API密钥是否正确
- 确认网络连接正常
- 查看日志文件: `data/processed/rag/logs/rag_system.log`

#### 4. 依赖安装问题

```bash
# 清理pip缓存
pip cache purge

# 重新安装
pip install --no-cache-dir -r requirements.txt
```

### 性能优化

#### 1. GPU优化

```bash
# 设置GPU内存增长
export TF_FORCE_GPU_ALLOW_GROWTH=true

# 优化CUDA设置
export CUDA_LAUNCH_BLOCKING=0
```

#### 2. 向量索引优化

- 大数据量时会自动使用IVF索引
- 可手动调用系统优化功能
- 定期清理不需要的索引

## 📊 监控和维护

### 系统状态监控

Web界面侧边栏显示：
- GPU内存使用情况
- 向量索引统计
- API状态
- 记忆系统状态

### 日志管理

```bash
# 查看实时日志
tail -f data/processed/rag/logs/rag_system.log

# 清理旧日志
find data/processed/rag/logs -name "*.log" -mtime +7 -delete
```

### 数据备份

重要数据文件：
- `data/processed/rag/database/chat_logs.db` - 聊天记录
- `data/models/rag/faiss_index.pkl` - 向量索引
- `data/models/rag/chunks.pkl` - 文本块
- `data/processed/rag/memory/` - 记忆文件

## 🔄 更新和升级

### 更新代码

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### 迁移数据

系统会自动处理数据格式升级，无需手动迁移。

## 🆘 技术支持

### 获取帮助

1. 查看日志文件
2. 检查系统状态
3. 运行诊断工具

### 诊断工具

```bash
# 系统诊断
python -c "
from core.enhanced_rag_system import EnhancedRAGSystem
system = EnhancedRAGSystem()
print(system.get_system_status())
"
```

## 📈 扩展功能

### 添加新的API提供者

1. 在 `llm/multi_api_manager.py` 中添加新的Provider类
2. 在 `config_advanced.py` 中添加配置
3. 更新配置管理器

### 自定义文档处理器

1. 在 `document/document_processor.py` 中添加新的解析器
2. 更新支持的文件类型列表

### 集成其他模型

系统支持任何兼容的嵌入模型和LLM模型，只需更新配置即可。

---

🎉 **恭喜！您的增强版RAG系统已准备就绪！**

现在您可以享受多API支持和分布式计算带来的强大功能了。