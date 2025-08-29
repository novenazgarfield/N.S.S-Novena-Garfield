/**
 * Chronicle-ReAct集成模块
 * Chronicle-ReAct Integration Module
 * 
 * 第三章："智慧"的"注入" - 完整集成实现
 * Chapter 3: "The Integration of Wisdom" - Complete Integration Implementation
 * 
 * 职责：
 * 1. 将ReAct代理完全集成到Chronicle系统中
 * 2. 作为Chronicle系统的"智慧大脑"
 * 3. 处理所有复杂系统级故障
 * 4. 管理用户交互和确认流程
 */

const IntelligenceCoordinator = require('./intelligence-coordinator');
const ConfirmationInterface = require('../ui/confirmation-interface');
const { createModuleLogger } = require('../shared/logger');
const logger = createModuleLogger('chronicle-integration');
const { EventEmitter } = require('events');

class ChronicleReActIntegration extends EventEmitter {
    constructor(chronicleSystem) {
        super();
        this.chronicleSystem = chronicleSystem;
        this.isInitialized = false;
        this.isActive = false;
        
        // 核心组件
        this.intelligenceCoordinator = null;
        this.confirmationInterface = null;
        
        // 集成状态
        this.integrationStatus = {
            coordinator: false,
            confirmationUI: false,
            apiRoutes: false,
            eventListeners: false
        };
        
        // 统计信息
        this.stats = {
            totalInvestigations: 0,
            successfulRepairs: 0,
            userApprovals: 0,
            userDenials: 0,
            startTime: new Date()
        };
        
        logger.info('🧠 Chronicle-ReAct Integration module created');
    }

    /**
     * 初始化集成系统
     */
    async initialize() {
        try {
            logger.info('🚀 Initializing Chronicle-ReAct Integration...');
            
            // 1. 初始化确认界面
            await this.initializeConfirmationInterface();
            
            // 2. 初始化智能协调器
            await this.initializeIntelligenceCoordinator();
            
            // 3. 设置事件监听器
            await this.setupEventListeners();
            
            // 4. 集成API路由
            await this.integrateAPIRoutes();
            
            // 5. 启动监控
            await this.startMonitoring();
            
            this.isInitialized = true;
            this.isActive = true;
            
            logger.info('✅ Chronicle-ReAct Integration initialized successfully');
            this.logIntegrationStatus();
            
            return true;
            
        } catch (error) {
            logger.error(`❌ Failed to initialize Chronicle-ReAct Integration: ${error.message}`);
            throw error;
        }
    }

    /**
     * 初始化确认界面
     */
    async initializeConfirmationInterface() {
        try {
            this.confirmationInterface = new ConfirmationInterface({
                autoTimeout: 300000, // 5分钟
                requireReason: true,
                logDecisions: true
            });
            
            // 监听确认界面事件
            this.confirmationInterface.on('confirmation_displayed', (data) => {
                logger.info(`🖥️ Confirmation interface displayed: ${data.confirmationId}`);
                this.emit('confirmation_displayed', data);
            });
            
            this.confirmationInterface.on('user_decision', (data) => {
                this.handleUserDecision(data);
            });
            
            this.integrationStatus.confirmationUI = true;
            logger.info('✅ Confirmation Interface initialized');
            
        } catch (error) {
            logger.error(`❌ Failed to initialize Confirmation Interface: ${error.message}`);
            throw error;
        }
    }

    /**
     * 初始化智能协调器
     */
    async initializeIntelligenceCoordinator() {
        try {
            this.intelligenceCoordinator = new IntelligenceCoordinator(this.chronicleSystem);
            
            // 监听智能协调器事件
            this.intelligenceCoordinator.on('user_confirmation_needed', (data) => {
                this.handleConfirmationRequest(data);
            });
            
            this.intelligenceCoordinator.on('investigation_completed', (data) => {
                this.handleInvestigationCompleted(data);
            });
            
            this.integrationStatus.coordinator = true;
            logger.info('✅ Intelligence Coordinator initialized');
            
        } catch (error) {
            logger.error(`❌ Failed to initialize Intelligence Coordinator: ${error.message}`);
            throw error;
        }
    }

