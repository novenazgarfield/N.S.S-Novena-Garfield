/**
 * 🔧 N.S.S-Novena-Garfield 全局配置管理
 * 统一管理所有系统的配置参数
 */

const path = require('path');

// 基础路径配置
const BASE_PATH = process.env.NSS_BASE_PATH || '/workspace';
const SYSTEMS_PATH = path.join(BASE_PATH, 'systems');
const API_PATH = path.join(BASE_PATH, 'api');

// 全局配置对象
const globalConfig = {
  // 🌐 服务配置
  services: {
    ai: {
      url: process.env.AI_SERVICE_URL || 'http://localhost:8001',
      timeout: parseInt(process.env.AI_TIMEOUT) || 30000,
      retries: parseInt(process.env.AI_RETRIES) || 3
    },
    chronicle: {
      url: process.env.CHRONICLE_URL || 'http://localhost:3000',
      timeout: parseInt(process.env.CHRONICLE_TIMEOUT) || 30000,
      retries: parseInt(process.env.CHRONICLE_RETRIES) || 3
    },
    rag: {
      url: process.env.RAG_SERVICE_URL || 'http://localhost:8501',
      timeout: parseInt(process.env.RAG_TIMEOUT) || 60000,
      retries: parseInt(process.env.RAG_RETRIES) || 2
    },
    nexus: {
      url: process.env.NEXUS_URL || 'http://localhost:8080',
      timeout: parseInt(process.env.NEXUS_TIMEOUT) || 30000,
      retries: parseInt(process.env.NEXUS_RETRIES) || 3
    },
    changlee: {
      webPort: parseInt(process.env.CHANGLEE_WEB_PORT) || 8082,
      backendPort: parseInt(process.env.CHANGLEE_BACKEND_PORT) || 8083,
      timeout: parseInt(process.env.CHANGLEE_TIMEOUT) || 30000
    }
  },

  // 🔌 端口配置
  ports: {
    ai: parseInt(process.env.AI_PORT) || 8001,
    chronicle: parseInt(process.env.CHRONICLE_PORT) || 3000,
    rag: parseInt(process.env.RAG_PORT) || 8501,
    nexus: parseInt(process.env.NEXUS_PORT) || 8080,
    changlee_web: parseInt(process.env.CHANGLEE_WEB_PORT) || 8082,
    changlee_backend: parseInt(process.env.CHANGLEE_BACKEND_PORT) || 8083,
    bovine: parseInt(process.env.BOVINE_PORT) || 8084,
    genome: parseInt(process.env.GENOME_PORT) || 8085,
    kinetic: parseInt(process.env.KINETIC_PORT) || 8086,
    api_manager: parseInt(process.env.API_MANAGER_PORT) || 8000
  },

  // 🗄️ 数据库配置
  database: {
    sqlite: {
      path: process.env.DB_PATH || path.join(BASE_PATH, 'management/data/nss.db'),
      timeout: parseInt(process.env.DB_TIMEOUT) || 10000
    },
    sessions: {
      path: process.env.SESSIONS_PATH || path.join(SYSTEMS_PATH, 'rag-system/sessions.json'),
      backup: process.env.SESSIONS_BACKUP || true
    }
  },

  // 🔐 安全配置
  security: {
    cors: {
      enabled: process.env.CORS_ENABLED !== 'false',
      origins: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : ['*']
    },
    rateLimit: {
      enabled: process.env.RATE_LIMIT_ENABLED !== 'false',
      windowMs: parseInt(process.env.RATE_LIMIT_WINDOW) || 900000, // 15分钟
      max: parseInt(process.env.RATE_LIMIT_MAX) || 100
    }
  },

  // 📁 路径配置
  paths: {
    base: BASE_PATH,
    systems: SYSTEMS_PATH,
    api: API_PATH,
    management: path.join(BASE_PATH, 'management'),
    logs: process.env.LOGS_PATH || path.join(BASE_PATH, 'management/logs'),
    temp: process.env.TEMP_PATH || path.join(BASE_PATH, 'management/temp'),
    data: process.env.DATA_PATH || path.join(BASE_PATH, 'management/data')
  },

  // 🔧 开发配置
  development: {
    debug: process.env.NODE_ENV === 'development' || process.env.DEBUG === 'true',
    hotReload: process.env.HOT_RELOAD !== 'false',
    verbose: process.env.VERBOSE === 'true'
  },

  // 🐳 Docker配置
  docker: {
    enabled: process.env.DOCKER_ENABLED !== 'false',
    network: process.env.DOCKER_NETWORK || 'nss-network',
    compose: {
      file: process.env.COMPOSE_FILE || 'docker-compose.yml',
      project: process.env.COMPOSE_PROJECT_NAME || 'nss-novena-garfield'
    }
  },

  // ⚡ 性能配置
  performance: {
    responseTimeThreshold: parseInt(process.env.RESPONSE_TIME_THRESHOLD) || 5000,
    memoryLimit: process.env.MEMORY_LIMIT || '512m',
    cpuLimit: process.env.CPU_LIMIT || '1.0'
  }
};

// 配置验证函数
function validateConfig() {
  const errors = [];
  
  // 验证端口范围
  Object.entries(globalConfig.ports).forEach(([service, port]) => {
    if (port < 1024 || port > 65535) {
      errors.push(`Invalid port for ${service}: ${port}`);
    }
  });
  
  // 验证路径存在性
  const fs = require('fs');
  if (!fs.existsSync(globalConfig.paths.base)) {
    errors.push(`Base path does not exist: ${globalConfig.paths.base}`);
  }
  
  return errors;
}

// 获取系统特定配置
function getSystemConfig(systemName) {
  const baseConfig = {
    ...globalConfig,
    system: {
      name: systemName,
      port: globalConfig.ports[systemName] || 8000,
      url: globalConfig.services[systemName]?.url || `http://localhost:${globalConfig.ports[systemName] || 8000}`,
      path: path.join(globalConfig.paths.systems, systemName)
    }
  };
  
  return baseConfig;
}

// 导出配置
module.exports = {
  globalConfig,
  validateConfig,
  getSystemConfig,
  
  // 便捷访问器
  get services() { return globalConfig.services; },
  get ports() { return globalConfig.ports; },
  get paths() { return globalConfig.paths; },
  get database() { return globalConfig.database; },
  get security() { return globalConfig.security; },
  get development() { return globalConfig.development; },
  get docker() { return globalConfig.docker; },
  get performance() { return globalConfig.performance; }
};