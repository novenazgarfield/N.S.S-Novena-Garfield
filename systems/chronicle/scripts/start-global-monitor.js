#!/usr/bin/env node

/**
 * 🌍 Chronicle全系统监控启动脚本
 * ===============================
 * 
 * 启动Chronicle全系统监控，覆盖：
 * - /workspace/systems下的所有项目
 * - 本机系统日志和资源监控
 * - 跨项目故障关联分析
 * 
 * Usage:
 *   node scripts/start-global-monitor.js [options]
 * 
 * Options:
 *   --api-only    只启动API服务器，不启动监控
 *   --monitor-only 只启动监控，不启动API服务器
 *   --port PORT   指定API服务器端口 (默认: 3000)
 *   --config FILE 指定配置文件路径
 * 
 * Author: N.S.S-Novena-Garfield Project
 * Version: 2.0.0 - "Global Federation"
 */

const path = require('path');
const fs = require('fs');
const { program } = require('commander');

// 设置项目根目录
const PROJECT_ROOT = path.resolve(__dirname, '..');
process.chdir(PROJECT_ROOT);

// 导入模块
const logger = require('../src/shared/logger');
const config = require('../src/shared/config');
const APIServer = require('../src/api/server');
const GlobalSystemMonitor = require('../src/system-monitor/global-monitor');

// 解析命令行参数
program
  .name('start-global-monitor')
  .description('启动Chronicle全系统监控')
  .option('--api-only', '只启动API服务器，不启动监控')
  .option('--monitor-only', '只启动监控，不启动API服务器')
  .option('--port <port>', '指定API服务器端口', '3000')
  .option('--config <file>', '指定配置文件路径')
  .option('--verbose', '详细日志输出')
  .option('--dry-run', '试运行模式，不实际启动服务')
  .parse();

const options = program.opts();

// 全局变量
let apiServer = null;
let globalMonitor = null;
let isShuttingDown = false;

/**
 * 主启动函数
 */
async function main() {
  try {
    logger.info('🌍 Chronicle全系统监控启动器');
    logger.info('=====================================');

    // 显示启动配置
    displayStartupConfig();

    if (options.dryRun) {
      logger.info('🧪 试运行模式 - 不会实际启动服务');
      await performDryRun();
      return;
    }

    // 初始化配置
    await initializeConfig();

    // 启动服务
    if (!options.monitorOnly) {
      await startAPIServer();
    }

    if (!options.apiOnly) {
      await startGlobalMonitoring();
    }

    // 设置优雅关闭
    setupGracefulShutdown();

    logger.info('✅ Chronicle全系统监控启动完成');
    logger.info('=====================================');

    // 显示访问信息
    displayAccessInfo();

  } catch (error) {
    logger.error('❌ 启动失败:', error);
    process.exit(1);
  }
}

/**
 * 显示启动配置
 */
function displayStartupConfig() {
  logger.info('📋 启动配置:');
  logger.info(`   API服务器: ${options.apiOnly ? '仅API' : options.monitorOnly ? '禁用' : '启用'}`);
  logger.info(`   全系统监控: ${options.monitorOnly ? '仅监控' : options.apiOnly ? '禁用' : '启用'}`);
  logger.info(`   端口: ${options.port}`);
  logger.info(`   配置文件: ${options.config || '默认'}`);
  logger.info(`   详细日志: ${options.verbose ? '启用' : '禁用'}`);
  logger.info(`   工作目录: ${PROJECT_ROOT}`);
  logger.info('');
}

/**
 * 执行试运行
 */
async function performDryRun() {
  logger.info('🔍 检查系统环境...');

  // 检查必需的目录
  const requiredDirs = [
    '/workspace/systems',
    path.join(PROJECT_ROOT, 'src'),
    path.join(PROJECT_ROOT, 'src/system-monitor'),
    path.join(PROJECT_ROOT, 'src/api')
  ];

  for (const dir of requiredDirs) {
    if (fs.existsSync(dir)) {
      logger.info(`   ✅ 目录存在: ${dir}`);
    } else {
      logger.warn(`   ❌ 目录缺失: ${dir}`);
    }
  }

  // 检查项目
  logger.info('🔍 扫描项目...');
  try {
    const systemsPath = '/workspace/systems';
    const entries = fs.readdirSync(systemsPath, { withFileTypes: true });
    const projects = entries.filter(entry => entry.isDirectory()).map(entry => entry.name);
    
    logger.info(`   发现 ${projects.length} 个项目:`);
    for (const project of projects) {
      logger.info(`   📁 ${project}`);
    }
  } catch (error) {
    logger.error('   ❌ 无法扫描项目目录:', error.message);
  }

  // 检查系统日志
  logger.info('🔍 检查系统日志...');
  const logPaths = [
    '/var/log/syslog',
    '/var/log/messages',
    '/var/log/kern.log'
  ];

  for (const logPath of logPaths) {
    if (fs.existsSync(logPath)) {
      logger.info(`   ✅ 日志文件: ${logPath}`);
    } else {
      logger.info(`   ⚠️  日志文件不存在: ${logPath}`);
    }
  }

  logger.info('✅ 试运行完成');
}

/**
 * 初始化配置
 */
