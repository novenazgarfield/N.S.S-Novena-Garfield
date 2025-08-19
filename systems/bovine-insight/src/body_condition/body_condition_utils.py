"""
体况评分工具类
Body Condition Scoring Utilities

定义体况评分相关的数据结构和工具函数
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import cv2

class BCSScale(Enum):
    """体况评分标准"""
    SCALE_1_5 = "1-5"      # 1-5分制
    SCALE_1_9 = "1-9"      # 1-9分制

class BCSCategory(Enum):
    """体况分类"""
    VERY_THIN = "very_thin"        # 极瘦 (1.0-1.5)
    THIN = "thin"                  # 瘦 (1.5-2.5)
    MODERATE = "moderate"          # 适中 (2.5-3.5)
    GOOD = "good"                  # 良好 (3.5-4.5)
    OBESE = "obese"                # 肥胖 (4.5-5.0)

@dataclass
class AnatomicalKeypoints:
    """解剖学关键点"""
    # 脊椎相关
    spine_points: List[Tuple[float, float]] = field(default_factory=list)
    
    # 髋骨相关
    hip_bone_left: Optional[Tuple[float, float]] = None
    hip_bone_right: Optional[Tuple[float, float]] = None
    
    # 尾根
    tail_base: Optional[Tuple[float, float]] = None
    
    # 肋骨
    rib_points: List[Tuple[float, float]] = field(default_factory=list)
    
    # 肩胛骨
    shoulder_blade_left: Optional[Tuple[float, float]] = None
    shoulder_blade_right: Optional[Tuple[float, float]] = None
    
    # 腰椎
    lumbar_points: List[Tuple[float, float]] = field(default_factory=list)
    
    # 置信度
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    
    def get_all_points(self) -> List[Tuple[float, float]]:
        """获取所有关键点"""
        points = []
        points.extend(self.spine_points)
        points.extend(self.rib_points)
        points.extend(self.lumbar_points)
        
        if self.hip_bone_left:
            points.append(self.hip_bone_left)
        if self.hip_bone_right:
            points.append(self.hip_bone_right)
        if self.tail_base:
            points.append(self.tail_base)
        if self.shoulder_blade_left:
            points.append(self.shoulder_blade_left)
        if self.shoulder_blade_right:
            points.append(self.shoulder_blade_right)
        
        return points
    
    def get_keypoint_count(self) -> int:
        """获取检测到的关键点数量"""
        return len(self.get_all_points())
    
    def get_average_confidence(self) -> float:
        """获取平均置信度"""
        if not self.confidence_scores:
            return 0.0
        return np.mean(list(self.confidence_scores.values()))

@dataclass
class GeometricFeatures:
    """几何特征"""
    # 距离特征
    spine_length: float = 0.0
    hip_width: float = 0.0
    rib_depth: float = 0.0
    
    # 角度特征
    spine_curvature: float = 0.0
    hip_angle: float = 0.0
    
    # 面积特征
    body_area: float = 0.0
    hip_area: float = 0.0
    
    # 比例特征
    length_width_ratio: float = 0.0
    depth_width_ratio: float = 0.0
    
    # 轮廓特征
    contour_smoothness: float = 0.0
    contour_convexity: float = 0.0
    
    # 纹理特征
    fat_coverage_score: float = 0.0
    muscle_definition_score: float = 0.0
    
    def to_feature_vector(self) -> np.ndarray:
        """转换为特征向量"""
        features = [
            self.spine_length,
            self.hip_width,
            self.rib_depth,
            self.spine_curvature,
            self.hip_angle,
            self.body_area,
            self.hip_area,
            self.length_width_ratio,
            self.depth_width_ratio,
            self.contour_smoothness,
            self.contour_convexity,
            self.fat_coverage_score,
            self.muscle_definition_score
        ]
        return np.array(features, dtype=np.float32)
    
    @classmethod
    def from_feature_vector(cls, vector: np.ndarray) -> 'GeometricFeatures':
        """从特征向量创建"""
        if len(vector) < 13:
            vector = np.pad(vector, (0, 13 - len(vector)), 'constant')
        
        return cls(
            spine_length=float(vector[0]),
            hip_width=float(vector[1]),
            rib_depth=float(vector[2]),
            spine_curvature=float(vector[3]),
            hip_angle=float(vector[4]),
            body_area=float(vector[5]),
            hip_area=float(vector[6]),
            length_width_ratio=float(vector[7]),
            depth_width_ratio=float(vector[8]),
            contour_smoothness=float(vector[9]),
            contour_convexity=float(vector[10]),
            fat_coverage_score=float(vector[11]),
            muscle_definition_score=float(vector[12])
        )

@dataclass
class BCSResult:
    """体况评分结果"""
    bcs_score: float
    bcs_category: BCSCategory
    confidence: float
    keypoints: Optional[AnatomicalKeypoints] = None
    geometric_features: Optional[GeometricFeatures] = None
    scale: BCSScale = BCSScale.SCALE_1_5
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """后处理"""
        # 根据分数确定类别
        if self.scale == BCSScale.SCALE_1_5:
            if self.bcs_score <= 1.5:
                self.bcs_category = BCSCategory.VERY_THIN
            elif self.bcs_score <= 2.5:
                self.bcs_category = BCSCategory.THIN
            elif self.bcs_score <= 3.5:
                self.bcs_category = BCSCategory.MODERATE
            elif self.bcs_score <= 4.5:
                self.bcs_category = BCSCategory.GOOD
            else:
                self.bcs_category = BCSCategory.OBESE
    
    def get_description(self) -> str:
        """获取描述"""
        descriptions = {
            BCSCategory.VERY_THIN: "极瘦 - 骨骼突出明显，无脂肪覆盖",
            BCSCategory.THIN: "瘦 - 骨骼可见，脂肪覆盖少",
            BCSCategory.MODERATE: "适中 - 骨骼轮廓可触及，脂肪覆盖适度",
            BCSCategory.GOOD: "良好 - 骨骼不易触及，脂肪覆盖良好",
            BCSCategory.OBESE: "肥胖 - 骨骼难以触及，脂肪覆盖过厚"
        }
        return descriptions.get(self.bcs_category, "未知")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            'bcs_score': self.bcs_score,
            'bcs_category': self.bcs_category.value,
            'confidence': self.confidence,
            'scale': self.scale.value,
            'description': self.get_description(),
            'metadata': self.metadata
        }
        
        if self.keypoints:
            result['keypoints'] = {
                'spine_points': self.keypoints.spine_points,
                'hip_bone_left': self.keypoints.hip_bone_left,
                'hip_bone_right': self.keypoints.hip_bone_right,
                'tail_base': self.keypoints.tail_base,
                'rib_points': self.keypoints.rib_points,
                'keypoint_count': self.keypoints.get_keypoint_count(),
                'average_confidence': self.keypoints.get_average_confidence()
            }
        
        if self.geometric_features:
            result['geometric_features'] = {
                'spine_length': self.geometric_features.spine_length,
                'hip_width': self.geometric_features.hip_width,
                'rib_depth': self.geometric_features.rib_depth,
                'body_area': self.geometric_features.body_area,
                'length_width_ratio': self.geometric_features.length_width_ratio
            }
        
        return result

class ContourAnalyzer:
    """轮廓分析器"""
    
    def __init__(self):
        pass
    
    def extract_body_contour(self, image: np.ndarray, mask: Optional[np.ndarray] = None) -> np.ndarray:
        """提取身体轮廓"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 如果提供了掩码，应用掩码
        if mask is not None:
            gray = cv2.bitwise_and(gray, mask)
        
        # 边缘检测
        edges = cv2.Canny(gray, 50, 150)
        
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return np.array([])
        
        # 选择最大的轮廓
        largest_contour = max(contours, key=cv2.contourArea)
        
        return largest_contour
    
    def calculate_contour_features(self, contour: np.ndarray) -> Dict[str, float]:
        """计算轮廓特征"""
        if len(contour) == 0:
            return {}
        
        features = {}
        
        # 面积和周长
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        features['area'] = area
        features['perimeter'] = perimeter
        
        # 圆形度
        if perimeter > 0:
            features['circularity'] = 4 * np.pi * area / (perimeter * perimeter)
        else:
            features['circularity'] = 0.0
        
        # 凸包
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        
        if hull_area > 0:
            features['convexity'] = area / hull_area
        else:
            features['convexity'] = 0.0
        
        # 边界矩形
        x, y, w, h = cv2.boundingRect(contour)
        features['aspect_ratio'] = float(w) / h if h > 0 else 0.0
        features['extent'] = area / (w * h) if w * h > 0 else 0.0
        
        # 最小外接椭圆
        if len(contour) >= 5:
            ellipse = cv2.fitEllipse(contour)
            features['ellipse_aspect_ratio'] = ellipse[1][0] / ellipse[1][1] if ellipse[1][1] > 0 else 0.0
        
        return features

