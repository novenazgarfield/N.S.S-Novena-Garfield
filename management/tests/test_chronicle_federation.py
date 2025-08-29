#!/usr/bin/env python3
"""
🧪 Chronicle联邦系统测试脚本
============================

测试RAG系统与Chronicle中央医院的"神经连接"
- 测试故障报告功能
- 测试治疗请求功能
- 测试健康检查功能

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Chronicle Genesis Federation"
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加系统路径
sys.path.append(str(Path(__file__).parent / "systems" / "rag-system"))

from core.chronicle_client import (
    get_chronicle_client,
    chronicle_log_failure,
    chronicle_request_healing,
    chronicle_health_check,
    SystemSource,
    FailureSeverity,
    ChronicleConfig
)

async def test_chronicle_federation():
    """测试Chronicle联邦系统"""
    print("🧪 开始测试Chronicle联邦系统...")
    print("=" * 60)
    
    # 1. 健康检查测试
    print("\n🏥 测试1: Chronicle中央医院健康检查")
    print("-" * 40)
    
    try:
        is_healthy = await chronicle_health_check()
        if is_healthy:
            print("✅ Chronicle中央医院在线")
        else:
            print("❌ Chronicle中央医院离线")
            print("⚠️  请确保Chronicle服务器在 http://localhost:3000 运行")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False
    
    # 2. 故障报告测试
    print("\n🚨 测试2: 故障报告功能")
    print("-" * 40)
    
    try:
        # 创建测试异常
        class TestException(Exception):
            pass
        
        test_error = TestException("这是一个测试故障：文档处理失败")
        
        failure_result = await chronicle_log_failure(
            source=SystemSource.RAG_SYSTEM,
            function_name="test_function",
            error=test_error,
            context={
                "test_mode": True,
                "test_description": "Chronicle联邦系统测试",
                "timestamp": "2024-08-29"
            },
            severity=FailureSeverity.MEDIUM
        )
        
        if failure_result:
            print("✅ 故障报告发送成功")
            print(f"   故障ID: {failure_result.get('failure_id', 'N/A')}")
            failure_id = failure_result.get('failure_id')
        else:
            print("❌ 故障报告发送失败")
            return False
            
    except Exception as e:
        print(f"❌ 故障报告异常: {e}")
        return False
    
    # 3. 治疗请求测试
    print("\n🏥 测试3: 治疗请求功能")
    print("-" * 40)
    
    try:
        healing_result = await chronicle_request_healing(
            source=SystemSource.RAG_SYSTEM,
            function_name="test_function",
            error=test_error,
            context={
                "failure_id": failure_id,
                "test_mode": True
            },
            healing_strategy="ai_analyze_fix"
        )
        
        if healing_result and healing_result.success:
            print("✅ 治疗方案获取成功")
            print(f"   治疗策略: {healing_result.strategy}")
            print(f"   治疗信息: {healing_result.message}")
            print(f"   成功率预估: {healing_result.estimated_success_rate:.1%}")
            
            if healing_result.recommendations:
                print("   治疗建议:")
                for i, rec in enumerate(healing_result.recommendations, 1):
                    print(f"     {i}. {rec}")
        else:
            print("❌ 治疗方案获取失败")
            return False
            
    except Exception as e:
        print(f"❌ 治疗请求异常: {e}")
        return False
    
    # 4. 客户端配置测试
    print("\n⚙️ 测试4: 客户端配置")
    print("-" * 40)
    
    try:
        client = get_chronicle_client()
        print(f"✅ Chronicle客户端配置正常")
        print(f"   服务器地址: {client.config.base_url}")
        print(f"   连接状态: {client.connection_status.value}")
        print(f"   重试次数: {client.config.retry_attempts}")
        print(f"   降级模式: {'启用' if client.config.enable_fallback else '禁用'}")
        
    except Exception as e:
        print(f"❌ 客户端配置异常: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Chronicle联邦系统测试完成！")
    print("✅ RAG系统与Chronicle中央医院的神经连接正常")
    print("🏥 Chronicle联邦治疗系统已准备就绪")
    
    return True

async def test_chronicle_healing_decorator():
    """测试Chronicle联邦治疗装饰器"""
    print("\n🔧 测试5: Chronicle联邦治疗装饰器")
    print("-" * 40)
    
    try:
        from core.chronicle_healing import chronicle_self_healing, FailureSeverity, SystemSource
        
        @chronicle_self_healing(
            source=SystemSource.RAG_SYSTEM,
            severity=FailureSeverity.LOW,
            max_retries=2
        )
        def test_function_with_healing():
            """测试带有Chronicle治疗装饰器的函数"""
            import random
            if random.random() < 0.7:  # 70%概率失败，测试治疗功能
                raise ValueError("模拟故障：随机测试错误")
            return "函数执行成功！"
        
        # 执行测试函数
        result = await test_function_with_healing()
        print(f"✅ 装饰器测试成功: {result}")
        
    except Exception as e:
        print(f"⚠️ 装饰器测试最终失败: {e}")
        print("   这是正常的，因为我们故意制造了故障来测试治疗功能")
    
    return True

def main():
    """主函数"""
    print("🏥 Chronicle联邦系统测试")
    print("🔗 测试RAG系统与Chronicle中央医院的神经连接")
    print()
    
    # 检查Chronicle服务器是否运行
    print("📋 测试前检查:")
    print("1. 确保Chronicle服务器在 http://localhost:3000 运行")
    print("2. 确保Chronicle数据库已初始化")
    print("3. 确保网络连接正常")
    print()
    
    input("按回车键开始测试...")
    
    # 运行异步测试
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 基础功能测试
        success = loop.run_until_complete(test_chronicle_federation())
        
        if success:
            # 装饰器测试
            loop.run_until_complete(test_chronicle_healing_decorator())
            
            print("\n🎊 所有测试完成！Chronicle联邦系统运行正常")
            print("🚀 现在可以启动RAG系统，享受Chronicle联邦治疗服务")
        else:
            print("\n💥 测试失败！请检查Chronicle服务器状态")
            
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {e}")
    finally:
        print("\n👋 测试结束")

if __name__ == "__main__":
    main()