"""
检测工具类
Detection Utilities

定义检测结果的数据结构和工具函数
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum

class DetectionClass(Enum):
    """检测类别枚举"""
    COW = "cow"
    EAR_TAG = "ear_tag"
    UNKNOWN = "unknown"

@dataclass
class BoundingBox:
    """边界框数据结构"""
    x1: float  # 左上角x坐标
    y1: float  # 左上角y坐标
    x2: float  # 右下角x坐标
    y2: float  # 右下角y坐标
    
    @property
    def width(self) -> float:
        """边界框宽度"""
        return self.x2 - self.x1
    
    @property
    def height(self) -> float:
        """边界框高度"""
        return self.y2 - self.y1
    
    @property
    def center(self) -> Tuple[float, float]:
        """边界框中心点"""
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)
    
    @property
    def area(self) -> float:
        """边界框面积"""
        return self.width * self.height
    
    def to_xyxy(self) -> List[float]:
        """转换为xyxy格式"""
        return [self.x1, self.y1, self.x2, self.y2]
    
    def to_xywh(self) -> List[float]:
        """转换为xywh格式"""
        return [self.x1, self.y1, self.width, self.height]
    
    def to_cxcywh(self) -> List[float]:
        """转换为中心点+宽高格式"""
        cx, cy = self.center
        return [cx, cy, self.width, self.height]
    
    def iou(self, other: 'BoundingBox') -> float:
        """计算与另一个边界框的IoU"""
        # 计算交集区域
        x1_inter = max(self.x1, other.x1)
        y1_inter = max(self.y1, other.y1)
        x2_inter = min(self.x2, other.x2)
        y2_inter = min(self.y2, other.y2)
        
        # 检查是否有交集
        if x1_inter >= x2_inter or y1_inter >= y2_inter:
            return 0.0
        
        # 计算交集面积
        inter_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)
        
        # 计算并集面积
        union_area = self.area + other.area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0
    
    def expand(self, factor: float) -> 'BoundingBox':
        """扩展边界框"""
        center_x, center_y = self.center
        new_width = self.width * factor
        new_height = self.height * factor
        
        return BoundingBox(
            x1=center_x - new_width / 2,
            y1=center_y - new_height / 2,
            x2=center_x + new_width / 2,
            y2=center_y + new_height / 2
        )
    
    def clip(self, img_width: int, img_height: int) -> 'BoundingBox':
        """将边界框限制在图像范围内"""
        return BoundingBox(
            x1=max(0, min(self.x1, img_width)),
            y1=max(0, min(self.y1, img_height)),
            x2=max(0, min(self.x2, img_width)),
            y2=max(0, min(self.y2, img_height))
        )

@dataclass
class DetectionResult:
    """检测结果数据结构"""
    bbox: BoundingBox
    confidence: float
    class_id: int
    class_name: str
    track_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @classmethod
    def from_yolo_output(cls, detection: np.ndarray, class_names: List[str]) -> 'DetectionResult':
        """从YOLO输出创建检测结果"""
        x1, y1, x2, y2, conf, class_id = detection[:6]
        
        bbox = BoundingBox(x1=float(x1), y1=float(y1), x2=float(x2), y2=float(y2))
        class_id = int(class_id)
        class_name = class_names[class_id] if class_id < len(class_names) else "unknown"
        
        return cls(
            bbox=bbox,
            confidence=float(conf),
            class_id=class_id,
            class_name=class_name
        )

class DetectionFilter:
    """检测结果过滤器"""
    
    def __init__(self, 
                 min_confidence: float = 0.5,
                 min_area: float = 100.0,
                 max_area: float = None,
                 allowed_classes: List[str] = None):
        self.min_confidence = min_confidence
        self.min_area = min_area
        self.max_area = max_area
        self.allowed_classes = allowed_classes or []
    
    def filter_detections(self, detections: List[DetectionResult]) -> List[DetectionResult]:
        """过滤检测结果"""
        filtered = []
        
        for detection in detections:
            # 置信度过滤
            if detection.confidence < self.min_confidence:
                continue
            
            # 类别过滤
            if self.allowed_classes and detection.class_name not in self.allowed_classes:
                continue
            
            # 面积过滤
            area = detection.bbox.area
            if area < self.min_area:
                continue
            
            if self.max_area and area > self.max_area:
                continue
            
            filtered.append(detection)
        
        return filtered

class NonMaxSuppression:
    """非极大值抑制"""
    
    def __init__(self, iou_threshold: float = 0.5):
        self.iou_threshold = iou_threshold
    
    def apply(self, detections: List[DetectionResult]) -> List[DetectionResult]:
        """应用非极大值抑制"""
        if not detections:
            return []
        
        # 按置信度排序
        detections = sorted(detections, key=lambda x: x.confidence, reverse=True)
        
        # 按类别分组处理
        class_groups = {}
        for detection in detections:
            class_name = detection.class_name
            if class_name not in class_groups:
                class_groups[class_name] = []
            class_groups[class_name].append(detection)
        
        # 对每个类别应用NMS
        final_detections = []
        for class_name, class_detections in class_groups.items():
            nms_results = self._nms_single_class(class_detections)
            final_detections.extend(nms_results)
        
        return final_detections
    
    def _nms_single_class(self, detections: List[DetectionResult]) -> List[DetectionResult]:
        """对单个类别应用NMS"""
        if not detections:
            return []
        
        keep = []
        remaining = list(range(len(detections)))
        
        while remaining:
            # 选择置信度最高的检测
            current_idx = remaining[0]
            keep.append(detections[current_idx])
            remaining.remove(current_idx)
            
            # 移除与当前检测IoU过高的其他检测
            to_remove = []
            for idx in remaining:
                iou = detections[current_idx].bbox.iou(detections[idx].bbox)
                if iou > self.iou_threshold:
                    to_remove.append(idx)
            
            for idx in to_remove:
                remaining.remove(idx)
        
        return keep

class DetectionTracker:
    """简单的检测跟踪器"""
    
    def __init__(self, max_disappeared: int = 10, max_distance: float = 50.0):
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        self.next_id = 0
        self.objects = {}  # {track_id: {'bbox': BoundingBox, 'disappeared': int}}
    
    def update(self, detections: List[DetectionResult]) -> List[DetectionResult]:
        """更新跟踪"""
        if not detections:
            # 增加所有对象的消失计数
            for track_id in list(self.objects.keys()):
                self.objects[track_id]['disappeared'] += 1
                if self.objects[track_id]['disappeared'] > self.max_disappeared:
                    del self.objects[track_id]
            return []
        
        # 如果没有现有对象，为所有检测分配新ID
        if not self.objects:
            for detection in detections:
                detection.track_id = self.next_id
                self.objects[self.next_id] = {
                    'bbox': detection.bbox,
                    'disappeared': 0
                }
                self.next_id += 1
            return detections
        
        # 计算检测与现有对象的距离矩阵
        object_ids = list(self.objects.keys())
        distances = np.zeros((len(detections), len(object_ids)))
        
        for i, detection in enumerate(detections):
            det_center = detection.bbox.center
            for j, obj_id in enumerate(object_ids):
                obj_center = self.objects[obj_id]['bbox'].center
                distances[i, j] = np.sqrt(
                    (det_center[0] - obj_center[0]) ** 2 + 
                    (det_center[1] - obj_center[1]) ** 2
                )
        
        # 使用匈牙利算法或简单贪心匹配
        matched_detections = []
        used_detection_indices = set()
        used_object_indices = set()
        
        # 简单贪心匹配
        for _ in range(min(len(detections), len(object_ids))):
            min_distance = float('inf')
            min_i, min_j = -1, -1
            
            for i in range(len(detections)):
                if i in used_detection_indices:
                    continue
                for j in range(len(object_ids)):
                    if j in used_object_indices:
                        continue
                    if distances[i, j] < min_distance and distances[i, j] < self.max_distance:
                        min_distance = distances[i, j]
                        min_i, min_j = i, j
            
            if min_i != -1 and min_j != -1:
                # 匹配成功
                detection = detections[min_i]
                obj_id = object_ids[min_j]
                detection.track_id = obj_id
                
                # 更新对象信息
                self.objects[obj_id]['bbox'] = detection.bbox
                self.objects[obj_id]['disappeared'] = 0
                
                matched_detections.append(detection)
                used_detection_indices.add(min_i)
                used_object_indices.add(min_j)
        
        # 处理未匹配的检测（分配新ID）
        for i, detection in enumerate(detections):
            if i not in used_detection_indices:
                detection.track_id = self.next_id
                self.objects[self.next_id] = {
                    'bbox': detection.bbox,
                    'disappeared': 0
                }
                self.next_id += 1
                matched_detections.append(detection)
        
        # 处理未匹配的对象（增加消失计数）
        for j, obj_id in enumerate(object_ids):
            if j not in used_object_indices:
                self.objects[obj_id]['disappeared'] += 1
                if self.objects[obj_id]['disappeared'] > self.max_disappeared:
                    del self.objects[obj_id]
        
        return matched_detections

def calculate_detection_metrics(predictions: List[DetectionResult], 
                              ground_truths: List[DetectionResult],
                              iou_threshold: float = 0.5) -> Dict[str, float]:
    """计算检测指标"""
    if not predictions and not ground_truths:
        return {'precision': 1.0, 'recall': 1.0, 'f1': 1.0}
    
    if not predictions:
        return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
    
    if not ground_truths:
        return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
    
    # 计算TP, FP, FN
    tp = 0
    matched_gt = set()
    
    for pred in predictions:
        best_iou = 0.0
        best_gt_idx = -1
        
        for i, gt in enumerate(ground_truths):
            if i in matched_gt:
                continue
            
            if pred.class_name == gt.class_name:
                iou = pred.bbox.iou(gt.bbox)
                if iou > best_iou:
                    best_iou = iou
                    best_gt_idx = i
        
        if best_iou >= iou_threshold and best_gt_idx != -1:
            tp += 1
            matched_gt.add(best_gt_idx)
    
    fp = len(predictions) - tp
    fn = len(ground_truths) - tp
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'tp': tp,
        'fp': fp,
        'fn': fn
    }