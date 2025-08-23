# Changlee-Link UI 设计指南

## 🎨 设计理念

### 核心原则
1. **极简主义** - 每个界面只专注一个核心功能
2. **触控优先** - 为小屏幕触控操作优化
3. **情境感知** - 根据使用场景智能调整界面
4. **一致性** - 跨平台保持统一的视觉语言

### 设计目标
- **可用性**：在1.5英寸屏幕上清晰可读
- **效率性**：3秒内完成常用操作
- **美观性**：现代化的视觉设计
- **适应性**：适配不同光线和使用场景

## 📐 布局规范

### 屏幕尺寸适配

| 设备类型 | 屏幕尺寸 | 分辨率 | 设计要点 |
|---------|---------|--------|---------|
| **Apple Watch** | 40mm/44mm/45mm | 324×394 / 368×448 / 396×484 | 圆角矩形，Digital Crown交互 |
| **Wear OS** | 1.2"-1.4" | 390×390 / 454×454 | 圆形/方形，旋转表冠 |
| **HarmonyOS** | 1.43" | 466×466 | 圆形，3D旋转表冠 |

### 安全区域定义
```css
/* 通用安全区域 */
.safe-area {
    padding: 8px 12px;
    margin: 4px;
}

/* Apple Watch 安全区域 */
.apple-watch-safe {
    padding: 10px 14px;
    border-radius: 8px;
}

/* Wear OS 圆形屏幕 */
.wear-os-round {
    padding: 16px;
    border-radius: 50%;
}
```

## 🎯 界面层级结构

### 主界面架构
```
主控面板 (Main Dashboard)
├── 系统状态 (System Status)
│   ├── 在线系统列表
│   ├── 离线系统提醒
│   └── 受限系统申请
├── 快速操作 (Quick Actions)
│   ├── 远程控制
│   ├── RAG问答
│   ├── 唤醒长离
│   └── 查看日志
├── 健康监测 (Health Monitor)
│   ├── 实时健康数据
│   ├── 专注度分析
│   └── 工作建议
└── 通知中心 (Notification Center)
    ├── 系统告警
    ├── AI消息
    └── 操作反馈
```

### 导航模式

#### 1. 标签式导航 (Tab Navigation)
```
┌─────────────────────────────┐
│  🏠    🌐    💓    🔔      │ ← 底部标签栏
├─────────────────────────────┤
│                             │
│        主要内容区域          │
│                             │
│                             │
└─────────────────────────────┘
```

#### 2. 卡片式滑动 (Card Swipe)
```
┌─────────────────────────────┐
│  ← 系统状态 →               │ ← 左右滑动切换
├─────────────────────────────┤
│  🟢 在线: 5个系统           │
│  🟡 离线: 1个系统           │
│  🔒 受限: 3个系统           │
│                             │
│  [查看详情] [刷新状态]      │
└─────────────────────────────┘
```

## 🎨 视觉设计系统

### 色彩方案

#### 主色调 (Primary Colors)
```css
:root {
    /* NEXUS 品牌色 */
    --nexus-primary: #3b82f6;      /* 蓝色 */
    --nexus-secondary: #10b981;    /* 绿色 */
    --nexus-accent: #f59e0b;       /* 橙色 */
    
    /* 状态色 */
    --status-online: #22c55e;      /* 在线绿 */
    --status-offline: #ef4444;     /* 离线红 */
    --status-restricted: #f59e0b;  /* 受限橙 */
    --status-warning: #eab308;     /* 警告黄 */
}
```

#### 深色主题 (Dark Theme)
```css
:root[data-theme="dark"] {
    --bg-primary: #0f172a;         /* 主背景 */
    --bg-secondary: #1e293b;       /* 次背景 */
    --bg-tertiary: #334155;        /* 三级背景 */
    
    --text-primary: #f8fafc;       /* 主文字 */
    --text-secondary: #cbd5e1;     /* 次文字 */
    --text-tertiary: #94a3b8;      /* 三级文字 */
    
    --border-color: #475569;       /* 边框色 */
    --shadow-color: rgba(0,0,0,0.5); /* 阴影色 */
}
```

#### 浅色主题 (Light Theme)
```css
:root[data-theme="light"] {
    --bg-primary: #ffffff;         /* 主背景 */
    --bg-secondary: #f8fafc;       /* 次背景 */
    --bg-tertiary: #e2e8f0;        /* 三级背景 */
    
    --text-primary: #0f172a;       /* 主文字 */
    --text-secondary: #334155;     /* 次文字 */
    --text-tertiary: #64748b;      /* 三级文字 */
    
    --border-color: #cbd5e1;       /* 边框色 */
    --shadow-color: rgba(0,0,0,0.1); /* 阴影色 */
}
```