class GeometricCalculator:
    """几何计算器"""
    
    def __init__(self):
        pass
    
    def calculate_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """计算两点间距离"""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def calculate_angle(self, p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
        """计算三点构成的角度"""
        v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
        v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        
        return np.arccos(cos_angle) * 180 / np.pi
    
    def calculate_spine_curvature(self, spine_points: List[Tuple[float, float]]) -> float:
        """计算脊椎弯曲度"""
        if len(spine_points) < 3:
            return 0.0
        
        # 计算相邻三点的角度变化
        angles = []
        for i in range(1, len(spine_points) - 1):
            angle = self.calculate_angle(spine_points[i-1], spine_points[i], spine_points[i+1])
            angles.append(abs(180 - angle))  # 偏离直线的角度
        
        return np.mean(angles) if angles else 0.0
    
    def calculate_body_proportions(self, keypoints: AnatomicalKeypoints) -> Dict[str, float]:
        """计算身体比例"""
        proportions = {}
        
        # 脊椎长度
        if len(keypoints.spine_points) >= 2:
            spine_length = 0.0
            for i in range(1, len(keypoints.spine_points)):
                spine_length += self.calculate_distance(
                    keypoints.spine_points[i-1], 
                    keypoints.spine_points[i]
                )
            proportions['spine_length'] = spine_length
        
        # 髋骨宽度
        if keypoints.hip_bone_left and keypoints.hip_bone_right:
            hip_width = self.calculate_distance(
                keypoints.hip_bone_left, 
                keypoints.hip_bone_right
            )
            proportions['hip_width'] = hip_width
        
        # 长宽比
        if 'spine_length' in proportions and 'hip_width' in proportions:
            proportions['length_width_ratio'] = proportions['spine_length'] / proportions['hip_width']
        
        return proportions

def normalize_bcs_score(score: float, source_scale: BCSScale, target_scale: BCSScale) -> float:
    """标准化BCS评分"""
    if source_scale == target_scale:
        return score
    
    if source_scale == BCSScale.SCALE_1_5 and target_scale == BCSScale.SCALE_1_9:
        # 1-5 转 1-9
        return 1 + (score - 1) * 8 / 4
    elif source_scale == BCSScale.SCALE_1_9 and target_scale == BCSScale.SCALE_1_5:
        # 1-9 转 1-5
        return 1 + (score - 1) * 4 / 8
    
    return score

def validate_bcs_score(score: float, scale: BCSScale) -> bool:
    """验证BCS评分有效性"""
    if scale == BCSScale.SCALE_1_5:
        return 1.0 <= score <= 5.0
    elif scale == BCSScale.SCALE_1_9:
        return 1.0 <= score <= 9.0
    
    return False

def get_bcs_recommendations(bcs_result: BCSResult) -> List[str]:
    """获取BCS建议"""
    recommendations = []
    
    if bcs_result.bcs_category == BCSCategory.VERY_THIN:
        recommendations.extend([
            "增加饲料营养密度",
            "检查是否有疾病或寄生虫",
            "提供高质量粗饲料",
            "考虑补充精饲料"
        ])
    elif bcs_result.bcs_category == BCSCategory.THIN:
        recommendations.extend([
            "适当增加饲料供给",
            "改善饲料质量",
            "确保充足的饮水"
        ])
    elif bcs_result.bcs_category == BCSCategory.MODERATE:
        recommendations.extend([
            "维持当前饲养管理",
            "定期监测体况变化"
        ])
    elif bcs_result.bcs_category == BCSCategory.GOOD:
        recommendations.extend([
            "体况良好，继续保持",
            "注意防止过度肥胖"
        ])
    elif bcs_result.bcs_category == BCSCategory.OBESE:
        recommendations.extend([
            "减少精饲料供给",
            "增加运动量",
            "控制饲料摄入量",
            "监测代谢疾病风险"
        ])
    
    return recommendations