/**
 * NEXUS用户确认界面 - ReAct代理行动计划确认系统
 * NEXUS User Confirmation Interface - ReAct Agent Action Plan Confirmation System
 * 
 * 这是用户拥有"最终否决权"的神圣界面
 * This is the sacred interface where users hold the "Final Veto Power"
 * 
 * 功能：
 * 1. 展示ReAct代理的完整行动计划书
 * 2. 显示风险评估和安全措施
 * 3. 提供用户批准/拒绝选项
 * 4. 记录用户决策和反馈
 */

const { createModuleLogger } = require('../shared/logger');
const logger = createModuleLogger('confirmation-interface');
const { EventEmitter } = require('events');

class ConfirmationInterface extends EventEmitter {
    constructor(options = {}) {
        super();
        this.options = {
            autoTimeout: options.autoTimeout || 300000, // 5分钟自动超时
            requireReason: options.requireReason !== false,
            logDecisions: options.logDecisions !== false,
            ...options
        };
        
        this.pendingConfirmations = new Map();
        this.decisionHistory = [];
        
        logger.info('🖥️ NEXUS Confirmation Interface initialized');
    }

    /**
     * 显示确认请求 - 核心确认界面
     */
    async showConfirmationRequest(actionPlan, investigationId) {
        const confirmationId = `confirm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        const confirmationData = {
            id: confirmationId,
            investigationId,
            actionPlan,
            timestamp: new Date().toISOString(),
            status: 'pending',
            timeoutId: null
        };

        // 设置自动超时
        if (this.options.autoTimeout > 0) {
            confirmationData.timeoutId = setTimeout(() => {
                this.handleTimeout(confirmationId);
            }, this.options.autoTimeout);
        }

        this.pendingConfirmations.set(confirmationId, confirmationData);

        // 生成用户界面HTML
        const interfaceHTML = this.generateConfirmationHTML(actionPlan, confirmationId);
        
        // 记录确认请求
        logger.info(`🔔 Confirmation request displayed: ${confirmationId}`);
        
        // 发出界面显示事件
        this.emit('confirmation_displayed', {
            confirmationId,
            investigationId,
            html: interfaceHTML,
            actionPlan
        });

        return {
            confirmationId,
            html: interfaceHTML,
            timeout: this.options.autoTimeout
        };
    }

    /**
     * 生成确认界面HTML
     */
    generateConfirmationHTML(actionPlan, confirmationId) {
        const riskColor = this.getRiskColor(actionPlan.problemAnalysis.riskLevel);
        const confidenceBar = this.generateConfidenceBar(actionPlan.problemAnalysis.confidence);
        
        return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chronicle ReAct Agent - Action Confirmation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #333;
        }
        
        .confirmation-container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 800px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from { transform: translateY(-20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 24px;
            border-radius: 16px 16px 0 0;
            text-align: center;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }
        
        .header .subtitle {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .content {
            padding: 24px;
        }
        
        .section {
            margin-bottom: 24px;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            background: #f8f9ff;
        }
        
        .section h3 {
            color: #4a5568;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .risk-indicator {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            color: white;
            background: ${riskColor};
        }
        
        .confidence-container {
            margin: 12px 0;
        }
        
        .confidence-bar {
            width: 100%;
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #48bb78, #38a169);
            width: ${(actionPlan.problemAnalysis.confidence * 100).toFixed(1)}%;
            transition: width 0.3s ease;
        }
        
        .steps-list {
            list-style: none;
            counter-reset: step-counter;
        }
        
        .steps-list li {
            counter-increment: step-counter;
            margin-bottom: 12px;
            padding: 12px;
            background: white;
            border-radius: 8px;
            border-left: 3px solid #667eea;
            position: relative;
        }
        
        .steps-list li::before {
            content: counter(step-counter);
            position: absolute;
            left: -15px;
            top: 12px;
            background: #667eea;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }
        
        .reasoning-chain {
            background: #f7fafc;
            border-radius: 8px;
            padding: 16px;
            margin-top: 12px;
        }
        
        .reasoning-step {
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .reasoning-step:last-child {
            border-bottom: none;
        }
        
        .reasoning-step strong {
            color: #4a5568;
        }
        
        .safety-measures {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-top: 12px;
        }
        
        .safety-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: white;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
        }
        
        .safety-item.enabled {
            border-color: #48bb78;
            background: #f0fff4;
        }
        
        .actions {
            display: flex;
            gap: 16px;
            justify-content: center;
            padding: 24px;
            background: #f8f9fa;
            border-radius: 0 0 16px 16px;
        }
        
        .btn {
            padding: 12px 32px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            min-width: 120px;
        }
        
        .btn-approve {
            background: linear-gradient(135deg, #48bb78, #38a169);
            color: white;
        }
        
        .btn-approve:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(72, 187, 120, 0.3);
        }
        
        .btn-deny {
            background: linear-gradient(135deg, #f56565, #e53e3e);
            color: white;
        }
        
        .btn-deny:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(245, 101, 101, 0.3);
        }
        
        .reason-input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 14px;
            margin-top: 12px;
            resize: vertical;
            min-height: 80px;
        }
        
        .reason-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .timer {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
        }
        
        .metadata {
            font-size: 12px;
            color: #718096;
            margin-top: 8px;
        }
    </style>
</head>
<body>
    <div class="confirmation-container">
        <div class="header">
            <h1>
                🧠 Chronicle ReAct Agent
                <span style="font-size: 16px;">Action Confirmation Required</span>
            </h1>
            <div class="subtitle">
                Task ID: ${actionPlan.taskId} | ${actionPlan.timestamp}
            </div>
        </div>
        
        <div class="content">
            <!-- 问题分析 -->
            <div class="section">
                <h3>🔍 Problem Analysis</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                    <div>
                        <strong>Root Cause:</strong><br>
                        <code>${actionPlan.problemAnalysis.rootCause}</code>
                    </div>
                    <div>
                        <strong>Risk Level:</strong><br>
                        <span class="risk-indicator">${actionPlan.problemAnalysis.riskLevel}</span>
                    </div>
                </div>
                
                <div class="confidence-container">
                    <strong>AI Confidence Level:</strong>
                    <div class="confidence-bar">
                        <div class="confidence-fill"></div>
                    </div>
                    <div class="metadata">${(actionPlan.problemAnalysis.confidence * 100).toFixed(1)}% confidence</div>
                </div>
                
                <div><strong>Detected Symptoms:</strong></div>
                <ul style="margin-left: 20px; margin-top: 8px;">
                    ${actionPlan.problemAnalysis.symptoms.map(symptom => `<li>${symptom}</li>`).join('')}
                </ul>
            </div>
            
            <!-- 推荐解决方案 -->
            <div class="section">
                <h3>🎯 Recommended Solution</h3>
                <div><strong>Strategy:</strong> ${actionPlan.recommendedSolution.strategy}</div>
                <div class="metadata">${actionPlan.recommendedSolution.description}</div>
                
                <div style="margin-top: 16px;"><strong>Execution Steps:</strong></div>
                <ol class="steps-list">
                    ${actionPlan.recommendedSolution.steps.map(step => `
                        <li>
                            <strong>${step.description}</strong>
                            <div class="metadata">
                                Type: ${step.type} | 
                                Critical: ${step.critical ? 'Yes' : 'No'} | 
                                Est. Time: ${step.estimatedTime}
                            </div>
                        </li>
                    `).join('')}
                </ol>
                
                <div style="margin-top: 16px;">
                    <strong>Estimated Total Time:</strong> ${actionPlan.recommendedSolution.estimatedTime}
                </div>
            </div>
            
            <!-- 安全措施 -->
            <div class="section">
                <h3>🛡️ Safety Measures</h3>
                <div class="safety-measures">
                    <div class="safety-item ${actionPlan.safetyMeasures.backupRequired ? 'enabled' : ''}">
                        ${actionPlan.safetyMeasures.backupRequired ? '✅' : '❌'} Backup Required
                    </div>
                    <div class="safety-item ${actionPlan.safetyMeasures.sandboxTesting ? 'enabled' : ''}">
                        ${actionPlan.safetyMeasures.sandboxTesting ? '✅' : '❌'} Sandbox Testing
                    </div>
                    <div class="safety-item ${actionPlan.safetyMeasures.userApproval ? 'enabled' : ''}">
                        ${actionPlan.safetyMeasures.userApproval ? '✅' : '❌'} User Approval
                    </div>
                    <div class="safety-item ${actionPlan.safetyMeasures.monitoringEnabled ? 'enabled' : ''}">
                        ${actionPlan.safetyMeasures.monitoringEnabled ? '✅' : '❌'} Monitoring Enabled
                    </div>
                </div>
                
                ${actionPlan.recommendedSolution.rollbackPlan ? `
                <div style="margin-top: 16px;">
                    <strong>🔄 Rollback Plan Available:</strong>
                    <div class="metadata">${actionPlan.recommendedSolution.rollbackPlan.description}</div>
                </div>
                ` : ''}
            </div>
            
            <!-- AI推理过程 -->
            <div class="section">
                <h3>🤖 AI Reasoning Process</h3>
                <div class="reasoning-chain">
                    ${actionPlan.reasoningProcess.map(step => `
                        <div class="reasoning-step">
                            <strong>Step ${step.step}:</strong> ${step.description}
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <!-- 用户反馈区域 -->
            <div class="section">
                <h3>💬 Your Decision & Feedback</h3>
                <textarea 
                    id="userReason" 
                    class="reason-input" 
                    placeholder="Please provide your reason for approval/denial (optional but recommended)..."
                ></textarea>
            </div>
        </div>
        
        <div class="actions">
            <button class="btn btn-approve" onclick="submitDecision(true)">
                ✅ Approve & Execute
            </button>
            <button class="btn btn-deny" onclick="submitDecision(false)">
                ❌ Deny & Cancel
            </button>
        </div>
    </div>
    
    <div class="timer" id="timer">
        Time remaining: <span id="countdown">${Math.floor(this.options.autoTimeout / 1000)}</span>s
    </div>
    
    <script>
        const confirmationId = '${confirmationId}';
        let timeRemaining = ${Math.floor(this.options.autoTimeout / 1000)};
        
        // 倒计时器
        const countdownInterval = setInterval(() => {
            timeRemaining--;
            document.getElementById('countdown').textContent = timeRemaining;
            
            if (timeRemaining <= 0) {
                clearInterval(countdownInterval);
                document.getElementById('timer').innerHTML = '⏰ Timeout - Auto-denied';
                document.getElementById('timer').style.background = 'rgba(245, 101, 101, 0.9)';
                
                // 禁用按钮
                document.querySelectorAll('.btn').forEach(btn => {
                    btn.disabled = true;
                    btn.style.opacity = '0.5';
                    btn.style.cursor = 'not-allowed';
                });
            }
        }, 1000);
        
        // 提交决策
        function submitDecision(approved) {
            const reason = document.getElementById('userReason').value.trim();
            
            // 清除倒计时
            clearInterval(countdownInterval);
            
            // 发送决策到后端
            fetch('/api/confirmation/respond', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    confirmationId: confirmationId,
                    approved: approved,
                    reason: reason,
                    timestamp: new Date().toISOString()
                })
            }).then(response => {
                if (response.ok) {
                    // 显示成功消息
                    document.body.innerHTML = \`
                        <div style="display: flex; align-items: center; justify-content: center; min-height: 100vh; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);">
                            <div style="background: white; padding: 40px; border-radius: 16px; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.1);">
                                <h2 style="color: \${approved ? '#48bb78' : '#f56565'}; margin-bottom: 16px;">
                                    \${approved ? '✅ Action Approved' : '❌ Action Denied'}
                                </h2>
                                <p style="color: #4a5568;">
                                    Your decision has been recorded and communicated to the ReAct Agent.
                                </p>
                                <div style="margin-top: 20px; font-size: 14px; color: #718096;">
                                    Confirmation ID: \${confirmationId}
                                </div>
                            </div>
                        </div>
                    \`;
                } else {
                    alert('Failed to submit decision. Please try again.');
                }
            }).catch(error => {
                console.error('Error submitting decision:', error);
                alert('Network error. Please check your connection and try again.');
            });
        }
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    submitDecision(true);
                } else if (e.key === 'Backspace') {
                    e.preventDefault();
                    submitDecision(false);
                }
            }
        });
        
        // 页面加载完成后的动画
        document.addEventListener('DOMContentLoaded', () => {
            document.querySelector('.confirmation-container').style.animation = 'slideIn 0.5s ease-out';
        });
    </script>
</body>
</html>`;
    }

    /**
     * 处理用户决策响应
     */
    async handleUserResponse(confirmationId, approved, reason = '') {
        const confirmation = this.pendingConfirmations.get(confirmationId);
        
        if (!confirmation) {
            throw new Error(`Confirmation not found: ${confirmationId}`);
        }

        // 清除超时定时器
        if (confirmation.timeoutId) {
            clearTimeout(confirmation.timeoutId);
        }

        // 更新确认状态
        confirmation.status = approved ? 'approved' : 'denied';
        confirmation.userReason = reason;
        confirmation.responseTime = new Date().toISOString();
        confirmation.responseDelay = new Date() - new Date(confirmation.timestamp);

        // 记录决策历史
        const decision = {
            confirmationId,
            investigationId: confirmation.investigationId,
            approved,
            reason,
            timestamp: confirmation.responseTime,
            responseDelay: confirmation.responseDelay,
            actionPlan: confirmation.actionPlan.title,
            riskLevel: confirmation.actionPlan.problemAnalysis.riskLevel
        };

        if (this.options.logDecisions) {
            this.decisionHistory.push(decision);
            logger.info(`👤 User decision recorded: ${approved ? 'APPROVED' : 'DENIED'} - ${confirmationId}`);
            
            if (reason) {
                logger.info(`💬 User reason: ${reason}`);
            }
        }

        // 发出决策事件
        this.emit('user_decision', {
            confirmationId,
            investigationId: confirmation.investigationId,
            approved,
            reason,
            decision
        });

        // 从待处理列表中移除
        this.pendingConfirmations.delete(confirmationId);

        return decision;
    }

    /**
     * 处理超时
     */
    handleTimeout(confirmationId) {
        const confirmation = this.pendingConfirmations.get(confirmationId);
        
        if (confirmation && confirmation.status === 'pending') {
            logger.warn(`⏰ Confirmation timeout: ${confirmationId}`);
            
            // 自动拒绝
            this.handleUserResponse(confirmationId, false, 'Automatic denial due to timeout');
        }
    }

    /**
     * 获取风险颜色
     */
    getRiskColor(riskLevel) {
        switch (riskLevel.toLowerCase()) {
            case 'high': return '#f56565';
            case 'medium': return '#ed8936';
            case 'low': return '#48bb78';
            default: return '#718096';
        }
    }

    /**
     * 生成置信度条
     */
    generateConfidenceBar(confidence) {
        const percentage = (confidence * 100).toFixed(1);
        const color = confidence >= 0.8 ? '#48bb78' : 
                     confidence >= 0.6 ? '#ed8936' : '#f56565';
        
        return {
            percentage,
            color,
            width: percentage + '%'
        };
    }

    /**
     * 获取待处理确认列表
     */
    getPendingConfirmations() {
        return Array.from(this.pendingConfirmations.values()).map(conf => ({
            id: conf.id,
            investigationId: conf.investigationId,
            timestamp: conf.timestamp,
            status: conf.status,
            actionPlan: {
                title: conf.actionPlan.title,
                riskLevel: conf.actionPlan.problemAnalysis.riskLevel,
                confidence: conf.actionPlan.problemAnalysis.confidence
            }
        }));
    }

    /**
     * 获取决策历史
     */
    getDecisionHistory(limit = 50) {
        return this.decisionHistory
            .slice(-limit)
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    }

    /**
     * 获取决策统计
     */
    getDecisionStats() {
        const total = this.decisionHistory.length;
        const approved = this.decisionHistory.filter(d => d.approved).length;
        const denied = total - approved;
        
        const avgResponseTime = this.decisionHistory.reduce((sum, d) => sum + d.responseDelay, 0) / total;
        
        return {
            total,
            approved,
            denied,
            approvalRate: total > 0 ? (approved / total * 100).toFixed(1) + '%' : '0%',
            averageResponseTime: total > 0 ? Math.round(avgResponseTime / 1000) + 's' : '0s'
        };
    }

    /**
     * 清理过期确认
     */
    cleanup() {
        const now = new Date();
        const expired = [];
        
        for (const [id, confirmation] of this.pendingConfirmations) {
            const age = now - new Date(confirmation.timestamp);
            if (age > this.options.autoTimeout * 2) { // 超过两倍超时时间
                expired.push(id);
            }
        }
        
        expired.forEach(id => {
            this.pendingConfirmations.delete(id);
            logger.info(`🧹 Cleaned up expired confirmation: ${id}`);
        });
        
        return expired.length;
    }
}

module.exports = ConfirmationInterface;