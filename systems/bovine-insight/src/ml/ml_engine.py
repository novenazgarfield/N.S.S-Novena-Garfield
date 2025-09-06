#!/usr/bin/env python3
"""
BovineInsight 机器学习引擎
训练和部署BCS评分预测模型
"""

import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import joblib

from ..database.dao import CattleDAO, BCSHistoryDAO, DetectionDAO, log_info, log_warning, log_error
from ..database.models import MLModel, get_db_session, BCSHistory, Detection

logger = logging.getLogger(__name__)

class BCSPredictor:
    """BCS评分预测器"""
    
    def __init__(self, model_name: str = "bcs_predictor_v1"):
        self.model_name = model_name
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'days_since_last_measurement',
            'previous_bcs',
            'bcs_trend_7d',
            'bcs_trend_14d',
            'detection_frequency',
            'avg_confidence',
            'weight_change_indicator'  # 模拟特征
        ]
        self.model_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'models', f'{model_name}.pkl'
        )
        self.scaler_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'models', f'{model_name}_scaler.pkl'
        )
        
        # 确保模型目录存在
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
    
    def generate_training_data(self, days_back: int = 90, min_records: int = 5) -> pd.DataFrame:
        """生成训练数据"""
        log_info('MLEngine', f'开始生成训练数据，回溯 {days_back} 天')
        
        try:
            # 获取所有牛只
            all_cattle = CattleDAO.get_all_cattle()
            training_data = []
            
            for cattle in all_cattle:
                # 获取BCS历史记录
                bcs_history = BCSHistoryDAO.get_cattle_bcs_history(cattle.cattle_id, days=days_back)
                
                if len(bcs_history) < min_records:
                    continue
                
                # 获取检测记录
                detections = DetectionDAO.get_cattle_detections(cattle.cattle_id, days=days_back)
                
                # 为每个BCS记录生成特征
                for i, bcs_record in enumerate(bcs_history[1:], 1):  # 跳过第一个记录
                    features = self._extract_features(
                        cattle.cattle_id, bcs_history[:i], detections, bcs_record.measurement_date
                    )
                    
                    if features:
                        features['target_bcs'] = bcs_record.bcs_score
                        features['cattle_id'] = cattle.cattle_id
                        training_data.append(features)
            
            df = pd.DataFrame(training_data)
            log_info('MLEngine', f'生成训练数据完成: {len(df)} 条记录')
            
            return df
            
        except Exception as e:
            log_error('MLEngine', f'生成训练数据失败: {e}')
            raise
    
    def _extract_features(self, cattle_id: str, bcs_history: List, detections: List, 
                         target_date: datetime) -> Dict[str, float]:
        """提取特征"""
        if not bcs_history:
            return None
        
        try:
            # 基础特征
            latest_bcs = bcs_history[-1]
            days_since_last = (target_date - latest_bcs.measurement_date).days
            
            # BCS趋势特征
            bcs_scores = [record.bcs_score for record in bcs_history]
            
            # 7天趋势
            recent_7d = [record for record in bcs_history 
                        if (target_date - record.measurement_date).days <= 7]
            bcs_trend_7d = 0.0
            if len(recent_7d) >= 2:
                bcs_trend_7d = recent_7d[-1].bcs_score - recent_7d[0].bcs_score
            
            # 14天趋势
            recent_14d = [record for record in bcs_history 
                         if (target_date - record.measurement_date).days <= 14]
            bcs_trend_14d = 0.0
            if len(recent_14d) >= 2:
                bcs_trend_14d = recent_14d[-1].bcs_score - recent_14d[0].bcs_score
            
            # 检测频率特征
            recent_detections = [d for d in detections 
                               if (target_date - d.detection_time).days <= 7]
            detection_frequency = len(recent_detections)
            
            # 平均置信度
            avg_confidence = 0.9  # 默认值
            if recent_detections:
                avg_confidence = np.mean([d.confidence for d in recent_detections])
            
            # 模拟权重变化指标 (实际应用中可以从其他传感器获取)
            weight_change_indicator = np.random.normal(0, 0.1)  # 模拟特征
            
            return {
                'days_since_last_measurement': days_since_last,
                'previous_bcs': latest_bcs.bcs_score,
                'bcs_trend_7d': bcs_trend_7d,
                'bcs_trend_14d': bcs_trend_14d,
                'detection_frequency': detection_frequency,
                'avg_confidence': avg_confidence,
                'weight_change_indicator': weight_change_indicator
            }
            
        except Exception as e:
            log_error('MLEngine', f'特征提取失败 {cattle_id}: {e}')
            return None
    
    def train_model(self, df: pd.DataFrame, model_type: str = 'random_forest') -> Dict[str, Any]:
        """训练模型"""
        log_info('MLEngine', f'开始训练 {model_type} 模型')
        
        try:
            # 准备数据
            X = df[self.feature_columns]
            y = df['target_bcs']
            
            # 数据预处理
            X_scaled = self.scaler.fit_transform(X)
            
            # 分割数据
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # 选择模型
            if model_type == 'random_forest':
                self.model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
            elif model_type == 'gradient_boosting':
                self.model = GradientBoostingRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )
            else:
                self.model = LinearRegression()
            
            # 训练模型
            self.model.fit(X_train, y_train)
            
            # 评估模型
            y_pred_train = self.model.predict(X_train)
            y_pred_test = self.model.predict(X_test)
            
            # 计算指标
            train_mse = mean_squared_error(y_train, y_pred_train)
            test_mse = mean_squared_error(y_test, y_pred_test)
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            train_mae = mean_absolute_error(y_train, y_pred_train)
            test_mae = mean_absolute_error(y_test, y_pred_test)
            
            # 交叉验证
            cv_scores = cross_val_score(self.model, X_scaled, y, cv=5, scoring='r2')
            
            metrics = {
                'model_type': model_type,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'train_mse': train_mse,
                'test_mse': test_mse,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'train_mae': train_mae,
                'test_mae': test_mae,
                'cv_r2_mean': cv_scores.mean(),
                'cv_r2_std': cv_scores.std(),
                'feature_importance': self._get_feature_importance()
            }
            
            log_info('MLEngine', f'模型训练完成 - R²: {test_r2:.3f}, MAE: {test_mae:.3f}')
            
            return metrics
            
        except Exception as e:
            log_error('MLEngine', f'模型训练失败: {e}')
            raise
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性"""
        if hasattr(self.model, 'feature_importances_'):
            importance = dict(zip(self.feature_columns, self.model.feature_importances_))
            return {k: float(v) for k, v in importance.items()}
        elif hasattr(self.model, 'coef_'):
            importance = dict(zip(self.feature_columns, abs(self.model.coef_)))
            return {k: float(v) for k, v in importance.items()}
        else:
            return {}
    
    def save_model(self, metrics: Dict[str, Any]):
        """保存模型"""
        try:
            # 保存模型和缩放器
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            # 保存模型信息到数据库
            session = get_db_session()
            try:
                # 检查是否已存在同名模型
                existing_model = session.query(MLModel).filter(
                    MLModel.model_name == self.model_name
                ).first()
                
                if existing_model:
                    # 更新现有模型
                    existing_model.model_version = str(float(existing_model.model_version) + 0.1)
                    existing_model.training_data_size = metrics['training_samples'] + metrics['test_samples']
                    existing_model.accuracy = metrics['test_r2']
                    existing_model.precision = metrics['test_mae']  # 使用MAE作为精度指标
                    existing_model.updated_at = datetime.utcnow()
                else:
                    # 创建新模型记录
                    ml_model = MLModel(
                        model_name=self.model_name,
                        model_type=metrics['model_type'],
                        model_path=self.model_path,
                        training_data_size=metrics['training_samples'] + metrics['test_samples'],
                        accuracy=metrics['test_r2'],
                        precision=metrics['test_mae'],
                        f1_score=metrics['cv_r2_mean']
                    )
                    session.add(ml_model)
                
                session.commit()
                log_info('MLEngine', f'模型保存成功: {self.model_path}')
                
            finally:
                session.close()
                
        except Exception as e:
            log_error('MLEngine', f'模型保存失败: {e}')
            raise
    
    def load_model(self) -> bool:
        """加载模型"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                log_info('MLEngine', f'模型加载成功: {self.model_path}')
                return True
            else:
                log_warning('MLEngine', f'模型文件不存在: {self.model_path}')
                return False
        except Exception as e:
            log_error('MLEngine', f'模型加载失败: {e}')
            return False
    
    def predict_bcs(self, cattle_id: str) -> Optional[Dict[str, Any]]:
        """预测BCS评分"""
        if self.model is None:
            if not self.load_model():
                return None
        
        try:
            # 获取历史数据
            bcs_history = BCSHistoryDAO.get_cattle_bcs_history(cattle_id, days=30)
            detections = DetectionDAO.get_cattle_detections(cattle_id, days=30)
            
            if not bcs_history:
                return None
            
            # 提取特征
            features = self._extract_features(
                cattle_id, bcs_history, detections, datetime.utcnow()
            )
            
            if not features:
                return None
            
            # 预测
            X = np.array([[features[col] for col in self.feature_columns]])
            X_scaled = self.scaler.transform(X)
            
            predicted_bcs = self.model.predict(X_scaled)[0]
            
            # 计算置信度 (基于历史数据的稳定性)
            confidence = self._calculate_prediction_confidence(bcs_history)
            
            return {
                'cattle_id': cattle_id,
                'predicted_bcs': round(float(predicted_bcs), 2),
                'confidence': round(confidence, 3),
                'features_used': features,
                'prediction_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            log_error('MLEngine', f'BCS预测失败 {cattle_id}: {e}')
            return None
    
    def _calculate_prediction_confidence(self, bcs_history: List) -> float:
        """计算预测置信度"""
        if len(bcs_history) < 3:
            return 0.5
        
        # 基于历史数据的变异性计算置信度
        bcs_scores = [record.bcs_score for record in bcs_history[-10:]]  # 最近10次记录
        std_dev = np.std(bcs_scores)
        
        # 标准差越小，置信度越高
        confidence = max(0.1, min(0.95, 1.0 - (std_dev / 2.0)))
        
        return confidence

class MLEngine:
    """机器学习引擎主类"""
    
    def __init__(self):
        self.bcs_predictor = BCSPredictor()
        self.training_in_progress = False
    
    def train_bcs_model(self, model_type: str = 'random_forest', 
                       days_back: int = 90) -> Dict[str, Any]:
        """训练BCS预测模型"""
        if self.training_in_progress:
            return {'error': '模型训练正在进行中'}
        
        self.training_in_progress = True
        
        try:
            log_info('MLEngine', '开始BCS模型训练流程')
            
            # 生成训练数据
            training_data = self.bcs_predictor.generate_training_data(days_back=days_back)
            
            if len(training_data) < 50:  # 最少需要50条记录
                return {
                    'error': f'训练数据不足: {len(training_data)} 条记录 (最少需要50条)',
                    'suggestion': '请等待系统收集更多数据后再进行训练'
                }
            
            # 训练模型
            metrics = self.bcs_predictor.train_model(training_data, model_type)
            
            # 保存模型
            self.bcs_predictor.save_model(metrics)
            
            log_info('MLEngine', 'BCS模型训练完成')
            
            return {
                'success': True,
                'metrics': metrics,
                'training_data_size': len(training_data),
                'model_path': self.bcs_predictor.model_path
            }
            
        except Exception as e:
            log_error('MLEngine', f'BCS模型训练失败: {e}')
            return {'error': str(e)}
        
        finally:
            self.training_in_progress = False
    
    def predict_cattle_bcs(self, cattle_id: str) -> Optional[Dict[str, Any]]:
        """预测牛只BCS评分"""
        return self.bcs_predictor.predict_bcs(cattle_id)
    
    def batch_predict_bcs(self, cattle_ids: List[str] = None) -> List[Dict[str, Any]]:
        """批量预测BCS评分"""
        if cattle_ids is None:
            # 获取所有牛只
            all_cattle = CattleDAO.get_all_cattle()
            cattle_ids = [cattle.cattle_id for cattle in all_cattle]
        
        predictions = []
        for cattle_id in cattle_ids:
            prediction = self.predict_cattle_bcs(cattle_id)
            if prediction:
                predictions.append(prediction)
        
        return predictions
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        session = get_db_session()
        try:
            model_info = session.query(MLModel).filter(
                MLModel.model_name == self.bcs_predictor.model_name
            ).first()
            
            if model_info:
                return {
                    'model_name': model_info.model_name,
                    'model_type': model_info.model_type,
                    'version': model_info.model_version,
                    'training_data_size': model_info.training_data_size,
                    'accuracy': model_info.accuracy,
                    'precision': model_info.precision,
                    'is_active': model_info.is_active,
                    'created_at': model_info.created_at.isoformat(),
                    'updated_at': model_info.updated_at.isoformat()
                }
            else:
                return {'error': '模型信息不存在'}
                
        finally:
            session.close()
    
    def create_test_data(self, num_records: int = 200):
        """创建测试数据 (仅用于演示，训练完成后会删除)"""
        log_info('MLEngine', f'创建 {num_records} 条测试数据')
        
        try:
            # 获取现有牛只
            all_cattle = CattleDAO.get_all_cattle()
            
            if not all_cattle:
                log_warning('MLEngine', '没有找到牛只数据，无法创建测试数据')
                return
            
            # 为每头牛创建历史BCS记录
            for cattle in all_cattle[:min(20, len(all_cattle))]:  # 最多20头牛
                records_per_cattle = num_records // min(20, len(all_cattle))
                
                current_bcs = cattle.current_bcs
                
                for i in range(records_per_cattle):
                    # 模拟BCS变化
                    days_ago = records_per_cattle - i
                    measurement_date = datetime.utcnow() - timedelta(days=days_ago)
                    
                    # 添加一些随机变化
                    bcs_variation = np.random.normal(0, 0.2)
                    simulated_bcs = max(1.0, min(5.0, current_bcs + bcs_variation))
                    
                    # 添加BCS记录
                    BCSHistoryDAO.add_bcs_record(
                        cattle_id=cattle.cattle_id,
                        bcs_score=simulated_bcs,
                        confidence=0.85 + np.random.random() * 0.1,
                        method='simulated'
                    )
                    
                    # 添加对应的检测记录
                    DetectionDAO.save_detection({
                        'cattle_id': cattle.cattle_id,
                        'camera_id': f'camera_0{np.random.randint(1, 5)}',
                        'detection_time': measurement_date,
                        'confidence': 0.85 + np.random.random() * 0.1,
                        'bcs_score': simulated_bcs,
                        'bbox_x': np.random.random() * 100,
                        'bbox_y': np.random.random() * 100,
                        'bbox_width': 50 + np.random.random() * 50,
                        'bbox_height': 50 + np.random.random() * 50,
                        'identification_method': 'simulated'
                    })
            
            log_info('MLEngine', f'测试数据创建完成: {num_records} 条记录')
            
        except Exception as e:
            log_error('MLEngine', f'创建测试数据失败: {e}')
            raise
    
    def cleanup_test_data(self):
        """清理测试数据"""
        log_info('MLEngine', '清理测试数据')
        
        try:
            session = get_db_session()
            
            # 删除模拟的BCS记录
            deleted_bcs = session.query(BCSHistory).filter(
                BCSHistory.measurement_method == 'simulated'
            ).delete()
            
            # 删除模拟的检测记录
            deleted_detections = session.query(Detection).filter(
                Detection.identification_method == 'simulated'
            ).delete()
            
            session.commit()
            
            log_info('MLEngine', f'测试数据清理完成: {deleted_bcs} BCS记录, {deleted_detections} 检测记录')
            
        except Exception as e:
            log_error('MLEngine', f'清理测试数据失败: {e}')
            session.rollback()
        finally:
            session.close()

# 全局ML引擎实例
ml_engine = MLEngine()

def get_ml_engine() -> MLEngine:
    """获取ML引擎实例"""
    return ml_engine