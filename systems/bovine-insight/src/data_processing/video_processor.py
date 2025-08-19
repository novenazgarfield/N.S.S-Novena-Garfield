"""
视频处理器
Video Processor

负责对视频帧进行预处理，包括图像增强、标准化等操作
"""

import cv2
import numpy as np
import threading
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum

class ProcessingMode(Enum):
    """处理模式"""
    REAL_TIME = "real_time"      # 实时处理
    BATCH = "batch"              # 批处理
    QUALITY = "quality"          # 质量优先

@dataclass
class ProcessingConfig:
    """处理配置"""
    mode: ProcessingMode = ProcessingMode.REAL_TIME
    target_size: Tuple[int, int] = (640, 640)  # 目标尺寸
    normalize: bool = True                      # 是否标准化
    enhance_contrast: bool = True               # 是否增强对比度
    denoise: bool = False                       # 是否降噪
    brightness_adjustment: float = 0.0          # 亮度调整 (-1.0 to 1.0)
    contrast_adjustment: float = 1.0            # 对比度调整 (0.5 to 2.0)
    gamma_correction: float = 1.0               # 伽马校正 (0.5 to 2.0)

class FrameProcessor:
    """单帧处理器"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        
    def process_frame(self, frame: np.ndarray, camera_type: str = None) -> np.ndarray:
        """处理单帧图像"""
        if frame is None:
            return None
        
        processed_frame = frame.copy()
        
        # 根据摄像头类型进行特定处理
        if camera_type == "ear_tag":
            processed_frame = self._process_ear_tag_frame(processed_frame)
        elif camera_type == "body_condition":
            processed_frame = self._process_body_condition_frame(processed_frame)
        
        # 通用处理
        processed_frame = self._apply_common_processing(processed_frame)
        
        return processed_frame
    
    def _process_ear_tag_frame(self, frame: np.ndarray) -> np.ndarray:
        """处理耳标识别专用帧"""
        # 增强对比度以便更好地识别耳标文字
        if self.config.enhance_contrast:
            frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
        
        # 锐化处理，提高文字清晰度
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        frame = cv2.filter2D(frame, -1, kernel)
        
        return frame
    
    def _process_body_condition_frame(self, frame: np.ndarray) -> np.ndarray:
        """处理体况评分专用帧"""
        # 轻微模糊以减少噪声，便于轮廓检测
        if self.config.denoise:
            frame = cv2.GaussianBlur(frame, (3, 3), 0)
        
        # 增强边缘
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # 将边缘信息融合到原图
        frame = cv2.addWeighted(frame, 0.8, edges_colored, 0.2, 0)
        
        return frame
    
    def _apply_common_processing(self, frame: np.ndarray) -> np.ndarray:
        """应用通用处理"""
        # 亮度调整
        if self.config.brightness_adjustment != 0.0:
            frame = cv2.convertScaleAbs(frame, alpha=1.0, 
                                      beta=self.config.brightness_adjustment * 255)
        
        # 对比度调整
        if self.config.contrast_adjustment != 1.0:
            frame = cv2.convertScaleAbs(frame, alpha=self.config.contrast_adjustment, beta=0)
        
        # 伽马校正
        if self.config.gamma_correction != 1.0:
            gamma = self.config.gamma_correction
            inv_gamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255 
                            for i in np.arange(0, 256)]).astype("uint8")
            frame = cv2.LUT(frame, table)
        
        # 降噪
        if self.config.denoise:
            frame = cv2.bilateralFilter(frame, 9, 75, 75)
        
        # 尺寸调整
        if self.config.target_size:
            frame = cv2.resize(frame, self.config.target_size)
        
        # 标准化
        if self.config.normalize:
            frame = frame.astype(np.float32) / 255.0
        
        return frame

class VideoProcessor:
    """视频处理器主类"""
    
    def __init__(self, config: ProcessingConfig = None):
        self.config = config or ProcessingConfig()
        self.frame_processor = FrameProcessor(self.config)
        self.processing_stats = {
            'total_frames': 0,
            'processing_time': 0.0,
            'average_fps': 0.0
        }
        self.lock = threading.Lock()
        
    def process_frames(self, frames: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """批量处理多个摄像头的帧"""
        start_time = time.time()
        processed_frames = {}
        
        for camera_name, frame in frames.items():
            if frame is not None:
                # 根据摄像头名称推断类型
                camera_type = self._infer_camera_type(camera_name)
                processed_frame = self.frame_processor.process_frame(frame, camera_type)
                processed_frames[camera_name] = processed_frame
        
        # 更新统计信息
        processing_time = time.time() - start_time
        with self.lock:
            self.processing_stats['total_frames'] += len(frames)
            self.processing_stats['processing_time'] += processing_time
            if self.processing_stats['processing_time'] > 0:
                self.processing_stats['average_fps'] = (
                    self.processing_stats['total_frames'] / 
                    self.processing_stats['processing_time']
                )
        
        return processed_frames
    
    def _infer_camera_type(self, camera_name: str) -> str:
        """根据摄像头名称推断类型"""
        name_lower = camera_name.lower()
        if 'ear_tag' in name_lower or 'ear' in name_lower:
            return 'ear_tag'
        elif 'body' in name_lower or 'condition' in name_lower:
            return 'body_condition'
        else:
            return 'general'
    
    def create_preprocessing_pipeline(self, camera_type: str) -> Callable:
        """创建预处理管道"""
        def pipeline(frame: np.ndarray) -> np.ndarray:
            return self.frame_processor.process_frame(frame, camera_type)
        return pipeline
    
    def get_stats(self) -> Dict:
        """获取处理统计信息"""
        with self.lock:
            return self.processing_stats.copy()
    
    def reset_stats(self):
        """重置统计信息"""
        with self.lock:
            self.processing_stats = {
                'total_frames': 0,
                'processing_time': 0.0,
                'average_fps': 0.0
            }

class AdaptiveProcessor:
    """自适应处理器 - 根据系统负载自动调整处理参数"""
    
    def __init__(self, base_config: ProcessingConfig):
        self.base_config = base_config
        self.current_config = base_config
        self.performance_history = []
        self.adaptation_threshold = 0.8  # 性能阈值
        
    def adapt_processing(self, current_fps: float, target_fps: float = 30.0):
        """根据当前性能自适应调整处理参数"""
        performance_ratio = current_fps / target_fps
        self.performance_history.append(performance_ratio)
        
        # 保持最近10次的性能记录
        if len(self.performance_history) > 10:
            self.performance_history.pop(0)
        
        # 计算平均性能
        avg_performance = np.mean(self.performance_history)
        
        if avg_performance < self.adaptation_threshold:
            # 性能不足，降低处理质量
            self._reduce_quality()
        elif avg_performance > 1.2:
            # 性能充足，可以提高处理质量
            self._increase_quality()
    
    def _reduce_quality(self):
        """降低处理质量以提高性能"""
        # 减小目标尺寸
        current_size = self.current_config.target_size
        new_size = (int(current_size[0] * 0.9), int(current_size[1] * 0.9))
        self.current_config.target_size = max(new_size, (320, 320))
        
        # 关闭一些耗时的处理
        self.current_config.denoise = False
        self.current_config.enhance_contrast = False
    
    def _increase_quality(self):
        """提高处理质量"""
        # 增大目标尺寸（不超过基础配置）
        base_size = self.base_config.target_size
        current_size = self.current_config.target_size
        if current_size[0] < base_size[0]:
            new_size = (int(current_size[0] * 1.1), int(current_size[1] * 1.1))
            self.current_config.target_size = min(new_size, base_size)
        
        # 恢复处理选项
        self.current_config.denoise = self.base_config.denoise
        self.current_config.enhance_contrast = self.base_config.enhance_contrast

# 预定义的处理配置
PROCESSING_CONFIGS = {
    'high_quality': ProcessingConfig(
        mode=ProcessingMode.QUALITY,
        target_size=(1280, 1280),
        normalize=True,
        enhance_contrast=True,
        denoise=True,
        gamma_correction=1.2
    ),
    'balanced': ProcessingConfig(
        mode=ProcessingMode.REAL_TIME,
        target_size=(640, 640),
        normalize=True,
        enhance_contrast=True,
        denoise=False,
        gamma_correction=1.0
    ),
    'fast': ProcessingConfig(
        mode=ProcessingMode.REAL_TIME,
        target_size=(416, 416),
        normalize=True,
        enhance_contrast=False,
        denoise=False,
        gamma_correction=1.0
    )
}