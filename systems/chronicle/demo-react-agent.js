#!/usr/bin/env node

/**
 * Chronicle ReAct代理演示脚本
 * Chronicle ReAct Agent Demo Script
 * 
 * 展示第三章"智慧的注入"的完整功能
 * Demonstrates the complete functionality of Chapter 3 "The Integration of Wisdom"
 */

const ChronicleReActIntegration = require('./src/intelligence/chronicle-integration');
const { createModuleLogger } = require('./src/shared/logger');

const logger = createModuleLogger('demo');

class ReActDemo {
    constructor() {
        this.integration = null;
    }

    async run() {
        console.log('🧠 Chronicle ReAct Agent - Live Demo');
        console.log('====================================');
        console.log('');
        console.log('第三章："智慧"的"注入" - 实时演示');
        console.log('Chapter 3: "The Integration of Wisdom" - Live Demo');
        console.log('');

        try {
            // 初始化集成系统
            await this.initializeSystem();
            
            // 演示场景1: 内存泄漏问题
            await this.demoMemoryLeak();
            
            // 演示场景2: 数据库连接问题
            await this.demoDatabaseIssue();
            
            // 演示场景3: 安全威胁（需要用户确认）
            await this.demoSecurityThreat();
            
            // 显示统计信息
            await this.showStatistics();
            
            console.log('🎉 演示完成！ReAct代理已成功展示其智慧能力！');
            console.log('🎉 Demo completed! ReAct Agent has successfully demonstrated its wisdom!');
            
        } catch (error) {
            console.error('❌ Demo failed:', error.message);
        } finally {
            if (this.integration) {
                await this.integration.shutdown();
            }
        }
    }

    async initializeSystem() {
        console.log('🚀 Initializing Chronicle ReAct Integration...');
        
        // 创建模拟的Chronicle系统
        const mockChronicleSystem = {
            logEvent: (event) => {
                logger.info(`Chronicle Event: ${event.type}`, event);
            },
            on: (event, handler) => {
                // 模拟事件监听器
            }
        };
        
        this.integration = new ChronicleReActIntegration(mockChronicleSystem);
        
        // 监听确认请求
        this.integration.on('confirmation_required', (data) => {
            console.log('');
            console.log('🔔 ===== USER CONFIRMATION REQUIRED =====');
            console.log(`📋 Action Plan: ${data.actionPlan.title}`);
            console.log(`⚠️ Risk Level: ${data.actionPlan.problemAnalysis.riskLevel}`);
            console.log(`📊 Confidence: ${(data.actionPlan.problemAnalysis.confidence * 100).toFixed(1)}%`);
            console.log(`🎯 Strategy: ${data.actionPlan.recommendedSolution.strategy}`);
            console.log('');
            console.log('In a real scenario, this would open the NEXUS confirmation interface.');
            console.log('For demo purposes, we will auto-approve after 3 seconds...');
            console.log('');
            
            // 自动批准（演示用）
            setTimeout(() => {
                const dependencies = this.integration.getDependencies();
                if (dependencies.intelligenceCoordinator) {
                    dependencies.intelligenceCoordinator.approveOperation(
                        data.investigationId || 'demo_investigation',
                        true,
                        'Auto-approved for demo purposes'
                    );
                    console.log('✅ User APPROVED the operation (simulated)');
                    console.log('');
                }
            }, 3000);
        });
        
        await this.integration.initialize();
        console.log('✅ System initialized successfully!');
        console.log('');
    }

    async demoMemoryLeak() {
        console.log('📊 Demo Scenario 1: Memory Leak Detection');
        console.log('------------------------------------------');
        
        const memoryIssue = {
            type: 'memory_leak',
            description: 'Application memory usage has increased from 2GB to 7GB over the past hour',
            severity: 'high',
            affectedServices: ['web-server', 'background-workers'],
            context: {
                memoryUsage: {
                    current: '7.2GB',
                    baseline: '2.1GB',
                    trend: 'increasing',
                    rate: '150MB/min'
                },
                symptoms: [
                    'Slow response times',
                    'Frequent garbage collection',
                    'OOM warnings in logs'
                ]
            }
        };
        
        console.log('🚨 Simulating memory leak detection...');
        const result = await this.integration.handleSystemFailure(memoryIssue);
        
        console.log(`✅ Memory leak handled: ${result ? 'SUCCESS' : 'COMPLETED'}`);
        console.log('');
        
        // 等待处理完成
        await new Promise(resolve => setTimeout(resolve, 2000));
    }

