"""
🧠 中央情报大脑 (Central Intelligence Brain)
==============================================

按照"大宪章"构建的新一代RAG核心系统
- 拥有长期记忆、深度理解、自我修复与精准控制能力
- 实现"三位一体"智能分块架构
- 支持知识的永恒烙印与自动归档

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Genesis"
"""

import uuid
import sqlite3
import chromadb
import nltk
import spacy
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from datetime import datetime
import json
import hashlib

from config import StorageConfig, DocumentConfig
from utils.logger import logger
from core.memory_nebula import MemoryNebula
from core.shields_of_order import ShieldsOfOrder
from core.fire_control_system import FireControlSystem, SearchScope, AttentionTarget
from core.chronicle_healing import (
    chronicle_self_healing as ai_self_healing, 
    intelligence_brain_self_healing,
    FailureSeverity,
    SystemSource,
    configure_chronicle_healing,
    check_chronicle_federation_health
)

# 确保NLTK数据可用
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class KnowledgeAtom:
    """知识原子 - 句子级别的最小知识单元"""
    
    def __init__(self, content: str, document_id: str, paragraph_id: str, sentence_id: str):
        self.content = content
        self.document_id = document_id
        self.paragraph_id = paragraph_id
        self.sentence_id = sentence_id
        self.atom_id = self._generate_atom_id()
        self.created_at = datetime.now().isoformat()
        
    def _generate_atom_id(self) -> str:
        """生成唯一的原子ID"""
        content_hash = hashlib.md5(self.content.encode()).hexdigest()[:8]
        return f"{self.document_id}_{self.paragraph_id}_{self.sentence_id}_{content_hash}"
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取完整的元数据铭牌"""
        return {
            "atom_id": self.atom_id,
            "document_id": self.document_id,
            "paragraph_id": self.paragraph_id,
            "sentence_id": self.sentence_id,
            "created_at": self.created_at,
            "content_length": len(self.content),
            "content_hash": hashlib.md5(self.content.encode()).hexdigest()
        }

class TrinityChunker:
    """三位一体智能分块器"""
    
    def __init__(self):
        self.nlp = None
        self._load_nlp_model()
    
    def _load_nlp_model(self):
        """加载spaCy模型"""
        try:
            # 尝试加载中文模型
            self.nlp = spacy.load("zh_core_web_sm")
            logger.info("已加载中文spaCy模型")
        except OSError:
            try:
                # 尝试加载英文模型
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("已加载英文spaCy模型")
            except OSError:
                logger.warning("未找到spaCy模型，将使用NLTK进行句子分割")
                self.nlp = None
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """第一层：将文本精准分割为句子原子"""
        try:
            if self.nlp:
                # 使用spaCy进行句子分割
                doc = self.nlp(text)
                sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
            else:
                # 使用NLTK进行句子分割
                sentences = nltk.sent_tokenize(text)
                sentences = [sent.strip() for sent in sentences if sent.strip()]
            
            logger.debug(f"文本分割为 {len(sentences)} 个句子")
            return sentences
            
        except Exception as e:
            logger.error(f"句子分割失败: {e}")
            # 降级处理：按句号分割
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            return sentences
    
    def _group_into_paragraphs(self, text: str) -> List[str]:
        """第二层：根据换行符将句子聚合为段落分子"""
        try:
            # 按双换行符分割段落
            paragraphs = text.split('\n\n')
            # 清理空段落
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            
            # 如果没有双换行符，按单换行符分割
            if len(paragraphs) == 1:
                paragraphs = text.split('\n')
                paragraphs = [p.strip() for p in paragraphs if p.strip()]
            
            logger.debug(f"文本分割为 {len(paragraphs)} 个段落")
            return paragraphs
            
        except Exception as e:
            logger.error(f"段落分割失败: {e}")
            return [text]  # 降级处理：整个文本作为一个段落
    
    def trinity_chunk(self, document_content: str, document_id: str) -> List[KnowledgeAtom]:
        """执行三位一体分块处理"""
        try:
            logger.info(f"开始对文档 {document_id} 执行三位一体分块...")
            
            knowledge_atoms = []
            
            # 第二层：段落分子
            paragraphs = self._group_into_paragraphs(document_content)
            
            for para_idx, paragraph in enumerate(paragraphs):
                paragraph_id = f"para_{para_idx:04d}"
                
                # 第一层：句子原子
                sentences = self._split_into_sentences(paragraph)
                
                for sent_idx, sentence in enumerate(sentences):
                    sentence_id = f"sent_{sent_idx:04d}"
                    
                    # 创建知识原子
                    atom = KnowledgeAtom(
                        content=sentence,
                        document_id=document_id,
                        paragraph_id=paragraph_id,
                        sentence_id=sentence_id
                    )
                    
                    knowledge_atoms.append(atom)
            
            logger.info(f"三位一体分块完成: {len(knowledge_atoms)} 个知识原子")
            return knowledge_atoms
            
        except Exception as e:
            logger.error(f"三位一体分块失败: {e}")
            raise

class EternalArchive:
    """永恒归档系统 - 实现知识的永恒烙印"""
    
    def __init__(self):
        self.chroma_client = None
        self.sqlite_conn = None
        self.vector_collection = None
        self._initialize_storage()
    
    def _initialize_storage(self):
        """初始化持久化存储系统"""
        try:
            # 初始化ChromaDB（向量数据库）
            chroma_path = StorageConfig.MODELS_DATA_DIR / "chroma_db"
            chroma_path.mkdir(parents=True, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(path=str(chroma_path))
            self.vector_collection = self.chroma_client.get_or_create_collection(
                name="knowledge_atoms",
                metadata={"description": "知识原子向量存储"}
            )
            
            # 初始化SQLite（关系型数据库）
            sqlite_path = StorageConfig.MODELS_DATA_DIR / "intelligence_brain.db"
            self.sqlite_conn = sqlite3.connect(str(sqlite_path), check_same_thread=False)
            self._create_tables()
            
            logger.info("永恒归档系统初始化完成")
            
        except Exception as e:
            logger.error(f"永恒归档系统初始化失败: {e}")
            raise
    
    def _create_tables(self):
        """创建SQLite表结构"""
        try:
            cursor = self.sqlite_conn.cursor()
            
            # 文档索引表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_path TEXT,
                    file_size INTEGER,
                    file_hash TEXT,
                    upload_time TEXT NOT NULL,
                    processed_time TEXT NOT NULL,
                    total_atoms INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            # 知识原子索引表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_atoms (
                    atom_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    paragraph_id TEXT NOT NULL,
                    sentence_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    content_length INTEGER,
                    content_hash TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents (document_id)
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_id ON knowledge_atoms (document_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON knowledge_atoms (content_hash)")
            
            self.sqlite_conn.commit()
            logger.info("SQLite表结构创建完成")
            
        except Exception as e:
            logger.error(f"创建SQLite表失败: {e}")
            raise
    
    def archive_document(self, document_id: str, filename: str, file_path: str = None, 
                        file_size: int = None, metadata: Dict = None) -> bool:
        """归档文档信息到关系型数据库"""
        try:
            cursor = self.sqlite_conn.cursor()
            
            # 计算文件哈希（如果有文件路径）
            file_hash = None
            if file_path and Path(file_path).exists():
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
            
            cursor.execute("""
                INSERT OR REPLACE INTO documents 
                (document_id, filename, file_path, file_size, file_hash, upload_time, processed_time, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document_id,
                filename,
                file_path,
                file_size,
                file_hash,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                json.dumps(metadata) if metadata else None
            ))
            
            self.sqlite_conn.commit()
            logger.info(f"文档 {document_id} 已归档到关系型数据库")
            return True
            
        except Exception as e:
            logger.error(f"归档文档失败: {e}")
            return False
    
    def archive_knowledge_atoms(self, knowledge_atoms: List[KnowledgeAtom]) -> bool:
        """归档知识原子到向量数据库和关系型数据库"""
        try:
            if not knowledge_atoms:
                logger.warning("没有知识原子需要归档")
                return False
            
            # 准备数据
            atom_ids = []
            contents = []
            metadatas = []
            
            # SQLite批量插入数据
            cursor = self.sqlite_conn.cursor()
            sqlite_data = []
            
            for atom in knowledge_atoms:
                atom_ids.append(atom.atom_id)
                contents.append(atom.content)
                metadatas.append(atom.get_metadata())
                
                sqlite_data.append((
                    atom.atom_id,
                    atom.document_id,
                    atom.paragraph_id,
                    atom.sentence_id,
                    atom.content,
                    len(atom.content),
                    hashlib.md5(atom.content.encode()).hexdigest(),
                    atom.created_at
                ))
            
            # 归档到ChromaDB（向量数据库）
            self.vector_collection.add(
                ids=atom_ids,
                documents=contents,
                metadatas=metadatas
            )
            
            # 归档到SQLite（关系型数据库）
            cursor.executemany("""
                INSERT OR REPLACE INTO knowledge_atoms 
                (atom_id, document_id, paragraph_id, sentence_id, content, content_length, content_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, sqlite_data)
            
            # 更新文档的原子计数
            document_id = knowledge_atoms[0].document_id
            cursor.execute("""
                UPDATE documents SET total_atoms = (
                    SELECT COUNT(*) FROM knowledge_atoms WHERE document_id = ?
                ) WHERE document_id = ?
            """, (document_id, document_id))
            
            self.sqlite_conn.commit()
            
            logger.info(f"成功归档 {len(knowledge_atoms)} 个知识原子")
            return True
            
        except Exception as e:
            logger.error(f"归档知识原子失败: {e}")
            return False
    
    def search_knowledge_atoms(self, query: str, top_k: int = 10, 
                             document_id: str = None) -> List[Dict[str, Any]]:
        """搜索知识原子"""
        try:
            # 构建查询条件
            where_clause = {}
            if document_id:
                where_clause["document_id"] = document_id
            
            # 在ChromaDB中搜索
            results = self.vector_collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_clause if where_clause else None
            )
            
            # 格式化结果
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    search_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity_score": 1 - distance,  # 转换为相似度分数
                        "rank": i + 1
                    })
            
            logger.info(f"搜索完成，返回 {len(search_results)} 个结果")
            return search_results
            
        except Exception as e:
            logger.error(f"搜索知识原子失败: {e}")
            return []
    
    def get_document_stats(self) -> Dict[str, Any]:
        """获取文档统计信息"""
        try:
            cursor = self.sqlite_conn.cursor()
            
            # 文档统计
            cursor.execute("SELECT COUNT(*) FROM documents")
            total_documents = cursor.fetchone()[0]
            
            # 知识原子统计
            cursor.execute("SELECT COUNT(*) FROM knowledge_atoms")
            total_atoms = cursor.fetchone()[0]
            
            # 向量集合统计
            vector_count = self.vector_collection.count()
            
            return {
                "total_documents": total_documents,
                "total_knowledge_atoms": total_atoms,
                "vector_count": vector_count,
                "storage_status": "operational"
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {"error": str(e)}

class IntelligenceBrain:
    """中央情报大脑 - 主控制器"""
    
    def __init__(self, llm_manager=None):
        self.trinity_chunker = TrinityChunker()
        self.eternal_archive = EternalArchive()
        self.memory_nebula = MemoryNebula(llm_manager)
        self.shields_of_order = ShieldsOfOrder(self.eternal_archive, self.memory_nebula, llm_manager)
        self.fire_control_system = FireControlSystem()
        # 配置Chronicle联邦治疗系统
        configure_chronicle_healing(
            chronicle_url="http://localhost:3000",
            max_retries=3,
            enable_fallback=True,
            default_source=SystemSource.INTELLIGENCE_BRAIN
        )
        logger.info("🧠 中央情报大脑已启动 - 集成记忆星图、秩序之盾、火控系统，连接Chronicle中央医院")
    
    @intelligence_brain_self_healing(severity=FailureSeverity.MEDIUM, max_retries=2)
    def ingest_document(self, document_content: str, filename: str, 
                       file_path: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """摄取文档并执行完整的知识处理流程"""
        try:
            # 生成文档ID
            document_id = f"doc_{uuid.uuid4().hex[:12]}"
            
            logger.info(f"开始摄取文档: {filename} (ID: {document_id})")
            
            # 第一步：三位一体智能分块
            knowledge_atoms = self.trinity_chunker.trinity_chunk(document_content, document_id)
            
            if not knowledge_atoms:
                return {
                    "success": False,
                    "message": "文档分块失败，未生成知识原子",
                    "document_id": document_id
                }
            
            # 第二步：归档文档信息
            doc_archived = self.eternal_archive.archive_document(
                document_id=document_id,
                filename=filename,
                file_path=file_path,
                file_size=len(document_content),
                metadata=metadata
            )
            
            if not doc_archived:
                logger.warning(f"文档 {document_id} 归档失败")
            
            # 第三步：归档知识原子（自动归档）
            atoms_archived = self.eternal_archive.archive_knowledge_atoms(knowledge_atoms)
            
            if not atoms_archived:
                return {
                    "success": False,
                    "message": "知识原子归档失败",
                    "document_id": document_id
                }
            
            # 第四步：构建记忆星图（关系提取和知识图谱构建）
            nebula_result = self.memory_nebula.process_paragraph_relations(knowledge_atoms, document_id)
            
            # 返回处理结果
            result = {
                "success": True,
                "message": f"文档摄取成功！生成了 {len(knowledge_atoms)} 个知识原子",
                "document_id": document_id,
                "filename": filename,
                "knowledge_atoms_count": len(knowledge_atoms),
                "knowledge_triplets_count": nebula_result.get("total_triplets", 0),
                "memory_nebula_stats": nebula_result.get("graph_stats", {}),
                "processing_time": datetime.now().isoformat()
            }
            
            logger.info(f"文档摄取完成: {filename} -> {len(knowledge_atoms)} 个知识原子")
            return result
            
        except Exception as e:
            logger.error(f"文档摄取失败: {e}")
            return {
                "success": False,
                "message": f"文档摄取失败: {str(e)}",
                "document_id": document_id if 'document_id' in locals() else None
            }
    
    def query_intelligence(self, query: str, top_k: int = 10, 
                          document_id: str = None) -> Dict[str, Any]:
        """查询中央情报大脑"""
        try:
            logger.info(f"收到智能查询: {query[:50]}...")
            
            # 搜索相关知识原子
            search_results = self.eternal_archive.search_knowledge_atoms(
                query=query,
                top_k=top_k,
                document_id=document_id
            )
            
            if not search_results:
                return {
                    "success": False,
                    "message": "未找到相关的知识原子",
                    "query": query,
                    "results": []
                }
            
            # 构建智能回答上下文
            context_parts = []
            for result in search_results:
                context_parts.append(f"[相似度: {result['similarity_score']:.3f}] {result['content']}")
            
            context = "\n\n".join(context_parts)
            
            return {
                "success": True,
                "message": f"找到 {len(search_results)} 个相关知识原子",
                "query": query,
                "results": search_results,
                "context": context,
                "query_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"智能查询失败: {e}")
            return {
                "success": False,
                "message": f"查询失败: {str(e)}",
                "query": query,
                "results": []
            }
    
    def query_knowledge_graph(self, entity: str, max_depth: int = 2) -> Dict[str, Any]:
        """基于知识图谱的关联查询"""
        try:
            logger.info(f"执行知识图谱查询: {entity}")
            
            # 使用记忆星图进行关联查询
            nebula_result = self.memory_nebula.query_related_knowledge(entity, max_depth)
            
            if nebula_result["success"]:
                # 同时进行向量检索作为补充
                vector_results = self.eternal_archive.search_knowledge_atoms(entity, top_k=5)
                
                return {
                    "success": True,
                    "query_entity": entity,
                    "graph_relations": nebula_result.get("related_entities", []),
                    "vector_matches": vector_results,
                    "total_graph_relations": nebula_result.get("total_found", 0),
                    "query_time": datetime.now().isoformat()
                }
            else:
                return nebula_result
                
        except Exception as e:
            logger.error(f"知识图谱查询失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "query_entity": entity
            }
    
    def protected_query_intelligence(self, query: str, top_k: int = 10, 
                                   enable_reranking: bool = True) -> Dict[str, Any]:
        """受保护的智能查询 - 使用秩序之盾"""
        try:
            logger.info(f"执行受保护查询: {query[:50]}...")
            
            # 使用秩序之盾进行受保护检索
            shields_result = self.shields_of_order.protected_retrieve(
                query=query,
                top_k=top_k,
                enable_reranking=enable_reranking
            )
            
            if shields_result["success"]:
                return {
                    "success": True,
                    "message": "秩序之盾保护下的查询完成",
                    "query": query,
                    "results": shields_result["results"],
                    "complexity_analysis": shields_result.get("complexity_analysis", {}),
                    "processing_time": shields_result.get("processing_time", 0),
                    "retrieval_strategy": shields_result.get("retrieval_strategy", "unknown"),
                    "reranking_enabled": enable_reranking,
                    "shields_protection": True,
                    "query_time": datetime.now().isoformat()
                }
            else:
                return shields_result
                
        except Exception as e:
            logger.error(f"受保护查询失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "shields_protection": False
            }
    
    @intelligence_brain_self_healing(severity=FailureSeverity.HIGH, max_retries=3)
    def fire_controlled_query(self, query: str, search_scope: str = None, 
                            target_id: str = None, top_k: int = 10,
                            enable_reranking: bool = True) -> Dict[str, Any]:
        """火控系统控制的查询 - AI注意力精确控制"""
        try:
            logger.info(f"🎯 执行火控查询: {query[:50]}... (范围: {search_scope})")
            
            # 设置注意力目标
            if search_scope:
                try:
                    scope_enum = SearchScope(search_scope)
                    target_result = self.fire_control_system.set_attention_target(
                        scope=scope_enum,
                        target_id=target_id
                    )
                    
                    if not target_result["success"]:
                        return target_result
                        
                except ValueError:
                    return {
                        "success": False,
                        "message": f"无效的搜索范围: {search_scope}",
                        "available_scopes": [s["value"] for s in self.fire_control_system.get_available_scopes()]
                    }
            
            # 获取检索策略
            strategy = self.fire_control_system.get_retrieval_strategy(query)
            
            # 根据策略执行检索
            if strategy["scope"] == SearchScope.CURRENT_CHAT.value:
                results = self._execute_chat_retrieval(query, strategy, top_k)
            elif strategy["scope"] == SearchScope.CURRENT_DOCUMENT.value:
                results = self._execute_document_retrieval(query, strategy, top_k)
            elif strategy["scope"] == SearchScope.FULL_DATABASE.value:
                results = self._execute_database_retrieval(query, strategy, top_k, enable_reranking)
            elif strategy["scope"] == SearchScope.GOD_MODE.value:
                results = self._execute_god_mode_retrieval(query, strategy, top_k)
            else:
                # 备用策略
                results = self._execute_database_retrieval(query, strategy, top_k, enable_reranking)
            
            return {
                "success": True,
                "message": f"火控系统查询完成 - 注意力聚焦于{self.fire_control_system._get_scope_description(SearchScope(strategy['scope']))}",
                "query": query,
                "search_scope": strategy["scope"],
                "target_id": target_id,
                "results": results.get("results", []),
                "fire_control_strategy": strategy,
                "processing_time": results.get("processing_time", 0),
                "fire_control_active": True,
                "query_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"火控查询失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "search_scope": search_scope,
                "fire_control_active": False
            }
    
    def _execute_chat_retrieval(self, query: str, strategy: Dict, top_k: int) -> Dict[str, Any]:
        """执行聊天范围检索"""
        try:
            # 从聊天历史中检索
            chat_history = self.fire_control_system.chat_history
            
            if not chat_history:
                return {
                    "results": [],
                    "message": "当前聊天历史为空",
                    "processing_time": 0
                }
            
            # 简单的关键词匹配（可以后续优化为向量搜索）
            query_words = set(query.lower().split())
            scored_messages = []
            
            for msg in chat_history[-strategy["filters"]["limit"]:]:
                content = msg.get("content", "").lower()
                content_words = set(content.split())
                
                # 计算相似度
                overlap = len(query_words.intersection(content_words))
                if overlap > 0:
                    score = overlap / len(query_words.union(content_words))
                    scored_messages.append({
                        "content": msg.get("content", ""),
                        "similarity_score": score,
                        "metadata": {
                            "timestamp": msg.get("timestamp"),
                            "role": msg.get("role"),
                            "source": "chat_history"
                        }
                    })
            
            # 排序并返回前top_k个
            scored_messages.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return {
                "results": scored_messages[:top_k],
                "processing_time": 0.1,
                "total_searched": len(chat_history)
            }
            
        except Exception as e:
            logger.error(f"聊天检索失败: {e}")
            return {"results": [], "error": str(e)}
    
    def _execute_document_retrieval(self, query: str, strategy: Dict, top_k: int) -> Dict[str, Any]:
        """执行文档范围检索"""
        try:
            document_id = strategy.get("target_id")
            if not document_id:
                return {
                    "results": [],
                    "message": "未指定目标文档",
                    "processing_time": 0
                }
            
            # 使用永恒归档进行文档内检索
            # 添加文档ID过滤器
            results = self.eternal_archive.search_knowledge_atoms(
                query, 
                top_k=top_k,
                filters={"document_id": document_id}
            )
            
            return {
                "results": results,
                "processing_time": 0.5,
                "document_id": document_id
            }
            
        except Exception as e:
            logger.error(f"文档检索失败: {e}")
            return {"results": [], "error": str(e)}
    
    def _execute_database_retrieval(self, query: str, strategy: Dict, top_k: int, 
                                  enable_reranking: bool) -> Dict[str, Any]:
        """执行全数据库检索"""
        try:
            if enable_reranking and strategy.get("use_shields"):
                # 使用秩序之盾进行受保护检索
                return self.shields_of_order.protected_retrieve(
                    query=query,
                    top_k=top_k,
                    enable_reranking=enable_reranking
                )
            else:
                # 直接使用永恒归档
                results = self.eternal_archive.search_knowledge_atoms(query, top_k=top_k)
                return {
                    "results": results,
                    "processing_time": 1.0
                }
                
        except Exception as e:
            logger.error(f"数据库检索失败: {e}")
            return {"results": [], "error": str(e)}
    
    def _execute_god_mode_retrieval(self, query: str, strategy: Dict, top_k: int) -> Dict[str, Any]:
        """执行神之档位检索（预留接口）"""
        try:
            logger.info("🔥 神之档位检索 - 当前文档对比全数据库")
            
            # 这是预留的接口，未来实现文档对比全数据库的终极洞察
            return {
                "results": [],
                "message": "神之档位功能正在开发中...",
                "processing_time": 0,
                "god_mode_preview": True,
                "future_capabilities": [
                    "当前文档与全数据库的深度对比分析",
                    "自动发现文档中的独特见解",
                    "跨文档关联性分析",
                    "智能洞察生成"
                ]
            }
            
        except Exception as e:
            logger.error(f"神之档位检索失败: {e}")
            return {"results": [], "error": str(e)}
    
    async def check_chronicle_federation_health(self) -> Dict[str, Any]:
        """检查Chronicle联邦健康状态"""
        try:
            logger.info("🏥 检查Chronicle联邦健康状态...")
            
            # 使用Chronicle联邦健康检查
            health_status = await check_chronicle_federation_health()
            
            return {
                "success": True,
                "message": "Chronicle联邦健康检查完成",
                "federation_status": health_status,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Chronicle联邦健康检查失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "federation_status": "error"
            }
    
    async def get_chronicle_healing_statistics(self) -> Dict[str, Any]:
        """获取Chronicle联邦治疗统计"""
        try:
            from core.chronicle_client import get_chronicle_client
            client = get_chronicle_client()
            health_report = await client.get_health_report(source="intelligence_brain")
            
            return {
                "success": True,
                "message": "Chronicle治疗统计获取成功",
                "healing_statistics": health_report,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"获取Chronicle治疗统计失败: {e}")
            return {"error": str(e), "success": False}
    
    def get_brain_status(self) -> Dict[str, Any]:
        """获取大脑状态"""
        try:
            stats = self.eternal_archive.get_document_stats()
            nebula_status = self.memory_nebula.get_nebula_status()
            shields_status = self.shields_of_order.get_shields_status()
            fire_control_status = self.fire_control_system.get_fire_control_status()
            
            return {
                "status": "operational",
                "brain_version": "2.0.0-Chronicle-Federation",
                "architecture": "Trinity Smart Chunking + Memory Nebula + Shields of Order + Fire Control System + Chronicle Federation",
                "capabilities": [
                    "长期记忆",
                    "深度理解", 
                    "自我修复",
                    "精准控制",
                    "关系提取",
                    "知识图谱构建",
                    "实体关联查询",
                    "二级精炼机制",
                    "星图导航策略",
                    "防腐烂机制",
                    "AI注意力控制",
                    "三段式拨盘",
                    "火控系统",
                    "Chronicle联邦治疗",
                    "中央医院求救",
                    "故障记录委托",
                    "治疗方案获取",
                    "联邦免疫系统"
                ],
                "statistics": stats,
                "memory_nebula": nebula_status,
                "shields_of_order": shields_status,
                "fire_control_system": fire_control_status,
                "chronicle_federation": "connected",
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取大脑状态失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }