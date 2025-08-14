#!/usr/bin/env python3
"""
RAG系统简单测试 - 只测试核心功能
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

def test_config():
    """测试配置"""
    print("🔧 测试配置...")
    
    try:
        from config import init_config, StorageConfig, ModelConfig
        
        init_config()
        print(f"✅ 数据目录: {StorageConfig.DATA_DIR}")
        print(f"✅ 嵌入模型: {ModelConfig.EMBEDDING_MODEL_PATH}")
        print(f"✅ LLM模型: {ModelConfig.LLM_MODEL_PATH}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_database():
    """测试数据库"""
    print("\n💾 测试数据库...")
    
    try:
        from database.chat_db import ChatDatabase
        import numpy as np
        
        db = ChatDatabase()
        print("✅ 数据库初始化成功")
        
        # 测试存储消息
        test_embedding = np.random.rand(384).astype('float32')
        db.store_message("user", "测试问题", test_embedding, "test_task")
        print("✅ 消息存储成功")
        
        # 测试获取消息
        messages = db.get_recent_messages(5, "test_task")
        print(f"✅ 消息获取成功，数量: {len(messages)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_memory():
    """测试记忆管理"""
    print("\n🧠 测试记忆管理...")
    
    try:
        from memory.memory_manager import MemoryManager
        
        memory = MemoryManager()
        print("✅ 记忆管理器初始化成功")
        
        # 测试保存临时记忆
        memory.save_temporary_memory("这是一个测试记忆", "test_task")
        print("✅ 临时记忆保存成功")
        
        # 测试加载临时记忆
        memories = memory.load_temporary_memory("test_task")
        print(f"✅ 临时记忆加载成功，数量: {len(memories)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 记忆管理测试失败: {e}")
        return False

def test_document_basic():
    """测试基础文档处理"""
    print("\n📄 测试基础文档处理...")
    
    try:
        # 创建测试文本文件
        test_file = Path("test_doc.txt")
        test_content = "这是一个测试文档。包含一些测试内容用于验证文档处理功能。"
        
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        from document.document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        
        # 测试文本文件处理
        text = processor.extract_text(test_file)
        print(f"✅ 文档读取成功，长度: {len(text)} 字符")
        
        # 测试文本分块
        chunks = processor.chunk_text(text, chunk_size=10, overlap=2)
        print(f"✅ 文本分块成功，块数: {len(chunks)}")
        
        # 清理测试文件
        test_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ 文档处理测试失败: {e}")
        return False

def test_streamlit_import():
    """测试Streamlit导入"""
    print("\n🌐 测试Streamlit导入...")
    
    try:
        import streamlit as st
        print("✅ Streamlit导入成功")
        return True
        
    except Exception as e:
        print(f"❌ Streamlit导入失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始RAG系统简单测试\n")
    
    tests = [
        ("配置", test_config),
        ("数据库", test_database),
        ("记忆管理", test_memory),
        ("基础文档处理", test_document_basic),
        ("Streamlit导入", test_streamlit_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {name} 测试通过")
            else:
                print(f"❌ {name} 测试失败")
        except Exception as e:
            print(f"❌ {name} 测试异常: {e}")
        
        print("-" * 50)
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed >= 3:  # 至少通过3个核心测试
        print("🎉 核心功能测试通过！可以尝试启动系统")
        return True
    else:
        print("⚠️  核心测试失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)