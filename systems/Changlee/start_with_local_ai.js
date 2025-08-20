#!/usr/bin/env node

/**
 * Changlee集成启动脚本
 * 同时启动Changlee主服务和本地AI服务
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const axios = require('axios');

class ChangleeIntegratedLauncher {
  constructor() {
    this.processes = new Map();
    this.services = {
      localAI: {
        name: 'Changlee本地AI服务',
        path: path.join(__dirname, 'src/backend'),
        command: 'python',
        args: ['local_ai_server.py', '--host', '0.0.0.0', '--port', '8001'],
        port: 8001,
        healthUrl: 'http://localhost:8001/health',
        ready: false,
        env: {
          ...process.env,
          PYTHONPATH: path.join(__dirname, 'src/backend'),
          LOCAL_AI_ENABLED: 'true'
        }
      },
      changlee: {
        name: 'Changlee主服务',
        path: path.join(__dirname, 'src/backend'),
        command: 'node',
        args: ['server.js'],
        port: 3001,
        healthUrl: 'http://localhost:3001/health',
        ready: false,
        env: {
          ...process.env,
          LOCAL_AI_ENABLED: 'true',
          LOCAL_AI_URL: 'http://localhost:8001',
          LOCAL_AI_TIMEOUT: '15000',
          LOCAL_AI_RETRY: '3'
        }
      }
    };
    
    this.startupTimeout = 120000; // 2分钟启动超时
    this.healthCheckInterval = 3000; // 3秒健康检查间隔
  }

  /**
   * 启动集成系统
   */
  async start() {
    console.log('🚀 启动Changlee集成系统（含本地AI）...\n');

    try {
      // 检查环境
      await this.checkEnvironment();
      
      // 安装Python依赖
      await this.installPythonDependencies();
      
      // 启动服务
      await this.startServices();
      
      // 验证集成
      await this.verifyIntegration();
      
      // 设置信号处理
      this.setupSignalHandlers();
      
      console.log('\n✅ Changlee集成系统启动完成！');
      console.log('🤖 本地AI服务: http://localhost:8001');
      console.log('🎓 Changlee主服务: http://localhost:3001');
      console.log('\n按 Ctrl+C 停止所有服务');
      
      // 保持进程运行
      await this.keepAlive();
      
    } catch (error) {
      console.error('❌ 启动失败:', error.message);
      await this.cleanup();
      process.exit(1);
    }
  }

  /**
   * 检查环境
   */
  async checkEnvironment() {
    console.log('🔍 检查环境...');
    
    // 检查Node.js版本
    const nodeVersion = process.version;
    console.log(`   Node.js版本: ${nodeVersion}`);
    
    // 检查Python版本
    try {
      const pythonVersion = await this.execCommand('python --version');
      console.log(`   Python版本: ${pythonVersion.trim()}`);
    } catch (error) {
      try {
        const python3Version = await this.execCommand('python3 --version');
        console.log(`   Python版本: ${python3Version.trim()}`);
        // 更新Python命令
        this.services.localAI.command = 'python3';
      } catch (error3) {
        throw new Error('Python未安装或不在PATH中');
      }
    }
    
    // 检查项目目录
    for (const [key, service] of Object.entries(this.services)) {
      if (!fs.existsSync(service.path)) {
        throw new Error(`${service.name}项目目录不存在: ${service.path}`);
      }
      console.log(`   ✅ ${service.name}项目目录检查通过`);
    }
    
    // 检查端口占用
    await this.checkPorts();
    
    console.log('✅ 环境检查完成\n');
  }

  /**
   * 安装Python依赖
   */
  async installPythonDependencies() {
    console.log('📦 检查Python依赖...');
    
    const requirementsPath = path.join(__dirname, 'requirements_local_ai.txt');
    
    if (fs.existsSync(requirementsPath)) {
      try {
        console.log('   安装本地AI依赖...');
        const pythonCmd = this.services.localAI.command;
        await this.execCommand(`${pythonCmd} -m pip install -r "${requirementsPath}"`);
        console.log('   ✅ Python依赖安装完成');
      } catch (error) {
        console.warn('   ⚠️ Python依赖安装失败，可能影响本地AI功能');
        console.warn('   请手动运行: pip install -r requirements_local_ai.txt');
      }
    } else {
      console.log('   ⚠️ requirements_local_ai.txt不存在，跳过依赖安装');
    }
    
    console.log('');
  }

  /**
   * 检查端口占用
   */
  async checkPorts() {
    for (const [key, service] of Object.entries(this.services)) {
      const isPortInUse = await this.isPortInUse(service.port);
      if (isPortInUse) {
        console.warn(`   ⚠️ 端口 ${service.port} 已被占用，${service.name}可能无法启动`);
      } else {
        console.log(`   ✅ 端口 ${service.port} 可用`);
      }
    }
  }

  /**
   * 检查端口是否被占用
   */
  async isPortInUse(port) {
    return new Promise((resolve) => {
      const net = require('net');
      const server = net.createServer();
      
      server.listen(port, () => {
        server.once('close', () => resolve(false));
        server.close();
      });
      
      server.on('error', () => resolve(true));
    });
  }

  /**
   * 启动所有服务
   */
  async startServices() {
    console.log('🔧 启动服务...');
    
    // 首先启动本地AI服务
    await this.startService('localAI');
    
    // 等待本地AI服务就绪后启动Changlee主服务
    await this.waitForService('localAI');
    await this.startService('changlee');
    
    // 等待所有服务就绪
    await this.waitForAllServices();
    
    console.log('✅ 所有服务启动完成\n');
  }

  /**
   * 启动单个服务
   */
  async startService(serviceKey) {
    const service = this.services[serviceKey];
    console.log(`   🚀 启动${service.name}...`);
    
    const process = spawn(service.command, service.args, {
      cwd: service.path,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: service.env
    });

    // 处理输出
    process.stdout.on('data', (data) => {
      const output = data.toString().trim();
      if (output) {
        console.log(`   [${service.name}] ${output}`);
      }
    });

    process.stderr.on('data', (data) => {
      const output = data.toString().trim();
      if (output && !output.includes('warning') && !output.includes('Warning')) {
        console.error(`   [${service.name}] ${output}`);
      }
    });

    process.on('exit', (code) => {
      console.log(`   [${service.name}] 进程退出，代码: ${code}`);
      service.ready = false;
      this.processes.delete(serviceKey);
    });

    process.on('error', (error) => {
      console.error(`   [${service.name}] 启动错误:`, error.message);
      service.ready = false;
    });

    this.processes.set(serviceKey, process);
    console.log(`   ✅ ${service.name}进程已启动 (PID: ${process.pid})`);
  }

  /**
   * 等待服务就绪
   */
  async waitForService(serviceKey) {
    const service = this.services[serviceKey];
    console.log(`   ⏳ 等待${service.name}就绪...`);
    
    const startTime = Date.now();
    
    while (Date.now() - startTime < this.startupTimeout) {
      try {
        const response = await axios.get(service.healthUrl, { 
          timeout: 5000,
          validateStatus: () => true // 接受所有状态码
        });
        
        if (response.status === 200) {
          service.ready = true;
          console.log(`   ✅ ${service.name}已就绪`);
          return;
        }
      } catch (error) {
        // 继续等待
      }
      
      await this.sleep(this.healthCheckInterval);
    }
    
    throw new Error(`${service.name}启动超时`);
  }

  /**
   * 等待所有服务就绪
   */
  async waitForAllServices() {
    const pendingServices = Object.keys(this.services).filter(
      key => !this.services[key].ready
    );
    
    if (pendingServices.length === 0) {
      return;
    }
    
    console.log(`   ⏳ 等待服务就绪: ${pendingServices.map(k => this.services[k].name).join(', ')}`);
    
    await Promise.all(
      pendingServices.map(key => this.waitForService(key))
    );
  }

  /**
   * 验证集成
   */
  async verifyIntegration() {
    console.log('🔗 验证系统集成...');
    
    try {
      // 检查Changlee的本地AI集成状态
      const response = await axios.get('http://localhost:3001/api/local-ai/status');
      
      if (response.data.success) {
        const status = response.data.data;
        console.log(`   ✅ 本地AI集成状态: ${status.enabled ? '已启用' : '未启用'}`);
        console.log(`   🤖 AI模型状态: ${status.is_loaded ? '已加载' : '未加载'}`);
        
        if (!status.is_loaded) {
          console.log('   ⏳ AI模型正在加载中，请稍等...');
        }
      } else {
        console.warn('   ⚠️ 无法获取本地AI集成状态');
      }
      
      // 测试AI生成功能
      try {
        const testResponse = await axios.post('http://localhost:3001/api/local-ai/greeting', {
          time_of_day: 'morning'
        }, { timeout: 30000 });
        
        if (testResponse.data.success) {
          console.log(`   ✅ AI生成测试成功: ${testResponse.data.response}`);
        } else {
          console.warn('   ⚠️ AI生成测试失败，但服务将继续运行');
        }
      } catch (error) {
        console.warn('   ⚠️ AI生成测试失败（可能模型还在加载）');
      }
      
    } catch (error) {
      console.warn('   ⚠️ 集成验证失败:', error.message);
    }
    
    console.log('✅ 集成验证完成\n');
  }

  /**
   * 设置信号处理
   */
  setupSignalHandlers() {
    const signals = ['SIGINT', 'SIGTERM'];
    
    signals.forEach(signal => {
      process.on(signal, async () => {
        console.log(`\n🛑 收到${signal}信号，正在关闭服务...`);
        await this.cleanup();
        process.exit(0);
      });
    });
    
    process.on('uncaughtException', async (error) => {
      console.error('❌ 未捕获的异常:', error);
      await this.cleanup();
      process.exit(1);
    });
    
    process.on('unhandledRejection', async (reason) => {
      console.error('❌ 未处理的Promise拒绝:', reason);
      await this.cleanup();
      process.exit(1);
    });
  }

  /**
   * 保持进程运行
   */
  async keepAlive() {
    // 定期检查服务状态
    const healthCheckInterval = setInterval(async () => {
      for (const [key, service] of Object.entries(this.services)) {
        if (service.ready) {
          try {
            await axios.get(service.healthUrl, { timeout: 5000 });
          } catch (error) {
            console.warn(`⚠️ ${service.name}健康检查失败:`, error.message);
            service.ready = false;
          }
        }
      }
    }, 60000); // 每分钟检查一次
    
    // 等待进程结束
    return new Promise((resolve) => {
      process.on('exit', () => {
        clearInterval(healthCheckInterval);
        resolve();
      });
    });
  }

  /**
   * 清理资源
   */
  async cleanup() {
    console.log('🧹 清理资源...');
    
    // 停止所有子进程
    for (const [key, process] of this.processes) {
      try {
        console.log(`   🛑 停止${this.services[key].name}...`);
        process.kill('SIGTERM');
        
        // 等待进程结束
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
        
        console.log(`   ✅ ${this.services[key].name}已停止`);
      } catch (error) {
        console.error(`   ❌ 停止${this.services[key].name}失败:`, error.message);
      }
    }
    
    this.processes.clear();
    console.log('✅ 资源清理完成');
  }

  /**
   * 执行命令
   */
  execCommand(command) {
    return new Promise((resolve, reject) => {
      exec(command, (error, stdout, stderr) => {
        if (error) {
          reject(error);
        } else {
          resolve(stdout);
        }
      });
    });
  }

  /**
   * 睡眠函数
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * 显示帮助信息
 */
