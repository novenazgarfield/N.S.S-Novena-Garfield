"""
统一配置管理器
支持YAML配置文件和环境变量覆盖
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import re
from dataclasses import dataclass

@dataclass
class SystemConfig:
    """系统配置"""
    name: str
    version: str
    debug: bool
    log_level: str

@dataclass
class ModelConfig:
    """模型配置"""
    embedding_model_path: str
    embedding_device: str
    llm_model_path: Optional[str]
    llm_n_ctx: int
    llm_max_tokens: int
    auto_gpu_layers: bool

@dataclass
class StorageConfig:
    """存储配置"""
    base_dir: Path
    data_dir: Path
    shared_dir: Path
    raw_data_dir: Path
    processed_data_dir: Path
    models_data_dir: Path
    results_data_dir: Path
    memory_dir: Path
    database_dir: Path
    library_dir: Path
    logs_dir: Path

@dataclass
class DocumentConfig:
    """文档处理配置"""
    supported_extensions: list
    chunk_size: int
    chunk_overlap: int
    max_retrieved_chunks: int
    max_similar_history: int

@dataclass
class InterfaceConfig:
    """界面配置"""
    web: dict
    desktop: dict
    mobile: dict
    api: dict

class ConfigManager:
    """统一配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self._raw_config = None
        self._processed_config = None
        self.load_config()
    
    def _find_config_file(self) -> str:
        """查找配置文件"""
        possible_paths = [
            Path(__file__).parent.parent.parent / "config.yaml",
            Path.cwd() / "config.yaml",
            Path.cwd() / "config" / "config.yaml"
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError("找不到配置文件 config.yaml")
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._raw_config = yaml.safe_load(f)
            
            # 处理环境变量替换
            self._processed_config = self._process_env_vars(self._raw_config)
            
            # 创建配置对象
            self._create_config_objects()
            
        except Exception as e:
            raise RuntimeError(f"配置文件加载失败: {e}")
    
    def _process_env_vars(self, config: Any) -> Any:
        """处理环境变量替换"""
        if isinstance(config, dict):
            return {k: self._process_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._process_env_vars(item) for item in config]
        elif isinstance(config, str):
            return self._replace_env_vars(config)
        else:
            return config
    
    def _replace_env_vars(self, value: str) -> Any:
        """替换环境变量"""
        if not isinstance(value, str):
            return value
            
        # 匹配 ${VAR:default} 格式
        pattern = r'\$\{([^:}]+):([^}]*)\}'
        
        def replace_match(match):
            env_var = match.group(1)
            default_value = match.group(2)
            
            # 获取环境变量值
            env_value = os.getenv(env_var, default_value)
            
            # 类型转换
            if isinstance(env_value, str):
                if env_value.lower() in ('true', 'false'):
                    return str(env_value.lower() == 'true')
                elif env_value.lower() == 'null':
                    return 'null'
                elif env_value.isdigit():
                    return env_value
                elif self._is_float(env_value):
                    return env_value
                else:
                    return env_value
            else:
                return str(env_value)
        
        if '${' in value:
            result = re.sub(pattern, replace_match, value)
            # 后处理类型转换
            if result.lower() == 'true':
                return True
            elif result.lower() == 'false':
                return False
            elif result.lower() == 'null':
                return None
            elif result.isdigit():
                return int(result)
            elif self._is_float(result):
                return float(result)
            else:
                return result
        return value
    
    def _is_float(self, value: str) -> bool:
        """检查是否为浮点数"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _create_config_objects(self):
        """创建配置对象"""
        config = self._processed_config
        
        # 系统配置
        self.system = SystemConfig(
            name=config['system']['name'],
            version=config['system']['version'],
            debug=config['system']['debug'],
            log_level=config['system']['log_level']
        )
        
        # 模型配置
        self.models = ModelConfig(
            embedding_model_path=config['models']['embedding']['model_path'],
            embedding_device=config['models']['embedding']['device'],
            llm_model_path=config['models']['llm']['model_path'],
            llm_n_ctx=config['models']['llm']['n_ctx'],
            llm_max_tokens=config['models']['llm']['max_tokens'],
            auto_gpu_layers=config['models']['llm']['auto_gpu_layers']
        )
        
        # 存储配置
        base_dir = Path(config['storage']['base_dir']).resolve()
        data_dir = Path(config['storage']['data_dir']).resolve()
        shared_dir = Path(config['storage']['shared_dir']).resolve()
        
        dirs = config['storage']['directories']
        
        self.storage = StorageConfig(
            base_dir=base_dir,
            data_dir=data_dir,
            shared_dir=shared_dir,
            raw_data_dir=data_dir / dirs['raw_data'],
            processed_data_dir=data_dir / dirs['processed_data'],
            models_data_dir=data_dir / dirs['models_data'],
            results_data_dir=data_dir / dirs['results_data'],
            memory_dir=data_dir / dirs['memory'],
            database_dir=data_dir / dirs['database'],
            library_dir=data_dir / dirs['library'],
            logs_dir=data_dir / dirs['logs']
        )
        
        # 文档配置
        self.document = DocumentConfig(
            supported_extensions=config['document']['supported_extensions'],
            chunk_size=config['document']['chunking']['chunk_size'],
            chunk_overlap=config['document']['chunking']['chunk_overlap'],
            max_retrieved_chunks=config['document']['retrieval']['max_retrieved_chunks'],
            max_similar_history=config['document']['retrieval']['max_similar_history']
        )
        
        # 界面配置
        self.interfaces = InterfaceConfig(
            web=config['interfaces']['web'],
            desktop=config['interfaces']['desktop'],
            mobile=config['interfaces']['mobile'],
            api=config['interfaces']['api']
        )
    
    def ensure_directories(self):
        """确保所有必要目录存在"""
        dirs_to_create = [
            self.storage.raw_data_dir,
            self.storage.processed_data_dir,
            self.storage.models_data_dir,
            self.storage.results_data_dir,
            self.storage.memory_dir,
            self.storage.database_dir,
            self.storage.library_dir,
            self.storage.logs_dir
        ]
        
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self._processed_config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def reload(self):
        """重新加载配置"""
        self.load_config()

# 全局配置实例
_config_manager = None

def get_config() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def init_config(config_path: Optional[str] = None) -> ConfigManager:
    """初始化配置管理器"""
    global _config_manager
    _config_manager = ConfigManager(config_path)
    _config_manager.ensure_directories()
    return _config_manager