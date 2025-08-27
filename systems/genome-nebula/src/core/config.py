"""
配置管理模块
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = "config/default.yaml"):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config_data = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        
        # 加载环境变量覆盖
        self._load_env_overrides()
    
    def _load_env_overrides(self):
        """加载环境变量覆盖配置"""
        env_prefix = "GENOME_JIGSAW_"
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower().replace('_', '.')
                self.set(config_key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点分隔的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split('.')
        config = self.config_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_database_url(self, db_type: str = "postgresql") -> str:
        """
        获取数据库连接URL
        
        Args:
            db_type: 数据库类型
            
        Returns:
            数据库连接URL
        """
        if db_type == "postgresql":
            host = self.get("database.postgresql.host", "localhost")
            port = self.get("database.postgresql.port", 5432)
            database = self.get("database.postgresql.database", "genome_jigsaw")
            username = self.get("database.postgresql.username", "postgres")
            password = self.get("database.postgresql.password", "password")
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        
        elif db_type == "mongodb":
            host = self.get("database.mongodb.host", "localhost")
            port = self.get("database.mongodb.port", 27017)
            database = self.get("database.mongodb.database", "genome_jigsaw")
            return f"mongodb://{host}:{port}/{database}"
        
        elif db_type == "redis":
            host = self.get("database.redis.host", "localhost")
            port = self.get("database.redis.port", 6379)
            database = self.get("database.redis.database", 0)
            return f"redis://{host}:{port}/{database}"
        
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")
    
    def get_paths(self) -> Dict[str, str]:
        """获取所有路径配置"""
        paths = self.get("paths", {})
        
        # 确保路径存在
        for path_name, path_value in paths.items():
            path_obj = Path(path_value)
            if not path_obj.exists():
                path_obj.mkdir(parents=True, exist_ok=True)
        
        return paths
    
    def validate(self) -> bool:
        """验证配置的有效性"""
        required_keys = [
            "system.name",
            "system.version",
            "paths.data_root",
            "database.postgresql.host"
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                raise ValueError(f"缺少必需的配置项: {key}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.config_data.copy()
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Config(file={self.config_file})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"Config(file={self.config_file}, keys={list(self.config_data.keys())})"