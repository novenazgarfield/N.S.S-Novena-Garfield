#!/usr/bin/env python3
"""
启动完整的Gemini AI系统
包括API管理界面和Gemini聊天应用
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_services():
    """启动所有服务"""
    print("🚀 启动Gemini AI完整系统")
    print("=" * 50)
    
    # 切换到API管理目录
    api_dir = Path(__file__).parent
    os.chdir(api_dir)
    
    # 确保日志目录存在
    logs_dir = api_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    processes = []
    
    try:
        # 1. 初始化系统
        print("🔧 初始化API管理系统...")
        init_result = subprocess.run([
            sys.executable, "start_api_manager.py", "init"
        ], capture_output=True, text=True)
        
        if init_result.returncode == 0:
            print("✅ 系统初始化成功")
        else:
            print(f"❌ 系统初始化失败: {init_result.stderr}")
            return
        
        # 2. 启动API管理界面
        print("🌐 启动API管理界面...")
        api_process = subprocess.Popen([
            "streamlit", "run", "api_web_manager.py",
            "--server.port", "56336",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ], stdout=open(logs_dir / "api_manager.log", "w"), 
           stderr=subprocess.STDOUT)
        
        processes.append(("API管理界面", api_process, "http://localhost:56336"))
        print(f"✅ API管理界面已启动 (PID: {api_process.pid})")
        
        # 3. 启动Gemini聊天应用
        print("🤖 启动Gemini聊天应用...")
        gemini_process = subprocess.Popen([
            "streamlit", "run", "gemini_chat_app.py",
            "--server.port", "51657",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ], stdout=open(logs_dir / "gemini_chat.log", "w"), 
           stderr=subprocess.STDOUT)
        
        processes.append(("Gemini聊天应用", gemini_process, "http://localhost:51657"))
        print(f"✅ Gemini聊天应用已启动 (PID: {gemini_process.pid})")
        
        # 等待服务启动
        print("\n⏳ 等待服务启动...")
        time.sleep(8)
        
        # 检查服务状态
        print("\n📊 服务状态检查:")
        import requests
        
        for name, process, url in processes:
            if process.poll() is None:  # 进程仍在运行
                try:
                    response = requests.get(url, timeout=3)
                    if response.status_code == 200:
                        print(f"✅ {name}: 运行正常 - {url}")
                    else:
                        print(f"⚠️ {name}: 响应异常 ({response.status_code}) - {url}")
                except requests.RequestException:
                    print(f"❌ {name}: 连接失败 - {url}")
            else:
                print(f"❌ {name}: 进程已退出")
        
        print("\n🎉 Gemini AI系统启动完成！")
        print("=" * 50)
        print("📱 访问地址:")
        print("   🌐 API管理界面: http://localhost:56336")
        print("   🤖 Gemini聊天应用: http://localhost:51657")
        print("\n💡 功能说明:")
        print("   • API管理界面: 管理API密钥、查看使用统计、配置权限")
        print("   • Gemini聊天应用: 与Gemini AI对话、生成代码、查看使用情况")
        print("\n⚠️ 注意事项:")
        print("   • 确保您的Gemini API密钥已正确配置")
        print("   • 不同用户角色有不同的功能权限")
        print("   • 系统会自动记录API使用情况和限制")
        
        print("\n按 Ctrl+C 停止所有服务...")
        
        # 等待用户中断
        try:
            while True:
                # 检查进程是否还在运行
                running_processes = [p for _, p, _ in processes if p.poll() is None]
                if not running_processes:
                    print("❌ 所有服务都已停止")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 正在停止所有服务...")
            
            for name, process, _ in processes:
                if process.poll() is None:
                    print(f"   停止 {name}...")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                        print(f"   ✅ {name} 已停止")
                    except subprocess.TimeoutExpired:
                        print(f"   🔥 强制终止 {name}")
                        process.kill()
            
            print("✅ 所有服务已停止")
    
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        
        # 清理进程
        for name, process, _ in processes:
            if process.poll() is None:
                process.terminate()

def show_help():
    """显示帮助信息"""
    print("🤖 Gemini AI系统启动脚本")
    print("=" * 30)
    print("用法: python start_gemini_system.py [选项]")
    print("\n选项:")
    print("  start    启动完整系统 (默认)")
    print("  help     显示此帮助信息")
    print("\n示例:")
    print("  python start_gemini_system.py")
    print("  python start_gemini_system.py start")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "help":
            show_help()
            return
        elif command != "start":
            print(f"❌ 未知命令: {command}")
            show_help()
            return
    
    start_services()

if __name__ == "__main__":
    main()