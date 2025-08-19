#!/usr/bin/env node

const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const { createModuleLogger } = require('../shared/logger');
const config = require('../shared/config');
const apiServer = require('../api/server');

const logger = createModuleLogger('daemon-service');

class DaemonService {
  constructor() {
    this.isRunning = false;
    this.pidFile = path.join(__dirname, '../../data/chronicle.pid');
    this.logFile = path.join(__dirname, '../../logs/daemon.log');
    this.restartCount = 0;
    this.maxRestarts = 5;
    this.restartDelay = 5000; // 5秒
  }

  /**
   * 启动守护进程
   */
  async start(options = {}) {
    try {
      // 检查是否已经在运行
      if (this.isAlreadyRunning()) {
        console.log('Service is already running');
        return false;
      }

      // 根据选项决定是否后台运行
      if (options.daemon !== false) {
        this.daemonize();
        return true;
      }

      // 前台运行
      await this.runService();
      return true;

    } catch (error) {
      logger.error('Failed to start daemon service', { error: error.message });
      console.error('Failed to start service:', error.message);
      return false;
    }
  }

  /**
   * 停止守护进程
   */
  async stop() {
    try {
      const pid = this.readPidFile();
      if (!pid) {
        console.log('Service is not running');
        return false;
      }

      // 发送终止信号
      process.kill(pid, 'SIGTERM');
      
      // 等待进程结束
      await this.waitForProcessEnd(pid);
      
      // 清理PID文件
      this.removePidFile();
      
      console.log('Service stopped successfully');
      return true;

    } catch (error) {
      if (error.code === 'ESRCH') {
        // 进程不存在，清理PID文件
        this.removePidFile();
        console.log('Service was not running (cleaned up stale PID file)');
        return true;
      }
      
      logger.error('Failed to stop daemon service', { error: error.message });
      console.error('Failed to stop service:', error.message);
      return false;
    }
  }

  /**
   * 重启守护进程
   */
  async restart() {
    console.log('Restarting service...');
    
    const stopped = await this.stop();
    if (stopped) {
      // 等待一下确保完全停止
      await new Promise(resolve => setTimeout(resolve, 2000));
      return await this.start();
    }
    
    return false;
  }

  /**
   * 获取服务状态
   */
  getStatus() {
    const pid = this.readPidFile();
    
    if (!pid) {
      return {
        status: 'stopped',
        pid: null,
        uptime: null,
        memory: null
      };
    }

    try {
      // 检查进程是否存在
      process.kill(pid, 0);
      
      // 获取进程信息
      const processInfo = this.getProcessInfo(pid);
      
      return {
        status: 'running',
        pid: pid,
        uptime: processInfo.uptime,
        memory: processInfo.memory,
        startTime: processInfo.startTime
      };
      
    } catch (error) {
      if (error.code === 'ESRCH') {
        // 进程不存在，清理PID文件
        this.removePidFile();
        return {
          status: 'stopped',
          pid: null,
          uptime: null,
          memory: null
        };
      }
      
      return {
        status: 'unknown',
        pid: pid,
        error: error.message
      };
    }
  }

  /**
   * 后台化进程
   */
  daemonize() {
    console.log('Starting service in daemon mode...');
    
    // 创建子进程
    const child = spawn(process.execPath, [__filename, '--no-daemon'], {
      detached: true,
      stdio: ['ignore', 'ignore', 'ignore']
    });

    // 分离子进程
    child.unref();
    
    console.log(`Service started with PID: ${child.pid}`);
    
    // 父进程退出
    process.exit(0);
  }

  /**
   * 运行服务
   */
  async runService() {
    try {
      // 写入PID文件
      this.writePidFile(process.pid);
      
      // 设置进程标题
      process.title = 'chronicle-daemon';
      
      // 设置信号处理
      this.setupSignalHandlers();
      
      // 设置自动重启
      this.setupAutoRestart();
      
      logger.info('Daemon service starting', { 
        pid: process.pid,
        version: '1.0.0'
      });

      // 启动API服务器
      await apiServer.start();
      
      this.isRunning = true;
      logger.info('Daemon service started successfully');
      
      // 保持进程运行
      this.keepAlive();

    } catch (error) {
      logger.error('Failed to run service', { error: error.message });
      this.cleanup();
      process.exit(1);
    }
  }

