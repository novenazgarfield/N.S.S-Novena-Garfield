#!/usr/bin/env python3
"""
NEXUS Research Workstation - Changlee桌宠启动器
快速启动长离的学习胶囊桌面宠物系统
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_node_installed():
    """检查Node.js是否已安装"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js已安装: {version}")
            return True
        else:
            print("❌ Node.js未安装")
            return False
    except FileNotFoundError:
        print("❌ Node.js未安装")
        return False

def check_npm_installed():
    """检查npm是否已安装"""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ npm已安装: {version}")
            return True
        else:
            print("❌ npm未安装")
            return False
    except FileNotFoundError:
        print("❌ npm未安装")
        return False

def install_dependencies():
    """安装Changlee依赖"""
    changlee_path = Path("/workspace/systems/Changlee")
    
    if not changlee_path.exists():
        print("❌ Changlee项目目录不存在")
        return False
    
    print("📦 正在安装Changlee依赖...")
    
    try:
        # 切换到Changlee目录并安装依赖
        os.chdir(changlee_path)
        result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 依赖安装成功")
            return True
        else:
            print(f"❌ 依赖安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")
        return False

def start_changlee():
    """启动Changlee桌宠"""
    changlee_path = Path("/workspace/systems/Changlee")
    
    if not changlee_path.exists():
        print("❌ Changlee项目目录不存在")
        return False
    
    print("🚀 正在启动Changlee桌面宠物...")
    
    try:
        os.chdir(changlee_path)
        
        # 检查是否有start脚本
        if Path("start.js").exists():
            print("📱 使用start.js启动...")
            subprocess.Popen(['node', 'start.js'])
        elif Path("easy_start.js").exists():
            print("📱 使用easy_start.js启动...")
            subprocess.Popen(['node', 'easy_start.js'])
        else:
            print("📱 使用npm start启动...")
            subprocess.Popen(['npm', 'start'])
        
        print("✅ Changlee启动成功！")
        print("🐱 长离正在准备与你见面...")
        return True
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def show_changlee_info():
    """显示Changlee信息"""
    info = """
🐱 Changlee - 长离的学习胶囊

🎯 项目简介：
一款以"情感陪伴"为核心的桌面宠物英语学习应用。
通过与AI伙伴"长离"的日常互动，将枯燥的单词记忆转化为趣味学习体验。

🌟 核心特性：
• 🐱 智能桌宠 - 可拖拽的2D宠物，多种状态动画
• 📮 漂流瓶推送 - 智能时机推送学习内容，避免打扰
• 💊 学习胶囊 - 美观的卡片式学习界面
• 🏖️ 魔法沙滩 - 游戏化拼写练习
• 🤖 长离AI - 基于Gemini的个性化内容生成
• 📚 智能复习 - 间隔重复算法优化记忆

🏗️ 技术架构：
• 前端: Electron + React + CSS Animation
• 后端: Node.js + Express + SQLite
• AI集成: Google Gemini API
• 动画: CSS3 + Canvas
• 数据: SQLite + 间隔重复算法

💡 使用提示：
1. 首次启动会自动安装依赖包
2. 长离会在桌面右下角出现
3. 可以拖拽长离到任意位置
4. 点击长离开始学习互动
5. 接收漂流瓶学习任务

🚀 准备启动长离的学习胶囊！
    """
    print(info)

def main():
    print("🚀 NEXUS Research Workstation - Changlee启动器")
    print("="*60)
    
    show_changlee_info()
    
    # 检查环境
    print("\n🔍 检查运行环境...")
    
    if not check_node_installed():
        print("\n❌ 请先安装Node.js: https://nodejs.org/")
        return 1
    
    if not check_npm_installed():
        print("\n❌ 请先安装npm包管理器")
        return 1
    
    # 询问是否安装依赖
    install_deps = input("\n📦 是否安装/更新Changlee依赖？(y/n): ").lower().strip()
    
    if install_deps == 'y':
        if not install_dependencies():
            print("\n❌ 依赖安装失败，无法启动Changlee")
            return 1
    
    # 询问是否启动
    start_app = input("\n🚀 是否启动Changlee桌面宠物？(y/n): ").lower().strip()
    
    if start_app == 'y':
        if start_changlee():
            print("\n🎉 Changlee启动成功！")
            print("🐱 长离正在桌面等待与你互动...")
            print("💡 提示：如果没有看到长离，请检查系统托盘")
            return 0
        else:
            print("\n❌ Changlee启动失败")
            return 1
    else:
        print("\n⏭️ 跳过启动")
        return 0

if __name__ == "__main__":
    sys.exit(main())