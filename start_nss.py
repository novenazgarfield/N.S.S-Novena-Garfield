#!/usr/bin/env python3
"""
🚀 N.S.S 一键启动脚本
自动启动所有服务并显示访问地址
"""

import sys
import os
from pathlib import Path

# 添加管理服务路径
sys.path.append(str(Path(__file__).parent / "management" / "services"))

from smart_launcher import SmartLauncher

def main():
    print("🌟 N.S.S-Novena-Garfield 智能启动系统")
    print("=" * 50)
    print("🔧 功能特性:")
    print("  • 自动端口分配，避免冲突")
    print("  • 动态服务发现")
    print("  • 自动隧道创建")
    print("  • 前后端自动连接")
    print("=" * 50)
    
    try:
        launcher = SmartLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n👋 感谢使用 N.S.S 系统！")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()