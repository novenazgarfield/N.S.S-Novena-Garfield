/**
 * 🌐 动态配置加载器
 * 自动发现和连接后端服务
 */

class DynamicConfig {
    constructor() {
        this.config = null;
        this.apiEndpoints = {};
        this.retryCount = 0;
        this.maxRetries = 5;
        
        // 默认配置
        this.defaultConfig = {
            api_endpoints: {
                rag_api: 'http://localhost:5000',
                health_check: 'http://localhost:5000/api/health',
                chat: 'http://localhost:5000/api/chat',
                upload: 'http://localhost:5000/api/upload'
            }
        };
    }
    
    /**
     * 加载动态配置
     */
    async loadConfig() {
        try {
            // 尝试从本地配置文件加载
            const response = await fetch('/api_config.json');
            if (response.ok) {
                this.config = await response.json();
                this.apiEndpoints = this.config.api_endpoints;
                console.log('✅ 动态配置加载成功:', this.config);
                return this.config;
            }
        } catch (error) {
            console.warn('⚠️ 本地配置文件加载失败:', error);
        }
        
        // 尝试从服务发现系统获取配置
        try {
            const discoveryResponse = await fetch('http://localhost:8000/api/services/config');
            if (discoveryResponse.ok) {
                const discoveryConfig = await discoveryResponse.json();
                this.updateConfigFromDiscovery(discoveryConfig);
                console.log('✅ 服务发现配置加载成功:', discoveryConfig);
                return this.config;
            }
        } catch (error) {
            console.warn('⚠️ 服务发现配置加载失败:', error);
        }
        
        // 使用默认配置
        console.log('📝 使用默认配置');
        this.config = this.defaultConfig;
        this.apiEndpoints = this.config.api_endpoints;
        return this.config;
    }
    
    /**
     * 从服务发现更新配置
     */
    updateConfigFromDiscovery(discoveryConfig) {
        const services = discoveryConfig.services || {};
        
        this.config = {
            api_endpoints: {},
            updated_at: discoveryConfig.updated_at
        };
        
        // 映射服务到API端点
        if (services.rag_api) {
            const ragUrl = services.rag_api.local_url;
            this.config.api_endpoints = {
                rag_api: ragUrl,
                health_check: `${ragUrl}/api/health`,
                chat: `${ragUrl}/api/chat`,
                upload: `${ragUrl}/api/upload`
            };
        }
        
        this.apiEndpoints = this.config.api_endpoints;
    }
    
    /**
     * 获取API端点
     */
    getApiEndpoint(name) {
        return this.apiEndpoints[name] || this.defaultConfig.api_endpoints[name];
    }
    
    /**
     * 检查服务健康状态
     */
    async checkServiceHealth(serviceName = 'rag_api') {
        const healthUrl = this.getApiEndpoint('health_check');
        
        try {
            const response = await fetch(healthUrl, {
                method: 'GET',
                timeout: 5000
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ ${serviceName} 服务健康检查通过:`, data);
                return true;
            }
        } catch (error) {
            console.warn(`⚠️ ${serviceName} 服务健康检查失败:`, error);
        }
        
        return false;
    }
    
    /**
     * 自动重连机制
     */
    async autoReconnect() {
        if (this.retryCount >= this.maxRetries) {
            console.error('❌ 达到最大重试次数，停止重连');
            return false;
        }
        
        this.retryCount++;
        console.log(`🔄 尝试重连 (${this.retryCount}/${this.maxRetries})...`);
        
        // 重新加载配置
        await this.loadConfig();
        
        // 检查服务健康状态
        const isHealthy = await this.checkServiceHealth();
        
        if (isHealthy) {
            this.retryCount = 0; // 重置重试计数
            console.log('✅ 重连成功');
            return true;
        }
        
        // 等待后重试
        await new Promise(resolve => setTimeout(resolve, 2000 * this.retryCount));
        return this.autoReconnect();
    }
    
    /**
     * 发送API请求（带自动重连）
     */
    async apiRequest(endpoint, options = {}) {
        const url = this.getApiEndpoint(endpoint);
        
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.warn(`⚠️ API请求失败 (${endpoint}):`, error);
            
            // 尝试自动重连
            const reconnected = await this.autoReconnect();
            if (reconnected) {
                // 重连成功，重试请求
                const retryUrl = this.getApiEndpoint(endpoint);
                const retryResponse = await fetch(retryUrl, options);
                if (retryResponse.ok) {
                    return await retryResponse.json();
                }
            }
            
            throw error;
        }
    }
    
    /**
     * 获取当前配置状态
     */
    getStatus() {
        return {
            config: this.config,
            apiEndpoints: this.apiEndpoints,
            retryCount: this.retryCount,
            isConfigured: !!this.config
        };
    }
}

// 创建全局实例
window.dynamicConfig = new DynamicConfig();

// 自动初始化
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 初始化动态配置系统...');
    await window.dynamicConfig.loadConfig();
    
    // 检查服务健康状态
    const isHealthy = await window.dynamicConfig.checkServiceHealth();
    if (!isHealthy) {
        console.warn('⚠️ 后端服务不可用，将在需要时自动重连');
    }
    
    // 触发配置加载完成事件
    window.dispatchEvent(new CustomEvent('configLoaded', {
        detail: window.dynamicConfig.getStatus()
    }));
});

// 导出配置类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DynamicConfig;
}