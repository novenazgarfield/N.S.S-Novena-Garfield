const winston = require('winston');
const path = require('path');
const config = require('./config');

// 自定义日志格式
const logFormat = winston.format.combine(
  winston.format.timestamp({
    format: 'YYYY-MM-DD HH:mm:ss.SSS'
  }),
  winston.format.errors({ stack: true }),
  winston.format.json(),
  winston.format.printf(({ timestamp, level, message, stack, ...meta }) => {
    let log = `${timestamp} [${level.toUpperCase()}]`;
    
    if (meta.module) {
      log += ` [${meta.module}]`;
    }
    
    log += `: ${message}`;
    
    if (stack) {
      log += `\n${stack}`;
    }
    
    if (Object.keys(meta).length > 0 && !meta.module) {
      log += `\n${JSON.stringify(meta, null, 2)}`;
    }
    
    return log;
  })
);

// 创建日志器
const logger = winston.createLogger({
  level: config.logging.level,
  format: logFormat,
  defaultMeta: { service: 'chronicle' },
  transports: [
    // 文件日志
    new winston.transports.File({
      filename: config.logging.file,
      maxsize: config.logging.maxSize,
      maxFiles: config.logging.maxFiles,
      tailable: true
    }),
    
    // 错误日志单独文件
    new winston.transports.File({
      filename: path.join(path.dirname(config.logging.file), 'error.log'),
      level: 'error',
      maxsize: config.logging.maxSize,
      maxFiles: config.logging.maxFiles,
      tailable: true
    })
  ]
});

// 开发环境添加控制台输出
if (config.server.env === 'development') {
  logger.add(new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize(),
      winston.format.simple(),
      winston.format.printf(({ timestamp, level, message, module }) => {
        let log = `${timestamp} [${level}]`;
        if (module) {
          log += ` [${module}]`;
        }
        log += `: ${message}`;
        return log;
      })
    )
  }));
}

// 创建模块化日志器
function createModuleLogger(moduleName) {
  return {
    debug: (message, meta = {}) => logger.debug(message, { module: moduleName, ...meta }),
    info: (message, meta = {}) => logger.info(message, { module: moduleName, ...meta }),
    warn: (message, meta = {}) => logger.warn(message, { module: moduleName, ...meta }),
    error: (message, meta = {}) => logger.error(message, { module: moduleName, ...meta }),
    
    // 性能日志
    perf: (operation, duration, meta = {}) => {
      logger.info(`Performance: ${operation} completed in ${duration}ms`, {
        module: moduleName,
        operation,
        duration,
        ...meta
      });
    },
    
    // 审计日志
    audit: (action, details = {}) => {
      logger.info(`Audit: ${action}`, {
        module: moduleName,
        action,
        audit: true,
        ...details
      });
    }
  };
}

// 错误处理
logger.on('error', (error) => {
  console.error('Logger error:', error);
});

// 优雅关闭
process.on('SIGINT', () => {
  logger.info('Shutting down logger...');
  logger.end();
});

process.on('SIGTERM', () => {
  logger.info('Shutting down logger...');
  logger.end();
});

module.exports = {
  logger,
  createModuleLogger
};