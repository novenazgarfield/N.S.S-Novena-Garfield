#!/usr/bin/env python3
"""
API管理系统统一入口点
为整个研究工作站项目提供统一的API管理服务
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

class APIManagerStarter:
    """API管理系统启动器"""
    
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
            print("🔧 API管理系统 - 统一入口点")
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
            if mode == 'web':
                self.run_web_interface(options)
            elif mode == 'gemini':
                self.run_gemini_system(options)
            elif mode == 'energy':
                self.run_energy_server(options)
            elif mode == 'rag':
                self.run_rag_system(options)
            elif mode == 'demo':
                self.run_demo_system(options)
            elif mode == 'test':
                self.run_test_mode(options)
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
                'name': 'API管理系统',
                'version': '1.0.0',
                'description': '研究工作站API统一管理服务'
            },
            'web': {
                'host': '0.0.0.0',
                'port': 56336,
                'app': 'api_web_manager.py'
            },
            'gemini': {
                'host': '0.0.0.0',
                'port': 56337,
                'app': 'gemini_chat_app.py'
            },
            'energy': {
                'host': '0.0.0.0',
                'port': 56338,
                'app': 'energy_api_server.py'
            },
            'rag': {
                'host': '0.0.0.0',
                'port': 56339,
                'app': 'simple_dynamic_rag.py'
            },
            'paths': {
                'config': str(self.project_root / 'config'),
                'logs': str(self.project_root / 'logs'),
                'integrations': str(self.project_root / 'integrations'),
                'docs': str(self.project_root / 'docs')
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
                logging.FileHandler(log_dir / 'api_manager.log'),
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
    
    def run_web_interface(self, options):
        """运行Web管理界面"""
        print("🌐 启动API管理Web界面...")
        
        web_config = self.config.get('web', {})
        host = options.get('host') or web_config.get('host', '0.0.0.0')
        port = options.get('port') or web_config.get('port', 56336)
        app = web_config.get('app', 'api_web_manager.py')
        
        print(f"📍 地址: http://{host}:{port}")
        
        # 检查Streamlit
        if not shutil.which('streamlit'):
            print("❌ Streamlit未安装，请运行: pip install streamlit")
            sys.exit(1)
        
        # 启动Streamlit应用
        cmd = [
            'streamlit', 'run', app,
            '--server.port', str(port),
            '--server.address', host,
            '--server.allowRunOnSave', 'true',
            '--server.runOnSave', 'true',
            '--server.headless', 'true'
        ]
        
        try:
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
                    print(f"[Web] {line.rstrip()}")
            
            threading.Thread(target=log_output, daemon=True).start()
            
            self.processes.append(process)
            self.wait_for_processes()
            
        except Exception as e:
            print(f"❌ Web界面启动失败: {e}")
            sys.exit(1)
    
    def run_gemini_system(self, options):
        """运行Gemini AI系统"""
        print("🤖 启动Gemini AI系统...")
        
        # 启动API管理界面
        if not options.get('chat_only'):
            print("🌐 启动API管理界面...")
            web_process = self.start_streamlit_app(
                'api_web_manager.py',
                self.config['web']['port'],
                self.config['web']['host']
            )
            if web_process:
                self.processes.append(web_process)
                time.sleep(3)  # 等待Web界面启动
        
        # 启动Gemini聊天应用
        print("💬 启动Gemini聊天应用...")
        gemini_process = self.start_streamlit_app(
            'gemini_chat_app.py',
            self.config['gemini']['port'],
            self.config['gemini']['host']
        )
        if gemini_process:
            self.processes.append(gemini_process)
        
        self.wait_for_processes()
    
    def run_energy_server(self, options):
        """运行能源API服务器"""
        print("⚡ 启动能源API服务器...")
        
        energy_config = self.config.get('energy', {})
        host = options.get('host') or energy_config.get('host', '0.0.0.0')
        port = options.get('port') or energy_config.get('port', 56338)
        app = energy_config.get('app', 'energy_api_server.py')
        
        print(f"📍 地址: http://{host}:{port}")
        
        try:
            process = subprocess.Popen(
                [sys.executable, app, '--host', host, '--port', str(port)],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 启动日志输出线程
            def log_output():
                for line in process.stdout:
                    print(f"[Energy] {line.rstrip()}")
            
            threading.Thread(target=log_output, daemon=True).start()
            
            self.processes.append(process)
            self.wait_for_processes()
            
        except Exception as e:
            print(f"❌ 能源服务器启动失败: {e}")
            sys.exit(1)
    
    def run_rag_system(self, options):
        """运行RAG系统"""
        print("📚 启动动态RAG系统...")
        
        rag_config = self.config.get('rag', {})
        host = options.get('host') or rag_config.get('host', '0.0.0.0')
        port = options.get('port') or rag_config.get('port', 56339)
        app = rag_config.get('app', 'simple_dynamic_rag.py')
        
        print(f"📍 地址: http://{host}:{port}")
        
        rag_process = self.start_streamlit_app(app, port, host)
        if rag_process:
            self.processes.append(rag_process)
            self.wait_for_processes()
    
    def run_demo_system(self, options):
        """运行演示系统"""
        print("🎭 启动完整演示系统...")
        
        # 启动所有服务
        services = [
            ('API管理界面', 'api_web_manager.py', self.config['web']['port']),
            ('Gemini聊天', 'gemini_chat_app.py', self.config['gemini']['port']),
            ('动态RAG', 'simple_dynamic_rag.py', self.config['rag']['port'])
        ]
        
        for name, app, port in services:
            print(f"🚀 启动{name}...")
            process = self.start_streamlit_app(app, port, '0.0.0.0')
            if process:
                self.processes.append(process)
                time.sleep(2)  # 错开启动时间
        
        # 显示访问信息
        print("\n✅ 演示系统启动完成！")
        print("📍 访问地址:")
        for name, _, port in services:
            print(f"   {name}: http://localhost:{port}")
        
        self.wait_for_processes()
    
    def run_test_mode(self, options):
        """运行测试模式"""
        print("🧪 运行系统测试...")
        
        # 运行测试脚本
        test_scripts = [
            'test_gemini_key.py',
            'test_complete_system.py'
        ]
        
        for script in test_scripts:
            script_path = self.project_root / script
            if script_path.exists():
                print(f"🔍 运行测试: {script}")
                try:
                    result = subprocess.run(
                        [sys.executable, str(script_path)],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        print(f"✅ {script} 测试通过")
                        if result.stdout:
                            print(f"   输出: {result.stdout.strip()}")
                    else:
                        print(f"❌ {script} 测试失败")
                        if result.stderr:
                            print(f"   错误: {result.stderr.strip()}")
                except Exception as e:
                    print(f"❌ 运行{script}失败: {e}")
            else:
                print(f"⚠️ 测试脚本不存在: {script}")
    
    def start_streamlit_app(self, app, port, host='0.0.0.0'):
        """启动Streamlit应用"""
        if not shutil.which('streamlit'):
            print("❌ Streamlit未安装，请运行: pip install streamlit")
            return None
        
        cmd = [
            'streamlit', 'run', app,
            '--server.port', str(port),
            '--server.address', host,
            '--server.allowRunOnSave', 'true',
            '--server.runOnSave', 'true',
            '--server.headless', 'true'
        ]
        
        try:
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
                    print(f"[{app}] {line.rstrip()}")
            
            threading.Thread(target=log_output, daemon=True).start()
            
            return process
        except Exception as e:
            print(f"❌ {app}启动失败: {e}")
            return None
    
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
        print("📊 API管理系统状态:")
        print("")
        
        # 系统信息
        system_config = self.config.get('system', {})
        print("🔧 系统信息:")
        print(f"   名称: {system_config.get('name', 'API管理系统')}")
        print(f"   版本: {system_config.get('version', '1.0.0')}")
        print(f"   描述: {system_config.get('description', '研究工作站API统一管理服务')}")
        print("")
        
        # 服务配置
        services = ['web', 'gemini', 'energy', 'rag']
        print("🌐 服务配置:")
        for service in services:
            config = self.config.get(service, {})
            host = config.get('host', '0.0.0.0')
            port = config.get('port', 'N/A')
            app = config.get('app', 'N/A')
            print(f"   {service.upper()}: http://{host}:{port} ({app})")
        print("")
        
        # 路径配置
        paths = self.config.get('paths', {})
        print("📁 路径配置:")
        for key, path in paths.items():
            path_obj = Path(path)
            status = "✅ 存在" if path_obj.exists() else "❌ 不存在"
            print(f"   {key}: {path} ({status})")
        print("")
        
        # 依赖状态
        print("🔧 依赖状态:")
        self.check_dependencies(verbose=False)
    
    def check_dependencies(self, verbose=True):
        """检查依赖"""
        if verbose:
            print("🔧 检查系统依赖...")
        
        # Python工具
        python_tools = {
            'python3': 'Python 3',
            'pip': 'Python包管理器'
        }
        
        # Web工具
        web_tools = {
            'streamlit': 'Streamlit Web框架'
        }
        
        all_available = True
        
        # 检查Python工具
        if verbose:
            print("\n🐍 Python工具:")
        for tool, description in python_tools.items():
            available = shutil.which(tool) is not None
            status = "✅ 可用" if available else "❌ 缺失"
            print(f"   {tool}: {status} - {description}")
            if not available:
                all_available = False
        
        # 检查Web工具
        if verbose:
            print("\n🌐 Web工具:")
        for tool, description in web_tools.items():
            available = shutil.which(tool) is not None
            status = "✅ 可用" if available else "❌ 缺失"
            print(f"   {tool}: {status} - {description}")
            if not available:
                all_available = False
        
        # 检查Python包
        if verbose:
            print("\n📦 Python包:")
        python_packages = ['streamlit', 'requests', 'cryptography']
        for package in python_packages:
            try:
                __import__(package)
                print(f"   {package}: ✅ 已安装")
            except ImportError:
                print(f"   {package}: ❌ 未安装")
                all_available = False
        
        # 检查配置文件
        if verbose:
            print("\n📄 配置文件:")
        config_files = [
            'config/api_endpoints.json',
            'config/private_apis.json'
        ]
        for config_file in config_files:
            config_path = self.project_root / config_file
            status = "✅ 存在" if config_path.exists() else "❌ 不存在"
            print(f"   {config_file}: {status}")
        
        if verbose:
            if all_available:
                print("\n✅ 所有依赖检查通过")
            else:
                print("\n❌ 部分依赖缺失")
                print("\n💡 安装建议:")
                print("   安装Streamlit: pip install streamlit")
                print("   安装其他依赖: pip install requests cryptography")
        
        return all_available
    
    def run_setup(self):
        """运行系统设置"""
        print("⚙️ 运行系统设置...")
        
        # 创建必要目录
        paths = self.config.get('paths', {})
        for key, path in paths.items():
            path_obj = Path(path)
            if not path_obj.exists():
                path_obj.mkdir(parents=True, exist_ok=True)
                print(f"📁 创建目录: {path}")
            else:
                print(f"📁 目录已存在: {path}")
        
        # 安装Python依赖
        print("\n📦 安装Python依赖...")
        packages = ['streamlit', 'requests', 'cryptography']
        for package in packages:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             check=True, capture_output=True)
                print(f"✅ {package} 安装完成")
            except subprocess.CalledProcessError as e:
                print(f"❌ {package} 安装失败: {e}")
        
        # 检查配置文件
        print("\n📄 检查配置文件...")
        config_dir = self.project_root / 'config'
        if not config_dir.exists():
            config_dir.mkdir(exist_ok=True)
            print("📁 创建配置目录")
        
        # 创建默认配置文件
        default_configs = {
            'api_endpoints.json': {
                'gemini': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
                'energy': 'http://localhost:56338/api/energy'
            },
            'private_apis.json': {
                'apis': {},
                'encryption_enabled': True
            }
        }
        
        for filename, content in default_configs.items():
            config_file = config_dir / filename
            if not config_file.exists():
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2, ensure_ascii=False)
                print(f"📄 创建配置文件: {filename}")
            else:
                print(f"📄 配置文件已存在: {filename}")
        
        print("\n✅ 系统设置完成")
    
    def show_help(self):
        """显示帮助信息"""
        print(f"""
