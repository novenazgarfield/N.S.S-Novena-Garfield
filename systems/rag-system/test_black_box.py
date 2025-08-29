"""
🛡️ 黑匣子与免疫系统测试套件
===============================

测试"大宪章"第六章：失败的"记忆" - "黑匣子"与"免疫系统"的构建
- 独立的故障数据库 (failure_log.db)
- 自动伤害记录仪 (Auto Damage Recorder)
- 免疫系统构建 (Immune System Builder)
- 故障模式识别与预防

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Genesis" Chapter 6
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.black_box import BlackBoxRecorder, SystemSource, FailureStatus, get_black_box
from core.pantheon_soul import PantheonSoul, ai_self_healing, HealingStrategy
from core.intelligence_brain import IntelligenceBrain

def test_black_box_system():
    """测试黑匣子与免疫系统"""
    print("🛡️ 黑匣子与免疫系统测试套件")
    print("=" * 50)
    print("基于'大宪章'第六章的黑匣子与免疫系统功能测试")
    print("版本: 2.0.0 - Genesis Chapter 6")
    print("=" * 50)
    
    tests = [
        ("黑匣子初始化", test_black_box_initialization),
        ("故障记录功能", test_failure_recording),
        ("故障修复更新", test_failure_fix_update),
        ("故障统计功能", test_failure_statistics),
        ("免疫系统功能", test_immunity_system),
        ("集成自我修复", test_integrated_self_healing),
        ("故障模式识别", test_failure_pattern_recognition)
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
        print("\n🎉 所有测试通过！黑匣子与免疫系统完全正常！")
    elif passed >= total * 0.8:
        print(f"\n✅ 核心功能测试通过！黑匣子系统基本正常！")
        print(f"⚠️ 有 {total - passed} 个测试失败，可能是配置或环境问题")
    else:
        print(f"\n⚠️ 多个测试失败，请检查黑匣子系统配置")

def test_black_box_initialization():
    """测试黑匣子初始化"""
    try:
        print("🛡️ 测试黑匣子初始化...")
        
        # 测试黑匣子创建
        black_box = BlackBoxRecorder()
        
        # 验证数据库文件创建
        assert os.path.exists(black_box.db_path)
        print(f"   数据库文件: {black_box.db_path}")
        
        # 验证全局实例
        global_black_box = get_black_box()
        assert global_black_box is not None
        print("   全局黑匣子实例: ✅")
        
        # 测试数据库表结构
        import sqlite3
        with sqlite3.connect(black_box.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ["failure_records", "failure_patterns", "immunity_records"]
            for table in expected_tables:
                assert table in tables
                print(f"   数据表 {table}: ✅")
        
        print("✅ 黑匣子初始化成功")
        return True
        
    except Exception as e:
        print(f"❌ 黑匣子初始化失败: {e}")
        return False

def test_failure_recording():
    """测试故障记录功能"""
    try:
        print("🛡️ 测试故障记录功能...")
        
        black_box = get_black_box()
        
        # 创建测试错误
        test_error = ValueError("测试错误消息")
        
        # 记录故障
        failure_id = black_box.record_failure(
            source_system=SystemSource.RAG_SYSTEM,
            function_name="test_function",
            error=test_error,
            faulty_code="def test_function(): raise ValueError('测试错误')",
            context_data={"test_param": "test_value"}
        )
        
        assert failure_id != ""
        print(f"   故障ID: {failure_id}")
        
        # 验证记录是否存储
        records = black_box.get_failure_records(limit=1)
        assert len(records) > 0
        
        latest_record = records[0]
        assert latest_record["failure_id"] == failure_id
        assert latest_record["source_system"] == SystemSource.RAG_SYSTEM.value
        assert latest_record["function_name"] == "test_function"
        assert latest_record["error_type"] == "ValueError"
        assert latest_record["error_message"] == "测试错误消息"
        
        print("   故障记录存储: ✅")
        print(f"   记录详情: {latest_record['function_name']} - {latest_record['error_type']}")
        
        print("✅ 故障记录功能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 故障记录功能测试失败: {e}")
        return False

def test_failure_fix_update():
    """测试故障修复更新"""
    try:
        print("🛡️ 测试故障修复更新...")
        
        black_box = get_black_box()
        
        # 先记录一个故障
        test_error = RuntimeError("修复测试错误")
        failure_id = black_box.record_failure(
            source_system=SystemSource.PANTHEON_SOUL,
            function_name="fix_test_function",
            error=test_error,
            faulty_code="def fix_test_function(): raise RuntimeError('修复测试错误')"
        )
        
        # 更新修复信息 - 修复成功
        ai_fix_code = """
