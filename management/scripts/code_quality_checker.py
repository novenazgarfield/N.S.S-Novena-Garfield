#!/usr/bin/env python3
"""
🔍 N.S.S-Novena-Garfield 代码质量检查器
自动检查代码质量、重复代码、语法错误等问题
"""

import os
import sys
import ast
import json
import hashlib
import subprocess
from pathlib import Path
from collections import defaultdict
import argparse

class CodeQualityChecker:
    def __init__(self, workspace_path="."):
        self.workspace_path = Path(workspace_path)
        self.issues = []
        self.stats = {
            'python_files': 0,
            'js_files': 0,
            'json_files': 0,
            'syntax_errors': 0,
            'json_errors': 0,
            'duplicates': 0,
            'todos': 0
        }
    
    def log_issue(self, level, category, file_path, message):
        """记录问题"""
        self.issues.append({
            'level': level,  # 'error', 'warning', 'info'
            'category': category,
            'file': str(file_path),
            'message': message
        })
    
    def check_python_syntax(self):
        """检查Python语法"""
        print("🐍 检查Python语法...")
        
        python_files = list(self.workspace_path.rglob("*.py"))
        # 排除node_modules
        python_files = [f for f in python_files if 'node_modules' not in str(f)]
        
        self.stats['python_files'] = len(python_files)
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                self.log_issue('error', 'syntax', py_file, f'Python语法错误: {e}')
                self.stats['syntax_errors'] += 1
            except Exception as e:
                self.log_issue('warning', 'syntax', py_file, f'Python文件读取错误: {e}')
    
    def check_javascript_syntax(self):
        """检查JavaScript语法（需要node）"""
        print("📜 检查JavaScript语法...")
        
        js_files = list(self.workspace_path.rglob("*.js"))
        # 排除node_modules
        js_files = [f for f in js_files if 'node_modules' not in str(f)]
        
        self.stats['js_files'] = len(js_files)
        
        # 检查是否有node命令
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
            node_available = True
        except:
            node_available = False
            self.log_issue('warning', 'tool', '', 'Node.js不可用，跳过JavaScript语法检查')
        
        if node_available:
            for js_file in js_files[:10]:  # 只检查前10个文件，避免太慢
                try:
                    result = subprocess.run(['node', '-c', str(js_file)], 
                                          capture_output=True, text=True)
                    if result.returncode != 0:
                        self.log_issue('error', 'syntax', js_file, 
                                     f'JavaScript语法错误: {result.stderr}')
                        self.stats['syntax_errors'] += 1
                except Exception as e:
                    self.log_issue('warning', 'syntax', js_file, f'JavaScript检查错误: {e}')
    
    def check_json_format(self):
        """检查JSON格式"""
        print("📋 检查JSON格式...")
        
        json_files = list(self.workspace_path.rglob("*.json"))
        # 排除node_modules
        json_files = [f for f in json_files if 'node_modules' not in str(f)]
        
        self.stats['json_files'] = len(json_files)
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                self.log_issue('error', 'json', json_file, f'JSON格式错误: {e}')
                self.stats['json_errors'] += 1
            except Exception as e:
                self.log_issue('warning', 'json', json_file, f'JSON文件读取错误: {e}')
    
    def check_duplicates(self):
        """检查重复文件"""
        print("🔄 检查重复文件...")
        
        file_hashes = defaultdict(list)
        
        # 检查核心Python和JS文件
        for pattern in ["*.py", "*.js"]:
            files = list(self.workspace_path.rglob(pattern))
            # 排除node_modules和大文件
            files = [f for f in files if 'node_modules' not in str(f) and f.stat().st_size < 1024*1024]
            
            for file_path in files:
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    file_hash = hashlib.md5(content).hexdigest()
                    file_hashes[file_hash].append(file_path)
                except Exception as e:
                    self.log_issue('warning', 'duplicate', file_path, f'文件读取错误: {e}')
        
        # 报告重复文件
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                self.log_issue('warning', 'duplicate', '', 
                             f'发现重复文件: {[str(f) for f in files]}')
                self.stats['duplicates'] += 1
    
    def check_todos(self):
        """检查TODO和FIXME"""
        print("📝 检查TODO和FIXME...")
        
        patterns = ['TODO', 'FIXME', 'XXX', 'HACK']
        
        for pattern in ["*.py", "*.js"]:
            files = list(self.workspace_path.rglob(pattern))
            # 排除node_modules
            files = [f for f in files if 'node_modules' not in str(f)]
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    for line_num, line in enumerate(lines, 1):
                        for todo_pattern in patterns:
                            if todo_pattern in line:
                                self.log_issue('info', 'todo', file_path, 
                                             f'第{line_num}行: {line.strip()}')
                                self.stats['todos'] += 1
                except Exception:
                    pass  # 忽略读取错误
    
    def check_hardcoded_values(self):
        """检查硬编码值"""
        print("🔧 检查硬编码配置...")
        
        hardcoded_patterns = ['localhost', '127.0.0.1', 'http://', 'https://']
        
        for pattern in ["*.py", "*.js"]:
            files = list(self.workspace_path.rglob(pattern))
            # 排除node_modules和测试文件
            files = [f for f in files if 'node_modules' not in str(f) and 'test' not in str(f).lower()]
            
            for file_path in files[:20]:  # 限制检查数量
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for hc_pattern in hardcoded_patterns:
                        if hc_pattern in content:
                            self.log_issue('info', 'hardcode', file_path, 
                                         f'发现硬编码: {hc_pattern}')
                except Exception:
                    pass
    
    def generate_report(self):
        """生成报告"""
        print("\n" + "="*60)
        print("🔍 代码质量检查报告")
        print("="*60)
        
        # 统计信息
        print(f"\n📊 文件统计:")
        print(f"  Python文件: {self.stats['python_files']}")
        print(f"  JavaScript文件: {self.stats['js_files']}")
        print(f"  JSON文件: {self.stats['json_files']}")
        
        # 问题统计
        print(f"\n⚠️ 问题统计:")
        print(f"  语法错误: {self.stats['syntax_errors']}")
        print(f"  JSON错误: {self.stats['json_errors']}")
        print(f"  重复文件: {self.stats['duplicates']}")
        print(f"  TODO项: {self.stats['todos']}")
        
        # 按级别分类问题
        errors = [i for i in self.issues if i['level'] == 'error']
        warnings = [i for i in self.issues if i['level'] == 'warning']
        infos = [i for i in self.issues if i['level'] == 'info']
        
        if errors:
            print(f"\n❌ 错误 ({len(errors)}个):")
            for issue in errors[:10]:  # 只显示前10个
                print(f"  {issue['file']}: {issue['message']}")
        
        if warnings:
            print(f"\n⚠️ 警告 ({len(warnings)}个):")
            for issue in warnings[:10]:  # 只显示前10个
                print(f"  {issue['file']}: {issue['message']}")
        
        if infos:
            print(f"\n💡 信息 ({len(infos)}个):")
            for issue in infos[:5]:  # 只显示前5个
                print(f"  {issue['file']}: {issue['message']}")
        
        # 总体评分
        total_issues = len(errors) + len(warnings)
        if total_issues == 0:
            score = 100
            grade = "🟢 优秀"
        elif total_issues <= 5:
            score = 90
            grade = "🟢 良好"
        elif total_issues <= 15:
            score = 75
            grade = "🟡 一般"
        else:
            score = 60
            grade = "🔴 需要改进"
        
        print(f"\n🎯 总体评分: {score}/100 - {grade}")
        
        if total_issues == 0:
            print("✅ 恭喜！没有发现严重问题。")
        else:
            print(f"📋 建议优先修复 {len(errors)} 个错误和 {len(warnings)} 个警告。")
    
    def run_all_checks(self):
        """运行所有检查"""
        print("🚀 开始代码质量检查...")
        
        self.check_python_syntax()
        self.check_javascript_syntax()
        self.check_json_format()
        self.check_duplicates()
        self.check_todos()
        self.check_hardcoded_values()
        
        self.generate_report()

def main():
    parser = argparse.ArgumentParser(description='N.S.S-Novena-Garfield 代码质量检查器')
    parser.add_argument('--path', default='.', help='检查路径 (默认: 当前目录)')
    parser.add_argument('--quick', action='store_true', help='快速检查模式')
    
    args = parser.parse_args()
    
    checker = CodeQualityChecker(args.path)
    
    if args.quick:
        print("⚡ 快速检查模式")
        checker.check_python_syntax()
        checker.check_json_format()
        checker.generate_report()
    else:
        checker.run_all_checks()

if __name__ == "__main__":
    main()