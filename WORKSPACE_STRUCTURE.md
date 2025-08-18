# 🗂️ Workspace 文件夹结构

## 📁 整理后的目录结构

```
workspace/
├── 📁 rag_system/              # 🎯 主要RAG系统项目
│   ├── common/                 # 共享组件
│   ├── config/                 # 配置文件
│   ├── desktop/                # 桌面端界面
│   ├── mobile/                 # 移动端界面
│   ├── public/                 # 公共访问应用
│   ├── logs/                   # 系统日志
│   └── tests/                  # 系统测试
│
├── 📁 backend/                 # 后端服务架构
│   ├── api-gateway/            # API网关
│   ├── auth-service/           # 认证服务
│   ├── compute-service/        # 计算服务
│   └── file-service/           # 文件服务
│
├── 📁 frontend/                # 前端项目
│
├── 📁 systems/                 # 其他系统项目
│   ├── desktop-pet/            # 桌面宠物系统
│   ├── ml-cattle-model/        # 机器学习模型
│   ├── molecular-dynamics/     # 分子动力学
│   ├── rag-system/             # RAG系统备份
│   └── sequence-analysis/      # 序列分析
│
├── 📁 shared/                  # 共享资源
│   ├── configs/                # 共享配置
│   ├── database/               # 数据库文件
│   ├── models/                 # 共享模型
│   └── utils/                  # 工具函数
│
├── 📁 data/                    # 数据文件
│   ├── models/                 # 模型文件
│   ├── processed/              # 处理后数据
│   ├── raw/                    # 原始数据
│   └── results/                # 结果数据
│
├── 📁 docs/                    # 📚 所有文档
│   ├── CHANGELOG.md            # 更新日志
│   ├── DEPLOYMENT_SUMMARY.md   # 部署总结
│   ├── PROJECT_SUMMARY.md      # 项目总结
│   ├── README.md               # 主要说明
│   └── ...                     # 其他文档
│
├── 📁 tests/                   # 🧪 测试文件
│   ├── *_rag.py               # RAG系统测试
│   ├── colab_*.py             # Colab相关测试
│   └── streamlit_app.py       # Streamlit测试
│
├── 📁 logs/                    # 📋 日志文件
│   ├── *_streamlit.log        # Streamlit日志
│   ├── cloudflare*.log        # Cloudflare日志
│   └── ngrok.log              # Ngrok日志
│
├── 📁 temp/                    # 🗃️ 临时文件
│   ├── test_*.txt             # 测试文档
│   ├── demo_*.pdf             # 演示文件
│   └── *.png                  # 图片文件
│
├── 📁 tools/                   # 🔧 工具文件
│   ├── frp_0.52.3_linux_amd64/ # FRP内网穿透工具
│   └── pwa_demo/              # PWA演示
│
├── 📁 archive/                 # 📦 归档文件
│   ├── *.tar.gz               # 压缩包
│   ├── *.ipynb                # Jupyter笔记本
│   └── *.sh                   # 脚本文件
│
├── 📁 configs/                 # ⚙️ 配置目录
│
├── 📄 requirements.txt         # Python依赖
├── 📄 requirements_chat.txt    # 聊天功能依赖
└── 📄 WORKSPACE_STRUCTURE.md   # 本文档
```

## 🎯 主要项目

### RAG系统 (rag_system/)
- **状态**: ✅ 正在运行
- **访问地址**: https://beer-entries-joel-reunion.trycloudflare.com
- **功能**: 完整的RAG智能对话系统，支持用户管理、多端适配

### 后端服务 (backend/)
- **架构**: 微服务架构
- **服务**: API网关、认证、计算、文件服务

### 其他系统 (systems/)
- **桌面宠物**: 桌面交互系统
- **机器学习**: 各种ML模型
- **分子动力学**: 科学计算项目

## 🧹 整理说明

### 已整理的文件类型
- ✅ **文档文件**: 所有.md文件移至docs/
- ✅ **日志文件**: 所有.log文件移至logs/
- ✅ **测试文件**: 所有测试相关.py文件移至tests/
- ✅ **临时文件**: 测试文档、图片等移至temp/
- ✅ **工具文件**: 第三方工具移至tools/
- ✅ **归档文件**: 压缩包、脚本等移至archive/

### 保留在根目录的文件
- `requirements.txt` - 主要依赖文件
- `requirements_chat.txt` - 聊天功能依赖
- 各个主要项目文件夹

## 📊 文件统计

- **主要项目**: 1个 (rag_system)
- **文档文件**: 13个
- **测试文件**: 12个
- **日志文件**: 10个
- **临时文件**: 5个
- **工具项目**: 2个
- **归档文件**: 3个

## 🚀 当前运行状态

- **RAG系统**: ✅ 运行中
- **公网访问**: ✅ 可用
- **Cloudflare Tunnel**: ✅ 活跃
- **所有功能**: ✅ 正常