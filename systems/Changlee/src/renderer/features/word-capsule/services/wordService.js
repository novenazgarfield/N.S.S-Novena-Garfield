// 单词学习服务
class WordService {
  constructor() {
    this.storageKeys = {
      wordList: 'word_learning_list',
      progress: 'word_learning_progress',
      history: 'word_learning_history'
    };
  }

  // 获取单词列表
  async getWordList() {
    try {
      // 首先尝试从本地存储获取
      const stored = localStorage.getItem(this.storageKeys.wordList);
      if (stored) {
        return JSON.parse(stored);
      }

      // 如果没有本地数据，加载默认单词列表
      const defaultWords = await this.loadDefaultWordList();
      await this.saveWordList(defaultWords);
      return defaultWords;
    } catch (error) {
      console.error('获取单词列表失败:', error);
      return [];
    }
  }

  // 加载默认单词列表
  async loadDefaultWordList() {
    // 这里可以从文件或API加载单词列表
    // 现在返回一些示例单词
    return [
      {
        id: 'word_1',
        word: 'adventure',
        phonetic: '/ədˈventʃər/',
        definition: '冒险；奇遇',
        difficulty: 'intermediate',
        category: 'noun',
        mastered: false,
        learning: false,
        lastReviewed: null,
        reviewCount: 0,
        correctCount: 0
      },
      {
        id: 'word_2',
        word: 'brilliant',
        phonetic: '/ˈbrɪljənt/',
        definition: '聪明的；杰出的；明亮的',
        difficulty: 'intermediate',
        category: 'adjective',
        mastered: false,
        learning: false,
        lastReviewed: null,
        reviewCount: 0,
        correctCount: 0
      },
      {
        id: 'word_3',
        word: 'curious',
        phonetic: '/ˈkjʊriəs/',
        definition: '好奇的；奇特的',
        difficulty: 'beginner',
        category: 'adjective',
        mastered: false,
        learning: false,
        lastReviewed: null,
        reviewCount: 0,
        correctCount: 0
      },
      {
        id: 'word_4',
        word: 'delightful',
        phonetic: '/dɪˈlaɪtfəl/',
        definition: '令人愉快的；可爱的',
        difficulty: 'intermediate',
        category: 'adjective',
        mastered: false,
        learning: false,
        lastReviewed: null,
        reviewCount: 0,
        correctCount: 0
      },
      {
        id: 'word_5',
        word: 'explore',
        phonetic: '/ɪkˈsplɔːr/',
        definition: '探索；探究',
        difficulty: 'beginner',
        category: 'verb',
        mastered: false,
        learning: false,
        lastReviewed: null,
        reviewCount: 0,
        correctCount: 0
      }
    ];
  }

  // 保存单词列表
  async saveWordList(wordList) {
    try {
      localStorage.setItem(this.storageKeys.wordList, JSON.stringify(wordList));
    } catch (error) {
      console.error('保存单词列表失败:', error);
    }
  }

  // 获取学习进度
  async getProgress() {
    try {
      const stored = localStorage.getItem(this.storageKeys.progress);
      if (stored) {
        return JSON.parse(stored);
      }

      // 返回默认进度
      return {
        todayLearned: 0,
        todayTarget: 10,
        totalMastered: 0,
        streakDays: 0,
        level: 1,
        experiencePoints: 0,
        nextLevelXP: 100,
        lastStudyDate: null
      };
    } catch (error) {
      console.error('获取学习进度失败:', error);
      return {};
    }
  }

  // 保存学习进度
  async saveProgress(progress) {
    try {
      localStorage.setItem(this.storageKeys.progress, JSON.stringify(progress));
    } catch (error) {
      console.error('保存学习进度失败:', error);
    }
  }

  // 更新学习进度
  async updateProgress(result) {
    const currentProgress = await this.getProgress();
    const today = new Date().toDateString();
    const lastStudyDate = currentProgress.lastStudyDate;

    // 更新今日学习数量
    if (lastStudyDate !== today) {
      // 新的一天
      currentProgress.todayLearned = 1;
      
      // 更新连续天数
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      if (lastStudyDate === yesterday.toDateString()) {
        currentProgress.streakDays += 1;
      } else if (lastStudyDate !== today) {
        currentProgress.streakDays = 1;
      }
    } else {
      currentProgress.todayLearned += 1;
    }

    currentProgress.lastStudyDate = today;

    // 更新经验值
    let xpGained = 10; // 基础经验值
    if (result.isCorrect) {
      xpGained += 5; // 正确答案额外经验
    }
    if (result.mistakes === 0) {
      xpGained += 5; // 无错误额外经验
    }
    if (result.timeSpent < 30000) { // 30秒内完成
      xpGained += 3; // 快速完成额外经验
    }

    currentProgress.experiencePoints += xpGained;

    // 检查升级
    while (currentProgress.experiencePoints >= currentProgress.nextLevelXP) {
      currentProgress.experiencePoints -= currentProgress.nextLevelXP;
      currentProgress.level += 1;
      currentProgress.nextLevelXP = Math.floor(currentProgress.nextLevelXP * 1.2);
    }

    // 更新掌握单词数
    if (result.isCorrect && result.wordMastered) {
      currentProgress.totalMastered += 1;
    }

    await this.saveProgress(currentProgress);
    return currentProgress;
  }

