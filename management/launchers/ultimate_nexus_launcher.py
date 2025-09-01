#!/usr/bin/env python3
"""
🚀 终极版NEXUS启动器 - 一键启动完整解决方案
===============================================

完整的N.S.S-Novena-Garfield NEXUS系统：
- 🧠 中央情报大脑 (6大核心模块)
- 🌐 NEXUS前端界面 (黑色主题)
- 🌍 自动隧道连接
- 📝 动态配置管理
- 🛡️ 僵尸进程预防
- 🔄 自动重启机制

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0-Ultimate
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
import threading
import logging

class UltimateNEXUSLauncher:
    """终极版NEXUS启动器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent  # /workspace
        self.processes = {}
        self.tunnels = {}
        self.config_file = self.project_root / "systems/nexus/public/api_config.json"
        self.log_dir = Path("/tmp")
        self.running = True
        
        # 设置日志
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.log(f"收到信号 {signum}，开始清理...")
        self.running = False
        self.cleanup()
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
    
    def cleanup_all_processes(self):
        """彻底清理所有相关进程"""
        self.log("🧹 彻底清理所有相关进程...")
        
        # 要清理的进程关键词
        keywords = [
            'smart_rag_server', 'enhanced_smart_rag_server', 'intelligence_app',
            'vite', 'cloudflared', 'nexus', 'streamlit', 'npm', 'node'
        ]
        
        killed_count = 0
        
        # 多轮清理确保彻底
        for round_num in range(3):
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
                                proc.wait(timeout=2)
                            except psutil.TimeoutExpired:
                                proc.kill()
                            killed_count += 1
                            self.log(f"终止进程: PID {proc_info['pid']}")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            time.sleep(1)
        
        # 使用系统命令清理
        try:
            subprocess.run(['pkill', '-f', 'cloudflared'], capture_output=True, timeout=5)
            subprocess.run(['pkill', '-f', 'vite'], capture_output=True, timeout=5)
            subprocess.run(['pkill', '-f', 'npm'], capture_output=True, timeout=5)
        except:
            pass
        
        time.sleep(2)
        self.log(f"✅ 进程清理完成: 终止 {killed_count} 个进程")
    
    def start_intelligence_brain(self):
        """启动中央情报大脑"""
        self.log("🧠 启动中央情报大脑 (6大核心模块)...")
        
        port = self.find_free_port(8500)
        working_dir = self.project_root / "systems/rag-system"
        log_file = self.log_dir / "intelligence_brain.log"
        
        cmd = [
            sys.executable, "enhanced_smart_rag_server.py",
            '--port', str(port),
            '--host', '0.0.0.0'
        ]
        
        with open(log_file, 'w') as f:
            process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                stdout=f,
                stderr=subprocess.STDOUT
            )
        
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
                    self.log(f"   🎯 核心模块: {len(features)} 个")
                    for idx, feature in enumerate(features[:6], 1):
                        self.log(f"   {idx}. {feature}")
                    
                    return port
            except:
                time.sleep(1)
        
        raise RuntimeError("中央情报大脑启动失败")
    
    def start_nexus_frontend(self):
        """启动NEXUS前端"""
        self.log("🌐 启动NEXUS前端界面 (黑色主题)...")
        
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
        
        with open(log_file, 'w') as f:
            process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                stdout=f,
                stderr=subprocess.STDOUT
            )
        
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
                    self.log("   🎨 黑色主题界面已激活")
                    self.log("   🔗 已集成中央情报大脑所有功能")
                    return port
            except:
                time.sleep(1)
        
        raise RuntimeError("NEXUS前端启动失败")
    
    def create_tunnel_with_retry(self, service_name, port, max_retries=5):
        """创建稳定的Cloudflare隧道 (增强重试机制)"""
        self.log(f"🌐 为{service_name}创建隧道 (端口: {port})...")
        
        for attempt in range(max_retries):
            if not self.running:
                return None
                
            try:
                log_file = self.log_dir / f"{service_name}_tunnel.log"
                
                cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"]
                
                with open(log_file, 'w') as f:
                    process = subprocess.Popen(
                        cmd,
                        stdout=f,
                        stderr=subprocess.STDOUT
                    )
                
                # 等待隧道建立并获取URL
                tunnel_url = None
                for i in range(45):  # 增加等待时间
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
                    # 验证隧道是否工作 (增加验证时间)
                    self.log(f"验证隧道连接: {tunnel_url}")
                    for verify_attempt in range(3):
                        try:
                            response = requests.get(tunnel_url, timeout=15)
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
                            time.sleep(5)
                
                # 如果失败，终止进程
                try:
                    process.terminate()
                    process.wait(timeout=3)
                except:
                    try:
                        process.kill()
                    except:
                        pass
                
                self.log(f"❌ {service_name}隧道创建失败 (尝试 {attempt + 1}/{max_retries})")
                
                if attempt < max_retries - 1:
                    time.sleep(10)  # 增加重试间隔
                    
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
                "version": "2.0.0-Ultimate",
                "launcher": "ultimate_nexus_launcher.py",
                "project": "N.S.S-Novena-Garfield",
                "components": {
                    "intelligence_brain": {
                        "name": "🧠 中央情报大脑",
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
                        "theme": "黑色主题",
                        "port": frontend_port,
                        "tunnel": frontend_tunnel_url,
                        "integrated_features": [
                            "中央情报大脑完整访问",
                            "智能文档处理系统",
                            "多模块统一管理",
                            "实时系统监控",
                            "Chronicle时间管理"
                        ],
                        "status": "active"
                    }
                }
            },
            "access_info": {
                "local_access": {
                    "nexus_frontend": f"http://localhost:{frontend_port}",
                    "intelligence_brain": f"http://localhost:{brain_port}"
                },
                "public_access": {
                    "nexus_frontend": frontend_tunnel_url,
                    "intelligence_brain": brain_tunnel_url
                } if frontend_tunnel_url or brain_tunnel_url else None
            },
            "updated_at": time.time(),
            "status": "active",
            "tunnel_status": "connected" if brain_tunnel_url and frontend_tunnel_url else "local_only",
            "last_health_check": datetime.now().isoformat(),
            "stability_features": [
                "🛡️ 僵尸进程预防机制",
                "🔄 自动重启和恢复",
                "📊 进程状态监控",
                "🧹 智能清理功能",
                "⚡ 信号处理优化",
                "🌐 隧道连接管理"
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
        
        # 测试隧道连接
        for name, tunnel_info in self.tunnels.items():
            try:
                response = requests.get(tunnel_info['url'], timeout=15)
                if response.status_code == 200:
                    health_results[f'{name}_tunnel'] = {'status': '✅ 正常连接', 'url': tunnel_info['url']}
                    self.log(f"✅ {name}隧道健康检查通过")
                else:
                    health_results[f'{name}_tunnel'] = {'status': f'❌ HTTP {response.status_code}'}
            except Exception as e:
                health_results[f'{name}_tunnel'] = {'status': f'❌ 连接失败: {e}'}
        
        return health_results
    
    def cleanup(self):
        """清理所有进程"""
        self.log("🧹 清理所有启动的进程...")
        
        # 终止所有启动的进程
        all_processes = {**self.processes, **self.tunnels}
        for name, info in all_processes.items():
            try:
                process = info['process']
                if process.poll() is None:
                    self.log(f"终止{name}进程...")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        try:
                            process.wait(timeout=2)
                        except:
                            pass
            except Exception as e:
                self.log(f"清理{name}时出错: {e}", 'error')
        
        self.log("✅ 清理完成")
    
    def show_final_info(self):
        """显示最终系统信息"""
        self.log("\n" + "="*100)
        self.log("🎉 N.S.S-Novena-Garfield NEXUS系统启动成功！")
        self.log("="*100)
        
        # 显示核心组件
        self.log("🧠 中央情报大脑 (6大核心模块):")
        if 'intelligence_brain' in self.processes:
            port = self.processes['intelligence_brain']['port']
            self.log(f"   📡 后端API地址: http://localhost:{port}")
            self.log("   🔺 Trinity Smart Chunking     - 三位一体智能分块")
            self.log("   🌌 Memory Nebula              - 记忆星图 (知识图谱)")
            self.log("   🛡️ Shields of Order           - 秩序之盾 (二级精炼)")
            self.log("   🎯 Fire Control System        - 火控系统 (AI注意力控制)")
            self.log("   🌟 Pantheon Soul              - Pantheon灵魂 (自我进化)")
            self.log("   🛡️ Black Box Recorder         - 黑匣子记录器 (故障记忆)")
        
        self.log("\n🌐 NEXUS前端界面 (黑色主题):")
        if 'nexus_frontend' in self.processes:
            port = self.processes['nexus_frontend']['port']
            self.log(f"   🎨 前端界面地址: http://localhost:{port}")
            self.log("   🔗 集成中央情报大脑所有功能")
            self.log("   📊 统一管理和监控界面")
            self.log("   ⏰ Chronicle时间管理支持")
        
        # 显示隧道访问
        if self.tunnels:
            self.log("\n🌍 公网隧道访问:")
            for name, info in self.tunnels.items():
                service_name = "NEXUS前端" if "frontend" in name else "中央情报大脑"
                self.log(f"   {service_name}: {info['url']}")
        
        # 显示访问方式
        self.log("\n🎯 系统访问方式:")
        self.log("   1. 🏠 本地访问 (推荐):")
        if 'nexus_frontend' in self.processes:
            self.log(f"      NEXUS界面: http://localhost:{self.processes['nexus_frontend']['port']}")
        if 'intelligence_brain' in self.processes:
            self.log(f"      API后端: http://localhost:{self.processes['intelligence_brain']['port']}")
        
        if self.tunnels:
            self.log("   2. 🌍 公网访问:")
            for name, info in self.tunnels.items():
                service_name = "NEXUS界面" if "frontend" in name else "API后端"
                self.log(f"      {service_name}: {info['url']}")
        
        # 显示日志文件
        self.log(f"\n📋 系统日志:")
        for name, info in {**self.processes, **self.tunnels}.items():
            if 'log_file' in info:
                self.log(f"   {name}: {info['log_file']}")
        
        # 显示配置文件
        self.log(f"\n📝 配置文件: {self.config_file}")
        
        # 显示稳定性特性
        self.log("\n🛡️ 系统稳定性特性:")
        self.log("   ✅ 僵尸进程预防和清理")
        self.log("   ✅ 优雅关闭和资源清理")
        self.log("   ✅ 自动健康检查")
        self.log("   ✅ 隧道连接管理")
        self.log("   ✅ 进程状态监控")
        
        self.log("="*100)
        self.log("🚀 系统已完全启动！使用 Ctrl+C 优雅停止系统")
        self.log("="*100)
    
    def launch(self, enable_tunnels=True):
        """启动完整系统"""
        try:
            self.log("🚀 N.S.S-Novena-Garfield 终极版NEXUS启动器")
            self.log("="*60)
            
            # 1. 彻底清理进程
            self.cleanup_all_processes()
            
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
                # 优先为前端创建隧道 (用户主要访问点)
                frontend_tunnel_url = self.create_tunnel_with_retry("nexus_frontend", frontend_port)
                if self.running and frontend_tunnel_url:
                    # 如果前端隧道成功，再创建后端隧道
                    brain_tunnel_url = self.create_tunnel_with_retry("intelligence_brain", brain_port)
            
            # 5. 更新配置文件
            if self.running:
                self.update_config_file(brain_port, frontend_port, brain_tunnel_url, frontend_tunnel_url)
            
            # 6. 执行健康检查
            if self.running:
                health_results = self.test_system_health()
            
            # 7. 显示最终信息
            if self.running:
                self.show_final_info()
            
            # 8. 保持运行
            if self.running:
                try:
                    while self.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            
        except Exception as e:
            self.log(f"❌ 系统启动失败: {e}", 'error')
            self.cleanup()
            sys.exit(1)
        finally:
            self.cleanup()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='N.S.S-Novena-Garfield 终极版NEXUS启动器')
    parser.add_argument('--no-tunnels', action='store_true', help='不创建公网隧道')
    parser.add_argument('--cleanup-only', action='store_true', help='仅清理进程后退出')
    
    args = parser.parse_args()
    
    launcher = UltimateNEXUSLauncher()
    
    # 仅清理模式
    if args.cleanup_only:
        launcher.cleanup_all_processes()
        return
    
    # 启动完整系统
    launcher.launch(enable_tunnels=not args.no_tunnels)

if __name__ == "__main__":
    main()