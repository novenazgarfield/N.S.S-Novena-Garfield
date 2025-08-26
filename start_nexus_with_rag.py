#!/usr/bin/env python3
"""
启动NEXUS仪表板和RAG系统的集成服务
"""
import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path

def start_http_server():
    """启动HTTP服务器"""
    print("🌐 启动HTTP服务器...")
    os.chdir("/workspace/N.S.S-Novena-Garfield")
    
    # 启动HTTP服务器
    server_process = subprocess.Popen([
        sys.executable, "-m", "http.server", "52943"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return server_process

def start_rag_api():
    """启动RAG API服务器"""
    print("🤖 启动RAG API服务器...")
    
    # 切换到RAG系统目录
    rag_dir = Path("/workspace/N.S.S-Novena-Garfield/systems/rag-system")
    os.chdir(str(rag_dir))
    
    # 启动RAG API服务器
    api_process = subprocess.Popen([
        sys.executable, "api_server.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return api_process

def main():
    """主函数"""
    print("🚀 启动NEXUS + RAG集成系统...")
    print("=" * 50)
    
    processes = []
    
    try:
        # 启动HTTP服务器
        http_process = start_http_server()
        processes.append(("HTTP服务器", http_process))
        time.sleep(2)
        
        # 启动RAG API服务器
        rag_process = start_rag_api()
        processes.append(("RAG API服务器", rag_process))
        time.sleep(3)
        
        print("✅ 所有服务启动完成！")
        print("=" * 50)
        print("🌐 前端地址: http://localhost:52943/systems/nexus/nexus-dashboard-restored.html")
        print("🤖 RAG API: http://localhost:5000")
        print("📊 RAG健康检查: http://localhost:5000/api/health")
        print("=" * 50)
        print("按 Ctrl+C 停止所有服务")
        
        # 等待进程
        while True:
            time.sleep(1)
            
            # 检查进程状态
            for name, process in processes:
                if process.poll() is not None:
                    print(f"❌ {name} 已停止")
                    return
    
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号，正在关闭服务...")
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        
    finally:
        # 停止所有进程
        for name, process in processes:
            try:
                print(f"🛑 停止 {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"⚠️ 强制停止 {name}...")
                process.kill()
            except Exception as e:
                print(f"⚠️ 停止 {name} 时出错: {e}")
        
        print("👋 所有服务已停止")

if __name__ == "__main__":
    main()