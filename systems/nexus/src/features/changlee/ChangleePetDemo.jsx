/**
 * ChangleePetDemo - 长离桌面宠物演示组件
 * 
 * 这个组件展示了如何使用我们的3D/2D模型展示框架
 * 演示了模型加载、动画控制、用户交互等功能
 */

import React, { useRef, useEffect, useState } from 'react';
import PetCanvas from './components/PetCanvas.jsx';

const ChangleePetDemo = () => {
  const petCanvasRef = useRef(null);
  const [renderMode, setRenderMode] = useState('3D');
  const [currentAnimation, setCurrentAnimation] = useState('idle');
  const [isLoading, setIsLoading] = useState(false);
  const [canvasStatus, setCanvasStatus] = useState(null);
  const [availableAnimations, setAvailableAnimations] = useState([]);

  // 动画列表 (与AnimationController中的定义对应)
  const animationList = [
    { name: 'idle', displayName: '待机', icon: '😴' },
    { name: 'happy', displayName: '开心', icon: '😊' },
    { name: 'sad', displayName: '难过', icon: '😢' },
    { name: 'angry', displayName: '生气', icon: '😠' },
    { name: 'surprised', displayName: '惊讶', icon: '😲' },
    { name: 'walk', displayName: '行走', icon: '🚶' },
    { name: 'run', displayName: '奔跑', icon: '🏃' },
    { name: 'jump', displayName: '跳跃', icon: '🦘' },
    { name: 'sleep', displayName: '睡觉', icon: '💤' },
    { name: 'eat', displayName: '吃饭', icon: '🍽️' },
    { name: 'wave', displayName: '挥手', icon: '👋' },
    { name: 'dance', displayName: '跳舞', icon: '💃' },
    { name: 'stretch', displayName: '伸懒腰', icon: '🤸' },
    { name: 'changlee_thinking', displayName: '思考', icon: '🤔' },
    { name: 'changlee_cute', displayName: '卖萌', icon: '🥰' },
    { name: 'changlee_magic', displayName: '施法', icon: '✨' }
  ];

  // 模型加载完成回调
  const handleModelLoaded = (model) => {
    console.log('🎯 模型加载完成:', model);
    setIsLoading(false);
  };

  // 动画完成回调
  const handleAnimationComplete = (animationName) => {
    console.log('🏁 动画完成:', animationName);
    // 可以在这里添加动画完成后的逻辑
  };

  // 播放动画
  const playAnimation = (animationName) => {
    if (petCanvasRef.current) {
      const success = petCanvasRef.current.playAnimation(animationName, {
        speed: 1.0,
        fadeIn: 0.3,
        fadeOut: 0.3
      });
      
      if (success) {
        setCurrentAnimation(animationName);
        console.log(`🎭 播放动画: ${animationName}`);
      }
    }
  };

  // 停止动画
  const stopAnimation = () => {
    if (petCanvasRef.current) {
      petCanvasRef.current.stopAnimation();
      setCurrentAnimation('idle');
    }
  };

  // 切换渲染模式
  const switchRenderMode = (newMode) => {
    setRenderMode(newMode);
    setIsLoading(true);
    console.log(`🔄 切换渲染模式: ${newMode}`);
  };

  // 获取画布状态
  const updateCanvasStatus = () => {
    if (petCanvasRef.current) {
      const status = petCanvasRef.current.getStatus();
      setCanvasStatus(status);
    }
  };

  // 定期更新状态
  useEffect(() => {
    const interval = setInterval(updateCanvasStatus, 1000);
    return () => clearInterval(interval);
  }, []);

  // 组件样式
  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    minHeight: '100vh',
    color: 'white'
  };

  const titleStyle = {
    fontSize: '2.5em',
    marginBottom: '20px',
    textAlign: 'center',
    textShadow: '2px 2px 4px rgba(0,0,0,0.5)'
  };

  const canvasContainerStyle = {
    background: 'rgba(255,255,255,0.1)',
    borderRadius: '20px',
    padding: '20px',
    marginBottom: '20px',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255,255,255,0.2)'
  };

  const controlPanelStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
    background: 'rgba(255,255,255,0.1)',
    borderRadius: '15px',
    padding: '20px',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255,255,255,0.2)',
    maxWidth: '800px',
    width: '100%'
  };

  const sectionStyle = {
    marginBottom: '15px'
  };

  const sectionTitleStyle = {
    fontSize: '1.2em',
    marginBottom: '10px',
    color: '#fff',
    borderBottom: '2px solid rgba(255,255,255,0.3)',
    paddingBottom: '5px'
  };

  const buttonGroupStyle = {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '10px'
  };

  const buttonStyle = {
    padding: '8px 16px',
    border: 'none',
    borderRadius: '8px',
    background: 'rgba(255,255,255,0.2)',
    color: 'white',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    fontSize: '14px',
    display: 'flex',
    alignItems: 'center',
    gap: '5px'
  };

  const activeButtonStyle = {
    ...buttonStyle,
    background: 'rgba(255,255,255,0.4)',
    transform: 'scale(1.05)'
  };

  const statusStyle = {
    background: 'rgba(0,0,0,0.3)',
    borderRadius: '10px',
    padding: '15px',
    fontSize: '14px',
    fontFamily: 'monospace'
  };

  return (
    <div style={containerStyle}>
      <h1 style={titleStyle}>🐱 长离桌面宠物演示</h1>
      
      {/* 3D/2D画布 */}
      <div style={canvasContainerStyle}>
        <PetCanvas
          ref={petCanvasRef}
          renderMode={renderMode}
          width={400}
          height={400}
          transparent={true}
          onModelLoaded={handleModelLoaded}
          onAnimationComplete={handleAnimationComplete}
          className="changlee-pet-canvas"
        />
      </div>

      {/* 控制面板 */}
      <div style={controlPanelStyle}>
        {/* 渲染模式切换 */}
        <div style={sectionStyle}>
          <h3 style={sectionTitleStyle}>🎨 渲染模式</h3>
          <div style={buttonGroupStyle}>
            <button
              style={renderMode === '3D' ? activeButtonStyle : buttonStyle}
              onClick={() => switchRenderMode('3D')}
            >
              🎲 3D模式
            </button>
            <button
              style={renderMode === '2D' ? activeButtonStyle : buttonStyle}
              onClick={() => switchRenderMode('2D')}
            >
              🎨 2D模式
            </button>
          </div>
        </div>

        {/* 基础动画控制 */}
        <div style={sectionStyle}>
          <h3 style={sectionTitleStyle}>😊 情绪动画</h3>
          <div style={buttonGroupStyle}>
            {animationList.filter(anim => 
              ['idle', 'happy', 'sad', 'angry', 'surprised'].includes(anim.name)
            ).map(anim => (
              <button
                key={anim.name}
                style={currentAnimation === anim.name ? activeButtonStyle : buttonStyle}
                onClick={() => playAnimation(anim.name)}
              >
                {anim.icon} {anim.displayName}
              </button>
            ))}
          </div>
        </div>

        {/* 动作动画 */}
        <div style={sectionStyle}>
          <h3 style={sectionTitleStyle}>🏃 动作动画</h3>
          <div style={buttonGroupStyle}>
            {animationList.filter(anim => 
              ['walk', 'run', 'jump', 'sleep', 'eat', 'wave', 'dance', 'stretch'].includes(anim.name)
            ).map(anim => (
              <button
                key={anim.name}
                style={currentAnimation === anim.name ? activeButtonStyle : buttonStyle}
                onClick={() => playAnimation(anim.name)}
              >
                {anim.icon} {anim.displayName}
              </button>
            ))}
          </div>
        </div>

        {/* 长离特有动画 */}
        <div style={sectionStyle}>
          <h3 style={sectionTitleStyle}>✨ 长离特色</h3>
          <div style={buttonGroupStyle}>
            {animationList.filter(anim => 
              anim.name.startsWith('changlee_')
            ).map(anim => (
              <button
                key={anim.name}
                style={currentAnimation === anim.name ? activeButtonStyle : buttonStyle}
                onClick={() => playAnimation(anim.name)}
              >
                {anim.icon} {anim.displayName}
              </button>
            ))}
          </div>
        </div>

        {/* 动画控制 */}
        <div style={sectionStyle}>
          <h3 style={sectionTitleStyle}>🎮 动画控制</h3>
          <div style={buttonGroupStyle}>
            <button
              style={buttonStyle}
              onClick={stopAnimation}
            >
              ⏹️ 停止动画
            </button>
            <button
              style={buttonStyle}
              onClick={() => playAnimation('idle')}
            >
              🔄 重置待机
            </button>
          </div>
        </div>

        {/* 状态信息 */}
        <div style={sectionStyle}>
          <h3 style={sectionTitleStyle}>📊 系统状态</h3>
          <div style={statusStyle}>
            {canvasStatus ? (
              <>
                <div>🎨 渲染模式: {canvasStatus.renderMode}</div>
                <div>🔧 初始化状态: {canvasStatus.isInitialized ? '✅ 已完成' : '⏳ 进行中'}</div>
                <div>📦 加载状态: {canvasStatus.isLoading ? '⏳ 加载中' : '✅ 已完成'}</div>
                <div>🐱 模型状态: {canvasStatus.hasModel ? '✅ 已加载' : '❌ 未加载'}</div>
                <div>🎭 当前动画: {currentAnimation}</div>
                {canvasStatus.error && (
                  <div style={{color: '#ff6b6b'}}>❌ 错误: {canvasStatus.error}</div>
                )}
              </>
            ) : (
              <div>⏳ 获取状态中...</div>
            )}
          </div>
        </div>

        {/* 使用说明 */}
        <div style={sectionStyle}>
          <h3 style={sectionTitleStyle}>📖 使用说明</h3>
          <div style={{fontSize: '14px', lineHeight: '1.6'}}>
            <p>🎯 <strong>模型展示框架特点:</strong></p>
            <ul style={{paddingLeft: '20px'}}>
              <li>✅ 支持3D和2D两种渲染模式无缝切换</li>
              <li>✅ 模型加载与桌宠逻辑完全分离</li>
              <li>✅ 可替换的占位模型系统</li>
              <li>✅ 丰富的内置动画系统</li>
              <li>✅ 基于Three.js和PIXI.js的高性能渲染</li>
            </ul>
            
            <p>🔧 <strong>技术架构:</strong></p>
            <ul style={{paddingLeft: '20px'}}>
              <li>📦 <strong>PetCanvas:</strong> 透明渲染画布组件</li>
              <li>🔧 <strong>ModelLoader:</strong> 模型加载服务</li>
              <li>🎭 <strong>AnimationController:</strong> 动画控制服务</li>
            </ul>
            
            <p>🚀 <strong>未来扩展:</strong></p>
            <ul style={{paddingLeft: '20px'}}>
              <li>🎨 支持加载.gltf/.glb 3D模型文件</li>
              <li>💃 支持Live2D和Spine 2D动画</li>
              <li>🎵 支持音效和语音同步</li>
              <li>🤖 支持AI驱动的智能行为</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChangleePetDemo;