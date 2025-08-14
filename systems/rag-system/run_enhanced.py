#!/usr/bin/env python3
"""
增强版RAG系统启动脚本
支持多API和分布式计算
"""
import sys
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = [
        "streamlit",
        "sentence_transformers", 
        "faiss_cpu",
        "torch",
        "transformers"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 核心依赖检查通过")
    return True

def check_gpu():
    """检查GPU状态"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            print(f"✅ 检测到 {gpu_count} 个GPU设备:")
            
            for i in range(gpu_count):
                gpu_name = torch.cuda.get_device_name(i)
                memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print(f"  GPU {i}: {gpu_name} ({memory:.1f} GB)")
            
            return True
        else:
            print("⚠️  未检测到CUDA GPU，将使用CPU模式")
            return False
    except Exception as e:
        print(f"⚠️  GPU检查失败: {e}")
        return False

def run_config_manager():
    """运行配置管理器"""
    script_dir = Path(__file__).parent
    config_script = script_dir / "config_manager.py"
    
    if not config_script.exists():
        print(f"❌ 配置管理脚本不存在: {config_script}")
        return False
    
    try:
        subprocess.run([sys.executable, str(config_script)], cwd=script_dir)
        return True
    except Exception as e:
        print(f"❌ 运行配置管理器失败: {e}")
        return False

def run_streamlit_app(app_type="enhanced", port=8501, host="0.0.0.0"):
    """运行Streamlit应用"""
    script_dir = Path(__file__).parent
    
    if app_type == "enhanced":
        app_path = script_dir / "app_enhanced.py"
    elif app_type == "simple":
        app_path = script_dir / "app_simple.py"
    else:
        app_path = script_dir / "app.py"
    
    if not app_path.exists():
        print(f"❌ 应用文件不存在: {app_path}")
        return False
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        str(app_path),
        "--server.port", str(port),
        "--server.address", host,
        "--server.allowRunOnSave", "true",
        "--server.runOnSave", "true",
        "--theme.base", "dark"
    ]
    
    print(f"🚀 启动命令: {' '.join(cmd)}")
    print(f"🌐 访问地址: http://localhost:{port}")
    print("⏹️  按 Ctrl+C 停止服务")
    
    try:
        subprocess.run(cmd, cwd=script_dir)
        return True
    except KeyboardInterrupt:
        print("\n👋 RAG系统已停止")
        return True
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def run_cli_demo():
    """运行命令行演示"""
    script_dir = Path(__file__).parent
    demo_script = script_dir / "app_simple.py"
    
    if not demo_script.exists():
        print(f"❌ 演示脚本不存在: {demo_script}")
        return False
    
    try:
        subprocess.run([sys.executable, str(demo_script)], cwd=script_dir)
        return True
    except Exception as e:
        print(f"❌ 运行演示失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="增强版RAG系统启动器")
    parser.add_argument("--mode", choices=["web", "cli", "config"], default="web",
                       help="运行模式: web(Web界面), cli(命令行), config(配置管理)")
    parser.add_argument("--app", choices=["enhanced", "simple", "basic"], default="enhanced",
                       help="应用类型: enhanced(增强版), simple(简化版), basic(基础版)")
    parser.add_argument("--port", type=int, default=8501, help="Web服务端口")
    parser.add_argument("--host", default="0.0.0.0", help="Web服务主机")
    parser.add_argument("--skip-check", action="store_true", help="跳过依赖检查")
    
    args = parser.parse_args()
    
    print("🚀 启动增强版RAG系统...")
    print(f"运行模式: {args.mode}")
    
    # 检查依赖
    if not args.skip_check:
        if not check_dependencies():
            sys.exit(1)
        
        # 检查GPU（可选）
        check_gpu()
    
    # 根据模式运行
    if args.mode == "config":
        success = run_config_manager()
    elif args.mode == "cli":
        success = run_cli_demo()
    elif args.mode == "web":
        success = run_streamlit_app(args.app, args.port, args.host)
    else:
        print(f"❌ 未知模式: {args.mode}")
        success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()