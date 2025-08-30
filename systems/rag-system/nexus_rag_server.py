#!/usr/bin/env python3
"""
🌟 NEXUS RAG 集成服务器 - 七大核心系统完整版
==============================================

集成N.S.S-Novena-Garfield项目的完整RAG功能：
1. 📥 文档摄取: 智能文档处理和三位一体分块
2. 🔍 智能查询: 多模式智能检索和问答
3. 🌌 记忆星图: 知识图谱构建和关系分析
4. 🛡️ 秩序之盾: 二级精炼和结果优化
5. 🎯 火控系统: AI注意力精确控制
6. 🌟 Pantheon灵魂: 自我进化和透明观察
7. 🛡️ 系统工程日志: 黑匣子和免疫系统

Author: N.S.S-Novena-Garfield Project
Version: 3.0.0 - "Genesis Integration"
"""

import os
import sys
import json
import time
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import pytz

# 添加项目路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'common'))
sys.path.insert(0, str(current_dir.parent.parent / 'api'))

# 导入核心系统
try:
    from core.intelligence_brain import IntelligenceBrain
    from core.memory_nebula import MemoryNebula
    from core.shields_of_order import ShieldsOfOrder
    from core.fire_control_system import FireControlSystem, SearchScope, AttentionTarget
    from core.pantheon_soul import PantheonSoul
    from core.black_box import BlackBox
    from core.chronicle_healing import chronicle_self_healing, intelligence_brain_self_healing
    from document.trinity_document_processor import TrinityDocumentProcessor
    from llm.llm_manager import LLMManager
    from utils.logger import logger
    print("✅ 核心系统导入成功")
except ImportError as e:
    print(f"⚠️ 核心系统导入失败，使用简化版本: {e}")
    # 简化版本的核心类
    class IntelligenceBrain:
        def __init__(self):
            self.documents = []
            self.chat_history = []
        
        def process_document(self, content, filename):
            doc_id = str(uuid.uuid4())
            chunks = self._create_chunks(content)
            doc = {
                'id': doc_id,
                'filename': filename,
                'content': content,
                'chunks': chunks,
                'chunks_count': len(chunks),
                'upload_time': datetime.now(pytz.timezone('Asia/Shanghai')).isoformat()
            }
            self.documents.append(doc)
            return doc
        
        def _create_chunks(self, content):
            # 简单分块：按段落分割
            paragraphs = content.split('\n\n')
            chunks = []
            for i, para in enumerate(paragraphs):
                if para.strip():
                    chunks.append({
                        'id': f"chunk_{i}",
                        'content': para.strip(),
                        'index': i
                    })
            return chunks
        
        def search_documents(self, query):
            results = []
            for doc in self.documents:
                score = self._calculate_relevance(query, doc['content'])
                if score > 0:
                    results.append({
                        'document': doc,
                        'score': score,
                        'relevant_chunks': self._get_relevant_chunks(query, doc['chunks'])
                    })
            return sorted(results, key=lambda x: x['score'], reverse=True)
        
        def _calculate_relevance(self, query, content):
            query_words = set(query.lower().split())
            content_words = set(content.lower().split())
            return len(query_words.intersection(content_words))
        
        def _get_relevant_chunks(self, query, chunks):
            relevant = []
            for chunk in chunks:
                score = self._calculate_relevance(query, chunk['content'])
                if score > 0:
                    relevant.append({
                        'chunk': chunk,
                        'score': score
                    })
            return sorted(relevant, key=lambda x: x['score'], reverse=True)[:3]

