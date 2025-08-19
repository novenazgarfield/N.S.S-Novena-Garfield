#!/usr/bin/env python3
"""
启动集成Gemini的RAG系统
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'streamlit',
        'google-generativeai',
        'cryptography'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def setup_environment():
    """设置环境"""
    # 添加路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    sys.path.insert(0, os.path.join(current_dir, 'common'))
    
    # 设置环境变量
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'

def start_rag_system():
    """启动RAG系统"""
    print("🚀 启动集成Gemini的RAG系统...")
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 设置环境
    setup_environment()
    
    # 启动Streamlit应用
    app_file = os.path.join(os.path.dirname(__file__), 'universal_app.py')
    
    cmd = [
        'streamlit', 'run', app_file,
        '--server.port', '51658',
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'false',
        '--server.enableXsrfProtection', 'false',
        '--browser.gatherUsageStats', 'false'
    ]
    
    print(f"📱 RAG系统将在以下地址启动:")
    print(f"   - http://localhost:51658")
    print(f"   - http://0.0.0.0:51658")
    print()
    print("✨ 功能特性:")
    print("   - 🤖 支持多种AI模型 (OpenAI, Gemini, Claude)")
    print("   - 📄 智能文档分析")
    print("   - 💬 RAG增强对话")
    print("   - 🔑 API密钥管理")
    print("   - 📱 移动端适配")
    print()
    print("⚙️ 使用说明:")
    print("   1. 在设置中配置您的API密钥")
    print("   2. 选择要使用的AI模型")
    print("   3. 上传文档进行分析")
    print("   4. 开始智能对话")
    print()
    print("🔧 按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 RAG系统已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_rag_system()