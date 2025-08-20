/**
 * Chronicle集成配置文件
 * 管理Chronicle与Changlee之间的集成设置
 */

const path = require('path');

const chronicleConfig = {
  // Chronicle服务连接配置
  connection: {
    // Chronicle服务URL
    baseUrl: process.env.CHRONICLE_URL || 'http://localhost:3000',
    
    // API密钥（如果Chronicle启用了认证）
    apiKey: process.env.CHRONICLE_API_KEY || null,
    
    // 连接超时时间（毫秒）
    timeout: parseInt(process.env.CHRONICLE_TIMEOUT) || 30000,
    
    // 重试配置
    retry: {
      attempts: parseInt(process.env.CHRONICLE_RETRY_ATTEMPTS) || 3,
      delay: parseInt(process.env.CHRONICLE_RETRY_DELAY) || 1000
    },
    
    // 自动重连
    autoReconnect: process.env.CHRONICLE_AUTO_RECONNECT !== 'false',
    
    // 健康检查间隔（毫秒）
    healthCheckInterval: parseInt(process.env.CHRONICLE_HEALTH_INTERVAL) || 60000
  },

  // 学习会话监控配置
  monitoring: {
    // 默认监控设置
    defaults: {
      fileMonitoring: true,      // 文件系统监控
      windowMonitoring: true,    // 窗口活动监控
      commandMonitoring: false   // 命令行监控（默认关闭以保护隐私）
    },
    
    // 按学习类型的监控配置
    byLearningType: {
      word_learning: {
        fileMonitoring: true,
        windowMonitoring: true,
        commandMonitoring: false
      },
      spelling_practice: {
        fileMonitoring: false,
        windowMonitoring: true,
        commandMonitoring: false
      },
      reading_session: {
        fileMonitoring: true,
        windowMonitoring: true,
        commandMonitoring: false
      },
      ai_conversation: {
        fileMonitoring: false,
        windowMonitoring: true,
        commandMonitoring: false
      },
      music_learning: {
        fileMonitoring: false,
        windowMonitoring: true,
        commandMonitoring: false
      },
      rag_interaction: {
        fileMonitoring: true,
        windowMonitoring: true,
        commandMonitoring: false
      }
    }
  },

  // 学习分析配置
  analysis: {
    // 启用Changlee特定的学习分析
    enableChangleeAnalysis: true,
    
    // 分析类型
    analysisTypes: [
      'attention_patterns',     // 注意力模式分析
      'learning_efficiency',    // 学习效率分析
      'progress_tracking',      // 进度跟踪
      'behavior_insights',      // 行为洞察
      'recommendation_engine'   // 推荐引擎
    ],
    
    // 报告生成配置
    reports: {
      // 自动生成报告
      autoGenerate: true,
      
      // 报告格式
      formats: ['json', 'summary'],
      
      // 包含原始数据
      includeRawData: false,
      
      // 报告保留时间（天）
      retentionDays: 30
    }
  },

  // 数据隐私和安全配置
  privacy: {
    // 数据匿名化
    anonymizeData: true,
    
    // 敏感信息过滤
    filterSensitiveInfo: true,
    
    // 允许的文件扩展名监控
    allowedFileExtensions: [
      '.txt', '.md', '.json', '.js', '.jsx', '.ts', '.tsx',
      '.py', '.html', '.css', '.yml', '.yaml'
    ],
    
    // 排除的目录
    excludedDirectories: [
      'node_modules',
      '.git',
      'dist',
      'build',
      'temp',
      'cache',
      '.env'
    ],
    
    // 敏感关键词过滤
    sensitiveKeywords: [
      'password',
      'token',
      'secret',
      'key',
      'credential',
      'auth'
    ]
  },

  // 性能优化配置
  performance: {
    // 批处理大小
    batchSize: 100,
    
    // 数据压缩
    enableCompression: true,
    
    // 缓存配置
    cache: {
      enabled: true,
      ttl: 300000, // 5分钟
      maxSize: 1000
    },
    
    // 限流配置
    rateLimit: {
      enabled: true,
      maxRequests: 100,
      windowMs: 60000 // 1分钟
    }
  },

  // 学习类型映射
  learningTypes: {
    WORD_LEARNING: {
      id: 'word_learning',
      name: '单词学习',
      description: '英语单词学习和记忆',
      icon: '📝',
      color: '#667eea'
    },
    SPELLING_PRACTICE: {
      id: 'spelling_practice',
      name: '拼写练习',
      description: '单词拼写练习和测试',
      icon: '✏️',
      color: '#f093fb'
    },
    READING_SESSION: {
      id: 'reading_session',
      name: '阅读会话',
      description: '英语阅读理解练习',
      icon: '📖',
      color: '#4facfe'
    },
    AI_CONVERSATION: {
      id: 'ai_conversation',
      name: 'AI对话',
      description: '与长离AI的学习对话',
      icon: '🤖',
      color: '#764ba2'
    },
    MUSIC_LEARNING: {
      id: 'music_learning',
      name: '音乐学习',
      description: '通过音乐学习英语',
      icon: '🎵',
      color: '#FF6B6B'
    },
    RAG_INTERACTION: {
      id: 'rag_interaction',
      name: 'RAG交互',
      description: '文档检索和问答学习',
      icon: '🔍',
      color: '#4ECDC4'
    }
  },

  // 通知配置
  notifications: {
    // 启用通知
    enabled: true,
    
    // 通知类型
    types: {
      sessionStart: true,      // 会话开始通知
      sessionEnd: true,        // 会话结束通知
      reportReady: true,       // 报告生成完成通知
      connectionLost: true,    // 连接断开通知
      connectionRestored: true // 连接恢复通知
    },
    
    // 通知样式
    style: {
      position: 'top-right',
      duration: 5000,
      showProgress: true
    }
  },

  // 开发和调试配置
  development: {
    // 启用调试模式
    debug: process.env.NODE_ENV === 'development',
    
    // 详细日志
    verboseLogging: process.env.CHRONICLE_VERBOSE === 'true',
    
    // 模拟模式（用于测试）
    mockMode: process.env.CHRONICLE_MOCK === 'true',
    
    // 测试配置
    testing: {
      enabled: process.env.NODE_ENV === 'test',
      mockResponses: true,
      skipActualRequests: true
    }
  },

  // 集成特性开关
  features: {
    // 启用学习会话记录
    sessionRecording: true,
    
    // 启用智能分析
    intelligentAnalysis: true,
    
    // 启用学习建议
    learningRecommendations: true,
    
    // 启用进度跟踪
    progressTracking: true,
    
    // 启用历史分析
    historicalAnalysis: true,
    
    // 启用实时监控
    realTimeMonitoring: true,
    
    // 启用批量操作
    batchOperations: true
  },

  // 错误处理配置
  errorHandling: {
    // 错误重试策略
    retryStrategy: 'exponential',
    
    // 最大重试次数
    maxRetries: 3,
    
    // 错误日志级别
    logLevel: 'error',
    
    // 静默错误（不显示给用户）
    silentErrors: [
      'ECONNREFUSED',
      'TIMEOUT',
      'NETWORK_ERROR'
    ],
    
    // 降级策略
    fallbackStrategy: 'graceful'
  }
};

