"""
牛只检测器
Cattle Detector

使用YOLOv8模型进行牛只检测
"""

import cv2
import numpy as np
import torch
import logging
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from .detection_utils import DetectionResult, BoundingBox, DetectionFilter, NonMaxSuppression, DetectionTracker

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("ultralytics not available, using mock detector")

class MockYOLO:
    """YOLO模拟器，用于测试"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.names = {0: 'cow', 1: 'ear_tag'}
    
    def predict(self, source, conf=0.5, iou=0.5, verbose=False):
        """模拟预测"""
        if isinstance(source, np.ndarray):
            h, w = source.shape[:2]
            # 生成模拟检测结果
            mock_results = []
            
            # 模拟一个牛的检测框
            if np.random.random() > 0.3:  # 70%概率检测到牛
                x1 = np.random.randint(0, w//3)
                y1 = np.random.randint(0, h//3)
                x2 = x1 + np.random.randint(w//4, w//2)
                y2 = y1 + np.random.randint(h//4, h//2)
                
                # 确保边界框在图像范围内
                x2 = min(x2, w)
                y2 = min(y2, h)
                
                detection = np.array([x1, y1, x2, y2, 0.8, 0])  # cow class
                mock_results.append(MockResult([detection]))
        
        return mock_results

class MockResult:
    """模拟YOLO结果"""
    
    def __init__(self, boxes_data):
        self.boxes = MockBoxes(boxes_data)

class MockBoxes:
    """模拟YOLO边界框"""
    
    def __init__(self, boxes_data):
        self.data = torch.tensor(boxes_data) if boxes_data else torch.empty((0, 6))

class CattleDetector:
    """牛只检测器主类"""
    
    def __init__(self, 
                 model_path: str = None,
                 confidence_threshold: float = 0.5,
                 iou_threshold: float = 0.5,
                 device: str = 'auto'):
        """
        初始化牛只检测器
        
        Args:
            model_path: YOLO模型路径
            confidence_threshold: 置信度阈值
            iou_threshold: IoU阈值
            device: 设备类型 ('auto', 'cpu', 'cuda')
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.device = self._setup_device(device)
        
        # 初始化模型
        self.model = self._load_model()
        
        # 初始化后处理组件
        self.filter = DetectionFilter(
            min_confidence=confidence_threshold,
            min_area=500,  # 最小面积，过滤小的误检
            allowed_classes=['cow', 'cattle', 'bovine']
        )
        self.nms = NonMaxSuppression(iou_threshold=iou_threshold)
        self.tracker = DetectionTracker()
        
        # 统计信息
        self.stats = {
            'total_detections': 0,
            'total_frames': 0,
            'average_detections_per_frame': 0.0,
            'processing_time': 0.0
        }
        
        logging.info(f"牛只检测器初始化完成，设备: {self.device}")
    
    def _setup_device(self, device: str) -> str:
        """设置计算设备"""
        if device == 'auto':
            if torch.cuda.is_available():
                return 'cuda'
            else:
                return 'cpu'
        return device
    
    def _load_model(self):
        """加载YOLO模型"""
        if not YOLO_AVAILABLE:
            logging.warning("使用模拟检测器")
            return MockYOLO(self.model_path or "mock_model")
        
        try:
            if self.model_path and Path(self.model_path).exists():
                model = YOLO(self.model_path)
                logging.info(f"加载自定义模型: {self.model_path}")
            else:
                # 使用预训练模型
                model = YOLO('yolov8n.pt')  # 使用nano版本，速度快
                logging.info("加载预训练YOLOv8模型")
            
            # 移动到指定设备
            if self.device == 'cuda' and torch.cuda.is_available():
                model.to('cuda')
            
            return model
            
        except Exception as e:
            logging.error(f"模型加载失败: {e}")
            logging.warning("使用模拟检测器")
            return MockYOLO(self.model_path or "mock_model")
    
    def detect(self, image: np.ndarray, enable_tracking: bool = True) -> List[DetectionResult]:
        """
        检测图像中的牛只
        
        Args:
            image: 输入图像
            enable_tracking: 是否启用跟踪
        
        Returns:
            检测结果列表
        """
        if image is None:
            return []
        
        import time
        start_time = time.time()
        
        try:
            # 运行YOLO检测
            results = self.model.predict(
                source=image,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False
            )
            
            # 解析检测结果
            detections = self._parse_yolo_results(results)
            
            # 应用过滤器
            detections = self.filter.filter_detections(detections)
            
            # 应用非极大值抑制
            detections = self.nms.apply(detections)
            
            # 应用跟踪
            if enable_tracking:
                detections = self.tracker.update(detections)
            
            # 更新统计信息
            processing_time = time.time() - start_time
            self._update_stats(len(detections), processing_time)
            
            return detections
            
        except Exception as e:
            logging.error(f"检测过程出错: {e}")
            return []
    
    def _parse_yolo_results(self, results) -> List[DetectionResult]:
        """解析YOLO检测结果"""
        detections = []
        
        if not results:
            return detections
        
        for result in results:
            if hasattr(result, 'boxes') and result.boxes is not None:
                boxes_data = result.boxes.data
                
                if len(boxes_data) > 0:
                    for box_data in boxes_data:
                        # YOLO输出格式: [x1, y1, x2, y2, confidence, class_id]
                        if len(box_data) >= 6:
                            x1, y1, x2, y2, conf, class_id = box_data[:6]
                            
                            # 获取类别名称
                            class_names = getattr(self.model, 'names', {0: 'cow'})
                            class_name = class_names.get(int(class_id), 'unknown')
                            
                            # 只保留牛相关的检测
                            if class_name.lower() in ['cow', 'cattle', 'bovine', '0']:
                                bbox = BoundingBox(
                                    x1=float(x1), y1=float(y1),
                                    x2=float(x2), y2=float(y2)
                                )
                                
                                detection = DetectionResult(
                                    bbox=bbox,
                                    confidence=float(conf),
                                    class_id=int(class_id),
                                    class_name='cow'  # 统一为cow
                                )
                                
                                detections.append(detection)
        
        return detections
    
    def detect_batch(self, images: List[np.ndarray]) -> List[List[DetectionResult]]:
        """批量检测"""
        results = []
        for image in images:
            detections = self.detect(image, enable_tracking=False)
            results.append(detections)
        return results
    
    def detect_and_crop(self, image: np.ndarray, expand_factor: float = 1.1) -> List[Tuple[DetectionResult, np.ndarray]]:
        """检测并裁剪牛只区域"""
        detections = self.detect(image, enable_tracking=False)
        cropped_results = []
        
        h, w = image.shape[:2]
        
        for detection in detections:
            # 扩展边界框
            expanded_bbox = detection.bbox.expand(expand_factor)
            
            # 限制在图像范围内
            clipped_bbox = expanded_bbox.clip(w, h)
            
            # 裁剪图像
            x1, y1, x2, y2 = map(int, clipped_bbox.to_xyxy())
            cropped_image = image[y1:y2, x1:x2]
            
            if cropped_image.size > 0:
                cropped_results.append((detection, cropped_image))
        
        return cropped_results
    
    def _update_stats(self, num_detections: int, processing_time: float):
        """更新统计信息"""
        self.stats['total_detections'] += num_detections
        self.stats['total_frames'] += 1
        self.stats['processing_time'] += processing_time
        
        if self.stats['total_frames'] > 0:
            self.stats['average_detections_per_frame'] = (
                self.stats['total_detections'] / self.stats['total_frames']
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取检测统计信息"""
        stats = self.stats.copy()
        if self.stats['total_frames'] > 0:
            stats['average_processing_time'] = (
                self.stats['processing_time'] / self.stats['total_frames']
            )
        else:
            stats['average_processing_time'] = 0.0
        
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_detections': 0,
            'total_frames': 0,
            'average_detections_per_frame': 0.0,
            'processing_time': 0.0
        }
        
    def update_config(self, **kwargs):
        """更新配置参数"""
        if 'confidence_threshold' in kwargs:
            self.confidence_threshold = kwargs['confidence_threshold']
            self.filter.min_confidence = kwargs['confidence_threshold']
        
        if 'iou_threshold' in kwargs:
            self.iou_threshold = kwargs['iou_threshold']
            self.nms.iou_threshold = kwargs['iou_threshold']
    
    def visualize_detections(self, image: np.ndarray, detections: List[DetectionResult]) -> np.ndarray:
        """可视化检测结果"""
        vis_image = image.copy()
        
        for detection in detections:
            bbox = detection.bbox
            x1, y1, x2, y2 = map(int, bbox.to_xyxy())
            
            # 绘制边界框
            color = (0, 255, 0)  # 绿色
            thickness = 2
            cv2.rectangle(vis_image, (x1, y1), (x2, y2), color, thickness)
            
            # 绘制标签
            label = f"{detection.class_name}: {detection.confidence:.2f}"
            if detection.track_id is not None:
                label += f" ID:{detection.track_id}"
            
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            cv2.rectangle(vis_image, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(vis_image, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return vis_image

class EarTagDetector(CattleDetector):
    """耳标检测器（继承自牛只检测器）"""
    
    def __init__(self, model_path: str = None, **kwargs):
        super().__init__(model_path, **kwargs)
        
        # 专门用于耳标检测的过滤器
        self.filter = DetectionFilter(
            min_confidence=0.3,  # 耳标检测可以使用较低的阈值
            min_area=50,         # 耳标面积较小
            max_area=5000,       # 限制最大面积
            allowed_classes=['ear_tag', 'tag', 'ear']
        )
    
    def detect_ear_tags_in_cattle(self, image: np.ndarray, cattle_bbox: BoundingBox) -> List[DetectionResult]:
        """在牛只区域内检测耳标"""
        # 裁剪牛只区域
        x1, y1, x2, y2 = map(int, cattle_bbox.to_xyxy())
        cattle_region = image[y1:y2, x1:x2]
        
        if cattle_region.size == 0:
            return []
        
        # 在裁剪区域内检测耳标
        ear_tag_detections = self.detect(cattle_region, enable_tracking=False)
        
        # 将坐标转换回原图坐标系
        for detection in ear_tag_detections:
            detection.bbox.x1 += x1
            detection.bbox.y1 += y1
            detection.bbox.x2 += x1
            detection.bbox.y2 += y1
        
        return ear_tag_detections