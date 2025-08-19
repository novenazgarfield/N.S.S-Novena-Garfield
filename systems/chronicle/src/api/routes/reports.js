const express = require('express');
const { createModuleLogger } = require('../../shared/logger');
const database = require('../../collector/database');
const reportGenerator = require('../../analyst/report-generator');
const { validatePath, validateQuery, validateBody, pathSchemas, customValidators } = require('../middleware/validation');

const logger = createModuleLogger('reports-api');
const router = express.Router();

/**
 * GET /reports/:sessionId
 * 生成并获取会话报告
 */
router.get('/:sessionId',
  validatePath('sessionId', pathSchemas.sessionId),
  customValidators.validateSessionExists,
  validateQuery('generateReport'),
  async (req, res) => {
    try {
      const { sessionId } = req.params;
      const { type, format, include_raw_data, max_events, date_range } = req.query;

      logger.info('Generating report', { 
        sessionId, 
        type, 
        format, 
        include_raw_data,
        max_events 
      });

      // 生成报告选项
      const options = {
        type,
        format,
        includeRawData: include_raw_data,
        maxEvents: max_events,
        dateRange: date_range
      };

      // 生成报告
      const { reportId, report } = await reportGenerator.generateSessionReport(sessionId, options);

      // 根据格式返回不同内容
      if (format === 'json') {
        res.json({
          reportId,
          sessionId,
          generatedAt: new Date().toISOString(),
          format,
          report
        });
      } else {
        // 导出为其他格式
        const exportedContent = await reportGenerator.exportReport(report, format);
        
        // 设置适当的Content-Type
        const contentTypes = {
          markdown: 'text/markdown',
          html: 'text/html'
        };
        
        res.set('Content-Type', contentTypes[format] || 'text/plain');
        res.set('Content-Disposition', `attachment; filename="report-${sessionId}.${format}"`);
        res.send(exportedContent);
      }

      logger.audit('Report generated', { 
        sessionId, 
        reportId, 
        type, 
        format 
      });

    } catch (error) {
      logger.error('Failed to generate report', { 
        sessionId: req.params.sessionId, 
        error: error.message 
      });
      
      res.status(500).json({
        error: 'Failed to generate report',
        message: error.message,
        sessionId: req.params.sessionId
      });
    }
  }
);

/**
 * GET /reports/:sessionId/raw
 * 获取会话原始数据
 */
router.get('/:sessionId/raw',
  validatePath('sessionId', pathSchemas.sessionId),
  customValidators.validateSessionExists,
  validateQuery(),
  async (req, res) => {
    try {
      const { sessionId } = req.params;
      const { limit, type, start_time, end_time } = req.query;

      logger.info('Fetching raw session data', { sessionId, limit, type });

      // 获取会话信息
      const session = req.session;

      // 获取事件数据
      const events = await database.getSessionEvents(sessionId, type, limit);

      // 过滤时间范围
      let filteredEvents = events;
      if (start_time || end_time) {
        filteredEvents = events.filter(event => {
          const eventTime = event.timestamp;
          if (start_time && eventTime < new Date(start_time).getTime()) {
            return false;
          }
          if (end_time && eventTime > new Date(end_time).getTime()) {
            return false;
          }
          return true;
        });
      }

      // 获取详细事件数据
      const detailedEvents = await Promise.all(
        filteredEvents.map(async (event) => {
          try {
            let detailData = null;
            
            switch (event.type) {
              case 'file':
                detailData = await database.get(
                  'SELECT * FROM file_events WHERE id = ?',
                  [event.id]
                );
                break;
              case 'window':
                detailData = await database.get(
                  'SELECT * FROM window_events WHERE id = ?',
                  [event.id]
                );
                break;
              case 'command':
                detailData = await database.get(
                  'SELECT * FROM command_events WHERE id = ?',
                  [event.id]
                );
                break;
            }

            return {
              ...event,
              details: detailData
            };
          } catch (error) {
            logger.warn('Failed to get event details', { 
              eventId: event.id, 
              error: error.message 
            });
            return event;
          }
        })
      );

      // 获取统计信息
      const stats = await database.getSessionStats(sessionId);

      const response = {
        sessionId,
        session: {
          id: session.id,
          project_name: session.project_name,
          project_path: session.project_path,
          status: session.status,
          start_time: session.start_time,
          end_time: session.end_time,
          metadata: session.metadata
        },
        stats,
        events: detailedEvents,
        filters: {
          type,
          start_time,
          end_time,
          limit,
          applied: filteredEvents.length !== events.length
        },
        exportedAt: new Date().toISOString()
      };

      res.json(response);

    } catch (error) {
      logger.error('Failed to get raw session data', { 
        sessionId: req.params.sessionId, 
        error: error.message 
      });
      
      res.status(500).json({
        error: 'Failed to get raw session data',
        message: error.message
      });
    }
  }
);

