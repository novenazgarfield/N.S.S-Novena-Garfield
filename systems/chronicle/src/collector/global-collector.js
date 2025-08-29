/**
 * 🌍 Chronicle全域数据采集器 (Global Data Collector)
 * ===================================================
 * 
 * 第一章：能力的"扩展" - 全域视野的建立
 * 
 * 功能：
 * - 扫描并解析所有子项目 (/workspace/systems/) 的输出日志
 * - 监控核心操作系统日志 (/var/log/syslog等)
 * - 控制CPU占用率，保持静默运行
 * - 定期扫描，不影响用户正常使用
 * 
 * 安全原则：
 * - 默认只读权限
 * - 最小化系统资源占用
 * - 静默运行，不干扰用户体验
 * 
 * Author: N.S.S-Novena-Garfield Project
 * Version: 3.0.0 - "The Great Expansion"
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');
const { spawn, exec } = require('child_process');
const { promisify } = require('util');
const chokidar = require('chokidar');
const logger = require('../shared/logger');
const { getChronicleBlackBox, SystemSource, FailureSeverity } = require('../genesis/black-box');

const execAsync = promisify(exec);

class GlobalDataCollector {
  constructor() {
    this.isCollecting = false;
    this.projectLogWatchers = new Map();
    this.systemLogWatchers = new Map();
    this.scanIntervals = new Map();
    
    // 性能控制配置 - 确保静默运行
    this.performanceConfig = {
      maxCpuUsage: 5,           // 最大CPU使用率 5%
      scanInterval: 60000,      // 扫描间隔 1分钟
      batchSize: 10,            // 批处理大小
      maxLogLines: 50,          // 每次最多读取50行日志
      throttleDelay: 100,       // 节流延迟 100ms
      maxConcurrentScans: 3,    // 最大并发扫描数
      quietHours: {             // 静默时间段
        enabled: true,
        start: 22,              // 22:00
        end: 8                  // 08:00
      }
    };

    // 全域监控配置
    this.globalConfig = {
      projectsPath: '/workspace/systems',
      systemLogPaths: this.getSystemLogPaths(),
      excludePatterns: [
        'node_modules',
        '.git',
        'dist',
        'build',
        '__pycache__',
        '.pytest_cache',
        'coverage'
      ],
      logFilePatterns: [
        '*.log',
        '*.out',
        '*.err',
        'logs/**/*.log',
        'log/**/*.log'
      ]
    };

    this.blackBox = getChronicleBlackBox();
    this.currentScans = 0;
    
    logger.info('🌍 全域数据采集器初始化完成 - 静默模式');
  }

  /**
   * 启动全域数据采集
   */
  async startGlobalCollection() {
    try {
      if (this.isCollecting) {
        logger.warn('全域数据采集已在运行中');
        return { success: true, message: '采集器已运行' };
      }

      logger.info('🚀 启动Chronicle全域数据采集 - 静默模式');

      // 检查系统资源
      await this.checkSystemResources();

      // 1. 扫描并注册所有项目
      const projects = await this.discoverProjects();
      
      // 2. 启动项目日志监控
      await this.startProjectLogMonitoring(projects);

      // 3. 启动系统日志监控
      await this.startSystemLogMonitoring();

      // 4. 启动定期扫描
      this.startPeriodicScanning();

      // 5. 启动性能监控
      this.startPerformanceMonitoring();

      this.isCollecting = true;
      
      logger.info('✅ 全域数据采集启动成功 - 静默运行中');

      return {
        success: true,
        message: '全域数据采集已启动',
        data: {
          monitored_projects: projects.length,
          system_logs: this.globalConfig.systemLogPaths.length,
          performance_mode: 'silent',
          cpu_limit: this.performanceConfig.maxCpuUsage + '%'
        }
      };

    } catch (error) {
      logger.error('❌ 启动全域数据采集失败:', error);
      
      await this.blackBox.recordFailure({
        source: SystemSource.CHRONICLE,
        function_name: 'startGlobalCollection',
        error_type: error.constructor.name,
        error_message: error.message,
        stack_trace: error.stack,
        severity: FailureSeverity.HIGH
      });
      
      throw error;
    }
  }

  /**
   * 检查系统资源
   */
  async checkSystemResources() {
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const memUsage = ((totalMem - freeMem) / totalMem) * 100;

    if (memUsage > 90) {
      logger.warn('⚠️ 系统内存使用率过高，降低采集频率');
      this.performanceConfig.scanInterval *= 2; // 降低扫描频率
    }

    // 检查是否在静默时间段
    const currentHour = new Date().getHours();
    const quietHours = this.performanceConfig.quietHours;
    
    if (quietHours.enabled && 
        (currentHour >= quietHours.start || currentHour < quietHours.end)) {
      logger.info('🌙 进入静默时间段，降低监控频率');
      this.performanceConfig.scanInterval *= 3; // 静默时间段降低频率
    }
  }

  /**
   * 发现所有项目
   */
  async discoverProjects() {
    try {
      logger.info('🔍 静默扫描项目目录...');

      const projectsPath = this.globalConfig.projectsPath;
      const entries = await fs.readdir(projectsPath, { withFileTypes: true });
      const projects = [];

      for (const entry of entries) {
        if (entry.isDirectory() && !this.isExcludedDirectory(entry.name)) {
          const projectPath = path.join(projectsPath, entry.name);
          const projectInfo = await this.analyzeProjectQuietly(projectPath, entry.name);
          
          if (projectInfo) {
            projects.push(projectInfo);
          }

          // 节流控制 - 避免CPU占用过高
          await this.throttle();
        }
      }

      logger.info(`✅ 静默发现 ${projects.length} 个项目`);
      return projects;

    } catch (error) {
      logger.error('❌ 项目发现失败:', error);
      throw error;
    }
  }

  /**
   * 静默分析项目
   */
  async analyzeProjectQuietly(projectPath, projectName) {
    try {
      const projectInfo = {
        name: projectName,
        path: projectPath,
        type: 'unknown',
        logPaths: [],
        configFiles: [],
        lastScanned: new Date().toISOString()
      };

      // 静默检查项目文件
      const files = await fs.readdir(projectPath).catch(() => []);

      // 检测项目类型
      if (files.includes('package.json')) {
        projectInfo.type = 'nodejs';
      } else if (files.includes('requirements.txt') || files.includes('pyproject.toml')) {
        projectInfo.type = 'python';
      } else if (files.includes('Cargo.toml')) {
        projectInfo.type = 'rust';
      } else if (files.includes('go.mod')) {
        projectInfo.type = 'go';
      }

      // 发现日志文件
      projectInfo.logPaths = await this.discoverLogFiles(projectPath);

      // 发现配置文件
      projectInfo.configFiles = await this.discoverConfigFiles(projectPath);

      return projectInfo;

    } catch (error) {
      logger.debug(`项目分析失败 ${projectName}:`, error.message);
      return null;
    }
  }

  /**
   * 发现日志文件
   */
  async discoverLogFiles(projectPath) {
    const logPaths = [];
    
    try {
      // 检查常见日志目录
      const logDirs = ['logs', 'log', 'var/log'];
      
      for (const logDir of logDirs) {
        const fullLogPath = path.join(projectPath, logDir);
        
        try {
          await fs.access(fullLogPath);
          logPaths.push(fullLogPath);
        } catch (e) {
          // 目录不存在，继续
        }
      }

      // 检查根目录的日志文件
      const files = await fs.readdir(projectPath).catch(() => []);
      for (const file of files) {
        if (file.endsWith('.log') || file.endsWith('.out') || file.endsWith('.err')) {
          logPaths.push(path.join(projectPath, file));
        }
      }

    } catch (error) {
      logger.debug('发现日志文件失败:', error.message);
    }

    return logPaths;
  }

  /**
   * 发现配置文件
   */
  async discoverConfigFiles(projectPath) {
    const configFiles = [];
    const configPatterns = [
      'config.json', 'config.yaml', 'config.yml', '.env',
      'package.json', 'requirements.txt', 'Dockerfile'
    ];

    try {
      const files = await fs.readdir(projectPath).catch(() => []);
      
      for (const pattern of configPatterns) {
        if (files.includes(pattern)) {
          configFiles.push(pattern);
        }
      }
    } catch (error) {
      logger.debug('发现配置文件失败:', error.message);
    }

    return configFiles;
  }

  /**
   * 启动项目日志监控
   */
  async startProjectLogMonitoring(projects) {
    logger.info('📊 启动项目日志监控 - 静默模式');

    for (const project of projects) {
      try {
        await this.startSingleProjectLogMonitoring(project);
        
        // 节流控制
        await this.throttle();
        
      } catch (error) {
        logger.debug(`项目日志监控启动失败 ${project.name}:`, error.message);
      }
    }
  }

  /**
   * 启动单个项目日志监控
   */
  async startSingleProjectLogMonitoring(project) {
    if (project.logPaths.length === 0) {
      return; // 没有日志文件，跳过
    }

    const watchers = [];

    for (const logPath of project.logPaths) {
      try {
        const watcher = chokidar.watch(logPath, {
          persistent: true,
          ignoreInitial: true,
          usePolling: true,        // 使用轮询模式，减少系统负载
          interval: 5000,          // 5秒轮询间隔
          binaryInterval: 10000,   // 二进制文件10秒间隔
          depth: 2                 // 限制深度
        });

        watcher.on('change', async (filePath) => {
          await this.handleProjectLogChange(project.name, filePath);
        });

        watchers.push(watcher);

      } catch (error) {
        logger.debug(`监控日志文件失败 ${logPath}:`, error.message);
      }
    }

    if (watchers.length > 0) {
      this.projectLogWatchers.set(project.name, watchers);
      logger.debug(`✅ 项目 ${project.name} 日志监控启动 (${watchers.length} 个文件)`);
    }
  }

  /**
   * 处理项目日志变化
   */
  async handleProjectLogChange(projectName, logPath) {
    try {
      // 限制并发处理
      if (this.currentScans >= this.performanceConfig.maxConcurrentScans) {
        return; // 跳过此次处理，避免系统负载过高
      }

      this.currentScans++;

      // 读取日志文件的最后几行
      const logLines = await this.readLogFileQuietly(logPath);
      
      // 分析日志内容
      for (const line of logLines) {
        if (this.isErrorLogLine(line)) {
          await this.processErrorLogLine(projectName, logPath, line);
        }
      }

    } catch (error) {
      logger.debug(`处理项目日志变化失败 ${projectName}:`, error.message);
    } finally {
      this.currentScans--;
    }
  }

  /**
   * 静默读取日志文件
   */
  async readLogFileQuietly(logPath) {
    try {
      const maxLines = this.performanceConfig.maxLogLines;
      const { stdout } = await execAsync(`tail -n ${maxLines} "${logPath}" 2>/dev/null || echo ""`);
      
      return stdout.trim().split('\n').filter(line => line.trim());
      
    } catch (error) {
      return []; // 静默失败，返回空数组
    }
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
      /EACCES/i
    ];

    return errorPatterns.some(pattern => pattern.test(logLine));
  }

  /**
   * 处理错误日志行
   */
  async processErrorLogLine(projectName, logPath, errorLine) {
    try {
      // 解析错误信息
      const errorInfo = this.parseErrorFromLogLine(errorLine);

      // 记录到黑匣子
      await this.blackBox.recordFailure({
        source: SystemSource.PROJECT,
        function_name: 'log_analysis',
        error_type: errorInfo.type,
        error_message: errorInfo.message,
        context: {
          projectName,
          logPath,
          fullLogLine: errorLine,
          detectedBy: 'global_collector',
          timestamp: new Date().toISOString()
        },
        severity: errorInfo.severity
      });

      logger.debug(`🔍 检测到项目错误: ${projectName} - ${errorInfo.type}`);

    } catch (error) {
      logger.debug('处理错误日志行失败:', error.message);
    }
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
    }

    return {
      type,
      message: logLine.trim().substring(0, 500), // 限制长度
      severity
    };
  }

  /**
   * 启动系统日志监控
   */
  async startSystemLogMonitoring() {
    logger.info('🖥️ 启动系统日志监控 - 静默模式');

    const systemLogPaths = this.globalConfig.systemLogPaths;

    for (const logPath of systemLogPaths) {
      try {
        await fs.access(logPath);
        
        const watcher = chokidar.watch(logPath, {
          persistent: true,
          ignoreInitial: true,
          usePolling: true,
          interval: 10000,         // 系统日志10秒轮询
          binaryInterval: 20000
        });

        watcher.on('change', async () => {
          await this.handleSystemLogChange(logPath);
        });

        this.systemLogWatchers.set(path.basename(logPath), watcher);
        logger.debug(`📋 监控系统日志: ${logPath}`);

      } catch (error) {
        logger.debug(`无法监控系统日志 ${logPath}:`, error.message);
      }
    }
  }

  /**
   * 处理系统日志变化
   */
  async handleSystemLogChange(logPath) {
    try {
      if (this.currentScans >= this.performanceConfig.maxConcurrentScans) {
        return; // 限制并发
      }

      this.currentScans++;

      const logLines = await this.readLogFileQuietly(logPath);

      for (const line of logLines) {
        if (this.isSystemErrorLogLine(line)) {
          await this.processSystemErrorLogLine(logPath, line);
        }
      }

    } catch (error) {
      logger.debug(`处理系统日志变化失败 ${logPath}:`, error.message);
    } finally {
      this.currentScans--;
    }
  }

  /**
   * 检查是否是系统错误日志行
   */
  isSystemErrorLogLine(logLine) {
    const systemErrorPatterns = [
      /kernel panic/i,
      /segmentation fault/i,
      /out of memory/i,
      /disk full/i,
      /authentication failure/i,
      /service failed/i,
      /critical/i,
      /fatal/i,
      /emergency/i,
      /alert/i
    ];

    return systemErrorPatterns.some(pattern => pattern.test(logLine));
  }

  /**
   * 处理系统错误日志行
   */
  async processSystemErrorLogLine(logPath, errorLine) {
    try {
      const errorInfo = this.parseSystemErrorFromLogLine(errorLine);

      await this.blackBox.recordFailure({
        source: SystemSource.SYSTEM,
        function_name: 'system_log_analysis',
        error_type: errorInfo.type,
        error_message: errorInfo.message,
        context: {
          logPath,
          fullLogLine: errorLine,
          detectedBy: 'global_collector',
          systemInfo: {
            platform: os.platform(),
            arch: os.arch(),
            release: os.release()
          },
          timestamp: new Date().toISOString()
        },
        severity: errorInfo.severity
      });

      logger.debug(`🚨 检测到系统错误: ${errorInfo.type}`);

    } catch (error) {
      logger.debug('处理系统错误日志行失败:', error.message);
    }
  }

  /**
   * 从系统日志行解析错误信息
   */
  parseSystemErrorFromLogLine(logLine) {
    let type = 'SystemError';
    let severity = FailureSeverity.HIGH;

    if (/kernel panic/i.test(logLine)) {
      type = 'KernelPanic';
      severity = FailureSeverity.CRITICAL;
    } else if (/out of memory/i.test(logLine)) {
      type = 'OutOfMemory';
      severity = FailureSeverity.CRITICAL;
    } else if (/disk full/i.test(logLine)) {
      type = 'DiskFull';
      severity = FailureSeverity.HIGH;
    } else if (/authentication failure/i.test(logLine)) {
      type = 'AuthenticationFailure';
      severity = FailureSeverity.MEDIUM;
    } else if (/service failed/i.test(logLine)) {
      type = 'ServiceFailure';
      severity = FailureSeverity.HIGH;
    }

    return {
      type,
      message: logLine.trim().substring(0, 500),
      severity
    };
  }

  /**
   * 启动定期扫描
   */
  startPeriodicScanning() {
    logger.info('⏰ 启动定期扫描 - 静默模式');

    // 项目扫描
    const projectScanInterval = setInterval(async () => {
      await this.performPeriodicProjectScan();
    }, this.performanceConfig.scanInterval);

    // 系统扫描
    const systemScanInterval = setInterval(async () => {
      await this.performPeriodicSystemScan();
    }, this.performanceConfig.scanInterval * 2); // 系统扫描频率更低

    this.scanIntervals.set('project_scan', projectScanInterval);
    this.scanIntervals.set('system_scan', systemScanInterval);
  }

  /**
   * 执行定期项目扫描
   */
  async performPeriodicProjectScan() {
    try {
      if (this.currentScans >= this.performanceConfig.maxConcurrentScans) {
        return; // 跳过此次扫描
      }

      logger.debug('🔍 执行定期项目扫描...');

      const projects = await this.discoverProjects();
      
      // 检查新项目
      for (const project of projects) {
        if (!this.projectLogWatchers.has(project.name)) {
          logger.info(`📁 发现新项目: ${project.name}`);
          await this.startSingleProjectLogMonitoring(project);
        }
      }

    } catch (error) {
      logger.debug('定期项目扫描失败:', error.message);
    }
  }

  /**
   * 执行定期系统扫描
   */
  async performPeriodicSystemScan() {
    try {
      logger.debug('🖥️ 执行定期系统扫描...');

      // 检查系统资源状态
      await this.checkSystemResources();

      // 检查系统日志文件是否有新增
      const currentLogPaths = this.getSystemLogPaths();
      
      for (const logPath of currentLogPaths) {
        if (!this.systemLogWatchers.has(path.basename(logPath))) {
          try {
            await fs.access(logPath);
            logger.info(`📋 发现新系统日志: ${logPath}`);
            // 这里可以添加新日志文件的监控
          } catch (e) {
            // 日志文件不存在
          }
        }
      }

    } catch (error) {
      logger.debug('定期系统扫描失败:', error.message);
    }
  }

  /**
   * 启动性能监控
   */
  startPerformanceMonitoring() {
    logger.info('📊 启动性能监控 - 确保静默运行');

    const performanceMonitor = setInterval(async () => {
      await this.monitorPerformance();
    }, 30000); // 30秒检查一次性能

    this.scanIntervals.set('performance_monitor', performanceMonitor);
  }

  /**
   * 监控性能
   */
  async monitorPerformance() {
    try {
      const usage = process.cpuUsage();
      const memUsage = process.memoryUsage();

      // 检查CPU使用率
      const cpuPercent = (usage.user + usage.system) / 1000000; // 转换为秒
      
      if (cpuPercent > this.performanceConfig.maxCpuUsage) {
        logger.warn(`⚠️ CPU使用率过高: ${cpuPercent.toFixed(2)}%，降低扫描频率`);
        
        // 动态调整扫描频率
        this.performanceConfig.scanInterval *= 1.5;
        this.performanceConfig.maxConcurrentScans = Math.max(1, this.performanceConfig.maxConcurrentScans - 1);
      }

      // 检查内存使用
      const memMB = memUsage.heapUsed / 1024 / 1024;
      if (memMB > 100) { // 超过100MB
        logger.warn(`⚠️ 内存使用过高: ${memMB.toFixed(2)}MB，触发垃圾回收`);
        
        if (global.gc) {
          global.gc();
        }
      }

    } catch (error) {
      logger.debug('性能监控失败:', error.message);
    }
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
          '/var/log/auth.log'
        ];
      case 'darwin': // macOS
        return [
          '/var/log/system.log',
          '/var/log/kernel.log'
        ];
      case 'win32':
        return []; // Windows事件日志需要特殊处理
      default:
        return [];
    }
  }

  /**
   * 检查是否是排除的目录
   */
  isExcludedDirectory(dirName) {
    return this.globalConfig.excludePatterns.some(pattern => 
      dirName.includes(pattern)
    );
  }

  /**
   * 节流控制
   */
  async throttle() {
    return new Promise(resolve => {
      setTimeout(resolve, this.performanceConfig.throttleDelay);
    });
  }

  /**
   * 停止全域数据采集
   */
  async stopGlobalCollection() {
    try {
      logger.info('🛑 停止全域数据采集...');

      // 停止项目日志监控
      for (const [projectName, watchers] of this.projectLogWatchers) {
        for (const watcher of watchers) {
          await watcher.close();
        }
      }
      this.projectLogWatchers.clear();

      // 停止系统日志监控
      for (const [name, watcher] of this.systemLogWatchers) {
        await watcher.close();
      }
      this.systemLogWatchers.clear();

      // 停止定期扫描
      for (const [name, interval] of this.scanIntervals) {
        clearInterval(interval);
      }
      this.scanIntervals.clear();

      this.isCollecting = false;
      logger.info('✅ 全域数据采集已停止');

      return {
        success: true,
        message: '全域数据采集已停止'
      };

    } catch (error) {
      logger.error('❌ 停止全域数据采集失败:', error);
      throw error;
    }
  }

  /**
   * 获取采集状态
   */
  getCollectionStatus() {
    return {
      isCollecting: this.isCollecting,
      monitoredProjects: Array.from(this.projectLogWatchers.keys()),
      systemLogWatchers: Array.from(this.systemLogWatchers.keys()),
      currentScans: this.currentScans,
      performanceConfig: this.performanceConfig,
      globalConfig: this.globalConfig,
      systemInfo: {
        platform: os.platform(),
        arch: os.arch(),
        totalMemory: os.totalmem(),
        freeMemory: os.freemem(),
        uptime: os.uptime()
      }
    };
  }
}

module.exports = GlobalDataCollector;