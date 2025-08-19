import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import LearningCapsule from './LearningCapsule';
import MagicBeach from './MagicBeach';
import WordProgress from './WordProgress';
import { useWordLearning } from '../hooks/useWordLearning';

const WordCapsule = ({ onAnimationChange }) => {
  const [currentView, setCurrentView] = useState('menu'); // 'menu' | 'learning' | 'practice'
  const [selectedWord, setSelectedWord] = useState(null);
  
  const {
    currentWord,
    wordList,
    progress,
    loadNextWord,
    markWordCompleted,
    resetProgress
  } = useWordLearning();

  const handleStartLearning = () => {
    const word = loadNextWord();
    if (word) {
      setSelectedWord(word);
      setCurrentView('learning');
      if (onAnimationChange) {
        onAnimationChange('studying');
      }
    }
  };

  const handleStartPractice = (wordData) => {
    setSelectedWord(wordData);
    setCurrentView('practice');
    if (onAnimationChange) {
      onAnimationChange('practicing');
    }
  };

  const handlePracticeComplete = (result) => {
    markWordCompleted(result);
    setCurrentView('menu');
    if (onAnimationChange) {
      onAnimationChange('celebrating');
    }
    
    // 3秒后回到idle状态
    setTimeout(() => {
      if (onAnimationChange) {
        onAnimationChange('idle');
      }
    }, 3000);
  };

  const handleClose = () => {
    setCurrentView('menu');
    setSelectedWord(null);
    if (onAnimationChange) {
      onAnimationChange('idle');
    }
  };

  return (
    <div className="word-capsule">
      <AnimatePresence mode="wait">
        {currentView === 'menu' && (
          <motion.div
            key="menu"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="word-menu"
          >
            <div className="menu-header">
              <h2>📚 长离的学习胶囊</h2>
              <p>和长离一起学习新单词吧！</p>
            </div>

            <WordProgress progress={progress} />

            <div className="menu-actions">
              <motion.button
                className="action-btn primary"
                onClick={handleStartLearning}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                disabled={!currentWord}
              >
                🌟 开始学习
              </motion.button>

              <motion.button
                className="action-btn secondary"
                onClick={() => {
                  // 显示单词列表或其他功能
                }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                📖 单词本
              </motion.button>

              <motion.button
                className="action-btn secondary"
                onClick={resetProgress}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                🔄 重置进度
              </motion.button>
            </div>

            <div className="stats">
              <div className="stat-item">
                <span className="stat-label">今日学习</span>
                <span className="stat-value">{progress.todayLearned}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">总计掌握</span>
                <span className="stat-value">{progress.totalMastered}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">学习天数</span>
                <span className="stat-value">{progress.streakDays}</span>
              </div>
            </div>
          </motion.div>
        )}

        {currentView === 'learning' && selectedWord && (
          <LearningCapsule
            key="learning"
            wordData={selectedWord}
            onClose={handleClose}
            onStartPractice={handleStartPractice}
            onAnimationChange={onAnimationChange}
          />
        )}

        {currentView === 'practice' && selectedWord && (
          <MagicBeach
            key="practice"
            wordData={selectedWord}
            onComplete={handlePracticeComplete}
            onClose={handleClose}
            onAnimationChange={onAnimationChange}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default WordCapsule;