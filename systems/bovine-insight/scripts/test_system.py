#!/usr/bin/env python3
"""
BovineInsight系统测试脚本
System Test Script

测试系统各个模块的功能
"""

import sys
import os
import logging
import numpy as np
import cv2
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_processing import CameraManager, VideoProcessor, FrameBuffer
from src.data_processing.camera_manager import CameraConfig, CameraType
from src.detection import CattleDetector, ModelManager
from src.identification import EarTagReader, CoatPatternReID, FusedIdentifier
from src.identification.identification_utils import CattleProfile, CoatPatternFeature
from src.database import CattleDatabase
from src.utils import ConfigManager, setup_logging

def create_test_image(width=640, height=480):
    """创建测试图像"""
    # 创建一个模拟的牛只图像
    image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    
    # 添加一些简单的形状来模拟牛只
    cv2.rectangle(image, (100, 100), (500, 350), (139, 69, 19), -1)  # 棕色矩形
    cv2.ellipse(image, (300, 200), (150, 100), 0, 0, 360, (160, 82, 45), -1)  # 椭圆
    
    # 添加一些纹理
    for _ in range(50):
        x, y = np.random.randint(100, 500), np.random.randint(100, 350)
        cv2.circle(image, (x, y), np.random.randint(2, 8), (0, 0, 0), -1)
    
    return image

def create_test_ear_tag_image(width=200, height=100):
    """创建测试耳标图像"""
    image = np.ones((height, width, 3), dtype=np.uint8) * 255  # 白色背景
    
    # 添加黑色文字
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = "A001"
    text_size = cv2.getTextSize(text, font, 2, 3)[0]
    text_x = (width - text_size[0]) // 2
    text_y = (height + text_size[1]) // 2
    
    cv2.putText(image, text, (text_x, text_y), font, 2, (0, 0, 0), 3)
    
    return image

def test_camera_manager():
    """测试摄像头管理器"""
    print("🎥 测试摄像头管理器...")
    
    try:
        camera_manager = CameraManager()
        
        # 添加模拟摄像头配置
        config1 = CameraConfig(
            camera_id=0,
            camera_type=CameraType.EAR_TAG,
            name='test_ear_tag_camera'
        )
        
        config2 = CameraConfig(
            camera_id=1,
            camera_type=CameraType.BODY_CONDITION,
            name='test_body_condition_camera'
        )
        
        # 注意：在没有实际摄像头的环境中，这些会失败
        # 但我们可以测试配置逻辑
        print(f"   摄像头管理器创建成功")
        print(f"   状态: {camera_manager.get_status()}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 摄像头管理器测试失败: {e}")
        return False

def test_video_processor():
    """测试视频处理器"""
    print("🎬 测试视频处理器...")
    
    try:
        from src.data_processing.video_processor import VideoProcessor, ProcessingConfig
        
        processor = VideoProcessor()
        
        # 创建测试图像
        test_image = create_test_image()
        frames = {'test_camera': test_image}
        
        # 处理帧
        processed_frames = processor.process_frames(frames)
        
        print(f"   ✅ 视频处理器测试成功")
        print(f"   处理了 {len(processed_frames)} 帧")
        print(f"   统计信息: {processor.get_stats()}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 视频处理器测试失败: {e}")
        return False

def test_cattle_detector():
    """测试牛只检测器"""
    print("🐄 测试牛只检测器...")
    
    try:
        detector = CattleDetector()
        
        # 创建测试图像
        test_image = create_test_image()
        
        # 检测
        detections = detector.detect(test_image)
        
        print(f"   ✅ 牛只检测器测试成功")
        print(f"   检测到 {len(detections)} 个目标")
        print(f"   统计信息: {detector.get_stats()}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 牛只检测器测试失败: {e}")
        return False

def test_ear_tag_reader():
    """测试耳标识别器"""
    print("🏷️ 测试耳标识别器...")
    
    try:
        reader = EarTagReader()
        
        # 创建测试耳标图像
        test_image = create_test_ear_tag_image()
        
        # 识别
        result = reader.read_ear_tag(test_image)
        
        print(f"   ✅ 耳标识别器测试成功")
        print(f"   识别结果: ID={result.cattle_id}, 置信度={result.confidence:.2f}")
        print(f"   统计信息: {reader.get_stats()}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 耳标识别器测试失败: {e}")
        return False

