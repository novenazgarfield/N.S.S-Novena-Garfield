"""
BovineInsight: 工具模块
Utilities Module

提供配置管理、日志设置等工具功能
"""

from .config_manager import ConfigManager
from .logger import setup_logging

__all__ = ['ConfigManager', 'setup_logging']