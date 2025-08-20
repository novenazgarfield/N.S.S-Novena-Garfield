/**
 * Changlee AI服务配置
 * 支持本地AI和云端API的混合配置
 */

const path = require('path');

// AI服务配置
const aiConfig = {
    // 混合AI服务配置
    hybrid: {
        enabled: process.env.HYBRID_AI_ENABLED !== 'false',
        preferredService: process.env.PREFERRED_AI_SERVICE || 'auto', // auto, local, gemini, deepseek
        fallbackEnabled: process.env.AI_FALLBACK_ENABLED !== 'false',
        timeout: parseInt(process.env.AI_TIMEOUT) || 30000, // 30秒超时
        retryAttempts: parseInt(process.env.AI_RETRY_ATTEMPTS) || 2
    },

    // 本地AI配置
    local: {
        enabled: process.env.LOCAL_AI_ENABLED !== 'false',
        serverUrl: process.env.LOCAL_AI_URL || 'http://localhost:8001',
        modelName: process.env.LOCAL_MODEL_NAME || 'google/gemma-2-2b',
        maxMemoryGB: parseFloat(process.env.MAX_MEMORY_GB) || 4.0,
        quantization: process.env.USE_QUANTIZATION === 'true',
        device: process.env.AI_DEVICE || 'auto' // auto, cpu, cuda
    },

    // Gemini API配置
    gemini: {
        enabled: !!process.env.GEMINI_API_KEY,
        apiKey: process.env.GEMINI_API_KEY,
        model: process.env.GEMINI_MODEL || 'gemini-1.5-flash',
        baseUrl: process.env.GEMINI_BASE_URL || 'https://generativelanguage.googleapis.com',
        timeout: parseInt(process.env.GEMINI_TIMEOUT) || 30000,
        maxTokens: parseInt(process.env.GEMINI_MAX_TOKENS) || 256,
        temperature: parseFloat(process.env.GEMINI_TEMPERATURE) || 0.7
    },

    // DeepSeek API配置
    deepseek: {
        enabled: !!process.env.DEEPSEEK_API_KEY,
        apiKey: process.env.DEEPSEEK_API_KEY,
        model: process.env.DEEPSEEK_MODEL || 'deepseek-chat',
        baseUrl: process.env.DEEPSEEK_BASE_URL || 'https://api.deepseek.com/v1',
        timeout: parseInt(process.env.DEEPSEEK_TIMEOUT) || 30000,
        maxTokens: parseInt(process.env.DEEPSEEK_MAX_TOKENS) || 256,
        temperature: parseFloat(process.env.DEEPSEEK_TEMPERATURE) || 0.7
    },

    // 其他AI服务配置（可扩展）
    openai: {
        enabled: !!process.env.OPENAI_API_KEY,
        apiKey: process.env.OPENAI_API_KEY,
        model: process.env.OPENAI_MODEL || 'gpt-3.5-turbo',
        baseUrl: process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1',
        timeout: parseInt(process.env.OPENAI_TIMEOUT) || 30000
    },

    // 长离人格配置
    personality: {
        name: '长离',
        description: '温暖、智慧的AI学习伙伴',
        traits: [
            '温柔耐心，善于鼓励',
            '富有创意，能用有趣的方式解释知识',
            '关心用户的学习进度和情感状态',
            '说话风格亲切自然，偶尔使用可爱的表情符号'
        ],
        contexts: {
            daily_greeting: '日常问候',
            word_learning: '单词学习',
            spelling_practice: '拼写练习',
            encouragement: '学习鼓励',
            explanation: '概念解释',
            study_planning: '学习规划',
            progress_review: '进度回顾'
        }
    },

    // 性能优化配置
    performance: {
        cacheEnabled: process.env.AI_CACHE_ENABLED !== 'false',
        cacheSize: parseInt(process.env.AI_CACHE_SIZE) || 100,
        cacheTTL: parseInt(process.env.AI_CACHE_TTL) || 3600, // 1小时
        memoryOptimization: process.env.MEMORY_OPTIMIZATION === 'true',
        batchProcessing: process.env.BATCH_PROCESSING === 'true',
        maxConcurrentRequests: parseInt(process.env.MAX_CONCURRENT_REQUESTS) || 5
    },

    // 安全配置
    security: {
        rateLimiting: {
            enabled: process.env.RATE_LIMITING_ENABLED !== 'false',
            maxRequests: parseInt(process.env.MAX_REQUESTS_PER_MINUTE) || 60,
            windowMs: parseInt(process.env.RATE_LIMIT_WINDOW) || 60000 // 1分钟
        },
        inputValidation: {
            maxPromptLength: parseInt(process.env.MAX_PROMPT_LENGTH) || 1000,
            allowedContexts: Object.keys(aiConfig?.personality?.contexts || {}),
            sanitizeInput: process.env.SANITIZE_INPUT !== 'false'
        },
        privacy: {
            logUserInputs: process.env.LOG_USER_INPUTS === 'true',
            dataRetention: parseInt(process.env.DATA_RETENTION_DAYS) || 30,
            anonymizeData: process.env.ANONYMIZE_DATA !== 'false'
        }
    },

    // 监控和日志配置
    monitoring: {
        enabled: process.env.AI_MONITORING_ENABLED !== 'false',
        metricsCollection: process.env.COLLECT_METRICS !== 'false',
        healthCheckInterval: parseInt(process.env.HEALTH_CHECK_INTERVAL) || 60000, // 1分钟
        alerting: {
            enabled: process.env.ALERTING_ENABLED === 'true',
            errorThreshold: parseInt(process.env.ERROR_THRESHOLD) || 10,
            responseTimeThreshold: parseInt(process.env.RESPONSE_TIME_THRESHOLD) || 5000
        }
    },

    // 开发和调试配置
    development: {
        debug: process.env.NODE_ENV === 'development',
        verbose: process.env.AI_VERBOSE === 'true',
        mockResponses: process.env.MOCK_AI_RESPONSES === 'true',
        testMode: process.env.AI_TEST_MODE === 'true'
    }
};

