#!/usr/bin/env python3
"""
NEXUS Research Workstation - 依赖检查工具
检查并安装项目所需的依赖包
"""

import sys
import subprocess
import importlib
import pkg_resources
from pathlib import Path
import json

class DependencyChecker:
    def __init__(self):
        self.missing_packages = []
        self.installed_packages = []
        self.failed_packages = []
        
    def check_package(self, package_name, import_name=None):
        """检查单个包是否已安装"""
        if import_name is None:
            import_name = package_name
            
        try:
            importlib.import_module(import_name)
            self.installed_packages.append(package_name)
            return True
        except ImportError:
            self.missing_packages.append(package_name)
            return False
    
    def install_package(self, package_name):
        """安装单个包"""
        try:
            print(f"📦 正在安装 {package_name}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package_name
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {package_name} 安装成功")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ {package_name} 安装失败")
            self.failed_packages.append(package_name)
            return False
    
    def check_core_dependencies(self):
        """检查核心依赖"""
        print("🔍 检查核心依赖...")
        
        core_deps = {
            'numpy': 'numpy',
            'opencv-python': 'cv2',
            'Pillow': 'PIL',
            'torch': 'torch',
            'torchvision': 'torchvision',
            'scikit-learn': 'sklearn',
            'pandas': 'pandas',
            'matplotlib': 'matplotlib',
            'requests': 'requests',
            'pyyaml': 'yaml',
        }
        
        for package, import_name in core_deps.items():
            self.check_package(package, import_name)
    
    def check_bovine_insight_dependencies(self):
        """检查BovineInsight特定依赖"""
        print("🐄 检查BovineInsight依赖...")
        
        bovine_deps = {
            'ultralytics': 'ultralytics',
            'pytesseract': 'pytesseract',
            'easyocr': 'easyocr',
            'sqlalchemy': 'sqlalchemy',
            'loguru': 'loguru',
            'tqdm': 'tqdm',
            'psutil': 'psutil',
        }
        
        for package, import_name in bovine_deps.items():
            self.check_package(package, import_name)
    
    def check_optional_dependencies(self):
        """检查可选依赖"""
        print("🔧 检查可选依赖...")
        
        optional_deps = {
            'transformers': 'transformers',
            'accelerate': 'accelerate',
            'albumentations': 'albumentations',
            'timm': 'timm',
            'streamlit': 'streamlit',
            'plotly': 'plotly',
        }
        
        for package, import_name in optional_deps.items():
            self.check_package(package, import_name)
    
    def install_missing_packages(self):
        """安装缺失的包"""
        if not self.missing_packages:
            print("✅ 所有依赖都已安装！")
            return
        
        print(f"\n📋 发现 {len(self.missing_packages)} 个缺失的包:")
        for pkg in self.missing_packages:
            print(f"  • {pkg}")
        
        install_choice = input("\n是否自动安装缺失的包? (y/n): ").lower().strip()
        
        if install_choice == 'y':
            print("\n🚀 开始安装缺失的包...")
            for package in self.missing_packages:
                self.install_package(package)
        else:
            print("⏭️ 跳过自动安装")
    
    def generate_report(self):
        """生成依赖检查报告"""
        report = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "python_version": sys.version,
            "installed_packages": self.installed_packages,
            "missing_packages": self.missing_packages,
            "failed_packages": self.failed_packages,
            "total_checked": len(self.installed_packages) + len(self.missing_packages),
            "success_rate": len(self.installed_packages) / (len(self.installed_packages) + len(self.missing_packages)) * 100
        }
        
        # 保存报告
        report_file = Path("dependency_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def print_summary(self):
        """打印检查摘要"""
        total = len(self.installed_packages) + len(self.missing_packages)
        success_rate = len(self.installed_packages) / total * 100 if total > 0 else 0
        
        print("\n" + "="*60)
        print("📊 依赖检查摘要")
        print("="*60)
        print(f"✅ 已安装: {len(self.installed_packages)} 个包")
        print(f"❌ 缺失: {len(self.missing_packages)} 个包")
        print(f"🚫 安装失败: {len(self.failed_packages)} 个包")
        print(f"📈 成功率: {success_rate:.1f}%")
        print("="*60)
        
        if self.missing_packages:
            print("\n❌ 缺失的包:")
            for pkg in self.missing_packages:
                print(f"  • {pkg}")
        
        if self.failed_packages:
            print("\n🚫 安装失败的包:")
            for pkg in self.failed_packages:
                print(f"  • {pkg}")
        
        print(f"\n📄 详细报告已保存到: dependency_report.json")

def main():
    print("🚀 NEXUS Research Workstation - 依赖检查工具")
    print("="*60)
    
    checker = DependencyChecker()
    
    # 检查各类依赖
    checker.check_core_dependencies()
    checker.check_bovine_insight_dependencies()
    checker.check_optional_dependencies()
    
    # 安装缺失的包
    checker.install_missing_packages()
    
    # 生成报告
    report = checker.generate_report()
    
    # 打印摘要
    checker.print_summary()
    
    # 返回状态码
    if checker.missing_packages or checker.failed_packages:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())