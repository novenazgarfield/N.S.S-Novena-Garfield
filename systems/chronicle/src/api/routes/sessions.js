const express = require('express');
const { createModuleLogger } = require('../../shared/logger');
const { formatDuration } = require('../../shared/utils');
const database = require('../../collector/database');
const fileMonitor = require('../../collector/file-monitor');
const windowMonitor = require('../../collector/window-monitor');
const commandMonitor = require('../../collector/command-monitor');
const { validateBody, validatePath, validateQuery, pathSchemas, customValidators } = require('../middleware/validation');

const logger = createModuleLogger('sessions-api');
const router = express.Router();

/**
 * POST /sessions/start
 * 启动新的记录会话
 */
router.post('/start',
  validateBody('startSession'),
  customValidators.validateFilePath,
  async (req, res) => {
    try {
      const { project_name, project_path, metadata = {}, options = {} } = req.body;

      logger.info('Starting new session', { project_name, project_path, options });

      // 创建会话
      const sessionId = await database.createSession(project_name, project_path, {
        ...metadata,
        startedBy: req.ip,
        userAgent: req.get('User-Agent'),
        options
      });

      // 启动监控服务
      const monitoringResults = {};

      if (options.file_monitoring !== false) {
        monitoringResults.fileMonitoring = await fileMonitor.startMonitoring(sessionId, project_path);
      }

      if (options.window_monitoring !== false) {
        monitoringResults.windowMonitoring = await windowMonitor.startMonitoring(sessionId, project_path);
      }

      if (options.command_monitoring !== false) {
        monitoringResults.commandMonitoring = await commandMonitor.startMonitoring(sessionId, project_path);
      }

      // 检查监控启动结果
      const failedMonitors = Object.entries(monitoringResults)
        .filter(([_, success]) => !success)
        .map(([monitor, _]) => monitor);

      if (failedMonitors.length > 0) {
        logger.warn('Some monitors failed to start', { sessionId, failedMonitors });
      }

      const response = {
        success: true,
        sessionId,
        project: {
          name: project_name,
          path: project_path
        },
        monitoring: monitoringResults,
        startTime: Date.now(),
        message: 'Session started successfully'
      };

      if (failedMonitors.length > 0) {
        response.warnings = [`Failed to start: ${failedMonitors.join(', ')}`];
      }

      logger.audit('Session started', { sessionId, project_name, monitoring: monitoringResults });

      res.status(201).json(response);

    } catch (error) {
      logger.error('Failed to start session', { error: error.message, body: req.body });
      
      res.status(500).json({
        success: false,
        error: 'Failed to start session',
        message: error.message
      });
    }
  }
);

/**
 * POST /sessions/:sessionId/stop
 * 停止记录会话
 */
router.post('/:sessionId/stop',
  validatePath('sessionId', pathSchemas.sessionId),
  customValidators.validateSessionExists,
  validateBody('stopSession'),
  async (req, res) => {
    try {
      const { sessionId } = req.params;
      const { force = false } = req.body;

      logger.info('Stopping session', { sessionId, force });

      // 检查会话状态
      if (req.session.status !== 'active' && !force) {
        return res.status(400).json({
          success: false,
          error: 'Session not active',
          message: 'Session is already stopped or completed',
          status: req.session.status
        });
      }

      // 停止监控服务
      const stopResults = {};
      stopResults.fileMonitoring = await fileMonitor.stopMonitoring(sessionId);
      stopResults.windowMonitoring = await windowMonitor.stopMonitoring(sessionId);
      stopResults.commandMonitoring = await commandMonitor.stopMonitoring(sessionId);

      // 结束会话
      const sessionEnded = await database.endSession(sessionId);

      if (!sessionEnded && !force) {
        return res.status(400).json({
          success: false,
          error: 'Failed to stop session',
          message: 'Session could not be stopped'
        });
      }

      // 获取会话统计
      const stats = await database.getSessionStats(sessionId);
      const updatedSession = await database.getSession(sessionId);
      
      const duration = updatedSession.end_time - updatedSession.start_time;

      logger.audit('Session stopped', { 
        sessionId, 
        duration: formatDuration(duration),
        stats,
        stopResults 
      });

      res.json({
        success: true,
        sessionId,
        duration: formatDuration(duration),
        stats,
        monitoring: stopResults,
        message: 'Session stopped successfully'
      });

    } catch (error) {
      logger.error('Failed to stop session', { 
        sessionId: req.params.sessionId, 
        error: error.message 
      });
      
      res.status(500).json({
        success: false,
        error: 'Failed to stop session',
        message: error.message
      });
    }
  }
);

