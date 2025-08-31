#!/usr/bin/env python3
"""
🚀 NEXUS启动器 - 简单有效的解决方案
==================================

N.S.S-Novena-Garfield NEXUS系统：
- 🧠 中央情报大脑 (完整6大模块)
- 🌐 NEXUS前端界面 (黑色主题)
- 🌍 Cloudflare隧道连接
- 🛡️ 父子进程同步关闭

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0-Simple
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

class NEXUSLauncher:
    """NEXUS启动器 - 简单有效"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = []
        self.config_file = self.project_root / "systems/nexus/public/api_config.json"
        self.running = True
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n收到信号 {signum}，开始清理...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def log(self, message):
        """日志输出"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def find_free_port(self, start_port=5000):
        """查找可用端口"""
        import socket
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise RuntimeError(f"无法找到可用端口")
    
    def cleanup_existing_processes(self):
        """清理现有进程"""
        self.log("🧹 清理现有相关进程...")
        
        keywords = ['smart_rag_server', 'enhanced_smart_rag_server', 'vite', 'cloudflared', 'npm', 'node']
        killed_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(keyword in cmdline.lower() for keyword in keywords) and proc.info['pid'] != os.getpid():
                    try:
                        proc.terminate()
                        proc.wait(timeout=3)
                        killed_count += 1
                    except:
                        try:
                            proc.kill()
                        except:
                            pass
            except:
                continue
        
        self.log(f"✅ 清理完成: 终止 {killed_count} 个进程")
    
    def start_intelligence_brain(self):
        """启动中央情报大脑"""
        self.log("🧠 启动中央情报大脑...")
        
        port = self.find_free_port(8500)
        working_dir = self.project_root / "systems/rag-system"
        
        cmd = [sys.executable, "enhanced_smart_rag_server.py", '--port', str(port), '--host', '0.0.0.0']
        
        # 使用新的会话组，确保父子进程同步关闭
        process = subprocess.Popen(
            cmd,
            cwd=working_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        self.processes.append(('intelligence_brain', process, port))
        
        # 等待启动
        for i in range(30):
            if not self.running:
                return None
            try:
                response = requests.get(f"http://localhost:{port}/api/health", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"✅ 中央情报大脑启动成功: http://localhost:{port}")
                    self.log(f"   版本: {data.get('version', 'Unknown')}")
                    self.log(f"   模块: {len(data.get('data', {}).get('features', []))} 个")
                    return port
            except:
                time.sleep(1)
        
        raise RuntimeError("中央情报大脑启动失败")
    
    def start_nexus_frontend(self):
        """启动NEXUS前端"""
        self.log("🌐 启动NEXUS前端界面...")
        
        port = self.find_free_port(52300)
        working_dir = self.project_root / "systems/nexus"
        
        cmd = ['npm', 'run', 'dev', '--', '--host', '0.0.0.0', '--port', str(port)]
        
        process = subprocess.Popen(
            cmd,
            cwd=working_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        self.processes.append(('nexus_frontend', process, port))
        
        # 等待启动
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
    
    def create_tunnel(self, service_name, port):
        """创建隧道"""
        self.log(f"🌐 为{service_name}创建隧道...")
        
        cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True
        )
        
        self.processes.append((f'{service_name}_tunnel', process, port))
        
        # 获取隧道URL
        tunnel_url = None
        for i in range(30):
            if not self.running:
                return None
            
            line = process.stdout.readline()
            if line:
                import re
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if match:
                    tunnel_url = match.group(0)
                    break
            time.sleep(1)
        
        if tunnel_url:
            self.log(f"✅ {service_name}隧道创建成功: {tunnel_url}")
            return tunnel_url
        else:
            self.log(f"❌ {service_name}隧道创建失败")
            return None
    
    def update_config_file(self, brain_port, frontend_port, brain_tunnel=None, frontend_tunnel=None):
        """更新配置文件"""
        self.log("📝 更新配置文件...")
        
        config = {
            "api_endpoints": {
                "rag_api": brain_tunnel or f"http://localhost:{brain_port}",
                "health_check": f"{brain_tunnel or f'http://localhost:{brain_port}'}/api/health",
                "chat": f"{brain_tunnel or f'http://localhost:{brain_port}'}/api/chat",
                "upload": f"{brain_tunnel or f'http://localhost:{brain_port}'}/api/upload",
                "documents": f"{brain_tunnel or f'http://localhost:{brain_port}'}/api/documents",
                "chat_history": f"{brain_tunnel or f'http://localhost:{brain_port}'}/api/chat/history"
            },
            "local_endpoints": {
                "intelligence_brain": f"http://localhost:{brain_port}",
                "nexus_frontend": f"http://localhost:{frontend_port}"
            },
            "tunnel_endpoints": {
                "intelligence_brain": brain_tunnel,
                "nexus_frontend": frontend_tunnel
            },
            "system_info": {
                "version": "2.0.0-Simple",
                "project": "N.S.S-Novena-Garfield",
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
                        "tunnel": brain_tunnel
                    },
                    "nexus_frontend": {
                        "name": "🌐 NEXUS前端界面",
                        "theme": "黑色主题",
                        "port": frontend_port,
                        "tunnel": frontend_tunnel
                    }
                }
            },
            "updated_at": time.time(),
            "status": "active"
        }
        
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.log(f"✅ 配置文件已更新")
    
    def cleanup(self):
        """清理所有进程"""
        self.log("🧹 清理所有进程...")
        
        for name, process, port in self.processes:
            try:
                if process.poll() is None:
                    # 终止进程组
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            except:
                try:
                    process.terminate()
                    process.wait(timeout=2)
                except:
                    try:
                        process.kill()
                    except:
                        pass
        
        self.log("✅ 清理完成")
    
    def show_info(self, brain_port, frontend_port, brain_tunnel=None, frontend_tunnel=None):
        """显示系统信息"""
        self.log("\n" + "="*80)
        self.log("🎉 N.S.S-Novena-Garfield NEXUS系统启动成功！")
        self.log("="*80)
        
        self.log("🧠 中央情报大脑 (6大核心模块):")
        self.log(f"   📡 本地地址: http://localhost:{brain_port}")
        if brain_tunnel:
            self.log(f"   🌍 公网地址: {brain_tunnel}")
        
        self.log("\n🌐 NEXUS前端界面 (黑色主题):")
        self.log(f"   🎨 本地地址: http://localhost:{frontend_port}")
        if frontend_tunnel:
            self.log(f"   🌍 公网地址: {frontend_tunnel}")
        
        self.log("\n🎯 主要访问地址:")
        self.log(f"   🏠 本地访问: http://localhost:{frontend_port}")
        if frontend_tunnel:
            self.log(f"   🌍 公网访问: {frontend_tunnel}")
        
        self.log("\n🛡️ 系统特性:")
        self.log("   ✅ 父子进程同步关闭")
        self.log("   ✅ 自动进程清理")
        self.log("   ✅ 动态配置管理")
        
        self.log("="*80)
        self.log("🚀 系统运行中！按 Ctrl+C 停止")
        self.log("="*80)
    
    def launch(self, enable_tunnels=True):
        """启动系统"""
        try:
            self.log("🚀 N.S.S-Novena-Garfield NEXUS启动器")
            self.log("="*50)
            
            # 1. 清理现有进程
            self.cleanup_existing_processes()
            
            # 2. 启动中央情报大脑
            brain_port = self.start_intelligence_brain()
            if not brain_port:
                return
            
            # 3. 启动NEXUS前端
            frontend_port = self.start_nexus_frontend()
            if not frontend_port:
                return
            
            # 4. 创建隧道
            brain_tunnel = None
            frontend_tunnel = None
            
            if enable_tunnels and self.running:
                frontend_tunnel = self.create_tunnel("nexus_frontend", frontend_port)
                if self.running:
                    brain_tunnel = self.create_tunnel("intelligence_brain", brain_port)
            
            # 5. 更新配置
            if self.running:
                self.update_config_file(brain_port, frontend_port, brain_tunnel, frontend_tunnel)
            
            # 6. 显示信息
            if self.running:
                self.show_info(brain_port, frontend_port, brain_tunnel, frontend_tunnel)
            
            # 7. 保持运行
            if self.running:
                try:
                    while self.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            
        except Exception as e:
            self.log(f"❌ 启动失败: {e}")
            self.cleanup()
            sys.exit(1)
        finally:
            self.cleanup()

def main():
    parser = argparse.ArgumentParser(description='N.S.S-Novena-Garfield NEXUS启动器')
    parser.add_argument('--no-tunnels', action='store_true', help='不创建隧道')
    parser.add_argument('--cleanup-only', action='store_true', help='仅清理进程')
    
    args = parser.parse_args()
    
    launcher = NEXUSLauncher()
    
    if args.cleanup_only:
        launcher.cleanup_existing_processes()
        return
    
    launcher.launch(enable_tunnels=not args.no_tunnels)

if __name__ == "__main__":
    main()