  // 获取学习历史
  async getLearningHistory() {
    try {
      const stored = localStorage.getItem(this.storageKeys.history);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('获取学习历史失败:', error);
      return [];
    }
  }

  // 保存学习历史
  async saveLearningHistory(history) {
    try {
      // 只保留最近1000条记录
      const limitedHistory = history.slice(-1000);
      localStorage.setItem(this.storageKeys.history, JSON.stringify(limitedHistory));
    } catch (error) {
      console.error('保存学习历史失败:', error);
    }
  }

  // 更新单词进度
  async updateWordProgress(wordId, result) {
    const wordList = await this.getWordList();
    const wordIndex = wordList.findIndex(word => word.id === wordId);
    
    if (wordIndex === -1) return null;

    const word = wordList[wordIndex];
    
    // 更新单词统计
    word.reviewCount += 1;
    word.lastReviewed = Date.now();
    word.learning = true;

    if (result.isCorrect) {
      word.correctCount += 1;
    }

    // 判断是否掌握（连续3次正确或正确率超过80%且复习次数>=5）
    const accuracy = word.correctCount / word.reviewCount;
    if ((word.correctCount >= 3 && result.isCorrect) || 
        (accuracy >= 0.8 && word.reviewCount >= 5)) {
      word.mastered = true;
      result.wordMastered = true;
    }

    wordList[wordIndex] = word;
    await this.saveWordList(wordList);
    
    return word;
  }

  // 智能选择下一个单词
  selectNextWord(unmasteredWords, learningHistory) {
    if (unmasteredWords.length === 0) return null;

    // 按优先级排序：
    // 1. 从未学习的新单词
    // 2. 需要复习的单词（基于遗忘曲线）
    // 3. 学习中但还未掌握的单词

    const now = Date.now();
    const newWords = unmasteredWords.filter(word => !word.learning);
    const learningWords = unmasteredWords.filter(word => word.learning);

    // 如果有新单词，优先选择新单词
    if (newWords.length > 0) {
      return newWords[0];
    }

    // 选择需要复习的单词
    const wordsNeedReview = learningWords.filter(word => {
      if (!word.lastReviewed) return true;
      
      const timeSinceReview = now - word.lastReviewed;
      const reviewInterval = this.calculateReviewInterval(word);
      
      return timeSinceReview >= reviewInterval;
    });

    if (wordsNeedReview.length > 0) {
      // 按最后复习时间排序，最久未复习的优先
      wordsNeedReview.sort((a, b) => (a.lastReviewed || 0) - (b.lastReviewed || 0));
      return wordsNeedReview[0];
    }

    // 如果没有需要复习的，返回任意一个学习中的单词
    return learningWords[0] || null;
  }

  // 计算复习间隔（基于遗忘曲线）
  calculateReviewInterval(word) {
    const baseInterval = 24 * 60 * 60 * 1000; // 24小时
    const accuracy = word.reviewCount > 0 ? word.correctCount / word.reviewCount : 0;
    
    // 根据正确率调整间隔
    let multiplier = 1;
    if (accuracy >= 0.9) multiplier = 3;
    else if (accuracy >= 0.7) multiplier = 2;
    else if (accuracy >= 0.5) multiplier = 1.5;
    else multiplier = 0.5;

    return baseInterval * multiplier;
  }

  // 重置进度
  async resetProgress() {
    try {
      localStorage.removeItem(this.storageKeys.progress);
      localStorage.removeItem(this.storageKeys.history);
      
      // 重置单词状态
      const wordList = await this.getWordList();
      const resetWords = wordList.map(word => ({
        ...word,
        mastered: false,
        learning: false,
        lastReviewed: null,
        reviewCount: 0,
        correctCount: 0
      }));
      
      await this.saveWordList(resetWords);
    } catch (error) {
      console.error('重置进度失败:', error);
    }
  }

  // 导出学习数据
  async exportLearningData() {
    try {
      const wordList = await this.getWordList();
      const progress = await this.getProgress();
      const history = await this.getLearningHistory();

      return {
        wordList,
        progress,
        history,
        exportDate: new Date().toISOString()
      };
    } catch (error) {
      console.error('导出学习数据失败:', error);
      return null;
    }
  }

  // 导入学习数据
  async importLearningData(data) {
    try {
      if (data.wordList) {
        await this.saveWordList(data.wordList);
      }
      if (data.progress) {
        await this.saveProgress(data.progress);
      }
      if (data.history) {
        await this.saveLearningHistory(data.history);
      }
      return true;
    } catch (error) {
      console.error('导入学习数据失败:', error);
      return false;
    }
  }
}

export const wordService = new WordService();