async function initializeConfig() {
  logger.info('⚙️ 初始化配置...');

  // 加载自定义配置文件
  if (options.config) {
    if (fs.existsSync(options.config)) {
      logger.info(`   📄 加载配置文件: ${options.config}`);
      // 这里可以加载自定义配置
    } else {
      logger.warn(`   ⚠️  配置文件不存在: ${options.config}`);
    }
  }

  // 初始化默认配置
  config.init();

  // 设置详细日志
  if (options.verbose) {
    logger.level = 'debug';
  }

  logger.info('   ✅ 配置初始化完成');
}

/**
 * 启动API服务器
 */
async function startAPIServer() {
  logger.info('🚀 启动API服务器...');

  try {
    apiServer = new APIServer();
    await apiServer.init();
    await apiServer.start(parseInt(options.port));

    logger.info(`   ✅ API服务器启动成功 (端口: ${options.port})`);

  } catch (error) {
    logger.error('   ❌ API服务器启动失败:', error);
    throw error;
  }
}

/**
 * 启动全系统监控
 */
async function startGlobalMonitoring() {
  logger.info('🌍 启动全系统监控...');

  try {
    globalMonitor = new GlobalSystemMonitor();
    const result = await globalMonitor.startGlobalMonitoring();

    logger.info('   ✅ 全系统监控启动成功');
    logger.info(`   📊 监控项目数: ${result.monitored_projects.length}`);
    logger.info(`   🔍 系统监控器: ${result.system_monitors.length}`);

    // 显示监控的项目
    if (result.monitored_projects.length > 0) {
      logger.info('   📁 监控项目列表:');
      for (const project of result.monitored_projects) {
        logger.info(`      - ${project}`);
      }
    }

  } catch (error) {
    logger.error('   ❌ 全系统监控启动失败:', error);
    throw error;
  }
}

/**
 * 设置优雅关闭
 */
function setupGracefulShutdown() {
  const signals = ['SIGINT', 'SIGTERM', 'SIGQUIT'];

  for (const signal of signals) {
    process.on(signal, async () => {
      if (isShuttingDown) {
        logger.warn('强制退出...');
        process.exit(1);
      }

      isShuttingDown = true;
      logger.info(`\n🛑 收到 ${signal} 信号，开始优雅关闭...`);

      await gracefulShutdown();
    });
  }

  // 处理未捕获的异常
  process.on('uncaughtException', (error) => {
    logger.error('❌ 未捕获的异常:', error);
    gracefulShutdown().then(() => process.exit(1));
  });

  process.on('unhandledRejection', (reason, promise) => {
    logger.error('❌ 未处理的Promise拒绝:', reason);
    gracefulShutdown().then(() => process.exit(1));
  });
}

/**
 * 优雅关闭
 */
async function gracefulShutdown() {
  try {
    logger.info('🛑 开始关闭服务...');

    // 停止全系统监控
    if (globalMonitor) {
      logger.info('   🌍 停止全系统监控...');
      await globalMonitor.stopGlobalMonitoring();
      logger.info('   ✅ 全系统监控已停止');
    }

    // 停止API服务器
    if (apiServer) {
      logger.info('   🚀 停止API服务器...');
      await apiServer.stop();
      logger.info('   ✅ API服务器已停止');
    }

    logger.info('✅ 所有服务已优雅关闭');
    process.exit(0);

  } catch (error) {
    logger.error('❌ 关闭过程中出错:', error);
    process.exit(1);
  }
}

/**
 * 显示访问信息
 */
function displayAccessInfo() {
  if (!options.monitorOnly) {
    logger.info('🌐 API访问信息:');
    logger.info(`   健康检查: http://localhost:${options.port}/health`);
    logger.info(`   API信息: http://localhost:${options.port}/info`);
    logger.info(`   API文档: http://localhost:${options.port}/docs`);
    logger.info('');
    logger.info('🏥 Genesis中央医院API:');
    logger.info(`   故障记录: POST http://localhost:${options.port}/api/log_failure`);
    logger.info(`   治疗请求: POST http://localhost:${options.port}/api/request_healing`);
    logger.info(`   健康报告: GET http://localhost:${options.port}/api/health_report`);
    logger.info('');
    logger.info('🌍 全系统监控API:');
    logger.info(`   启动监控: POST http://localhost:${options.port}/api/global/start`);
    logger.info(`   监控状态: GET http://localhost:${options.port}/api/global/status`);
    logger.info(`   项目列表: GET http://localhost:${options.port}/api/global/projects`);
    logger.info(`   系统健康: GET http://localhost:${options.port}/api/global/system-health`);
    logger.info('');
  }

  if (!options.apiOnly) {
    logger.info('🔍 监控范围:');
    logger.info('   📁 项目监控: /workspace/systems/*');
    logger.info('   📋 系统日志: /var/log/*');
    logger.info('   📊 资源监控: CPU, 内存, 磁盘');
    logger.info('   🔗 跨项目分析: 故障关联分析');
    logger.info('');
  }

  logger.info('💡 使用提示:');
  logger.info('   - 按 Ctrl+C 优雅关闭服务');
  logger.info('   - 查看日志了解监控状态');
  logger.info('   - 使用API接口进行远程管理');
  logger.info('');
}

// 启动应用
if (require.main === module) {
  main().catch((error) => {
    logger.error('❌ 启动失败:', error);
    process.exit(1);
  });
}

module.exports = {
  startAPIServer,
  startGlobalMonitoring,
  gracefulShutdown
};