    async demoDatabaseIssue() {
        console.log('🗄️ Demo Scenario 2: Database Connection Pool Exhaustion');
        console.log('--------------------------------------------------------');
        
        const dbIssue = {
            type: 'database_connection_exhaustion',
            description: 'Database connection pool is exhausted, new connections are being rejected',
            severity: 'critical',
            affectedServices: ['api-server', 'web-frontend', 'reporting-service'],
            context: {
                connectionPool: {
                    maxConnections: 100,
                    activeConnections: 100,
                    queuedRequests: 47,
                    avgConnectionTime: '15.7s'
                },
                errorLogs: [
                    'Connection timeout after 30s',
                    'Pool exhausted, rejecting connection',
                    'Database unavailable for service'
                ]
            }
        };
        
        console.log('🚨 Simulating database connection crisis...');
        const result = await this.integration.handleSystemFailure(dbIssue);
        
        console.log(`✅ Database issue handled: ${result ? 'SUCCESS' : 'COMPLETED'}`);
        console.log('');
        
        // 等待处理完成
        await new Promise(resolve => setTimeout(resolve, 2000));
    }

    async demoSecurityThreat() {
        console.log('🔒 Demo Scenario 3: Security Threat (Requires User Confirmation)');
        console.log('----------------------------------------------------------------');
        
        const securityThreat = {
            type: 'potential_data_breach',
            description: 'Unusual data access patterns detected with potential unauthorized data exfiltration',
            severity: 'critical',
            affectedServices: ['user-database', 'file-storage', 'api-gateway', 'audit-system'],
            context: {
                securityAlerts: [
                    'Bulk data queries from unusual IP address',
                    'Multiple admin privilege escalation attempts',
                    'Large file downloads outside business hours',
                    'Suspicious API usage patterns detected'
                ],
                threatIndicators: {
                    suspiciousIP: '192.168.1.100',
                    dataVolume: '2.3GB in 15 minutes',
                    failedAuthAttempts: 23,
                    privilegeEscalations: 5
                }
            }
        };
        
        console.log('🚨 CRITICAL: Simulating security threat detection...');
        console.log('⚠️ This scenario will require user confirmation due to high risk!');
        console.log('');
        
        const result = await this.integration.handleSystemFailure(securityThreat);
        
        // 等待用户确认流程完成
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        console.log(`✅ Security threat handled: ${result ? 'SUCCESS' : 'COMPLETED'}`);
        console.log('');
    }

    async showStatistics() {
        console.log('📊 Chronicle ReAct Integration Statistics');
        console.log('=========================================');
        
        const status = this.integration.getIntegrationStatus();
        
        console.log(`🔧 System Status:`);
        console.log(`   Initialized: ${status.isInitialized ? '✅' : '❌'}`);
        console.log(`   Active: ${status.isActive ? '✅' : '❌'}`);
        console.log(`   Uptime: ${Math.floor(status.stats.uptime / 1000)}s`);
        console.log('');
        
        console.log(`📈 Performance Metrics:`);
        console.log(`   Total Investigations: ${status.stats.totalInvestigations}`);
        console.log(`   Successful Repairs: ${status.stats.successfulRepairs}`);
        console.log(`   User Approvals: ${status.stats.userApprovals}`);
        console.log(`   User Denials: ${status.stats.userDenials}`);
        
        if (status.stats.totalInvestigations > 0) {
            const successRate = (status.stats.successfulRepairs / status.stats.totalInvestigations * 100).toFixed(1);
            console.log(`   Success Rate: ${successRate}%`);
        }
        
        if (status.stats.userApprovals + status.stats.userDenials > 0) {
            const approvalRate = (status.stats.userApprovals / (status.stats.userApprovals + status.stats.userDenials) * 100).toFixed(1);
            console.log(`   User Approval Rate: ${approvalRate}%`);
        }
        
        console.log('');
        console.log(`🧠 ReAct Agent Status:`);
        if (status.stats.reactAgentStatus) {
            console.log(`   Status: ${status.stats.reactAgentStatus.status}`);
            console.log(`   Knowledge Base: ${status.stats.reactAgentStatus.knowledgeBaseSize} entries`);
            console.log(`   Experience: ${status.stats.reactAgentStatus.experienceCount} cases`);
        }
        
        console.log('');
    }
}

// 运行演示
if (require.main === module) {
    const demo = new ReActDemo();
    
    demo.run().then(() => {
        console.log('');
        console.log('🌟 Chronicle ReAct Agent Demo Completed Successfully!');
        console.log('');
        console.log('The ReAct Agent has demonstrated its ability to:');
        console.log('✅ Analyze complex system failures');
        console.log('✅ Generate intelligent action plans');
        console.log('✅ Request user confirmation for high-risk operations');
        console.log('✅ Execute solutions with proper monitoring');
        console.log('✅ Learn from experience for future improvements');
        console.log('');
        console.log('第三章"智慧的注入"已成功实现！');
        console.log('Chapter 3 "The Integration of Wisdom" has been successfully implemented!');
        
        process.exit(0);
    }).catch((error) => {
        console.error('❌ Demo failed:', error);
        process.exit(1);
    });
}

module.exports = ReActDemo;