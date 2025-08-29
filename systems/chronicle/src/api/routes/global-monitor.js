/**
 * 🌍 Chronicle全系统监控API路由
 * ===============================
 * 
 * 提供全系统监控的API接口：
 * - POST /api/global/start - 启动全系统监控
 * - POST /api/global/stop - 停止全系统监控
 * - GET /api/global/status - 获取监控状态
 * - GET /api/global/projects - 获取项目列表
 * - GET /api/global/system-health - 获取系统健康状态
 * - POST /api/global/project/:name/restart - 重启指定项目
 * 
 * Author: N.S.S-Novena-Garfield Project
 * Version: 2.0.0 - "Global Federation"
 */

const express = require('express');
const router = express.Router();
const logger = require('../../shared/logger');
const GlobalSystemMonitor = require('../../system-monitor/global-monitor');

// 全局监控器实例
let globalMonitor = null;

/**
 * 获取或创建全局监控器实例
 */
function getGlobalMonitor() {
  if (!globalMonitor) {
    globalMonitor = new GlobalSystemMonitor();
  }
  return globalMonitor;
}

/**
 * 🚀 POST /api/global/start - 启动全系统监控
 */
router.post('/start', async (req, res) => {
  try {
    logger.info('🚀 收到启动全系统监控请求');

    const monitor = getGlobalMonitor();
    const result = await monitor.startGlobalMonitoring();

    res.json({
      success: true,
      message: 'Chronicle全系统监控已启动',
      data: result
    });

  } catch (error) {
    logger.error('❌ 启动全系统监控失败:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start global monitoring',
      message: error.message,
      code: 'GLOBAL_MONITOR_START_ERROR'
    });
  }
});

/**
 * 🛑 POST /api/global/stop - 停止全系统监控
 */
router.post('/stop', async (req, res) => {
  try {
    logger.info('🛑 收到停止全系统监控请求');

    const monitor = getGlobalMonitor();
    const result = await monitor.stopGlobalMonitoring();

    res.json({
      success: true,
      message: 'Chronicle全系统监控已停止',
      data: result
    });

  } catch (error) {
    logger.error('❌ 停止全系统监控失败:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to stop global monitoring',
      message: error.message,
      code: 'GLOBAL_MONITOR_STOP_ERROR'
    });
  }
});

/**
 * 📊 GET /api/global/status - 获取监控状态
 */
