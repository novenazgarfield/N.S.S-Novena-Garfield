/**
 * 智能协调器 - ReAct代理与Chronicle系统的桥梁
 * Intelligence Coordinator - Bridge between ReAct Agent and Chronicle System
 * 
 * 职责：
 * 1. 监听Chronicle系统的复杂故障事件
 * 2. 激活ReAct代理进行智能分析
 * 3. 协调各个子系统的协作
 * 4. 管理用户交互和确认流程
 */

const ReActAgent = require('./react-agent');
const { createModuleLogger } = require('../shared/logger');
const logger = createModuleLogger('intelligence-coordinator');
const { EventEmitter } = require('events');

class IntelligenceCoordinator extends EventEmitter {
    constructor(chronicleSystem) {
        super();
        this.chronicleSystem = chronicleSystem;
        this.reactAgent = new ReActAgent({
            maxReasoningSteps: 7,
            confidenceThreshold: 0.7,
            riskAssessmentEnabled: true,
            userConfirmationRequired: true
        });
        
        this.activeInvestigations = new Map();
        this.systemIntegrations = {
            collector: null,
            analyst: null,
            repairService: null,
            sandbox: null,
            permissionManager: null
        };
        
        this.setupEventListeners();
        this.setupSystemIntegrations();
        
        logger.info('🎯 Intelligence Coordinator initialized');
    }

    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 监听ReAct代理的用户确认请求
        this.reactAgent.on('user_confirmation_required', (data) => {
            this.handleUserConfirmationRequest(data);
        });

        // 监听Chronicle系统的复杂故障事件
        this.on('complex_failure_detected', (failureData) => {
            this.handleComplexFailure(failureData);
        });

