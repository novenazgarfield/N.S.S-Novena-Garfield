/**
 * Chronicle客户端SDK
 * 提供简化的API来与Chronicle服务交互
 */

const axios = require('axios');
const { EventEmitter } = require('events');

class ChronicleClient extends EventEmitter {
  constructor(options = {}) {
    super();
    
    this.config = {
      baseUrl: options.baseUrl || 'http://localhost:3000',
      apiKey: options.apiKey || process.env.CHRONICLE_API_KEY,
      timeout: options.timeout || 30000,
      retryAttempts: options.retryAttempts || 3,
      retryDelay: options.retryDelay || 1000,
      autoReconnect: options.autoReconnect !== false
    };

    this.isConnected = false;
    this.connectionAttempts = 0;
    this.maxConnectionAttempts = 10;
    
    // 请求拦截器
    this.setupAxiosInterceptors();
  }

  /**
   * 设置Axios拦截器
   */
  setupAxiosInterceptors() {
    // 请求拦截器
    axios.interceptors.request.use(
      (config) => {
        if (this.config.apiKey) {
          config.headers['X-API-Key'] = this.config.apiKey;
        }
        config.headers['User-Agent'] = 'Changlee-Chronicle-Client/1.0';
        return config;
      },
      (error) => Promise.reject(error)
    );

    // 响应拦截器
    axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
          this.handleConnectionError(error);
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * 连接到Chronicle服务
   */
  async connect() {
    try {
      const health = await this.checkHealth();
      if (health.status === 'healthy') {
        this.isConnected = true;
        this.connectionAttempts = 0;
        this.emit('connected', health);
        console.log('✅ Chronicle客户端连接成功');
        return true;
      }
      throw new Error('Chronicle服务状态异常');
    } catch (error) {
      this.isConnected = false;
      this.connectionAttempts++;
      this.emit('connectionError', error);
      
      if (this.config.autoReconnect && this.connectionAttempts < this.maxConnectionAttempts) {
        console.warn(`Chronicle连接失败，${this.config.retryDelay}ms后重试... (${this.connectionAttempts}/${this.maxConnectionAttempts})`);
        setTimeout(() => this.connect(), this.config.retryDelay * this.connectionAttempts);
      }
      
      throw error;
    }
  }

  /**
   * 检查服务健康状态
   */
  async checkHealth() {
    const response = await this.request('GET', '/health');
    return response.data;
  }

  /**
   * 获取服务信息
   */
  async getInfo() {
    const response = await this.request('GET', '/info');
    return response.data;
  }

  /**
   * 启动新的记录会话
   */
  async startSession(sessionConfig) {
    const response = await this.request('POST', '/sessions/start', sessionConfig);
    
    if (response.data.success) {
      this.emit('sessionStarted', response.data);
      return response.data;
    }
    
    throw new Error(response.data.error || '启动会话失败');
  }

  /**
   * 停止记录会话
   */
  async stopSession(sessionId, metadata = {}) {
    const response = await this.request('POST', `/sessions/${sessionId}/stop`, metadata);
    
    if (response.data.success) {
      this.emit('sessionStopped', { sessionId, ...response.data });
      return response.data;
    }
    
    throw new Error(response.data.error || '停止会话失败');
  }

  /**
   * 获取会话信息
   */
  async getSession(sessionId) {
    const response = await this.request('GET', `/sessions/${sessionId}`);
    return response.data;
  }

  /**
   * 获取所有会话列表
   */
  async getSessions(options = {}) {
    const response = await this.request('GET', '/sessions', options);
    return response.data;
  }

  /**
   * 获取会话事件
   */
  async getSessionEvents(sessionId, options = {}) {
    const response = await this.request('GET', `/sessions/${sessionId}/events`, options);
    return response.data;
  }

  /**
   * 获取会话统计
   */
  async getSessionStats(sessionId) {
    const response = await this.request('GET', `/sessions/${sessionId}/stats`);
    return response.data;
  }

  /**
   * 删除会话
   */
  async deleteSession(sessionId) {
    const response = await this.request('DELETE', `/sessions/${sessionId}`);
    return response.data;
  }

  /**
   * 生成会话报告
   */
  async generateReport(sessionId, options = {}) {
    const response = await this.request('GET', `/reports/${sessionId}`, options);
    return response.data;
  }

  /**
   * 获取原始会话数据
   */
  async getRawData(sessionId) {
    const response = await this.request('GET', `/reports/${sessionId}/raw`);
    return response.data;
  }

  /**
   * 执行深度分析
   */
  async performDeepAnalysis(sessionId, analysisConfig = {}) {
    const response = await this.request('POST', `/reports/${sessionId}/analyze`, analysisConfig);
    return response.data;
  }

  /**
   * 获取会话摘要
   */
  async getSessionSummary(sessionId) {
    const response = await this.request('GET', `/reports/${sessionId}/summary`);
    return response.data;
  }

  /**
   * 获取所有报告列表
   */
  async getReports(options = {}) {
    const response = await this.request('GET', '/reports', options);
    return response.data;
  }

  /**
   * 删除报告
   */
  async deleteReport(reportId) {
    const response = await this.request('DELETE', `/reports/${reportId}`);
    return response.data;
  }

  /**
   * 获取系统状态
   */
  async getSystemStatus() {
    const response = await this.request('GET', '/admin/status');
    return response.data;
  }

  /**
   * 获取配置信息
   */
  async getConfig() {
    const response = await this.request('GET', '/admin/config');
    return response.data;
  }

  /**
   * 执行数据库清理
   */
  async cleanupDatabase(days = 30) {
    const response = await this.request('POST', '/admin/cleanup', { days });
    return response.data;
  }

  /**
   * 重启服务
   */
  async restartService() {
    const response = await this.request('POST', '/admin/restart');
    return response.data;
  }

  /**
   * 通用请求方法
   */
  async request(method, endpoint, data = null) {
    if (!this.isConnected && endpoint !== '/health') {
      throw new Error('Chronicle客户端未连接');
    }

    const url = `${this.config.baseUrl}${endpoint}`;
    const config = {
      method,
      url,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json'
      }
    };

    if (data) {
      if (method === 'GET') {
        config.params = data;
      } else {
        config.data = data;
      }
    }

    let lastError;
    for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
      try {
        const response = await axios(config);
        return response;
      } catch (error) {
        lastError = error;
        
        if (attempt < this.config.retryAttempts) {
          await this.delay(this.config.retryDelay * attempt);
        }
      }
    }

