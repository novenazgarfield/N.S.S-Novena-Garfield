"""
桌面端界面组件
专为桌面设备优化的UI组件
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

class DesktopInterface:
    """桌面端界面管理"""
    
    def __init__(self):
        self.config = system_config
        self.processor = document_processor
        self.generator = response_generator
    
    def apply_desktop_css(self):
        """应用桌面端CSS样式"""
        st.markdown("""
        <style>
        /* 桌面端优化样式 */
        .main .block-container {
            padding-top: 2rem;
            max-width: 1200px;
        }
        
        /* 基础样式 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 设置按钮 */
        .settings-button {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
            color: white;
            border: none;
            border-radius: 50%;
            width: 55px;
            height: 55px;
            font-size: 22px;
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
            height: 600px;
            overflow-y: auto;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        /* 侧边栏样式 */
        .sidebar-section {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        /* 快捷按钮样式 */
        .quick-button {
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 15px;
            margin: 5px;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0,123,255,0.3);
        }
        
        .quick-button:hover {
            background: linear-gradient(135deg, #0056b3 0%, #004085 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,123,255,0.4);
        }
        
        /* 文档卡片样式 */
        .document-card {
            background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #007bff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .document-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }
        
        /* 上传区域样式 */
        .upload-section {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border: 2px dashed #2196f3;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            margin: 20px 0;
            transition: all 0.3s ease;
        }
        
        .upload-section:hover {
            background: linear-gradient(135deg, #bbdefb 0%, #90caf9 100%);
            border-color: #1976d2;
        }
        
        /* 统计卡片样式 */
        .stat-card {
            background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }
        
        /* 页脚样式 */
        .footer-info {
            text-align: center;
            color: #666;
            font-size: 0.9rem;
            padding: 30px 0;
            border-top: 1px solid #e0e0e0;
            margin-top: 40px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self):
        """渲染桌面端头部"""
        col1, col2 = st.columns([5, 1])
        
        with col1:
            st.markdown("# 💬 RAG智能对话系统")
            st.markdown("### 🖥️ 桌面端完整版")
        
        with col2:
            if st.button("⚙️", key="desktop_settings_btn", help="系统设置"):
                st.session_state.show_settings = not st.session_state.show_settings
                st.rerun()
    
    def render_main_layout(self):
        """渲染主要布局（两栏式）"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            self.render_chat_section()
        
        with col2:
            self.render_sidebar()
    
    def render_chat_section(self):
        """渲染聊天区域"""
        st.markdown("### 💬 智能对话")
        
        # 聊天消息显示
        with st.container():
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for message in st.session_state.messages:
                UIComponents.render_message_bubble(
                    message, 
                    show_timestamp=self.config.get("show_timestamps", True)
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 快捷问题按钮
        self.render_quick_questions()
        
        # 聊天输入
        self.render_chat_input()
    
    def render_quick_questions(self):
        """渲染快捷问题按钮"""
        st.markdown("**💡 快捷问题:**")
        
        col1, col2, col3, col4 = st.columns(4)
        quick_questions = ["什么是RAG？", "使用帮助", "分析文档", "系统设置"]
        
        for i, question in enumerate(quick_questions):
            with [col1, col2, col3, col4][i]:
                if st.button(
                    question, 
                    key=f"desktop_quick_{i}", 
                    use_container_width=True,
                    help=f"点击询问：{question}"
                ):
                    if "设置" in question:
                        st.session_state.show_settings = True
                        st.rerun()
                    else:
                        self._handle_quick_question(question)
    
    def _handle_quick_question(self, question: str):
        """处理快捷问题"""
        # 检查查询限制
        max_queries = self.config.get("max_daily_queries", 500)
        if st.session_state.query_count >= max_queries:
            st.error(f"❌ 今日查询次数已达上限 ({max_queries} 次)")
            return
        
        # 添加用户消息
        SessionManager.add_message("user", question)
        
        # 生成AI回答
        with st.spinner("🤔 AI思考中..."):
            time.sleep(self.config.get("chat_speed", 1.0))
            
            context = self._get_document_context(question)
            response = self.generator.generate_response(question, context)
        
        SessionManager.add_message("assistant", response)
        st.session_state.query_count += 1
        st.rerun()
    
    def render_chat_input(self):
        """渲染聊天输入框"""
        max_chars = self.config.get("max_message_length", 5000)
        if prompt := st.chat_input("💬 输入消息...", max_chars=max_chars, key="desktop_chat_input"):
            self._handle_chat_input(prompt)
    
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
    
    def render_sidebar(self):
        """渲染侧边栏"""
        # 文件上传
        self.render_file_upload()
        
        # 已上传文档
        self.render_uploaded_documents()
        
        # 预留空间提示
        self.render_sidebar_placeholder()
    
    def render_sidebar_placeholder(self):
        """渲染侧边栏预留空间"""
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("#### 💡 更多功能")
        
        st.info("""
        🚀 **即将推出更多功能:**
        
        • 📊 实时数据分析
        • 🔍 智能搜索建议  
        • 📈 使用统计图表
        • 🎯 个性化推荐
        • 🔗 快捷操作面板
        
        💡 系统统计信息已移至 **⚙️ 设置 → 📊 系统** 标签页
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # def render_system_stats(self):
    #     """渲染系统统计 - 已移至设置面板"""
    #     # 此功能已移至设置面板的"📊 系统"标签页
    #     pass
    
    def render_file_upload(self):
        """渲染文件上传区域"""
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("#### 📄 文档上传")
        
        # 检查文档数量限制
        max_docs = self.config.get("max_documents", 20)
        current_docs = len(st.session_state.uploaded_documents)
        
        if current_docs >= max_docs:
            st.warning(f"⚠️ 已达到最大文档数量限制 ({max_docs} 个)")
            st.info("💡 请删除一些文档后再上传新文档")
        else:
            # 文件上传器
            uploaded_file = st.file_uploader(
                "选择文档",
                type=[ext[1:] for ext in self.config.get("supported_formats", [])],
                help=f"支持格式: {', '.join(self.config.get('supported_formats', []))}\n最大文件大小: {self.config.get('max_file_size', 50)}MB",
                key="desktop_file_uploader"
            )
            
            if uploaded_file is not None:
                self._handle_file_upload(uploaded_file)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _handle_file_upload(self, uploaded_file):
        """处理文件上传"""
        # 显示文件信息
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.info(f"📄 **{uploaded_file.name}**\n📊 大小: {file_size_mb:.2f} MB")
        
        # 检查文件大小
        max_size = self.config.get("max_file_size", 50)
        if uploaded_file.size > max_size * 1024 * 1024:
            st.error(f"❌ 文件过大，最大支持 {max_size}MB")
            return
        
        # 上传按钮
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 上传", type="primary", use_container_width=True, key="desktop_upload_btn"):
                self._process_file_upload(uploaded_file)
        
        with col2:
            if st.button("❌ 取消", use_container_width=True, key="desktop_cancel_btn"):
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
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("#### 📋 已上传文档")
            
            for doc_id, doc_info in st.session_state.uploaded_documents.items():
                UIComponents.render_document_card(doc_id, doc_info, show_delete=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
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
            f"💬 <b>{self.config.get('system_name')}</b> {self.config.get('version')} | "
            f"🖥️ 桌面端完整版 | 🌐 全平台支持<br>"
            f"📊 查询: {st.session_state.query_count}/{self.config.get('max_daily_queries')} | "
            f"📄 文档: {len(st.session_state.uploaded_documents)}/{self.config.get('max_documents')} | "
            f"💬 对话: {len(st.session_state.messages)//2} 轮"
            f"</div>",
            unsafe_allow_html=True
        )
    
    def render_complete_interface(self):
        """渲染完整的桌面端界面"""
        # 应用CSS样式
        self.apply_desktop_css()
        
        # 渲染头部
        self.render_header()
        
        # 渲染主要布局
        self.render_main_layout()
        
        # 渲染页脚
        self.render_footer()

# 创建桌面端界面实例
desktop_interface = DesktopInterface()