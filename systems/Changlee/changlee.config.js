/**
 * Changlee系统统一配置文件
 * 整合所有分散的配置，支持环境变量覆盖
 */

const path = require('path');

// 环境变量辅助函数
const env = (key, defaultValue, type = 'string') => {
  const value = process.env[key] || defaultValue;
  
  switch (type) {
    case 'number':
      return Number(value);
    case 'boolean':
      return value === 'true' || value === true;
    case 'json':
      try {
        return JSON.parse(value);
      } catch {
        return defaultValue;
      }
    default:
      return value;
  }
};

module.exports = {
  // 系统基础配置
  system: {
    name: env('APP_NAME', '长离的学习胶囊'),
    version: env('APP_VERSION', '2.0.0'),
    description: '情感陪伴式桌面宠物英语学习应用',
    author: 'Changlee Team',
    homepage: env('APP_HOMEPAGE', 'https://changlee.example.com'),
    debug: env('DEBUG', false, 'boolean'),
    logLevel: env('LOG_LEVEL', 'info')
  },

  // 服务器配置
  servers: {
    web: {
      port: env('WEB_PORT', 8080, 'number'),
      host: env('WEB_HOST', 'localhost'),
      staticPath: path.join(__dirname, 'src/web/public')
    },
    backend: {
      port: env('BACKEND_PORT', 3001, 'number'),
      host: env('BACKEND_HOST', 'localhost'),
      cors: {
        origin: env('CORS_ORIGIN', '*'),
        credentials: true
      }
    },
    electron: {
      width: env('ELECTRON_WIDTH', 1200, 'number'),
      height: env('ELECTRON_HEIGHT', 800, 'number'),
      devTools: env('ELECTRON_DEV_TOOLS', false, 'boolean')
    }
  },

  // 桌宠配置
  pet: {
    defaultPosition: {
      x: env('PET_X', 800, 'number'),
      y: env('PET_Y', 600, 'number')
    },
    size: {
      width: env('PET_WIDTH', 120, 'number'),
      height: env('PET_HEIGHT', 120, 'number')
    },
    animations: {
      idle: { duration: 3000, repeat: true },
      excited: { duration: 600, repeat: 3 },
      dragging: { duration: 200 },
      sleeping: { duration: 5000 }
    },
    behaviors: {
      randomActionInterval: [10000, 30000],
      sleepTime: { start: '23:00', end: '07:00' },
      activeHours: { start: '08:00', end: '22:00' }
    }
  },

  // AI配置
  ai: {
    provider: env('AI_PROVIDER', 'openai'),
    apiKey: env('AI_API_KEY', ''),
    model: env('AI_MODEL', 'gpt-3.5-turbo'),
    maxTokens: env('AI_MAX_TOKENS', 150, 'number'),
    temperature: env('AI_TEMPERATURE', 0.7, 'number'),
    
    // 本地AI配置
    local: {
      enabled: env('LOCAL_AI_ENABLED', false, 'boolean'),
      modelPath: env('LOCAL_AI_MODEL_PATH', ''),
      port: env('LOCAL_AI_PORT', 8080, 'number')
    }
  },

  // RAG系统配置
  rag: {
    enabled: env('RAG_ENABLED', false, 'boolean'),
    endpoint: env('RAG_ENDPOINT', 'http://localhost:8501'),
    apiKey: env('RAG_API_KEY', ''),
    timeout: env('RAG_TIMEOUT', 30000, 'number')
  },

  // Chronicle集成配置
  chronicle: {
    enabled: env('CHRONICLE_ENABLED', false, 'boolean'),
    endpoint: env('CHRONICLE_ENDPOINT', 'http://localhost:3000'),
    apiKey: env('CHRONICLE_API_KEY', ''),
    syncInterval: env('CHRONICLE_SYNC_INTERVAL', 300000, 'number') // 5分钟
  },

  // 数据库配置
  database: {
    type: env('DB_TYPE', 'sqlite'),
    path: env('DB_PATH', path.join(__dirname, 'database/changlee.db')),
    
    // 其他数据库选项
    mysql: {
      host: env('MYSQL_HOST', 'localhost'),
      port: env('MYSQL_PORT', 3306, 'number'),
      user: env('MYSQL_USER', 'root'),
      password: env('MYSQL_PASSWORD', ''),
      database: env('MYSQL_DATABASE', 'changlee')
    }
  },

  // 学习系统配置
  learning: {
    spacedRepetition: {
      initialInterval: env('SR_INITIAL_INTERVAL', 1, 'number'),
      maxInterval: env('SR_MAX_INTERVAL', 365, 'number'),
      easeFactor: env('SR_EASE_FACTOR', 2.5, 'number'),
      easyBonus: env('SR_EASY_BONUS', 1.3, 'number'),
      hardPenalty: env('SR_HARD_PENALTY', 0.8, 'number')
    },
    
    dailyGoals: {
      newWords: env('DAILY_NEW_WORDS', 10, 'number'),
      reviews: env('DAILY_REVIEWS', 50, 'number'),
      studyMinutes: env('DAILY_STUDY_MINUTES', 30, 'number')
    },
    
    gamification: {
      pointsPerCorrect: env('POINTS_PER_CORRECT', 10, 'number'),
      pointsPerStreak: env('POINTS_PER_STREAK', 5, 'number'),
      levelUpThreshold: env('LEVEL_UP_THRESHOLD', 1000, 'number')
    }
  },

  // 推送系统配置
  push: {
    dailyLimit: env('PUSH_DAILY_LIMIT', 3, 'number'),
    cooldownMinutes: env('PUSH_COOLDOWN', 120, 'number'),
    quietHours: { 
      start: env('PUSH_QUIET_START', '22:00'), 
      end: env('PUSH_QUIET_END', '08:00') 
    },
    
    types: {
      newWord: { weight: 0.4, message: '发现新单词' },
      review: { weight: 0.5, message: '复习时间到' },
      encouragement: { weight: 0.1, message: '鼓励消息' }
    },
    
    triggers: {
      inactiveMinutes: env('PUSH_INACTIVE_MINUTES', 30, 'number'),
      learningStreak: env('PUSH_LEARNING_STREAK', true, 'boolean'),
      timeBasedOptimization: env('PUSH_TIME_OPTIMIZATION', true, 'boolean')
    }
  },

  // 文件路径配置
  paths: {
    root: __dirname,
    src: path.join(__dirname, 'src'),
    database: path.join(__dirname, 'database'),
    assets: path.join(__dirname, 'assets'),
    logs: path.join(__dirname, 'logs'),
    temp: path.join(__dirname, 'temp'),
    
    // 子系统路径
    ragSystem: env('RAG_SYSTEM_PATH', path.resolve(__dirname, '../rag-system')),
    chronicle: env('CHRONICLE_PATH', path.resolve(__dirname, '../chronicle'))
  },

  // 开发配置
  development: {
    hotReload: env('HOT_RELOAD', true, 'boolean'),
    mockData: env('MOCK_DATA', false, 'boolean'),
    debugMode: env('DEBUG_MODE', false, 'boolean'),
    logRequests: env('LOG_REQUESTS', true, 'boolean')
  },

  // 生产配置
  production: {
    minify: env('MINIFY', true, 'boolean'),
    compress: env('COMPRESS', true, 'boolean'),
    cacheStatic: env('CACHE_STATIC', true, 'boolean'),
    errorReporting: env('ERROR_REPORTING', true, 'boolean')
  },

  // 安全配置
  security: {
    sessionSecret: env('SESSION_SECRET', 'changlee-secret-key'),
    jwtSecret: env('JWT_SECRET', 'changlee-jwt-secret'),
    rateLimitWindow: env('RATE_LIMIT_WINDOW', 900000, 'number'), // 15分钟
    rateLimitMax: env('RATE_LIMIT_MAX', 100, 'number'),
    
    cors: {
      origin: env('CORS_ORIGINS', ['http://localhost:3000', 'http://localhost:8080'], 'json'),
      credentials: true
    }
  },

  // 日志配置
  logging: {
    level: env('LOG_LEVEL', 'info'),
    file: env('LOG_FILE', path.join(__dirname, 'logs/changlee.log')),
    maxSize: env('LOG_MAX_SIZE', '10m'),
    maxFiles: env('LOG_MAX_FILES', 5, 'number'),
    
    categories: {
      app: env('LOG_APP', true, 'boolean'),
      ai: env('LOG_AI', true, 'boolean'),
      database: env('LOG_DATABASE', true, 'boolean'),
      learning: env('LOG_LEARNING', true, 'boolean'),
      push: env('LOG_PUSH', true, 'boolean')
    }
  }
};

// 配置验证函数
module.exports.validate = function() {
  const config = module.exports;
  const errors = [];
  
  // 验证必需的配置
  if (!config.system.name) {
    errors.push('系统名称不能为空');
  }
  
  if (config.servers.web.port < 1 || config.servers.web.port > 65535) {
    errors.push('Web端口必须在1-65535之间');
  }
  
  if (config.servers.backend.port < 1 || config.servers.backend.port > 65535) {
    errors.push('Backend端口必须在1-65535之间');
  }
  
  if (config.ai.enabled && !config.ai.apiKey) {
    errors.push('启用AI时必须提供API密钥');
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
};

// 获取当前环境配置
module.exports.getEnvironmentConfig = function() {
  const env = process.env.NODE_ENV || 'development';
  const config = module.exports;
  
  return {
    ...config,
    environment: env,
    isDevelopment: env === 'development',
    isProduction: env === 'production',
    isTest: env === 'test'
  };
};