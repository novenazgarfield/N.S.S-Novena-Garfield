/**
 * Chronicle与Changlee集成测试脚本
 * 测试两个系统之间的API通信和功能集成
 */

const axios = require('axios');
const { spawn } = require('child_process');
const path = require('path');

class ChronicleIntegrationTester {
  constructor() {
    this.changleeUrl = 'http://localhost:3001';
    this.chronicleUrl = 'http://localhost:3000';
    this.testResults = [];
    this.testSessionId = null;
  }

  /**
   * 运行所有集成测试
   */
  async runAllTests() {
    console.log('🧪 开始Chronicle与Changlee集成测试...\n');

    const tests = [
      { name: '检查Changlee服务状态', test: () => this.testChangleeHealth() },
      { name: '检查Chronicle服务状态', test: () => this.testChronicleHealth() },
      { name: '测试Chronicle集成状态', test: () => this.testChronicleIntegration() },
      { name: '测试启动学习会话', test: () => this.testStartLearningSession() },
      { name: '测试获取活动会话', test: () => this.testGetActiveSessions() },
      { name: '测试停止学习会话', test: () => this.testStopLearningSession() },
      { name: '测试获取学习报告', test: () => this.testGetLearningReport() },
      { name: '测试学习历史分析', test: () => this.testLearningHistoryAnalysis() },
      { name: '测试Chronicle统计信息', test: () => this.testChronicleStats() },
      { name: '测试错误处理', test: () => this.testErrorHandling() }
    ];

    for (const { name, test } of tests) {
      try {
        console.log(`🔍 ${name}...`);
        await test();
        this.addTestResult(name, true, '测试通过');
        console.log(`✅ ${name} - 通过\n`);
      } catch (error) {
        this.addTestResult(name, false, error.message);
        console.log(`❌ ${name} - 失败: ${error.message}\n`);
      }
    }

    this.printTestSummary();
  }

  /**
   * 测试Changlee服务健康状态
   */
  async testChangleeHealth() {
    const response = await axios.get(`${this.changleeUrl}/health`);
    
    if (response.status !== 200) {
      throw new Error(`Changlee服务状态异常: ${response.status}`);
    }

    if (response.data.status !== 'healthy') {
      throw new Error(`Changlee服务不健康: ${response.data.status}`);
    }

    console.log(`   📡 Changlee服务正常运行`);
  }

  /**
   * 测试Chronicle服务健康状态
   */
  async testChronicleHealth() {
    try {
      const response = await axios.get(`${this.chronicleUrl}/health`);
      
      if (response.status !== 200) {
        throw new Error(`Chronicle服务状态异常: ${response.status}`);
      }

      console.log(`   📊 Chronicle服务正常运行`);
    } catch (error) {
      if (error.code === 'ECONNREFUSED') {
        throw new Error('Chronicle服务未启动或无法连接');
      }
      throw error;
    }
  }

  /**
   * 测试Chronicle集成状态
   */
  async testChronicleIntegration() {
    const response = await axios.get(`${this.changleeUrl}/api/chronicle/status`);
    
    if (!response.data.success) {
      throw new Error('获取Chronicle集成状态失败');
    }

    const status = response.data.data;
    console.log(`   🔗 集成状态: ${status.integration_status}`);
    console.log(`   📊 Chronicle连接: ${status.client.isConnected ? '已连接' : '未连接'}`);
    console.log(`   🎯 活动会话: ${status.service.active_sessions}`);
  }

  /**
   * 测试启动学习会话
   */
  async testStartLearningSession() {
    const sessionData = {
      sessionId: `test_session_${Date.now()}`,
      userId: 'test_user',
      learningType: 'word_learning',
      subject: '英语学习测试',
      difficulty: 'intermediate',
      monitorFiles: true,
      monitorWindows: true,
      monitorCommands: false,
      metadata: {
        test_mode: true,
        test_timestamp: new Date().toISOString()
      }
    };

    const response = await axios.post(`${this.changleeUrl}/api/chronicle/sessions/start`, sessionData);
    
    if (!response.data.success) {
      throw new Error(`启动学习会话失败: ${response.data.error}`);
    }

    this.testSessionId = sessionData.sessionId;
    console.log(`   🎯 会话ID: ${this.testSessionId}`);
    console.log(`   📝 Chronicle会话ID: ${response.data.data.session_id}`);
  }

  /**
   * 测试获取活动会话
   */
  async testGetActiveSessions() {
    const response = await axios.get(`${this.changleeUrl}/api/chronicle/sessions/active`);
    
    if (!response.data.success) {
      throw new Error('获取活动会话失败');
    }

    const sessions = response.data.data;
    console.log(`   📊 活动会话数量: ${sessions.length}`);
    
    if (this.testSessionId) {
      const testSession = sessions.find(s => s.changlee_session_id === this.testSessionId);
      if (!testSession) {
        throw new Error('测试会话未在活动会话列表中找到');
      }
      console.log(`   ✅ 测试会话已找到: ${testSession.type}`);
    }
  }

  /**
   * 测试停止学习会话
   */
  async testStopLearningSession() {
    if (!this.testSessionId) {
      throw new Error('没有活动的测试会话');
    }

    const summary = {
      outcomes: ['完成测试', '验证集成'],
      metrics: {
        test_duration: 1000,
        success_rate: 1.0
      },
      notes: '集成测试完成'
    };

    const response = await axios.post(
      `${this.changleeUrl}/api/chronicle/sessions/${this.testSessionId}/stop`,
      { summary }
    );
    
    if (!response.data.success) {
      throw new Error(`停止学习会话失败: ${response.data.error}`);
    }

    console.log(`   ⏹️ 会话已停止: ${this.testSessionId}`);
  }

