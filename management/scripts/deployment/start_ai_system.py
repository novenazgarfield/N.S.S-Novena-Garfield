#!/usr/bin/env python3
"""
🚀 三阶段AI模型管理系统启动脚本
启动中央能源数据库和动态RAG系统
"""

import subprocess
import time
import sys
import os

def start_service(script_path, service_name, port):
    """启动服务"""
    print(f"🚀 启动 {service_name} (端口 {port})...")
    try:
        process = subprocess.Popen([
            sys.executable, script_path
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
        print(f"✅ {service_name} 已启动 (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ 启动 {service_name} 失败: {e}")
        return None

def main():
    print("=" * 60)
    print("🎯 三阶段AI模型管理系统启动器")
    print("=" * 60)
    
    # 启动中央能源数据库
    energy_process = start_service(
        "api_management/simple_energy_server.py",
        "中央能源数据库",
        56420
    )
    
    if not energy_process:
        print("❌ 中央能源数据库启动失败，退出")
        return False
    
    time.sleep(2)
    
    # 启动动态RAG系统
    rag_process = start_service(
        "api_management/simple_dynamic_rag.py", 
        "动态RAG系统",
        60010
    )
    
    if not rag_process:
        print("❌ 动态RAG系统启动失败，退出")
        energy_process.terminate()
        return False
    
    print("\n" + "=" * 60)
    print("🎉 AI系统启动完成！")
    print("=" * 60)
    print("🔗 访问地址:")
    print("   🖥️ NEXUS主界面: http://localhost:8080")
    print("   🔋 中央能源API: http://localhost:56420")
    print("   🤖 动态RAG API: http://localhost:60010")
    print("\n📚 使用指南:")
    print("   1. 访问NEXUS界面")
    print("   2. 点击右上角⚙️进入设置")
    print("   3. 在'AI模型配置'部分管理您的AI配置")
    print("   4. 享受智能化的AI模型管理体验！")
    print("\n⚠️ 按 Ctrl+C 停止所有服务")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务...")
        energy_process.terminate()
        rag_process.terminate()
        print("✅ 所有服务已停止")

if __name__ == "__main__":
    main()