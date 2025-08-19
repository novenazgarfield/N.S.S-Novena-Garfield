"""
牛只数据库管理器
Cattle Database Manager

管理牛只档案、识别记录和体况评分历史
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from contextlib import contextmanager

from ..identification.identification_utils import CattleProfile, IdentificationResult, CoatPatternFeature
from ..body_condition.body_condition_utils import BCSResult

class CattleDatabase:
    """牛只数据库管理器"""
    
    def __init__(self, db_path: str):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库表
        self._initialize_database()
        
        logging.info(f"牛只数据库初始化完成: {self.db_path}")
    
    def _initialize_database(self):
        """初始化数据库表结构"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 牛只档案表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cattle_profiles (
                    cattle_id TEXT PRIMARY KEY,
                    ear_tag_ids TEXT,  -- JSON数组
                    coat_pattern_features TEXT,  -- JSON数组
                    breed TEXT,
                    birth_date TEXT,
                    gender TEXT,
                    weight_history TEXT,  -- JSON数组
                    health_records TEXT,  -- JSON数组
                    metadata TEXT,  -- JSON对象
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # 识别记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS identification_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cattle_id TEXT,
                    method TEXT,
                    confidence REAL,
                    ear_tag_id TEXT,
                    coat_pattern_match TEXT,
                    metadata TEXT,  -- JSON对象
                    timestamp TEXT,
                    FOREIGN KEY (cattle_id) REFERENCES cattle_profiles (cattle_id)
                )
            ''')
            
            # 体况评分记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bcs_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cattle_id TEXT,
                    bcs_score REAL,
                    bcs_category TEXT,
                    confidence REAL,
                    scale_type TEXT,
                    keypoints_data TEXT,  -- JSON对象
                    geometric_features TEXT,  -- JSON对象
                    metadata TEXT,  -- JSON对象
                    timestamp TEXT,
                    FOREIGN KEY (cattle_id) REFERENCES cattle_profiles (cattle_id)
                )
            ''')
            
            # 系统日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT,
                    message TEXT,
                    module TEXT,
                    metadata TEXT,  -- JSON对象
                    timestamp TEXT
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_identification_cattle_id ON identification_records (cattle_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_identification_timestamp ON identification_records (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bcs_cattle_id ON bcs_records (cattle_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bcs_timestamp ON bcs_records (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs (timestamp)')
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # 使结果可以按列名访问
        try:
            yield conn
        finally:
            conn.close()
    
    def add_cattle_profile(self, profile: CattleProfile) -> bool:
        """
        添加牛只档案
        
        Args:
            profile: 牛只档案
        
        Returns:
            添加是否成功
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO cattle_profiles 
                    (cattle_id, ear_tag_ids, coat_pattern_features, breed, birth_date, 
                     gender, weight_history, health_records, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    profile.cattle_id,
                    json.dumps(profile.ear_tag_ids),
                    json.dumps([f.to_dict() for f in profile.coat_pattern_features]),
                    profile.breed,
                    profile.birth_date.isoformat() if profile.birth_date else None,
                    profile.gender,
                    json.dumps([(dt.isoformat(), weight) for dt, weight in profile.weight_history]),
                    json.dumps(profile.health_records),
                    json.dumps(profile.metadata),
                    profile.created_at.isoformat(),
                    profile.updated_at.isoformat()
                ))
                
                conn.commit()
                logging.info(f"牛只档案添加成功: {profile.cattle_id}")
                return True
                
        except Exception as e:
            logging.error(f"添加牛只档案失败: {e}")
            return False
    
    def get_cattle_profile(self, cattle_id: str) -> Optional[CattleProfile]:
        """
        获取牛只档案
        
        Args:
            cattle_id: 牛只ID
        
        Returns:
            牛只档案或None
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM cattle_profiles WHERE cattle_id = ?
                ''', (cattle_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # 解析JSON字段
                ear_tag_ids = json.loads(row['ear_tag_ids']) if row['ear_tag_ids'] else []
                
                coat_pattern_features = []
                if row['coat_pattern_features']:
                    features_data = json.loads(row['coat_pattern_features'])
                    for feature_data in features_data:
                        feature = CoatPatternFeature.from_dict(feature_data)
                        coat_pattern_features.append(feature)
                
                weight_history = []
                if row['weight_history']:
                    weight_data = json.loads(row['weight_history'])
                    for dt_str, weight in weight_data:
                        weight_history.append((datetime.fromisoformat(dt_str), weight))
                
                health_records = json.loads(row['health_records']) if row['health_records'] else []
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                
                # 创建档案对象
                profile = CattleProfile(
                    cattle_id=row['cattle_id'],
                    ear_tag_ids=ear_tag_ids,
                    coat_pattern_features=coat_pattern_features,
                    breed=row['breed'],
                    gender=row['gender'],
                    weight_history=weight_history,
                    health_records=health_records,
                    metadata=metadata,
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                
                if row['birth_date']:
                    profile.birth_date = datetime.fromisoformat(row['birth_date'])
                
                return profile
                
        except Exception as e:
            logging.error(f"获取牛只档案失败: {e}")
            return None
    
    def get_all_cattle_profiles(self) -> List[CattleProfile]:
        """获取所有牛只档案"""
        profiles = []
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT cattle_id FROM cattle_profiles')
                rows = cursor.fetchall()
                
                for row in rows:
                    profile = self.get_cattle_profile(row['cattle_id'])
                    if profile:
                        profiles.append(profile)
                
        except Exception as e:
            logging.error(f"获取所有牛只档案失败: {e}")
        
        return profiles
    
    def update_cattle_profile(self, profile: CattleProfile) -> bool:
        """更新牛只档案"""
        profile.updated_at = datetime.now()
        return self.add_cattle_profile(profile)
    
    def delete_cattle_profile(self, cattle_id: str) -> bool:
        """
        删除牛只档案
        
        Args:
            cattle_id: 牛只ID
        
        Returns:
            删除是否成功
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 删除相关记录
                cursor.execute('DELETE FROM identification_records WHERE cattle_id = ?', (cattle_id,))
                cursor.execute('DELETE FROM bcs_records WHERE cattle_id = ?', (cattle_id,))
                cursor.execute('DELETE FROM cattle_profiles WHERE cattle_id = ?', (cattle_id,))
                
                conn.commit()
                logging.info(f"牛只档案删除成功: {cattle_id}")
                return True
                
        except Exception as e:
            logging.error(f"删除牛只档案失败: {e}")
            return False
    
    def add_identification_record(self, result: IdentificationResult) -> bool:
        """
        添加识别记录
        
        Args:
            result: 识别结果
        
        Returns:
            添加是否成功
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO identification_records 
                    (cattle_id, method, confidence, ear_tag_id, coat_pattern_match, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result.cattle_id,
                    result.method.value,
                    result.confidence,
                    result.ear_tag_id,
                    result.coat_pattern_match,
                    json.dumps(result.metadata),
                    result.timestamp.isoformat()
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logging.error(f"添加识别记录失败: {e}")
            return False
    
    def get_identification_records(self, 
                                 cattle_id: Optional[str] = None,
                                 start_time: Optional[datetime] = None,
                                 end_time: Optional[datetime] = None,
                                 limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取识别记录
        
        Args:
            cattle_id: 牛只ID（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            limit: 记录数量限制
        
        Returns:
            识别记录列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = 'SELECT * FROM identification_records WHERE 1=1'
                params = []
                
                if cattle_id:
                    query += ' AND cattle_id = ?'
                    params.append(cattle_id)
                
                if start_time:
                    query += ' AND timestamp >= ?'
                    params.append(start_time.isoformat())
                
                if end_time:
                    query += ' AND timestamp <= ?'
                    params.append(end_time.isoformat())
                
                query += ' ORDER BY timestamp DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    record = {
                        'id': row['id'],
                        'cattle_id': row['cattle_id'],
                        'method': row['method'],
                        'confidence': row['confidence'],
                        'ear_tag_id': row['ear_tag_id'],
                        'coat_pattern_match': row['coat_pattern_match'],
                        'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                        'timestamp': datetime.fromisoformat(row['timestamp'])
                    }
                    records.append(record)
                
                return records
                
        except Exception as e:
            logging.error(f"获取识别记录失败: {e}")
            return []
    
    def add_bcs_record(self, cattle_id: str, bcs_result: BCSResult) -> bool:
        """
        添加体况评分记录
        
        Args:
            cattle_id: 牛只ID
            bcs_result: 体况评分结果
        
        Returns:
            添加是否成功
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                keypoints_data = None
                if bcs_result.keypoints:
                    keypoints_data = json.dumps({
                        'spine_points': bcs_result.keypoints.spine_points,
                        'hip_bone_left': bcs_result.keypoints.hip_bone_left,
                        'hip_bone_right': bcs_result.keypoints.hip_bone_right,
                        'tail_base': bcs_result.keypoints.tail_base,
                        'rib_points': bcs_result.keypoints.rib_points,
                        'confidence_scores': bcs_result.keypoints.confidence_scores
                    })
                
                geometric_features = None
                if bcs_result.geometric_features:
                    geometric_features = json.dumps({
                        'spine_length': bcs_result.geometric_features.spine_length,
                        'hip_width': bcs_result.geometric_features.hip_width,
                        'rib_depth': bcs_result.geometric_features.rib_depth,
                        'body_area': bcs_result.geometric_features.body_area,
                        'length_width_ratio': bcs_result.geometric_features.length_width_ratio
                    })
                
                cursor.execute('''
                    INSERT INTO bcs_records 
                    (cattle_id, bcs_score, bcs_category, confidence, scale_type, 
                     keypoints_data, geometric_features, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cattle_id,
                    bcs_result.bcs_score,
                    bcs_result.bcs_category.value,
                    bcs_result.confidence,
                    bcs_result.scale.value,
                    keypoints_data,
                    geometric_features,
                    json.dumps(bcs_result.metadata),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logging.error(f"添加体况评分记录失败: {e}")
            return False
    
    def get_bcs_records(self, 
                       cattle_id: Optional[str] = None,
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """获取体况评分记录"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = 'SELECT * FROM bcs_records WHERE 1=1'
                params = []
                
                if cattle_id:
                    query += ' AND cattle_id = ?'
                    params.append(cattle_id)
                
                if start_time:
                    query += ' AND timestamp >= ?'
                    params.append(start_time.isoformat())
                
                if end_time:
                    query += ' AND timestamp <= ?'
                    params.append(end_time.isoformat())
                
                query += ' ORDER BY timestamp DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    record = {
                        'id': row['id'],
                        'cattle_id': row['cattle_id'],
                        'bcs_score': row['bcs_score'],
                        'bcs_category': row['bcs_category'],
                        'confidence': row['confidence'],
                        'scale_type': row['scale_type'],
                        'keypoints_data': json.loads(row['keypoints_data']) if row['keypoints_data'] else None,
                        'geometric_features': json.loads(row['geometric_features']) if row['geometric_features'] else None,
                        'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                        'timestamp': datetime.fromisoformat(row['timestamp'])
                    }
                    records.append(record)
                
                return records
                
        except Exception as e:
            logging.error(f"获取体况评分记录失败: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 牛只总数
                cursor.execute('SELECT COUNT(*) as count FROM cattle_profiles')
                cattle_count = cursor.fetchone()['count']
                
                # 识别记录总数
                cursor.execute('SELECT COUNT(*) as count FROM identification_records')
                identification_count = cursor.fetchone()['count']
                
                # 体况评分记录总数
                cursor.execute('SELECT COUNT(*) as count FROM bcs_records')
                bcs_count = cursor.fetchone()['count']
                
                # 最近24小时的识别次数
                yesterday = datetime.now() - timedelta(days=1)
                cursor.execute('''
                    SELECT COUNT(*) as count FROM identification_records 
                    WHERE timestamp >= ?
                ''', (yesterday.isoformat(),))
                recent_identifications = cursor.fetchone()['count']
                
                # 识别方法分布
                cursor.execute('''
                    SELECT method, COUNT(*) as count 
                    FROM identification_records 
                    GROUP BY method
                ''')
                method_distribution = {row['method']: row['count'] for row in cursor.fetchall()}
                
                return {
                    'total_cattle': cattle_count,
                    'total_identifications': identification_count,
                    'total_bcs_records': bcs_count,
                    'recent_identifications_24h': recent_identifications,
                    'identification_methods': method_distribution,
                    'database_size': self.db_path.stat().st_size if self.db_path.exists() else 0
                }
                
        except Exception as e:
            logging.error(f"获取统计信息失败: {e}")
            return {}
    
    def backup_database(self, backup_path: str) -> bool:
        """
        备份数据库
        
        Args:
            backup_path: 备份文件路径
        
        Returns:
            备份是否成功
        """
        try:
            import shutil
            
            backup_file = Path(backup_path)
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(self.db_path, backup_file)
            
            logging.info(f"数据库备份成功: {backup_path}")
            return True
            
        except Exception as e:
            logging.error(f"数据库备份失败: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """
        从备份恢复数据库
        
        Args:
            backup_path: 备份文件路径
        
        Returns:
            恢复是否成功
        """
        try:
            import shutil
            
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_path}")
            
            shutil.copy2(backup_file, self.db_path)
            
            logging.info(f"数据库恢复成功: {backup_path}")
            return True
            
        except Exception as e:
            logging.error(f"数据库恢复失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        # SQLite连接在上下文管理器中自动关闭
        logging.info("数据库连接已关闭")