"""
🛡️ 秩序之盾 (Shields of Order)
===============================

实现"大宪章"第三章：知识的"守护"
- 二级精炼机制 (Re-Ranking)
- 星图导航策略 (Hierarchical Retrieval)
- 防腐烂机制 (Anti-Entropy)

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Genesis" Chapter 3
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import sqlite3
from pathlib import Path
import json
import re

from utils.logger import logger
from config import StorageConfig

from sentence_transformers import SentenceTransformer, CrossEncoder

@dataclass
class RetrievalResult:
    """检索结果数据类"""
    content: str
    metadata: Dict[str, Any]
    initial_score: float
    rerank_score: Optional[float] = None
    retrieval_level: str = "atom"  # atom, paragraph, document
    source_document: str = ""
    relevance_explanation: str = ""
    
    def get_final_score(self) -> float:
        """获取最终评分"""
        return self.rerank_score if self.rerank_score is not None else self.initial_score

@dataclass
class QueryComplexity:
    """查询复杂度分析"""
    complexity_level: str  # simple, medium, complex
    requires_hierarchical: bool
    suggested_strategy: str
    confidence: float
    analysis_details: Dict[str, Any]

class CrossEncoderReRanker:
    """Cross-Encoder重排序器 - 二级精炼机制"""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.cross_encoder = None
        self._load_model()
        logger.info("🔄 Cross-Encoder重排序器已初始化")
    
    def _load_model(self):
        """加载Cross-Encoder模型"""
        try:
            logger.info(f"正在加载Cross-Encoder模型: {self.model_name}")
            self.cross_encoder = CrossEncoder(self.model_name)
            logger.info("Cross-Encoder模型加载成功")
        except Exception as e:
            logger.error(f"Cross-Encoder模型加载失败: {e}")
            # 尝试使用备用模型
            try:
                backup_model = "cross-encoder/ms-marco-TinyBERT-L-2-v2"
                logger.info(f"尝试加载备用模型: {backup_model}")
                self.cross_encoder = CrossEncoder(backup_model)
                self.model_name = backup_model
                logger.info("备用Cross-Encoder模型加载成功")
            except Exception as e2:
                logger.error(f"备用模型也加载失败: {e2}")
                self.cross_encoder = None
    
    def rerank_results(self, query: str, results: List[RetrievalResult], 
                      top_k: int = None) -> List[RetrievalResult]:
        """对检索结果进行重排序"""
        try:
            if not self.cross_encoder or not results:
                logger.warning("Cross-Encoder未加载或结果为空，使用备用重排序方法")
                return self._fallback_rerank(query, results, top_k)
            
            if top_k is None:
                top_k = len(results)
            
            logger.info(f"开始对 {len(results)} 个结果进行Cross-Encoder重排序")
            
            # 准备查询-文档对
            query_doc_pairs = []
            for result in results:
                query_doc_pairs.append([query, result.content])
            
            # 计算Cross-Encoder分数
            rerank_scores = self.cross_encoder.predict(query_doc_pairs)
            
            # 更新结果的重排序分数
            for i, result in enumerate(results):
                result.rerank_score = float(rerank_scores[i])
                result.relevance_explanation = f"Cross-Encoder评分: {result.rerank_score:.4f}"
            
            # 按重排序分数排序
            reranked_results = sorted(results, key=lambda x: x.get_final_score(), reverse=True)
            
            logger.info(f"重排序完成，返回前 {min(top_k, len(reranked_results))} 个结果")
            return reranked_results[:top_k]
            
        except Exception as e:
            logger.error(f"重排序失败: {e}")
            return self._fallback_rerank(query, results, top_k)
    
    def _fallback_rerank(self, query: str, results: List[RetrievalResult], 
                        top_k: int = None) -> List[RetrievalResult]:
        """备用重排序方法（基于简单的文本匹配）"""
        try:
            if top_k is None:
                top_k = len(results)
            
            logger.info("使用备用重排序方法")
            
            query_words = set(query.lower().split())
            
            # 计算简单的匹配分数
            for result in results:
                content_words = set(result.content.lower().split())
                
                # 计算词汇重叠度
                overlap = len(query_words.intersection(content_words))
                total_words = len(query_words.union(content_words))
                
                if total_words > 0:
                    overlap_score = overlap / total_words
                else:
                    overlap_score = 0
                
                # 结合初始分数和重叠分数
                result.rerank_score = (result.initial_score * 0.7) + (overlap_score * 0.3)
                result.relevance_explanation = f"备用重排序: {result.rerank_score:.4f} (词汇重叠: {overlap_score:.3f})"
            
            # 按重排序分数排序
            reranked_results = sorted(results, key=lambda x: x.get_final_score(), reverse=True)
            
            logger.info(f"备用重排序完成，返回前 {min(top_k, len(reranked_results))} 个结果")
            return reranked_results[:top_k]
            
        except Exception as e:
            logger.error(f"备用重排序失败: {e}")
            return results[:top_k] if top_k else results

class DocumentSummarizer:
    """文档摘要生成器"""
    
    def __init__(self, llm_manager=None):
        self.llm_manager = llm_manager
        self.summaries_cache = {}
        self._init_cache_storage()
        logger.info("📄 文档摘要生成器已初始化")
    
    def _init_cache_storage(self):
        """初始化摘要缓存存储"""
        try:
            self.cache_db_path = StorageConfig.MODELS_DATA_DIR / "document_summaries.db"
            self.cache_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(str(self.cache_db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_summaries (
                    document_id TEXT PRIMARY KEY,
                    content_hash TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    summary_type TEXT DEFAULT 'auto',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON document_summaries (content_hash)")
            
            conn.commit()
            conn.close()
            
            logger.info("文档摘要缓存数据库初始化完成")
            
        except Exception as e:
            logger.error(f"初始化摘要缓存失败: {e}")
    
    def generate_document_summary(self, document_content: str, document_id: str, 
                                max_length: int = 200) -> str:
        """生成文档摘要"""
        try:
            # 计算内容哈希
            content_hash = hashlib.md5(document_content.encode()).hexdigest()
            
            # 检查缓存
            cached_summary = self._get_cached_summary(document_id, content_hash)
            if cached_summary:
                logger.debug(f"使用缓存的文档摘要: {document_id}")
                return cached_summary
            
            # 生成新摘要
            if self.llm_manager:
                summary = self._generate_llm_summary(document_content, max_length)
            else:
                summary = self._generate_extractive_summary(document_content, max_length)
            
            # 缓存摘要
            self._cache_summary(document_id, content_hash, summary)
            
            logger.info(f"文档摘要生成完成: {document_id}")
            return summary
            
        except Exception as e:
            logger.error(f"生成文档摘要失败: {e}")
            return self._generate_fallback_summary(document_content, max_length)
    
    def _generate_llm_summary(self, content: str, max_length: int) -> str:
        """使用LLM生成摘要"""
        try:
            prompt = f"""请为以下文档生成一个简洁的摘要，长度不超过{max_length}字：