  /**
   * 设置信号处理
   */
  setupSignalHandlers() {
    // 优雅关闭
    process.on('SIGTERM', () => {
      logger.info('SIGTERM received, shutting down gracefully');
      this.gracefulShutdown();
    });

    process.on('SIGINT', () => {
      logger.info('SIGINT received, shutting down gracefully');
      this.gracefulShutdown();
    });

    // 重新加载配置
    process.on('SIGHUP', () => {
      logger.info('SIGHUP received, reloading configuration');
      this.reloadConfig();
    });

    // 处理未捕获的异常
    process.on('uncaughtException', (error) => {
      logger.error('Uncaught exception in daemon', { 
        error: error.message, 
        stack: error.stack 
      });
      this.handleCrash(error);
    });

    process.on('unhandledRejection', (reason, promise) => {
      logger.error('Unhandled promise rejection in daemon', { reason, promise });
      this.handleCrash(new Error(`Unhandled promise rejection: ${reason}`));
    });
  }

  /**
   * 设置自动重启
   */
  setupAutoRestart() {
    process.on('exit', (code) => {
      if (code !== 0 && this.restartCount < this.maxRestarts) {
        logger.warn('Process exited unexpectedly, attempting restart', { 
          code, 
          restartCount: this.restartCount 
        });
        
        setTimeout(() => {
          this.restartCount++;
          this.runService().catch(error => {
            logger.error('Failed to restart service', { error: error.message });
          });
        }, this.restartDelay);
      }
    });
  }

  /**
   * 处理崩溃
   */
  handleCrash(error) {
    logger.error('Service crashed', { error: error.message, stack: error.stack });
    
    if (this.restartCount < this.maxRestarts) {
      logger.info('Attempting to restart after crash', { restartCount: this.restartCount });
      this.restartCount++;
      
      setTimeout(() => {
        this.runService().catch(restartError => {
          logger.error('Failed to restart after crash', { error: restartError.message });
          process.exit(1);
        });
      }, this.restartDelay);
    } else {
      logger.error('Max restart attempts reached, giving up');
      this.cleanup();
      process.exit(1);
    }
  }

  /**
   * 优雅关闭
   */
  async gracefulShutdown() {
    if (!this.isRunning) {
      return;
    }

    this.isRunning = false;
    logger.info('Starting graceful shutdown');

    try {
      // 停止API服务器
      await apiServer.stop();
      
      // 清理资源
      this.cleanup();
      
      logger.info('Graceful shutdown completed');
      process.exit(0);

    } catch (error) {
      logger.error('Error during graceful shutdown', { error: error.message });
      process.exit(1);
    }
  }

  /**
   * 重新加载配置
   */
  reloadConfig() {
    try {
      // 重新加载配置文件
      delete require.cache[require.resolve('../shared/config')];
      const newConfig = require('../shared/config');
      
      logger.info('Configuration reloaded', { 
        server: newConfig.server,
        monitoring: newConfig.monitoring 
      });

    } catch (error) {
      logger.error('Failed to reload configuration', { error: error.message });
    }
  }

  /**
   * 保持进程运行
   */
  keepAlive() {
    // 定期检查服务健康状态
    const healthCheckInterval = setInterval(() => {
      if (!this.isRunning) {
        clearInterval(healthCheckInterval);
        return;
      }

      // 简单的健康检查
      const memoryUsage = process.memoryUsage();
      const uptime = process.uptime();

      logger.debug('Health check', { 
        uptime: Math.floor(uptime),
        memory: {
          rss: Math.floor(memoryUsage.rss / 1024 / 1024) + 'MB',
          heapUsed: Math.floor(memoryUsage.heapUsed / 1024 / 1024) + 'MB'
        }
      });

      // 检查内存使用是否过高
      const maxMemory = 500 * 1024 * 1024; // 500MB
      if (memoryUsage.rss > maxMemory) {
        logger.warn('High memory usage detected', { 
          current: Math.floor(memoryUsage.rss / 1024 / 1024) + 'MB',
          limit: Math.floor(maxMemory / 1024 / 1024) + 'MB'
        });
      }

    }, 60000); // 每分钟检查一次
  }

  /**
   * 检查是否已经在运行
   */
  isAlreadyRunning() {
    const pid = this.readPidFile();
    if (!pid) {
      return false;
    }

    try {
      process.kill(pid, 0);
      return true;
    } catch (error) {
      if (error.code === 'ESRCH') {
        // 进程不存在，清理PID文件
        this.removePidFile();
        return false;
      }
      throw error;
    }
  }

  /**
   * 读取PID文件
   */
  readPidFile() {
    try {
      if (fs.existsSync(this.pidFile)) {
        const pid = parseInt(fs.readFileSync(this.pidFile, 'utf8').trim());
        return isNaN(pid) ? null : pid;
      }
    } catch (error) {
      logger.warn('Failed to read PID file', { error: error.message });
    }
    return null;
  }

