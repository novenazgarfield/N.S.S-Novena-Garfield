#!/usr/bin/env python3
"""
简化的数据库初始化脚本
直接使用SQLAlchemy，避免复杂的模块依赖
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

try:
    from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, relationship
    
    print("🗄️ 直接初始化BovineInsight数据库...")
    
    # 创建数据库引擎
    db_dir = Path(__file__).parent / 'data'
    db_dir.mkdir(exist_ok=True)
    db_path = db_dir / 'bovine_insight.db'
    
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    
    # 定义数据模型
    class Cattle(Base):
        __tablename__ = 'cattle'
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        cattle_id = Column(String(50), unique=True, nullable=False, index=True)
        name = Column(String(100), nullable=False)
        ear_tag = Column(String(50), unique=True, nullable=False)
        breed = Column(String(50), default='Holstein')
        birth_date = Column(DateTime, nullable=True)
        gender = Column(String(10), default='Female')
        current_bcs = Column(Float, default=3.0)
        health_status = Column(String(20), default='健康')
        last_seen = Column(DateTime, default=datetime.utcnow)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow)
    
    class BCSHistory(Base):
        __tablename__ = 'bcs_history'
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        cattle_id = Column(String(50), ForeignKey('cattle.cattle_id'), nullable=False, index=True)
        bcs_score = Column(Float, nullable=False)
        measurement_date = Column(DateTime, default=datetime.utcnow, index=True)
        measurement_method = Column(String(20), default='auto')
        confidence = Column(Float, default=0.9)
        notes = Column(Text, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
    
    class Detection(Base):
        __tablename__ = 'detections'
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        cattle_id = Column(String(50), ForeignKey('cattle.cattle_id'), nullable=False, index=True)
        camera_id = Column(String(20), nullable=False, index=True)
        detection_time = Column(DateTime, default=datetime.utcnow, index=True)
        confidence = Column(Float, nullable=False)
        bcs_score = Column(Float, nullable=True)
        bbox_x = Column(Float, nullable=True)
        bbox_y = Column(Float, nullable=True)
        bbox_width = Column(Float, nullable=True)
        bbox_height = Column(Float, nullable=True)
        identification_method = Column(String(20), default='coat_pattern')
        image_path = Column(String(255), nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
    
    class Alert(Base):
        __tablename__ = 'alerts'
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        cattle_id = Column(String(50), ForeignKey('cattle.cattle_id'), nullable=False, index=True)
        alert_type = Column(String(20), nullable=False, index=True)
        alert_level = Column(String(20), default='medium')
        title = Column(String(100), nullable=False)
        message = Column(Text, nullable=False)
        is_resolved = Column(Boolean, default=False)
        created_at = Column(DateTime, default=datetime.utcnow, index=True)
        resolved_at = Column(DateTime, nullable=True)
        resolved_by = Column(String(50), nullable=True)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")
    
    # 创建会话
    session = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing_cattle = session.query(Cattle).first()
        if existing_cattle:
            cattle_count = session.query(Cattle).count()
            print(f"📋 发现现有数据: {cattle_count} 头牛")
        else:
            print("🐄 创建示例牛只数据...")
            
            # 创建示例牛只
            sample_cattle_data = [
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
            
            for cattle_data in sample_cattle_data:
                cattle = Cattle(**cattle_data)
                session.add(cattle)
                session.commit()
                session.refresh(cattle)
                print(f"  ✅ 创建牛只: {cattle.name} ({cattle.cattle_id})")
                
                # 为每头牛创建历史BCS记录
                for i in range(5, 15):
                    days_ago = i
                    measurement_date = datetime.utcnow() - timedelta(days=days_ago)
                    
                    # 模拟BCS变化
                    bcs_variation = np.random.normal(0, 0.15)
                    simulated_bcs = max(1.0, min(5.0, cattle_data['current_bcs'] + bcs_variation))
                    
                    # 添加BCS历史记录
                    bcs_record = BCSHistory(
                        cattle_id=cattle.cattle_id,
                        bcs_score=simulated_bcs,
                        measurement_date=measurement_date,
                        confidence=0.85 + np.random.random() * 0.1,
                        measurement_method='auto'
                    )
                    session.add(bcs_record)
                    
                    # 添加检测记录
                    detection = Detection(
                        cattle_id=cattle.cattle_id,
                        camera_id=f'camera_0{np.random.randint(1, 5)}',
                        detection_time=measurement_date,
                        confidence=0.85 + np.random.random() * 0.1,
                        bcs_score=simulated_bcs,
                        bbox_x=np.random.uniform(100, 300),
                        bbox_y=np.random.uniform(50, 200),
                        bbox_width=np.random.uniform(150, 250),
                        bbox_height=np.random.uniform(100, 180),
                        identification_method='coat_pattern'
                    )
                    session.add(detection)
                
                session.commit()
            
            # 创建一些示例预警
            sample_alerts = [
                {
                    'cattle_id': 'COW-0004',
                    'alert_type': 'orange',
                    'alert_level': 'medium',
                    'title': 'BCS评分偏低',
                    'message': '牛只莫莉的BCS评分为2.3，建议增加营养供应'
                },
                {
                    'cattle_id': 'COW-0005',
                    'alert_type': 'red',
                    'alert_level': 'high',
                    'title': 'BCS评分过高',
                    'message': '牛只安妮的BCS评分为4.1，需要控制饲料供应'
                }
            ]
            
            for alert_data in sample_alerts:
                alert = Alert(**alert_data)
                session.add(alert)
            
            session.commit()
            print(f"✅ 数据库初始化完成！创建了 {len(sample_cattle_data)} 头牛只")
        
        # 显示统计信息
        cattle_count = session.query(Cattle).count()
        bcs_count = session.query(BCSHistory).count()
        detection_count = session.query(Detection).count()
        alert_count = session.query(Alert).count()
        
        print(f"📊 数据库统计:")
        print(f"   - 牛只总数: {cattle_count}")
        print(f"   - BCS记录: {bcs_count}")
        print(f"   - 检测记录: {detection_count}")
        print(f"   - 预警信息: {alert_count}")
        
        print("🎉 数据库初始化成功！")
        print(f"📁 数据库文件: {db_path}")
        
    finally:
        session.close()
    
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    print("请确保已安装所需依赖: pip install sqlalchemy numpy")
except Exception as e:
    print(f"❌ 数据库初始化失败: {e}")
    import traceback
    traceback.print_exc()