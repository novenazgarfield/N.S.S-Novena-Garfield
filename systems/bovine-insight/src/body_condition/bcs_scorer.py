#!/usr/bin/env python3
"""
BCS评分器
基于身体状况特征计算Body Condition Score (BCS)
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from .feature_extractor import BodyConditionFeatureSet, BodyConditionFeature, create_feature_extractor

logger = logging.getLogger(__name__)

class BCSCategory(Enum):
    """BCS分类"""
    VERY_THIN = "very_thin"      # 1.0-1.5
    THIN = "thin"                # 1.5-2.5
    MODERATE = "moderate"        # 2.5-3.5
    GOOD = "good"               # 3.5-4.5
    OBESE = "obese"             # 4.5-5.0

@dataclass
class BCSResult:
    """BCS评分结果"""
    score: float                    # BCS评分 (1.0-5.0)
    category: BCSCategory          # BCS分类
    confidence: float              # 置信度 (0.0-1.0)
    feature_contributions: Dict[str, float]  # 各特征的贡献度
    recommendations: List[str]     # 建议
    scoring_method: str           # 评分方法

class BCSScorer:
    """BCS评分器"""
    
    def __init__(self, scoring_method: str = "feature_based"):
        self.scoring_method = scoring_method
        self.feature_extractor = create_feature_extractor(use_keypoints=True)
        
        # 特征权重配置
        self.feature_weights = {
            'body_ratio': 0.15,
            'fat_coverage': 0.25,
            'muscle_definition': 0.20,
            'spine_visibility': 0.15,
            'rib_visibility': 0.15,
            'hip_prominence': 0.10
        }
        
        # BCS分类阈值
        self.bcs_thresholds = {
            BCSCategory.VERY_THIN: (1.0, 1.5),
            BCSCategory.THIN: (1.5, 2.5),
            BCSCategory.MODERATE: (2.5, 3.5),
            BCSCategory.GOOD: (3.5, 4.5),
            BCSCategory.OBESE: (4.5, 5.0)
        }
        
        logger.info(f"✅ BCS评分器初始化成功: {scoring_method}")
    
    def score_bcs(self, image: np.ndarray, bbox: Tuple[int, int, int, int] = None) -> BCSResult:
        """
        计算BCS评分
        
        Args:
            image: 输入图像
            bbox: 牛只边界框
            
        Returns:
            BCS评分结果
        """
        try:
            # 提取特征
            feature_set = self.feature_extractor.extract_features(image, bbox)
            
            if not feature_set.features:
                return self._create_default_result("特征提取失败")
            
            # 根据评分方法计算BCS
            if self.scoring_method == "feature_based":
                return self._score_by_features(feature_set)
            elif self.scoring_method == "ml_based":
                return self._score_by_ml(feature_set)
            else:
                return self._score_by_simple_rules(feature_set)
                
        except Exception as e:
            logger.error(f"BCS评分失败: {e}")
            return self._create_default_result(f"评分失败: {e}")
    
    def _score_by_features(self, feature_set: BodyConditionFeatureSet) -> BCSResult:
        """基于特征的BCS评分"""
        try:
            feature_dict = {f.feature_name: f for f in feature_set.features}
            feature_contributions = {}
            weighted_score = 0.0
            total_weight = 0.0
            
            # 计算加权评分
            for feature_name, weight in self.feature_weights.items():
                if feature_name in feature_dict:
                    feature = feature_dict[feature_name]
                    
                    # 将特征值转换为BCS贡献
                    bcs_contribution = self._feature_to_bcs_contribution(feature)
                    feature_contributions[feature_name] = bcs_contribution
                    
                    weighted_score += bcs_contribution * weight * feature.confidence
                    total_weight += weight * feature.confidence
            
            # 计算最终BCS评分
            if total_weight > 0:
                final_score = weighted_score / total_weight
            else:
                final_score = 3.0  # 默认中等评分
            
            # 确保评分在有效范围内
            final_score = max(1.0, min(5.0, final_score))
            
            # 确定BCS分类
            category = self._score_to_category(final_score)
            
            # 计算整体置信度
            confidence = feature_set.overall_confidence
            
            # 生成建议
            recommendations = self._generate_recommendations(final_score, category, feature_dict)
            
            return BCSResult(
                score=round(final_score, 1),
                category=category,
                confidence=confidence,
                feature_contributions=feature_contributions,
                recommendations=recommendations,
                scoring_method=self.scoring_method
            )
            
        except Exception as e:
            logger.error(f"基于特征的BCS评分失败: {e}")
            return self._create_default_result(f"特征评分失败: {e}")
    
    def _feature_to_bcs_contribution(self, feature: BodyConditionFeature) -> float:
        """将特征值转换为BCS贡献"""
        feature_name = feature.feature_name
        feature_value = feature.feature_value
        
        if feature_name == "fat_coverage":
            # 脂肪覆盖越多，BCS越高
            return 1.0 + feature_value * 4.0
        
        elif feature_name == "muscle_definition":
            # 肌肉清晰度适中时BCS最佳
            if 0.2 <= feature_value <= 0.4:
                return 3.0 + (0.3 - abs(feature_value - 0.3)) * 3.33
            else:
                return 2.0 + feature_value * 2.0
        
        elif feature_name == "spine_visibility":
            # 脊椎可见性低时BCS较高
            return 5.0 - feature_value * 3.0
        
        elif feature_name == "rib_visibility":
            # 肋骨可见性低时BCS较高
            return 4.5 - feature_value * 3.0
        
        elif feature_name == "hip_prominence":
            # 臀部适度突出时BCS最佳
            if 0.5 <= feature_value <= 0.8:
                return 3.5
            else:
                return 2.0 + feature_value * 2.0
        
        elif feature_name == "body_ratio":
            # 身体比例适中时BCS最佳
            if 1.5 <= feature_value <= 2.0:
                return 3.0 + (1.75 - abs(feature_value - 1.75)) * 4.0
            else:
                return 2.5
        
        else:
            # 默认贡献
            return 2.5 + feature_value * 1.0
    
    def _score_by_ml(self, feature_set: BodyConditionFeatureSet) -> BCSResult:
        """基于机器学习的BCS评分（占位符）"""
        # 这里应该使用训练好的机器学习模型
        # 目前使用简化的规则作为占位符
        return self._score_by_features(feature_set)
    
    def _score_by_simple_rules(self, feature_set: BodyConditionFeatureSet) -> BCSResult:
        """基于简单规则的BCS评分"""
        try:
            feature_dict = {f.feature_name: f for f in feature_set.features}
            
            # 简单规则评分
            score = 3.0  # 基础分数
            
            # 根据脂肪覆盖调整
            if 'fat_coverage' in feature_dict:
                fat_coverage = feature_dict['fat_coverage'].feature_value
                if fat_coverage > 0.7:
                    score += 1.0
                elif fat_coverage < 0.3:
                    score -= 1.0
            
            # 根据肌肉清晰度调整
            if 'muscle_definition' in feature_dict:
                muscle_def = feature_dict['muscle_definition'].feature_value
                if muscle_def > 0.4:
                    score -= 0.5  # 肌肉过于清晰可能表示偏瘦
                elif muscle_def < 0.1:
                    score += 0.5  # 肌肉不清晰可能表示脂肪较多
            
            # 确保评分在有效范围内
            score = max(1.0, min(5.0, score))
            
            category = self._score_to_category(score)
            
            return BCSResult(
                score=round(score, 1),
                category=category,
                confidence=0.7,  # 简单规则的置信度较低
                feature_contributions={f.feature_name: f.feature_value for f in feature_set.features},
                recommendations=self._generate_recommendations(score, category, feature_dict),
                scoring_method=self.scoring_method
            )
            
        except Exception as e:
            logger.error(f"简单规则BCS评分失败: {e}")
            return self._create_default_result(f"规则评分失败: {e}")
    
    def _score_to_category(self, score: float) -> BCSCategory:
        """将BCS评分转换为分类"""
        for category, (min_score, max_score) in self.bcs_thresholds.items():
            if min_score <= score < max_score:
                return category
        
        # 处理边界情况
        if score >= 5.0:
            return BCSCategory.OBESE
        else:
            return BCSCategory.VERY_THIN
    
    def _generate_recommendations(self, score: float, category: BCSCategory, 
                                feature_dict: Dict[str, BodyConditionFeature]) -> List[str]:
        """生成BCS相关建议"""
        recommendations = []
        
        if category == BCSCategory.VERY_THIN:
            recommendations.extend([
                "牛只过于消瘦，需要立即增加营养供应",
                "建议增加高能量饲料和蛋白质补充",
                "检查是否有健康问题或寄生虫感染",
                "考虑兽医检查"
            ])
        
        elif category == BCSCategory.THIN:
            recommendations.extend([
                "牛只偏瘦，建议适当增加饲料供应",
                "提高饲料中的能量密度",
                "监控体重变化趋势"
            ])
        
        elif category == BCSCategory.MODERATE:
            recommendations.extend([
                "牛只体况良好，继续保持当前饲养管理",
                "定期监控BCS变化",
                "根据生产阶段调整营养方案"
            ])
        
        elif category == BCSCategory.GOOD:
            recommendations.extend([
                "牛只体况优良",
                "注意控制饲料供应，避免过肥",
                "适当增加运动量"
            ])
        
        elif category == BCSCategory.OBESE:
            recommendations.extend([
                "牛只过肥，需要控制饲料供应",
                "减少精料比例，增加粗饲料",
                "增加运动量",
                "过肥可能影响繁殖性能，建议调整"
            ])
        
        # 基于特征的额外建议
        if 'spine_visibility' in feature_dict:
            spine_vis = feature_dict['spine_visibility'].feature_value
            if spine_vis > 0.7:
                recommendations.append("脊椎过于明显，建议增加营养")
        
        if 'rib_visibility' in feature_dict:
            rib_vis = feature_dict['rib_visibility'].feature_value
            if rib_vis > 0.6:
                recommendations.append("肋骨过于明显，需要增加体重")
        
        return recommendations
    
    def _create_default_result(self, error_msg: str) -> BCSResult:
        """创建默认的BCS结果"""
        return BCSResult(
            score=3.0,
            category=BCSCategory.MODERATE,
            confidence=0.1,
            feature_contributions={},
            recommendations=[f"评分失败: {error_msg}", "建议人工评估"],
            scoring_method="default"
        )
    
    def batch_score(self, images_and_bboxes: List[Tuple[np.ndarray, Tuple[int, int, int, int]]]) -> List[BCSResult]:
        """批量BCS评分"""
        results = []
        
        for image, bbox in images_and_bboxes:
            try:
                result = self.score_bcs(image, bbox)
                results.append(result)
            except Exception as e:
                logger.error(f"批量评分中的单个图像失败: {e}")
                results.append(self._create_default_result(f"批量评分失败: {e}"))
        
        return results
    
    def get_scoring_statistics(self, results: List[BCSResult]) -> Dict[str, any]:
        """获取评分统计信息"""
        if not results:
            return {}
        
        scores = [r.score for r in results]
        categories = [r.category.value for r in results]
        confidences = [r.confidence for r in results]
        
        stats = {
            'total_count': len(results),
            'average_score': np.mean(scores),
            'median_score': np.median(scores),
            'score_std': np.std(scores),
            'min_score': np.min(scores),
            'max_score': np.max(scores),
            'average_confidence': np.mean(confidences),
            'category_distribution': {cat: categories.count(cat) for cat in set(categories)}
        }
        
        return stats

def create_bcs_scorer(scoring_method: str = "feature_based") -> BCSScorer:
    """
    创建BCS评分器
    
    Args:
        scoring_method: 评分方法 ("feature_based", "ml_based", "simple_rules")
        
    Returns:
        BCS评分器实例
    """
    return BCSScorer(scoring_method)

if __name__ == "__main__":
    # 测试BCS评分器
    print("🔍 测试BCS评分器...")
    
    # 创建测试图像
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    test_bbox = (100, 100, 200, 150)
    
    # 测试不同评分方法
    for method in ["feature_based", "simple_rules"]:
        print(f"\n测试 {method} 评分方法:")
        scorer = create_bcs_scorer(method)
        result = scorer.score_bcs(test_image, test_bbox)
        
        print(f"  BCS评分: {result.score}")
        print(f"  分类: {result.category.value}")
        print(f"  置信度: {result.confidence:.3f}")
        print(f"  建议数量: {len(result.recommendations)}")
        
        if result.feature_contributions:
            print("  特征贡献:")
            for feature, contribution in result.feature_contributions.items():
                print(f"    {feature}: {contribution:.3f}")
    
    print("\n🎉 BCS评分器测试完成！")