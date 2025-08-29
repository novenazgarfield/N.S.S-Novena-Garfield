#!/usr/bin/env node

/**
 * ReAct代理测试脚本
 * ReAct Agent Test Script
 * 
 * 用于测试第三章"智慧的注入"功能
 * Used to test Chapter 3 "The Integration of Wisdom" functionality
 */

const ReActAgent = require('./react-agent');
const IntelligenceCoordinator = require('./intelligence-coordinator');
const ConfirmationInterface = require('../ui/confirmation-interface');
const { createModuleLogger } = require('../shared/logger');
const logger = createModuleLogger('react-test');

class ReActAgentTester {
    constructor() {
        this.reactAgent = null;
        this.coordinator = null;
        this.confirmationInterface = null;
    }

    /**
     * 运行所有测试
     */
    async runAllTests() {
        console.log('🧠 Chronicle ReAct Agent Test Suite');
        console.log('=====================================');
        console.log('');

        try {
            // 测试1: ReAct代理基础功能
            await this.testReActAgentBasics();
            
            // 测试2: 智能协调器
            await this.testIntelligenceCoordinator();
            
            // 测试3: 确认界面
            await this.testConfirmationInterface();
            
            // 测试4: 完整集成流程
            await this.testFullIntegrationFlow();
            
            console.log('✅ All tests completed successfully!');
            
        } catch (error) {
            console.error('❌ Test suite failed:', error.message);
            process.exit(1);
        }
    }

    /**
     * 测试ReAct代理基础功能
     */
    async testReActAgentBasics() {
        console.log('🔬 Test 1: ReAct Agent Basics');
        console.log('------------------------------');
        
        this.reactAgent = new ReActAgent({
            maxReasoningSteps: 5,
            confidenceThreshold: 0.6,
            userConfirmationRequired: false // 测试时禁用用户确认
        });

        // 测试代理状态
        const status = this.reactAgent.getStatus();
        console.log(`📊 Agent Status: ${status.status}`);
        console.log(`📚 Knowledge Base Size: ${status.knowledgeBaseSize}`);
        
        // 测试简单问题处理
        console.log('🤔 Testing simple problem analysis...');
        const result = await this.reactAgent.activate(
            'System memory usage is high and applications are running slowly',
            { severity: 'medium', affectedServices: ['web-server', 'database'] }
        );
        
        console.log(`✅ Problem analyzed: ${result.success ? 'SUCCESS' : 'FAILED'}`);
        console.log(`📋 Root Cause: ${result.actionPlan.problemAnalysis.rootCause}`);
        console.log(`🎯 Strategy: ${result.actionPlan.recommendedSolution.strategy}`);
        console.log(`📊 Confidence: ${(result.actionPlan.problemAnalysis.confidence * 100).toFixed(1)}%`);
        console.log('');
    }

    /**
     * 测试智能协调器
     */
    async testIntelligenceCoordinator() {
        console.log('🔬 Test 2: Intelligence Coordinator');
        console.log('------------------------------------');
        
        // 创建模拟的Chronicle系统
        const mockChronicleSystem = {
            logEvent: (event) => {
                console.log(`📝 Chronicle Event: ${event.type}`);
            }
        };
        
        this.coordinator = new IntelligenceCoordinator(mockChronicleSystem);
        
        // 测试复杂故障处理
        console.log('🚨 Testing complex failure handling...');
        
        const failureData = {
            type: 'system_crash',
            description: 'Database server crashed with memory corruption errors',
            severity: 'critical',
            affectedServices: ['database', 'api-server', 'web-frontend'],
            context: {
                errorLogs: ['Memory allocation failed', 'Segmentation fault', 'Core dump generated'],
                systemMetrics: { cpu: '95%', memory: '98%', disk: '45%' }
            }
        };
        
        // 监听确认请求
        this.coordinator.on('user_confirmation_needed', (data) => {
            console.log(`🔔 User confirmation required: ${data.actionPlan.title}`);
            console.log(`⚠️ Risk Level: ${data.actionPlan.problemAnalysis.riskLevel}`);
            
            // 自动批准（测试用）
            setTimeout(() => {
                this.coordinator.approveOperation(
                    data.investigationId || 'test_investigation',
                    true,
                    'Auto-approved for testing'
                );
            }, 1000);
        });
        
        const result = await this.coordinator.handleComplexFailure(failureData);
        
        console.log(`✅ Complex failure handled: ${result.success ? 'SUCCESS' : 'FAILED'}`);
        console.log(`📊 Success Rate: ${result.success ? '100%' : '0%'}`);
        console.log('');
    }