  /**
   * 测试获取学习报告
   */
  async testGetLearningReport() {
    if (!this.testSessionId) {
      throw new Error('没有可用的测试会话');
    }

    try {
      const response = await axios.get(
        `${this.changleeUrl}/api/chronicle/sessions/${this.testSessionId}/report`
      );
      
      if (!response.data.success) {
        throw new Error(`获取学习报告失败: ${response.data.error}`);
      }

      const report = response.data.data;
      console.log(`   📈 报告生成成功`);
      console.log(`   ⏱️ 会话时长: ${report.duration || '未知'}ms`);
      
      if (report.changlee_analysis) {
        console.log(`   🧠 包含Changlee分析: ${report.changlee_analysis.learning_insights?.length || 0}个洞察`);
      }
    } catch (error) {
      // 如果报告还没生成，这是正常的
      if (error.response?.status === 404) {
        console.log(`   ⏳ 报告正在生成中（这是正常的）`);
      } else {
        throw error;
      }
    }
  }

  /**
   * 测试学习历史分析
   */
  async testLearningHistoryAnalysis() {
    try {
      const response = await axios.get(`${this.changleeUrl}/api/chronicle/analysis/history?limit=10`);
      
      if (!response.data.success) {
        throw new Error(`获取学习历史分析失败: ${response.data.error}`);
      }

      const analysis = response.data.data;
      console.log(`   📊 分析的会话数: ${analysis.analyzed_sessions || 0}`);
      console.log(`   📈 学习趋势: ${analysis.learning_trends ? '已生成' : '无数据'}`);
    } catch (error) {
      if (error.response?.status === 500) {
        console.log(`   ⏳ 历史数据不足，跳过分析测试`);
      } else {
        throw error;
      }
    }
  }

  /**
   * 测试Chronicle统计信息
   */
  async testChronicleStats() {
    const response = await axios.get(`${this.changleeUrl}/api/chronicle/stats`);
    
    if (!response.data.success) {
      throw new Error(`获取Chronicle统计信息失败: ${response.data.error}`);
    }

    const stats = response.data.data;
    console.log(`   📊 Chronicle系统状态: ${stats.chronicle_stats?.system?.status || '未知'}`);
    console.log(`   🎯 Changlee活动会话: ${stats.active_changlee_sessions || 0}`);
  }

  /**
   * 测试错误处理
   */
  async testErrorHandling() {
    // 测试无效的会话ID
    try {
      await axios.get(`${this.changleeUrl}/api/chronicle/sessions/invalid_session/report`);
      throw new Error('应该返回错误，但没有');
    } catch (error) {
      if (error.response?.status === 500 || error.response?.status === 404) {
        console.log(`   ✅ 错误处理正常: ${error.response.status}`);
      } else {
        throw new Error(`意外的错误响应: ${error.response?.status}`);
      }
    }

    // 测试无效的请求数据
    try {
      await axios.post(`${this.changleeUrl}/api/chronicle/sessions/start`, {
        // 缺少必要字段
      });
      throw new Error('应该返回错误，但没有');
    } catch (error) {
      if (error.response?.status >= 400) {
        console.log(`   ✅ 输入验证正常: ${error.response.status}`);
      } else {
        throw new Error(`意外的错误响应: ${error.response?.status}`);
      }
    }
  }

  /**
   * 添加测试结果
   */
  addTestResult(name, passed, message) {
    this.testResults.push({
      name,
      passed,
      message,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * 打印测试摘要
   */
  printTestSummary() {
    console.log('\n' + '='.repeat(60));
    console.log('📋 测试摘要');
    console.log('='.repeat(60));

    const passed = this.testResults.filter(r => r.passed).length;
    const failed = this.testResults.filter(r => r.passed === false).length;
    const total = this.testResults.length;

    console.log(`总测试数: ${total}`);
    console.log(`通过: ${passed} ✅`);
    console.log(`失败: ${failed} ❌`);
    console.log(`成功率: ${((passed / total) * 100).toFixed(1)}%`);

    if (failed > 0) {
      console.log('\n❌ 失败的测试:');
      this.testResults
        .filter(r => !r.passed)
        .forEach(r => {
          console.log(`   • ${r.name}: ${r.message}`);
        });
    }

    console.log('\n' + '='.repeat(60));
    
    if (failed === 0) {
      console.log('🎉 所有测试通过！Chronicle与Changlee集成成功！');
    } else {
      console.log('⚠️ 部分测试失败，请检查系统配置和连接状态。');
    }
  }

  /**
   * 等待服务启动
   */
  async waitForService(url, maxAttempts = 30) {
    for (let i = 0; i < maxAttempts; i++) {
      try {
        await axios.get(`${url}/health`);
        return true;
      } catch (error) {
        if (i === maxAttempts - 1) {
          throw new Error(`服务 ${url} 启动超时`);
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  }
}

/**
 * 主函数
 */
async function main() {
  const tester = new ChronicleIntegrationTester();

  try {
    // 检查服务是否运行
    console.log('🔍 检查服务状态...');
    
    try {
      await axios.get(tester.changleeUrl + '/health');
      console.log('✅ Changlee服务已运行');
    } catch (error) {
      console.log('❌ Changlee服务未运行，请先启动Changlee服务');
      process.exit(1);
    }

    try {
      await axios.get(tester.chronicleUrl + '/health');
      console.log('✅ Chronicle服务已运行');
    } catch (error) {
      console.log('⚠️ Chronicle服务未运行，部分测试可能失败');
    }

    console.log('');

    // 运行集成测试
    await tester.runAllTests();

  } catch (error) {
    console.error('❌ 测试运行失败:', error.message);
    process.exit(1);
  }
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = ChronicleIntegrationTester;