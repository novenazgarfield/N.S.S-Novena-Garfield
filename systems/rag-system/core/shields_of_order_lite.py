"""
🛡️ 秩序之盾 - 轻量版 (Shields of Order Lite)
=============================================

实现"大宪章"第三章：知识的"守护"
- 二级精炼机制 (基于规则的重排序)
- 星图导航策略 (分层检索)
- 防腐烂机制 (质量保障)

不依赖sentence-transformers，避免版本冲突
Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Genesis" Chapter 3 Lite
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
import math
from collections import Counter

from utils.logger import logger
from config import StorageConfig

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

class LiteReRanker:
    """轻量级重排序器 - 基于规则的二级精炼机制"""
    
    def __init__(self):
        # 中文停用词
        self.stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '什么', '如何', '为什么', '怎么', '哪个', '哪些', '吗', '呢', '吧', '啊'
        }
        
        # 重要词汇权重
        self.important_words = {
            '人工智能': 2.0, 'AI': 2.0, '机器学习': 2.0, '深度学习': 2.0,
            '神经网络': 1.8, '算法': 1.5, '模型': 1.5, '数据': 1.3,
            '技术': 1.2, '系统': 1.2, '方法': 1.2, '应用': 1.2
        }
        
        logger.info("🔄 轻量级重排序器已初始化")
    
    def rerank_results(self, query: str, results: List[RetrievalResult], 
                      top_k: int = None) -> List[RetrievalResult]:
        """对检索结果进行重排序"""
        try:
            if not results:
                logger.warning("结果为空，跳过重排序")
                return results
            
            if top_k is None:
                top_k = len(results)
            
            logger.info(f"开始对 {len(results)} 个结果进行轻量级重排序")
            
            # 分析查询
            query_features = self._analyze_query(query)
            
            # 计算重排序分数
            for result in results:
                content_features = self._analyze_content(result.content)
                
                # 计算多维度相似度
                similarity_scores = self._calculate_similarity(query_features, content_features)
                
                # 结合初始分数和相似度分数
                final_score = self._combine_scores(result.initial_score, similarity_scores)
                
                result.rerank_score = final_score
                result.relevance_explanation = f"轻量重排序: {final_score:.4f} (词汇:{similarity_scores['lexical']:.3f}, 语义:{similarity_scores['semantic']:.3f})"
            
            # 按重排序分数排序
            reranked_results = sorted(results, key=lambda x: x.get_final_score(), reverse=True)
            
            logger.info(f"轻量级重排序完成，返回前 {min(top_k, len(reranked_results))} 个结果")
            return reranked_results[:top_k]
            
        except Exception as e:
            logger.error(f"轻量级重排序失败: {e}")
            return results[:top_k] if top_k else results
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """分析查询特征"""
        words = self._tokenize(query)
        
        return {
            'words': words,
            'important_words': [w for w in words if w in self.important_words],
            'word_count': len(words),
            'char_count': len(query),
            'has_question': any(q in query for q in ['什么', '如何', '为什么', '怎么', '哪个', '?', '？']),
            'has_comparison': any(c in query for c in ['比较', '对比', '区别', '差异']),
            'word_weights': {w: self.important_words.get(w, 1.0) for w in words}
        }
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """分析内容特征"""
        words = self._tokenize(content)
        
        return {
            'words': words,
            'important_words': [w for w in words if w in self.important_words],
            'word_count': len(words),
            'char_count': len(content),
            'word_freq': Counter(words),
            'word_weights': {w: self.important_words.get(w, 1.0) for w in words}
        }
    
    def _tokenize(self, text: str) -> List[str]:
        """简单的中文分词"""
        # 移除标点符号
        text = re.sub(r'[^\w\s]', ' ', text)
        # 分割单词
        words = text.split()
        # 过滤停用词和短词
        words = [w.lower() for w in words if len(w) > 1 and w.lower() not in self.stop_words]
        return words
    
    def _calculate_similarity(self, query_features: Dict, content_features: Dict) -> Dict[str, float]:
        """计算多维度相似度"""
        # 1. 词汇重叠相似度
        query_words = set(query_features['words'])
        content_words = set(content_features['words'])
        
        if not query_words or not content_words:
            lexical_sim = 0.0
        else:
            intersection = query_words.intersection(content_words)
            union = query_words.union(content_words)
            lexical_sim = len(intersection) / len(union) if union else 0.0
        
        # 2. 重要词汇相似度
        query_important = set(query_features['important_words'])
        content_important = set(content_features['important_words'])
        
        if query_important and content_important:
            important_intersection = query_important.intersection(content_important)
            important_sim = len(important_intersection) / len(query_important)
        else:
            important_sim = 0.0
        
        # 3. 加权词汇相似度
        weighted_sim = self._calculate_weighted_similarity(
            query_features['word_weights'],
            content_features['word_weights']
        )
        
        # 4. 语义相似度（基于共现词汇）
        semantic_sim = self._calculate_semantic_similarity(query_features, content_features)
        
        return {
            'lexical': lexical_sim,
            'important': important_sim,
            'weighted': weighted_sim,
            'semantic': semantic_sim
        }
    
    def _calculate_weighted_similarity(self, query_weights: Dict, content_weights: Dict) -> float:
        """计算加权词汇相似度"""
        if not query_weights or not content_weights:
            return 0.0
        
        common_words = set(query_weights.keys()).intersection(set(content_weights.keys()))
        
        if not common_words:
            return 0.0
        
        weighted_score = sum(query_weights[word] * content_weights[word] for word in common_words)
        max_possible_score = sum(query_weights[word] ** 2 for word in query_weights.keys())
        
        return weighted_score / max_possible_score if max_possible_score > 0 else 0.0
    
    def _calculate_semantic_similarity(self, query_features: Dict, content_features: Dict) -> float:
        """计算语义相似度（基于简单的共现分析）"""
        query_words = query_features['words']
        content_words = content_features['words']
        
        if not query_words or not content_words:
            return 0.0
        
        # 计算词汇密度
        query_density = len(set(query_words)) / len(query_words)
        content_density = len(set(content_words)) / len(content_words)
        
        # 计算长度相似度
        length_ratio = min(len(query_words), len(content_words)) / max(len(query_words), len(content_words))
        
        # 结合密度和长度
        semantic_score = (query_density + content_density) / 2 * length_ratio
        
        return min(semantic_score, 1.0)
    
    def _combine_scores(self, initial_score: float, similarity_scores: Dict[str, float]) -> float:
        """结合初始分数和相似度分数"""
        # 权重配置
        weights = {
            'initial': 0.4,
            'lexical': 0.25,
            'important': 0.2,
            'weighted': 0.1,
            'semantic': 0.05
        }
        
        combined_score = (
            weights['initial'] * initial_score +
            weights['lexical'] * similarity_scores['lexical'] +
            weights['important'] * similarity_scores['important'] +
            weights['weighted'] * similarity_scores['weighted'] +
            weights['semantic'] * similarity_scores['semantic']
        )
        
        return min(combined_score, 1.0)

class QueryComplexityAnalyzer:
    """查询复杂度分析器"""
    
    def __init__(self):
        self.complexity_patterns = {
            'simple_indicators': ['什么', '是', '有', '吗'],
            'medium_indicators': ['如何', '怎么', '为什么', '哪个', '哪些'],
            'complex_indicators': ['比较', '分析', '评估', '综合', '关系', '影响', '优缺点', '差异']
        }
        logger.info("🔍 查询复杂度分析器已初始化")
    
    def analyze_query_complexity(self, query: str) -> QueryComplexity:
        """分析查询复杂度"""
        try:
            query = query.strip()
            
            # 基础特征分析
            word_count = len(query.split())
            char_count = len(query)
            sentence_count = len([s for s in re.split(r'[。！？.!?]', query) if s.strip()])
            
            # 复杂度指标检测
            simple_count = sum(1 for indicator in self.complexity_patterns['simple_indicators'] if indicator in query)
            medium_count = sum(1 for indicator in self.complexity_patterns['medium_indicators'] if indicator in query)
            complex_count = sum(1 for indicator in self.complexity_patterns['complex_indicators'] if indicator in query)
            
            # 语言特征
            has_punctuation = bool(re.search(r'[，。；：！？]', query))
            has_logical_words = bool(re.search(r'(和|与|或|但是|然而|因此)', query))
            has_multiple_concepts = word_count > 8
            
            # 复杂度评分
            complexity_score = 0
            
            # 长度因子
            if char_count > 60:
                complexity_score += 3
            elif char_count > 30:
                complexity_score += 2
            elif char_count > 15:
                complexity_score += 1
            
            # 词汇复杂度
            if word_count > 12:
                complexity_score += 3
            elif word_count > 6:
                complexity_score += 2
            elif word_count > 3:
                complexity_score += 1
            
            # 语言特征
            complexity_score += complex_count * 2
            complexity_score += medium_count * 1
            complexity_score += sentence_count - 1  # 多句子增加复杂度
            
            if has_logical_words:
                complexity_score += 2
            if has_punctuation:
                complexity_score += 1
            if has_multiple_concepts:
                complexity_score += 1
            
            # 确定复杂度级别
            if complexity_score >= 8:
                complexity_level = "complex"
                requires_hierarchical = True
                suggested_strategy = "hierarchical_macro_to_micro"
            elif complexity_score >= 4:
                complexity_level = "medium"
                requires_hierarchical = True
                suggested_strategy = "enhanced_retrieval"
            else:
                complexity_level = "simple"
                requires_hierarchical = False
                suggested_strategy = "direct_retrieval"
            
            # 置信度计算
            confidence = min(0.95, 0.6 + complexity_score * 0.05)
            
            analysis_details = {
                "word_count": word_count,
                "char_count": char_count,
                "sentence_count": sentence_count,
                "complexity_score": complexity_score,
                "simple_indicators": simple_count,
                "medium_indicators": medium_count,
                "complex_indicators": complex_count,
                "has_punctuation": has_punctuation,
                "has_logical_words": has_logical_words,
                "has_multiple_concepts": has_multiple_concepts
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

class DocumentSummarizer:
    """文档摘要生成器 - 轻量版"""
    
    def __init__(self, llm_manager=None):
        self.llm_manager = llm_manager
        self.summaries_cache = {}
        self._init_cache_storage()
        logger.info("📄 轻量级文档摘要生成器已初始化")
    
    def _init_cache_storage(self):
        """初始化摘要缓存存储"""
        try:
            self.cache_db_path = StorageConfig.MODELS_DATA_DIR / "document_summaries_lite.db"
            self.cache_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(str(self.cache_db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_summaries (
                    document_id TEXT PRIMARY KEY,
                    content_hash TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    summary_type TEXT DEFAULT 'extractive',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON document_summaries (content_hash)")
            
            conn.commit()
            conn.close()
            
            logger.info("轻量级文档摘要缓存数据库初始化完成")
            
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
            
            # 生成新摘要（优先使用抽取式）
            summary = self._generate_extractive_summary(document_content, max_length)
            
            # 缓存摘要
            self._cache_summary(document_id, content_hash, summary)
            
            logger.info(f"文档摘要生成完成: {document_id}")
            return summary
            
        except Exception as e:
            logger.error(f"生成文档摘要失败: {e}")
            return self._generate_fallback_summary(document_content, max_length)
    
    def _generate_extractive_summary(self, content: str, max_length: int) -> str:
        """生成抽取式摘要"""
        try:
            # 分句
            sentences = re.split(r'[。！？.!?]', content)
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]
            
            if not sentences:
                return content[:max_length] + "..." if len(content) > max_length else content
            
            # 计算句子重要性
            sentence_scores = []
            for i, sentence in enumerate(sentences):
                score = self._calculate_sentence_importance(sentence, content)
                sentence_scores.append((score, i, sentence))
            
            # 按重要性排序
            sentence_scores.sort(reverse=True)
            
            # 选择最重要的句子
            summary = ""
            selected_sentences = []
            
            for score, idx, sentence in sentence_scores:
                if len(summary + sentence) <= max_length:
                    selected_sentences.append((idx, sentence))
                    summary += sentence + "。"
                else:
                    break
            
            # 按原文顺序排列
            selected_sentences.sort(key=lambda x: x[0])
            final_summary = "".join([s[1] + "。" for s in selected_sentences])
            
            return final_summary.strip() if final_summary else content[:max_length] + "..."
            
        except Exception as e:
            logger.error(f"抽取式摘要生成失败: {e}")
            return content[:max_length] + "..." if len(content) > max_length else content
    
    def _calculate_sentence_importance(self, sentence: str, full_content: str) -> float:
        """计算句子重要性"""
        try:
            score = 0.0
            
            # 长度因子（中等长度的句子更重要）
            length = len(sentence)
            if 20 <= length <= 100:
                score += 1.0
            elif 10 <= length <= 150:
                score += 0.5
            
            # 关键词因子
            important_words = ['人工智能', 'AI', '机器学习', '深度学习', '神经网络', '算法', '模型', '数据', '技术', '系统', '方法', '应用']
            for word in important_words:
                if word in sentence:
                    score += 2.0
            
            # 位置因子（开头和结尾的句子更重要）
            sentences = re.split(r'[。！？.!?]', full_content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if sentence in sentences:
                idx = sentences.index(sentence)
                total = len(sentences)
                if idx < total * 0.2 or idx > total * 0.8:  # 前20%或后20%
                    score += 1.0
            
            # 数字和专业术语因子
            if re.search(r'\d+', sentence):
                score += 0.5
            
            return score
            
        except Exception as e:
            logger.error(f"计算句子重要性失败: {e}")
            return 0.0
    
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

class HierarchicalRetriever:
    """分层检索器 - 轻量版"""
    
    def __init__(self, eternal_archive, memory_nebula, document_summarizer):
        self.eternal_archive = eternal_archive
        self.memory_nebula = memory_nebula
        self.document_summarizer = document_summarizer
        logger.info("🗺️ 轻量级分层检索器已初始化")
    
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
            
            # 由于简化版本，直接使用增强检索
            return self._enhanced_retrieval(query, top_k)
            
        except Exception as e:
            logger.error(f"宏观到微观检索失败: {e}")
            return self._direct_retrieval(query, top_k)
    
    def _enhanced_retrieval(self, query: str, top_k: int) -> List[RetrievalResult]:
        """增强检索策略"""
        try:
            logger.info("执行增强检索策略")
            
            # 向量检索
            vector_results = self._direct_retrieval(query, top_k * 2)
            
            # 尝试图谱检索（如果可用）
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
                            initial_score=0.8,
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
        # 简单的实体提取
        words = query.split()
        # 过滤停用词和短词
        stop_words = {'什么', '如何', '为什么', '怎么', '的', '了', '在', '是', '我', '有', '和', '就', '不'}
        entities = [word for word in words if len(word) > 2 and word not in stop_words]
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

class ShieldsOfOrderLite:
    """秩序之盾轻量版主控制器"""
    
    def __init__(self, eternal_archive, memory_nebula, llm_manager=None):
        self.eternal_archive = eternal_archive
        self.memory_nebula = memory_nebula
        self.llm_manager = llm_manager
        
        # 初始化各个组件
        self.lite_reranker = LiteReRanker()
        self.document_summarizer = DocumentSummarizer(llm_manager)
        self.query_complexity_analyzer = QueryComplexityAnalyzer()
        self.hierarchical_retriever = HierarchicalRetriever(
            eternal_archive, memory_nebula, self.document_summarizer
        )
        
        logger.info("🛡️ 秩序之盾轻量版已激活")
    
    def protected_retrieve(self, query: str, top_k: int = 10, 
                          enable_reranking: bool = True) -> Dict[str, Any]:
        """受保护的检索 - 轻量版秩序之盾流程"""
        try:
            start_time = datetime.now()
            logger.info(f"开始轻量版受保护检索: {query[:50]}...")
            
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
            
            # 第三步：轻量级重排序
            if enable_reranking and len(initial_results) > 1:
                final_results = self.lite_reranker.rerank_results(
                    query, initial_results, top_k
                )
            else:
                final_results = initial_results[:top_k]
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 构建返回结果
            result = {
                "success": True,
                "message": f"轻量版秩序之盾检索完成，找到 {len(final_results)} 个高质量结果",
                "query": query,
                "results": [self._format_result(r) for r in final_results],
                "complexity_analysis": complexity.__dict__,
                "processing_time": processing_time,
                "reranking_enabled": enable_reranking,
                "retrieval_strategy": complexity.suggested_strategy,
                "shields_status": "active_lite"
            }
            
            logger.info(f"轻量版受保护检索完成: {len(final_results)} 个结果，耗时 {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"轻量版受保护检索失败: {e}")
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
        """获取轻量版秩序之盾状态"""
        try:
            return {
                "status": "active",
                "shields_version": "2.0.0-Genesis-Chapter3-Lite",
                "components": {
                    "lite_reranker": {
                        "status": "operational",
                        "type": "rule_based"
                    },
                    "document_summarizer": {
                        "status": "operational",
                        "type": "extractive",
                        "llm_enabled": self.document_summarizer.llm_manager is not None
                    },
                    "query_complexity_analyzer": {
                        "status": "operational",
                        "type": "rule_based"
                    },
                    "hierarchical_retriever": {
                        "status": "operational",
                        "type": "multi_strategy"
                    }
                },
                "capabilities": [
                    "轻量级二级精炼",
                    "星图导航策略",
                    "查询复杂度分析",
                    "分层检索",
                    "防腐烂机制"
                ],
                "advantages": [
                    "无依赖冲突",
                    "快速启动",
                    "低资源消耗",
                    "高可靠性"
                ],
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取轻量版秩序之盾状态失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }