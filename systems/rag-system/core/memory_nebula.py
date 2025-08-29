"""
🌌 记忆星图 (Memory Nebula)
===========================

实现"大宪章"第二章：知识的"连接"
- 关系提取流程
- 知识图谱构建
- 记忆星图管理

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Genesis" Chapter 2
"""

import json
import networkx as nx
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import sqlite3
from pathlib import Path

from utils.logger import logger
from config import StorageConfig

@dataclass
class KnowledgeTriplet:
    """知识三元组"""
    subject: str          # 主语
    relation: str         # 关系
    object: str          # 宾语
    sentence_index: int   # 句子索引
    sentence_content: str # 句子内容
    document_id: str     # 文档ID
    paragraph_id: str    # 段落ID
    confidence: float    # 置信度
    source: str          # 来源
    created_at: str      # 创建时间
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "subject": self.subject,
            "relation": self.relation,
            "object": self.object,
            "sentence_index": self.sentence_index,
            "sentence_content": self.sentence_content,
            "document_id": self.document_id,
            "paragraph_id": self.paragraph_id,
            "confidence": self.confidence,
            "source": self.source,
            "created_at": self.created_at
        }
    
    def get_triplet_id(self) -> str:
        """生成三元组唯一ID"""
        triplet_str = f"{self.subject}|{self.relation}|{self.object}"
        return hashlib.md5(triplet_str.encode()).hexdigest()

