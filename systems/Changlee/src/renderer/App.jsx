import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import styled, { createGlobalStyle, ThemeProvider } from 'styled-components';
import { AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';

// 导入新的模块化组件
import DesktopPet from './components/DesktopPet';
import { MusicPlayer } from './features/music-player';
import { RagChat } from './features/rag-chat';
import { WordCapsule } from './features/word-capsule';
import { Modal, LoadingSpinner } from './components';
import { useAppStore, usePetStore } from './store';
import { useAnimation, useNotification } from './hooks';

// 保留原有组件（向后兼容）
import IntelligentChat from './components/IntelligentChat';
import DocumentManager from './components/DocumentManager';
import Dashboard from './pages/Dashboard';

// 全局样式
const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background: ${props => props.theme.background};
    color: ${props => props.theme.text};
    overflow-x: hidden;
  }

  #root {
    min-height: 100vh;
  }

  /* 自定义滚动条 */
  ::-webkit-scrollbar {
    width: 8px;
  }

  ::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.5);
  }
`;

// 主题配置
const lightTheme = {
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  surface: 'rgba(255, 255, 255, 0.9)',
  text: '#333333',
  textSecondary: '#666666',
  primary: '#667eea',
  secondary: '#764ba2',
  accent: '#ff6b6b',
  success: '#4ecdc4',
  warning: '#feca57',
  error: '#ff6b6b'
};

const darkTheme = {
  background: 'linear-gradient(135deg, #2c3e50 0%, #34495e 100%)',
  surface: 'rgba(255, 255, 255, 0.1)',
  text: '#ffffff',
  textSecondary: '#cccccc',
  primary: '#3498db',
  secondary: '#9b59b6',
  accent: '#e74c3c',
  success: '#2ecc71',
  warning: '#f39c12',
  error: '#e74c3c'
};

// 应用容器
const AppContainer = styled.div`
  min-height: 100vh;
  background: ${props => props.theme.background};
  position: relative;
`;

// 主内容区域
const MainContent = styled.div`
  min-height: 100vh;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

