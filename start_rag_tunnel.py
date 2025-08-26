#!/usr/bin/env python3
"""
快速启动RAG服务器隧道
解决用户通过隧道访问时的连接问题
"""

import subprocess
import time
import sys
import signal
import os
import requests
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

def check_rag_server():
    """检查RAG服务器是否运行"""
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=3)
        if response.status_code == 200:
            data = response.json()
            print_status(f"RAG服务器运行正常 (历史: {data.get('chat_history_count', 0)}条)", "success")
            return True
        else:
            print_status(f"RAG服务器响应异常: {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"RAG服务器未运行: {e}", "error")
        return False

def start_rag_server():
    """启动RAG服务器"""
    print_status("启动RAG服务器...")
    try:
        process = subprocess.Popen([
            sys.executable, 'simple_rag_api.py', 
            '--host', '0.0.0.0',
            '--port', '5000'
        ], cwd='/workspace/N.S.S-Novena-Garfield')
        
        # 等待服务器启动
        for i in range(10):
            time.sleep(1)
            if check_rag_server():
                return process
            print(f"等待服务器启动... ({i+1}/10)")
        
        print_status("RAG服务器启动超时", "error")
        return None
        
    except Exception as e:
        print_status(f"启动RAG服务器失败: {e}", "error")
        return None

def start_tunnel():
    """启动Cloudflare隧道"""
    print_status("启动RAG服务器隧道...")
    try:
        # 检查cloudflared是否可用
        result = subprocess.run(['cloudflared', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print_status("cloudflared 未安装或不可用", "error")
            print("请安装 cloudflared 或使用本地访问方式")
            return None
        
        # 启动隧道
        process = subprocess.Popen([
            'cloudflared', 'tunnel', '--url', 'http://localhost:5000'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print_status("隧道启动中，请等待URL生成...", "info")
        
        # 监控输出，提取隧道URL
        def monitor_output():
            for line in iter(process.stdout.readline, ''):
                if 'trycloudflare.com' in line:
                    # 提取URL
                    import re
                    url_match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                    if url_match:
                        tunnel_url = url_match.group(0)
                        print_status(f"RAG隧道URL: {tunnel_url}", "success")
                        print("=" * 60)
                        print("🎉 RAG服务器隧道已启动！")
                        print(f"📡 隧道地址: {tunnel_url}")
                        print("💡 现在可以刷新前端页面，系统会自动连接到隧道地址")
                        print("=" * 60)
                        break
        
        # 在后台监控输出
        Thread(target=monitor_output, daemon=True).start()
        
        return process
        
    except FileNotFoundError:
        print_status("cloudflared 未安装", "error")
        print("请安装 cloudflared:")
        print("  - macOS: brew install cloudflared")
        print("  - Linux: 下载二进制文件或使用包管理器")
        print("  - Windows: 下载exe文件")
        return None
    except Exception as e:
        print_status(f"启动隧道失败: {e}", "error")
        return None

def signal_handler(signum, frame):
    """信号处理器"""
    print_status("\n收到退出信号，正在关闭服务...", "warning")
    
    # 终止所有子进程
    for process in processes:
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
                print_status(f"进程 {process.pid} 已终止", "success")
            except Exception as e:
                print_status(f"终止进程失败: {e}", "error")
                try:
                    process.kill()
                except:
                    pass
    
    print_status("服务已关闭", "success")
    sys.exit(0)

# 全局进程列表
processes = []

def main():
    """主函数"""
    print("🚀 RAG服务器隧道启动工具")
    print("=" * 50)
    print("💡 此工具专门解决通过隧道访问时的RAG连接问题")
    print("=" * 50)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 检查RAG服务器状态
    if check_rag_server():
        print_status("RAG服务器已运行，直接启动隧道", "info")
    else:
        print_status("RAG服务器未运行，正在启动...", "warning")
        rag_process = start_rag_server()
        if rag_process:
            processes.append(rag_process)
        else:
            print_status("无法启动RAG服务器，退出", "error")
            return 1
    
    # 启动隧道
    tunnel_process = start_tunnel()
    if tunnel_process:
        processes.append(tunnel_process)
    else:
        print_status("无法启动隧道", "error")
        print("\n🔧 替代方案:")
        print("1. 使用本地访问: http://localhost:52943/systems/nexus/nexus-dashboard-restored.html")
        print("2. 安装 cloudflared 后重试")
        print("3. 使用其他隧道工具 (ngrok, localtunnel等)")
        return 1
    
    print("\n" + "=" * 50)
    print_status("系统启动完成", "success")
    print("=" * 50)
    
    print("\n📋 使用说明:")
    print("1. 等待上方显示隧道URL")
    print("2. 刷新前端页面或点击'重新连接'")
    print("3. 系统会自动检测并连接到隧道地址")
    print("4. 按 Ctrl+C 退出")
    
    print("\n🔍 调试信息:")
    print("- 如果连接仍然失败，检查浏览器控制台")
    print("- 确保前端和RAG都通过隧道访问")
    print("- 查看右上角状态框的详细信息")
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
            # 检查进程状态
            for i, process in enumerate(processes):
                if process and process.poll() is not None:
                    print_status(f"进程 {process.pid} 已退出", "warning")
                    processes[i] = None
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    sys.exit(main())