#!/usr/bin/env node

/**
 * 长离的学习胶囊 - 启动脚本
 * 用于启动完整的桌宠学习系统
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

class ChangleeStarter {
  constructor() {
    this.processes = [];
    this.isShuttingDown = false;
  }

  async start() {
    console.log('🐱 启动长离的学习胶囊...');
    console.log('=====================================');
    
    try {
      // 检查环境
      await this.checkEnvironment();
      
      // 安装依赖
      await this.installDependencies();
      
      // 启动后端服务
      await this.startBackend();
      
      // 等待后端启动
      await this.waitForBackend();
      
      // 启动Electron应用
      await this.startElectron();
      
      // 设置优雅关闭
      this.setupGracefulShutdown();
      
      console.log('✅ 长离的学习胶囊启动成功！');
      console.log('🎯 桌宠已出现在你的桌面上');
      console.log('📚 开始你的英语学习之旅吧！');
      
    } catch (error) {
      console.error('❌ 启动失败:', error.message);
      await this.cleanup();
      process.exit(1);
    }
  }

  async checkEnvironment() {
    console.log('🔍 检查运行环境...');
    
    // 检查Node.js版本
    const nodeVersion = process.version;
    const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
    
    if (majorVersion < 16) {
      throw new Error(`需要Node.js 16+，当前版本: ${nodeVersion}`);
    }
    
    // 检查操作系统
    const platform = os.platform();
    console.log(`📱 操作系统: ${platform}`);
    
    // 检查必要文件
    const requiredFiles = [
      'package.json',
      'src/main/main.js',
      'src/backend/server.js'
    ];
    
    for (const file of requiredFiles) {
      if (!fs.existsSync(path.join(__dirname, file))) {
        throw new Error(`缺少必要文件: ${file}`);
      }
    }
    
    console.log('✅ 环境检查通过');
  }

  async installDependencies() {
    console.log('📦 检查并安装依赖...');
    
    // 检查是否需要安装依赖
    if (!fs.existsSync(path.join(__dirname, 'node_modules'))) {
      console.log('🔄 安装主项目依赖...');
      await this.runCommand('npm', ['install'], __dirname);
    }
    
    // 检查渲染进程依赖
    const rendererPath = path.join(__dirname, 'src/renderer');
    if (fs.existsSync(path.join(rendererPath, 'package.json')) && 
        !fs.existsSync(path.join(rendererPath, 'node_modules'))) {
      console.log('🔄 安装渲染进程依赖...');
      await this.runCommand('npm', ['install'], rendererPath);
    }
    
    console.log('✅ 依赖安装完成');
  }

  async startBackend() {
    console.log('🚀 启动后端服务...');
    
    const backendProcess = spawn('node', ['src/backend/server.js'], {
      cwd: __dirname,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, NODE_ENV: 'production' }
    });
    
    this.processes.push({
      name: 'backend',
      process: backendProcess
    });
    
    // 监听后端输出
    backendProcess.stdout.on('data', (data) => {
      const message = data.toString().trim();
      if (message) {
        console.log(`[后端] ${message}`);
      }
    });
    
    backendProcess.stderr.on('data', (data) => {
      const message = data.toString().trim();
      if (message && !message.includes('ExperimentalWarning')) {
        console.error(`[后端错误] ${message}`);
      }
    });
    
    backendProcess.on('exit', (code) => {
      if (!this.isShuttingDown) {
        console.error(`❌ 后端服务异常退出，代码: ${code}`);
        this.cleanup();
      }
    });
  }

  async waitForBackend() {
    console.log('⏳ 等待后端服务启动...');
    
    const maxAttempts = 30;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      try {
        const response = await fetch('http://localhost:3001/health');
        if (response.ok) {
          console.log('✅ 后端服务已就绪');
          return;
        }
      } catch (error) {
        // 继续等待
      }
      
      attempts++;
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    throw new Error('后端服务启动超时');
  }

  async startElectron() {
    console.log('🖥️ 启动Electron应用...');
    
    const electronProcess = spawn('npx', ['electron', '.'], {
      cwd: __dirname,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, NODE_ENV: 'production' }
    });
    
    this.processes.push({
      name: 'electron',
      process: electronProcess
    });
    
    // 监听Electron输出
    electronProcess.stdout.on('data', (data) => {
      const message = data.toString().trim();
      if (message) {
        console.log(`[Electron] ${message}`);
      }
    });
    
    electronProcess.stderr.on('data', (data) => {
      const message = data.toString().trim();
      if (message && !message.includes('Electron Security Warning')) {
        console.error(`[Electron错误] ${message}`);
      }
    });
    
    electronProcess.on('exit', (code) => {
      if (!this.isShuttingDown) {
        console.log(`🚪 Electron应用已退出，代码: ${code}`);
        this.cleanup();
      }
    });
  }

  setupGracefulShutdown() {
    const signals = ['SIGINT', 'SIGTERM', 'SIGQUIT'];
    
    signals.forEach(signal => {
      process.on(signal, async () => {
        console.log(`\n📡 收到 ${signal} 信号，正在优雅关闭...`);
        await this.cleanup();
        process.exit(0);
      });
    });
    
    process.on('uncaughtException', async (error) => {
      console.error('❌ 未捕获的异常:', error);
      await this.cleanup();
      process.exit(1);
    });
    
    process.on('unhandledRejection', async (reason, promise) => {
      console.error('❌ 未处理的Promise拒绝:', reason);
      await this.cleanup();
      process.exit(1);
    });
  }

  async cleanup() {
    if (this.isShuttingDown) return;
    this.isShuttingDown = true;
    
    console.log('🧹 清理资源...');
    
    for (const { name, process } of this.processes) {
      try {
        console.log(`🛑 关闭 ${name}...`);
        process.kill('SIGTERM');
        
        // 等待进程关闭
        await new Promise((resolve) => {
          const timeout = setTimeout(() => {
            process.kill('SIGKILL');
            resolve();
          }, 5000);
          
          process.on('exit', () => {
            clearTimeout(timeout);
            resolve();
          });
        });
      } catch (error) {
        console.error(`关闭 ${name} 失败:`, error.message);
      }
    }
    
    console.log('✅ 清理完成');
  }

  runCommand(command, args, cwd) {
    return new Promise((resolve, reject) => {
      const process = spawn(command, args, {
        cwd,
        stdio: 'inherit',
        shell: true
      });
      
      process.on('exit', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`命令执行失败: ${command} ${args.join(' ')}`));
        }
      });
      
      process.on('error', reject);
    });
  }
}

// 主函数
async function main() {
  const starter = new ChangleeStarter();
  await starter.start();
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(error => {
    console.error('启动失败:', error);
    process.exit(1);
  });
}

module.exports = ChangleeStarter;