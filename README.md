# 🧬 Research Workstation - 综合科研工作站

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/node.js-16+-green.svg)](https://nodejs.org)
[![AI Powered](https://img.shields.io/badge/AI-Powered-orange.svg)](README.md)

> 🎓 **从传统规则驱动系统成功升级为AI驱动的智能科研平台**

一个集成多个AI驱动系统的综合科研工作站，包含RAG智能问答、牛只识别分析、桌面宠物学习助手、实验记录系统等多个子系统，为科研工作提供全方位的智能化支持。

---

## 🌟 项目亮点

### 🚀 最新AI升级 (2025年8月)
- **🐄 BovineInsight**: 集成Meta DINOv2无监督特征提取 + 智谱GLM-4V专家级文本分析
- **🤖 Changlee**: 集成Google Gemma 2 (2B)本地AI核心，实现完全本地化智能对话
- **📊 多模态融合**: 传统算法 + 深度学习 + 大语言模型的三重融合架构
- **🔒 隐私保护**: 本地AI运行，数据不上传云端

### 🎯 核心价值
- **科研价值**: 解决数据标注难题，生成论文级分析报告
- **用户体验**: 隐私保护的智能对话，个性化学习陪伴
- **技术创新**: 模块化设计，便于维护和扩展

---

## 🏗️ 系统架构

```
Research Workstation
├── 🤖 RAG智能问答系统          # DeepSeek + multilingual-e5 + FAISS
├── 🐄 BovineInsight牛只识别    # DINOv2 + GLM-4V + 传统CV算法
├── 🐱 Changlee桌面宠物         # 混合AI架构 + Electron + React
├── 📊 Chronicle实验记录器      # 无头微服务 + AI分析引擎
├── 🧬 Genome Jigsaw测序分析    # 自动化细菌基因组分析流水线
├── 🧬 Molecular Simulation     # 分子动力学模拟工具箱
├── 🔧 API管理系统             # 统一配置管理 + 安全存储
└── 🛠️ 工具集                  # 部署工具 + 测试工具 + 文档
```

---

## 🎯 核心系统详解

### 🤖 RAG智能问答系统
**基于DeepSeek + multilingual-e5 + FAISS的模块化RAG系统**

#### 🌟 核心特性
- **多文档格式支持**: PDF、Word、TXT、Markdown等
- **智能对话记忆**: 上下文感知的多轮对话
- **多模态检索**: 文本 + 图像的混合检索
- **移动端适配**: PWA支持，跨平台访问
- **API集成**: Gemini、DeepSeek等多种LLM支持

#### 🛠️ 技术栈
- **后端**: Python + Streamlit + FAISS
- **LLM**: DeepSeek-V2.5 / Google Gemini
- **嵌入模型**: multilingual-e5-large
- **数据库**: SQLite + 向量数据库
- **部署**: Docker + Cloudflare Tunnel

#### 📁 核心模块
```
rag-system/
├── core/rag_system.py          # 主要业务逻辑
├── llm/llm_manager.py          # LLM管理
├── retrieval/vector_store.py   # 向量检索
├── document/document_processor.py # 文档处理
├── memory/memory_manager.py    # 记忆管理
└── database/chat_db.py         # 聊天记录
```

---

### 🐄 BovineInsight牛只识别系统 ⭐ **博士级AI升级**
**多摄像头牛只身份识别与体况评分系统**

#### 🧠 AI升级亮点
- **🔬 DINOv2无监督特征提取器**: Meta最新Vision Transformer，768维特征向量
- **📝 GLM-4V专家级文本分析**: 智谱AI视觉语言模型，生成论文级BCS报告
- **🎯 多模态融合分析**: 传统方法(60%) + DINOv2特征(40%) + GLM-4V文本

#### 🌟 核心功能
- **双重身份识别**: 耳标OCR + 花色重识别(Re-ID)
- **自动体况评分**: BCS 1-5分精确评估
- **专家级报告生成**: 结构化分析报告，包含饲养建议
- **多摄像头协同**: 不同角度的综合分析

#### 🛠️ 技术栈
- **深度学习**: PyTorch + DINOv2 + GLM-4V
- **计算机视觉**: OpenCV + YOLOv8
- **特征提取**: Siamese Networks + Triplet Loss
- **文本分析**: Transformers + 智谱AI API

#### 📁 核心模块
```
bovine-insight/
├── src/feature_extraction/     # DINOv2特征提取器 ⭐
├── src/text_analysis/          # GLM-4V文本分析 ⭐
├── src/identification/         # 身份识别模块
├── src/body_condition/         # 增强BCS分析器 ⭐
├── src/detection/              # 目标检测
└── src/database/               # 数据管理
```

---

### 🐱 Changlee桌面宠物 ⭐ **混合AI核心**
**情感陪伴型英语学习桌面宠物**

#### 🤖 混合AI升级亮点
- **🧠 本地AI核心**: Google Gemma 2 (2B)本地运行，完全隐私保护
- **☁️ 云端API集成**: 支持Gemini、DeepSeek等多种云端AI服务
- **🔄 智能切换**: 自动选择最佳AI服务，支持手动切换和回退
- **💬 长离人格化**: 温暖智慧的AI学习伙伴，个性化对话
- **⚡ FastAPI微服务**: 高性能异步API架构，支持并发处理

#### 🌟 核心特性
- **智能桌宠**: 可拖拽的2D宠物，多种状态动画
- **漂流瓶推送**: 智能时机推送学习内容
- **学习胶囊**: 美观的卡片式学习界面
- **魔法沙滩**: 游戏化拼写练习
- **智能复习**: 间隔重复算法优化记忆

#### 🛠️ 技术栈
- **前端**: Electron + React + CSS Animation
- **后端**: Node.js + Express + FastAPI
- **本地AI**: Google Gemma 2 (2B) + Transformers
- **数据**: SQLite + 间隔重复算法

#### 📁 核心模块
```
Changlee/
├── src/backend/services/HybridAIService.py   # 混合AI服务核心 ⭐
├── src/backend/hybrid_ai_server.py           # FastAPI混合AI服务器 ⭐
├── config/ai_config.js                      # AI服务配置管理 ⭐
├── src/renderer/components/LocalAIChat.jsx   # AI聊天组件
├── src/backend/services/ChronicleService.js  # Chronicle集成
└── start_with_local_ai.js                    # 集成启动脚本
```

---

### 📊 Chronicle实验记录器
**AI驱动的自动化实验记录微服务**

#### 🌟 核心特性
- **无头微服务**: 后台静默运行，不干扰工作流程
- **智能分析引擎**: AI提炼关键信息，生成结构化报告
- **多维度监控**: 文件系统、活动窗口、命令行监控
- **RESTful API**: 标准化接口，易于集成

#### 🛠️ 技术栈
- **后端**: Node.js + Express + SQLite
- **监控**: chokidar + active-win
- **AI分析**: LLM集成，智能摘要
- **API**: RESTful设计

#### 📁 核心模块
```
chronicle/
├── src/services/DataCollector.js    # 数据采集服务
├── src/services/AnalysisEngine.js   # AI分析引擎
├── src/api/SessionController.js     # 会话控制API
└── src/database/SessionManager.js   # 会话管理
```

---

### 🔧 API管理系统
**统一的API配置管理和私有密钥管理服务**

#### 🌟 核心特性
- **统一配置管理**: 所有子系统的API端点配置
- **安全密钥存储**: 加密存储私有API密钥
- **权限控制**: 基于角色的访问控制
- **可视化管理**: Web界面管理API配置
- **使用监控**: API调用统计和监控

#### 🛠️ 技术栈
- **后端**: Python + Flask
- **安全**: 加密存储 + 权限控制
- **前端**: Web管理界面
- **集成**: 支持所有子系统

---

### 🧬 Genome Jigsaw测序分析系统 ⭐ **新增**
**自动化细菌全基因组测序数据分析流水线**

#### 🌟 核心特性
- **完整分析流程**: 质量控制 → 数据清洗 → 基因组组装 → 注释 → 泛基因组分析 → 系统发育分析 → 基因筛选
- **一键自动化**: 单个脚本完成从原始数据到最终结果的全流程分析
- **标准化工具链**: FastQC + fastp + SPAdes + Prokka + Roary + MAFFT + IQ-TREE + ABricate
- **智能报告生成**: 自动生成详细的分析报告和统计信息
- **多样本支持**: 批量处理多个菌株的测序数据

#### 🛠️ 技术栈
- **环境管理**: Conda + Bioconda
- **质量控制**: FastQC + MultiQC + fastp
- **基因组组装**: SPAdes
- **基因组注释**: Prokka
- **比较基因组学**: Roary + MAFFT + IQ-TREE
- **基因筛选**: ABricate (多数据库支持)

#### 📁 核心模块
```
genome-jigsaw/
├── environment.yml                 # Conda环境配置
├── run_genome_jigsaw.sh           # 主执行脚本 ⭐
├── config/default.yaml            # 默认配置参数
├── scripts/setup.py               # 环境初始化
└── docs/USAGE.md                  # 详细使用指南
```

---

### 🧬 Molecular Simulation Toolkit ⭐ **新增**
**标准化分子动力学模拟工具箱**

#### 🌟 核心特性
- **模块化SOP脚本**: 系统搭建 + 模拟执行 + 轨迹分析的标准作业流程
- **高度可配置**: 通过简单变量修改适应不同研究体系
- **发表级图表**: 自动生成高质量的科研图表和统计分析
- **批量处理**: 支持多个PDB文件的批量模拟分析
- **专业示例**: Cas14a和多糖合成酶的完整分析流程

#### 🛠️ 技术栈
- **分子模拟**: GROMACS + AMBER/CHARMM力场
- **数据分析**: Python + Matplotlib + NumPy
- **图表生成**: Seaborn + 发表级样式
- **批量处理**: Bash脚本自动化

#### 📁 核心模块
```
molecular-simulation-toolkit/
├── sop_scripts/                   # 标准作业流程脚本 ⭐
│   ├── sop_prepare_system.sh     # 系统搭建SOP
│   ├── sop_run_simulation.sh     # 模拟执行SOP
│   └── sop_analyze_trajectory.sh # 轨迹分析SOP
├── analysis_tools/plot_results.py # 发表级图表生成 ⭐
├── templates/mdp_files/           # MDP参数模板
├── examples/                      # 使用示例
│   ├── cas14a_example/           # Cas14a蛋白质示例
│   └── enzyme_example/           # 多糖合成酶示例
└── utilities/batch_runner.sh     # 批量处理工具
```

---

## 🚀 快速开始

### 📋 环境要求
- **Python**: 3.8+
- **Node.js**: 16+
- **内存**: 8GB+ (推荐16GB+)
- **GPU**: 可选，但推荐用于AI模型加载

### ⚡ 一键启动

#### 1. 启动完整集成系统
```bash
# 启动Changlee + 本地AI + Chronicle集成
cd systems/Changlee
node start_with_local_ai.js

# 访问服务
# Changlee主服务: http://localhost:3001
# 本地AI服务: http://localhost:8001
# Chronicle服务: http://localhost:3000
```

#### 2. 启动RAG智能问答系统
```bash
cd systems/rag-system
pip install -r requirements.txt
python run.py

# 访问: http://localhost:8501
```

#### 3. 启动BovineInsight分析系统
```bash
cd systems/bovine-insight
pip install -r requirements.txt
python src/main.py

# 支持DINOv2特征提取和GLM-4V文本分析
```

#### 4. 启动API管理系统
```bash
cd api_management
python start_api_manager.py start

# Web管理界面: http://localhost:5000
```

#### 5. 运行Genome Jigsaw测序分析
```bash
cd systems/genome-jigsaw

# 创建conda环境
conda env create -f environment.yml
conda activate genome-jigsaw

# 运行完整分析流水线
./run_genome_jigsaw.sh /path/to/your/fastq/files

# 查看结果: results/GENOME_JIGSAW_REPORT.txt
```

#### 6. 使用Molecular Simulation Toolkit
```bash
cd systems/molecular-simulation-toolkit

# 复制工具箱到项目目录
cp -r . /path/to/your/project/

# 配置并运行完整MD模拟流程
./sop_scripts/sop_prepare_system.sh
./sop_scripts/sop_run_simulation.sh
./sop_scripts/sop_analyze_trajectory.sh

# 生成发表级图表
python analysis_tools/plot_results.py --summary analysis/
```

### 🔧 环境配置

#### Python依赖安装
```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装AI模型依赖（BovineInsight + Changlee）
pip install -r systems/Changlee/requirements_local_ai.txt
pip install -r systems/bovine-insight/requirements.txt

# 安装生物信息学工具依赖（Genome Jigsaw）
conda env create -f systems/genome-jigsaw/environment.yml

# 安装分子模拟工具依赖（需要GROMACS）
# 请参考GROMACS官方安装指南
```

#### Node.js依赖安装
```bash
# Changlee桌面宠物
cd systems/Changlee
npm install

# Chronicle实验记录器
cd systems/chronicle
npm install
```

---

## 🎯 使用场景

### 🔬 科研场景
- **文献调研**: RAG系统快速检索和总结文献
- **实验记录**: Chronicle自动记录实验过程
- **数据分析**: BovineInsight提供专业级分析报告
- **基因组学研究**: Genome Jigsaw自动化测序数据分析
- **分子模拟**: Molecular Simulation Toolkit标准化MD模拟
- **学术写作**: AI辅助生成论文级文本描述

### 📚 教育场景
- **英语学习**: Changlee提供个性化学习陪伴
- **知识问答**: RAG系统回答专业问题
- **学习记录**: Chronicle跟踪学习进度
- **智能辅导**: 本地AI提供隐私保护的学习指导

### 🏭 产业场景
- **畜牧业**: BovineInsight自动化牛只管理
- **生物技术**: Genome Jigsaw细菌基因组分析
- **制药工业**: Molecular Simulation药物-靶点模拟
- **智能客服**: RAG系统提供专业问答
- **数据分析**: 多模态AI融合分析
- **流程优化**: Chronicle记录和分析工作流程

---

## 🛠️ 开发指南

### 📁 项目结构
```
research-workstation/
├── 📂 systems/                    # 核心系统
│   ├── 🤖 rag-system/            # RAG智能问答
│   ├── 🐄 bovine-insight/        # 牛只识别分析
│   ├── 🐱 Changlee/              # 桌面宠物
│   ├── 📊 chronicle/             # 实验记录器
│   ├── 🧬 genome-jigsaw/         # 基因组测序分析
│   └── 🧬 molecular-simulation-toolkit/ # 分子动力学模拟
├── 📂 api_management/             # API管理系统
├── 📂 tools/                     # 开发工具
├── 📂 docs/                      # 文档集合
├── 📂 tests/                     # 测试文件
├── 📂 logs/                      # 日志文件
└── 📂 data/                      # 数据目录
```

### 🔧 开发环境设置
```bash
# 1. 克隆项目
git clone https://github.com/novenazgarfield/research-workstation.git
cd research-workstation

# 2. 设置Python环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 设置Node.js环境
cd systems/Changlee
npm install
cd ../chronicle
npm install

# 5. 设置生物信息学环境
cd ../genome-jigsaw
conda env create -f environment.yml

# 6. 检查GROMACS安装（用于分子模拟）
gmx --version
```

### 🧪 测试系统
```bash
# 测试AI升级功能
python systems/test_upgrades.py

# 测试RAG系统
cd systems/rag-system
python test_basic.py

# 测试Changlee集成
cd systems/Changlee
node test_chronicle_integration.js

# 测试Genome Jigsaw
cd systems/genome-jigsaw
./scripts/test_pipeline.sh --test-env

# 测试Molecular Simulation Toolkit
cd systems/molecular-simulation-toolkit
# 需要GROMACS环境
```

---

## 📊 技术规格

### 🤖 AI模型规格
| 系统 | 核心模型 | 参数规模 | 主要功能 | 运行方式 |
|------|----------|----------|----------|----------|
| **BovineInsight** | DINOv2 + GLM-4V | 86M-9B | 无监督特征+专家文本 | 云端+本地 |
| **Changlee** | Gemma 2 + Gemini + DeepSeek | 2B-236B | 混合智能对话 | 本地+云端 |
| **RAG系统** | DeepSeek + E5 | 236B+560M | 智能问答检索 | 云端API |
| **Chronicle** | LLM集成 | 可配置 | 智能分析摘要 | 云端API |
| **Genome Jigsaw** | 生物信息学工具链 | - | 基因组分析流水线 | 本地计算 |
| **Molecular Simulation** | GROMACS + 分析工具 | - | 分子动力学模拟 | 本地计算 |

### 🏗️ 架构特点
- **模块化设计**: 各系统独立部署，松耦合架构
- **多模态融合**: 文本、图像、语音的综合处理
- **隐私保护**: 本地AI运行，敏感数据不上传
- **可扩展性**: 标准化API接口，易于集成新功能
- **容错能力**: 优雅降级，重试机制，健康监控

---

## 🎯 未来发展方向

### 🚀 短期目标 (3-6个月)
- **🔧 性能优化**: 模型量化，推理加速，内存优化
- **📱 移动端扩展**: PWA增强，移动端适配
- **🌐 多语言支持**: 国际化界面，多语言模型
- **🔒 安全增强**: 端到端加密，权限细化
- **🧬 工具扩展**: 更多生物信息学和计算生物学工具

### 🌟 中期目标 (6-12个月)
- **🧠 模型升级**: 集成最新的开源大模型
- **🔗 系统集成**: 更深度的跨系统协作
- **📊 数据分析**: 高级分析和可视化功能
- **🤖 自动化**: 更多自动化工作流程
- **🧬 专业化**: 针对特定科研领域的深度定制

### 🎓 长期愿景 (1-2年)
- **🌍 开源生态**: 构建开发者社区和插件生态
- **🏭 产业应用**: 面向特定行业的定制化解决方案
- **🔬 科研平台**: 成为标准化的科研工作站平台
- **🎯 智能化**: 全面AI驱动的智能科研助手

---

## 🤝 贡献指南

### 💡 如何贡献
1. **Fork项目** 并创建特性分支
2. **提交更改** 并添加测试
3. **确保测试通过** 并更新文档
4. **提交Pull Request** 并描述更改

### 🐛 问题报告
- 使用GitHub Issues报告bug
- 提供详细的复现步骤
- 包含系统环境信息

### 📝 开发规范
- 遵循PEP 8 (Python) 和ESLint (JavaScript)
- 添加适当的注释和文档
- 编写单元测试覆盖新功能

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🙏 致谢

### 🤖 AI模型和技术
- **Meta**: DINOv2视觉特征提取模型
- **智谱AI**: GLM-4V视觉语言模型
- **Google**: Gemma 2本地化语言模型
- **DeepSeek**: 高性能语言模型API
- **OpenAI**: 技术架构参考

### 🛠️ 开源项目
- **PyTorch**: 深度学习框架
- **Transformers**: 模型加载和推理
- **Electron**: 跨平台桌面应用
- **React**: 前端用户界面
- **FastAPI**: 高性能API框架
- **GROMACS**: 分子动力学模拟引擎
- **Bioconda**: 生物信息学软件包管理

---

## 📞 联系方式

- **项目主页**: [GitHub Repository](https://github.com/novenazgarfield/research-workstation)
- **问题反馈**: [GitHub Issues](https://github.com/novenazgarfield/research-workstation/issues)
- **讨论交流**: [GitHub Discussions](https://github.com/novenazgarfield/research-workstation/discussions)

---

<div align="center">

**🎉 从传统规则驱动系统成功升级为AI驱动的智能科研平台！**

[![Star this repo](https://img.shields.io/github/stars/novenazgarfield/research-workstation?style=social)](https://github.com/novenazgarfield/research-workstation)
[![Fork this repo](https://img.shields.io/github/forks/novenazgarfield/research-workstation?style=social)](https://github.com/novenazgarfield/research-workstation/fork)

*让AI为科研工作赋能，让智能化成为生产力！* 🚀✨

</div>