### 字体规范

#### 字体大小层级
```css
/* Apple Watch 字体 */
.text-title { font-size: 20px; font-weight: 600; }
.text-headline { font-size: 16px; font-weight: 500; }
.text-body { font-size: 14px; font-weight: 400; }
.text-caption { font-size: 12px; font-weight: 400; }
.text-footnote { font-size: 10px; font-weight: 400; }

/* Wear OS 字体 */
.text-display { font-size: 24px; font-weight: 700; }
.text-title { font-size: 18px; font-weight: 600; }
.text-body { font-size: 14px; font-weight: 400; }
.text-label { font-size: 12px; font-weight: 500; }
```

#### 字体选择
- **Apple Watch**: SF Pro Display (系统默认)
- **Wear OS**: Roboto (Google 推荐)
- **HarmonyOS**: HarmonyOS Sans (华为定制)

### 图标系统

#### 图标尺寸规范
```css
.icon-large { width: 32px; height: 32px; }   /* 主要操作 */
.icon-medium { width: 24px; height: 24px; }  /* 次要操作 */
.icon-small { width: 16px; height: 16px; }   /* 状态指示 */
.icon-tiny { width: 12px; height: 12px; }    /* 装饰性 */
```

#### 系统图标映射
```typescript
const SystemIcons = {
    // 系统状态
    'nexus_remote': '🌐',
    'rag_system': '🧠',
    'changlee': '🐱',
    'chronicle': '📝',
    'bovine_insight': '🐄',
    'molecular_dynamics': '⚗️',
    'genome_jigsaw': '🧬',
    
    // 操作类型
    'power_on': '⚡',
    'power_off': '🔌',
    'restart': '🔄',
    'status': '📊',
    'settings': '⚙️',
    'notification': '🔔',
    
    // 健康数据
    'heart_rate': '💓',
    'blood_oxygen': '🫁',
    'stress': '😌',
    'focus': '🧠',
    'activity': '🏃'
};
```

## 📱 组件设计规范

### 按钮组件 (Button Components)

#### 主要按钮 (Primary Button)
```css
.btn-primary {
    background: var(--nexus-primary);
    color: white;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 600;
    min-height: 44px; /* 触控友好 */
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.btn-primary:active {
    transform: scale(0.95);
    box-shadow: 0 1px 4px rgba(59, 130, 246, 0.5);
}
```

#### 次要按钮 (Secondary Button)
```css
.btn-secondary {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 500;
    min-height: 40px;
}
```

### 卡片组件 (Card Components)

#### 系统状态卡片
```css
.system-card {
    background: var(--bg-secondary);
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
    border: 1px solid var(--border-color);
    box-shadow: 0 2px 8px var(--shadow-color);
}

.system-card-header {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.system-card-icon {
    width: 24px;
    height: 24px;
    margin-right: 8px;
    font-size: 20px;
}

.system-card-status {
    margin-left: auto;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: 600;
}
```

### 列表组件 (List Components)

#### 系统列表项
```css
.list-item {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    min-height: 48px;
}

.list-item:last-child {
    border-bottom: none;
}

.list-item-icon {
    width: 20px;
    height: 20px;
    margin-right: 12px;
}

.list-item-content {
    flex: 1;
}

.list-item-title {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
}

.list-item-subtitle {
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 2px;
}
```

## 🎭 交互设计

### 手势操作

#### 基础手势
```typescript
interface GestureActions {
    // 点击操作
    tap: {
        single: 'select',      // 单击选择
        double: 'activate',    // 双击激活
        long: 'context_menu'   // 长按菜单
    };
    
    // 滑动操作
    swipe: {
        left: 'next_page',     // 左滑下一页
        right: 'prev_page',    // 右滑上一页
        up: 'scroll_up',       // 上滑滚动
        down: 'scroll_down'    // 下滑滚动
    };
    
    // 表冠操作 (Apple Watch)
    crown: {
        rotate: 'scroll',      // 旋转滚动
        press: 'home',         // 按压回主页
        double_press: 'dock'   // 双击打开程序坞
    };
}
```

#### 触觉反馈
```swift
// Apple Watch 触觉反馈
import WatchKit

enum HapticType {
    case success    // 操作成功
    case warning    // 警告提示
    case failure    // 操作失败
    case selection  // 选择反馈
}

func playHaptic(_ type: HapticType) {
    let device = WKHapticType.success // 根据类型选择
    WKInterfaceDevice.current().play(device)
}
```

