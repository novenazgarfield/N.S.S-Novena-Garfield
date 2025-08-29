#!/usr/bin/env python3
"""
🧪 中央情报大脑测试套件
======================

测试"大宪章"架构的各个组件功能

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Genesis"
"""

import sys
import os
from pathlib import Path
import tempfile
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_trinity_chunker():
    """测试三位一体分块器"""
    print("🔄 测试三位一体分块器...")
    
    try:
        from core.intelligence_brain import TrinityChunker
        
        chunker = TrinityChunker()
        
        # 测试文档
        test_document = """
        这是第一段的内容。这是第一段的第二句话。
        
        这是第二段的开始。第二段有更多的内容。这是第二段的最后一句。
        
        第三段比较简短。
        """
        
        document_id = "test_doc_001"
        
        # 执行分块
        knowledge_atoms = chunker.trinity_chunk(test_document, document_id)
        
        print(f"✅ 分块成功: 生成了 {len(knowledge_atoms)} 个知识原子")
        
        # 显示前几个原子
        for i, atom in enumerate(knowledge_atoms[:3]):
            print(f"   原子 {i+1}: {atom.content[:50]}...")
            print(f"   元数据: {atom.document_id}/{atom.paragraph_id}/{atom.sentence_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ 三位一体分块器测试失败: {e}")
        return False

def test_document_processor():
    """测试文档处理器"""
    print("📄 测试三位一体文档处理器...")
    
    try:
        from document.trinity_document_processor import TrinityDocumentProcessor
        
        processor = TrinityDocumentProcessor()
        
        # 创建测试文本文件
        test_content = """
        # 测试文档标题
        
        这是一个测试文档的第一段。包含了一些基本的内容。
        
        ## 第二部分
        
        这里是第二部分的内容。有更多的详细信息。
        这一段有多个句子。每个句子都很重要。
        
        ## 结论
        
        这是文档的结论部分。总结了前面的内容。
        """
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name
        
        try:
            # 处理文档
            result = processor.process_document(temp_file_path)
            
            if result["success"]:
                print(f"✅ 文档处理成功")
                print(f"   文件名: {result['filename']}")
                print(f"   内容长度: {len(result['content'])} 字符")
                print(f"   字数统计: {result['metadata']['word_count']} 词")
                return True
            else:
                print(f"❌ 文档处理失败: {result['error']}")
                return False
                
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)
        
    except Exception as e:
        print(f"❌ 文档处理器测试失败: {e}")
        return False

def test_eternal_archive():
    """测试永恒归档系统"""
    print("💾 测试永恒归档系统...")
    
    try:
        from core.intelligence_brain import EternalArchive, KnowledgeAtom
        
        archive = EternalArchive()
        
        # 创建测试知识原子
        test_atoms = [
            KnowledgeAtom(
                content="这是第一个测试知识原子。",
                document_id="test_doc_001",
                paragraph_id="para_0001",
                sentence_id="sent_0001"
            ),
            KnowledgeAtom(
                content="这是第二个测试知识原子，包含不同的内容。",
                document_id="test_doc_001", 
                paragraph_id="para_0001",
                sentence_id="sent_0002"
            ),
            KnowledgeAtom(
                content="第三个知识原子来自不同的段落。",
                document_id="test_doc_001",
                paragraph_id="para_0002", 
                sentence_id="sent_0001"
            )
        ]
        
        # 归档文档信息
        doc_success = archive.archive_document(
            document_id="test_doc_001",
            filename="test_document.txt",
            metadata={"test": True}
        )
        
        if not doc_success:
            print("❌ 文档归档失败")
            return False
        
        # 归档知识原子
        atoms_success = archive.archive_knowledge_atoms(test_atoms)
        
        if not atoms_success:
            print("❌ 知识原子归档失败")
            return False
        
        # 测试搜索
        search_results = archive.search_knowledge_atoms("测试知识原子", top_k=2)
        
        if search_results:
            print(f"✅ 永恒归档系统测试成功")
            print(f"   归档了 {len(test_atoms)} 个知识原子")
            print(f"   搜索返回 {len(search_results)} 个结果")
            return True
        else:
            print("❌ 搜索功能失败")
            return False
        
    except Exception as e:
        print(f"❌ 永恒归档系统测试失败: {e}")
        return False

def test_intelligence_brain():
    """测试完整的中央情报大脑"""
    print("🧠 测试中央情报大脑...")
    
    try:
        from core.intelligence_brain import IntelligenceBrain
        
        brain = IntelligenceBrain()
        
        # 测试文档摄取
        test_content = """
        人工智能是计算机科学的一个分支。它致力于创建能够执行通常需要人类智能的任务的系统。
        
        机器学习是人工智能的一个子领域。它使用算法和统计模型来让计算机系统能够从数据中学习。
        
        深度学习是机器学习的一个分支。它使用人工神经网络来模拟人脑的学习过程。
        """
        
        # 摄取文档
        ingestion_result = brain.ingest_document(
            document_content=test_content,
            filename="ai_introduction.txt",
            metadata={"topic": "artificial_intelligence"}
        )
        
        if not ingestion_result["success"]:
            print(f"❌ 文档摄取失败: {ingestion_result['message']}")
            return False
        
        print(f"✅ 文档摄取成功: {ingestion_result['knowledge_atoms_count']} 个知识原子")
        
        # 测试智能查询
        query_result = brain.query_intelligence("什么是机器学习？", top_k=3)
        
        if query_result["success"]:
            print(f"✅ 智能查询成功: 找到 {len(query_result['results'])} 个相关原子")
            
            # 显示最相关的结果
            if query_result["results"]:
                best_result = query_result["results"][0]
                print(f"   最佳匹配: {best_result['content'][:50]}...")
                print(f"   相似度: {best_result['similarity_score']:.3f}")
            
            return True
        else:
            print(f"❌ 智能查询失败: {query_result['message']}")
            return False
        
    except Exception as e:
        print(f"❌ 中央情报大脑测试失败: {e}")
        return False

def test_brain_status():
    """测试大脑状态"""
    print("📊 测试大脑状态...")
    
    try:
        from core.intelligence_brain import IntelligenceBrain
        
        brain = IntelligenceBrain()
        status = brain.get_brain_status()
        
        if status["status"] == "operational":
            print("✅ 大脑状态正常")
            print(f"   版本: {status['brain_version']}")
            print(f"   架构: {status['architecture']}")
            print(f"   能力: {', '.join(status['capabilities'])}")
            
            stats = status.get("statistics", {})
            print(f"   文档数: {stats.get('total_documents', 0)}")
            print(f"   知识原子数: {stats.get('total_knowledge_atoms', 0)}")
            
            return True
        else:
            print(f"❌ 大脑状态异常: {status.get('error', '未知错误')}")
            return False
        
    except Exception as e:
        print(f"❌ 大脑状态测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 中央情报大脑测试套件")
    print("=" * 50)
    print("基于'大宪章'的新一代RAG系统测试")
    print("版本: 2.0.0 - Genesis")
    print("=" * 50)
    
    # 测试列表
    tests = [
        ("三位一体分块器", test_trinity_chunker),
        ("文档处理器", test_document_processor),
        ("永恒归档系统", test_eternal_archive),
        ("中央情报大脑", test_intelligence_brain),
        ("大脑状态", test_brain_status)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 运行测试: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                failed += 1
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} 测试异常: {e}")
    
    # 测试总结
    print("\n" + "=" * 50)
    print("🏁 测试总结")
    print("=" * 50)
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📊 总计: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 所有测试通过！中央情报大脑运行正常！")
        return 0
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败，请检查系统配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())