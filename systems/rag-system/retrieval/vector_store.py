"""
向量存储和检索系统
"""
import numpy as np
import faiss
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer
import pickle
from pathlib import Path

from config import ModelConfig, StorageConfig, DocumentConfig
from utils.logger import logger

class VectorStore:
    """向量存储和检索类"""
    
    def __init__(self):
        self.embedding_model = None
        self.faiss_index = None
        self.chunks = []
        self.index_file = StorageConfig.MODELS_DATA_DIR / "faiss_index.pkl"
        self.chunks_file = StorageConfig.MODELS_DATA_DIR / "chunks.pkl"
        
        # 确保目录存在
        StorageConfig.MODELS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def load_embedding_model(self) -> SentenceTransformer:
        """加载嵌入模型"""
        if self.embedding_model is None:
            try:
                logger.info(f"正在加载嵌入模型: {ModelConfig.EMBEDDING_MODEL_PATH}")
                self.embedding_model = SentenceTransformer(ModelConfig.EMBEDDING_MODEL_PATH)
                logger.info("嵌入模型加载成功")
            except Exception as e:
                logger.error(f"嵌入模型加载失败: {e}")
                # 尝试使用备用模型
                try:
                    logger.info("尝试使用备用模型: all-MiniLM-L6-v2")
                    self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                    logger.info("备用嵌入模型加载成功")
                except Exception as e2:
                    logger.error(f"备用模型也加载失败: {e2}")
                    raise
        
        return self.embedding_model
    
    def create_embeddings(self, texts: List[str], prefix: str = "passage") -> np.ndarray:
        """创建文本嵌入"""
        try:
            model = self.load_embedding_model()
            
            # 添加前缀以提高检索效果
            prefixed_texts = [f"{prefix}: {text}" for text in texts]
            
            logger.info(f"正在创建 {len(texts)} 个文本的嵌入向量...")
            embeddings = model.encode(
                prefixed_texts,
                normalize_embeddings=True,
                show_progress_bar=True,
                batch_size=32  # 控制批次大小以避免内存问题
            ).astype('float32')
            
            logger.info(f"嵌入向量创建完成: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"创建嵌入向量失败: {e}")
            raise
    
    def build_index(self, embeddings: np.ndarray):
        """构建FAISS索引"""
        try:
            dim = embeddings.shape[1]
            logger.info(f"正在构建FAISS索引，维度: {dim}")
            
            # 使用内积索引（适合归一化向量）
            self.faiss_index = faiss.IndexFlatIP(dim)
            self.faiss_index.add(embeddings)
            
            logger.info(f"FAISS索引构建完成，包含 {self.faiss_index.ntotal} 个向量")
            
        except Exception as e:
            logger.error(f"构建FAISS索引失败: {e}")
            raise
    
    def add_documents(self, texts: List[str], chunk_size: int = None, overlap: int = None):
        """添加文档到向量存储"""
        try:
            from document.document_processor import DocumentProcessor
            
            processor = DocumentProcessor()
            
            # 文本分块
            new_chunks = []
            for text in texts:
                chunks = processor.chunk_text(text, chunk_size, overlap)
                new_chunks.extend(chunks)
            
            if not new_chunks:
                logger.warning("没有新的文本块需要添加")
                return
            
            logger.info(f"准备添加 {len(new_chunks)} 个新文本块")
            
            # 创建嵌入向量
            new_embeddings = self.create_embeddings(new_chunks)
            
            # 如果索引不存在，创建新索引
            if self.faiss_index is None:
                self.chunks = new_chunks
                self.build_index(new_embeddings)
            else:
                # 增量添加到现有索引
                self.chunks.extend(new_chunks)
                self.faiss_index.add(new_embeddings)
                logger.info(f"增量添加完成，索引现包含 {self.faiss_index.ntotal} 个向量")
            
            # 保存索引和文本块
            self.save_index()
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            raise
    
    def search(self, query: str, top_k: int = None) -> List[str]:
        """搜索相似文档"""
        try:
            if self.faiss_index is None or self.faiss_index.ntotal == 0:
                logger.warning("FAISS索引为空，无法进行搜索")
                return []
            
            top_k = top_k or DocumentConfig.MAX_RETRIEVED_CHUNKS
            
            # 确保不超过索引中的向量总数
            k = min(top_k, self.faiss_index.ntotal)
            
            # 创建查询向量
            query_embedding = self.create_embeddings([query], prefix="query")
            
            # 搜索
            distances, indices = self.faiss_index.search(query_embedding, k)
            
            # 返回相似文档
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.chunks):
                    results.append(self.chunks[idx])
                    logger.debug(f"检索结果 {i+1}: 相似度 {distances[0][i]:.4f}")
            
            logger.info(f"检索完成，返回 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def save_index(self):
        """保存索引和文本块到文件"""
        try:
            if self.faiss_index is not None:
                # 保存FAISS索引
                faiss.write_index(self.faiss_index, str(self.index_file))
                logger.info(f"FAISS索引已保存到: {self.index_file}")
            
            # 保存文本块
            with open(self.chunks_file, 'wb') as f:
                pickle.dump(self.chunks, f)
            logger.info(f"文本块已保存到: {self.chunks_file}")
            
        except Exception as e:
            logger.error(f"保存索引失败: {e}")
            raise
    
    def load_index(self) -> bool:
        """从文件加载索引和文本块"""
        try:
            # 加载FAISS索引
            if self.index_file.exists():
                self.faiss_index = faiss.read_index(str(self.index_file))
                logger.info(f"FAISS索引已从文件加载: {self.faiss_index.ntotal} 个向量")
            else:
                logger.info("FAISS索引文件不存在")
                return False
            
            # 加载文本块
            if self.chunks_file.exists():
                with open(self.chunks_file, 'rb') as f:
                    self.chunks = pickle.load(f)
                logger.info(f"文本块已从文件加载: {len(self.chunks)} 个块")
            else:
                logger.warning("文本块文件不存在")
                self.chunks = []
            
            return True
            
        except Exception as e:
            logger.error(f"加载索引失败: {e}")
            return False
    
    def clear_index(self):
        """清空索引"""
        try:
            self.faiss_index = None
            self.chunks = []
            
            # 删除文件
            if self.index_file.exists():
                self.index_file.unlink()
            if self.chunks_file.exists():
                self.chunks_file.unlink()
            
            logger.info("索引已清空")
            
        except Exception as e:
            logger.error(f"清空索引失败: {e}")
            raise
    
    def get_stats(self) -> dict:
        """获取索引统计信息"""
        try:
            stats = {
                "total_vectors": self.faiss_index.ntotal if self.faiss_index else 0,
                "total_chunks": len(self.chunks),
                "index_dimension": self.faiss_index.d if self.faiss_index else 0,
                "model_loaded": self.embedding_model is not None
            }
            return stats
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {"error": str(e)}