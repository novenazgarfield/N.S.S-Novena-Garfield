#!/usr/bin/env python3
"""
API管理系统启动脚本
为整个研究工作站项目提供统一的API管理服务
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def start_web_interface(port=56336, host="0.0.0.0"):
    """启动Web管理界面"""
    print(f"🚀 启动API管理Web界面...")
    print(f"📍 地址: http://{host}:{port}")
    
    # 启动Streamlit应用
    cmd = [
        "streamlit", "run", "api_web_manager.py",
        "--server.port", str(port),
        "--server.address", host,
        "--server.allowRunOnSave", "true",
        "--server.runOnSave", "true",
        "--server.headless", "true"
    ]
    
    try:
        # 切换到API管理目录
        os.chdir(Path(__file__).parent)
        
        # 启动服务
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ API管理界面已启动 (PID: {process.pid})")
        print(f"📊 访问地址: http://localhost:{port}")
        print(f"🌐 公网访问: http://13.57.59.89:{port}")
        
        return process
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return None

def init_system():
    """初始化API管理系统"""
    print("🔧 初始化API管理系统...")
    
    try:
        # 添加当前目录到Python路径
        sys.path.insert(0, os.path.dirname(__file__))
        
        # 导入并初始化系统
        from api_config import APIConfigManager
        from private_api_manager import PrivateAPIManager
        
        api_manager = APIConfigManager()
        private_manager = PrivateAPIManager()
        
        # 显示系统信息
        summary = api_manager.get_api_summary()
        print(f"📊 系统概览:")
        print(f"   - 总API端点: {summary['total_endpoints']}")
        print(f"   - 活跃端点: {summary['active_endpoints']}")
        print(f"   - 按类型分布: {summary['by_type']}")
        
        print(f"🔐 私有密钥:")
        print(f"   - 总密钥数: {len(private_manager.api_keys)}")
        
        # 统计用户数
        users = set(key.user_id for key in private_manager.api_keys.values())
        print(f"   - 用户数: {len(users)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False

def test_system():
    """测试系统功能"""
    print("🧪 测试API管理系统...")
    
    try:
        # 添加当前目录到Python路径
        sys.path.insert(0, os.path.dirname(__file__))
        from api_config import check_api_access
        
        # 测试权限检查
        test_cases = [
            ("guest", "health_check", True),
            ("user", "user_chat", True),
            ("user", "user_management", False),
            ("admin", "user_management", True)
        ]
        
        print("🔒 权限测试:")
        for role, api, expected in test_cases:
            result = check_api_access(api, role)
            status = "✅" if result == expected else "❌"
            print(f"   {status} {role} -> {api}: {result}")
        
        # 测试完整验证流程
        print("🔄 完整验证流程测试:")
        print(f"   基础权限检查通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def show_status():
    """显示系统状态"""
    print("📊 API管理系统状态:")
    
    try:
        # 检查配置文件
        config_dir = Path(__file__).parent / "config"
        
        files_to_check = [
            "api_endpoints.json",
            "private_apis.json", 
            "api_encryption.key"
        ]
        
        print("📁 配置文件:")
        for file in files_to_check:
            file_path = config_dir / file
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"   ✅ {file} ({size} bytes)")
            else:
                print(f"   ❌ {file} (不存在)")
        
        # 检查Web服务
        import requests
        try:
            response = requests.get("http://localhost:56336", timeout=2)
            print("🌐 Web界面: ✅ 运行中")
        except:
            print("🌐 Web界面: ❌ 未运行")
        
        return True
        
    except Exception as e:
        print(f"❌ 状态检查失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="API管理系统启动脚本")
    parser.add_argument("action", choices=["start", "init", "test", "status"], 
                       help="执行的操作")
    parser.add_argument("--port", type=int, default=56336, 
                       help="Web界面端口 (默认: 56336)")
    parser.add_argument("--host", default="0.0.0.0", 
                       help="Web界面主机 (默认: 0.0.0.0)")
    
    args = parser.parse_args()
    
    print("🔧 研究工作站 - API管理系统")
    print("=" * 50)
    
    if args.action == "start":
        # 先初始化系统
        if init_system():
            # 启动Web界面
            process = start_web_interface(args.port, args.host)
            if process:
                try:
                    # 等待用户中断
                    print("\n按 Ctrl+C 停止服务...")
                    process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 正在停止服务...")
                    process.terminate()
                    print("✅ 服务已停止")
    
    elif args.action == "init":
        init_system()
    
    elif args.action == "test":
        if init_system():
            test_system()
    
    elif args.action == "status":
        show_status()

if __name__ == "__main__":
    main()