/**
 * POST /reports/:sessionId/analyze
 * 对会话进行深度分析
 */
router.post('/:sessionId/analyze',
  validatePath('sessionId', pathSchemas.sessionId),
  customValidators.validateSessionExists,
  validateBody('analyzeText'),
  async (req, res) => {
    try {
      const { sessionId } = req.params;
      const { options = {} } = req.body;

      logger.info('Starting deep analysis', { sessionId, options });

      // 获取会话事件
      const events = await database.getSessionEvents(sessionId);
      
      // 过滤需要分析的事件（主要是命令事件）
      const commandEvents = events.filter(e => e.type === 'command');
      
      const analysisResults = [];

      // 分析每个命令事件
      for (const event of commandEvents.slice(0, options.max_events || 10)) {
        try {
          const commandData = await database.get(
            'SELECT * FROM command_events WHERE id = ?',
            [event.id]
          );

          if (commandData && (commandData.stderr || commandData.stdout)) {
            const text = (commandData.stderr || '') + '\n' + (commandData.stdout || '');
            
            // 使用AI分析器
            const aiSummarizer = require('../../analyst/ai-summarizer');
            const analysis = await aiSummarizer.analyzeLog(text, {
              eventType: 'command',
              command: commandData.command,
              exitCode: commandData.exit_code,
              sessionId
            });

            // 保存分析结果
            const analysisId = await database.saveAnalysisResult(
              sessionId,
              event.id,
              'command',
              'ai_analysis',
              analysis,
              { analyzedAt: Date.now() }
            );

            analysisResults.push({
              eventId: event.id,
              analysisId,
              command: commandData.command,
              exitCode: commandData.exit_code,
              analysis
            });
          }
        } catch (error) {
          logger.warn('Failed to analyze event', { 
            eventId: event.id, 
            error: error.message 
          });
        }
      }

      // 生成分析摘要
      const summary = {
        totalEventsAnalyzed: analysisResults.length,
        highSeverityIssues: analysisResults.filter(r => 
          r.analysis.severity === 'high' || r.analysis.severity === 'critical'
        ).length,
        commonIssues: this.extractCommonIssues(analysisResults),
        recommendations: this.generateRecommendations(analysisResults)
      };

      logger.audit('Deep analysis completed', { 
        sessionId, 
        eventsAnalyzed: analysisResults.length,
        highSeverityIssues: summary.highSeverityIssues
      });

      res.json({
        sessionId,
        analysis: {
          summary,
          results: analysisResults,
          analyzedAt: new Date().toISOString()
        }
      });

    } catch (error) {
      logger.error('Failed to perform deep analysis', { 
        sessionId: req.params.sessionId, 
        error: error.message 
      });
      
      res.status(500).json({
        error: 'Failed to perform deep analysis',
        message: error.message
      });
    }
  }
);

/**
 * GET /reports/:sessionId/summary
 * 获取会话快速摘要
 */
router.get('/:sessionId/summary',
  validatePath('sessionId', pathSchemas.sessionId),
  customValidators.validateSessionExists,
  async (req, res) => {
    try {
      const { sessionId } = req.params;
      const session = req.session;

      logger.info('Generating session summary', { sessionId });

      // 获取基本统计
      const stats = await database.getSessionStats(sessionId);

      // 计算持续时间
      const duration = session.end_time ? 
        session.end_time - session.start_time : 
        Date.now() - session.start_time;

      // 获取最近的事件
      const recentEvents = await database.getSessionEvents(sessionId, null, 5);

      // 检查是否有错误
      const errorEvents = await database.all(`
        SELECT COUNT(*) as count 
        FROM command_events 
        WHERE session_id = ? AND exit_code != 0
      `, [sessionId]);

      const hasErrors = errorEvents[0]?.count > 0;

      // 获取最活跃的时间段
      const activityDistribution = await database.all(`
        SELECT strftime('%H', datetime(timestamp/1000, 'unixepoch')) as hour,
               COUNT(*) as activity
        FROM (
          SELECT timestamp FROM file_events WHERE session_id = ?
          UNION ALL
          SELECT timestamp FROM window_events WHERE session_id = ?
          UNION ALL
          SELECT start_time as timestamp FROM command_events WHERE session_id = ?
        )
        GROUP BY hour
        ORDER BY activity DESC
        LIMIT 3
      `, [sessionId, sessionId, sessionId]);

      const summary = {
        sessionId,
        project: {
          name: session.project_name,
          path: session.project_path
        },
        status: session.status,
        duration: this.formatDuration(duration),
        stats,
        health: {
          status: hasErrors ? 'warning' : 'healthy',
          hasErrors,
          errorCount: errorEvents[0]?.count || 0
        },
        activity: {
          totalEvents: stats.totalEvents,
          peakHours: activityDistribution.map(d => `${d.hour}:00`),
          recentEvents: recentEvents.map(e => ({
            type: e.type,
            timestamp: new Date(e.timestamp).toISOString(),
            description: this.formatEventDescription(e)
          }))
        },
        generatedAt: new Date().toISOString()
      };

      res.json(summary);

    } catch (error) {
      logger.error('Failed to generate session summary', { 
        sessionId: req.params.sessionId, 
        error: error.message 
      });
      
      res.status(500).json({
        error: 'Failed to generate session summary',
        message: error.message
      });
    }
  }
);

