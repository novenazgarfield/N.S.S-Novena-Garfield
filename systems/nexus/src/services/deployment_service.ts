/**
 * 部署执行服务
 * 负责系统级依赖安装和子系统部署
 */

import { exec, spawn } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs/promises';
import * as path from 'path';
import * as os from 'os';
import { systemsConfig } from '../features/systems/systems.json';

const execAsync = promisify(exec);

export interface ProgressCallback {
  (progress: number): void;
}

export interface LogCallback {
  (log: string): void;
}

export class DeploymentService {
  private platform: string;
  private workspaceRoot: string;
  private runningProcesses: Map<string, any> = new Map();

  constructor(workspaceRoot?: string) {
    this.platform = os.platform();
    this.workspaceRoot = workspaceRoot || path.join(os.homedir(), 'research-workstation');
  }

  /**
   * 确保依赖项已安装
   * 支持用户自定义安装路径和系统级安装
   */
  async ensureDependency(
    dependencyName: string,
    installPath: string,
    onProgress?: ProgressCallback,
    onLog?: LogCallback
  ): Promise<boolean> {
    try {
      onLog?.(`开始安装依赖: ${dependencyName}`);
      onProgress?.(0);

      // 查找依赖配置
      const dependency = systemsConfig.global_dependencies.find(
        dep => dep.name.toLowerCase() === dependencyName.toLowerCase()
      );

      if (!dependency) {
        throw new Error(`未找到依赖配置: ${dependencyName}`);
      }

      // 获取当前平台的安装方法
      const platformKey = this.getPlatformKey();
      const installMethod = dependency.install_methods[platformKey];

      if (!installMethod) {
        throw new Error(`不支持的平台: ${this.platform}`);
      }

      onLog?.(`使用安装方法: ${installMethod.method}`);
      onProgress?.(10);

      // 请求管理员权限
      if (await this.requiresElevation(installMethod.method)) {
        onLog?.('请求管理员权限...');
        await this.requestElevation();
      }

      onProgress?.(20);

      // 执行安装命令
      const installCommand = installMethod.command.replace('{install_path}', installPath);
      onLog?.(`执行安装命令: ${installCommand}`);

      await this.executeWithProgress(
        installCommand,
        (progress) => onProgress?.(20 + progress * 0.6),
        onLog
      );

      onProgress?.(80);

      // 验证安装
      onLog?.('验证安装...');
      const { stdout } = await execAsync(installMethod.verify);
      onLog?.(`验证成功: ${stdout.trim()}`);

      onProgress?.(100);
      onLog?.(`依赖 ${dependencyName} 安装完成`);

      return true;
    } catch (error) {
      onLog?.(`安装失败: ${(error as Error).message}`);
      return false;
    }
  }

  /**
   * 安装系统
   */
  async installSystem(
    systemName: string,
    onProgress?: ProgressCallback,
    onLog?: LogCallback
  ): Promise<boolean> {
    try {
      onLog?.(`开始安装系统: ${systemName}`);
      onProgress?.(0);

      // 查找系统配置
      const system = systemsConfig.systems.find(sys => sys.name === systemName || sys.id === systemName);
      if (!system) {
        throw new Error(`未找到系统配置: ${systemName}`);
      }

      const systemPath = path.join(this.workspaceRoot, system.path);

      // 1. 克隆代码库
      onLog?.('克隆代码库...');
      await this.cloneRepository(system.github_url, this.workspaceRoot, onLog);
      onProgress?.(30);

      // 2. 切换到系统目录
      process.chdir(systemPath);
      onLog?.(`切换到目录: ${systemPath}`);

      // 3. 安装依赖
      onLog?.('安装系统依赖...');
      for (let i = 0; i < system.install_commands.length; i++) {
        const command = system.install_commands[i];
        onLog?.(`执行: ${command}`);
        
        await this.executeWithProgress(
          command,
          (progress) => onProgress?.(30 + (i + 1) / system.install_commands.length * 60 + progress * 0.1),
          onLog
        );
      }

      onProgress?.(90);

      // 4. 创建启动脚本
      await this.createLaunchScript(system);
      onLog?.('创建启动脚本');

      onProgress?.(100);
      onLog?.(`系统 ${systemName} 安装完成`);

      return true;
    } catch (error) {
      onLog?.(`安装失败: ${(error as Error).message}`);
      return false;
    }
  }

