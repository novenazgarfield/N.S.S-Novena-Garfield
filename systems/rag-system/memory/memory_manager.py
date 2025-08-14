"""
记忆管理系统
"""
import os
import datetime
from typing import List
from pathlib import Path

from config import StorageConfig
from utils.logger import logger

class MemoryManager:
    """记忆管理类"""
    
    def __init__(self):
        self.permanent_memory_dir = StorageConfig.PERMANENT_MEMORY_DIR
        self.temporary_memory_dir = StorageConfig.TEMPORARY_MEMORY_DIR
        
        # 确保目录存在
        self.permanent_memory_dir.mkdir(parents=True, exist_ok=True)
        self.temporary_memory_dir.mkdir(parents=True, exist_ok=True)
    
    def save_permanent_memory(self, content: str, category: str = "general") -> str:
        """保存永久记忆"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"{category}_{timestamp}.txt"
            file_path = self.permanent_memory_dir / filename
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"时间: {datetime.datetime.now()}\n")
                f.write(f"类别: {category}\n")
                f.write(f"内容: {content}\n")
            
            logger.info(f"永久记忆保存成功: {filename}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"保存永久记忆失败: {e}")
            raise
    
    def save_temporary_memory(self, content: str, task_name: str) -> str:
        """保存临时记忆（按任务名）"""
        try:
            file_path = self.temporary_memory_dir / f"{task_name}.txt"
            
            # 追加模式写入
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"\n--- {datetime.datetime.now()} ---\n")
                f.write(f"{content}\n")
            
            logger.debug(f"临时记忆保存成功: {task_name}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"保存临时记忆失败: {e}")
            raise
    
    def load_permanent_memories(self, category: str = None) -> List[str]:
        """加载永久记忆"""
        try:
            memories = []
            
            for file_path in self.permanent_memory_dir.glob("*.txt"):
                # 如果指定了类别，只加载对应类别的记忆
                if category and not file_path.name.startswith(f"{category}_"):
                    continue
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            memories.append(content)
                except Exception as e:
                    logger.warning(f"读取永久记忆文件失败 {file_path}: {e}")
                    continue
            
            logger.info(f"加载永久记忆成功: {len(memories)} 条")
            return memories
            
        except Exception as e:
            logger.error(f"加载永久记忆失败: {e}")
            return []
    
    def load_temporary_memory(self, task_name: str) -> List[str]:
        """加载临时记忆（按任务名）"""
        try:
            file_path = self.temporary_memory_dir / f"{task_name}.txt"
            
            if not file_path.exists():
                logger.info(f"任务 {task_name} 的临时记忆文件不存在")
                return []
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    # 按分隔符分割记忆条目
                    memories = [mem.strip() for mem in content.split("---") if mem.strip()]
                    logger.info(f"加载临时记忆成功: {task_name}, {len(memories)} 条")
                    return memories
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"加载临时记忆失败 {task_name}: {e}")
            return []
    
    def clear_temporary_memory(self, task_name: str):
        """清除特定任务的临时记忆"""
        try:
            file_path = self.temporary_memory_dir / f"{task_name}.txt"
            if file_path.exists():
                file_path.unlink()
                logger.info(f"任务 {task_name} 的临时记忆已清除")
            else:
                logger.info(f"任务 {task_name} 的临时记忆文件不存在")
                
        except Exception as e:
            logger.error(f"清除临时记忆失败 {task_name}: {e}")
            raise
    
    def get_all_task_names(self) -> List[str]:
        """获取所有任务名称"""
        try:
            task_names = []
            for file_path in self.temporary_memory_dir.glob("*.txt"):
                task_name = file_path.stem
                task_names.append(task_name)
            return task_names
        except Exception as e:
            logger.error(f"获取任务名称失败: {e}")
            return []
    
    def get_memory_stats(self) -> dict:
        """获取记忆统计信息"""
        try:
            permanent_count = len(list(self.permanent_memory_dir.glob("*.txt")))
            temporary_count = len(list(self.temporary_memory_dir.glob("*.txt")))
            
            return {
                "permanent_memories": permanent_count,
                "temporary_tasks": temporary_count,
                "total_files": permanent_count + temporary_count
            }
        except Exception as e:
            logger.error(f"获取记忆统计失败: {e}")
            return {"permanent_memories": 0, "temporary_tasks": 0, "total_files": 0}