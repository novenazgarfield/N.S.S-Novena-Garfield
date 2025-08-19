#!/usr/bin/env python3
"""
BovineInsight系统简化测试脚本
Simplified System Test Script

测试系统核心功能（避免深度学习依赖）
"""

import sys
import os
import logging
import numpy as np
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试模块导入"""
    print("📦 测试模块导入...")
    
    try:
        # 测试基础模块导入
        from src.utils import ConfigManager, setup_logging
        print("   ✅ 工具模块导入成功")
        
        from src.data_processing.camera_manager import CameraManager, CameraConfig, CameraType
        print("   ✅ 摄像头管理模块导入成功")
        
        from src.data_processing.video_processor import VideoProcessor
        print("   ✅ 视频处理模块导入成功")
        
        from src.data_processing.frame_buffer import FrameBuffer
        print("   ✅ 帧缓冲模块导入成功")
        
        from src.identification.identification_utils import CattleProfile, IdentificationResult
        print("   ✅ 身份识别工具模块导入成功")
        
        from src.identification.ear_tag_reader import EarTagReader
        print("   ✅ 耳标识别模块导入成功")
        
        from src.body_condition.body_condition_utils import BCSResult, AnatomicalKeypoints
        print("   ✅ 体况评分工具模块导入成功")
        
        from src.database.cattle_database import CattleDatabase
        print("   ✅ 数据库模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 模块导入失败: {e}")
        return False

def test_config_manager():
    """测试配置管理器"""
    print("⚙️ 测试配置管理器...")
    
    try:
        from src.utils import ConfigManager
        
        config_manager = ConfigManager()
        
        # 获取配置
        config = config_manager.get_config()
        
        # 测试配置访问
        cameras = config_manager.get_section('cameras')
        detection_model = config_manager.get_value('detection.model', 'unknown')
        
        print(f"   ✅ 配置管理器测试成功")
        print(f"   摄像头数量: {len(cameras)}")
        print(f"   检测模型: {detection_model}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 配置管理器测试失败: {e}")
        return False

def test_camera_manager():
    """测试摄像头管理器"""
    print("🎥 测试摄像头管理器...")
    
    try:
        from src.data_processing.camera_manager import CameraManager, CameraConfig, CameraType
        
        camera_manager = CameraManager()
        
        # 创建测试配置
        config = CameraConfig(
            camera_id=999,  # 使用不存在的摄像头ID
            camera_type=CameraType.EAR_TAG,
            name='test_camera'
        )
        
        # 测试添加摄像头（预期会失败，但不应该崩溃）
        result = camera_manager.add_camera(config)
        
        # 获取状态
        status = camera_manager.get_status()
        
        print(f"   ✅ 摄像头管理器测试成功")
        print(f"   状态: {status['total_cameras']} 个摄像头")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 摄像头管理器测试失败: {e}")
        return False

def test_video_processor():
    """测试视频处理器"""
    print("🎬 测试视频处理器...")
    
    try:
        from src.data_processing.video_processor import VideoProcessor
        import cv2
        
        processor = VideoProcessor()
        
        # 创建测试图像
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        frames = {'test_camera': test_image}
        
        # 处理帧
        processed_frames = processor.process_frames(frames)
        
        print(f"   ✅ 视频处理器测试成功")
        print(f"   处理了 {len(processed_frames)} 帧")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 视频处理器测试失败: {e}")
        return False

def test_frame_buffer():
    """测试帧缓冲器"""
    print("🗃️ 测试帧缓冲器...")
    
    try:
        from src.data_processing.frame_buffer import FrameBuffer
        
        buffer = FrameBuffer(max_buffer_size=10)
        
        # 添加测试帧
        test_frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        for i in range(5):
            buffer.add_frame(f'camera_{i%2}', test_frame)
        
        # 获取最新帧
        latest_frames = buffer.get_latest_frames()
        
        # 获取状态
        status = buffer.get_buffer_status()
        
        print(f"   ✅ 帧缓冲器测试成功")
        print(f"   缓冲帧数: {len(latest_frames)}")
        print(f"   总摄像头: {status['total_cameras']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 帧缓冲器测试失败: {e}")
        return False

def test_ear_tag_reader():
    """测试耳标识别器"""
    print("🏷️ 测试耳标识别器...")
    
    try:
        from src.identification.ear_tag_reader import EarTagReader
        import cv2
        
        reader = EarTagReader()
        
        # 创建测试耳标图像
        test_image = np.ones((100, 200, 3), dtype=np.uint8) * 255
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(test_image, "A001", (50, 60), font, 1, (0, 0, 0), 2)
        
        # 识别
        result = reader.read_ear_tag(test_image)
        
        print(f"   ✅ 耳标识别器测试成功")
        print(f"   识别结果: ID={result.cattle_id}, 置信度={result.confidence:.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 耳标识别器测试失败: {e}")
        return False

def test_cattle_profile():
    """测试牛只档案"""
    print("📋 测试牛只档案...")
    
    try:
        from src.identification.identification_utils import CattleProfile
        
        # 创建测试档案
        profile = CattleProfile(
            cattle_id="TEST001",
            ear_tag_ids=["A001", "B001"],
            breed="Holstein",
            gender="Female"
        )
        
        # 测试方法
        profile.add_ear_tag("C001")
        
        # 转换为字典
        profile_dict = profile.to_dict()
        
        # 从字典创建
        new_profile = CattleProfile.from_dict(profile_dict)
        
        print(f"   ✅ 牛只档案测试成功")
        print(f"   档案ID: {new_profile.cattle_id}")
        print(f"   耳标数量: {len(new_profile.ear_tag_ids)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 牛只档案测试失败: {e}")
        return False

def test_database():
    """测试数据库"""
    print("🗄️ 测试数据库...")
    
    try:
        from src.database.cattle_database import CattleDatabase
        from src.identification.identification_utils import CattleProfile
        
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
        print(f"   统计信息: 总牛只数={stats.get('total_cattle', 0)}")
        
        # 清理测试数据库
        db.close()
        if Path("test_database.db").exists():
            Path("test_database.db").unlink()
        
        return True
        
    except Exception as e:
        print(f"   ❌ 数据库测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 BovineInsight系统简化测试开始")
    print("=" * 50)
    
    # 测试结果
    test_results = {}
    
    # 运行各项测试
    test_functions = [
        ("模块导入", test_imports),
        ("配置管理器", test_config_manager),
        ("摄像头管理器", test_camera_manager),
        ("视频处理器", test_video_processor),
        ("帧缓冲器", test_frame_buffer),
        ("耳标识别器", test_ear_tag_reader),
        ("牛只档案", test_cattle_profile),
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
        print("🎉 所有测试通过！系统核心功能正常。")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查相关模块。")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)