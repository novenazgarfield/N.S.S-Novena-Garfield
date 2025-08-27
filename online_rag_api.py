#!/usr/bin/env python3
"""
完整RAG API服务器
支持文档上传、解析、向量化和智能问答
使用Gemini AI作为后端
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
import google.generativeai as genai

# 文档处理库
try:
    import PyPDF2
    import docx
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import faiss
    PDF_SUPPORT = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"部分文档处理库未安装: {e}")
    PDF_SUPPORT = False

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# Gemini API配置
GEMINI_API_KEY = "AIzaSyBOlNcGkx43zNOvnDesd_PEhD4Lj9T8Tpo"  # 您的Gemini API密钥
MODEL_NAME = "gemini-2.0-flash-exp"

# 存储配置
UPLOAD_FOLDER = '/tmp/rag_documents'
VECTOR_DB_PATH = '/tmp/rag_vectors'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 创建必要的目录
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

# 全局存储
chat_history = []
document_store = {}  # 文档存储
vector_store = None  # 向量存储
embeddings_model = None  # 嵌入模型

# 初始化Gemini AI
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
    logger.info(f"✅ Gemini API初始化成功，使用模型: {MODEL_NAME}")
except Exception as e:
    logger.error(f"❌ Gemini API初始化失败: {e}")
    model = None

# 初始化嵌入模型（轻量级）
try:
    embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
    vector_store = faiss.IndexFlatL2(384)  # all-MiniLM-L6-v2的维度是384
    logger.info("✅ 向量化模型初始化成功")
except Exception as e:
    logger.warning(f"⚠️ 向量化模型初始化失败，将使用简化模式: {e}")
    embeddings_model = None
    vector_store = None

def extract_text_from_file(file_path: str, filename: str) -> str:
    """从文件中提取文本"""
    try:
        file_ext = Path(filename).suffix.lower()
        
        if file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        
        elif file_ext == '.pdf':
            try:
                import PyPDF2
                text = ""
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                return text
            except ImportError:
                return "PDF处理库未安装，请安装PyPDF2"
        
        elif file_ext in ['.docx', '.doc']:
            try:
                import docx
                doc = docx.Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except ImportError:
                return "Word文档处理库未安装，请安装python-docx"
        
        else:
            # 尝试作为文本文件读取
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
                
    except Exception as e:
        logger.error(f"文件文本提取失败: {e}")
        return f"文件读取失败: {str(e)}"

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """将文本分块"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # 尝试在句号、换行符或空格处分割
        if end < len(text):
            for delimiter in ['\n\n', '\n', '. ', '。', ' ']:
                last_delim = text.rfind(delimiter, start, end)
                if last_delim > start:
                    end = last_delim + len(delimiter)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

def add_document_to_vector_store(doc_id: str, text: str):
    """将文档添加到向量存储"""
    global vector_store, embeddings_model, document_store
    
    if not embeddings_model or not vector_store:
        logger.warning("向量化模型未初始化，跳过向量存储")
        return
    
    try:
        # 分块
        chunks = chunk_text(text)
        
        # 生成嵌入
        embeddings = embeddings_model.encode(chunks)
        
        # 添加到向量存储
        vector_store.add(embeddings)
        
        # 保存文档块信息
        start_idx = vector_store.ntotal - len(chunks)
        document_store[doc_id] = {
            'chunks': chunks,
            'start_idx': start_idx,
            'end_idx': vector_store.ntotal - 1,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"文档 {doc_id} 已添加到向量存储，共 {len(chunks)} 个块")
        
    except Exception as e:
        logger.error(f"向量存储失败: {e}")

def search_relevant_documents(query: str, top_k: int = 3) -> List[str]:
    """搜索相关文档"""
    global vector_store, embeddings_model, document_store
    
    if not embeddings_model or not vector_store or vector_store.ntotal == 0:
        return []
    
    try:
        # 生成查询嵌入
        query_embedding = embeddings_model.encode([query])
        
        # 搜索
        distances, indices = vector_store.search(query_embedding, min(top_k, vector_store.ntotal))
        
        # 获取相关文档块
        relevant_chunks = []
        for idx in indices[0]:
            if idx >= 0:  # faiss返回-1表示无效索引
                # 找到对应的文档块
                for doc_id, doc_info in document_store.items():
                    if doc_info['start_idx'] <= idx <= doc_info['end_idx']:
                        chunk_idx = idx - doc_info['start_idx']
                        if chunk_idx < len(doc_info['chunks']):
                            relevant_chunks.append(doc_info['chunks'][chunk_idx])
                        break
        
        return relevant_chunks
        
    except Exception as e:
        logger.error(f"文档搜索失败: {e}")
        return []

