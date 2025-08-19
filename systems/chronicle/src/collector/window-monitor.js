const activeWin = require('active-win');
const { createModuleLogger } = require('../shared/logger');
const { throttle, formatDuration } = require('../shared/utils');
const config = require('../shared/config');
const database = require('./database');

const logger = createModuleLogger('window-monitor');

class WindowMonitor {
  constructor() {
    this.sessions = new Map(); // sessionId -> monitoring info
    this.isEnabled = config.monitoring.window.enabled;
    this.pollInterval = config.monitoring.window.pollIntervalMs;
    this.trackInactive = config.monitoring.window.trackInactive;
    this.globalInterval = null;
    this.lastActiveWindow = null;
    this.windowStartTime = null;
  }

  /**
   * 启动窗口监控
   */
  async startMonitoring(sessionId, projectPath) {
    if (!this.isEnabled) {
      logger.warn('Window monitoring is disabled');
      return false;
    }

    try {
      // 检查是否支持窗口监控
      if (!this.isSupported()) {
        logger.warn('Window monitoring is not supported on this platform');
        return false;
      }

      // 如果已经在监控，先停止
      if (this.sessions.has(sessionId)) {
        await this.stopMonitoring(sessionId);
      }

      // 记录会话信息
      this.sessions.set(sessionId, {
        projectPath,
        startTime: Date.now(),
        lastWindowChange: Date.now(),
        windowHistory: [],
        isActive: true
      });

      // 启动全局监控（如果还没有启动）
      if (!this.globalInterval) {
        await this.startGlobalMonitoring();
      }

      logger.info('Window monitoring started', { sessionId, projectPath });
      return true;

    } catch (error) {
      logger.error('Failed to start window monitoring', { 
        sessionId, 
        projectPath, 
        error: error.message 
      });
      return false;
    }
  }

  /**
   * 停止窗口监控
   */
  async stopMonitoring(sessionId) {
    const sessionInfo = this.sessions.get(sessionId);
    if (!sessionInfo) {
      logger.warn('No window monitoring found for session', { sessionId });
      return false;
    }

    try {
      // 记录最后一个窗口的持续时间
      if (this.lastActiveWindow && this.windowStartTime) {
        await this.recordWindowDuration(sessionId);
      }

      // 移除会话
      this.sessions.delete(sessionId);

      // 如果没有活动会话，停止全局监控
      if (this.sessions.size === 0) {
        this.stopGlobalMonitoring();
      }

      const duration = Date.now() - sessionInfo.startTime;
      logger.info('Window monitoring stopped', { 
        sessionId, 
        duration: formatDuration(duration)
      });

      return true;

    } catch (error) {
      logger.error('Failed to stop window monitoring', { 
        sessionId, 
        error: error.message 
      });
      return false;
    }
  }

  /**
   * 启动全局窗口监控
   */
  async startGlobalMonitoring() {
    // 创建节流处理函数
    const throttledHandler = throttle(
      () => this.checkActiveWindow(),
      this.pollInterval
    );

    // 启动定时检查
    this.globalInterval = setInterval(throttledHandler, this.pollInterval);

    // 立即检查一次
    await this.checkActiveWindow();

    logger.info('Global window monitoring started', { 
      pollInterval: this.pollInterval 
    });
  }

  /**
   * 停止全局窗口监控
   */
  stopGlobalMonitoring() {
    if (this.globalInterval) {
      clearInterval(this.globalInterval);
      this.globalInterval = null;
      logger.info('Global window monitoring stopped');
    }
  }

  /**
   * 检查当前活动窗口
   */
  async checkActiveWindow() {
    try {
      const currentWindow = await activeWin();
      
      // 检查窗口是否发生变化
      if (this.hasWindowChanged(currentWindow)) {
        await this.handleWindowChange(currentWindow);
      }

    } catch (error) {
      logger.error('Failed to get active window', { error: error.message });
    }
  }

  /**
   * 检查窗口是否发生变化
   */
  hasWindowChanged(currentWindow) {
    if (!this.lastActiveWindow && !currentWindow) {
      return false;
    }

    if (!this.lastActiveWindow || !currentWindow) {
      return true;
    }

    return (
      this.lastActiveWindow.title !== currentWindow.title ||
      this.lastActiveWindow.owner?.name !== currentWindow.owner?.name ||
      this.lastActiveWindow.owner?.pid !== currentWindow.owner?.pid
    );
  }

  /**
   * 处理窗口变化
   */
  async handleWindowChange(currentWindow) {
    const now = Date.now();

    try {
      // 记录上一个窗口的持续时间
      if (this.lastActiveWindow && this.windowStartTime) {
        await this.recordWindowDuration();
      }

      // 更新当前窗口信息
      this.lastActiveWindow = currentWindow;
      this.windowStartTime = now;

      // 如果当前没有活动窗口且不跟踪非活动状态，则返回
      if (!currentWindow && !this.trackInactive) {
        return;
      }

      // 为所有活动会话记录窗口事件
      for (const [sessionId, sessionInfo] of this.sessions) {
        if (sessionInfo.isActive) {
          await this.recordWindowEvent(sessionId, currentWindow);
        }
      }

    } catch (error) {
      logger.error('Failed to handle window change', { error: error.message });
    }
  }

