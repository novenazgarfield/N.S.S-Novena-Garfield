const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const path = require('path');

const { createModuleLogger } = require('../shared/logger');
const config = require('../shared/config');
const database = require('../collector/database');
const { apiKeyAuth, auditLog, requestLimit } = require('./middleware/auth');
const { customValidators } = require('./middleware/validation');

// 路由导入
const sessionsRouter = require('./routes/sessions');
const reportsRouter = require('./routes/reports');
const genesisRouter = require('./routes/genesis'); // 🏥 Genesis中央医院API

const logger = createModuleLogger('api-server');

class APIServer {
  constructor() {
    this.app = express();
    this.server = null;
    this.isInitialized = false;
  }

  /**
   * 初始化服务器
   */
  async init() {
    try {
      // 初始化配置
      config.init();

      // 初始化数据库
      await database.init();

      // 设置中间件
      this.setupMiddleware();

      // 设置路由
      this.setupRoutes();

      // 设置错误处理
      this.setupErrorHandling();

      this.isInitialized = true;
      logger.info('API server initialized successfully');

    } catch (error) {
      logger.error('Failed to initialize API server', { error: error.message });
      throw error;
    }
  }

  /**
   * 设置中间件
   */
  setupMiddleware() {
    // 信任代理（用于获取真实IP）
    this.app.set('trust proxy', true);

    // 安全中间件
    if (config.security.enableHelmet) {
      this.app.use(helmet({
        contentSecurityPolicy: false, // 允许API调用
        crossOriginEmbedderPolicy: false
      }));
    }

    // CORS配置
    if (config.security.enableCors) {
      this.app.use(cors({
        origin: config.security.corsOrigins,
        credentials: true,
        methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        allowedHeaders: ['Content-Type', 'Authorization', 'X-API-Key']
      }));
    }

    // 压缩响应
    if (config.performance.enableCompression) {
      this.app.use(compression());
    }

    // 请求日志
    this.app.use(morgan('combined', {
      stream: {
        write: (message) => logger.info(message.trim(), { source: 'http' })
      }
    }));

    // 请求体解析
    this.app.use(express.json({ 
      limit: config.performance.maxRequestSize 
    }));
    this.app.use(express.urlencoded({ 
      extended: true, 
      limit: config.performance.maxRequestSize 
    }));

    // 请求超时
    this.app.use((req, res, next) => {
      req.setTimeout(config.performance.requestTimeout);
      res.setTimeout(config.performance.requestTimeout);
      next();
    });

    // 速率限制
    if (config.security.rateLimitEnabled) {
      this.app.use(requestLimit(
        config.security.rateLimitMax,
        config.security.rateLimitWindowMs
      ));
    }

    // 内容类型验证
    this.app.use(customValidators.validateContentType());

    // 请求大小验证
    this.app.use(customValidators.validateRequestSize());

    // 审计日志
    this.app.use(auditLog);

    // API密钥认证（应用到所有路由）
    this.app.use(apiKeyAuth);
  }

