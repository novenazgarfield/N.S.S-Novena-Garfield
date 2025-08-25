#!/usr/bin/env python3
"""
快速更新部署脚本
"""

import os
import shutil
import subprocess
import sys

def main():
    print("🚀 开始更新部署...")
    
    # 确保在正确的目录
    os.chdir('/workspace/N.S.S-Novena-Garfield/systems/nexus')
    
    # 构建项目
    print("📦 构建项目...")
    result = subprocess.run(['node', 'build.js'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 构建失败: {result.stderr}")
        return False
    
    print("✅ 构建完成!")
    
    # 检查dist目录
    if not os.path.exists('dist'):
        print("❌ dist目录不存在")
        return False
    
    # 显示更新的文件
    print("📄 更新的文件:")
    for file in os.listdir('dist'):
        if file.endswith('.html'):
            print(f"   ✓ {file}")
    
    print("🎉 更新完成!")
    print("💡 请手动将dist目录中的文件上传到你的部署平台")
    
    return True

if __name__ == "__main__":
    main()