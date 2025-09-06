#!/usr/bin/env python3
"""
清理机器学习模型，重置为干净状态
"""

import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

def create_clean_model():
    """创建干净的机器学习模型"""
    
    # 创建干净的随机森林模型
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    
    # 创建标准化器
    scaler = StandardScaler()
    
    # 使用基础的特征数据进行初始化训练
    # 这些是标准的牛只体况评分特征
    base_features = np.array([
        [0.5, 0.6, 0.7, 0.8, 0.9],  # 标准体型特征
        [0.6, 0.7, 0.8, 0.9, 1.0],  # 健康体型特征
        [0.4, 0.5, 0.6, 0.7, 0.8],  # 偏瘦体型特征
        [0.7, 0.8, 0.9, 1.0, 1.1],  # 偏胖体型特征
    ])
    
    base_scores = np.array([3.0, 3.5, 2.5, 4.0])  # 对应的BCS评分
    
    # 标准化特征
    scaler.fit(base_features)
    scaled_features = scaler.transform(base_features)
    
    # 训练模型
    model.fit(scaled_features, base_scores)
    
    return model, scaler

def save_clean_model():
    """保存干净的模型"""
    
    # 确保模型目录存在
    os.makedirs('models', exist_ok=True)
    
    # 创建干净的模型
    model, scaler = create_clean_model()
    
    # 保存模型
    with open('models/bcs_predictor_clean.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    # 保存标准化器
    with open('models/bcs_predictor_clean_scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    print("✅ 干净的机器学习模型已创建并保存")
    print("📁 模型文件: models/bcs_predictor_clean.pkl")
    print("📁 标准化器: models/bcs_predictor_clean_scaler.pkl")

if __name__ == "__main__":
    save_clean_model()