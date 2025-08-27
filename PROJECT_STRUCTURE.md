# 🏗️ N.S.S Novena Garfield 项目结构

## 📁 核心目录结构

```
N.S.S-Novena-Garfield/
├── 📋 README.md                    # 项目主文档
├── 📋 CHANGELOG.md                 # 更新日志
├── 📋 requirements.txt             # Python依赖
├── 🚀 start_ai_system.py          # AI系统启动脚本
├── 📋 PROJECT_STRUCTURE.md         # 项目结构说明 (本文件)
│
├── 🔧 api_management/              # API管理模块
│   ├── simple_energy_server.py    # 中央能源数据库服务器
│   ├── simple_dynamic_rag.py      # 动态RAG系统服务器
│   ├── test_complete_system.py    # 完整系统测试
│   ├── final_system_demo.py       # 系统演示脚本
│   ├── central_energy_db.py       # 中央能源数据库核心
│   ├── energy_api_server.py       # 能源API服务器
│   ├── api_config.py              # API配置管理
│   ├── config/                    # 配置文件目录
│   ├── docs/                      # API文档
│   └── integrations/              # 集成模块
│
├── 🖥️ systems/                     # 系统模块
│   ├── nexus/                     # NEXUS主控台
│   │   └── index.html             # 主界面 (已集成AI配置管理)
│   ├── rag-system/                # RAG系统
│   ├── Changlee/                  # Changlee系统
│   ├── bovine-insight/            # 牛类洞察系统
│   ├── chronicle/                 # 编年史系统
│   ├── genome-jigsaw/             # 基因拼图系统
│   └── molecular-simulation-toolkit/ # 分子模拟工具包
│
├── 📚 docs/                        # 文档目录
│   ├── status/                    # 状态文档
│   │   ├── SYSTEM_STATUS_FINAL.md # 最终系统状态
│   │   ├── PROJECT_STATUS_FINAL.md # 项目状态
│   │   ├── NEXUS_SYSTEM_STATUS.md # NEXUS系统状态
│   │   └── ...
│   ├── reports/                   # 报告文档
│   │   ├── PERFORMANCE_OPTIMIZATION_REPORT.md
│   │   ├── MEMORY_SYSTEM.md
│   │   ├── INTEGRATION_SUCCESS.md
│   │   └── ...
│   ├── guides/                    # 指南文档
│   │   ├── QUICK_START.md
│   │   ├── RAG_CONNECTION_GUIDE.md
│   │   ├── TUNNEL_ACCESS_GUIDE.md
│   │   └── ...
│   └── summaries/                 # 总结文档
│
├── 🧪 tests/                       # 测试目录
│   ├── integration/               # 集成测试
│   ├── performance/               # 性能测试
│   └── streamlit_app.py          # Streamlit测试应用
│
├── 📊 data/                        # 数据目录
│   ├── raw/                       # 原始数据
│   ├── processed/                 # 处理后数据
│   ├── samples/                   # 示例数据
│   └── exports/                   # 导出数据
│
├── 🛠️ tools/                       # 工具目录
│   ├── deployment/                # 部署工具
│   ├── scripts/                   # 脚本工具
│   ├── pwa_demo/                  # PWA演示
│   └── frp_0.52.3_linux_amd64/   # FRP内网穿透工具
│
├── 📦 archive/                     # 归档目录
│   ├── RAG_System_Colab.ipynb     # Colab笔记本
│   ├── quick_deploy.sh            # 快速部署脚本
│   └── research-workstation.tar.gz # 研究工作站打包
│
├── 📝 logs/                        # 日志目录
│   ├── archive/                   # 历史日志
│   └── *.log                      # 各种服务日志
│
└── 🗂️ temp/                        # 临时文件目录
    ├── demo_rag_document.pdf      # 演示文档
    ├── mobile_test.html           # 移动端测试
    └── rag_qrcode.png            # RAG二维码
```

## 🎯 核心功能模块

### 1. 🔋 中央能源数据库 (Phase 1)
- **位置**: `api_management/simple_energy_server.py`
- **端口**: 56420
- **功能**: AI配置统一管理、模型选择、密钥管理

### 2. 🖥️ NEXUS工程主控台 (Phase 2)  
- **位置**: `systems/nexus/index.html`
- **端口**: 8080
- **功能**: 统一界面、AI配置管理集成到Settings

### 3. 🤖 动态AI系统 (Phase 3)
- **位置**: `api_management/simple_dynamic_rag.py`
- **端口**: 60010
- **功能**: 动态模型调用、智能配置选择

## 🚀 快速启动

```bash
# 启动完整AI系统
python start_ai_system.py

# 访问NEXUS界面
http://localhost:8080

# AI配置管理
点击右上角⚙️ → AI模型配置 → 管理AI配置
```

## 📋 主要改进

### ✅ 界面优化
- AI配置管理集成到Settings页面
- 移除独立的🧠按钮，界面更整洁
- 添加AI状态实时监控

### ✅ 文件结构优化
- API相关文件统一到`api_management/`
- 文档按类型分类到`docs/`子目录
- 清理临时文件和有问题的版本

### ✅ 功能增强
- 统一的系统启动脚本
- 实时AI状态检查
- 更好的用户体验

## 🔗 相关链接

- 📚 [完整文档](docs/)
- 🧪 [测试指南](tests/)
- 🛠️ [部署工具](tools/)
- 📊 [系统状态](docs/status/SYSTEM_STATUS_FINAL.md)