class RelationExtractor:
    """关系提取器 - 生物信息关系提取官"""
    
    def __init__(self, llm_manager=None):
        self.llm_manager = llm_manager
        logger.info("🔬 关系提取器已初始化")
    
    def _build_extraction_prompt(self, sentence_list: List[str]) -> str:
        """构建关系提取的提示词"""
        sentences_json = []
        for i, sentence in enumerate(sentence_list):
            sentences_json.append({
                "index": i,
                "content": sentence.strip()
            })
        
        prompt = f"""你是一名'生物信息关系提取官'。你的任务，是从我下面，提供给你的这个'句子列表'中，为每一个句子，都，提取出所有可能的'知识三元组 (主语, 关系, 宾语)'。

请，以一个'JSON数组'的格式，返回你的结果。数组的每一个元素，都应该，对应一个句子，并包含'句子索引'和它所对应的'三元组列表'。

输入句子列表：
{json.dumps(sentences_json, ensure_ascii=False, indent=2)}

请严格按照以下JSON格式返回结果：
[
  {{
    "sentence_index": 0,
    "sentence_content": "句子内容",
    "triplets": [
      {{
        "subject": "主语",
        "relation": "关系",
        "object": "宾语",
        "confidence": 0.95
      }}
    ]
  }}
]

注意事项：
1. 每个句子至少提取1个三元组，最多提取5个
2. 主语和宾语应该是具体的实体或概念
3. 关系应该是动词或动词短语
4. confidence表示提取的置信度(0-1之间)
5. 只返回JSON，不要其他解释文字"""

        return prompt
    
    def extract_relations_from_paragraph(self, sentence_list: List[str], 
                                       document_id: str, paragraph_id: str) -> List[KnowledgeTriplet]:
        """从段落的句子列表中提取关系"""
        try:
            if not sentence_list:
                logger.warning("句子列表为空，跳过关系提取")
                return []
            
            logger.info(f"开始提取段落 {paragraph_id} 的关系，包含 {len(sentence_list)} 个句子")
            
            # 构建提示词
            prompt = self._build_extraction_prompt(sentence_list)
            
            # 调用LLM进行关系提取
            if self.llm_manager:
                try:
                    response = self.llm_manager.generate_response(prompt)
                    logger.debug(f"LLM响应: {response[:200]}...")
                    
                    # 解析JSON响应
                    triplets = self._parse_extraction_response(
                        response, sentence_list, document_id, paragraph_id
                    )
                    
                    logger.info(f"成功提取 {len(triplets)} 个知识三元组")
                    return triplets
                    
                except Exception as e:
                    logger.error(f"LLM关系提取失败: {e}")
                    return self._fallback_extraction(sentence_list, document_id, paragraph_id)
            else:
                logger.warning("LLM管理器未配置，使用备用提取方法")
                return self._fallback_extraction(sentence_list, document_id, paragraph_id)
                
        except Exception as e:
            logger.error(f"关系提取失败: {e}")
            return []
    
    def _parse_extraction_response(self, response: str, sentence_list: List[str],
                                 document_id: str, paragraph_id: str) -> List[KnowledgeTriplet]:
        """解析LLM的提取响应"""
        try:
            # 尝试提取JSON部分
            response = response.strip()
            
            # 查找JSON数组的开始和结束
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("响应中未找到JSON数组")
            
            json_str = response[start_idx:end_idx]
            extraction_results = json.loads(json_str)
            
            triplets = []
            current_time = datetime.now().isoformat()
            
            for result in extraction_results:
                sentence_index = result.get("sentence_index", 0)
                sentence_content = result.get("sentence_content", "")
                
                # 确保句子内容正确
                if sentence_index < len(sentence_list):
                    sentence_content = sentence_list[sentence_index]
                
                for triplet_data in result.get("triplets", []):
                    triplet = KnowledgeTriplet(
                        subject=triplet_data.get("subject", "").strip(),
                        relation=triplet_data.get("relation", "").strip(),
                        object=triplet_data.get("object", "").strip(),
                        sentence_index=sentence_index,
                        sentence_content=sentence_content,
                        document_id=document_id,
                        paragraph_id=paragraph_id,
                        confidence=float(triplet_data.get("confidence", 0.8)),
                        source="llm_extraction",
                        created_at=current_time
                    )
                    
                    # 验证三元组的有效性
                    if triplet.subject and triplet.relation and triplet.object:
                        triplets.append(triplet)
            
            return triplets
            
        except Exception as e:
            logger.error(f"解析提取响应失败: {e}")
            return self._fallback_extraction(sentence_list, document_id, paragraph_id)
    
    def _fallback_extraction(self, sentence_list: List[str], 
                           document_id: str, paragraph_id: str) -> List[KnowledgeTriplet]:
        """备用关系提取方法（基于规则）"""
        try:
            logger.info("使用备用关系提取方法")
            triplets = []
            current_time = datetime.now().isoformat()
            
            # 简单的规则提取（示例）
            for i, sentence in enumerate(sentence_list):
                sentence = sentence.strip()
                if len(sentence) > 10:  # 只处理有意义的句子
                    words = sentence.split()
                    if len(words) >= 3:
                        # 简单的规则：寻找常见的关系词
                        relation_words = ["是", "包含", "属于", "使用", "应用", "研究", "发展", "提升", "推动"]
                        
                        found_relation = None
                        relation_index = -1
                        
                        for j, word in enumerate(words):
                            if any(rel in word for rel in relation_words):
                                found_relation = word
                                relation_index = j
                                break
                        
                        if found_relation and relation_index > 0 and relation_index < len(words) - 1:
                            # 提取主语（关系词前的词）
                            subject_words = words[:relation_index]
                            subject = "".join(subject_words) if subject_words else words[0]
                            
                            # 提取宾语（关系词后的词）
                            object_words = words[relation_index + 1:]
                            obj = "".join(object_words) if object_words else words[-1]
                            
                            # 清理标点符号
                            subject = subject.rstrip('，。！？；：')
                            obj = obj.rstrip('，。！？；：')
                            
                            if subject and obj and subject != obj:
                                triplet = KnowledgeTriplet(
                                    subject=subject,
                                    relation=found_relation,
                                    object=obj,
                                    sentence_index=i,
                                    sentence_content=sentence,
                                    document_id=document_id,
                                    paragraph_id=paragraph_id,
                                    confidence=0.6,  # 中等置信度
                                    source="rule_based",
                                    created_at=current_time
                                )
                                triplets.append(triplet)
                        else:
                            # 如果没有找到关系词，使用简单的主谓宾结构
                            if len(words) >= 3:
                                triplet = KnowledgeTriplet(
                                    subject=words[0].rstrip('，。！？；：'),
                                    relation="相关于",
                                    object=words[-1].rstrip('，。！？；：'),
                                    sentence_index=i,
                                    sentence_content=sentence,
                                    document_id=document_id,
                                    paragraph_id=paragraph_id,
                                    confidence=0.4,  # 较低的置信度
                                    source="rule_based",
                                    created_at=current_time
                                )
                                triplets.append(triplet)
            
            logger.info(f"备用方法提取了 {len(triplets)} 个三元组")
            return triplets
            
        except Exception as e:
            logger.error(f"备用关系提取失败: {e}")
            return []