  /**
   * 启动系统
   */
  async launchSystem(systemName: string): Promise<boolean> {
    try {
      const system = systemsConfig.systems.find(sys => sys.name === systemName || sys.id === systemName);
      if (!system) {
        throw new Error(`未找到系统配置: ${systemName}`);
      }

      const systemPath = path.join(this.workspaceRoot, system.path);
      
      // 设置环境变量
      const env = { ...process.env, ...system.environment_variables };

      // 启动进程
      const child = spawn('bash', ['-c', system.start_command], {
        cwd: systemPath,
        env,
        detached: true,
        stdio: 'ignore'
      });

      child.unref();
      this.runningProcesses.set(systemName, child);

      // 等待一段时间确保启动成功
      await new Promise(resolve => setTimeout(resolve, 2000));

      return true;
    } catch (error) {
      console.error(`启动系统失败: ${error}`);
      return false;
    }
  }

  /**
   * 停止系统
   */
  async stopSystem(systemName: string): Promise<boolean> {
    try {
      const system = systemsConfig.systems.find(sys => sys.name === systemName || sys.id === systemName);
      if (!system) {
        throw new Error(`未找到系统配置: ${systemName}`);
      }

      // 如果有运行中的进程，先尝试优雅关闭
      const runningProcess = this.runningProcesses.get(systemName);
      if (runningProcess) {
        runningProcess.kill('SIGTERM');
        this.runningProcesses.delete(systemName);
      }

      // 执行停止命令
      if (system.stop_command) {
        await execAsync(system.stop_command);
      }

      return true;
    } catch (error) {
      console.error(`停止系统失败: ${error}`);
      return false;
    }
  }

  /**
   * 检查系统是否已安装
   */
  async isSystemInstalled(systemName: string): Promise<boolean> {
    try {
      const system = systemsConfig.systems.find(sys => sys.name === systemName || sys.id === systemName);
      if (!system) return false;

      const systemPath = path.join(this.workspaceRoot, system.path);
      const stats = await fs.stat(systemPath);
      return stats.isDirectory();
    } catch {
      return false;
    }
  }

