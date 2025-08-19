import { useState, useCallback } from 'react';

// 动画状态管理Hook
export const useAnimation = (initialAnimation = 'idle') => {
  const [currentAnimation, setCurrentAnimation] = useState(initialAnimation);
  const [animationQueue, setAnimationQueue] = useState([]);

  // 切换动画
  const changeAnimation = useCallback((newAnimation, duration = null) => {
    setCurrentAnimation(newAnimation);
    
    // 如果指定了持续时间，自动切换回idle
    if (duration) {
      setTimeout(() => {
        setCurrentAnimation('idle');
      }, duration);
    }
  }, []);

  // 添加动画到队列
  const queueAnimation = useCallback((animation, duration = 3000) => {
    setAnimationQueue(prev => [...prev, { animation, duration }]);
  }, []);

  // 播放动画队列
  const playAnimationQueue = useCallback(() => {
    if (animationQueue.length === 0) return;

    const [nextAnimation, ...remainingQueue] = animationQueue;
    setAnimationQueue(remainingQueue);
    
    changeAnimation(nextAnimation.animation, nextAnimation.duration);
  }, [animationQueue, changeAnimation]);

  // 清空动画队列
  const clearAnimationQueue = useCallback(() => {
    setAnimationQueue([]);
  }, []);

  // 获取动画配置
  const getAnimationConfig = useCallback((animationType) => {
    const configs = {
      idle: {
        duration: 0,
        loop: true,
        emoji: '😊'
      },
      thinking: {
        duration: 2000,
        loop: false,
        emoji: '🤔'
      },
      talking: {
        duration: 1000,
        loop: false,
        emoji: '😄'
      },
      listening: {
        duration: 0,
        loop: true,
        emoji: '🎵'
      },
      studying: {
        duration: 0,
        loop: true,
        emoji: '📚'
      },
      practicing: {
        duration: 0,
        loop: true,
        emoji: '✍️'
      },
      celebrating: {
        duration: 3000,
        loop: false,
        emoji: '🎉'
      },
      sleeping: {
        duration: 0,
        loop: true,
        emoji: '😴'
      },
      excited: {
        duration: 2000,
        loop: false,
        emoji: '🤩'
      },
      confused: {
        duration: 2000,
        loop: false,
        emoji: '😕'
      }
    };

    return configs[animationType] || configs.idle;
  }, []);

  return {
    currentAnimation,
    animationQueue,
    changeAnimation,
    queueAnimation,
    playAnimationQueue,
    clearAnimationQueue,
    getAnimationConfig
  };
};