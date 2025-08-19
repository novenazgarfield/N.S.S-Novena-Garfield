"""
BovineInsight: 融合身份识别模块
Fused Identification Module

结合耳标识别和花色重识别的双重身份识别系统
"""

from .ear_tag_reader import EarTagReader
from .coat_pattern_reid import CoatPatternReID
from .fused_identifier import FusedIdentifier
from .identification_utils import IdentificationResult, CattleProfile

__all__ = [
    'EarTagReader', 
    'CoatPatternReID', 
    'FusedIdentifier',
    'IdentificationResult',
    'CattleProfile'
]