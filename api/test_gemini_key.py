#!/usr/bin/env python3
"""
测试Gemini API密钥
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from private_api_manager import get_user_api_key

def test_gemini_key():
    """测试Gemini API密钥"""
    print("🔍 测试Gemini API密钥...")
    
    # 获取密钥
    result = get_user_api_key("admin", "google")
    
    if result:
        key_id, api_key = result
        print(f"✅ 成功获取Gemini API密钥")
        print(f"📋 密钥ID: {key_id}")
        print(f"🔑 密钥预览: {api_key[:10]}...{api_key[-4:]}")
        
        # 测试调用Gemini API
        try:
            import google.generativeai as genai
            
            # 配置API密钥
            genai.configure(api_key=api_key)
            
            # 创建模型
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # 测试简单对话
            print("\n🤖 测试Gemini API调用...")
            response = model.generate_content("你好，请简单介绍一下你自己")
            
            print(f"✅ API调用成功！")
            print(f"🗣️ Gemini回复: {response.text}")
            
            return True
            
        except Exception as e:
            print(f"❌ API调用失败: {str(e)}")
            return False
    else:
        print("❌ 未找到Gemini API密钥")
        return False

if __name__ == "__main__":
    test_gemini_key()