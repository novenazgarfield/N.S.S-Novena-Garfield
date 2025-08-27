"""
日志管理模块
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

def setup_logger(
    name: str = "genome_jigsaw",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    max_size: str = "10MB",
    backup_count: int = 5,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径
        max_size: 日志文件最大大小
        backup_count: 备份文件数量
        format_string: 日志格式字符串
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 清除现有的处理器
    logger.handlers.clear()
    
    # 设置日志格式
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_string)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 解析文件大小
        size_bytes = _parse_size(max_size)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=size_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def _parse_size(size_str: str) -> int:
    """
    解析大小字符串为字节数
    
    Args:
        size_str: 大小字符串，如 "10MB", "1GB"
        
    Returns:
        字节数
    """
    size_str = size_str.upper().strip()
    
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        return int(size_str)

class GenomeJigsawLogger:
    """Genome Jigsaw 专用日志记录器"""
    
    def __init__(self, config):
        """
        初始化日志记录器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.logger = setup_logger(
            name="genome_jigsaw",
            level=getattr(logging, config.get("logging.level", "INFO")),
            log_file=config.get("logging.file"),
            max_size=config.get("logging.max_size", "10MB"),
            backup_count=config.get("logging.backup_count", 5),
            format_string=config.get("logging.format")
        )
    
    def info(self, message: str, **kwargs):
        """记录信息日志"""
        self.logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        self.logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录警告日志"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """记录错误日志"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """记录严重错误日志"""
        self.logger.critical(message, **kwargs)
    
    def log_analysis_start(self, analysis_type: str, sample_id: str):
        """记录分析开始"""
        self.info(f"🔬 开始 {analysis_type} 分析 - 样本: {sample_id}")
    
    def log_analysis_complete(self, analysis_type: str, sample_id: str, duration: float):
        """记录分析完成"""
        self.info(f"✅ 完成 {analysis_type} 分析 - 样本: {sample_id}, 耗时: {duration:.2f}秒")
    
    def log_analysis_error(self, analysis_type: str, sample_id: str, error: str):
        """记录分析错误"""
        self.error(f"❌ {analysis_type} 分析失败 - 样本: {sample_id}, 错误: {error}")
    
    def log_file_processed(self, file_path: str, file_type: str):
        """记录文件处理"""
        self.info(f"📁 处理文件: {file_path} ({file_type})")
    
    def log_quality_metrics(self, sample_id: str, metrics: dict):
        """记录质量指标"""
        metrics_str = ", ".join([f"{k}: {v}" for k, v in metrics.items()])
        self.info(f"📊 质量指标 - 样本: {sample_id}, {metrics_str}")
    
    def log_variant_stats(self, sample_id: str, stats: dict):
        """记录变异统计"""
        stats_str = ", ".join([f"{k}: {v}" for k, v in stats.items()])
        self.info(f"🧬 变异统计 - 样本: {sample_id}, {stats_str}")