    /**
     * 设置事件监听器
     */
    async setupEventListeners() {
        try {
            // 监听Chronicle系统的故障事件
            if (this.chronicleSystem && this.chronicleSystem.on) {
                this.chronicleSystem.on('system_failure', (failureData) => {
                    this.handleSystemFailure(failureData);
                });
                
                this.chronicleSystem.on('complex_issue', (issueData) => {
                    this.handleComplexIssue(issueData);
                });
                
                this.chronicleSystem.on('repair_needed', (repairData) => {
                    this.handleRepairNeeded(repairData);
                });
            }
            
            // 监听全域采集器事件
            this.on('critical_event_detected', (eventData) => {
                this.evaluateEventComplexity(eventData);
            });
            
            this.integrationStatus.eventListeners = true;
            logger.info('✅ Event listeners setup complete');
            
        } catch (error) {
            logger.error(`❌ Failed to setup event listeners: ${error.message}`);
            throw error;
        }
    }

    /**
     * 集成API路由
     */
    async integrateAPIRoutes() {
        try {
            // 这里应该与Chronicle的API服务器集成
            // 由于我们需要访问Express应用实例，这部分将在server.js中完成
            
            this.integrationStatus.apiRoutes = true;
            logger.info('✅ API routes integration prepared');
            
        } catch (error) {
            logger.error(`❌ Failed to integrate API routes: ${error.message}`);
            throw error;
        }
    }

    /**
     * 启动监控
     */
    async startMonitoring() {
        try {
            // 定期清理过期确认
            setInterval(() => {
                if (this.confirmationInterface) {
                    this.confirmationInterface.cleanup();
                }
                
                if (this.intelligenceCoordinator) {
                    this.intelligenceCoordinator.cleanupCompletedInvestigations();
                }
            }, 60000); // 每分钟清理一次
            
            // 定期记录统计信息
            setInterval(() => {
                this.logStatistics();
            }, 300000); // 每5分钟记录一次统计
            
            logger.info('✅ Monitoring started');
            
        } catch (error) {
            logger.error(`❌ Failed to start monitoring: ${error.message}`);
            throw error;
        }
    }

    /**
     * 处理系统故障
     */
    async handleSystemFailure(failureData) {
        try {
            logger.info(`🚨 System failure detected: ${failureData.type}`);
            
            // 评估故障复杂度
            const complexity = this.assessFailureComplexity(failureData);
            
            if (complexity >= 0.7) {
                logger.info('🧠 High complexity failure - Activating ReAct Agent');
                
                // 激活智能协调器处理复杂故障
                await this.intelligenceCoordinator.handleComplexFailure({
                    ...failureData,
                    detectedBy: 'chronicle_system',
                    complexity: complexity
                });
                
                this.stats.totalInvestigations++;
            } else {
                logger.info('🔧 Low complexity failure - Using standard repair');
                
                // 使用标准修复流程
                this.emit('standard_repair_needed', failureData);
            }
            
        } catch (error) {
            logger.error(`❌ Failed to handle system failure: ${error.message}`);
        }
    }

    /**
     * 处理复杂问题
     */
    async handleComplexIssue(issueData) {
        try {
            logger.info(`🔍 Complex issue detected: ${issueData.description}`);
            
            // 直接激活ReAct代理
            await this.intelligenceCoordinator.handleComplexFailure({
                type: 'complex_issue',
                description: issueData.description,
                context: issueData,
                detectedBy: 'chronicle_analysis'
            });
            
            this.stats.totalInvestigations++;
            
        } catch (error) {
            logger.error(`❌ Failed to handle complex issue: ${error.message}`);
        }
    }

