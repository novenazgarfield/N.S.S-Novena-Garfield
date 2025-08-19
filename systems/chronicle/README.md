# Chronicle: AI-Driven Automated Experiment Recorder

## 🎯 项目愿景

创建一个强大的、无UI的后台微服务 (Headless Microservice)。该服务作为个人科研工作站的"黑匣子"，负责在后台静默记录指定的科研项目活动，并通过一个智能分析引擎，将原始、复杂的日志数据，提炼成简洁、聚焦关键点的结构化报告。

## 🏗️ 核心架构

采用"双层日志系统"和标准的RESTful API接口：

```
┌─────────────────────────────────────────────────────────────┐
│                       Chronicle                             │
├─────────────────────────────────────────────────────────────┤
│  第三层: API接口 (The Interface)                             │
│  ├─ POST /sessions/start                                   │
│  ├─ POST /sessions/{id}/stop                               │
│  ├─ GET /reports/{id}                                      │
│  └─ GET /reports/{id}/raw                                  │
├─────────────────────────────────────────────────────────────┤
│  第二层: 数据分析引擎 (The Analyst)                          │
│  ├─ 模式识别                                               │
│  ├─ AI智能摘要 (LLM Integration)                           │
│  ├─ 关键信息提取                                           │
│  └─ 报告格式化                                             │
├─────────────────────────────────────────────────────────────┤
│  第一层: 数据采集服务 (The Collector)                       │
│  ├─ 文件系统监控 (chokidar)                               │
│  ├─ 活动窗口监控 (active-win)                             │
│  ├─ 命令行监控 (WSL/Bash/PowerShell)                      │
│  └─ SQLite 原始日志数据库                                  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 项目结构

```
chronicle/
├── src/
│   ├── collector/          # 模块一：数据采集服务
│   │   ├── file-monitor.js
│   │   ├── window-monitor.js
│   │   ├── command-monitor.js
│   │   └── database.js
│   ├── analyst/            # 模块二：智能分析引擎
│   │   ├── pattern-recognizer.js
│   │   ├── ai-summarizer.js
│   │   └── report-generator.js
│   ├── api/                # 模块三：API服务
│   │   ├── server.js
│   │   ├── routes/
│   │   └── middleware/
│   ├── shared/             # 共享工具和配置
│   │   ├── config.js
│   │   ├── logger.js
│   │   └── utils.js
│   └── daemon/             # 守护进程
│       └── service.js
├── tests/                  # 测试文件
├── docs/                   # 文档
├── scripts/                # 部署和管理脚本
├── package.json
└── README.md
```

## 🚀 快速开始

### 安装依赖
```bash
npm install
```

### 启动服务
```bash
# 开发模式
npm run dev

# 生产模式
npm start

# 守护进程模式
npm run daemon
```

### API使用示例
```bash
# 启动记录会话
curl -X POST http://localhost:3000/sessions/start \
  -H "Content-Type: application/json" \
  -d '{"project_name": "my-experiment", "project_path": "/path/to/project"}'

# 停止记录会话
curl -X POST http://localhost:3000/sessions/{session_id}/stop

# 获取精炼报告
curl http://localhost:3000/reports/{session_id}

# 获取原始日志
curl http://localhost:3000/reports/{session_id}/raw
```

## 🔧 核心功能

### 1. 数据采集服务 (The Collector)
- **文件系统监控**: 实时监控项目文件的创建、修改、删除
- **活动窗口监控**: 记录与文件变动相关的前台应用程序
- **命令行监控**: 捕获WSL/Bash/PowerShell命令及其输出
- **完整流捕获**: 记录stdout、stderr的全部内容
- **数据持久化**: 原始数据存储到SQLite数据库

### 2. 智能分析引擎 (The Analyst)
- **模式识别**: 自动识别Stack Trace、编译错误等常见模式
- **AI智能摘要**: 使用LLM对长日志进行智能分析
- **关键信息提取**: 提取关键行号、关键词组
- **报告格式化**: 生成结构化的精炼报告

### 3. API服务 (The Interface)
- **RESTful API**: 标准的HTTP接口
- **会话管理**: 支持多个并发记录会话
- **报告生成**: 按需生成精炼或原始报告
- **跨平台兼容**: 支持Windows、Linux、macOS

## 🤖 AI集成

项目集成了大型语言模型(LLM)进行智能分析：

```json
{
  "summary": "编译错误：未找到头文件 'opencv2/opencv.hpp'",
  "key_lines": [15, 23, 45],
  "key_phrases": ["fatal error", "opencv2/opencv.hpp", "No such file"]
}
```

## 📊 数据流程

1. **数据采集**: 后台守护进程持续监控项目活动
2. **原始存储**: 所有数据完整存储到SQLite数据库
3. **智能分析**: 按需调用AI引擎分析原始数据
4. **报告生成**: 生成结构化的精炼报告
5. **API输出**: 通过RESTful API提供数据访问

## 🔒 安全与隐私

- 本地数据存储，不上传敏感信息
- 可配置的监控范围和过滤规则
- 支持数据加密和访问控制
- 完整的审计日志

## 📈 扩展性

- 插件化架构，支持自定义监控器
- 可配置的AI分析规则
- 支持多种输出格式（JSON、Markdown、HTML）
- 集成第三方工具和服务

## 🛠️ 技术栈

- **后端**: Node.js + Express/FastAPI
- **数据库**: SQLite
- **文件监控**: chokidar
- **窗口监控**: active-win
- **AI集成**: Gemini API / OpenAI API
- **进程管理**: PM2

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**Chronicle** - 让每一次实验都有迹可循 🔬✨