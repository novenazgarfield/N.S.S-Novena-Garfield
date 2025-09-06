# 🧠 N.S.S-Novena-Garfield 多模态AI融合研究工作站

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 16+](https://img.shields.io/badge/node.js-16+-green.svg)](https://nodejs.org/)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

> **基于NEXUS架构的智能系统平台，集成多个专业AI系统，提供统一的研究工作站环境**

## 🌟 项目概述

N.S.S-Novena-Garfield是一个综合性的多模态AI融合研究工作站，基于NEXUS架构设计，集成了7个专业AI系统，涵盖生物信息学、分子动力学、计算机视觉、自然语言处理、音频处理等多个领域。

### 🎯 核心特性

- **🧠 智能RAG系统** - 基于大语言模型的智能问答与知识检索
- **🧬 基因星云系统** - 基因组测序分析与生物信息学处理
- **🔬 动力学观测仪** - 分子动力学模拟与化学分析
- **🐄 牛识别系统** - 多摄像头牛只身份识别与体况评分
- **📚 Chronicle系统** - AI驱动的实验记录与数据管理
- **🎵 Changlee系统** - 音乐学习与音频处理平台
- **🌐 NEXUS核心** - 统一的Web界面与系统管理中心

## 📁 项目结构

```
N.S.S-Novena-Garfield/
├── 🌐 systems/                    # 核心系统目录
│   ├── 🧠 rag-system/            # RAG智能问答系统
│   ├── 🧬 genome-nebula/         # 基因星云系统
│   ├── 🔬 kinetic-scope/         # 动力学观测仪
│   ├── 🐄 bovine-insight/        # 牛识别系统
│   ├── 📚 chronicle/             # 实验记录系统
│   ├── 🎵 Changlee/              # 音乐学习系统
│   └── 🌐 nexus/                 # NEXUS核心界面
├── 🔧 api/                       # API管理系统
├── 📊 management/                # 系统管理工具
├── 📁 data/                      # 数据存储目录
├── 📋 requirements.txt           # Python依赖配置
└── 🌐 index.html                 # 主入口页面
```

## 🚀 快速开始

### 📋 系统要求

- **Python**: 3.8+ 
- **Node.js**: 16+
- **内存**: 8GB+ 推荐
- **存储**: 10GB+ 可用空间
- **操作系统**: Linux/macOS/Windows

### 🔧 安装步骤

#### 📦 部署选项说明

**💾 关于node_modules（重要）:**
- 当前仓库包含完整的node_modules（~1.6GB）
- 根据你的需求选择合适的部署方式

#### 🚀 选项1: 完整部署（推荐新手）

```bash
# 1. 克隆完整项目（包含node_modules）
git clone https://github.com/novenazgarfield/N.S.S-Novena-Garfield.git
cd N.S.S-Novena-Garfield

# 2. 安装Python依赖
pip install -r requirements.txt

# 3. 直接启动（无需npm install）
cd systems/nexus
python nexus.py dev
```

**✅ 优点**: 即开即用，无需Node.js环境  
**💾 缺点**: 下载大小1.9GB

#### ⚡ 选项2: 轻量部署（推荐开发者）

```bash
# 1. 克隆项目（排除node_modules）
git clone --depth 1 https://github.com/novenazgarfield/N.S.S-Novena-Garfield.git
cd N.S.S-Novena-Garfield

# 2. 删除现有node_modules（如果存在）
rm -rf systems/*/node_modules

# 3. 安装Python依赖
pip install -r requirements.txt

# 4. 安装Node.js依赖
cd systems/chronicle && npm install && cd ../..
cd systems/Changlee && npm install && cd ../..
cd systems/nexus && npm install && cd ../..

# 5. 启动系统
cd systems/nexus && python nexus.py dev
```

**✅ 优点**: 下载小（348MB），依赖最新，减少82%存储空间  
**💾 缺点**: 需要Node.js环境，安装时间较长

#### 🐍 选项3: 仅Python系统

```bash
# 1. 克隆项目
git clone https://github.com/novenazgarfield/N.S.S-Novena-Garfield.git
cd N.S.S-Novena-Garfield

# 2. 安装Python依赖
pip install -r requirements.txt

# 3. 启动Python系统
cd systems/rag-system && python smart_rag_server.py
# 或
cd systems/genome-nebula && python genome.py web
# 或
cd systems/kinetic-scope && python kinetic.py pipeline
```

**✅ 优点**: 最小化部署，快速启动  
**💾 缺点**: 无法使用Chronicle、Changlee、NEXUS前端

#### 🌐 快速访问

```bash
# 静态页面访问（无需Node.js）
python -m http.server 8000
# 访问 http://localhost:8000

# NEXUS完整界面（需要Node.js）
cd systems/nexus && python nexus.py dev
# 访问 http://localhost:8080
```

## 🎯 系统详解

### 🧠 RAG智能问答系统
- **功能**: 基于大语言模型的智能问答与文档检索
- **技术栈**: Python, Streamlit, FastAPI, ChromaDB
- **启动**: `cd systems/rag-system && python smart_rag_server.py`
- **访问**: http://localhost:8502

### 🧬 基因星云系统 (Genome-Nebula)
- **功能**: 基因组测序分析、质量控制、变异检测
- **技术栈**: Python, BioPython, NumPy, Pandas
- **启动**: `cd systems/genome-nebula && python genome.py web`
- **特性**: 支持多种基因组分析流程

### 🔬 动力学观测仪 (Kinetic-Scope)
- **功能**: 分子动力学模拟、化学反应分析
- **技术栈**: Python, MDAnalysis, RDKit, OpenMM
- **启动**: `cd systems/kinetic-scope && python kinetic.py pipeline`
- **特性**: 高性能分子模拟计算

### 🐄 牛识别系统 (Bovine-Insight)
- **功能**: 多摄像头牛只身份识别与体况评分
- **技术栈**: Python, OpenCV, PyTorch, YOLO
- **启动**: `cd systems/bovine-insight && python bovine.py system`
- **特性**: 实时视频分析与AI识别

### 📚 Chronicle系统
- **功能**: AI驱动的实验记录与数据管理
- **技术栈**: Node.js, React, MongoDB
- **启动**: `cd systems/chronicle && node chronicle.js server`
- **特性**: 智能实验记录与数据可视化

### 🎵 Changlee系统
- **功能**: 音乐学习与音频处理平台
- **技术栈**: Node.js, Web Audio API, TensorFlow.js
- **启动**: `cd systems/Changlee && node changlee.js server`
- **特性**: 音乐分析与学习辅助

### 🌐 NEXUS核心界面
- **功能**: 统一的Web界面与系统管理中心
- **技术栈**: HTML5, CSS3, JavaScript, Vue.js
- **特性**: 响应式设计、模块化架构、实时监控

## 🔧 配置说明

### 🌐 环境变量
```bash
# API配置
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# 数据库配置
export DB_HOST="localhost"
export DB_PORT="5432"
export REDIS_URL="redis://localhost:6379"

# 系统配置
export NEXUS_HOST="0.0.0.0"
export NEXUS_PORT="8080"
```

### 📊 数据库设置
```yaml
# config/database.yaml
postgresql:
  host: localhost
  port: 5432
  database: nexus_db
  username: postgres
  password: your-password

mongodb:
  host: localhost
  port: 27017
  database: nexus_mongo

redis:
  host: localhost
  port: 6379
  database: 0
```

## 🧪 测试

### 🔍 运行测试
```bash
# 运行所有系统测试
python -m pytest tests/ -v

# 测试特定系统
cd systems/rag-system && python -m pytest tests/
cd systems/genome-nebula && python genome.py check-tools
cd systems/kinetic-scope && python kinetic.py status
cd systems/bovine-insight && python bovine.py validate
```

### 📊 系统状态检查
```bash
# 检查所有系统状态
python management/health_check.py

# 检查特定系统
cd systems/nexus && python nexus.py status
```

## 📈 性能优化

### 🚀 系统优化建议
- **内存**: 推荐16GB+用于大规模数据处理
- **GPU**: 支持CUDA加速（牛识别、深度学习任务）
- **存储**: SSD推荐，提升I/O性能
- **网络**: 千兆网络用于多系统协作

### 🔧 配置优化
```python
# config/performance.py
SYSTEM_CONFIG = {
    'max_workers': 8,
    'memory_limit': '8GB',
    'gpu_enabled': True,
    'cache_size': '2GB',
    'batch_size': 32
}
```

## 🛠️ 开发指南

### 🏗️ 添加新系统
1. 在`systems/`目录下创建新系统目录
2. 实现统一的入口接口
3. 添加配置文件和文档
4. 更新NEXUS界面集成

### 🔌 API集成
```python
# 系统API标准接口
class SystemAPI:
    def __init__(self, config):
        self.config = config
    
    def start(self):
        """启动系统"""
        pass
    
    def stop(self):
        """停止系统"""
        pass
    
    def status(self):
        """获取系统状态"""
        pass
```

## 📚 文档

- **[API文档](api/docs/)** - 详细的API接口说明
- **[系统架构](management/docs/)** - 系统设计与架构文档
- **[部署指南](systems/nexus/DEPLOYMENT_GUIDE.md)** - 生产环境部署
- **[开发指南](management/docs/DEVELOPMENT.md)** - 开发环境搭建

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 📝 代码规范
- Python: 遵循PEP 8规范
- JavaScript: 使用ESLint配置
- 文档: 使用Markdown格式
- 测试: 保持90%+代码覆盖率

## 🙏 致谢

- **OpenAI** - GPT模型支持
- **Anthropic** - Claude模型支持
- **Hugging Face** - Transformers库
- **BioPython** - 生物信息学工具
- **OpenCV** - 计算机视觉库

## 📞 联系方式

- **项目主页**: https://github.com/novenazgarfield/N.S.S-Novena-Garfield
- **问题反馈**: https://github.com/novenazgarfield/N.S.S-Novena-Garfield/issues
- **邮箱**: novenazgarfield@example.com

## 🔄 更新日志

### v2.0.0 (2025-09-04)
- ✅ 完成系统优化与清理
- ✅ 统一依赖管理
- ✅ 修复所有简化版本问题
- ✅ 优化NEXUS界面弹窗大小
- ✅ 完善文档与测试

### v1.0.0 (2025-08-29)
- 🎉 Genesis项目完成
- 🧠 中央情报大脑系统上线
- 🌐 NEXUS核心界面发布
- 🧬 基因星云系统集成

---

<div align="center">

**🌟 如果这个项目对你有帮助，请给个Star！🌟**

Made with ❤️ by [Novena Garfield](https://github.com/novenazgarfield)

</div>