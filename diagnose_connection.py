#!/usr/bin/env python3
"""
RAG系统连接诊断工具
"""

import requests
import json
import time

def test_health_endpoint():
    """测试健康检查端点"""
    print("🔍 测试健康检查端点...")
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_chat_endpoint():
    """测试聊天端点"""
    print("\n🔍 测试聊天端点...")
    try:
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:52943'
        }
        data = {
            'message': '测试连接',
            'task_name': 'nexus_chat'
        }
        
        response = requests.post(
            'http://localhost:5000/api/chat', 
            headers=headers,
            json=data,
            timeout=10
        )
        
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应头: {dict(response.headers)}")
        print(f"✅ 响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 聊天API失败: {e}")
        return False

def test_cors_preflight():
    """测试CORS预检请求"""
    print("\n🔍 测试CORS预检请求...")
    try:
        headers = {
            'Origin': 'http://localhost:52943',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options(
            'http://localhost:5000/api/chat',
            headers=headers,
            timeout=5
        )
        
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ CORS头: {dict(response.headers)}")
        return True
    except Exception as e:
        print(f"❌ CORS预检失败: {e}")
        return False

def test_history_endpoint():
    """测试历史记录端点"""
    print("\n🔍 测试历史记录端点...")
    try:
        response = requests.get(
            'http://localhost:5000/api/history?task_name=nexus_chat',
            timeout=5
        )
        print(f"✅ 状态码: {response.status_code}")
        data = response.json()
        print(f"✅ 历史记录数量: {data.get('total_messages', 0)}")
        return True
    except Exception as e:
        print(f"❌ 历史记录API失败: {e}")
        return False

def main():
    print("🚀 RAG系统连接诊断开始...\n")
    
    tests = [
        test_health_endpoint,
        test_cors_preflight,
        test_chat_endpoint,
        test_history_endpoint
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        time.sleep(1)
    
    print(f"\n📊 诊断结果:")
    print(f"✅ 通过: {sum(results)}/{len(results)}")
    print(f"❌ 失败: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 所有测试通过！RAG系统连接正常。")
        print("💡 如果前端仍然报错，可能是浏览器缓存或JavaScript问题。")
    else:
        print("\n⚠️ 部分测试失败，请检查RAG服务器状态。")

if __name__ == "__main__":
    main()