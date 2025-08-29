"""
🎯 火控系统测试套件
==================

测试"大宪章"第四章：知识的"掌控" - "火控系统"的铸成
- 三段式拨盘控制
- AI注意力精确控制
- 后端请求路由
- 神之档位接口预留

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Genesis" Chapter 4
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.fire_control_system import FireControlSystem, SearchScope, AttentionTarget, FireControlConfig
from core.intelligence_brain import IntelligenceBrain

def test_fire_control_system():
    """测试火控系统基本功能"""
    print("🎯 火控系统测试套件")
    print("=" * 50)
    print("基于'大宪章'第四章的火控系统功能测试")
    print("版本: 2.0.0 - Genesis Chapter 4")
    print("=" * 50)
    
    tests = [
        ("火控系统初始化", test_fire_control_initialization),
        ("注意力目标设置", test_attention_target_setting),
        ("检索策略生成", test_retrieval_strategy_generation),
        ("三段式拨盘控制", test_three_stage_dial_control),
        ("聊天历史管理", test_chat_history_management),
        ("文档注册管理", test_document_registration),
        ("火控系统状态", test_fire_control_status),
        ("集成大脑测试", test_integrated_brain)
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
        print("\n🎉 所有测试通过！火控系统完全正常！")
    elif passed >= total * 0.8:
        print(f"\n✅ 核心功能测试通过！火控系统基本正常！")
        print(f"⚠️ 有 {total - passed} 个测试失败，可能是配置或环境问题")
    else:
        print(f"\n⚠️ 多个测试失败，请检查火控系统配置")

def test_fire_control_initialization():
    """测试火控系统初始化"""
    try:
        print("🎯 测试火控系统初始化...")
        
        # 测试默认配置初始化
        fire_control = FireControlSystem()
        
        # 验证初始状态
        assert fire_control.config.default_scope == SearchScope.FULL_DATABASE
        assert fire_control.current_target.scope == SearchScope.FULL_DATABASE
        assert len(fire_control.chat_history) == 0
        assert len(fire_control.active_documents) == 0
        
        print("✅ 火控系统初始化成功")
        print(f"   默认范围: {fire_control.config.default_scope.value}")
        print(f"   当前目标: {fire_control.current_target.scope.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 火控系统初始化失败: {e}")
        return False

def test_attention_target_setting():
    """测试注意力目标设置"""
    try:
        print("🎯 测试注意力目标设置...")
        
        fire_control = FireControlSystem()
        
        # 测试设置全数据库范围
        result = fire_control.set_attention_target(SearchScope.FULL_DATABASE)
        assert result["success"] == True
        assert fire_control.current_target.scope == SearchScope.FULL_DATABASE
        print(f"   全数据库范围设置: {result['message']}")
        
        # 测试设置聊天范围
        result = fire_control.set_attention_target(SearchScope.CURRENT_CHAT)
        assert result["success"] == True
        assert fire_control.current_target.scope == SearchScope.CURRENT_CHAT
        print(f"   当前聊天范围设置: {result['message']}")
        
        # 测试设置文档范围（应该失败，因为没有目标ID）
        result = fire_control.set_attention_target(SearchScope.CURRENT_DOCUMENT)
        assert result["success"] == False
        print(f"   文档范围设置（无目标ID）: {result['message']}")
        
        # 测试设置文档范围（有目标ID）
        result = fire_control.set_attention_target(SearchScope.CURRENT_DOCUMENT, "test_doc_123")
        assert result["success"] == True
        assert fire_control.current_target.target_id == "test_doc_123"
        print(f"   文档范围设置（有目标ID）: {result['message']}")
        
        print("✅ 注意力目标设置测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 注意力目标设置测试失败: {e}")
        return False

def test_retrieval_strategy_generation():
    """测试检索策略生成"""
    try:
        print("🎯 测试检索策略生成...")
        
        fire_control = FireControlSystem()
        test_query = "什么是人工智能？"
        
        # 测试全数据库策略
        fire_control.set_attention_target(SearchScope.FULL_DATABASE)
        strategy = fire_control.get_retrieval_strategy(test_query)
        assert strategy["scope"] == SearchScope.FULL_DATABASE.value
        assert strategy["retrieval_type"] == "full_database"
        assert strategy["use_shields"] == True
        print(f"   全数据库策略: {strategy['retrieval_type']}")
        
        # 测试聊天历史策略
        fire_control.set_attention_target(SearchScope.CURRENT_CHAT)
        strategy = fire_control.get_retrieval_strategy(test_query)
        assert strategy["scope"] == SearchScope.CURRENT_CHAT.value
        assert strategy["retrieval_type"] == "chat_history"
        assert strategy["time_decay"] == True
        print(f"   聊天历史策略: {strategy['retrieval_type']}")
        
        # 测试文档范围策略
        fire_control.set_attention_target(SearchScope.CURRENT_DOCUMENT, "test_doc")
        strategy = fire_control.get_retrieval_strategy(test_query)
        assert strategy["scope"] == SearchScope.CURRENT_DOCUMENT.value
        assert strategy["retrieval_type"] == "document_focused"
        assert strategy["hierarchical_search"] == True
        print(f"   文档范围策略: {strategy['retrieval_type']}")
        
        print("✅ 检索策略生成测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 检索策略生成测试失败: {e}")
        return False

def test_three_stage_dial_control():
    """测试三段式拨盘控制"""
    try:
        print("🎯 测试三段式拨盘控制...")
        
        fire_control = FireControlSystem()
        
        # 获取可用范围
        available_scopes = fire_control.get_available_scopes()
        assert len(available_scopes) >= 3  # 至少有三个基本范围
        
        # 验证基本范围
        scope_values = [scope["value"] for scope in available_scopes]
        assert SearchScope.CURRENT_CHAT.value in scope_values
        assert SearchScope.CURRENT_DOCUMENT.value in scope_values
        assert SearchScope.FULL_DATABASE.value in scope_values
        
        print(f"   可用范围数量: {len(available_scopes)}")
        for scope in available_scopes:
            status = "可用" if scope["available"] else "不可用"
            print(f"   {scope['icon']} {scope['label']}: {status}")
        
        # 测试神之档位（默认应该不可用）
        god_mode_available = any(s["value"] == SearchScope.GOD_MODE.value for s in available_scopes)
        if not god_mode_available:
            print("   🔮 神之档位: 未启用（符合预期）")
        
        print("✅ 三段式拨盘控制测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 三段式拨盘控制测试失败: {e}")
        return False

def test_chat_history_management():
    """测试聊天历史管理"""
    try:
        print("🎯 测试聊天历史管理...")
        
        fire_control = FireControlSystem()
        
        # 添加聊天消息
        messages = [
            {"content": "你好", "role": "user"},
            {"content": "您好！有什么可以帮助您的吗？", "role": "assistant"},
            {"content": "什么是人工智能？", "role": "user"},
            {"content": "人工智能是计算机科学的一个分支...", "role": "assistant"}
        ]
        
        for msg in messages:
            fire_control.update_chat_history(msg)
        
        assert len(fire_control.chat_history) == 4
        print(f"   聊天历史长度: {len(fire_control.chat_history)}")
        
        # 测试历史限制
        config = FireControlConfig(chat_history_limit=2)
        fire_control_limited = FireControlSystem(config)
        
        for msg in messages:
            fire_control_limited.update_chat_history(msg)
        
        assert len(fire_control_limited.chat_history) == 2
        print(f"   限制后历史长度: {len(fire_control_limited.chat_history)}")
        
        print("✅ 聊天历史管理测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 聊天历史管理测试失败: {e}")
        return False

def test_document_registration():
    """测试文档注册管理"""
    try:
        print("🎯 测试文档注册管理...")
        
        fire_control = FireControlSystem()
        
        # 注册测试文档
        doc_info = {
            "title": "人工智能基础",
            "size": 1024,
            "type": "pdf",
            "metadata": {"author": "测试作者"}
        }
        
        fire_control.register_document("doc_001", doc_info)
        
        assert "doc_001" in fire_control.active_documents
        assert fire_control.active_documents["doc_001"]["title"] == "人工智能基础"
        
        print(f"   注册文档数量: {len(fire_control.active_documents)}")
        print(f"   文档标题: {fire_control.active_documents['doc_001']['title']}")
        
        # 测试文档范围现在应该可用
        available_scopes = fire_control.get_available_scopes()
        doc_scope = next(s for s in available_scopes if s["value"] == SearchScope.CURRENT_DOCUMENT.value)
        assert doc_scope["available"] == True
        print("   文档范围现在可用: ✅")
        
        print("✅ 文档注册管理测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 文档注册管理测试失败: {e}")
        return False

def test_fire_control_status():
    """测试火控系统状态"""
    try:
        print("🎯 测试火控系统状态...")
        
        fire_control = FireControlSystem()
        
        # 添加一些测试数据
        fire_control.update_chat_history({"content": "测试消息", "role": "user"})
        fire_control.register_document("test_doc", {"title": "测试文档"})
        fire_control.set_attention_target(SearchScope.CURRENT_CHAT)
        
        status = fire_control.get_fire_control_status()
        
        assert status["status"] == "operational"
        assert status["system_version"] == "2.0.0-Genesis-Chapter4"
        assert len(status["capabilities"]) > 0
        assert status["statistics"]["chat_history_count"] == 1
        assert status["statistics"]["active_documents_count"] == 1
        
        print(f"   系统状态: {status['status']}")
        print(f"   版本: {status['system_version']}")
        print(f"   能力数量: {len(status['capabilities'])}")
        print(f"   聊天历史: {status['statistics']['chat_history_count']}")
        print(f"   活跃文档: {status['statistics']['active_documents_count']}")
        
        print("✅ 火控系统状态测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 火控系统状态测试失败: {e}")
        return False

def test_integrated_brain():
    """测试集成大脑的火控功能"""
    try:
        print("🎯 测试集成大脑的火控功能...")
        
        brain = IntelligenceBrain()
        
        # 验证火控系统已集成
        assert hasattr(brain, 'fire_control_system')
        assert brain.fire_control_system is not None
        
        # 测试大脑状态包含火控信息
        brain_status = brain.get_brain_status()
        assert "fire_control_system" in brain_status
        assert brain_status["brain_version"] == "2.0.0-Genesis-Chapter4"
        assert "火控系统" in brain_status["capabilities"]
        
        print(f"   大脑版本: {brain_status['brain_version']}")
        print(f"   架构: {brain_status['architecture']}")
        print("   火控系统已集成: ✅")
        
        # 测试火控查询方法存在
        assert hasattr(brain, 'fire_controlled_query')
        print("   火控查询方法: ✅")
        
        print("✅ 集成大脑测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 集成大脑测试失败: {e}")
        return False

if __name__ == "__main__":
    test_fire_control_system()