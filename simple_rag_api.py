#!/usr/bin/env python3
"""
简化版RAG系统API服务器 - 用于演示集成功能
不依赖复杂的机器学习模型，使用简单的文本匹配
"""
import os
import json
import time
import random
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 简单的内存存储
chat_history = []
uploaded_documents = []
document_content = {}

# 持久化聊天历史存储
import json
from pathlib import Path

CHAT_HISTORY_FILE = Path('chat_history.json')

def save_chat_history_to_file():
    """保存聊天历史到文件"""
    try:
        with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存聊天历史失败: {e}")

def load_chat_history_from_file():
    """从文件加载聊天历史"""
    global chat_history
    try:
        if CHAT_HISTORY_FILE.exists():
            with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                chat_history = json.load(f)
            print(f"📚 已加载聊天历史: {len(chat_history)} 条消息")
    except Exception as e:
        print(f"加载聊天历史失败: {e}")
        chat_history = []

def extract_text_from_file(file_path: Path) -> str:
    """简单的文本提取函数，支持多种格式"""
    try:
        # 支持的文本格式
        text_formats = ['.txt', '.md', '.markdown', '.py', '.js', '.html', '.css', '.json', '.xml', '.yml', '.yaml']
        
        if file_path.suffix.lower() in text_formats:
            content = file_path.read_text(encoding='utf-8')
            
            # 如果是Markdown文件，添加格式说明
            if file_path.suffix.lower() in ['.md', '.markdown']:
                return f"Markdown文档: {file_path.name}\n\n{content}"
            else:
                return content
        else:
            # 对于其他文件类型，返回文件信息
            return f"文件名: {file_path.name}\n文件大小: {file_path.stat().st_size} 字节\n文件类型: {file_path.suffix}\n注意: 此文件类型可能需要专门的解析器来提取内容。"
    except Exception as e:
        return f"无法读取文件 {file_path.name}: {str(e)}"

def simple_search(query: str, documents: List[str]) -> List[str]:
    """简单的文本搜索函数"""
    if not documents:
        return []
    
    # 处理中文和英文关键词
    query_lower = query.lower()
    # 分割中文和英文词汇
    import re
    words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', query_lower)
    
    results = []
    
    for doc in documents:
        doc_lower = doc.lower()
        score = 0
        
        # 检查整个查询字符串
        if query_lower in doc_lower:
            score += 10
        
        # 检查单个词汇
        for word in words:
            if word in doc_lower:
                score += doc_lower.count(word) * 2
        
        # 检查部分匹配
        for word in words:
            if len(word) > 1:
                for i in range(len(word) - 1):
                    partial = word[i:i+2]
                    if partial in doc_lower:
                        score += 1
        
        if score > 0:
            results.append((doc, score))
    
    # 按分数排序并返回前3个结果
    results.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in results[:3]]

