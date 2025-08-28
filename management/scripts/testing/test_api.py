#!/usr/bin/env python3
"""
API功能测试脚本
"""

import requests
import json
import io
from datetime import datetime

def test_api_endpoints():
    """测试API端点"""
    
    # 从状态文件获取API URL
    try:
        with open('/tmp/nexus_status.json', 'r') as f:
            config = json.load(f)
        api_url = config['api_url']
    except:
        print("❌ 无法获取API URL")
        return
    
    if not api_url:
        print("❌ API URL为空")
        return
    
    print(f"🧪 测试API: {api_url}")
    print("=" * 50)
    
    # 1. 测试健康检查
    print("1. 测试健康检查...")
    try:
        response = requests.get(f"{api_url}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
    
    print()
    
    # 2. 测试文档上传
    print("2. 测试文档上传...")
    try:
        # 创建测试文档
        test_content = """
        这是一个测试文档。
        
        关于人工智能：
        人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。
        
        关于机器学习：
        机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。
        
        关于深度学习：
        深度学习是机器学习的一个子集，使用神经网络来模拟人脑的工作方式。
        """
        
        files = {'file': ('test_document.txt', io.StringIO(test_content), 'text/plain')}
        response = requests.post(f"{api_url}/api/upload", files=files, timeout=10)
        
        if response.status_code == 200:
            print("✅ 文档上传成功")
            result = response.json()
            print(f"   文档ID: {result.get('doc_id', 'N/A')}")
            print(f"   文件名: {result.get('filename', 'N/A')}")
            print(f"   内容长度: {result.get('content_length', 'N/A')}")
        else:
            print(f"❌ 文档上传失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 文档上传异常: {e}")
    
    print()
    
    # 3. 测试文档列表
    print("3. 测试文档列表...")
    try:
        response = requests.get(f"{api_url}/api/documents", timeout=10)
        if response.status_code == 200:
            print("✅ 获取文档列表成功")
            result = response.json()
            print(f"   文档总数: {result.get('total_count', 0)}")
            for doc in result.get('documents', []):
                print(f"   - {doc.get('filename', 'N/A')} (创建时间: {doc.get('created_at', 'N/A')})")
        else:
            print(f"❌ 获取文档列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取文档列表异常: {e}")
    
    print()
    
    # 4. 测试聊天功能
    print("4. 测试聊天功能...")
    test_questions = [
        "什么是人工智能？",
        "机器学习和深度学习有什么区别？",
        "请介绍一下AI的发展历史"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"   问题 {i}: {question}")
        try:
            response = requests.post(
                f"{api_url}/api/chat",
                json={'message': question},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 回答: {result.get('response', 'N/A')[:100]}...")
                print(f"   📚 相关文档数: {len(result.get('relevant_documents', []))}")
            else:
                print(f"   ❌ 聊天失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 聊天异常: {e}")
        print()
    
    # 5. 测试聊天历史
    print("5. 测试聊天历史...")
    try:
        response = requests.get(f"{api_url}/api/chat/history", timeout=10)
        if response.status_code == 200:
            print("✅ 获取聊天历史成功")
            result = response.json()
            print(f"   历史记录总数: {result.get('total_count', 0)}")
        else:
            print(f"❌ 获取聊天历史失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取聊天历史异常: {e}")
    
    print()
    print("🎉 API测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_api_endpoints()