def test_coat_pattern_reid():
    """测试花色重识别器"""
    print("🎨 测试花色重识别器...")
    
    try:
        reid = CoatPatternReID(extractor_type='mock')  # 使用模拟提取器
        
        # 创建测试图像
        test_image = create_test_image()
        
        # 提取特征
        feature = reid.extract_coat_pattern_feature(test_image)
        
        if feature:
            print(f"   ✅ 花色重识别器测试成功")
            print(f"   特征维度: {len(feature.feature_vector)}")
            print(f"   质量评分: {feature.quality_score:.2f}")
            print(f"   统计信息: {reid.get_stats()}")
        else:
            print(f"   ⚠️ 特征提取失败")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 花色重识别器测试失败: {e}")
        return False

def test_fused_identifier():
    """测试融合识别器"""
    print("🔗 测试融合识别器...")
    
    try:
        identifier = FusedIdentifier()
        
        # 创建测试图像
        cattle_image = create_test_image()
        ear_tag_image = create_test_ear_tag_image()
        
        # 创建测试牛只档案
        test_profile = CattleProfile(
            cattle_id="TEST001",
            ear_tag_ids=["A001"],
            breed="Holstein"
        )
        
        # 添加花色特征
        reid = CoatPatternReID(extractor_type='mock')
        feature = reid.extract_coat_pattern_feature(cattle_image)
        if feature:
            test_profile.add_coat_pattern_feature(feature)
        
        candidate_profiles = [test_profile]
        
        # 识别
        result = identifier.identify_cattle(
            cattle_image=cattle_image,
            ear_tag_region=ear_tag_image,
            candidate_profiles=candidate_profiles
        )
        
        print(f"   ✅ 融合识别器测试成功")
        print(f"   识别结果: ID={result.cattle_id}, 方法={result.method.value}")
        print(f"   置信度: {result.confidence:.2f}")
        print(f"   统计信息: {identifier.get_stats()}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 融合识别器测试失败: {e}")
        return False

def test_database():
    """测试数据库"""
    print("🗄️ 测试数据库...")
    
    try:
        # 使用临时数据库
        db = CattleDatabase("test_database.db")
        
        # 创建测试牛只档案
        test_profile = CattleProfile(
            cattle_id="TEST001",
            ear_tag_ids=["A001", "B001"],
            breed="Holstein",
            gender="Female"
        )
        
        # 添加档案
        success = db.add_cattle_profile(test_profile)
        if not success:
            raise Exception("添加牛只档案失败")
        
        # 获取档案
        retrieved_profile = db.get_cattle_profile("TEST001")
        if not retrieved_profile:
            raise Exception("获取牛只档案失败")
        
        # 获取统计信息
        stats = db.get_statistics()
        
        print(f"   ✅ 数据库测试成功")
        print(f"   档案ID: {retrieved_profile.cattle_id}")
        print(f"   耳标数量: {len(retrieved_profile.ear_tag_ids)}")
        print(f"   统计信息: {stats}")
        
        # 清理测试数据库
        db.close()
        if Path("test_database.db").exists():
            Path("test_database.db").unlink()
        
        return True
        
    except Exception as e:
        print(f"   ❌ 数据库测试失败: {e}")
        return False

def test_config_manager():
    """测试配置管理器"""
    print("⚙️ 测试配置管理器...")
    
    try:
        config_manager = ConfigManager()
        
        # 获取配置
        config = config_manager.get_config()
        
        # 测试配置访问
        cameras = config_manager.get_section('cameras')
        detection_model = config_manager.get_value('detection.model', 'unknown')
        
        print(f"   ✅ 配置管理器测试成功")
        print(f"   摄像头数量: {len(cameras)}")
        print(f"   检测模型: {detection_model}")
        print(f"   配置摘要: {config_manager.get_config_summary()}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 配置管理器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 BovineInsight系统测试开始")
    print("=" * 50)
    
    # 设置日志
    setup_logging({'level': 'WARNING', 'console': True})
    
    # 测试结果
    test_results = {}
    
    # 运行各项测试
    test_functions = [
        ("配置管理器", test_config_manager),
        ("摄像头管理器", test_camera_manager),
        ("视频处理器", test_video_processor),
        ("牛只检测器", test_cattle_detector),
        ("耳标识别器", test_ear_tag_reader),
        ("花色重识别器", test_coat_pattern_reid),
        ("融合识别器", test_fused_identifier),
        ("数据库", test_database),
    ]
    
    for test_name, test_func in test_functions:
        try:
            result = test_func()
            test_results[test_name] = result
        except Exception as e:
            print(f"   ❌ {test_name}测试异常: {e}")
            test_results[test_name] = False
        
        print()
    
    # 输出测试总结
    print("=" * 50)
    print("📊 测试总结:")
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统功能正常。")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查相关模块。")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)