def generate_response(query: str, context: List[str]) -> str:
    """生成简单的回答"""
    if not context:
        responses = [
            "抱歉，我没有找到相关的信息来回答您的问题。请尝试上传相关文档或重新表述问题。",
            "我需要更多的文档信息才能回答您的问题。请上传相关文档。",
            "目前我的知识库中没有相关信息，请上传文档后再提问。"
        ]
        return random.choice(responses)
    
    # 简单的回答生成
    if "什么" in query or "是什么" in query:
        return f"根据文档内容，{query}的相关信息如下：\n\n" + "\n\n".join(context[:2])
    elif "如何" in query or "怎么" in query:
        return f"关于{query}，根据文档内容，我找到了以下相关信息：\n\n" + "\n\n".join(context[:2])
    elif "为什么" in query:
        return f"关于您问的{query}，文档中提到：\n\n" + "\n\n".join(context[:2])
    else:
        return f"根据文档内容，关于您的问题，我找到了以下相关信息：\n\n" + "\n\n".join(context[:2])

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "rag_system_ready": True,
        "documents_count": len(uploaded_documents),
        "chat_history_count": len(chat_history)
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天接口"""
    try:
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
        
        # 记录用户消息
        chat_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "task_name": task_name
        })
        
        # 搜索相关文档
        all_content = list(document_content.values())
        relevant_docs = simple_search(message, all_content)
        
        # 生成回答
        answer = generate_response(message, relevant_docs)
        
        # 记录助手回答
        chat_history.append({
            "role": "assistant",
            "content": answer,
            "timestamp": datetime.now().isoformat(),
            "task_name": task_name
        })
        
        # 保存聊天历史到文件
        save_chat_history_to_file()
        
        # 模拟处理时间
        time.sleep(0.5)
        
        return jsonify({
            "success": True,
            "response": answer,
            "timestamp": datetime.now().isoformat(),
            "documents_used": len(relevant_docs)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"处理消息时出错: {str(e)}"
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_documents():
    """文档上传接口"""
    try:
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
        
        # 创建临时目录
        temp_dir = Path("/tmp/rag_uploads")
        temp_dir.mkdir(exist_ok=True)
        
        processed_count = 0
        for file in files:
            if file.filename:
                # 保存文件
                file_path = temp_dir / file.filename
                file.save(str(file_path))
                
                # 提取文本内容
                content = extract_text_from_file(file_path)
                
                # 存储文档信息
                doc_id = f"{file.filename}_{int(time.time())}"
                uploaded_documents.append({
                    "id": doc_id,
                    "filename": file.filename,
                    "upload_time": datetime.now().isoformat(),
                    "size": len(content)
                })
                document_content[doc_id] = content
                processed_count += 1
                
                # 清理临时文件
                try:
                    file_path.unlink()
                except:
                    pass
        
        return jsonify({
            "success": True,
            "message": f"成功处理 {processed_count} 个文档",
            "processed_count": processed_count,
            "total_documents": len(uploaded_documents)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"上传文档时出错: {str(e)}"
        }), 500

@app.route('/api/history', methods=['GET'])
def get_chat_history():
    """获取聊天历史"""
    try:
        task_name = request.args.get('task_name', 'nexus_chat')
        
        # 过滤指定任务的聊天记录
        filtered_history = [
            msg for msg in chat_history 
            if msg.get('task_name', 'default') == task_name
        ]
        
        return jsonify({
            "success": True,
            "history": filtered_history,
            "total_messages": len(filtered_history),
            "task_name": task_name
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取聊天历史失败: {str(e)}"
        }), 500

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    """清空聊天记录"""
    try:
        data = request.get_json()
        task_name = data.get('task_name', 'default') if data else 'default'
        
        # 清除指定任务的聊天记录
        global chat_history
        chat_history = [
            msg for msg in chat_history 
            if msg.get('task_name') != task_name
        ]
        
        # 保存更新后的聊天历史到文件
        save_chat_history_to_file()
        
        return jsonify({
            "success": True,
            "message": "聊天记录已清空"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"清空聊天记录时出错: {str(e)}"
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_system_stats():
    """获取系统统计信息"""
    try:
        return jsonify({
            "success": True,
            "stats": {
                "total_documents": len(uploaded_documents),
                "total_chat_messages": len(chat_history),
                "document_list": [doc["filename"] for doc in uploaded_documents],
                "system_type": "简化版RAG系统",
                "features": ["文本搜索", "文档上传", "聊天记录"]
            }
        })
        
    except Exception as e:
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
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='RAG API服务器')
    parser.add_argument('--host', default='0.0.0.0', help='绑定主机地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='端口号 (默认: 5000)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    args = parser.parse_args()
    
    print("🚀 启动简化版RAG系统API服务器...")
    print("✅ 这是一个演示版本，使用简单的文本匹配算法")
    
    # 加载聊天历史
    load_chat_history_from_file()
    
    print("🌐 API服务器启动中...")
    print("📡 API端点:")
    print("  - POST /api/chat - 聊天接口")
    print("  - POST /api/upload - 文档上传")
    print("  - GET /api/history - 获取聊天历史")
    print("  - POST /api/clear - 清空聊天记录")
    print("  - GET /api/stats - 系统统计")
    print("  - GET /api/health - 健康检查")
    print(f"🎯 访问地址: http://{args.host}:{args.port}")
    print(f"🔧 调试模式: {'启用' if args.debug else '禁用'}")
    
    # 启动Flask应用
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True
    )