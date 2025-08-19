#!/usr/bin/env node

/**
 * 长离的学习胶囊 + RAG系统 集成启动脚本
 * 同时启动RAG系统和桌宠学习系统
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const axios = require('axios');

class IntegratedStarter {
  constructor() {
    this.processes = [];
    this.isShuttingDown = false;
    this.ragSystemPath = path.resolve(__dirname, '../../rag_system');
    this.petSystemPath = path.resolve(__dirname);
  }

  async start() {
    console.log('🚀 启动长离的学习胶囊 + RAG智能系统');
    console.log('================================================');
    
    try {
      // 检查系统环境
      await this.checkEnvironment();
      
      // 启动RAG系统
      await this.startRAGSystem();
      
      // 等待RAG系统启动完成
      await this.waitForRAGSystem();
      
      // 启动桌宠系统后端
      await this.startPetBackend();
      
      // 等待桌宠后端启动
      await this.waitForPetBackend();
      
      // 启动Electron应用
      await this.startElectronApp();
      
      // 设置优雅关闭
      this.setupGracefulShutdown();
      
      console.log('✅ 集成系统启动成功！');
      console.log('🎯 功能说明:');
      console.log('  • 桌宠长离: 可拖拽的桌面宠物');
      console.log('  • 智能问答: 基于RAG的问答系统');
      console.log('  • 文档分析: 上传文档提取单词');
      console.log('  • 学习胶囊: AI生成学习内容');
      console.log('  • 魔法沙滩: 游戏化拼写练习');
      console.log('');
      console.log('🌐 访问地址:');
      console.log('  • RAG系统: http://localhost:51658');
      console.log('  • 桌宠后端: http://localhost:3001');
      console.log('  • Electron应用: 桌面应用');
      
    } catch (error) {
      console.error('❌ 启动失败:', error.message);
      await this.cleanup();
      process.exit(1);
    }
  }

  async checkEnvironment() {
    console.log('🔍 检查系统环境...');
    
    // 检查RAG系统是否存在
    if (!fs.existsSync(this.ragSystemPath)) {
      throw new Error(`RAG系统路径不存在: ${this.ragSystemPath}`);
    }
    
    // 检查桌宠系统文件
    const requiredFiles = [
      'src/backend/server.js',
      'src/main/main.js',
      'package.json'
    ];
    
    for (const file of requiredFiles) {
      if (!fs.existsSync(path.join(this.petSystemPath, file))) {
        throw new Error(`缺少必要文件: ${file}`);
      }
    }
    
    console.log('✅ 环境检查通过');
  }

  async startRAGSystem() {
    console.log('🧠 启动RAG智能系统...');
    
    const ragProcess = spawn('python', ['-m', 'streamlit', 'run', 'universal_app.py', '--server.port=51658'], {
      cwd: this.ragSystemPath,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { 
        ...process.env, 
        PYTHONPATH: this.ragSystemPath,
        STREAMLIT_SERVER_HEADLESS: 'true'
      }
    });
    
    this.processes.push({
      name: 'RAG系统',
      process: ragProcess,
      type: 'rag'
    });
    
    // 监听RAG系统输出
    ragProcess.stdout.on('data', (data) => {
      const message = data.toString().trim();
      if (message && !message.includes('You can now view your Streamlit app')) {
        console.log(`[RAG] ${message}`);
      }
    });
    
    ragProcess.stderr.on('data', (data) => {
      const message = data.toString().trim();
      if (message && !message.includes('WARNING')) {
        console.error(`[RAG错误] ${message}`);
      }
    });
    
    ragProcess.on('exit', (code) => {
      if (!this.isShuttingDown) {
        console.error(`❌ RAG系统异常退出，代码: ${code}`);
        this.cleanup();
      }
    });
  }

  async waitForRAGSystem() {
    console.log('⏳ 等待RAG系统启动...');
    
    const maxAttempts = 60; // 最多等待60秒
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      try {
        const response = await axios.get('http://localhost:51658', { timeout: 2000 });
        if (response.status === 200) {
          console.log('✅ RAG系统已就绪');
          return;
        }
      } catch (error) {
        // 继续等待
      }
      
      attempts++;
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (attempts % 10 === 0) {
        console.log(`⏳ 等待RAG系统启动... (${attempts}/${maxAttempts})`);
      }
    }
    
    throw new Error('RAG系统启动超时');
  }

  async startPetBackend() {
    console.log('🐱 启动桌宠后端服务...');
    
    const backendProcess = spawn('node', ['src/backend/server.js'], {
      cwd: this.petSystemPath,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, NODE_ENV: 'production' }
    });
    
    this.processes.push({
      name: '桌宠后端',
      process: backendProcess,
      type: 'backend'
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
        console.error(`❌ 桌宠后端异常退出，代码: ${code}`);
        this.cleanup();
      }
    });
  }

  async waitForPetBackend() {
    console.log('⏳ 等待桌宠后端启动...');
    
    const maxAttempts = 30;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      try {
        const response = await axios.get('http://localhost:3001/health', { timeout: 2000 });
        if (response.status === 200) {
          console.log('✅ 桌宠后端已就绪');
          return;
        }
      } catch (error) {
        // 继续等待
      }
      
      attempts++;
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    throw new Error('桌宠后端启动超时');
  }

  async startElectronApp() {
    console.log('🖥️ 启动Electron桌面应用...');
    
    const electronProcess = spawn('npx', ['electron', '.'], {
      cwd: this.petSystemPath,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, NODE_ENV: 'production' }
    });
    
    this.processes.push({
      name: 'Electron应用',
      process: electronProcess,
      type: 'electron'
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
    
    console.log('🧹 清理系统资源...');
    
    // 按类型分组关闭进程
    const processGroups = {
      electron: [],
      backend: [],
      rag: []
    };
    
    this.processes.forEach(({ name, process, type }) => {
      processGroups[type].push({ name, process });
    });
    
    // 先关闭Electron应用
    for (const { name, process } of processGroups.electron) {
      await this.terminateProcess(name, process);
    }
    
    // 再关闭后端服务
    for (const { name, process } of processGroups.backend) {
      await this.terminateProcess(name, process);
    }
    
    // 最后关闭RAG系统
    for (const { name, process } of processGroups.rag) {
      await this.terminateProcess(name, process);
    }
    
    console.log('✅ 清理完成');
  }

  async terminateProcess(name, process) {
    try {
      console.log(`🛑 关闭 ${name}...`);
      
      // 发送SIGTERM信号
      process.kill('SIGTERM');
      
      // 等待进程关闭，最多等待5秒
      await new Promise((resolve) => {
        const timeout = setTimeout(() => {
          // 如果5秒后还没关闭，强制杀死
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

  // 显示系统状态
  async showStatus() {
    console.log('\n📊 系统状态检查:');
    
    // 检查RAG系统
    try {
      const ragResponse = await axios.get('http://localhost:51658', { timeout: 2000 });
      console.log('✅ RAG系统: 运行正常');
    } catch (error) {
      console.log('❌ RAG系统: 无法访问');
    }
    
    // 检查桌宠后端
    try {
      const backendResponse = await axios.get('http://localhost:3001/health', { timeout: 2000 });
      console.log('✅ 桌宠后端: 运行正常');
    } catch (error) {
      console.log('❌ 桌宠后端: 无法访问');
    }
    
    console.log(`📈 运行进程数: ${this.processes.length}`);
  }
}

// 主函数
async function main() {
  const starter = new IntegratedStarter();
  
  // 处理命令行参数
  const args = process.argv.slice(2);
  
  if (args.includes('--status')) {
    await starter.showStatus();
    return;
  }
  
  if (args.includes('--help')) {
    console.log('长离的学习胶囊 + RAG系统 集成启动器');
    console.log('');
    console.log('用法:');
    console.log('  node start_with_rag.js          启动完整系统');
    console.log('  node start_with_rag.js --status 检查系统状态');
    console.log('  node start_with_rag.js --help   显示帮助信息');
    return;
  }
  
  await starter.start();
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(error => {
    console.error('启动失败:', error);
    process.exit(1);
  });
}

module.exports = IntegratedStarter;