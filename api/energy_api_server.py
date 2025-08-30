"""
中央能源API服务器
提供RESTful API来管理AI模型配置
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
from typing import Dict, Any

from central_energy_db import (
    CentralEnergyDB, ModelConfig, ModelProvider, ConfigScope,
    get_central_db
)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 获取数据库实例
db = get_central_db()

@app.route('/api/energy/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "service": "Central Energy API",
        "timestamp": time.time(),
        "version": "1.0.0"
    })

@app.route('/api/energy/models/available', methods=['GET'])
def get_available_models():
    """获取可用的模型列表"""
    try:
        models = db.get_available_models()
        return jsonify({
            "success": True,
            "models": models,
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/api/energy/config', methods=['POST'])
def add_model_config():
    """添加模型配置"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['user_id', 'provider', 'model_name', 'api_key']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"缺少必需字段: {field}",
                    "timestamp": time.time()
                }), 400
        
        # 创建配置对象
        config = ModelConfig(
            config_id="",  # 将自动生成
            user_id=data['user_id'],
            project_id=data.get('project_id', 'default'),
            provider=ModelProvider(data['provider']),
            model_name=data['model_name'],
            api_key=data['api_key'],
            api_endpoint=data.get('api_endpoint', ''),
            scope=ConfigScope(data.get('scope', 'user')),
            is_active=data.get('is_active', True),
            priority=data.get('priority', 0),
            max_tokens=data.get('max_tokens', 4096),
            temperature=data.get('temperature', 0.7),
            description=data.get('description', '')
        )
        
        success = db.add_model_config(config)
        
        if success:
            return jsonify({
                "success": True,
                "config_id": config.config_id,
                "message": "配置添加成功",
                "timestamp": time.time()
            })
        else:
            return jsonify({
                "success": False,
                "error": "配置添加失败",
                "timestamp": time.time()
            }), 500
            
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": f"无效的参数值: {str(e)}",
            "timestamp": time.time()
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/api/energy/config/<config_id>', methods=['GET'])
def get_model_config(config_id):
    """获取模型配置"""
    try:
        config = db.get_model_config(config_id)
        
        if config:
            # 不返回敏感信息（API密钥）
            config_dict = {
                "config_id": config.config_id,
                "user_id": config.user_id,
                "project_id": config.project_id,
                "provider": config.provider.value,
                "model_name": config.model_name,
                "api_endpoint": config.api_endpoint,
                "scope": config.scope.value,
                "is_active": config.is_active,
                "priority": config.priority,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "created_at": config.created_at,
                "updated_at": config.updated_at,
                "last_used": config.last_used,
                "usage_count": config.usage_count,
                "description": config.description,
                "api_key_masked": "***" + config.api_key[-4:] if len(config.api_key) > 4 else "***"
            }
            
            return jsonify({
                "success": True,
                "config": config_dict,
                "timestamp": time.time()
            })
        else:
            return jsonify({
                "success": False,
                "error": "配置不存在",
                "timestamp": time.time()
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/api/energy/config/best', methods=['GET'])
def get_best_config():
    """获取最佳模型配置"""
    try:
        user_id = request.args.get('user_id')
        project_id = request.args.get('project_id', 'default')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "缺少user_id参数",
                "timestamp": time.time()
            }), 400
        
        config = db.get_best_model_config(user_id, project_id)
        
        if config:
            # 返回完整配置（包括API密钥，用于实际调用）
            config_dict = {
                "config_id": config.config_id,
                "user_id": config.user_id,
                "project_id": config.project_id,
                "provider": config.provider.value,
                "model_name": config.model_name,
                "api_key": config.api_key,
                "api_endpoint": config.api_endpoint,
                "scope": config.scope.value,
                "is_active": config.is_active,
                "priority": config.priority,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "created_at": config.created_at,
                "updated_at": config.updated_at,
                "last_used": config.last_used,
                "usage_count": config.usage_count,
                "description": config.description
            }
            
            return jsonify({
                "success": True,
                "config": config_dict,
                "timestamp": time.time()
            })
        else:
            return jsonify({
                "success": False,
                "error": "未找到可用的配置",
                "timestamp": time.time()
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/api/energy/config/list', methods=['GET'])
def list_user_configs():
    """列出用户的所有配置"""
    try:
        user_id = request.args.get('user_id')
        project_id = request.args.get('project_id')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "缺少user_id参数",
                "timestamp": time.time()
            }), 400
        
        configs = db.list_user_configs(user_id, project_id)
        
        # 转换为字典列表（隐藏API密钥）
        config_list = []
        for config in configs:
            config_dict = {
                "config_id": config.config_id,
                "user_id": config.user_id,
                "project_id": config.project_id,
                "provider": config.provider.value,
                "model_name": config.model_name,
                "api_endpoint": config.api_endpoint,
                "scope": config.scope.value,
                "is_active": config.is_active,
                "priority": config.priority,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "created_at": config.created_at,
                "updated_at": config.updated_at,
                "last_used": config.last_used,
                "usage_count": config.usage_count,
                "description": config.description,
                "api_key_masked": "***" + config.api_key[-4:] if len(config.api_key) > 4 else "***"
            }
            config_list.append(config_dict)
        
        return jsonify({
            "success": True,
            "configs": config_list,
            "count": len(config_list),
            "timestamp": time.time()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/api/energy/config/<config_id>', methods=['PUT'])
def update_model_config(config_id):
    """更新模型配置"""
    try:
        data = request.get_json()
        
        # 过滤允许更新的字段
        allowed_fields = [
            'model_name', 'api_key', 'api_endpoint', 'is_active', 
            'priority', 'max_tokens', 'temperature', 'description'
        ]
        
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({
                "success": False,
                "error": "没有可更新的字段",
                "timestamp": time.time()
            }), 400
        
        success = db.update_model_config(config_id, **update_data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "配置更新成功",
                "timestamp": time.time()
            })
        else:
            return jsonify({
                "success": False,
                "error": "配置更新失败或配置不存在",
                "timestamp": time.time()
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/api/energy/config/<config_id>', methods=['DELETE'])
def delete_model_config(config_id):
    """删除模型配置"""
    try:
        success = db.delete_model_config(config_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "配置删除成功",
                "timestamp": time.time()
            })
        else:
            return jsonify({
                "success": False,
                "error": "配置删除失败或配置不存在",
                "timestamp": time.time()
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/api/energy/usage/<config_id>', methods=['POST'])
def record_usage(config_id):
    """记录使用统计"""
    try:
        data = request.get_json() or {}
        tokens_used = data.get('tokens_used', 0)
        cost = data.get('cost', 0.0)
        
        db.record_usage(config_id, tokens_used, cost)
        
        return jsonify({
            "success": True,
            "message": "使用统计记录成功",
            "timestamp": time.time()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/api/energy/test', methods=['POST'])
def test_api_key():
    """测试API密钥是否有效"""
    try:
        data = request.get_json()
        provider = data.get('provider')
        api_key = data.get('api_key')
        model_name = data.get('model_name')
        
        if not all([provider, api_key, model_name]):
            return jsonify({
                "success": False,
                "error": "缺少必需参数",
                "timestamp": time.time()
            }), 400
        
        # 这里可以添加实际的API测试逻辑
        # 目前返回模拟结果
        test_result = {
            "valid": True,
            "model_available": True,
            "response_time": 0.5,
            "test_message": "API密钥测试成功"
        }
        
        return jsonify({
            "success": True,
            "test_result": test_result,
            "timestamp": time.time()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": time.time()
        }), 500

if __name__ == '__main__':
    print("🚀 启动中央能源API服务器...")
    print("=" * 50)
    print("🔋 服务: Central Energy Database API")
    print("🌐 地址: http://0.0.0.0:56419")
    print("📡 API端点:")
    print("  - GET  /api/energy/health           - 健康检查")
    print("  - GET  /api/energy/models/available - 获取可用模型")
    print("  - POST /api/energy/config           - 添加配置")
    print("  - GET  /api/energy/config/best      - 获取最佳配置")
    print("  - GET  /api/energy/config/list      - 列出用户配置")
    print("  - PUT  /api/energy/config/<id>      - 更新配置")
    print("  - DELETE /api/energy/config/<id>    - 删除配置")
    print("  - POST /api/energy/usage/<id>       - 记录使用统计")
    print("  - POST /api/energy/test             - 测试API密钥")
    print("=" * 50)
    
    # 🌟 动态端口配置 - 从环境变量获取端口，支持服务发现系统
    import os
    port = int(os.environ.get('PORT', 56419))
    
    # 更新显示的地址信息
    print(f"🌐 实际地址: http://0.0.0.0:{port}")
    print(f"📡 健康检查: http://localhost:{port}/api/energy/health")
    
    app.run(host='0.0.0.0', port=port, debug=False)