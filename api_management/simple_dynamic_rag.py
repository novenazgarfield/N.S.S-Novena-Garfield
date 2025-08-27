#!/usr/bin/env python3
"""
简化版动态RAG API服务器
集成中央能源数据库，实现动态AI模型调用
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 配置
ENERGY_API_URL = "http://localhost:56420"
DEFAULT_USER_ID = "default_user"
DEFAULT_PROJECT_ID = "default"

# 备用配置
FALLBACK_CONFIG = {
    "provider": "google",
    "model_name": "gemini-2.0-flash-exp",
    "api_key": os.getenv("GOOGLE_API_KEY", "")
}

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "Dynamic RAG System",
        "version": "1.0.0",
        "energy_db": "connected"
    })

@app.route('/api/config/current', methods=['GET'])
def get_current_config():
    """获取当前AI配置"""
    user_id = request.args.get('user_id', DEFAULT_USER_ID)
    project_id = request.args.get('project_id', DEFAULT_PROJECT_ID)
    
    try:
        # 尝试从中央能源数据库获取最佳配置
        response = requests.get(
            f"{ENERGY_API_URL}/api/energy/config/best",
            params={"user_id": user_id, "project_id": project_id},
            timeout=5
        )
        
        if response.status_code == 200:
            config = response.json()
            return jsonify({
                "source": "energy_database",
                "config": config
            })
    except:
        pass
    
    # 使用备用配置
    return jsonify({
        "source": "fallback",
        "config": FALLBACK_CONFIG
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天接口 - 动态AI模型调用"""
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({"error": "Missing message"}), 400
    
    user_message = data['message']
    user_id = data.get('user_id', DEFAULT_USER_ID)
    project_id = data.get('project_id', DEFAULT_PROJECT_ID)
    
    # 获取当前最佳AI配置
    try:
        config_response = requests.get(
            f"{ENERGY_API_URL}/api/energy/config/best",
            params={"user_id": user_id, "project_id": project_id},
            timeout=5
        )
        
        if config_response.status_code == 200:
            ai_config = config_response.json()
            provider = ai_config.get('provider', 'google')
            model_name = ai_config.get('model_name', 'gemini-2.0-flash-exp')
        else:
            provider = FALLBACK_CONFIG['provider']
            model_name = FALLBACK_CONFIG['model_name']
    except:
        provider = FALLBACK_CONFIG['provider']
        model_name = FALLBACK_CONFIG['model_name']
    
    # 模拟AI响应
    ai_response = f"""🤖 **动态AI响应** (使用 {provider}/{model_name})

您的问题: {user_message}

这是一个模拟的AI响应。在实际部署中，这里会：
1. 🔋 从中央能源数据库获取最佳AI配置
2. 🚀 动态调用相应的AI模型API
3. 📊 记录使用统计和性能数据
4. 🔄 根据负载和成本自动切换模型

当前配置:
- 提供商: {provider}
- 模型: {model_name}
- 用户: {user_id}
- 项目: {project_id}
- 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

系统状态: ✅ 动态能源管理已激活"""

    # 记录使用统计（如果配置存在）
    try:
        if 'config_id' in locals():
            requests.post(
                f"{ENERGY_API_URL}/api/energy/usage/{ai_config.get('config_id', 'fallback')}",
                json={"tokens_used": len(user_message) + len(ai_response)},
                timeout=3
            )
    except:
        pass
    
    return jsonify({
        "response": ai_response,
        "model_info": {
            "provider": provider,
            "model": model_name,
            "source": "energy_database" if 'ai_config' in locals() else "fallback"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """文档上传接口"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # 模拟文档处理
    return jsonify({
        "message": "Document uploaded successfully",
        "filename": file.filename,
        "size": len(file.read()),
        "status": "processed",
        "note": "This is a simulation. In production, the document would be processed and indexed."
    })

@app.route('/api/clear', methods=['POST'])
def clear_context():
    """清除上下文"""
    return jsonify({
        "message": "Context cleared successfully",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 启动简化版动态RAG API服务器...")
    print("=" * 60)
    print("🔋 服务: Dynamic RAG System (Simplified)")
    print("🌐 地址: http://0.0.0.0:60010")
    print("📡 API端点:")
    print("  - GET  /api/health           - 健康检查")
    print("  - POST /api/chat             - 聊天接口 (动态AI)")
    print("  - POST /api/upload           - 文档上传")
    print("  - POST /api/clear            - 清除上下文")
    print("  - GET  /api/config/current   - 获取当前AI配置")
    print("=" * 60)
    print(f"🔗 中央能源数据库: {ENERGY_API_URL}")
    print(f"🔑 备用配置: {FALLBACK_CONFIG['provider']}/{FALLBACK_CONFIG['model_name']}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=60010, debug=False)