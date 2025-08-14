#!/usr/bin/env python3
"""
RAG系统启动脚本
"""
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        import sentence_transformers
        import faiss
        import llama_cpp
        print("✅ 核心依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def main():
    """主函数"""
    print("🚀 启动RAG系统...")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 获取脚本目录
    script_dir = Path(__file__).parent
    app_path = script_dir / "app.py"
    
    if not app_path.exists():
        print(f"❌ 找不到应用文件: {app_path}")
        sys.exit(1)
    
    # 启动Streamlit应用
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        str(app_path),
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.allowRunOnSave", "true",
        "--server.runOnSave", "true"
    ]
    
    print(f"📱 启动命令: {' '.join(cmd)}")
    print("🌐 访问地址: http://localhost:8501")
    print("⏹️  按 Ctrl+C 停止服务")
    
    try:
        subprocess.run(cmd, cwd=script_dir)
    except KeyboardInterrupt:
        print("\n👋 RAG系统已停止")

if __name__ == "__main__":
    main()