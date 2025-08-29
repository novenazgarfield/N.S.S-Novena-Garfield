#!/usr/bin/env python3
"""
🏗️ N.S.S-Novena-Garfield 项目架构分析器
==========================================

全面分析项目架构、功能模块和代码量
生成详细的架构分析报告
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import subprocess
import re

class ProjectArchitectureAnalyzer:
    """项目架构分析器"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent
        self.analysis_results = {}
        
    def analyze_project_structure(self) -> Dict[str, Any]:
        """分析项目整体结构"""
        print("🔍 分析项目整体结构...")
        
        structure = {
            "project_name": "N.S.S-Novena-Garfield",
            "analysis_date": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "total_files": 0,
            "total_lines": 0,
            "systems": {},
            "file_types": {},
            "optimization_status": {}
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
                system_analysis = self.analyze_system(system_path, system_name)
                structure["systems"][system_key] = system_analysis
                structure["total_files"] += system_analysis["file_count"]
                structure["total_lines"] += system_analysis["total_lines"]
        
        # 分析文件类型分布
        structure["file_types"] = self.analyze_file_types()
        
        # 分析优化状态
        structure["optimization_status"] = self.analyze_optimization_status()
        
        return structure
    
    def analyze_system(self, system_path: Path, system_name: str) -> Dict[str, Any]:
        """分析单个系统"""
        print(f"  📊 分析 {system_name}...")
        
        analysis = {
            "name": system_name,
            "path": str(system_path),
            "file_count": 0,
            "total_lines": 0,
            "file_types": {},
            "main_modules": [],
            "config_files": [],
            "optimization_files": [],
            "key_features": []
        }
        
        if not system_path.exists():
            return analysis
        
        # 统计文件
        file_patterns = ["*.py", "*.js", "*.jsx", "*.ts", "*.html", "*.css", "*.json", "*.md", "*.sh"]
        
        for pattern in file_patterns:
            files = list(system_path.glob(f"**/{pattern}"))
            # 过滤掉node_modules和其他不需要的目录
            files = [f for f in files if "node_modules" not in str(f) and "__pycache__" not in str(f)]
            
            if files:
                file_ext = pattern[1:]  # 去掉*
                analysis["file_types"][file_ext] = len(files)
                analysis["file_count"] += len(files)
                
                # 统计代码行数
                for file_path in files:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                            analysis["total_lines"] += lines
                    except Exception:
                        continue
        
        # 识别主要模块
        analysis["main_modules"] = self.identify_main_modules(system_path)
        
        # 识别配置文件
        analysis["config_files"] = self.identify_config_files(system_path)
        
        # 识别优化文件
        analysis["optimization_files"] = self.identify_optimization_files(system_path)
        
        # 识别关键功能
        analysis["key_features"] = self.identify_key_features(system_path, system_name)
        
        return analysis
    
    def identify_main_modules(self, system_path: Path) -> List[str]:
        """识别主要模块"""
        main_patterns = [
            "main.py", "app.py", "server.py", "index.html", "index.js",
            "*_app.py", "*_main.py", "*_server.py", "unified_*.py"
        ]
        
        main_modules = []
        for pattern in main_patterns:
            files = list(system_path.glob(f"**/{pattern}"))
            files = [f for f in files if "node_modules" not in str(f)]
            main_modules.extend([f.name for f in files])
        
        return list(set(main_modules))[:10]  # 限制数量
    
    def identify_config_files(self, system_path: Path) -> List[str]:
        """识别配置文件"""
        config_patterns = [
            "config*.py", "config*.json", "config*.yaml", "*.config.js",
            "package.json", "requirements.txt", "Dockerfile"
        ]
        
        config_files = []
        for pattern in config_patterns:
            files = list(system_path.glob(f"**/{pattern}"))
            files = [f for f in files if "node_modules" not in str(f)]
            config_files.extend([f.name for f in files])
        
        return list(set(config_files))[:10]
    
    def identify_optimization_files(self, system_path: Path) -> List[str]:
        """识别优化相关文件"""
        optimization_patterns = [
            "*optimization*", "*unified*", "*optimize*", "*performance*",
            "*monitor*", "*health*", "*deploy*"
        ]
        
        optimization_files = []
        for pattern in optimization_patterns:
            files = list(system_path.glob(f"**/{pattern}"))
            files = [f for f in files if "node_modules" not in str(f)]
            optimization_files.extend([f.name for f in files])
        
        return list(set(optimization_files))[:10]
    
    def identify_key_features(self, system_path: Path, system_name: str) -> List[str]:
        """识别关键功能特性"""
        features = []
        
        if "RAG" in system_name:
            features = [
                "智能问答系统", "多模型支持", "向量数据库", "文档检索",
                "API服务", "Web界面", "配置管理", "多应用模式"
            ]
        elif "API" in system_name:
            features = [
                "API密钥管理", "多提供商支持", "使用统计", "Web管理界面",
                "安全认证", "请求代理", "错误处理", "配置管理"
            ]
        elif "Nexus" in system_name:
            features = [
                "中央控制面板", "系统监控", "可视化界面", "响应式设计",
                "多系统集成", "实时状态", "操作面板", "移动端适配"
            ]
        elif "Chronicle" in system_name:
            features = [
                "ReAct智能代理", "任务执行", "历史记录", "智能推理",
                "工具集成", "对话管理", "状态跟踪", "结果分析"
            ]
        elif "Changlee" in system_name:
            features = [
                "桌面宠物", "Electron应用", "音乐播放", "情感陪伴",
                "英语学习", "React界面", "本地存储", "系统集成"
            ]
        elif "Management" in system_name:
            features = [
                "项目管理", "脚本自动化", "部署管理", "系统监控",
                "健康检查", "日志管理", "配置管理", "运维工具"
            ]
        
        return features
    
    def analyze_file_types(self) -> Dict[str, int]:
        """分析文件类型分布"""
        print("📁 分析文件类型分布...")
        
        file_types = {}
        extensions = [".py", ".js", ".jsx", ".ts", ".html", ".css", ".json", ".md", ".sh", ".yaml"]
        
        for ext in extensions:
            try:
                result = subprocess.run(
                    f"find {self.project_root} -name '*{ext}' | grep -v node_modules | grep -v __pycache__ | grep -v .git | wc -l",
                    shell=True, capture_output=True, text=True
                )
                count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
                if count > 0:
                    file_types[ext[1:]] = count  # 去掉点号
            except Exception:
                continue
        
        return file_types
    
    def analyze_optimization_status(self) -> Dict[str, Any]:
        """分析优化状态"""
        print("🚀 分析优化状态...")
        
        optimization_status = {
            "phase_1_completed": False,
            "phase_2_completed": False,
            "unified_components": [],
            "optimization_reports": [],
            "performance_configs": [],
            "monitoring_systems": []
        }
        
        # 检查第一阶段优化
        phase1_indicators = [
            "unified_app.py", "unified_config.py", "unified_main.py", "unified_api_manager.py"
        ]
        
        found_phase1 = 0
        for indicator in phase1_indicators:
            if list(self.project_root.glob(f"**/{indicator}")):
                found_phase1 += 1
                optimization_status["unified_components"].append(indicator)
        
        optimization_status["phase_1_completed"] = found_phase1 >= 3
        
        # 检查第二阶段优化
        phase2_indicators = [
            "*optimization_report.json", "*performance_config.json", 
            "health_check.py", "*monitoring_config*"
        ]
        
        found_phase2 = 0
        for pattern in phase2_indicators:
            files = list(self.project_root.glob(f"**/{pattern}"))
            if files:
                found_phase2 += 1
                if "report" in pattern:
                    optimization_status["optimization_reports"].extend([f.name for f in files])
                elif "performance" in pattern:
                    optimization_status["performance_configs"].extend([f.name for f in files])
                elif "health" in pattern or "monitoring" in pattern:
                    optimization_status["monitoring_systems"].extend([f.name for f in files])
        
        optimization_status["phase_2_completed"] = found_phase2 >= 2
        
        return optimization_status
    
    def calculate_code_metrics(self) -> Dict[str, Any]:
        """计算代码指标"""
        print("📊 计算代码指标...")
        
        metrics = {
            "total_lines": 0,
            "code_lines": 0,
            "comment_lines": 0,
            "blank_lines": 0,
            "languages": {}
        }
        
        # 统计各种语言的代码行数
        language_extensions = {
            "Python": [".py"],
            "JavaScript": [".js", ".jsx"],
            "TypeScript": [".ts"],
            "HTML": [".html"],
            "CSS": [".css"],
            "JSON": [".json"],
            "Markdown": [".md"],
            "Shell": [".sh"]
        }
        
        for language, extensions in language_extensions.items():
            total_lines = 0
            for ext in extensions:
                try:
                    result = subprocess.run(
                        f"find {self.project_root} -name '*{ext}' | grep -v node_modules | grep -v __pycache__ | xargs wc -l | tail -1",
                        shell=True, capture_output=True, text=True
                    )
                    if result.stdout.strip() and "total" in result.stdout:
                        lines = int(result.stdout.strip().split()[0])
                        total_lines += lines
                except Exception:
                    continue
            
            if total_lines > 0:
                metrics["languages"][language] = total_lines
                metrics["total_lines"] += total_lines
        
        return metrics
    
    def generate_architecture_report(self) -> Dict[str, Any]:
        """生成完整的架构分析报告"""
        print("🏗️ 生成架构分析报告...")
        
        # 执行各项分析
        structure = self.analyze_project_structure()
        metrics = self.calculate_code_metrics()
        
        # 合并结果
        report = {
            **structure,
            "code_metrics": metrics,
            "summary": {
                "total_systems": len(structure["systems"]),
                "optimization_progress": {
                    "phase_1": structure["optimization_status"]["phase_1_completed"],
                    "phase_2": structure["optimization_status"]["phase_2_completed"]
                },
                "largest_system": max(structure["systems"].items(), 
                                    key=lambda x: x[1]["total_lines"])[0] if structure["systems"] else None,
                "most_files": max(structure["systems"].items(), 
                                key=lambda x: x[1]["file_count"])[0] if structure["systems"] else None
            }
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = "architecture_analysis_report.json"):
        """保存分析报告"""
        report_path = self.project_root / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 架构分析报告已保存到: {report_path}")
        return report_path
    
    def print_summary(self, report: Dict[str, Any]):
        """打印分析摘要"""
        print("\n" + "="*80)
        print("🏗️ N.S.S-Novena-Garfield 项目架构分析摘要")
        print("="*80)
        
        print(f"📊 项目概览:")
        print(f"  • 总文件数: {report['total_files']:,}")
        print(f"  • 总代码行数: {report['code_metrics']['total_lines']:,}")
        print(f"  • 系统模块数: {report['summary']['total_systems']}")
        
        print(f"\n🎯 各系统统计:")
        for system_key, system_data in report['systems'].items():
            print(f"  • {system_data['name']}: {system_data['file_count']} 文件, {system_data['total_lines']:,} 行")
        
        print(f"\n📁 文件类型分布:")
        for file_type, count in sorted(report['file_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"  • {file_type.upper()}: {count} 文件")
        
        print(f"\n💻 编程语言统计:")
        for language, lines in sorted(report['code_metrics']['languages'].items(), key=lambda x: x[1], reverse=True):
            print(f"  • {language}: {lines:,} 行")
        
        print(f"\n🚀 优化状态:")
        print(f"  • 第一阶段优化: {'✅ 完成' if report['optimization_status']['phase_1_completed'] else '❌ 未完成'}")
        print(f"  • 第二阶段优化: {'✅ 完成' if report['optimization_status']['phase_2_completed'] else '❌ 未完成'}")
        print(f"  • 统一组件: {len(report['optimization_status']['unified_components'])} 个")
        print(f"  • 优化报告: {len(report['optimization_status']['optimization_reports'])} 个")
        
        if report['summary']['largest_system']:
            largest = report['systems'][report['summary']['largest_system']]
            print(f"\n📈 最大系统: {largest['name']} ({largest['total_lines']:,} 行)")
        
        if report['summary']['most_files']:
            most_files = report['systems'][report['summary']['most_files']]
            print(f"📁 文件最多: {most_files['name']} ({most_files['file_count']} 文件)")

def main():
    """主函数"""
    analyzer = ProjectArchitectureAnalyzer()
    
    print("🚀 开始N.S.S-Novena-Garfield项目架构分析...")
    
    # 生成分析报告
    report = analyzer.generate_architecture_report()
    
    # 保存报告
    report_path = analyzer.save_report(report)
    
    # 打印摘要
    analyzer.print_summary(report)
    
    print(f"\n📄 完整报告已保存到: {report_path}")

if __name__ == "__main__":
    main()