🔧 API管理系统 - 统一入口点

用法: python api_manager.py [模式] [选项]

运行模式:
  web           - Web管理界面
  gemini        - Gemini AI系统 (API管理+聊天)
  energy        - 能源API服务器
  rag           - 动态RAG系统
  demo          - 完整演示系统 (所有服务)
  test          - 运行系统测试
  status        - 显示系统状态
  check-deps    - 检查系统依赖
  setup         - 运行系统设置

选项:
  --config <path>       - 指定配置文件路径
  --host <host>         - 指定主机地址 (默认: 0.0.0.0)
  --port <port>         - 指定端口号
  --chat-only           - 仅启动聊天应用 (gemini模式)
  --debug               - 启用调试模式
  --help                - 显示此帮助信息

示例:
  python api_manager.py web
  python api_manager.py web --host localhost --port 8080
  python api_manager.py gemini
  python api_manager.py gemini --chat-only
  python api_manager.py demo
  python api_manager.py status
  python api_manager.py setup

环境变量:
  API_CONFIG_PATH       - 配置文件路径
  API_DEBUG             - 调试模式
  API_HOST              - 主机地址
  API_PORT              - 端口号
        """)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="API管理系统统一入口点",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'mode',
        nargs='?',
        default='status',
        choices=['web', 'gemini', 'energy', 'rag', 'demo', 'test', 
                'status', 'check-deps', 'setup'],
        help='运行模式'
    )
    
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--host', help='主机地址')
    parser.add_argument('--port', type=int, help='端口号')
    parser.add_argument('--chat-only', action='store_true', help='仅启动聊天应用')
    parser.add_argument('--debug', '-d', action='store_true', help='启用调试模式')
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 处理环境变量
    if not args.config:
        args.config = os.getenv('API_CONFIG_PATH')
    
    if not args.debug:
        args.debug = os.getenv('API_DEBUG', '').lower() in ('true', '1', 'yes')
    
    if not args.host:
        args.host = os.getenv('API_HOST')
    
    if not args.port:
        port_env = os.getenv('API_PORT')
        if port_env:
            args.port = int(port_env)
    
    # 启动系统
    starter = APIManagerStarter()
    starter.start(args.mode, vars(args))

if __name__ == "__main__":
    main()