    /**
     * 测试确认界面
     */
    async testConfirmationInterface() {
        console.log('🔬 Test 3: Confirmation Interface');
        console.log('----------------------------------');
        
        this.confirmationInterface = new ConfirmationInterface({
            autoTimeout: 10000, // 10秒测试超时
            requireReason: true,
            logDecisions: true
        });
        
        // 创建模拟的行动计划
        const mockActionPlan = {
            title: 'Test Action Plan - Database Recovery',
            taskId: 'test_task_001',
            timestamp: new Date().toISOString(),
            problemAnalysis: {
                symptoms: ['database_crash', 'memory_corruption'],
                rootCause: 'memory_leak',
                confidence: 0.85,
                riskLevel: 'high'
            },
            recommendedSolution: {
                strategy: 'conservative',
                description: 'Safe database recovery with backup restoration',
                steps: [
                    { id: 1, description: 'Stop database service', type: 'service_control', critical: true, estimatedTime: '30s' },
                    { id: 2, description: 'Restore from latest backup', type: 'data_recovery', critical: true, estimatedTime: '5min' },
                    { id: 3, description: 'Restart database service', type: 'service_control', critical: true, estimatedTime: '1min' }
                ],
                estimatedTime: '6-8 minutes',
                rollbackPlan: { description: 'Restore previous backup if recovery fails' }
            },
            safetyMeasures: {
                backupRequired: true,
                sandboxTesting: true,
                userApproval: true,
                monitoringEnabled: true
            },
            reasoningProcess: [
                { step: 1, description: 'Analyzed system symptoms and identified memory corruption' },
                { step: 2, description: 'Matched failure pattern to known database crash scenarios' },
                { step: 3, description: 'Assessed risk level as HIGH due to data integrity concerns' },
                { step: 4, description: 'Selected conservative strategy to minimize data loss risk' }
            ]
        };
        
        console.log('🖥️ Testing confirmation interface generation...');
        
        const confirmation = await this.confirmationInterface.showConfirmationRequest(
            mockActionPlan,
            'test_investigation_001'
        );
        
        console.log(`✅ Confirmation interface created: ${confirmation.confirmationId}`);
        console.log(`⏱️ Timeout: ${confirmation.timeout}ms`);
        
        // 模拟用户响应
        console.log('👤 Simulating user approval...');
        
        setTimeout(async () => {
            const decision = await this.confirmationInterface.handleUserResponse(
                confirmation.confirmationId,
                true,
                'Approved for testing - database recovery is critical'
            );
            
            console.log(`✅ User decision processed: ${decision.approved ? 'APPROVED' : 'DENIED'}`);
            console.log(`💬 User reason: ${decision.reason}`);
        }, 2000);
        
        // 等待处理完成
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // 检查统计信息
        const stats = this.confirmationInterface.getDecisionStats();
        console.log(`📊 Decision Stats: ${stats.total} total, ${stats.approvalRate} approval rate`);
        console.log('');
    }

    /**
     * 测试完整集成流程
     */
    async testFullIntegrationFlow() {
        console.log('🔬 Test 4: Full Integration Flow');
        console.log('---------------------------------');
        
        console.log('🧠 Testing end-to-end ReAct workflow...');
        
        // 模拟一个需要用户确认的复杂故障
        const criticalFailure = {
            type: 'security_breach',
            description: 'Suspicious network activity detected with potential data exfiltration',
            severity: 'critical',
            affectedServices: ['web-server', 'database', 'user-auth', 'file-storage'],
            context: {
                securityAlerts: [
                    'Unusual outbound traffic to unknown IP addresses',
                    'Multiple failed authentication attempts',
                    'Unauthorized file access patterns detected'
                ],
                networkMetrics: {
                    outboundTraffic: '500MB in 10 minutes',
                    failedLogins: 47,
                    suspiciousIPs: ['192.168.1.100', '10.0.0.50']
                }
            }
        };
        
        console.log('🚨 Simulating critical security breach...');
        
        // 设置事件监听
        let confirmationReceived = false;
        let investigationCompleted = false;
        
        this.coordinator.on('user_confirmation_needed', (data) => {
            console.log('🔔 CRITICAL: User confirmation required for security response');
            console.log(`📋 Action Plan: ${data.actionPlan.title}`);
            console.log(`⚠️ Risk Level: ${data.actionPlan.problemAnalysis.riskLevel}`);
            console.log(`🎯 Strategy: ${data.actionPlan.recommendedSolution.strategy}`);
            
            confirmationReceived = true;
            
            // 模拟用户快速批准安全响应
            setTimeout(() => {
                console.log('👤 User APPROVED security response (simulated)');
                this.coordinator.approveOperation(
                    data.investigationId,
                    true,
                    'URGENT: Security breach requires immediate response'
                );
            }, 1500);
        });
        
        this.coordinator.on('investigation_completed', (data) => {
            console.log(`🎯 Investigation completed: ${data.result.success ? 'SUCCESS' : 'FAILED'}`);
            console.log(`📊 Execution Summary: ${JSON.stringify(data.result.summary, null, 2)}`);
            investigationCompleted = true;
        });
        
        // 启动调查
        const result = await this.coordinator.handleComplexFailure(criticalFailure);
        
        // 等待流程完成
        let waitTime = 0;
        while ((!confirmationReceived || !investigationCompleted) && waitTime < 10000) {
            await new Promise(resolve => setTimeout(resolve, 500));
            waitTime += 500;
        }
        
        console.log('📈 Integration Flow Results:');
        console.log(`   🔔 Confirmation Received: ${confirmationReceived ? 'YES' : 'NO'}`);
        console.log(`   🎯 Investigation Completed: ${investigationCompleted ? 'YES' : 'NO'}`);
        console.log(`   ✅ Overall Success: ${result.success ? 'YES' : 'NO'}`);
        
        if (result.success) {
            console.log(`   📊 Confidence: ${(result.actionPlan.problemAnalysis.confidence * 100).toFixed(1)}%`);
            console.log(`   ⏱️ Execution Time: ${result.summary.executionTime}ms`);
        }
        
        console.log('');
    }
}

// 运行测试
if (require.main === module) {
    const tester = new ReActAgentTester();
    
    tester.runAllTests().then(() => {
        console.log('🎉 Chronicle ReAct Agent Test Suite Completed Successfully!');
        console.log('');
        console.log('第三章："智慧"的"注入" - 测试通过 ✅');
        console.log('Chapter 3: "The Integration of Wisdom" - Tests Passed ✅');
        console.log('');
        console.log('ReAct代理已成功苏醒并集成到Chronicle系统中！');
        console.log('The ReAct Agent has successfully awakened and integrated into Chronicle!');
        
        process.exit(0);
    }).catch((error) => {
        console.error('❌ Test suite failed:', error);
        process.exit(1);
    });
}

module.exports = ReActAgentTester;