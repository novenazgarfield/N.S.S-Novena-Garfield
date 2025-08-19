"""
模型管理器
Model Manager

管理YOLO模型的下载、加载和版本控制
"""

import os
import logging
import hashlib
import requests
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass
from urllib.parse import urlparse

@dataclass
class ModelInfo:
    """模型信息"""
    name: str
    url: str
    local_path: str
    md5_hash: str
    description: str
    size_mb: float
    version: str = "1.0"

class ModelManager:
    """模型管理器"""
    
    # 预定义的模型配置
    AVAILABLE_MODELS = {
        'yolov8n': ModelInfo(
            name='YOLOv8 Nano',
            url='https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt',
            local_path='models/yolov8n.pt',
            md5_hash='',  # 实际使用时需要填入正确的hash
            description='YOLOv8 Nano - 最快的模型，适合实时检测',
            size_mb=6.2
        ),
        'yolov8s': ModelInfo(
            name='YOLOv8 Small',
            url='https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt',
            local_path='models/yolov8s.pt',
            md5_hash='',
            description='YOLOv8 Small - 平衡速度和精度',
            size_mb=21.5
        ),
        'yolov8m': ModelInfo(
            name='YOLOv8 Medium',
            url='https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt',
            local_path='models/yolov8m.pt',
            md5_hash='',
            description='YOLOv8 Medium - 更高精度',
            size_mb=49.7
        ),
        'cattle_custom': ModelInfo(
            name='Custom Cattle Model',
            url='',  # 需要用户提供
            local_path='models/cattle_custom.pt',
            md5_hash='',
            description='专门训练的牛只检测模型',
            size_mb=0.0
        )
    }
    
    def __init__(self, models_dir: str = "models"):
        """
        初始化模型管理器
        
        Args:
            models_dir: 模型存储目录
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # 更新本地路径
        for model_info in self.AVAILABLE_MODELS.values():
            model_info.local_path = str(self.models_dir / Path(model_info.local_path).name)
        
        logging.info(f"模型管理器初始化，模型目录: {self.models_dir}")
    
    def download_model(self, model_key: str, force_download: bool = False) -> bool:
        """
        下载模型
        
        Args:
            model_key: 模型键名
            force_download: 是否强制重新下载
        
        Returns:
            下载是否成功
        """
        if model_key not in self.AVAILABLE_MODELS:
            logging.error(f"未知模型: {model_key}")
            return False
        
        model_info = self.AVAILABLE_MODELS[model_key]
        local_path = Path(model_info.local_path)
        
        # 检查文件是否已存在
        if local_path.exists() and not force_download:
            if self._verify_model(model_key):
                logging.info(f"模型 {model_key} 已存在且验证通过")
                return True
            else:
                logging.warning(f"模型 {model_key} 验证失败，重新下载")
        
        # 检查URL是否有效
        if not model_info.url:
            logging.error(f"模型 {model_key} 没有下载URL")
            return False
        
        try:
            logging.info(f"开始下载模型 {model_key} 从 {model_info.url}")
            
            # 创建目录
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 下载文件
            response = requests.get(model_info.url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 显示下载进度
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}%", end='', flush=True)
            
            print()  # 换行
            logging.info(f"模型 {model_key} 下载完成")
            
            # 验证下载的文件
            if self._verify_model(model_key):
                logging.info(f"模型 {model_key} 验证成功")
                return True
            else:
                logging.error(f"模型 {model_key} 验证失败")
                local_path.unlink()  # 删除损坏的文件
                return False
                
        except Exception as e:
            logging.error(f"下载模型 {model_key} 失败: {e}")
            if local_path.exists():
                local_path.unlink()
            return False
    
    def _verify_model(self, model_key: str) -> bool:
        """验证模型文件"""
        model_info = self.AVAILABLE_MODELS[model_key]
        local_path = Path(model_info.local_path)
        
        if not local_path.exists():
            return False
        
        # 检查文件大小
        file_size_mb = local_path.stat().st_size / (1024 * 1024)
        if model_info.size_mb > 0 and abs(file_size_mb - model_info.size_mb) > 1.0:
            logging.warning(f"模型 {model_key} 文件大小不匹配: {file_size_mb:.1f}MB vs {model_info.size_mb:.1f}MB")
        
        # 检查MD5哈希（如果提供）
        if model_info.md5_hash:
            file_hash = self._calculate_md5(local_path)
            if file_hash != model_info.md5_hash:
                logging.error(f"模型 {model_key} MD5校验失败")
                return False
        
        return True
    
    def _calculate_md5(self, file_path: Path) -> str:
        """计算文件MD5哈希"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def get_model_path(self, model_key: str) -> Optional[str]:
        """获取模型本地路径"""
        if model_key not in self.AVAILABLE_MODELS:
            return None
        
        model_info = self.AVAILABLE_MODELS[model_key]
        local_path = Path(model_info.local_path)
        
        if local_path.exists():
            return str(local_path)
        else:
            return None
    
    def list_available_models(self) -> Dict[str, Dict]:
        """列出可用模型"""
        models_status = {}
        
        for key, model_info in self.AVAILABLE_MODELS.items():
            local_path = Path(model_info.local_path)
            
            status = {
                'name': model_info.name,
                'description': model_info.description,
                'size_mb': model_info.size_mb,
                'version': model_info.version,
                'downloaded': local_path.exists(),
                'verified': False
            }
            
            if status['downloaded']:
                status['verified'] = self._verify_model(key)
                status['local_path'] = str(local_path)
                status['file_size_mb'] = local_path.stat().st_size / (1024 * 1024)
            
            models_status[key] = status
        
        return models_status
    
    def delete_model(self, model_key: str) -> bool:
        """删除模型文件"""
        if model_key not in self.AVAILABLE_MODELS:
            logging.error(f"未知模型: {model_key}")
            return False
        
        model_info = self.AVAILABLE_MODELS[model_key]
        local_path = Path(model_info.local_path)
        
        if local_path.exists():
            try:
                local_path.unlink()
                logging.info(f"已删除模型 {model_key}")
                return True
            except Exception as e:
                logging.error(f"删除模型 {model_key} 失败: {e}")
                return False
        else:
            logging.warning(f"模型 {model_key} 不存在")
            return True
    
    def add_custom_model(self, model_key: str, model_info: ModelInfo) -> bool:
        """添加自定义模型"""
        if model_key in self.AVAILABLE_MODELS:
            logging.warning(f"模型 {model_key} 已存在，将被覆盖")
        
        # 更新本地路径
        model_info.local_path = str(self.models_dir / Path(model_info.local_path).name)
        
        self.AVAILABLE_MODELS[model_key] = model_info
        logging.info(f"已添加自定义模型 {model_key}")
        return True
    
    def get_best_model(self, criteria: str = 'balanced') -> Optional[str]:
        """
        根据标准获取最佳模型
        
        Args:
            criteria: 选择标准 ('speed', 'accuracy', 'balanced')
        
        Returns:
            最佳模型的键名
        """
        available_models = self.list_available_models()
        downloaded_models = {k: v for k, v in available_models.items() 
                           if v['downloaded'] and v['verified']}
        
        if not downloaded_models:
            return None
        
        if criteria == 'speed':
            # 选择最小的模型（通常最快）
            return min(downloaded_models.keys(), 
                      key=lambda k: downloaded_models[k]['size_mb'])
        elif criteria == 'accuracy':
            # 选择最大的模型（通常最准确）
            return max(downloaded_models.keys(), 
                      key=lambda k: downloaded_models[k]['size_mb'])
        else:  # balanced
            # 选择中等大小的模型
            sizes = [(k, v['size_mb']) for k, v in downloaded_models.items()]
            sizes.sort(key=lambda x: x[1])
            
            if len(sizes) == 1:
                return sizes[0][0]
            elif len(sizes) == 2:
                return sizes[0][0]  # 选择较小的
            else:
                return sizes[len(sizes) // 2][0]  # 选择中间的
    
    def setup_default_models(self) -> List[str]:
        """设置默认模型"""
        default_models = ['yolov8n', 'yolov8s']
        successfully_downloaded = []
        
        for model_key in default_models:
            if self.download_model(model_key):
                successfully_downloaded.append(model_key)
        
        return successfully_downloaded
    
    def cleanup_old_models(self, keep_latest: int = 2):
        """清理旧模型文件"""
        # 这里可以实现版本管理和清理逻辑
        # 目前只是一个占位符
        logging.info("模型清理功能待实现")
        pass

# 全局模型管理器实例
model_manager = ModelManager()