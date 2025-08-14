"""
日志系统
"""
import logging
import sys
from pathlib import Path
from config import SystemConfig

def setup_logger(name: str = "rag_system") -> logging.Logger:
    """设置日志系统"""
    logger = logging.getLogger(name)
    
    if logger.handlers:  # 避免重复添加handler
        return logger
    
    logger.setLevel(getattr(logging, SystemConfig.LOG_LEVEL))
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    if SystemConfig.LOG_FILE:
        file_handler = logging.FileHandler(SystemConfig.LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# 全局日志实例
logger = setup_logger()