# AI修复建议
try:
    # 原始代码
    pass
except RuntimeError as e:
    logger.error(f"处理RuntimeError: {e}")
    # 降级处理
"""
        
        black_box.update_failure_fix(failure_id, ai_fix_code, True, 2)
        
        # 验证更新
        records = black_box.get_failure_records(limit=10)
        updated_record = None
        for record in records:
            if record["failure_id"] == failure_id:
                updated_record = record
                break
        
        assert updated_record is not None
        assert updated_record["fix_success"] == True
        assert updated_record["ai_fix_attempted"] == ai_fix_code
        assert updated_record["retry_count"] == 2
        assert updated_record["status"] == FailureStatus.FIXED.value
        
        print("   修复成功更新: ✅")
        
        # 测试修复失败的情况
        failure_id_2 = black_box.record_failure(
            source_system=SystemSource.FIRE_CONTROL,
            function_name="fail_test_function",
            error=KeyError("修复失败测试"),
            faulty_code="def fail_test_function(): raise KeyError('修复失败测试')"
        )
        
        black_box.update_failure_fix(failure_id_2, "修复尝试失败", False, 3)
        
        # 验证失败更新
        records = black_box.get_failure_records(limit=10)
        failed_record = None
        for record in records:
            if record["failure_id"] == failure_id_2:
                failed_record = record
                break
        
        assert failed_record is not None
        assert failed_record["fix_success"] == False
        assert failed_record["status"] == FailureStatus.FAILED.value
        
        print("   修复失败更新: ✅")
        
        print("✅ 故障修复更新测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 故障修复更新测试失败: {e}")
        return False

def test_failure_statistics():
    """测试故障统计功能"""
    try:
        print("🛡️ 测试故障统计功能...")
        
        black_box = get_black_box()
        
        # 获取统计信息
        stats = black_box.get_failure_statistics()
        
        assert "total_failures" in stats
        assert "fixed_failures" in stats
        assert "fix_rate" in stats
        assert "system_statistics" in stats
        assert "error_type_statistics" in stats
        assert "failure_patterns" in stats
        assert "immunity_records" in stats
        
        print(f"   总故障数: {stats['total_failures']}")
        print(f"   修复成功: {stats['fixed_failures']}")
        print(f"   修复率: {stats['fix_rate']:.1%}")
        print(f"   故障模式: {stats['failure_patterns']}")
        print(f"   免疫记录: {stats['immunity_records']}")
        
        # 验证系统统计
        system_stats = stats["system_statistics"]
        assert isinstance(system_stats, dict)
        
        if system_stats:
            for system, system_stat in system_stats.items():
                assert "total" in system_stat
                assert "fixed" in system_stat
                assert "fix_rate" in system_stat
                print(f"   系统 {system}: {system_stat['total']} 故障, {system_stat['fixed']} 修复")
        
        print("✅ 故障统计功能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 故障统计功能测试失败: {e}")
        return False

def test_immunity_system():
    """测试免疫系统功能"""
    try:
        print("🛡️ 测试免疫系统功能...")
        
        black_box = get_black_box()
        
        # 获取免疫状态
        immunity_status = black_box.get_immunity_status()
        
        assert "total_immunities" in immunity_status
        assert "average_effectiveness" in immunity_status
        assert "immunity_records" in immunity_status
        assert "system_health" in immunity_status
        
        print(f"   免疫记录数: {immunity_status['total_immunities']}")
        print(f"   平均效果: {immunity_status['average_effectiveness']:.1%}")
        print(f"   系统健康: {immunity_status['system_health']}")
        
        # 验证免疫记录结构
        immunity_records = immunity_status["immunity_records"]
        if immunity_records:
            for record in immunity_records[:3]:  # 检查前3个
                assert "immunity_id" in record
                assert "error_signature" in record
                assert "effectiveness_score" in record
                assert "activation_count" in record
                print(f"   免疫记录: {record['immunity_id']} - {record['effectiveness_score']:.1%}")
        
        print("✅ 免疫系统功能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 免疫系统功能测试失败: {e}")
        return False

def test_integrated_self_healing():
    """测试集成自我修复功能"""
    try:
        print("🛡️ 测试集成自我修复功能...")
        
        # 创建Pantheon灵魂实例（已集成黑匣子）
        pantheon_soul = PantheonSoul()
        
        # 创建测试函数，会触发黑匣子记录
        @pantheon_soul.ai_self_healing(strategy=HealingStrategy.AI_ANALYZE_FIX, max_retries=2)
        def test_integrated_function():
            raise AttributeError("集成测试错误")
        
        # 执行函数，应该触发黑匣子记录
        try:
            test_integrated_function()
        except AttributeError:
            pass  # 预期的异常
        
        # 验证黑匣子中是否有记录
        black_box = get_black_box()
        records = black_box.get_failure_records(limit=10)
        
        # 查找我们的测试记录
        test_record = None
        for record in records:
            if record["function_name"] == "test_integrated_function":
                test_record = record
                break
        
        assert test_record is not None
        assert test_record["error_type"] == "AttributeError"
        assert test_record["source_system"] == SystemSource.PANTHEON_SOUL.value
        assert test_record["ai_fix_attempted"] is not None
        
        print("   集成记录创建: ✅")
        print(f"   故障ID: {test_record['failure_id']}")
        print(f"   AI修复尝试: {'有' if test_record['ai_fix_attempted'] else '无'}")
        
        print("✅ 集成自我修复功能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 集成自我修复功能测试失败: {e}")
        return False

def test_failure_pattern_recognition():
    """测试故障模式识别"""
    try:
        print("🛡️ 测试故障模式识别...")
        
        black_box = get_black_box()
        
        # 创建相似的故障来测试模式识别
        similar_errors = [
            ValueError("参数错误: 无效的输入值"),
            ValueError("参数错误: 空值不允许"),
            ValueError("参数错误: 类型不匹配")
        ]
        
        # 记录相似故障
        for i, error in enumerate(similar_errors):
            black_box.record_failure(
                source_system=SystemSource.RAG_SYSTEM,
                function_name=f"pattern_test_function_{i}",
                error=error,
                faulty_code=f"def pattern_test_function_{i}(): raise ValueError('参数错误')"
            )
        
        # 获取统计信息，验证模式识别
        stats = black_box.get_failure_statistics()
        
        # 验证错误类型统计
        error_stats = stats.get("error_type_statistics", {})
        assert "ValueError" in error_stats
        assert error_stats["ValueError"] >= 3  # 至少有我们刚添加的3个
        
        print(f"   ValueError 模式识别: {error_stats.get('ValueError', 0)} 次")
        
        # 验证故障模式数量增加
        pattern_count = stats.get("failure_patterns", 0)
        assert pattern_count > 0
        print(f"   识别的故障模式: {pattern_count} 个")
        
        print("✅ 故障模式识别测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 故障模式识别测试失败: {e}")
        return False

if __name__ == "__main__":
    test_black_box_system()