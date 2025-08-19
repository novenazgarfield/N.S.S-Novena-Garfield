#!/usr/bin/env node

/**
 * 长离的学习胶囊 - 简化启动脚本
 * 支持网页版和客户端版，让用户操作尽可能简单
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const http = require('http');
const express = require('express');
const open = require('open');

class EasyStarter {
  constructor() {
    this.processes = [];
    this.isShuttingDown = false;
    this.ragSystemPath = path.resolve(__dirname, '../../rag_system');
    this.petSystemPath = path.resolve(__dirname);
    this.webPort = 8080;
    this.backendPort = 3001;
    this.ragPort = 51658;
  }

  async start() {
    console.log('🚀 长离的学习胶囊 - 简化启动器');
    console.log('=====================================');
    
    // 显示启动选项
    await this.showStartupOptions();
  }

  async showStartupOptions() {
    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    console.log('\n🎯 请选择启动模式:');
    console.log('1. 🌐 网页版 (推荐) - 在浏览器中使用，简单快捷');
    console.log('2. 🖥️  桌面版 - 完整的桌宠体验，包含动画和交互');
    console.log('3. 🔧 开发模式 - 同时启动网页版和桌面版');
    console.log('4. ❓ 帮助 - 查看详细说明');
    console.log('');

    const choice = await new Promise(resolve => {
      rl.question('请输入选项编号 (1-4): ', resolve);
    });

    rl.close();

    switch (choice.trim()) {
      case '1':
        await this.startWebVersion();
        break;
      case '2':
        await this.startDesktopVersion();
        break;
      case '3':
        await this.startDevelopmentMode();
        break;
      case '4':
        this.showHelp();
        break;
      default:
        console.log('❌ 无效选项，默认启动网页版');
        await this.startWebVersion();
    }
  }

  async startWebVersion() {
    console.log('\n🌐 启动网页版...');
    console.log('=====================================');

    try {
      // 1. 检查并启动RAG系统
      console.log('🧠 启动RAG智能系统...');
      await this.startRAGSystem();
      await this.waitForService(this.ragPort, 'RAG系统', 60);

      // 2. 启动后端服务
      console.log('⚙️ 启动后端服务...');
      await this.startBackendService();
      await this.waitForService(this.backendPort, '后端服务', 30);

      // 3. 启动Web服务器
      console.log('🌐 启动Web服务器...');
      await this.startWebServer();

      // 4. 打开浏览器
      console.log('🚀 打开浏览器...');
      await this.openBrowser();

      console.log('\n✅ 网页版启动成功！');
      this.showWebVersionInfo();

    } catch (error) {
      console.error('❌ 网页版启动失败:', error.message);
      await this.cleanup();
      process.exit(1);
    }
  }

  async startDesktopVersion() {
    console.log('\n🖥️ 启动桌面版...');
    console.log('=====================================');

    try {
      // 1. 检查并启动RAG系统
      console.log('🧠 启动RAG智能系统...');
      await this.startRAGSystem();
      await this.waitForService(this.ragPort, 'RAG系统', 60);

      // 2. 启动后端服务
      console.log('⚙️ 启动后端服务...');
      await this.startBackendService();
      await this.waitForService(this.backendPort, '后端服务', 30);

      // 3. 启动Electron应用
      console.log('🐱 启动桌宠应用...');
      await this.startElectronApp();

      console.log('\n✅ 桌面版启动成功！');
      this.showDesktopVersionInfo();

    } catch (error) {
      console.error('❌ 桌面版启动失败:', error.message);
      await this.cleanup();
      process.exit(1);
    }
  }

  async startDevelopmentMode() {
    console.log('\n🔧 启动开发模式...');
    console.log('=====================================');

    try {
      // 启动所有服务
      await this.startRAGSystem();
      await this.waitForService(this.ragPort, 'RAG系统', 60);
      
      await this.startBackendService();
      await this.waitForService(this.backendPort, '后端服务', 30);
      
      await this.startWebServer();
      await this.startElectronApp();
      await this.openBrowser();

      console.log('\n✅ 开发模式启动成功！');
      this.showDevelopmentModeInfo();

    } catch (error) {
      console.error('❌ 开发模式启动失败:', error.message);
      await this.cleanup();
      process.exit(1);
    }
  }

  async startRAGSystem() {
    if (!fs.existsSync(this.ragSystemPath)) {
      throw new Error(`RAG系统路径不存在: ${this.ragSystemPath}`);
    }

    // 检查是否有增强版RAG应用
    const enhancedAppPath = path.join(this.ragSystemPath, 'enhanced_app.py');
    const useEnhanced = fs.existsSync(enhancedAppPath);
    
    const appFile = useEnhanced ? 'enhanced_app.py' : 'universal_app.py';
    console.log(`🧠 启动${useEnhanced ? '增强版' : '标准版'}RAG系统...`);

    const ragProcess = spawn('python', ['-m', 'streamlit', 'run', appFile, `--server.port=${this.ragPort}`, '--server.headless=true'], {
      cwd: this.ragSystemPath,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { 
        ...process.env, 
        PYTHONPATH: this.ragSystemPath,
        STREAMLIT_SERVER_HEADLESS: 'true'
      }
    });

    this.processes.push({
      name: `RAG系统${useEnhanced ? '(增强版)' : ''}`,
      process: ragProcess,
      type: 'rag'
    });

    ragProcess.on('exit', (code) => {
      if (!this.isShuttingDown) {
        console.error(`❌ RAG系统异常退出，代码: ${code}`);
      }
    });
  }

  async startBackendService() {
    const backendProcess = spawn('node', ['src/backend/server.js'], {
      cwd: this.petSystemPath,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, NODE_ENV: 'production', PORT: this.backendPort }
    });

    this.processes.push({
      name: '后端服务',
      process: backendProcess,
      type: 'backend'
    });

    backendProcess.on('exit', (code) => {
      if (!this.isShuttingDown) {
        console.error(`❌ 后端服务异常退出，代码: ${code}`);
      }
    });
  }

  async startWebServer() {
    const app = express();
    
    // 静态文件服务
    app.use(express.static(path.join(this.petSystemPath, 'src/web')));
    
    // 健康检查
    app.get('/health', (req, res) => {
      res.json({ status: 'ok', timestamp: new Date().toISOString() });
    });

    // 启动服务器
    const server = app.listen(this.webPort, () => {
      console.log(`✅ Web服务器已启动: http://localhost:${this.webPort}`);
    });

    this.processes.push({
      name: 'Web服务器',
      process: { kill: () => server.close() },
      type: 'web'
    });
  }

  async startElectronApp() {
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

    electronProcess.on('exit', (code) => {
      if (!this.isShuttingDown) {
        console.log(`🚪 Electron应用已退出，代码: ${code}`);
        this.cleanup();
      }
    });
  }

  async openBrowser() {
    try {
      await open(`http://localhost:${this.webPort}`);
    } catch (error) {
      console.log('⚠️ 无法自动打开浏览器，请手动访问: http://localhost:' + this.webPort);
    }
  }

  async waitForService(port, serviceName, maxWaitSeconds = 30) {
    console.log(`⏳ 等待${serviceName}启动...`);
    
    for (let i = 0; i < maxWaitSeconds; i++) {
      try {
        await this.checkPort(port);
        console.log(`✅ ${serviceName}已就绪`);
        return;
      } catch (error) {
        if (i % 10 === 0 && i > 0) {
          console.log(`⏳ 等待${serviceName}启动... (${i}/${maxWaitSeconds}秒)`);
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    throw new Error(`${serviceName}启动超时`);
  }

  checkPort(port) {
    return new Promise((resolve, reject) => {
      const req = http.get(`http://localhost:${port}`, (res) => {
        resolve();
      });
      
      req.on('error', reject);
      req.setTimeout(2000, () => {
        req.destroy();
        reject(new Error('Timeout'));
      });
    });
  }

  showWebVersionInfo() {
    console.log('\n🌟 网页版功能说明:');
    console.log('=====================================');
    console.log('🌐 访问地址: http://localhost:' + this.webPort);
    console.log('💬 智能问答: 向长离提问学习相关问题');
    console.log('📚 文档分析: 上传文档进行智能分析');
    console.log('🔍 文献检索: 在已上传文档中搜索信息');
    console.log('');
    console.log('💡 使用提示:');
    console.log('• 支持拖拽上传文档');
    console.log('• 可以使用快捷问题按钮');
    console.log('• 支持多轮对话');
    console.log('• 响应式设计，支持手机访问');
    console.log('');
    console.log('🛑 按 Ctrl+C 停止服务');
  }

  showDesktopVersionInfo() {
    console.log('\n🌟 桌面版功能说明:');
    console.log('=====================================');
    console.log('🐱 桌宠长离: 可拖拽的桌面宠物');
    console.log('💊 学习胶囊: AI生成的学习内容');
    console.log('🏖️ 魔法沙滩: 游戏化拼写练习');
    console.log('📊 学习统计: 详细的进度跟踪');
    console.log('');
    console.log('💡 使用提示:');
    console.log('• 点击长离触发不同交互');
    console.log('• 右键点击查看菜单');
    console.log('• 支持系统托盘运行');
    console.log('• 智能推送学习提醒');
    console.log('');
    console.log('🛑 关闭Electron窗口停止应用');
  }

  showDevelopmentModeInfo() {
    console.log('\n🌟 开发模式功能说明:');
    console.log('=====================================');
    console.log('🌐 网页版: http://localhost:' + this.webPort);
    console.log('🖥️ 桌面版: Electron应用窗口');
    console.log('⚙️ 后端API: http://localhost:' + this.backendPort);
    console.log('🧠 RAG系统: http://localhost:' + this.ragPort);
    console.log('');
    console.log('🔧 开发工具:');
    console.log('• 浏览器开发者工具');
    console.log('• Electron开发者工具');
    console.log('• 实时日志输出');
    console.log('• 热重载支持');
    console.log('');
    console.log('🛑 按 Ctrl+C 停止所有服务');
  }

  showHelp() {
    console.log('\n📖 长离的学习胶囊 - 帮助文档');
    console.log('=====================================');
    console.log('');
    console.log('🎯 启动模式说明:');
    console.log('');
    console.log('1. 🌐 网页版 (推荐新手)');
    console.log('   • 在浏览器中运行，无需安装');
    console.log('   • 支持所有核心功能');
    console.log('   • 响应式设计，支持手机');
    console.log('   • 启动速度快，资源占用少');
    console.log('');
    console.log('2. 🖥️ 桌面版 (完整体验)');
    console.log('   • 可爱的桌面宠物长离');
    console.log('   • 丰富的动画和交互');
    console.log('   • 系统托盘和通知');
    console.log('   • 离线使用支持');
    console.log('');
    console.log('3. 🔧 开发模式 (开发者)');
    console.log('   • 同时启动网页版和桌面版');
    console.log('   • 实时调试和日志');
    console.log('   • 适合开发和测试');
    console.log('');
    console.log('🔧 系统要求:');
    console.log('• Node.js 16+');
    console.log('• Python 3.8+ (用于RAG系统)');
    console.log('• 4GB+ 内存');
    console.log('• 现代浏览器 (Chrome, Firefox, Safari, Edge)');
    console.log('');
    console.log('🆘 常见问题:');
    console.log('• 如果启动失败，请检查端口占用');
    console.log('• 确保已安装所有依赖: npm install');
    console.log('• RAG系统需要Python环境');
    console.log('• 防火墙可能阻止端口访问');
    console.log('');
    console.log('📞 获取帮助:');
    console.log('• 查看 README.md 文档');
    console.log('• 运行 npm run test-rag 检查系统');
    console.log('• 查看日志文件排查问题');
    console.log('');
    console.log('🔄 重新运行此脚本选择启动模式');
  }

  async cleanup() {
    if (this.isShuttingDown) return;
    this.isShuttingDown = true;
    
    console.log('\n🧹 正在关闭服务...');
    
    for (const { name, process } of this.processes) {
      try {
        console.log(`🛑 关闭 ${name}...`);
        if (process.kill) {
          process.kill('SIGTERM');
        }
      } catch (error) {
        console.error(`关闭 ${name} 失败:`, error.message);
      }
    }
    
    console.log('✅ 清理完成');
  }

  setupGracefulShutdown() {
    const signals = ['SIGINT', 'SIGTERM', 'SIGQUIT'];
    
    signals.forEach(signal => {
      process.on(signal, async () => {
        console.log(`\n📡 收到 ${signal} 信号，正在关闭...`);
        await this.cleanup();
        process.exit(0);
      });
    });
  }
}

// 主函数
async function main() {
  const starter = new EasyStarter();
  starter.setupGracefulShutdown();
  
  const args = process.argv.slice(2);
  
  // 支持命令行参数
  if (args.includes('--web')) {
    await starter.startWebVersion();
  } else if (args.includes('--desktop')) {
    await starter.startDesktopVersion();
  } else if (args.includes('--dev')) {
    await starter.startDevelopmentMode();
  } else if (args.includes('--help')) {
    starter.showHelp();
  } else {
    await starter.start();
  }
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(error => {
    console.error('启动失败:', error);
    process.exit(1);
  });
}

module.exports = EasyStarter;