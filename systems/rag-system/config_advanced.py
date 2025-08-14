"""
高级配置 - 支持多API和分布式计算
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import json

# 基础路径配置
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR.parent.parent / "data"
SHARED_DIR = BASE_DIR.parent.parent / "shared"

class APIConfig:
    """API配置管理"""
    
    # API类型枚举
    API_TYPES = {
        "local": "本地模型",
        "modelscope": "魔搭API", 
        "openai": "OpenAI API",
        "anthropic": "Claude API",
        "zhipu": "智谱API",
        "baidu": "百度API",
        "alibaba": "阿里云API"
    }
    
    # 默认API配置
    DEFAULT_CONFIGS = {
        "local": {
            "model_path": "/models/deepseek-7b-chat-q5.gguf",
            "device": "cuda:0",  # 3090
            "n_ctx": 4096,
            "n_gpu_layers": 30
        },
        "modelscope": {
            "api_key": os.getenv("MODELSCOPE_API_KEY", ""),
            "base_url": "https://dashscope.aliyuncs.com/api/v1",
            "model": "qwen2.5-72b-instruct",
            "max_tokens": 2000
        },
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o-mini",
            "max_tokens": 2000
        },
        "zhipu": {
            "api_key": os.getenv("ZHIPU_API_KEY", ""),
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model": "glm-4-flash",
            "max_tokens": 2000
        }
    }
    
    @classmethod
    def get_config(cls, api_type: str) -> Dict[str, Any]:
        """获取指定API的配置"""
        return cls.DEFAULT_CONFIGS.get(api_type, {})
    
    @classmethod
    def set_config(cls, api_type: str, config: Dict[str, Any]):
        """设置指定API的配置"""
        cls.DEFAULT_CONFIGS[api_type] = config

class DistributedConfig:
    """分布式计算配置"""
    
    # 设备配置
    DEVICES = {
        "gpu_3090": {
            "device": "cuda:0",
            "memory": "24GB",
            "role": "llm_inference",  # 主要负责大模型推理
            "priority": 1
        },
        "gpu_4060": {
            "device": "cuda:1", 
            "memory": "8GB",
            "role": "embedding_processing",  # 负责嵌入计算和其他处理
            "priority": 2
        }
    }
    
    # 任务分配策略
    TASK_ALLOCATION = {
        "llm_inference": "gpu_3090",      # LLM推理 -> 3090
        "embedding": "gpu_4060",          # 嵌入计算 -> 4060
        "vector_search": "gpu_4060",      # 向量搜索 -> 4060
        "document_processing": "cpu",     # 文档处理 -> CPU
        "memory_management": "cpu"        # 记忆管理 -> CPU
    }
    
    @classmethod
    def get_device_for_task(cls, task: str) -> str:
        """获取任务对应的设备"""
        device_name = cls.TASK_ALLOCATION.get(task, "cpu")
        if device_name in cls.DEVICES:
            return cls.DEVICES[device_name]["device"]
        return device_name

class ModelConfig:
    """模型配置"""
    
    # 当前使用的API类型
    CURRENT_API = os.getenv("RAG_API_TYPE", "local")
    
    # 嵌入模型配置（在4060上运行）
    EMBEDDING_MODEL_PATH = "BAAI/bge-large-zh-v1.5"  # 中文效果更好
    EMBEDDING_DEVICE = DistributedConfig.get_device_for_task("embedding")
    
    # LLM配置（在3090上运行）
    LLM_DEVICE = DistributedConfig.get_device_for_task("llm_inference")
    
    @classmethod
    def get_current_config(cls) -> Dict[str, Any]:
        """获取当前API配置"""
        return APIConfig.get_config(cls.CURRENT_API)
    
    @classmethod
    def switch_api(cls, api_type: str):
        """切换API类型"""
        if api_type in APIConfig.API_TYPES:
            cls.CURRENT_API = api_type
            os.environ["RAG_API_TYPE"] = api_type
        else:
            raise ValueError(f"不支持的API类型: {api_type}")

class StorageConfig:
    """存储配置"""
    # 基础目录
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR.parent.parent / "data"
    SHARED_DIR = BASE_DIR.parent.parent / "shared"
    
    # 数据目录
    RAW_DATA_DIR = DATA_DIR / "raw" / "rag"
    PROCESSED_DATA_DIR = DATA_DIR / "processed" / "rag"
    MODELS_DATA_DIR = DATA_DIR / "models" / "rag"
    RESULTS_DATA_DIR = DATA_DIR / "results" / "rag"
    
    # 记忆系统路径
    MEMORY_DIR = DATA_DIR / "processed" / "rag" / "memory"
    PERMANENT_MEMORY_DIR = MEMORY_DIR / "permanent"
    TEMPORARY_MEMORY_DIR = MEMORY_DIR / "temporary"
    
    # 数据库路径
    DATABASE_DIR = DATA_DIR / "processed" / "rag" / "database"
    CHAT_DB_PATH = DATABASE_DIR / "chat_logs.db"
    
    # 本地文献库路径
    LIBRARY_DIR = RAW_DATA_DIR / "library"
    
    # 日志路径
    LOG_DIR = DATA_DIR / "processed" / "rag" / "logs"
    LOG_FILE = LOG_DIR / "rag_system.log"

class DocumentConfig:
    """文档处理配置"""
    SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".csv", ".txt", ".md", ".html", ".caj"]
    CHUNK_SIZE = 300
    CHUNK_OVERLAP = 50
    MAX_RETRIEVED_CHUNKS = 15
    MAX_SIMILAR_HISTORY = 5

class SystemConfig:
    """系统配置"""
    DEBUG = True
    LOG_LEVEL = "INFO"
    PAGE_TITLE = "🧬 综合科研工作站 - RAG智能问答"
    PAGE_ICON = "🤖"

def init_config():
    """初始化配置"""
    # 创建必要的目录
    directories = [
        StorageConfig.RAW_DATA_DIR,
        StorageConfig.PROCESSED_DATA_DIR,
        StorageConfig.MODELS_DATA_DIR,
        StorageConfig.RESULTS_DATA_DIR,
        StorageConfig.MEMORY_DIR,
        StorageConfig.PERMANENT_MEMORY_DIR,
        StorageConfig.TEMPORARY_MEMORY_DIR,
        StorageConfig.DATABASE_DIR,
        StorageConfig.LIBRARY_DIR,
        StorageConfig.LOG_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("RAG系统高级配置初始化完成")
    print(f"当前API类型: {ModelConfig.CURRENT_API}")
    print(f"LLM设备: {ModelConfig.LLM_DEVICE}")
    print(f"嵌入设备: {ModelConfig.EMBEDDING_DEVICE}")

def save_config_to_file(config_path: Optional[str] = None):
    """保存配置到文件"""
    if config_path is None:
        config_path = StorageConfig.DATA_DIR / "config.json"
    
    config_data = {
        "api_configs": APIConfig.DEFAULT_CONFIGS,
        "current_api": ModelConfig.CURRENT_API,
        "distributed_config": DistributedConfig.DEVICES,
        "task_allocation": DistributedConfig.TASK_ALLOCATION
    }
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    print(f"配置已保存到: {config_path}")

def load_config_from_file(config_path: Optional[str] = None):
    """从文件加载配置"""
    if config_path is None:
        config_path = StorageConfig.DATA_DIR / "config.json"
    
    if not Path(config_path).exists():
        print("配置文件不存在，使用默认配置")
        return
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        
        # 更新配置
        if "api_configs" in config_data:
            APIConfig.DEFAULT_CONFIGS.update(config_data["api_configs"])
        
        if "current_api" in config_data:
            ModelConfig.CURRENT_API = config_data["current_api"]
        
        print(f"配置已从文件加载: {config_path}")
        
    except Exception as e:
        print(f"加载配置文件失败: {e}")

# 自动初始化
if __name__ != "__main__":
    init_config()