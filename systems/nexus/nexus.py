#!/usr/bin/env python3
"""
NEXUS系统统一入口点
Research Workstation Command Center
"""

import sys
import argparse
import os
import logging
import subprocess
import shutil
import json
import time
from pathlib import Path
import threading
import signal

# 项目根目录
project_root = Path(__file__).parent

class NexusStarter:
    """NEXUS系统启动器"""
    
    def __init__(self):
        self.config = None
        self.logger = None
        self.project_root = project_root
        self.processes = []
    
    def start(self, mode, options=None):
        """主启动函数"""
        if options is None:
            options = {}
            
        try:
            print("🚀 NEXUS - Research Workstation Command Center")
            print("=" * 50)
            print(f"📍 运行模式: {mode}")
            print("")
            
            # 初始化配置
            self.init_config(options.get('config'))
            
            # 设置日志
            self.setup_logging(options.get('debug', False))
            
            # 设置信号处理
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            # 根据模式启动相应功能
            if mode == 'dev':
                self.run_development_mode(options)
            elif mode == 'prod':
                self.run_production_mode(options)
            elif mode == 'frontend':
                self.run_frontend_only(options)
            elif mode == 'backend':
                self.run_backend_only(options)
            elif mode == 'build':
                self.run_build_mode(options)
            elif mode == 'deploy':
                self.run_deploy_mode(options)
            elif mode == 'electron':
                self.run_electron_mode(options)
            elif mode == 'status':
                self.show_status()
            elif mode == 'check-deps':
                self.check_dependencies()
            elif mode == 'setup':
                self.run_setup()
            else:
                self.show_help()
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\n🛑 用户中断，正在退出...")
            self.cleanup()
            sys.exit(0)
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            if options.get('debug'):
                import traceback
                traceback.print_exc()
            self.cleanup()
            sys.exit(1)
    
    def init_config(self, config_path=None):
        """初始化配置"""
        # 创建默认配置
        self.config = {
            'system': {
                'name': 'NEXUS',
                'version': '1.0.0',
                'description': 'Research Workstation Command Center'
            },
            'frontend': {
                'host': '0.0.0.0',
                'port': 52305,
                'build_dir': 'dist'
            },
            'backend': {
                'host': '0.0.0.0',
                'port': 8765,
                'script': 'backend/websocket_server.py'
            },
            'paths': {
                'src': str(self.project_root / 'src'),
                'public': str(self.project_root / 'public'),
                'backend': str(self.project_root / 'backend'),
                'dist': str(self.project_root / 'dist'),
                'logs': str(self.project_root / 'logs')
            },
            'electron': {
                'main': 'public/electron.js',
                'wait_url': 'http://localhost:52305'
            }
        }
        
        # 如果提供了配置文件，尝试加载
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
                print(f"✅ 配置加载成功: {config_path}")
            except Exception as e:
                print(f"⚠️ 配置加载失败，使用默认配置: {e}")
        else:
            print("✅ 使用默认配置")
    
    def setup_logging(self, debug=False):
        """设置日志"""
        log_level = logging.DEBUG if debug else logging.INFO
        log_dir = Path(self.config.get('paths', {}).get('logs', 'logs'))
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'nexus.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("日志系统初始化完成")
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n🛑 收到信号 {signum}，正在清理...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """清理进程"""
        for process in self.processes:
            if process.poll() is None:
                print(f"🔄 终止进程 PID: {process.pid}")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        self.processes.clear()
    
    def run_development_mode(self, options):
        """运行开发模式"""
        print("🔧 启动开发模式...")
        
        # 检查依赖
        if not self.check_node_dependencies():
            print("❌ Node.js依赖检查失败")
            sys.exit(1)
        
        # 启动后端服务器
        if not options.get('frontend_only'):
            print("🐍 启动后端WebSocket服务器...")
            backend_process = self.start_backend_server()
            if backend_process:
                self.processes.append(backend_process)
                time.sleep(2)  # 等待后端启动
        
        # 启动前端开发服务器
        print("⚛️ 启动前端开发服务器...")
        frontend_process = self.start_frontend_dev_server(options)
        if frontend_process:
            self.processes.append(frontend_process)
        
        # 等待进程
        self.wait_for_processes()
    
    def run_production_mode(self, options):
        """运行生产模式"""
        print("🚀 启动生产模式...")
        
        # 构建前端
        if not options.get('skip_build'):
            print("📦 构建前端...")
            if not self.build_frontend():
                print("❌ 前端构建失败")
                sys.exit(1)
        
        # 启动后端服务器
        if not options.get('frontend_only'):
            print("🐍 启动后端WebSocket服务器...")
            backend_process = self.start_backend_server()
            if backend_process:
                self.processes.append(backend_process)
                time.sleep(2)
        
        # 启动前端生产服务器
        print("🌐 启动前端生产服务器...")
        frontend_process = self.start_frontend_prod_server(options)
        if frontend_process:
            self.processes.append(frontend_process)
        
        # 等待进程
        self.wait_for_processes()
    
    def run_frontend_only(self, options):
        """仅运行前端"""
        print("⚛️ 仅启动前端...")
        
        if options.get('build'):
            # 构建模式
            if not self.build_frontend():
                sys.exit(1)
            # 启动生产服务器
            frontend_process = self.start_frontend_prod_server(options)
        else:
            # 开发模式
            frontend_process = self.start_frontend_dev_server(options)
        
        if frontend_process:
            self.processes.append(frontend_process)
            self.wait_for_processes()
    
    def run_backend_only(self, options):
        """仅运行后端"""
        print("🐍 仅启动后端...")
        
        backend_process = self.start_backend_server()
        if backend_process:
            self.processes.append(backend_process)
            self.wait_for_processes()
    
    def run_build_mode(self, options):
        """运行构建模式"""
        print("📦 构建NEXUS系统...")
        
        if self.build_frontend():
            print("✅ 构建完成")
            
            # 显示构建信息
            dist_dir = Path(self.config['paths']['dist'])
            if dist_dir.exists():
                print(f"📁 构建输出: {dist_dir}")
                print("📊 构建统计:")
                for file in dist_dir.rglob('*'):
                    if file.is_file():
                        size = file.stat().st_size
                        print(f"   {file.relative_to(dist_dir)}: {size:,} bytes")
        else:
            print("❌ 构建失败")
            sys.exit(1)
    
    def run_deploy_mode(self, options):
        """运行部署模式"""
        print("🚀 部署NEXUS系统...")
        
        # 先构建
        if not self.build_frontend():
            print("❌ 构建失败，无法部署")
            sys.exit(1)
        
        # 运行部署脚本
        deploy_script = self.project_root / 'deployment' / 'deploy.js'
        if deploy_script.exists():
            try:
                subprocess.run(['node', str(deploy_script)], 
                             check=True, cwd=self.project_root)
                print("✅ 部署完成")
            except subprocess.CalledProcessError as e:
                print(f"❌ 部署失败: {e}")
                sys.exit(1)
        else:
            print("⚠️ 部署脚本不存在，跳过部署")
    
    def run_electron_mode(self, options):
        """运行Electron模式"""
        print("🖥️ 启动Electron应用...")
        
        # 检查Electron依赖
        if not shutil.which('electron'):
            print("❌ Electron未安装，请运行: npm install -g electron")
            sys.exit(1)
        
        # 启动后端
        if not options.get('frontend_only'):
            backend_process = self.start_backend_server()
            if backend_process:
                self.processes.append(backend_process)
                time.sleep(2)
        
        # 启动前端开发服务器
        frontend_process = self.start_frontend_dev_server(options)
        if frontend_process:
            self.processes.append(frontend_process)
            time.sleep(3)  # 等待前端启动
        
        # 启动Electron
        try:
            electron_process = subprocess.Popen(
                ['electron', '.'],
                cwd=self.project_root
            )
            self.processes.append(electron_process)
            self.wait_for_processes()
        except Exception as e:
            print(f"❌ Electron启动失败: {e}")
            sys.exit(1)
    
    def start_backend_server(self):
        """启动后端服务器"""
        backend_script = self.project_root / self.config['backend']['script']
        if not backend_script.exists():
            print(f"❌ 后端脚本不存在: {backend_script}")
            return None
        
        try:
            process = subprocess.Popen(
                [sys.executable, str(backend_script)],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 启动日志输出线程
            def log_output():
                for line in process.stdout:
                    print(f"[Backend] {line.rstrip()}")
            
            threading.Thread(target=log_output, daemon=True).start()
            
            return process
        except Exception as e:
            print(f"❌ 后端启动失败: {e}")
            return None
    
    def start_frontend_dev_server(self, options):
        """启动前端开发服务器"""
        try:
            cmd = ['npm', 'run', 'dev']
            if options.get('host'):
                cmd.extend(['--', '--host', options['host']])
            if options.get('port'):
                cmd.extend(['--', '--port', str(options['port'])])
            
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 启动日志输出线程
            def log_output():
                for line in process.stdout:
                    print(f"[Frontend] {line.rstrip()}")
            
            threading.Thread(target=log_output, daemon=True).start()
            
            return process
        except Exception as e:
            print(f"❌ 前端开发服务器启动失败: {e}")
            return None
    
    def start_frontend_prod_server(self, options):
        """启动前端生产服务器"""
        try:
            cmd = ['npm', 'run', 'preview']
            if options.get('host'):
                cmd.extend(['--', '--host', options['host']])
            if options.get('port'):
                cmd.extend(['--', '--port', str(options['port'])])
            
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 启动日志输出线程
            def log_output():
                for line in process.stdout:
                    print(f"[Frontend] {line.rstrip()}")
            
            threading.Thread(target=log_output, daemon=True).start()
            
            return process
        except Exception as e:
            print(f"❌ 前端生产服务器启动失败: {e}")
            return None
    
    def build_frontend(self):
        """构建前端"""
        try:
            result = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ 前端构建成功")
                return True
            else:
                print(f"❌ 前端构建失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 前端构建失败: {e}")
            return False
    
    def wait_for_processes(self):
        """等待进程结束"""
        if not self.processes:
            return
        
        print("🔄 系统运行中，按 Ctrl+C 退出...")
        
        try:
            # 等待任意进程结束
            while self.processes:
                for process in self.processes[:]:
                    if process.poll() is not None:
                        self.processes.remove(process)
                        print(f"⚠️ 进程 PID {process.pid} 已退出")
                
                if self.processes:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 收到中断信号...")
        finally:
            self.cleanup()
    
    def show_status(self):
        """显示系统状态"""
        print("📊 NEXUS系统状态:")
        print("")
        
        # 系统信息
        system_config = self.config.get('system', {})
        print("🚀 系统信息:")
        print(f"   名称: {system_config.get('name', 'NEXUS')}")
        print(f"   版本: {system_config.get('version', '1.0.0')}")
        print(f"   描述: {system_config.get('description', 'Research Workstation Command Center')}")
        print("")
        
        # 路径配置
        paths = self.config.get('paths', {})
        print("📁 路径配置:")
        for key, path in paths.items():
            path_obj = Path(path)
            status = "✅ 存在" if path_obj.exists() else "❌ 不存在"
            print(f"   {key}: {path} ({status})")
        print("")
        
        # 前端配置
        frontend = self.config.get('frontend', {})
        print("⚛️ 前端配置:")
        print(f"   主机: {frontend.get('host', '0.0.0.0')}")
        print(f"   端口: {frontend.get('port', 52305)}")
        print(f"   构建目录: {frontend.get('build_dir', 'dist')}")
        print("")
        
        # 后端配置
        backend = self.config.get('backend', {})
        print("🐍 后端配置:")
        print(f"   主机: {backend.get('host', '0.0.0.0')}")
        print(f"   端口: {backend.get('port', 8765)}")
        print(f"   脚本: {backend.get('script', 'backend/websocket_server.py')}")
        print("")
        
        # 依赖状态
        print("🔧 依赖状态:")
        self.check_dependencies(verbose=False)
    
    def check_dependencies(self, verbose=True):
        """检查依赖"""
        if verbose:
            print("🔧 检查系统依赖...")
        
        # Node.js工具
        node_tools = {
            'node': 'Node.js运行时',
            'npm': 'NPM包管理器',
            'vite': 'Vite构建工具'
        }
        
        # Python工具
        python_tools = {
            'python3': 'Python 3',
            'pip': 'Python包管理器'
        }
        
        # 可选工具
        optional_tools = {
            'electron': 'Electron桌面应用框架',
            'git': 'Git版本控制'
        }
        
        all_available = True
        
        # 检查Node.js工具
        if verbose:
            print("\n📦 Node.js工具:")
        for tool, description in node_tools.items():
            available = shutil.which(tool) is not None
            status = "✅ 可用" if available else "❌ 缺失"
            print(f"   {tool}: {status} - {description}")
            if not available and tool in ['node', 'npm']:
                all_available = False
        
        # 检查Python工具
        if verbose:
            print("\n🐍 Python工具:")
        for tool, description in python_tools.items():
            available = shutil.which(tool) is not None
            status = "✅ 可用" if available else "❌ 缺失"
            print(f"   {tool}: {status} - {description}")
            if not available:
                all_available = False
        
        # 检查可选工具
        if verbose:
            print("\n🔧 可选工具:")
        for tool, description in optional_tools.items():
            available = shutil.which(tool) is not None
            status = "✅ 可用" if available else "⚠️ 缺失"
            print(f"   {tool}: {status} - {description}")
        
        # 检查Node.js依赖
        if verbose:
            print("\n📦 Node.js依赖:")
        node_deps_ok = self.check_node_dependencies(verbose)
        
        # 检查Python依赖
        if verbose:
            print("\n🐍 Python依赖:")
        python_deps_ok = self.check_python_dependencies(verbose)
        
        if verbose:
            if all_available and node_deps_ok and python_deps_ok:
                print("\n✅ 所有依赖检查通过")
            else:
                print("\n❌ 部分依赖缺失")
                print("\n💡 安装建议:")
                if not all_available:
                    print("   安装Node.js: https://nodejs.org/")
                    print("   安装Python: https://python.org/")
                if not node_deps_ok:
                    print("   安装Node.js依赖: npm install")
                if not python_deps_ok:
                    print("   安装Python依赖: pip install -r backend/requirements.txt")
        
        return all_available and node_deps_ok and python_deps_ok
    
    def check_node_dependencies(self, verbose=True):
        """检查Node.js依赖"""
        package_json = self.project_root / 'package.json'
        if not package_json.exists():
            if verbose:
                print("   package.json: ❌ 不存在")
            return False
        
        node_modules = self.project_root / 'node_modules'
        if not node_modules.exists():
            if verbose:
                print("   node_modules: ❌ 不存在")
            return False
        
        if verbose:
            print("   package.json: ✅ 存在")
            print("   node_modules: ✅ 存在")
        
        return True
    
    def check_python_dependencies(self, verbose=True):
        """检查Python依赖"""
        requirements_file = self.project_root / 'backend' / 'requirements.txt'
        if not requirements_file.exists():
            if verbose:
                print("   requirements.txt: ❌ 不存在")
            return False
        
        if verbose:
            print("   requirements.txt: ✅ 存在")
        
        # 尝试导入主要依赖
        try:
            import websockets
            if verbose:
                print("   websockets: ✅ 已安装")
        except ImportError:
            if verbose:
                print("   websockets: ❌ 未安装")
            return False
        
        return True
    
    def run_setup(self):
        """运行系统设置"""
        print("⚙️ 运行系统设置...")
        
        # 创建必要目录
        paths = self.config.get('paths', {})
        for key, path in paths.items():
            if key in ['logs']:  # 只创建日志目录
                path_obj = Path(path)
                if not path_obj.exists():
                    path_obj.mkdir(parents=True, exist_ok=True)
                    print(f"📁 创建目录: {path}")
                else:
                    print(f"📁 目录已存在: {path}")
        
        # 安装Node.js依赖
        print("\n📦 安装Node.js依赖...")
        try:
            subprocess.run(['npm', 'install'], check=True, cwd=self.project_root)
            print("✅ Node.js依赖安装完成")
        except subprocess.CalledProcessError as e:
            print(f"❌ Node.js依赖安装失败: {e}")
        
        # 安装Python依赖
        print("\n🐍 安装Python依赖...")
        requirements_file = self.project_root / 'backend' / 'requirements.txt'
        if requirements_file.exists():
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], 
                             check=True)
                print("✅ Python依赖安装完成")
            except subprocess.CalledProcessError as e:
                print(f"❌ Python依赖安装失败: {e}")
        else:
            print("⚠️ requirements.txt不存在，跳过Python依赖安装")
        
        print("\n✅ 系统设置完成")
    
    def show_help(self):
        """显示帮助信息"""
        print(f"""
🚀 NEXUS - Research Workstation Command Center

用法: python nexus.py [模式] [选项]

运行模式:
  dev           - 开发模式 (前端+后端)
  prod          - 生产模式 (构建+部署)
  frontend      - 仅前端模式
  backend       - 仅后端模式
  build         - 构建模式
  deploy        - 部署模式
  electron      - Electron桌面应用模式
  status        - 显示系统状态
  check-deps    - 检查系统依赖
  setup         - 运行系统设置

选项:
  --config <path>       - 指定配置文件路径
  --host <host>         - 指定主机地址 (默认: 0.0.0.0)
  --port <port>         - 指定端口号 (默认: 52305)
  --frontend-only       - 仅启动前端 (dev模式)
  --skip-build          - 跳过构建步骤 (prod模式)
  --build               - 构建模式 (frontend模式)
  --debug               - 启用调试模式
  --help                - 显示此帮助信息

示例:
  python nexus.py dev
  python nexus.py dev --host localhost --port 3000
  python nexus.py prod --skip-build
  python nexus.py frontend --build
  python nexus.py backend
  python nexus.py build
  python nexus.py electron
  python nexus.py status
  python nexus.py setup

环境变量:
  NEXUS_CONFIG_PATH     - 配置文件路径
  NEXUS_DEBUG           - 调试模式
  NEXUS_HOST            - 主机地址
  NEXUS_PORT            - 端口号
        """)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="NEXUS系统统一入口点",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'mode',
        nargs='?',
        default='status',
        choices=['dev', 'prod', 'frontend', 'backend', 'build', 'deploy', 
                'electron', 'status', 'check-deps', 'setup'],
        help='运行模式'
    )
    
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--host', help='主机地址')
    parser.add_argument('--port', type=int, help='端口号')
    parser.add_argument('--frontend-only', action='store_true', help='仅启动前端')
    parser.add_argument('--skip-build', action='store_true', help='跳过构建步骤')
    parser.add_argument('--build', action='store_true', help='构建模式')
    parser.add_argument('--debug', '-d', action='store_true', help='启用调试模式')
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 处理环境变量
    if not args.config:
        args.config = os.getenv('NEXUS_CONFIG_PATH')
    
    if not args.debug:
        args.debug = os.getenv('NEXUS_DEBUG', '').lower() in ('true', '1', 'yes')
    
    if not args.host:
        args.host = os.getenv('NEXUS_HOST')
    
    if not args.port:
        port_env = os.getenv('NEXUS_PORT')
        if port_env:
            args.port = int(port_env)
    
    # 启动系统
    starter = NexusStarter()
    starter.start(args.mode, vars(args))

if __name__ == "__main__":
    main()