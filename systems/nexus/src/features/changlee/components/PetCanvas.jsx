/**
 * PetCanvas - 长离桌面宠物3D/2D模型渲染画布
 * 
 * 这是桌面上专门用于渲染长离的透明画布组件
 * 支持3D和2D两种渲染模式，可以无缝切换
 * 
 * 技术栈：
 * - 3D渲染: Three.js (https://threejs.org/)
 * - 2D动画: Pixi.js 
 * - 模型加载: GLTFLoader (https://github.com/mrdoob/three.js/)
 */

import React, { useRef, useEffect, useState, useImperativeHandle, forwardRef } from 'react';

const PetCanvas = forwardRef(({ 
  renderMode = '3D', // '3D' | '2D'
  width = 400, 
  height = 400,
  transparent = true,
  onModelLoaded = null,
  onAnimationComplete = null,
  className = ''
}, ref) => {
  const canvasRef = useRef(null);
  const rendererRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const pixiAppRef = useRef(null);
  const modelLoaderRef = useRef(null);
  const animationControllerRef = useRef(null);
  const animationFrameRef = useRef(null);
  
  const [isInitialized, setIsInitialized] = useState(false);
  const [currentModel, setCurrentModel] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [renderStats, setRenderStats] = useState({
    fps: 0,
    triangles: 0,
    drawCalls: 0,
    mode: renderMode
  });

  // 动态加载Three.js
  const loadThreeJS = async () => {
    try {
      // 从CDN加载Three.js
      if (!window.THREE) {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r158/three.min.js';
        script.async = true;
        
        return new Promise((resolve, reject) => {
          script.onload = () => {
            console.log('✅ Three.js 加载完成');
            resolve(window.THREE);
          };
          script.onerror = reject;
          document.head.appendChild(script);
        });
      }
      return window.THREE;
    } catch (error) {
      console.error('❌ Three.js 加载失败:', error);
      throw error;
    }
  };

  // 动态加载PIXI.js
  const loadPixiJS = async () => {
    try {
      if (!window.PIXI) {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pixi.js/7.3.2/pixi.min.js';
        script.async = true;
        
        return new Promise((resolve, reject) => {
          script.onload = () => {
            console.log('✅ PIXI.js 加载完成');
            resolve(window.PIXI);
          };
          script.onerror = reject;
          document.head.appendChild(script);
        });
      }
      return window.PIXI;
    } catch (error) {
      console.error('❌ PIXI.js 加载失败:', error);
      throw error;
    }
  };

  // 初始化3D渲染环境
  const init3D = async () => {
    if (!canvasRef.current) return;

    try {
      const THREE = await loadThreeJS();
      
      // 创建场景
      const scene = new THREE.Scene();
      sceneRef.current = scene;

      // 创建透视摄像机
      const camera = new THREE.PerspectiveCamera(
        75, // 视野角度
        width / height, // 宽高比
        0.1, // 近裁剪面
        1000 // 远裁剪面
      );
      camera.position.set(0, 0, 5);
      cameraRef.current = camera;

      // 创建WebGL渲染器
      const renderer = new THREE.WebGLRenderer({
        canvas: canvasRef.current,
        alpha: transparent, // 透明背景
        antialias: true, // 抗锯齿
        preserveDrawingBuffer: true // 保持绘制缓冲区
      });
      
      renderer.setSize(width, height);
      renderer.setPixelRatio(window.devicePixelRatio);
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      
      if (transparent) {
        renderer.setClearColor(0x000000, 0); // 完全透明
      }
      
      rendererRef.current = renderer;

      // 添加环境光和方向光
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
      scene.add(ambientLight);

      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
      directionalLight.position.set(10, 10, 5);
      directionalLight.castShadow = true;
      scene.add(directionalLight);

      console.log('✅ 3D渲染环境初始化完成');
      return true;
    } catch (error) {
      console.error('❌ 3D渲染环境初始化失败:', error);
      setError('3D渲染环境初始化失败');
      return false;
    }
  };

  // 初始化2D渲染环境
  const init2D = async () => {
    if (!canvasRef.current) return;

    try {
      const PIXI = await loadPixiJS();
      
      // 创建PIXI应用
      const app = new PIXI.Application({
        view: canvasRef.current,
        width,
        height,
        transparent,
        antialias: true,
        resolution: window.devicePixelRatio || 1,
        autoDensity: true
      });

      pixiAppRef.current = app;
      console.log('✅ 2D渲染环境初始化完成');
      return true;
    } catch (error) {
      console.error('❌ 2D渲染环境初始化失败:', error);
      setError('2D渲染环境初始化失败');
      return false;
    }
  };

  // 创建占位模型 - 3D版本
  const createPlaceholder3D = () => {
    const THREE = window.THREE;
    if (!THREE) return null;

    // 创建一个彩色的几何体组合，代表长离
    const group = new THREE.Group();

    // 身体 - 圆柱体
    const bodyGeometry = new THREE.CylinderGeometry(0.8, 1.0, 2.0, 8);
    const bodyMaterial = new THREE.MeshLambertMaterial({ 
      color: 0x4a90e2, // 蓝色
      transparent: true,
      opacity: 0.9
    });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.position.y = 0;
    group.add(body);

    // 头部 - 球体
    const headGeometry = new THREE.SphereGeometry(0.6, 16, 16);
    const headMaterial = new THREE.MeshLambertMaterial({ 
      color: 0xf5a623, // 橙色
      transparent: true,
      opacity: 0.9
    });
    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.position.y = 1.5;
    group.add(head);

    // 眼睛
    const eyeGeometry = new THREE.SphereGeometry(0.1, 8, 8);
    const eyeMaterial = new THREE.MeshLambertMaterial({ color: 0x000000 });
    
    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    leftEye.position.set(-0.2, 1.6, 0.5);
    group.add(leftEye);
    
    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    rightEye.position.set(0.2, 1.6, 0.5);
    group.add(rightEye);

    // 耳朵 - 三角锥
    const earGeometry = new THREE.ConeGeometry(0.2, 0.5, 4);
    const earMaterial = new THREE.MeshLambertMaterial({ color: 0xf5a623 });
    
    const leftEar = new THREE.Mesh(earGeometry, earMaterial);
    leftEar.position.set(-0.4, 2.0, 0);
    leftEar.rotation.z = -0.3;
    group.add(leftEar);
    
    const rightEar = new THREE.Mesh(earGeometry, earMaterial);
    rightEar.position.set(0.4, 2.0, 0);
    rightEar.rotation.z = 0.3;
    group.add(rightEar);

    // 添加简单的呼吸动画
    group.userData = {
      originalScale: group.scale.clone(),
      animationType: 'breathing',
      animationTime: 0
    };

    return group;
  };

  // 创建占位模型 - 2D版本
  const createPlaceholder2D = () => {
    const PIXI = window.PIXI;
    if (!PIXI) return null;

    const container = new PIXI.Container();

    // 身体
    const body = new PIXI.Graphics();
    body.beginFill(0x4a90e2, 0.9);
    body.drawEllipse(0, 0, 80, 100);
    body.endFill();
    body.x = width / 2;
    body.y = height / 2;
    container.addChild(body);

    // 头部
    const head = new PIXI.Graphics();
    head.beginFill(0xf5a623, 0.9);
    head.drawCircle(0, 0, 60);
    head.endFill();
    head.x = width / 2;
    head.y = height / 2 - 80;
    container.addChild(head);

    // 眼睛
    const leftEye = new PIXI.Graphics();
    leftEye.beginFill(0x000000);
    leftEye.drawCircle(0, 0, 8);
    leftEye.endFill();
    leftEye.x = width / 2 - 20;
    leftEye.y = height / 2 - 90;
    container.addChild(leftEye);

    const rightEye = new PIXI.Graphics();
    rightEye.beginFill(0x000000);
    rightEye.drawCircle(0, 0, 8);
    rightEye.endFill();
    rightEye.x = width / 2 + 20;
    rightEye.y = height / 2 - 90;
    container.addChild(rightEye);

    // 耳朵
    const leftEar = new PIXI.Graphics();
    leftEar.beginFill(0xf5a623);
    leftEar.drawPolygon([0, 0, -15, -40, 15, -40]);
    leftEar.endFill();
    leftEar.x = width / 2 - 35;
    leftEar.y = height / 2 - 120;
    container.addChild(leftEar);

    const rightEar = new PIXI.Graphics();
    rightEar.beginFill(0xf5a623);
    rightEar.drawPolygon([0, 0, -15, -40, 15, -40]);
    rightEar.endFill();
    rightEar.x = width / 2 + 35;
    rightEar.y = height / 2 - 120;
    container.addChild(rightEar);

    // 添加动画数据
    container.userData = {
      originalScale: { x: container.scale.x, y: container.scale.y },
      animationType: 'breathing',
      animationTime: 0
    };

    return container;
  };

  // 加载占位模型
  const loadPlaceholderModel = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      let model;
      
      if (renderMode === '3D') {
        model = createPlaceholder3D();
        if (model && sceneRef.current) {
          sceneRef.current.add(model);
        }
      } else {
        model = createPlaceholder2D();
        if (model && pixiAppRef.current) {
          pixiAppRef.current.stage.addChild(model);
        }
      }
      
      if (model) {
        setCurrentModel(model);
        console.log(`✅ ${renderMode} 占位模型加载完成`);
        
        if (onModelLoaded) {
          onModelLoaded(model);
        }
      }
      
    } catch (error) {
      console.error('❌ 占位模型加载失败:', error);
      setError('占位模型加载失败');
    } finally {
      setIsLoading(false);
    }
  };

  // 渲染循环
  const animate = () => {
    if (renderMode === '3D' && rendererRef.current && sceneRef.current && cameraRef.current) {
      // 更新3D动画
      if (currentModel && currentModel.userData) {
        const userData = currentModel.userData;
        if (userData.animationType === 'breathing') {
          userData.animationTime += 0.02;
          const scale = 1 + Math.sin(userData.animationTime) * 0.05;
          currentModel.scale.setScalar(scale);
          
          // 轻微旋转
          currentModel.rotation.y += 0.005;
        }
      }
      
      // 3D渲染
      rendererRef.current.render(sceneRef.current, cameraRef.current);
      
      // 更新渲染统计
      const info = rendererRef.current.info;
      setRenderStats(prev => ({
        ...prev,
        triangles: info.render.triangles,
        drawCalls: info.render.calls
      }));
      
    } else if (renderMode === '2D' && currentModel && currentModel.userData) {
      // 更新2D动画
      const userData = currentModel.userData;
      if (userData.animationType === 'breathing') {
        userData.animationTime += 0.02;
        const scale = 1 + Math.sin(userData.animationTime) * 0.05;
        currentModel.scale.set(scale, scale);
      }
    }
    
    animationFrameRef.current = requestAnimationFrame(animate);
  };

  // 组件初始化
  useEffect(() => {
    const initCanvas = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        let success = false;
        
        if (renderMode === '3D') {
          success = await init3D();
        } else {
          success = await init2D();
        }
        
        if (success) {
          setIsInitialized(true);
        }
      } catch (error) {
        console.error('❌ 画布初始化失败:', error);
        setError('画布初始化失败');
      } finally {
        setIsLoading(false);
      }
    };

    initCanvas();
  }, [renderMode, width, height, transparent]);

  // 加载占位模型
  useEffect(() => {
    if (isInitialized) {
      loadPlaceholderModel();
    }
  }, [isInitialized]);

  // 启动渲染循环
  useEffect(() => {
    if (isInitialized && !error) {
      animate();
    }
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isInitialized, error, currentModel]);

  // 清理资源
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      
      if (rendererRef.current) {
        rendererRef.current.dispose();
      }
      
      if (pixiAppRef.current) {
        pixiAppRef.current.destroy(true);
      }
    };
  }, []);

  // 公开的API方法
  const canvasAPI = {
    // 播放动画
    playAnimation: (animationName, options = {}) => {
      console.log(`🎭 播放动画: ${animationName}`, options);
      
      if (!currentModel) return false;
      
      // 简单的动画示例
      switch (animationName) {
        case 'happy':
          // 开心动画 - 快速缩放
          if (currentModel.userData) {
            currentModel.userData.animationType = 'happy';
            currentModel.userData.animationTime = 0;
          }
          break;
          
        case 'sleep':
          // 睡觉动画 - 慢慢缩小
          if (currentModel.userData) {
            currentModel.userData.animationType = 'sleep';
            currentModel.userData.animationTime = 0;
          }
          break;
          
        case 'walk':
          // 行走动画 - 左右摇摆
          if (currentModel.userData) {
            currentModel.userData.animationType = 'walk';
            currentModel.userData.animationTime = 0;
          }
          break;
          
        default:
          // 默认呼吸动画
          if (currentModel.userData) {
            currentModel.userData.animationType = 'breathing';
            currentModel.userData.animationTime = 0;
          }
      }
      
      return true;
    },
    
    // 停止动画
    stopAnimation: () => {
      if (currentModel && currentModel.userData) {
        currentModel.userData.animationType = 'idle';
      }
    },
    
    // 获取当前模型
    getCurrentModel: () => currentModel,
    
    // 获取渲染统计
    getRenderStats: () => renderStats,
    
    // 获取状态
    getStatus: () => ({
      isInitialized,
      isLoading,
      error,
      renderMode,
      hasModel: !!currentModel
    })
  };

  // 将API暴露给父组件
  useImperativeHandle(ref, () => canvasAPI);

  return (
    <div 
      className={`pet-canvas-container ${className}`} 
      style={{ 
        width, 
        height, 
        position: 'relative',
        borderRadius: '10px',
        overflow: 'hidden'
      }}
    >
      <canvas
        ref={canvasRef}
        style={{
          width: '100%',
          height: '100%',
          display: 'block',
          background: transparent ? 'transparent' : '#f0f0f0'
        }}
      />
      
      {/* 加载状态 */}
      {isLoading && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'rgba(0,0,0,0.8)',
          color: 'white',
          padding: '10px 20px',
          borderRadius: '5px',
          fontSize: '14px'
        }}>
          🔄 加载中...
        </div>
      )}
      
      {/* 错误状态 */}
      {error && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'rgba(255,0,0,0.8)',
          color: 'white',
          padding: '10px 20px',
          borderRadius: '5px',
          fontSize: '14px',
          textAlign: 'center'
        }}>
          ❌ {error}
        </div>
      )}
      
      {/* 调试信息 */}
      {process.env.NODE_ENV === 'development' && isInitialized && (
        <div style={{
          position: 'absolute',
          top: 10,
          left: 10,
          background: 'rgba(0,0,0,0.7)',
          color: 'white',
          padding: '5px 10px',
          borderRadius: '5px',
          fontSize: '12px',
          fontFamily: 'monospace'
        }}>
          <div>🎨 模式: {renderMode}</div>
          <div>📊 状态: {isInitialized ? '运行中' : '初始化中'}</div>
          {renderMode === '3D' && (
            <>
              <div>🔺 三角形: {renderStats.triangles}</div>
              <div>🎯 绘制: {renderStats.drawCalls}</div>
            </>
          )}
          <div>🐱 模型: {currentModel ? '已加载' : '无'}</div>
        </div>
      )}
    </div>
  );
});

PetCanvas.displayName = 'PetCanvas';

export default PetCanvas;