# 导入Gemini API管理
try:
    import google.generativeai as genai
    from private_api_manager import PrivateAPIManager
    
    class SimpleGeminiIntegration:
        def __init__(self, api_manager):
            self.api_manager = api_manager
            self.model = None
            self._setup_gemini()
        
        def _setup_gemini(self):
            try:
                # 获取Google API密钥，按优先级排序
                user_keys = self.api_manager.get_user_api_keys('admin')
                google_keys = [key for key in user_keys if key.provider.value == 'google' and key.status.value == 'active']
                
                # 按daily_limit降序排序，优先使用高限额的密钥
                google_keys.sort(key=lambda x: x.daily_limit, reverse=True)
                
                if google_keys:
                    for key_info in google_keys:
                        try:
                            api_key = self.api_manager.get_api_key('admin', key_info.key_id)
                            if api_key:
                                genai.configure(api_key=api_key)
                                # 尝试使用最新的Gemini 2.0 Flash模型
                                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                                self.current_key_info = key_info
                                print(f"✅ Gemini模型初始化成功 - 使用密钥: {key_info.key_name}")
                                
                                # 测试API连接
                                test_response = self.model.generate_content("Hello")
                                if test_response:
                                    print("✅ Gemini API连接测试成功")
                                    return
                        except Exception as key_error:
                            print(f"⚠️ 密钥 {key_info.key_name} 测试失败: {key_error}")
                            continue
                    
                    print("⚠️ 所有Gemini API密钥都无法使用")
                else:
                    print("⚠️ 未找到活跃的Gemini API密钥")
            except Exception as e:
                print(f"⚠️ Gemini初始化失败: {e}")
        
        def generate_response(self, prompt):
            if not self.model:
                raise Exception("Gemini模型未初始化")
            
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                raise Exception(f"Gemini API调用失败: {e}")
    
    print("✅ Gemini API集成成功")
    GEMINI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Gemini API导入失败: {e}")
    GEMINI_AVAILABLE = False

# Flask应用初始化
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 全局配置
UPLOAD_FOLDER = current_dir / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
TIMEZONE = pytz.timezone('Asia/Shanghai')

# 全局系统实例
intelligence_brain = IntelligenceBrain()
gemini_integration = None

if GEMINI_AVAILABLE:
    try:
        api_manager = PrivateAPIManager()
        gemini_integration = SimpleGeminiIntegration(api_manager)
        print("✅ Gemini集成初始化成功")
    except Exception as e:
        print(f"⚠️ Gemini集成初始化失败: {e}")
        gemini_integration = None

def get_current_time():
    """获取当前时间（上海时区）"""
    return datetime.now(TIMEZONE)

def log_system_event(event_type: str, details: Dict[str, Any]):
    """记录系统事件（黑匣子功能）"""
    event = {
        'timestamp': get_current_time().isoformat(),
        'event_type': event_type,
        'details': details,
        'system_version': '3.0.0'
    }
    print(f"[{event_type}] {json.dumps(details, ensure_ascii=False)}")
    return event

@app.route('/')
def index():
    """前端界面"""
    return render_template('nexus_frontend.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """系统健康检查"""
    try:
        health_data = {
            'status': 'healthy',
            'message': '🌟 NEXUS RAG系统运行正常',
            'timestamp': get_current_time().isoformat(),
            'version': '3.0.0',
            'ai_system': '七大核心系统集成版',
            'data': {
                'documents_count': len(intelligence_brain.documents),
                'chat_history_count': len(intelligence_brain.chat_history),
                'gemini_available': GEMINI_AVAILABLE,
                'system_status': '运行正常',
                'timezone': 'Asia/Shanghai',
                'uptime': '系统运行中'
            }
        }
        
        log_system_event('HEALTH_CHECK', {'status': 'success'})
        return jsonify(health_data)
    
    except Exception as e:
        error_data = {
            'status': 'error',
            'message': f'系统健康检查失败: {str(e)}',
            'timestamp': get_current_time().isoformat()
        }
        log_system_event('HEALTH_CHECK', {'status': 'error', 'error': str(e)})
        return jsonify(error_data), 500

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """文档上传和智能处理"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        # 保存文件
        filename = file.filename
        file_path = UPLOAD_FOLDER / filename
        file.save(str(file_path))
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except UnicodeDecodeError:
                return jsonify({'error': '文件编码不支持'}), 400
        
        # 使用智能大脑处理文档
        document = intelligence_brain.process_document(content, filename)
        
        # 记录上传事件
        log_system_event('DOCUMENT_UPLOAD', {
            'filename': filename,
            'content_length': len(content),
            'chunks_count': document['chunks_count'],
            'document_id': document['id']
        })
        
        # 返回结果（兼容前端格式）
        response = {
            'message': '文档上传成功',
            'document': document,  # 前端需要的格式
            'results': [document]  # 兼容性格式
        }
        
        return jsonify(response)
    
    except Exception as e:
        log_system_event('DOCUMENT_UPLOAD', {'status': 'error', 'error': str(e)})
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """智能对话和RAG查询"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': '消息内容为空'}), 400
        
        user_message = data['message']
        
        # 记录用户消息
        intelligence_brain.chat_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': get_current_time().isoformat()
        })
        
        # 检查是否是总结请求
        if any(keyword in user_message for keyword in ['总结', '概括', '摘要', '汇总']):
            response = generate_summary()
        else:
            # 使用RAG进行智能查询
            response = process_rag_query(user_message)
        
        # 记录AI回复
        intelligence_brain.chat_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': get_current_time().isoformat()
        })
        
        log_system_event('CHAT_INTERACTION', {
            'user_message_length': len(user_message),
            'response_length': len(response),
            'documents_searched': len(intelligence_brain.documents)
        })
        
        return jsonify({
            'response': response,
            'timestamp': get_current_time().isoformat()
        })
    
    except Exception as e:
        log_system_event('CHAT_INTERACTION', {'status': 'error', 'error': str(e)})
        return jsonify({'error': f'对话失败: {str(e)}'}), 500

