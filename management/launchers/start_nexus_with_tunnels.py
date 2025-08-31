#!/usr/bin/env python3
"""
NEXUS系统完整启动脚本 - 包含隧道自动连接
解决系统稳定性和动态配置问题
"""

import os
import sys
import time
import json
import signal
import subprocess
import requests
from pathlib import Path
from datetime import datetime
import psutil
import argparse

class NEXUSLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = {}
        self.tunnels = {}
        self.config_file = self.project_root / "systems/nexus/public/api_config.json"
        self.log_dir = Path("/tmp")
        
    def log(self, message):
        """日志输出"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
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
    
    def kill_existing_processes(self):
        """清理现有进程"""
        self.log("🧹 清理现有进程...")
        
        # 要清理的进程关键词
        keywords = ['smart_rag_server', 'vite', 'cloudflared', 'nexus', 'node.*vite']
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                for keyword in keywords:
                    if keyword in cmdline.lower():
                        self.log(f"终止进程: {proc.info['pid']} - {cmdline[:100]}")
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        time.sleep(2)
        self.log("✅ 进程清理完成")
    
    def start_rag_server(self):
        """启动RAG服务器"""
        self.log("🧠 启动RAG服务器...")
        
        # 查找可用端口
        rag_port = self.find_free_port(8500)
        self.log(f"RAG服务器端口: {rag_port}")
        
        # 启动RAG服务器
        rag_dir = self.project_root / "systems/rag-system"
        log_file = self.log_dir / "rag_server.log"
        
        cmd = [
            sys.executable, "smart_rag_server.py", 
            "--port", str(rag_port),
            "--host", "0.0.0.0"
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=rag_dir,
            stdout=open(log_file, 'w'),
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid  # 创建新的进程组
        )
        
        self.processes['rag_server'] = {
            'process': process,
            'port': rag_port,
            'log_file': log_file
        }
        
        # 等待服务器启动
        self.log("等待RAG服务器启动...")
        for i in range(30):
            try:
                response = requests.get(f"http://localhost:{rag_port}/api/health", timeout=2)
                if response.status_code == 200:
                    self.log(f"✅ RAG服务器启动成功: http://localhost:{rag_port}")
                    return rag_port
            except:
                time.sleep(1)
        
        raise RuntimeError("RAG服务器启动失败")
    
    def start_frontend(self):
        """启动前端服务器"""
        self.log("🌐 启动前端服务器...")
        
        # 查找可用端口
        frontend_port = self.find_free_port(52300)
        self.log(f"前端服务器端口: {frontend_port}")
        
        # 启动前端服务器
        frontend_dir = self.project_root / "systems/nexus"
        log_file = self.log_dir / "frontend_server.log"
        
        cmd = [
            "npm", "run", "dev", "--", 
            "--host", "0.0.0.0", 
            "--port", str(frontend_port)
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=frontend_dir,
            stdout=open(log_file, 'w'),
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid
        )
        
        self.processes['frontend'] = {
            'process': process,
            'port': frontend_port,
            'log_file': log_file
        }
        
        # 等待前端启动
        self.log("等待前端服务器启动...")
        for i in range(30):
            try:
                response = requests.get(f"http://localhost:{frontend_port}", timeout=2)
                if response.status_code == 200:
                    self.log(f"✅ 前端服务器启动成功: http://localhost:{frontend_port}")
                    return frontend_port
            except:
                time.sleep(1)
        
        raise RuntimeError("前端服务器启动失败")
    
    def create_tunnel(self, service_name, port):
        """创建Cloudflare隧道"""
        self.log(f"🌐 为{service_name}创建隧道 (端口: {port})...")
        
        log_file = self.log_dir / f"{service_name}_tunnel.log"
        
        cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"]
        
        process = subprocess.Popen(
            cmd,
            stdout=open(log_file, 'w'),
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid
        )
        
        # 等待隧道建立并获取URL
        self.log(f"等待{service_name}隧道建立...")
        tunnel_url = None
        
        for i in range(30):
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                    # 查找隧道URL
                    import re
                    match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', content)
                    if match:
                        tunnel_url = match.group(0)
                        break
            except:
                pass
            time.sleep(1)
        
        if not tunnel_url:
            self.log(f"❌ {service_name}隧道创建失败")
            process.terminate()
            return None
        
        self.tunnels[service_name] = {
            'process': process,
            'url': tunnel_url,
            'port': port,
            'log_file': log_file
        }
        
        self.log(f"✅ {service_name}隧道创建成功: {tunnel_url}")
        return tunnel_url
    
    def update_config_file(self, rag_port, frontend_port, rag_tunnel_url, frontend_tunnel_url):
        """更新配置文件"""
        self.log("📝 更新配置文件...")
        
        config = {
            "api_endpoints": {
                "rag_api": rag_tunnel_url if rag_tunnel_url else f"http://localhost:{rag_port}",
                "health_check": f"{rag_tunnel_url if rag_tunnel_url else f'http://localhost:{rag_port}'}/api/health",
                "chat": f"{rag_tunnel_url if rag_tunnel_url else f'http://localhost:{rag_port}'}/api/chat",
                "upload": f"{rag_tunnel_url if rag_tunnel_url else f'http://localhost:{rag_port}'}/api/upload",
                "rag_api_local": f"http://localhost:{rag_port}",
                "energy_api": "http://localhost:56400",
                "energy_health": "http://localhost:56400/api/energy/health",
                "energy_models": "http://localhost:56400/api/energy/models/available",
                "energy_config": "http://localhost:56400/api/energy/config"
            },
            "local_endpoints": {
                "rag_api": f"http://localhost:{rag_port}",
                "frontend": f"http://localhost:{frontend_port}"
            },
            "tunnel_endpoints": {
                "rag_backend": rag_tunnel_url,
                "nexus_frontend": frontend_tunnel_url
            } if rag_tunnel_url and frontend_tunnel_url else {},
            "updated_at": time.time(),
            "status": "active",
            "tunnel_status": "connected" if rag_tunnel_url and frontend_tunnel_url else "local_only",
            "last_health_check": datetime.now().isoformat(),
            "launcher_info": {
                "version": "2.0.0",
                "features": ["dynamic_ports", "auto_tunnels", "process_management", "health_monitoring"]
            }
        }
        
        # 确保目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入配置文件
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.log(f"✅ 配置文件已更新: {self.config_file}")
    
    def test_system(self):
        """测试系统功能"""
        self.log("🧪 测试系统功能...")
        
        # 测试RAG API
        rag_info = self.processes.get('rag_server')
        if rag_info:
            try:
                response = requests.get(f"http://localhost:{rag_info['port']}/api/health", timeout=5)
                if response.status_code == 200:
                    self.log("✅ RAG API健康检查通过")
                else:
                    self.log(f"❌ RAG API健康检查失败: {response.status_code}")
            except Exception as e:
                self.log(f"❌ RAG API连接失败: {e}")
        
        # 测试前端
        frontend_info = self.processes.get('frontend')
        if frontend_info:
            try:
                response = requests.get(f"http://localhost:{frontend_info['port']}", timeout=5)
                if response.status_code == 200:
                    self.log("✅ 前端服务器响应正常")
                else:
                    self.log(f"❌ 前端服务器响应异常: {response.status_code}")
            except Exception as e:
                self.log(f"❌ 前端服务器连接失败: {e}")
        
        # 测试隧道
        for name, tunnel_info in self.tunnels.items():
            try:
                response = requests.get(tunnel_info['url'], timeout=10)
                if response.status_code == 200:
                    self.log(f"✅ {name}隧道响应正常: {tunnel_info['url']}")
                else:
                    self.log(f"❌ {name}隧道响应异常: {response.status_code}")
            except Exception as e:
                self.log(f"❌ {name}隧道连接失败: {e}")
    
    def monitor_processes(self):
        """监控进程状态"""
        self.log("👁️ 开始进程监控...")
        
        try:
            while True:
                # 检查所有进程
                for name, info in self.processes.items():
                    process = info['process']
                    if process.poll() is not None:
                        self.log(f"❌ {name}进程已停止 (退出码: {process.returncode})")
                        # 可以在这里添加自动重启逻辑
                
                # 检查隧道进程
                for name, info in self.tunnels.items():
                    process = info['process']
                    if process.poll() is not None:
                        self.log(f"❌ {name}隧道已断开 (退出码: {process.returncode})")
                        # 可以在这里添加自动重连逻辑
                
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
                self.log(f"清理{name}时出错: {e}")
        
        self.log("✅ 清理完成")
    
    def start(self, enable_tunnels=True, monitor=True):
        """启动完整系统"""
        try:
            self.log("🚀 启动NEXUS系统...")
            
            # 1. 清理现有进程
            self.kill_existing_processes()
            
            # 2. 启动RAG服务器
            rag_port = self.start_rag_server()
            
            # 3. 启动前端服务器
            frontend_port = self.start_frontend()
            
            # 4. 创建隧道（如果启用）
            rag_tunnel_url = None
            frontend_tunnel_url = None
            
            if enable_tunnels:
                rag_tunnel_url = self.create_tunnel("rag_backend", rag_port)
                frontend_tunnel_url = self.create_tunnel("nexus_frontend", frontend_port)
            
            # 5. 更新配置文件
            self.update_config_file(rag_port, frontend_port, rag_tunnel_url, frontend_tunnel_url)
            
            # 6. 测试系统
            self.test_system()
            
            # 7. 显示访问信息
            self.show_access_info()
            
            # 8. 开始监控（如果启用）
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
            self.log(f"❌ 启动失败: {e}")
            self.cleanup()
            sys.exit(1)
        finally:
            self.cleanup()
    
    def show_access_info(self):
        """显示访问信息"""
        self.log("\n" + "="*60)
        self.log("🎉 NEXUS系统启动成功！")
        self.log("="*60)
        
        # 本地访问
        if 'frontend' in self.processes:
            port = self.processes['frontend']['port']
            self.log(f"🌐 本地访问: http://localhost:{port}")
        
        if 'rag_server' in self.processes:
            port = self.processes['rag_server']['port']
            self.log(f"🧠 RAG API: http://localhost:{port}")
        
        # 隧道访问
        if self.tunnels:
            self.log("\n🌍 公网访问:")
            for name, info in self.tunnels.items():
                self.log(f"  {name}: {info['url']}")
        
        # 日志文件
        self.log(f"\n📋 日志文件:")
        for name, info in {**self.processes, **self.tunnels}.items():
            if 'log_file' in info:
                self.log(f"  {name}: {info['log_file']}")
        
        self.log("="*60)

def main():
    parser = argparse.ArgumentParser(description='NEXUS系统启动器')
    parser.add_argument('--no-tunnels', action='store_true', help='不创建隧道')
    parser.add_argument('--no-monitor', action='store_true', help='不启用进程监控')
    
    args = parser.parse_args()
    
    launcher = NEXUSLauncher()
    
    # 设置信号处理
    def signal_handler(signum, frame):
        launcher.log("收到终止信号...")
        launcher.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动系统
    launcher.start(
        enable_tunnels=not args.no_tunnels,
        monitor=not args.no_monitor
    )

if __name__ == "__main__":
    main()