  /**
   * 写入PID文件
   */
  writePidFile(pid) {
    try {
      const pidDir = path.dirname(this.pidFile);
      if (!fs.existsSync(pidDir)) {
        fs.mkdirSync(pidDir, { recursive: true });
      }
      fs.writeFileSync(this.pidFile, pid.toString());
    } catch (error) {
      logger.error('Failed to write PID file', { error: error.message });
    }
  }

  /**
   * 删除PID文件
   */
  removePidFile() {
    try {
      if (fs.existsSync(this.pidFile)) {
        fs.unlinkSync(this.pidFile);
      }
    } catch (error) {
      logger.warn('Failed to remove PID file', { error: error.message });
    }
  }

  /**
   * 等待进程结束
   */
  async waitForProcessEnd(pid, timeout = 10000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      try {
        process.kill(pid, 0);
        await new Promise(resolve => setTimeout(resolve, 100));
      } catch (error) {
        if (error.code === 'ESRCH') {
          return; // 进程已结束
        }
        throw error;
      }
    }
    
    // 超时，强制终止
    try {
      process.kill(pid, 'SIGKILL');
    } catch (error) {
      // 忽略错误，可能进程已经结束
    }
  }

  /**
   * 获取进程信息
   */
  getProcessInfo(pid) {
    try {
      const stat = fs.readFileSync(`/proc/${pid}/stat`, 'utf8');
      const parts = stat.split(' ');
      
      // 启动时间（从系统启动开始的时钟滴答数）
      const starttime = parseInt(parts[21]);
      const clockTicks = require('os').constants.UV_CLOCK_TICKS || 100;
      const uptime = process.uptime();
      
      return {
        uptime: Math.floor(uptime),
        startTime: new Date(Date.now() - uptime * 1000).toISOString(),
        memory: this.getMemoryInfo(pid)
      };
    } catch (error) {
      // 如果无法读取/proc信息（非Linux系统），返回基本信息
      return {
        uptime: null,
        startTime: null,
        memory: null
      };
    }
  }

  /**
   * 获取内存信息
   */
  getMemoryInfo(pid) {
    try {
      const status = fs.readFileSync(`/proc/${pid}/status`, 'utf8');
      const lines = status.split('\n');
      
      const vmRSS = lines.find(line => line.startsWith('VmRSS:'));
      const vmSize = lines.find(line => line.startsWith('VmSize:'));
      
      return {
        rss: vmRSS ? vmRSS.split(/\s+/)[1] + ' kB' : null,
        size: vmSize ? vmSize.split(/\s+/)[1] + ' kB' : null
      };
    } catch (error) {
      return null;
    }
  }

  /**
   * 清理资源
   */
  cleanup() {
    this.removePidFile();
    logger.info('Cleanup completed');
  }
}

// 命令行接口
function main() {
  const daemon = new DaemonService();
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case 'start':
      daemon.start({ daemon: !args.includes('--no-daemon') })
        .then(success => {
          if (!success) {
            process.exit(1);
          }
        })
        .catch(error => {
          console.error('Failed to start:', error.message);
          process.exit(1);
        });
      break;

    case 'stop':
      daemon.stop()
        .then(success => {
          process.exit(success ? 0 : 1);
        })
        .catch(error => {
          console.error('Failed to stop:', error.message);
          process.exit(1);
        });
      break;

    case 'restart':
      daemon.restart()
        .then(success => {
          process.exit(success ? 0 : 1);
        })
        .catch(error => {
          console.error('Failed to restart:', error.message);
          process.exit(1);
        });
      break;

    case 'status':
      const status = daemon.getStatus();
      console.log('Service Status:', JSON.stringify(status, null, 2));
      process.exit(0);
      break;

    case '--no-daemon':
      // 内部使用，直接运行服务
      daemon.runService()
        .catch(error => {
          console.error('Service failed:', error.message);
          process.exit(1);
        });
      break;

    default:
      console.log(`
Chronicle Daemon Service

Usage: node service.js <command>

Commands:
  start     Start the daemon service
  stop      Stop the daemon service
  restart   Restart the daemon service
  status    Show service status

Options:
  --no-daemon   Run in foreground (for debugging)

Examples:
  node service.js start
  node service.js stop
  node service.js status
      `);
      process.exit(1);
  }
}

// 如果直接运行此文件
if (require.main === module) {
  main();
}

module.exports = DaemonService;