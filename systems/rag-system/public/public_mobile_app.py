"""
公网移动端RAG应用
专为公网访问优化的简洁移动端界面
"""

import streamlit as st
import sys
import os
import time
import datetime

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

from base_components import SessionManager, DocumentProcessor, ResponseGenerator, system_config
from user_management import auth_interface, user_manager
from language_config import get_text, get_language_options

# 页面配置
st.set_page_config(
    page_title="💬 RAG智能对话",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded"
)

class PublicMobileInterface:
    """公网移动端界面"""
    
    def __init__(self):
        self.processor = DocumentProcessor()
        self.generator = ResponseGenerator()
    
    def get_current_language(self):
        """获取当前用户语言设置"""
        user_info = st.session_state.get("user_info", {})
        settings = user_info.get("settings", {})
        return settings.get("language", "zh-CN")
    
    def t(self, key: str) -> str:
        """获取当前语言的文本"""
        return get_text(key, self.get_current_language())
    
    def apply_mobile_css(self):
        """应用移动端CSS样式"""
        # 获取用户主题设置
        user_info = st.session_state.get("user_info", {})
        settings = user_info.get("settings", {})
        theme = settings.get("theme", "light")
        
        # 根据主题设置CSS变量
        if theme == "dark":
            theme_css = """
            :root {
                --bg-color: #0e1117;
                --secondary-bg: #262730;
                --text-color: #fafafa;
                --border-color: #464853;
                --accent-color: #ff4b4b;
            }
            """
        else:
            theme_css = """
            :root {
                --bg-color: #ffffff;
                --secondary-bg: #f0f2f6;
                --text-color: #262730;
                --border-color: #d4d4d4;
                --accent-color: #ff4b4b;
            }
            """
        
        st.markdown(f"""
        <style>
        {theme_css}
        
        /* Emoji字体支持 */
        * {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji' !important;
        }}
        
        /* 主题应用 */
        .stApp {{
            background-color: var(--bg-color);
            color: var(--text-color);
        }}
        
        .stSidebar {{
            background-color: var(--secondary-bg);
        }}
        
        .stTextInput > div > div > input {{
            background-color: var(--secondary-bg);
            color: var(--text-color);
            border-color: var(--border-color);
        }}
        
        .stSelectbox > div > div > div {{
            background-color: var(--secondary-bg);
            color: var(--text-color);
        }}
        
        /* 隐藏Streamlit默认元素 */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stDeployButton {{display: none;}}
        
        /* 移动端优化 */
        .main .block-container {{
            padding: 1rem;
            max-width: 100%;
        }}
        
        /* 消息气泡样式 */
        .user-message {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 12px 16px;
            border-radius: 18px 18px 4px 18px;
            margin: 8px 0;
            margin-left: 10%;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            color: #1565c0;
        }}
        
        .assistant-message {{
            background: linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%);
            padding: 12px 16px;
            border-radius: 18px 18px 18px 4px;
            margin: 8px 0;
            margin-right: 10%;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            color: #2e7d32;
        }}
        
        .message-header {{
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 4px;
        }}
        
        .user-header {{
            color: #1976d2;
        }}
        
        .assistant-header {{
            color: #388e3c;
        }}
        
        .message-content {{
            color: #333;
            line-height: 1.5;
        }}
        
        /* 建议按钮样式 */
        .suggestion-container {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 15px;
            margin: 15px 0;
            border: 1px solid #e0e0e0;
        }}
        
        /* 文档卡片样式 */
        .document-card {{
            background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 12px;
            margin: 8px 0;
            border-left: 4px solid #007bff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        /* 用户信息卡片 */
        .user-info-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        
        /* 页脚样式 */
        .footer-info {{
            text-align: center;
            color: #666;
            font-size: 0.8rem;
            padding: 20px 0;
            border-top: 1px solid #e0e0e0;
            margin-top: 30px;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    def render_user_header(self):
        """渲染用户头部信息"""
        if "user_info" in st.session_state:
            user_info = st.session_state.user_info
            role_icon = "👑" if user_info["role"] == "admin" else "👤"
            
            # 标题 - 使用HTML确保emoji显示
            st.markdown("""
            <h1 style="font-size: 2rem; margin-bottom: 0.5rem;">
                <span style="font-family: 'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji', sans-serif;">🤖</span> 
                RAG智能对话
            </h1>
            """, unsafe_allow_html=True)
            st.markdown(f"### 欢迎，{user_info['display_name']} {role_icon}")
            
            # 功能按钮行 - 统一大小排成一排
            if user_info["role"] == "admin":
                # 管理员：5个按钮
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    if st.button("⚙️", key="settings_btn", help="设置", use_container_width=True):
                        st.session_state.show_user_settings = True
                        st.rerun()
                
                with col2:
                    # 智能建议按钮（只在没有对话记录时显示）
                    if len(st.session_state.messages) <= 1:
                        if st.button("💡", key="suggestions_btn", help="智能建议", use_container_width=True):
                            st.session_state.show_suggestions_dialog = True
                            st.rerun()
                    else:
                        st.button("💡", key="suggestions_btn_disabled", help="智能建议", use_container_width=True, disabled=True)
                
                with col3:
                    if st.button("🛠️", key="admin_btn", help="系统管理", use_container_width=True):
                        st.session_state.show_admin_panel = True
                        st.rerun()
                
                with col4:
                    if st.button("🚪", key="logout_btn", help="退出", use_container_width=True, type="secondary"):
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
                
                with col5:
                    if st.button("📤", key="upload_btn", help="上传文档", use_container_width=True):
                        st.session_state.show_upload_dialog = True
                        st.rerun()
            else:
                # 普通用户：4个按钮
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("⚙️", key="settings_btn", help="设置", use_container_width=True):
                        st.session_state.show_user_settings = True
                        st.rerun()
                
                with col2:
                    # 智能建议按钮（只在没有对话记录时显示）
                    if len(st.session_state.messages) <= 1:
                        if st.button("💡", key="suggestions_btn", help="智能建议", use_container_width=True):
                            st.session_state.show_suggestions_dialog = True
                            st.rerun()
                    else:
                        st.button("💡", key="suggestions_btn_disabled", help="智能建议", use_container_width=True, disabled=True)
                
                with col3:
                    if st.button("🚪", key="logout_btn", help="退出", use_container_width=True, type="secondary"):
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
                
                with col4:
                    if st.button("📤", key="upload_btn", help="上传文档", use_container_width=True):
                        st.session_state.show_upload_dialog = True
                        st.rerun()
    
    def render_chat_messages(self):
        """渲染聊天消息"""
        st.markdown("### 💬 对话记录")
        
        # 获取用户设置
        show_timestamps = True  # 默认显示时间戳
        if "user_info" in st.session_state:
            username = st.session_state.user_info.get("username", "")
            if username:
                user_settings = user_manager.get_user_settings(username)
                show_timestamps = user_settings.get("show_timestamps", True)
        
        for message in st.session_state.messages:
            timestamp_text = f" {message.get('timestamp', '')}" if show_timestamps else ""
            
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <div class="message-header user-header">👤 您{timestamp_text}</div>
                    <div class="message-content">{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    <div class="message-header assistant-header">🤖 AI助手{timestamp_text}</div>
                    <div class="message-content">{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_suggestions_dialog(self):
        """渲染智能建议弹窗"""
        # 智能建议弹窗
        if st.session_state.get("show_suggestions_dialog", False):
            with st.container():
                st.markdown("---")
                st.markdown("### 💡 智能建议")
                
                suggestions = [
                    "你好，介绍一下自己",
                    "什么是RAG技术？",
                    "如何上传和分析文档？",
                    "系统有哪些功能？",
                    "支持哪些文件格式？",
                    "如何进行多轮对话？"
                ]
                
                st.markdown("**点击下方问题快速开始对话：**")
                
                # 两列显示建议
                col1, col2 = st.columns(2)
                for i, suggestion in enumerate(suggestions):
                    with [col1, col2][i % 2]:
                        if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                            self._handle_user_input(suggestion)
                            st.session_state.show_suggestions_dialog = False
                            st.rerun()
                
                # 关闭按钮
                if st.button("✖️ 关闭", key="close_suggestions_dialog"):
                    st.session_state.show_suggestions_dialog = False
                    st.rerun()
                
                st.markdown("---")
    

    def render_upload_dialog(self):
        """渲染上传文档弹窗"""
        if st.session_state.get("show_upload_dialog", False):
            # 检查用户权限和限制
            user_info = st.session_state.get("user_info", {})
            user_limits = self._get_user_limits(user_info)
            
            current_docs = len(st.session_state.get("uploaded_documents", {}))
            max_docs = user_limits.get("max_documents", 5)
            
            # 使用弹窗容器
            with st.container():
                st.markdown("---")
                st.markdown("### 📤 上传文档")
                
                # 文件上传
                if current_docs >= max_docs:
                    st.warning(f"⚠️ 已达到文档数量限制 ({max_docs} 个)")
                    st.info("💡 请在设置中删除一些文档后再上传新文档")
                else:
                    uploaded_file = st.file_uploader(
                        "选择文档",
                        type=["pdf", "docx", "txt", "md", "pptx", "csv"],
                        help=f"支持PDF、Word、文本文件等，最大{user_limits.get('max_file_size', 10)}MB",
                        key="upload_dialog_file"
                    )
                    
                    if uploaded_file is not None:
                        # 检查文件大小
                        file_size_mb = uploaded_file.size / (1024 * 1024)
                        max_size = user_limits.get('max_file_size', 10)
                        
                        if file_size_mb > max_size:
                            st.error(f"❌ 文件过大 ({file_size_mb:.1f}MB)，您的限制是 {max_size}MB")
                        else:
                            st.info(f"📄 **{uploaded_file.name}** ({file_size_mb:.2f} MB)")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if st.button("🚀 上传分析", type="primary", use_container_width=True):
                                    self._process_file_upload(uploaded_file)
                                    st.session_state.show_upload_dialog = False
                                    st.rerun()
                            
                            with col2:
                                if st.button("❌ 取消", use_container_width=True):
                                    st.session_state.show_upload_dialog = False
                                    st.rerun()
                            
                            with col3:
                                if st.button("📋 查看文档", use_container_width=True):
                                    st.session_state.show_upload_dialog = False
                                    st.session_state.show_user_settings = True
                                    st.rerun()
                
                # 关闭按钮
                if st.button("✖️ 关闭", key="close_upload_dialog"):
                    st.session_state.show_upload_dialog = False
                    st.rerun()
                
                st.markdown("---")
    
    def _get_user_limits(self, user_info):
        """获取用户限制"""
        role = user_info.get("role", "user")
        username = user_info.get("username", "")
        
        # 默认限制
        if role == "admin":
            return {
                "max_documents": 50,
                "max_file_size": 100,
                "daily_queries": 2000,
                "max_message_length": 10000
            }
        elif username == "vip_user":  # VIP用户示例
            return {
                "max_documents": 20,
                "max_file_size": 50,
                "daily_queries": 500,
                "max_message_length": 5000
            }
        else:  # 普通用户
            return {
                "max_documents": 5,
                "max_file_size": 10,
                "daily_queries": 50,
                "max_message_length": 2000
            }
    
    def render_chat_input(self):
        """渲染聊天输入"""
        st.markdown("---")
        
        # 处理临时消息
        if hasattr(st.session_state, 'temp_message'):
            self._handle_user_input(st.session_state.temp_message)
            del st.session_state.temp_message
        
        # 聊天输入框
        if prompt := st.chat_input("💬 输入消息...", key="mobile_chat"):
            self._handle_user_input(prompt)
    
    def _handle_user_input(self, prompt: str):
        """处理用户输入"""
        # 添加用户消息
        SessionManager.add_message("user", prompt)
        
        # 生成AI回答
        with st.spinner("🤔 AI思考中..."):
            time.sleep(0.5)  # 简化的延迟
            
            # 获取文档上下文
            context = ""
            if st.session_state.uploaded_documents:
                doc_keywords = ["文档", "分析", "总结", "内容"]
                if any(keyword in prompt for keyword in doc_keywords):
                    latest_doc = list(st.session_state.uploaded_documents.values())[-1]
                    context = latest_doc["content"][:1000]  # 限制上下文长度
            
            response = self.generator.generate_response(prompt, context)
        
        SessionManager.add_message("assistant", response)
        st.session_state.query_count = st.session_state.get("query_count", 0) + 1
        st.rerun()
    
    def _process_file_upload(self, uploaded_file):
        """处理文件上传"""
        with st.spinner("🔄 处理中..."):
            try:
                content = self.processor.extract_text_from_file(uploaded_file)
                
                if content and content.strip():
                    # 添加文档
                    doc_id = SessionManager.add_document(
                        uploaded_file.name,
                        content,
                        uploaded_file.size
                    )
                    
                    st.success("✅ 上传成功！")
                    
                    # 自动分析
                    analysis_prompt = f"已上传文档 '{uploaded_file.name}'，请分析内容。"
                    self._handle_user_input(analysis_prompt)
                else:
                    st.error("❌ 文档处理失败")
            except Exception as e:
                st.error(f"❌ 上传失败: {str(e)}")
    
    def render_footer(self):
        """渲染页脚"""
        query_count = st.session_state.get("query_count", 0)
        doc_count = len(st.session_state.get("uploaded_documents", {}))
        
        st.markdown(f"""
        <div class="footer-info">
            💬 RAG智能对话 v3.2 | 📊 查询: {query_count} | 📄 文档: {doc_count}<br>
            🌐 公网移动端 | 🔐 安全访问
        </div>
        """, unsafe_allow_html=True)
    
    def render_complete_interface(self):
        """渲染完整界面"""
        # 应用CSS
        self.apply_mobile_css()
        
        # 用户头部
        self.render_user_header()
        
        # 上传文档弹窗
        self.render_upload_dialog()
        

        # 聊天消息
        self.render_chat_messages()
        
        # 智能建议弹窗
        self.render_suggestions_dialog()
        
        # 聊天输入
        self.render_chat_input()
        
        # 页脚
        self.render_footer()

def render_sidebar():
    """渲染侧边栏"""
    user_info = st.session_state.get("user_info", {})
    username = user_info.get("username", "")
    display_name = user_info.get("display_name", username)
    
    # 用户信息
    st.markdown("### 👤 用户信息")
    st.info(f"**用户**: {display_name}")
    
    role_name = "管理员" if user_info.get('role') == 'admin' else '普通用户'
    role_icon = "👑" if user_info.get('role') == 'admin' else '👤'
    st.info(f"**角色**: {role_icon} {role_name}")
    
    # 自动登录状态
    if st.session_state.get("session_token"):
        st.success("🔒 自动登录已启用")
    else:
        st.info("🔓 自动登录未启用")
    
    st.markdown("---")
    
    # 快捷操作
    st.markdown("### ⚡ 快捷操作")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚙️ 设置", use_container_width=True):
            st.session_state.show_user_settings = True
            st.rerun()
    
    with col2:
        if st.button("📤 上传", use_container_width=True):
            st.session_state.show_upload_dialog = True
            st.rerun()
    
    # 管理员功能
    if user_info.get('role') == 'admin':
        if st.button("🛠️ 管理", use_container_width=True):
            st.session_state.show_admin_panel = True
            st.rerun()
    
    # 智能建议
    if not st.session_state.get("messages", []):
        if st.button("💡 建议", use_container_width=True):
            st.session_state.show_suggestions = True
            st.rerun()
    
    # 退出登录
    st.markdown("---")
    if st.button("🚪 退出登录", use_container_width=True, type="secondary"):
        # 清理会话状态
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def render_main_chat_area(interface):
    """渲染主聊天区域"""
    # 检查特殊页面
    if st.session_state.get("show_user_settings", False):
        render_user_settings()
        return
    
    if st.session_state.get("show_admin_panel", False):
        render_admin_panel()
        return
    
    # 主聊天界面
    st.markdown("## 💬 智能对话")
    
    # 创建聊天容器
    with st.container():
        st.markdown("""
        <div style="
            border: 2px solid var(--border-color, #d4d4d4);
            border-radius: 10px;
            padding: 20px;
            background-color: var(--secondary-bg, #f0f2f6);
            min-height: 500px;
        ">
        """, unsafe_allow_html=True)
        
        # 渲染聊天消息
        interface.render_chat_messages()
        
        # 智能建议弹窗
        interface.render_suggestions_dialog()
        
        # 上传文档弹窗
        interface.render_upload_dialog()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 聊天输入框（在容器外面）
    st.markdown("---")
    interface.render_chat_input()

def main():
    """主程序"""
    # 用户认证
    if not auth_interface.check_authentication():
        return
    
    # 初始化会话状态
    SessionManager.init_session_state()
    
    # 渲染主界面（带侧边栏）
    interface = PublicMobileInterface()
    interface.apply_mobile_css()
    
    # 侧边栏内容
    with st.sidebar:
        render_sidebar()
    
    # 主内容区域
    render_main_chat_area(interface)

def render_user_settings():
    """渲染用户设置"""
    # 返回按钮
    if st.button("⬅️ 返回主界面", type="primary", key="return_from_settings"):
        st.session_state.show_user_settings = False
        st.rerun()
    
    st.markdown("## ⚙️ 个人设置")
    
    user_info = st.session_state.get("user_info", {})
    username = user_info.get("username", "")
    
    # 使用标签页组织设置
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 个人信息", "🎨 界面设置", "⚡ 功能设置", "📄 文档管理", "📊 使用统计"])
    
    with tab1:
        st.markdown("### 👤 个人信息")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**用户名**: {username}")
            st.info(f"**显示名称**: {user_info.get('display_name', username)}")
        with col2:
            role_name = "管理员" if user_info.get('role') == 'admin' else '普通用户'
            role_icon = "👑" if user_info.get('role') == 'admin' else '👤'
            st.info(f"**角色**: {role_icon} {role_name}")
            st.info(f"**权限**: {'完整权限' if user_info.get('role') == 'admin' else '基础权限'}")
        
        # 修改显示名称 - 使用折叠显示
        with st.expander("✏️ 修改显示名称", expanded=False):
            with st.form("update_display_name"):
                new_display_name = st.text_input(
                    "新显示名称",
                    value=user_info.get('display_name', username),
                    help="在系统中显示的名称"
                )
                if st.form_submit_button("💾 保存名称", type="primary"):
                    if new_display_name and new_display_name != user_info.get('display_name'):
                        # 更新显示名称
                        if user_manager.update_display_name(username, new_display_name):
                            st.session_state.user_info['display_name'] = new_display_name
                            st.success("✅ 显示名称更新成功")
                            st.rerun()
                        else:
                            st.error("❌ 显示名称更新失败")
                    else:
                        st.info("💡 显示名称未改变")
        
        # 修改密码 - 使用折叠显示
        with st.expander("🔒 修改密码", expanded=False):
            with st.form("change_password"):
                current_password = st.text_input("当前密码", type="password")
                new_password = st.text_input("新密码", type="password", help="至少6个字符")
                confirm_password = st.text_input("确认新密码", type="password")
                
                if st.form_submit_button("🔄 修改密码", type="secondary"):
                    if not current_password or not new_password:
                        st.error("❌ 请填写完整信息")
                    elif new_password != confirm_password:
                        st.error("❌ 两次密码输入不一致")
                    elif len(new_password) < 6:
                        st.error("❌ 新密码至少6个字符")
                    else:
                        # 验证当前密码并更新
                        if user_manager.change_password(username, current_password, new_password):
                            st.success("✅ 密码修改成功")
                        else:
                            st.error("❌ 当前密码错误")
        
        # 清空对话
        st.markdown("#### 🗑️ 对话管理")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ 清空当前对话", use_container_width=True, type="secondary"):
                SessionManager.clear_messages()
                st.success("✅ 对话已清空")
                st.rerun()
        with col2:
            if st.button("📊 对话统计", use_container_width=True):
                msg_count = len(st.session_state.get("messages", []))
                st.info(f"📊 当前对话共 {msg_count} 条消息")
    
    with tab2:
        st.markdown("### 🎨 界面设置")
        
        current_settings = user_manager.get_user_settings(username)
        
        # 主题设置
        theme_options = {
            "light": "🌞 浅色模式",
            "dark": "🌙 深色模式", 
            "auto": "🔄 自动跟随系统"
        }
        
        selected_theme = st.selectbox(
            "界面主题",
            options=list(theme_options.keys()),
            format_func=lambda x: theme_options[x],
            index=list(theme_options.keys()).index(current_settings.get("theme", "light")),
            help="选择界面颜色主题"
        )
        
        # 字体大小
        font_size = st.slider(
            "字体大小",
            min_value=12,
            max_value=20,
            value=16,
            step=1,
            help="调整界面字体大小"
        )
        
        # 时间戳显示
        show_timestamps = st.checkbox(
            "显示消息时间戳",
            value=current_settings.get("show_timestamps", True),
            help="在消息中显示发送时间"
        )
        
        # 自动滚动
        auto_scroll = st.checkbox(
            "自动滚动到新消息",
            value=current_settings.get("auto_scroll", True),
            help="新消息出现时自动滚动到底部"
        )
        
        # 语言设置
        language_options = {
            "zh-CN": "🇨🇳 简体中文",
            "en-US": "🇺🇸 English"
        }
        
        selected_language = st.selectbox(
            "界面语言",
            options=list(language_options.keys()),
            format_func=lambda x: language_options[x],
            index=list(language_options.keys()).index(current_settings.get("language", "zh-CN")),
            help="选择界面显示语言"
        )
        
        # 检测设置变化并提示
        current_lang = current_settings.get("language", "zh-CN")
        current_theme = current_settings.get("theme", "light")
        
        if selected_language != current_lang or selected_theme != current_theme:
            if selected_language != current_lang and selected_theme != current_theme:
                st.info("🔄 语言和主题已更改，点击保存后将自动刷新页面")
            elif selected_language != current_lang:
                st.info("🌐 语言已更改，点击保存后将自动刷新页面")
            elif selected_theme != current_theme:
                st.info("🎨 主题已更改，点击保存后将自动刷新页面")
        
        # 检测设置变化
        settings_changed = (
            selected_theme != current_theme or
            selected_language != current_lang or
            font_size != current_settings.get("font_size", 14) or
            show_timestamps != current_settings.get("show_timestamps", True) or
            auto_scroll != current_settings.get("auto_scroll", True)
        )

        # 保存界面设置
        if st.button("💾 保存界面设置", type="primary"):
            try:
                new_settings = {
                    "theme": selected_theme,
                    "font_size": font_size,
                    "show_timestamps": show_timestamps,
                    "auto_scroll": auto_scroll,
                    "language": selected_language
                }
                
                # 检查是否有需要刷新页面的变化
                theme_changed = selected_theme != current_theme
                lang_changed = selected_language != current_lang
                
                # 保存设置
                user_manager.update_user_settings(username, new_settings)
                st.session_state.user_info["settings"].update(new_settings)
                
                # 显示保存成功消息
                if theme_changed or lang_changed:
                    st.success("✅ 界面设置已更新，正在刷新页面...")
                    st.rerun()
                else:
                    st.success("✅ 界面设置保存成功")
                    
            except Exception as e:
                st.error(f"❌ 保存设置时出错: {str(e)}")
    
    with tab3:
        st.markdown("### ⚡ 功能设置")
        
        # 显示用户限制信息
        user_limits = PublicMobileInterface()._get_user_limits(user_info)
        
        st.markdown("#### 📊 您的账户限制")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📄 **文档数量限制**: {user_limits['max_documents']} 个")
            st.info(f"📊 **文件大小限制**: {user_limits['max_file_size']} MB")
        with col2:
            st.info(f"📈 **每日查询限制**: {user_limits['daily_queries']} 次")
            st.info(f"📝 **消息长度限制**: {user_limits['max_message_length']} 字符")
        
        if user_info.get("role") != "admin":
            st.warning("⚠️ 普通用户无法修改使用限制，如需提升权限请联系管理员")
        
        # AI回答速度（所有用户都可以调整）
        chat_speed = st.slider(
            "AI回答速度",
            min_value=0.1,
            max_value=3.0,
            value=current_settings.get("chat_speed", 1.0),
            step=0.1,
            help="控制AI回答的延迟时间，数值越小回答越快"
        )
        
        # 速度状态显示
        if chat_speed <= 0.5:
            st.success("⚡ 极快模式 - 即时响应")
        elif chat_speed <= 1.0:
            st.info("🚀 快速模式 - 快速响应")
        elif chat_speed <= 2.0:
            st.warning("🐢 正常模式 - 标准响应")
        else:
            st.error("🐌 慢速模式 - 深度思考")
        
        # 通知设置
        notifications = st.checkbox(
            "启用系统通知",
            value=current_settings.get("notifications", True),
            help="是否接收系统通知和提醒"
        )
        
        # 智能建议
        show_suggestions = st.checkbox(
            "显示智能建议",
            value=current_settings.get("show_suggestions", True),
            help="在对话开始时显示智能建议"
        )
        
        # 自动分析文档
        auto_analyze = st.checkbox(
            "自动分析上传文档",
            value=current_settings.get("auto_analyze", True),
            help="上传文档后自动进行内容分析"
        )
        
        # 自动登录管理
        st.markdown("#### 🔒 自动登录管理")
        
        current_auto_login = bool(st.session_state.get("session_token"))
        
        col1, col2 = st.columns([3, 1])
        with col1:
            enable_auto_login = st.checkbox(
                "启用自动登录（7天有效）",
                value=current_auto_login,
                help="启用后，7天内无需重复登录"
            )
        
        with col2:
            if st.button("💾 应用", key="apply_auto_login"):
                if enable_auto_login and not current_auto_login:
                    # 启用自动登录 - 创建令牌
                    username = st.session_state.user_info.get('username')
                    token = user_manager.create_session_token(username)
                    st.session_state.session_token = token
                    st.success("✅ 自动登录已启用")
                    st.rerun()
                elif not enable_auto_login and current_auto_login:
                    # 禁用自动登录 - 撤销令牌
                    token = st.session_state.get("session_token")
                    if token:
                        user_manager.revoke_session_token(token)
                        st.session_state.session_token = None
                        st.success("✅ 自动登录已禁用")
                        st.rerun()
                else:
                    st.info("💡 设置未改变")
        
        # 状态显示
        if current_auto_login:
            st.success("✅ 当前已启用自动登录（7天有效）")
        else:
            st.info("ℹ️ 当前未启用自动登录")
        
        # 保存功能设置
        if st.button("💾 保存功能设置", type="primary"):
            function_settings = {
                "chat_speed": chat_speed,
                "notifications": notifications,
                "show_suggestions": show_suggestions,
                "auto_analyze": auto_analyze
            }
            user_manager.update_user_settings(username, function_settings)
            st.session_state.user_info["settings"].update(function_settings)
            st.success("✅ 功能设置保存成功")
    
    with tab4:
        st.markdown("### 📄 文档管理")
        
        # 检查用户权限和限制
        user_limits = PublicMobileInterface()._get_user_limits(user_info)
        
        current_docs = len(st.session_state.get("uploaded_documents", {}))
        max_docs = user_limits.get("max_documents", 5)
        
        # 显示用户限制信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 文档数量", f"{current_docs}/{max_docs}")
        with col2:
            st.metric("📊 文件大小限制", f"{user_limits.get('max_file_size', 10)}MB")
        with col3:
            st.metric("📈 今日查询", f"{st.session_state.get('query_count', 0)}/{user_limits.get('daily_queries', 50)}")
        
        # 已上传文档列表
        if st.session_state.get("uploaded_documents"):
            st.markdown("#### 📋 已上传文档")
            
            for doc_id, doc_info in st.session_state.uploaded_documents.items():
                with st.expander(f"📄 {doc_info['name'][:40]}{'...' if len(doc_info['name']) > 40 else ''}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**文件名**: {doc_info['name']}")
                        st.write(f"**大小**: {doc_info['size']/(1024*1024):.2f} MB")
                        st.write(f"**上传时间**: {doc_info['upload_time']}")
                        st.write(f"**内容预览**: {doc_info['content'][:100]}...")
                    
                    with col2:
                        if st.button("🗑️ 删除", key=f"del_setting_{doc_id}", type="secondary"):
                            SessionManager.remove_document(doc_id)
                            st.success("✅ 文档已删除")
                            st.rerun()
        else:
            st.info("📄 暂无上传文档")
            st.markdown("💡 点击主界面的 **📤** 按钮上传文档")
        
        # 批量操作
        if st.session_state.get("uploaded_documents"):
            st.markdown("#### 🔧 批量操作")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ 删除所有文档", use_container_width=True, type="secondary"):
                    st.session_state.uploaded_documents = {}
                    st.success("✅ 所有文档已删除")
                    st.rerun()
            
            with col2:
                if st.button("📊 文档统计", use_container_width=True):
                    total_size = sum(doc['size'] for doc in st.session_state.uploaded_documents.values())
                    st.info(f"📊 总计 {len(st.session_state.uploaded_documents)} 个文档，{total_size/(1024*1024):.2f} MB")
    
    with tab5:
        st.markdown("### 📊 使用统计")
        
        # 基础统计
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "💬 对话轮次", 
                len(st.session_state.get("messages", [])) // 2,
                help="当前会话的对话轮次"
            )
        with col2:
            st.metric(
                "📄 文档数量", 
                len(st.session_state.get("uploaded_documents", {})),
                help="已上传的文档数量"
            )
        with col3:
            st.metric(
                "📈 查询次数", 
                st.session_state.get("query_count", 0),
                help="本次会话的查询次数"
            )
        
        # 详细统计
        st.markdown("#### 📋 详细信息")
        
        # 文档统计
        if st.session_state.get("uploaded_documents"):
            st.markdown("**📄 文档列表:**")
            for doc_id, doc_info in st.session_state.uploaded_documents.items():
                st.write(f"• {doc_info['name']} ({doc_info['size']/(1024*1024):.1f}MB) - {doc_info['upload_time']}")
        else:
            st.info("📄 暂无上传文档")
        
        # 会话信息
        st.markdown("**💬 会话信息:**")
        st.write(f"• 消息总数: {len(st.session_state.get('messages', []))}")
        st.write(f"• 用户消息: {len([m for m in st.session_state.get('messages', []) if m['role'] == 'user'])}")
        st.write(f"• AI回复: {len([m for m in st.session_state.get('messages', []) if m['role'] == 'assistant'])}")
        
        # 数据管理
        st.markdown("#### 🔧 数据管理")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ 清空对话", use_container_width=True, type="secondary"):
                SessionManager.clear_messages()
                st.success("✅ 对话记录已清空")
                st.rerun()
        
        with col2:
            if st.button("📄 删除所有文档", use_container_width=True, type="secondary"):
                st.session_state.uploaded_documents = {}
                st.success("✅ 所有文档已删除")
                st.rerun()
        
        # 导出数据
        st.markdown("#### 📤 数据导出")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 导出对话记录", use_container_width=True):
                st.info("📋 对话记录导出功能开发中...")
        
        with col2:
            if st.button("📊 导出使用报告", use_container_width=True):
                st.info("📊 使用报告导出功能开发中...")
    
    # 返回按钮
    st.markdown("---")
    if st.button("⬅️ 返回主界面", type="primary", key="return_from_settings_bottom"):
        st.session_state.show_user_settings = False
        st.rerun()

def render_admin_panel():
    """渲染管理员面板"""
    st.markdown("## 🛠️ 管理员面板")
    
    # 使用标签页组织管理功能
    tab1, tab2, tab3, tab4 = st.tabs(["📊 系统监控", "👥 用户管理", "⚙️ 用户限制", "🔧 系统操作"])
    
    with tab1:
        st.markdown("### 📊 系统监控")
        
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🖥️ CPU使用率", f"{cpu_percent:.1f}%")
                st.progress(cpu_percent / 100)
            with col2:
                st.metric("💾 内存使用率", f"{memory.percent:.1f}%")
                st.progress(memory.percent / 100)
            with col3:
                disk_percent = (disk.used / disk.total) * 100
                st.metric("💽 磁盘使用率", f"{disk_percent:.1f}%")
                st.progress(disk_percent / 100)
            
            # 服务状态
            st.markdown("#### 🚀 服务状态")
            services = [
                {"name": "公网移动端", "port": 51659, "status": "🟢 运行中"},
                {"name": "通用自适应版", "port": 51659, "status": "🟢 运行中"},
                {"name": "Cloudflare隧道", "port": "N/A", "status": "🟢 连接中"}
            ]
            
            for service in services:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{service['name']}**")
                with col2:
                    st.write(f"端口: {service['port']}")
                with col3:
                    st.write(service['status'])
        
        except Exception as e:
            st.error(f"❌ 系统监控数据获取失败: {str(e)}")
    
    with tab2:
        st.markdown("### 👥 用户管理")
        
        users = user_manager.get_all_users()
        
        # 用户统计
        admin_count = sum(1 for user in users.values() if user["role"] == "admin")
        user_count = sum(1 for user in users.values() if user["role"] == "user")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👑 管理员", admin_count)
        with col2:
            st.metric("👤 普通用户", user_count)
        with col3:
            st.metric("📊 总用户数", len(users))
        
        # 用户列表
        st.markdown("#### 📋 用户列表")
        
        for username, user_info in users.items():
            with st.expander(f"{'👑' if user_info['role'] == 'admin' else '👤'} {user_info['display_name']} (@{username})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**角色**: {user_info['role']}")
                    st.write(f"**创建时间**: {user_info['created_at'][:19]}")
                    st.write(f"**最后登录**: {user_info['last_login'][:19] if user_info['last_login'] else '从未登录'}")
                
                with col2:
                    # 获取用户限制
                    interface = PublicMobileInterface()
                    limits = interface._get_user_limits({"role": user_info["role"], "username": username})
                    st.write(f"**文档限制**: {limits['max_documents']} 个")
                    st.write(f"**文件大小**: {limits['max_file_size']} MB")
                    st.write(f"**每日查询**: {limits['daily_queries']} 次")
        
        # 创建新用户
        st.markdown("#### ➕ 创建新用户")
        
        with st.form("create_user_admin"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("用户名")
                new_password = st.text_input("密码", type="password")
            
            with col2:
                new_display_name = st.text_input("显示名称")
                new_role = st.selectbox("用户角色", ["user", "admin", "vip_user"])
            
            if st.form_submit_button("✅ 创建用户", type="primary"):
                if new_username and new_password:
                    if user_manager.create_user(new_username, new_password, new_role, new_display_name):
                        st.success(f"✅ 用户 {new_username} 创建成功")
                        st.rerun()
                    else:
                        st.error("❌ 用户名已存在")
                else:
                    st.error("❌ 请填写完整信息")
    
    with tab3:
        st.markdown("### ⚙️ 用户限制管理")
        
        st.markdown("#### 📊 当前限制配置")
        
        # 显示不同用户类型的限制
        interface = PublicMobileInterface()
        
        user_types = [
            {"name": "👑 管理员", "role": "admin", "username": "admin"},
            {"name": "💎 VIP用户", "role": "user", "username": "vip_user"},
            {"name": "👤 普通用户", "role": "user", "username": "regular_user"}
        ]
        
        for user_type in user_types:
            limits = interface._get_user_limits({"role": user_type["role"], "username": user_type["username"]})
            
            with st.expander(f"{user_type['name']} 限制配置"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"📄 **文档数量**: {limits['max_documents']} 个")
                    st.info(f"📊 **文件大小**: {limits['max_file_size']} MB")
                
                with col2:
                    st.info(f"📈 **每日查询**: {limits['daily_queries']} 次")
                    st.info(f"📝 **消息长度**: {limits['max_message_length']} 字符")
        
        # 用户升级功能
        st.markdown("#### 🔄 用户权限管理")
        
        users = user_manager.get_all_users()
        user_list = [f"{info['display_name']} (@{username})" for username, info in users.items()]
        
        selected_user = st.selectbox("选择用户", user_list)
        
        if selected_user:
            username = selected_user.split("(@")[1].rstrip(")")
            current_user = users[username]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**当前角色**: {current_user['role']}")
                current_limits = interface._get_user_limits({"role": current_user["role"], "username": username})
                st.write(f"**当前限制**: {current_limits['max_documents']}个文档, {current_limits['max_file_size']}MB文件")
            
            with col2:
                new_role = st.selectbox("修改角色", ["user", "vip_user", "admin"], 
                                      index=["user", "vip_user", "admin"].index(current_user.get("role", "user")))
                
                if st.button("🔄 更新用户权限", type="primary"):
                    st.info("🔄 用户权限更新功能开发中...")
    
    with tab4:
        st.markdown("### 🔧 系统操作")
        
        # 系统维护
        st.markdown("#### 🛠️ 系统维护")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 重启服务", use_container_width=True):
                st.info("🔄 重启功能开发中...")
        
        with col2:
            if st.button("🧹 清理缓存", use_container_width=True):
                st.info("🧹 清理功能开发中...")
        
        with col3:
            if st.button("📊 生成报告", use_container_width=True):
                st.info("📊 报告生成功能开发中...")
        
        # 数据管理
        st.markdown("#### 📄 数据管理")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 备份数据", use_container_width=True):
                st.info("💾 数据备份功能开发中...")
        
        with col2:
            if st.button("📥 恢复数据", use_container_width=True):
                st.info("📥 数据恢复功能开发中...")
        
        # 系统配置
        st.markdown("#### ⚙️ 系统配置")
        
        with st.form("system_config"):
            st.markdown("**全局系统设置**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                system_name = st.text_input("系统名称", value="RAG智能对话")
                maintenance_mode = st.checkbox("维护模式", value=False)
            
            with col2:
                max_concurrent_users = st.number_input("最大并发用户", min_value=10, max_value=1000, value=100)
                enable_registration = st.checkbox("允许用户注册", value=True)
            
            if st.form_submit_button("💾 保存系统配置", type="primary"):
                st.success("✅ 系统配置保存成功")
    
    # 返回按钮
    st.markdown("---")
    if st.button("⬅️ 返回主界面", type="primary", key="return_from_admin"):
        st.session_state.show_admin_panel = False
        st.rerun()

if __name__ == "__main__":
    main()