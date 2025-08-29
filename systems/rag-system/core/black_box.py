"""
🛡️ 黑匣子与免疫系统 (Black Box & Immune System)
=====================================================

实现"大宪章"第六章：失败的"记忆"
- 独立的故障数据库 (failure_log.db)
- 自动伤害记录仪 (Auto Damage Recorder)
- 免疫系统构建 (Immune System Builder)
- 故障模式识别与预防

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Genesis" Chapter 6
"""

import sqlite3
import json
import traceback
import inspect
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path

from utils.logger import logger

class FailureStatus(Enum):
    """故障状态"""
    DETECTED = "detected"           # 故障检测到
    ANALYZING = "analyzing"         # 正在分析
    FIXING = "fixing"              # 正在修复
    FIXED = "fixed"                # 修复成功
    FAILED = "failed"              # 修复失败
    IMMUNE = "immune"              # 已免疫

class SystemSource(Enum):
    """系统来源"""
    GENE_NEBULA = "gene_nebula"                    # 记忆星图
    RAG_SYSTEM = "rag_system"                      # RAG系统
    TRINITY_CHUNKER = "trinity_chunker"            # 三位一体分块器
    SHIELDS_OF_ORDER = "shields_of_order"          # 秩序之盾
    FIRE_CONTROL = "fire_control"                  # 火控系统
    PANTHEON_SOUL = "pantheon_soul"                # Pantheon灵魂
    INTELLIGENCE_BRAIN = "intelligence_brain"       # 中央情报大脑
    UNKNOWN = "unknown"                            # 未知系统

