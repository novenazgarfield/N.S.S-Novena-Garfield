#!/usr/bin/env python3
"""
测试前端API连接
模拟前端JavaScript的API调用流程
"""

import requests
import json
import time

def test_frontend_api_flow():
    """测试前端API连接流程"""
    print("🧪 模拟前端API连接流程")
    print("=" * 50)
    
    # 1. 加载配置文件（模拟loadApiConfig）
    print("1️⃣ 加载配置文件...")
    try:
        config_response = requests.get("http://localhost:52301/api_config.json", timeout=5)
        if config_response.status_code == 200:
            config = config_response.json()
            rag_api = config['api_endpoints']['rag_api']
            print(f"   ✅ 配置加载成功: {rag_api}")
        else:
            print(f"   ❌ 配置加载失败: {config_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 配置加载异常: {e}")
        return False
    
    # 2. 测试健康检查（模拟tryConnectToURL）
    print("\n2️⃣ 测试健康检查...")
    try:
        health_url = f"{rag_api}/api/health"
        print(f"   🔗 请求URL: {health_url}")
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        health_response = requests.get(health_url, headers=headers, timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ 健康检查成功:")
            print(f"      版本: {health_data.get('version', 'N/A')}")
            print(f"      聊天历史: {health_data.get('data', {}).get('chat_history_count', 'N/A')}")
            print(f"      文档数量: {health_data.get('data', {}).get('documents_count', 'N/A')}")
            print(f"      系统状态: {health_data.get('data', {}).get('system_status', 'N/A')}")
        else:
            print(f"   ❌ 健康检查失败: {health_response.status_code}")
            print(f"      响应: {health_response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ 健康检查异常: {e}")
        return False
    
    # 3. 测试系统状态（模拟showSystemStatus）
    print("\n3️⃣ 测试系统状态...")
    try:
        status_url = f"{rag_api}/api/system/status"
        print(f"   🔗 请求URL: {status_url}")
        
        status_response = requests.get(status_url, headers=headers, timeout=10)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"   ✅ 系统状态成功:")
            print(f"      状态: {status_data.get('status', 'N/A')}")
            print(f"      聊天历史: {status_data.get('data', {}).get('chat_history_count', 'N/A')}")
            print(f"      文档数量: {status_data.get('data', {}).get('documents_count', 'N/A')}")
            print(f"      系统健康: {status_data.get('data', {}).get('system_health', 'N/A')}")
        else:
            print(f"   ❌ 系统状态失败: {status_response.status_code}")
            print(f"      响应: {status_response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 系统状态异常: {e}")
    
    # 4. 测试文档列表
    print("\n4️⃣ 测试文档列表...")
    try:
        docs_url = f"{rag_api}/api/documents"
        print(f"   🔗 请求URL: {docs_url}")
        
        docs_response = requests.get(docs_url, headers=headers, timeout=10)
        if docs_response.status_code == 200:
            docs_data = docs_response.json()
            print(f"   ✅ 文档列表成功:")
            print(f"      文档数量: {len(docs_data.get('documents', []))}")
            if docs_data.get('documents'):
                for i, doc in enumerate(docs_data['documents'][:3]):
                    print(f"      文档{i+1}: {doc.get('filename', 'N/A')}")
        else:
            print(f"   ❌ 文档列表失败: {docs_response.status_code}")
            print(f"      响应: {docs_response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 文档列表异常: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 测试总结:")
    print("   前端应该能够正常连接到RAG API")
    print("   如果前端显示'undefined'，可能是JavaScript异步加载问题")
    
    return True

if __name__ == "__main__":
    test_frontend_api_flow()