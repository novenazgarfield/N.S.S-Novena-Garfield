#!/usr/bin/env python3
"""
Genome Jigsaw 系统初始化脚本
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, check=True):
    """运行命令"""
    print(f"🔧 执行: {command}")
    result = subprocess.run(command, shell=True, check=check)
    return result.returncode == 0

def setup_environment():
    """设置环境"""
    print("🌟 设置 Genome Jigsaw 环境...")
    
    # 创建虚拟环境
    if not Path("venv").exists():
        print("📦 创建Python虚拟环境...")
        run_command("python -m venv venv")
    
    # 激活虚拟环境并安装依赖
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
    else:  # Unix/Linux/Mac
        activate_cmd = "source venv/bin/activate"
    
    print("📚 安装Python依赖...")
    run_command(f"{activate_cmd} && pip install --upgrade pip")
    run_command(f"{activate_cmd} && pip install -r requirements.txt")

def setup_directories():
    """创建必要的目录"""
    print("📁 创建项目目录...")
    
    directories = [
        "data/raw",
        "data/processed", 
        "data/reference",
        "data/results",
        "data/temp",
        "logs",
        "tests/data",
        "docs/build"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")

def download_test_data():
    """下载测试数据"""
    print("🧬 下载测试数据...")
    
    # 这里可以添加下载测试数据的逻辑
    # 例如下载小的FASTQ文件用于测试
    test_data_url = "https://example.com/test_data.fastq.gz"
    test_data_path = "data/raw/test_sample.fastq.gz"
    
    print(f"   📥 下载测试数据到 {test_data_path}")
    # run_command(f"wget -O {test_data_path} {test_data_url}", check=False)

def setup_database():
    """设置数据库"""
    print("🗄️ 设置数据库...")
    
    # 检查PostgreSQL是否可用
    if run_command("which psql", check=False):
        print("   ✅ PostgreSQL 已安装")
        # 这里可以添加创建数据库的逻辑
    else:
        print("   ⚠️ PostgreSQL 未安装，请手动安装")
    
    # 检查Redis是否可用
    if run_command("which redis-cli", check=False):
        print("   ✅ Redis 已安装")
    else:
        print("   ⚠️ Redis 未安装，请手动安装")

def check_bioinformatics_tools():
    """检查生物信息学工具"""
    print("🔬 检查生物信息学工具...")
    
    tools = {
        "fastqc": "FastQC",
        "bwa": "BWA",
        "samtools": "SAMtools",
        "bcftools": "BCFtools",
        "gatk": "GATK"
    }
    
    for tool, name in tools.items():
        if run_command(f"which {tool}", check=False):
            print(f"   ✅ {name} 已安装")
        else:
            print(f"   ⚠️ {name} 未安装")

def create_config():
    """创建配置文件"""
    print("⚙️ 创建配置文件...")
    
    config_file = Path("config/local.yaml")
    if not config_file.exists():
        # 复制默认配置
        import shutil
        shutil.copy("config/default.yaml", config_file)
        print(f"   ✅ 创建本地配置文件: {config_file}")
    else:
        print(f"   ℹ️ 配置文件已存在: {config_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Genome Jigsaw 系统初始化")
    parser.add_argument("--skip-env", action="store_true", help="跳过环境设置")
    parser.add_argument("--skip-data", action="store_true", help="跳过测试数据下载")
    parser.add_argument("--skip-db", action="store_true", help="跳过数据库设置")
    
    args = parser.parse_args()
    
    print("🧬 Genome Jigsaw 系统初始化")
    print("=" * 50)
    
    # 创建目录
    setup_directories()
    
    # 设置环境
    if not args.skip_env:
        setup_environment()
    
    # 下载测试数据
    if not args.skip_data:
        download_test_data()
    
    # 设置数据库
    if not args.skip_db:
        setup_database()
    
    # 检查工具
    check_bioinformatics_tools()
    
    # 创建配置
    create_config()
    
    print("\n🎉 Genome Jigsaw 初始化完成！")
    print("\n📖 下一步:")
    print("   1. 配置 config/local.yaml 文件")
    print("   2. 安装缺失的生物信息学工具")
    print("   3. 运行 python src/main.py 启动系统")

if __name__ == "__main__":
    main()