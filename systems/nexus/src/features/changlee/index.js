/**
 * 长离桌面宠物框架 - 入口文件
 * 
 * 导出所有核心组件和服务
 */

// 核心组件
export { default as PetCanvas } from './components/PetCanvas.jsx';
export { default as ChangleePetDemo } from './ChangleePetDemo.jsx';

// 核心服务
export { ModelLoader } from './services/ModelLoader.js';
export { AnimationController } from './services/AnimationController.js';

// 现有的长离组件 (向后兼容)
export { default as ChangleeAssistant } from './ChangleeAssistant.tsx';
export { default as BasicChangleeAssistant } from './BasicChangleeAssistant.tsx';
export { default as SimpleChangleeAssistant } from './SimpleChangleeAssistant.tsx';

// 版本信息
export const VERSION = '1.0.0';
export const FRAMEWORK_NAME = 'Changlee Pet Framework';

// 框架配置
export const FRAMEWORK_CONFIG = {
  // 默认渲染设置
  defaultRenderMode: '3D',
  defaultCanvasSize: { width: 400, height: 400 },
  
  // 性能设置
  maxFPS: 60,
  enableDebug: process.env.NODE_ENV === 'development',
  
  // 动画设置
  defaultAnimationSpeed: 1.0,
  defaultFadeTime: 0.3,
  
  // 模型设置
  maxModelCacheSize: 10,
  enableModelCache: true,
  
  // CDN设置
  cdnUrls: {
    threejs: 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r158/three.min.js',
    pixijs: 'https://cdnjs.cloudflare.com/ajax/libs/pixi.js/7.3.2/pixi.min.js',
    gltfLoader: 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r158/examples/js/loaders/GLTFLoader.js'
  }
};

// 工具函数
export const FrameworkUtils = {
  /**
   * 检查浏览器兼容性
   */
  checkBrowserSupport() {
    const support = {
      webgl: !!window.WebGLRenderingContext,
      webgl2: !!window.WebGL2RenderingContext,
      canvas: !!document.createElement('canvas').getContext,
      requestAnimationFrame: !!window.requestAnimationFrame
    };
    
    const isSupported = support.webgl && support.canvas && support.requestAnimationFrame;
    
    return {
      ...support,
      isSupported,
      recommendation: isSupported ? '3D' : '2D'
    };
  },

  /**
   * 获取最佳渲染模式
   */
  getBestRenderMode() {
    const support = this.checkBrowserSupport();
    return support.recommendation;
  },

  /**
   * 格式化文件大小
   */
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  /**
   * 生成唯一ID
   */
  generateId() {
    return 'changlee_' + Math.random().toString(36).substr(2, 9);
  },

  /**
   * 深度克隆对象
   */
  deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime());
    if (obj instanceof Array) return obj.map(item => this.deepClone(item));
    if (typeof obj === 'object') {
      const clonedObj = {};
      for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
          clonedObj[key] = this.deepClone(obj[key]);
        }
      }
      return clonedObj;
    }
  }
};

// 框架初始化函数
export const initializeFramework = (config = {}) => {
  const finalConfig = { ...FRAMEWORK_CONFIG, ...config };
  
  console.log(`🚀 ${FRAMEWORK_NAME} v${VERSION} 初始化中...`);
  
  // 检查浏览器支持
  const browserSupport = FrameworkUtils.checkBrowserSupport();
  if (!browserSupport.isSupported) {
    console.warn('⚠️ 当前浏览器可能不完全支持3D渲染，建议使用2D模式');
  }
  
  // 设置全局配置
  window.CHANGLEE_FRAMEWORK_CONFIG = finalConfig;
  
  console.log('✅ 框架初始化完成');
  console.log('📊 浏览器支持情况:', browserSupport);
  console.log('⚙️ 框架配置:', finalConfig);
  
  return {
    config: finalConfig,
    browserSupport,
    version: VERSION
  };
};

// 默认导出
export default {
  // 组件
  PetCanvas,
  ChangleePetDemo,
  
  // 服务
  ModelLoader,
  AnimationController,
  
  // 工具
  FrameworkUtils,
  initializeFramework,
  
  // 配置
  FRAMEWORK_CONFIG,
  VERSION,
  FRAMEWORK_NAME
};