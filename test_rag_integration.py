#!/usr/bin/env python3
"""
测试RAG系统集成
"""
import sys
import os
from pathlib import Path
import requests
import time
import json

# 添加RAG系统路径
rag_path = Path("/workspace/N.S.S-Novena-Garfield/systems/rag-system")
sys.path.append(str(rag_path))

def test_rag_system_import():
    """测试RAG系统导入"""
    print("🧪 测试RAG系统导入...")
    try:
        # 设置环境变量
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        
        # 切换到RAG目录
        os.chdir(str(rag_path))
        
        # 测试导入
        from core.rag_system import RAGSystem
        print("✅ RAG系统导入成功")
        
        # 测试初始化
        rag = RAGSystem()
        print("✅ RAG系统初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_server():
    """测试API服务器"""
    print("🧪 测试API服务器...")
    
    # 检查健康状态
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API服务器运行正常")
            print(f"   状态: {data.get('status')}")
            print(f"   RAG系统就绪: {data.get('rag_system_ready')}")
            return True
        else:
            print(f"❌ API服务器响应异常: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器 (http://localhost:5000)")
        return False
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def test_chat_api():
    """测试聊天API"""
    print("🧪 测试聊天API...")
    
    try:
        response = requests.post(
            "http://localhost:5000/api/chat",
            json={"message": "你好，请介绍一下你自己", "task_name": "test"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 聊天API测试成功")
                print(f"   回复: {data.get('response', '')[:100]}...")
                return True
            else:
                print(f"❌ 聊天API返回错误: {data.get('error')}")
                return False
        else:
            print(f"❌ 聊天API响应异常: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 聊天API测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始RAG系统集成测试...")
    print("=" * 50)
    
    # 测试1: RAG系统导入
    if not test_rag_system_import():
        print("❌ RAG系统导入测试失败，请检查依赖")
        return False
    
    print()
    
    # 测试2: API服务器
    if not test_api_server():
        print("❌ API服务器测试失败，请先启动API服务器")
        print("   启动命令: python /workspace/N.S.S-Novena-Garfield/systems/rag-system/api_server.py")
        return False
    
    print()
    
    # 测试3: 聊天API
    if not test_chat_api():
        print("❌ 聊天API测试失败")
        return False
    
    print()
    print("=" * 50)
    print("✅ 所有测试通过！RAG系统集成正常")
    print("🌐 前端地址: http://localhost:52943/systems/nexus/nexus-dashboard-restored.html")
    print("🤖 RAG API: http://localhost:5000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)