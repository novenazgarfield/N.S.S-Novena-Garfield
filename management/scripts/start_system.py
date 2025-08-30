#!/usr/bin/env python3
"""
NEXUS AI 系统统一启动脚本
整合所有启动功能的主入口
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
WORKSPACE_DIR = SCRIPT_DIR.parent.parent
sys.path.append(str(SCRIPT_DIR / "management"))

def print_banner():
    """打印启动横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🚀 NEXUS AI 系统启动器                    ║
    ║                                                              ║
    ║  🤖 RAG智能问答系统  📱 前端界面  🌐 隧道服务  🔧 管理工具    ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def run_command(cmd, cwd=None, background=False):
    """执行命令"""
    try:
        if background:
            process = subprocess.Popen(
                cmd, shell=True, cwd=cwd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            return process
        else:
            result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
            return result
    except Exception as e:
        print(f"❌ 命令执行失败: {e}")
        return None

def start_simple_mode():
    """启动完整模式（原简化模式已升级为完整功能）"""
    print("🚀 启动完整RAG系统...")
    
    # 使用完整版RAG系统
    rag_dir = WORKSPACE_DIR.parent / "systems" / "rag-system"
    
    # 启动完整版RAG API服务
    print("  📡 启动完整版RAG API服务...")
    api_process = run_command(
        f"python {rag_dir}/smart_rag_server.py",
        background=True
    )
    
    if api_process:
        print("  ✅ API服务已启动")
        time.sleep(3)
        
        # 启动前端服务
        print("  🌐 启动前端服务...")
        frontend_process = run_command(
            f"python -m http.server 53870 --bind 0.0.0.0",
            cwd=WORKSPACE_DIR / "systems" / "nexus",
            background=True
        )
        
        if frontend_process:
            print("  ✅ 前端服务已启动")
            print("\n🎉 简化模式启动完成！")
            print("📱 前端访问: http://localhost:53870")
            print("🤖 API访问: http://localhost:5000")
            print("📊 健康检查: http://localhost:5000/api/health")
            return True
    
    print("❌ 简化模式启动失败")
    return False

def start_tunnel_mode():
    """启动隧道模式"""
    print("🌐 启动隧道模式...")
    
    deployment_dir = SCRIPT_DIR / "deployment"
    tunnel_script = deployment_dir / "start_tunnels.sh"
    
    if not tunnel_script.exists():
        print(f"❌ 隧道脚本不存在: {tunnel_script}")
        return False
    
    # 确保脚本有执行权限
    os.chmod(tunnel_script, 0o755)
    
    # 执行隧道启动脚本
    result = run_command(f"bash {tunnel_script}")
    
    if result and result.returncode == 0:
        print("✅ 隧道模式启动完成")
        return True
    else:
        print("❌ 隧道模式启动失败")
        if result:
            print(f"错误输出: {result.stderr}")
        return False

def check_status():
    """检查系统状态"""
    print("🔍 检查系统状态...")
    
    management_dir = SCRIPT_DIR / "management"
    status_script = management_dir / "service_status.py"
    
    if status_script.exists():
        result = run_command(f"python {status_script}")
        if result:
            print(result.stdout)
    else:
        print("❌ 状态检查脚本不存在")

def run_tests():
    """运行测试"""
    print("🧪 运行API测试...")
    
    testing_dir = SCRIPT_DIR / "testing"
    test_script = testing_dir / "test_api.py"
    
    if test_script.exists():
        result = run_command(f"python {test_script}")
        if result:
            print(result.stdout)
            if result.stderr:
                print("错误输出:", result.stderr)
    else:
        print("❌ 测试脚本不存在")

def stop_services():
    """停止所有服务"""
    print("🛑 停止所有服务...")
    
    # 停止Python进程
    run_command("pkill -f smart_rag_server.py")
    run_command("pkill -f online_rag_api.py")
    run_command("pkill -f 'http.server 53870'")
    run_command("pkill -f cloudflared")
    
    print("✅ 所有服务已停止")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="NEXUS AI 系统启动器")
    parser.add_argument("action", choices=[
        "simple", "tunnel", "status", "test", "stop", "help"
    ], help="要执行的操作")
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.action == "simple":
        start_simple_mode()
    elif args.action == "tunnel":
        start_tunnel_mode()
    elif args.action == "status":
        check_status()
    elif args.action == "test":
        run_tests()
    elif args.action == "stop":
        stop_services()
    elif args.action == "help":
        print_help()

def print_help():
    """打印帮助信息"""
    help_text = """
🎯 NEXUS AI 系统启动器使用指南

📋 可用命令:
  simple    启动简化模式 (本地访问)
  tunnel    启动隧道模式 (外网访问)
  status    检查系统状态
  test      运行API测试
  stop      停止所有服务
  help      显示此帮助信息

💡 使用示例:
  python start_system.py simple   # 启动简化模式
  python start_system.py tunnel   # 启动隧道模式
  python start_system.py status   # 检查状态
  python start_system.py test     # 运行测试
  python start_system.py stop     # 停止服务

🔧 模式说明:
  • 简化模式: 仅启动本地服务，适合开发测试
  • 隧道模式: 启动Cloudflare隧道，支持外网访问

📁 相关目录:
  • deployment/  部署脚本
  • management/  管理脚本
  • testing/     测试脚本

⚠️  注意事项:
  • 隧道模式需要cloudflared工具
  • 确保端口5000和53870未被占用
  • 隧道URL是临时的，重启后会变化
    """
    print(help_text)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_help()
    else:
        main()