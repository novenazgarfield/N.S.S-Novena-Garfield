/**
 * Chronicle集成服务
 * 将Chronicle的实验记录功能集成到Changlee学习系统中
 */

const axios = require('axios');
const path = require('path');
const { EventEmitter } = require('events');

class ChronicleService extends EventEmitter {
  constructor(config = {}) {
    super();
    
    // Chronicle服务配置
    this.chronicleConfig = {
      baseUrl: config.chronicleUrl || 'http://localhost:3000',
      apiKey: config.apiKey || process.env.CHRONICLE_API_KEY,
      timeout: config.timeout || 30000,
      retryAttempts: config.retryAttempts || 3,
      retryDelay: config.retryDelay || 1000
    };

    // 当前活动会话
    this.activeSessions = new Map();
    
    // 学习活动类型映射
    this.activityTypes = {
      WORD_LEARNING: 'word_learning',
      SPELLING_PRACTICE: 'spelling_practice',
      READING_SESSION: 'reading_session',
      AI_CONVERSATION: 'ai_conversation',
      MUSIC_LEARNING: 'music_learning',
      RAG_INTERACTION: 'rag_interaction'
    };

    // 初始化状态
    this.isConnected = false;
    this.lastHealthCheck = null;
    
    console.log('📊 Chronicle集成服务已初始化');
  }

  /**
   * 初始化Chronicle连接
   */
  async initialize() {
    try {
      await this.checkChronicleHealth();
      this.isConnected = true;
      console.log('✅ Chronicle服务连接成功');
      
      // 启动定期健康检查
      this.startHealthCheck();
      
      return true;
    } catch (error) {
      console.warn('⚠️ Chronicle服务连接失败，将在后台重试:', error.message);
      this.isConnected = false;
      
      // 启动重连机制
      this.startReconnection();
      
      return false;
    }
  }

  /**
   * 检查Chronicle服务健康状态
   */
  async checkChronicleHealth() {
    try {
      const response = await this.makeRequest('GET', '/health');
      this.lastHealthCheck = new Date();
      
      if (response.status === 'healthy') {
        if (!this.isConnected) {
          this.isConnected = true;
          this.emit('connected');
          console.log('🔄 Chronicle服务重新连接成功');
        }
        return true;
      }
      
      throw new Error('Chronicle服务状态异常');
    } catch (error) {
      if (this.isConnected) {
        this.isConnected = false;
        this.emit('disconnected');
        console.warn('❌ Chronicle服务连接断开');
      }
      throw error;
    }
  }

  /**
   * 启动学习会话记录
   */
  async startLearningSession(sessionData) {
    if (!this.isConnected) {
      console.warn('Chronicle服务未连接，跳过会话记录');
      return null;
    }

    try {
      const sessionConfig = {
        project_name: `changlee_learning_${sessionData.activityType}`,
        project_path: sessionData.projectPath || process.cwd(),
        metadata: {
          user_id: sessionData.userId,
          activity_type: sessionData.activityType,
          learning_context: sessionData.context,
          start_time: new Date().toISOString(),
          changlee_session_id: sessionData.sessionId,
          ...sessionData.metadata
        },
        monitoring: {
          file_monitoring: sessionData.monitorFiles !== false,
          window_monitoring: sessionData.monitorWindows !== false,
          command_monitoring: sessionData.monitorCommands !== false
        }
      };

      const response = await this.makeRequest('POST', '/sessions/start', sessionConfig);
      
      if (response.success) {
        const chronicleSessionId = response.session_id;
        
        // 存储会话映射
        this.activeSessions.set(sessionData.sessionId, {
          chronicleSessionId,
          activityType: sessionData.activityType,
          startTime: new Date(),
          metadata: sessionConfig.metadata
        });

        console.log(`📝 学习会话记录已启动: ${chronicleSessionId}`);
        this.emit('sessionStarted', { 
          changlee_session: sessionData.sessionId,
          chronicle_session: chronicleSessionId 
        });

        return chronicleSessionId;
      }

      throw new Error(response.error || '启动会话失败');
    } catch (error) {
      console.error('启动Chronicle学习会话失败:', error);
      return null;
    }
  }

