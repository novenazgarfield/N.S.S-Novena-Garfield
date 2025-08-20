"""
特征提取模块
基于DINOv2的无监督特征提取
"""

from .feature_extractor import DINOv2FeatureExtractor, CattleFeatureDatabase

__all__ = ['DINOv2FeatureExtractor', 'CattleFeatureDatabase']