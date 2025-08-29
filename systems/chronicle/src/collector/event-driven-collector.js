/**
 * 🎯 Chronicle事件驱动采集器 (Event-Driven Collector)
 * ====================================================
 * 
 * 架构革命：从"巡逻兵"到"守望者"
 * 
 * 核心理念：
 * - 废除定期扫描，采用事件驱动架构
 * - 实时订阅日志流 (tail -f)
 * - 注册系统钩子 (System Hooks)
 * - 毫秒级响应延迟
 * - 静默高效运行
 * 
 * 功能：
 * 1. 订阅日志流 - 实时监听所有日志文件变化
 * 2. 注册系统钩子 - 内核级事件回调
 * 3. 事件驱动处理 - 被动响应，主动沉睡
 * 
 * Author: N.S.S-Novena-Garfield Project
 * Version: 3.0.0 - "The Great Expansion - Event-Driven Revolution"
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');
const { spawn, exec } = require('child_process');
const { promisify } = require('util');
const { EventEmitter } = require('events');
const { Tail } = require('tail');
const logger = require('../shared/logger');
const { getChronicleBlackBox, SystemSource, FailureSeverity } = require('../genesis/black-box');

const execAsync = promisify(exec);

class EventDrivenCollector extends EventEmitter {
  constructor() {
    super();
    
    this.isListening = false;
    this.logStreamSubscriptions = new Map();
    this.systemHooks = new Map();
    this.eventQueue = [];
    
    // 事件驱动配置
    this.config = {
      // 日志流订阅配置
      logStreaming: {
        enabled: true,
        encoding: 'utf8',
        separator: '\n',
        fromBeginning: false,     // 只监听新内容
        follow: true,             // 跟随文件轮转
        flushAtEOF: true,         // 文件结束时刷新
        useWatchFile: false       // 使用inotify而非轮询
      },
      
      // 系统钩子配置
      systemHooks: {
        enabled: true,
        cpuThreshold: 90,         // CPU阈值 90%
        memoryThreshold: 85,      // 内存阈值 85%
        diskThreshold: 90,        // 磁盘阈值 90%
        hookInterval: 1000,       // 钩子检查间隔 1秒
        maxHooks: 20              // 最大钩子数量
      },
      
      // 事件处理配置
      eventProcessing: {
        maxQueueSize: 1000,       // 最大事件队列大小
        batchSize: 10,            // 批处理大小
        processingDelay: 100,     // 处理延迟 100ms
        maxConcurrentEvents: 5    // 最大并发事件处理数
      },
      
      // 性能优化配置
      performance: {
        silentMode: true,         // 静默模式
        lowCpuMode: true,         // 低CPU模式
        memoryLimit: 50,          // 内存限制 50MB
        gcInterval: 300000        // 垃圾回收间隔 5分钟
      }
    };

    this.blackBox = getChronicleBlackBox();
    this.currentEvents = 0;
    
    // 性能监控
    this.performanceStats = {
      eventsProcessed: 0,
      averageResponseTime: 0,
      memoryUsage: 0,
      cpuUsage: 0,
      lastGC: Date.now()
    };
    
    logger.info('🎯 事件驱动采集器初始化完成 - 守望者模式');
  }

  /**
   * 启动事件驱动监听
   */
  async startEventDrivenListening() {
    try {
      if (this.isListening) {
        logger.warn('事件驱动监听已在运行中');
        return { success: true, message: '监听器已运行' };
      }

      logger.info('🚀 启动Chronicle事件驱动监听 - 守望者觉醒');

      // 1. 发现并订阅所有日志流
      await this.discoverAndSubscribeLogStreams();

      // 2. 注册系统级钩子
      await this.registerSystemHooks();

      // 3. 启动事件处理引擎
      this.startEventProcessingEngine();

      // 4. 启动性能监控
      this.startPerformanceMonitoring();

      this.isListening = true;
      
      logger.info('✅ 事件驱动监听启动成功 - 守望者就位，静默待命');

      return {
        success: true,
        message: '事件驱动监听已启动',
        mode: 'event_driven_guardian',
        subscriptions: this.logStreamSubscriptions.size,
        hooks: this.systemHooks.size,
        responseTime: '毫秒级'
      };

    } catch (error) {
      logger.error('❌ 启动事件驱动监听失败:', error);
      
      await this.blackBox.recordFailure({
        source: SystemSource.CHRONICLE,
        function_name: 'startEventDrivenListening',
        error_type: error.constructor.name,
        error_message: error.message,
        stack_trace: error.stack,
        severity: FailureSeverity.HIGH
      });
      
      throw error;
    }
  }

  /**
   * 发现并订阅所有日志流
   */
  async discoverAndSubscribeLogStreams() {
    try {
      logger.info('🔍 发现日志文件并建立实时订阅...');

      // 发现项目日志文件
      const projectLogs = await this.discoverProjectLogFiles();
      
      // 发现系统日志文件
      const systemLogs = await this.discoverSystemLogFiles();
      
      // 合并所有日志文件
      const allLogFiles = [...projectLogs, ...systemLogs];
      
      logger.info(`📋 发现 ${allLogFiles.length} 个日志文件，开始建立实时订阅...`);

      // 为每个日志文件建立tail订阅
      for (const logFile of allLogFiles) {
        await this.subscribeToLogStream(logFile);
        
        // 避免同时创建太多订阅，造成系统负载
        await this.sleep(50);
      }

      logger.info(`✅ 成功订阅 ${this.logStreamSubscriptions.size} 个日志流`);

    } catch (error) {
      logger.error('❌ 发现和订阅日志流失败:', error);
      throw error;
    }
  }

  /**
   * 发现项目日志文件
   */
  async discoverProjectLogFiles() {
    const projectLogs = [];
    const projectsPath = '/workspace/systems';

    try {
      const projects = await fs.readdir(projectsPath, { withFileTypes: true });
      
      for (const project of projects) {
        if (project.isDirectory()) {
          const projectPath = path.join(projectsPath, project.name);
          const logs = await this.findLogFilesInProject(projectPath, project.name);
          projectLogs.push(...logs);
        }
      }

    } catch (error) {
      logger.debug('发现项目日志文件失败:', error.message);
    }

    return projectLogs;
  }

  /**
   * 在项目中查找日志文件
   */
  async findLogFilesInProject(projectPath, projectName) {
    const logFiles = [];
    
    try {
      // 检查常见日志目录
      const logDirs = ['logs', 'log', 'var/log'];
      
      for (const logDir of logDirs) {
        const fullLogPath = path.join(projectPath, logDir);
        
        try {
          const files = await fs.readdir(fullLogPath);
          
          for (const file of files) {
            if (file.endsWith('.log') || file.endsWith('.out') || file.endsWith('.err')) {
              logFiles.push({
                path: path.join(fullLogPath, file),
                type: 'project',
                project: projectName,
                name: file
              });
            }
          }
        } catch (e) {
          // 目录不存在，继续
        }
      }

      // 检查根目录的日志文件
      try {
        const files = await fs.readdir(projectPath);
        
        for (const file of files) {
          if (file.endsWith('.log') || file.endsWith('.out') || file.endsWith('.err')) {
            logFiles.push({
              path: path.join(projectPath, file),
              type: 'project',
              project: projectName,
              name: file
            });
          }
        }
      } catch (e) {
        // 忽略错误
      }

    } catch (error) {
      logger.debug(`查找项目 ${projectName} 日志文件失败:`, error.message);
    }

    return logFiles;
  }

  /**
   * 发现系统日志文件
   */
  async discoverSystemLogFiles() {
    const systemLogs = [];
    const systemLogPaths = this.getSystemLogPaths();

    for (const logPath of systemLogPaths) {
      try {
        await fs.access(logPath);
        systemLogs.push({
          path: logPath,
          type: 'system',
          name: path.basename(logPath)
        });
      } catch (e) {
        // 日志文件不存在或无权限访问
        logger.debug(`系统日志文件不可访问: ${logPath}`);
      }
    }

    return systemLogs;
  }

  /**
   * 获取系统日志路径
   */
  getSystemLogPaths() {
    const platform = os.platform();
    
    switch (platform) {
      case 'linux':
        return [
          '/var/log/syslog',
          '/var/log/messages',
          '/var/log/kern.log',
          '/var/log/auth.log',
          '/var/log/daemon.log',
          '/var/log/user.log'
        ];
      case 'darwin': // macOS
        return [
          '/var/log/system.log',
          '/var/log/kernel.log'
        ];
      default:
        return [];
    }
  }

  /**
   * 订阅单个日志流
   */
  async subscribeToLogStream(logFile) {
    try {
      logger.debug(`📡 订阅日志流: ${logFile.name} (${logFile.type})`);

      // 创建Tail实例 - 这是真正的tail -f实现
      const tail = new Tail(logFile.path, {
        separator: this.config.logStreaming.separator,
        fromBeginning: this.config.logStreaming.fromBeginning,
        follow: this.config.logStreaming.follow,
        flushAtEOF: this.config.logStreaming.flushAtEOF,
        useWatchFile: this.config.logStreaming.useWatchFile,
        encoding: this.config.logStreaming.encoding
      });

      // 监听新行事件 - 实时响应
      tail.on('line', (line) => {
        this.handleLogStreamEvent(logFile, line);
      });

      // 监听错误事件
      tail.on('error', (error) => {
        logger.debug(`日志流订阅错误 ${logFile.name}:`, error.message);
        this.handleLogStreamError(logFile, error);
      });

      // 存储订阅
      this.logStreamSubscriptions.set(logFile.path, {
        logFile: logFile,
        tail: tail,
        subscribedAt: new Date().toISOString(),
        eventCount: 0,
        lastEvent: null
      });

      logger.debug(`✅ 日志流订阅成功: ${logFile.name}`);

    } catch (error) {
      logger.debug(`❌ 订阅日志流失败 ${logFile.name}:`, error.message);
    }
  }

  /**
   * 处理日志流事件 - 毫秒级响应
   */
  handleLogStreamEvent(logFile, logLine) {
    try {
      // 立即检查是否是错误日志
      if (this.isErrorLogLine(logLine)) {
        const event = {
          id: this.generateEventId(),
          type: 'log_error',
          source: logFile.type,
          project: logFile.project || 'system',
          logFile: logFile.name,
          logPath: logFile.path,
          content: logLine,
          timestamp: new Date().toISOString(),
          priority: this.calculateEventPriority(logLine),
          processed: false
        };

        // 立即加入事件队列
        this.enqueueEvent(event);

        // 更新订阅统计
        const subscription = this.logStreamSubscriptions.get(logFile.path);
        if (subscription) {
          subscription.eventCount++;
          subscription.lastEvent = new Date().toISOString();
        }

        logger.debug(`🚨 检测到错误事件: ${logFile.project || 'system'} - ${logLine.substring(0, 100)}...`);
      }

    } catch (error) {
      logger.debug('处理日志流事件失败:', error.message);
    }
  }

  /**
   * 处理日志流错误
   */
  handleLogStreamError(logFile, error) {
    logger.debug(`日志流错误 ${logFile.name}:`, error.message);
    
    // 尝试重新订阅
    setTimeout(() => {
      this.resubscribeLogStream(logFile);
    }, 5000);
  }

  /**
   * 重新订阅日志流
   */
  async resubscribeLogStream(logFile) {
    try {
      // 清理旧订阅
      const oldSubscription = this.logStreamSubscriptions.get(logFile.path);
      if (oldSubscription && oldSubscription.tail) {
        oldSubscription.tail.unwatch();
      }
      
      this.logStreamSubscriptions.delete(logFile.path);

      // 重新订阅
      await this.subscribeToLogStream(logFile);
      
      logger.debug(`🔄 重新订阅日志流成功: ${logFile.name}`);

    } catch (error) {
      logger.debug(`重新订阅日志流失败 ${logFile.name}:`, error.message);
    }
  }

  /**
   * 注册系统级钩子
   */
  async registerSystemHooks() {
    try {
      logger.info('🪝 注册系统级钩子 - 内核回调模式');

      // CPU使用率钩子
      await this.registerCPUHook();

      // 内存使用率钩子
      await this.registerMemoryHook();

      // 磁盘使用率钩子
      await this.registerDiskHook();

      // 进程异常钩子
      await this.registerProcessHook();

      logger.info(`✅ 成功注册 ${this.systemHooks.size} 个系统钩子`);

    } catch (error) {
      logger.error('❌ 注册系统钩子失败:', error);
      throw error;
    }
  }

  /**
   * 注册CPU使用率钩子
   */
  async registerCPUHook() {
    const hookId = 'cpu_threshold_hook';
    
    try {
      // 使用系统命令监控CPU - 事件驱动方式
      const cpuMonitor = spawn('bash', ['-c', `
        while true; do
          cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | cut -d',' -f1)
          if (( $(echo "$cpu_usage > ${this.config.systemHooks.cpuThreshold}" | bc -l) )); then
            echo "CPU_THRESHOLD_EXCEEDED:$cpu_usage"
          fi
          sleep ${this.config.systemHooks.hookInterval / 1000}
        done
      `]);

      cpuMonitor.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output.startsWith('CPU_THRESHOLD_EXCEEDED:')) {
          const cpuUsage = parseFloat(output.split(':')[1]);
          this.handleSystemHookEvent('cpu_threshold', { cpuUsage });
        }
      });

      cpuMonitor.on('error', (error) => {
        logger.debug('CPU钩子错误:', error.message);
      });

      this.systemHooks.set(hookId, {
        type: 'cpu_threshold',
        process: cpuMonitor,
        threshold: this.config.systemHooks.cpuThreshold,
        registeredAt: new Date().toISOString(),
        eventCount: 0
      });

      logger.debug('✅ CPU使用率钩子已注册');

    } catch (error) {
      logger.debug('注册CPU钩子失败:', error.message);
    }
  }

  /**
   * 注册内存使用率钩子
   */
  async registerMemoryHook() {
    const hookId = 'memory_threshold_hook';
    
    try {
      const memoryMonitor = spawn('bash', ['-c', `
        while true; do
          memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
          if (( $(echo "$memory_usage > ${this.config.systemHooks.memoryThreshold}" | bc -l) )); then
            echo "MEMORY_THRESHOLD_EXCEEDED:$memory_usage"
          fi
          sleep ${this.config.systemHooks.hookInterval / 1000}
        done
      `]);

      memoryMonitor.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output.startsWith('MEMORY_THRESHOLD_EXCEEDED:')) {
          const memoryUsage = parseFloat(output.split(':')[1]);
          this.handleSystemHookEvent('memory_threshold', { memoryUsage });
        }
      });

      this.systemHooks.set(hookId, {
        type: 'memory_threshold',
        process: memoryMonitor,
        threshold: this.config.systemHooks.memoryThreshold,
        registeredAt: new Date().toISOString(),
        eventCount: 0
      });

      logger.debug('✅ 内存使用率钩子已注册');

    } catch (error) {
      logger.debug('注册内存钩子失败:', error.message);
    }
  }

  /**
   * 注册磁盘使用率钩子
   */
  async registerDiskHook() {
    const hookId = 'disk_threshold_hook';
    
    try {
      const diskMonitor = spawn('bash', ['-c', `
        while true; do
          disk_usage=$(df / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
          if [ "$disk_usage" -gt "${this.config.systemHooks.diskThreshold}" ]; then
            echo "DISK_THRESHOLD_EXCEEDED:$disk_usage"
          fi
          sleep ${this.config.systemHooks.hookInterval / 1000}
        done
      `]);

      diskMonitor.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output.startsWith('DISK_THRESHOLD_EXCEEDED:')) {
          const diskUsage = parseInt(output.split(':')[1]);
          this.handleSystemHookEvent('disk_threshold', { diskUsage });
        }
      });

      this.systemHooks.set(hookId, {
        type: 'disk_threshold',
        process: diskMonitor,
        threshold: this.config.systemHooks.diskThreshold,
        registeredAt: new Date().toISOString(),
        eventCount: 0
      });

      logger.debug('✅ 磁盘使用率钩子已注册');

    } catch (error) {
      logger.debug('注册磁盘钩子失败:', error.message);
    }
  }

  /**
   * 注册进程异常钩子
   */
  async registerProcessHook() {
    const hookId = 'process_anomaly_hook';
    
    try {
      // 监控进程异常退出
      const processMonitor = spawn('bash', ['-c', `
        while true; do
          # 检查是否有进程异常退出
          dmesg | tail -n 5 | grep -E "(killed|segfault|out of memory)" && echo "PROCESS_ANOMALY_DETECTED"
          sleep ${this.config.systemHooks.hookInterval / 1000}
        done
      `]);

      processMonitor.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output.includes('PROCESS_ANOMALY_DETECTED')) {
          this.handleSystemHookEvent('process_anomaly', { detected: true });
        }
      });

      this.systemHooks.set(hookId, {
        type: 'process_anomaly',
        process: processMonitor,
        registeredAt: new Date().toISOString(),
        eventCount: 0
      });

      logger.debug('✅ 进程异常钩子已注册');

    } catch (error) {
      logger.debug('注册进程钩子失败:', error.message);
    }
  }

  /**
   * 处理系统钩子事件
   */
  handleSystemHookEvent(hookType, data) {
    try {
      const event = {
        id: this.generateEventId(),
        type: 'system_hook',
        hookType: hookType,
        data: data,
        timestamp: new Date().toISOString(),
        priority: this.calculateSystemEventPriority(hookType, data),
        processed: false
      };

      // 立即加入事件队列
      this.enqueueEvent(event);

      // 更新钩子统计
      for (const [hookId, hook] of this.systemHooks) {
        if (hook.type === hookType) {
          hook.eventCount++;
          break;
        }
      }

      logger.debug(`🪝 系统钩子触发: ${hookType} - ${JSON.stringify(data)}`);

    } catch (error) {
      logger.debug('处理系统钩子事件失败:', error.message);
    }
  }

  /**
   * 启动事件处理引擎
   */
  startEventProcessingEngine() {
    logger.info('⚡ 启动事件处理引擎 - 毫秒级响应');

    // 使用setImmediate确保最高优先级处理
    const processEvents = () => {
      if (this.eventQueue.length > 0 && this.currentEvents < this.config.eventProcessing.maxConcurrentEvents) {
        const batchSize = Math.min(
          this.config.eventProcessing.batchSize,
          this.eventQueue.length,
          this.config.eventProcessing.maxConcurrentEvents - this.currentEvents
        );

        const batch = this.eventQueue.splice(0, batchSize);
        this.processBatchEvents(batch);
      }

      // 使用setImmediate而非setTimeout，确保最快响应
      setImmediate(processEvents);
    };

    // 启动事件处理循环
    setImmediate(processEvents);

    logger.info('✅ 事件处理引擎已启动 - 待命中');
  }

  /**
   * 批量处理事件
   */
  async processBatchEvents(events) {
    this.currentEvents += events.length;

    try {
      const startTime = Date.now();

      // 并行处理事件
      const promises = events.map(event => this.processEvent(event));
      await Promise.all(promises);

      // 更新性能统计
      const processingTime = Date.now() - startTime;
      this.updatePerformanceStats(events.length, processingTime);

    } catch (error) {
      logger.debug('批量处理事件失败:', error.message);
    } finally {
      this.currentEvents -= events.length;
    }
  }

  /**
   * 处理单个事件
   */
  async processEvent(event) {
    try {
      event.processedAt = new Date().toISOString();
      event.processed = true;

      // 根据事件类型处理
      switch (event.type) {
        case 'log_error':
          await this.processLogErrorEvent(event);
          break;
        case 'system_hook':
          await this.processSystemHookEvent(event);
          break;
        default:
          logger.debug(`未知事件类型: ${event.type}`);
      }

      // 发射事件给其他组件
      this.emit('event_processed', event);

    } catch (error) {
      logger.debug(`处理事件失败 ${event.id}:`, error.message);
      event.error = error.message;
    }
  }

  /**
   * 处理日志错误事件
   */
  async processLogErrorEvent(event) {
    try {
      // 解析错误信息
      const errorInfo = this.parseErrorFromLogLine(event.content);

      // 记录到黑匣子
      await this.blackBox.recordFailure({
        source: event.source === 'project' ? SystemSource.PROJECT : SystemSource.SYSTEM,
        function_name: 'event_driven_log_analysis',
        error_type: errorInfo.type,
        error_message: errorInfo.message,
        context: {
          project: event.project,
          logFile: event.logFile,
          logPath: event.logPath,
          fullLogLine: event.content,
          detectedBy: 'event_driven_collector',
          responseTime: 'milliseconds',
          eventId: event.id
        },
        severity: errorInfo.severity
      });

      logger.debug(`⚡ 毫秒级处理日志错误: ${event.project} - ${errorInfo.type}`);

    } catch (error) {
      logger.debug('处理日志错误事件失败:', error.message);
    }
  }

  /**
   * 处理系统钩子事件
   */
  async processSystemHookEvent(event) {
    try {
      let errorType = 'SystemHookEvent';
      let severity = FailureSeverity.MEDIUM;

      switch (event.hookType) {
        case 'cpu_threshold':
          errorType = 'HighCPUUsage';
          severity = event.data.cpuUsage > 95 ? FailureSeverity.CRITICAL : FailureSeverity.HIGH;
          break;
        case 'memory_threshold':
          errorType = 'HighMemoryUsage';
          severity = event.data.memoryUsage > 95 ? FailureSeverity.CRITICAL : FailureSeverity.HIGH;
          break;
        case 'disk_threshold':
          errorType = 'HighDiskUsage';
          severity = event.data.diskUsage > 95 ? FailureSeverity.CRITICAL : FailureSeverity.HIGH;
          break;
        case 'process_anomaly':
          errorType = 'ProcessAnomaly';
          severity = FailureSeverity.HIGH;
          break;
      }

      // 记录到黑匣子
      await this.blackBox.recordFailure({
        source: SystemSource.SYSTEM,
        function_name: 'event_driven_system_monitoring',
        error_type: errorType,
        error_message: `System hook triggered: ${event.hookType}`,
        context: {
          hookType: event.hookType,
          hookData: event.data,
          detectedBy: 'event_driven_collector',
          responseTime: 'milliseconds',
          eventId: event.id
        },
        severity: severity
      });

      logger.debug(`🪝 毫秒级处理系统钩子: ${event.hookType} - ${JSON.stringify(event.data)}`);

    } catch (error) {
      logger.debug('处理系统钩子事件失败:', error.message);
    }
  }

  /**
   * 启动性能监控
   */
  startPerformanceMonitoring() {
    logger.info('📊 启动性能监控 - 守望者自我监控');

    const performanceMonitor = setInterval(() => {
      this.monitorPerformance();
    }, 30000); // 30秒检查一次

    // 定期垃圾回收
    const gcInterval = setInterval(() => {
      if (global.gc && Date.now() - this.performanceStats.lastGC > this.config.performance.gcInterval) {
        global.gc();
        this.performanceStats.lastGC = Date.now();
        logger.debug('🧹 执行垃圾回收');
      }
    }, this.config.performance.gcInterval);

    this.systemHooks.set('performance_monitor', performanceMonitor);
    this.systemHooks.set('gc_interval', gcInterval);
  }

  /**
   * 监控性能
   */
  monitorPerformance() {
    try {
      const memUsage = process.memoryUsage();
      const memMB = memUsage.heapUsed / 1024 / 1024;

      this.performanceStats.memoryUsage = memMB;

      // 检查内存使用
      if (memMB > this.config.performance.memoryLimit) {
        logger.warn(`⚠️ 守望者内存使用过高: ${memMB.toFixed(2)}MB`);
        
        // 强制垃圾回收
        if (global.gc) {
          global.gc();
        }

        // 清理事件队列
        if (this.eventQueue.length > this.config.eventProcessing.maxQueueSize / 2) {
          this.eventQueue = this.eventQueue.slice(-this.config.eventProcessing.maxQueueSize / 2);
          logger.debug('🧹 清理事件队列');
        }
      }

      // 更新统计信息
      logger.debug(`📊 守望者状态: 内存=${memMB.toFixed(2)}MB, 事件队列=${this.eventQueue.length}, 订阅=${this.logStreamSubscriptions.size}, 钩子=${this.systemHooks.size}`);

    } catch (error) {
      logger.debug('性能监控失败:', error.message);
    }
  }

  /**
   * 更新性能统计
   */
  updatePerformanceStats(eventCount, processingTime) {
    this.performanceStats.eventsProcessed += eventCount;
    
    // 计算平均响应时间
    const currentAvg = this.performanceStats.averageResponseTime;
    const newAvg = (currentAvg + (processingTime / eventCount)) / 2;
    this.performanceStats.averageResponseTime = newAvg;
  }

  /**
   * 将事件加入队列
   */
  enqueueEvent(event) {
    // 检查队列大小
    if (this.eventQueue.length >= this.config.eventProcessing.maxQueueSize) {
      // 移除最老的事件
      this.eventQueue.shift();
    }

    // 根据优先级插入
    const insertIndex = this.findInsertIndex(event.priority);
    this.eventQueue.splice(insertIndex, 0, event);
  }

  /**
   * 查找插入位置（按优先级排序）
   */
  findInsertIndex(priority) {
    for (let i = 0; i < this.eventQueue.length; i++) {
      if (this.eventQueue[i].priority < priority) {
        return i;
      }
    }
    return this.eventQueue.length;
  }

  /**
   * 检查是否是错误日志行
   */
  isErrorLogLine(logLine) {
    const errorPatterns = [
      /ERROR/i,
      /FATAL/i,
      /CRITICAL/i,
      /Exception/i,
      /Traceback/i,
      /Failed/i,
      /Connection refused/i,
      /Timeout/i,
      /Out of memory/i,
      /Permission denied/i,
      /ENOENT/i,
      /EACCES/i,
      /Segmentation fault/i,
      /Core dumped/i
    ];

    return errorPatterns.some(pattern => pattern.test(logLine));
  }

  /**
   * 从日志行解析错误信息
   */
  parseErrorFromLogLine(logLine) {
    let type = 'UnknownError';
    let severity = FailureSeverity.MEDIUM;

    if (/FATAL|CRITICAL/i.test(logLine)) {
      severity = FailureSeverity.CRITICAL;
    } else if (/ERROR/i.test(logLine)) {
      severity = FailureSeverity.HIGH;
    }

    if (/Connection refused|ECONNREFUSED/i.test(logLine)) {
      type = 'ConnectionError';
    } else if (/Timeout|ETIMEDOUT/i.test(logLine)) {
      type = 'TimeoutError';
    } else if (/Out of memory|OOM/i.test(logLine)) {
      type = 'MemoryError';
      severity = FailureSeverity.CRITICAL;
    } else if (/Permission denied|EACCES/i.test(logLine)) {
      type = 'PermissionError';
    } else if (/No such file|ENOENT/i.test(logLine)) {
      type = 'FileNotFoundError';
    } else if (/Exception|Traceback/i.test(logLine)) {
      type = 'ApplicationError';
    } else if (/Segmentation fault|Core dumped/i.test(logLine)) {
      type = 'SegmentationFault';
      severity = FailureSeverity.CRITICAL;
    }

    return {
      type,
      message: logLine.trim().substring(0, 500),
      severity
    };
  }

  /**
   * 计算事件优先级
   */
  calculateEventPriority(logLine) {
    let priority = 50; // 基础优先级

    if (/CRITICAL|FATAL/i.test(logLine)) {
      priority = 100;
    } else if (/ERROR/i.test(logLine)) {
      priority = 80;
    } else if (/WARN/i.test(logLine)) {
      priority = 60;
    }

    // 特殊错误类型提高优先级
    if (/Out of memory|Segmentation fault|Core dumped/i.test(logLine)) {
      priority = 100;
    }

    return priority;
  }

  /**
   * 计算系统事件优先级
   */
  calculateSystemEventPriority(hookType, data) {
    switch (hookType) {
      case 'cpu_threshold':
        return data.cpuUsage > 95 ? 100 : 80;
      case 'memory_threshold':
        return data.memoryUsage > 95 ? 100 : 80;
      case 'disk_threshold':
        return data.diskUsage > 95 ? 100 : 80;
      case 'process_anomaly':
        return 90;
      default:
        return 70;
    }
  }

  /**
   * 生成事件ID
   */
  generateEventId() {
    return `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * 睡眠函数
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 停止事件驱动监听
   */
  async stopEventDrivenListening() {
    try {
      logger.info('🛑 停止事件驱动监听 - 守望者休眠');

      // 停止所有日志流订阅
      for (const [path, subscription] of this.logStreamSubscriptions) {
        if (subscription.tail) {
          subscription.tail.unwatch();
        }
      }
      this.logStreamSubscriptions.clear();

      // 停止所有系统钩子
      for (const [hookId, hook] of this.systemHooks) {
        if (hook.process && hook.process.kill) {
          hook.process.kill();
        } else if (typeof hook === 'number') {
          clearInterval(hook);
        }
      }
      this.systemHooks.clear();

      // 清理事件队列
      this.eventQueue = [];

      this.isListening = false;
      logger.info('✅ 事件驱动监听已停止 - 守望者已休眠');

      return {
        success: true,
        message: '事件驱动监听已停止'
      };

    } catch (error) {
      logger.error('❌ 停止事件驱动监听失败:', error);
      throw error;
    }
  }

  /**
   * 获取守望者状态
   */
  getGuardianStatus() {
    return {
      mode: 'event_driven_guardian',
      isListening: this.isListening,
      subscriptions: {
        total: this.logStreamSubscriptions.size,
        active: Array.from(this.logStreamSubscriptions.values()).filter(s => s.tail).length,
        details: Array.from(this.logStreamSubscriptions.entries()).map(([path, sub]) => ({
          path: path,
          type: sub.logFile.type,
          project: sub.logFile.project,
          eventCount: sub.eventCount,
          lastEvent: sub.lastEvent
        }))
      },
      systemHooks: {
        total: this.systemHooks.size,
        active: Array.from(this.systemHooks.values()).filter(h => h.process || typeof h === 'number').length,
        details: Array.from(this.systemHooks.entries()).map(([id, hook]) => ({
          id: id,
          type: hook.type || 'interval',
          eventCount: hook.eventCount || 0,
          registeredAt: hook.registeredAt
        }))
      },
      eventQueue: {
        size: this.eventQueue.length,
        maxSize: this.config.eventProcessing.maxQueueSize,
        currentProcessing: this.currentEvents
      },
      performance: this.performanceStats,
      config: this.config
    };
  }
}

module.exports = EventDrivenCollector;