/**
 * GET /reports
 * 获取所有报告列表
 */
router.get('/',
  validateQuery(),
  async (req, res) => {
    try {
      const { limit, offset } = req.query;

      // 获取报告列表
      const reports = await database.all(`
        SELECT r.*, s.project_name, s.project_path
        FROM reports r
        JOIN sessions s ON r.session_id = s.id
        ORDER BY r.generated_at DESC
        LIMIT ? OFFSET ?
      `, [limit, offset]);

      // 获取总数
      const totalResult = await database.get('SELECT COUNT(*) as total FROM reports');
      const total = totalResult.total;

      const formattedReports = reports.map(report => ({
        reportId: report.id,
        sessionId: report.session_id,
        projectName: report.project_name,
        reportType: report.report_type,
        title: report.title,
        format: report.format,
        generatedAt: new Date(report.generated_at).toISOString(),
        metadata: report.metadata ? JSON.parse(report.metadata) : {}
      }));

      res.json({
        reports: formattedReports,
        pagination: {
          total,
          limit,
          offset,
          hasMore: offset + limit < total
        }
      });

    } catch (error) {
      logger.error('Failed to get reports list', { error: error.message });
      
      res.status(500).json({
        error: 'Failed to get reports list',
        message: error.message
      });
    }
  }
);

/**
 * DELETE /reports/:reportId
 * 删除报告
 */
router.delete('/:reportId',
  validatePath('reportId', pathSchemas.reportId),
  async (req, res) => {
    try {
      const { reportId } = req.params;

      const result = await database.run(
        'DELETE FROM reports WHERE id = ?',
        [reportId]
      );

      if (result.changes === 0) {
        return res.status(404).json({
          error: 'Report not found',
          message: 'The specified report does not exist'
        });
      }

      logger.audit('Report deleted', { reportId, deletedBy: req.ip });

      res.json({
        success: true,
        message: 'Report deleted successfully',
        reportId
      });

    } catch (error) {
      logger.error('Failed to delete report', { 
        reportId: req.params.reportId, 
        error: error.message 
      });
      
      res.status(500).json({
        error: 'Failed to delete report',
        message: error.message
      });
    }
  }
);

// 辅助方法
router.formatDuration = function(ms) {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`;
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  } else {
    return `${seconds}s`;
  }
};

router.formatEventDescription = function(event) {
  switch (event.type) {
    case 'file':
      return `${event.event_type}: ${event.path}`;
    case 'window':
      return `Window: ${event.path}`;
    case 'command':
      return `Command: ${event.path}`;
    default:
      return `${event.type}: ${event.path}`;
  }
};

router.extractCommonIssues = function(analysisResults) {
  const issues = {};
  
  analysisResults.forEach(result => {
    if (result.analysis.error_type) {
      const errorType = result.analysis.error_type;
      if (!issues[errorType]) {
        issues[errorType] = 0;
      }
      issues[errorType]++;
    }
  });

  return Object.entries(issues)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5)
    .map(([type, count]) => ({ type, count }));
};

router.generateRecommendations = function(analysisResults) {
  const recommendations = new Set();
  
  analysisResults.forEach(result => {
    if (result.analysis.suggested_actions) {
      result.analysis.suggested_actions.forEach(action => {
        recommendations.add(action);
      });
    }
  });

  return Array.from(recommendations).slice(0, 5);
};

module.exports = router;