  /**
   * 停止学习会话记录
   */
  async stopLearningSession(changleeSessionId, sessionSummary = {}) {
    const sessionInfo = this.activeSessions.get(changleeSessionId);
    
    if (!sessionInfo || !this.isConnected) {
      console.warn('未找到活动会话或Chronicle服务未连接');
      return null;
    }

    try {
      const stopData = {
        end_metadata: {
          end_time: new Date().toISOString(),
          duration: Date.now() - sessionInfo.startTime.getTime(),
          session_summary: sessionSummary,
          learning_outcomes: sessionSummary.outcomes || [],
          performance_metrics: sessionSummary.metrics || {}
        }
      };

      const response = await this.makeRequest(
        'POST', 
        `/sessions/${sessionInfo.chronicleSessionId}/stop`,
        stopData
      );

      if (response.success) {
        this.activeSessions.delete(changleeSessionId);
        
        console.log(`✅ 学习会话记录已停止: ${sessionInfo.chronicleSessionId}`);
        this.emit('sessionStopped', {
          changlee_session: changleeSessionId,
          chronicle_session: sessionInfo.chronicleSessionId
        });

        return sessionInfo.chronicleSessionId;
      }

      throw new Error(response.error || '停止会话失败');
    } catch (error) {
      console.error('停止Chronicle学习会话失败:', error);
      return null;
    }
  }

  /**
   * 获取学习会话报告
   */
  async getLearningReport(changleeSessionId, reportType = 'summary') {
    const sessionInfo = this.activeSessions.get(changleeSessionId);
    
    if (!sessionInfo && !this.isConnected) {
      throw new Error('会话不存在或Chronicle服务未连接');
    }

    try {
      const endpoint = reportType === 'raw' 
        ? `/reports/${sessionInfo.chronicleSessionId}/raw`
        : `/reports/${sessionInfo.chronicleSessionId}`;

      const response = await this.makeRequest('GET', endpoint);

      if (response.success || response.report) {
        const report = response.report || response.data;
        
        // 增强报告数据，添加Changlee特定的学习分析
        const enhancedReport = await this.enhanceLearningReport(report, sessionInfo);
        
        return enhancedReport;
      }

      throw new Error(response.error || '获取报告失败');
    } catch (error) {
      console.error('获取Chronicle学习报告失败:', error);
      throw error;
    }
  }

  /**
   * 增强学习报告，添加Changlee特定分析
   */
  async enhanceLearningReport(chronicleReport, sessionInfo) {
    try {
      const enhancedReport = {
        ...chronicleReport,
        changlee_analysis: {
          activity_type: sessionInfo.activityType,
          session_duration: Date.now() - sessionInfo.startTime.getTime(),
          learning_insights: await this.generateLearningInsights(chronicleReport, sessionInfo),
          recommendations: await this.generateLearningRecommendations(chronicleReport, sessionInfo),
          progress_indicators: this.extractProgressIndicators(chronicleReport),
          attention_patterns: this.analyzeAttentionPatterns(chronicleReport)
        }
      };

      return enhancedReport;
    } catch (error) {
      console.error('增强学习报告失败:', error);
      return chronicleReport; // 返回原始报告
    }
  }

