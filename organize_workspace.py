#!/usr/bin/env python3
"""
Workspace Organization Script
整理workspace文件结构，确保所有文件都在正确的位置
"""

import os
import shutil
from pathlib import Path

def organize_workspace():
    """整理workspace文件结构"""
    workspace = Path("/workspace")
    
    print("🧹 开始整理workspace文件结构...")
    
    # 确保目录存在
    directories = {
        "docs/summaries": "项目总结文档",
        "docs/archive": "归档文档",
        "docs/guides": "使用指南",
        "tools/scripts": "工具脚本",
        "tools/deployment": "部署工具",
        "data/samples": "示例数据",
        "data/exports": "导出数据",
        "logs/archive": "历史日志",
        "tests/integration": "集成测试",
        "tests/performance": "性能测试"
    }
    
    for dir_path, description in directories.items():
        full_path = workspace / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ 创建目录: {dir_path} ({description})")
    
    # 移动零散文件到合适位置
    file_moves = [
        # 将系统级脚本移动到tools目录
        ("systems/demo_integration.js", "tools/scripts/demo_integration.js"),
        ("systems/start_integrated_system.js", "tools/scripts/start_integrated_system.js"),
        ("systems/test_upgrades.py", "tools/scripts/test_upgrades.py"),
        
        # 确保重要文档在正确位置
        ("systems/UPGRADE_SUMMARY.md", "docs/summaries/UPGRADE_SUMMARY.md"),
        ("systems/CHRONICLE_CHANGLEE_INTEGRATION.md", "docs/summaries/CHRONICLE_CHANGLEE_INTEGRATION.md"),
    ]
    
    for src, dst in file_moves:
        src_path = workspace / src
        dst_path = workspace / dst
        
        if src_path.exists() and not dst_path.exists():
            # 确保目标目录存在
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(dst_path))
            print(f"   📁 移动文件: {src} → {dst}")
    
    # 创建.gitignore文件
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/*.log

# Temporary files
temp/
tmp/
*.tmp

# API Keys and Secrets
*.key
*_key.txt
.env
config/secrets.json

# Database files
*.db
*.sqlite
*.sqlite3

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
build/
dist/
out/

# Cache
.cache/
*.cache

# AI Models (large files)
models/*.bin
models/*.safetensors
*.model

# Data files
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep

# Test outputs
test_output/
coverage/
.coverage
"""
    
    gitignore_path = workspace / ".gitignore"
    if not gitignore_path.exists():
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("   ✅ 创建 .gitignore 文件")
    
    # 创建空的.gitkeep文件
    gitkeep_dirs = [
        "data/raw",
        "data/processed", 
        "data/samples",
        "data/exports",
        "logs/archive",
        "tests/integration",
        "tests/performance"
    ]
    
    for dir_path in gitkeep_dirs:
        gitkeep_path = workspace / dir_path / ".gitkeep"
        if not gitkeep_path.exists():
            gitkeep_path.touch()
            print(f"   📝 创建 .gitkeep: {dir_path}")
    
    print("✅ Workspace文件结构整理完成！")
    
    # 显示最终的目录结构
    print("\n📁 当前workspace结构:")
    show_directory_tree(workspace, max_depth=2)

def show_directory_tree(path, prefix="", max_depth=3, current_depth=0):
    """显示目录树结构"""
    if current_depth >= max_depth:
        return
    
    path = Path(path)
    if not path.is_dir():
        return
    
    items = sorted([p for p in path.iterdir() if not p.name.startswith('.')])
    dirs = [p for p in items if p.is_dir()]
    files = [p for p in items if p.is_file()]
    
    # 显示目录
    for i, dir_path in enumerate(dirs):
        is_last_dir = (i == len(dirs) - 1) and len(files) == 0
        current_prefix = "└── " if is_last_dir else "├── "
        print(f"{prefix}{current_prefix}📂 {dir_path.name}/")
        
        next_prefix = prefix + ("    " if is_last_dir else "│   ")
        show_directory_tree(dir_path, next_prefix, max_depth, current_depth + 1)
    
    # 显示重要文件
    important_files = [f for f in files if f.suffix in ['.md', '.py', '.js', '.json', '.txt'] and not f.name.startswith('.')]
    for i, file_path in enumerate(important_files[:5]):  # 只显示前5个重要文件
        is_last = i == len(important_files) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}📄 {file_path.name}")
    
    if len(important_files) > 5:
        print(f"{prefix}    ... 还有 {len(important_files) - 5} 个文件")

def create_project_summary():
    """创建项目总结文件"""
    workspace = Path("/workspace")
    summary_path = workspace / "docs" / "PROJECT_SUMMARY.md"
    
    summary_content = """# 📋 Research Workstation 项目总结

## 🎯 项目概述
Research Workstation 是一个集成多个AI驱动系统的综合科研工作站，包含RAG智能问答、牛只识别分析、桌面宠物学习助手、实验记录系统等多个子系统。

## 🏗️ 系统架构
- **🤖 RAG智能问答系统**: DeepSeek + multilingual-e5 + FAISS
- **🐄 BovineInsight牛只识别**: DINOv2 + GLM-4V + 传统CV算法  
- **🐱 Changlee桌面宠物**: Gemma 2 + Electron + React
- **📊 Chronicle实验记录器**: 无头微服务 + AI分析引擎
- **🔧 API管理系统**: 统一配置管理 + 安全存储

## 🚀 最新升级
### v2.0.0 - 博士级AI升级
- **DINOv2无监督特征提取**: 解决数据标注难题
- **GLM-4V专家级文本分析**: 论文级分析报告
- **Gemma 2本地AI核心**: 隐私保护的智能对话
- **多模态融合分析**: 传统+深度学习+大语言模型

## 📊 技术指标
- **代码规模**: 50,000+ 行
- **AI模型**: 4个集成模型
- **系统数量**: 5个核心系统
- **文档数量**: 200+ 页

## 🎯 应用场景
- **科研**: 文献调研、实验记录、数据分析
- **教育**: 智能问答、学习辅导
- **产业**: 畜牧业管理、智能客服

## 📞 联系方式
- GitHub: https://github.com/novenazgarfield/research-workstation
- Issues: https://github.com/novenazgarfield/research-workstation/issues

---
*更新时间: 2025年8月20日*
"""
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"   ✅ 创建项目总结: {summary_path}")

if __name__ == "__main__":
    organize_workspace()
    create_project_summary()
    print("\n🎉 Workspace整理完成！项目已准备好上传到GitHub。")