// 模态框覆盖层
const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(10px);
`;

// 路由动画包装器
const AnimatedRoutes = () => {
  const location = useLocation();
  
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/pet" element={<PetView />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/statistics" element={<Statistics />} />
      </Routes>
    </AnimatePresence>
  );
};

// 桌宠视图组件
const PetView = () => {
  return (
    <div style={{ 
      width: '100vw', 
      height: '100vh', 
      background: 'transparent',
      position: 'relative'
    }}>
      <DesktopPet />
    </div>
  );
};

// 主应用组件
const App = () => {
  const [theme, setTheme] = useState(lightTheme);
  
  // 使用新的状态管理
  const { 
    activeModule, 
    modules, 
    appSettings,
    activateModule, 
    deactivateModule,
    updateAppSettings 
  } = useAppStore();
  
  const { 
    petInfo, 
    currentAnimation, 
    updatePetInfo,
    setAnimation,
    recordInteraction 
  } = usePetStore();
  
  const { currentAnimation: animationState, changeAnimation } = useAnimation();
  const { notifications, showPetNotification } = useNotification();

  // 初始化应用
  useEffect(() => {
    initializeApp();
    setupEventListeners();
    
    return () => {
      cleanupEventListeners();
    };
  }, []);

  const initializeApp = async () => {
    try {
      // 加载用户设置
      if (window.electronAPI) {
        const settings = await window.electronAPI.getSettings();
        updateAppSettings(settings);
        
        // 应用主题
        if (settings.theme === 'dark') {
          setTheme(darkTheme);
        }
      }
      
      // 显示欢迎消息
      showPetNotification('欢迎回来！长离已经准备好和你一起学习了！', '🎉');
      
      console.log('🚀 长离的学习胶囊已初始化');
    } catch (error) {
      console.error('应用初始化失败:', error);
    }
  };

  const setupEventListeners = () => {
    // 监听导航事件
    if (window.electronAPI) {
      window.electronAPI.onNavigateTo((event, path) => {
        window.location.hash = path;
      });
    }
  };

  const cleanupEventListeners = () => {
    if (window.electronAPI) {
      window.electronAPI.removeAllListeners('navigate-to');
    }
  };

  // 处理模块激活
  const handleModuleActivation = (moduleName) => {
    activateModule(moduleName);
    recordInteraction('module_activated', { module: moduleName });
    
    // 根据模块类型设置动画
    switch (moduleName) {
      case 'word-capsule':
        changeAnimation('studying');
        break;
      case 'rag-chat':
        changeAnimation('thinking');
        break;
      case 'music-player':
        changeAnimation('listening');
        break;
      default:
        changeAnimation('idle');
    }
  };

  // 处理模块关闭
  const handleModuleDeactivation = (moduleName) => {
    deactivateModule(moduleName);
    changeAnimation('idle');
  };

  // 处理动画变化
  const handleAnimationChange = (newAnimation) => {
    changeAnimation(newAnimation);
    setAnimation(newAnimation);
  };

  // 处理桌宠互动
  const handlePetInteraction = (interactionType, data = {}) => {
    recordInteraction(interactionType, data);
    
    // 根据互动类型显示不同反应
    switch (interactionType) {
      case 'word_learned':
        showPetNotification('太棒了！又学会了一个新单词！', '🎉');
        changeAnimation('celebrating', 3000);
        break;
      case 'chat_message':
        changeAnimation('talking', 2000);
        break;
      case 'music_played':
        changeAnimation('listening');
        break;
      default:
        changeAnimation('idle');
    }
  };

  // 切换主题
  const toggleTheme = () => {
    const newTheme = theme === lightTheme ? darkTheme : lightTheme;
    setTheme(newTheme);
    
    const themeMode = newTheme === darkTheme ? 'dark' : 'light';
    updateAppSettings({ theme: themeMode });
    
    // 保存设置
    if (window.electronAPI) {
      window.electronAPI.saveSettings({ theme: themeMode });
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <AppContainer>
        <Router>
          <MainContent>
            <AnimatedRoutes />
          </MainContent>
        </Router>

        {/* 桌宠组件 */}
        <DesktopPet 
          onModuleActivation={handleModuleActivation}
          onAnimationChange={handleAnimationChange}
          onInteraction={handlePetInteraction}
        />

        {/* 模块化功能组件 */}
        <AnimatePresence>
          {modules['music-player']?.isActive && (
            <Modal
              isOpen={true}
              onClose={() => handleModuleDeactivation('music-player')}
              title="🎵 音乐播放器"
              maxWidth="600px"
            >
              <MusicPlayer onAnimationChange={handleAnimationChange} />
            </Modal>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {modules['rag-chat']?.isActive && (
            <Modal
              isOpen={true}
              onClose={() => handleModuleDeactivation('rag-chat')}
              title="🤖 智能问答"
              maxWidth="700px"
            >
              <RagChat onAnimationChange={handleAnimationChange} />
            </Modal>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {modules['word-capsule']?.isActive && (
            <Modal
              isOpen={true}
              onClose={() => handleModuleDeactivation('word-capsule')}
              title="📚 学习胶囊"
              maxWidth="800px"
            >
              <WordCapsule 
                onAnimationChange={handleAnimationChange}
                onInteraction={handlePetInteraction}
              />
            </Modal>
          )}
        </AnimatePresence>

        {/* 通知显示组件 */}
        <div className="notifications-container">
          {notifications.map(notification => (
            <div key={notification.id} className="notification">
              {notification.title && <strong>{notification.title}</strong>}
              <p>{notification.message}</p>
            </div>
          ))}
        </div>

        {/* 全局通知 */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: theme.surface,
              color: theme.text,
              borderRadius: '15px',
              padding: '16px',
              boxShadow: '0 8px 25px rgba(0,0,0,0.1)',
            },
          }}
        />
      </AppContainer>
    </ThemeProvider>
  );
};

// 导出全局方法供Electron调用
if (typeof window !== 'undefined') {
  window.activateModule = (moduleName) => {
    // 通过自定义事件触发模块激活
    window.dispatchEvent(new CustomEvent('activateModule', { 
      detail: { moduleName } 
    }));
  };
  
  window.showWordCapsule = (wordData) => {
    window.dispatchEvent(new CustomEvent('showWordCapsule', { 
      detail: { wordData } 
    }));
  };
}

export default App;