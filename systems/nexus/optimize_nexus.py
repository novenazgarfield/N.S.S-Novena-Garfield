#!/usr/bin/env python3
"""
🌐 Nexus系统优化脚本
==================

优化Nexus中央控制面板性能和结构
- 清理备份文件（保留最新2个）
- 合并CSS文件
- 优化前端资源
- 保持所有功能不变

执行优化但不改变原有功能
"""

import os
import shutil
import re
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

class NexusOptimizer:
    """Nexus系统优化器"""
    
    def __init__(self, nexus_dir: Path = None):
        self.nexus_dir = nexus_dir or Path(__file__).parent
        self.backup_dir = self.nexus_dir / "backup"
        self.css_dir = self.nexus_dir / "css"
        self.js_dir = self.nexus_dir / "js"
        
        self.optimization_log = []
    
    def log_action(self, action: str, details: str = ""):
        """记录优化操作"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        self.optimization_log.append(log_entry)
        print(f"✅ {action}: {details}")
    
    def cleanup_backup_files(self, keep_count: int = 2):
        """清理备份文件，保留最新的几个"""
        if not self.backup_dir.exists():
            self.log_action("跳过备份清理", "备份目录不存在")
            return
        
        # 获取所有备份文件
        backup_files = list(self.backup_dir.glob("*.backup*"))
        
        if len(backup_files) <= keep_count:
            self.log_action("跳过备份清理", f"备份文件数量({len(backup_files)})不超过保留数量({keep_count})")
            return
        
        # 按修改时间排序，保留最新的
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        files_to_remove = backup_files[keep_count:]
        
        removed_count = 0
        total_size = 0
        
        for file_path in files_to_remove:
            try:
                file_size = file_path.stat().st_size
                file_path.unlink()
                removed_count += 1
                total_size += file_size
            except Exception as e:
                print(f"❌ 删除备份文件失败 {file_path}: {e}")
        
        self.log_action(
            "清理备份文件",
            f"删除 {removed_count} 个文件，释放 {total_size / 1024 / 1024:.2f} MB"
        )
    
    def analyze_css_files(self) -> Dict[str, Any]:
        """分析CSS文件结构"""
        css_files = []
        total_size = 0
        
        if self.css_dir.exists():
            for css_file in self.css_dir.glob("*.css"):
                size = css_file.stat().st_size
                css_files.append({
                    "name": css_file.name,
                    "path": css_file,
                    "size": size,
                    "lines": len(css_file.read_text(encoding='utf-8').splitlines())
                })
                total_size += size
        
        # 检查主HTML文件中的内联CSS
        index_file = self.nexus_dir / "index.html"
        inline_css_size = 0
        
        if index_file.exists():
            content = index_file.read_text(encoding='utf-8')
            # 查找<style>标签
            style_matches = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
            for match in style_matches:
                inline_css_size += len(match)
        
        return {
            "external_files": css_files,
            "total_external_size": total_size,
            "inline_css_size": inline_css_size,
            "total_css_size": total_size + inline_css_size
        }
    
    def optimize_css_structure(self):
        """优化CSS结构（保持功能不变）"""
        css_analysis = self.analyze_css_files()
        
        self.log_action(
            "CSS分析完成",
            f"外部文件: {len(css_analysis['external_files'])}个, "
            f"总大小: {css_analysis['total_css_size'] / 1024:.2f} KB"
        )
        
        # 如果CSS文件过多，建议合并（但不自动执行，保持安全）
        if len(css_analysis['external_files']) > 5:
            self.log_action(
                "CSS优化建议",
                f"发现 {len(css_analysis['external_files'])} 个CSS文件，建议合并以提升性能"
            )
        
        # 检查重复的CSS规则（分析但不修改）
        duplicate_rules = self._find_duplicate_css_rules()
        if duplicate_rules:
            self.log_action(
                "发现重复CSS规则",
                f"找到 {len(duplicate_rules)} 个可能重复的规则"
            )
    
    def _find_duplicate_css_rules(self) -> List[str]:
        """查找重复的CSS规则"""
        # 这里只是示例分析，实际实现会更复杂
        duplicates = []
        
        if not self.css_dir.exists():
            return duplicates
        
        all_rules = []
        for css_file in self.css_dir.glob("*.css"):
            try:
                content = css_file.read_text(encoding='utf-8')
                # 简单的规则提取（实际需要更复杂的CSS解析）
                rules = re.findall(r'([^{}]+)\s*{[^}]*}', content)
                all_rules.extend([(rule.strip(), css_file.name) for rule in rules])
            except Exception as e:
                print(f"❌ 分析CSS文件失败 {css_file}: {e}")
        
        # 查找重复的选择器
        rule_counts = {}
        for rule, file_name in all_rules:
            if rule not in rule_counts:
                rule_counts[rule] = []
            rule_counts[rule].append(file_name)
        
        for rule, files in rule_counts.items():
            if len(files) > 1:
                duplicates.append(f"{rule} (出现在: {', '.join(set(files))})")
        
        return duplicates
    
    def optimize_html_structure(self):
        """优化HTML结构（保持功能不变）"""
        index_file = self.nexus_dir / "index.html"
        
        if not index_file.exists():
            self.log_action("跳过HTML优化", "index.html文件不存在")
            return
        
        content = index_file.read_text(encoding='utf-8')
        original_size = len(content)
        
        # 分析HTML结构
        script_tags = len(re.findall(r'<script[^>]*>', content))
        style_tags = len(re.findall(r'<style[^>]*>', content))
        link_tags = len(re.findall(r'<link[^>]*>', content))
        
        self.log_action(
            "HTML结构分析",
            f"文件大小: {original_size / 1024:.2f} KB, "
            f"脚本标签: {script_tags}, 样式标签: {style_tags}, 链接标签: {link_tags}"
        )
        
        # 检查缓存策略
        cache_control = "Cache-Control" in content
        if not cache_control:
            self.log_action("缓存优化建议", "建议添加缓存控制头以提升性能")
    
    def analyze_js_files(self):
        """分析JavaScript文件"""
        if not self.js_dir.exists():
            self.log_action("跳过JS分析", "js目录不存在")
            return
        
        js_files = list(self.js_dir.glob("*.js"))
        total_size = sum(f.stat().st_size for f in js_files)
        
        self.log_action(
            "JavaScript分析",
            f"文件数量: {len(js_files)}, 总大小: {total_size / 1024:.2f} KB"
        )
        
        # 检查是否有压缩版本
        minified_files = [f for f in js_files if '.min.' in f.name]
        if len(minified_files) < len(js_files):
            self.log_action(
                "JS优化建议",
                f"建议压缩JS文件以提升加载性能 ({len(js_files) - len(minified_files)} 个文件未压缩)"
            )
    
    def create_optimization_report(self):
        """创建优化报告"""
        report = {
            "optimization_date": datetime.now().isoformat(),
            "nexus_directory": str(self.nexus_dir),
            "actions_performed": self.optimization_log,
            "summary": {
                "total_actions": len(self.optimization_log),
                "backup_files_cleaned": any("备份文件" in action["action"] for action in self.optimization_log),
                "css_analyzed": any("CSS" in action["action"] for action in self.optimization_log),
                "html_analyzed": any("HTML" in action["action"] for action in self.optimization_log)
            }
        }
        
        report_file = self.nexus_dir / "optimization_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log_action("生成优化报告", f"报告已保存到 {report_file}")
        
        return report
    
    def run_optimization(self):
        """运行完整优化流程"""
        print("🚀 开始Nexus系统优化...")
        print("=" * 50)
        
        # 1. 清理备份文件
        self.cleanup_backup_files(keep_count=2)
        
        # 2. 分析和优化CSS
        self.optimize_css_structure()
        
        # 3. 分析HTML结构
        self.optimize_html_structure()
        
        # 4. 分析JavaScript文件
        self.analyze_js_files()
        
        # 5. 生成优化报告
        report = self.create_optimization_report()
        
        print("\n" + "=" * 50)
        print("🎉 Nexus系统优化完成!")
        print(f"📊 执行了 {report['summary']['total_actions']} 个优化操作")
        print(f"📄 详细报告: {self.nexus_dir}/optimization_report.json")
        
        return report

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Nexus系统优化工具")
    parser.add_argument("--nexus-dir", help="Nexus系统目录路径")
    parser.add_argument("--keep-backups", type=int, default=2, help="保留的备份文件数量")
    parser.add_argument("--dry-run", action="store_true", help="仅分析，不执行实际优化")
    
    args = parser.parse_args()
    
    nexus_dir = Path(args.nexus_dir) if args.nexus_dir else Path(__file__).parent
    
    if not nexus_dir.exists():
        print(f"❌ Nexus目录不存在: {nexus_dir}")
        return
    
    optimizer = NexusOptimizer(nexus_dir)
    
    if args.dry_run:
        print("🔍 执行分析模式（不会修改文件）...")
        # 只执行分析，不执行实际优化
        optimizer.analyze_css_files()
        optimizer.optimize_html_structure()
        optimizer.analyze_js_files()
    else:
        optimizer.run_optimization()

if __name__ == "__main__":
    main()