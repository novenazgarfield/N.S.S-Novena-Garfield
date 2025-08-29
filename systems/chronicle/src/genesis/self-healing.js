/**
 * 🌟 Chronicle自我修复系统 (Self-Healing System)
 * ===============================================
 * 
 * 从RAG系统剥离的"工程大脑" - Pantheon灵魂的Node.js版本
 * - 自我修复装饰器 (@aiSelfHealing)
 * - 透明观察窗 (代码透明化)
 * - 战地指挥官 (ReAct代理模式)
 * - 智慧汲取与成长能力
 * 
 * Author: N.S.S-Novena-Garfield Project
 * Version: 2.0.0 - "Chronicle Genesis Federation"
 */

const logger = require('../shared/logger');
const { getChronicleBlackBox, FailureStatus, SystemSource, FailureSeverity } = require('./black-box');

// 治疗策略枚举
const HealingStrategy = {
  RETRY_SIMPLE: 'retry_simple',
  AI_ANALYZE_FIX: 'ai_analyze_fix',
  FALLBACK_MODE: 'fallback_mode',
  EMERGENCY_STOP: 'emergency_stop'
};

// 任务复杂度枚举
const TaskComplexity = {
  SIMPLE: 'simple',
  MODERATE: 'moderate',
  COMPLEX: 'complex',
  CRITICAL: 'critical'
};

class HealingConfig {
  constructor({
    maxRetries = 3,
    retryDelay = 1000,
    enableAiHealing = true,
    enableTransparency = true,
    logHealingProcess = true,
    emergencyFallback = true
  } = {}) {
    this.maxRetries = maxRetries;
    this.retryDelay = retryDelay;
    this.enableAiHealing = enableAiHealing;
    this.enableTransparency = enableTransparency;
    this.logHealingProcess = logHealingProcess;
    this.emergencyFallback = emergencyFallback;
  }
}

class ExecutionTrace {
  constructor(functionName) {
    this.functionName = functionName;
    this.startTime = new Date();
    this.endTime = null;
    this.success = false;
    this.errorMessage = null;
    this.healingAttempts = 0;
    this.healingStrategy = null;
    this.codeTransparency = {};
    this.executionPlan = [];
  }
}

class ChronicleHealingSystem {
  constructor(config = null) {
    this.config = config || new HealingConfig();
    this.executionTraces = [];
    this.healingKnowledge = new Map();
    this.transparencyCache = new Map();
    this.blackBox = getChronicleBlackBox();
    
    logger.info('🌟 Chronicle自我修复系统已启动 - 中央医院治疗部门开始运营');
  }

  /**
   * 🧬 自我修复装饰器 - Node.js版本
   */
  aiSelfHealing({
    strategy = HealingStrategy.AI_ANALYZE_FIX,
    maxRetries = null,
    enableTransparency = null,
    source = SystemSource.CHRONICLE,
    severity = FailureSeverity.MEDIUM
  } = {}) {
    return (target, propertyKey, descriptor) => {
      const originalMethod = descriptor.value;
      const self = this;

      descriptor.value = async function(...args) {
        const retries = maxRetries || self.config.maxRetries;
        const transparency = enableTransparency !== null ? enableTransparency : self.config.enableTransparency;
        
        // 创建执行轨迹
        const trace = new ExecutionTrace(propertyKey);
        self.executionTraces.push(trace);

        let lastError = null;
        let attempt = 0;

        while (attempt <= retries) {
          try {
            // 透明化记录
            if (transparency) {
              trace.codeTransparency = {
                attempt: attempt + 1,
                maxRetries: retries + 1,
                strategy: strategy,
                args: args.length,
                timestamp: new Date().toISOString()
              };
            }

            // 执行原始方法
            const result = await originalMethod.apply(this, args);
            
            // 成功执行
            trace.success = true;
            trace.endTime = new Date();
            
            if (attempt > 0) {
              logger.info(`✅ 自我修复成功: ${propertyKey} (尝试 ${attempt + 1}/${retries + 1})`);
            }
            
            return result;

          } catch (error) {
            lastError = error;
            attempt++;
            trace.healingAttempts = attempt;

            // 记录故障到黑匣子
            const failureRecord = await self.blackBox.recordFailure({
              source: source,
              function_name: propertyKey,
              error_type: error.constructor.name,
              error_message: error.message,
              stack_trace: error.stack,
              context: {
                attempt: attempt,
                maxRetries: retries,
                args: args.length,
                strategy: strategy
              },
              severity: severity
            });

            if (attempt <= retries) {
              logger.warn(`🏥 自我修复尝试 ${attempt}/${retries + 1}: ${propertyKey} - ${error.message}`);
              
              // 请求治疗方案
              try {
                const healingPlan = await self.blackBox.requestHealing(failureRecord.id, strategy);
                trace.healingStrategy = healingPlan.strategy;

                // 根据治疗方案执行修复
                await self.executeHealingPlan(healingPlan, error);
                
                // 等待重试延迟
                if (healingPlan.delay > 0) {
                  await new Promise(resolve => setTimeout(resolve, healingPlan.delay));
                }
              } catch (healingError) {
                logger.error(`❌ 治疗方案执行失败: ${healingError.message}`);
              }
            }
          }
        }

        // 所有重试都失败了
        trace.success = false;
        trace.endTime = new Date();
        trace.errorMessage = lastError.message;

        logger.error(`💀 自我修复失败: ${propertyKey} - 已尝试 ${retries + 1} 次`);
        
        // 建立免疫（如果适用）
        if (self.shouldBuildImmunity(lastError)) {
          await self.buildImmunityForError(propertyKey, lastError, source);
        }

        throw lastError;
      };

      return descriptor;
    };
  }