文档内容：
{content[:2000]}  # 限制输入长度

要求：
1. 提取文档的核心主题和关键信息
2. 保持摘要的完整性和可读性
3. 突出文档的主要观点和结论
4. 使用简洁明了的语言

摘要："""
            
            summary = self.llm_manager.generate_response(prompt)
            
            # 清理和截断摘要
            summary = summary.strip()
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"LLM摘要生成失败: {e}")
            return self._generate_extractive_summary(content, max_length)
    
    def _generate_extractive_summary(self, content: str, max_length: int) -> str:
        """生成抽取式摘要"""
        try:
            # 简单的抽取式摘要：取前几句话
            sentences = re.split(r'[。！？]', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            summary = ""
            for sentence in sentences:
                if len(summary + sentence) <= max_length:
                    summary += sentence + "。"
                else:
                    break
            
            return summary.strip() if summary else content[:max_length] + "..."
            
        except Exception as e:
            logger.error(f"抽取式摘要生成失败: {e}")
            return content[:max_length] + "..."
    
    def _generate_fallback_summary(self, content: str, max_length: int) -> str:
        """生成备用摘要"""
        return content[:max_length] + "..." if len(content) > max_length else content
    
    def _get_cached_summary(self, document_id: str, content_hash: str) -> Optional[str]:
        """获取缓存的摘要"""
        try:
            conn = sqlite3.connect(str(self.cache_db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT summary FROM document_summaries 
                WHERE document_id = ? AND content_hash = ?
            """, (document_id, content_hash))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"获取缓存摘要失败: {e}")
            return None
    
    def _cache_summary(self, document_id: str, content_hash: str, summary: str):
        """缓存摘要"""
        try:
            conn = sqlite3.connect(str(self.cache_db_path))
            cursor = conn.cursor()
            
            current_time = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT OR REPLACE INTO document_summaries 
                (document_id, content_hash, summary, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (document_id, content_hash, summary, current_time, current_time))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"缓存摘要失败: {e}")

