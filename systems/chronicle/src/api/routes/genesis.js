/**
 * 🏥 Chronicle Genesis API路由 - 中央医院API接口
 * ===============================================
 * 
 * 为RAG系统提供"求救"接口：
 * - POST /api/log_failure - 记录故障
 * - POST /api/request_healing - 请求治疗
 * - GET /api/health_report - 获取健康报告
 * - GET /api/failure_stats - 获取故障统计
 * 
 * Author: N.S.S-Novena-Garfield Project
 * Version: 2.0.0 - "Chronicle Genesis Federation"
 */

const express = require('express');
const router = express.Router();
const logger = require('../../shared/logger');
const { getChronicleBlackBox, SystemSource, FailureSeverity } = require('../../genesis/black-box');
const { getChronicleHealingSystem } = require('../../genesis/self-healing');

// 初始化系统
const blackBox = getChronicleBlackBox();
const healingSystem = getChronicleHealingSystem();

/**
 * 🚨 POST /api/log_failure - 记录故障 (RAG系统求救接口)
 */
router.post('/log_failure', async (req, res) => {
  try {
    const {
      source = SystemSource.UNKNOWN,
      function_name = '',
      error_type = '',
      error_message = '',
      stack_trace = '',
      context = {},
      severity = FailureSeverity.MEDIUM
    } = req.body;

    // 验证必需参数
    if (!function_name || !error_message) {
      return res.status(400).json({
        success: false,
        error: 'function_name and error_message are required',
        code: 'MISSING_REQUIRED_FIELDS'
      });
    }

    // 记录故障到黑匣子
    const failureRecord = await blackBox.recordFailure({
      source,
      function_name,
      error_type,
      error_message,
      stack_trace,
      context,
      severity,
      timestamp: new Date()
    });

    logger.info(`🚨 收到故障求救信号: ${source}:${function_name} - ${error_message}`);

    res.json({
      success: true,
      message: '故障已记录到中央医院',
      data: {
        failure_id: failureRecord.id,
        immune_signature: failureRecord.immune_signature,
        timestamp: failureRecord.timestamp,
        status: failureRecord.status
      }
    });

  } catch (error) {
    logger.error('❌ 记录故障失败:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to log failure',
      message: error.message,
      code: 'LOG_FAILURE_ERROR'
    });
  }
});

/**
 * 🏥 POST /api/request_healing - 请求治疗 (RAG系统求救接口)
 */
router.post('/request_healing', async (req, res) => {
  try {
    const {
      failure_id,
      healing_strategy = null,
      source = SystemSource.UNKNOWN,
      function_name = '',
      error_type = '',
      error_message = '',
      context = {}
    } = req.body;

    let healingPlan;

    if (failure_id) {
      // 基于已记录的故障ID请求治疗
      healingPlan = await blackBox.requestHealing(failure_id, healing_strategy);
    } else if (function_name && error_message) {
      // 直接请求治疗（先记录故障）
      const failureRecord = await blackBox.recordFailure({
        source,
        function_name,
        error_type,
        error_message,
        context,
        severity: FailureSeverity.MEDIUM
      });

      healingPlan = await blackBox.requestHealing(failureRecord.id, healing_strategy);
    } else {
      return res.status(400).json({
        success: false,
        error: 'Either failure_id or (function_name + error_message) is required',
        code: 'MISSING_REQUIRED_FIELDS'
      });
    }

    logger.info(`🏥 提供治疗方案: ${healingPlan.strategy} (故障ID: ${healingPlan.failure_id})`);

    res.json({
      success: true,
      message: '中央医院已提供治疗方案',
      data: {
        healing_plan: healingPlan,
        recommendations: generateHealingRecommendations(healingPlan),
        estimated_success_rate: healingPlan.success_rate || 0.8
      }
    });

  } catch (error) {
    logger.error('❌ 请求治疗失败:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to request healing',
      message: error.message,
      code: 'REQUEST_HEALING_ERROR'
    });
  }
});

/**
 * 📊 GET /api/health_report - 获取系统健康报告
 */
