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

# 导入数据库和智能决策模块
try:
    from src.database.models import init_database
    from src.database.dao import (
        CattleDAO, BCSHistoryDAO, DetectionDAO, AlertDAO, 
        log_info, log_warning, log_error
    )
    from src.decision.decision_engine import get_decision_engine
    from src.ml.ml_engine import get_ml_engine
    DATABASE_AVAILABLE = True
    print("✅ 数据库和智能决策模块加载成功")
except ImportError as e:
    print(f"⚠️ 数据库模块导入失败: {e}")
    DATABASE_AVAILABLE = False

# 导入BovineInsight核心模块
try:
    from src.utils.logger import setup_logger
    BOVINE_MODULES_AVAILABLE = False  # 暂时保持模拟模式
    print("📝 使用智能模拟数据模式运行")
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
decision_engine = None
ml_engine = None
system_initialized = False

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
        if DATABASE_AVAILABLE:
            # 从数据库获取最近的检测记录
            recent_detections = DetectionDAO.get_recent_detections(hours=1, limit=10)
            
            detections = []
            for detection in recent_detections:
                detections.append({
                    "cattle_id": detection.cattle_id,
                    "confidence": detection.confidence,
                    "bbox": [detection.bbox_x, detection.bbox_y, detection.bbox_width, detection.bbox_height],
                    "bcs_score": detection.bcs_score,
                    "camera_id": detection.camera_id,
                    "timestamp": detection.detection_time.isoformat()
                })
            
            # 如果没有最近的检测记录，生成一些模拟数据
            if not detections:
                # 随机选择一些牛只进行模拟检测
                all_cattle = CattleDAO.get_all_cattle(limit=5)
                for cattle in all_cattle:
                    if np.random.random() < 0.3:  # 30%概率被检测到
                        # 保存模拟检测记录到数据库
                        detection_data = {
                            'cattle_id': cattle.cattle_id,
                            'camera_id': np.random.choice(['camera_01', 'camera_02', 'camera_03', 'camera_04']),
                            'confidence': np.random.uniform(0.85, 0.99),
                            'bcs_score': cattle.current_bcs + np.random.normal(0, 0.1),
                            'bbox_x': np.random.uniform(100, 300),
                            'bbox_y': np.random.uniform(50, 200),
                            'bbox_width': np.random.uniform(150, 250),
                            'bbox_height': np.random.uniform(100, 180)
                        }
                        
                        saved_detection = DetectionDAO.save_detection(detection_data)
                        
                        detections.append({
                            "cattle_id": saved_detection.cattle_id,
                            "confidence": saved_detection.confidence,
                            "bbox": [saved_detection.bbox_x, saved_detection.bbox_y, 
                                   saved_detection.bbox_width, saved_detection.bbox_height],
                            "bcs_score": saved_detection.bcs_score,
                            "camera_id": saved_detection.camera_id,
                            "timestamp": saved_detection.detection_time.isoformat()
                        })
        else:
            # 回退到模拟模式
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
        if DATABASE_AVAILABLE:
            # 从数据库获取牛只信息
            cattle = CattleDAO.get_cattle_by_id(cattle_id)
            if not cattle:
                return jsonify({"success": False, "error": "牛只不存在"}), 404
            
            # 获取BCS历史记录
            bcs_history = BCSHistoryDAO.get_cattle_bcs_history(cattle_id, days=30)
            bcs_data = []
            for record in bcs_history:
                bcs_data.append({
                    "date": record.measurement_date.strftime("%Y-%m-%d"),
                    "bcs": record.bcs_score,
                    "confidence": record.confidence
                })
            
            # 获取识别历史
            detections = DetectionDAO.get_cattle_detections(cattle_id, days=7)
            identification_history = []
            for detection in detections:
                identification_history.append({
                    "timestamp": detection.detection_time.isoformat(),
                    "camera_id": detection.camera_id,
                    "confidence": detection.confidence,
                    "method": detection.identification_method
                })
            
            profile_data = {
                "cattle_id": cattle.cattle_id,
                "name": cattle.name,
                "ear_tag": cattle.ear_tag,
                "current_bcs": cattle.current_bcs,
                "health_status": cattle.health_status,
                "last_seen": cattle.last_seen.isoformat(),
                "photo_url": f"/static/cattle/{cattle.cattle_id}.jpg",  # 模拟照片URL
                "bcs_history": bcs_data,
                "identification_history": identification_history
            }
        else:
            # 回退到模拟模式
            if cattle_id not in mock_generator.cattle_ids:
                return jsonify({"success": False, "error": "牛只不存在"}), 404
            
            profile = mock_generator.generate_cattle_profile(cattle_id)
            profile_data = asdict(profile)
        
        return jsonify({
            "success": True,
            "data": profile_data
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
    global cattle_detector, fused_identifier, cattle_database, decision_engine, ml_engine, system_initialized, DATABASE_AVAILABLE
    
    logger.info("🚀 初始化BovineInsight API服务器...")
    
    # 初始化数据库
    if DATABASE_AVAILABLE:
        try:
            logger.info("📊 初始化数据库...")
            init_database()
            
            # 初始化智能决策引擎
            decision_engine = get_decision_engine()
            ml_engine = get_ml_engine()
            
            # 初始化基础牛只数据（如果数据库为空）
            initialize_cattle_data()
            
            logger.info("✅ 数据库和智能决策引擎初始化成功")
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
            DATABASE_AVAILABLE = False
    
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
        logger.info("📝 使用智能模拟数据模式运行")
    
    system_initialized = True
    logger.info("🎉 系统初始化完成！")

def initialize_cattle_data():
    """初始化基础牛只数据"""
    try:
        # 检查是否已有牛只数据
        existing_cattle = CattleDAO.get_all_cattle(limit=1)
        if existing_cattle:
            logger.info(f"📋 发现现有牛只数据: {len(CattleDAO.get_all_cattle())} 头牛")
            return
        
        # 创建示例牛只数据
        logger.info("🐄 创建示例牛只数据...")
        sample_cattle = [
            {
                'cattle_id': 'COW-0001',
                'name': '贝拉',
                'ear_tag': 'ET-001',
                'breed': 'Holstein',
                'current_bcs': 3.2,
                'health_status': '健康'
            },
            {
                'cattle_id': 'COW-0002', 
                'name': '露西',
                'ear_tag': 'ET-002',
                'breed': 'Holstein',
                'current_bcs': 2.8,
                'health_status': '健康'
            },
            {
                'cattle_id': 'COW-0003',
                'name': '黛西',
                'ear_tag': 'ET-003', 
                'breed': 'Holstein',
                'current_bcs': 3.5,
                'health_status': '良好'
            },
            {
                'cattle_id': 'COW-0004',
                'name': '莫莉',
                'ear_tag': 'ET-004',
                'breed': 'Holstein', 
                'current_bcs': 2.3,
                'health_status': '偏瘦'
            },
            {
                'cattle_id': 'COW-0005',
                'name': '安妮',
                'ear_tag': 'ET-005',
                'breed': 'Holstein',
                'current_bcs': 4.1,
                'health_status': '过肥'
            }
        ]
        
        for cattle_data in sample_cattle:
            CattleDAO.create_cattle(cattle_data)
            
        logger.info(f"✅ 创建了 {len(sample_cattle)} 头示例牛只")
        
    except Exception as e:
        logger.error(f"❌ 初始化牛只数据失败: {e}")

# ==================== 新增智能决策和机器学习API ====================

@app.route('/api/health-analysis', methods=['GET'])
def get_health_analysis():
    """获取牛群健康分析"""
    try:
        if DATABASE_AVAILABLE and decision_engine:
            # 使用智能决策引擎分析牛群健康
            analysis_result = decision_engine.analyze_herd_health()
            
            return jsonify({
                "success": True,
                "data": analysis_result
            })
        else:
            # 回退到模拟模式
            return jsonify({
                "success": True,
                "data": {
                    "total_cattle": 50,
                    "health_summary": {
                        "risk_distribution": {"low": 35, "medium": 12, "high": 3},
                        "trend_distribution": {"improving": 15, "stable": 30, "declining": 5},
                        "bcs_statistics": {"average": 3.2, "median": 3.1, "min": 2.1, "max": 4.3}
                    },
                    "alerts_generated": 5,
                    "recommendations": ["牛群整体健康状况良好，继续保持当前管理水平"]
                }
            })
    except Exception as e:
        logger.error(f"健康分析失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """获取预警信息"""
    try:
        if DATABASE_AVAILABLE:
            # 从数据库获取活跃预警
            active_alerts = AlertDAO.get_active_alerts(limit=20)
            
            alerts_data = []
            for alert in active_alerts:
                alerts_data.append({
                    "id": alert.id,
                    "cattle_id": alert.cattle_id,
                    "alert_type": alert.alert_type,
                    "title": alert.title,
                    "message": alert.message,
                    "level": alert.alert_level,
                    "timestamp": alert.created_at.isoformat()
                })
            
            return jsonify({
                "success": True,
                "data": {"alerts": alerts_data}
            })
        else:
            # 回退到模拟模式
            alerts = []
            alert_types = ["red", "orange", "yellow"]
            alert_messages = [
                "BCS评分持续下降",
                "长时间未出现",
                "健康状况异常",
                "建议兽医检查"
            ]
            
            for i in range(np.random.randint(3, 8)):
                cattle_id = f"COW-{np.random.randint(1, 51):04d}"
                alerts.append({
                    "cattle_id": cattle_id,
                    "alert_type": np.random.choice(alert_types),
                    "message": np.random.choice(alert_messages),
                    "timestamp": (datetime.now() - timedelta(hours=np.random.randint(1, 24))).isoformat()
                })
            
            return jsonify({
                "success": True,
                "data": {"alerts": alerts}
            })
    except Exception as e:
        logger.error(f"获取预警信息失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ml/train', methods=['POST'])
def train_ml_model():
    """训练机器学习模型"""
    try:
        if not DATABASE_AVAILABLE or not ml_engine:
            return jsonify({
                "success": False, 
                "error": "机器学习功能不可用"
            }), 503
        
        # 获取训练参数
        data = request.get_json() or {}
        model_type = data.get('model_type', 'random_forest')
        days_back = data.get('days_back', 90)
        
        # 创建测试数据（如果需要）
        if data.get('create_test_data', False):
            ml_engine.create_test_data(num_records=200)
        
        # 训练模型
        result = ml_engine.train_bcs_model(model_type=model_type, days_back=days_back)
        
        # 清理测试数据
        if data.get('create_test_data', False):
            ml_engine.cleanup_test_data()
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"模型训练失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ml/predict/<cattle_id>', methods=['GET'])
def predict_cattle_bcs(cattle_id: str):
    """预测牛只BCS评分"""
    try:
        if not DATABASE_AVAILABLE or not ml_engine:
            return jsonify({
                "success": False,
                "error": "机器学习功能不可用"
            }), 503
        
        prediction = ml_engine.predict_cattle_bcs(cattle_id)
        
        if prediction:
            return jsonify({
                "success": True,
                "data": prediction
            })
        else:
            return jsonify({
                "success": False,
                "error": "无法预测该牛只的BCS评分"
            }), 404
            
    except Exception as e:
        logger.error(f"BCS预测失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ml/model-info', methods=['GET'])
def get_model_info():
    """获取模型信息"""
    try:
        if not DATABASE_AVAILABLE or not ml_engine:
            return jsonify({
                "success": False,
                "error": "机器学习功能不可用"
            }), 503
        
        model_info = ml_engine.get_model_info()
        
        return jsonify({
            "success": True,
            "data": model_info
        })
        
    except Exception as e:
        logger.error(f"获取模型信息失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    """获取仪表盘数据"""
    try:
        if DATABASE_AVAILABLE:
            try:
                # 获取BCS分布
                all_cattle = CattleDAO.get_all_cattle()
                bcs_scores = [cattle.current_bcs for cattle in all_cattle]
                
                bcs_distribution = {
                    "1.0-1.5": len([s for s in bcs_scores if 1.0 <= s < 1.5]),
                    "1.5-2.5": len([s for s in bcs_scores if 1.5 <= s < 2.5]),
                    "2.5-3.5": len([s for s in bcs_scores if 2.5 <= s < 3.5]),
                    "3.5-4.5": len([s for s in bcs_scores if 3.5 <= s < 4.5]),
                    "4.5-5.0": len([s for s in bcs_scores if 4.5 <= s <= 5.0])
                }
                
                # 获取预警信息
                active_alerts = AlertDAO.get_active_alerts(limit=10)
                alerts = []
                for alert in active_alerts:
                    alerts.append({
                        "cattle_id": alert.cattle_id,
                        "alert_type": alert.alert_type,
                        "title": alert.title,
                        "message": alert.message,
                        "timestamp": alert.created_at.isoformat()
                    })
                
                # 计算统计数据
                total_cattle = len(all_cattle)
                avg_bcs = sum(bcs_scores) / len(bcs_scores) if bcs_scores else 0
                healthy_count = len([s for s in bcs_scores if 2.5 <= s <= 4.0])
                healthy_percentage = (healthy_count / total_cattle * 100) if total_cattle > 0 else 0
                
                return jsonify({
                    "success": True,
                    "data": {
                        "bcs_distribution": bcs_distribution,
                        "alerts": alerts,
                        "statistics": {
                            "total_cattle": total_cattle,
                            "average_bcs": round(avg_bcs, 2),
                            "healthy_percentage": round(healthy_percentage, 1)
                        }
                    }
                })
            except Exception as e:
                logger.error(f"数据库查询失败: {e}")
                # 回退到模拟模式
        else:
            # 回退到模拟模式
            bcs_distribution = {
                "1.0-1.5": np.random.randint(0, 3),
                "1.5-2.5": np.random.randint(3, 8),
                "2.5-3.5": np.random.randint(25, 35),
                "3.5-4.5": np.random.randint(8, 15),
                "4.5-5.0": np.random.randint(0, 3)
            }
            
            alerts = []
            for _ in range(np.random.randint(2, 6)):
                alerts.append({
                    "cattle_id": f"COW-{np.random.randint(1, 51):04d}",
                    "alert_type": np.random.choice(["red", "orange", "yellow"]),
                    "title": np.random.choice(["BCS评分异常", "长时间未出现", "健康状况下降"]),
                    "message": "需要关注",
                    "timestamp": datetime.now().isoformat()
                })
            
            return jsonify({
                "success": True,
                "data": {
                    "bcs_distribution": bcs_distribution,
                    "alerts": alerts,
                    "statistics": {
                        "total_cattle": 50,
                        "average_bcs": 3.2,
                        "healthy_percentage": 85.0
                    }
                }
            })
    except Exception as e:
        logger.error(f"获取仪表盘数据失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/feeding-advice/<cattle_id>', methods=['GET'])
def get_feeding_advice(cattle_id: str):
    """获取饲养建议"""
    try:
        if not DATABASE_AVAILABLE or not decision_engine:
            return jsonify({
                "success": False,
                "error": "智能决策功能不可用"
            }), 503
        
        advice = decision_engine.generate_feeding_advice(cattle_id)
        
        if advice:
            return jsonify({
                "success": True,
                "data": {
                    "cattle_id": advice.cattle_id,
                    "current_bcs": advice.current_bcs,
                    "target_bcs": advice.target_bcs,
                    "feed_adjustment": advice.feed_adjustment,
                    "feed_change_percentage": advice.feed_change_percentage,
                    "recommendations": advice.specific_recommendations
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": "无法生成该牛只的饲养建议"
            }), 404
            
    except Exception as e:
        logger.error(f"生成饲养建议失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

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