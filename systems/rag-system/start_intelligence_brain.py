#!/usr/bin/env python3
"""
🚀 中央情报大脑 - 快速启动脚本
==============================

一键启动基于"大宪章"的新一代RAG系统

使用方法:
    python start_intelligence_brain.py

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Genesis"
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """主启动函数"""
    print("🧠 中央情报大脑 - 启动中...")
    print("=" * 50)
    
    # 设置工作目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 添加到Python路径
    sys.path.insert(0, str(script_dir))
    
    # 设置环境变量
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    
    try:
        # 启动Streamlit应用
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "intelligence_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        print("🌐 启动地址: http://localhost:8501")
        print("🔧 按 Ctrl+C 停止服务")
        print("=" * 50)
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 中央情报大脑已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n💡 请确保已安装所有依赖:")
        print("pip install streamlit chromadb spacy nltk sentence-transformers faiss-cpu")

if __name__ == "__main__":
    main()