  /**
   * 🏥 执行治疗方案
   */
  async executeHealingPlan(healingPlan, originalError) {
    switch (healingPlan.strategy) {
      case HealingStrategy.RETRY_SIMPLE:
        // 简单重试，无需特殊处理
        logger.info(`🔄 执行简单重试策略`);
        break;

      case HealingStrategy.AI_ANALYZE_FIX:
        // AI分析修复
        logger.info(`🤖 执行AI分析修复策略`);
        await this.performAiAnalysis(originalError, healingPlan);
        break;

      case HealingStrategy.FALLBACK_MODE:
        // 降级模式
        logger.info(`⬇️ 执行降级模式策略`);
        await this.activateFallbackMode(healingPlan);
        break;

      case HealingStrategy.EMERGENCY_STOP:
        // 紧急停止
        logger.error(`🚨 执行紧急停止策略`);
        throw new Error('Emergency stop activated due to critical failure');

      default:
        logger.warn(`⚠️ 未知治疗策略: ${healingPlan.strategy}`);
    }
  }

  /**
   * 🤖 执行AI分析
   */
  async performAiAnalysis(error, healingPlan) {
    // 这里可以集成AI服务来分析错误
    logger.info(`🧠 AI正在分析错误: ${error.message}`);
    
    // 模拟AI分析过程
    const analysisResult = {
      errorCategory: this.categorizeError(error),
      suggestedFix: this.suggestFix(error),
      confidence: 0.8
    };

    logger.info(`🎯 AI分析结果: ${analysisResult.errorCategory} (置信度: ${analysisResult.confidence})`);
    
    // 更新治疗知识库
    this.updateHealingKnowledge(error, analysisResult);
  }

  /**
   * ⬇️ 激活降级模式
   */
  async activateFallbackMode(healingPlan) {
    logger.info(`🛡️ 激活降级模式保护`);
    // 这里可以实现具体的降级逻辑
    // 例如：使用缓存数据、简化处理逻辑等
  }

  /**
   * 🏷️ 错误分类
   */
  categorizeError(error) {
    const errorType = error.constructor.name;
    const errorMessage = error.message.toLowerCase();

    if (errorMessage.includes('network') || errorMessage.includes('connection')) {
      return 'network_error';
    } else if (errorMessage.includes('timeout')) {
      return 'timeout_error';
    } else if (errorMessage.includes('permission') || errorMessage.includes('access')) {
      return 'permission_error';
    } else if (errorType === 'TypeError') {
      return 'type_error';
    } else if (errorType === 'ReferenceError') {
      return 'reference_error';
    } else {
      return 'unknown_error';
    }
  }

  /**
   * 💡 建议修复方案
   */
  suggestFix(error) {
    const category = this.categorizeError(error);
    
    const fixSuggestions = {
      'network_error': '检查网络连接，考虑重试或使用缓存',
      'timeout_error': '增加超时时间或优化处理逻辑',
      'permission_error': '检查文件权限或API访问权限',
      'type_error': '检查数据类型和参数传递',
      'reference_error': '检查变量定义和作用域',
      'unknown_error': '进行详细日志分析和代码审查'
    };

    return fixSuggestions[category] || '需要人工介入分析';
  }

