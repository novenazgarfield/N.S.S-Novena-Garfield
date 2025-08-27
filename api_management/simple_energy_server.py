#!/usr/bin/env python3
"""
简化版中央能源API服务器
用于测试基本功能
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'api_management'))

app = Flask(__name__)
CORS(app)

# 内存存储配置（简化版）
configs_storage = []

@app.route('/api/energy/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "Central Energy Database API",
        "version": "1.0.0"
    })

@app.route('/api/energy/models/available', methods=['GET'])
def get_available_models():
    """获取可用模型"""
    models = {
        "google": {
            "gemini-2.0-flash-exp": {"context_length": 1000000, "cost_per_1k": 0.001},
            "gemini-1.5-pro": {"context_length": 2000000, "cost_per_1k": 0.002}
        },
        "openai": {
            "gpt-4": {"context_length": 8192, "cost_per_1k": 0.03},
            "gpt-3.5-turbo": {"context_length": 4096, "cost_per_1k": 0.002}
        }
    }
    return jsonify(models)

@app.route('/api/energy/config', methods=['POST'])
def add_config():
    """添加配置"""
    data = request.get_json()
    
    # 简单验证
    required_fields = ['user_id', 'project_id', 'provider', 'model_name', 'api_key']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    
    # 生成配置ID
    config_id = f"config_{data['user_id']}_{data['project_id']}_{len(configs_storage) + 1}"
    
    # 保存配置到内存
    config = {
        "config_id": config_id,
        "user_id": data['user_id'],
        "project_id": data['project_id'],
        "provider": data['provider'],
        "model_name": data['model_name'],
        "api_key": data['api_key'][:8] + "..." + data['api_key'][-4:],  # 隐藏API密钥
        "scope": data.get('scope', 'project'),
        "priority": data.get('priority', 1),
        "max_tokens": data.get('max_tokens', 4096),
        "temperature": data.get('temperature', 0.7),
        "description": data.get('description', ''),
        "created_at": "2025-08-27T09:35:00Z",
        "usage_count": 0,
        "last_used": None
    }
    
    configs_storage.append(config)
    
    return jsonify({
        "message": "Configuration added successfully",
        "config_id": config_id,
        "provider": data['provider'],
        "model_name": data['model_name']
    }), 201

@app.route('/api/energy/config/list', methods=['GET'])
def list_user_configs():
    """列出用户配置"""
    user_id = request.args.get('user_id', 'default_user')
    project_id = request.args.get('project_id', 'default')
    
    # 过滤用户的配置
    user_configs = [
        config for config in configs_storage 
        if config['user_id'] == user_id and config['project_id'] == project_id
    ]
    
    return jsonify({
        "success": True,
        "configs": user_configs,
        "total": len(user_configs)
    })

@app.route('/api/energy/config/best', methods=['GET'])
def get_best_config():
    """获取最佳配置"""
    user_id = request.args.get('user_id', 'default')
    project_id = request.args.get('project_id', 'default')
    
    # 查找用户的配置
    user_configs = [
        config for config in configs_storage 
        if config['user_id'] == user_id and config['project_id'] == project_id
    ]
    
    if user_configs:
        # 返回优先级最高的配置
        best_config = max(user_configs, key=lambda x: x['priority'])
        return jsonify(best_config)
    
    # 模拟返回默认配置
    return jsonify({
        "config_id": f"best_{user_id}_{project_id}",
        "provider": "google",
        "model_name": "gemini-2.0-flash-exp",
        "scope": "project",
        "priority": 1,
        "usage_count": 0,
        "last_used": None
    })

if __name__ == '__main__':
    print("🚀 启动简化版中央能源API服务器...")
    print("🌐 地址: http://0.0.0.0:56420")
    print("📡 API端点:")
    print("  - GET  /api/energy/health           - 健康检查")
    print("  - GET  /api/energy/models/available - 获取可用模型")
    print("  - POST /api/energy/config           - 添加配置")
    print("  - GET  /api/energy/config/list      - 列出用户配置")
    print("  - GET  /api/energy/config/best      - 获取最佳配置")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=56420, debug=False)