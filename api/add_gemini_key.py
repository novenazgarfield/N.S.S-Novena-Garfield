#!/usr/bin/env python3
"""
添加Gemini API密钥到系统中
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from private_api_manager import PrivateAPIManager, APIProvider

def add_gemini_key():
    """添加Gemini API密钥"""
    print("🔐 添加Gemini API密钥到系统...")
    
    # 创建私有API管理器
    manager = PrivateAPIManager()
    
    # 添加您的Gemini API密钥
    key_id = manager.add_api_key(
        user_id="admin",  # 管理员用户
        provider=APIProvider.GOOGLE,
        key_name="Gemini 2.5 Flash API",
        api_key="AIzaSyBOlNcGkx43zNOvnDesd_PEhD4Lj9T8Tpo",
        daily_limit=1000,  # 每日1000次调用
        monthly_limit=30000,  # 每月30000次调用
        description="Google AI Studio Gemini 2.5 Flash 个人API密钥"
    )
    
    if key_id:
        print(f"✅ Gemini API密钥添加成功！")
        print(f"📋 密钥ID: {key_id}")
        print(f"👤 用户: admin")
        print(f"🏷️ 名称: Gemini 2.5 Flash API")
        print(f"📊 限制: 1000/日, 30000/月")
        
        # 验证密钥是否可以获取
        from private_api_manager import get_user_api_key
        result = get_user_api_key("admin", "google")
        if result:
            key_id, api_key = result
            print(f"🔍 验证成功: 密钥已正确存储和加密")
            print(f"🔑 密钥预览: {api_key[:10]}...{api_key[-4:]}")
        else:
            print("❌ 验证失败: 无法获取刚添加的密钥")
    else:
        print("❌ 添加失败！可能是密钥名称重复。")

if __name__ == "__main__":
    add_gemini_key()