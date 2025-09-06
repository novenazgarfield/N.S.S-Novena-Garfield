#!/usr/bin/env python3
"""
BovineInsight 数据访问层 (DAO - Data Access Object)
提供所有数据库操作的高级接口
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from .models import (
    Cattle, BCSHistory, Detection, Alert, SystemLog, MLModel,
    get_db_session
)

logger = logging.getLogger(__name__)

class CattleDAO:
    """牛只数据访问对象"""
    
    @staticmethod
    def create_cattle(cattle_data: Dict[str, Any]) -> Cattle:
        """创建新牛只记录"""
        session = get_db_session()
        try:
            cattle = Cattle(**cattle_data)
            session.add(cattle)
            session.commit()
            session.refresh(cattle)
            logger.info(f"创建牛只记录: {cattle.cattle_id}")
            return cattle
        except Exception as e:
            session.rollback()
            logger.error(f"创建牛只记录失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_cattle_by_id(cattle_id: str) -> Optional[Cattle]:
        """根据ID获取牛只信息"""
        session = get_db_session()
        try:
            cattle = session.query(Cattle).filter(Cattle.cattle_id == cattle_id).first()
            return cattle
        finally:
            session.close()
    
    @staticmethod
    def get_all_cattle(limit: int = 100, offset: int = 0) -> List[Cattle]:
        """获取所有牛只列表"""
        session = get_db_session()
        try:
            cattle_list = session.query(Cattle)\
                .order_by(desc(Cattle.last_seen))\
                .limit(limit)\
                .offset(offset)\
                .all()
            return cattle_list
        finally:
            session.close()
    
    @staticmethod
    def update_cattle_bcs(cattle_id: str, bcs_score: float) -> bool:
        """更新牛只BCS评分"""
        session = get_db_session()
        try:
            cattle = session.query(Cattle).filter(Cattle.cattle_id == cattle_id).first()
            if cattle:
                cattle.current_bcs = bcs_score
                cattle.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"更新牛只BCS: {cattle_id} -> {bcs_score}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"更新牛只BCS失败: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def update_last_seen(cattle_id: str, timestamp: datetime = None) -> bool:
        """更新牛只最后出现时间"""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        session = get_db_session()
        try:
            cattle = session.query(Cattle).filter(Cattle.cattle_id == cattle_id).first()
            if cattle:
                cattle.last_seen = timestamp
                cattle.updated_at = datetime.utcnow()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"更新最后出现时间失败: {e}")
            return False
        finally:
            session.close()

class BCSHistoryDAO:
    """BCS历史数据访问对象"""
    
    @staticmethod
    def add_bcs_record(cattle_id: str, bcs_score: float, confidence: float = 0.9, 
                      method: str = 'auto') -> BCSHistory:
        """添加BCS历史记录"""
        session = get_db_session()
        try:
            bcs_record = BCSHistory(
                cattle_id=cattle_id,
                bcs_score=bcs_score,
                confidence=confidence,
                measurement_method=method
            )
            session.add(bcs_record)
            session.commit()
            session.refresh(bcs_record)
            
            # 同时更新牛只的当前BCS
            CattleDAO.update_cattle_bcs(cattle_id, bcs_score)
            
            logger.info(f"添加BCS记录: {cattle_id} -> {bcs_score}")
            return bcs_record
        except Exception as e:
            session.rollback()
            logger.error(f"添加BCS记录失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_cattle_bcs_history(cattle_id: str, days: int = 30) -> List[BCSHistory]:
        """获取牛只BCS历史记录"""
        session = get_db_session()
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            history = session.query(BCSHistory)\
                .filter(and_(
                    BCSHistory.cattle_id == cattle_id,
                    BCSHistory.measurement_date >= start_date
                ))\
                .order_by(BCSHistory.measurement_date)\
                .all()
            return history
        finally:
            session.close()
    
    @staticmethod
    def get_bcs_statistics() -> Dict[str, Any]:
        """获取BCS统计信息"""
        session = get_db_session()
        try:
            # 获取最新的BCS分布
            latest_bcs = session.query(Cattle.current_bcs).all()
            bcs_scores = [record[0] for record in latest_bcs if record[0] is not None]
            
            if not bcs_scores:
                return {
                    'total_cattle': 0,
                    'average_bcs': 0.0,
                    'distribution': {},
                    'healthy_percentage': 0.0
                }
            
            # 计算分布
            distribution = {
                '1.0-1.5': len([s for s in bcs_scores if 1.0 <= s < 1.5]),
                '1.5-2.5': len([s for s in bcs_scores if 1.5 <= s < 2.5]),
                '2.5-3.5': len([s for s in bcs_scores if 2.5 <= s < 3.5]),
                '3.5-4.5': len([s for s in bcs_scores if 3.5 <= s < 4.5]),
                '4.5-5.0': len([s for s in bcs_scores if 4.5 <= s <= 5.0])
            }
            
            # 计算健康比例 (2.5-4.0为健康范围)
            healthy_count = len([s for s in bcs_scores if 2.5 <= s <= 4.0])
            healthy_percentage = (healthy_count / len(bcs_scores)) * 100
            
            return {
                'total_cattle': len(bcs_scores),
                'average_bcs': round(sum(bcs_scores) / len(bcs_scores), 2),
                'distribution': distribution,
                'healthy_percentage': round(healthy_percentage, 1)
            }
        finally:
            session.close()

class DetectionDAO:
    """检测记录数据访问对象"""
    
    @staticmethod
    def save_detection(detection_data: Dict[str, Any]) -> Detection:
        """保存检测记录"""
        session = get_db_session()
        try:
            detection = Detection(**detection_data)
            session.add(detection)
            session.commit()
            session.refresh(detection)
            
            # 更新牛只最后出现时间
            CattleDAO.update_last_seen(detection.cattle_id, detection.detection_time)
            
            # 如果有BCS评分，添加到历史记录
            if detection.bcs_score:
                BCSHistoryDAO.add_bcs_record(
                    detection.cattle_id, 
                    detection.bcs_score, 
                    detection.confidence
                )
            
            logger.info(f"保存检测记录: {detection.cattle_id}")
            return detection
        except Exception as e:
            session.rollback()
            logger.error(f"保存检测记录失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_recent_detections(hours: int = 24, limit: int = 100) -> List[Detection]:
        """获取最近的检测记录"""
        session = get_db_session()
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            detections = session.query(Detection)\
                .filter(Detection.detection_time >= start_time)\
                .order_by(desc(Detection.detection_time))\
                .limit(limit)\
                .all()
            return detections
        finally:
            session.close()
    
    @staticmethod
    def get_cattle_detections(cattle_id: str, days: int = 7) -> List[Detection]:
        """获取特定牛只的检测记录"""
        session = get_db_session()
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            detections = session.query(Detection)\
                .filter(and_(
                    Detection.cattle_id == cattle_id,
                    Detection.detection_time >= start_date
                ))\
                .order_by(desc(Detection.detection_time))\
                .all()
            return detections
        finally:
            session.close()

class AlertDAO:
    """预警信息数据访问对象"""
    
    @staticmethod
    def create_alert(cattle_id: str, alert_type: str, title: str, 
                    message: str, level: str = 'medium') -> Alert:
        """创建预警信息"""
        session = get_db_session()
        try:
            alert = Alert(
                cattle_id=cattle_id,
                alert_type=alert_type,
                alert_level=level,
                title=title,
                message=message
            )
            session.add(alert)
            session.commit()
            session.refresh(alert)
            logger.info(f"创建预警: {cattle_id} - {title}")
            return alert
        except Exception as e:
            session.rollback()
            logger.error(f"创建预警失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_active_alerts(limit: int = 50) -> List[Alert]:
        """获取活跃的预警信息"""
        session = get_db_session()
        try:
            alerts = session.query(Alert)\
                .filter(Alert.is_resolved == False)\
                .order_by(desc(Alert.created_at))\
                .limit(limit)\
                .all()
            return alerts
        finally:
            session.close()
    
    @staticmethod
    def resolve_alert(alert_id: int, resolved_by: str = 'system') -> bool:
        """解决预警"""
        session = get_db_session()
        try:
            alert = session.query(Alert).filter(Alert.id == alert_id).first()
            if alert:
                alert.is_resolved = True
                alert.resolved_at = datetime.utcnow()
                alert.resolved_by = resolved_by
                session.commit()
                logger.info(f"解决预警: {alert_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"解决预警失败: {e}")
            return False
        finally:
            session.close()

class SystemLogDAO:
    """系统日志数据访问对象"""
    
    @staticmethod
    def log(level: str, module: str, message: str, details: str = None, 
           user_id: str = None, ip_address: str = None):
        """记录系统日志"""
        session = get_db_session()
        try:
            log_entry = SystemLog(
                log_level=level,
                module=module,
                message=message,
                details=details,
                user_id=user_id,
                ip_address=ip_address
            )
            session.add(log_entry)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"记录系统日志失败: {e}")
        finally:
            session.close()
    
    @staticmethod
    def get_logs(level: str = None, module: str = None, hours: int = 24, 
                limit: int = 1000) -> List[SystemLog]:
        """获取系统日志"""
        session = get_db_session()
        try:
            query = session.query(SystemLog)
            
            # 时间过滤
            start_time = datetime.utcnow() - timedelta(hours=hours)
            query = query.filter(SystemLog.timestamp >= start_time)
            
            # 级别过滤
            if level:
                query = query.filter(SystemLog.log_level == level)
            
            # 模块过滤
            if module:
                query = query.filter(SystemLog.module == module)
            
            logs = query.order_by(desc(SystemLog.timestamp)).limit(limit).all()
            return logs
        finally:
            session.close()

# 便捷函数
def log_info(module: str, message: str, **kwargs):
    """记录INFO级别日志"""
    SystemLogDAO.log('INFO', module, message, **kwargs)

def log_warning(module: str, message: str, **kwargs):
    """记录WARNING级别日志"""
    SystemLogDAO.log('WARNING', module, message, **kwargs)

def log_error(module: str, message: str, **kwargs):
    """记录ERROR级别日志"""
    SystemLogDAO.log('ERROR', module, message, **kwargs)