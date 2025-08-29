"""
🌟 Pantheon灵魂测试套件
======================

测试"大宪章"第五章：知识的"进化" - "Pantheon灵魂"的融合
- 自我修复基因 (@ai_self_healing装饰器)
- 透明观察窗 (代码透明化)
- 战地指挥官 (ReAct代理模式)
- 智慧汲取与成长能力

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Genesis" Chapter 5
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.pantheon_soul import (
    PantheonSoul, ReActAgent, ai_self_healing, 
    HealingStrategy, TaskComplexity, HealingConfig
)
from core.intelligence_brain import IntelligenceBrain

def test_pantheon_soul():
    """测试Pantheon灵魂系统"""
    print("🌟 Pantheon灵魂测试套件")
    print("=" * 50)
    print("基于'大宪章'第五章的Pantheon灵魂功能测试")
    print("版本: 2.0.0 - Genesis Chapter 5")
    print("=" * 50)
    
    tests = [
        ("Pantheon灵魂初始化", test_pantheon_soul_initialization),
        ("自我修复装饰器", test_ai_self_healing_decorator),
        ("透明观察窗", test_transparency_window),
        ("ReAct代理初始化", test_react_agent_initialization),
        ("复杂任务执行", test_complex_task_execution),
        ("修复统计功能", test_healing_statistics),
        ("集成大脑测试", test_integrated_brain_pantheon)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 运行测试: {test_name}")
        print("-" * 30)
        try:
            if test_func():
                print(f"✅ {test_name} 测试通过")
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 测试总结")
    print("=" * 50)
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {total - passed}")
    print(f"📊 总计: {total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！Pantheon灵魂完全觉醒！")
    elif passed >= total * 0.8:
        print(f"\n✅ 核心功能测试通过！Pantheon灵魂基本觉醒！")
        print(f"⚠️ 有 {total - passed} 个测试失败，可能是配置或环境问题")
    else:
        print(f"\n⚠️ 多个测试失败，请检查Pantheon灵魂配置")

def test_pantheon_soul_initialization():
    """测试Pantheon灵魂初始化"""
    try:
        print("🌟 测试Pantheon灵魂初始化...")
        
        # 测试默认配置初始化
        pantheon_soul = PantheonSoul()
        
        # 验证初始状态
        assert pantheon_soul.config.max_retries == 3
        assert pantheon_soul.config.enable_ai_healing == True
        assert pantheon_soul.config.enable_transparency == True
        assert len(pantheon_soul.execution_traces) == 0
        assert len(pantheon_soul.healing_knowledge) == 0
        
        print("✅ Pantheon灵魂初始化成功")
        print(f"   最大重试次数: {pantheon_soul.config.max_retries}")
        print(f"   AI修复启用: {pantheon_soul.config.enable_ai_healing}")
        print(f"   透明化启用: {pantheon_soul.config.enable_transparency}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pantheon灵魂初始化失败: {e}")
        return False

def test_ai_self_healing_decorator():
    """测试自我修复装饰器"""
    try:
        print("🧬 测试自我修复装饰器...")
        
        pantheon_soul = PantheonSoul()
        
        # 创建测试函数
        @pantheon_soul.ai_self_healing(strategy=HealingStrategy.AI_ANALYZE_FIX, max_retries=2)
        def test_function_success():
            return "success"
        
        @pantheon_soul.ai_self_healing(strategy=HealingStrategy.AI_ANALYZE_FIX, max_retries=2)
        def test_function_failure():
            raise ValueError("测试错误")
        
        # 测试成功执行
        result = test_function_success()
        assert result == "success"
        print("   成功函数执行: ✅")
        
        # 测试失败执行（应该触发自我修复）
        try:
            test_function_failure()
            print("   失败函数应该抛出异常")
            return False
        except ValueError:
            print("   失败函数正确触发修复机制: ✅")
        
        # 验证执行轨迹记录
        assert len(pantheon_soul.execution_traces) >= 2
        print(f"   执行轨迹记录: {len(pantheon_soul.execution_traces)} 条")
        
        # 验证修复知识库
        assert len(pantheon_soul.healing_knowledge) > 0
        print(f"   修复知识库: {len(pantheon_soul.healing_knowledge)} 个错误类型")
        
        print("✅ 自我修复装饰器测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 自我修复装饰器测试失败: {e}")
        return False

def test_transparency_window():
    """测试透明观察窗"""
    try:
        print("🔍 测试透明观察窗...")
        
        pantheon_soul = PantheonSoul()
        
        # 创建带透明化的测试函数
        @pantheon_soul.ai_self_healing(enable_transparency=True)
        def transparent_function(x, y=10):
            """这是一个测试函数"""
            return x + y
        
        # 执行函数
        result = transparent_function(5, y=15)
        assert result == 20
        print("   透明函数执行成功: ✅")
        
        # 获取透明视图
        transparency_view = pantheon_soul.get_transparency_view("transparent_function")
        
        assert transparency_view is not None
        assert "function_info" in transparency_view
        assert "code_transparency" in transparency_view
        
        # 验证代码透明性信息
        code_info = transparency_view["code_transparency"]
        assert code_info["function_name"] == "transparent_function"
        assert "source_code" in code_info
        assert "signature" in code_info
        assert "docstring" in code_info
        
        print("   透明视图获取成功: ✅")
        print(f"   函数签名: {code_info.get('signature', 'N/A')}")
        print(f"   文档字符串: {code_info.get('docstring', 'N/A')}")
        
        print("✅ 透明观察窗测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 透明观察窗测试失败: {e}")
        return False

def test_react_agent_initialization():
    """测试ReAct代理初始化"""
    try:
        print("🎖️ 测试ReAct代理初始化...")
        
        pantheon_soul = PantheonSoul()
        react_agent = ReActAgent(pantheon_soul)
        
        # 验证初始状态
        assert react_agent.pantheon_soul == pantheon_soul
        assert len(react_agent.planning_history) == 0
        
        # 获取代理状态
        status = react_agent.get_agent_status()
        
        assert status["agent_status"] == "operational"
        assert status["mode"] == "ReAct (Reason + Act)"
        assert status["version"] == "2.0.0-Genesis-Chapter5"
        assert len(status["capabilities"]) > 0
        
        print("✅ ReAct代理初始化成功")
        print(f"   代理状态: {status['agent_status']}")
        print(f"   模式: {status['mode']}")
        print(f"   能力数量: {len(status['capabilities'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ ReAct代理初始化失败: {e}")
        return False

def test_complex_task_execution():
    """测试复杂任务执行"""
    try:
        print("🎖️ 测试复杂任务执行...")
        
        pantheon_soul = PantheonSoul()
        react_agent = ReActAgent(pantheon_soul)
        
        # 测试不同复杂度的任务
        tasks = [
            ("简单任务：计算1+1", TaskComplexity.SIMPLE),
            ("中等任务：分析用户查询意图", TaskComplexity.MODERATE),
            ("复杂任务：构建知识图谱并进行推理", TaskComplexity.COMPLEX)
        ]
        
        for task_desc, complexity in tasks:
            print(f"   执行任务: {task_desc} ({complexity.value})")
            
            result = react_agent.execute_complex_task(task_desc, complexity)
            
            assert result["success"] == True
            assert result["react_mode"] == True
            assert "task_record" in result
            
            task_record = result["task_record"]
            assert task_record["complexity"] == complexity.value
            assert "plan" in task_record
            assert "execution" in task_record
            
            # 验证计划
            plan = task_record["plan"]
            assert len(plan["steps"]) > 0
            print(f"     计划步骤: {len(plan['steps'])} 个")
            
            # 验证执行
            execution = task_record["execution"]
            assert execution["success"] == True
            print(f"     执行成功率: {execution['success_rate']:.1%}")
        
        # 验证历史记录
        assert len(react_agent.planning_history) == len(tasks)
        print(f"   任务历史记录: {len(react_agent.planning_history)} 个")
        
        print("✅ 复杂任务执行测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 复杂任务执行测试失败: {e}")
        return False

def test_healing_statistics():
    """测试修复统计功能"""
    try:
        print("📊 测试修复统计功能...")
        
        pantheon_soul = PantheonSoul()
        
        # 执行一些测试函数来生成统计数据
        @pantheon_soul.ai_self_healing()
        def success_function():
            return "ok"
        
        @pantheon_soul.ai_self_healing()
        def failure_function():
            raise RuntimeError("测试错误")
        
        # 执行函数
        success_function()
        success_function()
        
        try:
            failure_function()
        except:
            pass
        
        # 获取统计信息
        stats = pantheon_soul.get_healing_statistics()
        
        assert "statistics" in stats
        assert "knowledge_base" in stats
        assert "recent_activity" in stats
        assert stats["pantheon_status"] == "evolving"
        
        statistics = stats["statistics"]
        assert statistics["total_executions"] >= 3
        assert statistics["successful_executions"] >= 2
        assert statistics["failed_executions"] >= 1
        
        print(f"   总执行次数: {statistics['total_executions']}")
        print(f"   成功执行: {statistics['successful_executions']}")
        print(f"   失败执行: {statistics['failed_executions']}")
        print(f"   整体成功率: {statistics['overall_success_rate']:.1%}")
        
        knowledge_base = stats["knowledge_base"]
        print(f"   学习的错误类型: {knowledge_base['error_types_learned']}")
        print(f"   修复尝试总数: {knowledge_base['total_healing_attempts']}")
        
        print("✅ 修复统计功能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复统计功能测试失败: {e}")
        return False

def test_integrated_brain_pantheon():
    """测试集成大脑的Pantheon功能"""
    try:
        print("🧠 测试集成大脑的Pantheon功能...")
        
        brain = IntelligenceBrain()
        
        # 验证Pantheon灵魂已集成
        assert hasattr(brain, 'pantheon_soul')
        assert hasattr(brain, 'react_agent')
        assert brain.pantheon_soul is not None
        assert brain.react_agent is not None
        
        # 测试大脑状态包含Pantheon信息
        brain_status = brain.get_brain_status()
        assert "pantheon_soul" in brain_status
        assert "react_agent" in brain_status
        assert brain_status["brain_version"] == "2.0.0-Genesis-Chapter5"
        assert "Pantheon灵魂" in brain_status["architecture"]
        
        # 验证新增能力
        capabilities = brain_status["capabilities"]
        pantheon_capabilities = ["自我修复基因", "透明观察窗", "ReAct代理模式", "智慧汲取与成长"]
        found_capabilities = [cap for cap in pantheon_capabilities if cap in capabilities]
        assert len(found_capabilities) >= 3  # 至少要有3个Pantheon能力
        
        print(f"   大脑版本: {brain_status['brain_version']}")
        print(f"   架构: {brain_status['architecture']}")
        print("   Pantheon灵魂已集成: ✅")
        print("   ReAct代理已集成: ✅")
        print(f"   找到Pantheon能力: {len(found_capabilities)}/4")
        
        # 测试透明观察窗方法
        transparency_view = brain.get_transparency_view("ingest_document")
        # 由于还没有执行过，可能为None，这是正常的
        print(f"   透明观察窗方法: {'✅' if hasattr(brain, 'get_transparency_view') else '❌'}")
        
        # 测试修复统计方法
        healing_stats = brain.get_healing_statistics()
        assert "pantheon_status" in healing_stats
        print(f"   修复统计方法: {'✅' if healing_stats else '❌'}")
        
        # 测试复杂任务执行方法
        assert hasattr(brain, 'execute_complex_task')
        print("   复杂任务执行方法: ✅")
        
        print("✅ 集成大脑Pantheon功能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 集成大脑Pantheon功能测试失败: {e}")
        return False

if __name__ == "__main__":
    test_pantheon_soul()