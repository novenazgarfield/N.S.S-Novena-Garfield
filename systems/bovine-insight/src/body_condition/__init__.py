"""
BovineInsight: 体况评分模块
Body Condition Scoring Module

评估牛只的体况评分(BCS - Body Condition Score)
"""

from .keypoint_detector import KeypointDetector
from .feature_extractor import BodyConditionFeatureExtractor
from .bcs_scorer import BCSScorer
from .body_condition_utils import BCSResult, AnatomicalKeypoints

__all__ = [
    'KeypointDetector',
    'BodyConditionFeatureExtractor', 
    'BCSScorer',
    'BCSResult',
    'AnatomicalKeypoints'
]