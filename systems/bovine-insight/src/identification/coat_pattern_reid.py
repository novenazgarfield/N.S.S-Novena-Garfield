"""
花色重识别模型
Coat Pattern Re-Identification Model

使用深度学习模型提取牛只花色特征并进行相似度匹配
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import logging
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path

from .identification_utils import (
    CoatPatternFeature, CattleProfile, IdentificationResult, 
    IdentificationMethod, FeatureExtractor, SimilarityMatcher
)

# 检查PyTorch可用性
TORCH_AVAILABLE = True
try:
    import torch
    import torchvision.transforms as transforms
    import torchvision.models as models
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available, using mock feature extractor")

class MockFeatureExtractor(FeatureExtractor):
    """模拟特征提取器"""
    
    def __init__(self):
        super().__init__("mock_extractor")
        self.feature_dim = 512
    
    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """提取模拟特征"""
        # 基于图像统计信息生成伪特征
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 计算基本统计特征
        features = []
        
        # 像素强度统计
        features.extend([
            np.mean(gray),
            np.std(gray),
            np.median(gray),
            np.min(gray),
            np.max(gray)
        ])
        
        # 纹理特征（简化版LBP）
        lbp_features = self._calculate_simple_lbp(gray)
        features.extend(lbp_features)
        
        # 边缘特征
        edges = cv2.Canny(gray, 50, 150)
        features.extend([
            np.sum(edges > 0) / edges.size,  # 边缘密度
            np.mean(edges),
            np.std(edges)
        ])
        
        # 填充到指定维度
        while len(features) < self.feature_dim:
            features.extend(features[:min(len(features), self.feature_dim - len(features))])
        
        return np.array(features[:self.feature_dim], dtype=np.float32)
    
    def _calculate_simple_lbp(self, image: np.ndarray) -> List[float]:
        """计算简化的LBP特征"""
        h, w = image.shape
        lbp_hist = np.zeros(256)
        
        for i in range(1, h-1):
            for j in range(1, w-1):
                center = image[i, j]
                code = 0
                
                # 8邻域
                neighbors = [
                    image[i-1, j-1], image[i-1, j], image[i-1, j+1],
                    image[i, j+1], image[i+1, j+1], image[i+1, j],
                    image[i+1, j-1], image[i, j-1]
                ]
                
                for k, neighbor in enumerate(neighbors):
                    if neighbor >= center:
                        code |= (1 << k)
                
                lbp_hist[code] += 1
        
        # 归一化
        lbp_hist = lbp_hist / np.sum(lbp_hist)
        
        # 返回前50个bin作为特征
        return lbp_hist[:50].tolist()

class ResNetFeatureExtractor(FeatureExtractor):
    """基于ResNet的特征提取器"""
    
    def __init__(self, model_name: str = 'resnet50', pretrained: bool = True):
        super().__init__(f"resnet_{model_name}")
        
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not available")
        
        # 加载预训练模型
        if model_name == 'resnet18':
            self.model = models.resnet18(pretrained=pretrained)
            self.feature_dim = 512
        elif model_name == 'resnet34':
            self.model = models.resnet34(pretrained=pretrained)
            self.feature_dim = 512
        elif model_name == 'resnet50':
            self.model = models.resnet50(pretrained=pretrained)
            self.feature_dim = 2048
        else:
            raise ValueError(f"Unsupported model: {model_name}")
        
        # 移除最后的分类层
        self.model = nn.Sequential(*list(self.model.children())[:-1])
        self.model.eval()
        
        # 图像预处理
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # 设备
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        logging.info(f"ResNet特征提取器初始化完成，模型: {model_name}, 设备: {self.device}")
    
    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """提取ResNet特征"""
        try:
            # 预处理图像
            if len(image.shape) == 3:
                # BGR to RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                # 灰度图转RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
            # 转换为tensor
            input_tensor = self.transform(image_rgb).unsqueeze(0).to(self.device)
            
            # 提取特征
            with torch.no_grad():
                features = self.model(input_tensor)
                features = features.view(features.size(0), -1)  # 展平
                features = F.normalize(features, p=2, dim=1)  # L2归一化
            
            return features.cpu().numpy().flatten()
            
        except Exception as e:
            logging.error(f"ResNet特征提取失败: {e}")
            # 返回零向量
            return np.zeros(self.feature_dim, dtype=np.float32)

class SiameseNetwork(nn.Module):
    """孪生网络用于相似度学习"""
    
    def __init__(self, backbone: str = 'resnet18', feature_dim: int = 128):
        super(SiameseNetwork, self).__init__()
        
        # 主干网络
        if backbone == 'resnet18':
            self.backbone = models.resnet18(pretrained=True)
            backbone_dim = 512
        elif backbone == 'resnet50':
            self.backbone = models.resnet50(pretrained=True)
            backbone_dim = 2048
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
        
        # 移除分类层
        self.backbone = nn.Sequential(*list(self.backbone.children())[:-1])
        
        # 特征投影层
        self.projector = nn.Sequential(
            nn.Linear(backbone_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, feature_dim)
        )
        
        self.feature_dim = feature_dim
    
    def forward_one(self, x):
        """前向传播单个输入"""
        features = self.backbone(x)
        features = features.view(features.size(0), -1)
        features = self.projector(features)
        return F.normalize(features, p=2, dim=1)
    
    def forward(self, x1, x2=None):
        """前向传播"""
        if x2 is None:
            return self.forward_one(x1)
        else:
            out1 = self.forward_one(x1)
            out2 = self.forward_one(x2)
            return out1, out2

class SiameseFeatureExtractor(FeatureExtractor):
    """基于孪生网络的特征提取器"""
    
    def __init__(self, model_path: Optional[str] = None, backbone: str = 'resnet18'):
        super().__init__(f"siamese_{backbone}")
        
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not available")
        
        self.feature_dim = 128
        self.model = SiameseNetwork(backbone=backbone, feature_dim=self.feature_dim)
        
        # 加载预训练权重
        if model_path and Path(model_path).exists():
            try:
                checkpoint = torch.load(model_path, map_location='cpu')
                self.model.load_state_dict(checkpoint['model_state_dict'])
                logging.info(f"加载预训练模型: {model_path}")
            except Exception as e:
                logging.warning(f"加载预训练模型失败: {e}")
        
        self.model.eval()
        
        # 图像预处理
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # 设备
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
    
    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """提取孪生网络特征"""
        try:
            # 预处理图像
            if len(image.shape) == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
            input_tensor = self.transform(image_rgb).unsqueeze(0).to(self.device)
            
            # 提取特征
            with torch.no_grad():
                features = self.model(input_tensor)
            
            return features.cpu().numpy().flatten()
            
        except Exception as e:
            logging.error(f"孪生网络特征提取失败: {e}")
            return np.zeros(self.feature_dim, dtype=np.float32)

class CoatPatternReID:
    """花色重识别主类"""
    
    def __init__(self, 
                 extractor_type: str = 'resnet',
                 model_path: Optional[str] = None,
                 similarity_threshold: float = 0.7):
        """
        初始化花色重识别器
        
        Args:
            extractor_type: 特征提取器类型 ('mock', 'resnet', 'siamese')
            model_path: 模型路径（用于siamese）
            similarity_threshold: 相似度阈值
        """
        self.similarity_threshold = similarity_threshold
        
        # 初始化特征提取器
        if extractor_type == 'mock' or not TORCH_AVAILABLE:
            self.feature_extractor = MockFeatureExtractor()
            logging.info("使用模拟特征提取器")
        elif extractor_type == 'resnet':
            try:
                self.feature_extractor = ResNetFeatureExtractor()
                logging.info("使用ResNet特征提取器")
            except Exception as e:
                logging.warning(f"ResNet初始化失败: {e}，使用模拟提取器")
                self.feature_extractor = MockFeatureExtractor()
        elif extractor_type == 'siamese':
            try:
                self.feature_extractor = SiameseFeatureExtractor(model_path)
                logging.info("使用孪生网络特征提取器")
            except Exception as e:
                logging.warning(f"孪生网络初始化失败: {e}，使用ResNet提取器")
                try:
                    self.feature_extractor = ResNetFeatureExtractor()
                except:
                    self.feature_extractor = MockFeatureExtractor()
        else:
            raise ValueError(f"不支持的特征提取器类型: {extractor_type}")
        
        # 相似度匹配器
        self.matcher = SimilarityMatcher(similarity_threshold)
        
        # 统计信息
        self.stats = {
            'total_extractions': 0,
            'total_matches': 0,
            'successful_matches': 0,
            'average_extraction_time': 0.0
        }
    
    def extract_coat_pattern_feature(self, image: np.ndarray) -> Optional[CoatPatternFeature]:
        """
        提取花色特征
        
        Args:
            image: 牛只图像
        
        Returns:
            花色特征对象
        """
        if image is None or image.size == 0:
            return None
        
        import time
        start_time = time.time()
        
        try:
            # 预处理图像
            processed_image = self._preprocess_image(image)
            
            # 提取特征向量
            feature_vector = self.feature_extractor.extract_features(processed_image)
            
            if feature_vector is None or len(feature_vector) == 0:
                return None
            
            # 计算图像哈希
            image_hash = self.feature_extractor.calculate_image_hash(processed_image)
            
            # 评估特征质量
            quality_score = self._evaluate_feature_quality(processed_image, feature_vector)
            
            # 更新统计信息
            extraction_time = time.time() - start_time
            self._update_extraction_stats(extraction_time)
            
            return CoatPatternFeature(
                feature_vector=feature_vector,
                extraction_method=self.feature_extractor.method_name,
                image_hash=image_hash,
                quality_score=quality_score,
                metadata={
                    'extraction_time': extraction_time,
                    'image_shape': image.shape,
                    'feature_dim': len(feature_vector)
                }
            )
            
        except Exception as e:
            logging.error(f"花色特征提取失败: {e}")
            return None
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """预处理图像"""
        # 调整图像大小
        target_size = (224, 224)
        resized = cv2.resize(image, target_size)
        
        # 增强对比度
        if len(resized.shape) == 3:
            lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(resized)
        
        return enhanced
    
    def _evaluate_feature_quality(self, image: np.ndarray, feature_vector: np.ndarray) -> float:
        """评估特征质量"""
        quality_factors = []
        
        # 图像质量因子
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 对比度
        contrast = np.std(gray) / 255.0
        quality_factors.append(min(contrast * 2, 1.0))
        
        # 清晰度（基于拉普拉斯算子）
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness = min(laplacian_var / 1000.0, 1.0)
        quality_factors.append(sharpness)
        
        # 特征向量质量
        feature_norm = np.linalg.norm(feature_vector)
        if feature_norm > 0:
            feature_quality = min(feature_norm / 10.0, 1.0)
        else:
            feature_quality = 0.0
        quality_factors.append(feature_quality)
        
        # 综合质量评分
        return np.mean(quality_factors)
    
    def identify_by_coat_pattern(self, 
                                image: np.ndarray,
                                candidate_profiles: List[CattleProfile]) -> IdentificationResult:
        """
        通过花色识别牛只身份
        
        Args:
            image: 牛只图像
            candidate_profiles: 候选牛只档案列表
        
        Returns:
            识别结果
        """
        self.stats['total_matches'] += 1
        
        # 提取查询特征
        query_feature = self.extract_coat_pattern_feature(image)
        
        if query_feature is None:
            return IdentificationResult(
                cattle_id=None,
                method=IdentificationMethod.COAT_PATTERN,
                confidence=0.0,
                metadata={'error': 'Feature extraction failed'}
            )
        
        # 查找最佳匹配
        best_match_id, similarity = self.matcher.find_best_match(
            query_feature, candidate_profiles
        )
        
        if best_match_id:
            self.stats['successful_matches'] += 1
            
            return IdentificationResult(
                cattle_id=best_match_id,
                method=IdentificationMethod.COAT_PATTERN,
                confidence=similarity,
                coat_pattern_match=best_match_id,
                metadata={
                    'similarity_score': similarity,
                    'feature_quality': query_feature.quality_score,
                    'extraction_method': query_feature.extraction_method,
                    'candidates_count': len(candidate_profiles)
                }
            )
        else:
            return IdentificationResult(
                cattle_id=None,
                method=IdentificationMethod.COAT_PATTERN,
                confidence=similarity,
                metadata={
                    'best_similarity': similarity,
                    'threshold': self.similarity_threshold,
                    'feature_quality': query_feature.quality_score
                }
            )
    
    def find_similar_cattle(self, 
                          image: np.ndarray,
                          candidate_profiles: List[CattleProfile],
                          top_k: int = 5) -> List[Tuple[str, float]]:
        """查找相似的牛只"""
        query_feature = self.extract_coat_pattern_feature(image)
        
        if query_feature is None:
            return []
        
        return self.matcher.find_top_matches(query_feature, candidate_profiles, top_k)
    
    def _update_extraction_stats(self, extraction_time: float):
        """更新提取统计信息"""
        self.stats['total_extractions'] += 1
        
        current_avg = self.stats['average_extraction_time']
        total_extractions = self.stats['total_extractions']
        
        if total_extractions == 1:
            self.stats['average_extraction_time'] = extraction_time
        else:
            self.stats['average_extraction_time'] = (
                (current_avg * (total_extractions - 1) + extraction_time) / total_extractions
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        
        if stats['total_matches'] > 0:
            stats['match_success_rate'] = stats['successful_matches'] / stats['total_matches']
        else:
            stats['match_success_rate'] = 0.0
        
        stats['feature_extractor'] = self.feature_extractor.method_name
        stats['similarity_threshold'] = self.similarity_threshold
        
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_extractions': 0,
            'total_matches': 0,
            'successful_matches': 0,
            'average_extraction_time': 0.0
        }
    
    def update_threshold(self, new_threshold: float):
        """更新相似度阈值"""
        self.similarity_threshold = new_threshold
        self.matcher.similarity_threshold = new_threshold
        logging.info(f"相似度阈值更新为: {new_threshold}")

# 预训练模型训练脚本（示例）
class TripletLoss(nn.Module):
    """三元组损失函数"""
    
    def __init__(self, margin: float = 1.0):
        super(TripletLoss, self).__init__()
        self.margin = margin
    
    def forward(self, anchor, positive, negative):
        distance_positive = F.pairwise_distance(anchor, positive, 2)
        distance_negative = F.pairwise_distance(anchor, negative, 2)
        losses = F.relu(distance_positive - distance_negative + self.margin)
        return losses.mean()

def train_siamese_model(train_loader, model, optimizer, criterion, device):
    """训练孪生网络（示例函数）"""
    model.train()
    total_loss = 0.0
    
    for batch_idx, (anchor, positive, negative) in enumerate(train_loader):
        anchor, positive, negative = anchor.to(device), positive.to(device), negative.to(device)
        
        optimizer.zero_grad()
        
        anchor_features = model(anchor)
        positive_features = model(positive)
        negative_features = model(negative)
        
        loss = criterion(anchor_features, positive_features, negative_features)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(train_loader)