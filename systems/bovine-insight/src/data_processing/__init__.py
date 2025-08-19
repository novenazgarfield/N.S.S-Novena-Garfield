"""
BovineInsight: 多源数据处理模块
Multi-Source Data Processing Module

负责处理来自不同摄像头的视频源，支持多线程并行处理
"""

from .camera_manager import CameraManager
from .video_processor import VideoProcessor
from .frame_buffer import FrameBuffer

__all__ = ['CameraManager', 'VideoProcessor', 'FrameBuffer']