  /**
   * 记录窗口持续时间
   */
  async recordWindowDuration(specificSessionId = null) {
    if (!this.lastActiveWindow || !this.windowStartTime) {
      return;
    }

    const duration = Date.now() - this.windowStartTime;
    
    // 只记录持续时间超过1秒的窗口
    if (duration < 1000) {
      return;
    }

    const sessionsToUpdate = specificSessionId 
      ? [specificSessionId]
      : Array.from(this.sessions.keys());

    for (const sessionId of sessionsToUpdate) {
      try {
        await database.recordWindowEvent(
          sessionId,
          this.lastActiveWindow,
          duration,
          {
            startTime: this.windowStartTime,
            endTime: Date.now(),
            duration
          }
        );

        logger.debug('Window duration recorded', { 
          sessionId, 
          duration: formatDuration(duration),
          windowTitle: this.lastActiveWindow.title 
        });

      } catch (error) {
        logger.error('Failed to record window duration', { 
          sessionId, 
          error: error.message 
        });
      }
    }
  }

  /**
   * 记录窗口事件
   */
  async recordWindowEvent(sessionId, windowInfo, metadata = {}) {
    try {
      // 构建窗口信息
      const windowData = {
        title: windowInfo?.title || 'Unknown',
        owner: {
          name: windowInfo?.owner?.name || 'Unknown',
          path: windowInfo?.owner?.path || null,
          pid: windowInfo?.owner?.pid || null
        }
      };

      // 添加元数据
      const eventMetadata = {
        ...metadata,
        platform: process.platform,
        timestamp: Date.now()
      };

      // 记录到数据库
      const eventId = await database.recordWindowEvent(
        sessionId,
        windowData,
        null, // duration will be recorded later
        eventMetadata
      );

      // 更新会话历史
      const sessionInfo = this.sessions.get(sessionId);
      if (sessionInfo) {
        sessionInfo.lastWindowChange = Date.now();
        sessionInfo.windowHistory.push({
          eventId,
          windowTitle: windowData.title,
          appName: windowData.owner.name,
          timestamp: Date.now()
        });

        // 限制历史记录长度
        if (sessionInfo.windowHistory.length > 100) {
          sessionInfo.windowHistory = sessionInfo.windowHistory.slice(-50);
        }
      }

      logger.debug('Window event recorded', { 
        sessionId, 
        eventId, 
        windowTitle: windowData.title,
        appName: windowData.owner.name
      });

      // 触发事件回调
      this.emit('windowEvent', {
        sessionId,
        eventId,
        windowInfo: windowData,
        metadata: eventMetadata
      });

      return eventId;

    } catch (error) {
      logger.error('Failed to record window event', { 
        sessionId, 
        error: error.message 
      });
      return null;
    }
  }

  /**
   * 检查平台支持
   */
  isSupported() {
    const supportedPlatforms = ['win32', 'darwin', 'linux'];
    return supportedPlatforms.includes(process.platform);
  }

  /**
   * 获取监控状态
   */
  getMonitoringStatus(sessionId) {
    const sessionInfo = this.sessions.get(sessionId);
    if (!sessionInfo) {
      return null;
    }

    return {
      sessionId,
      projectPath: sessionInfo.projectPath,
      startTime: sessionInfo.startTime,
      duration: Date.now() - sessionInfo.startTime,
      lastWindowChange: sessionInfo.lastWindowChange,
      windowHistoryCount: sessionInfo.windowHistory.length,
      currentWindow: this.lastActiveWindow,
      isActive: sessionInfo.isActive
    };
  }

  /**
   * 获取所有活动监控
   */
  getAllMonitoringStatus() {
    const statuses = [];
    for (const sessionId of this.sessions.keys()) {
      const status = this.getMonitoringStatus(sessionId);
      if (status) {
        statuses.push(status);
      }
    }
    return statuses;
  }

  /**
   * 获取窗口历史
   */
  getWindowHistory(sessionId, limit = 10) {
    const sessionInfo = this.sessions.get(sessionId);
    if (!sessionInfo) {
      return [];
    }

    return sessionInfo.windowHistory
      .slice(-limit)
      .reverse();
  }

  /**
   * 停止所有监控
   */
  async stopAllMonitoring() {
    const sessionIds = Array.from(this.sessions.keys());
    const results = await Promise.allSettled(
      sessionIds.map(sessionId => this.stopMonitoring(sessionId))
    );

    const successful = results.filter(r => r.status === 'fulfilled' && r.value).length;
    logger.info('Stopped all window monitoring', { 
      total: sessionIds.length, 
      successful 
    });

    return successful;
  }

  /**
   * 事件发射器功能
   */
  emit(eventName, data) {
    if (this.listeners && this.listeners[eventName]) {
      this.listeners[eventName].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          logger.error('Event listener error', { 
            eventName, 
            error: error.message 
          });
        }
      });
    }
  }

  /**
   * 添加事件监听器
   */
  on(eventName, callback) {
    if (!this.listeners) {
      this.listeners = {};
    }
    if (!this.listeners[eventName]) {
      this.listeners[eventName] = [];
    }
    this.listeners[eventName].push(callback);
  }

  /**
   * 移除事件监听器
   */
  off(eventName, callback) {
    if (this.listeners && this.listeners[eventName]) {
      const index = this.listeners[eventName].indexOf(callback);
      if (index > -1) {
        this.listeners[eventName].splice(index, 1);
      }
    }
  }

  /**
   * 获取监控统计信息
   */
  async getMonitoringStats(sessionId) {
    try {
      const stats = await database.getSessionStats(sessionId);
      const sessionInfo = this.sessions.get(sessionId);
      
      return {
        windowEvents: stats.windowEvents,
        monitoringDuration: sessionInfo ? Date.now() - sessionInfo.startTime : 0,
        windowHistoryCount: sessionInfo ? sessionInfo.windowHistory.length : 0
      };
    } catch (error) {
      logger.error('Failed to get monitoring stats', { 
        sessionId, 
        error: error.message 
      });
      return null;
    }
  }
}

// 创建单例实例
const windowMonitor = new WindowMonitor();

module.exports = windowMonitor;