#!/usr/bin/env python3
"""
BovineInsight API服务器
为NEXUS前端提供牛识别系统的API接口
"""

import os
import sys
import json
import time
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import cv2
import numpy as np

# 导入BovineInsight核心模块
try:
    # 先尝试导入基础模块
    from src.utils.logger import setup_logger
    # 暂时跳过有问题的模块，使用模拟模式
    BOVINE_MODULES_AVAILABLE = False
    print("📝 使用模拟数据模式运行（跳过核心模块导入）")
except ImportError as e:
    print(f"⚠️ BovineInsight模块导入失败: {e}")
    BOVINE_MODULES_AVAILABLE = False

# 设置日志
try:
    logger = setup_logger("bovine_api") if BOVINE_MODULES_AVAILABLE else logging.getLogger("bovine_api")
except:
    logger = logging.getLogger("bovine_api")
    logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量
cattle_detector = None
fused_identifier = None
cattle_database = None

@dataclass
class CattleDetectionResult:
    """牛只检测结果"""
    cattle_id: str
    confidence: float
    bbox: List[float]  # [x, y, width, height]
    ear_tag: Optional[str] = None
    bcs_score: Optional[float] = None
    timestamp: str = ""
    camera_id: str = "camera_01"

@dataclass
class SystemStatus:
    """系统状态"""
    online: bool
    fps: float
    active_cameras: int
    total_cattle: int
    last_update: str

@dataclass
class CattleProfile:
    """牛只档案"""
    cattle_id: str
    name: str
    ear_tag: str
    current_bcs: float
    health_status: str
    last_seen: str
    photo_url: str
    bcs_history: List[Dict[str, Any]]
    identification_history: List[Dict[str, Any]]

# 模拟数据生成器
class MockDataGenerator:
    """模拟数据生成器"""
    
    def __init__(self):
        self.cattle_ids = [f"COW-{i:04d}" for i in range(1, 51)]  # 50头牛
        self.camera_ids = ["camera_01", "camera_02", "camera_03", "camera_04"]
        self.last_detection_time = {}
        
    def generate_detection_result(self) -> CattleDetectionResult:
        """生成模拟检测结果"""
        cattle_id = np.random.choice(self.cattle_ids)
        
        return CattleDetectionResult(
            cattle_id=cattle_id,
            confidence=np.random.uniform(0.85, 0.99),
            bbox=[
                np.random.uniform(100, 300),  # x
                np.random.uniform(50, 200),   # y
                np.random.uniform(150, 250),  # width
                np.random.uniform(200, 300)   # height
            ],
            ear_tag=f"TAG-{cattle_id.split('-')[1]}",
            bcs_score=np.random.uniform(2.0, 4.5),
            timestamp=datetime.now().isoformat(),
            camera_id=np.random.choice(self.camera_ids)
        )
    
    def generate_cattle_profile(self, cattle_id: str) -> CattleProfile:
        """生成牛只档案"""
        # 生成BCS历史数据
        bcs_history = []
        base_date = datetime.now() - timedelta(days=90)
        base_bcs = np.random.uniform(2.5, 4.0)
        
        for i in range(30):  # 30个数据点
            date = base_date + timedelta(days=i * 3)
            bcs = base_bcs + np.random.normal(0, 0.2)
            bcs = max(1.0, min(5.0, bcs))  # 限制在1-5范围内
            
            bcs_history.append({
                "date": date.strftime("%Y-%m-%d"),
                "score": round(bcs, 1),
                "method": "auto_detection"
            })
        
        # 生成识别历史
        identification_history = []
        for i in range(10):  # 最近10次识别记录
            date = datetime.now() - timedelta(days=i * 2)
            identification_history.append({
                "timestamp": date.isoformat(),
                "method": np.random.choice(["ear_tag", "coat_pattern", "fusion"]),
                "confidence": np.random.uniform(0.8, 0.99),
                "camera_id": np.random.choice(self.camera_ids),
                "photo_url": f"/api/photos/{cattle_id}_{i}.jpg"
            })
        
        return CattleProfile(
            cattle_id=cattle_id,
            name=f"牛只-{cattle_id.split('-')[1]}",
            ear_tag=f"TAG-{cattle_id.split('-')[1]}",
            current_bcs=round(bcs_history[-1]["score"], 1),
            health_status=self._get_health_status(bcs_history[-1]["score"]),
            last_seen=datetime.now().isoformat(),
            photo_url=f"/api/photos/{cattle_id}_profile.jpg",
            bcs_history=bcs_history,
            identification_history=identification_history
        )
    
    def _get_health_status(self, bcs_score: float) -> str:
        """根据BCS评分获取健康状态"""
        if bcs_score < 2.0:
            return "过瘦"
        elif bcs_score < 2.5:
            return "偏瘦"
        elif bcs_score <= 3.5:
            return "健康"
        elif bcs_score <= 4.0:
            return "良好"
        else:
            return "过肥"

# 初始化模拟数据生成器
mock_generator = MockDataGenerator()

