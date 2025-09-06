#!/usr/bin/env python3
"""
BovineInsight 智能决策引擎
基于历史数据分析，生成智能预警和建议
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import logging
import statistics
from dataclasses import dataclass

from ..database.dao import CattleDAO, BCSHistoryDAO, DetectionDAO, AlertDAO, log_info, log_warning, log_error
from ..database.models import Cattle, BCSHistory, Detection

logger = logging.getLogger(__name__)

@dataclass
class HealthTrend:
    """健康趋势分析结果"""
    cattle_id: str
    trend_direction: str  # 'improving', 'stable', 'declining'
    trend_strength: float  # 0.0-1.0
    current_bcs: float
    average_bcs: float
    bcs_change_rate: float  # 每天的BCS变化率
    risk_level: str  # 'low', 'medium', 'high'
    recommendations: List[str]

@dataclass
class FeedingAdvice:
    """饲养建议"""
    cattle_id: str
    current_bcs: float
    target_bcs: float
    feed_adjustment: str  # 'increase', 'decrease', 'maintain'
    feed_change_percentage: float
    specific_recommendations: List[str]

class DecisionEngine:
    """智能决策引擎"""
    
    def __init__(self):
        self.bcs_healthy_range = (2.5, 4.0)  # 健康BCS范围
        self.bcs_optimal_range = (3.0, 3.5)  # 最佳BCS范围
        self.trend_analysis_days = 14  # 趋势分析天数
        self.missing_threshold_hours = 72  # 失踪预警阈值(小时)
        
    def analyze_herd_health(self) -> Dict[str, Any]:
        """分析整个牛群的健康状况"""
        log_info('DecisionEngine', '开始分析牛群健康状况')
        
        try:
            # 获取所有牛只
            all_cattle = CattleDAO.get_all_cattle()
            
            if not all_cattle:
                return {
                    'total_cattle': 0,
                    'health_summary': {},
                    'alerts_generated': 0,
                    'recommendations': []
                }
            
            health_trends = []
            alerts_generated = 0
            
            # 分析每头牛的健康趋势
            for cattle in all_cattle:
                trend = self.analyze_cattle_health_trend(cattle.cattle_id)
                if trend:
                    health_trends.append(trend)
                    
                    # 根据趋势生成预警
                    alerts = self._generate_health_alerts(trend)
                    alerts_generated += len(alerts)
            
            # 生成牛群级别的建议
            herd_recommendations = self._generate_herd_recommendations(health_trends)
            
            # 统计健康状况
            health_summary = self._summarize_health_trends(health_trends)
            
            log_info('DecisionEngine', f'牛群健康分析完成: {len(all_cattle)}头牛, {alerts_generated}个预警')
            
            return {
                'total_cattle': len(all_cattle),
                'health_summary': health_summary,
                'alerts_generated': alerts_generated,
                'recommendations': herd_recommendations,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            log_error('DecisionEngine', f'牛群健康分析失败: {e}')
            raise
    
    def analyze_cattle_health_trend(self, cattle_id: str) -> HealthTrend:
        """分析单头牛的健康趋势"""
        try:
            # 获取BCS历史数据
            bcs_history = BCSHistoryDAO.get_cattle_bcs_history(
                cattle_id, days=self.trend_analysis_days
            )
            
            if len(bcs_history) < 2:
                # 数据不足，返回基础分析
                cattle = CattleDAO.get_cattle_by_id(cattle_id)
                if not cattle:
                    return None
                    
                return HealthTrend(
                    cattle_id=cattle_id,
                    trend_direction='stable',
                    trend_strength=0.0,
                    current_bcs=cattle.current_bcs,
                    average_bcs=cattle.current_bcs,
                    bcs_change_rate=0.0,
                    risk_level='low',
                    recommendations=['需要更多数据进行趋势分析']
                )
            
            # 计算趋势
            bcs_scores = [record.bcs_score for record in bcs_history]
            timestamps = [record.measurement_date for record in bcs_history]
            
            current_bcs = bcs_scores[-1]
            average_bcs = statistics.mean(bcs_scores)
            
            # 计算变化率 (每天)
            time_span = (timestamps[-1] - timestamps[0]).days
            if time_span > 0:
                bcs_change_rate = (bcs_scores[-1] - bcs_scores[0]) / time_span
            else:
                bcs_change_rate = 0.0
            
            # 判断趋势方向和强度
            trend_direction, trend_strength = self._calculate_trend(bcs_scores)
            
            # 评估风险等级
            risk_level = self._assess_risk_level(current_bcs, bcs_change_rate, trend_direction)
            
            # 生成建议
            recommendations = self._generate_cattle_recommendations(
                current_bcs, bcs_change_rate, trend_direction
            )
            
            return HealthTrend(
                cattle_id=cattle_id,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                current_bcs=current_bcs,
                average_bcs=average_bcs,
                bcs_change_rate=bcs_change_rate,
                risk_level=risk_level,
                recommendations=recommendations
            )
            
        except Exception as e:
            log_error('DecisionEngine', f'分析牛只健康趋势失败 {cattle_id}: {e}')
            return None
    
    def generate_feeding_advice(self, cattle_id: str) -> FeedingAdvice:
        """生成饲养建议"""
        try:
            cattle = CattleDAO.get_cattle_by_id(cattle_id)
            if not cattle:
                return None
            
            current_bcs = cattle.current_bcs
            target_bcs = 3.25  # 目标BCS (最佳范围中值)
            
            # 计算BCS差异
            bcs_diff = current_bcs - target_bcs
            
            # 确定饲料调整方向
            if abs(bcs_diff) < 0.25:
                feed_adjustment = 'maintain'
                feed_change_percentage = 0.0
            elif bcs_diff > 0:
                feed_adjustment = 'decrease'
                feed_change_percentage = min(abs(bcs_diff) * 10, 20)  # 最多减少20%
            else:
                feed_adjustment = 'increase'
                feed_change_percentage = min(abs(bcs_diff) * 10, 25)  # 最多增加25%
            
            # 生成具体建议
            specific_recommendations = self._generate_feeding_recommendations(
                current_bcs, target_bcs, feed_adjustment, feed_change_percentage
            )
            
            return FeedingAdvice(
                cattle_id=cattle_id,
                current_bcs=current_bcs,
                target_bcs=target_bcs,
                feed_adjustment=feed_adjustment,
                feed_change_percentage=feed_change_percentage,
                specific_recommendations=specific_recommendations
            )
            
        except Exception as e:
            log_error('DecisionEngine', f'生成饲养建议失败 {cattle_id}: {e}')
            return None
    
    def check_missing_cattle(self) -> List[Dict[str, Any]]:
        """检查失踪的牛只"""
        try:
            all_cattle = CattleDAO.get_all_cattle()
            missing_cattle = []
            threshold_time = datetime.utcnow() - timedelta(hours=self.missing_threshold_hours)
            
            for cattle in all_cattle:
                if cattle.last_seen < threshold_time:
                    hours_missing = (datetime.utcnow() - cattle.last_seen).total_seconds() / 3600
                    missing_cattle.append({
                        'cattle_id': cattle.cattle_id,
                        'name': cattle.name,
                        'last_seen': cattle.last_seen,
                        'hours_missing': round(hours_missing, 1)
                    })
                    
                    # 生成失踪预警
                    AlertDAO.create_alert(
                        cattle_id=cattle.cattle_id,
                        alert_type='orange',
                        title='牛只失踪预警',
                        message=f'牛只 {cattle.name} 已超过 {round(hours_missing, 1)} 小时未出现',
                        level='high'
                    )
            
            if missing_cattle:
                log_warning('DecisionEngine', f'发现 {len(missing_cattle)} 头失踪牛只')
            
            return missing_cattle
            
        except Exception as e:
            log_error('DecisionEngine', f'检查失踪牛只失败: {e}')
            return []
    
    def _calculate_trend(self, bcs_scores: List[float]) -> Tuple[str, float]:
        """计算BCS趋势方向和强度"""
        if len(bcs_scores) < 3:
            return 'stable', 0.0
        
        # 使用线性回归计算趋势
        n = len(bcs_scores)
        x = list(range(n))
        y = bcs_scores
        
        # 计算斜率
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'stable', 0.0
        
        slope = numerator / denominator
        
        # 判断趋势方向和强度
        if abs(slope) < 0.01:
            return 'stable', abs(slope)
        elif slope > 0:
            return 'improving', min(abs(slope), 1.0)
        else:
            return 'declining', min(abs(slope), 1.0)
    
    def _assess_risk_level(self, current_bcs: float, change_rate: float, 
                          trend_direction: str) -> str:
        """评估风险等级"""
        # 基于当前BCS的风险
        if current_bcs < 2.0 or current_bcs > 4.5:
            base_risk = 'high'
        elif current_bcs < 2.5 or current_bcs > 4.0:
            base_risk = 'medium'
        else:
            base_risk = 'low'
        
        # 基于变化趋势的风险调整
        if trend_direction == 'declining' and abs(change_rate) > 0.05:
            if base_risk == 'low':
                return 'medium'
            elif base_risk == 'medium':
                return 'high'
        
        return base_risk
    
    def _generate_cattle_recommendations(self, current_bcs: float, change_rate: float, 
                                       trend_direction: str) -> List[str]:
        """生成单头牛的建议"""
        recommendations = []
        
        # 基于当前BCS的建议
        if current_bcs < 2.5:
            recommendations.append('增加高能量饲料供应')
            recommendations.append('检查是否有健康问题')
        elif current_bcs > 4.0:
            recommendations.append('减少精料供应，增加粗饲料比例')
            recommendations.append('增加运动量')
        
        # 基于趋势的建议
        if trend_direction == 'declining' and abs(change_rate) > 0.03:
            recommendations.append('密切监控健康状况')
            recommendations.append('考虑兽医检查')
        elif trend_direction == 'improving' and current_bcs > 3.5:
            recommendations.append('控制饲料供应，避免过肥')
        
        if not recommendations:
            recommendations.append('继续保持当前饲养管理')
        
        return recommendations
    
    def _generate_feeding_recommendations(self, current_bcs: float, target_bcs: float,
                                        adjustment: str, percentage: float) -> List[str]:
        """生成具体的饲养建议"""
        recommendations = []
        
        if adjustment == 'increase':
            recommendations.append(f'增加精料供应 {percentage:.1f}%')
            recommendations.append('提高饲料中蛋白质含量')
            recommendations.append('确保充足的饮水供应')
            if current_bcs < 2.0:
                recommendations.append('考虑添加高脂肪饲料补充剂')
        elif adjustment == 'decrease':
            recommendations.append(f'减少精料供应 {percentage:.1f}%')
            recommendations.append('增加粗饲料比例')
            recommendations.append('增加运动时间')
            if current_bcs > 4.0:
                recommendations.append('限制高能量饲料的摄入')
        else:
            recommendations.append('维持当前饲料配方')
            recommendations.append('继续定期监控BCS变化')
        
        return recommendations
    
    def _generate_health_alerts(self, trend: HealthTrend) -> List[Dict[str, Any]]:
        """根据健康趋势生成预警"""
        alerts = []
        
        # 高风险预警
        if trend.risk_level == 'high':
            if trend.current_bcs < 2.0:
                AlertDAO.create_alert(
                    cattle_id=trend.cattle_id,
                    alert_type='red',
                    title='严重营养不良',
                    message=f'BCS评分过低 ({trend.current_bcs:.1f})，需要立即干预',
                    level='high'
                )
                alerts.append({'type': 'red', 'message': '严重营养不良'})
            elif trend.current_bcs > 4.5:
                AlertDAO.create_alert(
                    cattle_id=trend.cattle_id,
                    alert_type='red',
                    title='严重过肥',
                    message=f'BCS评分过高 ({trend.current_bcs:.1f})，影响健康和繁殖',
                    level='high'
                )
                alerts.append({'type': 'red', 'message': '严重过肥'})
        
        # 中等风险预警
        elif trend.risk_level == 'medium':
            if trend.trend_direction == 'declining':
                AlertDAO.create_alert(
                    cattle_id=trend.cattle_id,
                    alert_type='orange',
                    title='健康状况下降',
                    message=f'BCS评分持续下降，当前 {trend.current_bcs:.1f}',
                    level='medium'
                )
                alerts.append({'type': 'orange', 'message': '健康状况下降'})
        
        return alerts
    
    def _generate_herd_recommendations(self, health_trends: List[HealthTrend]) -> List[str]:
        """生成牛群级别的建议"""
        if not health_trends:
            return []
        
        recommendations = []
        
        # 统计风险分布
        high_risk_count = len([t for t in health_trends if t.risk_level == 'high'])
        declining_count = len([t for t in health_trends if t.trend_direction == 'declining'])
        
        total_cattle = len(health_trends)
        
        # 基于风险分布的建议
        if high_risk_count > total_cattle * 0.1:  # 超过10%高风险
            recommendations.append('建议全群健康检查，评估饲养管理方案')
        
        if declining_count > total_cattle * 0.2:  # 超过20%健康下降
            recommendations.append('检查饲料质量和环境条件')
            recommendations.append('考虑调整饲养密度')
        
        # 基于平均BCS的建议
        avg_bcs = statistics.mean([t.current_bcs for t in health_trends])
        if avg_bcs < 2.8:
            recommendations.append('整体营养水平偏低，建议提高饲料质量')
        elif avg_bcs > 3.8:
            recommendations.append('整体营养水平偏高，注意控制精料供应')
        
        if not recommendations:
            recommendations.append('牛群整体健康状况良好，继续保持当前管理水平')
        
        return recommendations
    
    def _summarize_health_trends(self, health_trends: List[HealthTrend]) -> Dict[str, Any]:
        """汇总健康趋势统计"""
        if not health_trends:
            return {}
        
        # 风险等级分布
        risk_distribution = {
            'low': len([t for t in health_trends if t.risk_level == 'low']),
            'medium': len([t for t in health_trends if t.risk_level == 'medium']),
            'high': len([t for t in health_trends if t.risk_level == 'high'])
        }
        
        # 趋势方向分布
        trend_distribution = {
            'improving': len([t for t in health_trends if t.trend_direction == 'improving']),
            'stable': len([t for t in health_trends if t.trend_direction == 'stable']),
            'declining': len([t for t in health_trends if t.trend_direction == 'declining'])
        }
        
        # BCS统计
        bcs_scores = [t.current_bcs for t in health_trends]
        bcs_stats = {
            'average': round(statistics.mean(bcs_scores), 2),
            'median': round(statistics.median(bcs_scores), 2),
            'min': round(min(bcs_scores), 2),
            'max': round(max(bcs_scores), 2)
        }
        
        return {
            'risk_distribution': risk_distribution,
            'trend_distribution': trend_distribution,
            'bcs_statistics': bcs_stats,
            'total_analyzed': len(health_trends)
        }

# 全局决策引擎实例
decision_engine = DecisionEngine()

def get_decision_engine() -> DecisionEngine:
    """获取决策引擎实例"""
    return decision_engine