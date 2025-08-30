#!/usr/bin/env python3
"""
智能RAG系统服务器
修复文档上传和时区问题
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from pathlib import Path
import pytz
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 🌟 相对论引擎 - 动态路径发现系统
current_file = Path(__file__)
# 找到项目根目录 (假设此文件在 PROJECT_ROOT/systems/rag-system/ 下)
PROJECT_ROOT = current_file.parent.parent.parent

# 配置
TIMEZONE = pytz.timezone('Asia/Shanghai')
# 错误的"绝对"路径: UPLOAD_FOLDER = '/workspace/systems/rag-system/uploads'
# 正确的"相对"路径:
UPLOAD_FOLDER = current_file.parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)

# 模拟数据存储
chat_history = []
documents = []

def get_current_time():
    """获取当前时间（中国时区）"""
    return datetime.now(TIMEZONE)

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
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

def search_documents(query, max_results=3):
    """在文档中搜索相关内容"""
    if not documents:
        logger.info("搜索失败：没有文档")
        return []
    
    logger.info(f"搜索查询: '{query}', 文档数量: {len(documents)}")
    
    # 简单的关键词搜索
    results = []
    query_lower = query.lower()
    
    for i, doc in enumerate(documents):
        content = doc.get('content', '')
        filename = doc.get('filename', '')
        
        logger.info(f"检查文档 {i+1}: {filename}, 内容长度: {len(content)}")
        
        if not content:
            logger.warning(f"文档 {filename} 内容为空")
            continue
            
        content_lower = content.lower()
        
        # 计算相关性分数（简单的关键词匹配）
        score = 0
        # 简单的中英文分词处理
        import re
        # 提取中文字符和英文单词
        chinese_chars = re.findall(r'[\u4e00-\u9fff]+', query_lower)
        english_words = re.findall(r'[a-zA-Z]+', query_lower)
        
        # 合并所有关键词
        all_words = []
        for chinese in chinese_chars:
            # 对于中文，每个字符都作为关键词
            all_words.extend(list(chinese))
        all_words.extend(english_words)
        
        # 去除停用词和短词
        stop_words = {'的', '是', '在', '有', '和', '与', '或', '但', '而', '了', '吗', '呢', '什么', '怎么', '如何', '为什么', '帮', '我'}
        words = [word for word in all_words if word not in stop_words and len(word) >= 1]
        
        logger.info(f"处理后的关键词: {words}")
        
        for word in words:
            logger.info(f"搜索关键词: '{word}'")
            if word in content_lower:
                count = content_lower.count(word)
                score += count
                logger.info(f"关键词 '{word}' 在文档中出现 {count} 次")
            else:
                logger.info(f"关键词 '{word}' 未在文档中找到")
        
        logger.info(f"文档 {filename} 相关性分数: {score}")
        
        if score > 0:
            # 提取相关片段
            lines = content.split('\n')
            relevant_lines = []
            for line in lines:
                line_lower = line.lower()
                if any(word in line_lower for word in words):
                    relevant_lines.append(line.strip())
                    if len(relevant_lines) >= 5:  # 最多5行
                        break
            
            # 如果没有找到相关行，提取包含主要关键词的行
            if not relevant_lines:
                main_keywords = ['nexus', '功能', '系统']
                for line in lines:
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in main_keywords):
                        relevant_lines.append(line.strip())
                        if len(relevant_lines) >= 5:
                            break
            
            results.append({
                'filename': filename,
                'score': score,
                'content': '\n'.join(relevant_lines[:5]),
                'full_content': content
            })
    
    logger.info(f"搜索结果数量: {len(results)}")
    
    # 按相关性排序
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:max_results]

def generate_ai_response(message, current_time):
    """生成AI响应"""
    message_lower = message.lower()
    
    # 时间查询
    if '时间' in message or '现在' in message:
        return f'当前时间是 {current_time.strftime("%Y年%m月%d日 %H:%M:%S")} (北京时间)。'
    
    # 系统状态查询
    elif ('系统状态' in message or '运行状态' in message or '健康' in message) and not any(keyword in message_lower for keyword in ['rag', '智能', '功能', '特点']):
        return f'NEXUS系统运行正常！聊天历史: {len(chat_history)} 条，文档数量: {len(documents)} 个。'
    
    # 文档相关查询
    elif any(keyword in message_lower for keyword in ['总结', '内容', '文档', '介绍', '什么', '如何', '怎么', '功能', '特性']):
        if not documents:
            return '抱歉，目前没有上传任何文档。请先上传文档，然后我就可以帮您分析和回答相关问题了。'
        
        # 如果是总结请求，直接提供文档总结
        if '总结' in message_lower:
            response = "基于您上传的文档，我为您总结如下：\n\n"
            
            for i, doc in enumerate(documents, 1):
                content = doc.get('content', '')
                filename = doc.get('filename', '')
                
                response += f"**📄 {filename}**\n"
                
                # 提取文档的关键信息
                lines = content.split('\n')
                headers = [line for line in lines if line.startswith('#') and len(line.strip()) > 1]
                
                if headers:
                    response += "主要章节：\n"
                    for header in headers[:5]:  # 最多显示5个标题
                        response += f"• {header.strip()}\n"
                
                # 提取文档开头的描述性内容
                paragraphs = [line.strip() for line in lines if line.strip() and not line.startswith('#') and not line.startswith('-') and len(line.strip()) > 20]
                if paragraphs:
                    response += f"\n核心内容：\n{paragraphs[0][:200]}...\n"
                
                response += f"\n📊 文档统计：{len(content)} 个字符，{len(lines)} 行\n\n"
            
            return response
        
        # 对于其他文档相关查询，搜索相关内容
        search_results = search_documents(message)
        
        if not search_results:
            return f'我在已上传的 {len(documents)} 个文档中没有找到与您问题直接相关的内容。您可以尝试使用不同的关键词，或者告诉我您想了解文档的哪个方面。'
        
        # 生成基于文档内容的回答
        response = "基于您上传的文档，我为您总结如下：\n\n"
        
        for i, result in enumerate(search_results, 1):
            response += f"**📄 {result['filename']}**\n"
            response += f"{result['content']}\n\n"
        
        return response
    
    # 默认响应
    else:
        if documents:
            return f'您好！我是NEXUS AI助手，已加载了 {len(documents)} 个文档。您可以询问文档内容、要求总结，或者问我任何相关问题。当前时间是 {current_time.strftime("%H:%M:%S")}。'
        else:
            return f'您好！我是NEXUS AI助手，很高兴为您服务！请上传文档后，我就可以帮您分析和回答相关问题。当前时间是 {current_time.strftime("%H:%M:%S")}。'



@app.route('/api/health', methods=['GET'])
def health():
    """健康检查端点"""
    current_time = get_current_time()
    
    return jsonify({
        'status': 'healthy',
        'message': '智能RAG代理服务器运行正常',
        'ai_system': '本地智能响应系统',
        'version': '1.0.0',
        'timestamp': current_time.isoformat(),
        'data': {
            'chat_history_count': len(chat_history),
            'documents_count': len(documents),
            'system_status': '运行正常',
            'uptime': '系统运行中',
            'timezone': 'Asia/Shanghai'
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天端点"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({
                'status': 'error',
                'message': '消息不能为空'
            }), 400
        
        # 添加到聊天历史
        current_time = get_current_time()
        chat_entry = {
            'user_message': message,
            'timestamp': current_time.isoformat(),
            'id': len(chat_history) + 1
        }
        chat_history.append(chat_entry)
        
        # 生成AI响应
        response = generate_ai_response(message, current_time)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': current_time.isoformat(),
            'status': 'success',
            'chat_id': chat_entry['id']
        })
        
    except Exception as e:
        logger.error(f"聊天处理错误: {e}")
        return jsonify({
            'success': False,
            'status': 'error',
            'error': f'处理消息时发生错误: {str(e)}',
            'message': f'处理消息时发生错误: {str(e)}'
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload():
    """文档上传端点 - 修复chunks_count问题"""
    try:
        # 支持两种上传方式：单文件(file)和多文件(files)
        files = request.files.getlist('files') or request.files.getlist('file')
        
        if not files or not files[0].filename:
            return jsonify({
                'status': 'error',
                'message': '没有选择文件'
            }), 400
        
        results = []
        current_time = get_current_time()
        
        for file in files:
            if file and file.filename:
                # 保存文件
                filename = file.filename
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # 读取文件内容
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    logger.error(f"读取文件内容失败: {e}")
                    content = ""
                
                # 文档处理
                file_size = os.path.getsize(filepath)
                chunks = chunk_text(content) if content else []
                chunks_count = len(chunks)
                
                # 添加到文档列表
                doc_info = {
                    'filename': filename,
                    'filepath': filepath,
                    'content': content,  # 添加文件内容
                    'size': file_size,
                    'chunks_count': chunks_count,
                    'chunks': chunks,  # 添加分块内容
                    'upload_time': current_time.isoformat(),
                    'id': len(documents) + 1
                }
                documents.append(doc_info)
                
                result = {
                    'filename': filename,
                    'status': 'success',
                    'chunks_count': chunks_count,  # 确保chunks_count存在
                    'file_size': file_size,
                    'message': f'文档 {filename} 上传成功，已分割为 {chunks_count} 个片段'
                }
                results.append(result)
                
                logger.info(f"文档上传成功: {filename}, 大小: {file_size} bytes, 片段: {chunks_count}")
        
        # 构建响应
        response_data = {
            'success': True,
            'status': 'success',
            'message': f'成功上传 {len(results)} 个文件',
            'results': results,
            'timestamp': current_time.isoformat(),
            'total_documents': len(documents)
        }
        
        # 为单文件上传添加document字段（前端兼容性）
        if len(results) == 1:
            response_data['document'] = results[0]
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"文档上传错误: {e}")
        return jsonify({
            'success': False,
            'status': 'error',
            'error': f'上传失败: {str(e)}',
            'message': f'上传失败: {str(e)}'
        }), 500

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    """清除聊天历史"""
    global chat_history
    chat_history = []
    
    current_time = get_current_time()
    return jsonify({
        'success': True,
        'status': 'success',
        'message': '聊天历史已清除',
        'timestamp': current_time.isoformat()
    })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """获取文档列表"""
    current_time = get_current_time()
    
    return jsonify({
        'status': 'success',
        'documents': documents,
        'count': len(documents),
        'timestamp': current_time.isoformat()
    })

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """获取聊天历史"""
    current_time = get_current_time()
    
    return jsonify({
        'status': 'success',
        'chat_history': chat_history,
        'count': len(chat_history),
        'timestamp': current_time.isoformat()
    })

@app.route('/', methods=['GET'])
def index():
    """根路径"""
    current_time = get_current_time()
    
    return jsonify({
        'service': 'NEXUS RAG System',
        'status': 'running',
        'version': '1.0.0',
        'timestamp': current_time.isoformat(),
        'endpoints': [
            '/api/health',
            '/api/chat',
            '/api/upload',
            '/api/clear',
            '/api/documents',
            '/api/chat/history'
        ]
    })

if __name__ == '__main__':
    # 🌟 动态端口配置 - 从环境变量获取端口，支持服务发现系统
    port = int(os.environ.get('PORT', 8502))
    
    print("🚀 启动NEXUS RAG系统服务器...")
    print(f"📁 上传目录: {UPLOAD_FOLDER}")
    print(f"🕐 时区: {TIMEZONE}")
    print(f"🌐 服务器地址: http://0.0.0.0:{port}")
    print(f"📡 健康检查: http://localhost:{port}/api/health")
    print(f"💬 聊天接口: http://localhost:{port}/api/chat")
    print(f"📤 上传接口: http://localhost:{port}/api/upload")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )