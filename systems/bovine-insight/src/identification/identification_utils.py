"""
身份识别工具类
Identification Utilities

定义身份识别相关的数据结构和工具函数
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import hashlib
from datetime import datetime

class IdentificationMethod(Enum):
    """识别方法枚举"""
    EAR_TAG = "ear_tag"
    COAT_PATTERN = "coat_pattern"
    FUSED = "fused"
    UNKNOWN = "unknown"

class ConfidenceLevel(Enum):
    """置信度等级"""
    HIGH = "high"      # > 0.8
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"        # < 0.5

@dataclass
class IdentificationResult:
    """身份识别结果"""
    cattle_id: Optional[str]
    method: IdentificationMethod
    confidence: float
    ear_tag_id: Optional[str] = None
    coat_pattern_match: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """获取置信度等级"""
        if self.confidence > 0.8:
            return ConfidenceLevel.HIGH
        elif self.confidence > 0.5:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'cattle_id': self.cattle_id,
            'method': self.method.value,
            'confidence': self.confidence,
            'confidence_level': self.confidence_level.value,
            'ear_tag_id': self.ear_tag_id,
            'coat_pattern_match': self.coat_pattern_match,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IdentificationResult':
        """从字典创建"""
        return cls(
            cattle_id=data.get('cattle_id'),
            method=IdentificationMethod(data.get('method', 'unknown')),
            confidence=data.get('confidence', 0.0),
            ear_tag_id=data.get('ear_tag_id'),
            coat_pattern_match=data.get('coat_pattern_match'),
            metadata=data.get('metadata', {}),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
        )

@dataclass
class CoatPatternFeature:
    """花色特征"""
    feature_vector: np.ndarray
    extraction_method: str
    image_hash: str
    quality_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于存储）"""
        return {
            'feature_vector': self.feature_vector.tolist(),
            'extraction_method': self.extraction_method,
            'image_hash': self.image_hash,
            'quality_score': self.quality_score,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CoatPatternFeature':
        """从字典创建"""
        return cls(
            feature_vector=np.array(data['feature_vector']),
            extraction_method=data['extraction_method'],
            image_hash=data['image_hash'],
            quality_score=data.get('quality_score', 0.0),
            metadata=data.get('metadata', {})
        )
    
    def similarity(self, other: 'CoatPatternFeature') -> float:
        """计算与另一个特征的相似度"""
        if self.feature_vector.shape != other.feature_vector.shape:
            return 0.0
        
        # 使用余弦相似度
        dot_product = np.dot(self.feature_vector, other.feature_vector)
        norm_a = np.linalg.norm(self.feature_vector)
        norm_b = np.linalg.norm(other.feature_vector)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)

@dataclass
class CattleProfile:
    """牛只档案"""
    cattle_id: str
    ear_tag_ids: List[str] = field(default_factory=list)
    coat_pattern_features: List[CoatPatternFeature] = field(default_factory=list)
    breed: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    weight_history: List[Tuple[datetime, float]] = field(default_factory=list)
    health_records: List[Dict[str, Any]] = field(default_factory=list)
    identification_history: List[IdentificationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_ear_tag(self, ear_tag_id: str):
        """添加耳标ID"""
        if ear_tag_id not in self.ear_tag_ids:
            self.ear_tag_ids.append(ear_tag_id)
            self.updated_at = datetime.now()
    
    def add_coat_pattern_feature(self, feature: CoatPatternFeature):
        """添加花色特征"""
        # 检查是否已存在相似特征
        for existing_feature in self.coat_pattern_features:
            if existing_feature.similarity(feature) > 0.95:
                return  # 特征过于相似，不添加
        
        self.coat_pattern_features.append(feature)
        self.updated_at = datetime.now()
    
    def get_best_coat_pattern_feature(self) -> Optional[CoatPatternFeature]:
        """获取质量最好的花色特征"""
        if not self.coat_pattern_features:
            return None
        
        return max(self.coat_pattern_features, key=lambda f: f.quality_score)
    
    def add_identification_record(self, result: IdentificationResult):
        """添加识别记录"""
        self.identification_history.append(result)
        self.updated_at = datetime.now()
        
        # 保持最近100条记录
        if len(self.identification_history) > 100:
            self.identification_history = self.identification_history[-100:]
    
    def get_identification_stats(self) -> Dict[str, Any]:
        """获取识别统计信息"""
        if not self.identification_history:
            return {}
        
        total_identifications = len(self.identification_history)
        method_counts = {}
        confidence_sum = 0.0
        
        for result in self.identification_history:
            method = result.method.value
            method_counts[method] = method_counts.get(method, 0) + 1
            confidence_sum += result.confidence
        
        return {
            'total_identifications': total_identifications,
            'method_distribution': method_counts,
            'average_confidence': confidence_sum / total_identifications,
            'last_identification': self.identification_history[-1].timestamp
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'cattle_id': self.cattle_id,
            'ear_tag_ids': self.ear_tag_ids,
            'coat_pattern_features': [f.to_dict() for f in self.coat_pattern_features],
            'breed': self.breed,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'gender': self.gender,
            'weight_history': [(dt.isoformat(), weight) for dt, weight in self.weight_history],
            'health_records': self.health_records,
            'identification_history': [r.to_dict() for r in self.identification_history],
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CattleProfile':
        """从字典创建"""
        profile = cls(
            cattle_id=data['cattle_id'],
            ear_tag_ids=data.get('ear_tag_ids', []),
            breed=data.get('breed'),
            gender=data.get('gender'),
            health_records=data.get('health_records', []),
            metadata=data.get('metadata', {})
        )
        
        # 解析日期
        if data.get('birth_date'):
            profile.birth_date = datetime.fromisoformat(data['birth_date'])
        if data.get('created_at'):
            profile.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            profile.updated_at = datetime.fromisoformat(data['updated_at'])
        
        # 解析体重历史
        for dt_str, weight in data.get('weight_history', []):
            profile.weight_history.append((datetime.fromisoformat(dt_str), weight))
        
        # 解析花色特征
        for feature_data in data.get('coat_pattern_features', []):
            feature = CoatPatternFeature.from_dict(feature_data)
            profile.coat_pattern_features.append(feature)
        
        # 解析识别历史
        for result_data in data.get('identification_history', []):
            result = IdentificationResult.from_dict(result_data)
            profile.identification_history.append(result)
        
        return profile

class FeatureExtractor:
    """特征提取器基类"""
    
    def __init__(self, method_name: str):
        self.method_name = method_name
    
    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """提取特征向量"""
        raise NotImplementedError
    
    def calculate_image_hash(self, image: np.ndarray) -> str:
        """计算图像哈希"""
        # 简单的图像哈希
        resized = cv2.resize(image, (8, 8))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else resized
        
        # 计算平均值
        avg = gray.mean()
        
        # 生成哈希
        hash_bits = []
        for pixel in gray.flatten():
            hash_bits.append('1' if pixel > avg else '0')
        
        hash_str = ''.join(hash_bits)
        return hashlib.md5(hash_str.encode()).hexdigest()

class SimilarityMatcher:
    """相似度匹配器"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
    
    def find_best_match(self, 
                       query_feature: CoatPatternFeature,
                       candidate_profiles: List[CattleProfile]) -> Tuple[Optional[str], float]:
        """找到最佳匹配"""
        best_match_id = None
        best_similarity = 0.0
        
        for profile in candidate_profiles:
            for feature in profile.coat_pattern_features:
                similarity = query_feature.similarity(feature)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_id = profile.cattle_id
        
        if best_similarity >= self.similarity_threshold:
            return best_match_id, best_similarity
        else:
            return None, best_similarity
    
    def find_top_matches(self,
                        query_feature: CoatPatternFeature,
                        candidate_profiles: List[CattleProfile],
                        top_k: int = 5) -> List[Tuple[str, float]]:
        """找到前K个最佳匹配"""
        matches = []
        
        for profile in candidate_profiles:
            best_similarity = 0.0
            for feature in profile.coat_pattern_features:
                similarity = query_feature.similarity(feature)
                if similarity > best_similarity:
                    best_similarity = similarity
            
            if best_similarity > 0:
                matches.append((profile.cattle_id, best_similarity))
        
        # 按相似度排序
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches[:top_k]

def validate_ear_tag_format(ear_tag_id: str) -> bool:
    """验证耳标格式"""
    if not ear_tag_id:
        return False
    
    # 移除空白字符
    ear_tag_id = ear_tag_id.strip()
    
    # 基本长度检查
    if len(ear_tag_id) < 2 or len(ear_tag_id) > 20:
        return False
    
    # 检查是否包含有效字符（数字、字母、连字符）
    import re
    if not re.match(r'^[A-Za-z0-9\-]+$', ear_tag_id):
        return False
    
    return True

def normalize_ear_tag_id(ear_tag_id: str) -> str:
    """标准化耳标ID"""
    if not ear_tag_id:
        return ""
    
    # 移除空白字符并转换为大写
    normalized = ear_tag_id.strip().upper()
    
    # 移除特殊字符（保留字母数字和连字符）
    import re
    normalized = re.sub(r'[^A-Z0-9\-]', '', normalized)
    
    return normalized

# 导入OpenCV（如果可用）
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False