/**
 * 获取学习类型配置
 */
function getLearningTypeConfig(type) {
  return chronicleConfig.learningTypes[type.toUpperCase()] || 
         chronicleConfig.learningTypes.WORD_LEARNING;
}

/**
 * 获取监控配置
 */
function getMonitoringConfig(learningType) {
  return chronicleConfig.monitoring.byLearningType[learningType] || 
         chronicleConfig.monitoring.defaults;
}

/**
 * 验证配置
 */
function validateConfig() {
  const errors = [];
  
  // 检查必要的配置
  if (!chronicleConfig.connection.baseUrl) {
    errors.push('Chronicle服务URL未配置');
  }
  
  if (chronicleConfig.connection.timeout < 1000) {
    errors.push('连接超时时间过短');
  }
  
  if (chronicleConfig.connection.retry.attempts < 1) {
    errors.push('重试次数必须大于0');
  }
  
  return errors;
}

/**
 * 获取环境特定配置
 */
function getEnvironmentConfig() {
  const env = process.env.NODE_ENV || 'development';
  
  const envConfigs = {
    development: {
      connection: {
        timeout: 10000,
        retry: { attempts: 2, delay: 500 }
      },
      development: {
        debug: true,
        verboseLogging: true
      }
    },
    production: {
      connection: {
        timeout: 30000,
        retry: { attempts: 5, delay: 2000 }
      },
      development: {
        debug: false,
        verboseLogging: false
      },
      performance: {
        cache: { enabled: true, ttl: 600000 }
      }
    },
    test: {
      connection: {
        timeout: 5000,
        retry: { attempts: 1, delay: 100 }
      },
      development: {
        debug: false,
        mockMode: true
      }
    }
  };
  
  return envConfigs[env] || envConfigs.development;
}

/**
 * 合并配置
 */
function mergeConfig(baseConfig, envConfig) {
  function deepMerge(target, source) {
    for (const key in source) {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        target[key] = target[key] || {};
        deepMerge(target[key], source[key]);
      } else {
        target[key] = source[key];
      }
    }
    return target;
  }
  
  return deepMerge({ ...baseConfig }, envConfig);
}

// 应用环境特定配置
const envConfig = getEnvironmentConfig();
const finalConfig = mergeConfig(chronicleConfig, envConfig);

// 验证最终配置
const configErrors = validateConfig();
if (configErrors.length > 0) {
  console.warn('Chronicle配置警告:', configErrors.join(', '));
}

module.exports = {
  config: finalConfig,
  getLearningTypeConfig,
  getMonitoringConfig,
  validateConfig,
  getEnvironmentConfig
};