function showHelp() {
  console.log(`
Changlee集成系统启动器（含本地AI）

用法:
  node start_with_local_ai.js [选项]

选项:
  --help, -h     显示帮助信息
  --version, -v  显示版本信息
  --check        仅检查环境，不启动服务

环境变量:
  LOCAL_AI_ENABLED     启用本地AI服务 (默认: true)
  LOCAL_AI_URL         本地AI服务URL (默认: http://localhost:8001)
  LOCAL_AI_TIMEOUT     本地AI请求超时时间 (默认: 15000ms)
  LOCAL_AI_RETRY       本地AI请求重试次数 (默认: 3)

示例:
  node start_with_local_ai.js
  node start_with_local_ai.js --check
  LOCAL_AI_ENABLED=false node start_with_local_ai.js
`);
}

/**
 * 主函数
 */
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    showHelp();
    return;
  }
  
  if (args.includes('--version') || args.includes('-v')) {
    console.log('Changlee集成系统 v1.0.0 (含本地AI)');
    return;
  }
  
  const launcher = new ChangleeIntegratedLauncher();
  
  if (args.includes('--check')) {
    console.log('🔍 环境检查模式');
    await launcher.checkEnvironment();
    console.log('✅ 环境检查完成');
    return;
  }
  
  await launcher.start();
}

// 运行主函数
if (require.main === module) {
  main().catch(error => {
    console.error('❌ 启动器错误:', error);
    process.exit(1);
  });
}

module.exports = ChangleeIntegratedLauncher;