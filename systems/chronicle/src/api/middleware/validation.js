const Joi = require('joi');
const { createModuleLogger } = require('../../shared/logger');

const logger = createModuleLogger('validation-middleware');

/**
 * 创建验证中间件
 */
function createValidator(schema, source = 'body') {
  return (req, res, next) => {
    const data = req[source];
    const { error, value } = schema.validate(data, {
      abortEarly: false,
      stripUnknown: true,
      convert: true
    });

    if (error) {
      const errors = error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message,
        value: detail.context?.value
      }));

      logger.warn('Validation failed', {
        source,
        errors,
        originalData: data
      });

      return res.status(400).json({
        error: 'Validation failed',
        message: 'The request data is invalid',
        details: errors
      });
    }

    // 使用验证后的值替换原始数据
    req[source] = value;
    next();
  };
}

/**
 * 验证模式定义
 */
const schemas = {
  // 会话相关
  startSession: Joi.object({
    project_name: Joi.string().min(1).max(100).required()
      .messages({
        'string.empty': 'Project name cannot be empty',
        'string.max': 'Project name cannot exceed 100 characters'
      }),
    project_path: Joi.string().min(1).max(500).required()
      .messages({
        'string.empty': 'Project path cannot be empty',
        'string.max': 'Project path cannot exceed 500 characters'
      }),
    metadata: Joi.object().optional(),
    options: Joi.object({
      file_monitoring: Joi.boolean().default(true),
      window_monitoring: Joi.boolean().default(true),
      command_monitoring: Joi.boolean().default(true),
      ai_analysis: Joi.boolean().default(true)
    }).optional()
  }),

  stopSession: Joi.object({
    force: Joi.boolean().default(false)
  }),

  // 报告相关
  generateReport: Joi.object({
    type: Joi.string().valid('summary', 'detailed', 'error-focused', 'comprehensive')
      .default('comprehensive'),
    format: Joi.string().valid('json', 'markdown', 'html').default('json'),
    include_raw_data: Joi.boolean().default(false),
    max_events: Joi.number().integer().min(1).max(10000).optional(),
    date_range: Joi.object({
      start: Joi.date().iso().optional(),
      end: Joi.date().iso().optional()
    }).optional()
  }),

  // 查询参数
  queryParams: Joi.object({
    limit: Joi.number().integer().min(1).max(1000).default(50),
    offset: Joi.number().integer().min(0).default(0),
    sort: Joi.string().valid('asc', 'desc').default('desc'),
    sort_by: Joi.string().valid('timestamp', 'type', 'importance').default('timestamp'),
    type: Joi.string().valid('file', 'window', 'command').optional(),
    start_time: Joi.date().iso().optional(),
    end_time: Joi.date().iso().optional()
  }),

  // 配置更新
  updateConfig: Joi.object({
    monitoring: Joi.object({
      file_system: Joi.object({
        enabled: Joi.boolean(),
        debounce_ms: Joi.number().integer().min(10).max(5000),
        ignore_patterns: Joi.array().items(Joi.string())
      }).optional(),
      window: Joi.object({
        enabled: Joi.boolean(),
        poll_interval_ms: Joi.number().integer().min(100).max(10000),
        track_inactive: Joi.boolean()
      }).optional(),
      command: Joi.object({
        enabled: Joi.boolean(),
        max_output_length: Joi.number().integer().min(100).max(100000),
        capture_environment: Joi.boolean()
      }).optional()
    }).optional(),
    ai: Joi.object({
      provider: Joi.string().valid('gemini', 'openai'),
      model: Joi.string(),
      max_tokens: Joi.number().integer().min(100).max(8000),
      temperature: Joi.number().min(0).max(2)
    }).optional()
  }),

  // 分析请求
  analyzeText: Joi.object({
    text: Joi.string().min(1).max(50000).required(),
    context: Joi.object({
      event_type: Joi.string().optional(),
      command: Joi.string().optional(),
      exit_code: Joi.number().integer().optional(),
      file_extension: Joi.string().optional()
    }).optional(),
    options: Joi.object({
      use_ai: Joi.boolean().default(true),
      include_patterns: Joi.boolean().default(true),
      max_key_lines: Joi.number().integer().min(1).max(10).default(5),
      max_key_phrases: Joi.number().integer().min(1).max(10).default(5)
    }).optional()
  })
};

/**
 * 路径参数验证
 */
