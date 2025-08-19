// 长离的学习胶囊 - 应用配置文件

module.exports = {
  // 应用基本信息
  app: {
    name: '长离的学习胶囊',
    version: '1.0.0',
    description: '情感陪伴式桌面宠物英语学习应用',
    author: 'Changlee Team',
    homepage: 'https://changlee.example.com'
  },

  // 桌宠配置
  pet: {
    defaultPosition: { x: 800, y: 600 },
    size: { width: 120, height: 120 },
    animations: {
      idle: { duration: 3000, repeat: true },
      excited: { duration: 600, repeat: 3 },
      dragging: { duration: 200 },
      sleeping: { duration: 5000 }
    },
    behaviors: {
      randomActionInterval: [10000, 30000], // 10-30秒随机行为
      sleepTime: { start: '23:00', end: '07:00' },
      activeHours: { start: '08:00', end: '22:00' }
    }
  },

  // 推送系统配置
  push: {
    dailyLimit: 3,
    cooldownMinutes: 120, // 2小时冷却
    quietHours: { start: '22:00', end: '08:00' },
    types: {
      newWord: { weight: 0.4, message: '发现新单词' },
      review: { weight: 0.5, message: '复习时间到' },
      encouragement: { weight: 0.1, message: '鼓励消息' }
    },
    triggers: {
      inactiveMinutes: 30, // 30分钟无活动后可推送
      learningStreak: true, // 学习连续性检查
      timeBasedOptimization: true // 基于用户习惯优化时间
    }
  },

  // 学习系统配置
  learning: {
    // 间隔重复算法参数
    spacedRepetition: {
      initialInterval: 1, // 首次复习间隔（天）
      easyInterval: 6, // 简单复习间隔（天）
      defaultEaseFactor: 2.5,
      minEaseFactor: 1.3,
      maxEaseFactor: 4.0,
      easeFactorAdjustment: {
        perfect: 0.1,
        good: 0.0,
        hard: -0.15,
        again: -0.2
      }
    },
    
    // 学习目标
    dailyGoals: {
      newWords: 5,
      reviewWords: 10,
      practiceMinutes: 20,
      accuracy: 80 // 目标正确率
    },
    
    // 难度等级
    difficultyLevels: {
      1: { name: '入门', color: '#4ecdc4', multiplier: 0.8 },
      2: { name: '初级', color: '#45b7d1', multiplier: 1.0 },
      3: { name: '中级', color: '#f39c12', multiplier: 1.2 },
      4: { name: '高级', color: '#e67e22', multiplier: 1.5 },
      5: { name: '专家', color: '#e74c3c', multiplier: 2.0 }
    },
    
    // 单词分类
    categories: {
      ielts: { name: '雅思核心', priority: 1 },
      toefl: { name: '托福必备', priority: 1 },
      gre: { name: 'GRE词汇', priority: 2 },
      business: { name: '商务英语', priority: 2 },
      daily: { name: '日常用语', priority: 3 },
      academic: { name: '学术词汇', priority: 2 },
      custom: { name: '自定义', priority: 3 }
    }
  },

  // AI服务配置
  ai: {
    provider: 'gemini',
    model: 'gemini-pro',
    apiEndpoint: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
    maxTokens: 1024,
    temperature: 0.7,
    
    // 内容生成配置
    contentGeneration: {
      memoryStory: {
        maxLength: 150,
        style: 'warm_companion',
        includePersonality: true
      },
      contextStory: {
        maxLength: 120,
        includeRelatedWords: true,
        difficultyAdaptive: true
      },
      learningTips: {
        includeMnemonic: true,
        includeCollocations: true,
        includeCommonMistakes: true
      }
    },
    
    // 长离人设配置
    personality: {
      name: '长离',
      species: '智慧小猫',
      traits: ['温柔', '耐心', '智慧', '陪伴'],
      speakingStyle: '温暖亲切，善用比喻',
      relationship: '专属学习伙伴',
      background: '来自知识海洋的神秘小猫'
    }
  },

  // 数据库配置
  database: {
    type: 'sqlite',
    filename: 'changlee.db',
    backup: {
      enabled: true,
      interval: '24h',
      maxBackups: 7
    },
    optimization: {
      vacuumInterval: '7d',
      analyzeInterval: '1d'
    }
  },

  // 用户界面配置
  ui: {
    themes: {
      light: {
        primary: '#667eea',
        secondary: '#764ba2',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        surface: 'rgba(255, 255, 255, 0.9)',
        text: '#333333'
      },
      dark: {
        primary: '#3498db',
        secondary: '#9b59b6',
        background: 'linear-gradient(135deg, #2c3e50 0%, #34495e 100%)',
        surface: 'rgba(255, 255, 255, 0.1)',
        text: '#ffffff'
      }
    },
    
    animations: {
      enabled: true,
      reducedMotion: false,
      duration: {
        fast: 200,
        normal: 300,
        slow: 500
      }
    },
    
    sounds: {
      enabled: true,
      volume: 0.7,
      files: {
        'pet-click': 'pet-click.mp3',
        'notification': 'notification.mp3',
        'success': 'success.mp3',
        'error': 'error.mp3',
        'pronunciation': 'pronunciation.mp3'
      }
    }
  },

  // 性能配置
  performance: {
    maxMemoryUsage: 512, // MB
    cacheSize: 100, // 缓存的单词数量
    backgroundTaskInterval: 60000, // 1分钟
    statisticsUpdateInterval: 300000, // 5分钟
    
    // 渲染优化
    rendering: {
      enableGPUAcceleration: true,
      maxFPS: 60,
      enableVSync: true
    }
  },

  // 安全配置
  security: {
    encryptUserData: true,
    apiKeyEncryption: true,
    sessionTimeout: 24 * 60 * 60 * 1000, // 24小时
    maxLoginAttempts: 5
  },

  // 开发配置
  development: {
    enableDevTools: process.env.NODE_ENV === 'development',
    enableHotReload: true,
    logLevel: 'debug',
    mockAPI: false
  },

  // 更新配置
  updates: {
    checkInterval: '24h',
    autoDownload: false,
    notifyUser: true,
    updateServer: 'https://updates.changlee.example.com'
  },

  // 统计和分析
  analytics: {
    enabled: true,
    anonymizeData: true,
    trackingEvents: [
      'word_learned',
      'practice_completed',
      'streak_achieved',
      'level_up'
    ]
  },

  // 导出和备份
  export: {
    formats: ['json', 'csv', 'txt'],
    includeProgress: true,
    includeStatistics: true,
    compression: true
  }
};