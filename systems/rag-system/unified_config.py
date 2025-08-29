"""
🔧 RAG系统统一配置管理器
========================

整合所有配置文件，提供统一的配置接口
- 基础配置 (config.py)
- 高级配置 (config_advanced.py)
- API配置 (api_config.py)

保持向后兼容，不破坏现有功能
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from utils.logger import logger

# 基础路径配置
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR.parent.parent / "management" / "data"
SHARED_DIR = BASE_DIR.parent.parent / "shared"

@dataclass
class ModelConfig:
    """模型配置"""
    # 嵌入模型
    embedding_model_path: str = "all-MiniLM-L6-v2"
    embedding_model_device: str = "auto"
    
    # LLM模型
    llm_model_path: Optional[str] = None
    llm_n_ctx: int = 4096
    llm_max_tokens: int = 196
    llm_temperature: float = 0.7
    
    # GPU配置
    auto_gpu_layers: bool = True
    gpu_layers: int = -1

@dataclass
class StorageConfig:
    """存储配置"""
    base_dir: Path = BASE_DIR
    data_dir: Path = DATA_DIR
    shared_dir: Path = SHARED_DIR
    
    # 向量数据库
    vector_db_path: Path = field(default_factory=lambda: DATA_DIR / "vector_db")
    
    # 文档存储
    documents_path: Path = field(default_factory=lambda: DATA_DIR / "documents")
    processed_path: Path = field(default_factory=lambda: DATA_DIR / "processed")
    
    # 日志路径
    logs_path: Path = field(default_factory=lambda: DATA_DIR / "logs")

@dataclass
class APIConfig:
    """API配置"""
    # API类型
    api_types: Dict[str, str] = field(default_factory=lambda: {
        "local": "本地模型",
        "openai": "OpenAI API",
        "gemini": "Gemini API",
        "anthropic": "Claude API",
        "zhipu": "智谱API",
        "baidu": "百度API",
        "alibaba": "阿里云API"
    })
    
    # 当前使用的API
    current_api: str = "local"
    
    # API密钥
    api_keys: Dict[str, str] = field(default_factory=dict)
    
    # API端点
    api_endpoints: Dict[str, str] = field(default_factory=lambda: {
        "openai": "https://api.openai.com/v1",
        "gemini": "https://generativelanguage.googleapis.com/v1beta",
        "anthropic": "https://api.anthropic.com/v1"
    })

@dataclass
class SystemConfig:
    """系统配置"""
    # 页面配置
    page_title: str = "🧠 RAG智能系统"
    page_icon: str = "🧠"
    layout: str = "wide"
    
    # 系统信息
    version: str = "2.0.0"
    author: str = "N.S.S-Novena-Garfield Project"
    
    # 功能开关
    enable_chronicle: bool = True
    enable_healing: bool = True
    enable_monitoring: bool = True

@dataclass
class DocumentConfig:
    """文档配置"""
    # 支持的文件类型
    supported_types: list = field(default_factory=lambda: [
        'txt', 'pdf', 'docx', 'md', 'html', 'json', 'csv'
    ])
    
    # 文档处理参数
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    
    # 语言配置
    default_language: str = "zh"
    supported_languages: list = field(default_factory=lambda: ["zh", "en"])

class UnifiedConfigManager:
    """统一配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or str(BASE_DIR / "config.json")
        
        # 初始化配置
        self.model = ModelConfig()
        self.storage = StorageConfig()
        self.api = APIConfig()
        self.system = SystemConfig()
        self.document = DocumentConfig()
        
        # 加载配置
        self.load_config()
        
        # 确保目录存在
        self._ensure_directories()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 更新配置
                self._update_config_from_dict(config_data)
                logger.info(f"配置已从 {self.config_file} 加载")
            else:
                logger.info("配置文件不存在，使用默认配置")
                self.save_config()  # 保存默认配置
                
        except Exception as e:
            logger.error(f"加载配置失败: {str(e)}")
    
    def save_config(self):
        """保存配置到文件"""
        try:
            config_data = {
                "model": self._dataclass_to_dict(self.model),
                "storage": self._dataclass_to_dict(self.storage),
                "api": self._dataclass_to_dict(self.api),
                "system": self._dataclass_to_dict(self.system),
                "document": self._dataclass_to_dict(self.document)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"配置已保存到 {self.config_file}")
            
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """从字典更新配置"""
        for section, data in config_data.items():
            if hasattr(self, section) and isinstance(data, dict):
                config_obj = getattr(self, section)
                for key, value in data.items():
                    if hasattr(config_obj, key):
                        # 处理Path类型
                        if isinstance(getattr(config_obj, key), Path):
                            setattr(config_obj, key, Path(value))
                        else:
                            setattr(config_obj, key, value)
    
    def _dataclass_to_dict(self, obj) -> Dict[str, Any]:
        """将dataclass转换为字典"""
        result = {}
        for key, value in obj.__dict__.items():
            if isinstance(value, Path):
                result[key] = str(value)
            elif isinstance(value, (dict, list, str, int, float, bool)) or value is None:
                result[key] = value
            else:
                result[key] = str(value)
        return result
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.storage.data_dir,
            self.storage.vector_db_path,
            self.storage.documents_path,
            self.storage.processed_path,
            self.storage.logs_path
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_api_key(self, api_type: str) -> Optional[str]:
        """获取API密钥"""
        return self.api.api_keys.get(api_type)
    
    def set_api_key(self, api_type: str, api_key: str):
        """设置API密钥"""
        self.api.api_keys[api_type] = api_key
        self.save_config()
    
    def switch_api(self, api_type: str):
        """切换API类型"""
        if api_type in self.api.api_types:
            self.api.current_api = api_type
            self.save_config()
            logger.info(f"已切换到 {self.api.api_types[api_type]}")
        else:
            logger.error(f"不支持的API类型: {api_type}")
    
    def get_current_api_config(self) -> Dict[str, Any]:
        """获取当前API配置"""
        api_type = self.api.current_api
        return {
            "type": api_type,
            "name": self.api.api_types.get(api_type, "未知"),
            "key": self.api.api_keys.get(api_type),
            "endpoint": self.api.api_endpoints.get(api_type)
        }

