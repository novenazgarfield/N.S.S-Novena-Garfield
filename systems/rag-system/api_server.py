"""
RAG系统API服务器 - 为前端提供API接口
"""
import sys
from pathlib import Path
import os
import json
from typing import Dict, Any, List
import traceback
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

# 设置环境变量
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局RAG系统实例
rag_system = None

def init_rag_system():
    """初始化RAG系统"""
    global rag_system
    try:
        from core.rag_system import RAGSystem
        rag_system = RAGSystem()
        
        # 尝试加载本地文献库
        rag_system.load_local_library()
        
        logger.info("RAG系统初始化成功")
        return True
    except Exception as e:
        logger.error(f"RAG系统初始化失败: {e}")
        logger.error(traceback.format_exc())
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "rag_system_ready": rag_system is not None
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天接口"""
    try:
        if not rag_system:
            return jsonify({
                "success": False,
                "error": "RAG系统未初始化"
            }), 500
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "缺少消息内容"
            }), 400
        
        message = data['message'].strip()
        task_name = data.get('task_name', 'default')
        
        if not message:
            return jsonify({
                "success": False,
                "error": "消息不能为空"
            }), 400
        
        # 调用RAG系统处理问题
        answer = rag_system.search_and_answer(message, task_name)
        
        return jsonify({
            "success": True,
            "response": answer,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"聊天处理失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": f"处理消息时出错: {str(e)}"
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_documents():
    """文档上传接口"""
    try:
        if not rag_system:
            return jsonify({
                "success": False,
                "error": "RAG系统未初始化"
            }), 500
        
        if 'files' not in request.files:
            return jsonify({
                "success": False,
                "error": "没有上传文件"
            }), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({
                "success": False,
                "error": "没有选择文件"
            }), 400
        
        # 保存上传的文件到临时目录
        from config import StorageConfig
        temp_dir = StorageConfig.RAW_DATA_DIR / "temp_uploads"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        for file in files:
            if file.filename:
                # 生成安全的文件名
                filename = file.filename
                file_path = temp_dir / filename
                file.save(str(file_path))
                saved_files.append(file_path)
        
        if not saved_files:
            return jsonify({
                "success": False,
                "error": "没有成功保存的文件"
            }), 400
        
        # 处理文档
        result = rag_system.add_documents(saved_files)
        
        # 清理临时文件
        for file_path in saved_files:
            try:
                file_path.unlink()
            except:
                pass
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"文档上传失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": f"上传文档时出错: {str(e)}"
        }), 500

@app.route('/api/history', methods=['GET'])
def get_chat_history():
    """获取聊天历史"""
    try:
        if not rag_system:
            return jsonify({
                "success": False,
                "error": "RAG系统未初始化"
            }), 500
        
        task_name = request.args.get('task_name', 'default')
        limit = int(request.args.get('limit', 20))
        
        history = rag_system.get_chat_history(task_name, limit)
        
        return jsonify({
            "success": True,
            "history": history
        })
        
    except Exception as e:
        logger.error(f"获取聊天历史失败: {e}")
        return jsonify({
            "success": False,
            "error": f"获取聊天历史时出错: {str(e)}"
        }), 500

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    """清空聊天记录"""
    try:
        if not rag_system:
            return jsonify({
                "success": False,
                "error": "RAG系统未初始化"
            }), 500
        
        data = request.get_json()
        task_name = data.get('task_name', 'default') if data else 'default'
        
        rag_system.clear_task_data(task_name)
        
        return jsonify({
            "success": True,
            "message": "聊天记录已清空"
        })
        
    except Exception as e:
        logger.error(f"清空聊天记录失败: {e}")
        return jsonify({
            "success": False,
            "error": f"清空聊天记录时出错: {str(e)}"
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_system_stats():
    """获取系统统计信息"""
    try:
        if not rag_system:
            return jsonify({
                "success": False,
                "error": "RAG系统未初始化"
            }), 500
        
        stats = rag_system.get_system_stats()
        
        return jsonify({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"获取系统统计失败: {e}")
        return jsonify({
            "success": False,
            "error": f"获取系统统计时出错: {str(e)}"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "API端点不存在"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "服务器内部错误"
    }), 500

if __name__ == '__main__':
    print("🚀 启动RAG系统API服务器...")
    
    # 初始化RAG系统
    if init_rag_system():
        print("✅ RAG系统初始化成功")
        print("🌐 API服务器启动中...")
        print("📡 API端点:")
        print("  - POST /api/chat - 聊天接口")
        print("  - POST /api/upload - 文档上传")
        print("  - GET /api/history - 获取聊天历史")
        print("  - POST /api/clear - 清空聊天记录")
        print("  - GET /api/stats - 系统统计")
        print("  - GET /api/health - 健康检查")
        
        # 启动Flask应用
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
    else:
        print("❌ RAG系统初始化失败，无法启动API服务器")
        sys.exit(1)