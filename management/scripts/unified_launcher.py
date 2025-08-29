#!/usr/bin/env python3
"""
🚀 N.S.S-Novena-Garfield 统一启动器
==================================

第一阶段优化后的统一系统启动器
- RAG系统 (统一入口)
- API管理 (统一管理器)
- Nexus控制面板 (优化后)
- 其他核心系统

保持所有原有功能，提供统一的启动体验
"""

import os
import sys
import subprocess
import threading
import time
import signal
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import webbrowser
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

class SystemLauncher:
    """系统启动器"""
    
    def __init__(self):
        self.systems = {
            "rag": {
                "name": "🧠 RAG智能系统",
                "path": "systems/rag-system",
                "script": "unified_main.py",
                "port": 8501,
                "type": "streamlit",
                "description": "统一的RAG智能问答系统"
            },
            "api": {
                "name": "🌐 API管理系统", 
                "path": "api",
                "script": "unified_api_manager.py",
                "port": 8000,
                "type": "fastapi",
                "description": "统一的API管理服务"
            },
            "nexus": {
                "name": "🎯 Nexus控制面板",
                "path": "systems/nexus",
                "script": "index.html",
                "port": 8080,
                "type": "static",
                "description": "优化后的中央控制面板"
            },
            "chronicle": {
                "name": "📚 Chronicle编年史",
                "path": "systems/chronicle",
                "script": "chronicle.js",
                "port": 3000,
                "type": "node",
                "description": "ReAct智能代理系统"
            },
            "changlee": {
                "name": "🔄 Changlee桌面宠物",
                "path": "systems/Changlee",
                "script": "main.js",
                "port": None,
                "type": "electron",
                "description": "桌面宠物音乐系统"
            }
        }
        
        self.running_processes = {}
        self.status_log = []
    
    def log_status(self, system: str, status: str, details: str = ""):
        """记录系统状态"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "system": system,
            "status": status,
            "details": details
        }
        self.status_log.append(log_entry)
        print(f"[{system.upper()}] {status}: {details}")
    
    def check_system_requirements(self, system_key: str) -> bool:
        """检查系统运行要求"""
        system = self.systems[system_key]
        system_path = PROJECT_ROOT / system["path"]
        script_path = system_path / system["script"]
        
        if not system_path.exists():
            self.log_status(system_key, "❌ 错误", f"系统目录不存在: {system_path}")
            return False
        
        if not script_path.exists():
            self.log_status(system_key, "❌ 错误", f"启动脚本不存在: {script_path}")
            return False
        
        # 检查端口是否被占用
        if system["port"] and self._is_port_in_use(system["port"]):
            self.log_status(system_key, "⚠️ 警告", f"端口 {system['port']} 已被占用")
            return False
        
        return True
    
    def _is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    def start_system(self, system_key: str) -> bool:
        """启动单个系统"""
        if system_key not in self.systems:
            self.log_status(system_key, "❌ 错误", "未知的系统")
            return False
        
        system = self.systems[system_key]
        
        # 检查系统要求
        if not self.check_system_requirements(system_key):
            return False
        
        system_path = PROJECT_ROOT / system["path"]
        
        try:
            if system["type"] == "streamlit":
                cmd = [
                    sys.executable, "-m", "streamlit", "run",
                    system["script"],
                    "--server.port", str(system["port"]),
                    "--server.address", "0.0.0.0",
                    "--server.headless", "true",
                    "--browser.gatherUsageStats", "false"
                ]
                
            elif system["type"] == "fastapi":
                cmd = [sys.executable, system["script"], "--host", "0.0.0.0", "--port", str(system["port"])]
                
            elif system["type"] == "node":
                cmd = ["node", system["script"]]
                
            elif system["type"] == "electron":
                cmd = ["npm", "start"]
                
            elif system["type"] == "static":
                # 启动简单的HTTP服务器
                cmd = [sys.executable, "-m", "http.server", str(system["port"])]
            
            else:
                self.log_status(system_key, "❌ 错误", f"不支持的系统类型: {system['type']}")
                return False
            
            # 启动进程
            process = subprocess.Popen(
                cmd,
                cwd=system_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.running_processes[system_key] = process
            self.log_status(system_key, "✅ 启动", f"PID: {process.pid}, 端口: {system['port']}")
            
            # 等待一下确保启动成功
            time.sleep(2)
            
            if process.poll() is None:  # 进程仍在运行
                if system["port"]:
                    url = f"http://localhost:{system['port']}"
                    self.log_status(system_key, "🌐 就绪", f"访问地址: {url}")
                return True
            else:
                self.log_status(system_key, "❌ 失败", "进程意外退出")
                return False
                
        except Exception as e:
            self.log_status(system_key, "❌ 异常", str(e))
            return False
    
    def stop_system(self, system_key: str) -> bool:
        """停止单个系统"""
        if system_key not in self.running_processes:
            self.log_status(system_key, "⚠️ 警告", "系统未运行")
            return False
        
        process = self.running_processes[system_key]
        
        try:
            process.terminate()
            process.wait(timeout=10)
            del self.running_processes[system_key]
            self.log_status(system_key, "🛑 停止", "系统已关闭")
            return True
            
        except subprocess.TimeoutExpired:
            process.kill()
            del self.running_processes[system_key]
            self.log_status(system_key, "💀 强制停止", "系统已强制关闭")
            return True
            
        except Exception as e:
            self.log_status(system_key, "❌ 停止失败", str(e))
            return False
    
    def start_all_systems(self):
        """启动所有系统"""
        print("🚀 启动所有系统...")
        print("=" * 60)
        
        success_count = 0
        
        for system_key in self.systems:
            if self.start_system(system_key):
                success_count += 1
            time.sleep(1)  # 避免端口冲突
        
        print("\n" + "=" * 60)
        print(f"✅ 成功启动 {success_count}/{len(self.systems)} 个系统")
        
        if success_count > 0:
            self._show_access_info()
    
    def _show_access_info(self):
        """显示访问信息"""
        print("\n🌐 系统访问地址:")
        print("-" * 40)
        
        for system_key, process in self.running_processes.items():
            system = self.systems[system_key]
            if system["port"]:
                url = f"http://localhost:{system['port']}"
                print(f"{system['name']}: {url}")
        
        print("\n💡 提示: 按 Ctrl+C 停止所有系统")
    
    def stop_all_systems(self):
        """停止所有系统"""
        print("\n🛑 停止所有系统...")
        
        for system_key in list(self.running_processes.keys()):
            self.stop_system(system_key)
    
    def show_status(self):
        """显示系统状态"""
        print("📊 系统状态:")
        print("=" * 60)
        
        for system_key, system in self.systems.items():
            status = "🟢 运行中" if system_key in self.running_processes else "🔴 未运行"
            port_info = f":{system['port']}" if system["port"] else ""
            print(f"{system['name']:<25} {status} {port_info}")
            print(f"   📝 {system['description']}")
            print()
    
    def interactive_menu(self):
        """交互式菜单"""
        while True:
            print("\n" + "=" * 60)
            print("🎯 N.S.S-Novena-Garfield 统一启动器")
            print("=" * 60)
            print("1. 启动所有系统")
            print("2. 启动单个系统")
            print("3. 停止单个系统")
            print("4. 显示系统状态")
            print("5. 停止所有系统")
            print("0. 退出")
            print("-" * 60)
            
            try:
                choice = input("请选择操作 (0-5): ").strip()
                
                if choice == "0":
                    self.stop_all_systems()
                    print("👋 再见!")
                    break
                    
                elif choice == "1":
                    self.start_all_systems()
                    
                elif choice == "2":
                    self._interactive_start_system()
                    
                elif choice == "3":
                    self._interactive_stop_system()
                    
                elif choice == "4":
                    self.show_status()
                    
                elif choice == "5":
                    self.stop_all_systems()
                    
                else:
                    print("❌ 无效选择，请重试")
                    
            except KeyboardInterrupt:
                print("\n\n🛑 用户中断")
                self.stop_all_systems()
                break
            except Exception as e:
                print(f"❌ 操作失败: {e}")
    
    def _interactive_start_system(self):
        """交互式启动单个系统"""
        print("\n可用系统:")
        for i, (key, system) in enumerate(self.systems.items(), 1):
            status = "🟢" if key in self.running_processes else "🔴"
            print(f"{i}. {status} {system['name']}")
        
        try:
            choice = int(input("选择要启动的系统 (1-{}): ".format(len(self.systems))))
            if 1 <= choice <= len(self.systems):
                system_key = list(self.systems.keys())[choice - 1]
                self.start_system(system_key)
            else:
                print("❌ 无效选择")
        except ValueError:
            print("❌ 请输入有效数字")
    
    def _interactive_stop_system(self):
        """交互式停止单个系统"""
        if not self.running_processes:
            print("⚠️ 没有运行中的系统")
            return
        
        print("\n运行中的系统:")
        running_systems = list(self.running_processes.keys())
        for i, key in enumerate(running_systems, 1):
            system = self.systems[key]
            print(f"{i}. {system['name']}")
        
        try:
            choice = int(input("选择要停止的系统 (1-{}): ".format(len(running_systems))))
            if 1 <= choice <= len(running_systems):
                system_key = running_systems[choice - 1]
                self.stop_system(system_key)
            else:
                print("❌ 无效选择")
        except ValueError:
            print("❌ 请输入有效数字")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="N.S.S-Novena-Garfield 统一启动器")
    parser.add_argument("--system", "-s", help="启动指定系统")
    parser.add_argument("--all", "-a", action="store_true", help="启动所有系统")
    parser.add_argument("--status", action="store_true", help="显示系统状态")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互式模式")
    
    args = parser.parse_args()
    
    launcher = SystemLauncher()
    
    # 设置信号处理
    def signal_handler(sig, frame):
        print("\n\n🛑 接收到中断信号，正在关闭所有系统...")
        launcher.stop_all_systems()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.status:
            launcher.show_status()
            
        elif args.system:
            launcher.start_system(args.system)
            
        elif args.all:
            launcher.start_all_systems()
            # 保持运行直到用户中断
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                
        elif args.interactive:
            launcher.interactive_menu()
            
        else:
            # 默认启动交互式模式
            launcher.interactive_menu()
            
    except Exception as e:
        print(f"❌ 启动器异常: {e}")
    finally:
        launcher.stop_all_systems()

if __name__ == "__main__":
    main()