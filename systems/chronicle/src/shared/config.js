const path = require('path');
require('dotenv').config();

const config = {
  // 服务器配置
  server: {
    port: process.env.PORT || 3000,
    host: process.env.HOST || 'localhost',
    env: process.env.NODE_ENV || 'development'
  },

  // 数据库配置
  database: {
    path: process.env.DB_PATH || path.join(__dirname, '../../data/chronicle.db'),
    maxConnections: 10,
    timeout: 30000
  },

  // AI服务配置
  ai: {
    provider: process.env.AI_PROVIDER || 'gemini', // 'gemini' | 'openai'
    apiKey: process.env.AI_API_KEY || process.env.GEMINI_API_KEY || process.env.OPENAI_API_KEY,
    model: process.env.AI_MODEL || 'gemini-pro',
    maxTokens: parseInt(process.env.AI_MAX_TOKENS) || 2048,
    temperature: parseFloat(process.env.AI_TEMPERATURE) || 0.3,
    timeout: parseInt(process.env.AI_TIMEOUT) || 30000
  },

  // 监控配置
  monitoring: {
    // 文件系统监控
    fileSystem: {
      enabled: process.env.FS_MONITOR_ENABLED !== 'false',
      ignorePatterns: [
        '**/node_modules/**',
        '**/.git/**',
        '**/.vscode/**',
        '**/.idea/**',
        '**/dist/**',
        '**/build/**',
        '**/*.log',
        '**/*.tmp',
        '**/.DS_Store'
      ],
      debounceMs: parseInt(process.env.FS_DEBOUNCE_MS) || 100
    },

    // 窗口监控
    window: {
      enabled: process.env.WINDOW_MONITOR_ENABLED !== 'false',
      pollIntervalMs: parseInt(process.env.WINDOW_POLL_INTERVAL) || 1000,
      trackInactive: process.env.TRACK_INACTIVE_WINDOWS === 'true'
    },

    // 命令行监控
    command: {
      enabled: process.env.CMD_MONITOR_ENABLED !== 'false',
      shells: ['bash', 'zsh', 'fish', 'powershell', 'cmd'],
      maxOutputLength: parseInt(process.env.MAX_OUTPUT_LENGTH) || 10000,
      captureEnvironment: process.env.CAPTURE_ENV === 'true'
    }
  },

  // 分析配置
  analysis: {
    // 触发AI分析的阈值
    aiTriggerThreshold: {
      logLength: parseInt(process.env.AI_TRIGGER_LOG_LENGTH) || 1000,
      errorKeywords: ['error', 'exception', 'failed', 'fatal', 'panic', 'traceback'],
      warningKeywords: ['warning', 'warn', 'deprecated', 'caution']
    },

    // 报告生成配置
    report: {
      maxSummaryLength: parseInt(process.env.MAX_SUMMARY_LENGTH) || 200,
      maxKeyLines: parseInt(process.env.MAX_KEY_LINES) || 5,
      maxKeyPhrases: parseInt(process.env.MAX_KEY_PHRASES) || 5,
      includeTimestamps: process.env.INCLUDE_TIMESTAMPS !== 'false',
      includeMetadata: process.env.INCLUDE_METADATA !== 'false'
    }
  },

  // 日志配置
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    file: process.env.LOG_FILE || path.join(__dirname, '../../logs/chronicle.log'),
    maxSize: process.env.LOG_MAX_SIZE || '10m',
    maxFiles: parseInt(process.env.LOG_MAX_FILES) || 5,
    format: process.env.LOG_FORMAT || 'combined'
  },

  // 安全配置
  security: {
    enableCors: process.env.ENABLE_CORS !== 'false',
    corsOrigins: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : ['*'],
    enableHelmet: process.env.ENABLE_HELMET !== 'false',
    apiKeyRequired: process.env.API_KEY_REQUIRED === 'true',
    apiKey: process.env.API_KEY,
    rateLimitEnabled: process.env.RATE_LIMIT_ENABLED !== 'false',
    rateLimitMax: parseInt(process.env.RATE_LIMIT_MAX) || 100,
    rateLimitWindowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 900000 // 15分钟
  },

  // 性能配置
  performance: {
    enableCompression: process.env.ENABLE_COMPRESSION !== 'false',
    maxRequestSize: process.env.MAX_REQUEST_SIZE || '10mb',
    requestTimeout: parseInt(process.env.REQUEST_TIMEOUT) || 30000,
    keepAliveTimeout: parseInt(process.env.KEEP_ALIVE_TIMEOUT) || 5000
  }
};

// 验证必需的配置
function validateConfig() {
  const errors = [];

  if (config.ai.enabled && !config.ai.apiKey) {
    errors.push('AI API key is required when AI analysis is enabled');
  }

  if (config.security.apiKeyRequired && !config.security.apiKey) {
    errors.push('API key is required when API key authentication is enabled');
  }

  if (errors.length > 0) {
    throw new Error(`Configuration validation failed:\n${errors.join('\n')}`);
  }
}

// 创建必要的目录
function ensureDirectories() {
  const fs = require('fs');
  const dirs = [
    path.dirname(config.database.path),
    path.dirname(config.logging.file),
    path.join(__dirname, '../../data'),
    path.join(__dirname, '../../logs')
  ];

  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

// 初始化配置
function init() {
  try {
    ensureDirectories();
    validateConfig();
    return config;
  } catch (error) {
    console.error('Configuration initialization failed:', error.message);
    process.exit(1);
  }
}

module.exports = {
  ...config,
  init,
  validateConfig,
  ensureDirectories
};