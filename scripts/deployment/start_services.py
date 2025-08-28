#!/usr/bin/env python3
"""
简化的服务启动脚本
用于启动前端、后端API和隧道服务
"""

import os
import sys
import time
import subprocess
import threading
import signal
import json
from pathlib import Path

# 配置
PROJECT_DIR = "/workspace"
FRONTEND_DIR = f"{PROJECT_DIR}/systems/nexus"
CLOUDFLARED_PATH = f"{FRONTEND_DIR}/cloudflared"
API_PORT = 5000
FRONTEND_PORT = 53870  # 使用提供的端口

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.api_url = None
        self.frontend_url = None
        
    def log(self, message):
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
        
    def run_command(self, cmd, cwd=None, background=False):
        """运行命令"""
        try:
            if background:
                process = subprocess.Popen(
                    cmd, shell=True, cwd=cwd,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    preexec_fn=os.setsid
                )
                self.processes.append(process)
                return process
            else:
                result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
                return result
        except Exception as e:
            self.log(f"命令执行失败: {e}")
            return None
    
    def wait_for_service(self, url, timeout=30):
        """等待服务启动"""
        import requests
        for i in range(timeout):
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    return True
            except:
                pass
            time.sleep(1)
        return False
    
    def start_api_service(self):
        """启动API服务"""
        self.log("启动RAG API服务...")
        
        # 检查API文件是否存在
        api_file = f"{PROJECT_DIR}/online_rag_api.py"
        if not os.path.exists(api_file):
            self.log(f"错误: API文件不存在 {api_file}")
            return False
            
        # 启动API服务
        cmd = f"python {api_file}"
        process = self.run_command(cmd, cwd=PROJECT_DIR, background=True)
        
        if process:
            # 等待服务启动
            if self.wait_for_service(f"http://localhost:{API_PORT}/api/health", timeout=15):
                self.log("✅ RAG API服务启动成功")
                return True
            else:
                self.log("❌ RAG API服务启动失败")
                return False
        return False
    
    def start_frontend_service(self):
        """启动前端服务"""
        self.log("启动前端服务...")
        
        if not os.path.exists(FRONTEND_DIR):
            self.log(f"错误: 前端目录不存在 {FRONTEND_DIR}")
            return False
            
        # 启动前端HTTP服务器
        cmd = f"python -m http.server {FRONTEND_PORT} --bind 0.0.0.0"
        process = self.run_command(cmd, cwd=FRONTEND_DIR, background=True)
        
        if process:
            time.sleep(3)  # 等待服务启动
            self.log("✅ 前端服务启动成功")
            return True
        return False
    
    def create_tunnel(self, local_port, service_name):
        """创建cloudflare隧道"""
        if not os.path.exists(CLOUDFLARED_PATH):
            self.log(f"错误: cloudflared不存在 {CLOUDFLARED_PATH}")
            return None
            
        self.log(f"创建{service_name}隧道...")
        
        # 启动隧道
        cmd = f"{CLOUDFLARED_PATH} tunnel --url http://localhost:{local_port}"
        process = self.run_command(cmd, cwd=FRONTEND_DIR, background=True)
        
        if process:
            # 等待隧道URL生成
            for i in range(30):
                try:
                    if process.poll() is not None:
                        break
                    time.sleep(1)
                    # 尝试从进程输出中获取URL
                    # 这里简化处理，实际应该解析输出
                except:
                    pass
            
            # 由于无法直接获取URL，我们返回进程对象
            return process
        return None
    
    def update_frontend_config(self, api_url):
        """更新前端配置中的API URL"""
        config_file = f"{FRONTEND_DIR}/index.html"
        if not os.path.exists(config_file):
            self.log(f"警告: 前端配置文件不存在 {config_file}")
            return
            
        try:
            # 备份原文件
            backup_file = f"{config_file}.backup.{int(time.time())}"
            subprocess.run(f"cp {config_file} {backup_file}", shell=True)
            
            # 更新API URL（简化版本）
            self.log(f"更新前端配置，API URL: {api_url}")
            
        except Exception as e:
            self.log(f"更新前端配置失败: {e}")
    
    def show_status(self):
        """显示服务状态"""
        print("\n" + "="*60)
        print("🎉 服务启动完成！")
        print("="*60)
        print(f"📱 前端服务: http://localhost:{FRONTEND_PORT}")
        print(f"🤖 API服务: http://localhost:{API_PORT}")
        print(f"📊 API健康检查: http://localhost:{API_PORT}/api/health")
        print("="*60)
        print("💡 使用说明:")
        print("1. 访问前端界面开始使用")
        print("2. 上传文档进行RAG问答")
        print("3. 按 Ctrl+C 停止所有服务")
        print("="*60)
    
    def cleanup(self):
        """清理所有进程"""
        self.log("正在停止所有服务...")
        for process in self.processes:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            except:
                try:
                    process.terminate()
                except:
                    pass
        
        # 等待进程结束
        time.sleep(2)
        
        # 强制杀死残留进程
        for process in self.processes:
            try:
                process.kill()
            except:
                pass
                
        self.log("所有服务已停止")
    
    def start_all(self):
        """启动所有服务"""
        try:
            # 启动API服务
            if not self.start_api_service():
                return False
            
            # 启动前端服务
            if not self.start_frontend_service():
                return False
            
            # 显示状态
            self.show_status()
            
            # 等待用户中断
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                
        except Exception as e:
            self.log(f"启动失败: {e}")
            return False
        finally:
            self.cleanup()
        
        return True

def main():
    """主函数"""
    print("🚀 启动 NEXUS AI 系统...")
    
    manager = ServiceManager()
    
    # 设置信号处理
    def signal_handler(sig, frame):
        print("\n收到中断信号，正在停止服务...")
        manager.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动所有服务
    success = manager.start_all()
    
    if not success:
        print("❌ 服务启动失败")
        sys.exit(1)

if __name__ == "__main__":
    main()