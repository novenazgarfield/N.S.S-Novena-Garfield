# 🚀 Research Workstation 快速开始指南

> **版本**: v2.0.0 | **更新时间**: 2025年8月20日

欢迎使用Research Workstation！本指南将帮助您在5分钟内启动并运行整个系统。

---

## 📋 环境要求

### 🖥️ 系统要求
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **内存**: 8GB+ (推荐16GB+)
- **存储**: 10GB+ 可用空间
- **网络**: 稳定的互联网连接 (用于模型下载)

### 🛠️ 软件依赖
- **Python**: 3.8+ (推荐3.10+)
- **Node.js**: 16+ (推荐18+)
- **Git**: 最新版本

---

## ⚡ 一键启动 (推荐)

### 1. 克隆项目
```bash
git clone https://github.com/novenazgarfield/research-workstation.git
cd research-workstation
```

### 2. 启动完整系统
```bash
# 启动Changlee + 本地AI + Chronicle集成系统
cd systems/Changlee
node start_with_local_ai.js
```

### 3. 访问服务
- **Changlee主服务**: http://localhost:3001
- **本地AI服务**: http://localhost:8001  
- **Chronicle服务**: http://localhost:3000

---

## 🎯 分系统启动

### 🤖 RAG智能问答系统
```bash
cd systems/rag-system
pip install -r requirements.txt
python run.py

# 访问: http://localhost:8501
```

### 🐄 BovineInsight牛只识别
```bash
cd systems/bovine-insight
pip install -r requirements.txt
python src/main.py

# 支持DINOv2特征提取和GLM-4V文本分析
```

### 🔧 API管理系统
```bash
cd api_management
python start_api_manager.py start

# Web管理界面: http://localhost:5000
```

---

## 🔧 详细安装步骤

### 步骤1: 环境准备
```bash
# 1. 创建Python虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. 升级pip
pip install --upgrade pip
```

### 步骤2: 安装Python依赖
```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装AI模型依赖 (可选，用于本地AI功能)
pip install -r systems/Changlee/requirements_local_ai.txt
pip install -r systems/bovine-insight/requirements.txt
```

### 步骤3: 安装Node.js依赖
```bash
# Changlee桌面宠物
cd systems/Changlee
npm install

# Chronicle实验记录器
cd ../chronicle
npm install
```

### 步骤4: 配置API密钥 (可选但推荐)
```bash
# 配置Changlee混合AI服务
export GEMINI_API_KEY="your_gemini_api_key"        # Google Gemini (推荐)
export DEEPSEEK_API_KEY="your_deepseek_api_key"    # DeepSeek (备选)
export OPENAI_API_KEY="your_openai_api_key"        # OpenAI (可选)

# 配置RAG系统
export DEEPSEEK_API_KEY="your_deepseek_api_key"    # 用于RAG智能问答

# 配置BovineInsight系统
export GLM_API_KEY="your_glm_api_key"              # 智谱GLM-4V

# 配置AI服务偏好
export PREFERRED_AI_SERVICE="auto"                 # auto, local, gemini, deepseek
export HYBRID_AI_ENABLED="true"                    # 启用混合AI
export LOCAL_AI_ENABLED="true"                     # 启用本地AI
```

---

## 🎮 使用示例

### 🤖 RAG智能问答
1. 上传文档 (PDF、Word、TXT等)
2. 等待文档处理完成
3. 开始智能问答对话
4. 查看聊天历史和文档引用

### 🐱 Changlee学习助手
1. 启动桌面宠物应用
2. 选择AI服务类型 (本地AI/Gemini/DeepSeek)
3. 与长离AI进行个性化学习对话
4. 使用学习胶囊功能记忆单词
5. 在魔法沙滩进行拼写练习
6. 查看学习进度和AI服务状态

### 🐄 BovineInsight分析
1. 上传牛只图像
2. 选择分析模式 (身份识别/体况评分)
3. 查看AI分析结果
4. 导出专家级分析报告

### 📊 Chronicle记录
1. 启动实验记录会话
2. 进行科研工作
3. 停止记录会话
4. 查看AI生成的实验报告

---

## 🔍 故障排除

### 常见问题

#### Q1: Python依赖安装失败
```bash
# 解决方案: 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### Q2: Node.js依赖安装失败
```bash
# 解决方案: 使用淘宝镜像
npm install --registry https://registry.npmmirror.com
```

#### Q3: AI模型加载失败
```bash
# 解决方案: 检查网络连接，模型会自动下载
# 或手动下载模型到指定目录
```

#### Q4: 端口被占用
```bash
# 解决方案: 修改配置文件中的端口号
# 或停止占用端口的进程
```

### 🆘 获取帮助
- **GitHub Issues**: [问题反馈](https://github.com/novenazgarfield/research-workstation/issues)
- **文档中心**: 查看详细技术文档
- **社区讨论**: [GitHub Discussions](https://github.com/novenazgarfield/research-workstation/discussions)

---

## 🎯 下一步

### 🌟 推荐功能
1. **尝试本地AI对话**: 体验隐私保护的智能对话
2. **上传文档进行问答**: 测试RAG系统的智能检索
3. **使用BovineInsight分析**: 体验博士级AI分析能力
4. **记录学习过程**: 使用Chronicle跟踪学习进度

### 📚 深入学习
- 阅读 [项目架构文档](../PROJECT_ARCHITECTURE.md)
- 查看 [更新日志](../../CHANGELOG.md)
- 了解 [项目状态](../../PROJECT_STATUS.md)

### 🤝 参与贡献
- Fork项目并提交改进
- 报告bug和提出建议
- 分享使用经验和最佳实践

---

## 📊 性能优化建议

### 🚀 提升性能
```bash
# 1. 使用GPU加速 (如果有NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 2. 启用模型量化 (减少内存使用)
export USE_QUANTIZATION=true

# 3. 调整并发设置
export MAX_WORKERS=4
```

### 💾 节省内存
```bash
# 1. 使用较小的AI模型
export MODEL_SIZE=small

# 2. 启用内存优化
export MEMORY_OPTIMIZATION=true

# 3. 定期清理缓存
python -c "import torch; torch.cuda.empty_cache()"
```

---

## 🎉 恭喜！

您已经成功启动了Research Workstation！现在可以：

- ✅ 使用RAG系统进行智能问答
- ✅ 与Changlee AI进行学习对话  
- ✅ 体验BovineInsight的专业分析
- ✅ 记录和分析实验过程

**享受AI驱动的智能科研体验吧！** 🚀✨

---

*如果您觉得这个项目有用，请给我们一个⭐Star！*