  /**
   * 检查系统是否正在运行
   */
  async isSystemRunning(systemName: string): Promise<boolean> {
    try {
      const system = systemsConfig.systems.find(sys => sys.name === systemName || sys.id === systemName);
      if (!system || !system.health_check) return false;

      await execAsync(system.health_check);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * 获取系统安装路径
   */
  async getSystemPath(systemName: string): Promise<string | undefined> {
    const system = systemsConfig.systems.find(sys => sys.name === systemName || sys.id === systemName);
    if (!system) return undefined;

    const systemPath = path.join(this.workspaceRoot, system.path);
    try {
      await fs.access(systemPath);
      return systemPath;
    } catch {
      return undefined;
    }
  }

  /**
   * 获取系统版本
   */
  async getSystemVersion(systemName: string): Promise<string | undefined> {
    try {
      const systemPath = await this.getSystemPath(systemName);
      if (!systemPath) return undefined;

      // 尝试读取package.json或其他版本文件
      const packageJsonPath = path.join(systemPath, 'package.json');
      try {
        const packageJson = JSON.parse(await fs.readFile(packageJsonPath, 'utf-8'));
        return packageJson.version;
      } catch {
        // 如果没有package.json，尝试从git获取
        const { stdout } = await execAsync('git describe --tags --abbrev=0', { cwd: systemPath });
        return stdout.trim();
      }
    } catch {
      return undefined;
    }
  }

  /**
   * 获取最后更新时间
   */
  async getLastUpdated(systemName: string): Promise<Date | undefined> {
    try {
      const systemPath = await this.getSystemPath(systemName);
      if (!systemPath) return undefined;

      const stats = await fs.stat(systemPath);
      return stats.mtime;
    } catch {
      return undefined;
    }
  }

  /**
   * 克隆代码库
   */
  private async cloneRepository(
    repoUrl: string,
    targetDir: string,
    onLog?: LogCallback
  ): Promise<void> {
    try {
      // 检查目录是否已存在
      try {
        await fs.access(targetDir);
        onLog?.('目录已存在，跳过克隆');
        return;
      } catch {
        // 目录不存在，继续克隆
      }

      const command = `git clone ${repoUrl} ${targetDir}`;
      onLog?.(`执行: ${command}`);
      
      await execAsync(command);
      onLog?.('代码库克隆完成');
    } catch (error) {
      throw new Error(`克隆代码库失败: ${(error as Error).message}`);
    }
  }

  /**
   * 创建启动脚本
   */
  private async createLaunchScript(system: any): Promise<void> {
    const systemPath = path.join(this.workspaceRoot, system.path);
    const scriptPath = path.join(systemPath, 'launch.sh');

    let script = '#!/bin/bash\n\n';
    script += `# 启动脚本 - ${system.name}\n`;
    script += `cd "${systemPath}"\n\n`;

    // 添加环境变量
    if (system.environment_variables) {
      for (const [key, value] of Object.entries(system.environment_variables)) {
        script += `export ${key}="${value}"\n`;
      }
      script += '\n';
    }

    // 添加启动命令
    script += `${system.start_command}\n`;

    await fs.writeFile(scriptPath, script, { mode: 0o755 });
  }

  /**
   * 执行命令并提供进度反馈
   */
  private async executeWithProgress(
    command: string,
    onProgress?: ProgressCallback,
    onLog?: LogCallback
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      const child = spawn('bash', ['-c', command], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let output = '';
      let progress = 0;

      child.stdout?.on('data', (data) => {
        const text = data.toString();
        output += text;
        onLog?.(text.trim());
        
        // 简单的进度估算
        progress = Math.min(progress + 5, 95);
        onProgress?.(progress);
      });

      child.stderr?.on('data', (data) => {
        const text = data.toString();
        onLog?.(text.trim());
      });

      child.on('close', (code) => {
        if (code === 0) {
          onProgress?.(100);
          resolve();
        } else {
          reject(new Error(`命令执行失败，退出码: ${code}`));
        }
      });

      child.on('error', (error) => {
        reject(error);
      });
    });
  }

  /**
   * 检查是否需要管理员权限
   */
  private async requiresElevation(method: string): Promise<boolean> {
    const elevationMethods = ['winget', 'apt', 'homebrew'];
    return elevationMethods.includes(method);
  }

  /**
   * 请求管理员权限
   */
  private async requestElevation(): Promise<void> {
    // 在实际应用中，这里会弹出系统的权限请求对话框
    // 对于演示，我们只是记录日志
    console.log('请求管理员权限...');
    
    // 在Electron中，可以使用以下方式：
    // const { shell } = require('electron');
    // await shell.openExternal('ms-settings:appsfeatures');
  }

  /**
   * 获取平台键名
   */
  private getPlatformKey(): string {
    switch (this.platform) {
      case 'win32': return 'windows';
      case 'darwin': return 'macos';
      case 'linux': return 'linux';
      default: return 'linux';
    }
  }

  /**
   * 批量安装预设
   */
  async installPreset(
    presetName: string,
    onProgress?: ProgressCallback,
    onLog?: LogCallback
  ): Promise<boolean> {
    try {
      const preset = systemsConfig.installation_presets.find(p => p.name === presetName);
      if (!preset) {
        throw new Error(`未找到预设: ${presetName}`);
      }

      onLog?.(`开始安装预设: ${presetName}`);
      onLog?.(`预计时间: ${preset.estimated_time}`);
      onLog?.(`所需空间: ${preset.disk_space}`);

      const totalSystems = preset.systems.length;
      
      for (let i = 0; i < totalSystems; i++) {
        const systemId = preset.systems[i];
        const systemName = systemsConfig.systems.find(s => s.id === systemId)?.name || systemId;
        
        onLog?.(`安装系统 ${i + 1}/${totalSystems}: ${systemName}`);
        
        const success = await this.installSystem(
          systemId,
          (progress) => onProgress?.((i / totalSystems) * 100 + progress / totalSystems),
          onLog
        );

        if (!success) {
          throw new Error(`安装系统 ${systemName} 失败`);
        }
      }

      onProgress?.(100);
      onLog?.(`预设 ${presetName} 安装完成`);
      
      return true;
    } catch (error) {
      onLog?.(`预设安装失败: ${(error as Error).message}`);
      return false;
    }
  }

  /**
   * 获取系统状态摘要
   */
  async getSystemsSummary(): Promise<{
    total: number;
    installed: number;
    running: number;
    missing_deps: number;
  }> {
    const total = systemsConfig.systems.length;
    let installed = 0;
    let running = 0;
    let missing_deps = 0;

    for (const system of systemsConfig.systems) {
      const isInstalled = await this.isSystemInstalled(system.name);
      if (isInstalled) {
        installed++;
        const isRunning = await this.isSystemRunning(system.name);
        if (isRunning) running++;
      }

      // 检查依赖
      for (const dep of system.dependencies) {
        if (dep.required) {
          // 这里需要集成EnvironmentChecker
          // const checker = new EnvironmentChecker();
          // const hasDepency = await checker.checkDependency(dep.name);
          // if (!hasDepency) missing_deps++;
        }
      }
    }

    return { total, installed, running, missing_deps };
  }
}