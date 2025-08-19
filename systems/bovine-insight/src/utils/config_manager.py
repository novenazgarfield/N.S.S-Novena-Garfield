"""
配置管理器
Configuration Manager

管理系统配置文件的加载、保存和验证
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class SystemConfig:
    """系统配置数据类"""
    # 摄像头配置
    cameras: Dict[str, Dict[str, Any]]
    
    # 检测配置
    detection: Dict[str, Any]
    
    # 识别配置
    identification: Dict[str, Any]
    
    # 体况评分配置
    body_condition: Dict[str, Any]
    
    # 数据库配置
    database: Dict[str, Any]
    
    # 视频处理配置
    video_processing: Dict[str, Any]
    
    # 帧缓冲配置
    frame_buffer: Dict[str, Any]
    
    # 日志配置
    logging: Dict[str, Any]

class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        'cameras': {
            'ear_tag_camera': {
                'id': 0,
                'type': 'ear_tag',
                'resolution': [1920, 1080],
                'fps': 30,
                'auto_focus': True
            },
            'body_condition_camera': {
                'id': 1,
                'type': 'body_condition',
                'resolution': [1920, 1080],
                'fps': 30,
                'auto_focus': True
            }
        },
        'detection': {
            'model': 'yolov8n',
            'models_dir': 'models',
            'confidence_threshold': 0.5,
            'iou_threshold': 0.5,
            'device': 'auto'
        },
        'identification': {
            'fusion_strategy': 'ear_tag_priority',
            'min_ear_tag_confidence': 0.6,
            'min_coat_pattern_confidence': 0.7,
            'ear_tag': {
                'use_tesseract': True,
                'use_easyocr': True,
                'min_confidence': 0.5
            },
            'coat_pattern': {
                'extractor_type': 'resnet',
                'similarity_threshold': 0.7
            }
        },
        'body_condition': {
            'enable': True,
            'model_path': None,
            'scale': '1-5',
            'confidence_threshold': 0.6
        },
        'database': {
            'type': 'sqlite',
            'path': 'data/cattle_database.db',
            'backup_interval': 3600
        },
        'video_processing': {
            'mode': 'balanced',
            'target_size': [640, 640],
            'normalize': True,
            'enhance_contrast': True
        },
        'frame_buffer': {
            'max_size': 30,
            'sync_tolerance': 0.1
        },
        'logging': {
            'level': 'INFO',
            'file': 'logs/bovine_insight.log',
            'max_size': '10MB',
            'backup_count': 5,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or 'config/system_config.yaml'
        self.config = self.DEFAULT_CONFIG.copy()
        
        # 加载配置文件
        self.load_config()
        
        logging.info(f"配置管理器初始化完成，配置文件: {self.config_path}")
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            logging.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
            self.save_config()  # 保存默认配置
            return self.config
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() in ['.yaml', '.yml']:
                    loaded_config = yaml.safe_load(f)
                elif config_file.suffix.lower() == '.json':
                    loaded_config = json.load(f)
                else:
                    raise ValueError(f"不支持的配置文件格式: {config_file.suffix}")
            
            # 合并配置（保留默认值）
            self.config = self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
            
            # 验证配置
            self._validate_config()
            
            logging.info(f"配置文件加载成功: {self.config_path}")
            
        except Exception as e:
            logging.error(f"配置文件加载失败: {e}")
            logging.warning("使用默认配置")
        
        return self.config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存配置文件
        
        Args:
            config: 要保存的配置，如果为None则保存当前配置
        
        Returns:
            保存是否成功
        """
        if config is not None:
            self.config = config
        
        config_file = Path(self.config_path)
        
        try:
            # 确保目录存在
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                if config_file.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(self.config, f, default_flow_style=False, 
                             allow_unicode=True, indent=2)
                elif config_file.suffix.lower() == '.json':
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                else:
                    raise ValueError(f"不支持的配置文件格式: {config_file.suffix}")
            
            logging.info(f"配置文件保存成功: {self.config_path}")
            return True
            
        except Exception as e:
            logging.error(f"配置文件保存失败: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self.config.copy()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取配置节"""
        return self.config.get(section, {})
    
    def set_section(self, section: str, config: Dict[str, Any]):
        """设置配置节"""
        self.config[section] = config
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置值（支持点号分隔的嵌套键）
        
        Args:
            key: 配置键，如 'cameras.ear_tag_camera.resolution'
            default: 默认值
        
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_value(self, key: str, value: Any):
        """
        设置配置值（支持点号分隔的嵌套键）
        
        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        # 导航到父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置（递归）"""
        merged = default.copy()
        
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _validate_config(self):
        """验证配置有效性"""
        errors = []
        
        # 验证摄像头配置
        cameras = self.config.get('cameras', {})
        for camera_name, camera_config in cameras.items():
            if 'id' not in camera_config:
                errors.append(f"摄像头 {camera_name} 缺少 'id' 配置")
            if 'type' not in camera_config:
                errors.append(f"摄像头 {camera_name} 缺少 'type' 配置")
        
        # 验证检测配置
        detection = self.config.get('detection', {})
        if 'confidence_threshold' in detection:
            threshold = detection['confidence_threshold']
            if not (0.0 <= threshold <= 1.0):
                errors.append("检测置信度阈值必须在0-1之间")
        
        # 验证识别配置
        identification = self.config.get('identification', {})
        if 'min_ear_tag_confidence' in identification:
            threshold = identification['min_ear_tag_confidence']
            if not (0.0 <= threshold <= 1.0):
                errors.append("耳标识别置信度阈值必须在0-1之间")
        
        # 验证数据库配置
        database = self.config.get('database', {})
        if database.get('type') not in ['sqlite', 'postgresql', 'mysql']:
            errors.append("不支持的数据库类型")
        
        if errors:
            error_msg = "配置验证失败:\n" + "\n".join(f"- {error}" for error in errors)
            raise ValueError(error_msg)
    
    def create_backup(self) -> bool:
        """创建配置备份"""
        if not Path(self.config_path).exists():
            return False
        
        try:
            import shutil
            from datetime import datetime
            
            backup_path = f"{self.config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(self.config_path, backup_path)
            
            logging.info(f"配置备份创建成功: {backup_path}")
            return True
            
        except Exception as e:
            logging.error(f"配置备份创建失败: {e}")
            return False
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """从备份恢复配置"""
        try:
            import shutil
            
            if not Path(backup_path).exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_path}")
            
            shutil.copy2(backup_path, self.config_path)
            self.load_config()
            
            logging.info(f"配置从备份恢复成功: {backup_path}")
            return True
            
        except Exception as e:
            logging.error(f"配置恢复失败: {e}")
            return False
    
    def export_config(self, export_path: str, format: str = 'yaml') -> bool:
        """
        导出配置到指定文件
        
        Args:
            export_path: 导出路径
            format: 导出格式 ('yaml', 'json')
        
        Returns:
            导出是否成功
        """
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                if format.lower() == 'yaml':
                    yaml.dump(self.config, f, default_flow_style=False, 
                             allow_unicode=True, indent=2)
                elif format.lower() == 'json':
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                else:
                    raise ValueError(f"不支持的导出格式: {format}")
            
            logging.info(f"配置导出成功: {export_path}")
            return True
            
        except Exception as e:
            logging.error(f"配置导出失败: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        summary = {
            'config_file': self.config_path,
            'cameras_count': len(self.config.get('cameras', {})),
            'detection_model': self.config.get('detection', {}).get('model', 'unknown'),
            'identification_strategy': self.config.get('identification', {}).get('fusion_strategy', 'unknown'),
            'database_type': self.config.get('database', {}).get('type', 'unknown'),
            'logging_level': self.config.get('logging', {}).get('level', 'INFO')
        }
        
        return summary