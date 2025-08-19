#!/usr/bin/env python3
"""
设置Gemini集成 - 从API管理系统复制配置
"""

import os
import sys
import json
import shutil
from pathlib import Path

def setup_gemini_integration():
    """设置Gemini集成"""
    print("🔧 设置Gemini集成...")
    
    # 路径配置
    rag_dir = Path(__file__).parent
    api_management_dir = rag_dir.parent / 'api_management'
    
    # 检查API管理系统是否存在
    if not api_management_dir.exists():
        print("❌ 未找到API管理系统")
        return False
    
    # 复制必要的文件
    files_to_copy = [
        ('config/private_api_manager.py', 'config/private_api_manager.py'),
        ('config/api_encryption.key', 'config/api_encryption.key'),
        ('config/private_apis.json', 'config/private_apis.json'),
    ]
    
    # 确保目标目录存在
    (rag_dir / 'config').mkdir(exist_ok=True)
    
    copied_files = []
    for src_file, dst_file in files_to_copy:
        src_path = api_management_dir / src_file
        dst_path = rag_dir / dst_file
        
        if src_path.exists():
            try:
                shutil.copy2(src_path, dst_path)
                copied_files.append(dst_file)
                print(f"✅ 已复制: {dst_file}")
            except Exception as e:
                print(f"❌ 复制失败 {dst_file}: {e}")
        else:
            print(f"⚠️ 源文件不存在: {src_file}")
    
    # 检查是否有Gemini API密钥
    private_apis_file = rag_dir / 'config/private_apis.json'
    if private_apis_file.exists():
        try:
            with open(private_apis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            gemini_keys = []
            if 'api_keys' in data:
                for key_id, key_info in data['api_keys'].items():
                    if key_info.get('provider') == 'google':
                        gemini_keys.append({
                            'key_id': key_id,
                            'key_name': key_info.get('key_name', ''),
                            'status': key_info.get('status', ''),
                            'user_id': key_info.get('user_id', '')
                        })
            
            if gemini_keys:
                print(f"\n🔑 发现 {len(gemini_keys)} 个Gemini API密钥:")
                for key in gemini_keys:
                    print(f"   - {key['key_name']} (用户: {key['user_id']}, 状态: {key['status']})")
            else:
                print("\n⚠️ 未发现Gemini API密钥")
                print("💡 请在RAG系统的设置中添加您的Gemini API密钥")
        
        except Exception as e:
            print(f"❌ 读取API密钥配置失败: {e}")
    
    # 创建用户配置文件
    users_file = rag_dir / 'config/users.json'
    if not users_file.exists():
        default_users = {
            "admin": {
                "user_id": "admin",
                "username": "admin",
                "role": "admin",
                "created_at": "2024-01-01T00:00:00Z",
                "is_active": True
            },
            "default_user": {
                "user_id": "default_user", 
                "username": "default_user",
                "role": "user",
                "created_at": "2024-01-01T00:00:00Z",
                "is_active": True
            }
        }
        
        try:
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(default_users, f, indent=2, ensure_ascii=False)
            print(f"✅ 已创建用户配置文件: {users_file}")
        except Exception as e:
            print(f"❌ 创建用户配置失败: {e}")
    
    print(f"\n🎉 Gemini集成设置完成!")
    print(f"📁 配置文件位置: {rag_dir / 'config'}")
    print(f"🚀 运行以下命令启动系统:")
    print(f"   cd {rag_dir}")
    print(f"   python start_rag_with_gemini.py")
    
    return True

if __name__ == "__main__":
    setup_gemini_integration()