# API路由定义

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    try:
        status = SystemStatus(
            online=True,
            fps=np.random.uniform(25, 30),
            active_cameras=len(mock_generator.camera_ids),
            total_cattle=len(mock_generator.cattle_ids),
            last_update=datetime.now().isoformat()
        )
        
        return jsonify({
            "success": True,
            "data": asdict(status)
        })
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/live-detection', methods=['GET'])
def get_live_detection():
    """获取实时检测结果"""
    try:
        # 生成1-3个检测结果
        num_detections = np.random.randint(1, 4)
        detections = []
        
        for _ in range(num_detections):
            detection = mock_generator.generate_detection_result()
            detections.append(asdict(detection))
        
        return jsonify({
            "success": True,
            "data": {
                "detections": detections,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"获取实时检测结果失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/cattle/<cattle_id>', methods=['GET'])
def get_cattle_profile(cattle_id: str):
    """获取牛只档案"""
    try:
        if cattle_id not in mock_generator.cattle_ids:
            return jsonify({"success": False, "error": "牛只不存在"}), 404
        
        profile = mock_generator.generate_cattle_profile(cattle_id)
        
        return jsonify({
            "success": True,
            "data": asdict(profile)
        })
    except Exception as e:
        logger.error(f"获取牛只档案失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/cattle', methods=['GET'])
def get_cattle_list():
    """获取牛只列表"""
    try:
        cattle_list = []
        for cattle_id in mock_generator.cattle_ids[:20]:  # 返回前20头牛
            profile = mock_generator.generate_cattle_profile(cattle_id)
            cattle_list.append({
                "cattle_id": profile.cattle_id,
                "name": profile.name,
                "ear_tag": profile.ear_tag,
                "current_bcs": profile.current_bcs,
                "health_status": profile.health_status,
                "last_seen": profile.last_seen
            })
        
        return jsonify({
            "success": True,
            "data": cattle_list
        })
    except Exception as e:
        logger.error(f"获取牛只列表失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/herd-health', methods=['GET'])
def get_herd_health():
    """获取牛群健康统计"""
    try:
        # 生成BCS分布数据
        bcs_distribution = {
            "1.0-1.5": np.random.randint(0, 3),
            "1.5-2.5": np.random.randint(2, 8),
            "2.5-3.5": np.random.randint(15, 25),
            "3.5-4.5": np.random.randint(10, 20),
            "4.5-5.0": np.random.randint(0, 5)
        }
        
        # 生成预警列表
        alerts = []
        alert_types = ["red", "orange", "yellow"]
        alert_messages = [
            "BCS评分连续下降",
            "超过3天未出现",
            "体况评分异常",
            "需要营养补充",
            "建议兽医检查"
        ]
        
        for i in range(np.random.randint(3, 8)):
            cattle_id = np.random.choice(mock_generator.cattle_ids)
            alerts.append({
                "cattle_id": cattle_id,
                "alert_type": np.random.choice(alert_types),
                "message": np.random.choice(alert_messages),
                "timestamp": (datetime.now() - timedelta(hours=np.random.randint(1, 24))).isoformat()
            })
        
        # 计算统计数据
        total_cattle = len(mock_generator.cattle_ids)
        avg_bcs = np.random.uniform(3.0, 3.8)
        healthy_count = sum([count for range_key, count in bcs_distribution.items() 
                           if "2.5-3.5" in range_key or "3.5-4.5" in range_key])
        
        return jsonify({
            "success": True,
            "data": {
                "bcs_distribution": bcs_distribution,
                "alerts": alerts,
                "statistics": {
                    "total_cattle": total_cattle,
                    "average_bcs": round(avg_bcs, 1),
                    "healthy_percentage": round((healthy_count / total_cattle) * 100, 1),
                    "alert_count": len(alerts)
                }
            }
        })
    except Exception as e:
        logger.error(f"获取牛群健康统计失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/cameras', methods=['GET'])
def get_camera_status():
    """获取摄像头状态"""
    try:
        cameras = []
        for camera_id in mock_generator.camera_ids:
            cameras.append({
                "camera_id": camera_id,
                "name": f"摄像头-{camera_id.split('_')[1]}",
                "status": "online" if np.random.random() > 0.1 else "offline",
                "fps": np.random.uniform(25, 30),
                "resolution": "1920x1080",
                "last_detection": (datetime.now() - timedelta(seconds=np.random.randint(1, 300))).isoformat()
            })
        
        return jsonify({
            "success": True,
            "data": cameras
        })
    except Exception as e:
        logger.error(f"获取摄像头状态失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/video-stream/<camera_id>', methods=['GET'])
def get_video_stream(camera_id: str):
    """获取视频流（模拟）"""
    def generate_frame():
        """生成模拟视频帧"""
        while True:
            # 创建一个黑色图像作为模拟视频帧
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # 添加一些模拟内容
            cv2.putText(frame, f"Camera: {camera_id}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"Time: {datetime.now().strftime('%H:%M:%S')}", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 模拟检测框
            if np.random.random() > 0.3:  # 70%概率显示检测框
                x, y, w, h = 200, 150, 200, 180
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "COW-0001", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 编码为JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.1)  # 10 FPS
    
    return Response(generate_frame(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "BovineInsight API",
        "timestamp": datetime.now().isoformat(),
        "modules_available": BOVINE_MODULES_AVAILABLE
    })

def initialize_system():
    """初始化系统"""
    global cattle_detector, fused_identifier, cattle_database
    
    logger.info("🚀 初始化BovineInsight API服务器...")
    
    if BOVINE_MODULES_AVAILABLE:
        try:
            # 初始化核心模块
            cattle_detector = CattleDetector()
            fused_identifier = FusedIdentifier()
            cattle_database = CattleDatabase()
            logger.info("✅ BovineInsight核心模块初始化成功")
        except Exception as e:
            logger.warning(f"⚠️ 核心模块初始化失败，使用模拟模式: {e}")
    else:
        logger.info("📝 使用模拟数据模式运行")

if __name__ == '__main__':
    initialize_system()
    
    # 启动API服务器
    port = int(os.environ.get('BOVINE_API_PORT', 5001))
    host = os.environ.get('BOVINE_API_HOST', '0.0.0.0')
    
    logger.info(f"🌐 BovineInsight API服务器启动在 http://{host}:{port}")
    
    app.run(
        host=host,
        port=port,
        debug=False,
        threaded=True
    )