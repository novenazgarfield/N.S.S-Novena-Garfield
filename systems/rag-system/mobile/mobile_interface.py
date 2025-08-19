"""
移动端界面组件
专为移动设备优化的UI组件
"""

import streamlit as st
import time
import datetime
from typing import Dict, List, Any, Optional
import sys
import os

# 添加common目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
from base_components import (
    SystemConfig, DocumentProcessor, ResponseGenerator, 
    SessionManager, AuthManager, UIComponents,
    system_config, document_processor, response_generator
)

class MobileInterface:
    """移动端界面管理"""
    
    def __init__(self):
        self.config = system_config
        self.processor = document_processor
        self.generator = response_generator
    
    def apply_mobile_css(self):
        """应用移动端CSS样式"""
        st.markdown("""
        <style>
        /* 移动端优化样式 */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1rem;
                max-width: 100%;
            }
            
            .stColumns {
                flex-direction: column;
            }
            
            .stColumns > div {
                width: 100% !important;
                margin-bottom: 1rem;
            }
            
            .chat-container {
                height: 400px !important;
                overflow-y: auto;
            }
            
            .settings-button {
                width: 45px !important;
                height: 45px !important;
                font-size: 18px !important;
            }
            
            .upload-area {
                padding: 10px !important;
            }
            
            /* 消息气泡移动端优化 */
            .message-bubble {
                margin-left: 5% !important;
                margin-right: 5% !important;
                font-size: 0.9rem;
            }
        }
        
        /* 基础样式 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 设置按钮 */
        .settings-button {
            position: fixed;
            top: 15px;
            right: 15px;
            z-index: 1000;
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        
        .settings-button:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        
        /* 聊天容器 */
        .chat-container {
            height: 500px;
            overflow-y: auto;
            padding: 10px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            background: #fafafa;
            margin-bottom: 20px;
        }
        
        /* 智能提示样式 */
        .suggestion-button {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border: 1px solid #2196f3;
            border-radius: 20px;
            padding: 8px 16px;
            margin: 4px;
            color: #1976d2;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        
        .suggestion-button:hover {
            background: linear-gradient(135deg, #bbdefb 0%, #90caf9 100%);
            transform: translateY(-2px);
        }
        
        /* 文档卡片样式 */
        .document-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            border-left: 4px solid #007bff;
        }
        
        /* 上传区域样式 */
        .upload-section {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 2px dashed #6c757d;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin: 16px 0;
        }
        
        /* 页脚样式 */
        .footer-info {
            text-align: center;
            color: #666;
            font-size: 0.8rem;
            padding: 20px 0;
            border-top: 1px solid #e0e0e0;
            margin-top: 30px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self):
        """渲染移动端头部"""
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown("# 💬 RAG智能对话")
            st.markdown("### 📱 移动端优化版")
        
        with col2:
            if st.button("⚙️", key="mobile_settings_btn", help="设置"):
                st.session_state.show_settings = not st.session_state.show_settings
                st.rerun()
    
    def render_chat_messages(self):
        """渲染聊天消息（移动端优化）"""
        st.markdown("### 💬 对话记录")
        
        # 创建聊天容器
        with st.container():
            for message in st.session_state.messages:
                UIComponents.render_message_bubble(
                    message, 
                    show_timestamp=self.config.get("show_timestamps", True)
                )
        
        # 自动滚动到底部
        if self.config.get("auto_scroll", True):
            st.markdown("""
            <script>
            setTimeout(function() {
                var chatContainer = document.querySelector('.chat-container');
                if (chatContainer) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            }, 100);
            </script>
            """, unsafe_allow_html=True)
    
    def render_smart_suggestions(self):
        """渲染智能提示（替代快捷按钮）"""
        if len(st.session_state.messages) <= 1:
            with st.expander("💡 试试这些问题", expanded=False):
                st.markdown("**点击下方问题快速开始对话：**")
                
                col1, col2 = st.columns(2)
                suggestions = [
                    "你好", "什么是RAG？", 
                    "如何使用？", "分析文档"
                ]
                
                for i, suggestion in enumerate(suggestions):
                    col_idx = i % 2
                    with [col1, col2][col_idx]:
                        if st.button(
                            suggestion, 
                            key=f"mobile_sug_{i}", 
                            use_container_width=True,
                            help=f"点击发送：{suggestion}"
                        ):
                            self._handle_suggestion_click(suggestion)
    
    def _handle_suggestion_click(self, suggestion: str):
        """处理建议点击"""
        if "设置" in suggestion:
            st.session_state.show_settings = True
            st.rerun()
        else:
            st.session_state.temp_message = suggestion
            st.rerun()
    
    def render_file_upload(self):
        """渲染文件上传区域（移动端优化）"""
        st.markdown("---")
        st.markdown("### 📄 文档上传")
        
        # 检查文档数量限制
        max_docs = self.config.get("max_documents", 20)
        current_docs = len(st.session_state.uploaded_documents)
        
        if current_docs >= max_docs:
            st.warning(f"⚠️ 已达到最大文档数量限制 ({max_docs} 个)")
            st.info("💡 请删除一些文档后再上传新文档")
            return
        
        # 文件上传器
        uploaded_file = st.file_uploader(
            "选择文档",
            type=[ext[1:] for ext in self.config.get("supported_formats", [])],
            help=f"支持格式: {', '.join(self.config.get('supported_formats', []))}\n最大文件大小: {self.config.get('max_file_size', 50)}MB",
            key="mobile_file_uploader"
        )
        
        if uploaded_file is not None:
            self._handle_file_upload(uploaded_file)
    
    def _handle_file_upload(self, uploaded_file):
        """处理文件上传"""
        # 显示文件信息
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.info(f"📄 **{uploaded_file.name}** ({file_size_mb:.2f} MB)")
        
        # 检查文件大小
        max_size = self.config.get("max_file_size", 50)
        if uploaded_file.size > max_size * 1024 * 1024:
            st.error(f"❌ 文件过大，最大支持 {max_size}MB")
            return
        
        # 上传按钮
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 上传分析", type="primary", use_container_width=True, key="mobile_upload_btn"):
                self._process_file_upload(uploaded_file)
        
        with col2:
            if st.button("❌ 取消", use_container_width=True, key="mobile_cancel_btn"):
                st.rerun()
    
    def _process_file_upload(self, uploaded_file):
        """处理文件上传和分析"""
        with st.spinner("🔄 处理中..."):
            try:
                content = self.processor.extract_text_from_file(uploaded_file)
                
                if content and content.strip():
                    # 添加文档到会话
                    doc_id = SessionManager.add_document(
                        uploaded_file.name, 
                        content, 
                        uploaded_file.size
                    )
                    
                    st.success("✅ 上传成功！")
                    st.balloons()
                    
                    # 自动分析文档
                    analysis_message = f"已上传文档 '{uploaded_file.name}'，请分析内容。"
                    
                    SessionManager.add_message("user", analysis_message)
                    
                    # 生成分析回答
                    response = self.generator.generate_response(analysis_message, content)
                    SessionManager.add_message("assistant", response)
                    
                    st.session_state.query_count += 1
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ 文档内容为空或处理失败，请检查文件格式")
            except Exception as e:
                st.error(f"❌ 文档处理失败: {str(e)}")
    
    def render_uploaded_documents(self):
        """渲染已上传文档列表"""
        if st.session_state.uploaded_documents:
            st.markdown("### 📋 已上传文档")
            
            for doc_id, doc_info in st.session_state.uploaded_documents.items():
                UIComponents.render_document_card(doc_id, doc_info, show_delete=True)
    
    def render_chat_input(self):
        """渲染聊天输入框"""
        st.markdown("---")
        st.markdown("### 💬 开始对话")
        
        # 处理临时消息（来自建议点击）
        if hasattr(st.session_state, 'temp_message'):
            self._process_temp_message()
        
        # 聊天输入框
        max_chars = self.config.get("max_message_length", 5000)
        if prompt := st.chat_input("💬 输入消息...", max_chars=max_chars, key="mobile_chat_input"):
            self._handle_chat_input(prompt)
    
    def _process_temp_message(self):
        """处理临时消息"""
        prompt = st.session_state.temp_message
        del st.session_state.temp_message
        
        # 检查查询限制
        max_queries = self.config.get("max_daily_queries", 500)
        if st.session_state.query_count >= max_queries:
            st.error(f"❌ 今日查询次数已达上限 ({max_queries} 次)")
            return
        
        # 添加用户消息
        SessionManager.add_message("user", prompt)
        
        # 生成AI回答
        with st.spinner("🤔 AI思考中..."):
            time.sleep(self.config.get("chat_speed", 1.0))
            
            context = self._get_document_context(prompt)
            
            # 获取AI模型参数
            user_id = st.session_state.get("user_id", "default_user")
            temperature = st.session_state.get("ai_temperature", 0.7)
            max_tokens = st.session_state.get("ai_max_tokens", 2048)
            
            response = self.generator.generate_response(
                prompt, 
                context, 
                user_id=user_id,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        SessionManager.add_message("assistant", response)
        st.session_state.query_count += 1
        st.rerun()
    
    def _handle_chat_input(self, prompt: str):
        """处理聊天输入"""
        # 检查查询限制
        max_queries = self.config.get("max_daily_queries", 500)
        if st.session_state.query_count >= max_queries:
            st.error(f"❌ 今日查询次数已达上限 ({max_queries} 次)")
            return
        
        # 添加用户消息
        SessionManager.add_message("user", prompt)
        
        # 生成AI回答
        with st.spinner("🤔 AI思考中..."):
            time.sleep(self.config.get("chat_speed", 1.0))
            
            context = self._get_document_context(prompt)
            
            # 获取AI模型参数
            user_id = st.session_state.get("user_id", "default_user")
            temperature = st.session_state.get("ai_temperature", 0.7)
            max_tokens = st.session_state.get("ai_max_tokens", 2048)
            
            response = self.generator.generate_response(
                prompt, 
                context, 
                user_id=user_id,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        SessionManager.add_message("assistant", response)
        st.session_state.query_count += 1
        st.rerun()
    
    def _get_document_context(self, prompt: str) -> str:
        """获取文档上下文"""
        if not st.session_state.uploaded_documents:
            return ""
        
        # 检查是否需要文档上下文
        doc_keywords = ["文档", "分析", "总结", "内容", "资料"]
        if any(keyword in prompt for keyword in doc_keywords):
            # 返回最新文档的内容
            latest_doc = list(st.session_state.uploaded_documents.values())[-1]
            return latest_doc["content"]
        
        return ""
    
    def render_footer(self):
        """渲染页脚信息"""
        st.markdown("---")
        st.markdown(
            f"<div class='footer-info'>"
            f"💬 {self.config.get('system_name')} {self.config.get('version')} | "
            f"📊 查询: {st.session_state.query_count}/{self.config.get('max_daily_queries')} | "
            f"📄 文档: {len(st.session_state.uploaded_documents)}/{self.config.get('max_documents')}"
            f"</div>",
            unsafe_allow_html=True
        )
    
    def render_complete_interface(self):
        """渲染完整的移动端界面"""
        # 应用CSS样式
        self.apply_mobile_css()
        
        # 渲染头部
        self.render_header()
        
        # 渲染聊天消息
        self.render_chat_messages()
        
        # 渲染智能提示
        self.render_smart_suggestions()
        
        # 渲染文件上传
        self.render_file_upload()
        
        # 渲染已上传文档
        self.render_uploaded_documents()
        
        # 渲染聊天输入
        self.render_chat_input()
        
        # 渲染页脚
        self.render_footer()

# 创建移动端界面实例
mobile_interface = MobileInterface()