  /**
   * 📚 更新治疗知识库
   */
  updateHealingKnowledge(error, analysisResult) {
    const errorSignature = `${error.constructor.name}:${error.message}`;
    
    if (!this.healingKnowledge.has(errorSignature)) {
      this.healingKnowledge.set(errorSignature, {
        occurrences: 0,
        successfulFixes: 0,
        analysisResults: []
      });
    }

    const knowledge = this.healingKnowledge.get(errorSignature);
    knowledge.occurrences++;
    knowledge.analysisResults.push(analysisResult);
    
    logger.info(`📚 更新治疗知识库: ${errorSignature} (出现 ${knowledge.occurrences} 次)`);
  }

  /**
   * 🛡️ 判断是否应该建立免疫
   */
  shouldBuildImmunity(error) {
    // 对于某些类型的错误，可以建立免疫
    const immuneableErrors = [
      'NetworkError',
      'TimeoutError',
      'PermissionError'
    ];
    
    return immuneableErrors.includes(error.constructor.name);
  }

  /**
   * 💉 为错误建立免疫
   */
  async buildImmunityForError(functionName, error, source) {
    try {
      const failureRecord = {
        source: source,
        function_name: functionName,
        error_type: error.constructor.name,
        error_message: error.message,
        immune_signature: `${source}:${functionName}:${error.constructor.name}:${error.message}`
      };

      const preventionStrategy = this.generatePreventionStrategy(error);
      await this.blackBox.buildImmunity(failureRecord, preventionStrategy);
      
      logger.info(`💉 已为 ${functionName} 建立免疫: ${error.constructor.name}`);
    } catch (immunityError) {
      logger.error(`❌ 建立免疫失败: ${immunityError.message}`);
    }
  }

  /**
   * 🛡️ 生成预防策略
   */
  generatePreventionStrategy(error) {
    const category = this.categorizeError(error);
    
    const preventionStrategies = {
      'network_error': 'auto_retry_with_exponential_backoff',
      'timeout_error': 'increase_timeout_threshold',
      'permission_error': 'validate_permissions_before_execution',
      'type_error': 'add_type_validation',
      'reference_error': 'add_existence_check',
      'unknown_error': 'enable_detailed_logging'
    };

    return preventionStrategies[category] || 'manual_review_required';
  }

  /**
   * 📊 获取治疗统计
   */
  getHealingStats() {
    const totalTraces = this.executionTraces.length;
    const successfulTraces = this.executionTraces.filter(t => t.success).length;
    const healedTraces = this.executionTraces.filter(t => t.healingAttempts > 0 && t.success).length;
    
    return {
      totalExecutions: totalTraces,
      successfulExecutions: successfulTraces,
      healedExecutions: healedTraces,
      successRate: totalTraces > 0 ? (successfulTraces / totalTraces) : 0,
      healingSuccessRate: healedTraces > 0 ? (healedTraces / this.executionTraces.filter(t => t.healingAttempts > 0).length) : 0,
      knowledgeBaseSize: this.healingKnowledge.size
    };
  }

  /**
   * 🧹 清理执行轨迹
   */
  cleanupTraces(maxTraces = 1000) {
    if (this.executionTraces.length > maxTraces) {
      const removed = this.executionTraces.splice(0, this.executionTraces.length - maxTraces);
      logger.info(`🧹 清理了 ${removed.length} 条执行轨迹`);
    }
  }
}

// 单例模式
let chronicleHealingSystemInstance = null;

function getChronicleHealingSystem(config = null) {
  if (!chronicleHealingSystemInstance) {
    chronicleHealingSystemInstance = new ChronicleHealingSystem(config);
  }
  return chronicleHealingSystemInstance;
}

// 便捷的装饰器函数
function aiSelfHealing(options = {}) {
  const healingSystem = getChronicleHealingSystem();
  return healingSystem.aiSelfHealing(options);
}

module.exports = {
  ChronicleHealingSystem,
  HealingConfig,
  ExecutionTrace,
  HealingStrategy,
  TaskComplexity,
  getChronicleHealingSystem,
  aiSelfHealing
};