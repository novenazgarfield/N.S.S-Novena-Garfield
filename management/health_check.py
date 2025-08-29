#!/usr/bin/env python3
"""
🏥 系统健康检查脚本
==================

检查N.S.S-Novena-Garfield项目各系统健康状态
自动生成于: 2025-08-29T15:21:47.404340
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
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        # 检查CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        health_status["checks"]["cpu_usage"] = {
            "status": "ok" if cpu_usage < 80 else "warning",
            "value": cpu_usage,
            "unit": "%"
        }
        
        # 检查内存使用率
        memory = psutil.virtual_memory()
        health_status["checks"]["memory_usage"] = {
            "status": "ok" if memory.percent < 85 else "warning",
            "value": memory.percent,
            "unit": "%"
        }
        
        # 检查磁盘使用率
        disk = psutil.disk_usage(self.management_dir)
        disk_percent = (disk.used / disk.total) * 100
        health_status["checks"]["disk_usage"] = {
            "status": "ok" if disk_percent < 90 else "warning",
            "value": round(disk_percent, 2),
            "unit": "%"
        }
        
        # 检查关键目录
        critical_dirs = [
            self.project_root / "systems",
            self.project_root / "api",
            self.management_dir / "scripts"
        ]
        
        missing_dirs = [d for d in critical_dirs if not d.exists()]
        health_status["checks"]["critical_directories"] = {
            "status": "ok" if not missing_dirs else "error",
            "missing": [str(d) for d in missing_dirs]
        }
        
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
        status_emoji = {"healthy": "✅", "warning": "⚠️", "error": "❌"}
        overall_emoji = status_emoji.get(health_status["overall_status"], "❓")
        
        print(f"\n🏥 系统健康检查报告 - {overall_emoji} {health_status['overall_status'].upper()}")
        print(f"检查时间: {health_status['timestamp']}")
        print("\n详细检查结果:")
        
        for check_name, check_result in health_status["checks"].items():
            emoji = status_emoji.get(check_result["status"], "❓")
            print(f"  {emoji} {check_name.replace('_', ' ').title()}: {check_result['status']}")
            
            if "value" in check_result:
                print(f"      值: {check_result['value']}{check_result.get('unit', '')}")
            
            if "missing" in check_result and check_result["missing"]:
                print(f"      缺失: {', '.join(check_result['missing'])}")

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
    
    print(f"\n📄 详细报告已保存到: {report_file}")
    
    # 返回适当的退出码
    if health_status["overall_status"] == "error":
        sys.exit(1)
    elif health_status["overall_status"] == "warning":
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
