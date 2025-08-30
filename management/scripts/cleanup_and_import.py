#!/usr/bin/env python3
"""
N.S.S-Novena-Garfield 项目清理和导入脚本
清理workspace并从GitHub导入最新项目
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

def print_banner():
    """打印横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║              🧹 N.S.S-Novena-Garfield 项目管理器              ║
    ║                                                              ║
    ║  🗑️ 清理工作区  📥 导入项目  🔧 系统优化  📊 状态检查        ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def cleanup_workspace():
    """清理workspace"""
    print("🧹 开始清理workspace...")
    
    # 动态发现项目根目录
    script_dir = Path(__file__).resolve().parent
    workspace = script_dir.parent.parent  # management/scripts -> management -> project_root
    
    if not workspace.exists():
        print(f"❌ 项目根目录不存在: {workspace}")
        return False
    
    # 保留的重要文件和目录
    keep_items = {
        '.git',
        '.gitignore',
        'README.md',
        'requirements.txt',
        'CNAME'
    }
    
    # 获取当前目录内容
    items = list(workspace.iterdir())
    
    print(f"📁 发现 {len(items)} 个项目")
    
    # 清理项目
    cleaned_count = 0
    for item in items:
        if item.name in keep_items:
            print(f"⚠️ 保留: {item.name}")
            continue
        
        try:
            if item.is_dir():
                shutil.rmtree(item)
                print(f"🗑️ 删除目录: {item.name}")
            else:
                item.unlink()
                print(f"🗑️ 删除文件: {item.name}")
            cleaned_count += 1
        except Exception as e:
            print(f"❌ 删除失败 {item.name}: {e}")
    
    print(f"✅ 清理完成，删除了 {cleaned_count} 个项目")
    return True

def import_project(github_url, token=None):
    """从GitHub导入项目"""
    print(f"📥 开始导入项目: {github_url}")
    
    # 动态发现项目根目录
    script_dir = Path(__file__).resolve().parent
    workspace = script_dir.parent.parent
    
    # 构建git命令
    if token:
        # 使用token的URL格式
        if github_url.startswith('https://github.com/'):
            auth_url = github_url.replace('https://github.com/', f'https://{token}@github.com/')
        else:
            print("❌ 无效的GitHub URL格式")
            return False
    else:
        auth_url = github_url
    
    try:
        # 克隆项目
        print("🔄 正在克隆项目...")
        result = subprocess.run(
            ['git', 'clone', auth_url, str(workspace / 'temp_clone')],
            capture_output=True,
            text=True,
            cwd=workspace
        )
        
        if result.returncode != 0:
            print(f"❌ 克隆失败: {result.stderr}")
            return False
        
        # 移动文件到workspace根目录
        temp_clone = workspace / 'temp_clone'
        if temp_clone.exists():
            print("📦 正在移动文件...")
            for item in temp_clone.iterdir():
                if item.name == '.git':
                    continue  # 跳过.git目录
                
                dest = workspace / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                
                shutil.move(str(item), str(dest))
                print(f"📁 移动: {item.name}")
            
            # 移动.git目录
            git_src = temp_clone / '.git'
            git_dest = workspace / '.git'
            if git_src.exists():
                if git_dest.exists():
                    shutil.rmtree(git_dest)
                shutil.move(str(git_src), str(git_dest))
                print("📁 移动: .git")
            
            # 删除临时目录
            shutil.rmtree(temp_clone)
        
        print("✅ 项目导入完成")
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def check_optimization_status():
    """检查系统优化状态"""
    print("📊 检查系统优化状态...")
    
    # 动态发现项目根目录
    script_dir = Path(__file__).resolve().parent
    workspace = script_dir.parent.parent
    systems_dir = workspace / "systems"
    
    if not systems_dir.exists():
        print("❌ systems目录不存在")
        return
    
    # 检查系统目录
    systems = [
        ("rag-system", "main.py"),
        ("Changlee", "changlee.js"),
        ("chronicle", "chronicle.js"),
        ("bovine-insight", "bovine.py"),
        ("genome-nebula", "genome.py"),
        ("kinetic-scope", "kinetic.py"),
        ("nexus", "nexus.py")
    ]
    
    print("\n🔧 系统优化状态:")
    optimized_count = 0
    
    for system_name, entry_file in systems:
        system_path = systems_dir / system_name
        entry_path = system_path / entry_file
        
        if system_path.exists() and entry_path.exists():
            print(f"   ✅ {system_name}: 已优化 ({entry_file})")
            optimized_count += 1
        elif system_path.exists():
            print(f"   ⚠️ {system_name}: 存在但未优化")
        else:
            print(f"   ❌ {system_name}: 不存在")
    
    # 检查API管理系统
    api = workspace / "api"
    api_entry = api / "api_manager.py"
    
    if api.exists() and api_entry.exists():
        print(f"   ✅ API管理系统: 已优化 (api_manager.py)")
        optimized_count += 1
    elif api.exists():
        print(f"   ⚠️ API管理系统: 存在但未优化")
    else:
        print(f"   ❌ API管理系统: 不存在")
    
    total_systems = len(systems) + 1  # +1 for API management
    print(f"\n📈 优化进度: {optimized_count}/{total_systems} ({optimized_count/total_systems*100:.1f}%)")
    
    # 检查优化报告
    print("\n📄 优化报告:")
    optimization_reports = list(workspace.glob("**/*OPTIMIZATION_COMPLETE.md"))
    print(f"   发现 {len(optimization_reports)} 个优化完成报告")
    
    for report in optimization_reports:
        relative_path = report.relative_to(workspace)
        print(f"   📋 {relative_path}")

