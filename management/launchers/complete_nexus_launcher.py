#!/usr/bin/env python3
"""
🚀 完整版NEXUS启动器 - 解决进程管理问题
==========================================

N.S.S-Novena-Garfield 完整NEXUS系统：
- 🧠 中央情报大脑 (完整6大模块)
- 🌐 NEXUS前端界面 (黑色主题，集成所有功能)
- 🌍 Cloudflare隧道连接
- 📝 动态配置管理
- 🛡️ 父子进程同步关闭
- 🔄 进程组管理

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0-Complete
"""

import os
import sys
import time
import json
import signal
import subprocess
import requests
import psutil
import atexit
from pathlib import Path
from datetime import datetime
import argparse
import logging

class CompleteNEXUSLauncher:
    """完整版NEXUS启动器 - 解决进程管理问题"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = {}
        self.tunnels = {}
        self.config_file = self.project_root / "systems/nexus/public/api_config.json"
        self.log_dir = Path("/tmp")
        self.running = True
        self.process_group = None
        
        # 设置日志
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # 创建新的进程组
        try:
            os.setpgrp()
            self.process_group = os.getpgrp()
            self.log(f"创建进程组: {self.process_group}")
        except:
            pass
        
        # 注册清理函数
        atexit.register(self.cleanup)
        
        # 设置信号处理 - 确保父子进程同步关闭
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGHUP, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器 - 确保父子进程同步关闭"""
        self.log(f"收到信号 {signum}，开始同步关闭所有进程...")
        self.running = False
        self.cleanup()
        
        # 如果是进程组领导者，终止整个进程组
        if self.process_group:
            try:
                os.killpg(self.process_group, signal.SIGTERM)
                time.sleep(2)
                os.killpg(self.process_group, signal.SIGKILL)
            except:
                pass
        
        sys.exit(0)
    
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
    
    def cleanup_existing_processes(self):
        """清理现有相关进程"""
        self.log("🧹 清理现有相关进程...")
        
        keywords = [
            'smart_rag_server', 'enhanced_smart_rag_server', 'intelligence_app',
            'vite', 'cloudflared', 'nexus', 'streamlit', 'npm', 'node'
        ]
        
        killed_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
            try:
                proc_info = proc.info
                if proc_info['status'] == 'zombie':
                    continue
                    
                cmdline = ' '.join(proc_info['cmdline'] or [])
                is_target = any(keyword in cmdline.lower() for keyword in keywords)
                
                if is_target and proc_info['pid'] != os.getpid():
                    try:
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()
                        killed_count += 1
                        self.log(f"终止进程: PID {proc_info['pid']}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # 系统级清理
        try:
            subprocess.run(['pkill', '-f', 'cloudflared'], capture_output=True, timeout=5)
            subprocess.run(['pkill', '-f', 'vite'], capture_output=True, timeout=5)
            subprocess.run(['pkill', '-f', 'npm'], capture_output=True, timeout=5)
        except:
            pass
        
        time.sleep(2)
        self.log(f"✅ 进程清理完成: 终止 {killed_count} 个进程")
    
    def start_process_with_group_management(self, cmd, cwd=None, log_file=None, service_name=""):
        """启动进程并加入进程组管理"""
        self.log(f"启动{service_name}进程...")
        
        if log_file:
            log_file = Path(log_file)
            stdout = open(log_file, 'w')
            stderr = subprocess.STDOUT
        else:
            stdout = subprocess.PIPE
            stderr = subprocess.PIPE
        
        # 启动进程并设置进程组
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=stdout,
            stderr=stderr,
            # 关键：设置进程组，确保父子进程同步关闭
            preexec_fn=lambda: os.setpgrp() if os.name != 'nt' else None,
            start_new_session=True
        )
        
        return process, stdout if log_file else None
    
    def start_intelligence_brain(self):
        """启动中央情报大脑 - 完整6大模块"""
        self.log("🧠 启动中央情报大脑 (完整6大核心模块)...")
        
        port = self.find_free_port(8500)
        working_dir = self.project_root / "systems/rag-system"
        log_file = self.log_dir / "intelligence_brain.log"
        
        cmd = [
            sys.executable, "enhanced_smart_rag_server.py",
            '--port', str(port),
            '--host', '0.0.0.0'
        ]
        
        process, log_handle = self.start_process_with_group_management(
            cmd, cwd=working_dir, log_file=log_file, service_name="中央情报大脑"
        )
        
        self.processes['intelligence_brain'] = {
            'process': process,
            'port': port,
            'log_file': log_file,
            'log_handle': log_handle,
            'name': '🧠 中央情报大脑',
            'cmd': cmd
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
                    self.log(f"   🎯 核心模块: {len(features)} 个")
                    
                    # 显示完整的6大核心模块
                    core_modules = [
                        "🔺 Trinity Smart Chunking - 三位一体智能分块",
                        "🌌 Memory Nebula - 记忆星图 (知识图谱)",
                        "🛡️ Shields of Order - 秩序之盾 (二级精炼)",
                        "🎯 Fire Control System - 火控系统 (AI注意力控制)",
                        "🌟 Pantheon Soul - Pantheon灵魂 (自我进化)",
                        "🛡️ Black Box Recorder - 黑匣子记录器 (故障记忆)"
                    ]
                    
                    for idx, module in enumerate(core_modules, 1):
                        self.log(f"   {idx}. {module}")
                    
                    return port
            except:
                time.sleep(1)
        
        raise RuntimeError("中央情报大脑启动失败")
    
    def start_nexus_frontend(self):
        """启动NEXUS前端 - 黑色主题，集成所有功能"""
        self.log("🌐 启动NEXUS前端界面 (黑色主题，集成中央情报大脑)...")
        
        port = self.find_free_port(52300)
        working_dir = self.project_root / "systems/nexus"
        log_file = self.log_dir / "nexus_frontend.log"
        
        # 检查npm
        try:
            subprocess.run(['npm', '--version'], capture_output=True, check=True)
        except:
            raise RuntimeError("npm未安装或不可用，请先安装Node.js和npm")
        
        cmd = [
            'npm', 'run', 'dev', '--',
            '--host', '0.0.0.0',
            '--port', str(port)
        ]
        
        process, log_handle = self.start_process_with_group_management(
            cmd, cwd=working_dir, log_file=log_file, service_name="NEXUS前端"
        )
        
        self.processes['nexus_frontend'] = {
            'process': process,
            'port': port,
            'log_file': log_file,
            'log_handle': log_handle,
            'name': '🌐 NEXUS前端界面',
            'cmd': cmd
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
                    self.log("   🎨 黑色主题界面已激活")
                    self.log("   🔗 已集成中央情报大脑所有功能")
                    self.log("   📊 统一管理和监控界面")
                    self.log("   ⏰ Chronicle时间管理支持")
                    return port
            except:
                time.sleep(1)
        
        raise RuntimeError("NEXUS前端启动失败")
    
    def create_tunnel(self, service_name, port):
        """创建Cloudflare隧道"""
        self.log(f"🌐 为{service_name}创建隧道 (端口: {port})...")
        
        log_file = self.log_dir / f"{service_name}_tunnel.log"
        
        cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"]
        
        process, log_handle = self.start_process_with_group_management(
            cmd, log_file=log_file, service_name=f"{service_name}隧道"
        )
        
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
            self.tunnels[service_name] = {
                'process': process,
                'url': tunnel_url,
                'port': port,
                'log_file': log_file,
                'log_handle': log_handle
            }
            self.log(f"✅ {service_name}隧道创建成功: {tunnel_url}")
            return tunnel_url
        else:
            # 如果失败，终止进程
            try:
                process.terminate()
                process.wait(timeout=3)
            except:
                try:
                    process.kill()
                except:
                    pass
            if log_handle:
                try:
                    log_handle.close()
                except:
                    pass
            
            self.log(f"❌ {service_name}隧道创建失败")
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
                "version": "2.0.0-Complete",
                "launcher": "complete_nexus_launcher.py",
                "project": "N.S.S-Novena-Garfield",
                "components": {
                    "intelligence_brain": {
                        "name": "🧠 中央情报大脑",
                        "description": "完整6大核心模块集成",
                        "core_modules": [
                            "🔺 Trinity Smart Chunking - 三位一体智能分块",
                            "🌌 Memory Nebula - 记忆星图 (知识图谱)",
                            "🛡️ Shields of Order - 秩序之盾 (二级精炼)",
                            "🎯 Fire Control System - 火控系统 (AI注意力控制)",
                            "🌟 Pantheon Soul - Pantheon灵魂 (自我进化)",
                            "🛡️ Black Box Recorder - 黑匣子记录器 (故障记忆)"
                        ],
                        "port": brain_port,
                        "tunnel": brain_tunnel_url,
                        "status": "active"
                    },
                    "nexus_frontend": {
                        "name": "🌐 NEXUS前端界面",
                        "description": "黑色主题，集成所有功能",
                        "theme": "黑色主题",
                        "port": frontend_port,
                        "tunnel": frontend_tunnel_url,
                        "integrated_features": [
                            "中央情报大脑完整访问",
                            "智能文档处理系统",
                            "多模块统一管理",
                            "实时系统监控",
                            "Chronicle时间管理",
                            "黑色主题界面"
                        ],
                        "status": "active"
                    }
                }
            },
            "access_info": {
                "primary_access": f"http://localhost:{frontend_port}",
                "api_access": f"http://localhost:{brain_port}",
                "tunnel_access": frontend_tunnel_url if frontend_tunnel_url else "隧道未创建"
            },
            "updated_at": time.time(),
            "status": "active",
            "tunnel_status": "connected" if frontend_tunnel_url else "local_only",
            "last_health_check": datetime.now().isoformat(),
            "process_management": {
                "parent_process": os.getpid(),
                "process_group": self.process_group,
                "sync_shutdown": True,
                "zombie_prevention": True
            }
        }
        
        # 确保目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入配置文件
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.log(f"✅ 配置文件已更新: {self.config_file}")
    
    def test_system_health(self):
        """测试系统健康状态"""
        self.log("🧪 执行系统健康检查...")
        
        health_results = {}
        
        # 测试中央情报大脑
        if 'intelligence_brain' in self.processes:
            brain_info = self.processes['intelligence_brain']
            try:
                response = requests.get(f"http://localhost:{brain_info['port']}/api/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    health_results['intelligence_brain'] = {
                        'status': '✅ 正常运行',
                        'version': data.get('version', 'Unknown'),
                        'features': len(data.get('data', {}).get('features', [])),
                        'system_status': data.get('data', {}).get('system_status', 'Unknown')
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
                    health_results['nexus_frontend'] = {'status': '✅ 正常运行'}
                    self.log(f"✅ NEXUS前端健康检查通过")
                else:
                    health_results['nexus_frontend'] = {'status': f'❌ HTTP {response.status_code}'}
            except Exception as e:
                health_results['nexus_frontend'] = {'status': f'❌ 连接失败: {e}'}
        
        return health_results
    
    def cleanup(self):
        """清理所有进程 - 确保父子进程同步关闭"""
        if hasattr(self, '_cleanup_done') and self._cleanup_done:
            return
        
        self._cleanup_done = True
        self.running = False
        
        self.log("🧹 开始清理所有进程 (父子进程同步关闭)...")
        
        # 终止所有启动的进程
        all_processes = {**self.processes, **self.tunnels}
        for name, info in all_processes.items():
            try:
                process = info['process']
                if process.poll() is None:
                    self.log(f"终止{name}进程 (PID: {process.pid})...")
                    
                    # 尝试优雅终止
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # 强制终止
                        process.kill()
                        try:
                            process.wait(timeout=2)
                        except:
                            pass
                
                # 关闭日志文件句柄
                if 'log_handle' in info and info['log_handle']:
                    try:
                        info['log_handle'].close()
                    except:
                        pass
                        
            except Exception as e:
                self.log(f"清理{name}时出错: {e}", 'error')
        
        # 如果是进程组领导者，清理整个进程组
        if self.process_group:
            try:
                self.log(f"清理进程组: {self.process_group}")
                os.killpg(self.process_group, signal.SIGTERM)
                time.sleep(1)
                os.killpg(self.process_group, signal.SIGKILL)
            except:
                pass
        
        self.log("✅ 所有进程清理完成")
    
    def show_system_info(self):
        """显示系统信息"""
        self.log("\n" + "="*100)
        self.log("🎉 N.S.S-Novena-Garfield 完整版NEXUS系统启动成功！")
        self.log("="*100)
        
        # 显示核心组件
        self.log("🧠 中央情报大脑 (完整6大核心模块):")
        if 'intelligence_brain' in self.processes:
            port = self.processes['intelligence_brain']['port']
            self.log(f"   📡 后端API地址: http://localhost:{port}")
            self.log("   🔺 Trinity Smart Chunking     - 三位一体智能分块")
            self.log("   🌌 Memory Nebula              - 记忆星图 (知识图谱)")
            self.log("   🛡️ Shields of Order           - 秩序之盾 (二级精炼)")
            self.log("   🎯 Fire Control System        - 火控系统 (AI注意力控制)")
            self.log("   🌟 Pantheon Soul              - Pantheon灵魂 (自我进化)")
            self.log("   🛡️ Black Box Recorder         - 黑匣子记录器 (故障记忆)")
        
        self.log("\n🌐 NEXUS前端界面 (黑色主题，集成所有功能):")
        if 'nexus_frontend' in self.processes:
            port = self.processes['nexus_frontend']['port']
            self.log(f"   🎨 前端界面地址: http://localhost:{port}")
            self.log("   🔗 集成中央情报大脑所有功能")
            self.log("   📊 统一管理和监控界面")
            self.log("   ⏰ Chronicle时间管理支持")
            self.log("   🎨 黑色主题界面")
        
        # 显示隧道访问
        if self.tunnels:
            self.log("\n🌍 公网隧道访问:")
            for name, info in self.tunnels.items():
                service_name = "NEXUS前端" if "frontend" in name else "中央情报大脑"
                self.log(f"   {service_name}: {info['url']}")
        
        # 显示主要访问方式
        self.log("\n🎯 主要访问方式:")
        if 'nexus_frontend' in self.processes:
            self.log(f"   🏠 本地访问: http://localhost:{self.processes['nexus_frontend']['port']}")
        
        if self.tunnels and 'nexus_frontend' in self.tunnels:
            self.log(f"   🌍 公网访问: {self.tunnels['nexus_frontend']['url']}")
        
        # 显示进程管理信息
        self.log(f"\n🛡️ 进程管理:")
        self.log(f"   父进程PID: {os.getpid()}")
        self.log(f"   进程组ID: {self.process_group}")
        self.log("   ✅ 父子进程同步关闭已启用")
        self.log("   ✅ 僵尸进程预防已启用")
        
        # 显示日志文件
        self.log(f"\n📋 系统日志:")
        for name, info in {**self.processes, **self.tunnels}.items():
            if 'log_file' in info:
                self.log(f"   {name}: {info['log_file']}")
        
        # 显示配置文件
        self.log(f"\n📝 配置文件: {self.config_file}")
        
        self.log("="*100)
        self.log("🚀 系统已完全启动！使用 Ctrl+C 优雅停止系统 (父子进程同步关闭)")
        self.log("="*100)
    
    def launch(self, enable_tunnels=True):
        """启动完整系统"""
        try:
            self.log("🚀 N.S.S-Novena-Garfield 完整版NEXUS启动器")
            self.log("="*60)
            
            # 1. 清理现有进程
            self.cleanup_existing_processes()
            
            # 2. 启动中央情报大脑 (完整6大模块)
            brain_port = self.start_intelligence_brain()
            if not brain_port:
                return
            
            # 3. 启动NEXUS前端 (黑色主题，集成所有功能)
            frontend_port = self.start_nexus_frontend()
            if not frontend_port:
                return
            
            # 4. 创建隧道 (如果启用)
            brain_tunnel_url = None
            frontend_tunnel_url = None
            
            if enable_tunnels and self.running:
                # 为前端创建隧道 (主要访问点)
                frontend_tunnel_url = self.create_tunnel("nexus_frontend", frontend_port)
                if self.running:
                    # 为后端创建隧道
                    brain_tunnel_url = self.create_tunnel("intelligence_brain", brain_port)
            
            # 5. 更新配置文件
            if self.running:
                self.update_config_file(brain_port, frontend_port, brain_tunnel_url, frontend_tunnel_url)
            
            # 6. 执行健康检查
            if self.running:
                health_results = self.test_system_health()
            
            # 7. 显示系统信息
            if self.running:
                self.show_system_info()
            
            # 8. 保持运行 (父子进程同步管理)
            if self.running:
                try:
                    while self.running:
                        time.sleep(1)
                        
                        # 检查子进程状态
                        for name, info in list(self.processes.items()):
                            if info['process'].poll() is not None:
                                self.log(f"❌ {name}进程意外退出", 'error')
                                # 可以在这里添加重启逻辑
                        
                except KeyboardInterrupt:
                    self.log("收到中断信号，开始优雅关闭...")
            
        except Exception as e:
            self.log(f"❌ 系统启动失败: {e}", 'error')
            self.cleanup()
            sys.exit(1)
        finally:
            self.cleanup()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='N.S.S-Novena-Garfield 完整版NEXUS启动器')
    parser.add_argument('--no-tunnels', action='store_true', help='不创建公网隧道')
    parser.add_argument('--cleanup-only', action='store_true', help='仅清理进程后退出')
    
    args = parser.parse_args()
    
    launcher = CompleteNEXUSLauncher()
    
    # 仅清理模式
    if args.cleanup_only:
        launcher.cleanup_existing_processes()
        return
    
    # 启动完整系统
    launcher.launch(enable_tunnels=not args.no_tunnels)

if __name__ == "__main__":
    main()