### 动画效果

#### 页面转场动画
```css
/* 滑动转场 */
.page-transition-slide {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-enter {
    transform: translateX(100%);
}

.page-enter-active {
    transform: translateX(0);
}

.page-exit {
    transform: translateX(0);
}

.page-exit-active {
    transform: translateX(-100%);
}
```

#### 状态变化动画
```css
/* 状态指示器动画 */
.status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    transition: all 0.3s ease;
}

.status-online {
    background: var(--status-online);
    box-shadow: 0 0 8px var(--status-online);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
```

## 📊 数据可视化

### 图表组件

#### 环形进度条
```css
.circular-progress {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: conic-gradient(
        var(--nexus-primary) 0deg,
        var(--nexus-primary) calc(var(--progress) * 3.6deg),
        var(--bg-tertiary) calc(var(--progress) * 3.6deg),
        var(--bg-tertiary) 360deg
    );
    display: flex;
    align-items: center;
    justify-content: center;
}

.circular-progress::before {
    content: '';
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: var(--bg-primary);
}

.circular-progress-text {
    position: absolute;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-primary);
}
```

#### 迷你图表
```css
.mini-chart {
    width: 100%;
    height: 40px;
    background: linear-gradient(
        to right,
        transparent 0%,
        var(--nexus-primary) 50%,
        transparent 100%
    );
    border-radius: 4px;
    position: relative;
    overflow: hidden;
}

.mini-chart-line {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--nexus-primary);
    transform-origin: left;
    animation: chart-draw 1s ease-out;
}

@keyframes chart-draw {
    from { transform: scaleX(0); }
    to { transform: scaleX(1); }
}
```

## 🌙 深色模式适配

### 自动切换逻辑
```typescript
// 根据系统设置和时间自动切换主题
class ThemeManager {
    private currentTheme: 'light' | 'dark' | 'auto' = 'auto';
    
    updateTheme() {
        if (this.currentTheme === 'auto') {
            const hour = new Date().getHours();
            const isNightTime = hour < 7 || hour > 19;
            const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            const shouldUseDark = isNightTime || systemPrefersDark;
            document.documentElement.setAttribute('data-theme', shouldUseDark ? 'dark' : 'light');
        } else {
            document.documentElement.setAttribute('data-theme', this.currentTheme);
        }
    }
}
```

### 深色模式优化
```css
/* 深色模式下的特殊处理 */
[data-theme="dark"] .system-card {
    background: var(--bg-secondary);
    border-color: var(--border-color);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

[data-theme="dark"] .btn-primary {
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
}

[data-theme="dark"] .status-online {
    box-shadow: 0 0 8px rgba(34, 197, 94, 0.6);
}
```

## 📱 平台特定适配

### Apple Watch 特殊处理
```swift
// 适配不同尺寸的 Apple Watch
extension WKInterfaceDevice {
    var screenBounds: CGRect {
        return WKInterfaceDevice.current().screenBounds
    }
    
    var isLargeScreen: Bool {
        return screenBounds.width >= 368 // 44mm 及以上
    }
}

// 根据屏幕尺寸调整布局
if WKInterfaceDevice.current().isLargeScreen {
    // 使用大屏幕布局
    titleLabel.setFont(UIFont.systemFont(ofSize: 18, weight: .semibold))
} else {
    // 使用小屏幕布局
    titleLabel.setFont(UIFont.systemFont(ofSize: 16, weight: .semibold))
}
```

### Wear OS 圆形屏幕适配
```kotlin
// 检测屏幕形状
val isRound = resources.configuration.isScreenRound

if (isRound) {
    // 圆形屏幕布局
    val padding = (screenWidth * 0.146f).toInt() // 约15%的边距
    view.setPadding(padding, padding, padding, padding)
} else {
    // 方形屏幕布局
    view.setPadding(16, 16, 16, 16)
}
```

### HarmonyOS 分布式UI
```typescript
// 根据设备能力调整UI
@Component
struct AdaptiveUI {
    @State deviceCapabilities: DeviceCapabilities = getDeviceCapabilities();
    
    build() {
        if (this.deviceCapabilities.hasRotaryCrown) {
            // 支持旋转表冠的UI
            ScrollableList({ crownScrollEnabled: true })
        } else {
            // 触控滑动UI
            TouchScrollList()
        }
    }
}
```

---

**设计版本**：v1.0  
**最后更新**：2025-08-20  
**适用平台**：watchOS, Wear OS, HarmonyOS