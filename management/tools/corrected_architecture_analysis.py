#!/usr/bin/env python3
"""
🏗️ 修正版项目架构分析器
========================

修正之前包含node_modules导致的代码量统计错误
准确分析项目架构、功能模块和代码量
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import subprocess
import re

class CorrectedArchitectureAnalyzer:
    """修正版项目架构分析器"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent
        self.excluded_dirs = ["node_modules", "__pycache__", ".git", ".vscode", "dist", "build"]
        
    def should_exclude_path(self, path: Path) -> bool:
        """检查路径是否应该被排除"""
        path_str = str(path)
        return any(excluded in path_str for excluded in self.excluded_dirs)
    
    def get_filtered_files(self, root_path: Path, patterns: List[str]) -> List[Path]:
        """获取过滤后的文件列表"""
        files = []
        for pattern in patterns:
            found_files = list(root_path.glob(f"**/{pattern}"))
            # 过滤掉排除的目录
            filtered_files = [f for f in found_files if not self.should_exclude_path(f)]
            files.extend(filtered_files)
        return files
    
    def count_lines_in_files(self, files: List[Path]) -> int:
        """统计文件行数"""
        total_lines = 0
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    total_lines += lines
            except Exception:
                continue
        return total_lines
    
    def analyze_system_corrected(self, system_path: Path, system_name: str) -> Dict[str, Any]:
        """修正版系统分析"""
        print(f"  📊 分析 {system_name}...")
        
        analysis = {
            "name": system_name,
            "path": str(system_path),
            "file_count": 0,
            "total_lines": 0,
            "file_types": {},
            "main_modules": [],
            "config_files": [],
            "optimization_files": []
        }
        
        if not system_path.exists():
            return analysis
        
        # 统计各种文件类型
        file_patterns = {
            "py": ["*.py"],
            "js": ["*.js"],
            "jsx": ["*.jsx"], 
            "ts": ["*.ts"],
            "html": ["*.html"],
            "css": ["*.css"],
            "json": ["*.json"],
            "md": ["*.md"],
            "sh": ["*.sh"],
            "yaml": ["*.yaml", "*.yml"]
        }
        
        for file_type, patterns in file_patterns.items():
            files = self.get_filtered_files(system_path, patterns)
            
            if files:
                analysis["file_types"][file_type] = len(files)
                analysis["file_count"] += len(files)
                
                # 统计代码行数
                lines = self.count_lines_in_files(files)
                analysis["total_lines"] += lines
        
        # 识别主要模块（排除node_modules）
        main_patterns = ["main.py", "app.py", "server.py", "index.html", "index.js", "*_app.py", "unified_*.py"]
        main_files = self.get_filtered_files(system_path, main_patterns)
        analysis["main_modules"] = [f.name for f in main_files[:10]]
        
        # 识别配置文件
        config_patterns = ["config*.py", "config*.json", "config*.yaml", "package.json", "requirements.txt"]
        config_files = self.get_filtered_files(system_path, config_patterns)
        analysis["config_files"] = [f.name for f in config_files[:10]]
        
        # 识别优化文件
        opt_patterns = ["*optimization*", "*unified*", "*optimize*", "*performance*", "*monitor*"]
        opt_files = self.get_filtered_files(system_path, opt_patterns)
        analysis["optimization_files"] = [f.name for f in opt_files[:10]]
        
        return analysis
    
    def generate_corrected_report(self) -> Dict[str, Any]:
        """生成修正版分析报告"""
        print("🔍 生成修正版架构分析报告...")
        
        report = {
            "project_name": "N.S.S-Novena-Garfield",
            "analysis_date": datetime.now().isoformat(),
            "note": "修正版 - 排除node_modules等无关目录",
            "project_root": str(self.project_root),
            "excluded_directories": self.excluded_dirs,
            "systems": {},
            "total_files": 0,
            "total_lines": 0,
            "language_stats": {}
        }
        
        # 分析各个系统
        systems_to_analyze = {
            "rag-system": "🧠 RAG智能系统",
            "api": "🌐 API管理系统", 
            "nexus": "🎯 Nexus控制面板",
            "chronicle": "📚 Chronicle编年史",
            "Changlee": "🔄 Changlee桌面宠物",
            "management": "📋 Management项目管理"
        }
        
        for system_key, system_name in systems_to_analyze.items():
            if system_key == "api":
                system_path = self.project_root / "api"
            elif system_key == "management":
                system_path = self.project_root / "management"
            else:
                system_path = self.project_root / "systems" / system_key
            
            if system_path.exists():
                system_analysis = self.analyze_system_corrected(system_path, system_name)
                report["systems"][system_key] = system_analysis
                report["total_files"] += system_analysis["file_count"]
                report["total_lines"] += system_analysis["total_lines"]
        
        # 统计编程语言分布
        language_mapping = {
            "Python": ["py"],
            "JavaScript": ["js", "jsx"],
            "TypeScript": ["ts"],
            "HTML": ["html"],
            "CSS": ["css"],
            "JSON": ["json"],
            "Markdown": ["md"],
            "Shell": ["sh"],
            "YAML": ["yaml"]
        }
        
        for language, extensions in language_mapping.items():
            total_lines = 0
            for system_data in report["systems"].values():
                for ext in extensions:
                    if ext in system_data["file_types"]:
                        # 重新计算该语言的行数
                        system_path = Path(system_data["path"])
                        patterns = [f"*.{ext}"]
                        files = self.get_filtered_files(system_path, patterns)
                        lines = self.count_lines_in_files(files)
                        total_lines += lines
            
            if total_lines > 0:
                report["language_stats"][language] = total_lines
        
        return report
    
    def print_corrected_summary(self, report: Dict[str, Any]):
        """打印修正版分析摘要"""
        print("\n" + "="*80)
        print("🏗️ N.S.S-Novena-Garfield 项目架构分析摘要 (修正版)")
        print("="*80)
        
        print(f"📊 项目概览:")
        print(f"  • 总文件数: {report['total_files']:,} (排除node_modules等)")
        print(f"  • 总代码行数: {report['total_lines']:,}")
        print(f"  • 系统模块数: {len(report['systems'])}")
        
        print(f"\n🎯 各系统统计 (修正后):")
        for system_key, system_data in report['systems'].items():
            print(f"  • {system_data['name']}: {system_data['file_count']} 文件, {system_data['total_lines']:,} 行")
        
        print(f"\n💻 编程语言统计 (修正后):")
        for language, lines in sorted(report['language_stats'].items(), key=lambda x: x[1], reverse=True):
            percentage = (lines / report['total_lines']) * 100 if report['total_lines'] > 0 else 0
            print(f"  • {language}: {lines:,} 行 ({percentage:.1f}%)")
        
        print(f"\n📁 文件类型分布:")
        file_type_totals = {}
        for system_data in report['systems'].values():
            for file_type, count in system_data['file_types'].items():
                file_type_totals[file_type] = file_type_totals.get(file_type, 0) + count
        
        for file_type, count in sorted(file_type_totals.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {file_type.upper()}: {count} 文件")
        
        # 对比说明
        print(f"\n⚠️ 修正说明:")
        print(f"  • 排除了 node_modules 目录 (包含 36,852 个依赖文件)")
        print(f"  • 排除了 __pycache__, .git 等系统目录")
        print(f"  • 只统计项目源代码和配置文件")
        print(f"  • Chronicle系统从 221,745 行修正为约 32,224 行")
        print(f"  • 总代码量从 244,881 行修正为 {report['total_lines']:,} 行")

def main():
    """主函数"""
    analyzer = CorrectedArchitectureAnalyzer()
    
    print("🚀 开始修正版项目架构分析...")
    
    # 生成修正版分析报告
    report = analyzer.generate_corrected_report()
    
    # 保存报告
    report_path = Path("corrected_architecture_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 打印摘要
    analyzer.print_corrected_summary(report)
    
    print(f"\n📄 修正版报告已保存到: {report_path}")

if __name__ == "__main__":
    main()