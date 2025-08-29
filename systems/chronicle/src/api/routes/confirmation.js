/**
 * 确认API路由 - 处理用户确认响应
 * Confirmation API Routes - Handle User Confirmation Responses
 */

const express = require('express');
const router = express.Router();
const { createModuleLogger } = require('../../shared/logger');
const logger = createModuleLogger('confirmation-api');

// 全局确认界面实例（将由主应用注入）
let confirmationInterface = null;
let intelligenceCoordinator = null;

/**
 * 设置依赖注入
 */
function setDependencies(confirmationInterfaceInstance, intelligenceCoordinatorInstance) {
    confirmationInterface = confirmationInterfaceInstance;
    intelligenceCoordinator = intelligenceCoordinatorInstance;
}

/**
 * POST /api/confirmation/respond
 * 处理用户确认响应
 */
router.post('/respond', async (req, res) => {
    try {
        const { confirmationId, approved, reason, timestamp } = req.body;
        
        if (!confirmationId || typeof approved !== 'boolean') {
            return res.status(400).json({
                error: 'Missing required fields: confirmationId, approved'
            });
        }

        if (!confirmationInterface) {
            return res.status(500).json({
                error: 'Confirmation interface not initialized'
            });
        }

        // 处理用户响应
        const decision = await confirmationInterface.handleUserResponse(
            confirmationId, 
            approved, 
            reason || ''
        );

        // 通知智能协调器
        if (intelligenceCoordinator && decision.investigationId) {
            intelligenceCoordinator.approveOperation(
                decision.investigationId,
                approved,
                reason || ''
            );
        }

        logger.info(`✅ User confirmation processed: ${confirmationId} - ${approved ? 'APPROVED' : 'DENIED'}`);

        res.json({
            success: true,
            decision,
            message: `Action ${approved ? 'approved' : 'denied'} successfully`
        });

    } catch (error) {
        logger.error(`❌ Failed to process confirmation: ${error.message}`);
        res.status(500).json({
            error: 'Failed to process confirmation',
            details: error.message
        });
    }
});

/**
 * GET /api/confirmation/pending
 * 获取待处理的确认请求
 */
router.get('/pending', (req, res) => {
    try {
        if (!confirmationInterface) {
            return res.status(500).json({
                error: 'Confirmation interface not initialized'
            });
        }

        const pending = confirmationInterface.getPendingConfirmations();
        
        res.json({
            success: true,
            pending,
            count: pending.length
        });

    } catch (error) {
        logger.error(`❌ Failed to get pending confirmations: ${error.message}`);
        res.status(500).json({
            error: 'Failed to get pending confirmations',
            details: error.message
        });
    }
});

/**
 * GET /api/confirmation/history
 * 获取决策历史
 */
router.get('/history', (req, res) => {
    try {
        if (!confirmationInterface) {
            return res.status(500).json({
                error: 'Confirmation interface not initialized'
            });
        }

        const limit = parseInt(req.query.limit) || 50;
        const history = confirmationInterface.getDecisionHistory(limit);
        const stats = confirmationInterface.getDecisionStats();
        
        res.json({
            success: true,
            history,
            stats,
            count: history.length
        });

    } catch (error) {
        logger.error(`❌ Failed to get decision history: ${error.message}`);
        res.status(500).json({
            error: 'Failed to get decision history',
            details: error.message
        });
    }
});

/**
 * GET /api/confirmation/stats
 * 获取决策统计信息
 */
router.get('/stats', (req, res) => {
    try {
        if (!confirmationInterface) {
            return res.status(500).json({
                error: 'Confirmation interface not initialized'
            });
        }

        const stats = confirmationInterface.getDecisionStats();
        const pending = confirmationInterface.getPendingConfirmations();
        
        res.json({
            success: true,
            stats: {
                ...stats,
                pendingCount: pending.length,
                lastUpdate: new Date().toISOString()
            }
        });

    } catch (error) {
        logger.error(`❌ Failed to get confirmation stats: ${error.message}`);
        res.status(500).json({
            error: 'Failed to get confirmation stats',
            details: error.message
        });
    }
});

/**
 * POST /api/confirmation/cleanup
 * 清理过期的确认请求
 */
router.post('/cleanup', (req, res) => {
    try {
        if (!confirmationInterface) {
            return res.status(500).json({
                error: 'Confirmation interface not initialized'
            });
        }

        const cleanedCount = confirmationInterface.cleanup();
        
        logger.info(`🧹 Cleaned up ${cleanedCount} expired confirmations`);
        
        res.json({
            success: true,
            cleanedCount,
            message: `Cleaned up ${cleanedCount} expired confirmations`
        });

    } catch (error) {
        logger.error(`❌ Failed to cleanup confirmations: ${error.message}`);
        res.status(500).json({
            error: 'Failed to cleanup confirmations',
            details: error.message
        });
    }
});

/**
 * GET /api/confirmation/interface/:confirmationId
 * 获取特定确认请求的界面HTML
 */
router.get('/interface/:confirmationId', (req, res) => {
    try {
        const { confirmationId } = req.params;
        
        if (!confirmationInterface) {
            return res.status(500).send(`
                <html>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h2 style="color: #f56565;">❌ Confirmation Interface Not Available</h2>
                        <p>The confirmation interface is not properly initialized.</p>
                    </body>
                </html>
            `);
        }

        const pending = confirmationInterface.getPendingConfirmations();
        const confirmation = pending.find(c => c.id === confirmationId);
        
        if (!confirmation) {
            return res.status(404).send(`
                <html>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h2 style="color: #f56565;">❌ Confirmation Not Found</h2>
                        <p>The requested confirmation (${confirmationId}) was not found or has expired.</p>
                    </body>
                </html>
            `);
        }

        // 这里应该返回实际的HTML界面
        // 由于我们需要完整的actionPlan数据，这个路由可能需要重新设计
        res.send(`
            <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h2 style="color: #667eea;">🔔 Confirmation Required</h2>
                    <p>Confirmation ID: ${confirmationId}</p>
                    <p>Investigation ID: ${confirmation.investigationId}</p>
                    <p>Risk Level: ${confirmation.actionPlan.riskLevel}</p>
                    <p>Confidence: ${(confirmation.actionPlan.confidence * 100).toFixed(1)}%</p>
                    <div style="margin-top: 30px;">
                        <button onclick="respond(true)" style="background: #48bb78; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 0 10px; cursor: pointer;">
                            ✅ Approve
                        </button>
                        <button onclick="respond(false)" style="background: #f56565; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 0 10px; cursor: pointer;">
                            ❌ Deny
                        </button>
                    </div>
                    <script>
                        function respond(approved) {
                            fetch('/api/confirmation/respond', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    confirmationId: '${confirmationId}',
                                    approved: approved,
                                    reason: prompt('Please provide a reason (optional):') || ''
                                })
                            }).then(response => response.json())
                              .then(data => {
                                  if (data.success) {
                                      document.body.innerHTML = '<h2 style="color: #48bb78;">✅ Response Recorded</h2><p>Thank you for your decision.</p>';
                                  } else {
                                      alert('Error: ' + data.error);
                                  }
                              });
                        }
                    </script>
                </body>
            </html>
        `);

    } catch (error) {
        logger.error(`❌ Failed to serve confirmation interface: ${error.message}`);
        res.status(500).send(`
            <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h2 style="color: #f56565;">❌ Server Error</h2>
                    <p>Failed to load confirmation interface: ${error.message}</p>
                </body>
            </html>
        `);
    }
});

module.exports = {
    router,
    setDependencies
};