/**
 * GET /sessions/:sessionId
 * 获取会话信息
 */
router.get('/:sessionId',
  validatePath('sessionId', pathSchemas.sessionId),
  customValidators.validateSessionExists,
  async (req, res) => {
    try {
      const { sessionId } = req.params;
      const session = req.session;

      // 获取统计信息
      const stats = await database.getSessionStats(sessionId);

      // 获取监控状态
      const monitoringStatus = {
        fileMonitoring: fileMonitor.getMonitoringStatus(sessionId),
        windowMonitoring: windowMonitor.getMonitoringStatus(sessionId),
        commandMonitoring: commandMonitor.getMonitoringStatus(sessionId)
      };

      // 计算持续时间
      const duration = session.end_time ? 
        session.end_time - session.start_time : 
        Date.now() - session.start_time;

      const response = {
        sessionId: session.id,
        project: {
          name: session.project_name,
          path: session.project_path
        },
        status: session.status,
        timeRange: {
          start: new Date(session.start_time).toISOString(),
          end: session.end_time ? new Date(session.end_time).toISOString() : null,
          duration: formatDuration(duration)
        },
        stats,
        monitoring: monitoringStatus,
        metadata: session.metadata || {}
      };

      res.json(response);

    } catch (error) {
      logger.error('Failed to get session info', { 
        sessionId: req.params.sessionId, 
        error: error.message 
      });
      
      res.status(500).json({
        error: 'Failed to get session info',
        message: error.message
      });
    }
  }
);

/**
 * GET /sessions
 * 获取会话列表
 */
router.get('/',
  validateQuery(),
  async (req, res) => {
    try {
      const { limit, offset, sort, sort_by } = req.query;

      // 获取活动会话
      const activeSessions = await database.getActiveSessions();

      // 获取历史会话（简化实现，实际应支持分页和排序）
      const allSessions = await database.all(
        `SELECT id, project_name, project_path, status, start_time, end_time, 
                created_at, updated_at
         FROM sessions 
         ORDER BY ${sort_by === 'timestamp' ? 'start_time' : sort_by} ${sort.toUpperCase()}
         LIMIT ? OFFSET ?`,
        [limit, offset]
      );

      const sessions = allSessions.map(session => {
        const duration = session.end_time ? 
          session.end_time - session.start_time : 
          Date.now() - session.start_time;

        return {
          sessionId: session.id,
          projectName: session.project_name,
          projectPath: session.project_path,
          status: session.status,
          startTime: new Date(session.start_time).toISOString(),
          endTime: session.end_time ? new Date(session.end_time).toISOString() : null,
          duration: formatDuration(duration),
          isActive: session.status === 'active'
        };
      });

      // 获取总数
      const totalResult = await database.get('SELECT COUNT(*) as total FROM sessions');
      const total = totalResult.total;

      res.json({
        sessions,
        pagination: {
          total,
          limit,
          offset,
          hasMore: offset + limit < total
        },
        activeSessions: activeSessions.length
      });

    } catch (error) {
      logger.error('Failed to get sessions list', { error: error.message });
      
      res.status(500).json({
        error: 'Failed to get sessions list',
        message: error.message
      });
    }
  }
);

/**
 * GET /sessions/:sessionId/events
 * 获取会话事件
 */
