import { create } from 'zustand';

// 应用全局状态管理
export const useAppStore = create((set, get) => ({
  // 当前活动的功能模块
  activeModule: null, // 'music-player' | 'rag-chat' | 'word-capsule' | null

  // 模块状态
  modules: {
    'music-player': {
      isActive: false,
      isMinimized: false
    },
    'rag-chat': {
      isActive: false,
      isMinimized: false
    },
    'word-capsule': {
      isActive: false,
      isMinimized: false
    }
  },

  // 通知系统
  notifications: [],

  // 应用设置
  appSettings: {
    theme: 'light', // 'light' | 'dark'
    language: 'zh-CN',
    autoSave: true,
    debugMode: false
  },

  // Actions
  setActiveModule: (module) => set({ activeModule: module }),

  activateModule: (moduleName) => set((state) => ({
    activeModule: moduleName,
    modules: {
      ...state.modules,
      [moduleName]: {
        ...state.modules[moduleName],
        isActive: true,
        isMinimized: false
      }
    }
  })),

  deactivateModule: (moduleName) => set((state) => ({
    activeModule: state.activeModule === moduleName ? null : state.activeModule,
    modules: {
      ...state.modules,
      [moduleName]: {
        ...state.modules[moduleName],
        isActive: false
      }
    }
  })),

  toggleModuleMinimize: (moduleName) => set((state) => ({
    modules: {
      ...state.modules,
      [moduleName]: {
        ...state.modules[moduleName],
        isMinimized: !state.modules[moduleName].isMinimized
      }
    }
  })),

  addNotification: (notification) => set((state) => ({
    notifications: [...state.notifications, {
      id: Date.now() + Math.random(),
      timestamp: Date.now(),
      ...notification
    }]
  })),

  removeNotification: (id) => set((state) => ({
    notifications: state.notifications.filter(n => n.id !== id)
  })),

  clearNotifications: () => set({ notifications: [] }),

  updateAppSettings: (updates) => set((state) => ({
    appSettings: { ...state.appSettings, ...updates }
  })),

  // 获取模块状态
  getModuleState: (moduleName) => {
    const state = get();
    return state.modules[moduleName] || { isActive: false, isMinimized: false };
  },

  // 检查是否有活动模块
  hasActiveModule: () => {
    const state = get();
    return state.activeModule !== null;
  },

  // 获取所有活动模块
  getActiveModules: () => {
    const state = get();
    return Object.keys(state.modules).filter(
      moduleName => state.modules[moduleName].isActive
    );
  }
}));