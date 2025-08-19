import { useState, useEffect, useCallback } from 'react';
import { wordService } from '../services/wordService';

export const useWordLearning = () => {
  const [currentWord, setCurrentWord] = useState(null);
  const [wordList, setWordList] = useState([]);
  const [progress, setProgress] = useState({
    todayLearned: 0,
    todayTarget: 10,
    totalMastered: 0,
    streakDays: 0,
    level: 1,
    experiencePoints: 0,
    nextLevelXP: 100
  });
  const [learningHistory, setLearningHistory] = useState([]);

  // 初始化数据
  useEffect(() => {
    loadWordList();
    loadProgress();
    loadLearningHistory();
  }, []);

  // 加载单词列表
  const loadWordList = useCallback(async () => {
    try {
      const words = await wordService.getWordList();
      setWordList(words);
      
      // 设置当前单词为下一个未学习的单词
      const nextWord = words.find(word => !word.mastered);
      setCurrentWord(nextWord);
    } catch (error) {
      console.error('加载单词列表失败:', error);
    }
  }, []);

  // 加载学习进度
  const loadProgress = useCallback(async () => {
    try {
      const savedProgress = await wordService.getProgress();
      setProgress(savedProgress);
    } catch (error) {
      console.error('加载学习进度失败:', error);
    }
  }, []);

  // 加载学习历史
  const loadLearningHistory = useCallback(async () => {
    try {
      const history = await wordService.getLearningHistory();
      setLearningHistory(history);
    } catch (error) {
      console.error('加载学习历史失败:', error);
    }
  }, []);

  // 获取下一个单词
  const loadNextWord = useCallback(() => {
    const unmastered = wordList.filter(word => !word.mastered);
    if (unmastered.length === 0) {
      // 所有单词都已掌握，可以重新开始或加载新单词
      return null;
    }

    // 智能选择下一个单词（基于遗忘曲线和学习历史）
    const nextWord = wordService.selectNextWord(unmastered, learningHistory);
    setCurrentWord(nextWord);
    return nextWord;
  }, [wordList, learningHistory]);

  // 标记单词完成
  const markWordCompleted = useCallback(async (result) => {
    if (!currentWord) return;

    try {
      // 更新单词状态
      const updatedWord = await wordService.updateWordProgress(currentWord.id, result);
      
      // 更新单词列表
      setWordList(prev => prev.map(word => 
        word.id === currentWord.id ? updatedWord : word
      ));

      // 更新学习历史
      const historyEntry = {
        wordId: currentWord.id,
        word: currentWord.word,
        result,
        timestamp: Date.now()
      };
      setLearningHistory(prev => [...prev, historyEntry]);

      // 更新进度
      const newProgress = await wordService.updateProgress(result);
      setProgress(newProgress);

      // 保存数据
      await wordService.saveLearningHistory([...learningHistory, historyEntry]);
      await wordService.saveProgress(newProgress);

      // 加载下一个单词
      setTimeout(() => {
        loadNextWord();
      }, 1000);

    } catch (error) {
      console.error('标记单词完成失败:', error);
    }
  }, [currentWord, learningHistory, loadNextWord]);

  // 重置进度
  const resetProgress = useCallback(async () => {
    try {
      await wordService.resetProgress();
      await loadWordList();
      await loadProgress();
      setLearningHistory([]);
    } catch (error) {
      console.error('重置进度失败:', error);
    }
  }, [loadWordList, loadProgress]);

  // 获取单词统计
  const getWordStats = useCallback(() => {
    const total = wordList.length;
    const mastered = wordList.filter(word => word.mastered).length;
    const learning = wordList.filter(word => word.learning && !word.mastered).length;
    const new_words = total - mastered - learning;

    return {
      total,
      mastered,
      learning,
      new: new_words,
      masteredPercentage: total > 0 ? (mastered / total) * 100 : 0
    };
  }, [wordList]);

  // 获取今日学习统计
  const getTodayStats = useCallback(() => {
    const today = new Date().toDateString();
    const todayHistory = learningHistory.filter(entry => 
      new Date(entry.timestamp).toDateString() === today
    );

    const correct = todayHistory.filter(entry => entry.result.isCorrect).length;
    const total = todayHistory.length;
    const accuracy = total > 0 ? (correct / total) * 100 : 0;

    return {
      learned: total,
      correct,
      accuracy,
      timeSpent: todayHistory.reduce((sum, entry) => sum + (entry.result.timeSpent || 0), 0)
    };
  }, [learningHistory]);

  return {
    currentWord,
    wordList,
    progress,
    learningHistory,
    loadNextWord,
    markWordCompleted,
    resetProgress,
    getWordStats,
    getTodayStats
  };
};