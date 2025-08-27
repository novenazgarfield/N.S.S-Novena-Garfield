# 🐱 长离桌面宠物 - 3D/2D模型展示框架

## 📖 项目概述

这是一个为"Project: Changlee's Capsule"桌面宠物项目设计的灵活、可替换的3D/2D模型展示框架。该框架将**模型加载与渲染**的逻辑与**桌宠行为与交互**的逻辑彻底分离，实现了"换皮肤"式的模型替换能力。

## 🎯 核心设计目标

- ✅ **逻辑分离**: 渲染逻辑与业务逻辑完全解耦
- ✅ **模型可替换**: 支持从占位模型到精美3D/2D模型的无缝切换
- ✅ **双模式支持**: 同时支持3D和2D渲染模式
- ✅ **高性能**: 基于Three.js和PIXI.js的优化渲染
- ✅ **易扩展**: 模块化设计，便于添加新功能

## 🏗️ 架构设计

```
长离桌面宠物框架
├── 🎨 PetCanvas (渲染画布)
│   ├── 3D渲染 (Three.js)
│   └── 2D渲染 (PIXI.js)
├── 🔧 ModelLoader (模型加载器)
│   ├── 3D模型加载 (.gltf, .glb)
│   ├── 2D模型加载 (Live2D, Spine)
│   └── 占位模型生成
├── 🎭 AnimationController (动画控制器)
│   ├── 3D动画控制
│   ├── 2D动画控制
│   └── 程序化动画
└── 🧠 桌宠主逻辑 (业务层)
    ├── 行为决策
    ├── 状态管理
    └── 用户交互
```

## 📦 核心组件

### 1. PetCanvas - 模型舞台组件

**位置**: `components/PetCanvas.jsx`

**功能**: 桌面上专门用于渲染长离的透明画布

**特性**:
- 🎲 **3D模式**: Three.js WebGL渲染器，支持透明背景
- 🎨 **2D模式**: PIXI.js 2D渲染引擎
- 🔄 **模式切换**: 运行时动态切换渲染模式
- 📊 **性能监控**: 实时FPS和渲染统计
- 🐛 **调试模式**: 开发环境下的调试信息显示

**使用示例**:
```jsx
import PetCanvas from './components/PetCanvas.jsx';

<PetCanvas
  renderMode="3D"           // '3D' | '2D'
  width={400}
  height={400}
  transparent={true}
  onModelLoaded={handleModelLoaded}
  onAnimationComplete={handleAnimationComplete}
  ref={petCanvasRef}
/>
```

### 2. ModelLoader - 模型加载器服务

**位置**: `services/ModelLoader.js`

**功能**: 负责从硬盘读取模型文件并放到舞台上的"后台装卸工"

**支持格式**:
- 🎲 **3D模型**: .gltf, .glb (通过GLTFLoader)
- 🎨 **2D模型**: Live2D, Spine, 精灵图
- 🎯 **占位模型**: 程序化生成的几何体

**特性**:
- 📦 **模型缓存**: 避免重复加载
- ⏳ **加载进度**: 实时加载进度回调
- 🔄 **异步加载**: Promise基础的异步加载
- 🎨 **多种占位符**: 长离风格、立方体、球体等

**使用示例**:
```javascript
import { ModelLoader } from './services/ModelLoader.js';

const loader = new ModelLoader('3D');

// 加载占位模型
const placeholderModel = await loader.loadPlaceholder('changlee');

// 加载真实模型
const realModel = await loader.loadModel('/assets/models/changlee.gltf');
```

### 3. AnimationController - 动画控制器服务

**位置**: `services/AnimationController.js`

**功能**: 控制长离所有动作的"小脑"

**内置动画**:
- 😊 **情绪动画**: 开心、难过、生气、惊讶
- 🏃 **动作动画**: 行走、奔跑、跳跃、睡觉、吃饭
- ✨ **特色动画**: 长离思考、卖萌、施法
- 🎭 **特殊动画**: 挥手、跳舞、伸懒腰

**特性**:
- 🎬 **动画队列**: 支持动画排队播放
- 🔀 **动画混合**: 平滑的动画过渡
- ⚡ **速度控制**: 可调节动画播放速度
- 🔁 **循环控制**: 支持循环和单次播放

**使用示例**:
```javascript
import { AnimationController } from './services/AnimationController.js';

const animController = new AnimationController('3D');
animController.setModel(model);

// 播放动画
animController.playAnimation('happy', {
  speed: 1.0,
  fadeIn: 0.3,
  loop: false
});

// 停止动画
animController.stopAnimation();
```

## 🚀 快速开始

### 1. 基础使用

