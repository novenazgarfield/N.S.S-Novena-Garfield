#!/usr/bin/env node

/**
 * 长离的学习胶囊 - 系统测试脚本
 * 用于测试各个模块的基本功能
 */

const path = require('path');
const fs = require('fs');

// 导入测试模块
const DatabaseManager = require('./src/backend/database/DatabaseManager');
const AIService = require('./src/backend/services/AIService');
const WordService = require('./src/backend/services/WordService');
const LearningService = require('./src/backend/services/LearningService');

class SystemTester {
  constructor() {
    this.db = null;
    this.aiService = null;
    this.wordService = null;
    this.learningService = null;
    this.testResults = [];
  }

  async runAllTests() {
    console.log('🧪 开始系统测试...');
    console.log('=====================================');

    try {
      await this.initializeServices();
      await this.testDatabase();
      await this.testAIService();
      await this.testWordService();
      await this.testLearningService();
      await this.testIntegration();
      
      this.printResults();
    } catch (error) {
      console.error('❌ 测试过程中出现错误:', error);
    } finally {
      await this.cleanup();
    }
  }

  async initializeServices() {
    console.log('🔧 初始化服务...');
    
    this.db = new DatabaseManager();
    await this.db.initialize();
    
    this.aiService = new AIService();
    this.wordService = new WordService(this.db);
    this.learningService = new LearningService(this.db);
    
    console.log('✅ 服务初始化完成');
  }

  async testDatabase() {
    console.log('\n📚 测试数据库功能...');
    
    try {
      // 测试数据库连接
      const result = await this.db.get('SELECT COUNT(*) as count FROM words');
      this.addTestResult('数据库连接', true, `找到 ${result.count} 个单词`);
      
      // 测试数据插入
      const testWord = {
        word: 'test_word_' + Date.now(),
        phonetic: '/test/',
        definition: '测试单词',
        difficulty: 1,
        category: 'test'
      };
      
      const insertResult = await this.db.run(
        'INSERT INTO words (word, phonetic, definition, difficulty, category) VALUES (?, ?, ?, ?, ?)',
        [testWord.word, testWord.phonetic, testWord.definition, testWord.difficulty, testWord.category]
      );
      
      this.addTestResult('数据插入', insertResult.id > 0, `插入ID: ${insertResult.id}`);
      
      // 清理测试数据
      await this.db.run('DELETE FROM words WHERE word LIKE ?', ['test_word_%']);
      
    } catch (error) {
      this.addTestResult('数据库测试', false, error.message);
    }
  }

  async testAIService() {
    console.log('\n🤖 测试AI服务...');
    
    try {
      // 测试API连接状态
      const apiStatus = await this.aiService.checkAPIStatus();
      this.addTestResult('AI API连接', apiStatus.status === 'connected', apiStatus.response || apiStatus.error);
      
      // 测试内容生成
      const testWordData = {
        word: 'example',
        definition: 'n. 例子，实例',
        phonetic: '/ɪɡˈzæmpl/',
        difficulty: 2
      };
      
      const content = await this.aiService.generateLearningContent(testWordData);
      this.addTestResult('AI内容生成', !!content.memoryStory, `生成了 ${Object.keys(content).length} 种内容`);
      
      // 测试问候语生成
      const greeting = await this.aiService.generateDailyGreeting();
      this.addTestResult('问候语生成', greeting.length > 0, `长度: ${greeting.length} 字符`);
      
    } catch (error) {
      this.addTestResult('AI服务测试', false, error.message);
    }
  }

  async testWordService() {
    console.log('\n📖 测试单词服务...');
    
    try {
      // 测试获取随机单词
      const randomWord = await this.wordService.getRandomWords(1);
      this.addTestResult('获取随机单词', !!randomWord, `单词: ${randomWord?.word || 'N/A'}`);
      
      // 测试单词统计
      const stats = await this.wordService.getWordStatistics();
      this.addTestResult('单词统计', !!stats.total_words, `总计: ${stats.total_words} 个单词`);
      
      // 测试单词搜索
      const searchResults = await this.wordService.searchWords('test', 5);
      this.addTestResult('单词搜索', Array.isArray(searchResults), `找到: ${searchResults.length} 个结果`);
      
    } catch (error) {
      this.addTestResult('单词服务测试', false, error.message);
    }
  }

