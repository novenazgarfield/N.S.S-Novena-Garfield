#!/usr/bin/env python3
"""
🚀 中央情报大脑启动器
====================

启动基于"大宪章"构建的新一代RAG系统

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Genesis"
"""

import sys
import os
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查必要的依赖"""
    required_packages = [
        'streamlit',
        'chromadb', 
        'spacy',
        'nltk',
        'sentence_transformers',
        'faiss-cpu'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def download_nltk_data():
    """下载NLTK数据"""
    try:
        import nltk
        print("📥 下载NLTK数据...")
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        print("✅ NLTK数据下载完成")
    except Exception as e:
        print(f"⚠️ NLTK数据下载失败: {e}")

def setup_environment():
    """设置环境"""
    # 设置环境变量
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # 避免tokenizers警告
    
    # 创建必要的目录
    data_dir = project_root / "data"
    models_dir = data_dir / "models"
    chroma_dir = models_dir / "chroma_db"
    
    for directory in [data_dir, models_dir, chroma_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("✅ 环境设置完成")

def main():
    """主函数"""
    print("🧠 中央情报大脑启动器")
    print("=" * 50)
    print("基于'大宪章'的新一代RAG系统")
    print("版本: 2.0.0 - Genesis")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 下载NLTK数据
    download_nltk_data()
    
    # 设置环境
    setup_environment()
    
    # 启动Streamlit应用
    print("\n🚀 启动中央情报大脑...")
    print("=" * 50)
    
    app_path = project_root / "intelligence_app.py"
    
    if not app_path.exists():
        print(f"❌ 应用文件不存在: {app_path}")
        sys.exit(1)
    
    # 构建Streamlit命令
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.fileWatcherType", "none",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        print("🌐 访问地址: http://localhost:8501")
        print("🔧 使用 Ctrl+C 停止服务")
        print("=" * 50)
        
        # 启动应用
        subprocess.run(cmd, cwd=project_root)
        
    except KeyboardInterrupt:
        print("\n\n🛑 中央情报大脑已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()