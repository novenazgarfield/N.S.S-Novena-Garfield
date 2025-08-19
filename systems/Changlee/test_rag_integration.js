#!/usr/bin/env node

/**
 * RAG系统集成测试脚本
 * 测试桌宠系统与RAG系统的集成功能
 */

const axios = require('axios');
const path = require('path');

class RAGIntegrationTester {
  constructor() {
    this.ragURL = 'http://localhost:51658';
    this.petBackendURL = 'http://localhost:3001';
    this.testResults = [];
  }

  async runAllTests() {
    console.log('🧪 开始RAG集成测试...');
    console.log('=====================================');

    try {
      await this.testSystemConnectivity();
      await this.testRAGServiceIntegration();
      await this.testIntelligentQA();
      await this.testDocumentAnalysis();
      await this.testLearningRecommendations();
      await this.testProgressAnalysis();
      
      this.printResults();
    } catch (error) {
      console.error('❌ 测试过程中出现错误:', error);
    }
  }

  async testSystemConnectivity() {
    console.log('\n🔗 测试系统连接性...');
    
    try {
      // 测试RAG系统连接
      const ragResponse = await axios.get(this.ragURL, { timeout: 5000 });
      this.addTestResult('RAG系统连接', ragResponse.status === 200, `状态码: ${ragResponse.status}`);
      
      // 测试桌宠后端连接
      const backendResponse = await axios.get(`${this.petBackendURL}/health`, { timeout: 5000 });
      this.addTestResult('桌宠后端连接', backendResponse.status === 200, `状态码: ${backendResponse.status}`);
      
      // 测试RAG状态API
      const ragStatusResponse = await axios.get(`${this.petBackendURL}/api/rag/status`, { timeout: 5000 });
      this.addTestResult('RAG状态API', ragStatusResponse.data.success, JSON.stringify(ragStatusResponse.data.data));
      
    } catch (error) {
      this.addTestResult('系统连接测试', false, error.message);
    }
  }

  async testRAGServiceIntegration() {
    console.log('\n🤖 测试RAG服务集成...');
    
    try {
      // 测试基本问答功能
      const questionData = {
        question: '什么是英语学习的最佳方法？',
        context: {
          type: 'learning_method',
          userId: 'test_user'
        }
      };
      
      const response = await axios.post(`${this.petBackendURL}/api/rag/ask`, questionData, {
        timeout: 30000,
        headers: { 'Content-Type': 'application/json' }
      });
      
      const success = response.data.success && response.data.data && response.data.data.answer;
      this.addTestResult('RAG问答功能', success, success ? '回答长度: ' + response.data.data.answer.length : '无回答');
      
    } catch (error) {
      this.addTestResult('RAG服务集成', false, error.message);
    }
  }

  async testIntelligentQA() {
    console.log('\n💬 测试智能问答功能...');
    
    const testQuestions = [
      {
        question: '请解释单词 "abandon" 的含义',
        type: 'word_explanation'
      },
      {
        question: '英语语法中什么是现在完成时？',
        type: 'grammar_help'
      },
      {
        question: '如何提高英语口语能力？',
        type: 'learning_method'
      }
    ];

    for (const testQ of testQuestions) {
      try {
        const response = await axios.post(`${this.petBackendURL}/api/rag/ask`, {
          question: testQ.question,
          context: { type: testQ.type }
        }, { timeout: 30000 });

        const success = response.data.success && response.data.data.answer;
        this.addTestResult(`智能问答-${testQ.type}`, success, success ? '✅ 获得回答' : '❌ 无回答');
        
      } catch (error) {
        this.addTestResult(`智能问答-${testQ.type}`, false, error.message);
      }
    }
  }

  async testDocumentAnalysis() {
    console.log('\n📄 测试文档分析功能...');
    
    try {
      // 模拟文档分析请求
      const analysisData = {
        documentId: 'test_doc_123',
        difficulty: 2
      };
      
      const response = await axios.post(`${this.petBackendURL}/api/rag/analyze-document`, analysisData, {
        timeout: 30000,
        headers: { 'Content-Type': 'application/json' }
      });
      
      const success = response.data.success;
      this.addTestResult('文档分析功能', success, success ? '分析完成' : '分析失败');
      
    } catch (error) {
      this.addTestResult('文档分析功能', false, error.message);
    }
  }

