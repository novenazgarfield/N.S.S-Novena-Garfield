# RAG系统项目结构

## 📁 项目架构

```
rag_system/
├── 📁 common/              # 共享组件和工具
│   ├── admin_panel.py      # 管理员面板
│   ├── base_components.py  # 基础组件
│   ├── language_config.py  # 语言配置
│   ├── settings_panel.py   # 设置面板
│   └── user_management.py  # 用户管理
│
├── 📁 config/              # 配置文件
│   ├── sessions.json       # 会话数据
│   └── users.json          # 用户数据
│
├── 📁 desktop/             # 桌面端界面
│   └── desktop_interface.py
│
├── 📁 mobile/              # 移动端界面
│   └── mobile_interface.py
│
├── 📁 public/              # 公共访问应用
│   └── public_mobile_app.py # 公共移动端应用
│
├── 📁 logs/                # 日志文件
│   ├── desktop_streamlit.log
│   ├── mobile_streamlit.log
│   ├── public_mobile.log
│   └── universal_streamlit.log
│
├── 📁 tests/               # 测试文件（预留）
│
├── 📄 desktop_app.py       # 桌面端主程序
├── 📄 mobile_app.py        # 移动端主程序
├── 📄 universal_app.py     # 通用自适应主程序
├── 📄 README.md            # 项目说明
└── 📄 PROJECT_STRUCTURE.md # 项目结构说明
```

## 🚀 应用程序说明

### 主要应用程序
- **desktop_app.py**: 桌面端专用应用
- **mobile_app.py**: 移动端专用应用  
- **universal_app.py**: 自动检测设备类型的通用应用
- **public/public_mobile_app.py**: 公共访问的移动端应用

### 共享组件
- **common/**: 所有应用共享的组件和工具
- **config/**: 用户数据和会话配置
- **logs/**: 应用运行日志

## 🔧 启动方式

### 公共移动端应用（当前运行）
```bash
cd /workspace/rag_system
streamlit run public/public_mobile_app.py --server.port 51657 --server.address 0.0.0.0 --server.enableCORS true --server.enableXsrfProtection false
```

### 其他应用
```bash
# 桌面端
streamlit run desktop_app.py --server.port 8501

# 移动端
streamlit run mobile_app.py --server.port 8502

# 通用自适应
streamlit run universal_app.py --server.port 8503
```

## 📱 当前运行状态

- **服务地址**: http://localhost:51657
- **运行应用**: public/public_mobile_app.py
- **功能状态**: ✅ 全部功能正常
- **用户系统**: ✅ 登录/注册正常
- **聊天功能**: ✅ AI对话正常
- **设置功能**: ✅ 主题切换等正常

## 🏗️ 架构特点

1. **前后端分离**: 界面组件与业务逻辑分离
2. **模块化设计**: 共享组件可复用
3. **多端适配**: 支持桌面端、移动端、通用端
4. **用户管理**: 完整的用户认证和会话管理
5. **配置管理**: 集中的配置文件管理
6. **日志系统**: 完整的日志记录和管理