#!/usr/bin/env python3
"""
🔧 N.S.S-Novena-Garfield 配置验证工具
验证所有系统配置的正确性和一致性
"""

import os
import sys
import json
import socket
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any
import argparse

class ConfigValidator:
    def __init__(self, workspace_path="."):
        self.workspace_path = Path(workspace_path)
        self.errors = []
        self.warnings = []
        self.info = []
        
        # 预期的端口配置
        self.expected_ports = {
            'AI_PORT': 8001,
            'CHRONICLE_PORT': 3000,
            'RAG_PORT': 8501,
            'NEXUS_PORT': 8080,
            'API_MANAGER_PORT': 8000,
            'CHANGLEE_WEB_PORT': 8082,
            'CHANGLEE_BACKEND_PORT': 8083,
            'BOVINE_PORT': 8084,
            'GENOME_PORT': 8085,
            'KINETIC_PORT': 8086
        }
        
        # 必需的环境变量
        self.required_env_vars = [
            'NSS_BASE_PATH',
            'AI_SERVICE_URL',
            'CHRONICLE_URL',
            'RAG_SERVICE_URL',
            'NEXUS_URL'
        ]
        
        # 可选但推荐的环境变量
        self.recommended_env_vars = [
            'OPENAI_API_KEY',
            'GEMINI_API_KEY',
            'DEEPSEEK_API_KEY'
        ]
    
    def log_issue(self, level: str, category: str, message: str):
        """记录问题"""
        issue = {'level': level, 'category': category, 'message': message}
        
        if level == 'error':
            self.errors.append(issue)
        elif level == 'warning':
            self.warnings.append(issue)
        else:
            self.info.append(issue)
    
    def check_port_availability(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0  # 端口可用返回True
        except Exception:
            return True  # 假设可用
    
    def validate_environment_variables(self):
        """验证环境变量"""
        print("🔍 检查环境变量...")
        
        # 检查必需的环境变量
        for var in self.required_env_vars:
            if not os.getenv(var):
                self.log_issue('warning', 'env', f'推荐设置环境变量: {var}')
        
        # 检查推荐的环境变量
        for var in self.recommended_env_vars:
            if not os.getenv(var):
                self.log_issue('info', 'env', f'可选环境变量未设置: {var}')
        
        # 检查端口配置
        for port_var, default_port in self.expected_ports.items():
            port = int(os.getenv(port_var, default_port))
            if port < 1024 or port > 65535:
                self.log_issue('error', 'port', f'端口范围无效 {port_var}: {port}')
            elif not self.check_port_availability(port):
                self.log_issue('warning', 'port', f'端口可能被占用 {port_var}: {port}')
    
    def validate_paths(self):
        """验证路径配置"""
        print("📁 检查路径配置...")
        
        base_path = Path(os.getenv('NSS_BASE_PATH', self.workspace_path))
        
        # 检查基础路径
        if not base_path.exists():
            self.log_issue('error', 'path', f'基础路径不存在: {base_path}')
            return
        
        # 检查关键目录
        critical_dirs = [
            'systems',
            'api',
            'management',
            'management/config',
            'management/logs',
            'management/data'
        ]
        
        for dir_name in critical_dirs:
            dir_path = base_path / dir_name
            if not dir_path.exists():
                if dir_name in ['management/logs', 'management/data']:
                    # 自动创建日志和数据目录
                    try:
                        dir_path.mkdir(parents=True, exist_ok=True)
                        self.log_issue('info', 'path', f'自动创建目录: {dir_path}')
                    except Exception as e:
                        self.log_issue('error', 'path', f'无法创建目录 {dir_path}: {e}')
                else:
                    self.log_issue('error', 'path', f'关键目录不存在: {dir_path}')
    
    def validate_system_configs(self):
        """验证系统配置文件"""
        print("⚙️ 检查系统配置文件...")
        
        systems_path = self.workspace_path / 'systems'
        if not systems_path.exists():
            self.log_issue('error', 'config', 'systems目录不存在')
            return
        
        # 检查各系统的配置
        expected_systems = [
            'rag-system',
            'Changlee',
            'chronicle',
            'bovine-insight',
            'genome-nebula',
            'kinetic-scope',
            'nexus'
        ]
        
        for system in expected_systems:
            system_path = systems_path / system
            if not system_path.exists():
                self.log_issue('warning', 'config', f'系统目录不存在: {system}')
                continue
            
            # 检查入口文件
            entry_files = [
                f'{system}.py',
                'main.py',
                f'{system}.js',
                'app.py',
                'server.js'
            ]
            
            has_entry = False
            for entry_file in entry_files:
                if (system_path / entry_file).exists():
                    has_entry = True
                    break
            
            if not has_entry:
                self.log_issue('warning', 'config', f'系统 {system} 缺少入口文件')
    
    def validate_docker_config(self):
        """验证Docker配置"""
        print("🐳 检查Docker配置...")
        
        # 检查Docker是否可用
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.log_issue('info', 'docker', f'Docker可用: {result.stdout.strip()}')
            else:
                self.log_issue('warning', 'docker', 'Docker不可用')
        except Exception as e:
            self.log_issue('warning', 'docker', f'Docker检查失败: {e}')
        
        # 检查docker-compose.yml
        compose_file = self.workspace_path / 'management/deployment/docker-compose.yml'
        if compose_file.exists():
            try:
                # 简单的YAML语法检查
                with open(compose_file, 'r') as f:
                    content = f.read()
                if 'version:' in content and 'services:' in content:
                    self.log_issue('info', 'docker', 'docker-compose.yml格式正确')
                else:
                    self.log_issue('warning', 'docker', 'docker-compose.yml格式可能有问题')
            except Exception as e:
                self.log_issue('error', 'docker', f'docker-compose.yml读取失败: {e}')
        else:
            self.log_issue('info', 'docker', 'docker-compose.yml不存在（将创建）')
    
    def validate_global_config(self):
        """验证全局配置文件"""
        print("🌐 检查全局配置...")
        
        global_config_path = self.workspace_path / 'management/config/global.config.js'
        if not global_config_path.exists():
            self.log_issue('error', 'config', '全局配置文件不存在')
            return
        
        try:
            # 检查Node.js是否可用来验证配置
            result = subprocess.run(['node', '-c', str(global_config_path)], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_issue('info', 'config', '全局配置文件语法正确')
            else:
                self.log_issue('error', 'config', f'全局配置文件语法错误: {result.stderr}')
        except Exception as e:
            self.log_issue('warning', 'config', f'无法验证全局配置文件: {e}')
    
    def check_port_conflicts(self):
        """检查端口冲突"""
        print("🔌 检查端口冲突...")
        
        used_ports = set()
        
        for port_var, default_port in self.expected_ports.items():
            port = int(os.getenv(port_var, default_port))
            
            if port in used_ports:
                self.log_issue('error', 'port', f'端口冲突: {port} (来自 {port_var})')
            else:
                used_ports.add(port)
    
    def generate_report(self):
        """生成验证报告"""
        print("\n" + "="*60)
        print("🔧 配置验证报告")
        print("="*60)
        
        # 统计信息
        total_issues = len(self.errors) + len(self.warnings)
        print(f"\n📊 问题统计:")
        print(f"  错误: {len(self.errors)}")
        print(f"  警告: {len(self.warnings)}")
        print(f"  信息: {len(self.info)}")
        
        # 显示错误
        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)}个):")
            for error in self.errors:
                print(f"  [{error['category']}] {error['message']}")
        
        # 显示警告
        if self.warnings:
            print(f"\n⚠️ 警告 ({len(self.warnings)}个):")
            for warning in self.warnings:
                print(f"  [{warning['category']}] {warning['message']}")
        
        # 显示信息
        if self.info:
            print(f"\n💡 信息 ({len(self.info)}个):")
            for info in self.info[:5]:  # 只显示前5个
                print(f"  [{info['category']}] {info['message']}")
        
        # 总体评分
        if len(self.errors) == 0:
            if len(self.warnings) == 0:
                score = 100
                grade = "🟢 优秀"
            elif len(self.warnings) <= 3:
                score = 90
                grade = "🟢 良好"
            else:
                score = 80
                grade = "🟡 一般"
        else:
            score = max(60 - len(self.errors) * 10, 30)
            grade = "🔴 需要修复"
        
        print(f"\n🎯 配置质量评分: {score}/100 - {grade}")
        
        # 建议
        if len(self.errors) > 0:
            print(f"\n📋 建议优先修复 {len(self.errors)} 个错误")
        elif len(self.warnings) > 0:
            print(f"\n📋 建议处理 {len(self.warnings)} 个警告以提升配置质量")
        else:
            print("\n✅ 配置验证通过！系统配置良好。")
        
        return score >= 80
    
    def run_validation(self):
        """运行完整验证"""
        print("🚀 开始配置验证...")
        
        self.validate_environment_variables()
        self.validate_paths()
        self.validate_system_configs()
        self.validate_docker_config()
        self.validate_global_config()
        self.check_port_conflicts()
        
        return self.generate_report()

def main():
    parser = argparse.ArgumentParser(description='N.S.S-Novena-Garfield 配置验证工具')
    parser.add_argument('--path', default='.', help='工作空间路径 (默认: 当前目录)')
    parser.add_argument('--fix', action='store_true', help='自动修复可修复的问题')
    
    args = parser.parse_args()
    
    validator = ConfigValidator(args.path)
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()