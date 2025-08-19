import React from 'react';
import { motion } from 'framer-motion';

const WordProgress = ({ progress }) => {
  const { 
    todayLearned = 0, 
    todayTarget = 10, 
    totalMastered = 0, 
    streakDays = 0,
    level = 1,
    experiencePoints = 0,
    nextLevelXP = 100
  } = progress || {};

  const todayProgress = (todayLearned / todayTarget) * 100;
  const levelProgress = (experiencePoints / nextLevelXP) * 100;

  return (
    <div className="word-progress">
      <div className="progress-header">
        <h3>📊 学习进度</h3>
        <div className="level-badge">
          Lv.{level}
        </div>
      </div>

      {/* 今日进度 */}
      <div className="progress-section">
        <div className="progress-label">
          <span>今日目标</span>
          <span>{todayLearned}/{todayTarget}</span>
        </div>
        <div className="progress-bar">
          <motion.div
            className="progress-fill today"
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(todayProgress, 100)}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* 等级进度 */}
      <div className="progress-section">
        <div className="progress-label">
          <span>经验值</span>
          <span>{experiencePoints}/{nextLevelXP} XP</span>
        </div>
        <div className="progress-bar">
          <motion.div
            className="progress-fill level"
            initial={{ width: 0 }}
            animate={{ width: `${levelProgress}%` }}
            transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
          />
        </div>
      </div>

      {/* 统计信息 */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-info">
            <div className="stat-number">{totalMastered}</div>
            <div className="stat-label">掌握单词</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🔥</div>
          <div className="stat-info">
            <div className="stat-number">{streakDays}</div>
            <div className="stat-label">连续天数</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-info">
            <div className="stat-number">{level}</div>
            <div className="stat-label">当前等级</div>
          </div>
        </div>
      </div>

      {/* 成就提示 */}
      {todayProgress >= 100 && (
        <motion.div
          className="achievement-notification"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5 }}
        >
          🎉 今日目标达成！
        </motion.div>
      )}

      {streakDays > 0 && streakDays % 7 === 0 && (
        <motion.div
          className="achievement-notification"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2 }}
        >
          🏆 连续学习{streakDays}天！
        </motion.div>
      )}
    </div>
  );
};

export default WordProgress;