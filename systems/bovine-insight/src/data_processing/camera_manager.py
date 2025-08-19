"""
摄像头管理器
Camera Manager

管理多个摄像头的连接、配置和状态监控
"""

import cv2
import threading
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class CameraType(Enum):
    """摄像头类型枚举"""
    EAR_TAG = "ear_tag"           # 耳标识别摄像头
    BODY_CONDITION = "body_condition"  # 体况评分摄像头
    AUXILIARY = "auxiliary"       # 辅助摄像头

@dataclass
class CameraConfig:
    """摄像头配置"""
    camera_id: int
    camera_type: CameraType
    name: str
    resolution: Tuple[int, int] = (1920, 1080)
    fps: int = 30
    auto_focus: bool = True
    exposure: int = -1  # -1为自动曝光
    brightness: int = 50
    contrast: int = 50
    saturation: int = 50

class CameraStatus(Enum):
    """摄像头状态"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class Camera:
    """单个摄像头封装类"""
    
    def __init__(self, config: CameraConfig):
        self.config = config
        self.cap: Optional[cv2.VideoCapture] = None
        self.status = CameraStatus.DISCONNECTED
        self.last_frame = None
        self.last_frame_time = 0
        self.frame_count = 0
        self.error_count = 0
        self.lock = threading.Lock()
        
        # 性能统计
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.actual_fps = 0
        
    def connect(self) -> bool:
        """连接摄像头"""
        try:
            self.status = CameraStatus.CONNECTING
            logging.info(f"正在连接摄像头 {self.config.name} (ID: {self.config.camera_id})")
            
            # 创建VideoCapture对象
            self.cap = cv2.VideoCapture(self.config.camera_id)
            
            if not self.cap.isOpened():
                raise Exception(f"无法打开摄像头 {self.config.camera_id}")
            
            # 设置摄像头参数
            self._configure_camera()
            
            # 测试读取一帧
            ret, frame = self.cap.read()
            if not ret:
                raise Exception("无法读取摄像头数据")
            
            self.status = CameraStatus.CONNECTED
            self.error_count = 0
            logging.info(f"摄像头 {self.config.name} 连接成功")
            return True
            
        except Exception as e:
            self.status = CameraStatus.ERROR
            self.error_count += 1
            logging.error(f"摄像头 {self.config.name} 连接失败: {e}")
            if self.cap:
                self.cap.release()
                self.cap = None
            return False
    
    def _configure_camera(self):
        """配置摄像头参数"""
        if not self.cap:
            return
        
        # 设置分辨率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.resolution[1])
        
        # 设置帧率
        self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)
        
        # 设置其他参数
        if self.config.exposure != -1:
            self.cap.set(cv2.CAP_PROP_EXPOSURE, self.config.exposure)
        
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.config.brightness / 100.0)
        self.cap.set(cv2.CAP_PROP_CONTRAST, self.config.contrast / 100.0)
        self.cap.set(cv2.CAP_PROP_SATURATION, self.config.saturation / 100.0)
        
        if self.config.auto_focus:
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    
    def read_frame(self) -> Tuple[bool, Optional[Any]]:
        """读取一帧图像"""
        if not self.cap or self.status != CameraStatus.CONNECTED:
            return False, None
        
        try:
            with self.lock:
                ret, frame = self.cap.read()
                
                if ret:
                    self.last_frame = frame.copy()
                    self.last_frame_time = time.time()
                    self.frame_count += 1
                    self._update_fps()
                    return True, frame
                else:
                    self.error_count += 1
                    if self.error_count > 10:  # 连续错误超过10次
                        self.status = CameraStatus.ERROR
                        logging.warning(f"摄像头 {self.config.name} 读取失败次数过多")
                    return False, None
                    
        except Exception as e:
            self.error_count += 1
            logging.error(f"摄像头 {self.config.name} 读取异常: {e}")
            return False, None
    
    def _update_fps(self):
        """更新FPS统计"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:  # 每秒更新一次
            self.actual_fps = self.fps_counter / (current_time - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def disconnect(self):
        """断开摄像头连接"""
        if self.cap:
            self.cap.release()
            self.cap = None
        self.status = CameraStatus.DISCONNECTED
        logging.info(f"摄像头 {self.config.name} 已断开连接")
    
    def get_info(self) -> Dict:
        """获取摄像头信息"""
        return {
            'name': self.config.name,
            'type': self.config.camera_type.value,
            'status': self.status.value,
            'frame_count': self.frame_count,
            'error_count': self.error_count,
            'actual_fps': round(self.actual_fps, 2),
            'last_frame_time': self.last_frame_time
        }

class CameraManager:
    """摄像头管理器"""
    
    def __init__(self):
        self.cameras: Dict[str, Camera] = {}
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        
    def add_camera(self, config: CameraConfig) -> bool:
        """添加摄像头"""
        if config.name in self.cameras:
            logging.warning(f"摄像头 {config.name} 已存在")
            return False
        
        camera = Camera(config)
        if camera.connect():
            self.cameras[config.name] = camera
            logging.info(f"成功添加摄像头 {config.name}")
            return True
        else:
            logging.error(f"添加摄像头 {config.name} 失败")
            return False
    
    def remove_camera(self, name: str) -> bool:
        """移除摄像头"""
        if name not in self.cameras:
            logging.warning(f"摄像头 {name} 不存在")
            return False
        
        self.cameras[name].disconnect()
        del self.cameras[name]
        logging.info(f"已移除摄像头 {name}")
        return True
    
    def get_camera(self, name: str) -> Optional[Camera]:
        """获取指定摄像头"""
        return self.cameras.get(name)
    
    def get_cameras_by_type(self, camera_type: CameraType) -> List[Camera]:
        """根据类型获取摄像头列表"""
        return [cam for cam in self.cameras.values() 
                if cam.config.camera_type == camera_type]
    
    def read_all_frames(self) -> Dict[str, Any]:
        """读取所有摄像头的当前帧"""
        frames = {}
        for name, camera in self.cameras.items():
            ret, frame = camera.read_frame()
            if ret:
                frames[name] = frame
        return frames
    
    def start_monitoring(self):
        """启动摄像头状态监控"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_cameras)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logging.info("摄像头监控已启动")
    
    def stop_monitoring(self):
        """停止摄像头状态监控"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logging.info("摄像头监控已停止")
    
    def _monitor_cameras(self):
        """监控摄像头状态（后台线程）"""
        while self.running:
            for name, camera in self.cameras.items():
                if camera.status == CameraStatus.ERROR:
                    logging.warning(f"尝试重连摄像头 {name}")
                    camera.connect()
                elif camera.status == CameraStatus.CONNECTED:
                    # 检查是否长时间没有新帧
                    if time.time() - camera.last_frame_time > 5.0:
                        logging.warning(f"摄像头 {name} 长时间无新帧，尝试重连")
                        camera.disconnect()
                        camera.connect()
            
            time.sleep(2)  # 每2秒检查一次
    
    def get_status(self) -> Dict:
        """获取所有摄像头状态"""
        status = {
            'total_cameras': len(self.cameras),
            'connected_cameras': sum(1 for cam in self.cameras.values() 
                                   if cam.status == CameraStatus.CONNECTED),
            'cameras': {}
        }
        
        for name, camera in self.cameras.items():
            status['cameras'][name] = camera.get_info()
        
        return status
    
    def disconnect_all(self):
        """断开所有摄像头连接"""
        for camera in self.cameras.values():
            camera.disconnect()
        self.stop_monitoring()
        logging.info("所有摄像头已断开连接")
    
    def __del__(self):
        """析构函数"""
        self.disconnect_all()

# 预定义的摄像头配置
DEFAULT_CONFIGS = {
    'ear_tag_camera': CameraConfig(
        camera_id=0,
        camera_type=CameraType.EAR_TAG,
        name='ear_tag_camera',
        resolution=(1920, 1080),
        fps=30
    ),
    'body_condition_camera': CameraConfig(
        camera_id=1,
        camera_type=CameraType.BODY_CONDITION,
        name='body_condition_camera',
        resolution=(1920, 1080),
        fps=30
    )
}