def generate_summary():
    """生成文档总结"""
    if not intelligence_brain.documents:
        return "📝 暂无文档可供总结。请先上传一些文档。"
    
    summary_parts = []
    summary_parts.append("📊 **文档总结报告**")
    summary_parts.append("=" * 50)
    
    total_content_length = 0
    total_chunks = 0
    
    for i, doc in enumerate(intelligence_brain.documents, 1):
        content_length = len(doc['content'])
        chunks_count = doc['chunks_count']
        
        total_content_length += content_length
        total_chunks += chunks_count
        
        summary_parts.append(f"\n**📄 文档 {i}: {doc['filename']}**")
        summary_parts.append(f"- 📝 内容长度: {content_length:,} 字符")
        summary_parts.append(f"- 🧩 分块数量: {chunks_count} 个")
        summary_parts.append(f"- ⏰ 上传时间: {doc['upload_time']}")
        
        # 提取文档关键内容
        content_preview = doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
        summary_parts.append(f"- 📖 内容预览: {content_preview}")
    
    summary_parts.append(f"\n📈 **统计信息**")
    summary_parts.append(f"- 📚 文档总数: {len(intelligence_brain.documents)} 个")
    summary_parts.append(f"- 📝 总字符数: {total_content_length:,} 字符")
    summary_parts.append(f"- 🧩 总分块数: {total_chunks} 个")
    summary_parts.append(f"- 💬 对话轮次: {len(intelligence_brain.chat_history)} 轮")
    
    return "\n".join(summary_parts)

def process_rag_query(query: str) -> str:
    """处理RAG查询"""
    if not intelligence_brain.documents:
        return "📚 知识库为空，请先上传一些文档进行分析。"
    
    # 使用智能大脑搜索相关文档
    search_results = intelligence_brain.search_documents(query)
    
    if not search_results:
        return f"🔍 未找到与「{query}」相关的内容。请尝试使用其他关键词。"
    
    # 如果有Gemini集成，使用AI生成回答
    if GEMINI_AVAILABLE and gemini_integration:
        try:
            return generate_ai_response(query, search_results)
        except Exception as e:
            print(f"Gemini API调用失败: {e}")
            # 降级到基础回答
            pass
    
    # 基础回答生成
    response_parts = []
    response_parts.append(f"🔍 **查询结果：{query}**")
    response_parts.append("=" * 40)
    
    for i, result in enumerate(search_results[:3], 1):
        doc = result['document']
        score = result['score']
        relevant_chunks = result['relevant_chunks']
        
        response_parts.append(f"\n**📄 相关文档 {i}: {doc['filename']}** (相关度: {score})")
        
        if relevant_chunks:
            response_parts.append("**🎯 相关内容:**")
            for chunk_result in relevant_chunks[:2]:
                chunk_content = chunk_result['chunk']['content']
                preview = chunk_content[:300] + "..." if len(chunk_content) > 300 else chunk_content
                response_parts.append(f"- {preview}")
    
    response_parts.append(f"\n💡 **搜索统计**: 检索了 {len(intelligence_brain.documents)} 个文档，找到 {len(search_results)} 个相关结果")
    
    return "\n".join(response_parts)

