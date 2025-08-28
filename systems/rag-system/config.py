"""
RAG系统配置文件
"""
import os
from pathlib import Path

# 基础路径配置
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR.parent.parent / "management" / "data"
SHARED_DIR = BASE_DIR.parent.parent / "shared"

# 模型路径配置
class ModelConfig:
    # 嵌入模型路径 - 使用在线模型进行测试
    EMBEDDING_MODEL_PATH = "all-MiniLM-L6-v2"  # 使用轻量级在线模型
    
    # LLM模型路径 - 暂时设为None，用于测试
    LLM_MODEL_PATH = None  # 暂时不使用LLM模型
    
    # LLM参数
    LLM_N_CTX = 4096
    LLM_MAX_TOKENS = 196
    
    # GPU配置
    AUTO_GPU_LAYERS = True  # 自动检测GPU层数

# 数据存储路径配置
class StorageConfig:
    # 基础目录
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR.parent.parent / "management" / "data"
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
    
    # 确保所有目录存在
    @classmethod
    def ensure_dirs(cls):
        dirs = [
            cls.RAW_DATA_DIR,
            cls.PROCESSED_DATA_DIR,
            cls.MODELS_DATA_DIR,
            cls.RESULTS_DATA_DIR,
            cls.PERMANENT_MEMORY_DIR,
            cls.TEMPORARY_MEMORY_DIR,
            cls.DATABASE_DIR,
            cls.LIBRARY_DIR
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

# 文档处理配置
class DocumentConfig:
    # 支持的文件类型
    SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.pptx', '.xlsx', '.xls', '.csv', '.txt', '.py', '.md', '.html']
    
    # 文本分块参数
    CHUNK_SIZE = 300
    CHUNK_OVERLAP = 50
    
    # 检索参数
    MAX_RETRIEVED_CHUNKS = 15
    MAX_SIMILAR_HISTORY = 3

# 系统配置
class SystemConfig:
    # 调试模式
    DEBUG = True
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FILE = DATA_DIR / "processed" / "rag" / "logs" / "rag_system.log"
    
    # Streamlit配置
    PAGE_TITLE = "📚 本地多文献RAG问答系统"
    PAGE_ICON = "📚"

# 初始化配置
def init_config():
    """初始化配置，创建必要的目录"""
    StorageConfig.ensure_dirs()
    
    # 创建日志目录
    SystemConfig.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    print("RAG系统配置初始化完成")

if __name__ == "__main__":
    init_config()