router.get('/status', async (req, res) => {
  try {
    const monitor = getGlobalMonitor();
    const status = monitor.getMonitoringStatus();

    res.json({
      success: true,
      message: '全系统监控状态',
      data: {
        monitoring_status: status,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    logger.error('❌ 获取监控状态失败:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get monitoring status',
      message: error.message,
      code: 'GLOBAL_MONITOR_STATUS_ERROR'
    });
  }
});

/**
 * 📁 GET /api/global/projects - 获取项目列表
 */
router.get('/projects', async (req, res) => {
  try {
    const monitor = getGlobalMonitor();
    const status = monitor.getMonitoringStatus();

    const projectDetails = [];
    for (const [projectName, config] of monitor.projectConfigs) {
      projectDetails.push({
        name: projectName,
        type: config.type,
        language: config.language,
        framework: config.framework,
        path: config.path,
        criticalFiles: config.criticalFiles,
        logPaths: config.logPaths,
        healthCheckEndpoint: config.healthCheckEndpoint,
        monitoringEnabled: config.monitoringEnabled,
        isMonitored: status.projectWatchers.includes(projectName)
      });
    }

    res.json({
      success: true,
      message: '项目列表',
      data: {
        total_projects: projectDetails.length,
        monitored_projects: status.projectWatchers.length,
        projects: projectDetails,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    logger.error('❌ 获取项目列表失败:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get projects list',
      message: error.message,
      code: 'GLOBAL_MONITOR_PROJECTS_ERROR'
    });
  }
});

/**
 * 🏥 GET /api/global/system-health - 获取系统健康状态
 */
router.get('/system-health', async (req, res) => {
  try {
    const monitor = getGlobalMonitor();
    const status = monitor.getMonitoringStatus();

    // 获取系统资源信息
    const systemResources = await monitor.getSystemResources();

    // 计算整体健康分数
    const healthScore = calculateSystemHealthScore(systemResources, status);

    res.json({
      success: true,
      message: '系统健康状态',
      data: {
        overall_health: {
          score: healthScore.score,
          status: healthScore.status,
          level: healthScore.level
        },
        system_resources: systemResources,
        monitoring_status: {
          is_monitoring: status.isMonitoring,
          monitored_projects: status.monitoredProjects.length,
          active_watchers: status.systemWatchers.length
        },
        system_info: status.systemInfo,
        recommendations: generateHealthRecommendations(healthScore, systemResources),
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    logger.error('❌ 获取系统健康状态失败:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get system health',
      message: error.message,
      code: 'GLOBAL_MONITOR_HEALTH_ERROR'
    });
  }
});

/**
 * 🔄 POST /api/global/project/:name/restart - 重启指定项目
 */
router.post('/project/:name/restart', async (req, res) => {
  try {
    const { name: projectName } = req.params;
    const { force = false } = req.body;

    logger.info(`🔄 收到重启项目请求: ${projectName}`);

    const monitor = getGlobalMonitor();

    // 检查项目是否存在
    if (!monitor.projectConfigs.has(projectName)) {
      return res.status(404).json({
        success: false,
        error: 'Project not found',
        message: `Project '${projectName}' is not registered in the monitoring system`,
        code: 'PROJECT_NOT_FOUND'
      });
    }

    const projectConfig = monitor.projectConfigs.get(projectName);

    // 尝试重启项目
    const restartResult = await monitor.attemptProjectRestart(projectName, projectConfig);

    if (restartResult) {
      res.json({
        success: true,
        message: `项目 ${projectName} 重启成功`,
        data: {
          projectName,
          projectType: projectConfig.type,
          framework: projectConfig.framework,
          restartTime: new Date().toISOString(),
          force: force
        }
      });
    } else {
      res.status(500).json({
        success: false,
        error: 'Project restart failed',
        message: `Failed to restart project '${projectName}'`,
        code: 'PROJECT_RESTART_FAILED',
        data: {
          projectName,
          projectType: projectConfig.type
        }
      });
    }

  } catch (error) {
    logger.error(`❌ 重启项目失败: ${req.params.name}`, error);
    res.status(500).json({
      success: false,
      error: 'Failed to restart project',
      message: error.message,
      code: 'PROJECT_RESTART_ERROR'
    });
  }
});

/**
 * 🔧 POST /api/global/optimize-resources - 优化系统资源
 */
router.post('/optimize-resources', async (req, res) => {
  try {
    const { resourceType = 'all', force = false } = req.body;

    logger.info(`🔧 收到资源优化请求: ${resourceType}`);

    const monitor = getGlobalMonitor();
    const results = {};

    if (resourceType === 'all' || resourceType === 'memory') {
      results.memory = await monitor.attemptResourceOptimization('memory', 90);
    }

    if (resourceType === 'all' || resourceType === 'disk') {
      results.disk = await monitor.attemptResourceOptimization('disk', 90);
    }

    if (resourceType === 'all' || resourceType === 'cpu') {
      results.cpu = await monitor.attemptResourceOptimization('cpu', 90);
    }

    const successCount = Object.values(results).filter(r => r).length;
    const totalCount = Object.keys(results).length;

    res.json({
      success: successCount > 0,
      message: `资源优化完成 (${successCount}/${totalCount} 成功)`,
      data: {
        resourceType,
        optimization_results: results,
        success_rate: totalCount > 0 ? successCount / totalCount : 0,
        timestamp: new Date().toISOString(),
        force: force
      }
    });

  } catch (error) {
    logger.error('❌ 资源优化失败:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to optimize resources',
      message: error.message,
      code: 'RESOURCE_OPTIMIZATION_ERROR'
    });
  }
});

/**
 * 📈 GET /api/global/analytics - 获取监控分析数据
 */
router.get('/analytics', async (req, res) => {
  try {
    const { timeRange = '1h' } = req.query;

    logger.info(`📈 获取监控分析数据: ${timeRange}`);

    const monitor = getGlobalMonitor();
    
    // 获取故障统计
    const failureStats = await monitor.blackBox.getFailureStats(timeRange);
    
    // 获取治疗统计
    const healingStats = monitor.healingSystem.getHealingStats();

    // 计算分析指标
    const analytics = {
      time_range: timeRange,
      failure_analysis: {
        total_failures: failureStats.total_failures || 0,
        failure_by_source: failureStats.failure_by_source || {},
        failure_by_type: failureStats.failure_by_type || {},
        critical_failures: failureStats.critical_failures || 0
      },
      healing_analysis: {
        total_healing_attempts: healingStats.totalHealingAttempts || 0,
        successful_healings: healingStats.successfulHealings || 0,
        healing_success_rate: healingStats.healingSuccessRate || 0,
        healing_by_strategy: healingStats.healingByStrategy || {}
      },
      system_analysis: {
        monitored_projects: monitor.projectConfigs.size,
        active_watchers: monitor.systemWatchers.size,
        uptime: process.uptime(),
        memory_usage: process.memoryUsage()
      },
      trends: {
        failure_trend: calculateFailureTrend(failureStats),
        healing_trend: calculateHealingTrend(healingStats),
        system_trend: 'stable' // 简化实现
      }
    };

    res.json({
      success: true,
      message: '监控分析数据',
      data: analytics,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('❌ 获取监控分析数据失败:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get analytics data',
      message: error.message,
      code: 'GLOBAL_MONITOR_ANALYTICS_ERROR'
    });
  }
});

/**
 * 🔍 GET /api/global/project/:name/details - 获取项目详细信息
 */
router.get('/project/:name/details', async (req, res) => {
  try {
    const { name: projectName } = req.params;

    const monitor = getGlobalMonitor();

    if (!monitor.projectConfigs.has(projectName)) {
      return res.status(404).json({
        success: false,
        error: 'Project not found',
        message: `Project '${projectName}' is not registered`,
        code: 'PROJECT_NOT_FOUND'
      });
    }

    const projectConfig = monitor.projectConfigs.get(projectName);
    const status = monitor.getMonitoringStatus();

    // 获取项目相关的故障记录
    const projectFailures = await monitor.blackBox.getFailuresBySource('PROJECT', projectName);

    const projectDetails = {
      basic_info: {
        name: projectConfig.name,
        type: projectConfig.type,
        language: projectConfig.language,
        framework: projectConfig.framework,
        path: projectConfig.path
      },
      monitoring_info: {
        is_monitored: status.projectWatchers.includes(projectName),
        monitoring_enabled: projectConfig.monitoringEnabled,
        health_check_endpoint: projectConfig.healthCheckEndpoint,
        critical_files: projectConfig.criticalFiles,
        log_paths: projectConfig.logPaths,
        config_files: projectConfig.configFiles
      },
      failure_history: {
        total_failures: projectFailures.length,
        recent_failures: projectFailures.slice(0, 10),
        failure_types: getFailureTypeStats(projectFailures)
      },
      dependencies: projectConfig.dependencies || [],
      last_updated: new Date().toISOString()
    };

    res.json({
      success: true,
      message: `项目 ${projectName} 详细信息`,
      data: projectDetails
    });

  } catch (error) {
    logger.error(`❌ 获取项目详细信息失败: ${req.params.name}`, error);
    res.status(500).json({
      success: false,
      error: 'Failed to get project details',
      message: error.message,
      code: 'PROJECT_DETAILS_ERROR'
    });
  }
});

// 辅助函数

/**
 * 计算系统健康分数
 */
function calculateSystemHealthScore(resources, status) {
  let score = 100;

  // 基于资源使用率扣分
  if (resources.memory > 85) score -= 20;
  else if (resources.memory > 70) score -= 10;

  if (resources.disk > 90) score -= 25;
  else if (resources.disk > 80) score -= 15;

  if (resources.cpu > 80) score -= 15;
  else if (resources.cpu > 60) score -= 8;

  // 基于监控状态加分
  if (status.isMonitoring) score += 5;
  if (status.monitoredProjects.length > 0) score += 5;

  score = Math.max(0, Math.min(100, score));

  let healthStatus, level;
  if (score >= 90) {
    healthStatus = 'excellent';
    level = 'green';
  } else if (score >= 70) {
    healthStatus = 'good';
    level = 'yellow';
  } else if (score >= 50) {
    healthStatus = 'fair';
    level = 'orange';
  } else {
    healthStatus = 'poor';
    level = 'red';
  }

  return { score, status: healthStatus, level };
}

/**
 * 生成健康建议
 */
function generateHealthRecommendations(healthScore, resources) {
  const recommendations = [];

  if (resources.memory > 85) {
    recommendations.push({
      type: 'memory',
      priority: 'high',
      message: '内存使用率过高，建议清理内存或重启高内存占用进程',
      action: 'optimize_memory'
    });
  }

  if (resources.disk > 90) {
    recommendations.push({
      type: 'disk',
      priority: 'critical',
      message: '磁盘空间不足，建议清理临时文件和日志',
      action: 'cleanup_disk'
    });
  }

  if (resources.cpu > 80) {
    recommendations.push({
      type: 'cpu',
      priority: 'medium',
      message: 'CPU使用率较高，建议检查高CPU占用进程',
      action: 'optimize_cpu'
    });
  }

  if (healthScore.score < 70) {
    recommendations.push({
      type: 'general',
      priority: 'high',
      message: '系统整体健康状况需要关注，建议进行全面优化',
      action: 'full_optimization'
    });
  }

  return recommendations;
}

/**
 * 计算故障趋势
 */
function calculateFailureTrend(failureStats) {
  // 简化实现
  const totalFailures = failureStats.total_failures || 0;
  
  if (totalFailures === 0) return 'stable';
  if (totalFailures < 5) return 'improving';
  if (totalFailures < 20) return 'stable';
  return 'concerning';
}

/**
 * 计算治疗趋势
 */
function calculateHealingTrend(healingStats) {
  // 简化实现
  const successRate = healingStats.healingSuccessRate || 0;
  
  if (successRate >= 0.9) return 'excellent';
  if (successRate >= 0.7) return 'good';
  if (successRate >= 0.5) return 'fair';
  return 'poor';
}

/**
 * 获取故障类型统计
 */
function getFailureTypeStats(failures) {
  const stats = {};
  
  for (const failure of failures) {
    const type = failure.error_type || 'Unknown';
    stats[type] = (stats[type] || 0) + 1;
  }
  
  return stats;
}

module.exports = router;