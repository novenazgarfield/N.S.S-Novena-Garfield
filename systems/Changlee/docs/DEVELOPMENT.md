# 长离的学习胶囊 - 开发文档

## 项目概述

"长离的学习胶囊"是一款以情感陪伴为核心的桌面宠物英语学习应用。通过AI伙伴"长离"的陪伴，将枯燥的单词记忆转化为有趣的互动体验。

## 技术架构

### 整体架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Electron      │    │   React UI      │    │   Node.js       │
│   主进程        │◄──►│   渲染进程      │◄──►│   后端服务      │
│                 │    │                 │    │                 │
│ • 窗口管理      │    │ • 桌宠组件      │    │ • API服务       │
│ • 系统集成      │    │ • 学习界面      │    │ • 数据库管理    │
│ • 托盘管理      │    │ • 动画效果      │    │ • AI集成        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   SQLite DB     │
                    │                 │
                    │ • 单词数据      │
                    │ • 学习记录      │
                    │ • 用户设置      │
                    └─────────────────┘
```

### 核心模块

#### 1. 桌宠核心模块 (Pet Core Module)
- **位置**: `src/renderer/components/DesktopPet.jsx`
- **功能**: 
  - 可拖拽的桌面宠物
  - 多种动画状态（idle, excited, dragging）
  - 漂流瓶推送显示
  - 用户交互响应

#### 2. 学习胶囊模块 (Learning Capsule Module)
- **位置**: `src/renderer/components/LearningCapsule.jsx`
- **功能**:
  - 单词展示界面
  - AI生成内容显示
  - 发音功能
  - 可展开的学习内容

#### 3. 魔法沙滩模块 (Magic Beach Module)
- **位置**: `src/renderer/components/MagicBeach.jsx`
- **功能**:
  - Canvas描摹练习
  - 拼写输入检查
  - 游戏化反馈
  - 进度跟踪

#### 4. AI服务模块 (AI Service Module)
- **位置**: `src/backend/services/AIService.js`
- **功能**:
  - Gemini API集成
  - 内容生成（记忆故事、语境故事、学习技巧）
  - 长离人设维护
  - 错误处理和备用内容

#### 5. 学习服务模块 (Learning Service Module)
- **位置**: `src/backend/services/LearningService.js`
- **功能**:
  - 间隔重复算法（SM-2）
  - 学习进度跟踪
  - 统计数据计算
  - 学习建议生成

## 开发环境设置

### 环境要求
- Node.js 16+
- npm 8+
- Python 3.8+ (用于某些native模块)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd Changlee
```

2. **安装依赖**
```bash
# 安装主项目依赖
npm install

# 安装渲染进程依赖
cd src/renderer
npm install
cd ../..
```

3. **配置环境变量**
```bash
# 创建 .env 文件
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

4. **启动开发环境**
```bash
# 方式1: 使用启动脚本
node start.js

# 方式2: 分别启动各服务
npm run backend    # 启动后端服务
npm run electron-dev  # 启动Electron开发模式
```

## 核心功能实现

### 1. 间隔重复算法

基于SM-2算法实现，核心公式：
```javascript
// 计算新的难度因子
newEaseFactor = Math.max(1.3, easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)));

