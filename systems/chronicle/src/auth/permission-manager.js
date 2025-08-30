/**
 * 🔐 Chronicle权限管理器 (Permission Manager)
 * ============================================
 * 
 * 第二章："权力"的"制衡" - 权限最小化与提权申请
 * 
 * 核心法则：安全是第一性原理
 * 
 * 功能：
 * - 默认只读权限管理
 * - 提权申请流程
 * - 权限验证和授权
 * - 操作审计日志
 * 
 * 安全原则：
 * - 最小权限原则 (Principle of Least Privilege)
 * - 显式授权 (Explicit Authorization)
 * - 操作审计 (Operation Auditing)
 * - 时限控制 (Time-limited Permissions)
 * 
 * Author: N.S.S-Novena-Garfield Project
 * Version: 3.0.0 - "The Great Expansion"
 */

const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const logger = require('../shared/logger');
const { getChronicleBlackBox, SystemSource, FailureSeverity } = require('../genesis/black-box');

class PermissionManager {
  constructor() {
    this.permissions = new Map();
    this.pendingRequests = new Map();
    this.grantedPermissions = new Map();
    this.auditLog = [];
    
    // 权限配置
    this.config = {
      defaultPermissions: ['read'],           // 默认只读权限
      requireApprovalFor: [                   // 需要批准的操作
        'write',
        'execute',
        'delete',
        'modify_permissions',
        'system_command',
        'file_create',
        'file_modify',
        'file_delete',
        'service_restart',
        'config_change'
      ],
      permissionTimeout: 3600000,             // 权限超时时间 1小时
      maxPendingRequests: 50,                 // 最大待处理请求数
      auditLogMaxSize: 10000,                 // 审计日志最大条数
      allowedPaths: [                         // 允许操作的路径
        path.resolve(__dirname, '../../../../systems'),
        '/tmp/chronicle-sandbox'
      ],
      restrictedPaths: [                      // 受限路径
        '/etc',
        '/root',
        '/home/*/.ssh',
        '/var/lib',
        '/usr/bin',
        '/usr/sbin'
      ]
    };

    this.blackBox = getChronicleBlackBox();
    
    // 初始化默认权限
    this.initializeDefaultPermissions();
    
    logger.info('🔐 权限管理器初始化完成');
  }

  /**
   * 初始化默认权限
   */
  initializeDefaultPermissions() {
    // Chronicle系统默认权限
    this.permissions.set('chronicle_system', {
      permissions: this.config.defaultPermissions,
      paths: this.config.allowedPaths,
      restrictions: this.config.restrictedPaths,
      createdAt: new Date().toISOString(),
      source: 'system_default'
    });

    logger.info('✅ 默认权限已初始化');
  }

  /**
   * 检查权限
   */
  async checkPermission(operation, targetPath = null, context = {}) {
    try {
      const subject = context.subject || 'chronicle_system';
      const userPermissions = this.permissions.get(subject);

      if (!userPermissions) {
        return {
          allowed: false,
          reason: 'No permissions found for subject',
          requiresApproval: true
        };
      }

      // 检查操作权限
      if (!userPermissions.permissions.includes(operation)) {
        return {
          allowed: false,
          reason: `Operation '${operation}' not permitted`,
          requiresApproval: this.config.requireApprovalFor.includes(operation)
        };
      }

      // 检查路径权限
      if (targetPath) {
        const pathAllowed = this.checkPathPermission(targetPath, userPermissions);
        if (!pathAllowed.allowed) {
          return {
            allowed: false,
            reason: pathAllowed.reason,
            requiresApproval: true
          };
        }
      }

      // 记录权限检查
      await this.logPermissionCheck(subject, operation, targetPath, true, context);

      return {
        allowed: true,
        reason: 'Permission granted'
      };

    } catch (error) {
      logger.error('❌ 权限检查失败:', error);
      
      await this.blackBox.recordFailure({
        source: SystemSource.CHRONICLE,
        function_name: 'checkPermission',
        error_type: error.constructor.name,
        error_message: error.message,
        context: { operation, targetPath, context },
        severity: FailureSeverity.MEDIUM
      });

      return {
        allowed: false,
        reason: `Permission check failed: ${error.message}`,
        requiresApproval: true
      };
    }
  }

  /**
   * 检查路径权限
   */
  checkPathPermission(targetPath, userPermissions) {
    // 检查是否在允许的路径中
    const isAllowed = userPermissions.paths.some(allowedPath => {
      return targetPath.startsWith(allowedPath);
    });

    if (!isAllowed) {
      return {
        allowed: false,
        reason: `Path '${targetPath}' is not in allowed paths`
      };
    }

    // 检查是否在受限路径中
    const isRestricted = userPermissions.restrictions.some(restrictedPath => {
      // 处理通配符
      if (restrictedPath.includes('*')) {
        const pattern = restrictedPath.replace(/\*/g, '.*');
        const regex = new RegExp(`^${pattern}`);
        return regex.test(targetPath);
      }
      return targetPath.startsWith(restrictedPath);
    });

    if (isRestricted) {
      return {
        allowed: false,
        reason: `Path '${targetPath}' is restricted`
      };
    }

    return {
      allowed: true,
      reason: 'Path permission granted'
    };
  }

  /**
   * 创建提权申请
   */
  async createPermissionRequest(requestInfo) {
    try {
      logger.info(`🔐 创建提权申请: ${requestInfo.operation}`);

      // 验证请求信息
      const validation = this.validatePermissionRequest(requestInfo);
      if (!validation.isValid) {
        throw new Error(`Invalid permission request: ${validation.reason}`);
      }

      // 检查待处理请求数量
      if (this.pendingRequests.size >= this.config.maxPendingRequests) {
        throw new Error('Too many pending permission requests');
      }

      // 生成请求ID
      const requestId = uuidv4();

      // 创建权限请求
      const permissionRequest = {
        id: requestId,
        operation: requestInfo.operation,
        targetPath: requestInfo.targetPath,
        reason: requestInfo.reason,
        context: requestInfo.context || {},
        subject: requestInfo.subject || 'chronicle_system',
        requestedBy: requestInfo.requestedBy || 'system',
        status: 'pending',
        createdAt: new Date().toISOString(),
        expiresAt: new Date(Date.now() + this.config.permissionTimeout).toISOString(),
        riskLevel: this.assessRiskLevel(requestInfo),
        approvalRequired: true,
        repairScript: requestInfo.repairScript || null
      };

      // 添加到待处理队列
      this.pendingRequests.set(requestId, permissionRequest);

      // 记录到审计日志
      await this.logPermissionRequest(permissionRequest);

      // 记录到黑匣子
      await this.blackBox.recordFailure({
        source: SystemSource.CHRONICLE,
        function_name: 'createPermissionRequest',
        error_type: 'PermissionRequestCreated',
        error_message: `Permission request created for ${requestInfo.operation}`,
        context: {
          requestId,
          operation: requestInfo.operation,
          targetPath: requestInfo.targetPath,
          riskLevel: permissionRequest.riskLevel
        },
        severity: FailureSeverity.MEDIUM
      });

      logger.info(`✅ 提权申请已创建: ${requestId}`);

      return {
        success: true,
        requestId: requestId,
        permissionRequest: permissionRequest,
        requiresUserApproval: true
      };

    } catch (error) {
      logger.error('❌ 创建提权申请失败:', error);
      
      await this.blackBox.recordFailure({
        source: SystemSource.CHRONICLE,
        function_name: 'createPermissionRequest',
        error_type: error.constructor.name,
        error_message: error.message,
        context: { requestInfo },
        severity: FailureSeverity.HIGH
      });

      throw error;
    }
  }

  /**
   * 验证权限请求
   */
  validatePermissionRequest(requestInfo) {
    if (!requestInfo) {
      return { isValid: false, reason: 'Request info is required' };
    }

    if (!requestInfo.operation) {
      return { isValid: false, reason: 'Operation is required' };
    }

    if (!requestInfo.reason) {
      return { isValid: false, reason: 'Reason is required' };
    }

    if (requestInfo.targetPath && !this.isPathAllowedForRequest(requestInfo.targetPath)) {
      return { isValid: false, reason: 'Target path is not allowed for requests' };
    }

    return { isValid: true };
  }

  /**
   * 检查路径是否允许请求
   */
  isPathAllowedForRequest(targetPath) {
    // 检查是否在完全禁止的路径中
    const forbiddenPaths = [
      '/etc/passwd',
      '/etc/shadow',
      '/root',
      '/boot',
      '/sys',
      '/proc'
    ];

    return !forbiddenPaths.some(forbidden => targetPath.startsWith(forbidden));
  }

