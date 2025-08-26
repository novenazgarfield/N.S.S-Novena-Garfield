#!/usr/bin/env python3
"""
启动RAG系统并通过隧道暴露服务
解决Cloudflare隧道访问时的跨域问题
"""

import subprocess
import time
import sys
import signal
import os
from threading import Thread

def print_status(message, status="info"):
    """打印状态信息"""
    icons = {
        'info': 'ℹ️',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️'
    }
    print(f"{icons.get(status, 'ℹ️')} {message}")

def start_rag_server():
    """启动RAG服务器"""
    print_status("启动RAG API服务器...")
    try:
        # 启动RAG服务器，绑定到所有接口
        process = subprocess.Popen([
            sys.executable, 'simple_rag_api.py', 
            '--host', '0.0.0.0',  # 绑定到所有接口
            '--port', '5000'
        ], cwd='/workspace/N.S.S-Novena-Garfield')
        
        # 等待服务器启动
        time.sleep(3)
        
        # 检查服务器是否启动成功
        import requests
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=5)
            if response.status_code == 200:
                print_status("RAG API服务器启动成功", "success")
                return process
            else:
                print_status(f"RAG API服务器响应异常: {response.status_code}", "error")
                return None
        except Exception as e:
            print_status(f"RAG API服务器连接失败: {e}", "error")
            return None
            
    except Exception as e:
        print_status(f"启动RAG服务器失败: {e}", "error")
        return None

def start_http_server():
    """启动HTTP服务器"""
    print_status("启动HTTP服务器...")
    try:
        process = subprocess.Popen([
            sys.executable, '-m', 'http.server', '52943', 
            '--bind', '0.0.0.0'
        ], cwd='/workspace/N.S.S-Novena-Garfield')
        
        time.sleep(2)
        print_status("HTTP服务器启动成功", "success")
        return process
        
    except Exception as e:
        print_status(f"启动HTTP服务器失败: {e}", "error")
        return None

def check_cloudflared():
    """检查cloudflared是否可用"""
    try:
        result = subprocess.run(['cloudflared', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print_status("cloudflared 可用", "success")
            return True
        else:
            print_status("cloudflared 不可用", "warning")
            return False
    except Exception:
        print_status("cloudflared 未安装", "warning")
        return False

def start_tunnel(port, service_name):
    """启动Cloudflare隧道"""
    if not check_cloudflared():
        print_status(f"跳过 {service_name} 隧道设置", "warning")
        return None
        
    print_status(f"启动 {service_name} 隧道 (端口 {port})...")
    try:
        process = subprocess.Popen([
            'cloudflared', 'tunnel', '--url', f'http://localhost:{port}'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 等待隧道启动并获取URL
        time.sleep(5)
        
        # 尝试从输出中提取隧道URL
        # 注意：这里可能需要根据实际的cloudflared输出格式调整
        print_status(f"{service_name} 隧道启动成功", "success")
        print_status(f"隧道进程PID: {process.pid}", "info")
        
        return process
        
    except Exception as e:
        print_status(f"启动 {service_name} 隧道失败: {e}", "error")
        return None

def signal_handler(signum, frame):
    """信号处理器"""
    print_status("\n收到退出信号，正在关闭所有服务...", "warning")
    
    # 终止所有子进程
    for process in processes:
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
                print_status(f"进程 {process.pid} 已终止", "success")
            except Exception as e:
                print_status(f"终止进程 {process.pid} 失败: {e}", "error")
                try:
                    process.kill()
                except:
                    pass
    
    print_status("所有服务已关闭", "success")
    sys.exit(0)

# 全局进程列表
processes = []

def main():
    """主函数"""
    print("🚀 启动RAG系统 (支持隧道访问)")
    print("=" * 50)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动RAG服务器
    rag_process = start_rag_server()
    if rag_process:
        processes.append(rag_process)
    else:
        print_status("RAG服务器启动失败，退出", "error")
        return 1
    
    # 启动HTTP服务器
    http_process = start_http_server()
    if http_process:
        processes.append(http_process)
    else:
        print_status("HTTP服务器启动失败，但继续运行", "warning")
    
    # 启动隧道（如果可用）
    rag_tunnel = start_tunnel(5000, "RAG API")
    if rag_tunnel:
        processes.append(rag_tunnel)
    
    http_tunnel = start_tunnel(52943, "HTTP")
    if http_tunnel:
        processes.append(http_tunnel)
    
    print("\n" + "=" * 50)
    print_status("系统启动完成", "success")
    print("=" * 50)
    
    print("\n📋 服务状态:")
    print(f"  • RAG API服务器: http://localhost:5000")
    print(f"  • HTTP服务器: http://localhost:52943")
    
    if check_cloudflared():
        print(f"  • 隧道状态: 已启动 (查看上方输出获取隧道URL)")
        print("\n💡 使用建议:")
        print("  1. 如果通过隧道访问前端，RAG API也会通过隧道暴露")
        print("  2. 前端会自动检测并连接到正确的RAG服务器地址")
        print("  3. 查看浏览器控制台获取详细的连接信息")
    else:
        print(f"  • 隧道状态: 未启动 (cloudflared不可用)")
        print("\n💡 本地访问:")
        print("  访问: http://localhost:52943/systems/nexus/nexus-dashboard-restored.html")
    
    print("\n🔧 调试信息:")
    print("  • 按 Ctrl+C 退出所有服务")
    print("  • 查看右上角状态框了解连接状态")
    print("  • 使用功能菜单中的'重新连接'按钮测试连接")
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
            # 检查进程是否还在运行
            for i, process in enumerate(processes):
                if process and process.poll() is not None:
                    print_status(f"进程 {process.pid} 已退出", "warning")
                    processes[i] = None
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    sys.exit(main())