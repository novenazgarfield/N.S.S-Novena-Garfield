#!/usr/bin/env python3
"""
📋 Management项目管理系统自动化优化器 (简化版)
============================================

优化Management系统的自动化程度和运维效率
- 整合重复脚本功能
- 添加自动化部署流程
- 完善系统监控
- 统一日志管理
- 添加健康检查机制

保持所有原有功能不变
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class ManagementOptimizer:
    """Management系统优化器"""
    
    def __init__(self, management_dir: Path = None):
        self.management_dir = management_dir or Path(__file__).parent
        self.scripts_dir = self.management_dir / "scripts"
        self.logs_dir = self.management_dir / "logs"
        self.config_dir = self.management_dir / "config"
        
        self.optimization_log = []
        self.script_analysis = {}
        
        # 确保目录存在
        self.logs_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
    
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
    
    def analyze_script_redundancy(self) -> Dict[str, Any]:
        """分析脚本冗余"""
        self.log_action("开始脚本冗余分析", "扫描所有管理脚本")
        
        if not self.scripts_dir.exists():
            self.log_action("脚本目录不存在", str(self.scripts_dir), "WARN")
            return {}
        
        # 收集所有脚本文件
        script_files = []
        for pattern in ["*.py", "*.sh", "*.js", "*.bat"]:
            script_files.extend(self.scripts_dir.glob(f"**/{pattern}"))
        
        # 分析脚本功能
        script_functions = {}
        duplicate_groups = {}
        
        for script_file in script_files:
            analysis = self._analyze_script_file(script_file)
            script_functions[script_file.name] = analysis
            
            # 按功能分组
            function_type = analysis.get("function_type", "unknown")
            if function_type not in duplicate_groups:
                duplicate_groups[function_type] = []
            duplicate_groups[function_type].append(script_file.name)
        
        # 找出重复功能
        redundant_groups = {k: v for k, v in duplicate_groups.items() if len(v) > 1}
        
        analysis_result = {
            "total_scripts": len(script_files),
            "script_functions": script_functions,
            "duplicate_groups": duplicate_groups,
            "redundant_groups": redundant_groups,
            "redundancy_percentage": len(redundant_groups) / len(duplicate_groups) * 100 if duplicate_groups else 0
        }
        
        self.script_analysis = analysis_result
        
        self.log_action(
            "脚本冗余分析完成",
            f"总脚本: {len(script_files)}, 冗余组: {len(redundant_groups)}, "
            f"冗余率: {analysis_result['redundancy_percentage']:.1f}%"
        )
        
        return analysis_result
    
    def _analyze_script_file(self, script_file: Path) -> Dict[str, Any]:
        """分析单个脚本文件"""
        try:
            content = script_file.read_text(encoding='utf-8')
            
            # 确定脚本功能类型
            function_type = self._determine_function_type(script_file.name, content)
            
            # 分析脚本复杂度
            lines = content.splitlines()
            code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            
            return {
                "function_type": function_type,
                "size": len(content),
                "lines": len(lines),
                "code_lines": len(code_lines),
                "last_modified": datetime.fromtimestamp(script_file.stat().st_mtime).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _determine_function_type(self, filename: str, content: str) -> str:
        """确定脚本功能类型"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        if any(keyword in filename_lower for keyword in ["start", "launch", "run"]):
            return "startup"
        elif any(keyword in filename_lower for keyword in ["deploy", "deployment"]):
            return "deployment"
        elif any(keyword in filename_lower for keyword in ["monitor", "check", "health"]):
            return "monitoring"
        elif any(keyword in filename_lower for keyword in ["backup", "archive"]):
            return "backup"
        elif any(keyword in filename_lower for keyword in ["clean", "cleanup"]):
            return "cleanup"
        elif any(keyword in filename_lower for keyword in ["test", "testing"]):
            return "testing"
        else:
            return "utility"
    
    def create_unified_script_manager(self):
        """创建统一脚本管理器"""
        self.log_action("创建统一脚本管理器", "整合所有管理脚本功能")
        
        # 生成脚本分类
        script_categories = self._generate_script_categories()
        
        unified_manager = f'''#!/usr/bin/env python3
"""
📋 统一脚本管理器
================

整合所有Management脚本功能，提供统一的管理接口
自动生成于: {datetime.now().isoformat()}
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class UnifiedScriptManager:
    """统一脚本管理器"""
    
    def __init__(self):
        self.management_dir = Path(__file__).parent
        self.scripts_dir = self.management_dir / "scripts"
        self.logs_dir = self.management_dir / "logs"
        
        # 脚本分类
        self.script_categories = {json.dumps(script_categories, indent=8)}
        
        # 运行状态
        self.running_processes = {{}}
        
        # 确保目录存在
        self.logs_dir.mkdir(exist_ok=True)
    
    def list_scripts(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """列出所有脚本"""
        if category:
            return {{category: self.script_categories.get(category, [])}}
        return self.script_categories
    
    def run_script(self, script_name: str, args: List[str] = None) -> bool:
        """运行指定脚本"""
        script_path = self._find_script(script_name)
        if not script_path:
            print(f"Script not found: {{script_name}}")
            return False
        
        try:
            cmd = [sys.executable if script_path.suffix == '.py' else 'bash', str(script_path)]
            if args:
                cmd.extend(args)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=script_path.parent
            )
            
            self.running_processes[script_name] = process
            print(f"Started script: {{script_name}} (PID: {{process.pid}})")
            
            return True
            
        except Exception as e:
            print(f"Failed to run script {{script_name}}: {{e}}")
            return False
    
    def _find_script(self, script_name: str) -> Optional[Path]:
        """查找脚本文件"""
        # 尝试不同的扩展名
        for ext in ['.py', '.sh', '.js']:
            script_path = self.scripts_dir / f"{{script_name}}{{ext}}"
            if script_path.exists():
                return script_path
        
        # 在子目录中查找
        for script_file in self.scripts_dir.glob(f"**/{{script_name}}.*"):
            return script_file
        
        return None
    
    def get_script_status(self) -> Dict[str, str]:
        """获取脚本运行状态"""
        status = {{}}
        
        for script_name, process in list(self.running_processes.items()):
            if process.poll() is None:
                status[script_name] = "running"
            else:
                status[script_name] = "stopped"
                del self.running_processes[script_name]
        
        return status
    
    def interactive_menu(self):
        """交互式菜单"""
        while True:
            print("\\n" + "=" * 60)
            print("📋 统一脚本管理器")
            print("=" * 60)
            print("1. 列出所有脚本")
            print("2. 运行脚本")
            print("3. 查看脚本状态")
            print("0. 退出")
            print("-" * 60)
            
            try:
                choice = input("请选择操作 (0-3): ").strip()
                
                if choice == "0":
                    print("👋 再见!")
                    break
                elif choice == "1":
                    self._show_scripts()
                elif choice == "2":
                    self._interactive_run_script()
                elif choice == "3":
                    self._show_script_status()
                else:
                    print("❌ 无效选择，请重试")
                    
            except KeyboardInterrupt:
                print("\\n\\n🛑 用户中断")
                break
    
    def _show_scripts(self):
        """显示所有脚本"""
        print("\\n📜 可用脚本:")
        for category, scripts in self.script_categories.items():
            print(f"\\n{{category.upper()}}:")
            for script in scripts:
                print(f"  - {{script}}")
    
    def _interactive_run_script(self):
        """交互式运行脚本"""
        script_name = input("请输入脚本名称: ").strip()
        if script_name:
            if self.run_script(script_name):
                print(f"✅ 脚本 {{script_name}} 已启动")
            else:
                print(f"❌ 脚本 {{script_name}} 启动失败")
    
    def _show_script_status(self):
        """显示脚本状态"""
        status = self.get_script_status()
        
        if not status:
            print("⚠️ 没有运行中的脚本")
            return
        
        print("\\n📊 脚本状态:")
        for script_name, script_status in status.items():
            emoji = "🟢" if script_status == "running" else "🔴"
            print(f"  {{emoji}} {{script_name}}: {{script_status}}")

def main():
    """主函数"""
    manager = UnifiedScriptManager()
    manager.interactive_menu()

if __name__ == "__main__":
    main()
'''
        
        manager_path = self.management_dir / "unified_script_manager.py"
        with open(manager_path, 'w', encoding='utf-8') as f:
            f.write(unified_manager)
        
        # 设置执行权限
        os.chmod(manager_path, 0o755)
        
        self.log_action("统一脚本管理器创建完成", f"管理器保存到 {manager_path}")
    
    def _generate_script_categories(self) -> Dict[str, List[str]]:
        """生成脚本分类"""
        categories = {}
        
        if hasattr(self, 'script_analysis') and 'script_functions' in self.script_analysis:
            for script_name, analysis in self.script_analysis['script_functions'].items():
                function_type = analysis.get('function_type', 'utility')
                
                if function_type not in categories:
                    categories[function_type] = []
                
                # 移除扩展名
                script_base_name = Path(script_name).stem
                categories[function_type].append(script_base_name)
        
        return categories
    
    def create_automated_deployment_config(self):
        """创建自动化部署配置"""
        self.log_action("创建自动化部署配置", "设置CI/CD流程配置")
        
        deployment_config = {
            "deployment": {
                "environments": {
                    "development": {
                        "auto_deploy": True,
                        "branch": "develop",
                        "health_check": True
                    },
                    "production": {
                        "auto_deploy": False,
                        "branch": "main",
                        "health_check": True,
                        "approval_required": True
                    }
                },
                "steps": [
                    "pre_deployment_checks",
                    "backup_current_version",
                    "deploy_new_version",
                    "run_health_checks"
                ]
            }
        }
        
        config_path = self.config_dir / "deployment_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(deployment_config, f, indent=2, ensure_ascii=False)
        
        self.log_action("自动化部署配置创建完成", f"配置保存到 {config_path}")
    
    def create_monitoring_config(self):
        """创建监控配置"""
        self.log_action("创建系统监控配置", "设置监控和告警配置")
        
        monitoring_config = {
            "monitoring": {
                "enabled": True,
                "interval": 60,
                "metrics": {
                    "cpu_usage": True,
                    "memory_usage": True,
                    "disk_usage": True
                },
                "alerts": {
                    "cpu_threshold": 80,
                    "memory_threshold": 85,
                    "disk_threshold": 90
                }
            }
        }
        
        config_path = self.config_dir / "monitoring_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(monitoring_config, f, indent=2, ensure_ascii=False)
        
        self.log_action("系统监控配置创建完成", f"配置保存到 {config_path}")
    
    def create_logging_config(self):
        """创建日志配置"""
        self.log_action("创建统一日志配置", "设置集中化日志管理")
        
        logging_config = {
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "handlers": {
                    "console": True,
                    "file": {
                        "enabled": True,
                        "filename": "logs/application.log",
                        "max_size": "10MB",
                        "backup_count": 5
                    }
                },
                "retention_days": 30
            }
        }
        
        config_path = self.config_dir / "logging_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(logging_config, f, indent=2, ensure_ascii=False)
        
        self.log_action("统一日志配置创建完成", f"配置保存到 {config_path}")
    
    def create_health_check_script(self):
        """创建健康检查脚本"""
        self.log_action("创建健康检查脚本", "设置系统健康监控")
        
        health_check_script = f'''#!/usr/bin/env python3
"""
🏥 系统健康检查脚本
==================

检查N.S.S-Novena-Garfield项目各系统健康状态
自动生成于: {datetime.now().isoformat()}
"""

import os
import sys
import json
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class HealthChecker:
    """系统健康检查器"""
    
    def __init__(self):
        self.management_dir = Path(__file__).parent
        self.project_root = self.management_dir.parent
        
    def check_system_health(self) -> Dict[str, Any]:
        """检查系统健康状态"""
        health_status = {{
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {{}}
        }}
        
        # 检查CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        health_status["checks"]["cpu_usage"] = {{
            "status": "ok" if cpu_usage < 80 else "warning",
            "value": cpu_usage,
            "unit": "%"
        }}
        
        # 检查内存使用率
        memory = psutil.virtual_memory()
        health_status["checks"]["memory_usage"] = {{
            "status": "ok" if memory.percent < 85 else "warning",
            "value": memory.percent,
            "unit": "%"
        }}
        
        # 检查磁盘使用率
        disk = psutil.disk_usage(self.management_dir)
        disk_percent = (disk.used / disk.total) * 100
        health_status["checks"]["disk_usage"] = {{
            "status": "ok" if disk_percent < 90 else "warning",
            "value": round(disk_percent, 2),
            "unit": "%"
        }}
        
        # 检查关键目录
        critical_dirs = [
            self.project_root / "systems",
            self.project_root / "api",
            self.management_dir / "scripts"
        ]
        
        missing_dirs = [d for d in critical_dirs if not d.exists()]
        health_status["checks"]["critical_directories"] = {{
            "status": "ok" if not missing_dirs else "error",
            "missing": [str(d) for d in missing_dirs]
        }}
        
        # 确定总体状态
        error_checks = [check for check in health_status["checks"].values() if check["status"] == "error"]
        warning_checks = [check for check in health_status["checks"].values() if check["status"] == "warning"]
        
        if error_checks:
            health_status["overall_status"] = "error"
        elif warning_checks:
            health_status["overall_status"] = "warning"
        
        return health_status
    
    def print_health_report(self, health_status: Dict[str, Any]):
        """打印健康检查报告"""
        status_emoji = {{"healthy": "✅", "warning": "⚠️", "error": "❌"}}
        overall_emoji = status_emoji.get(health_status["overall_status"], "❓")
        
        print(f"\\n🏥 系统健康检查报告 - {{overall_emoji}} {{health_status['overall_status'].upper()}}")
        print(f"检查时间: {{health_status['timestamp']}}")
        print("\\n详细检查结果:")
        
        for check_name, check_result in health_status["checks"].items():
            emoji = status_emoji.get(check_result["status"], "❓")
            print(f"  {{emoji}} {{check_name.replace('_', ' ').title()}}: {{check_result['status']}}")
            
            if "value" in check_result:
                print(f"      值: {{check_result['value']}}{{check_result.get('unit', '')}}")
            
            if "missing" in check_result and check_result["missing"]:
                print(f"      缺失: {{', '.join(check_result['missing'])}}")

def main():
    """主函数"""
    checker = HealthChecker()
    health_status = checker.check_system_health()
    
    # 打印报告
    checker.print_health_report(health_status)
    
    # 保存报告
    report_file = Path(__file__).parent / "logs" / "health_check.json"
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(health_status, f, indent=2, ensure_ascii=False)
    
    print(f"\\n📄 详细报告已保存到: {{report_file}}")
    
    # 返回适当的退出码
    if health_status["overall_status"] == "error":
        sys.exit(1)
    elif health_status["overall_status"] == "warning":
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
'''
        
        script_path = self.management_dir / "health_check.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(health_check_script)
        
        # 设置执行权限
        os.chmod(script_path, 0o755)
        
        self.log_action("健康检查脚本创建完成", f"脚本保存到 {script_path}")
    
    def create_optimization_report(self):
        """创建优化报告"""
        report = {
            "optimization_date": datetime.now().isoformat(),
            "management_directory": str(self.management_dir),
            "actions_performed": self.optimization_log,
            "script_analysis": self.script_analysis,
            "summary": {
                "total_actions": len(self.optimization_log),
                "scripts_analyzed": self.script_analysis.get("total_scripts", 0),
                "redundancy_percentage": self.script_analysis.get("redundancy_percentage", 0),
                "unified_manager_created": any("统一脚本管理器" in action["action"] for action in self.optimization_log),
                "deployment_config_created": any("自动化部署" in action["action"] for action in self.optimization_log),
                "monitoring_config_created": any("系统监控" in action["action"] for action in self.optimization_log),
                "logging_config_created": any("日志配置" in action["action"] for action in self.optimization_log),
                "health_check_created": any("健康检查" in action["action"] for action in self.optimization_log)
            },
            "recommendations": [
                "定期运行健康检查脚本监控系统状态",
                "使用统一脚本管理器简化运维操作",
                "实施自动化部署提高发布效率",
                "建立完善的日志分析机制",
                "定期清理和归档旧数据"
            ]
        }
        
        report_file = self.management_dir / "management_optimization_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log_action("生成优化报告", f"报告已保存到 {report_file}")
        
        return report
    
    def run_optimization(self):
        """运行完整优化流程"""
        print("📋 开始Management系统自动化优化...")
        print("=" * 70)
        
        # 1. 分析脚本冗余
        self.analyze_script_redundancy()
        
        # 2. 创建统一脚本管理器
        self.create_unified_script_manager()
        
        # 3. 创建自动化部署配置
        self.create_automated_deployment_config()
        
        # 4. 创建系统监控配置
        self.create_monitoring_config()
        
        # 5. 创建统一日志配置
        self.create_logging_config()
        
        # 6. 创建健康检查脚本
        self.create_health_check_script()
        
        # 7. 生成优化报告
        report = self.create_optimization_report()
        
        print("\n" + "=" * 70)
        print("🎉 Management系统自动化优化完成!")
        print(f"📊 执行了 {report['summary']['total_actions']} 个优化操作")
        print(f"📄 详细报告: {self.management_dir}/management_optimization_report.json")
        
        return report

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Management系统自动化优化工具")
    parser.add_argument("--management-dir", help="Management系统目录路径")
    parser.add_argument("--dry-run", action="store_true", help="仅分析，不执行实际优化")
    
    args = parser.parse_args()
    
    management_dir = Path(args.management_dir) if args.management_dir else Path(__file__).parent
    
    if not management_dir.exists():
        print(f"❌ Management目录不存在: {management_dir}")
        return
    
    optimizer = ManagementOptimizer(management_dir)
    
    if args.dry_run:
        print("🔍 执行分析模式（不会修改文件）...")
        optimizer.analyze_script_redundancy()
    else:
        optimizer.run_optimization()

if __name__ == "__main__":
    main()