    /**
     * 处理修复需求
     */
    async handleRepairNeeded(repairData) {
        try {
            logger.info(`🔧 Repair needed: ${repairData.type}`);
            
            // 通过智能协调器处理修复请求
            await this.intelligenceCoordinator.handleRepairRequest(repairData);
            
        } catch (error) {
            logger.error(`❌ Failed to handle repair request: ${error.message}`);
        }
    }

    /**
     * 处理确认请求
     */
    async handleConfirmationRequest(data) {
        try {
            logger.info(`🔔 User confirmation required for: ${data.actionPlan.title}`);
            
            // 显示确认界面
            const confirmation = await this.confirmationInterface.showConfirmationRequest(
                data.actionPlan,
                data.investigationId || 'unknown'
            );
            
            // 发出确认显示事件
            this.emit('confirmation_required', {
                ...confirmation,
                actionPlan: data.actionPlan,
                message: data.message
            });
            
        } catch (error) {
            logger.error(`❌ Failed to handle confirmation request: ${error.message}`);
        }
    }

    /**
     * 处理用户决策
     */
    handleUserDecision(data) {
        try {
            const { approved, reason, investigationId } = data;
            
            logger.info(`👤 User decision: ${approved ? 'APPROVED' : 'DENIED'} - ${investigationId}`);
            
            if (approved) {
                this.stats.userApprovals++;
            } else {
                this.stats.userDenials++;
            }
            
            // 通知智能协调器
            if (this.intelligenceCoordinator && investigationId) {
                this.intelligenceCoordinator.approveOperation(investigationId, approved, reason);
            }
            
            // 发出决策事件
            this.emit('user_decision_processed', data);
            
        } catch (error) {
            logger.error(`❌ Failed to handle user decision: ${error.message}`);
        }
    }

    /**
     * 处理调查完成
     */
    handleInvestigationCompleted(data) {
        try {
            const { investigationId, result } = data;
            
            logger.info(`🎯 Investigation completed: ${investigationId} - ${result.success ? 'SUCCESS' : 'FAILED'}`);
            
            if (result.success) {
                this.stats.successfulRepairs++;
            }
            
            // 发出调查完成事件
            this.emit('investigation_completed', data);
            
        } catch (error) {
            logger.error(`❌ Failed to handle investigation completion: ${error.message}`);
        }
    }

    /**
     * 评估事件复杂度
     */
    evaluateEventComplexity(eventData) {
        const complexity = this.assessFailureComplexity(eventData);
        
        if (complexity >= 0.8) {
            logger.info(`🚨 Critical complexity event detected: ${eventData.type}`);
            
            // 立即激活ReAct代理
            this.handleSystemFailure({
                ...eventData,
                priority: 'critical',
                autoActivateReAct: true
            });
        }
    }

    /**
     * 评估故障复杂度
     */
    assessFailureComplexity(failureData) {
        let complexity = 0;
        
        // 基于关键词评估
        const criticalKeywords = ['system', 'kernel', 'database', 'network', 'security', 'memory', 'disk'];
        const description = (failureData.description || failureData.type || '').toLowerCase();
        
        criticalKeywords.forEach(keyword => {
            if (description.includes(keyword)) {
                complexity += 0.15;
            }
        });
        
        // 基于影响范围评估
        if (failureData.affectedServices && failureData.affectedServices.length > 2) {
            complexity += 0.3;
        }
        
        // 基于严重程度评估
        if (failureData.severity === 'critical') {
            complexity += 0.4;
        } else if (failureData.severity === 'high') {
            complexity += 0.2;
        }
        
        // 基于错误频率评估
        if (failureData.frequency && failureData.frequency > 5) {
            complexity += 0.2;
        }
        
        return Math.min(complexity, 1.0);
    }

