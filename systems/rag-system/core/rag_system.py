"""
RAG系统核心逻辑
"""
from typing import List, Dict, Any
import os
from pathlib import Path

from config import StorageConfig, DocumentConfig, init_config
from utils.logger import logger
from database.chat_db import ChatDatabase
from memory.memory_manager import MemoryManager
from document.document_processor import DocumentProcessor
from retrieval.vector_store import VectorStore
from llm.llm_manager import LLMManager

class RAGSystem:
    """RAG系统主类"""
    
    def __init__(self):
        # 初始化配置
        init_config()
        
        # 初始化各个组件
        self.chat_db = ChatDatabase()
        self.memory_manager = MemoryManager()
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.llm_manager = LLMManager()
        
        logger.info("RAG系统初始化完成")
    
    def load_local_library(self) -> bool:
        """加载本地文献库"""
        try:
            library_path = StorageConfig.LIBRARY_DIR
            
            if not library_path.exists():
                logger.info(f"本地文献库不存在: {library_path}")
                return False
            
            # 获取所有支持的文件
            supported_files = []
            for ext in DocumentConfig.SUPPORTED_EXTENSIONS:
                supported_files.extend(library_path.glob(f"*{ext}"))
            
            if not supported_files:
                logger.info("本地文献库中没有支持的文件")
                return False
            
            logger.info(f"发现 {len(supported_files)} 个文献文件")
            
            # 处理文件
            texts = self.document_processor.process_files(supported_files)
            
            if texts:
                # 添加到向量存储
                self.vector_store.add_documents(texts)
                logger.info(f"本地文献库加载成功: {len(texts)} 个文档")
                return True
            else:
                logger.warning("本地文献库中没有有效内容")
                return False
                
        except Exception as e:
            logger.error(f"加载本地文献库失败: {e}")
            return False
    
    def add_documents(self, files: List) -> Dict[str, Any]:
        """添加新文档"""
        try:
            logger.info(f"开始处理 {len(files)} 个上传文件")
            
            # 处理文档
            texts = self.document_processor.process_files(files)
            
            if not texts:
                return {
                    "success": False,
                    "message": "没有成功处理的文档",
                    "processed_count": 0
                }
            
            # 添加到向量存储
            self.vector_store.add_documents(texts)
            
            # 获取统计信息
            stats = self.vector_store.get_stats()
            
            return {
                "success": True,
                "message": f"成功处理 {len(texts)} 个文档",
                "processed_count": len(texts),
                "total_chunks": stats.get("total_chunks", 0),
                "total_vectors": stats.get("total_vectors", 0)
            }
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return {
                "success": False,
                "message": f"处理文档时出错: {str(e)}",
                "processed_count": 0
            }
    
    def search_and_answer(self, question: str, task_name: str = "default") -> str:
        """搜索并回答问题"""
        try:
            logger.info(f"处理问题: {question[:50]}...")
            
            # 1. 存储用户问题
            query_embedding = self.vector_store.create_embeddings([question])[0]
            self.chat_db.store_message("user", question, query_embedding, task_name)
            
            # 2. 检索相关信息
            # 加载记忆
            permanent_memories = self.memory_manager.load_permanent_memories()
            temporary_memories = self.memory_manager.load_temporary_memory(task_name)
            
            # 检索相似历史对话
            similar_history = self.chat_db.retrieve_similar_messages(
                query_embedding, 
                top_k=DocumentConfig.MAX_SIMILAR_HISTORY,
                task_name=task_name
            )
            
            # 检索相关文档
            retrieved_chunks = self.vector_store.search(question)
            
            # 3. 构建上下文
            context_parts = []
            
            # 添加记忆内容
            if permanent_memories or temporary_memories or similar_history:
                memory_content = "\n".join(permanent_memories + temporary_memories + similar_history)
                context_parts.append(f"--- 历史记忆和对话 ---\n{memory_content}")
            
            # 添加文档内容
            if retrieved_chunks:
                docs_content = "\n\n".join(retrieved_chunks)
                context_parts.append(f"--- 相关文档内容 ---\n{docs_content}")
            
            context = "\n\n".join(context_parts)
            
            # 4. 生成回答
            if not context.strip():
                answer = "抱歉，我没有找到相关的信息来回答您的问题。请尝试上传相关文档或重新表述问题。"
            else:
                prompt = self.llm_manager.build_prompt(question, context)
                answer = self.llm_manager.generate_response(prompt)
            
            # 5. 存储回答
            answer_embedding = self.vector_store.create_embeddings([answer])[0]
            self.chat_db.store_message("assistant", answer, answer_embedding, task_name)
            
            # 保存到临时记忆
            self.memory_manager.save_temporary_memory(answer, task_name)
            
            logger.info("问答处理完成")
            return answer
            
        except Exception as e:
            logger.error(f"搜索回答失败: {e}")
            return f"抱歉，处理您的问题时出现错误: {str(e)}"
    
    def get_chat_history(self, task_name: str = None, limit: int = 10) -> List[Dict]:
        """获取聊天历史"""
        try:
            messages = self.chat_db.get_recent_messages(limit, task_name)
            
            history = []
            for role, content, timestamp in messages:
                history.append({
                    "role": role,
                    "content": content,
                    "timestamp": timestamp
                })
            
            return history
            
        except Exception as e:
            logger.error(f"获取聊天历史失败: {e}")
            return []
    
    def clear_task_data(self, task_name: str):
        """清除特定任务的所有数据"""
        try:
            # 清除聊天历史
            self.chat_db.clear_task_history(task_name)
            
            # 清除临时记忆
            self.memory_manager.clear_temporary_memory(task_name)
            
            logger.info(f"任务 {task_name} 的数据已清除")
            
        except Exception as e:
            logger.error(f"清除任务数据失败: {e}")
            raise
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        try:
            vector_stats = self.vector_store.get_stats()
            memory_stats = self.memory_manager.get_memory_stats()
            llm_info = self.llm_manager.get_model_info()
            
            return {
                "vector_store": vector_stats,
                "memory": memory_stats,
                "llm": llm_info,
                "database_path": str(StorageConfig.CHAT_DB_PATH),
                "library_path": str(StorageConfig.LIBRARY_DIR)
            }
            
        except Exception as e:
            logger.error(f"获取系统统计失败: {e}")
            return {"error": str(e)}
    
    def initialize_system(self) -> bool:
        """初始化系统（加载模型和索引）"""
        try:
            logger.info("开始初始化RAG系统...")
            
            # 尝试加载已保存的索引
            if self.vector_store.load_index():
                logger.info("已加载保存的向量索引")
            else:
                # 如果没有保存的索引，尝试加载本地文献库
                if self.load_local_library():
                    logger.info("已从本地文献库构建索引")
                else:
                    logger.info("没有可用的文档，等待用户上传")
            
            # 预加载嵌入模型（可选）
            try:
                self.vector_store.load_embedding_model()
                logger.info("嵌入模型预加载成功")
            except Exception as e:
                logger.warning(f"嵌入模型预加载失败: {e}")
            
            logger.info("RAG系统初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"RAG系统初始化失败: {e}")
            return False