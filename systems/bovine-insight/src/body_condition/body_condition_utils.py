"""
体况评分工具类
Body Condition Scoring Utilities

定义体况评分相关的数据结构和工具函数
集成GLM-4V文本分析功能
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import cv2
import logging

# 导入GLM-4V文本分析服务
try:
    from ..text_analysis.bovine_description_service import BovineDescriptionService
    GLM4V_AVAILABLE = True
except ImportError:
    GLM4V_AVAILABLE = False
    logging.warning("GLM-4V文本分析服务不可用")

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


class EnhancedBCSAnalyzer:
    """
    增强的BCS分析器
    集成DINOv2特征提取和GLM-4V文本分析
    """
    
    def __init__(self, 
                 use_dinov2: bool = True,
                 use_glm4v: bool = True,
                 model_cache_dir: Optional[str] = None):
        """
        初始化增强BCS分析器
        
        Args:
            use_dinov2: 是否使用DINOv2特征提取
            use_glm4v: 是否使用GLM-4V文本分析
            model_cache_dir: 模型缓存目录
        """
        self.use_dinov2 = use_dinov2
        self.use_glm4v = use_glm4v
        
        # 初始化DINOv2特征提取器
        self.dinov2_extractor = None
        if use_dinov2:
            try:
                from ..feature_extraction.feature_extractor import DINOv2FeatureExtractor
                self.dinov2_extractor = DINOv2FeatureExtractor(
                    model_name='dinov2_vitb14',
                    cache_dir=model_cache_dir
                )
                logging.info("DINOv2特征提取器初始化成功")
            except Exception as e:
                logging.warning(f"DINOv2初始化失败: {str(e)}")
                self.use_dinov2 = False
        
        # 初始化GLM-4V文本分析服务
        self.text_analyzer = None
        if use_glm4v and GLM4V_AVAILABLE:
            try:
                self.text_analyzer = BovineDescriptionService(cache_dir=model_cache_dir)
                logging.info("GLM-4V文本分析服务初始化成功")
            except Exception as e:
                logging.warning(f"GLM-4V初始化失败: {str(e)}")
                self.use_glm4v = False
        
        # 传统BCS评分器
        self.traditional_scorer = BCSScorer()
        
        # 统计信息
        self.stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'feature_extraction_time': 0.0,
            'text_generation_time': 0.0
        }
    
    def analyze_body_condition(self, 
                              image: np.ndarray,
                              region: str = "tail_head",
                              generate_report: bool = True) -> Dict[str, Any]:
        """
        综合分析牛只体况
        
        Args:
            image: 牛只图像
            region: 评估区域
            generate_report: 是否生成文本报告
            
        Returns:
            综合分析结果
        """
        self.stats['total_analyses'] += 1
        
        try:
            # 1. 传统BCS评分
            traditional_result = self._traditional_bcs_analysis(image, region)
            
            # 2. DINOv2特征提取
            dinov2_features = None
            if self.use_dinov2 and self.dinov2_extractor:
                try:
                    dinov2_features = self.dinov2_extractor.extract_features(image)
                    logging.info(f"DINOv2特征提取成功，维度: {dinov2_features.shape}")
                except Exception as e:
                    logging.warning(f"DINOv2特征提取失败: {str(e)}")
            
            # 3. 基于特征的BCS预测
            feature_based_score = None
            if dinov2_features is not None:
                feature_based_score = self._predict_bcs_from_features(dinov2_features, region)
            
            # 4. 融合评分
            final_score = self._fuse_bcs_scores(
                traditional_result.bcs_score,
                feature_based_score
            )
            
            # 5. 生成文本报告
            text_report = None
            if generate_report and self.use_glm4v and self.text_analyzer:
                try:
                    text_report = self.text_analyzer.generate_bcs_description(
                        image, final_score, region
                    )
                    logging.info("GLM-4V文本报告生成成功")
                except Exception as e:
                    logging.warning(f"文本报告生成失败: {str(e)}")
            
            # 6. 构建综合结果
            comprehensive_result = {
                'final_bcs_score': final_score,
                'bcs_category': self._score_to_category(final_score),
                'region': region,
                'analysis_timestamp': np.datetime64('now'),
                
                # 各种分析结果
                'traditional_analysis': {
                    'score': traditional_result.bcs_score,
                    'category': traditional_result.bcs_category.value,
                    'confidence': traditional_result.confidence,
                    'keypoints': traditional_result.anatomical_keypoints
                },
                
                'feature_analysis': {
                    'dinov2_available': self.use_dinov2,
                    'feature_based_score': feature_based_score,
                    'feature_dimension': dinov2_features.shape[0] if dinov2_features is not None else 0
                },
                
                'text_analysis': text_report,
                
                # 质量评估
                'analysis_quality': self._assess_analysis_quality(
                    traditional_result, dinov2_features, text_report
                ),
                
                # 建议
                'recommendations': self._generate_enhanced_recommendations(
                    final_score, traditional_result, text_report
                ),
                
                # 元数据
                'metadata': {
                    'image_shape': image.shape,
                    'analysis_methods': self._get_active_methods(),
                    'model_versions': self._get_model_versions()
                }
            }
            
            self.stats['successful_analyses'] += 1
            return comprehensive_result
            
        except Exception as e:
            logging.error(f"综合BCS分析失败: {str(e)}")
            return {
                'error': str(e),
                'final_bcs_score': None,
                'analysis_timestamp': np.datetime64('now')
            }
    
    def batch_analyze_body_condition(self, 
                                    images_data: List[Tuple[np.ndarray, str]],
                                    generate_reports: bool = True) -> List[Dict[str, Any]]:
        """
        批量分析体况
        
        Args:
            images_data: 图像数据列表 [(image, region), ...]
            generate_reports: 是否生成文本报告
            
        Returns:
            批量分析结果列表
        """
        results = []
        
        for i, (image, region) in enumerate(images_data):
            try:
                result = self.analyze_body_condition(
                    image, region, generate_reports
                )
                result['batch_index'] = i
                results.append(result)
                
                logging.info(f"批量分析进度: {i+1}/{len(images_data)}")
                
            except Exception as e:
                logging.error(f"批量分析第{i+1}项失败: {str(e)}")
                results.append({
                    'batch_index': i,
                    'error': str(e),
                    'final_bcs_score': None
                })
        
        return results
    
    def _traditional_bcs_analysis(self, image: np.ndarray, region: str) -> BCSResult:
        """传统BCS分析"""
        # 使用传统方法进行BCS评分
        keypoints = self._extract_anatomical_keypoints(image, region)
        score = self.traditional_scorer.calculate_bcs_score(image, keypoints)
        
        return BCSResult(
            bcs_score=score,
            bcs_category=self._score_to_category(score),
            confidence=0.8,  # 传统方法的置信度
            anatomical_keypoints=keypoints,
            region_scores={region: score},
            metadata={'method': 'traditional'}
        )
    
    def _extract_anatomical_keypoints(self, image: np.ndarray, region: str) -> AnatomicalKeypoints:
        """提取解剖学关键点"""
        # 简化的关键点提取逻辑
        keypoints = AnatomicalKeypoints()
        
        # 基于图像处理的关键点检测
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # 使用边缘检测找到可能的骨骼轮廓
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 根据区域类型提取相应的关键点
        if region == "tail_head":
            # 尾根和髋骨区域的关键点
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                moments = cv2.moments(largest_contour)
                if moments['m00'] != 0:
                    cx = int(moments['m10'] / moments['m00'])
                    cy = int(moments['m01'] / moments['m00'])
                    keypoints.tail_base = (cx, cy)
        
        elif region == "ribs":
            # 肋骨区域的关键点
            for contour in contours[:5]:  # 取前5个轮廓
                moments = cv2.moments(contour)
                if moments['m00'] != 0:
                    cx = int(moments['m10'] / moments['m00'])
                    cy = int(moments['m01'] / moments['m00'])
                    keypoints.rib_points.append((cx, cy))
        
        return keypoints
    
    def _predict_bcs_from_features(self, features: np.ndarray, region: str) -> Optional[float]:
        """基于DINOv2特征预测BCS评分"""
        try:
            # 这里应该使用训练好的回归模型
            # 为了演示，使用简化的特征映射
            
            # 计算特征统计量
            feature_mean = np.mean(features)
            feature_std = np.std(features)
            feature_norm = np.linalg.norm(features)
            
            # 简化的评分映射（实际应用中需要训练专门的模型）
            # 基于特征的统计特性估算BCS评分
            if feature_norm < 10:
                base_score = 2.0  # 偏瘦
            elif feature_norm < 15:
                base_score = 3.0  # 中等
            elif feature_norm < 20:
                base_score = 4.0  # 良好
            else:
                base_score = 4.5  # 偏胖
            
            # 根据特征均值和标准差进行微调
            adjustment = (feature_mean - 0.5) * 0.5 + (feature_std - 0.2) * 0.3
            predicted_score = np.clip(base_score + adjustment, 1.0, 5.0)
            
            return float(predicted_score)
            
        except Exception as e:
            logging.warning(f"基于特征的BCS预测失败: {str(e)}")
            return None
    
    def _fuse_bcs_scores(self, 
                        traditional_score: float,
                        feature_score: Optional[float]) -> float:
        """融合不同方法的BCS评分"""
        if feature_score is None:
            return traditional_score
        
        # 加权融合
        traditional_weight = 0.6
        feature_weight = 0.4
        
        fused_score = (traditional_weight * traditional_score + 
                      feature_weight * feature_score)
        
        return np.clip(fused_score, 1.0, 5.0)
    
    def _score_to_category(self, score: float) -> BCSCategory:
        """将评分转换为类别"""
        if score < 1.75:
            return BCSCategory.VERY_THIN
        elif score < 2.75:
            return BCSCategory.THIN
        elif score < 3.75:
            return BCSCategory.MODERATE
        elif score < 4.25:
            return BCSCategory.GOOD
        else:
            return BCSCategory.OBESE
    
    def _assess_analysis_quality(self, 
                               traditional_result: BCSResult,
                               dinov2_features: Optional[np.ndarray],
                               text_report: Optional[Dict]) -> Dict[str, float]:
        """评估分析质量"""
        quality_scores = {}
        
        # 传统方法质量
        quality_scores['traditional_quality'] = traditional_result.confidence
        
        # 特征提取质量
        if dinov2_features is not None:
            feature_quality = min(np.linalg.norm(dinov2_features) / 20.0, 1.0)
            quality_scores['feature_quality'] = feature_quality
        else:
            quality_scores['feature_quality'] = 0.0
        
        # 文本分析质量
        if text_report:
            text_quality = 1.0 if 'expert_description' in text_report else 0.5
            quality_scores['text_quality'] = text_quality
        else:
            quality_scores['text_quality'] = 0.0
        
        # 综合质量
        quality_scores['overall_quality'] = np.mean(list(quality_scores.values()))
        
        return quality_scores
    
    def _generate_enhanced_recommendations(self, 
                                         final_score: float,
                                         traditional_result: BCSResult,
                                         text_report: Optional[Dict]) -> List[str]:
        """生成增强的建议"""
        recommendations = []
        
        # 基础建议
        basic_recommendations = generate_bcs_recommendations(traditional_result)
        recommendations.extend(basic_recommendations)
        
        # 基于文本分析的建议
        if text_report and 'professional_advice' in text_report:
            recommendations.append(f"专家建议: {text_report['professional_advice']}")
        
        # 基于综合评分的额外建议
        if final_score < 2.5:
            recommendations.append("建议进行兽医检查，排除疾病因素")
        elif final_score > 4.5:
            recommendations.append("建议制定减重计划，预防代谢疾病")
        
        return recommendations
    
    def _get_active_methods(self) -> List[str]:
        """获取活跃的分析方法"""
        methods = ['traditional']
        
        if self.use_dinov2:
            methods.append('dinov2')
        
        if self.use_glm4v:
            methods.append('glm4v')
        
        return methods
    
    def _get_model_versions(self) -> Dict[str, str]:
        """获取模型版本信息"""
        versions = {'traditional': '1.0'}
        
        if self.dinov2_extractor:
            versions['dinov2'] = self.dinov2_extractor.model_name
        
        if self.text_analyzer:
            versions['glm4v'] = self.text_analyzer.model_name
        
        return versions
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """获取分析统计信息"""
        stats = self.stats.copy()
        
        if stats['total_analyses'] > 0:
            stats['success_rate'] = stats['successful_analyses'] / stats['total_analyses']
        else:
            stats['success_rate'] = 0.0
        
        stats['active_methods'] = self._get_active_methods()
        stats['model_versions'] = self._get_model_versions()
        
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'feature_extraction_time': 0.0,
            'text_generation_time': 0.0
        }


# 工厂函数
def create_enhanced_bcs_analyzer(**kwargs) -> EnhancedBCSAnalyzer:
    """
    创建增强BCS分析器
    
    Args:
        **kwargs: 配置参数
        
    Returns:
        增强BCS分析器实例
    """
    return EnhancedBCSAnalyzer(**kwargs)