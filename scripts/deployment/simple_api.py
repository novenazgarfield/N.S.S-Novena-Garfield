#!/usr/bin/env python3
"""
简化版RAG API服务器
基础功能版本，用于演示和测试
"""

import os
import json
import logging
import hashlib
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional
import traceback
import re
from pathlib import Path

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 存储配置
UPLOAD_FOLDER = '/tmp/rag_documents'
VECTOR_DB_PATH = '/tmp/rag_vectors'

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

# 简单的文档存储
documents_store = {}
chat_history = []

class SimpleRAGSystem:
    def __init__(self):
        self.documents = {}
        self.chat_history = []
    
    def add_document(self, filename: str, content: str) -> str:
        """添加文档到系统"""
        doc_id = hashlib.md5(f"{filename}_{content[:100]}".encode()).hexdigest()
        self.documents[doc_id] = {
            'filename': filename,
            'content': content,
            'created_at': datetime.now().isoformat(),
            'chunks': self._chunk_text(content)
        }
        logger.info(f"添加文档: {filename} (ID: {doc_id})")
        return doc_id
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """将文本分块"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def search_documents(self, query: str, top_k: int = 3) -> List[Dict]:
        """简单的文档搜索（基于关键词匹配）"""
        results = []
        query_lower = query.lower()
        query_words = [word.strip() for word in query_lower.split() if len(word.strip()) > 1]
        
        for doc_id, doc in self.documents.items():
            score = 0
            matching_chunks = []
            
            # 搜索整个文档内容
            content_lower = doc['content'].lower()
            
            # 检查查询词是否在文档中
            for word in query_words:
                if word in content_lower:
                    score += content_lower.count(word) * 2  # 提高权重
            
            # 搜索分块内容
            for chunk in doc['chunks']:
                chunk_lower = chunk.lower()
                chunk_score = 0
                
                for word in query_words:
                    if word in chunk_lower:
                        chunk_score += chunk_lower.count(word)
                
                if chunk_score > 0:
                    score += chunk_score
                    if chunk not in matching_chunks:
                        matching_chunks.append(chunk)
            
            # 如果没有精确匹配，尝试模糊匹配
            if score == 0:
                for word in query_words:
                    for chunk in doc['chunks']:
                        chunk_lower = chunk.lower()
                        # 检查是否包含相关词汇
                        if any(related in chunk_lower for related in [word[:3], word[:4]] if len(word) > 3):
                            score += 1
                            if chunk not in matching_chunks:
                                matching_chunks.append(chunk)
            
            if score > 0:
                results.append({
                    'doc_id': doc_id,
                    'filename': doc['filename'],
                    'score': score,
                    'matching_chunks': matching_chunks[:3],  # 最多返回3个匹配块
                    'created_at': doc['created_at']
                })
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def generate_answer(self, query: str, context_docs: List[Dict]) -> str:
        """生成答案（简化版本）"""
        if not context_docs:
            return "抱歉，我在文档中没有找到相关信息来回答您的问题。请尝试上传相关文档或重新表述您的问题。"
        
        # 构建上下文
        context_text = ""
        for doc in context_docs:
            context_text += f"\n来自文档 '{doc['filename']}':\n"
            for chunk in doc['matching_chunks']:
                context_text += f"- {chunk}\n"
        
        # 简单的答案生成
        answer = f"基于您上传的文档，我找到了以下相关信息：\n{context_text}\n"
        answer += f"针对您的问题「{query}」，根据文档内容，这些信息可能对您有帮助。"
        
        return answer

# 创建RAG系统实例
rag_system = SimpleRAGSystem()

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'documents_count': len(rag_system.documents),
        'service': 'Simple RAG API'
    })

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """上传文档端点"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件被上传'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 读取文件内容
        content = file.read().decode('utf-8', errors='ignore')
        
        if not content.strip():
            return jsonify({'error': '文件内容为空'}), 400
        
        # 添加到RAG系统
        doc_id = rag_system.add_document(file.filename, content)
        
        # 保存文件到本地
        file_path = os.path.join(UPLOAD_FOLDER, f"{doc_id}_{file.filename}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            'success': True,
            'doc_id': doc_id,
            'filename': file.filename,
            'content_length': len(content),
            'message': f'文档 "{file.filename}" 上传成功'
        })
        
    except Exception as e:
        logger.error(f"文档上传失败: {e}")
        return jsonify({'error': f'文档上传失败: {str(e)}'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天端点"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': '缺少消息内容'}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({'error': '消息不能为空'}), 400
        
        # 搜索相关文档
        relevant_docs = rag_system.search_documents(user_message)
        
        # 生成答案
        answer = rag_system.generate_answer(user_message, relevant_docs)
        
        # 记录对话历史
        chat_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'assistant_response': answer,
            'relevant_docs': [doc['filename'] for doc in relevant_docs],
            'doc_count': len(relevant_docs)
        }
        rag_system.chat_history.append(chat_entry)
        
        return jsonify({
            'success': True,
            'response': answer,
            'relevant_documents': relevant_docs,
            'timestamp': chat_entry['timestamp']
        })
        
    except Exception as e:
        logger.error(f"聊天处理失败: {e}")
        return jsonify({'error': f'聊天处理失败: {str(e)}'}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """列出所有文档"""
    try:
        docs = []
        for doc_id, doc in rag_system.documents.items():
            docs.append({
                'doc_id': doc_id,
                'filename': doc['filename'],
                'created_at': doc['created_at'],
                'content_length': len(doc['content']),
                'chunks_count': len(doc['chunks'])
            })
        
        return jsonify({
            'success': True,
            'documents': docs,
            'total_count': len(docs)
        })
        
    except Exception as e:
        logger.error(f"获取文档列表失败: {e}")
        return jsonify({'error': f'获取文档列表失败: {str(e)}'}), 500

@app.route('/api/chat/history', methods=['GET'])
def chat_history():
    """获取聊天历史"""
    try:
        return jsonify({
            'success': True,
            'history': rag_system.chat_history[-10:],  # 返回最近10条
            'total_count': len(rag_system.chat_history)
        })
        
    except Exception as e:
        logger.error(f"获取聊天历史失败: {e}")
        return jsonify({'error': f'获取聊天历史失败: {str(e)}'}), 500

@app.route('/api/clear', methods=['POST'])
def clear_data():
    """清空所有数据"""
    try:
        rag_system.documents.clear()
        rag_system.chat_history.clear()
        
        # 清理上传的文件
        for file in os.listdir(UPLOAD_FOLDER):
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, file))
            except:
                pass
        
        return jsonify({
            'success': True,
            'message': '所有数据已清空'
        })
        
    except Exception as e:
        logger.error(f"清空数据失败: {e}")
        return jsonify({'error': f'清空数据失败: {str(e)}'}), 500

@app.route('/', methods=['GET'])
def index():
    """根路径"""
    return jsonify({
        'service': 'Simple RAG API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': [
            '/api/health',
            '/api/upload',
            '/api/chat',
            '/api/documents',
            '/api/chat/history',
            '/api/clear'
        ]
    })

if __name__ == '__main__':
    logger.info("启动简化版RAG API服务器...")
    logger.info(f"上传目录: {UPLOAD_FOLDER}")
    logger.info(f"向量数据库目录: {VECTOR_DB_PATH}")
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )