#!/usr/bin/env node

/**
 * 集成系统启动脚本
 * 同时启动Chronicle和Changlee服务，并验证集成
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const axios = require('axios');

class IntegratedSystemLauncher {
  constructor() {
    this.processes = new Map();
    this.services = {
      chronicle: {
        name: 'Chronicle',
        path: path.join(__dirname, 'systems/chronicle'),
        command: 'npm',
        args: ['start'],
        port: 3000,
        healthUrl: 'http://localhost:3000/health',
        ready: false
      },
      changlee: {
        name: 'Changlee',
        path: path.join(__dirname, 'systems/Changlee'),
        command: 'npm',
        args: ['run', 'backend'],
        port: 3001,
        healthUrl: 'http://localhost:3001/health',
        ready: false
      }
    };
    
    this.startupTimeout = 60000; // 60秒启动超时
    this.healthCheckInterval = 2000; // 2秒健康检查间隔
  }

  /**
   * 启动集成系统
   */
  async start() {
    console.log('🚀 启动Chronicle-Changlee集成系统...\n');

    try {
      // 检查环境
      await this.checkEnvironment();
      
      // 启动服务
      await this.startServices();
      
      // 验证集成
      await this.verifyIntegration();
      
      // 设置信号处理
      this.setupSignalHandlers();
      
      console.log('\n✅ 集成系统启动完成！');
      console.log('📊 Chronicle服务: http://localhost:3000');
      console.log('🎓 Changlee服务: http://localhost:3001');
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
    
    // 检查项目目录
    for (const [key, service] of Object.entries(this.services)) {
      if (!fs.existsSync(service.path)) {
        throw new Error(`${service.name}项目目录不存在: ${service.path}`);
      }
      
      const packageJsonPath = path.join(service.path, 'package.json');
      if (!fs.existsSync(packageJsonPath)) {
        throw new Error(`${service.name}的package.json不存在`);
      }
      
      console.log(`   ✅ ${service.name}项目目录检查通过`);
    }
    
    // 检查端口占用
    await this.checkPorts();
    
    console.log('✅ 环境检查完成\n');
  }

  /**
   * 检查端口占用
   */
  async checkPorts() {
    for (const [key, service] of Object.entries(this.services)) {
      const isPortInUse = await this.isPortInUse(service.port);
      if (isPortInUse) {
        console.warn(`⚠️ 端口 ${service.port} 已被占用，${service.name}可能无法启动`);
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
    
    // 首先启动Chronicle
    await this.startService('chronicle');
    
    // 等待Chronicle就绪后启动Changlee
    await this.waitForService('chronicle');
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
    
    // 检查依赖是否安装
    await this.ensureDependencies(service);
    
    const process = spawn(service.command, service.args, {
      cwd: service.path,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: {
        ...process.env,
        NODE_ENV: 'development',
        // Chronicle特定环境变量
        ...(serviceKey === 'changlee' && {
          CHRONICLE_URL: 'http://localhost:3000',
          CHRONICLE_API_KEY: process.env.CHRONICLE_API_KEY || ''
        })
      }
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
      if (output && !output.includes('warning')) {
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
   * 确保依赖已安装
   */
  async ensureDependencies(service) {
    const nodeModulesPath = path.join(service.path, 'node_modules');
    
    if (!fs.existsSync(nodeModulesPath)) {
      console.log(`   📦 安装${service.name}依赖...`);
      
      await new Promise((resolve, reject) => {
        const installProcess = spawn('npm', ['install'], {
          cwd: service.path,
          stdio: 'inherit'
        });
        
        installProcess.on('exit', (code) => {
          if (code === 0) {
            resolve();
          } else {
            reject(new Error(`${service.name}依赖安装失败`));
          }
        });
      });
      
      console.log(`   ✅ ${service.name}依赖安装完成`);
    }
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
        const response = await axios.get(service.healthUrl, { timeout: 5000 });
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
      // 检查Changlee的Chronicle集成状态
      const response = await axios.get('http://localhost:3001/api/chronicle/status');
      
      if (response.data.success) {
        const status = response.data.data;
        console.log(`   ✅ Chronicle集成状态: ${status.integration_status}`);
        console.log(`   📊 Chronicle连接: ${status.client.isConnected ? '已连接' : '未连接'}`);
        
        if (!status.client.isConnected) {
          console.warn('   ⚠️ Chronicle连接未建立，但服务将继续运行');
        }
      } else {
        console.warn('   ⚠️ 无法获取Chronicle集成状态');
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
    }, 30000); // 每30秒检查一次
    
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
Chronicle-Changlee集成系统启动器

用法:
  node start_integrated_system.js [选项]

选项:
  --help, -h     显示帮助信息
  --version, -v  显示版本信息
  --check        仅检查环境，不启动服务
  --test         启动后运行集成测试

环境变量:
  CHRONICLE_API_KEY    Chronicle API密钥（可选）
  NODE_ENV            运行环境 (development/production)

示例:
  node start_integrated_system.js
  node start_integrated_system.js --check
  node start_integrated_system.js --test
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
    console.log('Chronicle-Changlee集成系统 v1.0.0');
    return;
  }
  
  const launcher = new IntegratedSystemLauncher();
  
  if (args.includes('--check')) {
    console.log('🔍 环境检查模式');
    await launcher.checkEnvironment();
    console.log('✅ 环境检查完成');
    return;
  }
  
  await launcher.start();
  
  if (args.includes('--test')) {
    console.log('\n🧪 运行集成测试...');
    try {
      const ChronicleIntegrationTester = require('./systems/Changlee/test_chronicle_integration.js');
      const tester = new ChronicleIntegrationTester();
      await tester.runAllTests();
    } catch (error) {
      console.error('❌ 集成测试失败:', error.message);
    }
  }
}

// 运行主函数
if (require.main === module) {
  main().catch(error => {
    console.error('❌ 启动器错误:', error);
    process.exit(1);
  });
}

module.exports = IntegratedSystemLauncher;