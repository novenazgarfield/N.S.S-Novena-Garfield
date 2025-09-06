#!/usr/bin/env python3
"""
BovineInsight 数据库模型定义
使用SQLAlchemy ORM定义所有数据表结构
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Cattle(Base):
    """牛只基本信息表"""
    __tablename__ = 'cattle'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cattle_id = Column(String(50), unique=True, nullable=False, index=True)  # COW-0001
    name = Column(String(100), nullable=False)  # 牛只名称
    ear_tag = Column(String(50), unique=True, nullable=False)  # 耳标号
    breed = Column(String(50), default='Holstein')  # 品种
    birth_date = Column(DateTime, nullable=True)  # 出生日期
    gender = Column(String(10), default='Female')  # 性别
    current_bcs = Column(Float, default=3.0)  # 当前BCS评分
    health_status = Column(String(20), default='健康')  # 健康状态
    last_seen = Column(DateTime, default=datetime.utcnow)  # 最后出现时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    bcs_history = relationship("BCSHistory", back_populates="cattle", cascade="all, delete-orphan")
    detections = relationship("Detection", back_populates="cattle", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="cattle", cascade="all, delete-orphan")

class BCSHistory(Base):
    """BCS评分历史记录表"""
    __tablename__ = 'bcs_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cattle_id = Column(String(50), ForeignKey('cattle.cattle_id'), nullable=False, index=True)
    bcs_score = Column(Float, nullable=False)  # BCS评分
    measurement_date = Column(DateTime, default=datetime.utcnow, index=True)  # 测量日期
    measurement_method = Column(String(20), default='auto')  # 测量方法: auto/manual
    confidence = Column(Float, default=0.9)  # 置信度
    notes = Column(Text, nullable=True)  # 备注
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    cattle = relationship("Cattle", back_populates="bcs_history")

class Detection(Base):
    """检测记录表"""
    __tablename__ = 'detections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cattle_id = Column(String(50), ForeignKey('cattle.cattle_id'), nullable=False, index=True)
    camera_id = Column(String(20), nullable=False, index=True)  # 摄像头ID
    detection_time = Column(DateTime, default=datetime.utcnow, index=True)  # 检测时间
    confidence = Column(Float, nullable=False)  # 检测置信度
    bcs_score = Column(Float, nullable=True)  # 检测到的BCS评分
    bbox_x = Column(Float, nullable=True)  # 边界框坐标
    bbox_y = Column(Float, nullable=True)
    bbox_width = Column(Float, nullable=True)
    bbox_height = Column(Float, nullable=True)
    identification_method = Column(String(20), default='coat_pattern')  # 识别方法
    image_path = Column(String(255), nullable=True)  # 图像路径
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    cattle = relationship("Cattle", back_populates="detections")

class Alert(Base):
    """预警信息表"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cattle_id = Column(String(50), ForeignKey('cattle.cattle_id'), nullable=False, index=True)
    alert_type = Column(String(20), nullable=False, index=True)  # red/orange/yellow
    alert_level = Column(String(20), default='medium')  # high/medium/low
    title = Column(String(100), nullable=False)  # 预警标题
    message = Column(Text, nullable=False)  # 预警消息
    is_resolved = Column(Boolean, default=False)  # 是否已解决
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)  # 解决时间
    resolved_by = Column(String(50), nullable=True)  # 解决人
    
    # 关联关系
    cattle = relationship("Cattle", back_populates="alerts")

class SystemLog(Base):
    """系统日志表"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    log_level = Column(String(10), nullable=False, index=True)  # DEBUG/INFO/WARNING/ERROR
    module = Column(String(50), nullable=False, index=True)  # 模块名
    message = Column(Text, nullable=False)  # 日志消息
    details = Column(Text, nullable=True)  # 详细信息
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String(50), nullable=True)  # 用户ID
    ip_address = Column(String(45), nullable=True)  # IP地址

class MLModel(Base):
    """机器学习模型信息表"""
    __tablename__ = 'ml_models'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False, unique=True)  # 模型名称
    model_type = Column(String(50), nullable=False)  # 模型类型
    model_version = Column(String(20), default='1.0')  # 模型版本
    model_path = Column(String(255), nullable=False)  # 模型文件路径
    training_data_size = Column(Integer, default=0)  # 训练数据量
    accuracy = Column(Float, nullable=True)  # 准确率
    precision = Column(Float, nullable=True)  # 精确率
    recall = Column(Float, nullable=True)  # 召回率
    f1_score = Column(Float, nullable=True)  # F1分数
    is_active = Column(Boolean, default=True)  # 是否激活
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 数据库引擎和会话管理
class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            # 默认数据库路径
            db_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'bovine_insight.db')
        
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """创建所有数据表"""
        Base.metadata.create_all(bind=self.engine)
        print(f"✅ 数据库表创建完成: {self.db_path}")
        
    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()
        
    def close(self):
        """关闭数据库连接"""
        self.engine.dispose()

# 全局数据库管理器实例
db_manager = DatabaseManager()

def init_database():
    """初始化数据库"""
    db_manager.create_tables()
    return db_manager

def get_db_session():
    """获取数据库会话的便捷函数"""
    return db_manager.get_session()

if __name__ == "__main__":
    # 测试数据库创建
    print("🗄️ 初始化BovineInsight数据库...")
    init_database()
    print("✅ 数据库初始化完成！")