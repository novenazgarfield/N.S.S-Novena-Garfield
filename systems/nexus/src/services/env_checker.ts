/**
 * 环境诊断服务
 * 负责检测系统中各种依赖项的安装状态
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs/promises';
import * as path from 'path';
import * as os from 'os';

const execAsync = promisify(exec);

export interface DependencyInfo {
  name: string;
  installed: boolean;
  version?: string;
  path?: string;
  error?: string;
}

export class EnvironmentChecker {
  private platform: string;
  private cache: Map<string, DependencyInfo> = new Map();

  constructor() {
    this.platform = os.platform();
  }

  /**
   * 检查指定依赖项是否已安装
   */
  async checkDependency(name: string): Promise<boolean> {
    try {
      const info = await this.getDependencyInfo(name);
      return info.installed;
    } catch (error) {
      console.error(`检查依赖 ${name} 失败:`, error);
      return false;
    }
  }

  /**
   * 获取依赖项的版本信息
   */
  async getDependencyVersion(name: string): Promise<string | undefined> {
    try {
      const info = await this.getDependencyInfo(name);
      return info.version;
    } catch (error) {
      console.error(`获取 ${name} 版本失败:`, error);
      return undefined;
    }
  }

  /**
   * 获取依赖项的安装路径
   */
  async getDependencyPath(name: string): Promise<string | undefined> {
    try {
      const info = await this.getDependencyInfo(name);
      return info.path;
    } catch (error) {
      console.error(`获取 ${name} 路径失败:`, error);
      return undefined;
    }
  }

  /**
   * 获取依赖项的完整信息
   */
  async getDependencyInfo(name: string): Promise<DependencyInfo> {
    // 检查缓存
    if (this.cache.has(name)) {
      return this.cache.get(name)!;
    }

    let info: DependencyInfo;

    switch (name.toLowerCase()) {
      case 'git':
        info = await this.checkGit();
        break;
      case 'python':
        info = await this.checkPython();
        break;
      case 'nodejs':
      case 'node':
        info = await this.checkNodeJS();
        break;
      case 'npm':
        info = await this.checkNpm();
        break;
      case 'pip':
        info = await this.checkPip();
        break;
      case 'conda':
        info = await this.checkConda();
        break;
      case 'mamba':
        info = await this.checkMamba();
        break;
      case 'gromacs':
      case 'gmx':
        info = await this.checkGromacs();
        break;
      case 'cuda':
        info = await this.checkCuda();
        break;
      default:
        info = await this.checkGenericCommand(name);
    }

    // 缓存结果
    this.cache.set(name, info);
    return info;
  }

  /**
   * 清除缓存，强制重新检查
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * 检查Git
   */
  private async checkGit(): Promise<DependencyInfo> {
    try {
      const { stdout: version } = await execAsync('git --version');
      const { stdout: path } = await execAsync(this.getWhichCommand('git'));
      
      return {
        name: 'git',
        installed: true,
        version: version.trim().replace('git version ', ''),
        path: path.trim()
      };
    } catch (error) {
      return {
        name: 'git',
        installed: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * 检查Python
   */
  private async checkPython(): Promise<DependencyInfo> {
    const pythonCommands = ['python', 'python3', 'py'];
    
    for (const cmd of pythonCommands) {
      try {
        const { stdout: version } = await execAsync(`${cmd} --version`);
        const { stdout: path } = await execAsync(this.getWhichCommand(cmd));
        
        return {
          name: 'python',
          installed: true,
          version: version.trim().replace('Python ', ''),
          path: path.trim()
        };
      } catch (error) {
        continue;
      }
    }

    return {
      name: 'python',
      installed: false,
      error: 'Python not found in PATH'
    };
  }

  /**
   * 检查Node.js
   */
  private async checkNodeJS(): Promise<DependencyInfo> {
    try {
      const { stdout: version } = await execAsync('node --version');
      const { stdout: path } = await execAsync(this.getWhichCommand('node'));
      
      return {
        name: 'nodejs',
        installed: true,
        version: version.trim().replace('v', ''),
        path: path.trim()
      };
    } catch (error) {
      return {
        name: 'nodejs',
        installed: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * 检查npm
   */
  private async checkNpm(): Promise<DependencyInfo> {
    try {
      const { stdout: version } = await execAsync('npm --version');
      const { stdout: path } = await execAsync(this.getWhichCommand('npm'));
      
      return {
        name: 'npm',
        installed: true,
        version: version.trim(),
        path: path.trim()
      };
    } catch (error) {
      return {
        name: 'npm',
        installed: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * 检查pip
   */
  private async checkPip(): Promise<DependencyInfo> {
    const pipCommands = ['pip', 'pip3'];
    
    for (const cmd of pipCommands) {
      try {
        const { stdout: version } = await execAsync(`${cmd} --version`);
        const { stdout: path } = await execAsync(this.getWhichCommand(cmd));
        
        const versionMatch = version.match(/pip ([\d.]+)/);
        return {
          name: 'pip',
          installed: true,
          version: versionMatch ? versionMatch[1] : version.trim(),
          path: path.trim()
        };
      } catch (error) {
        continue;
      }
    }

    return {
      name: 'pip',
      installed: false,
      error: 'pip not found in PATH'
    };
  }

  /**
   * 检查Conda
   */
  private async checkConda(): Promise<DependencyInfo> {
    try {
      const { stdout: version } = await execAsync('conda --version');
      const { stdout: path } = await execAsync(this.getWhichCommand('conda'));
      
      return {
        name: 'conda',
        installed: true,
        version: version.trim().replace('conda ', ''),
        path: path.trim()
      };
    } catch (error) {
      return {
        name: 'conda',
        installed: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * 检查Mamba
   */
  private async checkMamba(): Promise<DependencyInfo> {
    try {
      const { stdout: version } = await execAsync('mamba --version');
      const { stdout: path } = await execAsync(this.getWhichCommand('mamba'));
      
      return {
        name: 'mamba',
        installed: true,
        version: version.trim().replace('mamba ', ''),
        path: path.trim()
      };
    } catch (error) {
      return {
        name: 'mamba',
        installed: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * 检查GROMACS
   */
  private async checkGromacs(): Promise<DependencyInfo> {
    try {
      const { stdout: version } = await execAsync('gmx --version');
      const { stdout: path } = await execAsync(this.getWhichCommand('gmx'));
      
      const versionMatch = version.match(/GROMACS version:\s+([\d.]+)/);
      return {
        name: 'gromacs',
        installed: true,
        version: versionMatch ? versionMatch[1] : 'unknown',
        path: path.trim()
      };
    } catch (error) {
      return {
        name: 'gromacs',
        installed: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * 检查CUDA
   */
  private async checkCuda(): Promise<DependencyInfo> {
    try {
      const { stdout: version } = await execAsync('nvcc --version');
      const versionMatch = version.match(/release ([\d.]+)/);
      
      return {
        name: 'cuda',
        installed: true,
        version: versionMatch ? versionMatch[1] : 'unknown',
        path: '/usr/local/cuda' // 默认CUDA路径
      };
    } catch (error) {
      return {
        name: 'cuda',
        installed: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * 检查通用命令
   */
  private async checkGenericCommand(command: string): Promise<DependencyInfo> {
    try {
      // 尝试获取版本信息
      let version = 'unknown';
      try {
        const { stdout } = await execAsync(`${command} --version`);
        version = stdout.trim().split('\n')[0];
      } catch {
        // 如果 --version 失败，尝试 -v
        try {
          const { stdout } = await execAsync(`${command} -v`);
          version = stdout.trim().split('\n')[0];
        } catch {
          // 如果都失败，保持 unknown
        }
      }

      const { stdout: path } = await execAsync(this.getWhichCommand(command));
      
      return {
        name: command,
        installed: true,
        version,
        path: path.trim()
      };
    } catch (error) {
      return {
        name: command,
        installed: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * 获取适合当前平台的which命令
   */
  private getWhichCommand(command: string): string {
    return this.platform === 'win32' ? `where ${command}` : `which ${command}`;
  }

  /**
   * 检查系统环境概览
   */
  async getSystemOverview(): Promise<{
    platform: string;
    arch: string;
    nodeVersion?: string;
    pythonVersion?: string;
    gitVersion?: string;
    totalMemory: string;
    freeMemory: string;
  }> {
    const nodeInfo = await this.getDependencyInfo('nodejs');
    const pythonInfo = await this.getDependencyInfo('python');
    const gitInfo = await this.getDependencyInfo('git');

    return {
      platform: os.platform(),
      arch: os.arch(),
      nodeVersion: nodeInfo.version,
      pythonVersion: pythonInfo.version,
      gitVersion: gitInfo.version,
      totalMemory: `${Math.round(os.totalmem() / 1024 / 1024 / 1024)}GB`,
      freeMemory: `${Math.round(os.freemem() / 1024 / 1024 / 1024)}GB`
    };
  }

  /**
   * 生成环境诊断报告
   */
  async generateDiagnosticReport(): Promise<string> {
    const overview = await this.getSystemOverview();
    const dependencies = ['git', 'python', 'nodejs', 'npm', 'pip', 'conda'];
    
    let report = '# 环境诊断报告\n\n';
    report += `## 系统信息\n`;
    report += `- 平台: ${overview.platform}\n`;
    report += `- 架构: ${overview.arch}\n`;
    report += `- 总内存: ${overview.totalMemory}\n`;
    report += `- 可用内存: ${overview.freeMemory}\n\n`;

    report += `## 依赖项检查\n`;
    for (const dep of dependencies) {
      const info = await this.getDependencyInfo(dep);
      const status = info.installed ? '✅' : '❌';
      const version = info.version ? ` (${info.version})` : '';
      const path = info.path ? ` - ${info.path}` : '';
      const error = info.error ? ` - 错误: ${info.error}` : '';
      
      report += `- ${status} ${dep}${version}${path}${error}\n`;
    }

    report += `\n## 生成时间\n${new Date().toLocaleString()}\n`;
    
    return report;
  }
}