"""
聊天记录数据库系统
"""
import sqlite3
import datetime
import numpy as np
from typing import List, Tuple
from pathlib import Path

from config import StorageConfig
from utils.logger import logger

class ChatDatabase:
    """聊天记录数据库管理类"""
    
    def __init__(self):
        self.db_path = StorageConfig.CHAT_DB_PATH
        self.init_db()
    
    def init_db(self):
        """初始化数据库表"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                embedding BLOB,
                task_name TEXT DEFAULT 'default'
            )''')
            conn.commit()
            conn.close()
            logger.info(f"数据库初始化成功: {self.db_path}")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def store_message(self, role: str, content: str, embedding: np.ndarray = None, task_name: str = "default"):
        """存储聊天消息"""
        try:
            embedding_blob = None
            if embedding is not None:
                embedding_blob = embedding.astype(np.float32).tobytes()
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(
                "INSERT INTO chat_logs (role, content, timestamp, embedding, task_name) VALUES (?, ?, ?, ?, ?)",
                (role, content, datetime.datetime.now(), embedding_blob, task_name)
            )
            conn.commit()
            conn.close()
            logger.debug(f"消息存储成功: {role} - {content[:50]}...")
        except Exception as e:
            logger.error(f"消息存储失败: {e}")
            raise
    
    def retrieve_similar_messages(self, query_embedding: np.ndarray, top_k: int = 3, task_name: str = None) -> List[str]:
        """检索相似的历史消息"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # 构建查询条件
            query = "SELECT id, content, embedding FROM chat_logs WHERE embedding IS NOT NULL"
            params = []
            
            if task_name:
                query += " AND task_name = ?"
                params.append(task_name)
            
            c.execute(query, params)
            rows = c.fetchall()
            conn.close()
            
            if not rows:
                return []
            
            # 分离内容和嵌入向量
            contents = []
            embeddings = []
            
            for _, content, emb_blob in rows:
                try:
                    vec = np.frombuffer(emb_blob, dtype=np.float32)
                    if vec.ndim == 1 and vec.shape[0] == query_embedding.shape[0]:
                        contents.append(content)
                        embeddings.append(vec)
                except Exception as e:
                    logger.warning(f"跳过损坏的嵌入向量: {e}")
                    continue
            
            if not embeddings:
                return []
            
            # 计算相似度
            embeddings_matrix = np.stack(embeddings)
            similarities = np.dot(embeddings_matrix, query_embedding)
            
            # 获取top_k个最相似的
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            return [contents[i] for i in top_indices if i < len(contents)]
            
        except Exception as e:
            logger.error(f"检索相似消息失败: {e}")
            return []
    
    def get_recent_messages(self, limit: int = 10, task_name: str = None) -> List[Tuple[str, str, str]]:
        """获取最近的聊天记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            query = "SELECT role, content, timestamp FROM chat_logs"
            params = []
            
            if task_name:
                query += " WHERE task_name = ?"
                params.append(task_name)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            c.execute(query, params)
            rows = c.fetchall()
            conn.close()
            
            return rows
            
        except Exception as e:
            logger.error(f"获取最近消息失败: {e}")
            return []
    
    def clear_task_history(self, task_name: str):
        """清除特定任务的聊天历史"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("DELETE FROM chat_logs WHERE task_name = ?", (task_name,))
            conn.commit()
            conn.close()
            logger.info(f"任务 {task_name} 的聊天历史已清除")
        except Exception as e:
            logger.error(f"清除聊天历史失败: {e}")
            raise