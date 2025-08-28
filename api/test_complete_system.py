#!/usr/bin/env python3
"""
完整系统测试脚本
测试三阶段AI模型管理系统的所有功能
"""

import requests
import json
import time
from datetime import datetime

def print_header(title):
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def test_energy_api():
    """测试中央能源API"""
    print_header("测试中央能源API")
    
    base_url = "http://localhost:56420"
    
    try:
        # 1. 健康检查
        print("1️⃣ 健康检查...")
        response = requests.get(f"{base_url}/api/energy/health", timeout=5)
        print(f"   状态: {response.status_code}")
        print(f"   响应: {response.json()}")
        
        # 2. 获取可用模型
        print("\n2️⃣ 获取可用模型...")
        response = requests.get(f"{base_url}/api/energy/models/available", timeout=5)
        models = response.json()
        print(f"   状态: {response.status_code}")
        print(f"   Google模型: {list(models.get('google', {}).keys())}")
        print(f"   OpenAI模型: {list(models.get('openai', {}).keys())}")
        
        # 3. 添加配置
        print("\n3️⃣ 添加AI配置...")
        config_data = {
            "user_id": "test_user",
            "project_id": "test_project",
            "provider": "google",
            "model_name": "gemini-2.0-flash-exp",
            "api_key": "test_api_key_12345",
            "scope": "project",
            "priority": 1
        }
        response = requests.post(f"{base_url}/api/energy/config", json=config_data, timeout=5)
        print(f"   状态: {response.status_code}")
        print(f"   响应: {response.json()}")
        
        # 4. 获取最佳配置
        print("\n4️⃣ 获取最佳配置...")
        response = requests.get(
            f"{base_url}/api/energy/config/best",
            params={"user_id": "test_user", "project_id": "test_project"},
            timeout=5
        )
        print(f"   状态: {response.status_code}")
        print(f"   响应: {response.json()}")
        
        print("\n✅ 中央能源API测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ 中央能源API测试失败: {e}")
        return False

def test_dynamic_rag_api():
    """测试动态RAG API"""
    print_header("测试动态RAG API")
    
    base_url = "http://localhost:60010"
    
    try:
        # 1. 健康检查
        print("1️⃣ 健康检查...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"   状态: {response.status_code}")
        print(f"   响应: {response.json()}")
        
        # 2. 获取当前配置
        print("\n2️⃣ 获取当前AI配置...")
        response = requests.get(
            f"{base_url}/api/config/current",
            params={"user_id": "test_user", "project_id": "test_project"},
            timeout=5
        )
        print(f"   状态: {response.status_code}")
        config_info = response.json()
        print(f"   配置来源: {config_info.get('source')}")
        print(f"   AI配置: {config_info.get('config')}")
        
        # 3. 测试聊天功能
        print("\n3️⃣ 测试动态AI聊天...")
        chat_data = {
            "message": "你好，请介绍一下这个动态AI系统的特点",
            "user_id": "test_user",
            "project_id": "test_project"
        }
        response = requests.post(f"{base_url}/api/chat", json=chat_data, timeout=10)
        print(f"   状态: {response.status_code}")
        chat_result = response.json()
        print(f"   模型信息: {chat_result.get('model_info')}")
        print(f"   响应预览: {chat_result.get('response', '')[:100]}...")
        
        # 4. 测试上下文清除
        print("\n4️⃣ 测试上下文清除...")
        response = requests.post(f"{base_url}/api/clear", timeout=5)
        print(f"   状态: {response.status_code}")
        print(f"   响应: {response.json()}")
        
        print("\n✅ 动态RAG API测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ 动态RAG API测试失败: {e}")
        return False

def test_nexus_interface():
    """测试NEXUS界面"""
    print_header("测试NEXUS界面")
    
    try:
        # 测试NEXUS主页
        print("1️⃣ 测试NEXUS主页...")
        response = requests.get("http://localhost:8080", timeout=5)
        print(f"   状态: {response.status_code}")
        print(f"   内容长度: {len(response.text)} 字符")
        
        # 检查是否包含AI配置管理功能
        if "AI配置管理" in response.text or "aiConfigManager" in response.text:
            print("   ✅ AI配置管理功能已集成")
        else:
            print("   ⚠️ 未检测到AI配置管理功能")
        
        print("\n✅ NEXUS界面测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ NEXUS界面测试失败: {e}")
        return False

def test_integration():
    """测试系统集成"""
    print_header("测试系统集成")
    
    try:
        print("1️⃣ 测试端到端流程...")
        
        # 步骤1: 添加配置到中央能源数据库
        print("   📝 添加AI配置...")
        config_data = {
            "user_id": "integration_test",
            "project_id": "test_integration",
            "provider": "google",
            "model_name": "gemini-1.5-pro",
            "api_key": "integration_test_key",
            "scope": "project",
            "priority": 2
        }
        response = requests.post("http://localhost:56420/api/energy/config", json=config_data, timeout=5)
        print(f"      状态: {response.status_code}")
        
        # 步骤2: 通过动态RAG API使用配置
        print("   🤖 通过动态RAG使用配置...")
        chat_data = {
            "message": "集成测试：请确认当前使用的AI模型",
            "user_id": "integration_test",
            "project_id": "test_integration"
        }
        response = requests.post("http://localhost:60010/api/chat", json=chat_data, timeout=10)
        print(f"      状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            model_info = result.get('model_info', {})
            print(f"      使用的模型: {model_info.get('provider')}/{model_info.get('model')}")
            print(f"      配置来源: {model_info.get('source')}")
        
        print("\n✅ 系统集成测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ 系统集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始完整系统测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 测试各个组件
    results.append(("中央能源API", test_energy_api()))
    results.append(("动态RAG API", test_dynamic_rag_api()))
    results.append(("NEXUS界面", test_nexus_interface()))
    results.append(("系统集成", test_integration()))
    
    # 汇总结果
    print_header("测试结果汇总")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！三阶段AI模型管理系统运行正常！")
        print("\n📋 系统状态:")
        print("   Phase 1: ✅ 中央能源数据库 (端口 56420)")
        print("   Phase 2: ✅ NEXUS工程主控台 (端口 8080)")
        print("   Phase 3: ✅ 动态RAG AI系统 (端口 60010)")
        print("\n🔗 访问地址:")
        print("   NEXUS界面: http://localhost:8080")
        print("   能源API: http://localhost:56420")
        print("   动态RAG: http://localhost:60010")
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败，请检查系统配置")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)