router.get('/health_report', async (req, res) => {
  try {
    const { source } = req.query;
    
    const healthReport = await blackBox.getHealthReport(source);
    const healingStats = healingSystem.getHealingStats();
    const failureStats = await blackBox.getFailureStats('24h');

    const overallHealth = calculateOverallHealth(healthReport, healingStats, failureStats);

    res.json({
      success: true,
      message: '系统健康报告',
      data: {
        overall_health: overallHealth,
        system_reports: healthReport,
        healing_statistics: healingStats,
        failure_statistics: failureStats,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    logger.error('❌ 获取健康报告失败:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get health report',
      message: error.message,
      code: 'HEALTH_REPORT_ERROR'
    });
  }
});

/**
 * 📈 GET /api/failure_stats - 获取故障统计
 */
router.get('/failure_stats', async (req, res) => {
  try {
    const { time_range = '24h', source } = req.query;
    
    const stats = await blackBox.getFailureStats(time_range);
    const healthReport = await blackBox.getHealthReport(source);

    res.json({
      success: true,
      message: '故障统计报告',
      data: {
        time_range: time_range,
        statistics: stats,
        system_breakdown: healthReport,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    logger.error('❌ 获取故障统计失败:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get failure stats',
      message: error.message,
      code: 'FAILURE_STATS_ERROR'
    });
  }
});

/**
 * 💉 POST /api/build_immunity - 建立免疫
 */
router.post('/build_immunity', async (req, res) => {
  try {
    const {
      source,
      function_name,
      error_type,
      error_message,
      prevention_strategy
    } = req.body;

    if (!source || !function_name || !error_type) {
      return res.status(400).json({
        success: false,
        error: 'source, function_name, and error_type are required',
        code: 'MISSING_REQUIRED_FIELDS'
      });
    }

    const failureRecord = {
      source,
      function_name,
      error_type,
      error_message,
      immune_signature: `${source}:${function_name}:${error_type}:${error_message}`
    };

    await blackBox.buildImmunity(failureRecord, prevention_strategy);

    res.json({
      success: true,
      message: '免疫已建立',
      data: {
        immune_signature: failureRecord.immune_signature,
        prevention_strategy: prevention_strategy
      }
    });

  } catch (error) {
    logger.error('❌ 建立免疫失败:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to build immunity',
      message: error.message,
      code: 'BUILD_IMMUNITY_ERROR'
    });
  }
});

/**
 * 🔍 GET /api/immunity_status - 检查免疫状态
 */
router.get('/immunity_status', async (req, res) => {
  try {
    const { immune_signature } = req.query;

    if (!immune_signature) {
      return res.status(400).json({
        success: false,
        error: 'immune_signature is required',
        code: 'MISSING_REQUIRED_FIELDS'
      });
    }

    const isImmune = await blackBox.checkImmunity(immune_signature);

    res.json({
      success: true,
      message: '免疫状态检查完成',
      data: {
        immune_signature: immune_signature,
        is_immune: isImmune,
        status: isImmune ? 'immune' : 'vulnerable'
      }
    });

  } catch (error) {
    logger.error('❌ 检查免疫状态失败:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to check immunity status',
      message: error.message,
      code: 'IMMUNITY_STATUS_ERROR'
    });
  }
});

/**
 * 🧹 POST /api/cleanup - 清理过期记录
 */
router.post('/cleanup', async (req, res) => {
  try {
    const { days_to_keep = 30 } = req.body;
    
    const cleanedRecords = await blackBox.cleanupOldRecords(days_to_keep);
    healingSystem.cleanupTraces();

    res.json({
      success: true,
      message: '清理完成',
      data: {
        cleaned_records: cleanedRecords,
        days_kept: days_to_keep
      }
    });

  } catch (error) {
    logger.error('❌ 清理失败:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to cleanup',
      message: error.message,
      code: 'CLEANUP_ERROR'
    });
  }
});

// 辅助函数

/**
 * 生成治疗建议
 */
function generateHealingRecommendations(healingPlan) {
  const recommendations = [];

  switch (healingPlan.strategy) {
    case 'retry_simple':
      recommendations.push('建议在重试前检查网络连接');
      recommendations.push('考虑增加重试间隔时间');
      break;
    case 'ai_analyze_fix':
      recommendations.push('AI正在分析错误模式');
      recommendations.push('建议收集更多上下文信息');
      break;
    case 'fallback_mode':
      recommendations.push('系统将使用降级模式运行');
      recommendations.push('功能可能受限，但保证基本可用');
      break;
    case 'emergency_stop':
      recommendations.push('检测到严重错误，建议人工介入');
      recommendations.push('停止相关操作以防止数据损坏');
      break;
    default:
      recommendations.push('使用默认修复策略');
  }

  return recommendations;
}

/**
 * 计算整体健康度
 */
function calculateOverallHealth(healthReport, healingStats, failureStats) {
  let totalScore = 100;

  // 基于故障率扣分
  if (failureStats.total_failures > 0) {
    const failureRate = failureStats.total_failures / (failureStats.total_failures + healingStats.successfulExecutions || 1);
    totalScore -= failureRate * 50;
  }

  // 基于修复成功率加分
  if (healingStats.healingSuccessRate > 0) {
    totalScore += healingStats.healingSuccessRate * 10;
  }

  // 基于免疫系统加分
  if (failureStats.immune_count > 0) {
    totalScore += Math.min(failureStats.immune_count * 2, 20);
  }

  return {
    score: Math.max(0, Math.min(100, Math.round(totalScore))),
    status: totalScore >= 80 ? 'excellent' : totalScore >= 60 ? 'good' : totalScore >= 40 ? 'fair' : 'poor',
    factors: {
      failure_rate: failureStats.total_failures > 0 ? (failureStats.total_failures / (failureStats.total_failures + healingStats.successfulExecutions || 1)) : 0,
      healing_success_rate: healingStats.healingSuccessRate,
      immune_responses: failureStats.immune_count || 0
    }
  };
}

module.exports = router;