router.get('/:sessionId/events',
  validatePath('sessionId', pathSchemas.sessionId),
  customValidators.validateSessionExists,
  validateQuery(),
  async (req, res) => {
    try {
      const { sessionId } = req.params;
      const { limit, type, start_time, end_time } = req.query;

      // 获取事件
      const events = await database.getSessionEvents(sessionId, type, limit);

      // 过滤时间范围（如果指定）
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

      // 格式化事件
      const formattedEvents = filteredEvents.map(event => ({
        id: event.id,
        type: event.type,
        timestamp: new Date(event.timestamp).toISOString(),
        event: event.event_type,
        path: event.path,
        metadata: event.metadata
      }));

      res.json({
        sessionId,
        events: formattedEvents,
        total: formattedEvents.length,
        filters: {
          type,
          start_time,
          end_time,
          limit
        }
      });

    } catch (error) {
      logger.error('Failed to get session events', { 
        sessionId: req.params.sessionId, 
        error: error.message 
      });
      
      res.status(500).json({
        error: 'Failed to get session events',
        message: error.message
      });
    }
  }
);

/**
 * GET /sessions/:sessionId/stats
 * 获取会话统计信息
 */
router.get('/:sessionId/stats',
  validatePath('sessionId', pathSchemas.sessionId),
  customValidators.validateSessionExists,
  async (req, res) => {
    try {
      const { sessionId } = req.params;

      // 获取基本统计
      const stats = await database.getSessionStats(sessionId);

      // 获取监控统计
      const monitoringStats = {
        fileMonitoring: await fileMonitor.getMonitoringStats(sessionId),
        windowMonitoring: await windowMonitor.getMonitoringStats(sessionId),
        commandMonitoring: await commandMonitor.getMonitoringStats(sessionId)
      };

      // 获取时间分布统计
      const hourlyDistribution = await database.all(`
        SELECT strftime('%H', datetime(timestamp/1000, 'unixepoch')) as hour,
               COUNT(*) as count,
               type
        FROM (
          SELECT timestamp, 'file' as type FROM file_events WHERE session_id = ?
          UNION ALL
          SELECT timestamp, 'window' as type FROM window_events WHERE session_id = ?
          UNION ALL
          SELECT start_time as timestamp, 'command' as type FROM command_events WHERE session_id = ?
        )
        GROUP BY hour, type
        ORDER BY hour
      `, [sessionId, sessionId, sessionId]);

      res.json({
        sessionId,
        basicStats: stats,
        monitoringStats,
        timeDistribution: {
          hourly: hourlyDistribution
        }
      });

    } catch (error) {
      logger.error('Failed to get session stats', { 
        sessionId: req.params.sessionId, 
        error: error.message 
      });
      
      res.status(500).json({
        error: 'Failed to get session stats',
        message: error.message
      });
    }
  }
);

/**
 * DELETE /sessions/:sessionId
 * 删除会话（管理员功能）
 */
router.delete('/:sessionId',
  validatePath('sessionId', pathSchemas.sessionId),
  customValidators.validateSessionExists,
  async (req, res) => {
    try {
      const { sessionId } = req.params;

      // 如果会话仍在活动，先停止它
      if (req.session.status === 'active') {
        await fileMonitor.stopMonitoring(sessionId);
        await windowMonitor.stopMonitoring(sessionId);
        await commandMonitor.stopMonitoring(sessionId);
      }

      // 删除会话（级联删除相关数据）
      const result = await database.run(
        'DELETE FROM sessions WHERE id = ?',
        [sessionId]
      );

      if (result.changes === 0) {
        return res.status(404).json({
          error: 'Session not found',
          message: 'Session may have already been deleted'
        });
      }

      logger.audit('Session deleted', { 
        sessionId, 
        projectName: req.session.project_name,
        deletedBy: req.ip
      });

      res.json({
        success: true,
        message: 'Session deleted successfully',
        sessionId
      });

    } catch (error) {
      logger.error('Failed to delete session', { 
        sessionId: req.params.sessionId, 
        error: error.message 
      });
      
      res.status(500).json({
        error: 'Failed to delete session',
        message: error.message
      });
    }
  }
);

module.exports = router;