def show_project_structure():
    """显示项目结构"""
    print("📁 项目结构:")
    
    # 动态发现项目根目录
    script_dir = Path(__file__).resolve().parent
    workspace = script_dir.parent.parent
    
    if not workspace.exists():
        print(f"❌ 项目根目录不存在: {workspace}")
        return
    
    # 显示主要目录
    main_dirs = [
        "systems",
        "api", 
        "scripts",
        "docs",
        "tests",
        "tools"
    ]
    
    for dir_name in main_dirs:
        dir_path = workspace / dir_name
        if dir_path.exists():
            subdirs = [d.name for d in dir_path.iterdir() if d.is_dir()]
            files = [f.name for f in dir_path.iterdir() if f.is_file()]
            print(f"   📁 {dir_name}/ ({len(subdirs)} 目录, {len(files)} 文件)")
            
            # 显示系统子目录
            if dir_name == "systems" and subdirs:
                for subdir in sorted(subdirs)[:5]:  # 只显示前5个
                    print(f"      📂 {subdir}/")
                if len(subdirs) > 5:
                    print(f"      ... 还有 {len(subdirs) - 5} 个目录")
        else:
            print(f"   ❌ {dir_name}/ (不存在)")

def run_system_tests():
    """运行系统测试"""
    print("🧪 运行系统测试...")
    
    # 动态发现项目根目录
    script_dir = Path(__file__).resolve().parent
    workspace = script_dir.parent.parent
    
    # 测试统一入口点
    test_commands = [
        ("RAG-System", "systems/rag-system/main.py", ["--help"]),
        ("Changlee", "systems/Changlee/changlee.js", ["--help"]),
        ("Chronicle", "systems/chronicle/chronicle.js", ["--help"]),
        ("Bovine-Insight", "systems/bovine-insight/bovine.py", ["--help"]),
        ("Genome-Nebula", "systems/genome-nebula/genome.py", ["--help"]),
        ("Kinetic-Scope", "systems/kinetic-scope/kinetic.py", ["--help"]),
        ("NEXUS", "systems/nexus/nexus.py", ["--help"]),
        ("API管理系统", "api/api_manager.py", ["--help"])
    ]
    
    print("\n🔍 测试统一入口点:")
    success_count = 0
    
    for system_name, script_path, args in test_commands:
        full_path = workspace / script_path
        
        if not full_path.exists():
            print(f"   ❌ {system_name}: 文件不存在 ({script_path})")
            continue
        
        try:
            # 确定运行命令
            if script_path.endswith('.py'):
                cmd = ['python', str(full_path)] + args
            elif script_path.endswith('.js'):
                cmd = ['node', str(full_path)] + args
            else:
                print(f"   ❌ {system_name}: 未知文件类型")
                continue
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=full_path.parent
            )
            
            if result.returncode == 0:
                print(f"   ✅ {system_name}: 入口点正常")
                success_count += 1
            else:
                print(f"   ⚠️ {system_name}: 入口点异常 (退出码: {result.returncode})")
                
        except subprocess.TimeoutExpired:
            print(f"   ⚠️ {system_name}: 测试超时")
        except Exception as e:
            print(f"   ❌ {system_name}: 测试失败 ({e})")
    
    total_tests = len(test_commands)
    print(f"\n📊 测试结果: {success_count}/{total_tests} ({success_count/total_tests*100:.1f}%) 通过")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="N.S.S-Novena-Garfield 项目管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'action',
        choices=['cleanup', 'import', 'status', 'structure', 'test', 'all'],
        help='要执行的操作'
    )
    
    parser.add_argument('--url', help='GitHub项目URL')
    parser.add_argument('--token', help='GitHub访问令牌')
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.action == 'cleanup':
        cleanup_workspace()
    
    elif args.action == 'import':
        if not args.url:
            print("❌ 请提供GitHub项目URL (--url)")
            sys.exit(1)
        import_project(args.url, args.token)
    
    elif args.action == 'status':
        check_optimization_status()
    
    elif args.action == 'structure':
        show_project_structure()
    
    elif args.action == 'test':
        run_system_tests()
    
    elif args.action == 'all':
        if args.url:
            print("🔄 执行完整流程...")
            if cleanup_workspace():
                if import_project(args.url, args.token):
                    print("\n" + "="*60)
                    check_optimization_status()
                    print("\n" + "="*60)
                    show_project_structure()
                    print("\n" + "="*60)
                    run_system_tests()
        else:
            print("❌ 完整流程需要提供GitHub项目URL (--url)")
            sys.exit(1)
    
    print("\n✅ 操作完成")

if __name__ == "__main__":
    main()