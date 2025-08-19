# 桌宠系统模块化结构说明

## 📁 新的文件夹结构

```
src/renderer/
├── features/                    # 功能模块
│   ├── music-player/           # 音乐播放模块
│   │   ├── components/         # 音乐播放相关组件
│   │   ├── hooks/             # 音乐播放相关Hooks
│   │   ├── services/          # 音乐服务
│   │   └── index.js           # 模块入口
│   ├── rag-chat/              # RAG聊天模块
│   │   ├── components/        # 聊天相关组件
│   │   ├── hooks/             # 聊天相关Hooks
│   │   └── index.js           # 模块入口
│   └── word-capsule/          # 背单词模块
│       ├── components/        # 学习相关组件
│       ├── hooks/             # 学习相关Hooks
│       ├── services/          # 单词服务
│       └── index.js           # 模块入口
├── components/                 # 通用组件
│   ├── Button.jsx             # 通用按钮组件
│   ├── Modal.jsx              # 通用模态框组件
│   ├── LoadingSpinner.jsx     # 加载动画组件
│   └── index.js               # 组件入口
├── services/                   # 通用服务
│   ├── ragService.js          # RAG服务
│   ├── apiClient.js           # API客户端
│   └── index.js               # 服务入口
├── hooks/                      # 通用Hooks
│   ├── useLocalStorage.js     # 本地存储Hook
│   ├── useAnimation.js        # 动画管理Hook
│   ├── useNotification.js     # 通知系统Hook
│   └── index.js               # Hooks入口
├── store/                      # 状态管理
│   ├── petStore.js            # 桌宠状态
│   ├── appStore.js            # 应用状态
│   └── index.js               # 状态入口
└── App.jsx                     # 主应用组件
```

## 🎵 音乐播放模块 (music-player)

### 组件
- **MusicPlayer**: 主音乐播放器组件
- **MusicControls**: 播放控制组件
- **PlaylistView**: 播放列表组件

### 功能
- 本地音乐文件扫描
- 音乐播放控制（播放/暂停/上一首/下一首）
- 音量控制和进度条
- 播放列表管理
- 桌宠动画联动（播放时切换到listening动画）

### 使用方法
```jsx
import { MusicPlayer } from './features/music-player';

<MusicPlayer onAnimationChange={handleAnimationChange} />
```

## 🤖 RAG聊天模块 (rag-chat)

### 组件
- **RagChat**: 主聊天界面组件
- **ChatMessage**: 聊天消息组件
- **ChatInput**: 聊天输入组件

### 功能
- 与RAG系统后端通信
- 智能问答对话
- 消息历史记录
- 参考资料显示
- 桌宠动画联动（思考时切换到thinking动画）

### 使用方法
```jsx
import { RagChat } from './features/rag-chat';

<RagChat onAnimationChange={handleAnimationChange} />
```

## 📚 背单词模块 (word-capsule)

### 组件
- **WordCapsule**: 主学习界面组件
- **LearningCapsule**: 单词学习组件（从原有组件迁移）
- **MagicBeach**: 拼写练习组件（从原有组件迁移）
- **WordProgress**: 学习进度组件

### 功能
- 单词学习和记忆
- AI生成的学习内容
- 拼写练习游戏
- 学习进度跟踪
- 经验值和等级系统
- 桌宠动画联动（学习时切换到studying动画）

### 使用方法
```jsx
import { WordCapsule } from './features/word-capsule';

<WordCapsule 
  onAnimationChange={handleAnimationChange}
  onInteraction={handlePetInteraction}
/>
```

## 🧩 通用组件

### Button
通用按钮组件，支持多种样式和状态
```jsx
import { Button } from './components';

<Button variant="primary" size="large" onClick={handleClick}>
  点击我
</Button>
```

### Modal
通用模态框组件，支持自定义内容和样式
```jsx
import { Modal } from './components';

<Modal isOpen={true} onClose={handleClose} title="标题">
  <p>模态框内容</p>
</Modal>
```

### LoadingSpinner
加载动画组件，支持多种样式
```jsx
import { LoadingSpinner } from './components';

<LoadingSpinner size="large" text="加载中..." type="emoji" emoji="🤔" />
```

## 🎣 通用Hooks

### useLocalStorage
本地存储管理Hook
```jsx
import { useLocalStorage } from './hooks';

const [value, setValue, removeValue] = useLocalStorage('key', defaultValue);
```

### useAnimation
动画状态管理Hook
```jsx
import { useAnimation } from './hooks';

const { currentAnimation, changeAnimation, queueAnimation } = useAnimation();
```

### useNotification
通知系统Hook
```jsx
import { useNotification } from './hooks';

const { showSuccess, showError, showPetNotification } = useNotification();
```

## 🏪 状态管理

### usePetStore
桌宠状态管理，包括：
- 桌宠基本信息（等级、经验、心情等）
- 当前动画和活动状态
- 学习统计数据
- 用户设置

### useAppStore
应用全局状态管理，包括：
- 当前活动模块
- 模块状态（激活/最小化）
- 通知系统
- 应用设置

## 🔧 服务层

### ragService
RAG系统通信服务，提供：
- 查询接口
- 文档管理
- 服务状态检查

### apiClient
通用API客户端，提供：
- HTTP请求封装
- 文件上传/下载
- 错误处理

## 🚀 使用指南

### 1. 激活模块
```jsx
// 通过状态管理激活模块
const { activateModule } = useAppStore();
activateModule('music-player');

// 或通过全局方法（供Electron调用）
window.activateModule('word-capsule');
```

### 2. 桌宠互动
```jsx
// 记录互动并触发动画
const { recordInteraction } = usePetStore();
recordInteraction('word_learned', { word: 'example' });
```

### 3. 显示通知
```jsx
const { showPetNotification } = useNotification();
showPetNotification('学习完成！', '🎉');
```

## 📈 优势

1. **模块化**: 每个功能独立开发和维护
2. **可复用**: 通用组件和Hooks可在多个模块中使用
3. **可扩展**: 易于添加新功能模块
4. **状态管理**: 统一的状态管理系统
5. **类型安全**: 清晰的接口定义
6. **性能优化**: 按需加载和渲染

## 🔄 迁移说明

原有的组件已经迁移到对应的功能模块中：
- `LearningCapsule.jsx` → `features/word-capsule/components/`
- `MagicBeach.jsx` → `features/word-capsule/components/`
- 新增了模块化的音乐播放和RAG聊天功能

所有原有功能保持兼容，同时增加了新的模块化架构支持。