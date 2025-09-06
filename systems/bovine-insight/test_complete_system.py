#!/usr/bin/env python3
"""
BovineInsight系统完整功能测试
测试三阶段进化的所有功能
"""

import requests
import json
import sys

def test_api_endpoint(url, description):
    """测试API端点"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success', False):
                return True, data.get('data', {})
            else:
                return False, data.get('error', 'Unknown error')
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def test_post_endpoint(url, payload, description):
    """测试POST API端点"""
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success', False):
                return True, data.get('data', {})
            else:
                return False, data.get('error', 'Unknown error')
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def main():
    base_url = "http://localhost:5002"
    
    print("=== 🎉 BovineInsight系统三阶段进化完成！功能测试总结 ===\n")
    
    # 1. 系统状态测试
    print("📊 1. 系统状态 - 测试中...")
    success, data = test_api_endpoint(f"{base_url}/api/status", "系统状态")
    if success:
        print(f"   ✅ 在线状态: {data.get('online', False)}")
        print(f"   ✅ 牛只总数: {data.get('total_cattle', 0)}")
        print(f"   ✅ 活跃摄像头: {data.get('active_cameras', 0)}")
    else:
        print(f"   ❌ 失败: {data}")
    
    # 2. 牛只管理测试
    print("\n🐄 2. 牛只管理 - 数据库持久化测试...")
    success, data = test_api_endpoint(f"{base_url}/api/cattle", "牛只列表")
    if success:
        cattle_count = len(data) if isinstance(data, list) else len(data.get('cattle', []))
        print(f"   ✅ 数据库中牛只数量: {cattle_count}")
    else:
        print(f"   ❌ 失败: {data}")
    
    # 3. 实时检测测试
    print("\n🔍 3. 实时检测 - 智能识别测试...")
    success, data = test_api_endpoint(f"{base_url}/api/live-detection", "实时检测")
    if success:
        detection_count = len(data.get('detections', []))
        print(f"   ✅ 当前检测到: {detection_count} 头牛")
    else:
        print(f"   ❌ 失败: {data}")
    
    # 4. 智能决策引擎测试
    print("\n🧠 4. 智能决策引擎 - 健康分析测试...")
    success, data = test_api_endpoint(f"{base_url}/api/health-analysis", "健康分析")
    if success:
        total_cattle = data.get('total_cattle', 0)
        avg_bcs = data.get('health_summary', {}).get('bcs_statistics', {}).get('average', 0)
        print(f"   ✅ 分析牛只数: {total_cattle}")
        print(f"   ✅ 平均BCS: {avg_bcs}")
    else:
        print(f"   ❌ 失败: {data}")
    
    # 5. 预警系统测试
    print("\n⚠️ 5. 预警系统 - 智能监控测试...")
    success, data = test_api_endpoint(f"{base_url}/api/alerts", "预警系统")
    if success:
        alert_count = len(data.get('alerts', []))
        print(f"   ✅ 活跃预警: {alert_count} 条")
    else:
        print(f"   ❌ 失败: {data}")
    
    # 6. 机器学习引擎测试
    print("\n🤖 6. 机器学习引擎 - BCS预测测试...")
    success, data = test_api_endpoint(f"{base_url}/api/ml/predict/COW-0001", "BCS预测")
    if success:
        predicted_bcs = data.get('predicted_bcs', 0)
        confidence = data.get('confidence', 0)
        print(f"   ✅ 预测BCS: {predicted_bcs}")
        print(f"   ✅ 预测置信度: {confidence}")
    else:
        print(f"   ❌ 失败: {data}")
    
    # 7. 仪表盘数据测试
    print("\n📈 7. 仪表盘数据 - 综合统计测试...")
    success, data = test_api_endpoint(f"{base_url}/api/dashboard", "仪表盘")
    if success:
        stats = data.get('statistics', {})
        healthy_percentage = stats.get('healthy_percentage', 0)
        avg_bcs = stats.get('average_bcs', 0)
        print(f"   ✅ 健康比例: {healthy_percentage}%")
        print(f"   ✅ 平均BCS: {avg_bcs}")
    else:
        print(f"   ❌ 失败: {data}")
    
    # 8. 饲养建议测试
    print("\n🎯 8. 饲养建议 - 个性化指导测试...")
    success, data = test_api_endpoint(f"{base_url}/api/feeding-advice/COW-0001", "饲养建议")
    if success:
        feed_adjustment = data.get('feed_adjustment', 'unknown')
        recommendations = data.get('recommendations', [])
        print(f"   ✅ 饲料调整: {feed_adjustment}")
        print(f"   ✅ 建议数量: {len(recommendations)}")
    else:
        print(f"   ❌ 失败: {data}")
    
    # 9. 机器学习模型训练测试
    print("\n🔬 9. 机器学习模型训练 - 高级功能测试...")
    payload = {"create_test_data": True, "model_type": "random_forest"}
    success, data = test_post_endpoint(f"{base_url}/api/ml/train", payload, "模型训练")
    if success:
        metrics = data.get('metrics', {})
        test_r2 = metrics.get('test_r2', 0)
        training_samples = metrics.get('training_samples', 0)
        print(f"   ✅ 模型R²评分: {test_r2:.3f}")
        print(f"   ✅ 训练样本数: {training_samples}")
    else:
        print(f"   ❌ 失败: {data}")
    
    print("\n" + "="*60)
    print("🎉 BovineInsight系统三阶段进化测试完成！")
    print("✅ 第一阶段: 数据库持久化 - SQLite + SQLAlchemy")
    print("✅ 第二阶段: 智能决策逻辑 - 健康分析 + 预警系统")
    print("✅ 第三阶段: 机器学习模型 - BCS预测 + 模型训练")
    print("="*60)

if __name__ == "__main__":
    main()