const pathSchemas = {
  sessionId: Joi.string().pattern(/^session_[a-zA-Z0-9_]+$/).required()
    .messages({
      'string.pattern.base': 'Invalid session ID format'
    }),
  
  reportId: Joi.string().pattern(/^report_[a-zA-Z0-9_]+$/).required()
    .messages({
      'string.pattern.base': 'Invalid report ID format'
    }),

  eventId: Joi.string().pattern(/^(file|window|command)_[a-zA-Z0-9_]+$/).required()
    .messages({
      'string.pattern.base': 'Invalid event ID format'
    })
};

/**
 * 验证路径参数
 */
function validatePath(paramName, schema) {
  return (req, res, next) => {
    const value = req.params[paramName];
    const { error, value: validatedValue } = schema.validate(value);

    if (error) {
      logger.warn('Path parameter validation failed', {
        parameter: paramName,
        value,
        error: error.message
      });

      return res.status(400).json({
        error: 'Invalid path parameter',
        message: error.message,
        parameter: paramName
      });
    }

    req.params[paramName] = validatedValue;
    next();
  };
}

/**
 * 验证请求体
 */
function validateBody(schemaName) {
  const schema = schemas[schemaName];
  if (!schema) {
    throw new Error(`Unknown validation schema: ${schemaName}`);
  }
  return createValidator(schema, 'body');
}

/**
 * 验证查询参数
 */
function validateQuery(schemaName = 'queryParams') {
  const schema = schemas[schemaName];
  if (!schema) {
    throw new Error(`Unknown validation schema: ${schemaName}`);
  }
  return createValidator(schema, 'query');
}

/**
 * 自定义验证器
 */
const customValidators = {
  /**
   * 验证文件路径
   */
  validateFilePath: (req, res, next) => {
    const { project_path } = req.body;
    
    if (project_path) {
      const path = require('path');
      const fs = require('fs');
      
      try {
        const resolvedPath = path.resolve(project_path);
        
        // 检查路径是否存在
        if (!fs.existsSync(resolvedPath)) {
          return res.status(400).json({
            error: 'Invalid project path',
            message: 'The specified project path does not exist',
            path: project_path
          });
        }

        // 检查是否为目录
        const stats = fs.statSync(resolvedPath);
        if (!stats.isDirectory()) {
          return res.status(400).json({
            error: 'Invalid project path',
            message: 'The specified path is not a directory',
            path: project_path
          });
        }

        // 更新为解析后的绝对路径
        req.body.project_path = resolvedPath;
        
      } catch (error) {
        logger.error('File path validation error', { 
          path: project_path, 
          error: error.message 
        });
        
        return res.status(400).json({
          error: 'Invalid project path',
          message: 'Cannot access the specified project path',
          details: error.message
        });
      }
    }
    
    next();
  },

  /**
   * 验证会话存在性
   */
  validateSessionExists: async (req, res, next) => {
    const sessionId = req.params.sessionId;
    
    try {
      const database = require('../../collector/database');
      const session = await database.getSession(sessionId);
      
      if (!session) {
        return res.status(404).json({
          error: 'Session not found',
          message: `No session found with ID: ${sessionId}`,
          sessionId
        });
      }

      req.session = session;
      next();
      
    } catch (error) {
      logger.error('Session validation error', { 
        sessionId, 
        error: error.message 
      });
      
      return res.status(500).json({
        error: 'Session validation failed',
        message: 'Unable to validate session existence'
      });
    }
  },

  /**
   * 验证内容类型
   */
  validateContentType: (expectedType = 'application/json') => {
    return (req, res, next) => {
      if (req.method === 'GET' || req.method === 'DELETE') {
        return next();
      }

      const contentType = req.get('Content-Type');
      
      if (!contentType || !contentType.includes(expectedType)) {
        return res.status(400).json({
          error: 'Invalid content type',
          message: `Expected ${expectedType}`,
          received: contentType || 'none'
        });
      }

      next();
    };
  },

  /**
   * 验证请求大小
   */
  validateRequestSize: (maxSize = 10 * 1024 * 1024) => {
    return (req, res, next) => {
      const contentLength = parseInt(req.get('Content-Length') || '0');
      
      if (contentLength > maxSize) {
        return res.status(413).json({
          error: 'Request too large',
          message: `Request size exceeds maximum allowed size of ${maxSize} bytes`,
          size: contentLength,
          maxSize
        });
      }

      next();
    };
  }
};

/**
 * 组合验证中间件
 */
function combineValidators(...validators) {
  return (req, res, next) => {
    let index = 0;

    function runNext(error) {
      if (error) {
        return next(error);
      }

      if (index >= validators.length) {
        return next();
      }

      const validator = validators[index++];
      validator(req, res, runNext);
    }

    runNext();
  };
}

module.exports = {
  schemas,
  pathSchemas,
  validateBody,
  validateQuery,
  validatePath,
  customValidators,
  combineValidators,
  createValidator
};