class KnowledgeGraph:
    """知识图谱管理器"""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()  # 支持多重边的有向图
        self.triplet_storage = TripletStorage()
        logger.info("🌐 知识图谱管理器已初始化")
    
    def add_triplets(self, triplets: List[KnowledgeTriplet]) -> Dict[str, Any]:
        """添加知识三元组到图谱"""
        try:
            if not triplets:
                return {"added": 0, "updated": 0, "total_nodes": 0, "total_edges": 0}
            
            added_count = 0
            updated_count = 0
            
            for triplet in triplets:
                # 存储到数据库
                stored = self.triplet_storage.store_triplet(triplet)
                
                if stored:
                    # 添加到NetworkX图
                    self._add_triplet_to_graph(triplet)
                    added_count += 1
                else:
                    # 更新权重
                    self._update_triplet_weight(triplet)
                    updated_count += 1
            
            stats = {
                "added": added_count,
                "updated": updated_count,
                "total_nodes": self.graph.number_of_nodes(),
                "total_edges": self.graph.number_of_edges()
            }
            
            logger.info(f"图谱更新完成: 新增 {added_count}, 更新 {updated_count}")
            return stats
            
        except Exception as e:
            logger.error(f"添加三元组到图谱失败: {e}")
            return {"error": str(e)}
    
    def _add_triplet_to_graph(self, triplet: KnowledgeTriplet):
        """将三元组添加到NetworkX图"""
        try:
            # 添加节点（如果不存在）
            if not self.graph.has_node(triplet.subject):
                self.graph.add_node(triplet.subject, type="entity")
            
            if not self.graph.has_node(triplet.object):
                self.graph.add_node(triplet.object, type="entity")
            
            # 添加边
            edge_data = {
                "relation": triplet.relation,
                "weight": 1.0,
                "confidence": triplet.confidence,
                "sources": [triplet.source],
                "documents": [triplet.document_id],
                "created_at": triplet.created_at,
                "triplet_id": triplet.get_triplet_id()
            }
            
            self.graph.add_edge(triplet.subject, triplet.object, **edge_data)
            
        except Exception as e:
            logger.error(f"添加三元组到图失败: {e}")
    
    def _update_triplet_weight(self, triplet: KnowledgeTriplet):
        """更新已存在三元组的权重"""
        try:
            # 查找现有边
            if self.graph.has_edge(triplet.subject, triplet.object):
                edges = self.graph[triplet.subject][triplet.object]
                
                # 查找相同关系的边
                for key, edge_data in edges.items():
                    if edge_data.get("relation") == triplet.relation:
                        # 增加权重
                        edge_data["weight"] = edge_data.get("weight", 1.0) + 1.0
                        
                        # 添加新的来源
                        sources = edge_data.get("sources", [])
                        if triplet.source not in sources:
                            sources.append(triplet.source)
                        edge_data["sources"] = sources
                        
                        # 添加新的文档
                        documents = edge_data.get("documents", [])
                        if triplet.document_id not in documents:
                            documents.append(triplet.document_id)
                        edge_data["documents"] = documents
                        
                        logger.debug(f"更新三元组权重: {triplet.subject} -> {triplet.object}")
                        break
                        
        except Exception as e:
            logger.error(f"更新三元组权重失败: {e}")
    
    def find_related_entities(self, entity: str, max_depth: int = 2) -> Dict[str, Any]:
        """查找与实体相关的其他实体"""
        try:
            if not self.graph.has_node(entity):
                return {"entity": entity, "related": [], "paths": []}
            
            # 使用BFS查找相关实体
            related_entities = []
            visited = set()
            queue = [(entity, 0, [])]  # (节点, 深度, 路径)
            
            while queue:
                current_entity, depth, path = queue.pop(0)
                
                if current_entity in visited or depth > max_depth:
                    continue
                
                visited.add(current_entity)
                
                if current_entity != entity:
                    related_entities.append({
                        "entity": current_entity,
                        "depth": depth,
                        "path": path + [current_entity]
                    })
                
                # 添加邻居节点
                if depth < max_depth:
                    for neighbor in self.graph.neighbors(current_entity):
                        if neighbor not in visited:
                            queue.append((neighbor, depth + 1, path + [current_entity]))
            
            return {
                "entity": entity,
                "related": related_entities[:20],  # 限制返回数量
                "total_found": len(related_entities)
            }
            
        except Exception as e:
            logger.error(f"查找相关实体失败: {e}")
            return {"entity": entity, "error": str(e)}
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """获取图谱统计信息"""
        try:
            stats = {
                "total_nodes": self.graph.number_of_nodes(),
                "total_edges": self.graph.number_of_edges(),
                "density": nx.density(self.graph),
                "is_connected": nx.is_weakly_connected(self.graph) if self.graph.number_of_nodes() > 0 else False
            }
            
            # 获取度数统计
            if self.graph.number_of_nodes() > 0:
                degrees = dict(self.graph.degree())
                stats["avg_degree"] = sum(degrees.values()) / len(degrees)
                stats["max_degree"] = max(degrees.values()) if degrees else 0
                stats["min_degree"] = min(degrees.values()) if degrees else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"获取图谱统计失败: {e}")
            return {"error": str(e)}