  /**
   * 评估风险级别
   */
  assessRiskLevel(requestInfo) {
    let riskScore = 0;

    // 基于操作类型的风险
    const operationRisks = {
      'delete': 40,
      'file_delete': 35,
      'system_command': 50,
      'service_restart': 30,
      'modify_permissions': 45,
      'config_change': 25,
      'file_modify': 20,
      'file_create': 15,
      'write': 10,
      'execute': 20
    };

    riskScore += operationRisks[requestInfo.operation] || 10;

    // 基于目标路径的风险
    if (requestInfo.targetPath) {
      if (requestInfo.targetPath.startsWith('/etc')) {
        riskScore += 30;
      } else if (requestInfo.targetPath.startsWith('/usr')) {
        riskScore += 20;
      } else if (requestInfo.targetPath.startsWith('/var')) {
        riskScore += 15;
      }
    }

    // 基于修复脚本内容的风险
    if (requestInfo.repairScript) {
      const scriptContent = requestInfo.repairScript.content.toLowerCase();
      if (scriptContent.includes('sudo') || scriptContent.includes('su ')) {
        riskScore += 40;
      }
      if (scriptContent.includes('rm -rf') || scriptContent.includes('rm -f')) {
        riskScore += 35;
      }
      if (scriptContent.includes('chmod') || scriptContent.includes('chown')) {
        riskScore += 20;
      }
    }

    // 确定风险级别
    if (riskScore >= 70) {
      return 'CRITICAL';
    } else if (riskScore >= 50) {
      return 'HIGH';
    } else if (riskScore >= 30) {
      return 'MEDIUM';
    } else {
      return 'LOW';
    }
  }

  /**
   * 处理权限批准
   */
  async approvePermissionRequest(requestId, approvalInfo = {}) {
    try {
      logger.info(`✅ 处理权限批准: ${requestId}`);

      const request = this.pendingRequests.get(requestId);
      if (!request) {
        throw new Error(`Permission request not found: ${requestId}`);
      }

      if (request.status !== 'pending') {
        throw new Error(`Permission request is not pending: ${request.status}`);
      }

      // 检查是否过期
      if (new Date() > new Date(request.expiresAt)) {
        request.status = 'expired';
        throw new Error('Permission request has expired');
      }

      // 更新请求状态
      request.status = 'approved';
      request.approvedAt = new Date().toISOString();
      request.approvedBy = approvalInfo.approvedBy || 'user';
      request.approvalReason = approvalInfo.reason || 'User approved';

      // 授予临时权限
      const grantedPermission = await this.grantTemporaryPermission(request);

      // 从待处理队列移除
      this.pendingRequests.delete(requestId);

      // 记录到审计日志
      await this.logPermissionApproval(request, grantedPermission);

      logger.info(`✅ 权限已批准: ${requestId}`);

      return {
        success: true,
        requestId: requestId,
        grantedPermission: grantedPermission,
        message: 'Permission approved and granted'
      };

    } catch (error) {
      logger.error(`❌ 权限批准失败: ${requestId}`, error);
      throw error;
    }
  }

  /**
   * 拒绝权限请求
   */
  async denyPermissionRequest(requestId, denialInfo = {}) {
    try {
      logger.info(`❌ 拒绝权限请求: ${requestId}`);

      const request = this.pendingRequests.get(requestId);
      if (!request) {
        throw new Error(`Permission request not found: ${requestId}`);
      }

      // 更新请求状态
      request.status = 'denied';
      request.deniedAt = new Date().toISOString();
      request.deniedBy = denialInfo.deniedBy || 'user';
      request.denialReason = denialInfo.reason || 'User denied';

      // 从待处理队列移除
      this.pendingRequests.delete(requestId);

      // 记录到审计日志
      await this.logPermissionDenial(request);

      logger.info(`✅ 权限请求已拒绝: ${requestId}`);

      return {
        success: true,
        requestId: requestId,
        message: 'Permission request denied'
      };

    } catch (error) {
      logger.error(`❌ 拒绝权限请求失败: ${requestId}`, error);
      throw error;
    }
  }

  /**
   * 授予临时权限
   */
  async grantTemporaryPermission(request) {
    const permissionId = uuidv4();
    const expiresAt = new Date(Date.now() + this.config.permissionTimeout);

    const grantedPermission = {
      id: permissionId,
      subject: request.subject,
      operation: request.operation,
      targetPath: request.targetPath,
      grantedAt: new Date().toISOString(),
      expiresAt: expiresAt.toISOString(),
      requestId: request.id,
      riskLevel: request.riskLevel,
      used: false,
      usedAt: null
    };

    this.grantedPermissions.set(permissionId, grantedPermission);

    // 设置自动过期
    setTimeout(() => {
      this.revokePermission(permissionId);
    }, this.config.permissionTimeout);

    return grantedPermission;
  }

  /**
   * 撤销权限
   */
  async revokePermission(permissionId) {
    try {
      const permission = this.grantedPermissions.get(permissionId);
      if (permission) {
        this.grantedPermissions.delete(permissionId);
        await this.logPermissionRevocation(permission);
        logger.debug(`🔐 权限已撤销: ${permissionId}`);
      }
    } catch (error) {
      logger.error(`❌ 撤销权限失败: ${permissionId}`, error);
    }
  }

  /**
   * 获取待处理的权限请求
   */
  getPendingPermissionRequests() {
    const pending = [];
    
    for (const [id, request] of this.pendingRequests) {
      if (request.status === 'pending' && new Date() < new Date(request.expiresAt)) {
        pending.push({
          id: id,
          operation: request.operation,
          targetPath: request.targetPath,
          reason: request.reason,
          riskLevel: request.riskLevel,
          createdAt: request.createdAt,
          expiresAt: request.expiresAt,
          repairScript: request.repairScript ? {
            type: request.repairScript.type,
            content: request.repairScript.content,
            metadata: request.repairScript.metadata
          } : null
        });
      }
    }

    return pending.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
  }

  /**
   * 记录权限检查
   */
  async logPermissionCheck(subject, operation, targetPath, allowed, context) {
    const logEntry = {
      type: 'permission_check',
      subject: subject,
      operation: operation,
      targetPath: targetPath,
      allowed: allowed,
      context: context,
      timestamp: new Date().toISOString()
    };

    this.addToAuditLog(logEntry);
  }

  /**
   * 记录权限请求
   */
  async logPermissionRequest(request) {
    const logEntry = {
      type: 'permission_request',
      requestId: request.id,
      operation: request.operation,
      targetPath: request.targetPath,
      reason: request.reason,
      riskLevel: request.riskLevel,
      timestamp: request.createdAt
    };

    this.addToAuditLog(logEntry);
  }

  /**
   * 记录权限批准
   */
  async logPermissionApproval(request, grantedPermission) {
    const logEntry = {
      type: 'permission_approval',
      requestId: request.id,
      permissionId: grantedPermission.id,
      operation: request.operation,
      approvedBy: request.approvedBy,
      timestamp: request.approvedAt
    };

    this.addToAuditLog(logEntry);
  }

  /**
   * 记录权限拒绝
   */
  async logPermissionDenial(request) {
    const logEntry = {
      type: 'permission_denial',
      requestId: request.id,
      operation: request.operation,
      deniedBy: request.deniedBy,
      denialReason: request.denialReason,
      timestamp: request.deniedAt
    };

    this.addToAuditLog(logEntry);
  }

  /**
   * 记录权限撤销
   */
  async logPermissionRevocation(permission) {
    const logEntry = {
      type: 'permission_revocation',
      permissionId: permission.id,
      operation: permission.operation,
      reason: 'expired',
      timestamp: new Date().toISOString()
    };

    this.addToAuditLog(logEntry);
  }

  /**
   * 添加到审计日志
   */
  addToAuditLog(logEntry) {
    this.auditLog.push(logEntry);

    // 限制审计日志大小
    if (this.auditLog.length > this.config.auditLogMaxSize) {
      this.auditLog = this.auditLog.slice(-this.config.auditLogMaxSize);
    }
  }

  /**
   * 获取权限管理器状态
   */
  getPermissionManagerStatus() {
    return {
      isActive: true,
      config: this.config,
      stats: {
        totalPermissions: this.permissions.size,
        pendingRequests: this.pendingRequests.size,
        grantedPermissions: this.grantedPermissions.size,
        auditLogEntries: this.auditLog.length
      },
      pendingRequests: this.getPendingPermissionRequests(),
      recentAuditEntries: this.auditLog.slice(-10)
    };
  }
}

module.exports = PermissionManager;