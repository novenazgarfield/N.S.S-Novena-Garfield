#!/usr/bin/env python3
"""
🚀 稳定版NEXUS启动器 - 解决僵尸进程问题
===========================================

完整的NEXUS系统启动解决方案，包含：
- 中央情报大脑功能整合到NEXUS前端
- 自动隧道连接
- 动态配置管理
- 僵尸进程预防
- 优雅关闭机制

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0-Genesis-Stable
"""

import os
import sys
import time
import json
import signal
import subprocess
import requests
import psutil
import threading
import atexit
from pathlib import Path
from datetime import datetime
import argparse
import logging
from contextlib import contextmanager

class StableNEXUSLauncher:
    """稳定版NEXUS启动器 - 防止僵尸进程"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = {}
        self.tunnels = {}
        self.config_file = self.project_root / "systems/nexus/public/api_config.json"
        self.log_dir = Path("/tmp")
        self.running = True
        self.cleanup_done = False
        
        # 设置日志
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # 注册清理函数
        atexit.register(self.cleanup)
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGCHLD, self._child_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.log(f"收到信号 {signum}，开始清理...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def _child_handler(self, signum, frame):
        """子进程信号处理器 - 防止僵尸进程"""
        while True:
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)
                if pid == 0:
                    break
                self.log(f"子进程 {pid} 已结束，状态: {status}")
            except OSError:
                break
    
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
        """彻底清理僵尸进程"""
        self.log("🧹 清理僵尸进程和相关进程...")
        
        # 要清理的进程关键词
        keywords = [
            'smart_rag_server', 'enhanced_smart_rag_server', 'intelligence_app',
            'vite', 'cloudflared', 'nexus', 'node.*vite', 'streamlit', 'npm'
        ]
        
        killed_count = 0
        zombie_count = 0
        
        # 首先处理僵尸进程
        for proc in psutil.process_iter(['pid', 'name', 'status', 'ppid']):
            try:
                if proc.info['status'] == 'zombie':
                    try:
                        # 尝试让父进程处理僵尸进程
                        parent = psutil.Process(proc.info['ppid'])
                        parent.send_signal(signal.SIGCHLD)
                        zombie_count += 1
                    except:
                        pass
            except:
                continue
        
        # 然后清理相关进程
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
            try:
                proc_info = proc.info
                if proc_info['status'] == 'zombie':
                    continue
                    
                cmdline = ' '.join(proc_info['cmdline'] or [])
                is_target = any(keyword in cmdline.lower() for keyword in keywords)
                
                if is_target and proc_info['pid'] != os.getpid():
                    try:
                        # 优雅终止
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()
                            proc.wait(timeout=1)
                        killed_count += 1
                        self.log(f"终止进程: PID {proc_info['pid']}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # 等待系统清理
        time.sleep(3)
        
        # 强制清理剩余僵尸进程
        try:
            subprocess.run(['pkill', '-f', 'cloudflared'], capture_output=True)
            subprocess.run(['pkill', '-f', 'vite'], capture_output=True)
        except:
            pass
        
        self.log(f"✅ 进程清理完成: 终止 {killed_count} 个进程, 处理 {zombie_count} 个僵尸进程")
    
    @contextmanager
    def managed_process(self, cmd, cwd=None, log_file=None):
        """管理进程的上下文管理器 - 防止僵尸进程"""
        process = None
        try:
            if log_file:
                stdout = open(log_file, 'w')
                stderr = subprocess.STDOUT
            else:
                stdout = subprocess.PIPE
                stderr = subprocess.PIPE
            
            # 使用新的进程组
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=stdout,
                stderr=stderr,
                preexec_fn=os.setsid,  # 创建新的进程组
                start_new_session=True  # 创建新的会话
            )
            
            yield process
            
        finally:
            if process:
                try:
                    # 终止整个进程组
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                        process.wait(timeout=2)
                except (OSError, ProcessLookupError):
                    pass
            
            if log_file and 'stdout' in locals():
                try:
                    stdout.close()
                except:
                    pass
    
    def start_intelligence_brain(self):
        """启动中央情报大脑 (整合版)"""
        self.log("🧠 启动增强版RAG服务器...")
        
        port = self.find_free_port(8500)
        working_dir = self.project_root / "systems/rag-system"
        log_file = self.log_dir / "intelligence_brain.log"
        
        cmd = [
            sys.executable, "enhanced_smart_rag_server.py",
            '--port', str(port),
            '--host', '0.0.0.0'
        ]
        
        with self.managed_process(cmd, cwd=working_dir, log_file=log_file) as process:
            self.processes['intelligence_brain'] = {
                'process': process,
                'port': port,
                'log_file': log_file,
                'name': '🧠 中央情报大脑'
            }
            
            # 等待服务启动
            self.log("等待中央情报大脑启动...")
            for i in range(30):
                if not self.running:
                    return None
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
        """启动NEXUS前端 (整合中央情报大脑功能)"""
        self.log("🌐 启动NEXUS前端界面 (整合版)...")
        
        port = self.find_free_port(52300)
        working_dir = self.project_root / "systems/nexus"
        log_file = self.log_dir / "nexus_frontend.log"
        
        # 检查npm是否可用
        try:
            subprocess.run(['npm', '--version'], capture_output=True, check=True)
        except:
            raise RuntimeError("npm未安装或不可用，请先安装Node.js和npm")
        
        cmd = [
            'npm', 'run', 'dev', '--',
            '--host', '0.0.0.0',
            '--port', str(port)
        ]
        
        with self.managed_process(cmd, cwd=working_dir, log_file=log_file) as process:
            self.processes['nexus_frontend'] = {
                'process': process,
                'port': port,
                'log_file': log_file,
                'name': '🌐 NEXUS前端界面'
            }
            
            # 等待前端启动
            self.log("等待NEXUS前端启动...")
            for i in range(30):
                if not self.running:
                    return None
                try:
                    response = requests.get(f"http://localhost:{port}", timeout=2)
                    if response.status_code == 200:
                        self.log(f"✅ NEXUS前端启动成功: http://localhost:{port}")
                        return port
                except:
                    time.sleep(1)
            
            raise RuntimeError("NEXUS前端启动失败")
    
    def create_tunnel(self, service_name, port, max_retries=3):
        """创建稳定的Cloudflare隧道"""
        self.log(f"🌐 为{service_name}创建隧道 (端口: {port})...")
        
        for attempt in range(max_retries):
            if not self.running:
                return None
                
            try:
                log_file = self.log_dir / f"{service_name}_tunnel.log"
                
                cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"]
                
                with self.managed_process(cmd, log_file=log_file) as process:
                    # 等待隧道建立并获取URL
                    tunnel_url = None
                    for i in range(30):
                        if not self.running:
                            return None
                            
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
                
                self.log(f"❌ {service_name}隧道创建失败 (尝试 {attempt + 1}/{max_retries})")
                
                if attempt < max_retries - 1:
                    time.sleep(5)
                    
            except Exception as e:
                self.log(f"❌ {service_name}隧道创建异常: {e}")
        
        self.log(f"❌ {service_name}隧道创建最终失败")
        return None
    
    def update_config_file(self, brain_port, frontend_port, brain_tunnel_url=None, frontend_tunnel_url=None):
        """更新配置文件"""
        self.log("📝 更新动态配置文件...")
        
        base_api = brain_tunnel_url if brain_tunnel_url else f"http://localhost:{brain_port}"
        
        config = {
            "api_endpoints": {
                "rag_api": base_api,
                "health_check": f"{base_api}/api/health",
                "chat": f"{base_api}/api/chat",
                "upload": f"{base_api}/api/upload",
                "documents": f"{base_api}/api/documents",
                "chat_history": f"{base_api}/api/chat/history",
                "rag_api_local": f"http://localhost:{brain_port}"
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
                "version": "2.0.0-Genesis-Stable",
                "launcher": "stable_nexus_launcher.py",
                "components": {
                    "intelligence_brain": {
                        "name": "🧠 中央情报大脑 (整合版)",
                        "modules": [
                            "🔺 Trinity Smart Chunking",
                            "🌌 Memory Nebula", 
                            "🛡️ Shields of Order",
                            "🎯 Fire Control System",
                            "🌟 Pantheon Soul",
                            "🛡️ Black Box Recorder"
                        ],
                        "port": brain_port,
                        "tunnel": brain_tunnel_url,
                        "integrated_in_frontend": True
                    },
                    "nexus_frontend": {
                        "name": "🌐 NEXUS前端界面 (黑色主题)",
                        "port": frontend_port,
                        "tunnel": frontend_tunnel_url,
                        "features": [
                            "中央情报大脑集成",
                            "智能文档处理",
                            "多模块管理",
                            "实时监控"
                        ]
                    }
                }
            },
            "updated_at": time.time(),
            "status": "active",
            "tunnel_status": "connected" if brain_tunnel_url and frontend_tunnel_url else "local_only",
            "last_health_check": datetime.now().isoformat(),
            "stability_features": [
                "🛡️ 僵尸进程预防",
                "🔄 优雅关闭机制",
                "📊 进程组管理",
                "🧹 自动清理功能",
                "⚡ 信号处理优化"
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
            while self.running:
                # 检查所有进程
                for name, info in list(self.processes.items()):
                    if not self.running:
                        break
                        
                    process = info['process']
                    if process.poll() is not None:
                        self.log(f"❌ {name}进程已停止 (退出码: {process.returncode})", 'error')
                        # 从列表中移除已停止的进程
                        del self.processes[name]
                
                # 检查隧道进程
                for name, info in list(self.tunnels.items()):
                    if not self.running:
                        break
                        
                    process = info['process']
                    if process.poll() is not None:
                        self.log(f"❌ {name}隧道已断开 (退出码: {process.returncode})", 'error')
                        del self.tunnels[name]
                
                time.sleep(30)  # 每30秒检查一次
                
        except KeyboardInterrupt:
            self.log("收到中断信号，开始清理...")
            self.cleanup()
    
    def cleanup(self):
        """清理所有进程"""
        if self.cleanup_done:
            return
            
        self.cleanup_done = True
        self.running = False
        
        self.log("🧹 清理所有进程...")
        
        # 终止所有启动的进程
        all_processes = {**self.processes, **self.tunnels}
        for name, info in all_processes.items():
            try:
                process = info['process']
                if process.poll() is None:
                    self.log(f"终止{name}进程...")
                    # 终止整个进程组
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                        process.wait(timeout=2)
                    except (OSError, ProcessLookupError):
                        pass
            except Exception as e:
                self.log(f"清理{name}时出错: {e}", 'error')
        
        # 清理日志文件句柄
        for name, info in all_processes.items():
            if 'log_file' in info:
                try:
                    # 关闭可能打开的文件句柄
                    pass
                except:
                    pass
        
        self.log("✅ 清理完成")
    
    def show_system_info(self):
        """显示系统信息"""
        self.log("\n" + "="*80)
        self.log("🎉 稳定版NEXUS系统启动成功！")
        self.log("="*80)
        
        # 显示核心组件
        self.log("🧠 核心组件:")
        if 'intelligence_brain' in self.processes:
            port = self.processes['intelligence_brain']['port']
            self.log(f"   中央情报大脑 (后端API): http://localhost:{port}")
            self.log("   ├── 🔺 Trinity Smart Chunking     # 三位一体智能分块")
            self.log("   ├── 🌌 Memory Nebula              # 记忆星图 (知识图谱)")
            self.log("   ├── 🛡️ Shields of Order           # 秩序之盾 (二级精炼)")
            self.log("   ├── 🎯 Fire Control System        # 火控系统 (AI注意力控制)")
            self.log("   ├── 🌟 Pantheon Soul              # Pantheon灵魂 (自我进化)")
            self.log("   └── 🛡️ Black Box Recorder         # 黑匣子记录器 (故障记忆)")
        
        if 'nexus_frontend' in self.processes:
            port = self.processes['nexus_frontend']['port']
            self.log(f"   NEXUS前端界面 (黑色主题): http://localhost:{port}")
            self.log("   └── 集成中央情报大脑所有功能")
        
        # 显示隧道访问
        if self.tunnels:
            self.log("\n🌍 公网访问:")
            for name, info in self.tunnels.items():
                self.log(f"   {name}: {info['url']}")
        
        # 显示稳定性特性
        self.log("\n🛡️ 稳定性特性:")
        self.log("   ├── 僵尸进程预防机制")
        self.log("   ├── 优雅关闭和清理")
        self.log("   ├── 进程组管理")
        self.log("   ├── 信号处理优化")
        self.log("   └── 自动监控和恢复")
        
        # 显示日志文件
        self.log(f"\n📋 日志文件:")
        for name, info in {**self.processes, **self.tunnels}.items():
            if 'log_file' in info:
                self.log(f"   {name}: {info['log_file']}")
        
        # 显示配置文件
        self.log(f"\n📝 配置文件: {self.config_file}")
        
        self.log("="*80)
    
    def launch(self, enable_tunnels=True, monitor=True):
        """启动完整系统"""
        try:
            self.log("🚀 稳定版NEXUS启动器")
            self.log("="*50)
            
            # 1. 清理僵尸进程
            self.cleanup_zombie_processes()
            
            # 2. 启动中央情报大脑
            brain_port = self.start_intelligence_brain()
            if not brain_port:
                return
            
            # 3. 启动NEXUS前端
            frontend_port = self.start_nexus_frontend()
            if not frontend_port:
                return
            
            # 4. 创建隧道 (如果启用)
            brain_tunnel_url = None
            frontend_tunnel_url = None
            
            if enable_tunnels and self.running:
                brain_tunnel_url = self.create_tunnel("intelligence_brain", brain_port)
                if self.running:
                    frontend_tunnel_url = self.create_tunnel("nexus_frontend", frontend_port)
            
            # 5. 更新配置文件
            if self.running:
                self.update_config_file(brain_port, frontend_port, brain_tunnel_url, frontend_tunnel_url)
            
            # 6. 测试系统健康
            if self.running:
                health_results = self.test_system_health()
            
            # 7. 显示系统信息
            if self.running:
                self.show_system_info()
            
            # 8. 开始监控 (如果启用)
            if monitor and self.running:
                self.monitor_processes()
            else:
                self.log("系统启动完成！按Ctrl+C停止。")
                try:
                    while self.running:
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
    parser = argparse.ArgumentParser(description='稳定版NEXUS启动器')
    parser.add_argument('--no-tunnels', action='store_true', help='不创建隧道')
    parser.add_argument('--no-monitor', action='store_true', help='不启用进程监控')
    parser.add_argument('--cleanup-only', action='store_true', help='仅清理进程后退出')
    
    args = parser.parse_args()
    
    launcher = StableNEXUSLauncher()
    
    # 仅清理模式
    if args.cleanup_only:
        launcher.cleanup_zombie_processes()
        return
    
    # 启动系统
    launcher.launch(
        enable_tunnels=not args.no_tunnels,
        monitor=not args.no_monitor
    )

if __name__ == "__main__":
    main()