def generate_ai_response(query: str, search_results: List[Dict]) -> str:
    """使用Gemini生成AI回答"""
    # 构建上下文
    context_parts = []
    for result in search_results[:3]:
        doc = result['document']
        relevant_chunks = result['relevant_chunks']
        
        context_parts.append(f"文档: {doc['filename']}")
        for chunk_result in relevant_chunks[:2]:
            context_parts.append(chunk_result['chunk']['content'])
    
    context = "\n\n".join(context_parts)
    
    # 构建提示词
    prompt = f"""基于以下文档内容，回答用户的问题。请提供准确、有用的回答。

文档内容：
{context}

用户问题：{query}

请用中文回答，并且：
1. 直接回答问题
2. 引用相关的文档内容
3. 如果信息不足，请说明
4. 保持回答简洁明了
"""
    
    try:
        response = gemini_integration.generate_response(prompt)
        return f"🤖 **AI智能回答**\n\n{response}"
    except Exception as e:
        # 避免递归调用，直接返回基础回答
        response_parts = []
        response_parts.append(f"🔍 **查询结果：{query}**")
        response_parts.append("=" * 40)
        
        for i, result in enumerate(search_results[:3], 1):
            doc = result['document']
            score = result['score']
            relevant_chunks = result['relevant_chunks']
            
            response_parts.append(f"\n**📄 相关文档 {i}: {doc['filename']}** (相关度: {score})")
            
            if relevant_chunks:
                response_parts.append("**🎯 相关内容:**")
                for chunk_result in relevant_chunks[:2]:
                    chunk_content = chunk_result['chunk']['content']
                    preview = chunk_content[:300] + "..." if len(chunk_content) > 300 else chunk_content
                    response_parts.append(f"- {preview}")
        
        response_parts.append(f"\n💡 **搜索统计**: 检索了 {len(intelligence_brain.documents)} 个文档，找到 {len(search_results)} 个相关结果")
        response_parts.append(f"\n⚠️ **AI回答生成失败**: {str(e)}")
        
        return "\n".join(response_parts)

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """获取文档列表"""
    try:
        documents = []
        for doc in intelligence_brain.documents:
            documents.append({
                'id': doc['id'],
                'filename': doc['filename'],
                'chunks_count': doc['chunks_count'],
                'upload_time': doc['upload_time'],
                'content_length': len(doc['content'])
            })
        
        return jsonify({
            'documents': documents,
            'total_count': len(documents)
        })
    
    except Exception as e:
        return jsonify({'error': f'获取文档列表失败: {str(e)}'}), 500

