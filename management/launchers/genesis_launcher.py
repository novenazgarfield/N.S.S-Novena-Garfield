#!/usr/bin/env python3
"""
🧠 Genesis中央情报大脑 - 一键启动器
=====================================

完整的NEXUS系统启动解决方案，包含：
- 中央情报大脑 (Trinity Smart Chunking, Memory Nebula, Shields of Order, Fire Control System, Pantheon Soul, Black Box Recorder)
- NEXUS前端界面
- 自动隧道连接
- 动态配置管理
- Chronicle时间管理集成
- 系统稳定性保障

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0-Genesis-Enhanced
"""

import os
import sys
import time
import json
import signal
import subprocess
import requests
import psutil
from pathlib import Path
from datetime import datetime
import argparse
import threading
import logging

class GenesisLauncher:
    """Genesis中央情报大脑启动器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = {}
        self.tunnels = {}
        self.config_file = self.project_root / "systems/nexus/public/api_config.json"
        self.log_dir = Path("/tmp")
        self.chronicle_enabled = False
        
        # 设置日志
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # 系统组件配置
        self.components = {
            'intelligence_brain': {
                'name': '🧠 中央情报大脑',
                'description': 'Trinity Smart Chunking + Memory Nebula + Shields of Order + Fire Control System + Pantheon Soul + Black Box Recorder',
                'type': 'flask_api',
                'port_range': (8500, 8510),
                'startup_script': 'enhanced_smart_rag_server.py',
                'working_dir': 'systems/rag-system',
                'health_endpoint': '/api/health'
            },
            'nexus_frontend': {
                'name': '🌐 NEXUS前端界面',
                'description': 'React + Vite前端界面',
                'type': 'vite_dev',
                'port_range': (52300, 52310),
                'startup_command': ['npm', 'run', 'dev'],
                'working_dir': 'systems/nexus',
                'health_endpoint': '/'
            },
            'chronicle': {
                'name': '📝 Chronicle时间管理',
                'description': 'Chronicle时间管理系统',
                'type': 'optional',
                'port_range': (53000, 53010),
                'enabled': False
            }
        }
    
    def log(self, message, level='info'):
        """统一日志输出"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        print(formatted_message)
        
        if level == 'info':
            self.logger.info(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'warning':
            self.logger.warning(message)
    
    def find_free_port(self, start_port=5000, max_attempts=100):
        """查找可用端口"""
        import socket
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise RuntimeError(f"无法找到可用端口 (尝试范围: {start_port}-{start_port + max_attempts})")
    
    def cleanup_zombie_processes(self):
        """清理僵尸进程和相关进程"""
        self.log("🧹 清理僵尸进程和旧进程...")
        
        # 要清理的进程关键词
        keywords = [
            'smart_rag_server', 'enhanced_smart_rag_server', 'intelligence_app',
            'vite', 'cloudflared', 'nexus', 'node.*vite', 'streamlit'
        ]
        
        killed_count = 0
        zombie_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cmdline']):
            try:
                proc_info = proc.info
                cmdline = ' '.join(proc_info['cmdline'] or [])
                
                # 检查僵尸进程
                if proc_info['status'] in ['zombie', 'stopped']:
                    try:
                        proc.kill()
                        zombie_count += 1
                        self.log(f"清理僵尸进程: PID {proc_info['pid']}")
                    except:
                        pass
                    continue
                
                # 检查是否是目标进程
                is_target = any(keyword in cmdline.lower() for keyword in keywords)
                if is_target:
                    try:
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()
                        killed_count += 1
                        self.log(f"终止进程: PID {proc_info['pid']} - {cmdline[:80]}...")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        time.sleep(2)
        self.log(f"✅ 进程清理完成: 终止 {killed_count} 个进程, 清理 {zombie_count} 个僵尸进程")
    
    def start_intelligence_brain(self):
        """启动中央情报大脑"""
        self.log("🧠 启动中央情报大脑...")
        
        component = self.components['intelligence_brain']
        port = self.find_free_port(component['port_range'][0])
        
        working_dir = self.project_root / component['working_dir']
        log_file = self.log_dir / "intelligence_brain.log"
        
        # 启动增强版RAG服务器
        cmd = [
            sys.executable, component['startup_script'],
            '--port', str(port),
            '--host', '0.0.0.0'
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=working_dir,
            stdout=open(log_file, 'w'),
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid
        )
        
        self.processes['intelligence_brain'] = {
            'process': process,
            'port': port,
            'log_file': log_file,
            'component': component
        }
        
        # 等待服务启动
        self.log("等待中央情报大脑启动...")
        for i in range(30):
            try:
                response = requests.get(f"http://localhost:{port}/api/health", timeout=2)
                if response.status_code == 200:
                    health_data = response.json()
                    version = health_data.get('version', 'Unknown')
                    features = health_data.get('data', {}).get('features', [])
                    
                    self.log(f"✅ 中央情报大脑启动成功!")
                    self.log(f"   📡 地址: http://localhost:{port}")
                    self.log(f"   🔖 版本: {version}")
                    self.log(f"   🎯 核心功能: {len(features)} 个模块")
                    
                    return port
            except:
                time.sleep(1)
        
        raise RuntimeError("中央情报大脑启动失败")
    
    def start_nexus_frontend(self):
        """启动NEXUS前端"""
        self.log("🌐 启动NEXUS前端界面...")
        
        component = self.components['nexus_frontend']
        port = self.find_free_port(component['port_range'][0])
        
        working_dir = self.project_root / component['working_dir']
        log_file = self.log_dir / "nexus_frontend.log"
        
        # 检查npm是否可用
        try:
            subprocess.run(['npm', '--version'], capture_output=True, check=True)
        except:
            raise RuntimeError("npm未安装或不可用，请先安装Node.js和npm")
        
        # 启动前端开发服务器
        cmd = component['startup_command'] + [
            '--', '--host', '0.0.0.0', '--port', str(port)
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=working_dir,
            stdout=open(log_file, 'w'),
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid
        )
        
        self.processes['nexus_frontend'] = {
            'process': process,
            'port': port,
            'log_file': log_file,
            'component': component
        }
        
        # 等待前端启动
        self.log("等待NEXUS前端启动...")
        for i in range(30):
            try:
                response = requests.get(f"http://localhost:{port}", timeout=2)
                if response.status_code == 200:
                    self.log(f"✅ NEXUS前端启动成功: http://localhost:{port}")
                    return port
            except:
                time.sleep(1)
        
        raise RuntimeError("NEXUS前端启动失败")
    
    def start_chronicle(self):
        """启动Chronicle时间管理 (可选)"""
        if not self.chronicle_enabled:
            return None
            
        self.log("📝 启动Chronicle时间管理...")
        # 这里可以添加Chronicle启动逻辑
        # 暂时返回None，表示未启动
        return None
    
    def create_tunnel(self, service_name, port, max_retries=3):
        """创建Cloudflare隧道"""
        self.log(f"🌐 为{service_name}创建隧道 (端口: {port})...")
        
        for attempt in range(max_retries):
            try:
                log_file = self.log_dir / f"{service_name}_tunnel.log"
                
                # 清理旧的日志文件
                if log_file.exists():
                    log_file.unlink()
                
                cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"]
                
                process = subprocess.Popen(
                    cmd,
                    stdout=open(log_file, 'w'),
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid
                )
                
                # 等待隧道建立并获取URL
                tunnel_url = None
                for i in range(30):
                    try:
                        if log_file.exists():
                            with open(log_file, 'r') as f:
                                content = f.read()
                                import re
                                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', content)
                                if match:
                                    tunnel_url = match.group(0)
                                    break
                    except:
                        pass
                    time.sleep(1)
                
                if tunnel_url:
                    # 验证隧道是否工作
                    try:
                        response = requests.get(tunnel_url, timeout=10)
                        if response.status_code == 200:
                            self.tunnels[service_name] = {
                                'process': process,
                                'url': tunnel_url,
                                'port': port,
                                'log_file': log_file
                            }
                            self.log(f"✅ {service_name}隧道创建成功: {tunnel_url}")
                            return tunnel_url
                    except:
                        pass
                
                # 如果失败，终止进程并重试
                process.terminate()
                self.log(f"❌ {service_name}隧道创建失败 (尝试 {attempt + 1}/{max_retries})")
                
                if attempt < max_retries - 1:
                    time.sleep(5)  # 等待5秒后重试
                    
            except Exception as e:
                self.log(f"❌ {service_name}隧道创建异常: {e}")
        
        self.log(f"❌ {service_name}隧道创建最终失败")
        return None
    
    def update_config_file(self, brain_port, frontend_port, brain_tunnel_url=None, frontend_tunnel_url=None):
        """更新配置文件"""
        self.log("📝 更新动态配置文件...")
        
        # 基础API端点
        base_api = brain_tunnel_url if brain_tunnel_url else f"http://localhost:{brain_port}"
        
        config = {
            "api_endpoints": {
                "rag_api": base_api,
                "health_check": f"{base_api}/api/health",
                "chat": f"{base_api}/api/chat",
                "upload": f"{base_api}/api/upload",
                "documents": f"{base_api}/api/documents",
                "chat_history": f"{base_api}/api/chat/history",
                "rag_api_local": f"http://localhost:{brain_port}",
                "energy_api": "http://localhost:56400",
                "energy_health": "http://localhost:56400/api/energy/health",
                "energy_models": "http://localhost:56400/api/energy/models/available",
                "energy_config": "http://localhost:56400/api/energy/config"
            },
            "local_endpoints": {
                "intelligence_brain": f"http://localhost:{brain_port}",
                "nexus_frontend": f"http://localhost:{frontend_port}"
            },
            "tunnel_endpoints": {
                "intelligence_brain": brain_tunnel_url,
                "nexus_frontend": frontend_tunnel_url
            } if brain_tunnel_url or frontend_tunnel_url else {},
            "system_info": {
                "version": "2.0.0-Genesis-Enhanced",
                "launcher": "genesis_launcher.py",
                "components": {
                    "intelligence_brain": {
                        "name": "🧠 中央情报大脑",
                        "modules": [
                            "🔺 Trinity Smart Chunking",
                            "🌌 Memory Nebula", 
                            "🛡️ Shields of Order",
                            "🎯 Fire Control System",
                            "🌟 Pantheon Soul",
                            "🛡️ Black Box Recorder"
                        ],
                        "port": brain_port,
                        "tunnel": brain_tunnel_url
                    },
                    "nexus_frontend": {
                        "name": "🌐 NEXUS前端界面",
                        "port": frontend_port,
                        "tunnel": frontend_tunnel_url
                    }
                }
            },
            "updated_at": time.time(),
            "status": "active",
            "tunnel_status": "connected" if brain_tunnel_url and frontend_tunnel_url else "local_only",
            "last_health_check": datetime.now().isoformat(),
            "features": [
                "🧠 中央情报大脑 (6大核心模块)",
                "🌐 动态端口管理",
                "🔄 自动隧道连接", 
                "📝 智能配置更新",
                "🛡️ 系统稳定性保障",
                "📊 实时健康监控",
                "🔧 一键启动部署"
            ]
        }
        
        # 确保目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入配置文件
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.log(f"✅ 配置文件已更新: {self.config_file}")
    
    def test_system_health(self):
        """测试系统健康状态"""
        self.log("🧪 测试系统健康状态...")
        
        health_results = {}
        
        # 测试中央情报大脑
        if 'intelligence_brain' in self.processes:
            brain_info = self.processes['intelligence_brain']
            try:
                response = requests.get(f"http://localhost:{brain_info['port']}/api/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    health_results['intelligence_brain'] = {
                        'status': '✅ 正常',
                        'version': data.get('version', 'Unknown'),
                        'features': len(data.get('data', {}).get('features', []))
                    }
                    self.log(f"✅ 中央情报大脑健康检查通过")
                else:
                    health_results['intelligence_brain'] = {'status': f'❌ HTTP {response.status_code}'}
            except Exception as e:
                health_results['intelligence_brain'] = {'status': f'❌ 连接失败: {e}'}
        
        # 测试NEXUS前端
        if 'nexus_frontend' in self.processes:
            frontend_info = self.processes['nexus_frontend']
            try:
                response = requests.get(f"http://localhost:{frontend_info['port']}", timeout=5)
                if response.status_code == 200:
                    health_results['nexus_frontend'] = {'status': '✅ 正常'}
                    self.log(f"✅ NEXUS前端健康检查通过")
                else:
                    health_results['nexus_frontend'] = {'status': f'❌ HTTP {response.status_code}'}
            except Exception as e:
                health_results['nexus_frontend'] = {'status': f'❌ 连接失败: {e}'}
        
        # 测试隧道连接
        for name, tunnel_info in self.tunnels.items():
            try:
                response = requests.get(tunnel_info['url'], timeout=10)
                if response.status_code == 200:
                    health_results[f'{name}_tunnel'] = {'status': '✅ 正常', 'url': tunnel_info['url']}
                    self.log(f"✅ {name}隧道健康检查通过")
                else:
                    health_results[f'{name}_tunnel'] = {'status': f'❌ HTTP {response.status_code}'}
            except Exception as e:
                health_results[f'{name}_tunnel'] = {'status': f'❌ 连接失败: {e}'}
        
        return health_results
    
    def monitor_processes(self):
        """监控进程状态"""
        self.log("👁️ 开始进程监控...")
        
        try:
            while True:
                # 检查所有进程
                for name, info in self.processes.items():
                    process = info['process']
                    if process.poll() is not None:
                        self.log(f"❌ {name}进程已停止 (退出码: {process.returncode})", 'error')
                        # 这里可以添加自动重启逻辑
                
                # 检查隧道进程
                for name, info in self.tunnels.items():
                    process = info['process']
                    if process.poll() is not None:
                        self.log(f"❌ {name}隧道已断开 (退出码: {process.returncode})", 'error')
                        # 这里可以添加自动重连逻辑
                
                time.sleep(30)  # 每30秒检查一次
                
        except KeyboardInterrupt:
            self.log("收到中断信号，开始清理...")
            self.cleanup()
    
    def cleanup(self):
        """清理所有进程"""
        self.log("🧹 清理所有进程...")
        
        # 终止所有启动的进程
        for name, info in {**self.processes, **self.tunnels}.items():
            try:
                process = info['process']
                if process.poll() is None:
                    self.log(f"终止{name}进程...")
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            except Exception as e:
                self.log(f"清理{name}时出错: {e}", 'error')
        
        self.log("✅ 清理完成")
    
    def show_system_info(self):
        """显示系统信息"""
        self.log("\n" + "="*80)
        self.log("🎉 Genesis中央情报大脑系统启动成功！")
        self.log("="*80)
        
        # 显示核心组件
        self.log("🧠 核心组件:")
        if 'intelligence_brain' in self.processes:
            port = self.processes['intelligence_brain']['port']
            self.log(f"   中央情报大脑: http://localhost:{port}")
            self.log("   ├── 🔺 Trinity Smart Chunking     # 三位一体智能分块")
            self.log("   ├── 🌌 Memory Nebula              # 记忆星图 (知识图谱)")
            self.log("   ├── 🛡️ Shields of Order           # 秩序之盾 (二级精炼)")
            self.log("   ├── 🎯 Fire Control System        # 火控系统 (AI注意力控制)")
            self.log("   ├── 🌟 Pantheon Soul              # Pantheon灵魂 (自我进化)")
            self.log("   └── 🛡️ Black Box Recorder         # 黑匣子记录器 (故障记忆)")
        
        if 'nexus_frontend' in self.processes:
            port = self.processes['nexus_frontend']['port']
            self.log(f"   NEXUS前端界面: http://localhost:{port}")
        
        # 显示隧道访问
        if self.tunnels:
            self.log("\n🌍 公网访问:")
            for name, info in self.tunnels.items():
                self.log(f"   {name}: {info['url']}")
        
        # 显示日志文件
        self.log(f"\n📋 日志文件:")
        for name, info in {**self.processes, **self.tunnels}.items():
            if 'log_file' in info:
                self.log(f"   {name}: {info['log_file']}")
        
        # 显示配置文件
        self.log(f"\n📝 配置文件: {self.config_file}")
        
        self.log("="*80)
    
    def launch(self, enable_tunnels=True, enable_chronicle=False, monitor=True):
        """启动完整系统"""
        try:
            self.chronicle_enabled = enable_chronicle
            
            self.log("🚀 Genesis中央情报大脑启动器")
            self.log("="*50)
            
            # 1. 清理僵尸进程
            self.cleanup_zombie_processes()
            
            # 2. 启动中央情报大脑
            brain_port = self.start_intelligence_brain()
            
            # 3. 启动NEXUS前端
            frontend_port = self.start_nexus_frontend()
            
            # 4. 启动Chronicle (可选)
            chronicle_port = self.start_chronicle()
            
            # 5. 创建隧道 (如果启用)
            brain_tunnel_url = None
            frontend_tunnel_url = None
            
            if enable_tunnels:
                brain_tunnel_url = self.create_tunnel("intelligence_brain", brain_port)
                frontend_tunnel_url = self.create_tunnel("nexus_frontend", frontend_port)
            
            # 6. 更新配置文件
            self.update_config_file(brain_port, frontend_port, brain_tunnel_url, frontend_tunnel_url)
            
            # 7. 测试系统健康
            health_results = self.test_system_health()
            
            # 8. 显示系统信息
            self.show_system_info()
            
            # 9. 开始监控 (如果启用)
            if monitor:
                self.monitor_processes()
            else:
                self.log("系统启动完成！按Ctrl+C停止。")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            
        except Exception as e:
            self.log(f"❌ 启动失败: {e}", 'error')
            self.cleanup()
            sys.exit(1)
        finally:
            self.cleanup()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Genesis中央情报大脑启动器')
    parser.add_argument('--no-tunnels', action='store_true', help='不创建隧道')
    parser.add_argument('--no-monitor', action='store_true', help='不启用进程监控')
    parser.add_argument('--enable-chronicle', action='store_true', help='启用Chronicle时间管理')
    parser.add_argument('--cleanup-only', action='store_true', help='仅清理进程后退出')
    
    args = parser.parse_args()
    
    launcher = GenesisLauncher()
    
    # 仅清理模式
    if args.cleanup_only:
        launcher.cleanup_zombie_processes()
        return
    
    # 设置信号处理
    def signal_handler(signum, frame):
        launcher.log("收到终止信号...")
        launcher.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动系统
    launcher.launch(
        enable_tunnels=not args.no_tunnels,
        enable_chronicle=args.enable_chronicle,
        monitor=not args.no_monitor
    )

if __name__ == "__main__":
    main()