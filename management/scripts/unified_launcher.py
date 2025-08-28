#!/usr/bin/env python3
"""
🚀 N.S.S-Novena-Garfield 统一启动器
集成所有系统的一键启动功能，支持Docker和本地模式
"""

import os
import sys
import json
import time
import signal
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import webbrowser
from datetime import datetime

class UnifiedLauncher:
    def __init__(self, workspace_path="."):
        self.workspace_path = Path(workspace_path).resolve()
        self.processes = {}
        self.running = True
        self.docker_mode = False
        
        # 系统配置
        self.systems = {
            'api-manager': {
                'name': 'API管理器',
                'path': 'api',
                'entry': 'api_manager.py',
                'port': int(os.getenv('API_MANAGER_PORT', 8000)),
                'type': 'python',
                'required': True
            },
            'rag-system': {
                'name': 'RAG智能系统',
                'path': 'systems/rag-system',
                'entry': 'main.py',
                'port': int(os.getenv('RAG_PORT', 8501)),
                'type': 'streamlit',
                'required': True
            },
            'changlee': {
                'name': 'Changlee音乐播放器',
                'path': 'systems/Changlee',
                'entry': 'easy_start.js',
                'port': int(os.getenv('CHANGLEE_WEB_PORT', 8082)),
                'type': 'node',
                'required': False
            },
            'chronicle': {
                'name': 'Chronicle时间管理',
                'path': 'systems/chronicle',
                'entry': 'chronicle.js',
                'port': int(os.getenv('CHRONICLE_PORT', 3000)),
                'type': 'node',
                'required': False
            },
            'nexus': {
                'name': 'Nexus集成管理',
                'path': 'systems/nexus',
                'entry': 'main.js',
                'port': int(os.getenv('NEXUS_PORT', 8080)),
                'type': 'node',
                'required': False
            },
            'bovine-insight': {
                'name': 'Bovine洞察系统',
                'path': 'systems/bovine-insight',
                'entry': 'bovine.py',
                'port': int(os.getenv('BOVINE_PORT', 8084)),
                'type': 'python',
                'required': False
            },
            'genome-nebula': {
                'name': 'Genome基因分析',
                'path': 'systems/genome-nebula',
                'entry': 'genome.py',
                'port': int(os.getenv('GENOME_PORT', 8085)),
                'type': 'python',
                'required': False
            },
            'kinetic-scope': {
                'name': 'Kinetic分子动力学',
                'path': 'systems/kinetic-scope',
                'entry': 'kinetic.py',
                'port': int(os.getenv('KINETIC_PORT', 8086)),
                'type': 'python',
                'required': False
            }
        }
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理退出信号"""
        print(f"\n🛑 收到退出信号 ({signum})，正在关闭所有服务...")
        self.running = False
        self.stop_all_services()
        sys.exit(0)
    
    def log(self, message: str, level: str = "INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def check_dependencies(self) -> bool:
        """检查依赖项"""
        self.log("🔍 检查系统依赖...")
        
        dependencies = {
            'python3': 'Python 3.x',
            'node': 'Node.js',
            'npm': 'NPM'
        }
        
        missing = []
        for cmd, name in dependencies.items():
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log(f"✅ {name}: {result.stdout.strip().split()[0]}")
                else:
                    missing.append(name)
            except Exception:
                missing.append(name)
        
        if missing:
            self.log(f"❌ 缺少依赖: {', '.join(missing)}", "ERROR")
            return False
        
        return True
    
    def check_docker(self) -> bool:
        """检查Docker是否可用"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.log(f"🐳 Docker可用: {result.stdout.strip()}")
                
                # 检查Docker Compose
                result = subprocess.run(['docker', 'compose', 'version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log(f"🐳 Docker Compose可用: {result.stdout.strip()}")
                    return True
                else:
                    self.log("⚠️ Docker Compose不可用", "WARNING")
                    return False
            else:
                return False
        except Exception:
            return False
    
    def install_dependencies(self, system_id: str) -> bool:
        """安装系统依赖"""
        system = self.systems[system_id]
        system_path = self.workspace_path / system['path']
        
        if not system_path.exists():
            self.log(f"❌ 系统路径不存在: {system_path}", "ERROR")
            return False
        
        self.log(f"📦 安装 {system['name']} 依赖...")
        
        try:
            if system['type'] in ['node', 'streamlit']:
                # 检查package.json
                package_json = system_path / 'package.json'
                if package_json.exists():
                    result = subprocess.run(['npm', 'install'], 
                                          cwd=system_path, 
                                          capture_output=True, text=True, timeout=120)
                    if result.returncode != 0:
                        self.log(f"❌ NPM安装失败: {result.stderr}", "ERROR")
                        return False
            
            elif system['type'] == 'python':
                # 检查requirements.txt
                requirements = system_path / 'requirements.txt'
                if requirements.exists():
                    result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                                          cwd=system_path, 
                                          capture_output=True, text=True, timeout=180)
                    if result.returncode != 0:
                        self.log(f"❌ Python依赖安装失败: {result.stderr}", "ERROR")
                        return False
            
            return True
            
        except Exception as e:
            self.log(f"❌ 依赖安装异常: {e}", "ERROR")
            return False
    
    def start_system_local(self, system_id: str) -> Optional[subprocess.Popen]:
        """本地启动系统"""
        system = self.systems[system_id]
        system_path = self.workspace_path / system['path']
        entry_file = system_path / system['entry']
        
        if not entry_file.exists():
            self.log(f"❌ 入口文件不存在: {entry_file}", "ERROR")
            return None
        
        self.log(f"🚀 启动 {system['name']} (本地模式)")
        
        try:
            env = os.environ.copy()
            env['PORT'] = str(system['port'])
            
            if system['type'] == 'python':
                cmd = [sys.executable, system['entry']]
            elif system['type'] == 'streamlit':
                cmd = ['streamlit', 'run', system['entry'], '--server.port', str(system['port']), '--server.address', '0.0.0.0']
            elif system['type'] == 'node':
                cmd = ['node', system['entry']]
            else:
                self.log(f"❌ 未知系统类型: {system['type']}", "ERROR")
                return None
            
            process = subprocess.Popen(
                cmd,
                cwd=system_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return process
            
        except Exception as e:
            self.log(f"❌ 启动失败 {system['name']}: {e}", "ERROR")
            return None
    
    def start_docker_compose(self, services: List[str] = None):
        """启动Docker Compose服务"""
        self.log("🐳 启动Docker Compose服务...")
        
        compose_file = self.workspace_path / 'management/deployment/docker-compose.yml'
        if not compose_file.exists():
            self.log("❌ docker-compose.yml不存在", "ERROR")
            return False
        
        try:
            cmd = ['docker', 'compose', '-f', 'management/deployment/docker-compose.yml', 'up', '-d']
            if services:
                cmd.extend(services)
            
            result = subprocess.run(cmd, cwd=self.workspace_path, 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log("✅ Docker Compose服务启动成功")
                return True
            else:
                self.log(f"❌ Docker Compose启动失败: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Docker Compose启动异常: {e}", "ERROR")
            return False
    
    def stop_docker_compose(self):
        """停止Docker Compose服务"""
        self.log("🛑 停止Docker Compose服务...")
        
        try:
            result = subprocess.run(['docker', 'compose', '-f', 'management/deployment/docker-compose.yml', 'down'], 
                                  cwd=self.workspace_path, 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log("✅ Docker Compose服务已停止")
            else:
                self.log(f"⚠️ Docker Compose停止警告: {result.stderr}", "WARNING")
                
        except Exception as e:
            self.log(f"❌ Docker Compose停止异常: {e}", "ERROR")
    
    def monitor_process(self, system_id: str, process: subprocess.Popen):
        """监控进程输出"""
        system = self.systems[system_id]
        
        def read_output(stream, prefix):
            for line in iter(stream.readline, ''):
                if line.strip():
                    self.log(f"[{system['name']}] {line.strip()}")
        
        # 启动输出监控线程
        threading.Thread(target=read_output, args=(process.stdout, "OUT"), daemon=True).start()
        threading.Thread(target=read_output, args=(process.stderr, "ERR"), daemon=True).start()
    
    def wait_for_service(self, port: int, timeout: int = 30) -> bool:
        """等待服务启动"""
        import socket
        
        for i in range(timeout):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', port))
                    if result == 0:
                        return True
            except Exception:
                pass
            time.sleep(1)
        
        return False
    
    def start_services(self, systems: List[str] = None, docker: bool = False):
        """启动服务"""
        if docker and self.check_docker():
            self.docker_mode = True
            return self.start_docker_compose(systems)
        
        # 本地模式启动
        if not self.check_dependencies():
            return False
        
        systems_to_start = systems or list(self.systems.keys())
        
        # 首先启动必需的系统
        required_systems = [s for s in systems_to_start if self.systems[s]['required']]
        optional_systems = [s for s in systems_to_start if not self.systems[s]['required']]
        
        all_systems = required_systems + optional_systems
        
        for system_id in all_systems:
            system = self.systems[system_id]
            
            # 安装依赖
            if not self.install_dependencies(system_id):
                if system['required']:
                    self.log(f"❌ 必需系统 {system['name']} 依赖安装失败", "ERROR")
                    return False
                else:
                    self.log(f"⚠️ 可选系统 {system['name']} 依赖安装失败，跳过", "WARNING")
                    continue
            
            # 启动系统
            process = self.start_system_local(system_id)
            if process:
                self.processes[system_id] = process
                self.monitor_process(system_id, process)
                
                # 等待服务启动
                if self.wait_for_service(system['port'], 10):
                    self.log(f"✅ {system['name']} 启动成功 (端口: {system['port']})")
                else:
                    self.log(f"⚠️ {system['name']} 可能未完全启动", "WARNING")
            else:
                if system['required']:
                    self.log(f"❌ 必需系统 {system['name']} 启动失败", "ERROR")
                    return False
                else:
                    self.log(f"⚠️ 可选系统 {system['name']} 启动失败，跳过", "WARNING")
        
        return True
    
    def stop_all_services(self):
        """停止所有服务"""
        if self.docker_mode:
            self.stop_docker_compose()
        else:
            self.log("🛑 停止所有本地服务...")
            for system_id, process in self.processes.items():
                try:
                    process.terminate()
                    process.wait(timeout=10)
                    self.log(f"✅ {self.systems[system_id]['name']} 已停止")
                except Exception as e:
                    self.log(f"⚠️ 停止 {self.systems[system_id]['name']} 时出错: {e}", "WARNING")
                    try:
                        process.kill()
                    except:
                        pass
        
        self.processes.clear()
    
    def show_status(self):
        """显示服务状态"""
        self.log("📊 服务状态:")
        
        if self.docker_mode:
            try:
                result = subprocess.run(['docker', 'compose', '-f', 'management/deployment/docker-compose.yml', 'ps'], 
                                      cwd=self.workspace_path, 
                                      capture_output=True, text=True, timeout=10)
                print(result.stdout)
            except Exception as e:
                self.log(f"❌ 获取Docker状态失败: {e}", "ERROR")
        else:
            for system_id, system in self.systems.items():
                if system_id in self.processes:
                    process = self.processes[system_id]
                    status = "运行中" if process.poll() is None else "已停止"
                    self.log(f"  {system['name']}: {status} (端口: {system['port']})")
                else:
                    self.log(f"  {system['name']}: 未启动")
    
    def open_web_interfaces(self):
        """打开Web界面"""
        self.log("🌐 打开Web界面...")
        
        web_services = [
            ('rag-system', 'RAG智能系统'),
            ('changlee', 'Changlee音乐播放器'),
            ('chronicle', 'Chronicle时间管理'),
            ('nexus', 'Nexus集成管理')
        ]
        
        for system_id, name in web_services:
            if system_id in self.processes or self.docker_mode:
                port = self.systems[system_id]['port']
                url = f"http://localhost:{port}"
                try:
                    webbrowser.open(url)
                    self.log(f"🌐 已打开 {name}: {url}")
                except Exception as e:
                    self.log(f"⚠️ 无法打开 {name}: {e}", "WARNING")
    
    def run_interactive(self):
        """交互式运行"""
        self.log("🎮 进入交互模式 (输入 'help' 查看命令)")
        
        while self.running:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'help':
                    print("""
可用命令:
  status  - 显示服务状态
  web     - 打开Web界面
  stop    - 停止所有服务
  restart - 重启所有服务
  quit    - 退出程序
                    """)
                elif command == 'status':
                    self.show_status()
                elif command == 'web':
                    self.open_web_interfaces()
                elif command == 'stop':
                    self.stop_all_services()
                elif command == 'restart':
                    self.stop_all_services()
                    time.sleep(2)
                    self.start_services(docker=self.docker_mode)
                elif command in ['quit', 'exit', 'q']:
                    break
                elif command == '':
                    continue
                else:
                    print(f"未知命令: {command}")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        self.stop_all_services()

def main():
    parser = argparse.ArgumentParser(description='N.S.S-Novena-Garfield 统一启动器')
    parser.add_argument('--docker', action='store_true', help='使用Docker模式启动')
    parser.add_argument('--systems', nargs='+', help='指定要启动的系统')
    parser.add_argument('--no-web', action='store_true', help='不自动打开Web界面')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    parser.add_argument('--path', default='.', help='工作空间路径')
    
    args = parser.parse_args()
    
    launcher = UnifiedLauncher(args.path)
    
    print("🚀 N.S.S-Novena-Garfield 统一启动器")
    print("="*50)
    
    # 启动服务
    if launcher.start_services(args.systems, args.docker):
        launcher.log("✅ 所有服务启动完成")
        
        # 显示状态
        launcher.show_status()
        
        # 打开Web界面
        if not args.no_web:
            time.sleep(2)
            launcher.open_web_interfaces()
        
        # 交互模式或等待
        if args.interactive:
            launcher.run_interactive()
        else:
            launcher.log("💡 按 Ctrl+C 停止所有服务")
            try:
                while launcher.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
    else:
        launcher.log("❌ 服务启动失败", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()