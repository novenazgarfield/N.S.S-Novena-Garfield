#!/usr/bin/env node

/**
 * Chronicle系统统一入口点
 * AI-Driven Automated Experiment Recorder
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const http = require('http');

// 加载配置
const config = require('./src/shared/config.js');
const logger = require('./src/shared/logger.js');

class ChronicleStarter {
  constructor() {
    this.processes = [];
    this.isShuttingDown = false;
    
    // 绑定退出处理
    process.on('SIGINT', () => this.shutdown());
    process.on('SIGTERM', () => this.shutdown());
    process.on('exit', () => this.cleanup());
  }

  /**
   * 主启动函数
   */
  async start(mode, options = {}) {
    try {
      console.log('📚 Chronicle - AI-Driven Experiment Recorder');
      console.log('===============================================');
      console.log(`📍 运行模式: ${mode}`);
      console.log(`🌍 环境: ${config.server.env}`);
      console.log('');

      // 验证配置
      this.validateConfig();

      // 确保必要目录存在
      this.ensureDirectories();

      // 根据模式启动相应服务
      switch (mode) {
        case 'server':
          await this.startServerMode(options);
          break;
        case 'daemon':
          await this.startDaemonMode(options);
          break;
        case 'dev':
          await this.startDevMode(options);
          break;
        case 'setup':
          await this.runSetup(options);
          break;
        case 'status':
          await this.showStatus();
          break;
        case 'test':
          await this.runTests(options);
          break;
        case 'install-service':
          await this.installService(options);
          break;
        default:
          this.showHelp();
          process.exit(1);
      }

    } catch (error) {
      console.error('❌ 启动失败:', error.message);
      if (options.debug) {
        console.error(error.stack);
      }
      process.exit(1);
    }
  }

  /**
   * API服务器模式
   */
  async startServerMode(options) {
    console.log('🌐 启动API服务器模式...');
    
    const serverPath = path.join(__dirname, 'src/api/server.js');
    
    if (!fs.existsSync(serverPath)) {
      throw new Error('API服务器文件不存在');
    }

    console.log(`🚀 启动API服务器 (端口: ${config.server.port})...`);
    
    const serverProcess = spawn('node', [serverPath], {
      stdio: 'inherit',
      cwd: __dirname,
      env: {
        ...process.env,
        PORT: options.port || config.server.port,
        HOST: options.host || config.server.host,
        NODE_ENV: options.env || config.server.env
      }
    });

    this.processes.push(serverProcess);

    serverProcess.on('error', (error) => {
      console.error('❌ API服务器启动失败:', error.message);
      process.exit(1);
    });

    serverProcess.on('exit', (code) => {
      console.log(`API服务器退出，代码: ${code}`);
      if (!this.isShuttingDown) {
        process.exit(code);
      }
    });

    // 等待服务器启动
    await this.waitForServer(config.server.port);
    console.log('✅ API服务器启动成功');
    
    this.keepAlive();
  }

  /**
   * 后台守护进程模式
   */
  async startDaemonMode(options) {
    console.log('🔧 启动后台守护进程模式...');
    
    const daemonPath = path.join(__dirname, 'src/daemon/service.js');
    
    if (!fs.existsSync(daemonPath)) {
      throw new Error('守护进程文件不存在');
    }

    console.log('🤖 启动后台监控服务...');
    
    const daemonProcess = spawn('node', [daemonPath], {
      stdio: options.detach ? 'ignore' : 'inherit',
      cwd: __dirname,
      detached: options.detach || false,
      env: {
        ...process.env,
        NODE_ENV: options.env || config.server.env
      }
    });

    if (options.detach) {
      daemonProcess.unref();
      console.log(`✅ 后台守护进程已启动 (PID: ${daemonProcess.pid})`);
      console.log('使用 "chronicle.js status" 查看状态');
      process.exit(0);
    } else {
      this.processes.push(daemonProcess);

      daemonProcess.on('error', (error) => {
        console.error('❌ 守护进程启动失败:', error.message);
        process.exit(1);
      });

      daemonProcess.on('exit', (code) => {
        console.log(`守护进程退出，代码: ${code}`);
        if (!this.isShuttingDown) {
          process.exit(code);
        }
      });

      console.log('✅ 后台守护进程启动成功');
      this.keepAlive();
    }
  }

  /**
   * 开发模式
   */
  async startDevMode(options) {
    console.log('🔧 启动开发模式...');
    
    // 设置开发环境
    process.env.NODE_ENV = 'development';
    
    // 启动API服务器 (使用nodemon)
    const serverPath = path.join(__dirname, 'src/api/server.js');
    
    console.log('🚀 启动API服务器 (开发模式)...');
    
    const serverProcess = spawn('npx', ['nodemon', serverPath], {
      stdio: 'inherit',
      cwd: __dirname,
      env: {
        ...process.env,
        PORT: options.port || config.server.port,
        HOST: options.host || config.server.host,
        NODE_ENV: 'development'
      }
    });

    this.processes.push(serverProcess);

    serverProcess.on('error', (error) => {
      console.error('❌ 开发服务器启动失败:', error.message);
      process.exit(1);
    });

    // 同时启动守护进程 (如果需要)
    if (options.daemon) {
      setTimeout(() => {
        this.startDaemonMode({ env: 'development' });
      }, 3000);
    }

    console.log('✅ 开发模式启动成功');
    console.log('🔥 热重载已启用');
    this.keepAlive();
  }

  /**
   * 运行设置
   */
  async runSetup(options) {
    console.log('⚙️ 运行系统设置...');
    
    const setupPath = path.join(__dirname, 'scripts/setup.js');
    
    if (!fs.existsSync(setupPath)) {
      console.log('⚠️ 设置脚本不存在，跳过设置');
      return;
    }

    const setupProcess = spawn('node', [setupPath], {
      stdio: 'inherit',
      cwd: __dirname
    });

    return new Promise((resolve, reject) => {
      setupProcess.on('exit', (code) => {
        if (code === 0) {
          console.log('✅ 系统设置完成');
          resolve();
        } else {
          console.error('❌ 系统设置失败');
          reject(new Error(`设置脚本退出码: ${code}`));
        }
      });

      setupProcess.on('error', (error) => {
        console.error('❌ 设置脚本执行失败:', error.message);
        reject(error);
      });
    });
  }

  /**
   * 显示系统状态
   */
  async showStatus() {
    console.log('📊 Chronicle系统状态:');
    console.log(`   版本: ${require('./package.json').version}`);
    console.log(`   环境: ${config.server.env}`);
    console.log(`   API端口: ${config.server.port}`);
    console.log('');
    
    // 检查API服务器状态
    try {
      await this.checkServerHealth(config.server.port);
      console.log('🌐 API服务器: ✅ 运行中');
    } catch (error) {
      console.log('🌐 API服务器: ❌ 未运行');
    }
    
    // 检查数据库状态
    try {
      const dbPath = config.database.path;
      if (fs.existsSync(dbPath)) {
        const stats = fs.statSync(dbPath);
        console.log(`💾 数据库: ✅ 正常 (${(stats.size / 1024).toFixed(1)}KB)`);
      } else {
        console.log('💾 数据库: ⚠️ 未初始化');
      }
    } catch (error) {
      console.log('💾 数据库: ❌ 错误');
    }
    
    // 检查AI配置
    if (config.ai.apiKey) {
      console.log(`🤖 AI服务: ✅ 已配置 (${config.ai.provider})`);
    } else {
      console.log('🤖 AI服务: ⚠️ 未配置API密钥');
    }
    
    // 检查监控配置
    console.log('');
    console.log('📡 监控配置:');
    console.log(`   文件系统监控: ${config.monitoring.fileSystem.enabled ? '✅ 启用' : '❌ 禁用'}`);
    console.log(`   窗口监控: ${config.monitoring.window.enabled ? '✅ 启用' : '❌ 禁用'}`);
    console.log(`   命令监控: ${config.monitoring.command.enabled ? '✅ 启用' : '❌ 禁用'}`);
  }

  /**
   * 运行测试
   */
  async runTests(options) {
    console.log('🧪 运行系统测试...');
    
    const testArgs = ['test'];
    if (options.watch) {
      testArgs.push('--watch');
    }
    if (options.coverage) {
      testArgs.push('--coverage');
    }

    const testProcess = spawn('npm', testArgs, {
      stdio: 'inherit',
      cwd: __dirname
    });

    return new Promise((resolve, reject) => {
      testProcess.on('exit', (code) => {
        if (code === 0) {
          console.log('✅ 测试完成');
          resolve();
        } else {
          console.error('❌ 测试失败');
          reject(new Error(`测试退出码: ${code}`));
        }
      });

      testProcess.on('error', (error) => {
        console.error('❌ 测试执行失败:', error.message);
        reject(error);
      });
    });
  }

  /**
   * 安装系统服务
   */
  async installService(options) {
    console.log('📦 安装系统服务...');
    
    const installPath = path.join(__dirname, 'scripts/install-service.js');
    
    if (!fs.existsSync(installPath)) {
      console.log('⚠️ 服务安装脚本不存在');
      return;
    }

    const installProcess = spawn('node', [installPath], {
      stdio: 'inherit',
      cwd: __dirname
    });

    return new Promise((resolve, reject) => {
      installProcess.on('exit', (code) => {
        if (code === 0) {
          console.log('✅ 系统服务安装完成');
          resolve();
        } else {
          console.error('❌ 系统服务安装失败');
          reject(new Error(`安装脚本退出码: ${code}`));
        }
      });

      installProcess.on('error', (error) => {
        console.error('❌ 安装脚本执行失败:', error.message);
        reject(error);
      });
    });
  }

  /**
   * 验证配置
   */
  validateConfig() {
    const errors = [];
    
    // 检查必需的配置
    if (!config.server.port || config.server.port < 1 || config.server.port > 65535) {
      errors.push('服务器端口必须在1-65535之间');
    }
    
    if (config.ai.enabled && !config.ai.apiKey) {
      errors.push('启用AI服务时必须提供API密钥');
    }
    
    if (!fs.existsSync(path.dirname(config.database.path))) {
      try {
        fs.mkdirSync(path.dirname(config.database.path), { recursive: true });
      } catch (error) {
        errors.push(`无法创建数据库目录: ${error.message}`);
      }
    }
    
    if (errors.length > 0) {
      console.error('❌ 配置验证失败:');
      errors.forEach(error => console.error(`   ${error}`));
      process.exit(1);
    }
  }

  /**
   * 确保必要目录存在
   */
  ensureDirectories() {
    const dirs = [
      path.dirname(config.database.path),
      path.join(__dirname, 'logs'),
      path.join(__dirname, 'data'),
      path.join(__dirname, 'temp')
    ];

    dirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
  }

  /**
   * 等待服务器启动
   */
  async waitForServer(port, timeout = 30000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      try {
        await this.checkServerHealth(port);
        return;
      } catch (error) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    throw new Error('服务器启动超时');
  }

  /**
   * 检查服务器健康状态
   */
  async checkServerHealth(port) {
    return new Promise((resolve, reject) => {
      const req = http.get(`http://localhost:${port}/health`, (res) => {
        if (res.statusCode === 200) {
          resolve();
        } else {
          reject(new Error(`服务器返回状态码: ${res.statusCode}`));
        }
      });

      req.on('error', reject);
      req.setTimeout(5000, () => {
        req.destroy();
        reject(new Error('健康检查超时'));
      });
    });
  }

  /**
   * 保持进程运行
   */
  keepAlive() {
    console.log('');
    console.log('📚 Chronicle正在运行...');
    console.log('按 Ctrl+C 退出');
    
    // 保持进程运行
    setInterval(() => {
      // 心跳检查
    }, 30000);
  }

  /**
   * 显示帮助信息
   */
  showHelp() {
    console.log(`
📚 Chronicle - AI-Driven Experiment Recorder v${require('./package.json').version}

用法: node chronicle.js [模式] [选项]

运行模式:
  server            - 启动API服务器
  daemon            - 启动后台守护进程
  dev               - 开发模式 (热重载)
  setup             - 运行系统设置
  status            - 显示系统状态
  test              - 运行测试
  install-service   - 安装系统服务

选项:
  --port <port>     - 指定服务器端口
  --host <host>     - 指定服务器主机
  --env <env>       - 指定运行环境
  --detach          - 后台运行 (仅daemon模式)
  --daemon          - 同时启动守护进程 (仅dev模式)
  --watch           - 监视模式 (仅test模式)
  --coverage        - 生成覆盖率报告 (仅test模式)
  --debug           - 启用调试模式
  --help            - 显示此帮助信息

示例:
  node chronicle.js server
  node chronicle.js daemon --detach
  node chronicle.js dev --daemon
  node chronicle.js test --watch
  node chronicle.js status

环境变量:
  PORT              - 服务器端口
  HOST              - 服务器主机
  NODE_ENV          - 运行环境
  AI_API_KEY        - AI服务API密钥
  DB_PATH           - 数据库路径
    `);
  }

  /**
   * 优雅关闭
   */
  async shutdown() {
    if (this.isShuttingDown) return;
    
    this.isShuttingDown = true;
    console.log('\n🛑 正在关闭Chronicle系统...');

    // 关闭所有子进程
    for (const process of this.processes) {
      try {
        if (process.kill) {
          process.kill('SIGTERM');
        } else if (process.pid) {
          process.kill('SIGTERM');
        }
      } catch (error) {
        console.error('关闭进程时出错:', error.message);
      }
    }

    // 等待进程关闭
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    console.log('👋 Chronicle系统已关闭');
    process.exit(0);
  }

  /**
   * 清理资源
   */
  cleanup() {
    // 清理临时文件等
  }
}

// 命令行参数解析
function parseArgs() {
  const args = process.argv.slice(2);
  const mode = args[0] || 'server';
  const options = {};

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    
    switch (arg) {
      case '--port':
        options.port = parseInt(args[++i]);
        break;
      case '--host':
        options.host = args[++i];
        break;
      case '--env':
        options.env = args[++i];
        break;
      case '--detach':
        options.detach = true;
        break;
      case '--daemon':
        options.daemon = true;
        break;
      case '--watch':
        options.watch = true;
        break;
      case '--coverage':
        options.coverage = true;
        break;
      case '--debug':
        options.debug = true;
        process.env.DEBUG = 'true';
        break;
      case '--help':
        return { mode: 'help' };
    }
  }

  return { mode, options };
}

// 主函数
async function main() {
  const { mode, options } = parseArgs();
  
  if (mode === 'help') {
    const starter = new ChronicleStarter();
    starter.showHelp();
    return;
  }

  const starter = new ChronicleStarter();
  await starter.start(mode, options);
}

// 运行主函数
if (require.main === module) {
  main().catch(error => {
    console.error('❌ 启动失败:', error.message);
    process.exit(1);
  });
}

module.exports = ChronicleStarter;