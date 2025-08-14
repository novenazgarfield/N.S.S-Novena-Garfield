"""
分布式向量存储管理器
支持3090+4060的分布式计算架构
"""
import numpy as np
import faiss
import torch
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer
import pickle
from pathlib import Path

from config_advanced import ModelConfig, StorageConfig, DocumentConfig, DistributedConfig
from utils.logger import logger

class DistributedVectorStore:
    """分布式向量存储和检索类"""
    
    def __init__(self):
        self.embedding_model = None
        self.faiss_index = None
        self.chunks = []
        self.index_file = StorageConfig.MODELS_DATA_DIR / "faiss_index.pkl"
        self.chunks_file = StorageConfig.MODELS_DATA_DIR / "chunks.pkl"
        
        # 设备配置
        self.embedding_device = ModelConfig.EMBEDDING_DEVICE  # 4060
        self.search_device = DistributedConfig.get_device_for_task("vector_search")  # 4060
        
        # 确保目录存在
        StorageConfig.MODELS_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"向量存储初始化 - 嵌入设备: {self.embedding_device}, 搜索设备: {self.search_device}")
    
    def load_embedding_model(self) -> SentenceTransformer:
        """加载嵌入模型（在4060上运行）"""
        if self.embedding_model is None:
            try:
                logger.info(f"正在加载嵌入模型: {ModelConfig.EMBEDDING_MODEL_PATH}")
                logger.info(f"目标设备: {self.embedding_device}")
                
                # 检查设备可用性
                if self.embedding_device.startswith("cuda"):
                    device_id = int(self.embedding_device.split(":")[-1])
                    if not torch.cuda.is_available() or device_id >= torch.cuda.device_count():
                        logger.warning(f"CUDA设备 {self.embedding_device} 不可用，使用CPU")
                        self.embedding_device = "cpu"
                
                self.embedding_model = SentenceTransformer(
                    ModelConfig.EMBEDDING_MODEL_PATH,
                    device=self.embedding_device
                )
                
                logger.info(f"嵌入模型加载成功，运行在: {self.embedding_device}")
                
            except Exception as e:
                logger.error(f"嵌入模型加载失败: {e}")
                # 尝试使用备用模型
                try:
                    logger.info("尝试使用备用模型: all-MiniLM-L6-v2")
                    self.embedding_model = SentenceTransformer(
                        'all-MiniLM-L6-v2',
                        device=self.embedding_device
                    )
                    logger.info("备用嵌入模型加载成功")
                except Exception as e2:
                    logger.error(f"备用模型也加载失败: {e2}")
                    # 最后尝试CPU
                    try:
                        self.embedding_device = "cpu"
                        self.embedding_model = SentenceTransformer(
                            'all-MiniLM-L6-v2',
                            device="cpu"
                        )
                        logger.info("使用CPU模式加载备用模型成功")
                    except Exception as e3:
                        logger.error(f"所有模型加载尝试都失败: {e3}")
                        raise
        
        return self.embedding_model
    
    def create_embeddings(self, texts: List[str], prefix: str = "passage", batch_size: int = 32) -> np.ndarray:
        """创建文本嵌入（在4060上运行）"""
        try:
            model = self.load_embedding_model()
            
            # 添加前缀以提高检索效果
            prefixed_texts = [f"{prefix}: {text}" for text in texts]
            
            logger.info(f"正在创建 {len(texts)} 个文本的嵌入向量...")
            logger.info(f"使用设备: {self.embedding_device}, 批次大小: {batch_size}")
            
            # 分批处理以避免内存问题
            all_embeddings = []
            for i in range(0, len(prefixed_texts), batch_size):
                batch_texts = prefixed_texts[i:i + batch_size]
                
                with torch.cuda.device(self.embedding_device) if self.embedding_device.startswith("cuda") else torch.no_grad():
                    batch_embeddings = model.encode(
                        batch_texts,
                        normalize_embeddings=True,
                        show_progress_bar=True,
                        batch_size=min(batch_size, len(batch_texts)),
                        convert_to_numpy=True
                    ).astype('float32')
                
                all_embeddings.append(batch_embeddings)
                
                # 清理GPU缓存
                if self.embedding_device.startswith("cuda"):
                    torch.cuda.empty_cache()
            
            embeddings = np.vstack(all_embeddings)
            logger.info(f"嵌入向量创建完成: {embeddings.shape}")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"创建嵌入向量失败: {e}")
            raise
    
    def build_index(self, embeddings: np.ndarray):
        """构建FAISS索引（在4060上运行）"""
        try:
            dim = embeddings.shape[1]
            logger.info(f"正在构建FAISS索引，维度: {dim}")
            
            # 根据数据量选择索引类型
            if len(embeddings) < 10000:
                # 小数据量使用精确搜索
                self.faiss_index = faiss.IndexFlatIP(dim)
            else:
                # 大数据量使用近似搜索
                nlist = min(100, len(embeddings) // 100)  # 聚类中心数
                quantizer = faiss.IndexFlatIP(dim)
                self.faiss_index = faiss.IndexIVFFlat(quantizer, dim, nlist)
                
                # 训练索引
                logger.info("训练FAISS索引...")
                self.faiss_index.train(embeddings)
            
            # 添加向量到索引
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
            
            # 创建嵌入向量（在4060上）
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
        """搜索相似文档（在4060上运行）"""
        try:
            if self.faiss_index is None or self.faiss_index.ntotal == 0:
                logger.warning("FAISS索引为空，无法进行搜索")
                return []
            
            top_k = top_k or DocumentConfig.MAX_RETRIEVED_CHUNKS
            
            # 确保不超过索引中的向量总数
            k = min(top_k, self.faiss_index.ntotal)
            
            # 创建查询向量（在4060上）
            query_embedding = self.create_embeddings([query], prefix="query")
            
            # 搜索
            logger.info(f"在设备 {self.search_device} 上执行向量搜索")
            
            # 如果是IVF索引，设置搜索参数
            if hasattr(self.faiss_index, 'nprobe'):
                self.faiss_index.nprobe = min(10, self.faiss_index.nlist)
            
            distances, indices = self.faiss_index.search(query_embedding, k)
            
            # 返回相似文档
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.chunks) and idx >= 0:  # 确保索引有效
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
            
            # 清理GPU缓存
            if self.embedding_device.startswith("cuda"):
                torch.cuda.empty_cache()
            
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
                "model_loaded": self.embedding_model is not None,
                "embedding_device": self.embedding_device,
                "search_device": self.search_device,
                "index_type": type(self.faiss_index).__name__ if self.faiss_index else "None"
            }
            return stats
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {"error": str(e)}
    
    def optimize_for_search(self):
        """优化索引以提高搜索性能"""
        try:
            if self.faiss_index is None:
                logger.warning("索引为空，无法优化")
                return
            
            # 如果是IVF索引，可以进行优化
            if hasattr(self.faiss_index, 'make_direct_map'):
                self.faiss_index.make_direct_map()
                logger.info("FAISS索引已优化")
            
        except Exception as e:
            logger.error(f"索引优化失败: {e}")
    
    def get_memory_usage(self) -> dict:
        """获取内存使用情况"""
        try:
            memory_info = {}
            
            if self.embedding_device.startswith("cuda"):
                device_id = int(self.embedding_device.split(":")[-1])
                if torch.cuda.is_available() and device_id < torch.cuda.device_count():
                    memory_info["gpu_allocated"] = torch.cuda.memory_allocated(device_id) / 1024**3  # GB
                    memory_info["gpu_cached"] = torch.cuda.memory_reserved(device_id) / 1024**3  # GB
                    memory_info["gpu_max_allocated"] = torch.cuda.max_memory_allocated(device_id) / 1024**3  # GB
            
            return memory_info
            
        except Exception as e:
            logger.error(f"获取内存使用情况失败: {e}")
            return {"error": str(e)}