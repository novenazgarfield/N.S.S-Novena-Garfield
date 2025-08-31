#!/usr/bin/env python3
"""
增强版智能RAG系统服务器
真正的AI文档理解和问答能力
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import re
from datetime import datetime
from pathlib import Path
import pytz
import logging
import argparse
from typing import List, Dict, Any
import hashlib
from docx import Document

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 配置
TIMEZONE = pytz.timezone('Asia/Shanghai')
current_file = Path(__file__)
UPLOAD_FOLDER = current_file.parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)

# 数据存储
chat_history = []
documents = []
document_embeddings = {}

class EnhancedDocumentProcessor:
    """增强版文档处理器"""
    
    def __init__(self):
        self.stop_words = {
            '的', '是', '在', '有', '和', '与', '或', '但', '而', '了', '吗', '呢', 
            '什么', '怎么', '如何', '为什么', '帮', '我', '你', '他', '她', '它',
            'the', 'is', 'at', 'which', 'on', 'and', 'or', 'but', 'a', 'an'
        }
    
    def extract_document_structure(self, content: str, filename: str) -> Dict[str, Any]:
        """提取文档结构和关键信息"""
        lines = content.split('\n')
        
        structure = {
            'filename': filename,
            'content': content,
            'headers': [],
            'sections': {},
            'key_points': [],
            'features': [],
            'statistics': {},
            'summary': ''
        }
        
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 提取标题
            if line.startswith('#'):
                if current_section and current_content:
                    structure['sections'][current_section] = '\n'.join(current_content)
                
                header_level = len(line) - len(line.lstrip('#'))
                header_text = line.lstrip('#').strip()
                structure['headers'].append({
                    'level': header_level,
                    'text': header_text,
                    'line': line
                })
                current_section = header_text
                current_content = []
            
            # 提取列表项和特性
            elif line.startswith(('- ', '* ', '+ ', '├──', '└──')):
                feature = line.lstrip('- *+├──└── ').strip()
                if len(feature) > 5:  # 过滤太短的项目
                    structure['features'].append(feature)
                current_content.append(line)
            
            # 提取关键点（包含特殊符号的行）
            elif any(symbol in line for symbol in ['✅', '🎯', '⭐', '🚀', '💡', '📊', '🔧']):
                structure['key_points'].append(line)
                current_content.append(line)
            
            else:
                current_content.append(line)
        
        # 处理最后一个section
        if current_section and current_content:
            structure['sections'][current_section] = '\n'.join(current_content)
        
        # 生成统计信息
        structure['statistics'] = {
            'total_lines': len(lines),
            'headers_count': len(structure['headers']),
            'sections_count': len(structure['sections']),
            'features_count': len(structure['features']),
            'key_points_count': len(structure['key_points']),
            'character_count': len(content),
            'word_count': len(content.split())
        }
        
        # 生成智能摘要
        structure['summary'] = self.generate_smart_summary(structure)
        
        return structure
    
    def generate_smart_summary(self, structure: Dict[str, Any]) -> str:
        """生成智能摘要"""
        filename = structure['filename']
        headers = structure['headers']
        features = structure['features']
        key_points = structure['key_points']
        stats = structure['statistics']
        
        summary = f"**📄 {filename}**\n"
        
        # 添加徽章和描述
        content = structure['content']
        if 'badge' in content.lower() or '[![' in content:
            badges = re.findall(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', content)
            if badges:
                summary += f"徽章信息: {len(badges)} 个项目徽章\n"
        
        # 识别项目类型
        project_type = self.identify_project_type(content)
        if project_type:
            summary += f"项目类型: {project_type}\n"
        
        # 主要章节
        if headers:
            summary += "主要章节:\n"
            for header in headers[:8]:  # 最多显示8个标题
                level_indicator = "  " * (header['level'] - 1)
                summary += f"{level_indicator}• {header['text']}\n"
        
        # 核心特性
        if features:
            summary += "\n核心特性:\n"
            for feature in features[:10]:  # 最多显示10个特性
                # 清理特性文本
                clean_feature = re.sub(r'[🔺🌌🛡️🎯🌟📥🔍🧠⚡🔧🎵📚🐄🧬🔬🚀]', '', feature).strip()
                if len(clean_feature) > 10:
                    summary += f"  • {clean_feature}\n"
        
        # 关键亮点
        if key_points:
            summary += "\n关键亮点:\n"
            for point in key_points[:5]:  # 最多显示5个关键点
                clean_point = point.strip()
                if len(clean_point) > 10:
                    summary += f"  • {clean_point}\n"
        
        # 技术栈识别
        tech_stack = self.identify_tech_stack(content)
        if tech_stack:
            summary += f"\n技术栈: {', '.join(tech_stack)}\n"
        
        # 统计信息
        summary += f"\n📊 文档统计: {stats['character_count']} 个字符，{stats['word_count']} 个词，{stats['headers_count']} 个章节"
        
        return summary
    
    def identify_project_type(self, content: str) -> str:
        """识别项目类型"""
        content_lower = content.lower()
        
        if 'rag' in content_lower and ('ai' in content_lower or '智能' in content):
            return "AI智能问答系统"
        elif 'genesis' in content_lower and 'brain' in content_lower:
            return "AI大脑系统"
        elif 'api' in content_lower and 'server' in content_lower:
            return "API服务系统"
        elif 'web' in content_lower and ('frontend' in content_lower or '前端' in content):
            return "Web前端应用"
        elif 'database' in content_lower or '数据库' in content:
            return "数据库系统"
        elif 'machine learning' in content_lower or 'ml' in content_lower:
            return "机器学习项目"
        elif 'research' in content_lower or '科研' in content:
            return "科研平台"
        else:
            return "综合系统平台"
    
    def identify_tech_stack(self, content: str) -> List[str]:
        """识别技术栈"""
        tech_stack = []
        content_lower = content.lower()
        
        # 编程语言
        if 'python' in content_lower:
            tech_stack.append('Python')
        if 'javascript' in content_lower or 'node' in content_lower:
            tech_stack.append('JavaScript/Node.js')
        if 'typescript' in content_lower:
            tech_stack.append('TypeScript')
        
        # 框架
        if 'flask' in content_lower:
            tech_stack.append('Flask')
        if 'streamlit' in content_lower:
            tech_stack.append('Streamlit')
        if 'vite' in content_lower:
            tech_stack.append('Vite')
        if 'react' in content_lower:
            tech_stack.append('React')
        
        # AI/ML
        if any(term in content_lower for term in ['openai', 'gpt', 'llm', 'ai']):
            tech_stack.append('AI/LLM')
        if 'vector' in content_lower or 'embedding' in content_lower:
            tech_stack.append('向量数据库')
        
        # 数据库
        if 'sqlite' in content_lower:
            tech_stack.append('SQLite')
        if 'postgresql' in content_lower:
            tech_stack.append('PostgreSQL')
        
        # 部署
        if 'docker' in content_lower:
            tech_stack.append('Docker')
        if 'cloudflare' in content_lower:
            tech_stack.append('Cloudflare')
        
        return tech_stack

class EnhancedRAGEngine:
    """增强版RAG引擎"""
    
    def __init__(self):
        self.doc_processor = EnhancedDocumentProcessor()
    
    def search_documents(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """智能文档搜索"""
        if not documents:
            return []
        
        query_lower = query.lower()
        results = []
        
        # 提取查询关键词
        query_keywords = self.extract_keywords(query)
        logger.info(f"查询关键词: {query_keywords}")
        
        for doc in documents:
            score = self.calculate_relevance_score(doc, query_keywords, query_lower)
            if score > 0:
                # 提取相关内容
                relevant_content = self.extract_relevant_content(doc, query_keywords, query_lower)
                results.append({
                    'document': doc,
                    'score': score,
                    'relevant_content': relevant_content
                })
        
        # 按相关性排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]
    
    def extract_keywords(self, query: str) -> List[str]:
        """提取查询关键词"""
        # 中文分词（简单版）
        chinese_chars = re.findall(r'[\u4e00-\u9fff]+', query)
        english_words = re.findall(r'[a-zA-Z]+', query.lower())
        
        keywords = []
        
        # 处理中文
        for chinese in chinese_chars:
            if len(chinese) >= 2:
                # 提取2-4字的词组
                for i in range(len(chinese)):
                    for length in [4, 3, 2]:
                        if i + length <= len(chinese):
                            word = chinese[i:i+length]
                            if word not in self.doc_processor.stop_words:
                                keywords.append(word)
        
        # 处理英文
        keywords.extend([word for word in english_words if word not in self.doc_processor.stop_words and len(word) > 2])
        
        # 去重并保持顺序
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:10]  # 最多10个关键词
    
    def calculate_relevance_score(self, doc: Dict[str, Any], keywords: List[str], query_lower: str) -> float:
        """计算文档相关性分数"""
        content = doc.get('content', '').lower()
        structure = doc.get('structure', {})
        
        score = 0.0
        
        # 关键词匹配
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # 标题匹配（高权重）
            for header in structure.get('headers', []):
                if keyword_lower in header.get('text', '').lower():
                    score += 5.0
            
            # 特性匹配（中权重）
            for feature in structure.get('features', []):
                if keyword_lower in feature.lower():
                    score += 3.0
            
            # 关键点匹配（中权重）
            for point in structure.get('key_points', []):
                if keyword_lower in point.lower():
                    score += 3.0
            
            # 内容匹配（基础权重）
            content_matches = content.count(keyword_lower)
            score += content_matches * 1.0
        
        # 查询短语完整匹配（高权重）
        if query_lower in content:
            score += 10.0
        
        return score
    
    def extract_relevant_content(self, doc: Dict[str, Any], keywords: List[str], query_lower: str) -> str:
        """提取相关内容"""
        structure = doc.get('structure', {})
        content = doc.get('content', '')
        
        relevant_parts = []
        
        # 添加匹配的标题
        matching_headers = []
        for header in structure.get('headers', []):
            header_text = header.get('text', '').lower()
            if any(keyword.lower() in header_text for keyword in keywords) or query_lower in header_text:
                matching_headers.append(header.get('line', ''))
        
        if matching_headers:
            relevant_parts.append("相关章节:")
            relevant_parts.extend(matching_headers[:3])
        
        # 添加匹配的特性
        matching_features = []
        for feature in structure.get('features', []):
            feature_lower = feature.lower()
            if any(keyword.lower() in feature_lower for keyword in keywords) or query_lower in feature_lower:
                matching_features.append(f"• {feature}")
        
        if matching_features:
            relevant_parts.append("\n核心特性:")
            relevant_parts.extend(matching_features[:5])
        
        # 添加匹配的关键点
        matching_points = []
        for point in structure.get('key_points', []):
            point_lower = point.lower()
            if any(keyword.lower() in point_lower for keyword in keywords) or query_lower in point_lower:
                matching_points.append(f"• {point}")
        
        if matching_points:
            relevant_parts.append("\n关键亮点:")
            relevant_parts.extend(matching_points[:3])
        
        # 如果没有找到特定匹配，返回摘要
        if not relevant_parts:
            return structure.get('summary', content[:500] + '...')
        
        return '\n'.join(relevant_parts)
    
    def generate_intelligent_response(self, message: str, search_results: List[Dict[str, Any]]) -> str:
        """生成智能回答"""
        message_lower = message.lower()
        
        # 如果没有搜索结果
        if not search_results:
            if any(keyword in message_lower for keyword in ['总结', '介绍', '什么', '如何', '功能', '特性']):
                return "抱歉，我没有找到相关的文档内容。请先上传文档，然后我就可以帮您分析和回答相关问题了。"
            else:
                return "您好！我是NEXUS AI助手，很高兴为您服务！请上传文档后，我就可以帮您分析和回答相关问题。"
        
        # 基于搜索结果生成回答
        response_parts = []
        
        # 问题类型识别
        if '总结' in message_lower or '介绍' in message_lower:
            response_parts.append("基于您上传的文档，我为您总结如下：\n")
            
            for i, result in enumerate(search_results, 1):
                doc = result['document']
                structure = doc.get('structure', {})
                response_parts.append(f"**{i}. {structure.get('filename', '文档')}**")
                response_parts.append(structure.get('summary', ''))
                response_parts.append("")
        
        elif any(keyword in message_lower for keyword in ['功能', '特性', '能力', '特点']):
            response_parts.append("根据文档分析，主要功能特性包括：\n")
            
            all_features = []
            for result in search_results:
                structure = result['document'].get('structure', {})
                all_features.extend(structure.get('features', []))
            
            # 去重并选择最相关的特性
            unique_features = list(dict.fromkeys(all_features))
            for feature in unique_features[:10]:
                clean_feature = re.sub(r'[🔺🌌🛡️🎯🌟📥🔍🧠⚡🔧🎵📚🐄🧬🔬🚀]', '', feature).strip()
                if len(clean_feature) > 5:
                    response_parts.append(f"• {clean_feature}")
        
        elif any(keyword in message_lower for keyword in ['如何', '怎么', '使用', '操作']):
            response_parts.append("根据文档内容，使用方法如下：\n")
            
            for result in search_results:
                relevant_content = result['relevant_content']
                if relevant_content:
                    response_parts.append(relevant_content)
                    response_parts.append("")
        
        else:
            # 通用问答
            response_parts.append("根据您的问题，我找到了以下相关信息：\n")
            
            for i, result in enumerate(search_results, 1):
                response_parts.append(f"**{i}. 相关内容：**")
                response_parts.append(result['relevant_content'])
                response_parts.append("")
        
        # 添加统计信息
        if search_results:
            total_docs = len(documents)
            matched_docs = len(search_results)
            response_parts.append(f"\n📊 搜索统计：在 {total_docs} 个文档中找到 {matched_docs} 个相关文档")
        
        return '\n'.join(response_parts)

# 初始化增强版RAG引擎
rag_engine = EnhancedRAGEngine()

def get_current_time():
    """获取当前时间（中国时区）"""
    return datetime.now(TIMEZONE)

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    current_time = get_current_time()
    
    return jsonify({
        "status": "healthy",
        "message": "增强版智能RAG代理服务器运行正常",
        "ai_system": "增强版本地智能响应系统",
        "version": "2.0.0-Enhanced",
        "timestamp": current_time.isoformat(),
        "data": {
            "chat_history_count": len(chat_history),
            "documents_count": len(documents),
            "system_status": "运行正常",
            "timezone": "Asia/Shanghai",
            "uptime": "系统运行中",
            "features": [
                "智能文档结构分析",
                "增强版关键词提取",
                "上下文相关性计算",
                "智能摘要生成",
                "技术栈识别"
            ]
        }
    })

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """系统状态检查 - 为前端提供详细状态信息"""
    current_time = get_current_time()
    
    return jsonify({
        "status": "active",
        "message": "系统运行正常",
        "timestamp": current_time.isoformat(),
        "data": {
            "chat_history_count": len(chat_history),
            "documents_count": len(documents),
            "system_health": "healthy",
            "uptime": "运行中",
            "version": "2.0.0-Enhanced",
            "features_active": len([
                "智能文档结构分析",
                "增强版关键词提取", 
                "上下文相关性计算",
                "智能摘要生成",
                "技术栈识别"
            ]),
            "api_endpoints": {
                "health": "/api/health",
                "upload": "/api/upload", 
                "chat": "/api/chat",
                "documents": "/api/documents",
                "chat_history": "/api/chat/history",
                "system_status": "/api/system/status"
            }
        }
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "没有文件"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "message": "没有选择文件"}), 400
        
        if file:
            filename = file.filename
            filepath = UPLOAD_FOLDER / filename
            file.save(filepath)
            
            # 读取文件内容
            content = ""
            file_extension = filename.lower().split('.')[-1]
            
            if file_extension == 'docx':
                # 处理.docx文件
                try:
                    doc = Document(filepath)
                    paragraphs = []
                    for paragraph in doc.paragraphs:
                        if paragraph.text.strip():
                            paragraphs.append(paragraph.text.strip())
                    content = '\n'.join(paragraphs)
                    logger.info(f"成功解析.docx文件: {filename}, 段落数: {len(paragraphs)}")
                except Exception as e:
                    logger.error(f"解析.docx文件失败: {filename}, 错误: {str(e)}")
                    return jsonify({
                        "success": False, 
                        "message": f"解析.docx文件失败: {str(e)}"
                    }), 500
            else:
                # 处理文本文件
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(filepath, 'r', encoding='gbk') as f:
                            content = f.read()
                    except Exception as e:
                        logger.error(f"读取文件失败: {filename}, 错误: {str(e)}")
                        return jsonify({
                            "success": False, 
                            "message": f"读取文件失败: {str(e)}"
                        }), 500
            
            # 使用增强版文档处理器
            structure = rag_engine.doc_processor.extract_document_structure(content, filename)
            
            # 存储文档
            doc_id = hashlib.md5(f"{filename}{content}".encode()).hexdigest()
            document = {
                "id": doc_id,
                "filename": filename,
                "content": content,
                "structure": structure,
                "upload_time": get_current_time().isoformat(),
                "file_size": len(content)
            }
            
            # 检查是否已存在
            existing_doc = next((doc for doc in documents if doc['id'] == doc_id), None)
            if existing_doc:
                return jsonify({
                    "success": True,
                    "message": f"文档 {filename} 已存在",
                    "document_info": {
                        "filename": filename,
                        "size": len(content),
                        "structure_info": structure['statistics']
                    }
                })
            
            documents.append(document)
            
            logger.info(f"文档上传成功: {filename}, 大小: {len(content)} 字符")
            
            return jsonify({
                "success": True,
                "message": f"文档 {filename} 上传成功",
                "document_info": {
                    "filename": filename,
                    "size": len(content),
                    "structure_info": structure['statistics'],
                    "summary": structure['summary'][:200] + "..." if len(structure['summary']) > 200 else structure['summary']
                }
            })
            
    except Exception as e:
        logger.error(f"文件上传错误: {e}")
        return jsonify({"success": False, "message": f"上传失败: {str(e)}"}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天接口"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', 'default')
        
        if not message:
            return jsonify({"success": False, "message": "消息不能为空"}), 400
        
        current_time = get_current_time()
        
        # 使用增强版RAG引擎搜索和生成回答
        search_results = rag_engine.search_documents(message)
        response = rag_engine.generate_intelligent_response(message, search_results)
        
        # 记录聊天历史
        chat_record = {
            "id": len(chat_history) + 1,
            "conversation_id": conversation_id,
            "message": message,
            "response": response,
            "timestamp": current_time.isoformat(),
            "search_results_count": len(search_results)
        }
        
        chat_history.append(chat_record)
        
        logger.info(f"聊天记录: {message[:50]}... -> {len(search_results)} 个搜索结果")
        
        return jsonify({
            "success": True,
            "status": "success",
            "chat_id": chat_record["id"],
            "response": response,
            "timestamp": current_time.isoformat(),
            "search_info": {
                "documents_searched": len(documents),
                "results_found": len(search_results)
            }
        })
        
    except Exception as e:
        logger.error(f"聊天处理错误: {e}")
        return jsonify({"success": False, "message": f"处理失败: {str(e)}"}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """获取文档列表"""
    doc_list = []
    for doc in documents:
        structure = doc.get('structure', {})
        doc_list.append({
            "id": doc['id'],
            "filename": doc['filename'],
            "upload_time": doc['upload_time'],
            "file_size": doc['file_size'],
            "statistics": structure.get('statistics', {}),
            "summary": structure.get('summary', '')[:100] + "..." if len(structure.get('summary', '')) > 100 else structure.get('summary', '')
        })
    
    return jsonify({
        "success": True,
        "documents": doc_list,
        "total_count": len(documents)
    })

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """获取聊天历史"""
    conversation_id = request.args.get('conversation_id', 'default')
    
    filtered_history = [
        chat for chat in chat_history 
        if chat.get('conversation_id') == conversation_id
    ]
    
    return jsonify({
        "success": True,
        "chat_history": filtered_history,
        "total_count": len(filtered_history)
    })

@app.route('/api/clear/test', methods=['POST'])
def clear_test_data():
    """清理测试数据"""
    global documents, chat_history
    
    try:
        # 定义测试关键词
        test_keywords = ['test', 'demo', 'sample', '测试', '示例', '样本']
        
        # 找到需要删除的文档
        deleted_documents = []
        remaining_documents = []
        
        for doc in documents:
            filename = doc.get('structure', {}).get('filename', '').lower()
            is_test_doc = any(keyword in filename for keyword in test_keywords)
            
            if is_test_doc:
                deleted_documents.append({
                    'filename': doc.get('structure', {}).get('filename', ''),
                    'id': doc.get('id', ''),
                    'upload_time': doc.get('upload_time', '')
                })
            else:
                remaining_documents.append(doc)
        
        # 清理测试文档
        documents = remaining_documents
        
        # 清理相关的聊天历史（简单实现：清理所有历史）
        deleted_chats = len(chat_history)
        chat_history = []
        
        return jsonify({
            "success": True,
            "deleted_documents": deleted_documents,
            "deleted_chats": deleted_chats,
            "remaining_documents": len(remaining_documents),
            "timestamp": datetime.now().isoformat(),
            "message": f"成功清理 {len(deleted_documents)} 个测试文档和 {deleted_chats} 条聊天记录"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "清理测试数据时发生错误"
        }), 500

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat_history():
    """清空聊天记录"""
    global chat_history
    
    try:
        cleared_count = len(chat_history)
        chat_history = []
        
        return jsonify({
            "success": True,
            "cleared_count": cleared_count,
            "timestamp": datetime.now().isoformat(),
            "message": f"成功清空 {cleared_count} 条聊天记录"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "清空聊天记录时发生错误"
        }), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='增强版智能RAG服务器')
    parser.add_argument('--port', type=int, default=8502, help='服务器端口')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    
    args = parser.parse_args()
    
    print(f"🧠 增强版智能RAG系统启动中...")
    print(f"📡 健康检查: http://{args.host}:{args.port}/api/health")
    print(f"💬 聊天接口: http://{args.host}:{args.port}/api/chat")
    print(f"📤 上传接口: http://{args.host}:{args.port}/api/upload")
    print(f"📚 文档列表: http://{args.host}:{args.port}/api/documents")
    
    app.run(host=args.host, port=args.port, debug=args.debug)