def get_ai_response(message: str) -> str:
    """获取AI响应（支持RAG）"""
    try:
        if not model:
            return "抱歉，AI服务暂时不可用，请稍后再试。"
        
        # 搜索相关文档
        relevant_docs = search_relevant_documents(message)
        
        # 构建对话上下文
        context = "你是NEXUS AI，一个友好的智能助手。请用中文回答问题，保持简洁明了但信息丰富。"
        
        # 如果有相关文档，添加到上下文中
        if relevant_docs:
            context += "\n\n参考文档内容:\n"
            for i, doc in enumerate(relevant_docs, 1):
                context += f"文档片段{i}: {doc}\n\n"
            context += "请基于以上文档内容回答用户问题。如果文档中没有相关信息，请说明并提供一般性回答。"
        
        # 添加聊天历史作为上下文（最近3条，避免上下文过长）
        recent_history = chat_history[-3:] if len(chat_history) > 3 else chat_history
        if recent_history:
            context += "\n\n最近的对话历史:\n"
            for item in recent_history:
                context += f"用户: {item['user']}\n助手: {item['assistant']}\n"
        
        context += f"\n\n当前用户问题: {message}"
        
        # 调用Gemini API
        response = model.generate_content(context)
        
        if response.text:
            return response.text.strip()
        else:
            return "抱歉，我无法理解您的问题，请重新表述。"
            
    except Exception as e:
        logger.error(f"AI响应生成失败: {e}")
        return f"抱歉，处理您的请求时出现错误: {str(e)}"

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'ok',
        'backend': 'Gemini AI',
        'model': MODEL_NAME,
        'rag_system_ready': model is not None,
        'vector_store_ready': embeddings_model is not None and vector_store is not None,
        'chat_history_count': len(chat_history),
        'documents_count': len(document_store),
        'vector_count': vector_store.ntotal if vector_store else 0,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天端点"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': '请提供消息内容'
            }), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({
                'success': False,
                'error': '消息不能为空'
            }), 400
        
        # 获取AI响应
        ai_response = get_ai_response(user_message)
        
        # 保存到聊天历史
        chat_history.append({
            'user': user_message,
            'assistant': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # 限制历史记录数量
        if len(chat_history) > 100:
            chat_history.pop(0)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'backend': 'Gemini AI',
            'model': MODEL_NAME,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"聊天处理失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'处理请求时出现错误: {str(e)}'
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """文档上传端点"""
    try:
        logger.info(f"收到上传请求，文件列表: {list(request.files.keys())}")
        
        if 'file' not in request.files:
            logger.warning("上传请求中没有找到'file'字段")
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        file = request.files['file']
        logger.info(f"处理文件: {file.filename}, 大小: {file.content_length if hasattr(file, 'content_length') else '未知'}")
        
        if file.filename == '':
            logger.warning("文件名为空")
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        logger.info(f"文件 {file.filename} 实际大小: {file_size} 字节 ({file_size / (1024*1024):.2f} MB)")
        
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"文件 {file.filename} 大小超限: {file_size} > {MAX_FILE_SIZE}")
            return jsonify({
                'success': False,
                'error': f'文件大小超过限制 ({MAX_FILE_SIZE // (1024*1024)}MB)，当前文件大小: {file_size / (1024*1024):.2f}MB'
            }), 400
        
        # 生成文件ID
        file_hash = hashlib.md5(f"{file.filename}{datetime.now()}".encode()).hexdigest()
        file_path = os.path.join(UPLOAD_FOLDER, f"{file_hash}_{file.filename}")
        
        # 保存文件
        file.save(file_path)
        
        # 提取文本
        text_content = extract_text_from_file(file_path, file.filename)
        
        if not text_content or text_content.startswith("文件读取失败"):
            return jsonify({
                'success': False,
                'error': f'文件处理失败: {text_content}'
            }), 400
        
        # 添加到向量存储
        add_document_to_vector_store(file_hash, text_content)
        
        # 保存文档信息
        doc_info = {
            'id': file_hash,
            'filename': file.filename,
            'size': file_size,
            'upload_time': datetime.now().isoformat(),
            'text_length': len(text_content),
            'chunks_count': len(chunk_text(text_content)) if text_content else 0
        }
        
        return jsonify({
            'success': True,
            'message': '文档上传成功',
            'document': doc_info,
            'preview': text_content[:500] + "..." if len(text_content) > 500 else text_content
        })
        
    except Exception as e:
        logger.error(f"文档上传失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'文档上传失败: {str(e)}'
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """获取聊天历史"""
    return jsonify({
        'success': True,
        'history': chat_history,
        'count': len(chat_history)
    })

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """清空聊天历史"""
    global chat_history
    chat_history = []
    return jsonify({
        'success': True,
        'message': '聊天历史已清空'
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取系统统计"""
    return jsonify({
        'backend': 'Gemini AI',
        'model': MODEL_NAME,
        'chat_history_count': len(chat_history),
        'documents_count': len(document_store),
        'vector_count': vector_store.ntotal if vector_store else 0,
        'system_ready': model is not None,
        'vector_store_ready': embeddings_model is not None and vector_store is not None,
        'supported_formats': ['txt', 'pdf', 'docx', 'doc'],
        'max_file_size_mb': MAX_FILE_SIZE // (1024*1024),
        'uptime': 'N/A',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """获取已上传的文档列表"""
    docs = []
    for doc_id, doc_info in document_store.items():
        docs.append({
            'id': doc_id,
            'chunks_count': len(doc_info['chunks']),
            'timestamp': doc_info['timestamp']
        })
    
    return jsonify({
        'success': True,
        'documents': docs,
        'total_count': len(docs)
    })

if __name__ == '__main__':
    print("🚀 启动在线RAG API服务器...")
    print("=" * 50)
    print(f"🤖 后端: Gemini AI")
    print(f"🧠 模型: {MODEL_NAME}")
    print(f"🌐 服务地址: http://0.0.0.0:5000")
    print("📡 API端点:")
    print("  - GET  /api/health  - 健康检查")
    print("  - POST /api/chat    - 聊天接口")
    print("  - POST /api/upload  - 文档上传")
    print("  - GET  /api/history - 聊天历史")
    print("  - POST /api/clear   - 清空记录")
    print("  - GET  /api/stats   - 系统统计")
    print("=" * 50)
    
    if model:
        print("✅ Gemini API配置正常")
    else:
        print("❌ Gemini API配置异常，请检查API密钥")
    
    print("\n🎯 使用说明:")
    print("1. 这是一个在线RAG服务，使用Gemini AI作为后端")
    print("2. 无需本地部署大模型，只需要Gemini API密钥")
    print("3. 支持智能对话、文档处理等功能")
    print("4. 前端会自动连接到此API服务")
    
    app.run(host='0.0.0.0', port=5000, debug=False)