  async testLearningRecommendations() {
    console.log('\n🎯 测试学习建议功能...');
    
    try {
      const userProfile = {
        level: '中级',
        goal: '提高词汇量',
        wordsLearned: 150,
        studyDays: 30,
        accuracy: 85,
        weakAreas: ['语法', '听力']
      };
      
      const response = await axios.post(`${this.petBackendURL}/api/rag/recommendations`, {
        userProfile
      }, { timeout: 30000 });
      
      const success = response.data.success && response.data.data.answer;
      this.addTestResult('学习建议生成', success, success ? '建议已生成' : '生成失败');
      
    } catch (error) {
      this.addTestResult('学习建议功能', false, error.message);
    }
  }

  async testProgressAnalysis() {
    console.log('\n📊 测试进度分析功能...');
    
    try {
      const progressData = {
        totalDays: 30,
        wordsLearned: 150,
        wordsReviewed: 300,
        averageAccuracy: 85,
        totalTime: 1200,
        streakDays: 15
      };
      
      const response = await axios.post(`${this.petBackendURL}/api/rag/progress-analysis`, {
        progressData
      }, { timeout: 30000 });
      
      const success = response.data.success && response.data.data.answer;
      this.addTestResult('进度分析功能', success, success ? '分析完成' : '分析失败');
      
    } catch (error) {
      this.addTestResult('进度分析功能', false, error.message);
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
    console.log('\n📊 RAG集成测试结果汇总');
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
      
      console.log('\n💡 故障排除建议:');
      console.log('1. 确保RAG系统正在运行 (http://localhost:51658)');
      console.log('2. 确保桌宠后端正在运行 (http://localhost:3001)');
      console.log('3. 检查网络连接和防火墙设置');
      console.log('4. 查看系统日志获取详细错误信息');
    } else {
      console.log('\n🎉 所有测试通过！RAG集成功能正常工作');
      console.log('\n🚀 可以使用的功能:');
      console.log('• 智能问答: 向长离提问学习相关问题');
      console.log('• 文档分析: 上传文档提取重点单词');
      console.log('• 学习建议: 获得个性化学习建议');
      console.log('• 进度分析: 分析学习进度和表现');
    }
    
    // 保存测试报告
    this.saveTestReport();
  }

  saveTestReport() {
    const report = {
      timestamp: new Date().toISOString(),
      testType: 'RAG Integration Test',
      summary: {
        total: this.testResults.length,
        passed: this.testResults.filter(r => r.passed).length,
        failed: this.testResults.filter(r => !r.passed).length
      },
      results: this.testResults,
      environment: {
        ragURL: this.ragURL,
        petBackendURL: this.petBackendURL,
        nodeVersion: process.version,
        platform: process.platform
      }
    };
    
    const fs = require('fs');
    const reportPath = path.join(__dirname, 'rag-integration-test-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\n📄 测试报告已保存: ${reportPath}`);
  }

  // 交互式测试模式
  async interactiveTest() {
    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    console.log('\n🎮 进入交互式测试模式');
    console.log('你可以直接向长离提问，测试RAG功能');
    console.log('输入 "exit" 退出测试模式\n');

    while (true) {
      const question = await new Promise(resolve => {
        rl.question('🤔 请输入问题: ', resolve);
      });

      if (question.toLowerCase() === 'exit') {
        break;
      }

      try {
        console.log('🤖 长离正在思考...');
        const response = await axios.post(`${this.petBackendURL}/api/rag/ask`, {
          question,
          context: { type: 'interactive_test' }
        }, { timeout: 30000 });

        if (response.data.success && response.data.data.answer) {
          console.log(`\n🐱 长离: ${response.data.data.answer}\n`);
          
          if (response.data.data.sources && response.data.data.sources.length > 0) {
            console.log('📚 参考资料:');
            response.data.data.sources.forEach((source, index) => {
              console.log(`  ${index + 1}. ${source.title || source.filename || '未知来源'}`);
            });
            console.log('');
          }
        } else {
          console.log('❌ 长离暂时无法回答这个问题\n');
        }
      } catch (error) {
        console.log(`❌ 出现错误: ${error.message}\n`);
      }
    }

    rl.close();
    console.log('👋 退出交互式测试模式');
  }
}

// 主函数
async function main() {
  const tester = new RAGIntegrationTester();
  const args = process.argv.slice(2);

  if (args.includes('--interactive')) {
    await tester.interactiveTest();
  } else {
    await tester.runAllTests();
  }
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(error => {
    console.error('测试失败:', error);
    process.exit(1);
  });
}

module.exports = RAGIntegrationTester;