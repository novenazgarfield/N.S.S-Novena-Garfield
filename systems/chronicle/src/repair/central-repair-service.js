/**
 * 🏥 Chronicle中央修复服务 (Central Repair Service)
 * =================================================
 * 
 * 第一章：能力的"扩展" - 主动修复的授权
 * 
 * 功能：
 * - 接收外部错误信息
 * - 生成修复脚本
 * - 中央化修复服务
 * - 支持多种错误类型的修复策略
 * 
 * 安全原则：
 * - 默认只读权限
 * - 所有修复脚本必须经过沙箱测试
 * - 需要用户授权才能执行修复
 * 
 * Author: N.S.S-Novena-Garfield Project
 * Version: 3.0.0 - "The Great Expansion"
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');
const { v4: uuidv4 } = require('uuid');
const logger = require('../shared/logger');
const { getChronicleBlackBox, SystemSource, FailureSeverity } = require('../genesis/black-box');

class CentralRepairService {
  constructor() {
    this.repairQueue = new Map();
    this.repairHistory = [];
    this.repairStrategies = new Map();
    this.sandboxPath = path.join(os.tmpdir(), 'chronicle-sandbox');
    
    // 修复服务配置
    this.config = {
      maxQueueSize: 100,
      maxHistorySize: 1000,
      defaultTimeout: 30000,
      sandboxEnabled: true,
      requireUserApproval: true,
      supportedErrorTypes: [
        'ConnectionError',
        'FileNotFoundError',
        'PermissionError',
        'MemoryError',
        'TimeoutError',
        'ConfigurationError',
        'DependencyError',
        'ServiceError'
      ]
    };

    this.blackBox = getChronicleBlackBox();
    
    // 初始化修复策略
    this.initializeRepairStrategies();
    
    logger.info('🏥 中央修复服务初始化完成');
  }

  /**
   * 初始化修复策略
   */
  initializeRepairStrategies() {
    // 连接错误修复策略
    this.repairStrategies.set('ConnectionError', {
      name: 'Connection Error Repair',
      description: '修复网络连接相关错误',
      priority: 'HIGH',
      estimatedTime: 30,
      steps: [
        'check_network_connectivity',
        'restart_network_service',
        'clear_dns_cache',
        'retry_connection'
      ],
      generateScript: (context) => this.generateConnectionRepairScript(context),
      testScript: (script) => this.testConnectionRepairScript(script)
    });

    // 文件未找到错误修复策略
    this.repairStrategies.set('FileNotFoundError', {
      name: 'File Not Found Repair',
      description: '修复文件缺失相关错误',
      priority: 'MEDIUM',
      estimatedTime: 15,
      steps: [
        'locate_missing_file',
        'check_backup_locations',
        'restore_from_backup',
        'create_default_file'
      ],
      generateScript: (context) => this.generateFileRepairScript(context),
      testScript: (script) => this.testFileRepairScript(script)
    });

    // 权限错误修复策略
    this.repairStrategies.set('PermissionError', {
      name: 'Permission Error Repair',
      description: '修复文件权限相关错误',
      priority: 'MEDIUM',
      estimatedTime: 10,
      steps: [
        'check_file_permissions',
        'identify_required_permissions',
        'fix_file_permissions',
        'verify_access'
      ],
      generateScript: (context) => this.generatePermissionRepairScript(context),
      testScript: (script) => this.testPermissionRepairScript(script)
    });

    // 内存错误修复策略
    this.repairStrategies.set('MemoryError', {
      name: 'Memory Error Repair',
      description: '修复内存不足相关错误',
      priority: 'HIGH',
      estimatedTime: 20,
      steps: [
        'check_memory_usage',
        'identify_memory_hogs',
        'clear_memory_cache',
        'restart_services_if_needed'
      ],
      generateScript: (context) => this.generateMemoryRepairScript(context),
      testScript: (script) => this.testMemoryRepairScript(script)
    });

    // 配置错误修复策略
    this.repairStrategies.set('ConfigurationError', {
      name: 'Configuration Error Repair',
      description: '修复配置文件相关错误',
      priority: 'MEDIUM',
      estimatedTime: 25,
      steps: [
        'validate_configuration',
        'backup_current_config',
        'restore_default_config',
        'test_configuration'
      ],
      generateScript: (context) => this.generateConfigRepairScript(context),
      testScript: (script) => this.testConfigRepairScript(script)
    });

    logger.info(`✅ 初始化了 ${this.repairStrategies.size} 个修复策略`);
  }

  /**
   * 接收外部错误信息并生成修复方案
   */
  async receiveExternalError(errorInfo) {
    try {
      logger.info(`🚨 接收到外部错误: ${errorInfo.error_type} - ${errorInfo.source}`);

      // 验证错误信息
      const validatedError = this.validateErrorInfo(errorInfo);
      if (!validatedError.isValid) {
        throw new Error(`Invalid error info: ${validatedError.reason}`);
      }

      // 生成修复请求ID
      const repairRequestId = uuidv4();

      // 创建修复请求
      const repairRequest = {
        id: repairRequestId,
        errorInfo: errorInfo,
        status: 'pending',
        createdAt: new Date().toISOString(),
        priority: this.calculatePriority(errorInfo),
        estimatedTime: 0,
        repairPlan: null,
        approvalRequired: this.config.requireUserApproval,
        sandboxTested: false
      };

      // 生成修复计划
      const repairPlan = await this.generateRepairPlan(errorInfo);
      repairRequest.repairPlan = repairPlan;
      repairRequest.estimatedTime = repairPlan.estimatedTime;

      // 添加到修复队列
      this.repairQueue.set(repairRequestId, repairRequest);

      // 记录到黑匣子
      await this.blackBox.recordFailure({
        source: SystemSource.CHRONICLE,
        function_name: 'receiveExternalError',
        error_type: 'RepairRequestCreated',
        error_message: `Created repair request for ${errorInfo.error_type}`,
        context: {
          repairRequestId,
          originalError: errorInfo,
          repairPlan: repairPlan
        },
        severity: FailureSeverity.MEDIUM
      });

      logger.info(`✅ 修复请求已创建: ${repairRequestId}`);

      return {
        success: true,
        repairRequestId: repairRequestId,
        repairPlan: repairPlan,
        requiresApproval: repairRequest.approvalRequired,
        estimatedTime: repairRequest.estimatedTime
      };

    } catch (error) {
      logger.error('❌ 处理外部错误失败:', error);
      
      await this.blackBox.recordFailure({
        source: SystemSource.CHRONICLE,
        function_name: 'receiveExternalError',
        error_type: error.constructor.name,
        error_message: error.message,
        context: { originalError: errorInfo },
        severity: FailureSeverity.HIGH
      });

      throw error;
    }
  }

  /**
   * 验证错误信息
   */
  validateErrorInfo(errorInfo) {
    if (!errorInfo) {
      return { isValid: false, reason: 'Error info is required' };
    }

    if (!errorInfo.error_type) {
      return { isValid: false, reason: 'Error type is required' };
    }

    if (!errorInfo.error_message) {
      return { isValid: false, reason: 'Error message is required' };
    }

    if (!errorInfo.source) {
      return { isValid: false, reason: 'Error source is required' };
    }

    if (!this.config.supportedErrorTypes.includes(errorInfo.error_type)) {
      return { isValid: false, reason: `Unsupported error type: ${errorInfo.error_type}` };
    }

    return { isValid: true };
  }

  /**
   * 计算修复优先级
   */
  calculatePriority(errorInfo) {
    const severity = errorInfo.severity || 'MEDIUM';
    const errorType = errorInfo.error_type;

    // 基于严重性的基础优先级
    let priority = 50;

    switch (severity) {
      case 'CRITICAL':
        priority = 90;
        break;
      case 'HIGH':
        priority = 70;
        break;
      case 'MEDIUM':
        priority = 50;
        break;
      case 'LOW':
        priority = 30;
        break;
    }

    // 基于错误类型的调整
    if (errorType === 'MemoryError' || errorType === 'ConnectionError') {
      priority += 20;
    } else if (errorType === 'FileNotFoundError' || errorType === 'PermissionError') {
      priority += 10;
    }

    return Math.min(100, priority);
  }

  /**
   * 生成修复计划
   */
  async generateRepairPlan(errorInfo) {
    try {
      const errorType = errorInfo.error_type;
      const strategy = this.repairStrategies.get(errorType);

      if (!strategy) {
        throw new Error(`No repair strategy found for error type: ${errorType}`);
      }

      // 生成修复脚本
      const repairScript = await strategy.generateScript(errorInfo);

      // 创建修复计划
      const repairPlan = {
        strategyName: strategy.name,
        description: strategy.description,
        priority: strategy.priority,
        estimatedTime: strategy.estimatedTime,
        steps: strategy.steps,
        repairScript: repairScript,
        testScript: null,
        riskLevel: this.assessRiskLevel(errorInfo, repairScript),
        backupRequired: this.isBackupRequired(errorInfo),
        rollbackPlan: this.generateRollbackPlan(errorInfo, repairScript)
      };

      // 生成测试脚本
      if (strategy.testScript) {
        repairPlan.testScript = await strategy.testScript(repairScript);
      }

      logger.info(`✅ 修复计划已生成: ${strategy.name}`);

      return repairPlan;

    } catch (error) {
      logger.error('❌ 生成修复计划失败:', error);
      throw error;
    }
  }

  /**
   * 生成连接修复脚本
   */
  generateConnectionRepairScript(errorInfo) {
    const context = errorInfo.context || {};
    const host = context.host || 'localhost';
    const port = context.port || '80';

    return {
      type: 'bash',
      content: `#!/bin/bash
# Chronicle自动生成的连接修复脚本
echo "🔧 开始修复连接错误..."
echo "目标: ${host}:${port}"
ping -c 3 ${host} > /dev/null 2>&1 && echo "✅ 网络连接正常" || echo "❌ 网络连接异常"
echo "🔧 连接修复脚本执行完成"
`,
      metadata: {
        errorType: errorInfo.error_type,
        targetHost: host,
        targetPort: port,
        generatedAt: new Date().toISOString()
      }
    };
  }

  /**
   * 生成文件修复脚本
   */
  generateFileRepairScript(errorInfo) {
    const context = errorInfo.context || {};
    const filePath = context.filePath || context.fileName || 'unknown';

    return {
      type: 'bash',
      content: `#!/bin/bash
# Chronicle自动生成的文件修复脚本
echo "🔧 开始修复文件缺失错误..."
echo "目标文件: ${filePath}"
[ -f "${filePath}" ] && echo "✅ 文件已存在" || echo "❌ 文件不存在，需要创建"
echo "🔧 文件修复脚本执行完成"
`,
      metadata: {
        errorType: errorInfo.error_type,
        targetFile: filePath,
        generatedAt: new Date().toISOString()
      }
    };
  }

  /**
   * 生成权限修复脚本
   */
  generatePermissionRepairScript(errorInfo) {
    const context = errorInfo.context || {};
    const filePath = context.filePath || context.fileName || 'unknown';

    return {
      type: 'bash',
      content: `#!/bin/bash
# Chronicle自动生成的权限修复脚本
echo "🔧 开始修复权限错误..."
echo "目标路径: ${filePath}"
[ -e "${filePath}" ] && ls -la "${filePath}" || echo "❌ 目标路径不存在"
echo "🔧 权限修复脚本执行完成"
`,
      metadata: {
        errorType: errorInfo.error_type,
        targetPath: filePath,
        generatedAt: new Date().toISOString()
      }
    };
  }

  /**
   * 生成内存修复脚本
   */
  generateMemoryRepairScript(errorInfo) {
    const context = errorInfo.context || {};
    const processName = context.processName || context.projectName || 'unknown';

    return {
      type: 'bash',
      content: `#!/bin/bash
# Chronicle自动生成的内存修复脚本
echo "🔧 开始修复内存错误..."
echo "目标进程: ${processName}"
free -h
echo "🔧 内存修复脚本执行完成"
`,
      metadata: {
        errorType: errorInfo.error_type,
        processName: processName,
        generatedAt: new Date().toISOString()
      }
    };
  }

  /**
   * 生成配置修复脚本
   */
  generateConfigRepairScript(errorInfo) {
    const context = errorInfo.context || {};
    const configFile = context.configFile || context.filePath || 'config.json';

    return {
      type: 'bash',
      content: `#!/bin/bash
# Chronicle自动生成的配置修复脚本
echo "🔧 开始修复配置错误..."
echo "配置文件: ${configFile}"
[ -f "${configFile}" ] && echo "✅ 配置文件存在" || echo "❌ 配置文件不存在"
echo "🔧 配置修复脚本执行完成"
`,
      metadata: {
        errorType: errorInfo.error_type,
        configFile: configFile,
        generatedAt: new Date().toISOString()
      }
    };
  }

  /**
   * 评估风险级别
   */
  assessRiskLevel(errorInfo, repairScript) {
    let riskScore = 0;

    // 基于错误类型的风险
    switch (errorInfo.error_type) {
      case 'MemoryError':
        riskScore += 30;
        break;
      case 'PermissionError':
        riskScore += 20;
        break;
      case 'ConfigurationError':
        riskScore += 25;
        break;
      case 'FileNotFoundError':
        riskScore += 15;
        break;
      case 'ConnectionError':
        riskScore += 10;
        break;
    }

    // 基于脚本内容的风险
    const scriptContent = repairScript.content.toLowerCase();
    if (scriptContent.includes('sudo') || scriptContent.includes('rm ')) {
      riskScore += 40;
    }
    if (scriptContent.includes('chmod') || scriptContent.includes('chown')) {
      riskScore += 20;
    }

    // 确定风险级别
    if (riskScore >= 70) {
      return 'HIGH';
    } else if (riskScore >= 40) {
      return 'MEDIUM';
    } else {
      return 'LOW';
    }
  }

  /**
   * 判断是否需要备份
   */
  isBackupRequired(errorInfo) {
    const highRiskTypes = ['ConfigurationError', 'PermissionError'];
    return highRiskTypes.includes(errorInfo.error_type);
  }

  /**
   * 生成回滚计划
   */
  generateRollbackPlan(errorInfo, repairScript) {
    return {
      description: '如果修复失败，可以执行以下回滚操作',
      steps: [
        '停止相关服务',
        '恢复备份文件',
        '重置权限设置',
        '重启服务',
        '验证系统状态'
      ],
      automaticRollback: false
    };
  }

  /**
   * 获取修复请求
   */
  getRepairRequest(repairRequestId) {
    return this.repairQueue.get(repairRequestId);
  }

  /**
   * 获取所有待处理的修复请求
   */
  getPendingRepairRequests() {
    const pending = [];
    for (const [id, request] of this.repairQueue) {
      if (request.status === 'pending') {
        pending.push({
          id: id,
          errorType: request.errorInfo.error_type,
          source: request.errorInfo.source,
          priority: request.priority,
          estimatedTime: request.estimatedTime,
          createdAt: request.createdAt,
          requiresApproval: request.approvalRequired
        });
      }
    }
    return pending.sort((a, b) => b.priority - a.priority);
  }

  /**
   * 获取修复服务状态
   */
  getServiceStatus() {
    const queueStats = {
      total: this.repairQueue.size,
      pending: 0,
      approved: 0,
      executing: 0,
      completed: 0,
      failed: 0
    };

    for (const request of this.repairQueue.values()) {
      queueStats[request.status]++;
    }

    return {
      isActive: true,
      config: this.config,
      queueStats: queueStats,
      supportedErrorTypes: this.config.supportedErrorTypes,
      availableStrategies: Array.from(this.repairStrategies.keys()),
      historySize: this.repairHistory.length,
      sandboxPath: this.sandboxPath
    };
  }
}

module.exports = CentralRepairService;