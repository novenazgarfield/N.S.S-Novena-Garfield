"""
日志设置工具
Logger Setup Utilities

配置系统日志记录
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Any, Optional

def setup_logging(config: Dict[str, Any]):
    """
    设置日志系统
    
    Args:
        config: 日志配置字典
    """
    # 默认配置
    default_config = {
        'level': 'INFO',
        'file': 'logs/bovine_insight.log',
        'max_size': '10MB',
        'backup_count': 5,
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'console': True
    }
    
    # 合并配置
    log_config = {**default_config, **config}
    
    # 创建日志目录
    log_file = Path(log_config['file'])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 设置日志级别
    level = getattr(logging, log_config['level'].upper(), logging.INFO)
    
    # 创建格式器
    formatter = logging.Formatter(log_config['format'])
    
    # 获取根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 文件处理器（带轮转）
    max_bytes = parse_size(log_config['max_size'])
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=log_config['backup_count'],
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)
    
    # 控制台处理器
    if log_config.get('console', True):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    
    logging.info(f"日志系统初始化完成，级别: {log_config['level']}, 文件: {log_file}")

def parse_size(size_str: str) -> int:
    """
    解析大小字符串
    
    Args:
        size_str: 大小字符串，如 '10MB', '1GB'
    
    Returns:
        字节数
    """
    size_str = size_str.upper().strip()
    
    if size_str.endswith('KB'):
        return int(float(size_str[:-2]) * 1024)
    elif size_str.endswith('MB'):
        return int(float(size_str[:-2]) * 1024 * 1024)
    elif size_str.endswith('GB'):
        return int(float(size_str[:-2]) * 1024 * 1024 * 1024)
    else:
        return int(size_str)

class ColoredFormatter(logging.Formatter):
    """彩色日志格式器"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)

def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    获取指定名称的日志器
    
    Args:
        name: 日志器名称
        level: 日志级别（可选）
    
    Returns:
        日志器实例
    """
    logger = logging.getLogger(name)
    
    if level:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    return logger