@dataclass
class FailureRecord:
    """故障记录数据类"""
    failure_id: str
    timestamp: datetime
    source_system: SystemSource
    function_name: str
    error_type: str
    error_message: str
    error_traceback: str
    faulty_code: str
    context_data: Dict[str, Any]
    ai_fix_attempted: Optional[str] = None
    fix_success: bool = False
    status: FailureStatus = FailureStatus.DETECTED
    retry_count: int = 0
    immunity_level: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class BlackBoxRecorder:
    """黑匣子记录器 - 独立的故障数据库"""
    
    def __init__(self, db_path: str = None):
        # 确保黑匣子数据库与主数据库完全隔离
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "..", "data", "failure_log.db")
        
        self.db_path = db_path
        self.ensure_data_directory()
        self.init_database()
        
        logger.info("🛡️ 黑匣子记录器已激活 - 故障记忆系统启动")
    
    def ensure_data_directory(self):
        """确保数据目录存在"""
        data_dir = os.path.dirname(self.db_path)
        Path(data_dir).mkdir(parents=True, exist_ok=True)
    
    def init_database(self):
        """初始化黑匣子数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建故障记录表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS failure_records (
                    failure_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    function_name TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    error_traceback TEXT NOT NULL,
                    faulty_code TEXT NOT NULL,
                    context_data TEXT NOT NULL,
                    ai_fix_attempted TEXT,
                    fix_success BOOLEAN DEFAULT FALSE,
                    status TEXT DEFAULT 'detected',
                    retry_count INTEGER DEFAULT 0,
                    immunity_level INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """)
                
                # 创建故障模式表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS failure_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    error_signature TEXT NOT NULL,
                    occurrence_count INTEGER DEFAULT 1,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    immunity_developed BOOLEAN DEFAULT FALSE,
                    prevention_strategy TEXT,
                    success_rate REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """)
                
                # 创建免疫记录表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS immunity_records (
                    immunity_id TEXT PRIMARY KEY,
                    error_signature TEXT NOT NULL,
                    prevention_code TEXT NOT NULL,
                    effectiveness_score REAL DEFAULT 0.0,
                    activation_count INTEGER DEFAULT 0,
                    last_activation TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """)
                
                # 创建索引
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON failure_records(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_system ON failure_records(source_system)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_type ON failure_records(error_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON failure_records(status)")
                
                conn.commit()
                logger.info("🛡️ 黑匣子数据库初始化完成")
                
        except Exception as e:
            logger.error(f"黑匣子数据库初始化失败: {e}")
            raise
    
    def record_failure(self, 
                      source_system: SystemSource,
                      function_name: str,
                      error: Exception,
                      faulty_code: str = "",
                      context_data: Dict[str, Any] = None) -> str:
        """记录故障到黑匣子"""
        try:
            # 生成故障ID
            failure_id = self._generate_failure_id(source_system, function_name, error)
            
            # 创建故障记录
            record = FailureRecord(
                failure_id=failure_id,
                timestamp=datetime.now(),
                source_system=source_system,
                function_name=function_name,
                error_type=type(error).__name__,
                error_message=str(error),
                error_traceback=traceback.format_exc(),
                faulty_code=faulty_code,
                context_data=context_data or {}
            )
            
            # 存储到数据库
            self._save_failure_record(record)
            
            # 更新故障模式
            self._update_failure_pattern(record)
            
            logger.warning(f"🛡️ 故障已记录到黑匣子: {failure_id}")
            return failure_id
            
        except Exception as e:
            logger.error(f"黑匣子记录失败: {e}")
            return ""
    
    def update_failure_fix(self, 
                          failure_id: str, 
                          ai_fix_code: str, 
                          fix_success: bool,
                          retry_count: int = 0):
        """更新故障修复信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                status = FailureStatus.FIXED.value if fix_success else FailureStatus.FAILED.value
                
                cursor.execute("""
                UPDATE failure_records 
                SET ai_fix_attempted = ?, 
                    fix_success = ?, 
                    status = ?,
                    retry_count = ?,
                    updated_at = ?
                WHERE failure_id = ?
                """, (ai_fix_code, fix_success, status, retry_count, datetime.now().isoformat(), failure_id))
                
                conn.commit()
                
                if fix_success:
                    logger.info(f"🛡️ 故障修复成功记录: {failure_id}")
                    # 尝试开发免疫力
                    self._develop_immunity(failure_id)
                else:
                    logger.warning(f"🛡️ 故障修复失败记录: {failure_id}")
                
        except Exception as e:
            logger.error(f"更新故障修复信息失败: {e}")
    
    def _generate_failure_id(self, source_system: SystemSource, function_name: str, error: Exception) -> str:
        """生成故障ID"""
        timestamp = datetime.now().isoformat()
        content = f"{source_system.value}_{function_name}_{type(error).__name__}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _save_failure_record(self, record: FailureRecord):
        """保存故障记录到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT OR REPLACE INTO failure_records 
                (failure_id, timestamp, source_system, function_name, error_type, 
                 error_message, error_traceback, faulty_code, context_data, 
                 ai_fix_attempted, fix_success, status, retry_count, immunity_level,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.failure_id,
                    record.timestamp.isoformat(),
                    record.source_system.value,
                    record.function_name,
                    record.error_type,
                    record.error_message,
                    record.error_traceback,
                    record.faulty_code,
                    json.dumps(record.context_data),
                    record.ai_fix_attempted,
                    record.fix_success,
                    record.status.value,
                    record.retry_count,
                    record.immunity_level,
                    record.created_at.isoformat(),
                    record.updated_at.isoformat()
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"保存故障记录失败: {e}")
            raise
    
    def _update_failure_pattern(self, record: FailureRecord):
        """更新故障模式"""
        try:
            # 生成错误签名
            error_signature = self._generate_error_signature(record)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 检查是否已存在该模式
                cursor.execute("""
                SELECT pattern_id, occurrence_count FROM failure_patterns 
                WHERE error_signature = ?
                """, (error_signature,))
                
                result = cursor.fetchone()
                
                if result:
                    # 更新现有模式
                    pattern_id, count = result
                    cursor.execute("""
                    UPDATE failure_patterns 
                    SET occurrence_count = ?, last_seen = ?, updated_at = ?
                    WHERE pattern_id = ?
                    """, (count + 1, record.timestamp.isoformat(), datetime.now().isoformat(), pattern_id))
                else:
                    # 创建新模式
                    pattern_id = hashlib.md5(error_signature.encode()).hexdigest()[:12]
                    cursor.execute("""
                    INSERT INTO failure_patterns 
                    (pattern_id, error_signature, occurrence_count, first_seen, last_seen, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        pattern_id,
                        error_signature,
                        1,
                        record.timestamp.isoformat(),
                        record.timestamp.isoformat(),
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"更新故障模式失败: {e}")
    
    def _generate_error_signature(self, record: FailureRecord) -> str:
        """生成错误签名"""
        # 基于错误类型、函数名和关键错误信息生成签名
        key_elements = [
            record.source_system.value,
            record.function_name,
            record.error_type,
            # 提取错误消息的关键部分（去除变量值）
            self._normalize_error_message(record.error_message)
        ]
        return "|".join(key_elements)
    
    def _normalize_error_message(self, error_message: str) -> str:
        """标准化错误消息，去除变量值"""
        # 简单的标准化，可以根据需要扩展
        import re
        # 替换数字和路径
        normalized = re.sub(r'\d+', '<NUM>', error_message)
        normalized = re.sub(r'/[^\s]+', '<PATH>', normalized)
        normalized = re.sub(r"'[^']*'", '<STR>', normalized)
        return normalized[:200]  # 限制长度
    
    def _develop_immunity(self, failure_id: str):
        """开发免疫力"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取故障记录
                cursor.execute("""
                SELECT error_type, error_message, ai_fix_attempted, source_system, function_name
                FROM failure_records WHERE failure_id = ? AND fix_success = TRUE
                """, (failure_id,))
                
                result = cursor.fetchone()
                if not result:
                    return
                
                error_type, error_message, ai_fix, source_system, function_name = result
                
                # 生成错误签名
                error_signature = f"{source_system}|{function_name}|{error_type}"
                
                # 检查是否已有免疫记录
                cursor.execute("""
                SELECT immunity_id FROM immunity_records WHERE error_signature = ?
                """, (error_signature,))
                
                if not cursor.fetchone() and ai_fix:
                    # 创建免疫记录
                    immunity_id = hashlib.md5(f"{error_signature}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
                    
                    cursor.execute("""
                    INSERT INTO immunity_records 
                    (immunity_id, error_signature, prevention_code, effectiveness_score, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        immunity_id,
                        error_signature,
                        ai_fix,
                        0.8,  # 初始效果评分
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                    
                    conn.commit()
                    logger.info(f"🛡️ 免疫力已开发: {immunity_id}")
                
        except Exception as e:
            logger.error(f"开发免疫力失败: {e}")
    
    def get_failure_records(self, 
                           limit: int = 100, 
                           source_system: SystemSource = None,
                           status: FailureStatus = None) -> List[Dict[str, Any]]:
        """获取故障记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM failure_records"
                params = []
                conditions = []
                
                if source_system:
                    conditions.append("source_system = ?")
                    params.append(source_system.value)
                
                if status:
                    conditions.append("status = ?")
                    params.append(status.value)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                
                columns = [description[0] for description in cursor.description]
                records = []
                
                for row in cursor.fetchall():
                    record = dict(zip(columns, row))
                    # 解析JSON字段
                    if record['context_data']:
                        record['context_data'] = json.loads(record['context_data'])
                    records.append(record)
                
                return records
                
        except Exception as e:
            logger.error(f"获取故障记录失败: {e}")
            return []
    
    def get_failure_statistics(self) -> Dict[str, Any]:
        """获取故障统计信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 总故障数
                cursor.execute("SELECT COUNT(*) FROM failure_records")
                total_failures = cursor.fetchone()[0]
                
                # 修复成功数
                cursor.execute("SELECT COUNT(*) FROM failure_records WHERE fix_success = TRUE")
                fixed_failures = cursor.fetchone()[0]
                
                # 按系统分组统计
                cursor.execute("""
                SELECT source_system, COUNT(*) as count, 
                       SUM(CASE WHEN fix_success = TRUE THEN 1 ELSE 0 END) as fixed_count
                FROM failure_records 
                GROUP BY source_system
                """)
                system_stats = {}
                for row in cursor.fetchall():
                    system, count, fixed = row
                    system_stats[system] = {
                        "total": count,
                        "fixed": fixed,
                        "fix_rate": fixed / count if count > 0 else 0
                    }
                
                # 按错误类型统计
                cursor.execute("""
                SELECT error_type, COUNT(*) as count
                FROM failure_records 
                GROUP BY error_type 
                ORDER BY count DESC 
                LIMIT 10
                """)
                error_type_stats = dict(cursor.fetchall())
                
                # 故障模式数
                cursor.execute("SELECT COUNT(*) FROM failure_patterns")
                pattern_count = cursor.fetchone()[0]
                
                # 免疫记录数
                cursor.execute("SELECT COUNT(*) FROM immunity_records")
                immunity_count = cursor.fetchone()[0]
                
                return {
                    "total_failures": total_failures,
                    "fixed_failures": fixed_failures,
                    "fix_rate": fixed_failures / total_failures if total_failures > 0 else 0,
                    "system_statistics": system_stats,
                    "error_type_statistics": error_type_stats,
                    "failure_patterns": pattern_count,
                    "immunity_records": immunity_count,
                    "last_update": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"获取故障统计失败: {e}")
            return {}
    
    def get_immunity_status(self) -> Dict[str, Any]:
        """获取免疫系统状态"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取所有免疫记录
                cursor.execute("""
                SELECT immunity_id, error_signature, effectiveness_score, 
                       activation_count, last_activation, created_at
                FROM immunity_records 
                ORDER BY effectiveness_score DESC
                """)
                
                immunity_records = []
                for row in cursor.fetchall():
                    immunity_id, signature, score, count, last_activation, created = row
                    immunity_records.append({
                        "immunity_id": immunity_id,
                        "error_signature": signature,
                        "effectiveness_score": score,
                        "activation_count": count,
                        "last_activation": last_activation,
                        "created_at": created
                    })
                
                # 计算免疫系统健康度
                total_immunities = len(immunity_records)
                avg_effectiveness = sum(r["effectiveness_score"] for r in immunity_records) / max(total_immunities, 1)
                
                return {
                    "total_immunities": total_immunities,
                    "average_effectiveness": avg_effectiveness,
                    "immunity_records": immunity_records[:20],  # 返回前20个
                    "system_health": "excellent" if avg_effectiveness > 0.8 else "good" if avg_effectiveness > 0.6 else "needs_improvement",
                    "last_update": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"获取免疫状态失败: {e}")
            return {}

# 全局黑匣子实例
_global_black_box = None

def get_black_box() -> BlackBoxRecorder:
    """获取全局黑匣子实例"""
    global _global_black_box
    if _global_black_box is None:
        _global_black_box = BlackBoxRecorder()
    return _global_black_box