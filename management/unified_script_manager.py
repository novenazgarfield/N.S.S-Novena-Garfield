#!/usr/bin/env python3
"""
📋 统一脚本管理器
================

整合所有Management脚本功能，提供统一的管理接口
自动生成于: 2025-08-29T15:21:47.403595
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
        self.script_categories = {
        "cleanup": [
                "cleanup_and_import",
                "cleanup"
        ],
        "monitoring": [
                "code_quality_checker",
                "check_status"
        ],
        "utility": [
                "config_validator",
                "workspace_organizer",
                "online_rag_api",
                "smart_rag_server",
                "service_status"
        ],
        "startup": [
                "start_system",
                "unified_launcher",
                "start_ai_system",
                "start_services",
                "start_federation",
                "quick_start",
                "start_tunnels"
        ],
        "testing": [
                "test_api"
        ]
}
        
        # 运行状态
        self.running_processes = {}
        
        # 确保目录存在
        self.logs_dir.mkdir(exist_ok=True)
    
    def list_scripts(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """列出所有脚本"""
        if category:
            return {category: self.script_categories.get(category, [])}
        return self.script_categories
    
    def run_script(self, script_name: str, args: List[str] = None) -> bool:
        """运行指定脚本"""
        script_path = self._find_script(script_name)
        if not script_path:
            print(f"Script not found: {script_name}")
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
            print(f"Started script: {script_name} (PID: {process.pid})")
            
            return True
            
        except Exception as e:
            print(f"Failed to run script {script_name}: {e}")
            return False
    
    def _find_script(self, script_name: str) -> Optional[Path]:
        """查找脚本文件"""
        # 尝试不同的扩展名
        for ext in ['.py', '.sh', '.js']:
            script_path = self.scripts_dir / f"{script_name}{ext}"
            if script_path.exists():
                return script_path
        
        # 在子目录中查找
        for script_file in self.scripts_dir.glob(f"**/{script_name}.*"):
            return script_file
        
        return None
    
    def get_script_status(self) -> Dict[str, str]:
        """获取脚本运行状态"""
        status = {}
        
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
            print("\n" + "=" * 60)
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
                print("\n\n🛑 用户中断")
                break
    
    def _show_scripts(self):
        """显示所有脚本"""
        print("\n📜 可用脚本:")
        for category, scripts in self.script_categories.items():
            print(f"\n{category.upper()}:")
            for script in scripts:
                print(f"  - {script}")
    
    def _interactive_run_script(self):
        """交互式运行脚本"""
        script_name = input("请输入脚本名称: ").strip()
        if script_name:
            if self.run_script(script_name):
                print(f"✅ 脚本 {script_name} 已启动")
            else:
                print(f"❌ 脚本 {script_name} 启动失败")
    
    def _show_script_status(self):
        """显示脚本状态"""
        status = self.get_script_status()
        
        if not status:
            print("⚠️ 没有运行中的脚本")
            return
        
        print("\n📊 脚本状态:")
        for script_name, script_status in status.items():
            emoji = "🟢" if script_status == "running" else "🔴"
            print(f"  {emoji} {script_name}: {script_status}")

def main():
    """主函数"""
    manager = UnifiedScriptManager()
    manager.interactive_menu()

if __name__ == "__main__":
    main()
