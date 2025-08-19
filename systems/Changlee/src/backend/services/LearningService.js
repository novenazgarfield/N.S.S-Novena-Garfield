class LearningService {
  constructor(database) {
    this.db = database;
  }

  // 获取下一个需要学习的单词（基于间隔重复算法）
  async getNextWordToLearn() {
    try {
      // 优先获取需要复习的单词
      let word = await this.db.get(`
        SELECT w.*, lr.* 
        FROM words w 
        JOIN learning_records lr ON w.id = lr.word_id 
        WHERE lr.next_review <= datetime('now') 
        ORDER BY lr.next_review ASC, lr.ease_factor ASC 
        LIMIT 1
      `);

      // 如果没有需要复习的，获取新单词
      if (!word) {
        word = await this.db.get(`
          SELECT w.*, lr.* 
          FROM words w 
          JOIN learning_records lr ON w.id = lr.word_id 
          WHERE lr.status = 'new' 
          ORDER BY w.difficulty ASC, RANDOM() 
          LIMIT 1
        `);
      }

      if (!word) {
        // 如果没有新单词，随机选择一个学习中的单词
        word = await this.db.get(`
          SELECT w.*, lr.* 
          FROM words w 
          JOIN learning_records lr ON w.id = lr.word_id 
          WHERE lr.status = 'learning' 
          ORDER BY RANDOM() 
          LIMIT 1
        `);
      }

      return word;
    } catch (error) {
      console.error('获取下一个学习单词失败:', error);
      throw error;
    }
  }

  // 更新单词学习状态（间隔重复算法核心）
  async updateWordStatus(wordId, result) {
    try {
      const { quality, timeSpent } = result; // quality: 0-5 (0=完全不记得, 5=完美记住)
      
      const learningRecord = await this.db.get(
        'SELECT * FROM learning_records WHERE word_id = ?',
        [wordId]
      );

      if (!learningRecord) {
        throw new Error('学习记录不存在');
      }

      // 计算新的间隔和难度因子
      const newRecord = this.calculateSpacedRepetition(learningRecord, quality);
      
      // 更新学习记录
      await this.db.run(`
        UPDATE learning_records 
        SET status = ?, review_count = ?, correct_count = ?, 
            last_reviewed = datetime('now'), next_review = ?, 
            ease_factor = ?, interval_days = ?, updated_at = datetime('now')
        WHERE word_id = ?
      `, [
        newRecord.status,
        newRecord.review_count,
        newRecord.correct_count,
        newRecord.next_review,
        newRecord.ease_factor,
        newRecord.interval_days,
        wordId
      ]);

      // 记录学习统计
      await this.recordLearningActivity(wordId, quality, timeSpent);

      return newRecord;
    } catch (error) {
      console.error('更新单词状态失败:', error);
      throw error;
    }
  }

  // 间隔重复算法实现（基于SM-2算法）
  calculateSpacedRepetition(record, quality) {
    const { review_count, correct_count, ease_factor, interval_days } = record;
    
    let newEaseFactor = ease_factor;
    let newInterval = interval_days;
    let newStatus = record.status;
    let newCorrectCount = correct_count;

    // 更新复习次数
    const newReviewCount = review_count + 1;

    // 如果回答正确（quality >= 3）
    if (quality >= 3) {
      newCorrectCount += 1;

      // 计算新的难度因子
      newEaseFactor = Math.max(1.3, ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)));

      // 计算新的间隔
      if (newReviewCount === 1) {
        newInterval = 1;
      } else if (newReviewCount === 2) {
        newInterval = 6;
      } else {
        newInterval = Math.round(interval_days * newEaseFactor);
      }

      // 更新状态
      if (newReviewCount >= 3 && quality >= 4 && newInterval >= 21) {
        newStatus = 'mastered';
      } else if (newStatus === 'new') {
        newStatus = 'learning';
      }
    } else {
      // 回答错误，重置间隔
      newInterval = 1;
      newEaseFactor = Math.max(1.3, ease_factor - 0.2);
      
      if (newStatus === 'mastered') {
        newStatus = 'learning';
      }
    }

    // 计算下次复习时间
    const nextReview = new Date();
    nextReview.setDate(nextReview.getDate() + newInterval);

    return {
      status: newStatus,
      review_count: newReviewCount,
      correct_count: newCorrectCount,
      ease_factor: newEaseFactor,
      interval_days: newInterval,
      next_review: nextReview.toISOString().slice(0, 19).replace('T', ' ')
    };
  }

  // 提交拼写练习结果
  async submitSpellingResult(wordId, result) {
    try {
      const { isCorrect, timeSpent, mistakes = 0, userInput } = result;

      // 记录拼写练习
      await this.db.run(`
        INSERT INTO spelling_records (word_id, is_correct, time_spent, mistakes) 
        VALUES (?, ?, ?, ?)
      `, [wordId, isCorrect, timeSpent, mistakes]);

      // 根据拼写结果更新学习状态
      const quality = isCorrect ? (mistakes === 0 ? 5 : 4) : (mistakes <= 2 ? 2 : 1);
      
      return await this.updateWordStatus(wordId, { quality, timeSpent });
    } catch (error) {
      console.error('提交拼写结果失败:', error);
      throw error;
    }
  }

  // 获取学习进度
  async getLearningProgress() {
    try {
      // 总体统计
      const overallStats = await this.db.get(`
        SELECT 
          COUNT(*) as total_words,
          COUNT(CASE WHEN lr.status = 'new' THEN 1 END) as new_words,
          COUNT(CASE WHEN lr.status = 'learning' THEN 1 END) as learning_words,
          COUNT(CASE WHEN lr.status = 'mastered' THEN 1 END) as mastered_words,
          AVG(CASE WHEN lr.review_count > 0 THEN (lr.correct_count * 100.0 / lr.review_count) END) as accuracy_rate
        FROM words w
        JOIN learning_records lr ON w.id = lr.word_id
      `);

      // 今日学习统计
      const todayStats = await this.db.get(`
        SELECT 
          COUNT(DISTINCT sr.word_id) as words_practiced,
          COUNT(*) as total_attempts,
          COUNT(CASE WHEN sr.is_correct THEN 1 END) as correct_attempts,
          AVG(sr.time_spent) as avg_time_spent
        FROM spelling_records sr
        WHERE DATE(sr.attempt_time) = DATE('now')
      `);

      // 学习连续天数
      const streakDays = await this.calculateLearningStreak();

      // 本周学习统计
      const weeklyStats = await this.db.all(`
        SELECT 
          DATE(sr.attempt_time) as date,
          COUNT(DISTINCT sr.word_id) as words_count,
          COUNT(*) as attempts_count,
          COUNT(CASE WHEN sr.is_correct THEN 1 END) as correct_count
        FROM spelling_records sr
        WHERE sr.attempt_time >= datetime('now', '-7 days')
        GROUP BY DATE(sr.attempt_time)
        ORDER BY date
      `);

      return {
        overall: overallStats,
        today: todayStats,
        streakDays,
        weekly: weeklyStats,
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      console.error('获取学习进度失败:', error);
      throw error;
    }
  }

  // 计算学习连续天数
  async calculateLearningStreak() {
    try {
      const learningDays = await this.db.all(`
        SELECT DISTINCT DATE(attempt_time) as date
        FROM spelling_records
        WHERE attempt_time >= datetime('now', '-30 days')
        ORDER BY date DESC
      `);

      let streak = 0;
      const today = new Date().toISOString().split('T')[0];
      
      for (let i = 0; i < learningDays.length; i++) {
        const expectedDate = new Date();
        expectedDate.setDate(expectedDate.getDate() - i);
        const expectedDateStr = expectedDate.toISOString().split('T')[0];
        
        if (learningDays[i].date === expectedDateStr) {
          streak++;
        } else {
          break;
        }
      }

      return streak;
    } catch (error) {
      console.error('计算学习连续天数失败:', error);
      return 0;
    }
  }

  // 记录学习活动
  async recordLearningActivity(wordId, quality, timeSpent) {
    try {
      const today = new Date().toISOString().split('T')[0];
      
      // 检查今日统计记录是否存在
      let todayStats = await this.db.get(
        'SELECT * FROM learning_stats WHERE date = ?',
        [today]
      );

      if (!todayStats) {
        // 创建今日统计记录
        await this.db.run(`
          INSERT INTO learning_stats (date, words_learned, words_reviewed, time_spent, accuracy_rate) 
          VALUES (?, 0, 0, 0, 0)
        `, [today]);
        
        todayStats = { words_learned: 0, words_reviewed: 0, time_spent: 0, accuracy_rate: 0 };
      }

      // 更新统计
      const isCorrect = quality >= 3 ? 1 : 0;
      const newTimeSpent = (todayStats.time_spent || 0) + (timeSpent || 0);
      const newWordsReviewed = (todayStats.words_reviewed || 0) + 1;
      
      // 计算新的正确率
      const totalAttempts = await this.db.get(`
        SELECT COUNT(*) as count 
        FROM spelling_records 
        WHERE DATE(attempt_time) = ?
      `, [today]);
      
      const correctAttempts = await this.db.get(`
        SELECT COUNT(*) as count 
        FROM spelling_records 
        WHERE DATE(attempt_time) = ? AND is_correct = 1
      `, [today]);

      const newAccuracyRate = totalAttempts.count > 0 ? 
        (correctAttempts.count / totalAttempts.count) * 100 : 0;

      await this.db.run(`
        UPDATE learning_stats 
        SET words_reviewed = ?, time_spent = ?, accuracy_rate = ?, updated_at = datetime('now')
        WHERE date = ?
      `, [newWordsReviewed, newTimeSpent, newAccuracyRate, today]);

    } catch (error) {
      console.error('记录学习活动失败:', error);
    }
  }

  // 获取学习统计
  async getStatistics() {
    try {
      const stats = await this.getLearningProgress();
      
      // 获取最近30天的学习数据
      const monthlyData = await this.db.all(`
        SELECT 
          date,
          words_learned,
          words_reviewed,
          time_spent,
          accuracy_rate
        FROM learning_stats
        WHERE date >= date('now', '-30 days')
        ORDER BY date
      `);

      // 获取单词难度分布
      const difficultyDistribution = await this.db.all(`
        SELECT 
          w.difficulty,
          COUNT(*) as count,
          COUNT(CASE WHEN lr.status = 'mastered' THEN 1 END) as mastered_count
        FROM words w
        JOIN learning_records lr ON w.id = lr.word_id
        GROUP BY w.difficulty
        ORDER BY w.difficulty
      `);

      return {
        ...stats,
        monthlyData,
        difficultyDistribution,
        generatedAt: new Date().toISOString()
      };
    } catch (error) {
      console.error('获取学习统计失败:', error);
      throw error;
    }
  }

  // 更新每周统计
  async updateWeeklyStats() {
    try {
      const weekStart = new Date();
      weekStart.setDate(weekStart.getDate() - weekStart.getDay());
      const weekStartStr = weekStart.toISOString().split('T')[0];

      const weeklyStats = await this.db.get(`
        SELECT 
          COUNT(DISTINCT sr.word_id) as words_practiced,
          COUNT(*) as total_attempts,
          COUNT(CASE WHEN sr.is_correct THEN 1 END) as correct_attempts,
          SUM(sr.time_spent) as total_time
        FROM spelling_records sr
        WHERE DATE(sr.attempt_time) >= ?
      `, [weekStartStr]);

      console.log('本周学习统计:', weeklyStats);
      return weeklyStats;
    } catch (error) {
      console.error('更新每周统计失败:', error);
      throw error;
    }
  }

  // 重置单词学习进度
  async resetWordProgress(wordId) {
    try {
      await this.db.run(`
        UPDATE learning_records 
        SET status = 'new', review_count = 0, correct_count = 0, 
            last_reviewed = NULL, next_review = datetime('now', '+1 day'),
            ease_factor = 2.5, interval_days = 1, updated_at = datetime('now')
        WHERE word_id = ?
      `, [wordId]);

      return { success: true };
    } catch (error) {
      console.error('重置单词进度失败:', error);
      throw error;
    }
  }

  // 获取学习建议
  async getLearningRecommendations() {
    try {
      const progress = await this.getLearningProgress();
      const recommendations = [];

      // 基于学习进度给出建议
      if (progress.today.words_practiced < 5) {
        recommendations.push({
          type: 'daily_goal',
          message: '今天还没有达到学习目标，建议再学习几个单词',
          priority: 'high'
        });
      }

      if (progress.overall.accuracy_rate < 70) {
        recommendations.push({
          type: 'accuracy',
          message: '正确率偏低，建议放慢学习节奏，加强复习',
          priority: 'medium'
        });
      }

      if (progress.streakDays === 0) {
        recommendations.push({
          type: 'consistency',
          message: '保持每日学习习惯很重要，今天开始新的连续学习记录吧！',
          priority: 'high'
        });
      }

      return recommendations;
    } catch (error) {
      console.error('获取学习建议失败:', error);
      return [];
    }
  }
}

module.exports = LearningService;