/**
 * Changlee错误恢复机制
 * 自动处理应用崩溃和错误恢复
 */

class ErrorRecoveryManager {
    constructor() {
        this.restartAttempts = 0;
        this.maxRestartAttempts = 3;
        this.restartDelay = 5000;
        this.isRecovering = false;
        
        this.setupErrorHandlers();
        this.setupMemoryMonitoring();
    }
    
    setupErrorHandlers() {
        // 主进程错误处理
        process.on('uncaughtException', (error) => {
            console.error('Uncaught Exception:', error);
            this.handleCrash(error);
        });
        
        process.on('unhandledRejection', (reason, promise) => {
            console.error('Unhandled Rejection at:', promise, 'reason:', reason);
            this.handleCrash(reason);
        });
    }
    
    setupMemoryMonitoring() {
        setInterval(() => {
            const memoryUsage = process.memoryUsage();
            const heapUsedMB = memoryUsage.heapUsed / 1024 / 1024;
            
            if (heapUsedMB > 512) { // 512MB阈值
                console.warn(`High memory usage: ${heapUsedMB.toFixed(2)}MB`);
                this.triggerGarbageCollection();
            }
        }, 60000); // 每分钟检查一次
    }
    
    handleCrash(error) {
        if (this.isRecovering) return;
        
        this.isRecovering = true;
        
        // 保存应用状态
        this.saveApplicationState();
        
        // 记录错误
        this.logError(error);
        
        // 尝试重启
        if (this.restartAttempts < this.maxRestartAttempts) {
            setTimeout(() => {
                this.attemptRestart();
            }, this.restartDelay);
        } else {
            console.error('Max restart attempts reached. Manual intervention required.');
            this.showCrashDialog();
        }
    }
    
    saveApplicationState() {
        try {
            const state = {
                timestamp: new Date().toISOString(),
                memoryUsage: process.memoryUsage(),
                // 添加更多状态信息
            };
            
            require('fs').writeFileSync(
                require('path').join(__dirname, 'crash_state.json'),
                JSON.stringify(state, null, 2)
            );
        } catch (err) {
            console.error('Failed to save application state:', err);
        }
    }
    
    logError(error) {
        const errorLog = {
            timestamp: new Date().toISOString(),
            error: error.toString(),
            stack: error.stack,
            memoryUsage: process.memoryUsage()
        };
        
        try {
            const fs = require('fs');
            const path = require('path');
            const logPath = path.join(__dirname, 'error.log');
            
            fs.appendFileSync(logPath, JSON.stringify(errorLog) + '\n');
        } catch (err) {
            console.error('Failed to log error:', err);
        }
    }
    
    attemptRestart() {
        this.restartAttempts++;
        console.log(`Attempting restart ${this.restartAttempts}/${this.maxRestartAttempts}`);
        
        // 这里实现重启逻辑
        // 具体实现取决于应用架构
    }
    
    triggerGarbageCollection() {
        if (global.gc) {
            global.gc();
            console.log('Garbage collection triggered');
        }
    }
    
    showCrashDialog() {
        // 显示崩溃对话框，让用户选择操作
        const { dialog } = require('electron');
        
        dialog.showErrorBox(
            'Application Crash',
            'Changlee has encountered multiple crashes. Please restart the application manually.'
        );
    }
}

module.exports = ErrorRecoveryManager;
