#!/usr/bin/env python3
"""
NEXUS Research Workstation - 核心依赖安装器
只安装最必要的核心依赖包
"""

import sys
import subprocess

def install_package(package_name):
    """安装单个包"""
    try:
        print(f"📦 正在安装 {package_name}...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package_name, "--quiet"
        ])
        print(f"✅ {package_name} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package_name} 安装失败: {e}")
        return False

def main():
    print("🚀 NEXUS Research Workstation - 核心依赖安装器")
    print("="*60)
    
    # 只安装最核心的依赖
    core_packages = [
        "opencv-python",
        "matplotlib", 
        "sqlalchemy",
        "plotly"
    ]
    
    print(f"📋 将安装 {len(core_packages)} 个核心包:")
    for pkg in core_packages:
        print(f"  • {pkg}")
    
    print("\n🚀 开始安装...")
    
    success_count = 0
    for package in core_packages:
        if install_package(package):
            success_count += 1
    
    print("\n" + "="*60)
    print(f"📊 安装完成: {success_count}/{len(core_packages)} 个包安装成功")
    print("="*60)
    
    if success_count == len(core_packages):
        print("✅ 所有核心依赖安装成功！")
        return 0
    else:
        print("⚠️ 部分依赖安装失败，但系统仍可基本运行")
        return 1

if __name__ == "__main__":
    sys.exit(main())