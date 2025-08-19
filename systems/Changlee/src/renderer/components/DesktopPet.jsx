import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styled from 'styled-components';
import { useDrag } from 'react-use-gesture';

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
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 4px;
    height: 4px;
    background: white;
    border-radius: 50%;
  }
`;

const Mouth = styled(motion.div)`
  position: absolute;
  top: 55px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 10px;
  border: 2px solid #333;
  border-top: none;
  border-radius: 0 0 20px 20px;
`;

const Bottle = styled(motion.div)`
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  width: 25px;
  height: 35px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 8px 8px 15px 15px;
  box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
  
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

const DesktopPet = () => {
  const [position, setPosition] = useState({ x: 800, y: 600 });
  const [animationState, setAnimationState] = useState('idle');
  const [showBottle, setShowBottle] = useState(false);
  const [floatingText, setFloatingText] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const petRef = useRef(null);

  // 拖拽手势
  const bind = useDrag(({ down, movement: [mx, my], first, last }) => {
    if (first) {
      setIsDragging(true);
      setAnimationState('dragging');
    }
    
    if (last) {
      setIsDragging(false);
      setAnimationState('idle');
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
          y: [0, -10, 0],
          transition: { 
            duration: 0.6, 
            repeat: 3 
          }
        };
      case 'dragging':
        return {
          scale: 1.1,
          rotate: isDragging ? 5 : 0,
          transition: { duration: 0.2 }
        };
      default:
        return {};
    }
  };

  // 眼睛眨眼动画
  const blinkAnimation = {
    scaleY: [1, 0.1, 1],
    transition: { 
      duration: 0.3, 
      repeat: Infinity, 
      repeatDelay: Math.random() * 3 + 2 
    }
  };

  // 处理点击事件
  const handlePetClick = async () => {
    if (isDragging) return;
    
    setAnimationState('excited');
    
    // 随机选择不同的交互方式
    const interactions = [
      { text: '喵～ 想学习吗？', action: 'learning' },
      { text: '有什么问题要问我吗？', action: 'chat' },
      { text: '要上传学习资料吗？', action: 'document' },
      { text: '来练习单词吧！', action: 'practice' }
    ];
    
    const randomInteraction = interactions[Math.floor(Math.random() * interactions.length)];
    setFloatingText(randomInteraction.text);
    
    // 播放音效
    if (window.utils) {
      window.utils.playSound('pet-click');
    }
    
    setTimeout(() => {
      setAnimationState('idle');
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
    }
  };

  // 处理漂流瓶点击
  const handleBottleClick = async (e) => {
    e.stopPropagation();
    
    setShowBottle(false);
    setFloatingText('打开学习胶囊...');
    
    // 通知主进程显示学习界面
    if (window.electronAPI) {
      try {
        const nextWord = await window.backendAPI.getNextWord();
        await window.electronAPI.showLearningCapsule(nextWord.data);
      } catch (error) {
        console.error('打开学习胶囊失败:', error);
      }
    }
    
    setTimeout(() => {
      setFloatingText('');
    }, 1500);
  };

  // 监听推送事件
  useEffect(() => {
    const handlePush = (pushData) => {
      setShowBottle(true);
      setAnimationState('excited');
      setFloatingText(pushData.learningTip);
      
      // 播放通知音效
      if (window.utils) {
        window.utils.playSound('notification');
      }
      
      setTimeout(() => {
        setAnimationState('idle');
      }, 2000);
    };

    // 模拟推送事件监听
    const checkForPush = async () => {
      try {
        if (window.backendAPI) {
          const pushData = await window.backendAPI.getNextPush();
          if (pushData.success && pushData.data) {
            handlePush(pushData.data);
          }
        }
      } catch (error) {
        console.error('检查推送失败:', error);
      }
    };

    // 每30分钟检查一次推送
    const pushInterval = setInterval(checkForPush, 30 * 60 * 1000);
    
    return () => clearInterval(pushInterval);
  }, []);

  // 随机行为
  useEffect(() => {
    const randomBehavior = () => {
      if (isDragging || showBottle) return;
      
      const behaviors = ['idle', 'blink', 'yawn'];
      const randomBehavior = behaviors[Math.floor(Math.random() * behaviors.length)];
      
      switch (randomBehavior) {
        case 'blink':
          // 眨眼已经通过CSS动画处理
          break;
        case 'yawn':
          setFloatingText('哈～');
          setTimeout(() => setFloatingText(''), 2000);
          break;
        default:
          break;
      }
    };

    const behaviorInterval = setInterval(randomBehavior, 10000 + Math.random() * 20000);
    return () => clearInterval(behaviorInterval);
  }, [isDragging, showBottle]);

  return (
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
            scaleY: animationState === 'excited' ? [1, 1.5, 1] : 1,
            transition: { duration: 0.3 }
          }}
        />
      </PetBody>
      
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
  );
};

export default DesktopPet;