  /**
   * 生成学习洞察
   */
  async generateLearningInsights(chronicleReport, sessionInfo) {
    const insights = [];

    // 分析文件操作模式
    if (chronicleReport.file_events && chronicleReport.file_events.length > 0) {
      const filePatterns = this.analyzeFilePatterns(chronicleReport.file_events);
      insights.push({
        type: 'file_interaction',
        insight: '学习过程中的文件操作模式分析',
        details: filePatterns
      });
    }

    // 分析窗口切换模式
    if (chronicleReport.window_events && chronicleReport.window_events.length > 0) {
      const focusPatterns = this.analyzeFocusPatterns(chronicleReport.window_events);
      insights.push({
        type: 'attention_focus',
        insight: '注意力集中度和切换模式分析',
        details: focusPatterns
      });
    }

    // 分析命令行活动
    if (chronicleReport.command_events && chronicleReport.command_events.length > 0) {
      const commandPatterns = this.analyzeCommandPatterns(chronicleReport.command_events);
      insights.push({
        type: 'interaction_patterns',
        insight: '学习交互模式分析',
        details: commandPatterns
      });
    }

    return insights;
  }

  /**
   * 生成学习建议
   */
  async generateLearningRecommendations(chronicleReport, sessionInfo) {
    const recommendations = [];

    // 基于活动类型的建议
    switch (sessionInfo.activityType) {
      case this.activityTypes.WORD_LEARNING:
        recommendations.push(...this.getWordLearningRecommendations(chronicleReport));
        break;
      case this.activityTypes.SPELLING_PRACTICE:
        recommendations.push(...this.getSpellingRecommendations(chronicleReport));
        break;
      case this.activityTypes.READING_SESSION:
        recommendations.push(...this.getReadingRecommendations(chronicleReport));
        break;
      default:
        recommendations.push(...this.getGeneralLearningRecommendations(chronicleReport));
    }

    return recommendations;
  }

  /**
   * 获取所有活动会话的统计信息
   */
  async getAllSessionsStats() {
    if (!this.isConnected) {
      return { error: 'Chronicle服务未连接' };
    }

    try {
      const response = await this.makeRequest('GET', '/admin/status');
      
      return {
        chronicle_stats: response,
        active_changlee_sessions: this.activeSessions.size,
        session_details: Array.from(this.activeSessions.entries()).map(([id, info]) => ({
          changlee_session_id: id,
          chronicle_session_id: info.chronicleSessionId,
          activity_type: info.activityType,
          duration: Date.now() - info.startTime.getTime()
        }))
      };
    } catch (error) {
      console.error('获取Chronicle统计信息失败:', error);
      return { error: error.message };
    }
  }

  /**
   * 批量分析历史学习会话
   */
  async analyzeLearningHistory(options = {}) {
    if (!this.isConnected) {
      throw new Error('Chronicle服务未连接');
    }

    try {
      // 获取历史会话列表
      const sessionsResponse = await this.makeRequest('GET', '/sessions', {
        limit: options.limit || 50,
        filter: 'changlee_learning'
      });

      if (!sessionsResponse.success) {
        throw new Error('获取历史会话失败');
      }

      const sessions = sessionsResponse.sessions || [];
      const analysisResults = [];

      // 批量分析会话
      for (const session of sessions) {
        try {
          const report = await this.makeRequest('GET', `/reports/${session.id}`);
          if (report.success) {
            const analysis = await this.analyzeSingleSession(report.report, session);
            analysisResults.push(analysis);
          }
        } catch (error) {
          console.warn(`分析会话 ${session.id} 失败:`, error.message);
        }
      }

      return {
        total_sessions: sessions.length,
        analyzed_sessions: analysisResults.length,
        learning_trends: this.extractLearningTrends(analysisResults),
        performance_metrics: this.calculatePerformanceMetrics(analysisResults),
        recommendations: this.generateHistoricalRecommendations(analysisResults)
      };
    } catch (error) {
      console.error('分析学习历史失败:', error);
      throw error;
    }
  }

