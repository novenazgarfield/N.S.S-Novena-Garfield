"""
BovineInsight: 多摄像头牛只身份识别与体况评分系统
主程序入口

Main Entry Point for BovineInsight System
"""

import os
import sys
import logging
import argparse
import time
import signal
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_processing import CameraManager, VideoProcessor, FrameBuffer
from src.data_processing.camera_manager import CameraConfig, CameraType, DEFAULT_CONFIGS
from src.detection import CattleDetector, ModelManager
from src.identification import FusedIdentifier, EarTagReader, CoatPatternReID
from src.database.cattle_database import CattleDatabase
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logging

class BovineInsightSystem:
    """BovineInsight系统主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化系统
        
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # 设置日志
        setup_logging(self.config.get('logging', {}))
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.camera_manager = None
        self.video_processor = None
        self.frame_buffer = None
        self.cattle_detector = None
        self.fused_identifier = None
        self.database = None
        
        # 系统状态
        self.running = False
        self.stats = {
            'total_frames_processed': 0,
            'total_cattle_detected': 0,
            'total_identifications': 0,
            'start_time': None,
            'uptime': 0.0
        }
        
        self.logger.info("BovineInsight系统初始化开始")
        self._initialize_components()
        self.logger.info("BovineInsight系统初始化完成")
    
    def _initialize_components(self):
        """初始化系统组件"""
        try:
            # 初始化数据库
            self._initialize_database()
            
            # 初始化摄像头管理器
            self._initialize_camera_manager()
            
            # 初始化视频处理器
            self._initialize_video_processor()
            
            # 初始化帧缓冲器
            self._initialize_frame_buffer()
            
            # 初始化检测器
            self._initialize_detector()
            
            # 初始化识别器
            self._initialize_identifier()
            
        except Exception as e:
            self.logger.error(f"组件初始化失败: {e}")
            raise
    
    def _initialize_database(self):
        """初始化数据库"""
        db_config = self.config.get('database', {})
        db_path = db_config.get('path', 'data/cattle_database.db')
        
        # 确保数据库目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.database = CattleDatabase(db_path)
        self.logger.info(f"数据库初始化完成: {db_path}")
    
    def _initialize_camera_manager(self):
        """初始化摄像头管理器"""
        self.camera_manager = CameraManager()
        
        # 从配置文件添加摄像头
        cameras_config = self.config.get('cameras', {})
        
        for camera_name, camera_config in cameras_config.items():
            config = CameraConfig(
                camera_id=camera_config.get('id', 0),
                camera_type=CameraType(camera_config.get('type', 'auxiliary')),
                name=camera_name,
                resolution=tuple(camera_config.get('resolution', [1920, 1080])),
                fps=camera_config.get('fps', 30)
            )
            
            success = self.camera_manager.add_camera(config)
            if success:
                self.logger.info(f"摄像头 {camera_name} 添加成功")
            else:
                self.logger.warning(f"摄像头 {camera_name} 添加失败")
        
        # 如果没有配置摄像头，使用默认配置
        if not cameras_config:
            self.logger.info("使用默认摄像头配置")
            for name, config in DEFAULT_CONFIGS.items():
                self.camera_manager.add_camera(config)
    
    def _initialize_video_processor(self):
        """初始化视频处理器"""
        from src.data_processing.video_processor import ProcessingConfig, PROCESSING_CONFIGS
        
        processing_config_name = self.config.get('video_processing', {}).get('mode', 'balanced')
        processing_config = PROCESSING_CONFIGS.get(processing_config_name)
        
        self.video_processor = VideoProcessor(processing_config)
        self.logger.info(f"视频处理器初始化完成，模式: {processing_config_name}")
    
    def _initialize_frame_buffer(self):
        """初始化帧缓冲器"""
        buffer_config = self.config.get('frame_buffer', {})
        
        self.frame_buffer = FrameBuffer(
            max_buffer_size=buffer_config.get('max_size', 30),
            sync_tolerance=buffer_config.get('sync_tolerance', 0.1)
        )
        self.logger.info("帧缓冲器初始化完成")
    
    def _initialize_detector(self):
        """初始化检测器"""
        detection_config = self.config.get('detection', {})
        
        # 初始化模型管理器
        model_manager = ModelManager(detection_config.get('models_dir', 'models'))
        
        # 下载默认模型
        model_key = detection_config.get('model', 'yolov8n')
        if not model_manager.get_model_path(model_key):
            self.logger.info(f"下载模型: {model_key}")
            model_manager.download_model(model_key)
        
        model_path = model_manager.get_model_path(model_key)
        
        self.cattle_detector = CattleDetector(
            model_path=model_path,
            confidence_threshold=detection_config.get('confidence_threshold', 0.5),
            iou_threshold=detection_config.get('iou_threshold', 0.5)
        )
        self.logger.info("牛只检测器初始化完成")
    
    def _initialize_identifier(self):
        """初始化识别器"""
        identification_config = self.config.get('identification', {})
        
        # 初始化耳标识别器
        ear_tag_config = identification_config.get('ear_tag', {})
        ear_tag_reader = EarTagReader(
            use_tesseract=ear_tag_config.get('use_tesseract', True),
            use_easyocr=ear_tag_config.get('use_easyocr', True),
            min_confidence=ear_tag_config.get('min_confidence', 0.5)
        )
        
        # 初始化花色识别器
        coat_pattern_config = identification_config.get('coat_pattern', {})
        coat_pattern_reid = CoatPatternReID(
            extractor_type=coat_pattern_config.get('extractor_type', 'resnet'),
            similarity_threshold=coat_pattern_config.get('similarity_threshold', 0.7)
        )
        
        # 初始化融合识别器
        from src.identification.fused_identifier import FusionConfig, FusionStrategy
        fusion_config = FusionConfig(
            strategy=FusionStrategy(identification_config.get('fusion_strategy', 'ear_tag_priority')),
            min_ear_tag_confidence=identification_config.get('min_ear_tag_confidence', 0.6),
            min_coat_pattern_confidence=identification_config.get('min_coat_pattern_confidence', 0.7)
        )
        
        self.fused_identifier = FusedIdentifier(
            ear_tag_reader=ear_tag_reader,
            coat_pattern_reid=coat_pattern_reid,
            config=fusion_config
        )
        self.logger.info("融合识别器初始化完成")
    
    def start(self):
        """启动系统"""
        if self.running:
            self.logger.warning("系统已在运行")
            return
        
        self.logger.info("启动BovineInsight系统")
        self.running = True
        self.stats['start_time'] = time.time()
        
        # 启动摄像头监控
        self.camera_manager.start_monitoring()
        
        try:
            self._main_loop()
        except KeyboardInterrupt:
            self.logger.info("接收到中断信号，正在停止系统")
        except Exception as e:
            self.logger.error(f"系统运行异常: {e}")
        finally:
            self.stop()
    
    def _main_loop(self):
        """主循环"""
        self.logger.info("进入主处理循环")
        
        while self.running:
            try:
                # 读取所有摄像头的帧
                frames = self.camera_manager.read_all_frames()
                
                if not frames:
                    time.sleep(0.1)
                    continue
                
                # 添加帧到缓冲区
                for camera_name, frame in frames.items():
                    self.frame_buffer.add_frame(camera_name, frame)
                
                # 获取同步帧
                sync_frames = self.frame_buffer.get_synchronized_frames()
                
                if sync_frames:
                    self._process_synchronized_frames(sync_frames)
                
                # 清理过期帧
                self.frame_buffer.remove_old_frames()
                
                # 更新统计信息
                self.stats['total_frames_processed'] += len(frames)
                self.stats['uptime'] = time.time() - self.stats['start_time']
                
                # 短暂休眠以避免过度占用CPU
                time.sleep(0.01)
                
            except Exception as e:
                self.logger.error(f"主循环处理异常: {e}")
                time.sleep(1)
    
    def _process_synchronized_frames(self, sync_frames: Dict[str, any]):
        """处理同步帧"""
        try:
            # 预处理帧
            processed_frames = self.video_processor.process_frames(sync_frames)
            
            # 获取主要摄像头的帧进行检测
            main_frame = None
            ear_tag_frame = None
            
            for camera_name, frame in processed_frames.items():
                if 'body_condition' in camera_name.lower():
                    main_frame = frame
                elif 'ear_tag' in camera_name.lower():
                    ear_tag_frame = frame
            
            if main_frame is None:
                # 使用第一个可用帧
                main_frame = next(iter(processed_frames.values()))
            
            # 检测牛只
            detections = self.cattle_detector.detect(main_frame)
            
            if detections:
                self.stats['total_cattle_detected'] += len(detections)
                
                # 处理每个检测到的牛只
                for detection in detections:
                    self._process_cattle_detection(detection, main_frame, ear_tag_frame)
            
        except Exception as e:
            self.logger.error(f"同步帧处理异常: {e}")
    
    def _process_cattle_detection(self, detection, main_frame, ear_tag_frame):
        """处理单个牛只检测"""
        try:
            # 裁剪牛只区域
            bbox = detection.bbox
            x1, y1, x2, y2 = map(int, bbox.to_xyxy())
            cattle_image = main_frame[y1:y2, x1:x2]
            
            if cattle_image.size == 0:
                return
            
            # 获取候选牛只档案
            candidate_profiles = self.database.get_all_cattle_profiles()
            
            # 身份识别
            identification_result = self.fused_identifier.identify_cattle(
                cattle_image=cattle_image,
                ear_tag_region=ear_tag_frame,
                candidate_profiles=candidate_profiles
            )
            
            if identification_result.cattle_id:
                self.stats['total_identifications'] += 1
                
                # 保存识别结果到数据库
                self.database.add_identification_record(identification_result)
                
                self.logger.info(
                    f"识别成功: ID={identification_result.cattle_id}, "
                    f"方法={identification_result.method.value}, "
                    f"置信度={identification_result.confidence:.2f}"
                )
            
        except Exception as e:
            self.logger.error(f"牛只检测处理异常: {e}")
    
    def stop(self):
        """停止系统"""
        if not self.running:
            return
        
        self.logger.info("停止BovineInsight系统")
        self.running = False
        
        # 停止摄像头
        if self.camera_manager:
            self.camera_manager.disconnect_all()
        
        # 关闭数据库
        if self.database:
            self.database.close()
        
        self.logger.info("系统已停止")
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        status = {
            'running': self.running,
            'stats': self.stats.copy(),
            'components': {}
        }
        
        if self.camera_manager:
            status['components']['cameras'] = self.camera_manager.get_status()
        
        if self.video_processor:
            status['components']['video_processor'] = self.video_processor.get_stats()
        
        if self.frame_buffer:
            status['components']['frame_buffer'] = self.frame_buffer.get_buffer_status()
        
        if self.cattle_detector:
            status['components']['cattle_detector'] = self.cattle_detector.get_stats()
        
        if self.fused_identifier:
            status['components']['fused_identifier'] = self.fused_identifier.get_stats()
        
        return status
    
    def add_camera(self, camera_config: CameraConfig) -> bool:
        """添加摄像头"""
        if self.camera_manager:
            return self.camera_manager.add_camera(camera_config)
        return False
    
    def remove_camera(self, camera_name: str) -> bool:
        """移除摄像头"""
        if self.camera_manager:
            return self.camera_manager.remove_camera(camera_name)
        return False

def signal_handler(signum, frame):
    """信号处理器"""
    global system
    if system:
        system.stop()
    sys.exit(0)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='BovineInsight: 多摄像头牛只身份识别与体况评分系统')
    parser.add_argument('--config', '-c', type=str, help='配置文件路径')
    parser.add_argument('--log-level', type=str, default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='日志级别')
    parser.add_argument('--daemon', '-d', action='store_true', help='后台运行')
    
    args = parser.parse_args()
    
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 初始化系统
        global system
        system = BovineInsightSystem(args.config)
        
        # 启动系统
        system.start()
        
    except Exception as e:
        logging.error(f"系统启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()