# 全局配置实例
config_manager = UnifiedConfigManager()

# 向后兼容的配置类
class ModelConfig:
    """向后兼容的模型配置"""
    EMBEDDING_MODEL_PATH = config_manager.model.embedding_model_path
    LLM_MODEL_PATH = config_manager.model.llm_model_path
    LLM_N_CTX = config_manager.model.llm_n_ctx
    LLM_MAX_TOKENS = config_manager.model.llm_max_tokens
    AUTO_GPU_LAYERS = config_manager.model.auto_gpu_layers

class StorageConfig:
    """向后兼容的存储配置"""
    BASE_DIR = config_manager.storage.base_dir
    DATA_DIR = config_manager.storage.data_dir
    VECTOR_DB_PATH = config_manager.storage.vector_db_path
    DOCUMENTS_PATH = config_manager.storage.documents_path

class SystemConfig:
    """向后兼容的系统配置"""
    PAGE_TITLE = config_manager.system.page_title
    PAGE_ICON = config_manager.system.page_icon
    VERSION = config_manager.system.version

class DocumentConfig:
    """向后兼容的文档配置"""
    SUPPORTED_TYPES = config_manager.document.supported_types
    CHUNK_SIZE = config_manager.document.chunk_size
    CHUNK_OVERLAP = config_manager.document.chunk_overlap

# 导出配置管理器
__all__ = [
    'config_manager',
    'ModelConfig', 
    'StorageConfig',
    'SystemConfig',
    'DocumentConfig',
    'UnifiedConfigManager'
]