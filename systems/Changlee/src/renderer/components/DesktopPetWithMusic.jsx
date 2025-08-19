/**
 * Changlee's Groove: 桌宠音乐集成模块
 * 增强版桌宠组件 - 集成音乐播放功能
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styled from 'styled-components';
import { useDrag } from 'react-use-gesture';
import { MusicPlayer } from '../features/music-player';

const PetContainer = styled(motion.div)`
  position: fixed;
  width: 120px;
  height: 120px;
  cursor: grab;
  user-select: none;
  z-index: 9999;
  
  &:active {
    cursor: grabbing;
  }
`;

const PetBody = styled(motion.div)`
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
  border-radius: 50% 50% 45% 45%;
  position: relative;
  box-shadow: 0 8px 25px rgba(255, 154, 158, 0.3);
  
  &::before {
    content: '';
    position: absolute;
    top: 15px;
    left: 20px;
    width: 15px;
    height: 25px;
    background: #ff9a9e;
    border-radius: 50% 50% 0 0;
    transform: rotate(-20deg);
  }
  
  &::after {
    content: '';
    position: absolute;
    top: 15px;
    right: 20px;
    width: 15px;
    height: 25px;
    background: #ff9a9e;
    border-radius: 50% 50% 0 0;
    transform: rotate(20deg);
  }
`;

const Eyes = styled.div`
  position: absolute;
  top: 35px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 15px;
`;

const Eye = styled(motion.div)`
  width: 12px;
  height: 12px;
  background: #333;
  border-radius: 50%;
`;

const Mouth = styled(motion.div)`
  position: absolute;
  bottom: 35px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 10px;
  border: 2px solid #333;
  border-top: none;
  border-radius: 0 0 20px 20px;
`;

// 音乐图标区域
const MusicIcon = styled(motion.div)`
  position: absolute;
  top: -15px;
  right: -15px;
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  z-index: 10;
  
  &:hover {
    transform: scale(1.1);
  }
`;

// 音乐播放状态指示器
const MusicIndicator = styled(motion.div)`
  position: absolute;
  top: -5px;
  left: -5px;
  width: 20px;
  height: 20px;
  background: linear-gradient(45deg, #ff6b6b, #feca57);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  animation: pulse 1.5s ease-in-out infinite;
  
  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.1); }
  }
`;

const Bottle = styled(motion.div)`
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  width: 25px;
  height: 35px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 8px 8px 15px 15px;
  box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
  cursor: pointer;
  
  &::before {
    content: '📜';
    position: absolute;
    top: 8px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 12px;
  }
  
  &::after {
    content: '';
    position: absolute;
    top: -5px;
    left: 50%;
    transform: translateX(-50%);
    width: 8px;
    height: 8px;
    background: #4facfe;
    border-radius: 50%;
  }
`;

const FloatingText = styled(motion.div)`
  position: absolute;
  top: -60px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.95);
  padding: 8px 12px;
  border-radius: 15px;
  font-size: 12px;
  color: #333;
  white-space: nowrap;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  
  &::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid rgba(255, 255, 255, 0.95);
  }
`;

const DesktopPetWithMusic = () => {
  const [position, setPosition] = useState({ x: 800, y: 600 });
  const [animationState, setAnimationState] = useState('idle');
  const [showBottle, setShowBottle] = useState(false);
  const [floatingText, setFloatingText] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  
  // 音乐播放器状态
  const [showMusicPlayer, setShowMusicPlayer] = useState(false);
  const [isPlayingMusic, setIsPlayingMusic] = useState(false);
  const [currentTrack, setCurrentTrack] = useState(null);
  
  const petRef = useRef(null);

  // 拖拽手势
  const bind = useDrag(({ down, movement: [mx, my], first, last }) => {
    if (first) {
      setIsDragging(true);
      setAnimationState('dragging');
    }
    
    if (last) {
      setIsDragging(false);
      setAnimationState(isPlayingMusic ? 'listening' : 'idle');
      // 通知主进程更新位置
      if (window.electronAPI) {
        window.electronAPI.updatePetPosition({ 
          x: position.x + mx, 
          y: position.y + my 
        });
      }
    }
    
    setPosition({ 
      x: position.x + mx, 
      y: position.y + my 
    });
  });

  // 动画状态管理
  const getAnimationVariants = () => {
    switch (animationState) {
      case 'idle':
        return {
          scale: [1, 1.05, 1],
          rotate: [0, -2, 2, 0],
          transition: { 
            duration: 3, 
            repeat: Infinity, 
            ease: "easeInOut" 
          }
        };
      case 'excited':
        return {
          scale: [1, 1.2, 1],
          rotate: [0, -5, 5, 0],
          transition: { 
            duration: 0.8, 
            repeat: 3, 
            ease: "easeInOut" 
          }
        };
      case 'listening':
        return {
          scale: [1, 1.08, 1.02, 1.08, 1],
          rotate: [0, -3, 3, -1, 1, 0],
          transition: { 
            duration: 2, 
            repeat: Infinity, 
            ease: "easeInOut" 
          }
        };
      case 'dragging':
        return {
          scale: 1.1,
          rotate: 0,
          transition: { duration: 0.2 }
        };
      default:
        return {};
    }
  };

  // 眨眼动画
  const blinkAnimation = {
    scaleY: [1, 0.1, 1],
    transition: {
      duration: 0.3,
      repeat: Infinity,
      repeatDelay: Math.random() * 3 + 2
    }
  };

  // 处理桌宠点击
  const handlePetClick = async (e) => {
    if (isDragging) return;
    e.stopPropagation();
    
    setAnimationState('excited');
    
    const interactions = [
      { text: '长离想听音乐了~', action: 'music' },
      { text: '要不要一起学习呢？', action: 'learning' },
      { text: '今天心情不错呢！', action: 'mood' },
      { text: '让我们放松一下吧~', action: 'relax' },
      { text: '音乐能让学习更有趣！', action: 'music' }
    ];
    
    const randomInteraction = interactions[Math.floor(Math.random() * interactions.length)];
    setFloatingText(randomInteraction.text);
    
    // 播放音效
    if (window.utils) {
      window.utils.playSound('pet-click');
    }
    
    setTimeout(() => {
      setAnimationState(isPlayingMusic ? 'listening' : 'idle');
      setFloatingText('');
    }, 3000);

    // 根据交互类型执行不同操作
    if (randomInteraction.action === 'learning') {
      // 获取学习内容
      try {
        if (window.backendAPI) {
          const nextWord = await window.backendAPI.getNextWord();
          if (nextWord.success && nextWord.data) {
            setTimeout(() => {
              setShowBottle(true);
              setFloatingText(`新单词: ${nextWord.data.word}`);
            }, 1000);
          }
        }
      } catch (error) {
        console.error('获取学习内容失败:', error);
      }
    } else if (randomInteraction.action === 'music') {
      // 显示音乐播放器
      setTimeout(() => {
        setShowMusicPlayer(true);
        setFloatingText('打开音乐播放器~');
      }, 1000);
    }
  };

  // 处理漂流瓶点击
  const handleBottleClick = async (e) => {
    e.stopPropagation();
    
    setShowBottle(false);
    setFloatingText('打开学习胶囊...');
    
    // 播放音效
    if (window.utils) {
      window.utils.playSound('bottle-open');
    }
    
    // 这里可以触发学习模块
    setTimeout(() => {
      setFloatingText('');
    }, 2000);
  };

  // 处理音乐图标点击
  const handleMusicIconClick = (e) => {
    e.stopPropagation();
    setShowMusicPlayer(true);
    setFloatingText('🎵 Changlee\'s Groove');
    
    setTimeout(() => {
      setFloatingText('');
    }, 2000);
  };

  // 处理音乐播放状态变化
  const handlePlayingStateChange = (playing, track) => {
    setIsPlayingMusic(playing);
    setCurrentTrack(track);
    
    if (playing && !isDragging) {
      setAnimationState('listening');
      if (track) {
        setFloatingText(`🎵 ${track.title}`);
        setTimeout(() => setFloatingText(''), 3000);
      }
    } else if (!playing && !isDragging) {
      setAnimationState('idle');
    }
  };

  // 初始化位置
  useEffect(() => {
    if (window.electronAPI) {
      window.electronAPI.getPetPosition().then(pos => {
        if (pos) {
          setPosition(pos);
        }
      });
    }
  }, []);

  return (
    <>
      <PetContainer
        ref={petRef}
        {...bind()}
        style={{
          x: position.x,
          y: position.y,
          touchAction: 'none'
        }}
        animate={getAnimationVariants()}
        onClick={handlePetClick}
      >
        <PetBody>
          <Eyes>
            <Eye animate={blinkAnimation} />
            <Eye animate={blinkAnimation} />
          </Eyes>
          <Mouth
            animate={{
              scaleY: animationState === 'excited' ? [1, 1.5, 1] : 
                     animationState === 'listening' ? [1, 1.2, 1] : 1,
              transition: { duration: 0.3 }
            }}
          />
        </PetBody>

        {/* 音乐控制图标 */}
        <MusicIcon
          onClick={handleMusicIconClick}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          🎵
        </MusicIcon>

        {/* 音乐播放状态指示器 */}
        <AnimatePresence>
          {isPlayingMusic && (
            <MusicIndicator
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
            >
              🎶
            </MusicIndicator>
          )}
        </AnimatePresence>

        {/* 学习胶囊 */}
        <AnimatePresence>
          {showBottle && (
            <Bottle
              initial={{ scale: 0, y: -20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0, y: -20 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
              onClick={handleBottleClick}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            />
          )}
        </AnimatePresence>

        {/* 浮动文字 */}
        <AnimatePresence>
          {floatingText && (
            <FloatingText
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
            >
              {floatingText}
            </FloatingText>
          )}
        </AnimatePresence>
      </PetContainer>

      {/* 音乐播放器 */}
      <MusicPlayer
        isVisible={showMusicPlayer}
        onClose={() => setShowMusicPlayer(false)}
        onPlayingStateChange={handlePlayingStateChange}
      />
    </>
  );
};

export default DesktopPetWithMusic;