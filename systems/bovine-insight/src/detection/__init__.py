"""
BovineInsight: 牛只检测模块
Cattle Detection Module

使用YOLOv8进行牛只检测和边界框提取
"""

from .cattle_detector import CattleDetector
from .detection_utils import DetectionResult, BoundingBox
from .model_manager import ModelManager

__all__ = ['CattleDetector', 'DetectionResult', 'BoundingBox', 'ModelManager']