  /**
   * 发送HTTP请求到Chronicle服务
   */
  async makeRequest(method, endpoint, data = null) {
    const url = `${this.chronicleConfig.baseUrl}${endpoint}`;
    const config = {
      method,
      url,
      timeout: this.chronicleConfig.timeout,
      headers: {
        'Content-Type': 'application/json'
      }
    };

    // 添加API密钥认证
    if (this.chronicleConfig.apiKey) {
      config.headers['X-API-Key'] = this.chronicleConfig.apiKey;
    }

    // 添加请求数据
    if (data && (method === 'POST' || method === 'PUT')) {
      config.data = data;
    } else if (data && method === 'GET') {
      config.params = data;
    }

    // 重试机制
    let lastError;
    for (let attempt = 1; attempt <= this.chronicleConfig.retryAttempts; attempt++) {
      try {
        const response = await axios(config);
        return response.data;
      } catch (error) {
        lastError = error;
        
        if (attempt < this.chronicleConfig.retryAttempts) {
          console.warn(`Chronicle请求失败，第${attempt}次重试...`);
          await this.delay(this.chronicleConfig.retryDelay * attempt);
        }
      }
    }

    throw lastError;
  }

  /**
   * 启动定期健康检查
   */
  startHealthCheck() {
    setInterval(async () => {
      try {
        await this.checkChronicleHealth();
      } catch (error) {
        // 健康检查失败已在checkChronicleHealth中处理
      }
    }, 60000); // 每分钟检查一次
  }

  /**
   * 启动重连机制
   */
  startReconnection() {
    const reconnectInterval = setInterval(async () => {
      try {
        await this.checkChronicleHealth();
        if (this.isConnected) {
          clearInterval(reconnectInterval);
          console.log('🔄 Chronicle服务重连成功');
        }
      } catch (error) {
        // 继续重试
      }
    }, 30000); // 每30秒重试一次
  }

  /**
   * 工具方法：延迟
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 分析文件操作模式
   */
  analyzeFilePatterns(fileEvents) {
    // 实现文件操作模式分析逻辑
    return {
      total_operations: fileEvents.length,
      operation_types: this.groupBy(fileEvents, 'type'),
      most_active_files: this.getMostActiveFiles(fileEvents),
      time_distribution: this.getTimeDistribution(fileEvents)
    };
  }

  /**
   * 分析注意力集中模式
   */
  analyzeFocusPatterns(windowEvents) {
    // 实现注意力模式分析逻辑
    return {
      total_switches: windowEvents.length,
      focus_duration: this.calculateFocusDuration(windowEvents),
      distraction_events: this.identifyDistractions(windowEvents),
      productivity_score: this.calculateProductivityScore(windowEvents)
    };
  }

  /**
   * 分析命令行交互模式
   */
  analyzeCommandPatterns(commandEvents) {
    // 实现命令行模式分析逻辑
    return {
      total_commands: commandEvents.length,
      command_types: this.groupBy(commandEvents, 'command'),
      success_rate: this.calculateCommandSuccessRate(commandEvents),
      learning_indicators: this.extractLearningIndicators(commandEvents)
    };
  }

  /**
   * 工具方法：按字段分组
   */
  groupBy(array, key) {
    return array.reduce((groups, item) => {
      const group = item[key] || 'unknown';
      groups[group] = (groups[group] || 0) + 1;
      return groups;
    }, {});
  }

  /**
   * 获取服务状态
   */
  getServiceStatus() {
    return {
      service_name: 'Chronicle集成服务',
      is_connected: this.isConnected,
      last_health_check: this.lastHealthCheck,
      active_sessions: this.activeSessions.size,
      chronicle_config: {
        base_url: this.chronicleConfig.baseUrl,
        has_api_key: !!this.chronicleConfig.apiKey,
        timeout: this.chronicleConfig.timeout
      }
    };
  }

  /**
   * 清理资源
   */
  async cleanup() {
    console.log('🧹 清理Chronicle集成服务资源...');
    
    // 停止所有活动会话
    const stopPromises = Array.from(this.activeSessions.keys()).map(sessionId => 
      this.stopLearningSession(sessionId, { reason: 'service_cleanup' })
    );
    
    await Promise.allSettled(stopPromises);
    
    // 清理事件监听器
    this.removeAllListeners();
    
    console.log('✅ Chronicle集成服务资源清理完成');
  }
}

module.exports = ChronicleService;