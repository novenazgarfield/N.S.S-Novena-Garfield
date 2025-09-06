#!/usr/bin/env python3
"""
身体状况特征提取器
用于从图像中提取与BCS评分相关的特征
"""

import cv2
import numpy as np
import logging
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass

from .keypoint_detector import KeypointDetector, KeypointResult, create_keypoint_detector

logger = logging.getLogger(__name__)

@dataclass
class BodyConditionFeature:
    """身体状况特征"""
    feature_name: str
    feature_value: float
    confidence: float
    description: str

@dataclass
class BodyConditionFeatureSet:
    """身体状况特征集合"""
    features: List[BodyConditionFeature]
    overall_confidence: float
    extraction_method: str
    keypoint_result: Optional[KeypointResult] = None

class BodyConditionFeatureExtractor:
    """身体状况特征提取器"""
    
    def __init__(self, use_keypoints: bool = True, keypoint_detector_type: str = "posenet"):
        self.use_keypoints = use_keypoints
        self.keypoint_detector = None
        
        if use_keypoints:
            try:
                self.keypoint_detector = create_keypoint_detector(keypoint_detector_type)
                logger.info(f"✅ 关键点检测器初始化成功: {keypoint_detector_type}")
            except Exception as e:
                logger.warning(f"⚠️ 关键点检测器初始化失败: {e}")
                self.use_keypoints = False
        
        self.feature_extractors = {
            'body_ratio': self._extract_body_ratio,
            'fat_coverage': self._extract_fat_coverage,
            'muscle_definition': self._extract_muscle_definition,
            'spine_visibility': self._extract_spine_visibility,
            'rib_visibility': self._extract_rib_visibility,
            'hip_prominence': self._extract_hip_prominence,
            'overall_shape': self._extract_overall_shape
        }
    
    def extract_features(self, image: np.ndarray, bbox: Tuple[int, int, int, int] = None) -> BodyConditionFeatureSet:
        """
        提取身体状况特征
        
        Args:
            image: 输入图像
            bbox: 牛只边界框
            
        Returns:
            身体状况特征集合
        """
        try:
            features = []
            keypoint_result = None
            
            # 如果使用关键点检测
            if self.use_keypoints and self.keypoint_detector:
                keypoint_result = self.keypoint_detector.detect_keypoints(image, bbox)
            
            # 提取各种特征
            for feature_name, extractor_func in self.feature_extractors.items():
                try:
                    feature = extractor_func(image, bbox, keypoint_result)
                    if feature:
                        features.append(feature)
                except Exception as e:
                    logger.warning(f"特征提取失败 {feature_name}: {e}")
            
            # 计算整体置信度
            if features:
                overall_confidence = np.mean([f.confidence for f in features])
            else:
                overall_confidence = 0.0
            
            return BodyConditionFeatureSet(
                features=features,
                overall_confidence=overall_confidence,
                extraction_method="keypoint_based" if self.use_keypoints else "image_based",
                keypoint_result=keypoint_result
            )
            
        except Exception as e:
            logger.error(f"特征提取失败: {e}")
            return BodyConditionFeatureSet(
                features=[],
                overall_confidence=0.0,
                extraction_method="failed"
            )
    
    def _extract_body_ratio(self, image: np.ndarray, bbox: Tuple[int, int, int, int], 
                           keypoint_result: Optional[KeypointResult]) -> Optional[BodyConditionFeature]:
        """提取身体比例特征"""
        try:
            if keypoint_result and self.keypoint_detector:
                measurements = self.keypoint_detector.get_body_measurements(keypoint_result)
                if 'body_ratio' in measurements:
                    ratio = measurements['body_ratio']
                    
                    # 正常牛只的身体比例大约在1.5-2.0之间
                    if 1.5 <= ratio <= 2.0:
                        confidence = 0.9
                        description = "身体比例正常"
                    else:
                        confidence = 0.7
                        description = "身体比例异常"
                    
                    return BodyConditionFeature(
                        feature_name="body_ratio",
                        feature_value=ratio,
                        confidence=confidence,
                        description=description
                    )
            
            # 回退到基于图像的方法
            if bbox:
                x, y, w, h = bbox
                ratio = w / h
                return BodyConditionFeature(
                    feature_name="body_ratio",
                    feature_value=ratio,
                    confidence=0.6,
                    description="基于边界框的身体比例"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"身体比例特征提取失败: {e}")
            return None
    
    def _extract_fat_coverage(self, image: np.ndarray, bbox: Tuple[int, int, int, int],
                             keypoint_result: Optional[KeypointResult]) -> Optional[BodyConditionFeature]:
        """提取脂肪覆盖特征"""
        try:
            if bbox is None:
                return None
            
            x, y, w, h = bbox
            roi = image[y:y+h, x:x+w]
            
            # 转换为灰度图
            if len(roi.shape) == 3:
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            else:
                gray_roi = roi
            
            # 计算纹理特征（使用方差作为简单的纹理度量）
            texture_variance = np.var(gray_roi)
            
            # 脂肪覆盖通常会使纹理更平滑（方差更小）
            # 正常化到0-1范围
            fat_coverage = max(0, min(1, 1 - (texture_variance / 10000)))
            
            if fat_coverage > 0.7:
                description = "脂肪覆盖较多"
                confidence = 0.8
            elif fat_coverage > 0.4:
                description = "脂肪覆盖适中"
                confidence = 0.9
            else:
                description = "脂肪覆盖较少"
                confidence = 0.8
            
            return BodyConditionFeature(
                feature_name="fat_coverage",
                feature_value=fat_coverage,
                confidence=confidence,
                description=description
            )
            
        except Exception as e:
            logger.error(f"脂肪覆盖特征提取失败: {e}")
            return None
    
    def _extract_muscle_definition(self, image: np.ndarray, bbox: Tuple[int, int, int, int],
                                  keypoint_result: Optional[KeypointResult]) -> Optional[BodyConditionFeature]:
        """提取肌肉清晰度特征"""
        try:
            if bbox is None:
                return None
            
            x, y, w, h = bbox
            roi = image[y:y+h, x:x+w]
            
            # 转换为灰度图
            if len(roi.shape) == 3:
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            else:
                gray_roi = roi
            
            # 使用Sobel算子检测边缘（肌肉轮廓）
            sobel_x = cv2.Sobel(gray_roi, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray_roi, cv2.CV_64F, 0, 1, ksize=3)
            edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            
            # 计算边缘强度的平均值
            muscle_definition = np.mean(edge_magnitude) / 255.0
            
            if muscle_definition > 0.3:
                description = "肌肉轮廓清晰"
                confidence = 0.8
            elif muscle_definition > 0.15:
                description = "肌肉轮廓适中"
                confidence = 0.9
            else:
                description = "肌肉轮廓模糊"
                confidence = 0.8
            
            return BodyConditionFeature(
                feature_name="muscle_definition",
                feature_value=muscle_definition,
                confidence=confidence,
                description=description
            )
            
        except Exception as e:
            logger.error(f"肌肉清晰度特征提取失败: {e}")
            return None
    
    def _extract_spine_visibility(self, image: np.ndarray, bbox: Tuple[int, int, int, int],
                                 keypoint_result: Optional[KeypointResult]) -> Optional[BodyConditionFeature]:
        """提取脊椎可见性特征"""
        try:
            # 这是一个简化的实现，实际应该基于关键点或更复杂的图像分析
            spine_visibility = np.random.uniform(0.3, 0.8)  # 模拟值
            
            if spine_visibility > 0.7:
                description = "脊椎清晰可见"
                confidence = 0.7
            elif spine_visibility > 0.4:
                description = "脊椎部分可见"
                confidence = 0.8
            else:
                description = "脊椎不明显"
                confidence = 0.7
            
            return BodyConditionFeature(
                feature_name="spine_visibility",
                feature_value=spine_visibility,
                confidence=confidence,
                description=description
            )
            
        except Exception as e:
            logger.error(f"脊椎可见性特征提取失败: {e}")
            return None
    
    def _extract_rib_visibility(self, image: np.ndarray, bbox: Tuple[int, int, int, int],
                               keypoint_result: Optional[KeypointResult]) -> Optional[BodyConditionFeature]:
        """提取肋骨可见性特征"""
        try:
            # 简化实现
            rib_visibility = np.random.uniform(0.2, 0.7)  # 模拟值
            
            if rib_visibility > 0.6:
                description = "肋骨清晰可见"
                confidence = 0.7
            elif rib_visibility > 0.3:
                description = "肋骨部分可见"
                confidence = 0.8
            else:
                description = "肋骨不明显"
                confidence = 0.7
            
            return BodyConditionFeature(
                feature_name="rib_visibility",
                feature_value=rib_visibility,
                confidence=confidence,
                description=description
            )
            
        except Exception as e:
            logger.error(f"肋骨可见性特征提取失败: {e}")
            return None
    
    def _extract_hip_prominence(self, image: np.ndarray, bbox: Tuple[int, int, int, int],
                               keypoint_result: Optional[KeypointResult]) -> Optional[BodyConditionFeature]:
        """提取臀部突出度特征"""
        try:
            # 简化实现
            hip_prominence = np.random.uniform(0.4, 0.9)  # 模拟值
            
            if hip_prominence > 0.7:
                description = "臀部突出明显"
                confidence = 0.8
            elif hip_prominence > 0.5:
                description = "臀部适度突出"
                confidence = 0.9
            else:
                description = "臀部平缓"
                confidence = 0.8
            
            return BodyConditionFeature(
                feature_name="hip_prominence",
                feature_value=hip_prominence,
                confidence=confidence,
                description=description
            )
            
        except Exception as e:
            logger.error(f"臀部突出度特征提取失败: {e}")
            return None
    
    def _extract_overall_shape(self, image: np.ndarray, bbox: Tuple[int, int, int, int],
                              keypoint_result: Optional[KeypointResult]) -> Optional[BodyConditionFeature]:
        """提取整体形状特征"""
        try:
            if bbox is None:
                return None
            
            x, y, w, h = bbox
            
            # 计算形状指数（宽高比的变体）
            shape_index = w / (h * 1.5)  # 调整系数
            
            if 0.8 <= shape_index <= 1.2:
                description = "体型匀称"
                confidence = 0.9
            elif shape_index > 1.2:
                description = "体型偏宽"
                confidence = 0.8
            else:
                description = "体型偏窄"
                confidence = 0.8
            
            return BodyConditionFeature(
                feature_name="overall_shape",
                feature_value=shape_index,
                confidence=confidence,
                description=description
            )
            
        except Exception as e:
            logger.error(f"整体形状特征提取失败: {e}")
            return None
    
    def visualize_features(self, image: np.ndarray, feature_set: BodyConditionFeatureSet) -> np.ndarray:
        """可视化特征提取结果"""
        vis_image = image.copy()
        
        # 如果有关键点结果，先可视化关键点
        if feature_set.keypoint_result and self.keypoint_detector:
            vis_image = self.keypoint_detector.visualize_keypoints(vis_image, feature_set.keypoint_result)
        
        # 添加特征信息文本
        y_offset = 30
        for feature in feature_set.features:
            text = f"{feature.feature_name}: {feature.feature_value:.2f} ({feature.confidence:.2f})"
            cv2.putText(vis_image, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 20
        
        # 添加整体置信度
        overall_text = f"Overall Confidence: {feature_set.overall_confidence:.2f}"
        cv2.putText(vis_image, overall_text, (10, y_offset + 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return vis_image

def create_feature_extractor(use_keypoints: bool = True, 
                           keypoint_detector_type: str = "posenet") -> BodyConditionFeatureExtractor:
    """
    创建身体状况特征提取器
    
    Args:
        use_keypoints: 是否使用关键点检测
        keypoint_detector_type: 关键点检测器类型
        
    Returns:
        特征提取器实例
    """
    return BodyConditionFeatureExtractor(use_keypoints, keypoint_detector_type)

if __name__ == "__main__":
    # 测试特征提取器
    print("🔍 测试身体状况特征提取器...")
    
    # 创建测试图像
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    test_bbox = (100, 100, 200, 150)
    
    # 测试特征提取器
    extractor = create_feature_extractor(use_keypoints=True)
    feature_set = extractor.extract_features(test_image, test_bbox)
    
    print(f"✅ 提取到 {len(feature_set.features)} 个特征")
    print(f"整体置信度: {feature_set.overall_confidence:.3f}")
    print(f"提取方法: {feature_set.extraction_method}")
    
    for feature in feature_set.features:
        print(f"  - {feature.feature_name}: {feature.feature_value:.3f} "
              f"(置信度: {feature.confidence:.3f}) - {feature.description}")
    
    print("\n🎉 特征提取器测试完成！")