/**
 * 获取当前可用的AI服务列表
 */
function getAvailableServices() {
    const services = [];
    
    if (aiConfig.local.enabled) {
        services.push({
            type: 'local',
            name: '本地AI (Gemma 2)',
            description: '完全本地运行，保护隐私',
            model: aiConfig.local.modelName,
            priority: 2
        });
    }
    
    if (aiConfig.gemini.enabled) {
        services.push({
            type: 'gemini',
            name: 'Google Gemini',
            description: '强大的多模态AI',
            model: aiConfig.gemini.model,
            priority: 1
        });
    }
    
    if (aiConfig.deepseek.enabled) {
        services.push({
            type: 'deepseek',
            name: 'DeepSeek',
            description: '高性能语言模型',
            model: aiConfig.deepseek.model,
            priority: 3
        });
    }
    
    if (aiConfig.openai.enabled) {
        services.push({
            type: 'openai',
            name: 'OpenAI GPT',
            description: '经典的对话AI',
            model: aiConfig.openai.model,
            priority: 4
        });
    }
    
    return services.sort((a, b) => a.priority - b.priority);
}

/**
 * 获取首选AI服务
 */
function getPreferredService() {
    const preferred = aiConfig.hybrid.preferredService.toLowerCase();
    const available = getAvailableServices();
    
    if (preferred === 'auto') {
        return available[0]?.type || null;
    }
    
    return available.find(s => s.type === preferred)?.type || available[0]?.type || null;
}

/**
 * 验证AI配置
 */
function validateConfig() {
    const errors = [];
    const warnings = [];
    
    // 检查是否至少有一个AI服务可用
    const availableServices = getAvailableServices();
    if (availableServices.length === 0) {
        errors.push('没有可用的AI服务，请配置至少一个AI服务');
    }
    
    // 检查本地AI配置
    if (aiConfig.local.enabled) {
        if (!aiConfig.local.serverUrl) {
            warnings.push('本地AI服务URL未配置');
        }
        if (aiConfig.local.maxMemoryGB < 2) {
            warnings.push('本地AI内存配置可能不足，建议至少4GB');
        }
    }
    
    // 检查API密钥
    if (aiConfig.gemini.enabled && !aiConfig.gemini.apiKey) {
        errors.push('Gemini API密钥未配置');
    }
    
    if (aiConfig.deepseek.enabled && !aiConfig.deepseek.apiKey) {
        errors.push('DeepSeek API密钥未配置');
    }
    
    // 检查性能配置
    if (aiConfig.performance.maxConcurrentRequests > 10) {
        warnings.push('并发请求数过高，可能影响性能');
    }
    
    return { errors, warnings };
}

/**
 * 获取环境变量配置示例
 */
function getEnvExample() {
    return `
# Changlee AI服务配置示例

# 混合AI配置
HYBRID_AI_ENABLED=true
PREFERRED_AI_SERVICE=auto  # auto, local, gemini, deepseek
AI_FALLBACK_ENABLED=true
AI_TIMEOUT=30000

# 本地AI配置
LOCAL_AI_ENABLED=true
LOCAL_AI_URL=http://localhost:8001
LOCAL_MODEL_NAME=google/gemma-2-2b
MAX_MEMORY_GB=4.0
USE_QUANTIZATION=false
AI_DEVICE=auto

# Gemini API配置
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TIMEOUT=30000
GEMINI_MAX_TOKENS=256
GEMINI_TEMPERATURE=0.7

# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TIMEOUT=30000
DEEPSEEK_MAX_TOKENS=256
DEEPSEEK_TEMPERATURE=0.7

# 性能优化
AI_CACHE_ENABLED=true
AI_CACHE_SIZE=100
MEMORY_OPTIMIZATION=true
MAX_CONCURRENT_REQUESTS=5

# 安全配置
RATE_LIMITING_ENABLED=true
MAX_REQUESTS_PER_MINUTE=60
MAX_PROMPT_LENGTH=1000
SANITIZE_INPUT=true

# 监控配置
AI_MONITORING_ENABLED=true
COLLECT_METRICS=true
HEALTH_CHECK_INTERVAL=60000

# 开发配置
NODE_ENV=development
AI_VERBOSE=false
MOCK_AI_RESPONSES=false
AI_TEST_MODE=false
`;
}

module.exports = {
    aiConfig,
    getAvailableServices,
    getPreferredService,
    validateConfig,
    getEnvExample
};