// 计算复习间隔
if (reviewCount === 1) {
  newInterval = 1;
} else if (reviewCount === 2) {
  newInterval = 6;
} else {
  newInterval = Math.round(previousInterval * easeFactor);
}
```

### 2. AI内容生成

使用Gemini API生成个性化学习内容：
```javascript
const prompt = `
你是长离，一只温柔智慧的小猫AI伙伴。请为单词"${word}"创作一个温馨的记忆故事。
要求：
1. 以第一人称"我"（长离）的视角讲述
2. 故事要温暖有趣，包含这个单词的使用场景
3. 体现长离的猫咪特质和温柔性格
4. 故事长度控制在100-150字
`;
```

### 3. 推送系统

智能推送机制：
- 每日推送限制（默认3次）
- 冷却时间控制（默认2小时）
- 用户活动检测
- 最佳时机算法

### 4. 桌宠动画

使用Framer Motion实现流畅动画：
```javascript
const getAnimationVariants = () => {
  switch (animationState) {
    case 'idle':
      return {
        scale: [1, 1.05, 1],
        rotate: [0, -2, 2, 0],
        transition: { duration: 3, repeat: Infinity }
      };
    case 'excited':
      return {
        scale: [1, 1.2, 1],
        y: [0, -10, 0],
        transition: { duration: 0.6, repeat: 3 }
      };
  }
};
```

## 数据库设计

### 核心表结构

#### words 表
```sql
CREATE TABLE words (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  word TEXT UNIQUE NOT NULL,
  phonetic TEXT,
  definition TEXT NOT NULL,
  difficulty INTEGER DEFAULT 1,
  category TEXT DEFAULT 'general',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### learning_records 表
```sql
CREATE TABLE learning_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  word_id INTEGER NOT NULL,
  status TEXT DEFAULT 'new',
  review_count INTEGER DEFAULT 0,
  correct_count INTEGER DEFAULT 0,
  ease_factor REAL DEFAULT 2.5,
  interval_days INTEGER DEFAULT 1,
  next_review DATETIME,
  FOREIGN KEY (word_id) REFERENCES words (id)
);
```

## API接口文档

### 后端API

#### 获取下一个学习单词
```
GET /api/words/next
Response: {
  "success": true,
  "data": {
    "id": 1,
    "word": "abandon",
    "definition": "v. 放弃，抛弃",
    "phonetic": "/əˈbændən/",
    "difficulty": 2
  }
}
```

#### 生成AI内容
```
POST /api/ai/generate
Body: {
  "word": "abandon",
  "definition": "v. 放弃，抛弃",
  "difficulty": 2
}
Response: {
  "success": true,
  "data": {
    "memoryStory": "...",
    "contextStory": "...",
    "learningTips": "..."
  }
}
```

#### 提交拼写结果
```
POST /api/words/:id/spelling
Body: {
  "isCorrect": true,
  "timeSpent": 5000,
  "mistakes": 0
}
Response: {
  "success": true,
  "data": {
    "nextReview": "2025-08-15T10:00:00Z",
    "status": "learning"
  }
}
```

## 测试指南

### 单元测试
```bash
npm test
```

### 集成测试
```bash
npm run test:integration
```

### E2E测试
```bash
npm run test:e2e
```

## 构建和部署

### 开发构建
```bash
npm run build
```

### 生产构建
```bash
npm run build:prod
```

### 打包应用
```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

## 性能优化

### 1. 内存管理
- 限制缓存大小
- 及时清理未使用的资源
- 使用对象池减少GC压力

### 2. 渲染优化
- 使用React.memo减少不必要的重渲染
- 虚拟化长列表
- 懒加载组件

### 3. 数据库优化
- 创建适当的索引
- 定期执行VACUUM
- 使用事务批量操作

## 调试技巧

### 1. Electron调试
```bash
# 启用开发者工具
ELECTRON_IS_DEV=1 npm run electron
```

### 2. 后端调试
```bash
# 启用调试模式
DEBUG=* npm run backend
```

### 3. 日志查看
- 主进程日志：`logs/main.log`
- 渲染进程日志：浏览器开发者工具
- 后端日志：`logs/backend.log`

## 贡献指南

### 代码规范
- 使用ESLint和Prettier
- 遵循React Hooks规范
- 编写有意义的提交信息

### 提交流程
1. Fork项目
2. 创建功能分支
3. 编写测试
4. 提交代码
5. 创建Pull Request

## 常见问题

### Q: 桌宠不显示怎么办？
A: 检查Electron进程是否正常启动，查看主进程日志。

### Q: AI内容生成失败？
A: 检查Gemini API密钥是否正确配置，网络连接是否正常。

### Q: 数据库连接失败？
A: 检查数据库文件权限，确保目录可写。

### Q: 推送不工作？
A: 检查推送设置是否启用，是否在静默时间内。

## 更新日志

### v1.0.0 (2025-08-14)
- 初始版本发布
- 实现核心桌宠功能
- 集成Gemini AI
- 完成学习系统
- 添加魔法沙滩练习

---

*更多信息请参考项目Wiki或联系开发团队*