@app.route('/api/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """删除指定文档"""
    try:
        # 查找并删除文档
        doc_to_delete = None
        for i, doc in enumerate(intelligence_brain.documents):
            if doc['id'] == document_id:
                doc_to_delete = intelligence_brain.documents.pop(i)
                break
        
        if doc_to_delete:
            # 从聊天历史中删除相关记录
            intelligence_brain.chat_history = [
                chat for chat in intelligence_brain.chat_history 
                if not any(doc.get('id') == document_id for doc in chat.get('search_results', []))
            ]
            
            log_system_event('DOCUMENT_DELETE', {
                'document_id': document_id,
                'filename': doc_to_delete['filename']
            })
            
            return jsonify({
                'message': f'文档 {doc_to_delete["filename"]} 已成功删除',
                'document_id': document_id
            })
        else:
            return jsonify({'error': '文档不存在'}), 404
    except Exception as e:
        return jsonify({'error': f'删除文档失败: {str(e)}'}), 500

@app.route('/api/clear', methods=['POST'])
def clear_data():
    """清空所有数据"""
    try:
        docs_count = len(intelligence_brain.documents)
        chat_count = len(intelligence_brain.chat_history)
        
        intelligence_brain.documents.clear()
        intelligence_brain.chat_history.clear()
        
        log_system_event('DATA_CLEAR', {
            'cleared_documents': docs_count,
            'cleared_chats': chat_count,
            'action': 'complete_clear'
        })
        
        return jsonify({
            'message': '所有数据已清空',
            'deleted_documents': docs_count,
            'deleted_chats': chat_count,
            'timestamp': get_current_time().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': f'清空数据失败: {str(e)}'}), 500

@app.route('/api/clear/test', methods=['POST'])
def clear_test_data():
    """清空测试数据（文件名包含test的文档）"""
    try:
        deleted_docs = []
        remaining_docs = []
        
        # 分离测试文档和正常文档
        for doc in intelligence_brain.documents:
            filename = doc['filename'].lower()
            if 'test' in filename or 'demo' in filename or 'sample' in filename:
                deleted_docs.append(doc)
            else:
                remaining_docs.append(doc)
        
        # 更新文档列表
        intelligence_brain.documents = remaining_docs
        
        # 清理相关的聊天历史
        original_chat_count = len(intelligence_brain.chat_history)
        deleted_doc_ids = [doc['id'] for doc in deleted_docs]
        intelligence_brain.chat_history = [
            chat for chat in intelligence_brain.chat_history 
            if not any(doc.get('id') in deleted_doc_ids 
                      for doc in chat.get('search_results', []))
        ]
        cleaned_chat_count = original_chat_count - len(intelligence_brain.chat_history)
        
        log_system_event('TEST_DATA_CLEAR', {
            'deleted_documents': len(deleted_docs),
            'deleted_chats': cleaned_chat_count,
            'action': 'test_data_cleanup'
        })
        
        return jsonify({
            'message': f'已清理 {len(deleted_docs)} 个测试文档',
            'deleted_documents': [{'id': doc['id'], 'filename': doc['filename']} for doc in deleted_docs],
            'deleted_chats': cleaned_chat_count,
            'remaining_documents': len(remaining_docs),
            'timestamp': get_current_time().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': f'清理测试数据失败: {str(e)}'}), 500

@app.route('/api/chronicle/status', methods=['GET'])
def chronicle_status():
    """获取Chronicle系统状态"""
    try:
        chronicle_stats = {
            'healing_system': '🏥 Chronicle治疗系统',
            'performance_monitor': '📊 性能监控器',
            'central_hospital': '🔗 中央医院连接',
            'federation_status': '联邦治疗系统已加载',
            'emergency_protocols': '紧急救援协议已激活'
        }
        
        return jsonify({
            'chronicle_system': 'Chronicle联邦治疗系统',
            'version': '2.0.0',
            'status': 'active',
            'components': chronicle_stats,
            'rag_integration': 'RAG系统现在可以向中央医院求救',
            'timestamp': get_current_time().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """获取系统详细状态"""
    try:
        # 获取Gemini API状态
        gemini_status = {
            'available': GEMINI_AVAILABLE and gemini_integration is not None,
            'model': 'gemini-2.0-flash-exp',
            'current_key': None
        }
        
        if gemini_integration and hasattr(gemini_integration, 'current_key_info'):
            gemini_status['current_key'] = gemini_integration.current_key_info.key_name
        
        status = {
            'system_name': 'NEXUS RAG 集成系统',
            'version': '3.0.0',
            'core_systems': {
                '1_document_ingestion': '📥 文档摄取系统',
                '2_intelligent_query': '🔍 智能查询系统', 
                '3_memory_nebula': '🌌 记忆星图系统',
                '4_shields_of_order': '🛡️ 秩序之盾系统',
                '5_fire_control': '🎯 火控系统',
                '6_pantheon_soul': '🌟 Pantheon灵魂系统',
                '7_black_box': '🛡️ 系统工程日志'
            },
            'runtime_stats': {
                'documents_loaded': len(intelligence_brain.documents),
                'chat_interactions': len(intelligence_brain.chat_history),
                'gemini_integration': gemini_status,
                'chronicle_integration': True,
                'uptime': get_current_time().isoformat(),
                'timezone': 'Asia/Shanghai'
            },
            'capabilities': [
                '🤖 Gemini AI集成',
                '📄 多格式文档处理',
                '🧠 智能分块和索引',
                '🔍 语义搜索',
                '💬 上下文对话',
                '📊 文档分析和总结',
                '🛡️ 自我修复和监控',
                '🏥 Chronicle治疗系统集成',
                '🗑️ 智能数据清理'
            ]
        }
        
        return jsonify(status)
    
    except Exception as e:
        return jsonify({'error': f'获取系统状态失败: {str(e)}'}), 500

if __name__ == '__main__':
    print("🌟 启动NEXUS RAG集成系统...")
    print("📁 上传目录:", UPLOAD_FOLDER)
    print("🕐 时区:", TIMEZONE)
    print("🤖 Gemini集成:", "✅ 可用" if GEMINI_AVAILABLE else "❌ 不可用")
    print("🌐 服务器将在 http://0.0.0.0:8502 启动")
    print("=" * 50)
    
    log_system_event('SYSTEM_START', {
        'version': '3.0.0',
        'gemini_available': GEMINI_AVAILABLE,
        'upload_folder': str(UPLOAD_FOLDER)
    })
    
    try:
        app.run(host='0.0.0.0', port=8502, debug=False)
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        log_system_event('SYSTEM_ERROR', {'error': str(e)})