  /**
   * 设置路由
   */
  setupRoutes() {
    // 健康检查
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        database: database.isInitialized ? 'connected' : 'disconnected'
      });
    });

    // API信息
    this.app.get('/info', (req, res) => {
      res.json({
        name: 'Chronicle API',
        version: '1.0.0',
        description: 'AI-Driven Automated Experiment Recorder API',
        endpoints: {
          sessions: '/sessions',
          reports: '/reports',
          genesis: '/api', // 🏥 Genesis中央医院API
          health: '/health',
          info: '/info'
        },
        documentation: '/docs',
        timestamp: new Date().toISOString()
      });
    });

    // API文档（简单版本）
    this.app.get('/docs', (req, res) => {
      res.json({
        title: 'Chronicle API Documentation',
        version: '1.0.0',
        baseUrl: `${req.protocol}://${req.get('host')}`,
        endpoints: {
          sessions: {
            'POST /sessions/start': 'Start a new recording session',
            'POST /sessions/:id/stop': 'Stop a recording session',
            'GET /sessions/:id': 'Get session information',
            'GET /sessions': 'List all sessions',
            'GET /sessions/:id/events': 'Get session events',
            'GET /sessions/:id/stats': 'Get session statistics',
            'DELETE /sessions/:id': 'Delete a session'
          },
          reports: {
            'GET /reports/:sessionId': 'Generate and get session report',
            'GET /reports/:sessionId/raw': 'Get raw session data',
            'POST /reports/:sessionId/analyze': 'Perform deep analysis',
            'GET /reports/:sessionId/summary': 'Get session summary',
            'GET /reports': 'List all reports',
            'DELETE /reports/:id': 'Delete a report'
          }
        },
        authentication: {
          type: config.security.apiKeyRequired ? 'API Key' : 'None',
          header: 'X-API-Key',
          query: 'api_key'
        }
      });
    });

    // 主要路由
    this.app.use('/sessions', sessionsRouter);
    this.app.use('/reports', reportsRouter);
    this.app.use('/api', genesisRouter); // 🏥 Genesis中央医院API路由

    // 管理路由
    this.setupAdminRoutes();

    // 404处理
    this.app.use('*', (req, res) => {
      res.status(404).json({
        error: 'Not Found',
        message: `The requested endpoint ${req.method} ${req.originalUrl} was not found`,
        availableEndpoints: ['/health', '/info', '/docs', '/sessions', '/reports']
      });
    });
  }

  /**
   * 设置管理路由
   */
  setupAdminRoutes() {
    const adminRouter = express.Router();

    // 系统状态
    adminRouter.get('/status', async (req, res) => {
      try {
        const activeSessions = await database.getActiveSessions();
        const totalSessions = await database.get('SELECT COUNT(*) as count FROM sessions');
        const totalReports = await database.get('SELECT COUNT(*) as count FROM reports');

        res.json({
          system: {
            status: 'running',
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            version: '1.0.0'
          },
          database: {
            status: database.isInitialized ? 'connected' : 'disconnected',
            totalSessions: totalSessions.count,
            activeSessions: activeSessions.length,
            totalReports: totalReports.count
          },
          monitoring: {
            fileMonitoring: 'available',
            windowMonitoring: 'available',
            commandMonitoring: 'available'
          },
          ai: {
            enabled: !!config.ai.apiKey,
            provider: config.ai.provider,
            model: config.ai.model
          }
        });
      } catch (error) {
        res.status(500).json({
          error: 'Failed to get system status',
          message: error.message
        });
      }
    });

    // 配置信息
    adminRouter.get('/config', (req, res) => {
      const safeConfig = {
        server: config.server,
        monitoring: config.monitoring,
        analysis: config.analysis,
        security: {
          ...config.security,
          apiKey: config.security.apiKey ? '***' : null
        },
        ai: {
          ...config.ai,
          apiKey: config.ai.apiKey ? '***' : null
        }
      };

      res.json(safeConfig);
    });

    // 清理数据库
    adminRouter.post('/cleanup', async (req, res) => {
      try {
        const { days = 30 } = req.body;
        const deletedCount = await database.cleanup(days);

        logger.audit('Database cleanup performed', { 
          daysToKeep: days, 
          deletedSessions: deletedCount,
          performedBy: req.ip
        });

        res.json({
          success: true,
          message: 'Database cleanup completed',
          deletedSessions: deletedCount,
          daysToKeep: days
        });
      } catch (error) {
        res.status(500).json({
          error: 'Database cleanup failed',
          message: error.message
        });
      }
    });

    // 重启服务
    adminRouter.post('/restart', (req, res) => {
      logger.audit('Service restart requested', { requestedBy: req.ip });
      
      res.json({
        success: true,
        message: 'Service restart initiated'
      });

      // 延迟重启以确保响应发送
      setTimeout(() => {
        process.exit(0);
      }, 1000);
    });

    this.app.use('/admin', adminRouter);
  }

  /**
   * 设置错误处理
   */
  setupErrorHandling() {
    // 全局错误处理中间件
    this.app.use((error, req, res, next) => {
      logger.error('Unhandled API error', {
        error: error.message,
        stack: error.stack,
        method: req.method,
        path: req.path,
        ip: req.ip
      });

      // 不要泄露内部错误信息到生产环境
      const isDevelopment = config.server.env === 'development';

      res.status(error.status || 500).json({
        error: 'Internal Server Error',
        message: isDevelopment ? error.message : 'An unexpected error occurred',
        timestamp: new Date().toISOString(),
        ...(isDevelopment && { stack: error.stack })
      });
    });

    // 处理未捕获的异常
    process.on('uncaughtException', (error) => {
      logger.error('Uncaught exception', { error: error.message, stack: error.stack });
      this.gracefulShutdown('uncaughtException');
    });

    // 处理未处理的Promise拒绝
    process.on('unhandledRejection', (reason, promise) => {
      logger.error('Unhandled promise rejection', { reason, promise });
      this.gracefulShutdown('unhandledRejection');
    });

    // 处理进程信号
    process.on('SIGTERM', () => {
      logger.info('SIGTERM received, starting graceful shutdown');
      this.gracefulShutdown('SIGTERM');
    });

    process.on('SIGINT', () => {
      logger.info('SIGINT received, starting graceful shutdown');
      this.gracefulShutdown('SIGINT');
    });
  }

  /**
   * 启动服务器
   */
  async start() {
    if (!this.isInitialized) {
      await this.init();
    }

    return new Promise((resolve, reject) => {
      this.server = this.app.listen(config.server.port, config.server.host, (error) => {
        if (error) {
          logger.error('Failed to start API server', { error: error.message });
          reject(error);
        } else {
          logger.info('API server started', {
            host: config.server.host,
            port: config.server.port,
            env: config.server.env,
            pid: process.pid
          });
          resolve();
        }
      });

      // 设置服务器超时
      this.server.keepAliveTimeout = config.performance.keepAliveTimeout;
      this.server.headersTimeout = config.performance.keepAliveTimeout + 1000;
    });
  }

  /**
   * 停止服务器
   */
  async stop() {
    if (!this.server) {
      return;
    }

    return new Promise((resolve) => {
      this.server.close(async () => {
        logger.info('API server stopped');
        
        // 关闭数据库连接
        await database.close();
        
        resolve();
      });
    });
  }

  /**
   * 优雅关闭
   */
  async gracefulShutdown(signal) {
    logger.info(`Graceful shutdown initiated by ${signal}`);

    try {
      // 停止接受新连接
      await this.stop();

      // 停止所有监控
      const fileMonitor = require('../collector/file-monitor');
      const windowMonitor = require('../collector/window-monitor');
      const commandMonitor = require('../collector/command-monitor');

      await Promise.all([
        fileMonitor.stopAllMonitoring(),
        windowMonitor.stopAllMonitoring(),
        commandMonitor.stopAllMonitoring()
      ]);

      logger.info('Graceful shutdown completed');
      process.exit(0);

    } catch (error) {
      logger.error('Error during graceful shutdown', { error: error.message });
      process.exit(1);
    }
  }

  /**
   * 获取应用实例
   */
  getApp() {
    return this.app;
  }

  /**
   * 获取服务器实例
   */
  getServer() {
    return this.server;
  }
}

// 创建服务器实例
const apiServer = new APIServer();

// 如果直接运行此文件，启动服务器
if (require.main === module) {
  apiServer.start().catch((error) => {
    console.error('Failed to start server:', error);
    process.exit(1);
  });
}

module.exports = apiServer;