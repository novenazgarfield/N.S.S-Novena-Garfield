#!/usr/bin/env node

/**
 * Changlee系统统一入口点
 * 支持多种运行模式：web, desktop, dev, demo, rag, cli
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const http = require('http');
const express = require('express');
const open = require('open');

// 加载配置
const config = require('./changlee.config.js');

class ChangleeStarter {
  constructor() {
    this.processes = [];
    this.isShuttingDown = false;
    this.config = config.getEnvironmentConfig();
    
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
      // 验证配置
      const validation = this.config.validate();
      if (!validation.valid) {
        console.error('❌ 配置验证失败:');
        validation.errors.forEach(error => console.error(`   ${error}`));
        process.exit(1);
      }

      console.log(`🎵 ${this.config.system.name} v${this.config.system.version}`);
      console.log('=====================================');
      console.log(`📍 运行模式: ${mode}`);
      console.log(`🌍 环境: ${this.config.environment}`);
      console.log('');

      // 确保必要目录存在
      this.ensureDirectories();

      // 根据模式启动相应服务
      switch (mode) {
        case 'web':
          await this.startWebMode(options);
          break;
        case 'desktop':
          await this.startDesktopMode(options);
          break;
        case 'dev':
          await this.startDevMode(options);
          break;
        case 'demo':
          await this.startDemoMode(options);
          break;
        case 'rag':
          await this.startRagMode(options);
          break;
        case 'cli':
          await this.startCliMode(options);
          break;
        case 'status':
          await this.showStatus();
          break;
        default:
          this.showHelp();
          process.exit(1);
      }

    } catch (error) {
      console.error('❌ 启动失败:', error.message);
      if (this.config.system.debug) {
        console.error(error.stack);
      }
      process.exit(1);
    }
  }

  /**
   * Web模式启动
   */
  async startWebMode(options) {
    console.log('🌐 启动Web模式...');
    
    // 启动后端服务
    await this.startBackendServer();
    
    // 启动Web服务器
    await this.startWebServer();
    
    // 自动打开浏览器
    if (!options.noBrowser) {
      const url = `http://${this.config.servers.web.host}:${this.config.servers.web.port}`;
      console.log(`🚀 正在打开浏览器: ${url}`);
      await open(url);
    }
    
    console.log('✅ Web模式启动完成');
    this.keepAlive();
  }

  /**
   * 桌面模式启动
   */
  async startDesktopMode(options) {
    console.log('🖥️ 启动桌面模式...');
    
    // 启动后端服务
    await this.startBackendServer();
    
    // 启动Electron应用
    await this.startElectronApp();
    
    console.log('✅ 桌面模式启动完成');
    this.keepAlive();
  }

  /**
   * 开发模式启动
   */
  async startDevMode(options) {
    console.log('🔧 启动开发模式...');
    
    // 设置开发环境
    process.env.NODE_ENV = 'development';
    process.env.ELECTRON_IS_DEV = '1';
    
    // 启动后端服务
    await this.startBackendServer();
    
    // 启动Web服务器
    await this.startWebServer();
    
    // 启动Electron应用（开发模式）
    await this.startElectronApp(true);
    
    console.log('✅ 开发模式启动完成');
    console.log('🔥 热重载已启用');
    this.keepAlive();
  }

  /**
   * 演示模式启动
   */
  async startDemoMode(options) {
    console.log('🎭 启动演示模式...');
    
    try {
      // 使用原有的demo.js
      const demoPath = path.join(__dirname, 'demo.js');
      if (fs.existsSync(demoPath)) {
        const demoProcess = spawn('node', [demoPath], {
          stdio: 'inherit',
          cwd: __dirname
        });
        
        this.processes.push(demoProcess);
        
        demoProcess.on('exit', (code) => {
          console.log(`演示模式退出，代码: ${code}`);
          process.exit(code);
        });
      } else {
        console.error('❌ 找不到演示脚本');
        process.exit(1);
      }
    } catch (error) {
      console.error('❌ 演示模式启动失败:', error.message);
      process.exit(1);
    }
  }

  /**
   * RAG集成模式启动
   */
  async startRagMode(options) {
    console.log('🤖 启动RAG集成模式...');
    
    // 检查RAG系统是否可用
    if (!this.config.rag.enabled) {
      console.log('⚠️ RAG系统未启用，正在启用...');
      this.config.rag.enabled = true;
    }
    
    try {
      // 使用原有的start_with_rag.js
      const ragStartPath = path.join(__dirname, 'start_with_rag.js');
      if (fs.existsSync(ragStartPath)) {
        const ragProcess = spawn('node', [ragStartPath], {
          stdio: 'inherit',
          cwd: __dirname,
          env: { ...process.env, RAG_ENABLED: 'true' }
        });
        
        this.processes.push(ragProcess);
        
        ragProcess.on('exit', (code) => {
          console.log(`RAG模式退出，代码: ${code}`);
          process.exit(code);
        });
      } else {
        console.error('❌ 找不到RAG启动脚本');
        process.exit(1);
      }
    } catch (error) {
      console.error('❌ RAG模式启动失败:', error.message);
      process.exit(1);
    }
  }

  /**
   * 命令行模式启动
   */
  async startCliMode(options) {
    console.log('💻 启动命令行模式...');
    
    // 简单的CLI交互
    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    console.log('');
    console.log('🎯 Changlee CLI 模式');
    console.log('输入 "help" 查看命令，"exit" 退出');
    console.log('');

    const askQuestion = () => {
      rl.question('changlee> ', (input) => {
        const command = input.trim().toLowerCase();
        
        switch (command) {
          case 'help':
            console.log('可用命令:');
            console.log('  status  - 显示系统状态');
            console.log('  config  - 显示配置信息');
            console.log('  test    - 运行测试');
            console.log('  exit    - 退出');
            break;
          
          case 'status':
            this.showStatus();
            break;
          
          case 'config':
            console.log('当前配置:');
            console.log(JSON.stringify(this.config, null, 2));
            break;
          
          case 'test':
            console.log('运行系统测试...');
            this.runTests();
            break;
          
          case 'exit':
            console.log('👋 再见！');
            rl.close();
            return;
          
          default:
            if (command) {
              console.log(`未知命令: ${command}`);
            }
        }
        
        askQuestion();
      });
    };

    askQuestion();
  }

  /**
   * 启动后端服务器
   */
  async startBackendServer() {
    return new Promise((resolve, reject) => {
      const backendPath = path.join(__dirname, 'src/backend/server.js');
      
      if (!fs.existsSync(backendPath)) {
        console.log('⚠️ 后端服务器文件不存在，跳过启动');
        resolve();
        return;
      }

      console.log(`🔧 启动后端服务器 (端口: ${this.config.servers.backend.port})...`);
      
      const backendProcess = spawn('node', [backendPath], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: __dirname,
        env: {
          ...process.env,
          PORT: this.config.servers.backend.port,
          HOST: this.config.servers.backend.host
        }
      });

      this.processes.push(backendProcess);

      backendProcess.stdout.on('data', (data) => {
        if (this.config.development.logRequests) {
          console.log(`[Backend] ${data.toString().trim()}`);
        }
      });

      backendProcess.stderr.on('data', (data) => {
        console.error(`[Backend Error] ${data.toString().trim()}`);
      });

      backendProcess.on('error', (error) => {
        console.error('❌ 后端服务器启动失败:', error.message);
        reject(error);
      });

      // 等待服务器启动
      setTimeout(() => {
        this.checkServerHealth(this.config.servers.backend.port)
          .then(() => {
            console.log('✅ 后端服务器启动成功');
            resolve();
          })
          .catch(() => {
            console.log('⚠️ 后端服务器可能未完全启动，继续执行...');
            resolve();
          });
      }, 2000);
    });
  }

  /**
   * 启动Web服务器
   */
  async startWebServer() {
    return new Promise((resolve) => {
      const app = express();
      
      // 静态文件服务
      app.use(express.static(this.config.servers.web.staticPath));
      
      // 健康检查
      app.get('/health', (req, res) => {
        res.json({ status: 'ok', timestamp: new Date().toISOString() });
      });

      const server = app.listen(this.config.servers.web.port, this.config.servers.web.host, () => {
        console.log(`✅ Web服务器启动成功: http://${this.config.servers.web.host}:${this.config.servers.web.port}`);
        resolve();
      });

      this.processes.push({ kill: () => server.close() });
    });
  }

  /**
   * 启动Electron应用
   */
  async startElectronApp(devMode = false) {
    return new Promise((resolve, reject) => {
      console.log('🖥️ 启动Electron应用...');
      
      const electronArgs = ['.'];
      if (devMode) {
        electronArgs.unshift('--inspect=9229');
      }

      const electronProcess = spawn('npx', ['electron', ...electronArgs], {
        stdio: 'inherit',
        cwd: __dirname,
        env: {
          ...process.env,
          ELECTRON_IS_DEV: devMode ? '1' : '0'
        }
      });

      this.processes.push(electronProcess);

      electronProcess.on('error', (error) => {
        console.error('❌ Electron启动失败:', error.message);
        reject(error);
      });

      electronProcess.on('exit', (code) => {
        console.log(`Electron应用退出，代码: ${code}`);
        if (!this.isShuttingDown) {
          process.exit(code);
        }
      });

      // Electron启动需要时间
      setTimeout(() => {
        console.log('✅ Electron应用启动完成');
        resolve();
      }, 3000);
    });
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
   * 显示系统状态
   */
  async showStatus() {
    console.log('📊 系统状态:');
    console.log(`   名称: ${this.config.system.name}`);
    console.log(`   版本: ${this.config.system.version}`);
    console.log(`   环境: ${this.config.environment}`);
    console.log(`   调试模式: ${this.config.system.debug ? '开启' : '关闭'}`);
    console.log('');
    
    console.log('🌐 服务器配置:');
    console.log(`   Web端口: ${this.config.servers.web.port}`);
    console.log(`   后端端口: ${this.config.servers.backend.port}`);
    console.log('');
    
    console.log('🤖 AI配置:');
    console.log(`   提供商: ${this.config.ai.provider}`);
    console.log(`   模型: ${this.config.ai.model}`);
    console.log(`   本地AI: ${this.config.ai.local.enabled ? '启用' : '禁用'}`);
    console.log('');
    
    console.log('🔗 集成状态:');
    console.log(`   RAG系统: ${this.config.rag.enabled ? '启用' : '禁用'}`);
    console.log(`   Chronicle: ${this.config.chronicle.enabled ? '启用' : '禁用'}`);
  }

  /**
   * 运行测试
   */
  async runTests() {
    console.log('🧪 运行系统测试...');
    
    const testFiles = [
      'test_system.js',
      'test_rag_integration.js',
      'test_chronicle_integration.js',
      'test_music_module.js'
    ];

    for (const testFile of testFiles) {
      const testPath = path.join(__dirname, testFile);
      if (fs.existsSync(testPath)) {
        console.log(`   运行: ${testFile}`);
        try {
          const testProcess = spawn('node', [testPath], {
            stdio: 'pipe',
            cwd: __dirname
          });

          await new Promise((resolve) => {
            testProcess.on('exit', (code) => {
              console.log(`   ${testFile}: ${code === 0 ? '✅ 通过' : '❌ 失败'}`);
              resolve();
            });
          });
        } catch (error) {
          console.log(`   ${testFile}: ❌ 错误 - ${error.message}`);
        }
      }
    }
    
    console.log('🧪 测试完成');
  }

  /**
   * 确保必要目录存在
   */
  ensureDirectories() {
    const dirs = [
      this.config.paths.logs,
      this.config.paths.temp,
      this.config.paths.database
    ];

    dirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
  }

  /**
   * 保持进程运行
   */
  keepAlive() {
    console.log('');
    console.log('🎵 Changlee正在运行...');
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
🎵 ${this.config.system.name} v${this.config.system.version}

用法: node changlee.js [模式] [选项]

运行模式:
  web       - Web界面模式 (默认)
  desktop   - 桌面应用模式
  dev       - 开发模式 (Web + Desktop)
  demo      - 演示模式
  rag       - RAG集成模式
  cli       - 命令行交互模式
  status    - 显示系统状态

选项:
  --no-browser    - Web模式下不自动打开浏览器
  --port <port>   - 指定Web服务器端口
  --debug         - 启用调试模式
  --help          - 显示此帮助信息

示例:
  node changlee.js web
  node changlee.js desktop
  node changlee.js dev --debug
  node changlee.js rag
  node changlee.js status

环境变量:
  NODE_ENV        - 运行环境 (development/production)
  WEB_PORT        - Web服务器端口
  BACKEND_PORT    - 后端服务器端口
  DEBUG           - 调试模式
  RAG_ENABLED     - 启用RAG系统
    `);
  }

  /**
   * 优雅关闭
   */
  async shutdown() {
    if (this.isShuttingDown) return;
    
    this.isShuttingDown = true;
    console.log('\n🛑 正在关闭Changlee系统...');

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
    
    console.log('👋 Changlee系统已关闭');
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
  const mode = args[0] || 'web';
  const options = {};

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    
    switch (arg) {
      case '--no-browser':
        options.noBrowser = true;
        break;
      case '--port':
        options.port = parseInt(args[++i]);
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
    const starter = new ChangleeStarter();
    starter.showHelp();
    return;
  }

  const starter = new ChangleeStarter();
  await starter.start(mode, options);
}

// 运行主函数
if (require.main === module) {
  main().catch(error => {
    console.error('❌ 启动失败:', error.message);
    process.exit(1);
  });
}

module.exports = ChangleeStarter;