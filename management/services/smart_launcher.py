#!/usr/bin/env python3
"""
🚀 N.S.S 智能服务启动器
自动启动所有服务并创建隧道
"""

import os
import sys
import time
import subprocess
import threading
import signal
import json
from pathlib import Path
from service_discovery import ServiceDiscovery

class SmartLauncher:
    def __init__(self):
        self.sd = ServiceDiscovery()
        self.processes = {}
        self.tunnels = {}
        self.running = True
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理退出信号"""
        print("\n🛑 收到退出信号，正在关闭所有服务...")
        self.running = False
        self.stop_all_services()
        sys.exit(0)
    
    def start_rag_api(self):
        """启动完整版RAG API服务"""
        service_info = self.sd.register_service('rag_api', 'rag_api')
        if not service_info:
            return False
        
        port = service_info['port']
        
        # 使用完整版RAG系统
        rag_script = self.sd.project_root / "systems" / "rag-system" / "smart_rag_server.py"
        rag_dir = self.sd.project_root / "systems" / "rag-system"
        
        # 启动服务
        env = os.environ.copy()
        env['PORT'] = str(port)
        
        process = subprocess.Popen([
            sys.executable, str(rag_script)
        ], env=env, cwd=rag_dir)
        
        self.processes['rag_api'] = process
        
        # 等待服务启动
        time.sleep(5)  # 完整版需要更多启动时间
        
        # 检查服务状态
        try:
            import requests
            response = requests.get(f"http://localhost:{port}/api/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ 完整版RAG API 启动成功: http://localhost:{port}")
                print(f"📋 功能包括: 智能问答、文档上传、聊天历史、文档搜索")
                return True
        except Exception as e:
            print(f"⚠️ RAG API健康检查失败: {e}")
        
        print(f"❌ RAG API 启动失败")
        return False
    
    def start_energy_api(self):
        """启动能源API服务"""
        service_info = self.sd.register_service('energy_api', 'energy_api')
        if not service_info:
            return False
        
        port = service_info['port']
        
        # 使用完整版能源API系统
        energy_script = self.sd.project_root / "api" / "energy_api_server.py"
        energy_dir = self.sd.project_root / "api"
        
        # 启动服务
        env = os.environ.copy()
        env['PORT'] = str(port)
        
        process = subprocess.Popen([
            sys.executable, str(energy_script)
        ], env=env, cwd=energy_dir)
        
        self.processes['energy_api'] = process
        
        # 等待服务启动
        time.sleep(3)
        
        # 检查服务状态
        try:
            import requests
            response = requests.get(f"http://localhost:{port}/api/energy/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ 能源API 启动成功: http://localhost:{port}")
                print(f"📋 功能包括: 模型配置、API密钥管理、使用统计")
                return True
        except Exception as e:
            print(f"⚠️ 能源API健康检查失败: {e}")
        
        print(f"❌ 能源API 启动失败")
        return False
    
    def start_nexus_frontend(self):
        """启动Nexus前端"""
        service_info = self.sd.register_service('nexus_frontend', 'nexus_frontend')
        if not service_info:
            return False
        
        port = service_info['port']
        nexus_dir = self.sd.project_root / "systems" / "nexus"
        
        # 更新前端配置以使用动态API地址
        self.update_frontend_config()
        
        # 启动前端服务
        env = os.environ.copy()
        env['PORT'] = str(port)
        env['VITE_PORT'] = str(port)  # 确保Vite和Electron都能获取到端口
        
        process = subprocess.Popen([
            "npm", "run", "dev", "--", "--port", str(port), "--host", "0.0.0.0"
        ], cwd=nexus_dir, env=env)
        
        self.processes['nexus_frontend'] = process
        
        # 等待服务启动
        time.sleep(10)
        
        print(f"✅ Nexus前端启动成功: http://localhost:{port}")
        return True
    
    def update_frontend_config(self):
        """更新前端配置以使用动态API地址"""
        try:
            # 获取RAG API地址
            rag_service = self.sd.services.get('rag_api')
            if not rag_service:
                return
            
            # 创建动态配置文件，包含所有API端点
            config = {
                'api_endpoints': {
                    'rag_api': rag_service['local_url'],
                    'health_check': f"{rag_service['local_url']}/api/health",
                    'chat': f"{rag_service['local_url']}/api/chat",
                    'upload': f"{rag_service['local_url']}/api/upload"
                },
                'updated_at': time.time()
            }
            
            # 添加能源API端点
            energy_service = self.sd.services.get('energy_api')
            if energy_service:
                config['api_endpoints']['energy_api'] = energy_service['local_url']
                config['api_endpoints']['energy_health'] = f"{energy_service['local_url']}/api/energy/health"
                config['api_endpoints']['energy_models'] = f"{energy_service['local_url']}/api/energy/models/available"
                config['api_endpoints']['energy_config'] = f"{energy_service['local_url']}/api/energy/config"
            
            config_file = self.sd.project_root / "systems" / "nexus" / "public" / "api_config.json"
            config_file.parent.mkdir(exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"📝 前端配置已更新: {config_file}")
            
        except Exception as e:
            print(f"❌ 更新前端配置失败: {e}")
    
    def create_tunnels(self):
        """为所有服务创建隧道"""
        cloudflared_path = self.sd.project_root / "systems" / "nexus" / "cloudflared"
        
        if not cloudflared_path.exists():
            print("❌ cloudflared 未找到，跳过隧道创建")
            return
        
        # 为前端创建隧道
        nexus_service = self.sd.services.get('nexus_frontend')
        if nexus_service:
            tunnel_url = self.create_tunnel('nexus_frontend', nexus_service['local_url'])
            if tunnel_url:
                print(f"🌐 Nexus前端隧道: {tunnel_url}")
        
        # 为API创建隧道
        rag_service = self.sd.services.get('rag_api')
        if rag_service:
            tunnel_url = self.create_tunnel('rag_api', rag_service['local_url'])
            if tunnel_url:
                print(f"🌐 RAG API隧道: {tunnel_url}")
    
    def create_tunnel(self, service_name, local_url):
        """创建单个隧道"""
        try:
            cloudflared_path = self.sd.project_root / "systems" / "nexus" / "cloudflared"
            
            process = subprocess.Popen([
                str(cloudflared_path), "tunnel", "--url", local_url
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.tunnels[service_name] = process
            
            # 等待隧道URL
            for _ in range(30):
                if process.poll() is not None:
                    break
                
                try:
                    output = process.stderr.readline()
                    if 'trycloudflare.com' in output:
                        import re
                        match = re.search(r'https://[^\s]+\.trycloudflare\.com', output)
                        if match:
                            tunnel_url = match.group(0)
                            
                            # 更新服务信息
                            if service_name in self.sd.services:
                                self.sd.services[service_name]['tunnel_url'] = tunnel_url
                                self.sd.save_registry()
                            
                            return tunnel_url
                except:
                    pass
                
                time.sleep(1)
            
            return None
            
        except Exception as e:
            print(f"❌ 创建隧道失败 {service_name}: {e}")
            return None
    
    def start_all_services(self):
        """启动所有服务"""
        print("🚀 启动所有服务...")
        print("=" * 50)
        
        # 1. 启动RAG API
        print("📡 启动RAG API服务...")
        if not self.start_rag_api():
            print("❌ RAG API启动失败，继续启动其他服务...")
        
        # 2. 启动能源API
        print("🔋 启动能源API服务...")
        if not self.start_energy_api():
            print("❌ 能源API启动失败，继续启动其他服务...")
        
        # 3. 启动Nexus前端
        print("🖥️  启动Nexus前端...")
        if not self.start_nexus_frontend():
            print("❌ Nexus前端启动失败，继续启动其他服务...")
        
        # 3. 创建隧道
        print("🌐 创建公网隧道...")
        self.create_tunnels()
        
        # 4. 显示服务状态
        self.show_service_status()
        
        return True
    
    def show_service_status(self):
        """显示服务状态"""
        print("\n" + "=" * 50)
        print("🌟 N.S.S 服务状态报告")
        print("=" * 50)
        
        for name, service in self.sd.services.items():
            print(f"📋 {name}:")
            print(f"   🔗 本地地址: {service['local_url']}")
            if service.get('tunnel_url'):
                print(f"   🌐 公网地址: {service['tunnel_url']}")
            print(f"   📊 状态: {service['status']}")
            print()
        
        print("🎯 所有服务已启动完成！")
        print("💡 按 Ctrl+C 停止所有服务")
    
    def stop_all_services(self):
        """停止所有服务"""
        print("🛑 正在停止所有服务...")
        
        # 停止隧道
        for name, process in self.tunnels.items():
            try:
                process.terminate()
                print(f"🔌 隧道已停止: {name}")
            except:
                pass
        
        # 停止服务
        for name, process in self.processes.items():
            try:
                process.terminate()
                print(f"⏹️  服务已停止: {name}")
            except:
                pass
        
        # 等待进程结束
        time.sleep(2)
        
        # 强制杀死未结束的进程
        for name, process in list(self.processes.items()):
            try:
                if process.poll() is None:
                    process.kill()
                    print(f"💀 强制停止: {name}")
            except:
                pass
    
    def monitor_services(self):
        """监控服务状态"""
        while self.running:
            try:
                time.sleep(30)  # 每30秒检查一次
                
                for name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        print(f"⚠️  服务异常退出: {name}")
                        # 这里可以添加自动重启逻辑
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ 监控异常: {e}")
    
    def run(self):
        """运行启动器"""
        try:
            # 启动所有服务
            if not self.start_all_services():
                print("❌ 服务启动失败")
                return
            
            # 启动监控线程
            monitor_thread = threading.Thread(target=self.monitor_services)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # 主线程等待
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 用户中断")
        except Exception as e:
            print(f"❌ 运行异常: {e}")
        finally:
            self.stop_all_services()

if __name__ == '__main__':
    launcher = SmartLauncher()
    launcher.run()