class TripletStorage:
    """三元组存储管理器"""
    
    def __init__(self):
        self.db_path = StorageConfig.MODELS_DATA_DIR / "knowledge_graph.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        logger.info("💾 三元组存储管理器已初始化")
    
    def _init_database(self):
        """初始化数据库表"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # 创建三元组表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_triplets (
                    triplet_id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    object TEXT NOT NULL,
                    sentence_index INTEGER,
                    sentence_content TEXT,
                    document_id TEXT,
                    paragraph_id TEXT,
                    confidence REAL,
                    source TEXT,
                    weight REAL DEFAULT 1.0,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_subject ON knowledge_triplets (subject)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_object ON knowledge_triplets (object)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_relation ON knowledge_triplets (relation)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_document ON knowledge_triplets (document_id)")
            
            conn.commit()
            conn.close()
            
            logger.info("三元组数据库表创建完成")
            
        except Exception as e:
            logger.error(f"初始化三元组数据库失败: {e}")
            raise
    
    def store_triplet(self, triplet: KnowledgeTriplet) -> bool:
        """存储三元组"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            triplet_id = triplet.get_triplet_id()
            current_time = datetime.now().isoformat()
            
            # 检查是否已存在
            cursor.execute("SELECT weight FROM knowledge_triplets WHERE triplet_id = ?", (triplet_id,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新权重
                new_weight = existing[0] + 1.0
                cursor.execute("""
                    UPDATE knowledge_triplets 
                    SET weight = ?, updated_at = ?
                    WHERE triplet_id = ?
                """, (new_weight, current_time, triplet_id))
                
                conn.commit()
                conn.close()
                return False  # 表示更新而非新增
            else:
                # 插入新记录
                cursor.execute("""
                    INSERT INTO knowledge_triplets 
                    (triplet_id, subject, relation, object, sentence_index, sentence_content,
                     document_id, paragraph_id, confidence, source, weight, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    triplet_id, triplet.subject, triplet.relation, triplet.object,
                    triplet.sentence_index, triplet.sentence_content, triplet.document_id,
                    triplet.paragraph_id, triplet.confidence, triplet.source, 1.0,
                    triplet.created_at, current_time
                ))
                
                conn.commit()
                conn.close()
                return True  # 表示新增
                
        except Exception as e:
            logger.error(f"存储三元组失败: {e}")
            return False
    
    def get_triplets_by_document(self, document_id: str) -> List[Dict[str, Any]]:
        """获取文档的所有三元组"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM knowledge_triplets 
                WHERE document_id = ?
                ORDER BY weight DESC
            """, (document_id,))
            
            columns = [desc[0] for desc in cursor.description]
            triplets = []
            
            for row in cursor.fetchall():
                triplet_dict = dict(zip(columns, row))
                triplets.append(triplet_dict)
            
            conn.close()
            return triplets
            
        except Exception as e:
            logger.error(f"获取文档三元组失败: {e}")
            return []

class MemoryNebula:
    """记忆星图主控制器"""
    
    def __init__(self, llm_manager=None):
        self.relation_extractor = RelationExtractor(llm_manager)
        self.knowledge_graph = KnowledgeGraph()
        logger.info("🌌 记忆星图已启动")
    
    def process_paragraph_relations(self, knowledge_atoms: List, document_id: str) -> Dict[str, Any]:
        """处理段落关系提取"""
        try:
            logger.info(f"开始处理文档 {document_id} 的关系提取")
            
            # 按段落分组知识原子
            paragraph_groups = {}
            for atom in knowledge_atoms:
                para_id = atom.paragraph_id
                if para_id not in paragraph_groups:
                    paragraph_groups[para_id] = []
                paragraph_groups[para_id].append(atom)
            
            total_triplets = []
            processed_paragraphs = 0
            
            # 处理每个段落
            for para_id, atoms in paragraph_groups.items():
                logger.info(f"处理段落 {para_id}，包含 {len(atoms)} 个知识原子")
                
                # 提取句子列表
                sentence_list = [atom.content for atom in atoms]
                
                # 提取关系
                triplets = self.relation_extractor.extract_relations_from_paragraph(
                    sentence_list, document_id, para_id
                )
                
                if triplets:
                    # 添加到知识图谱
                    graph_stats = self.knowledge_graph.add_triplets(triplets)
                    total_triplets.extend(triplets)
                    
                    logger.info(f"段落 {para_id} 提取了 {len(triplets)} 个三元组")
                
                processed_paragraphs += 1
            
            result = {
                "success": True,
                "document_id": document_id,
                "processed_paragraphs": processed_paragraphs,
                "total_triplets": len(total_triplets),
                "graph_stats": self.knowledge_graph.get_graph_stats(),
                "processing_time": datetime.now().isoformat()
            }
            
            logger.info(f"文档 {document_id} 关系提取完成: {len(total_triplets)} 个三元组")
            return result
            
        except Exception as e:
            logger.error(f"处理段落关系失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id
            }
    
    def query_related_knowledge(self, entity: str, max_depth: int = 2) -> Dict[str, Any]:
        """查询相关知识"""
        try:
            logger.info(f"查询实体 '{entity}' 的相关知识")
            
            related_info = self.knowledge_graph.find_related_entities(entity, max_depth)
            
            return {
                "success": True,
                "query_entity": entity,
                "related_entities": related_info.get("related", []),
                "total_found": related_info.get("total_found", 0),
                "query_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"查询相关知识失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "query_entity": entity
            }
    
    def get_nebula_status(self) -> Dict[str, Any]:
        """获取记忆星图状态"""
        try:
            graph_stats = self.knowledge_graph.get_graph_stats()
            
            return {
                "status": "operational",
                "nebula_version": "2.0.0-Genesis-Chapter2",
                "capabilities": [
                    "关系提取",
                    "知识图谱构建",
                    "实体关联查询",
                    "权重管理"
                ],
                "graph_statistics": graph_stats,
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取记忆星图状态失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }