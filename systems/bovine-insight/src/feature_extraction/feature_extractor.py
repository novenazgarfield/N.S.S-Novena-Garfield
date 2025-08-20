"""
无监督特征提取器 - 基于Meta DINOv2
用于在无标签的牛只图像数据上提取高质量的视觉特征
"""

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import logging
from typing import Union, List, Tuple, Optional
import cv2
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DINOv2FeatureExtractor:
    """
    基于Meta DINOv2的无监督特征提取器
    用于牛只图像的高质量特征提取，支持花色重识别和体况评分
    """
    
    def __init__(self, 
                 model_name: str = 'dinov2_vitb14',
                 device: Optional[str] = None,
                 cache_dir: Optional[str] = None):
        """
        初始化DINOv2特征提取器
        
        Args:
            model_name: DINOv2模型名称 ('dinov2_vits14', 'dinov2_vitb14', 'dinov2_vitl14', 'dinov2_vitg14')
            device: 计算设备 ('cuda', 'cpu', 或 None 自动选择)
            cache_dir: 模型缓存目录
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.cache_dir = cache_dir or str(Path.home() / '.cache' / 'torch' / 'hub')
        
        # 模型配置
        self.model_configs = {
            'dinov2_vits14': {'patch_size': 14, 'embed_dim': 384},
            'dinov2_vitb14': {'patch_size': 14, 'embed_dim': 768},
            'dinov2_vitl14': {'patch_size': 14, 'embed_dim': 1024},
            'dinov2_vitg14': {'patch_size': 14, 'embed_dim': 1536}
        }
        
        self.model = None
        self.transform = None
        self.feature_dim = self.model_configs[model_name]['embed_dim']
        
        logger.info(f"初始化DINOv2特征提取器: {model_name}, 设备: {self.device}")
        
    def load_model(self):
        """加载DINOv2预训练模型"""
        try:
            logger.info(f"加载DINOv2模型: {self.model_name}")
            
            # 加载预训练模型
            self.model = torch.hub.load(
                'facebookresearch/dinov2', 
                self.model_name,
                cache_dir=self.cache_dir
            )
            
            # 移动到指定设备
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # 定义图像预处理变换
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),  # DINOv2标准输入尺寸
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],  # ImageNet标准化
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            logger.info(f"模型加载成功，特征维度: {self.feature_dim}")
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise
    
    def preprocess_image(self, image: Union[str, np.ndarray, Image.Image]) -> torch.Tensor:
        """
        预处理图像
        
        Args:
            image: 输入图像 (文件路径、numpy数组或PIL图像)
            
        Returns:
            预处理后的张量
        """
        try:
            # 统一转换为PIL图像
            if isinstance(image, str):
                pil_image = Image.open(image).convert('RGB')
            elif isinstance(image, np.ndarray):
                if image.shape[-1] == 3:  # BGR to RGB
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(image)
            elif isinstance(image, Image.Image):
                pil_image = image.convert('RGB')
            else:
                raise ValueError(f"不支持的图像类型: {type(image)}")
            
            # 应用预处理变换
            tensor = self.transform(pil_image)
            
            # 添加批次维度
            if tensor.dim() == 3:
                tensor = tensor.unsqueeze(0)
                
            return tensor.to(self.device)
            
        except Exception as e:
            logger.error(f"图像预处理失败: {str(e)}")
            raise
    
    def extract_features(self, image: Union[str, np.ndarray, Image.Image]) -> np.ndarray:
        """
        提取图像特征向量
        
        Args:
            image: 输入图像
            
        Returns:
            特征向量 (numpy数组)
        """
        if self.model is None:
            self.load_model()
            
        try:
            # 预处理图像
            input_tensor = self.preprocess_image(image)
            
            # 提取特征
            with torch.no_grad():
                features = self.model(input_tensor)
                
                # 如果返回的是字典，取CLS token特征
                if isinstance(features, dict):
                    features = features['x_norm_clstoken']
                elif features.dim() > 2:
                    # 取CLS token (第一个token)
                    features = features[:, 0]
                
                # 转换为numpy数组
                features = features.cpu().numpy()
                
                # 如果是批次，取第一个
                if features.ndim > 1 and features.shape[0] == 1:
                    features = features[0]
                    
            logger.debug(f"提取特征成功，维度: {features.shape}")
            return features
            
        except Exception as e:
            logger.error(f"特征提取失败: {str(e)}")
            raise
    
    def extract_patch_features(self, image: Union[str, np.ndarray, Image.Image]) -> np.ndarray:
        """
        提取图像块特征 (用于更细粒度的分析)
        
        Args:
            image: 输入图像
            
        Returns:
            图像块特征矩阵
        """
        if self.model is None:
            self.load_model()
            
        try:
            input_tensor = self.preprocess_image(image)
            
            with torch.no_grad():
                # 获取所有patch的特征
                features = self.model.forward_features(input_tensor)
                
                # 移除CLS token，只保留patch特征
                patch_features = features['x_norm_patchtokens']
                
                # 转换为numpy数组
                patch_features = patch_features.cpu().numpy()
                
                if patch_features.ndim > 2 and patch_features.shape[0] == 1:
                    patch_features = patch_features[0]
                    
            logger.debug(f"提取patch特征成功，维度: {patch_features.shape}")
            return patch_features
            
        except Exception as e:
            logger.error(f"Patch特征提取失败: {str(e)}")
            raise
    
    def compute_similarity(self, 
                          features1: np.ndarray, 
                          features2: np.ndarray,
                          metric: str = 'cosine') -> float:
        """
        计算特征相似度
        
        Args:
            features1: 第一个特征向量
            features2: 第二个特征向量
            metric: 相似度度量方式 ('cosine', 'euclidean', 'dot')
            
        Returns:
            相似度分数
        """
        try:
            if metric == 'cosine':
                # 余弦相似度
                norm1 = np.linalg.norm(features1)
                norm2 = np.linalg.norm(features2)
                if norm1 == 0 or norm2 == 0:
                    return 0.0
                similarity = np.dot(features1, features2) / (norm1 * norm2)
                
            elif metric == 'euclidean':
                # 欧几里得距离 (转换为相似度)
                distance = np.linalg.norm(features1 - features2)
                similarity = 1.0 / (1.0 + distance)
                
            elif metric == 'dot':
                # 点积相似度
                similarity = np.dot(features1, features2)
                
            else:
                raise ValueError(f"不支持的相似度度量: {metric}")
                
            return float(similarity)
            
        except Exception as e:
            logger.error(f"相似度计算失败: {str(e)}")
            raise
    
    def batch_extract_features(self, 
                              images: List[Union[str, np.ndarray, Image.Image]],
                              batch_size: int = 8) -> List[np.ndarray]:
        """
        批量提取特征
        
        Args:
            images: 图像列表
            batch_size: 批次大小
            
        Returns:
            特征向量列表
        """
        if self.model is None:
            self.load_model()
            
        features_list = []
        
        try:
            for i in range(0, len(images), batch_size):
                batch_images = images[i:i + batch_size]
                batch_tensors = []
                
                # 预处理批次图像
                for img in batch_images:
                    tensor = self.preprocess_image(img)
                    batch_tensors.append(tensor)
                
                # 合并为批次张量
                batch_tensor = torch.cat(batch_tensors, dim=0)
                
                # 批量提取特征
                with torch.no_grad():
                    batch_features = self.model(batch_tensor)
                    
                    if isinstance(batch_features, dict):
                        batch_features = batch_features['x_norm_clstoken']
                    elif batch_features.dim() > 2:
                        batch_features = batch_features[:, 0]
                    
                    batch_features = batch_features.cpu().numpy()
                
                # 添加到结果列表
                for j in range(batch_features.shape[0]):
                    features_list.append(batch_features[j])
                
                logger.info(f"批量处理进度: {min(i + batch_size, len(images))}/{len(images)}")
                
            return features_list
            
        except Exception as e:
            logger.error(f"批量特征提取失败: {str(e)}")
            raise
    
    def save_features(self, features: np.ndarray, filepath: str):
        """保存特征到文件"""
        try:
            np.save(filepath, features)
            logger.info(f"特征已保存到: {filepath}")
        except Exception as e:
            logger.error(f"特征保存失败: {str(e)}")
            raise
    
    def load_features(self, filepath: str) -> np.ndarray:
        """从文件加载特征"""
        try:
            features = np.load(filepath)
            logger.info(f"特征已从文件加载: {filepath}")
            return features
        except Exception as e:
            logger.error(f"特征加载失败: {str(e)}")
            raise
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            'model_name': self.model_name,
            'feature_dim': self.feature_dim,
            'device': self.device,
            'patch_size': self.model_configs[self.model_name]['patch_size'],
            'is_loaded': self.model is not None
        }


class CattleFeatureDatabase:
    """
    牛只特征数据库
    用于存储和检索牛只的DINOv2特征向量
    """
    
    def __init__(self, db_path: str = "cattle_features.npz"):
        """
        初始化特征数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.features_db = {}
        self.metadata_db = {}
        self.load_database()
        
    def add_cattle_features(self, 
                           cattle_id: str, 
                           features: np.ndarray,
                           metadata: Optional[dict] = None):
        """
        添加牛只特征
        
        Args:
            cattle_id: 牛只ID
            features: 特征向量
            metadata: 元数据 (可选)
        """
        self.features_db[cattle_id] = features
        self.metadata_db[cattle_id] = metadata or {}
        logger.info(f"添加牛只特征: {cattle_id}")
    
    def find_similar_cattle(self, 
                           query_features: np.ndarray,
                           top_k: int = 5,
                           threshold: float = 0.7) -> List[Tuple[str, float]]:
        """
        查找相似的牛只
        
        Args:
            query_features: 查询特征向量
            top_k: 返回前K个结果
            threshold: 相似度阈值
            
        Returns:
            相似牛只列表 [(cattle_id, similarity_score), ...]
        """
        similarities = []
        
        for cattle_id, stored_features in self.features_db.items():
            # 计算余弦相似度
            norm1 = np.linalg.norm(query_features)
            norm2 = np.linalg.norm(stored_features)
            
            if norm1 > 0 and norm2 > 0:
                similarity = np.dot(query_features, stored_features) / (norm1 * norm2)
                if similarity >= threshold:
                    similarities.append((cattle_id, float(similarity)))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def save_database(self):
        """保存数据库到文件"""
        try:
            np.savez_compressed(
                self.db_path,
                features=self.features_db,
                metadata=self.metadata_db
            )
            logger.info(f"特征数据库已保存: {self.db_path}")
        except Exception as e:
            logger.error(f"数据库保存失败: {str(e)}")
    
    def load_database(self):
        """从文件加载数据库"""
        try:
            if Path(self.db_path).exists():
                data = np.load(self.db_path, allow_pickle=True)
                self.features_db = data['features'].item()
                self.metadata_db = data['metadata'].item()
                logger.info(f"特征数据库已加载: {len(self.features_db)}条记录")
        except Exception as e:
            logger.warning(f"数据库加载失败，将创建新数据库: {str(e)}")
            self.features_db = {}
            self.metadata_db = {}
    
    def get_database_stats(self) -> dict:
        """获取数据库统计信息"""
        return {
            'total_cattle': len(self.features_db),
            'feature_dim': len(next(iter(self.features_db.values()))) if self.features_db else 0,
            'db_path': self.db_path
        }


# 使用示例和测试函数
def test_feature_extractor():
    """测试特征提取器"""
    try:
        # 初始化特征提取器
        extractor = DINOv2FeatureExtractor(model_name='dinov2_vitb14')
        
        # 创建测试图像 (随机图像)
        test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        # 提取特征
        features = extractor.extract_features(test_image)
        print(f"特征维度: {features.shape}")
        print(f"特征范围: [{features.min():.4f}, {features.max():.4f}]")
        
        # 测试相似度计算
        features2 = extractor.extract_features(test_image)
        similarity = extractor.compute_similarity(features, features2)
        print(f"自相似度: {similarity:.4f}")
        
        # 测试特征数据库
        db = CattleFeatureDatabase("test_cattle_features.npz")
        db.add_cattle_features("cattle_001", features, {"breed": "Holstein"})
        
        similar_cattle = db.find_similar_cattle(features2, top_k=3)
        print(f"相似牛只: {similar_cattle}")
        
        print("✅ 特征提取器测试通过")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")


if __name__ == "__main__":
    test_feature_extractor()