"""
中央能源数据库 - Central Energy Database
管理所有AI模型的API配置，支持用户级别和项目级别的动态配置
"""

import os
import sqlite3
import json
import hashlib
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from cryptography.fernet import Fernet
import threading

class ModelProvider(Enum):
    """AI模型提供商"""
    OPENAI = "openai"
    GOOGLE = "google"  # Gemini
    CLAUDE = "claude"
    BAIDU = "baidu"
    ALIBABA = "alibaba"
    CUSTOM = "custom"

class ConfigScope(Enum):
    """配置作用域"""
    GLOBAL = "global"      # 全局生效
    PROJECT = "project"    # 项目级别
    USER = "user"         # 用户级别

@dataclass
class ModelConfig:
    """AI模型配置"""
    config_id: str
    user_id: str
    project_id: str
    provider: ModelProvider
    model_name: str
    api_key: str
    api_endpoint: str
    scope: ConfigScope
    is_active: bool = True
    priority: int = 0  # 优先级，数字越大优先级越高
    max_tokens: int = 4096
    temperature: float = 0.7
    created_at: float = None
    updated_at: float = None
    last_used: float = None
    usage_count: int = 0
    description: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
        if self.updated_at is None:
            self.updated_at = time.time()

class CentralEnergyDB:
    """中央能源数据库管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "config", "central_energy.db")
        
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_encryption()
        self._init_database()
    
    def _init_encryption(self):
        """初始化加密密钥"""
        key_file = os.path.join(os.path.dirname(__file__), "config", "energy_encryption.key")
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            self.encryption_key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(self.encryption_key)
        
        self.cipher = Fernet(self.encryption_key)
    
    def _init_database(self):
        """初始化数据库表"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建模型配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_configs (
                    config_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    encrypted_api_key TEXT NOT NULL,
                    api_endpoint TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    priority INTEGER DEFAULT 0,
                    max_tokens INTEGER DEFAULT 4096,
                    temperature REAL DEFAULT 0.7,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    last_used REAL,
                    usage_count INTEGER DEFAULT 0,
                    description TEXT DEFAULT ''
                )
            ''')
            
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT,
                    role TEXT DEFAULT 'user',
                    is_active INTEGER DEFAULT 1,
                    created_at REAL NOT NULL,
                    last_login REAL
                )
            ''')
            
            # 创建项目表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    is_active INTEGER DEFAULT 1,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (owner_id) REFERENCES users (user_id)
                )
            ''')
            
            # 创建使用统计表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usage_stats (
                    stat_id TEXT PRIMARY KEY,
                    config_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    tokens_used INTEGER DEFAULT 0,
                    requests_count INTEGER DEFAULT 0,
                    cost REAL DEFAULT 0.0,
                    date TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (config_id) REFERENCES model_configs (config_id)
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_configs ON model_configs (user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_configs ON model_configs (project_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_active_configs ON model_configs (is_active)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON model_configs (priority DESC)')
            
            conn.commit()
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """加密API密钥"""
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """解密API密钥"""
        return self.cipher.decrypt(encrypted_key.encode()).decode()
    
    def _generate_config_id(self, user_id: str, project_id: str, provider: str, model_name: str) -> str:
        """生成配置ID"""
        data = f"{user_id}:{project_id}:{provider}:{model_name}:{time.time()}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def add_model_config(self, config: ModelConfig) -> bool:
        """添加模型配置"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # 生成配置ID
                    if not config.config_id:
                        config.config_id = self._generate_config_id(
                            config.user_id, config.project_id, 
                            config.provider.value, config.model_name
                        )
                    
                    # 加密API密钥
                    encrypted_key = self._encrypt_api_key(config.api_key)
                    
                    cursor.execute('''
                        INSERT INTO model_configs (
                            config_id, user_id, project_id, provider, model_name,
                            encrypted_api_key, api_endpoint, scope, is_active, priority,
                            max_tokens, temperature, created_at, updated_at, description
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        config.config_id, config.user_id, config.project_id,
                        config.provider.value, config.model_name, encrypted_key,
                        config.api_endpoint, config.scope.value, config.is_active,
                        config.priority, config.max_tokens, config.temperature,
                        config.created_at, config.updated_at, config.description
                    ))
                    
                    conn.commit()
                    return True
        except Exception as e:
            print(f"添加模型配置失败: {e}")
            return False
    
    def get_model_config(self, config_id: str) -> Optional[ModelConfig]:
        """获取模型配置"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM model_configs WHERE config_id = ?', (config_id,))
                row = cursor.fetchone()
                
                if row:
                    config_data = {
                        'config_id': row[0], 'user_id': row[1], 'project_id': row[2],
                        'provider': ModelProvider(row[3]), 'model_name': row[4],
                        'api_key': self._decrypt_api_key(row[5]), 'api_endpoint': row[6],
                        'scope': ConfigScope(row[7]), 'is_active': bool(row[8]),
                        'priority': row[9], 'max_tokens': row[10], 'temperature': row[11],
                        'created_at': row[12], 'updated_at': row[13], 'last_used': row[14],
                        'usage_count': row[15], 'description': row[16]
                    }
                    return ModelConfig(**config_data)
        except Exception as e:
            print(f"获取模型配置失败: {e}")
        return None
    
    def get_best_model_config(self, user_id: str, project_id: str = "default") -> Optional[ModelConfig]:
        """获取最佳模型配置（根据优先级和作用域）"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 按优先级查找：项目级别 > 用户级别 > 全局级别
                query = '''
                    SELECT * FROM model_configs 
                    WHERE is_active = 1 AND (
                        (user_id = ? AND project_id = ? AND scope = 'project') OR
                        (user_id = ? AND scope = 'user') OR
                        (scope = 'global')
                    )
                    ORDER BY 
                        CASE scope 
                            WHEN 'project' THEN 3
                            WHEN 'user' THEN 2
                            WHEN 'global' THEN 1
                        END DESC,
                        priority DESC,
                        created_at DESC
                    LIMIT 1
                '''
                
                cursor.execute(query, (user_id, project_id, user_id))
                row = cursor.fetchone()
                
                if row:
                    config_data = {
                        'config_id': row[0], 'user_id': row[1], 'project_id': row[2],
                        'provider': ModelProvider(row[3]), 'model_name': row[4],
                        'api_key': self._decrypt_api_key(row[5]), 'api_endpoint': row[6],
                        'scope': ConfigScope(row[7]), 'is_active': bool(row[8]),
                        'priority': row[9], 'max_tokens': row[10], 'temperature': row[11],
                        'created_at': row[12], 'updated_at': row[13], 'last_used': row[14],
                        'usage_count': row[15], 'description': row[16]
                    }
                    return ModelConfig(**config_data)
        except Exception as e:
            print(f"获取最佳模型配置失败: {e}")
        return None
    
    def list_user_configs(self, user_id: str, project_id: str = None) -> List[ModelConfig]:
        """列出用户的所有配置"""
        configs = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if project_id:
                    query = '''
                        SELECT * FROM model_configs 
                        WHERE user_id = ? AND project_id = ?
                        ORDER BY priority DESC, created_at DESC
                    '''
                    cursor.execute(query, (user_id, project_id))
                else:
                    query = '''
                        SELECT * FROM model_configs 
                        WHERE user_id = ?
                        ORDER BY priority DESC, created_at DESC
                    '''
                    cursor.execute(query, (user_id,))
                
                for row in cursor.fetchall():
                    config_data = {
                        'config_id': row[0], 'user_id': row[1], 'project_id': row[2],
                        'provider': ModelProvider(row[3]), 'model_name': row[4],
                        'api_key': self._decrypt_api_key(row[5]), 'api_endpoint': row[6],
                        'scope': ConfigScope(row[7]), 'is_active': bool(row[8]),
                        'priority': row[9], 'max_tokens': row[10], 'temperature': row[11],
                        'created_at': row[12], 'updated_at': row[13], 'last_used': row[14],
                        'usage_count': row[15], 'description': row[16]
                    }
                    configs.append(ModelConfig(**config_data))
        except Exception as e:
            print(f"列出用户配置失败: {e}")
        
        return configs
    
    def update_model_config(self, config_id: str, **kwargs) -> bool:
        """更新模型配置"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # 构建更新语句
                    update_fields = []
                    values = []
                    
                    for key, value in kwargs.items():
                        if key == 'api_key':
                            update_fields.append('encrypted_api_key = ?')
                            values.append(self._encrypt_api_key(value))
                        elif key in ['provider', 'scope']:
                            update_fields.append(f'{key} = ?')
                            values.append(value.value if hasattr(value, 'value') else value)
                        elif key in ['model_name', 'api_endpoint', 'is_active', 'priority', 
                                   'max_tokens', 'temperature', 'description']:
                            update_fields.append(f'{key} = ?')
                            values.append(value)
                    
                    if update_fields:
                        update_fields.append('updated_at = ?')
                        values.append(time.time())
                        values.append(config_id)
                        
                        query = f"UPDATE model_configs SET {', '.join(update_fields)} WHERE config_id = ?"
                        cursor.execute(query, values)
                        conn.commit()
                        return cursor.rowcount > 0
        except Exception as e:
            print(f"更新模型配置失败: {e}")
        return False
    
    def delete_model_config(self, config_id: str) -> bool:
        """删除模型配置"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM model_configs WHERE config_id = ?', (config_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"删除模型配置失败: {e}")
        return False
    
    def record_usage(self, config_id: str, tokens_used: int = 0, cost: float = 0.0):
        """记录使用统计"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # 更新配置的使用统计
                    cursor.execute('''
                        UPDATE model_configs 
                        SET usage_count = usage_count + 1, last_used = ?
                        WHERE config_id = ?
                    ''', (time.time(), config_id))
                    
                    # 记录详细统计
                    today = time.strftime('%Y-%m-%d')
                    stat_id = hashlib.md5(f"{config_id}:{today}".encode()).hexdigest()
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO usage_stats (
                            stat_id, config_id, user_id, project_id,
                            tokens_used, requests_count, cost, date, created_at
                        ) SELECT 
                            ?, config_id, user_id, project_id,
                            COALESCE((SELECT tokens_used FROM usage_stats WHERE stat_id = ?), 0) + ?,
                            COALESCE((SELECT requests_count FROM usage_stats WHERE stat_id = ?), 0) + 1,
                            COALESCE((SELECT cost FROM usage_stats WHERE stat_id = ?), 0) + ?,
                            ?, ?
                        FROM model_configs WHERE config_id = ?
                    ''', (stat_id, stat_id, tokens_used, stat_id, stat_id, cost, today, time.time(), config_id))
                    
                    conn.commit()
        except Exception as e:
            print(f"记录使用统计失败: {e}")
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """获取可用的模型列表"""
        return {
            "openai": [
                "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo",
                "gpt-4o", "gpt-4o-mini"
            ],
            "google": [
                "gemini-2.0-flash-exp", "gemini-1.5-pro", 
                "gemini-1.5-flash", "gemini-pro"
            ],
            "claude": [
                "claude-3-opus", "claude-3-sonnet", 
                "claude-3-haiku", "claude-2"
            ],
            "custom": ["custom-model"]
        }

# 全局数据库实例
central_db = CentralEnergyDB()

def get_central_db() -> CentralEnergyDB:
    """获取中央数据库实例"""
    return central_db

if __name__ == "__main__":
    # 测试代码
    db = CentralEnergyDB()
    
    # 添加测试配置
    test_config = ModelConfig(
        config_id="",
        user_id="test_user",
        project_id="default",
        provider=ModelProvider.GOOGLE,
        model_name="gemini-2.0-flash-exp",
        api_key="test_api_key",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta",
        scope=ConfigScope.USER,
        description="测试配置"
    )
    
    success = db.add_model_config(test_config)
    print(f"添加配置: {'成功' if success else '失败'}")
    
    # 获取最佳配置
    best_config = db.get_best_model_config("test_user", "default")
    if best_config:
        print(f"最佳配置: {best_config.model_name} ({best_config.provider.value})")
    
    # 列出用户配置
    configs = db.list_user_configs("test_user")
    print(f"用户配置数量: {len(configs)}")