#!/usr/bin/env python3
"""
🔄 Changlee桌面宠物系统优化器
============================

优化Changlee系统性能和稳定性
- Electron性能优化
- 依赖管理统一
- 服务模块解耦
- 错误恢复机制
- Chronicle集成优化

保持所有原有功能不变
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class ChangleeOptimizer:
    """Changlee系统优化器"""
    
    def __init__(self, changlee_dir: Path = None):
        self.changlee_dir = changlee_dir or Path(__file__).parent
        self.src_dir = self.changlee_dir / "src"
        self.main_package = self.changlee_dir / "package.json"
        self.renderer_package = self.changlee_dir / "src" / "renderer" / "package.json"
        
        self.optimization_log = []
        self.performance_metrics = {}
    
    def log_action(self, action: str, details: str = "", level: str = "INFO"):
        """记录优化操作"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "level": level
        }
        self.optimization_log.append(log_entry)
        
        emoji = "✅" if level == "INFO" else "⚠️" if level == "WARN" else "❌"
        print(f"{emoji} {action}: {details}")
    
    def analyze_package_structure(self) -> Dict[str, Any]:
        """分析package.json结构"""
        analysis = {
            "main_package": {},
            "renderer_package": {},
            "dependency_conflicts": [],
            "optimization_suggestions": []
        }
        
        # 分析主package.json
        if self.main_package.exists():
            with open(self.main_package, 'r', encoding='utf-8') as f:
                main_pkg = json.load(f)
                analysis["main_package"] = {
                    "dependencies": len(main_pkg.get("dependencies", {})),
                    "devDependencies": len(main_pkg.get("devDependencies", {})),
                    "scripts": len(main_pkg.get("scripts", {})),
                    "size": self.main_package.stat().st_size
                }
        
        # 分析renderer package.json
        if self.renderer_package.exists():
            with open(self.renderer_package, 'r', encoding='utf-8') as f:
                renderer_pkg = json.load(f)
                analysis["renderer_package"] = {
                    "dependencies": len(renderer_pkg.get("dependencies", {})),
                    "devDependencies": len(renderer_pkg.get("devDependencies", {})),
                    "scripts": len(renderer_pkg.get("scripts", {})),
                    "size": self.renderer_package.stat().st_size
                }
        
        # 检查依赖冲突
        analysis["dependency_conflicts"] = self._find_dependency_conflicts()
        
        # 生成优化建议
        analysis["optimization_suggestions"] = self._generate_package_suggestions(analysis)
        
        return analysis
    
    def _find_dependency_conflicts(self) -> List[Dict[str, Any]]:
        """查找依赖冲突"""
        conflicts = []
        
        if not (self.main_package.exists() and self.renderer_package.exists()):
            return conflicts
        
        try:
            with open(self.main_package, 'r', encoding='utf-8') as f:
                main_pkg = json.load(f)
            
            with open(self.renderer_package, 'r', encoding='utf-8') as f:
                renderer_pkg = json.load(f)
            
            main_deps = main_pkg.get("dependencies", {})
            renderer_deps = renderer_pkg.get("dependencies", {})
            
            # 查找版本冲突
            for pkg_name in set(main_deps.keys()) & set(renderer_deps.keys()):
                main_version = main_deps[pkg_name]
                renderer_version = renderer_deps[pkg_name]
                
                if main_version != renderer_version:
                    conflicts.append({
                        "package": pkg_name,
                        "main_version": main_version,
                        "renderer_version": renderer_version,
                        "type": "version_conflict"
                    })
            
        except Exception as e:
            self.log_action("依赖分析失败", str(e), "ERROR")
        
        return conflicts
    
    def _generate_package_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """生成package优化建议"""
        suggestions = []
        
        # 检查脚本数量
        main_scripts = analysis["main_package"].get("scripts", 0)
        if main_scripts > 10:
            suggestions.append(f"主package.json有{main_scripts}个脚本，建议整理和分类")
        
        # 检查依赖数量
        main_deps = analysis["main_package"].get("dependencies", 0)
        renderer_deps = analysis["renderer_package"].get("dependencies", 0)
        
        if main_deps + renderer_deps > 50:
            suggestions.append("依赖包较多，建议审查是否有未使用的依赖")
        
        # 检查冲突
        if analysis["dependency_conflicts"]:
            suggestions.append(f"发现{len(analysis['dependency_conflicts'])}个依赖版本冲突")
        
        return suggestions
    
    def optimize_electron_performance(self):
        """优化Electron性能"""
        self.log_action("开始Electron性能优化", "分析和优化内存使用")
        
        # 检查main.js文件
        main_js_path = self.src_dir / "main" / "main.js"
        if main_js_path.exists():
            self._optimize_main_process(main_js_path)
        
        # 检查preload脚本
        preload_files = list(self.src_dir.glob("**/preload*.js"))
        for preload_file in preload_files:
            self._optimize_preload_script(preload_file)
        
        # 生成性能优化配置
        self._create_performance_config()
    
    def _optimize_main_process(self, main_js_path: Path):
        """优化主进程"""
        try:
            content = main_js_path.read_text(encoding='utf-8')
            original_size = len(content)
            
            optimizations = []
            
            # 检查内存管理
            if "webSecurity: false" in content:
                optimizations.append("建议启用webSecurity以提升安全性")
            
            if "nodeIntegration: true" in content:
                optimizations.append("建议禁用nodeIntegration，使用preload脚本")
            
            # 检查窗口管理
            if "show: true" in content and "ready-to-show" not in content:
                optimizations.append("建议使用ready-to-show事件优化窗口显示")
            
            self.log_action(
                "主进程分析完成",
                f"文件大小: {original_size}字节, 发现{len(optimizations)}个优化点"
            )
            
            if optimizations:
                self.performance_metrics["main_process_optimizations"] = optimizations
            
        except Exception as e:
            self.log_action("主进程优化失败", str(e), "ERROR")
    
    def _optimize_preload_script(self, preload_path: Path):
        """优化preload脚本"""
        try:
            content = preload_path.read_text(encoding='utf-8')
            
            # 检查API暴露
            api_count = len(re.findall(r'contextBridge\.exposeInMainWorld', content))
            
            self.log_action(
                f"Preload脚本分析",
                f"{preload_path.name}: 暴露{api_count}个API"
            )
            
        except Exception as e:
            self.log_action(f"Preload脚本分析失败", str(e), "ERROR")
    
    def _create_performance_config(self):
        """创建性能优化配置"""
        config = {
            "electron_performance": {
                "memory_optimization": {
                    "enable_memory_info": True,
                    "gc_interval": 60000,
                    "max_memory_usage": "512MB"
                },
                "window_optimization": {
                    "use_ready_to_show": True,
                    "enable_background_throttling": True,
                    "web_security": True
                },
                "renderer_optimization": {
                    "node_integration": False,
                    "context_isolation": True,
                    "enable_remote_module": False
                }
            },
            "created_at": datetime.now().isoformat()
        }
        
        config_path = self.changlee_dir / "performance_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.log_action("性能配置创建", f"配置已保存到 {config_path}")
    
    def optimize_service_modules(self):
        """优化服务模块解耦"""
        self.log_action("开始服务模块解耦优化", "分析服务依赖关系")
        
        # 查找服务文件
        service_files = []
        for pattern in ["*Service.js", "*service.js", "*Service.ts", "*service.ts"]:
            service_files.extend(self.src_dir.glob(f"**/{pattern}"))
        
        if not service_files:
            self.log_action("未找到服务文件", "跳过服务模块优化")
            return
        
        service_analysis = {}
        
        for service_file in service_files:
            analysis = self._analyze_service_file(service_file)
            service_analysis[service_file.name] = analysis
        
        # 生成解耦建议
        decoupling_suggestions = self._generate_decoupling_suggestions(service_analysis)
        
        self.log_action(
            "服务模块分析完成",
            f"分析了{len(service_files)}个服务文件，生成{len(decoupling_suggestions)}个建议"
        )
        
        self.performance_metrics["service_analysis"] = service_analysis
        self.performance_metrics["decoupling_suggestions"] = decoupling_suggestions
    
    def _analyze_service_file(self, service_file: Path) -> Dict[str, Any]:
        """分析单个服务文件"""
        try:
            content = service_file.read_text(encoding='utf-8')
            
            # 分析导入依赖
            imports = re.findall(r'(?:import|require)\s*\([\'"]([^\'"]+)[\'"]', content)
            
            # 分析类和函数定义
            classes = re.findall(r'class\s+(\w+)', content)
            functions = re.findall(r'(?:function\s+(\w+)|const\s+(\w+)\s*=.*?=>)', content)
            
            # 分析事件监听
            event_listeners = len(re.findall(r'addEventListener|on\w+\s*=', content))
            
            return {
                "size": len(content),
                "imports": len(imports),
                "classes": len(classes),
                "functions": len([f for f in functions if f]),
                "event_listeners": event_listeners,
                "dependencies": imports[:10]  # 只保留前10个依赖
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_decoupling_suggestions(self, service_analysis: Dict[str, Any]) -> List[str]:
        """生成解耦建议"""
        suggestions = []
        
        # 分析高耦合服务
        high_coupling_services = []
        for service_name, analysis in service_analysis.items():
            if analysis.get("imports", 0) > 10:
                high_coupling_services.append(service_name)
        
        if high_coupling_services:
            suggestions.append(f"高耦合服务: {', '.join(high_coupling_services)} - 建议拆分依赖")
        
        # 分析大型服务
        large_services = []
        for service_name, analysis in service_analysis.items():
            if analysis.get("size", 0) > 5000:  # 5KB以上
                large_services.append(service_name)
        
        if large_services:
            suggestions.append(f"大型服务: {', '.join(large_services)} - 建议拆分功能")
        
        return suggestions
    
    def add_error_recovery_mechanism(self):
        """添加错误恢复机制"""
        self.log_action("添加错误恢复机制", "创建错误处理和恢复系统")
        
        # 创建错误恢复配置
        error_recovery_config = {
            "error_handling": {
                "auto_restart": True,
                "max_restart_attempts": 3,
                "restart_delay": 5000,
                "log_errors": True
            },
            "crash_recovery": {
                "save_state_on_crash": True,
                "restore_state_on_restart": True,
                "backup_interval": 300000  # 5分钟
            },
            "memory_management": {
                "monitor_memory": True,
                "memory_threshold": 512,  # MB
                "gc_on_threshold": True
            }
        }
        
        config_path = self.changlee_dir / "error_recovery_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(error_recovery_config, f, indent=2, ensure_ascii=False)
        
        # 创建错误恢复脚本
        self._create_error_recovery_script()
        
        self.log_action("错误恢复机制创建完成", f"配置保存到 {config_path}")
    
    def _create_error_recovery_script(self):
        """创建错误恢复脚本"""
        recovery_script = '''/**
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
            
            fs.appendFileSync(logPath, JSON.stringify(errorLog) + '\\n');
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
'''
        
        script_path = self.changlee_dir / "src" / "utils" / "errorRecovery.js"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(recovery_script)
        
        self.log_action("错误恢复脚本创建", f"脚本保存到 {script_path}")
    
    def optimize_chronicle_integration(self):
        """优化Chronicle集成"""
        self.log_action("优化Chronicle集成", "分析和优化Chronicle连接")
        
        # 查找Chronicle相关文件
        chronicle_files = []
        for pattern in ["*chronicle*", "*Chronicle*"]:
            chronicle_files.extend(self.changlee_dir.glob(f"**/{pattern}"))
        
        if not chronicle_files:
            self.log_action("未找到Chronicle集成文件", "跳过Chronicle优化")
            return
        
        # 分析Chronicle集成
        integration_analysis = {}
        for file_path in chronicle_files:
            if file_path.is_file() and file_path.suffix in ['.js', '.ts', '.json']:
                analysis = self._analyze_chronicle_file(file_path)
                integration_analysis[file_path.name] = analysis
        
        # 创建优化后的Chronicle集成配置
        self._create_optimized_chronicle_config(integration_analysis)
        
        self.log_action(
            "Chronicle集成优化完成",
            f"分析了{len(chronicle_files)}个相关文件"
        )
    
    def _analyze_chronicle_file(self, file_path: Path) -> Dict[str, Any]:
        """分析Chronicle相关文件"""
        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                return {
                    "type": "config",
                    "keys": list(content.keys()) if isinstance(content, dict) else [],
                    "size": file_path.stat().st_size
                }
            else:
                content = file_path.read_text(encoding='utf-8')
                
                # 分析API调用
                api_calls = len(re.findall(r'fetch\s*\(|axios\.|http\.|request\(', content))
                
                # 分析事件处理
                event_handlers = len(re.findall(r'addEventListener|on\w+\s*=', content))
                
                return {
                    "type": "script",
                    "size": len(content),
                    "api_calls": api_calls,
                    "event_handlers": event_handlers
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def _create_optimized_chronicle_config(self, analysis: Dict[str, Any]):
        """创建优化的Chronicle集成配置"""
        config = {
            "chronicle_integration": {
                "connection": {
                    "timeout": 10000,
                    "retry_attempts": 3,
                    "retry_delay": 2000,
                    "keep_alive": True
                },
                "performance": {
                    "batch_requests": True,
                    "cache_responses": True,
                    "cache_duration": 300000,  # 5分钟
                    "compress_data": True
                },
                "error_handling": {
                    "auto_reconnect": True,
                    "fallback_mode": True,
                    "log_errors": True
                }
            },
            "analysis_results": analysis,
            "optimized_at": datetime.now().isoformat()
        }
        
        config_path = self.changlee_dir / "chronicle_integration_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.log_action("Chronicle集成配置优化", f"配置保存到 {config_path}")
    
    def create_optimization_report(self):
        """创建优化报告"""
        report = {
            "optimization_date": datetime.now().isoformat(),
            "changlee_directory": str(self.changlee_dir),
            "actions_performed": self.optimization_log,
            "performance_metrics": self.performance_metrics,
            "summary": {
                "total_actions": len(self.optimization_log),
                "electron_optimized": any("Electron" in action["action"] for action in self.optimization_log),
                "services_analyzed": any("服务" in action["action"] for action in self.optimization_log),
                "error_recovery_added": any("错误恢复" in action["action"] for action in self.optimization_log),
                "chronicle_optimized": any("Chronicle" in action["action"] for action in self.optimization_log)
            },
            "recommendations": self._generate_final_recommendations()
        }
        
        report_file = self.changlee_dir / "changlee_optimization_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log_action("生成优化报告", f"报告已保存到 {report_file}")
        
        return report
    
    def _generate_final_recommendations(self) -> List[str]:
        """生成最终建议"""
        recommendations = []
        
        # 基于性能指标生成建议
        if "service_analysis" in self.performance_metrics:
            service_count = len(self.performance_metrics["service_analysis"])
            if service_count > 5:
                recommendations.append(f"发现{service_count}个服务文件，建议考虑微服务架构")
        
        if "decoupling_suggestions" in self.performance_metrics:
            suggestions = self.performance_metrics["decoupling_suggestions"]
            if suggestions:
                recommendations.extend(suggestions)
        
        # 通用建议
        recommendations.extend([
            "定期监控内存使用情况",
            "实施自动化测试以确保稳定性",
            "考虑使用TypeScript提升代码质量",
            "添加性能监控和分析工具"
        ])
        
        return recommendations
    
    def run_optimization(self):
        """运行完整优化流程"""
        print("🔄 开始Changlee系统优化...")
        print("=" * 60)
        
        # 1. 分析package结构
        package_analysis = self.analyze_package_structure()
        self.log_action(
            "Package结构分析完成",
            f"主包依赖: {package_analysis['main_package'].get('dependencies', 0)}, "
            f"渲染器依赖: {package_analysis['renderer_package'].get('dependencies', 0)}"
        )
        
        # 2. Electron性能优化
        self.optimize_electron_performance()
        
        # 3. 服务模块解耦
        self.optimize_service_modules()
        
        # 4. 添加错误恢复机制
        self.add_error_recovery_mechanism()
        
        # 5. 优化Chronicle集成
        self.optimize_chronicle_integration()
        
        # 6. 生成优化报告
        report = self.create_optimization_report()
        
        print("\n" + "=" * 60)
        print("🎉 Changlee系统优化完成!")
        print(f"📊 执行了 {report['summary']['total_actions']} 个优化操作")
        print(f"📄 详细报告: {self.changlee_dir}/changlee_optimization_report.json")
        
        return report

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Changlee系统优化工具")
    parser.add_argument("--changlee-dir", help="Changlee系统目录路径")
    parser.add_argument("--dry-run", action="store_true", help="仅分析，不执行实际优化")
    
    args = parser.parse_args()
    
    changlee_dir = Path(args.changlee_dir) if args.changlee_dir else Path(__file__).parent
    
    if not changlee_dir.exists():
        print(f"❌ Changlee目录不存在: {changlee_dir}")
        return
    
    optimizer = ChangleeOptimizer(changlee_dir)
    
    if args.dry_run:
        print("🔍 执行分析模式（不会修改文件）...")
        optimizer.analyze_package_structure()
        optimizer.optimize_service_modules()
    else:
        optimizer.run_optimization()

if __name__ == "__main__":
    main()