class QueryComplexityAnalyzer:
    """查询复杂度分析器"""
    
    def __init__(self):
        self.complexity_patterns = {
            'simple': [
                r'^.{1,20}$',  # 很短的查询
                r'^\w+$',      # 单个词
            ],
            'medium': [
                r'^.{21,50}$',  # 中等长度
                r'\b(什么|如何|为什么|怎么)\b',  # 简单疑问词
            ],
            'complex': [
                r'^.{51,}$',    # 长查询
                r'\b(比较|分析|评估|综合|关系|影响)\b',  # 复杂概念
                r'[，。；：]',   # 包含标点符号
                r'\b(和|与|或|但是|然而|因此)\b',  # 逻辑连接词
            ]
        }
        logger.info("🔍 查询复杂度分析器已初始化")
    
    def analyze_query_complexity(self, query: str) -> QueryComplexity:
        """分析查询复杂度"""
        try:
            query = query.strip()
            
            # 基础特征分析
            word_count = len(query.split())
            char_count = len(query)
            has_punctuation = bool(re.search(r'[，。；：！？]', query))
            has_logical_words = bool(re.search(r'\b(和|与|或|但是|然而|因此|比较|分析)\b', query))
            has_question_words = bool(re.search(r'\b(什么|如何|为什么|怎么|哪个|哪些)\b', query))
            
            # 复杂度评分
            complexity_score = 0
            
            # 长度因子
            if char_count > 50:
                complexity_score += 2
            elif char_count > 20:
                complexity_score += 1
            
            # 词汇复杂度
            if word_count > 10:
                complexity_score += 2
            elif word_count > 5:
                complexity_score += 1
            
            # 语言特征
            if has_logical_words:
                complexity_score += 2
            if has_punctuation:
                complexity_score += 1
            if has_question_words:
                complexity_score += 1
            
            # 确定复杂度级别
            if complexity_score >= 5:
                complexity_level = "complex"
                requires_hierarchical = True
                suggested_strategy = "hierarchical_macro_to_micro"
            elif complexity_score >= 2:
                complexity_level = "medium"
                requires_hierarchical = True
                suggested_strategy = "enhanced_retrieval"
            else:
                complexity_level = "simple"
                requires_hierarchical = False
                suggested_strategy = "direct_retrieval"
            
            # 置信度计算
            confidence = min(0.9, 0.5 + complexity_score * 0.1)
            
            analysis_details = {
                "word_count": word_count,
                "char_count": char_count,
                "complexity_score": complexity_score,
                "has_punctuation": has_punctuation,
                "has_logical_words": has_logical_words,
                "has_question_words": has_question_words
            }
            
            result = QueryComplexity(
                complexity_level=complexity_level,
                requires_hierarchical=requires_hierarchical,
                suggested_strategy=suggested_strategy,
                confidence=confidence,
                analysis_details=analysis_details
            )
            
            logger.info(f"查询复杂度分析完成: {complexity_level} (置信度: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"查询复杂度分析失败: {e}")
            # 返回默认分析结果
            return QueryComplexity(
                complexity_level="medium",
                requires_hierarchical=True,
                suggested_strategy="enhanced_retrieval",
                confidence=0.5,
                analysis_details={"error": str(e)}
            )

class HierarchicalRetriever:
    """分层检索器 - 星图导航策略"""
    
    def __init__(self, eternal_archive, memory_nebula, document_summarizer):
        self.eternal_archive = eternal_archive
        self.memory_nebula = memory_nebula
        self.document_summarizer = document_summarizer
        self.document_summaries = {}
        logger.info("🗺️ 分层检索器已初始化")
    
    def hierarchical_retrieve(self, query: str, complexity: QueryComplexity, 
                            top_k: int = 10) -> List[RetrievalResult]:
        """执行分层检索"""
        try:
            logger.info(f"开始分层检索: {complexity.suggested_strategy}")
            
            if complexity.suggested_strategy == "hierarchical_macro_to_micro":
                return self._macro_to_micro_retrieval(query, top_k)
            elif complexity.suggested_strategy == "enhanced_retrieval":
                return self._enhanced_retrieval(query, top_k)
            else:
                return self._direct_retrieval(query, top_k)
                
        except Exception as e:
            logger.error(f"分层检索失败: {e}")
            return self._direct_retrieval(query, top_k)
    
    def _macro_to_micro_retrieval(self, query: str, top_k: int) -> List[RetrievalResult]:
        """宏观到微观的分层检索"""
        try:
            logger.info("执行宏观到微观检索策略")
            
            # 第一步：文档级检索（宏观层面）
            document_results = self._retrieve_at_document_level(query, top_k * 2)
            
            if not document_results:
                logger.warning("文档级检索无结果，降级到直接检索")
                return self._direct_retrieval(query, top_k)
            
            # 第二步：在高相关性文档内进行微观检索
            micro_results = []
            for doc_result in document_results[:min(5, len(document_results))]:  # 限制文档数量
                doc_id = doc_result.metadata.get('document_id')
                if doc_id:
                    # 在特定文档内检索句子
                    sentence_results = self._retrieve_sentences_in_document(query, doc_id, top_k // 2)
                    micro_results.extend(sentence_results)
            
            # 合并和排序结果
            all_results = document_results + micro_results
            
            # 去重（基于内容）
            unique_results = self._deduplicate_results(all_results)
            
            logger.info(f"宏观到微观检索完成: {len(unique_results)} 个结果")
            return unique_results[:top_k]
            
        except Exception as e:
            logger.error(f"宏观到微观检索失败: {e}")
            return self._direct_retrieval(query, top_k)
    
    def _enhanced_retrieval(self, query: str, top_k: int) -> List[RetrievalResult]:
        """增强检索策略"""
        try:
            logger.info("执行增强检索策略")
            
            # 结合向量检索和图谱检索
            vector_results = self._direct_retrieval(query, top_k)
            
            # 尝试图谱检索
            try:
                graph_results = self._retrieve_from_knowledge_graph(query, top_k // 2)
                all_results = vector_results + graph_results
            except Exception as e:
                logger.warning(f"图谱检索失败: {e}")
                all_results = vector_results
            
            # 去重和排序
            unique_results = self._deduplicate_results(all_results)
            
            logger.info(f"增强检索完成: {len(unique_results)} 个结果")
            return unique_results[:top_k]
            
        except Exception as e:
            logger.error(f"增强检索失败: {e}")
            return self._direct_retrieval(query, top_k)
    
    def _direct_retrieval(self, query: str, top_k: int) -> List[RetrievalResult]:
        """直接检索策略"""
        try:
            logger.info("执行直接检索策略")
            
            # 使用永恒归档进行向量检索
            search_results = self.eternal_archive.search_knowledge_atoms(query, top_k)
            
            results = []
            for result in search_results:
                retrieval_result = RetrievalResult(
                    content=result["content"],
                    metadata=result["metadata"],
                    initial_score=result["similarity_score"],
                    retrieval_level="atom",
                    source_document=result["metadata"].get("document_id", ""),
                    relevance_explanation=f"向量相似度: {result['similarity_score']:.4f}"
                )
                results.append(retrieval_result)
            
            logger.info(f"直接检索完成: {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"直接检索失败: {e}")
            return []
    
    def _retrieve_at_document_level(self, query: str, top_k: int) -> List[RetrievalResult]:
        """文档级检索"""
        try:
            # 获取所有文档的摘要
            document_stats = self.eternal_archive.get_document_stats()
            # 这里需要实现文档级检索逻辑
            # 暂时返回空结果，实际实现需要根据文档摘要进行检索
            return []
            
        except Exception as e:
            logger.error(f"文档级检索失败: {e}")
            return []
    
    def _retrieve_sentences_in_document(self, query: str, document_id: str, top_k: int) -> List[RetrievalResult]:
        """在特定文档内检索句子"""
        try:
            # 使用文档ID过滤检索结果
            search_results = self.eternal_archive.search_knowledge_atoms(query, top_k * 2, document_id)
            
            results = []
            for result in search_results:
                if result["metadata"].get("document_id") == document_id:
                    retrieval_result = RetrievalResult(
                        content=result["content"],
                        metadata=result["metadata"],
                        initial_score=result["similarity_score"],
                        retrieval_level="atom",
                        source_document=document_id,
                        relevance_explanation=f"文档内检索: {result['similarity_score']:.4f}"
                    )
                    results.append(retrieval_result)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"文档内句子检索失败: {e}")
            return []
    
    def _retrieve_from_knowledge_graph(self, query: str, top_k: int) -> List[RetrievalResult]:
        """从知识图谱检索"""
        try:
            # 提取查询中的实体
            entities = self._extract_entities_from_query(query)
            
            results = []
            for entity in entities:
                graph_result = self.memory_nebula.query_related_knowledge(entity, max_depth=2)
                
                if graph_result["success"]:
                    for related in graph_result.get("related_entities", []):
                        retrieval_result = RetrievalResult(
                            content=f"实体关联: {entity} -> {related['entity']}",
                            metadata={"entity": entity, "related_entity": related["entity"]},
                            initial_score=0.8,  # 图谱检索的基础分数
                            retrieval_level="graph",
                            source_document="knowledge_graph",
                            relevance_explanation=f"图谱关联深度: {related['depth']}"
                        )
                        results.append(retrieval_result)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"知识图谱检索失败: {e}")
            return []
    
    def _extract_entities_from_query(self, query: str) -> List[str]:
        """从查询中提取实体"""
        # 简单的实体提取（可以后续优化）
        words = query.split()
        # 过滤停用词和短词
        entities = [word for word in words if len(word) > 2 and word not in ['什么', '如何', '为什么', '怎么']]
        return entities[:3]  # 限制实体数量
    
    def _deduplicate_results(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """去重检索结果"""
        seen_content = set()
        unique_results = []
        
        for result in results:
            content_hash = hashlib.md5(result.content.encode()).hexdigest()
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append(result)
        
        # 按分数排序
        unique_results.sort(key=lambda x: x.get_final_score(), reverse=True)
        return unique_results

class ShieldsOfOrder:
    """秩序之盾主控制器"""
    
    def __init__(self, eternal_archive, memory_nebula, llm_manager=None):
        self.eternal_archive = eternal_archive
        self.memory_nebula = memory_nebula
        self.llm_manager = llm_manager
        
        # 初始化各个组件
        self.cross_encoder_reranker = CrossEncoderReRanker()
        self.document_summarizer = DocumentSummarizer(llm_manager)
        self.query_complexity_analyzer = QueryComplexityAnalyzer()
        self.hierarchical_retriever = HierarchicalRetriever(
            eternal_archive, memory_nebula, self.document_summarizer
        )
        
        logger.info("🛡️ 秩序之盾已激活")
    
    def protected_retrieve(self, query: str, top_k: int = 10, 
                          enable_reranking: bool = True) -> Dict[str, Any]:
        """受保护的检索 - 完整的秩序之盾流程"""
        try:
            start_time = datetime.now()
            logger.info(f"开始受保护检索: {query[:50]}...")
            
            # 第一步：查询复杂度分析
            complexity = self.query_complexity_analyzer.analyze_query_complexity(query)
            
            # 第二步：分层检索（星图导航）
            initial_results = self.hierarchical_retriever.hierarchical_retrieve(
                query, complexity, top_k * 2  # 获取更多结果用于重排序
            )
            
            if not initial_results:
                return {
                    "success": False,
                    "message": "未找到相关结果",
                    "query": query,
                    "results": [],
                    "complexity_analysis": complexity.__dict__
                }
            
            # 第三步：二级精炼（Re-Ranking）
            if enable_reranking and len(initial_results) > 1:
                final_results = self.cross_encoder_reranker.rerank_results(
                    query, initial_results, top_k
                )
            else:
                final_results = initial_results[:top_k]
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 构建返回结果
            result = {
                "success": True,
                "message": f"秩序之盾检索完成，找到 {len(final_results)} 个高质量结果",
                "query": query,
                "results": [self._format_result(r) for r in final_results],
                "complexity_analysis": complexity.__dict__,
                "processing_time": processing_time,
                "reranking_enabled": enable_reranking,
                "retrieval_strategy": complexity.suggested_strategy,
                "shields_status": "active"
            }
            
            logger.info(f"受保护检索完成: {len(final_results)} 个结果，耗时 {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"受保护检索失败: {e}")
            return {
                "success": False,
                "message": f"检索过程中发生错误: {str(e)}",
                "query": query,
                "results": [],
                "error": str(e)
            }
    
    def _format_result(self, result: RetrievalResult) -> Dict[str, Any]:
        """格式化检索结果"""
        return {
            "content": result.content,
            "metadata": result.metadata,
            "initial_score": result.initial_score,
            "rerank_score": result.rerank_score,
            "final_score": result.get_final_score(),
            "retrieval_level": result.retrieval_level,
            "source_document": result.source_document,
            "relevance_explanation": result.relevance_explanation
        }
    
    def get_shields_status(self) -> Dict[str, Any]:
        """获取秩序之盾状态"""
        try:
            return {
                "status": "active",
                "shields_version": "2.0.0-Genesis-Chapter3",
                "components": {
                    "cross_encoder_reranker": {
                        "status": "operational" if self.cross_encoder_reranker.cross_encoder else "offline",
                        "model": self.cross_encoder_reranker.model_name
                    },
                    "document_summarizer": {
                        "status": "operational",
                        "llm_enabled": self.document_summarizer.llm_manager is not None
                    },
                    "query_complexity_analyzer": {
                        "status": "operational"
                    },
                    "hierarchical_retriever": {
                        "status": "operational"
                    }
                },
                "capabilities": [
                    "二级精炼机制",
                    "星图导航策略",
                    "查询复杂度分析",
                    "分层检索",
                    "防腐烂机制"
                ],
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取秩序之盾状态失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }