"""
帧缓冲器
Frame Buffer

管理多摄像头的帧缓存，支持时间同步和帧匹配
"""

import threading
import time
import numpy as np
from collections import deque
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

@dataclass
class FrameData:
    """帧数据结构"""
    frame: np.ndarray
    timestamp: float
    camera_name: str
    frame_id: int
    metadata: Dict = None

class FrameBuffer:
    """帧缓冲器"""
    
    def __init__(self, max_buffer_size: int = 30, sync_tolerance: float = 0.1):
        """
        初始化帧缓冲器
        
        Args:
            max_buffer_size: 每个摄像头的最大缓存帧数
            sync_tolerance: 时间同步容差（秒）
        """
        self.max_buffer_size = max_buffer_size
        self.sync_tolerance = sync_tolerance
        self.buffers: Dict[str, deque] = {}
        self.frame_counters: Dict[str, int] = {}
        self.lock = threading.Lock()
        
        # 统计信息
        self.stats = {
            'total_frames_added': 0,
            'total_frames_retrieved': 0,
            'sync_matches': 0,
            'buffer_overflows': 0
        }
    
    def add_frame(self, camera_name: str, frame: np.ndarray, metadata: Dict = None):
        """添加帧到缓冲区"""
        with self.lock:
            # 初始化摄像头缓冲区
            if camera_name not in self.buffers:
                self.buffers[camera_name] = deque(maxlen=self.max_buffer_size)
                self.frame_counters[camera_name] = 0
            
            # 创建帧数据
            frame_data = FrameData(
                frame=frame.copy(),
                timestamp=time.time(),
                camera_name=camera_name,
                frame_id=self.frame_counters[camera_name],
                metadata=metadata or {}
            )
            
            # 检查缓冲区是否已满
            if len(self.buffers[camera_name]) >= self.max_buffer_size:
                self.stats['buffer_overflows'] += 1
            
            # 添加到缓冲区
            self.buffers[camera_name].append(frame_data)
            self.frame_counters[camera_name] += 1
            self.stats['total_frames_added'] += 1
    
    def get_latest_frames(self) -> Dict[str, FrameData]:
        """获取所有摄像头的最新帧"""
        with self.lock:
            latest_frames = {}
            for camera_name, buffer in self.buffers.items():
                if buffer:
                    latest_frames[camera_name] = buffer[-1]
            
            self.stats['total_frames_retrieved'] += len(latest_frames)
            return latest_frames
    
    def get_synchronized_frames(self, reference_camera: str = None) -> Optional[Dict[str, FrameData]]:
        """
        获取时间同步的帧组
        
        Args:
            reference_camera: 参考摄像头名称，如果为None则使用最新的帧作为参考
        
        Returns:
            同步的帧组，如果无法同步则返回None
        """
        with self.lock:
            if not self.buffers:
                return None
            
            # 确定参考时间戳
            reference_timestamp = None
            if reference_camera and reference_camera in self.buffers:
                if self.buffers[reference_camera]:
                    reference_timestamp = self.buffers[reference_camera][-1].timestamp
            else:
                # 使用所有摄像头中最新的时间戳作为参考
                latest_timestamps = []
                for buffer in self.buffers.values():
                    if buffer:
                        latest_timestamps.append(buffer[-1].timestamp)
                if latest_timestamps:
                    reference_timestamp = max(latest_timestamps)
            
            if reference_timestamp is None:
                return None
            
            # 查找每个摄像头中最接近参考时间戳的帧
            synchronized_frames = {}
            for camera_name, buffer in self.buffers.items():
                best_frame = self._find_closest_frame(buffer, reference_timestamp)
                if best_frame:
                    synchronized_frames[camera_name] = best_frame
            
            # 检查是否所有摄像头都找到了同步帧
            if len(synchronized_frames) == len(self.buffers):
                self.stats['sync_matches'] += 1
                self.stats['total_frames_retrieved'] += len(synchronized_frames)
                return synchronized_frames
            
            return None
    
    def _find_closest_frame(self, buffer: deque, target_timestamp: float) -> Optional[FrameData]:
        """在缓冲区中查找最接近目标时间戳的帧"""
        if not buffer:
            return None
        
        best_frame = None
        min_time_diff = float('inf')
        
        for frame_data in buffer:
            time_diff = abs(frame_data.timestamp - target_timestamp)
            if time_diff < min_time_diff and time_diff <= self.sync_tolerance:
                min_time_diff = time_diff
                best_frame = frame_data
        
        return best_frame
    
    def get_frame_by_id(self, camera_name: str, frame_id: int) -> Optional[FrameData]:
        """根据帧ID获取特定帧"""
        with self.lock:
            if camera_name not in self.buffers:
                return None
            
            for frame_data in self.buffers[camera_name]:
                if frame_data.frame_id == frame_id:
                    return frame_data
            
            return None
    
    def get_frames_in_range(self, camera_name: str, start_time: float, end_time: float) -> List[FrameData]:
        """获取指定时间范围内的帧"""
        with self.lock:
            if camera_name not in self.buffers:
                return []
            
            frames_in_range = []
            for frame_data in self.buffers[camera_name]:
                if start_time <= frame_data.timestamp <= end_time:
                    frames_in_range.append(frame_data)
            
            return frames_in_range
    
    def clear_buffer(self, camera_name: str = None):
        """清空缓冲区"""
        with self.lock:
            if camera_name:
                if camera_name in self.buffers:
                    self.buffers[camera_name].clear()
            else:
                for buffer in self.buffers.values():
                    buffer.clear()
    
    def remove_old_frames(self, max_age: float = 5.0):
        """移除过期的帧"""
        current_time = time.time()
        with self.lock:
            for camera_name, buffer in self.buffers.items():
                # 从前面开始移除过期帧
                while buffer and (current_time - buffer[0].timestamp) > max_age:
                    buffer.popleft()
    
    def get_buffer_status(self) -> Dict:
        """获取缓冲区状态"""
        with self.lock:
            status = {
                'cameras': {},
                'total_cameras': len(self.buffers),
                'stats': self.stats.copy()
            }
            
            for camera_name, buffer in self.buffers.items():
                camera_status = {
                    'buffer_size': len(buffer),
                    'max_buffer_size': self.max_buffer_size,
                    'latest_timestamp': buffer[-1].timestamp if buffer else None,
                    'oldest_timestamp': buffer[0].timestamp if buffer else None,
                    'frame_count': self.frame_counters.get(camera_name, 0)
                }
                status['cameras'][camera_name] = camera_status
            
            return status
    
    def optimize_buffers(self):
        """优化缓冲区，移除重复或不必要的帧"""
        with self.lock:
            for camera_name, buffer in self.buffers.items():
                if len(buffer) <= 1:
                    continue
                
                # 移除时间戳过于接近的帧（可能是重复帧）
                optimized_buffer = deque(maxlen=self.max_buffer_size)
                last_timestamp = None
                
                for frame_data in buffer:
                    if last_timestamp is None or (frame_data.timestamp - last_timestamp) > 0.01:
                        optimized_buffer.append(frame_data)
                        last_timestamp = frame_data.timestamp
                
                self.buffers[camera_name] = optimized_buffer

class MultiCameraFrameSync:
    """多摄像头帧同步器"""
    
    def __init__(self, camera_names: List[str], sync_tolerance: float = 0.1):
        self.camera_names = camera_names
        self.sync_tolerance = sync_tolerance
        self.frame_buffer = FrameBuffer(sync_tolerance=sync_tolerance)
        self.sync_stats = {
            'successful_syncs': 0,
            'failed_syncs': 0,
            'average_sync_error': 0.0
        }
    
    def add_frames(self, frames: Dict[str, np.ndarray]):
        """添加多摄像头帧"""
        for camera_name, frame in frames.items():
            if camera_name in self.camera_names:
                self.frame_buffer.add_frame(camera_name, frame)
    
    def get_synchronized_set(self) -> Optional[Dict[str, np.ndarray]]:
        """获取同步的帧集合"""
        sync_frames = self.frame_buffer.get_synchronized_frames()
        
        if sync_frames and len(sync_frames) == len(self.camera_names):
            # 计算同步误差
            timestamps = [frame_data.timestamp for frame_data in sync_frames.values()]
            sync_error = max(timestamps) - min(timestamps)
            
            # 更新统计
            self.sync_stats['successful_syncs'] += 1
            self.sync_stats['average_sync_error'] = (
                (self.sync_stats['average_sync_error'] * (self.sync_stats['successful_syncs'] - 1) + sync_error) /
                self.sync_stats['successful_syncs']
            )
            
            # 返回纯帧数据
            result = {}
            for camera_name, frame_data in sync_frames.items():
                result[camera_name] = frame_data.frame
            
            return result
        else:
            self.sync_stats['failed_syncs'] += 1
            return None
    
    def get_sync_quality(self) -> float:
        """获取同步质量评分 (0-1)"""
        total_attempts = self.sync_stats['successful_syncs'] + self.sync_stats['failed_syncs']
        if total_attempts == 0:
            return 0.0
        
        success_rate = self.sync_stats['successful_syncs'] / total_attempts
        
        # 考虑同步误差
        if self.sync_stats['average_sync_error'] > 0:
            error_penalty = min(self.sync_stats['average_sync_error'] / self.sync_tolerance, 1.0)
            success_rate *= (1.0 - error_penalty * 0.5)
        
        return success_rate