        // 监听系统修复请求
        this.on('repair_request', (repairData) => {
            this.handleRepairRequest(repairData);
        });
    }

    /**
     * 设置系统集成
     */
    setupSystemIntegrations() {
        try {
            // 集成全域数据采集器
            const GlobalCollector = require('../collector/global-collector');
            this.systemIntegrations.collector = new GlobalCollector();
            
            // 集成数据分析引擎
            const PatternRecognizer = require('../analyst/pattern-recognizer');
            this.systemIntegrations.analyst = new PatternRecognizer();
            
            // 集成中央修复服务
            const CentralRepairService = require('../repair/central-repair-service');
            this.systemIntegrations.repairService = new CentralRepairService();
            
            // 集成Docker沙箱
            const DockerSandbox = require('../sandbox/docker-sandbox');
            this.systemIntegrations.sandbox = new DockerSandbox();
            
            // 集成权限管理器
            const PermissionManager = require('../auth/permission-manager');
            this.systemIntegrations.permissionManager = new PermissionManager();
            
            logger.info('✅ System integrations established');
        } catch (error) {
            logger.error(`❌ Failed to setup system integrations: ${error.message}`);
        }
    }

    /**
     * 处理复杂故障 - 激活ReAct代理
     */
    async handleComplexFailure(failureData) {
        const investigationId = `investigation_${Date.now()}`;
        
        try {
            logger.info(`🚨 Complex failure detected: ${failureData.type}`);
            logger.info(`🧠 Activating ReAct Agent for investigation: ${investigationId}`);
            
            // 记录调查开始
            this.activeInvestigations.set(investigationId, {
                id: investigationId,
                startTime: new Date(),
                failureData,
                status: 'investigating',
                reactAgent: this.reactAgent
            });

            // 收集额外的系统上下文
            const systemContext = await this.gatherSystemContext(failureData);
            
            // 激活ReAct代理
            const result = await this.reactAgent.activate(
                failureData.description || failureData.type,
                {
                    ...failureData,
                    systemContext,
                    investigationId
                }
            );

            // 更新调查状态
            const investigation = this.activeInvestigations.get(investigationId);
            investigation.status = result.success ? 'completed' : 'failed';
            investigation.result = result;
            investigation.endTime = new Date();

            // 发出结果事件
            this.emit('investigation_completed', {
                investigationId,
                result,
                investigation
            });

            logger.info(`✅ Investigation completed: ${investigationId}`);
            return result;

        } catch (error) {
            logger.error(`❌ Investigation failed: ${investigationId} - ${error.message}`);
            
            // 更新失败状态
            if (this.activeInvestigations.has(investigationId)) {
                const investigation = this.activeInvestigations.get(investigationId);
                investigation.status = 'error';
                investigation.error = error.message;
                investigation.endTime = new Date();
            }
            
            throw error;
        }
    }

    /**
     * 收集系统上下文信息
     */
    async gatherSystemContext(failureData) {
        const context = {
            timestamp: new Date().toISOString(),
            systemMetrics: {},
            recentEvents: [],
            systemHealth: {}
        };

        try {
            // 从数据采集器获取最新指标
            if (this.systemIntegrations.collector) {
                context.systemMetrics = await this.systemIntegrations.collector.getCurrentMetrics();
            }

            // 从分析引擎获取相关模式
            if (this.systemIntegrations.analyst) {
                context.recentPatterns = await this.systemIntegrations.analyst.getRecentPatterns();
            }

            // 获取系统健康状态
            context.systemHealth = await this.getSystemHealthSnapshot();

        } catch (error) {
            logger.warn(`⚠️ Failed to gather complete system context: ${error.message}`);
        }

        return context;
    }

    /**
     * 获取系统健康快照
     */
    async getSystemHealthSnapshot() {
        return {
            cpu: await this.getCPUUsage(),
            memory: await this.getMemoryUsage(),
            disk: await this.getDiskUsage(),
            network: await this.getNetworkStatus(),
            services: await this.getServiceStatus()
        };
    }

    /**
     * 处理用户确认请求
     */
    handleUserConfirmationRequest(data) {
        const { actionPlan, message } = data;
        
        logger.info('🔔 User confirmation required for high-risk operation');
        
        // 发出用户界面事件
        this.emit('user_confirmation_needed', {
            actionPlan,
            message,
            timestamp: new Date().toISOString(),
            requiresResponse: true
        });

        // 同时记录到Chronicle日志
        if (this.chronicleSystem && this.chronicleSystem.logEvent) {
            this.chronicleSystem.logEvent({
                type: 'user_confirmation_request',
                severity: 'high',
                data: {
                    actionPlan: actionPlan.title,
                    riskLevel: actionPlan.problemAnalysis.riskLevel,
                    estimatedTime: actionPlan.recommendedSolution.estimatedTime
                }
            });
        }
    }

    /**
     * 处理修复请求
     */
    async handleRepairRequest(repairData) {
        try {
            logger.info(`🔧 Processing repair request: ${repairData.type}`);
            
            // 评估是否需要ReAct代理介入
            const complexityScore = this.assessRepairComplexity(repairData);
            
            if (complexityScore >= 0.7) {
                // 复杂修复，激活ReAct代理
                logger.info('🧠 Complex repair detected, activating ReAct Agent');
                return await this.handleComplexFailure({
                    type: 'repair_request',
                    description: repairData.description,
                    ...repairData
                });
            } else {
                // 简单修复，直接使用修复服务
                logger.info('🔧 Simple repair, using direct repair service');
                return await this.systemIntegrations.repairService.executeRepair(repairData);
            }
            
        } catch (error) {
            logger.error(`❌ Repair request failed: ${error.message}`);
            throw error;
        }
    }

    /**
     * 评估修复复杂度
     */
    assessRepairComplexity(repairData) {
        let complexity = 0;
        
        // 基于关键词评估
        const complexKeywords = ['system', 'critical', 'database', 'network', 'security', 'kernel'];
        const description = (repairData.description || '').toLowerCase();
        
        complexKeywords.forEach(keyword => {
            if (description.includes(keyword)) {
                complexity += 0.2;
            }
        });
        
        // 基于影响范围评估
        if (repairData.affectedServices && repairData.affectedServices.length > 3) {
            complexity += 0.3;
        }
        
        // 基于风险级别评估
        if (repairData.riskLevel === 'high') {
            complexity += 0.4;
        } else if (repairData.riskLevel === 'medium') {
            complexity += 0.2;
        }
        
        return Math.min(complexity, 1.0);
    }

    /**
     * 用户批准操作
     */
    approveOperation(investigationId, approved, reason = '') {
        const investigation = this.activeInvestigations.get(investigationId);
        
        if (investigation && investigation.reactAgent) {
            investigation.reactAgent.approveAction(approved, reason);
            
            logger.info(`👤 User ${approved ? 'approved' : 'denied'} operation for investigation: ${investigationId}`);
            
            if (reason) {
                logger.info(`💬 User reason: ${reason}`);
            }
        } else {
            logger.warn(`⚠️ No active investigation found: ${investigationId}`);
        }
    }

    /**
     * 获取活动调查列表
     */
    getActiveInvestigations() {
        return Array.from(this.activeInvestigations.values()).map(inv => ({
            id: inv.id,
            status: inv.status,
            startTime: inv.startTime,
            failureType: inv.failureData.type,
            reactAgentStatus: inv.reactAgent.getStatus()
        }));
    }

    /**
     * 获取ReAct代理状态
     */
    getReActAgentStatus() {
        return this.reactAgent.getStatus();
    }

    /**
     * 强制休眠ReAct代理
     */
    sleepReActAgent() {
        this.reactAgent.sleep();
        logger.info('🧠 ReAct Agent forced to sleep mode');
    }

    /**
     * 系统健康检查辅助方法
     */
    async getCPUUsage() {
        // 简化实现
        return { usage: '15%', cores: 4 };
    }

    async getMemoryUsage() {
        // 简化实现
        return { used: '2.1GB', total: '8GB', percentage: '26%' };
    }

    async getDiskUsage() {
        // 简化实现
        return { used: '45GB', total: '100GB', percentage: '45%' };
    }

    async getNetworkStatus() {
        // 简化实现
        return { status: 'connected', latency: '12ms' };
    }

    async getServiceStatus() {
        // 简化实现
        return { 
            running: ['chronicle', 'nginx', 'database'],
            stopped: [],
            failed: []
        };
    }

    /**
     * 清理完成的调查
     */
    cleanupCompletedInvestigations(maxAge = 24 * 60 * 60 * 1000) { // 24小时
        const now = new Date();
        const toRemove = [];
        
        for (const [id, investigation] of this.activeInvestigations) {
            if (investigation.endTime && (now - investigation.endTime) > maxAge) {
                toRemove.push(id);
            }
        }
        
        toRemove.forEach(id => {
            this.activeInvestigations.delete(id);
            logger.info(`🧹 Cleaned up old investigation: ${id}`);
        });
        
        return toRemove.length;
    }

    /**
     * 关闭协调器
     */
    async shutdown() {
        logger.info('🔄 Shutting down Intelligence Coordinator...');
        
        // 休眠ReAct代理
        this.reactAgent.sleep();
        
        // 清理活动调查
        this.activeInvestigations.clear();
        
        // 移除所有监听器
        this.removeAllListeners();
        
        logger.info('✅ Intelligence Coordinator shutdown complete');
    }
}

module.exports = IntelligenceCoordinator;