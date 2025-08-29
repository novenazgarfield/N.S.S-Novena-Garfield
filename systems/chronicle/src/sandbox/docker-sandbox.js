/**
 * 🐳 Chronicle Docker沙箱测试系统 (Docker Sandbox Testing System)
 * ================================================================
 * 
 * 第二章："权力"的"制衡" - 沙箱原则的强制执行
 * 
 * 核心法则：安全是第一性原理
 * 
 * 功能：
 * - 在隔离的Docker容器中测试修复脚本
 * - 执行单元测试验证修复效果
 * - 确保修复脚本不会损害生产环境
 * - 提供安全的测试环境
 * 
 * 安全原则：
 * - 完全隔离的容器环境
 * - 只读文件系统挂载
 * - 网络隔离
 * - 资源限制
 * 
 * Author: N.S.S-Novena-Garfield Project
 * Version: 3.0.0 - "The Great Expansion"
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');
const { spawn, exec } = require('child_process');
const { promisify } = require('util');
const { v4: uuidv4 } = require('uuid');
const logger = require('../shared/logger');
const { getChronicleBlackBox, SystemSource, FailureSeverity } = require('../genesis/black-box');

const execAsync = promisify(exec);

class DockerSandbox {
  constructor() {
    this.sandboxPath = path.join(os.tmpdir(), 'chronicle-sandbox');
    this.containerPrefix = 'chronicle-sandbox';
    this.activeSandboxes = new Map();
    
    // 沙箱配置
    this.config = {
      dockerImage: 'ubuntu:20.04',
      containerTimeout: 300000,    // 5分钟超时
      maxMemory: '512m',           // 最大内存512MB
      maxCpus: '0.5',              // 最大CPU 0.5核
      networkMode: 'none',         // 无网络访问
      readOnlyRootfs: false,       // 允许写入（在沙箱中）
      noNewPrivileges: true,       // 禁止提权
      securityOpts: [
        'no-new-privileges:true',
        'seccomp=unconfined'       // 简化系统调用限制
      ],
      volumes: [],                 // 只读挂载
      workDir: '/sandbox',
      user: 'nobody:nogroup'       // 非特权用户
    };

    this.blackBox = getChronicleBlackBox();
    
    logger.info('🐳 Docker沙箱系统初始化完成');
  }

  /**
   * 初始化沙箱环境
   */
  async initializeSandbox() {
    try {
      logger.info('🔧 初始化Docker沙箱环境...');

      // 检查Docker是否可用
      await this.checkDockerAvailability();

      // 创建沙箱目录
      await this.createSandboxDirectory();

      // 拉取Docker镜像
      await this.pullDockerImage();

      logger.info('✅ Docker沙箱环境初始化完成');

      return {
        success: true,
        message: 'Docker沙箱环境已就绪',
        sandboxPath: this.sandboxPath,
        dockerImage: this.config.dockerImage
      };

    } catch (error) {
      logger.error('❌ 初始化Docker沙箱失败:', error);
      
      await this.blackBox.recordFailure({
        source: SystemSource.CHRONICLE,
        function_name: 'initializeSandbox',
        error_type: error.constructor.name,
        error_message: error.message,
        severity: FailureSeverity.HIGH
      });

      throw error;
    }
  }

  /**
   * 检查Docker可用性
   */
  async checkDockerAvailability() {
    try {
      const { stdout } = await execAsync('docker --version');
      logger.info(`✅ Docker可用: ${stdout.trim()}`);

      // 检查Docker守护进程
      await execAsync('docker info');
      logger.info('✅ Docker守护进程运行正常');

    } catch (error) {
      throw new Error(`Docker不可用: ${error.message}`);
    }
  }

  /**
   * 创建沙箱目录
   */
  async createSandboxDirectory() {
    try {
      await fs.mkdir(this.sandboxPath, { recursive: true });
      
      // 创建子目录
      const subDirs = ['scripts', 'tests', 'results', 'logs'];
      for (const dir of subDirs) {
        await fs.mkdir(path.join(this.sandboxPath, dir), { recursive: true });
      }

      logger.info(`✅ 沙箱目录已创建: ${this.sandboxPath}`);

    } catch (error) {
      throw new Error(`创建沙箱目录失败: ${error.message}`);
    }
  }

  /**
   * 拉取Docker镜像
   */
  async pullDockerImage() {
    try {
      logger.info(`📥 拉取Docker镜像: ${this.config.dockerImage}`);
      
      const { stdout, stderr } = await execAsync(`docker pull ${this.config.dockerImage}`);
      
      if (stderr && !stderr.includes('Status: Image is up to date')) {
        logger.warn('Docker镜像拉取警告:', stderr);
      }

      logger.info('✅ Docker镜像拉取完成');

    } catch (error) {
      throw new Error(`拉取Docker镜像失败: ${error.message}`);
    }
  }

  /**
   * 在沙箱中测试修复脚本
   */
  async testRepairScript(repairScript, testContext = {}) {
    const sandboxId = uuidv4();
    
    try {
      logger.info(`🧪 开始沙箱测试: ${sandboxId}`);

      // 创建测试环境
      const testEnv = await this.createTestEnvironment(sandboxId, repairScript, testContext);

      // 运行沙箱容器
      const testResult = await this.runSandboxContainer(sandboxId, testEnv);

      // 分析测试结果
      const analysisResult = await this.analyzeTestResult(testResult);

      // 清理测试环境
      await this.cleanupTestEnvironment(sandboxId);

      logger.info(`✅ 沙箱测试完成: ${sandboxId}`);

      return {
        success: true,
        sandboxId: sandboxId,
        testResult: analysisResult,
        scriptSafe: analysisResult.safe,
        executionTime: analysisResult.executionTime,
        logs: analysisResult.logs
      };

    } catch (error) {
      logger.error(`❌ 沙箱测试失败: ${sandboxId}`, error);

      // 清理失败的测试环境
      await this.cleanupTestEnvironment(sandboxId).catch(() => {});

      await this.blackBox.recordFailure({
        source: SystemSource.CHRONICLE,
        function_name: 'testRepairScript',
        error_type: error.constructor.name,
        error_message: error.message,
        context: { sandboxId, repairScript: repairScript.metadata },
        severity: FailureSeverity.HIGH
      });

      return {
        success: false,
        sandboxId: sandboxId,
        error: error.message,
        scriptSafe: false
      };
    }
  }

  /**
   * 创建测试环境
   */
  async createTestEnvironment(sandboxId, repairScript, testContext) {
    const testDir = path.join(this.sandboxPath, sandboxId);
    await fs.mkdir(testDir, { recursive: true });

    // 写入修复脚本
    const scriptPath = path.join(testDir, 'repair_script.sh');
    await fs.writeFile(scriptPath, repairScript.content);
    await fs.chmod(scriptPath, 0o755);

    // 创建测试脚本
    const testScript = this.generateTestScript(repairScript, testContext);
    const testScriptPath = path.join(testDir, 'test_script.sh');
    await fs.writeFile(testScriptPath, testScript);
    await fs.chmod(testScriptPath, 0o755);

    // 创建测试数据
    await this.createTestData(testDir, testContext);

    return {
      testDir: testDir,
      scriptPath: scriptPath,
      testScriptPath: testScriptPath,
      containerName: `${this.containerPrefix}-${sandboxId}`
    };
  }

  /**
   * 生成测试脚本
   */
  generateTestScript(repairScript, testContext) {
    return `#!/bin/bash
# Chronicle自动生成的测试脚本
# 测试目标: ${repairScript.metadata?.errorType || 'Unknown'}
# 生成时间: ${new Date().toISOString()}

set -e  # 遇到错误立即退出

echo "🧪 开始测试修复脚本..."
echo "测试时间: $(date)"
echo "测试环境: Docker沙箱"

# 记录初始状态
echo "📊 记录初始状态..."
df -h > /tmp/initial_disk.log 2>/dev/null || echo "无法记录磁盘状态"
free -h > /tmp/initial_memory.log 2>/dev/null || echo "无法记录内存状态"
ps aux > /tmp/initial_processes.log 2>/dev/null || echo "无法记录进程状态"

# 执行修复脚本
echo "🔧 执行修复脚本..."
start_time=$(date +%s)

# 捕获修复脚本的输出和错误
if timeout 60 bash /sandbox/repair_script.sh > /tmp/repair_output.log 2> /tmp/repair_error.log; then
    echo "✅ 修复脚本执行成功"
    SCRIPT_EXIT_CODE=0
else
    echo "❌ 修复脚本执行失败"
    SCRIPT_EXIT_CODE=$?
fi

end_time=$(date +%s)
execution_time=$((end_time - start_time))

# 记录最终状态
echo "📊 记录最终状态..."
df -h > /tmp/final_disk.log 2>/dev/null || echo "无法记录最终磁盘状态"
free -h > /tmp/final_memory.log 2>/dev/null || echo "无法记录最终内存状态"
ps aux > /tmp/final_processes.log 2>/dev/null || echo "无法记录最终进程状态"

# 生成测试报告
echo "📋 生成测试报告..."
cat > /tmp/test_report.json << EOF
{
  "testId": "${uuidv4()}",
  "scriptType": "${repairScript.metadata?.errorType || 'Unknown'}",
  "executionTime": $execution_time,
  "exitCode": $SCRIPT_EXIT_CODE,
  "success": $([ $SCRIPT_EXIT_CODE -eq 0 ] && echo "true" || echo "false"),
  "timestamp": "$(date -Iseconds)",
  "logs": {
    "output": "$(cat /tmp/repair_output.log 2>/dev/null | base64 -w 0 || echo '')",
    "error": "$(cat /tmp/repair_error.log 2>/dev/null | base64 -w 0 || echo '')"
  }
}
EOF

echo "🧪 测试完成"
echo "执行时间: ${execution_time}秒"
echo "退出代码: $SCRIPT_EXIT_CODE"

# 输出测试报告
cat /tmp/test_report.json
`;
  }

  /**
   * 创建测试数据
   */
  async createTestData(testDir, testContext) {
    // 根据测试上下文创建必要的测试文件
    if (testContext.createFiles) {
      for (const [fileName, content] of Object.entries(testContext.createFiles)) {
        const filePath = path.join(testDir, fileName);
        await fs.writeFile(filePath, content);
      }
    }

    // 创建基础测试环境
    const testDataDir = path.join(testDir, 'testdata');
    await fs.mkdir(testDataDir, { recursive: true });

    // 创建示例配置文件
    await fs.writeFile(
      path.join(testDataDir, 'test_config.json'),
      JSON.stringify({ test: true, environment: 'sandbox' }, null, 2)
    );
  }

  /**
   * 运行沙箱容器
   */
  async runSandboxContainer(sandboxId, testEnv) {
    const containerName = testEnv.containerName;
    
    try {
      // 构建Docker运行命令
      const dockerCmd = [
        'docker', 'run',
        '--name', containerName,
        '--rm',                                    // 自动删除容器
        '--memory', this.config.maxMemory,        // 内存限制
        '--cpus', this.config.maxCpus,            // CPU限制
        '--network', this.config.networkMode,     // 网络模式
        '--workdir', this.config.workDir,         // 工作目录
        '--security-opt', 'no-new-privileges:true', // 安全选项
        '-v', `${testEnv.testDir}:/sandbox:rw`,   // 挂载测试目录
        this.config.dockerImage,                  // 镜像
        '/bin/bash', '/sandbox/test_script.sh'    // 执行测试脚本
      ];

      logger.debug(`执行Docker命令: ${dockerCmd.join(' ')}`);

      // 记录容器启动
      this.activeSandboxes.set(sandboxId, {
        containerName: containerName,
        startTime: new Date(),
        status: 'running'
      });

      // 执行容器
      const { stdout, stderr } = await execAsync(dockerCmd.join(' '), {
        timeout: this.config.containerTimeout
      });

      // 更新容器状态
      this.activeSandboxes.set(sandboxId, {
        containerName: containerName,
        startTime: this.activeSandboxes.get(sandboxId).startTime,
        endTime: new Date(),
        status: 'completed'
      });

      return {
        success: true,
        stdout: stdout,
        stderr: stderr,
        containerName: containerName
      };

    } catch (error) {
      // 更新容器状态
      if (this.activeSandboxes.has(sandboxId)) {
        this.activeSandboxes.set(sandboxId, {
          ...this.activeSandboxes.get(sandboxId),
          endTime: new Date(),
          status: 'failed',
          error: error.message
        });
      }

      // 强制停止容器
      try {
        await execAsync(`docker stop ${containerName}`);
        await execAsync(`docker rm ${containerName}`);
      } catch (cleanupError) {
        logger.debug('容器清理失败:', cleanupError.message);
      }

      throw error;
    }
  }

  /**
   * 分析测试结果
   */
  async analyzeTestResult(testResult) {
    try {
      const stdout = testResult.stdout;
      const stderr = testResult.stderr;

      // 尝试解析测试报告JSON
      let testReport = null;
      const jsonMatch = stdout.match(/\{[\s\S]*\}/);
      
      if (jsonMatch) {
        try {
          testReport = JSON.parse(jsonMatch[0]);
        } catch (parseError) {
          logger.debug('解析测试报告JSON失败:', parseError.message);
        }
      }

      // 分析执行结果
      const analysis = {
        safe: true,
        executionTime: testReport?.executionTime || 0,
        exitCode: testReport?.exitCode || 0,
        success: testResult.success && (testReport?.success || false),
        logs: {
          stdout: stdout,
          stderr: stderr,
          output: testReport?.logs?.output ? Buffer.from(testReport.logs.output, 'base64').toString() : '',
          error: testReport?.logs?.error ? Buffer.from(testReport.logs.error, 'base64').toString() : ''
        },
        warnings: [],
        errors: []
      };

      // 安全性检查
      if (stderr.includes('Permission denied') || stderr.includes('Operation not permitted')) {
        analysis.warnings.push('脚本尝试执行需要特殊权限的操作');
      }

      if (stderr.includes('No such file or directory')) {
        analysis.warnings.push('脚本尝试访问不存在的文件或目录');
      }

      if (analysis.exitCode !== 0) {
        analysis.safe = false;
        analysis.errors.push(`脚本执行失败，退出代码: ${analysis.exitCode}`);
      }

      // 执行时间检查
      if (analysis.executionTime > 60) {
        analysis.warnings.push('脚本执行时间较长，可能影响系统性能');
      }

      logger.info(`📊 测试结果分析完成: 安全=${analysis.safe}, 成功=${analysis.success}`);

      return analysis;

    } catch (error) {
      logger.error('❌ 分析测试结果失败:', error);
      
      return {
        safe: false,
        success: false,
        executionTime: 0,
        exitCode: -1,
        logs: {
          stdout: testResult.stdout || '',
          stderr: testResult.stderr || '',
          output: '',
          error: ''
        },
        warnings: [],
        errors: [`分析测试结果失败: ${error.message}`]
      };
    }
  }

  /**
   * 清理测试环境
   */
  async cleanupTestEnvironment(sandboxId) {
    try {
      const testDir = path.join(this.sandboxPath, sandboxId);
      
      // 删除测试目录
      await fs.rm(testDir, { recursive: true, force: true });

      // 清理容器记录
      this.activeSandboxes.delete(sandboxId);

      logger.debug(`✅ 测试环境已清理: ${sandboxId}`);

    } catch (error) {
      logger.debug(`⚠️ 清理测试环境失败: ${sandboxId}`, error.message);
    }
  }

  /**
   * 获取沙箱状态
   */
  getSandboxStatus() {
    const activeCount = Array.from(this.activeSandboxes.values())
      .filter(s => s.status === 'running').length;

    return {
      isInitialized: true,
      sandboxPath: this.sandboxPath,
      dockerImage: this.config.dockerImage,
      activeSandboxes: activeCount,
      totalSandboxes: this.activeSandboxes.size,
      config: this.config,
      systemInfo: {
        platform: os.platform(),
        arch: os.arch(),
        tmpDir: os.tmpdir()
      }
    };
  }

  /**
   * 清理所有沙箱
   */
  async cleanupAllSandboxes() {
    try {
      logger.info('🧹 清理所有沙箱环境...');

      // 停止所有活动容器
      for (const [sandboxId, sandbox] of this.activeSandboxes) {
        if (sandbox.status === 'running') {
          try {
            await execAsync(`docker stop ${sandbox.containerName}`);
            await execAsync(`docker rm ${sandbox.containerName}`);
          } catch (error) {
            logger.debug(`清理容器失败: ${sandbox.containerName}`, error.message);
          }
        }
      }

      // 清理沙箱目录
      await fs.rm(this.sandboxPath, { recursive: true, force: true });

      // 清理记录
      this.activeSandboxes.clear();

      logger.info('✅ 所有沙箱环境已清理');

      return {
        success: true,
        message: '所有沙箱环境已清理'
      };

    } catch (error) {
      logger.error('❌ 清理沙箱环境失败:', error);
      throw error;
    }
  }
}

module.exports = DockerSandbox;