"""
融合身份识别器
Fused Identifier

结合耳标识别和花色重识别的智能决策系统
"""

import logging
import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .identification_utils import (
    IdentificationResult, IdentificationMethod, CattleProfile, 
    ConfidenceLevel, CoatPatternFeature
)
from .ear_tag_reader import EarTagReader
from .coat_pattern_reid import CoatPatternReID
from ..detection.detection_utils import DetectionResult, BoundingBox

class FusionStrategy(Enum):
    """融合策略枚举"""
    EAR_TAG_PRIORITY = "ear_tag_priority"      # 耳标优先
    COAT_PATTERN_FALLBACK = "coat_fallback"    # 花色备用
    WEIGHTED_FUSION = "weighted_fusion"        # 加权融合
    CONFIDENCE_BASED = "confidence_based"      # 基于置信度选择

@dataclass
class FusionConfig:
    """融合配置"""
    strategy: FusionStrategy = FusionStrategy.EAR_TAG_PRIORITY
    ear_tag_weight: float = 0.7
    coat_pattern_weight: float = 0.3
    min_ear_tag_confidence: float = 0.6
    min_coat_pattern_confidence: float = 0.7
    fusion_threshold: float = 0.8
    enable_cross_validation: bool = True

class FusedIdentifier:
    """融合身份识别器主类"""
    
    def __init__(self, 
                 ear_tag_reader: Optional[EarTagReader] = None,
                 coat_pattern_reid: Optional[CoatPatternReID] = None,
                 config: Optional[FusionConfig] = None):
        """
        初始化融合识别器
        
        Args:
            ear_tag_reader: 耳标识别器
            coat_pattern_reid: 花色重识别器
            config: 融合配置
        """
        self.config = config or FusionConfig()
        
        # 初始化子模块
        self.ear_tag_reader = ear_tag_reader or EarTagReader()
        self.coat_pattern_reid = coat_pattern_reid or CoatPatternReID()
        
        # 统计信息
        self.stats = {
            'total_identifications': 0,
            'ear_tag_only': 0,
            'coat_pattern_only': 0,
            'fused_results': 0,
            'failed_identifications': 0,
            'cross_validation_matches': 0,
            'cross_validation_conflicts': 0
        }
        
        logging.info(f"融合身份识别器初始化完成，策略: {self.config.strategy.value}")
    
    def identify_cattle(self, 
                       cattle_image: np.ndarray,
                       ear_tag_region: Optional[np.ndarray] = None,
                       candidate_profiles: Optional[List[CattleProfile]] = None) -> IdentificationResult:
        """
        识别牛只身份
        
        Args:
            cattle_image: 完整的牛只图像
            ear_tag_region: 耳标区域图像（可选）
            candidate_profiles: 候选牛只档案列表
        
        Returns:
            融合识别结果
        """
        self.stats['total_identifications'] += 1
        
        if candidate_profiles is None:
            candidate_profiles = []
        
        # 执行耳标识别
        ear_tag_result = None
        if ear_tag_region is not None:
            ear_tag_result = self.ear_tag_reader.read_ear_tag(ear_tag_region)
        
        # 执行花色识别
        coat_pattern_result = None
        if len(candidate_profiles) > 0:
            coat_pattern_result = self.coat_pattern_reid.identify_by_coat_pattern(
                cattle_image, candidate_profiles
            )
        
        # 根据策略融合结果
        fused_result = self._fuse_results(ear_tag_result, coat_pattern_result, candidate_profiles)
        
        # 交叉验证（如果启用）
        if self.config.enable_cross_validation and ear_tag_result and coat_pattern_result:
            self._cross_validate_results(ear_tag_result, coat_pattern_result, fused_result)
        
        # 更新统计信息
        self._update_stats(ear_tag_result, coat_pattern_result, fused_result)
        
        return fused_result
    
    def _fuse_results(self, 
                     ear_tag_result: Optional[IdentificationResult],
                     coat_pattern_result: Optional[IdentificationResult],
                     candidate_profiles: List[CattleProfile]) -> IdentificationResult:
        """融合识别结果"""
        
        if self.config.strategy == FusionStrategy.EAR_TAG_PRIORITY:
            return self._ear_tag_priority_fusion(ear_tag_result, coat_pattern_result)
        
        elif self.config.strategy == FusionStrategy.COAT_PATTERN_FALLBACK:
            return self._coat_pattern_fallback_fusion(ear_tag_result, coat_pattern_result)
        
        elif self.config.strategy == FusionStrategy.WEIGHTED_FUSION:
            return self._weighted_fusion(ear_tag_result, coat_pattern_result)
        
        elif self.config.strategy == FusionStrategy.CONFIDENCE_BASED:
            return self._confidence_based_fusion(ear_tag_result, coat_pattern_result)
        
        else:
            # 默认使用耳标优先策略
            return self._ear_tag_priority_fusion(ear_tag_result, coat_pattern_result)
    
    def _ear_tag_priority_fusion(self, 
                                ear_tag_result: Optional[IdentificationResult],
                                coat_pattern_result: Optional[IdentificationResult]) -> IdentificationResult:
        """耳标优先融合策略"""
        
        # 优先使用耳标结果
        if (ear_tag_result and 
            ear_tag_result.cattle_id and 
            ear_tag_result.confidence >= self.config.min_ear_tag_confidence):
            
            # 创建融合结果
            fused_result = IdentificationResult(
                cattle_id=ear_tag_result.cattle_id,
                method=IdentificationMethod.EAR_TAG,
                confidence=ear_tag_result.confidence,
                ear_tag_id=ear_tag_result.ear_tag_id,
                metadata={
                    'primary_method': 'ear_tag',
                    'ear_tag_confidence': ear_tag_result.confidence,
                    'coat_pattern_confidence': coat_pattern_result.confidence if coat_pattern_result else 0.0,
                    'fusion_strategy': self.config.strategy.value
                }
            )
            
            # 如果花色识别也成功，添加到元数据
            if (coat_pattern_result and 
                coat_pattern_result.cattle_id and 
                coat_pattern_result.confidence >= self.config.min_coat_pattern_confidence):
                fused_result.coat_pattern_match = coat_pattern_result.coat_pattern_match
                fused_result.metadata['coat_pattern_match'] = coat_pattern_result.cattle_id
            
            return fused_result
        
        # 耳标识别失败，使用花色识别
        elif (coat_pattern_result and 
              coat_pattern_result.cattle_id and 
              coat_pattern_result.confidence >= self.config.min_coat_pattern_confidence):
            
            fused_result = IdentificationResult(
                cattle_id=coat_pattern_result.cattle_id,
                method=IdentificationMethod.COAT_PATTERN,
                confidence=coat_pattern_result.confidence,
                coat_pattern_match=coat_pattern_result.coat_pattern_match,
                metadata={
                    'primary_method': 'coat_pattern',
                    'fallback_reason': 'ear_tag_failed',
                    'ear_tag_confidence': ear_tag_result.confidence if ear_tag_result else 0.0,
                    'coat_pattern_confidence': coat_pattern_result.confidence,
                    'fusion_strategy': self.config.strategy.value
                }
            )
            
            return fused_result
        
        # 两种方法都失败
        else:
            return IdentificationResult(
                cattle_id=None,
                method=IdentificationMethod.UNKNOWN,
                confidence=0.0,
                metadata={
                    'fusion_strategy': self.config.strategy.value,
                    'failure_reason': 'both_methods_failed',
                    'ear_tag_confidence': ear_tag_result.confidence if ear_tag_result else 0.0,
                    'coat_pattern_confidence': coat_pattern_result.confidence if coat_pattern_result else 0.0
                }
            )
    
    def _coat_pattern_fallback_fusion(self, 
                                     ear_tag_result: Optional[IdentificationResult],
                                     coat_pattern_result: Optional[IdentificationResult]) -> IdentificationResult:
        """花色备用融合策略"""
        # 与耳标优先策略相同的逻辑，但阈值可能不同
        return self._ear_tag_priority_fusion(ear_tag_result, coat_pattern_result)
    
    def _weighted_fusion(self, 
                        ear_tag_result: Optional[IdentificationResult],
                        coat_pattern_result: Optional[IdentificationResult]) -> IdentificationResult:
        """加权融合策略"""
        
        # 检查两种方法是否都有有效结果
        if not (ear_tag_result and ear_tag_result.cattle_id and 
                coat_pattern_result and coat_pattern_result.cattle_id):
            # 回退到优先策略
            return self._ear_tag_priority_fusion(ear_tag_result, coat_pattern_result)
        
        # 检查两种方法是否识别为同一头牛
        if ear_tag_result.cattle_id == coat_pattern_result.cattle_id:
            # 一致结果，计算加权置信度
            weighted_confidence = (
                ear_tag_result.confidence * self.config.ear_tag_weight +
                coat_pattern_result.confidence * self.config.coat_pattern_weight
            )
            
            return IdentificationResult(
                cattle_id=ear_tag_result.cattle_id,
                method=IdentificationMethod.FUSED,
                confidence=weighted_confidence,
                ear_tag_id=ear_tag_result.ear_tag_id,
                coat_pattern_match=coat_pattern_result.coat_pattern_match,
                metadata={
                    'fusion_strategy': 'weighted_fusion',
                    'ear_tag_confidence': ear_tag_result.confidence,
                    'coat_pattern_confidence': coat_pattern_result.confidence,
                    'weighted_confidence': weighted_confidence,
                    'agreement': True
                }
            )
        
        else:
            # 不一致结果，选择置信度更高的
            if ear_tag_result.confidence > coat_pattern_result.confidence:
                primary_result = ear_tag_result
                secondary_result = coat_pattern_result
                primary_method = 'ear_tag'
            else:
                primary_result = coat_pattern_result
                secondary_result = ear_tag_result
                primary_method = 'coat_pattern'
            
            return IdentificationResult(
                cattle_id=primary_result.cattle_id,
                method=IdentificationMethod.FUSED,
                confidence=primary_result.confidence,
                ear_tag_id=ear_tag_result.ear_tag_id if primary_method == 'ear_tag' else None,
                coat_pattern_match=coat_pattern_result.coat_pattern_match if primary_method == 'coat_pattern' else None,
                metadata={
                    'fusion_strategy': 'weighted_fusion',
                    'primary_method': primary_method,
                    'agreement': False,
                    'conflict_resolution': 'higher_confidence',
                    'ear_tag_confidence': ear_tag_result.confidence,
                    'coat_pattern_confidence': coat_pattern_result.confidence,
                    'alternative_id': secondary_result.cattle_id
                }
            )
    
    def _confidence_based_fusion(self, 
                                ear_tag_result: Optional[IdentificationResult],
                                coat_pattern_result: Optional[IdentificationResult]) -> IdentificationResult:
        """基于置信度的融合策略"""
        
        valid_results = []
        
        if (ear_tag_result and ear_tag_result.cattle_id and 
            ear_tag_result.confidence >= self.config.min_ear_tag_confidence):
            valid_results.append(('ear_tag', ear_tag_result))
        
        if (coat_pattern_result and coat_pattern_result.cattle_id and 
            coat_pattern_result.confidence >= self.config.min_coat_pattern_confidence):
            valid_results.append(('coat_pattern', coat_pattern_result))
        
        if not valid_results:
            # 没有有效结果
            return IdentificationResult(
                cattle_id=None,
                method=IdentificationMethod.UNKNOWN,
                confidence=0.0,
                metadata={'fusion_strategy': 'confidence_based', 'failure_reason': 'no_valid_results'}
            )
        
        elif len(valid_results) == 1:
            # 只有一个有效结果
            method_name, result = valid_results[0]
            result.metadata['fusion_strategy'] = 'confidence_based'
            result.metadata['single_method'] = method_name
            return result
        
        else:
            # 多个有效结果，选择置信度最高的
            best_method, best_result = max(valid_results, key=lambda x: x[1].confidence)
            
            best_result.method = IdentificationMethod.FUSED
            best_result.metadata.update({
                'fusion_strategy': 'confidence_based',
                'selected_method': best_method,
                'ear_tag_confidence': ear_tag_result.confidence if ear_tag_result else 0.0,
                'coat_pattern_confidence': coat_pattern_result.confidence if coat_pattern_result else 0.0
            })
            
            return best_result
    
    def _cross_validate_results(self, 
                               ear_tag_result: IdentificationResult,
                               coat_pattern_result: IdentificationResult,
                               fused_result: IdentificationResult):
        """交叉验证结果"""
        
        if (ear_tag_result.cattle_id and coat_pattern_result.cattle_id):
            if ear_tag_result.cattle_id == coat_pattern_result.cattle_id:
                self.stats['cross_validation_matches'] += 1
                fused_result.metadata['cross_validation'] = 'match'
            else:
                self.stats['cross_validation_conflicts'] += 1
                fused_result.metadata['cross_validation'] = 'conflict'
                fused_result.metadata['ear_tag_id_detected'] = ear_tag_result.cattle_id
                fused_result.metadata['coat_pattern_id_detected'] = coat_pattern_result.cattle_id
                
                # 记录冲突以供后续分析
                logging.warning(f"识别冲突: 耳标={ear_tag_result.cattle_id}, 花色={coat_pattern_result.cattle_id}")
    
    def _update_stats(self, 
                     ear_tag_result: Optional[IdentificationResult],
                     coat_pattern_result: Optional[IdentificationResult],
                     fused_result: IdentificationResult):
        """更新统计信息"""
        
        if fused_result.cattle_id:
            if fused_result.method == IdentificationMethod.EAR_TAG:
                self.stats['ear_tag_only'] += 1
            elif fused_result.method == IdentificationMethod.COAT_PATTERN:
                self.stats['coat_pattern_only'] += 1
            elif fused_result.method == IdentificationMethod.FUSED:
                self.stats['fused_results'] += 1
        else:
            self.stats['failed_identifications'] += 1
    
    def batch_identify(self, 
                      cattle_detections: List[Tuple[np.ndarray, Optional[np.ndarray]]],
                      candidate_profiles: List[CattleProfile]) -> List[IdentificationResult]:
        """批量识别"""
        results = []
        
        for cattle_image, ear_tag_region in cattle_detections:
            result = self.identify_cattle(cattle_image, ear_tag_region, candidate_profiles)
            results.append(result)
        
        return results
    
    def update_config(self, new_config: FusionConfig):
        """更新融合配置"""
        self.config = new_config
        logging.info(f"融合配置已更新，策略: {new_config.strategy.value}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        
        if stats['total_identifications'] > 0:
            stats['success_rate'] = (
                (stats['ear_tag_only'] + stats['coat_pattern_only'] + stats['fused_results']) /
                stats['total_identifications']
            )
            stats['failure_rate'] = stats['failed_identifications'] / stats['total_identifications']
        else:
            stats['success_rate'] = 0.0
            stats['failure_rate'] = 0.0
        
        # 添加子模块统计
        stats['ear_tag_reader_stats'] = self.ear_tag_reader.get_stats()
        stats['coat_pattern_reid_stats'] = self.coat_pattern_reid.get_stats()
        
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_identifications': 0,
            'ear_tag_only': 0,
            'coat_pattern_only': 0,
            'fused_results': 0,
            'failed_identifications': 0,
            'cross_validation_matches': 0,
            'cross_validation_conflicts': 0
        }
        
        # 重置子模块统计
        self.ear_tag_reader.reset_stats()
        self.coat_pattern_reid.reset_stats()
    
    def analyze_performance(self) -> Dict[str, Any]:
        """分析性能"""
        stats = self.get_stats()
        
        analysis = {
            'overall_performance': {
                'total_attempts': stats['total_identifications'],
                'success_rate': stats['success_rate'],
                'failure_rate': stats['failure_rate']
            },
            'method_distribution': {
                'ear_tag_only': stats['ear_tag_only'],
                'coat_pattern_only': stats['coat_pattern_only'],
                'fused_results': stats['fused_results']
            },
            'cross_validation': {
                'matches': stats['cross_validation_matches'],
                'conflicts': stats['cross_validation_conflicts'],
                'agreement_rate': (
                    stats['cross_validation_matches'] / 
                    max(stats['cross_validation_matches'] + stats['cross_validation_conflicts'], 1)
                )
            },
            'recommendations': []
        }
        
        # 生成建议
        if stats['failure_rate'] > 0.3:
            analysis['recommendations'].append("失败率较高，建议调整置信度阈值")
        
        if stats['cross_validation_conflicts'] > stats['cross_validation_matches']:
            analysis['recommendations'].append("交叉验证冲突较多，建议检查数据质量")
        
        if stats['ear_tag_only'] < stats['coat_pattern_only']:
            analysis['recommendations'].append("耳标识别效果不佳，建议优化OCR配置")
        
        return analysis

# 预定义的融合配置
FUSION_CONFIGS = {
    'conservative': FusionConfig(
        strategy=FusionStrategy.EAR_TAG_PRIORITY,
        min_ear_tag_confidence=0.8,
        min_coat_pattern_confidence=0.8,
        enable_cross_validation=True
    ),
    'balanced': FusionConfig(
        strategy=FusionStrategy.WEIGHTED_FUSION,
        ear_tag_weight=0.6,
        coat_pattern_weight=0.4,
        min_ear_tag_confidence=0.6,
        min_coat_pattern_confidence=0.7,
        enable_cross_validation=True
    ),
    'aggressive': FusionConfig(
        strategy=FusionStrategy.CONFIDENCE_BASED,
        min_ear_tag_confidence=0.4,
        min_coat_pattern_confidence=0.5,
        enable_cross_validation=True
    )
}