    /**
     * 获取集成状态
     */
    getIntegrationStatus() {
        return {
            isInitialized: this.isInitialized,
            isActive: this.isActive,
            components: this.integrationStatus,
            stats: {
                ...this.stats,
                uptime: new Date() - this.stats.startTime,
                reactAgentStatus: this.intelligenceCoordinator ? 
                    this.intelligenceCoordinator.getReActAgentStatus() : null,
                pendingConfirmations: this.confirmationInterface ? 
                    this.confirmationInterface.getPendingConfirmations().length : 0
            }
        };
    }

    /**
     * 获取依赖实例（用于API路由注入）
     */
    getDependencies() {
        return {
            confirmationInterface: this.confirmationInterface,
            intelligenceCoordinator: this.intelligenceCoordinator
        };
    }

    /**
     * 记录集成状态
     */
    logIntegrationStatus() {
        const status = this.getIntegrationStatus();
        
        logger.info('📊 Chronicle-ReAct Integration Status:');
        logger.info(`   🔧 Initialized: ${status.isInitialized}`);
        logger.info(`   ⚡ Active: ${status.isActive}`);
        logger.info(`   🎯 Coordinator: ${status.components.coordinator}`);
        logger.info(`   🖥️ Confirmation UI: ${status.components.confirmationUI}`);
        logger.info(`   🌐 API Routes: ${status.components.apiRoutes}`);
        logger.info(`   👂 Event Listeners: ${status.components.eventListeners}`);
    }

    /**
     * 记录统计信息
     */
    logStatistics() {
        const stats = this.stats;
        const uptime = Math.floor((new Date() - stats.startTime) / 1000);
        
        logger.info('📈 Chronicle-ReAct Statistics:');
        logger.info(`   🔍 Total Investigations: ${stats.totalInvestigations}`);
        logger.info(`   ✅ Successful Repairs: ${stats.successfulRepairs}`);
        logger.info(`   👍 User Approvals: ${stats.userApprovals}`);
        logger.info(`   👎 User Denials: ${stats.userDenials}`);
        logger.info(`   ⏱️ Uptime: ${uptime}s`);
        
        if (stats.totalInvestigations > 0) {
            const successRate = (stats.successfulRepairs / stats.totalInvestigations * 100).toFixed(1);
            const approvalRate = ((stats.userApprovals / (stats.userApprovals + stats.userDenials)) * 100).toFixed(1);
            
            logger.info(`   📊 Success Rate: ${successRate}%`);
            logger.info(`   📊 Approval Rate: ${approvalRate}%`);
        }
    }

    /**
     * 手动触发ReAct代理
     */
    async triggerReActAgent(problemDescription, context = {}) {
        try {
            logger.info(`🧠 Manually triggering ReAct Agent: ${problemDescription}`);
            
            const result = await this.intelligenceCoordinator.handleComplexFailure({
                type: 'manual_trigger',
                description: problemDescription,
                context: context,
                detectedBy: 'manual_trigger'
            });
            
            this.stats.totalInvestigations++;
            
            return result;
            
        } catch (error) {
            logger.error(`❌ Failed to trigger ReAct Agent: ${error.message}`);
            throw error;
        }
    }

    /**
     * 关闭集成系统
     */
    async shutdown() {
        try {
            logger.info('🔄 Shutting down Chronicle-ReAct Integration...');
            
            this.isActive = false;
            
            // 关闭智能协调器
            if (this.intelligenceCoordinator) {
                await this.intelligenceCoordinator.shutdown();
            }
            
            // 清理确认界面
            if (this.confirmationInterface) {
                this.confirmationInterface.cleanup();
            }
            
            // 移除所有监听器
            this.removeAllListeners();
            
            logger.info('✅ Chronicle-ReAct Integration shutdown complete');
            
        } catch (error) {
            logger.error(`❌ Failed to shutdown integration: ${error.message}`);
            throw error;
        }
    }
}

module.exports = ChronicleReActIntegration;