    throw lastError;
  }

  /**
   * 处理连接错误
   */
  handleConnectionError(error) {
    if (this.isConnected) {
      this.isConnected = false;
      this.emit('disconnected', error);
      console.warn('❌ Chronicle连接断开');
      
      if (this.config.autoReconnect) {
        setTimeout(() => this.connect(), this.config.retryDelay);
      }
    }
  }

  /**
   * 延迟工具方法
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 断开连接
   */
  disconnect() {
    this.isConnected = false;
    this.removeAllListeners();
    console.log('📡 Chronicle客户端已断开连接');
  }

  /**
   * 获取连接状态
   */
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      connectionAttempts: this.connectionAttempts,
      config: {
        baseUrl: this.config.baseUrl,
        hasApiKey: !!this.config.apiKey,
        timeout: this.config.timeout,
        autoReconnect: this.config.autoReconnect
      }
    };
  }
}

/**
 * Chronicle客户端工厂函数
 */
function createChronicleClient(options = {}) {
  return new ChronicleClient(options);
}

/**
 * 学习会话管理器
 * 专门用于管理Changlee的学习会话
 */
class LearningSessionManager {
  constructor(chronicleClient) {
    this.client = chronicleClient;
    this.activeSessions = new Map();
  }

  /**
   * 开始学习会话
   */
  async startLearningSession(sessionData) {
    const sessionConfig = {
      project_name: `changlee_${sessionData.type}_${Date.now()}`,
      project_path: sessionData.projectPath || process.cwd(),
      metadata: {
        changlee_session_id: sessionData.id,
        user_id: sessionData.userId,
        learning_type: sessionData.type,
        subject: sessionData.subject,
        difficulty: sessionData.difficulty,
        start_time: new Date().toISOString(),
        ...sessionData.metadata
      },
      monitoring: {
        file_monitoring: sessionData.monitorFiles !== false,
        window_monitoring: sessionData.monitorWindows !== false,
        command_monitoring: sessionData.monitorCommands !== false
      }
    };

    const result = await this.client.startSession(sessionConfig);
    
    if (result.success) {
      this.activeSessions.set(sessionData.id, {
        chronicleSessionId: result.session_id,
        startTime: new Date(),
        type: sessionData.type,
        metadata: sessionConfig.metadata
      });
    }

    return result;
  }

  /**
   * 结束学习会话
   */
  async endLearningSession(sessionId, summary = {}) {
    const sessionInfo = this.activeSessions.get(sessionId);
    
    if (!sessionInfo) {
      throw new Error(`学习会话 ${sessionId} 不存在`);
    }

    const endMetadata = {
      end_time: new Date().toISOString(),
      duration: Date.now() - sessionInfo.startTime.getTime(),
      learning_summary: summary,
      performance_metrics: summary.metrics || {},
      outcomes: summary.outcomes || []
    };

    const result = await this.client.stopSession(sessionInfo.chronicleSessionId, endMetadata);
    
    if (result.success) {
      this.activeSessions.delete(sessionId);
    }

    return result;
  }

  /**
   * 获取学习报告
   */
  async getLearningReport(sessionId, includeRawData = false) {
    const sessionInfo = this.activeSessions.get(sessionId);
    
    if (!sessionInfo) {
      throw new Error(`学习会话 ${sessionId} 不存在`);
    }

    const report = await this.client.generateReport(sessionInfo.chronicleSessionId);
    
    if (includeRawData) {
      const rawData = await this.client.getRawData(sessionInfo.chronicleSessionId);
      report.raw_data = rawData;
    }

    return report;
  }

  /**
   * 获取活动会话列表
   */
  getActiveSessions() {
    return Array.from(this.activeSessions.entries()).map(([id, info]) => ({
      changlee_session_id: id,
      chronicle_session_id: info.chronicleSessionId,
      type: info.type,
      start_time: info.startTime,
      duration: Date.now() - info.startTime.getTime()
    }));
  }
}

module.exports = {
  ChronicleClient,
  createChronicleClient,
  LearningSessionManager
};