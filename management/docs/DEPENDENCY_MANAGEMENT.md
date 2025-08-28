# 📦 N.S.S-Novena-Garfield 依赖管理指南

## 📋 依赖文件结构

### 主要依赖文件
- `/workspace/requirements.txt` - **项目主依赖文件** (整合所有Python系统)
- `management/deployment/.env.template` - 环境变量配置模板
- `management/config/global.config.js` - 全局配置管理

### 子系统依赖文件
- `systems/rag-system/requirements.txt` - RAG智能系统依赖
- `systems/bovine-insight/requirements.txt` - Bovine洞察系统依赖  
- `systems/genome-nebula/requirements.txt` - Genome基因分析依赖
- `systems/nexus/backend/requirements.txt` - Nexus后端依赖

## 🎯 依赖分类说明

### 1. 🌐 核心Web框架
用于所有Web服务的基础框架：
- **Streamlit**: RAG系统主界面
- **FastAPI**: 高性能API服务
- **Flask**: 轻量级Web应用
- **WebSockets**: 实时通信支持

### 2. 🤖 人工智能与机器学习
支持AI功能的核心库：
- **PyTorch/TensorFlow**: 深度学习框架
- **Transformers**: 预训练模型库
- **FAISS**: 向量相似性搜索
- **OpenCV**: 计算机视觉处理

### 3. 🧬 生物信息学 (Genome系统专用)
基因组分析专用库：
- **BioPython**: 生物信息学工具包
- **pysam**: SAM/BAM文件处理
- **cyvcf2**: VCF文件处理

### 4. 📊 数据科学与分析
数据处理和分析工具：
- **NumPy/Pandas**: 数据处理基础
- **Matplotlib/Plotly**: 数据可视化
- **Scikit-learn**: 机器学习算法

### 5. 📄 文档处理 (RAG系统)
多格式文档解析：
- **PyMuPDF**: PDF处理
- **python-docx**: Word文档
- **openpyxl**: Excel文件

## 🚀 安装指南

### 完整安装 (推荐)
```bash
# 安装所有依赖
pip install -r requirements.txt
```

### 按需安装
```bash
# 仅安装核心Web框架
pip install streamlit fastapi uvicorn flask flask-cors websockets

# 仅安装AI/ML相关
pip install torch torchvision transformers sentence-transformers faiss-cpu

# 仅安装数据科学工具
pip install numpy pandas matplotlib seaborn plotly scikit-learn
```

### Docker环境安装
```bash
# 使用Docker Compose (推荐)
cd management/deployment
docker compose up -d

# 手动构建Docker镜像
docker build -t nss-system .
```

## ⚙️ 环境配置

### Python版本要求
- **最低要求**: Python 3.8+
- **推荐版本**: Python 3.11+
- **最佳性能**: Python 3.11.x

### 系统依赖
某些Python包需要系统级依赖：

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    ffmpeg \
    graphviz \
    build-essential \
    python3-dev
```

#### macOS
```bash
brew install tesseract ffmpeg graphviz
```

#### Windows
- 安装 Visual C++ Build Tools
- 下载并安装 Tesseract OCR
- 安装 FFmpeg

### GPU支持 (可选)
如果有NVIDIA GPU，可启用GPU加速：

```bash
# 安装CUDA支持
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 替换CPU版本为GPU版本
pip uninstall faiss-cpu
pip install faiss-gpu
```

## 🔧 依赖管理最佳实践

### 1. 虚拟环境
始终使用虚拟环境：
```bash
# 创建虚拟环境
python -m venv nss-env

# 激活虚拟环境
source nss-env/bin/activate  # Linux/macOS
# 或
nss-env\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 依赖更新
定期更新依赖包：
```bash
# 检查过时的包
pip list --outdated

# 更新特定包
pip install --upgrade package_name

# 生成新的requirements.txt
pip freeze > requirements_new.txt
```

### 3. 依赖冲突解决
如遇到依赖冲突：
```bash
# 使用pip-tools管理依赖
pip install pip-tools

# 创建requirements.in文件（只列出直接依赖）
# 生成锁定版本的requirements.txt
pip-compile requirements.in
```

## 📊 依赖统计

### 按类别统计
- **Web框架**: 6个包
- **AI/ML**: 15个包  
- **生物信息学**: 4个包
- **数据科学**: 8个包
- **文档处理**: 5个包
- **数据库**: 4个包
- **工具库**: 12个包
- **开发工具**: 8个包

### 总计
- **核心依赖**: ~62个Python包
- **可选依赖**: ~8个包
- **系统依赖**: ~4个系统包

## 🐛 常见问题

### 1. 安装失败
```bash
# 升级pip和setuptools
pip install --upgrade pip setuptools wheel

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 2. 内存不足
```bash
# 分批安装大型包
pip install torch torchvision --no-cache-dir
pip install tensorflow --no-cache-dir
```

### 3. 版本冲突
```bash
# 创建新的虚拟环境
python -m venv fresh-env
source fresh-env/bin/activate
pip install -r requirements.txt
```

### 4. GPU支持问题
```bash
# 检查CUDA版本
nvidia-smi

# 安装对应CUDA版本的PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 🔄 依赖更新流程

### 1. 子系统依赖更新
当子系统添加新依赖时：
1. 更新子系统的 `requirements.txt`
2. 将新依赖添加到主 `requirements.txt`
3. 按分类整理并添加注释
4. 更新Docker文件
5. 测试完整安装流程

### 2. 版本升级
定期升级依赖版本：
1. 检查安全更新
2. 测试兼容性
3. 更新版本号
4. 更新文档

### 3. 依赖清理
定期清理不需要的依赖：
1. 分析实际使用情况
2. 移除未使用的包
3. 合并重复功能的包
4. 优化安装大小

## 📈 性能优化

### 1. 安装优化
```bash
# 使用预编译wheel包
pip install --only-binary=all -r requirements.txt

# 并行安装
pip install -r requirements.txt --upgrade --force-reinstall
```

### 2. 运行时优化
- 使用虚拟环境隔离
- 启用GPU加速（如可用）
- 配置合适的内存限制
- 使用缓存机制

## 🔒 安全考虑

### 1. 依赖安全扫描
```bash
# 安装安全扫描工具
pip install safety

# 扫描已知漏洞
safety check -r requirements.txt
```

### 2. 版本锁定
- 使用具体版本号而非范围
- 定期更新安全补丁
- 监控安全公告

---

📝 **维护说明**: 本文档随项目依赖变化而更新，请保持同步。