  async testLearningService() {
    console.log('\n🎓 测试学习服务...');
    
    try {
      // 测试获取下一个学习单词
      const nextWord = await this.learningService.getNextWordToLearn();
      this.addTestResult('获取学习单词', !!nextWord, `单词: ${nextWord?.word || 'N/A'}`);
      
      // 测试学习进度
      const progress = await this.learningService.getLearningProgress();
      this.addTestResult('学习进度', !!progress.overall, `总单词: ${progress.overall?.total_words || 0}`);
      
      // 测试间隔重复算法
      if (nextWord) {
        const mockResult = { quality: 4, timeSpent: 5000 };
        const updateResult = await this.learningService.updateWordStatus(nextWord.id, mockResult);
        this.addTestResult('间隔重复算法', !!updateResult.status, `新状态: ${updateResult.status}`);
      }
      
      // 测试学习统计
      const stats = await this.learningService.getStatistics();
      this.addTestResult('学习统计', !!stats.overall, '统计数据获取成功');
      
    } catch (error) {
      this.addTestResult('学习服务测试', false, error.message);
    }
  }

  async testIntegration() {
    console.log('\n🔗 测试系统集成...');
    
    try {
      // 测试完整学习流程
      const word = await this.learningService.getNextWordToLearn();
      if (word) {
        // 生成AI内容
        const aiContent = await this.aiService.generateLearningContent(word);
        
        // 模拟拼写练习
        const spellingResult = {
          isCorrect: true,
          timeSpent: 3000,
          mistakes: 0,
          userInput: word.word
        };
        
        const practiceResult = await this.learningService.submitSpellingResult(word.id, spellingResult);
        
        this.addTestResult('完整学习流程', !!practiceResult, '学习流程测试成功');
      } else {
        this.addTestResult('完整学习流程', false, '没有可学习的单词');
      }
      
    } catch (error) {
      this.addTestResult('系统集成测试', false, error.message);
    }
  }

  addTestResult(testName, passed, details = '') {
    this.testResults.push({
      name: testName,
      passed,
      details,
      timestamp: new Date().toISOString()
    });
    
    const status = passed ? '✅' : '❌';
    const detailsStr = details ? ` - ${details}` : '';
    console.log(`${status} ${testName}${detailsStr}`);
  }

  printResults() {
    console.log('\n📊 测试结果汇总');
    console.log('=====================================');
    
    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(r => r.passed).length;
    const failedTests = totalTests - passedTests;
    
    console.log(`总测试数: ${totalTests}`);
    console.log(`通过: ${passedTests} ✅`);
    console.log(`失败: ${failedTests} ❌`);
    console.log(`成功率: ${((passedTests / totalTests) * 100).toFixed(1)}%`);
    
    if (failedTests > 0) {
      console.log('\n❌ 失败的测试:');
      this.testResults
        .filter(r => !r.passed)
        .forEach(r => {
          console.log(`  • ${r.name}: ${r.details}`);
        });
    }
    
    // 保存测试报告
    this.saveTestReport();
  }

  saveTestReport() {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        total: this.testResults.length,
        passed: this.testResults.filter(r => r.passed).length,
        failed: this.testResults.filter(r => !r.passed).length
      },
      results: this.testResults
    };
    
    const reportPath = path.join(__dirname, 'test-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\n📄 测试报告已保存: ${reportPath}`);
  }

  async cleanup() {
    console.log('\n🧹 清理测试环境...');
    
    try {
      if (this.db) {
        await this.db.close();
      }
      console.log('✅ 清理完成');
    } catch (error) {
      console.error('清理过程中出现错误:', error);
    }
  }
}

// 主函数
async function main() {
  const tester = new SystemTester();
  await tester.runAllTests();
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(error => {
    console.error('测试失败:', error);
    process.exit(1);
  });
}

module.exports = SystemTester;