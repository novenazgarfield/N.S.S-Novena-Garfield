#!/usr/bin/env python3
"""
🔧 绝对路径修复工具
自动修复项目中的硬编码绝对路径
"""

import os
import re
import json
from pathlib import Path

def find_project_root():
    """动态发现项目根目录"""
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / "DEVELOPMENT_GUIDE.md").exists():
            return parent
    return current_path.parent.parent.parent

def fix_json_files():
    """修复JSON文件中的绝对路径"""
    project_root = find_project_root()
    json_files = []
    
    # 查找所有JSON文件
    for root, dirs, files in os.walk(project_root):
        # 跳过.git目录
        if '.git' in root:
            continue
        for file in files:
            if file.endswith('.json'):
                json_files.append(Path(root) / file)
    
    print(f"🔍 发现 {len(json_files)} 个JSON文件")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含绝对路径
            if '/workspace' in content:
                print(f"📝 修复: {json_file.relative_to(project_root)}")
                
                # 替换常见的绝对路径模式
                patterns = [
                    (r'"/workspace/systems', '"./systems'),
                    (r'"/workspace/api', '"./api'),
                    (r'"/workspace/management', '"./management'),
                    (r'"/workspace/', '"./'),
                    (r'"/workspace"', '"."'),
                    (r"'/workspace/systems", "'./systems"),
                    (r"'/workspace/api", "'./api"),
                    (r"'/workspace/management", "'./management"),
                    (r"'/workspace/", "'./"),
                    (r"'/workspace'", "'.'"),
                ]
                
                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content)
                
                # 验证JSON格式
                try:
                    json.loads(content)
                    with open(json_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  ✅ 修复完成")
                except json.JSONDecodeError as e:
                    print(f"  ❌ JSON格式错误，跳过: {e}")
                    
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")

def fix_markdown_files():
    """修复Markdown文件中的路径引用（仅修复代码块和路径引用）"""
    project_root = find_project_root()
    md_files = []
    
    # 查找所有Markdown文件
    for root, dirs, files in os.walk(project_root):
        if '.git' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                md_files.append(Path(root) / file)
    
    print(f"🔍 发现 {len(md_files)} 个Markdown文件")
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '/workspace' in content:
                print(f"📝 修复: {md_file.relative_to(project_root)}")
                
                # 只替换代码块中的路径和明确的路径引用
                patterns = [
                    # 代码块中的路径
                    (r'`/workspace/systems`', '`./systems`'),
                    (r'`/workspace/api`', '`./api`'),
                    (r'`/workspace/management`', '`./management`'),
                    (r'`/workspace`', '`.`'),
                    
                    # 配置文件路径
                    (r'"/workspace/systems"', '"./systems"'),
                    (r'"/workspace/api"', '"./api"'),
                    (r'"/workspace/management"', '"./management"'),
                    (r'"/workspace"', '"."'),
                    
                    # 脚本路径
                    (r"'/workspace/systems'", "'./systems'"),
                    (r"'/workspace/api'", "'./api'"),
                    (r"'/workspace/management'", "'./management'"),
                    (r"'/workspace'", "'.'"),
                ]
                
                original_content = content
                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  ✅ 修复完成")
                else:
                    print(f"  ℹ️  无需修复")
                    
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")

def main():
    print("🚀 开始修复绝对路径...")
    print("=" * 50)
    
    print("\n📄 修复JSON文件...")
    fix_json_files()
    
    print("\n📝 修复Markdown文件...")
    fix_markdown_files()
    
    print("\n✅ 绝对路径修复完成！")
    print("=" * 50)
    
    # 验证修复结果
    project_root = find_project_root()
    remaining_files = []
    
    for root, dirs, files in os.walk(project_root):
        if '.git' in root:
            continue
        for file in files:
            if file.endswith(('.py', '.js', '.json', '.md')):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if '/workspace' in content:
                        remaining_files.append(file_path.relative_to(project_root))
                except:
                    pass
    
    if remaining_files:
        print(f"\n⚠️  仍有 {len(remaining_files)} 个文件包含绝对路径:")
        for file in remaining_files[:10]:  # 只显示前10个
            print(f"   - {file}")
        if len(remaining_files) > 10:
            print(f"   ... 还有 {len(remaining_files) - 10} 个文件")
    else:
        print("\n🎉 所有绝对路径已修复完成！")

if __name__ == "__main__":
    main()