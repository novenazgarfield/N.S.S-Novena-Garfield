#!/usr/bin/env node

/**
 * Chronicle-Changlee集成演示脚本
 * 展示集成功能的基本使用方法
 */

const axios = require('axios');
const readline = require('readline');

class IntegrationDemo {
  constructor() {
    this.changleeUrl = 'http://localhost:3001';
    this.currentSessionId = null;
    
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  /**
   * 运行演示
   */
  async run() {
    console.log('🎓 Chronicle-Changlee集成演示\n');
    
    try {
      // 检查服务状态
      await this.checkServices();
      
      // 显示菜单
      await this.showMenu();
      
    } catch (error) {
      console.error('❌ 演示运行失败:', error.message);
      process.exit(1);
    }
  }

  /**
   * 检查服务状态
   */
  async checkServices() {
    console.log('🔍 检查服务状态...');
    
    try {
      // 检查Changlee服务
      const changleeHealth = await axios.get(`${this.changleeUrl}/health`);
      console.log('✅ Changlee服务正常');
      
      // 检查Chronicle集成状态
      const chronicleStatus = await axios.get(`${this.changleeUrl}/api/chronicle/status`);
      if (chronicleStatus.data.success) {
        const status = chronicleStatus.data.data;
        console.log(`✅ Chronicle集成状态: ${status.integration_status}`);
        console.log(`📊 Chronicle连接: ${status.client.isConnected ? '已连接' : '未连接'}`);
      } else {
        console.log('⚠️ Chronicle集成状态异常');
      }
      
    } catch (error) {
      throw new Error(`服务检查失败: ${error.message}`);
    }
    
    console.log('');
  }

  /**
   * 显示主菜单
   */
  async showMenu() {
    while (true) {
      console.log('📋 请选择演示功能:');
      console.log('1. 开始单词学习会话');
      console.log('2. 开始拼写练习会话');
      console.log('3. 开始阅读会话');
      console.log('4. 查看活动会话');
      console.log('5. 停止当前会话');
      console.log('6. 获取学习报告');
      console.log('7. 查看系统统计');
      console.log('8. 运行完整演示');
      console.log('0. 退出');
      console.log('');

      const choice = await this.prompt('请输入选择 (0-8): ');
      
      try {
        switch (choice) {
          case '1':
            await this.startLearningSession('word_learning', '单词学习');
            break;
          case '2':
            await this.startLearningSession('spelling_practice', '拼写练习');
            break;
          case '3':
            await this.startLearningSession('reading_session', '阅读会话');
            break;
          case '4':
            await this.showActiveSessions();
            break;
          case '5':
            await this.stopCurrentSession();
            break;
          case '6':
            await this.showLearningReport();
            break;
          case '7':
            await this.showSystemStats();
            break;
          case '8':
            await this.runFullDemo();
            break;
          case '0':
            console.log('👋 演示结束');
            this.rl.close();
            return;
          default:
            console.log('❌ 无效选择，请重试\n');
        }
      } catch (error) {
        console.error('❌ 操作失败:', error.message);
      }
      
      console.log('');
    }
  }

  /**
   * 开始学习会话
   */
  async startLearningSession(type, typeName) {
    if (this.currentSessionId) {
      console.log('⚠️ 已有活动会话，请先停止当前会话');
      return;
    }

    console.log(`🚀 启动${typeName}会话...`);
    
    const sessionData = {
      sessionId: `demo_${type}_${Date.now()}`,
      userId: 'demo_user',
      learningType: type,
      subject: `演示${typeName}`,
      difficulty: 'intermediate',
      monitorFiles: true,
      monitorWindows: true,
      monitorCommands: false,
      metadata: {
        demo_mode: true,
        start_time: new Date().toISOString()
      }
    };

    const response = await axios.post(`${this.changleeUrl}/api/chronicle/sessions/start`, sessionData);
    
    if (response.data.success) {
      this.currentSessionId = sessionData.sessionId;
      console.log(`✅ ${typeName}会话已启动`);
      console.log(`📝 会话ID: ${this.currentSessionId}`);
      console.log(`📊 Chronicle会话ID: ${response.data.data.session_id}`);
      
      // 模拟学习活动
      console.log('💡 提示: 现在您可以进行学习活动，Chronicle正在记录您的行为');
      console.log('   - 打开学习材料文件');
      console.log('   - 切换应用程序窗口');
      console.log('   - 进行学习练习');
    } else {
      console.log(`❌ 启动${typeName}会话失败:`, response.data.error);
    }
  }

  /**
   * 显示活动会话
   */
  async showActiveSessions() {
    console.log('📊 获取活动会话...');
    
    const response = await axios.get(`${this.changleeUrl}/api/chronicle/sessions/active`);
    
    if (response.data.success) {
      const sessions = response.data.data;
      
      if (sessions.length === 0) {
        console.log('📭 暂无活动会话');
      } else {
        console.log(`📋 活动会话列表 (${sessions.length}个):`);
        sessions.forEach((session, index) => {
          const duration = this.formatDuration(session.duration);
          console.log(`   ${index + 1}. ${session.type} - ${duration}`);
          console.log(`      会话ID: ${session.changlee_session_id}`);
          console.log(`      Chronicle ID: ${session.chronicle_session_id}`);
        });
      }
    } else {
      console.log('❌ 获取活动会话失败:', response.data.error);
    }
  }

  /**
   * 停止当前会话
   */
  async stopCurrentSession() {
    if (!this.currentSessionId) {
      console.log('⚠️ 没有活动的会话');
      return;
    }

    console.log('⏹️ 停止当前会话...');
    
    const summary = {
      outcomes: ['完成演示学习', '验证集成功能'],
      metrics: {
        demo_duration: Date.now() - new Date().getTime(),
        success_rate: 1.0,
        demo_completed: true
      },
      notes: '演示会话完成'
    };

    const response = await axios.post(
      `${this.changleeUrl}/api/chronicle/sessions/${this.currentSessionId}/stop`,
      { summary }
    );
    
    if (response.data.success) {
      console.log(`✅ 会话已停止: ${this.currentSessionId}`);
      console.log('📊 正在生成学习报告...');
      this.currentSessionId = null;
    } else {
      console.log('❌ 停止会话失败:', response.data.error);
    }
  }

  /**
   * 显示学习报告
   */
  async showLearningReport() {
    if (this.currentSessionId) {
      console.log('⚠️ 请先停止当前会话再查看报告');
      return;
    }

    // 获取最近的会话
    const sessionsResponse = await axios.get(`${this.changleeUrl}/api/chronicle/sessions/active`);
    
    if (!sessionsResponse.data.success || sessionsResponse.data.data.length === 0) {
      console.log('📭 没有可用的会话报告');
      return;
    }

    const sessionId = await this.prompt('请输入会话ID (或按回车使用最近的会话): ');
    const targetSessionId = sessionId.trim() || 'recent';

    console.log('📈 获取学习报告...');
    
    try {
      // 这里应该使用实际的会话ID，为了演示简化处理
      console.log('📊 学习报告示例:');
      console.log('   会话类型: 单词学习');
      console.log('   学习时长: 15分钟');
      console.log('   专注度: 85%');
      console.log('   学习效率: 良好');
      console.log('   建议: 可以尝试减少窗口切换以提高专注度');
      
    } catch (error) {
      if (error.response?.status === 404) {
        console.log('⏳ 报告正在生成中，请稍后再试');
      } else {
        console.log('❌ 获取报告失败:', error.message);
      }
    }
  }

  /**
   * 显示系统统计
   */
  async showSystemStats() {
    console.log('📊 获取系统统计信息...');
    
    const response = await axios.get(`${this.changleeUrl}/api/chronicle/stats`);
    
    if (response.data.success) {
      const stats = response.data.data;
      console.log('📈 系统统计:');
      console.log(`   Chronicle系统状态: ${stats.chronicle_stats?.system?.status || '未知'}`);
      console.log(`   活动会话数: ${stats.active_changlee_sessions || 0}`);
      console.log(`   总会话数: ${stats.chronicle_stats?.database?.totalSessions || 0}`);
      console.log(`   系统运行时间: ${this.formatUptime(stats.chronicle_stats?.system?.uptime || 0)}`);
    } else {
      console.log('❌ 获取统计信息失败:', response.data.error);
    }
  }

  /**
   * 运行完整演示
   */
  async runFullDemo() {
    console.log('🎬 开始完整演示...\n');
    
    try {
      // 1. 启动学习会话
      console.log('步骤 1: 启动单词学习会话');
      await this.startLearningSession('word_learning', '单词学习');
      await this.sleep(2000);
      
      // 2. 模拟学习活动
      console.log('\n步骤 2: 模拟学习活动 (5秒)');
      for (let i = 5; i > 0; i--) {
        process.stdout.write(`\r⏳ 模拟学习中... ${i}秒`);
        await this.sleep(1000);
      }
      console.log('\n✅ 学习活动完成');
      
      // 3. 查看活动会话
      console.log('\n步骤 3: 查看活动会话');
      await this.showActiveSessions();
      await this.sleep(1000);
      
      // 4. 停止会话
      console.log('\n步骤 4: 停止学习会话');
      await this.stopCurrentSession();
      await this.sleep(2000);
      
      // 5. 显示统计信息
      console.log('\n步骤 5: 显示系统统计');
      await this.showSystemStats();
      
      console.log('\n🎉 完整演示完成！');
      
    } catch (error) {
      console.error('\n❌ 演示过程中发生错误:', error.message);
    }
  }

  /**
   * 格式化持续时间
   */
  formatDuration(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}小时${minutes % 60}分钟`;
    } else if (minutes > 0) {
      return `${minutes}分钟${seconds % 60}秒`;
    } else {
      return `${seconds}秒`;
    }
  }

  /**
   * 格式化运行时间
   */
  formatUptime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}小时${minutes}分钟`;
    } else {
      return `${minutes}分钟`;
    }
  }

  /**
   * 提示用户输入
   */
  prompt(question) {
    return new Promise((resolve) => {
      this.rl.question(question, resolve);
    });
  }

  /**
   * 睡眠函数
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * 主函数
 */
async function main() {
  const demo = new IntegrationDemo();
  
  try {
    await demo.run();
  } catch (error) {
    console.error('❌ 演示失败:', error.message);
    process.exit(1);
  }
}

// 运行演示
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = IntegrationDemo;