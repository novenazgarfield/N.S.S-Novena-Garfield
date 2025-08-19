const chokidar = require('chokidar');
const path = require('path');
const { createModuleLogger } = require('../shared/logger');
const { debounce, getFileExtension, getFileStats } = require('../shared/utils');
const config = require('../shared/config');
const database = require('./database');

const logger = createModuleLogger('file-monitor');

class FileMonitor {
  constructor() {
    this.watchers = new Map(); // sessionId -> watcher
    this.isEnabled = config.monitoring.fileSystem.enabled;
    this.debounceMs = config.monitoring.fileSystem.debounceMs;
    this.ignorePatterns = config.monitoring.fileSystem.ignorePatterns;
  }

  /**
   * 启动文件监控
   */
  async startMonitoring(sessionId, projectPath) {
    if (!this.isEnabled) {
      logger.warn('File system monitoring is disabled');
      return false;
    }

    try {
      // 检查路径是否存在
      const fs = require('fs');
      if (!fs.existsSync(projectPath)) {
        throw new Error(`Project path does not exist: ${projectPath}`);
      }

      // 如果已经在监控，先停止
      if (this.watchers.has(sessionId)) {
        await this.stopMonitoring(sessionId);
      }

      // 创建监控器配置
      const watcherOptions = {
        ignored: this.ignorePatterns,
        persistent: true,
        ignoreInitial: true,
        followSymlinks: false,
        depth: 10, // 限制监控深度
        awaitWriteFinish: {
          stabilityThreshold: 100,
          pollInterval: 50
        }
      };

      // 创建文件监控器
      const watcher = chokidar.watch(projectPath, watcherOptions);

      // 创建防抖处理函数
      const debouncedHandler = debounce(
        (eventType, filePath, stats) => this.handleFileEvent(sessionId, eventType, filePath, stats),
        this.debounceMs
      );

      // 监听文件事件
      watcher
        .on('add', (filePath, stats) => {
          debouncedHandler('add', filePath, stats);
        })
        .on('change', (filePath, stats) => {
          debouncedHandler('change', filePath, stats);
        })
        .on('unlink', (filePath) => {
          debouncedHandler('unlink', filePath, null);
        })
        .on('addDir', (dirPath, stats) => {
          debouncedHandler('addDir', dirPath, stats);
        })
        .on('unlinkDir', (dirPath) => {
          debouncedHandler('unlinkDir', dirPath, null);
        })
        .on('error', (error) => {
          logger.error('File watcher error', { 
            sessionId, 
            projectPath, 
            error: error.message 
          });
        })
        .on('ready', () => {
          logger.info('File monitoring started', { sessionId, projectPath });
        });

      // 存储监控器
      this.watchers.set(sessionId, {
        watcher,
        projectPath,
        startTime: Date.now()
      });

      return true;
    } catch (error) {
      logger.error('Failed to start file monitoring', { 
        sessionId, 
        projectPath, 
        error: error.message 
      });
      return false;
    }
  }

  /**
   * 停止文件监控
   */
  async stopMonitoring(sessionId) {
    const watcherInfo = this.watchers.get(sessionId);
    if (!watcherInfo) {
      logger.warn('No file watcher found for session', { sessionId });
      return false;
    }

    try {
      await watcherInfo.watcher.close();
      this.watchers.delete(sessionId);
      
      const duration = Date.now() - watcherInfo.startTime;
      logger.info('File monitoring stopped', { 
        sessionId, 
        projectPath: watcherInfo.projectPath,
        duration 
      });
      
      return true;
    } catch (error) {
      logger.error('Failed to stop file monitoring', { 
        sessionId, 
        error: error.message 
      });
      return false;
    }
  }

  /**
   * 处理文件事件
   */
  async handleFileEvent(sessionId, eventType, filePath, stats) {
    try {
      // 获取文件信息
      const fileInfo = {
        path: filePath,
        name: path.basename(filePath),
        extension: getFileExtension(filePath),
        size: stats ? stats.size : null,
        isDirectory: stats ? stats.isDirectory() : false
      };

      // 过滤不需要记录的文件
      if (this.shouldIgnoreFile(fileInfo)) {
        return;
      }

      // 获取额外的文件统计信息
      let additionalStats = null;
      if (eventType !== 'unlink' && eventType !== 'unlinkDir') {
        additionalStats = await getFileStats(filePath);
      }

      // 构建元数据
      const metadata = {
        fileInfo,
        stats: additionalStats,
        eventTime: Date.now()
      };

      // 记录到数据库
      const eventId = await database.recordFileEvent(
        sessionId, 
        eventType, 
        filePath, 
        metadata
      );

      logger.debug('File event recorded', { 
        sessionId, 
        eventId, 
        eventType, 
        filePath: fileInfo.name 
      });

      // 触发事件回调（如果有）
      this.emit('fileEvent', {
        sessionId,
        eventId,
        eventType,
        filePath,
        fileInfo,
        metadata
      });

    } catch (error) {
      logger.error('Failed to handle file event', { 
        sessionId, 
        eventType, 
        filePath, 
        error: error.message 
      });
    }
  }

  /**
   * 判断是否应该忽略文件
   */
  shouldIgnoreFile(fileInfo) {
    // 忽略临时文件
    if (fileInfo.name.startsWith('.') && fileInfo.name.endsWith('.tmp')) {
      return true;
    }

    // 忽略系统文件
    const systemFiles = ['.DS_Store', 'Thumbs.db', 'desktop.ini'];
    if (systemFiles.includes(fileInfo.name)) {
      return true;
    }

    // 忽略特定扩展名
    const ignoredExtensions = ['tmp', 'temp', 'cache', 'log'];
    if (ignoredExtensions.includes(fileInfo.extension)) {
      return true;
    }

    // 忽略过大的文件（超过100MB）
    if (fileInfo.size && fileInfo.size > 100 * 1024 * 1024) {
      return true;
    }

    return false;
  }

  /**
   * 获取监控状态
   */
  getMonitoringStatus(sessionId) {
    const watcherInfo = this.watchers.get(sessionId);
    if (!watcherInfo) {
      return null;
    }

    return {
      sessionId,
      projectPath: watcherInfo.projectPath,
      startTime: watcherInfo.startTime,
      duration: Date.now() - watcherInfo.startTime,
      isActive: true
    };
  }

  /**
   * 获取所有活动监控
   */
  getAllMonitoringStatus() {
    const statuses = [];
    for (const [sessionId, watcherInfo] of this.watchers) {
      statuses.push({
        sessionId,
        projectPath: watcherInfo.projectPath,
        startTime: watcherInfo.startTime,
        duration: Date.now() - watcherInfo.startTime,
        isActive: true
      });
    }
    return statuses;
  }

  /**
   * 停止所有监控
   */
  async stopAllMonitoring() {
    const sessionIds = Array.from(this.watchers.keys());
    const results = await Promise.allSettled(
      sessionIds.map(sessionId => this.stopMonitoring(sessionId))
    );

    const successful = results.filter(r => r.status === 'fulfilled' && r.value).length;
    logger.info('Stopped all file monitoring', { 
      total: sessionIds.length, 
      successful 
    });

    return successful;
  }

  /**
   * 事件发射器功能
   */
  emit(eventName, data) {
    // 简单的事件发射实现
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
      return {
        fileEvents: stats.fileEvents,
        monitoringDuration: this.getMonitoringStatus(sessionId)?.duration || 0
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
const fileMonitor = new FileMonitor();

module.exports = fileMonitor;