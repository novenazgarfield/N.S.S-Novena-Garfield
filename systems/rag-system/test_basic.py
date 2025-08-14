#!/usr/bin/env python3
"""
RAG系统基础功能测试
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """测试基础导入"""
    print("🔍 测试基础导入...")
    
    try:
        from config import init_config, StorageConfig, ModelConfig
        print("✅ 配置模块导入成功")
        
        from utils.logger import logger
        print("✅ 日志模块导入成功")
        
        from database.chat_db import ChatDatabase
        print("✅ 数据库模块导入成功")
        
        from memory.memory_manager import MemoryManager
        print("✅ 记忆管理模块导入成功")
        
        from document.document_processor import DocumentProcessor
        print("✅ 文档处理模块导入成功")
        
        from retrieval.vector_store import VectorStore
        print("✅ 向量存储模块导入成功")
        
        from llm.llm_manager import LLMManager
        print("✅ LLM管理模块导入成功")
        
        from core.rag_system import RAGSystem
        print("✅ RAG核心系统导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_config():
    """测试配置初始化"""
    print("\n🔧 测试配置初始化...")
    
    try:
        from config import init_config, StorageConfig, ModelConfig
        
        init_config()
        print(f"✅ 数据目录: {StorageConfig.DATA_DIR}")
        print(f"✅ 嵌入模型: {ModelConfig.EMBEDDING_MODEL_PATH}")
        print(f"✅ LLM模型: {ModelConfig.LLM_MODEL_PATH}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置初始化失败: {e}")
        return False

def test_document_processing():
    """测试文档处理"""
    print("\n📄 测试文档处理...")
    
    try:
        from document.document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        
        # 测试文本文件处理
        test_file = Path("../../data/raw/rag/library/test_document.txt")
        if test_file.exists():
            text = processor.read_file(str(test_file))
            print(f"✅ 文档读取成功，长度: {len(text)} 字符")
            
            # 测试文本分块
            chunks = processor.chunk_text(text, chunk_size=100, overlap=20)
            print(f"✅ 文本分块成功，块数: {len(chunks)}")
            
            return True
        else:
            print(f"❌ 测试文件不存在: {test_file}")
            return False
            
    except Exception as e:
        print(f"❌ 文档处理失败: {e}")
        return False

def test_vector_store():
    """测试向量存储（不加载模型）"""
    print("\n🔍 测试向量存储...")
    
    try:
        from retrieval.vector_store import VectorStore
        
        vector_store = VectorStore()
        print("✅ 向量存储初始化成功")
        
        # 测试统计信息
        stats = vector_store.get_stats()
        print(f"✅ 统计信息获取成功: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ 向量存储测试失败: {e}")
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
        test_embedding = np.random.rand(384).astype('float32')  # 模拟嵌入向量
        db.store_message("user", "测试问题", test_embedding, "test_task")
        print("✅ 消息存储成功")
        
        # 测试获取消息
        messages = db.get_recent_messages(5, "test_task")
        print(f"✅ 消息获取成功，数量: {len(messages)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_memory_manager():
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
        
        # 测试统计信息
        stats = memory.get_memory_stats()
        print(f"✅ 记忆统计获取成功: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ 记忆管理测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始RAG系统基础功能测试\n")
    
    tests = [
        ("基础导入", test_imports),
        ("配置初始化", test_config),
        ("文档处理", test_document_processing),
        ("向量存储", test_vector_store),
        ("数据库", test_database),
        ("记忆管理", test_memory_manager),
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
    
    if passed == total:
        print("🎉 所有基础功能测试通过！")
        return True
    else:
        print("⚠️  部分测试失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)