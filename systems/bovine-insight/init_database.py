#!/usr/bin/env python3
"""
独立的数据库初始化脚本
避免复杂的模块依赖，直接初始化数据库
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

try:
    from src.database.models import init_database, get_db_session
    from src.database.dao import CattleDAO, BCSHistoryDAO, DetectionDAO
    from datetime import datetime, timedelta
    import numpy as np
    
    print("🗄️ 初始化BovineInsight数据库...")
    
    # 初始化数据库
    db_manager = init_database()
    print("✅ 数据库表创建完成")
    
    # 检查是否已有数据
    existing_cattle = CattleDAO.get_all_cattle(limit=1)
    if existing_cattle:
        print(f"📋 发现现有数据: {len(CattleDAO.get_all_cattle())} 头牛")
    else:
        print("🐄 创建示例牛只数据...")
        
        # 创建示例牛只
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
            cattle = CattleDAO.create_cattle(cattle_data)
            print(f"  ✅ 创建牛只: {cattle.name} ({cattle.cattle_id})")
            
            # 为每头牛创建一些历史BCS记录
            for i in range(5, 15):
                days_ago = i
                measurement_date = datetime.utcnow() - timedelta(days=days_ago)
                
                # 模拟BCS变化
                bcs_variation = np.random.normal(0, 0.15)
                simulated_bcs = max(1.0, min(5.0, cattle_data['current_bcs'] + bcs_variation))
                
                BCSHistoryDAO.add_bcs_record(
                    cattle_id=cattle.cattle_id,
                    bcs_score=simulated_bcs,
                    confidence=0.85 + np.random.random() * 0.1,
                    method='auto'
                )
                
                # 创建对应的检测记录
                DetectionDAO.save_detection({
                    'cattle_id': cattle.cattle_id,
                    'camera_id': f'camera_0{np.random.randint(1, 5)}',
                    'detection_time': measurement_date,
                    'confidence': 0.85 + np.random.random() * 0.1,
                    'bcs_score': simulated_bcs,
                    'bbox_x': np.random.uniform(100, 300),
                    'bbox_y': np.random.uniform(50, 200),
                    'bbox_width': np.random.uniform(150, 250),
                    'bbox_height': np.random.uniform(100, 180),
                    'identification_method': 'coat_pattern'
                })
        
        print(f"✅ 数据库初始化完成！创建了 {len(sample_cattle)} 头牛只")
    
    # 显示统计信息
    all_cattle = CattleDAO.get_all_cattle()
    print(f"📊 数据库统计:")
    print(f"   - 牛只总数: {len(all_cattle)}")
    
    for cattle in all_cattle:
        bcs_count = len(BCSHistoryDAO.get_cattle_bcs_history(cattle.cattle_id, days=30))
        detection_count = len(DetectionDAO.get_cattle_detections(cattle.cattle_id, days=30))
        print(f"   - {cattle.name} ({cattle.cattle_id}): {bcs_count} BCS记录, {detection_count} 检测记录")
    
    print("🎉 数据库初始化成功！")
    
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    print("请确保已安装所需依赖: pip install sqlalchemy scikit-learn pandas")
except Exception as e:
    print(f"❌ 数据库初始化失败: {e}")
    import traceback
    traceback.print_exc()