```jsx
import React, { useRef } from 'react';
import PetCanvas from './components/PetCanvas.jsx';

const MyPetApp = () => {
  const petCanvasRef = useRef(null);

  const handlePlayAnimation = (animationName) => {
    if (petCanvasRef.current) {
      petCanvasRef.current.playAnimation(animationName);
    }
  };

  return (
    <div>
      <PetCanvas
        ref={petCanvasRef}
        renderMode="3D"
        width={400}
        height={400}
        transparent={true}
      />
      
      <button onClick={() => handlePlayAnimation('happy')}>
        😊 开心
      </button>
      <button onClick={() => handlePlayAnimation('sleep')}>
        💤 睡觉
      </button>
    </div>
  );
};
```

### 2. 高级使用 - 模型替换

```jsx
const handleLoadCustomModel = async () => {
  if (petCanvasRef.current) {
    // 加载自定义3D模型
    const newModel = await petCanvasRef.current.loadModel('/assets/models/changlee_premium.gltf');
    
    if (newModel) {
      console.log('✅ 自定义模型加载成功');
    }
  }
};
```

### 3. 桌宠主逻辑集成

```jsx
// 桌宠主逻辑 - 完全不关心渲染细节
class ChangleePetLogic {
  constructor(petCanvas) {
    this.petCanvas = petCanvas;
    this.mood = 'happy';
    this.energy = 100;
  }

  // 抽象的行为指令
  expressEmotion(emotion) {
    // 主逻辑只需要发出抽象指令
    this.petCanvas.playAnimation(emotion);
  }

  // 定时行为
  performDailyRoutine() {
    if (this.energy < 30) {
      this.expressEmotion('sleep');
    } else if (this.mood === 'happy') {
      this.expressEmotion('dance');
    }
  }
}
```

## 🎨 技术栈详解

### Three.js - 3D渲染引擎
- **官方网站**: https://threejs.org/
- **GitHub**: https://github.com/mrdoob/three.js/
- **用途**: WebGL 3D渲染、模型加载、动画系统
- **加载器**: GLTFLoader (支持.gltf/.glb格式)

### PIXI.js - 2D渲染引擎
- **官方网站**: https://pixijs.com/
- **用途**: 高性能2D渲染、精灵动画、Live2D集成

### 模型格式支持
- **3D**: .gltf, .glb (推荐), .fbx, .obj
- **2D**: Live2D (.json), Spine (.skel), 精灵图 (.png/.jpg)

## 🔧 开发指南

### 添加新动画

1. **在AnimationController中定义动画**:
```javascript
// 在 _initBuiltInAnimations() 中添加
new_animation: {
  name: 'new_animation',
  displayName: '新动画',
  duration: 2000,
  loop: false,
  priority: 2
}
```

2. **实现动画逻辑**:
```javascript
// 添加对应的动画方法
_animateNewAnimation3D(progress) {
  // 3D动画实现
}

_animateNewAnimation2D(progress) {
  // 2D动画实现
}
```

### 添加新模型类型

1. **扩展ModelLoader**:
```javascript
async loadCustomModelType(modelPath) {
  // 实现自定义模型加载逻辑
}
```

2. **更新PetCanvas**:
```javascript
// 在PetCanvas中添加对新模型类型的支持
```

### 性能优化建议

1. **模型优化**:
   - 控制模型面数 (建议<10K三角形)
   - 使用纹理压缩
   - 合并材质和网格

2. **动画优化**:
   - 使用对象池复用动画对象
   - 避免频繁的DOM操作
   - 使用requestAnimationFrame

3. **内存管理**:
   - 及时清理不用的模型
   - 使用模型缓存
   - 监控内存使用

## 🐛 调试和测试

### 开发模式调试
```jsx
// 启用调试信息
<PetCanvas
  renderMode="3D"
  // ... 其他属性
/>
```

调试信息包括:
- 🎨 当前渲染模式
- 📊 FPS和性能统计
- 🔺 三角形数量
- 🎯 绘制调用次数
- 🐱 模型加载状态

### 常见问题排查

1. **模型不显示**:
   - 检查模型路径是否正确
   - 确认Three.js/PIXI.js已正确加载
   - 查看浏览器控制台错误信息

2. **动画不播放**:
   - 确认AnimationController已正确初始化
   - 检查动画名称是否正确
   - 验证模型是否已设置到控制器

3. **性能问题**:
   - 检查模型复杂度
   - 监控内存使用
   - 优化动画更新频率

## 🚀 未来扩展计划

### 短期目标 (1-2个月)
- ✅ 完善占位模型系统
- 🔄 实现模型热替换
- 🎵 添加音效支持
- 📱 移动端适配

### 中期目标 (3-6个月)
- 🎨 Live2D完整集成
- 🦴 Spine动画支持
- 🤖 AI驱动的智能行为
- 🌐 云端模型库

### 长期目标 (6个月+)
- 🎮 VR/AR支持
- 🗣️ 语音交互
- 🎭 表情识别
- 🌍 多平台部署

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 联系我们

- 项目主页: N.S.S Novena Garfield
- 邮箱: contact@changlee-capsule.com
- 讨论群: [加入我们的讨论群]

---

**🎉 让我们一起打造最可爱的桌面宠物长离！**