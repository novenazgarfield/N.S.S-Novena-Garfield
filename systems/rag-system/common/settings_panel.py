"""
设置面板组件
通用的设置界面，支持移动端和桌面端
"""

import streamlit as st
import datetime
from typing import Dict, List, Any, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from base_components import system_config, SessionManager

class SettingsPanel:
    """设置面板管理"""
    
    def __init__(self):
        self.config = system_config
    
    def render_settings_panel(self, device_type: str = "auto"):
        """渲染设置面板"""
        st.markdown("## ⚙️ 系统设置")
        st.markdown("---")
        
        # 根据设备类型调整布局
        if device_type == "mobile":
            self._render_mobile_settings()
        else:
            self._render_desktop_settings()
    
    def _render_mobile_settings(self):
        """移动端设置布局"""
        # 使用手风琴式布局
        with st.expander("🎨 外观设置", expanded=True):
            self._render_appearance_settings()
        
        with st.expander("⚡ 性能设置", expanded=False):
            self._render_performance_settings()
        
        with st.expander("📊 系统信息", expanded=False):
            self._render_system_info()
        
        with st.expander("🤖 AI模型设置", expanded=False):
            self._render_ai_model_settings()
        
        with st.expander("🔧 功能设置", expanded=False):
            self._render_function_settings()
        
        # 操作按钮
        self._render_action_buttons_mobile()
    
    def _render_desktop_settings(self):
        """桌面端设置布局"""
        # 使用标签页布局
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎨 外观", "⚡ 性能", "🤖 AI模型", "📊 系统", "🔧 功能"])
        
        with tab1:
            self._render_appearance_settings()
        
        with tab2:
            self._render_performance_settings()
        
        with tab3:
            self._render_ai_model_settings()
        
        with tab4:
            self._render_system_info()
        
        with tab5:
            self._render_function_settings()
        
        # 操作按钮
        self._render_action_buttons_desktop()
    
    def _render_appearance_settings(self):
        """渲染外观设置"""
        st.markdown("### 🎨 外观设置")
        
        # 界面主题选择
        st.markdown("**🌈 界面主题:**")
        theme_options = ["浅色模式", "深色模式", "自动跟随系统"]
        current_theme_index = 0
        if self.config.get("theme_mode") == "dark":
            current_theme_index = 1
        elif self.config.get("theme_mode") == "auto":
            current_theme_index = 2
            
        selected_theme = st.selectbox(
            "选择主题",
            theme_options,
            index=current_theme_index,
            help="选择界面的颜色主题"
        )
        
        # 更新主题配置
        if selected_theme == "浅色模式":
            self.config.set("theme_mode", "light")
        elif selected_theme == "深色模式":
            self.config.set("theme_mode", "dark")
        elif selected_theme == "自动跟随系统":
            self.config.set("theme_mode", "auto")
        
        # 显示主题预览
        if self.config.get("theme_mode") == "light":
            st.info("🌞 当前使用浅色主题")
        elif self.config.get("theme_mode") == "dark":
            st.info("🌙 当前使用深色主题")
        else:
            st.info("🔄 当前跟随系统主题设置")
        
        # 字体大小调节
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
            value=self.config.get("show_timestamps", True),
            help="在消息中显示发送时间"
        )
        self.config.set("show_timestamps", show_timestamps)
    
    def _render_performance_settings(self):
        """渲染性能设置"""
        st.markdown("### ⚡ 性能设置")
        
        # AI回答速度控制
        st.markdown("**🤖 AI回答速度:**")
        chat_speed = st.slider(
            "回答延迟 (秒)",
            min_value=0.1,
            max_value=5.0,
            value=self.config.get("chat_speed", 1.0),
            step=0.1,
            help="控制AI回答的速度，数值越小回答越快"
        )
        self.config.set("chat_speed", chat_speed)
        
        # 速度状态显示
        if chat_speed <= 0.5:
            st.success("⚡ 极快模式 - 即时响应")
        elif chat_speed <= 1.0:
            st.info("🚀 快速模式 - 快速响应")
        elif chat_speed <= 2.0:
            st.warning("🐢 正常模式 - 标准响应")
        else:
            st.error("🐌 慢速模式 - 深度思考")
        
        # 自动滚动设置
        auto_scroll = st.checkbox(
            "自动滚动到最新消息",
            value=self.config.get("auto_scroll", True),
            help="新消息出现时自动滚动到底部"
        )
        self.config.set("auto_scroll", auto_scroll)
        
        # 消息显示数量
        max_display_messages = st.number_input(
            "最大显示消息数",
            min_value=10,
            max_value=200,
            value=50,
            step=10,
            help="聊天界面最多显示的消息数量"
        )
    
    def _render_system_info(self):
        """渲染系统信息"""
        st.markdown("### 📊 系统信息")
        
        # 使用统计
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "💬 对话轮次",
                len(st.session_state.messages) // 2,
                help="当前会话的对话轮次"
            )
        
        with col2:
            st.metric(
                "📄 文档数量",
                len(st.session_state.uploaded_documents),
                help="已上传的文档数量"
            )
        
        with col3:
            st.metric(
                "📈 查询次数",
                st.session_state.query_count,
                help="今日查询次数"
            )
        
        # 系统状态
        st.markdown("**🖥️ 系统状态:**")
        
        if PSUTIL_AVAILABLE:
            try:
                # 内存使用情况
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("💾 内存使用率", f"{memory_percent:.1f}%")
                with col2:
                    st.metric("💽 可用内存", f"{memory.available / (1024**3):.1f} GB")
                
                # 内存使用进度条
                st.progress(memory_percent / 100)
                
                if memory_percent > 80:
                    st.warning("⚠️ 内存使用率较高，建议清理文档或重启系统")
                elif memory_percent > 90:
                    st.error("❌ 内存使用率过高，系统可能运行缓慢")
                else:
                    st.success("✅ 系统运行正常")
            
            except Exception as e:
                st.info("📊 系统监控信息暂不可用")
        else:
            st.info("📊 系统监控功能需要安装 psutil 库")
        
        # 配置信息
        st.markdown("**⚙️ 当前配置:**")
        config_info = f"""
        - 🏷️ **系统版本**: {self.config.get('version')}
        - 📄 **最大文件大小**: {self.config.get('max_file_size')}MB
        - 📈 **每日查询限制**: {self.config.get('max_daily_queries')}次
        - 📝 **最大消息长度**: {self.config.get('max_message_length')}字符
        - 📚 **最大文档数量**: {self.config.get('max_documents')}个
        - 💬 **最大对话数量**: {self.config.get('max_conversations')}条
        """
        st.markdown(config_info)
        
        # 支持格式
        st.markdown("**📎 支持格式:**")
        formats = ", ".join(self.config.get("supported_formats", []))
        st.code(formats)
    
    def _render_function_settings(self):
        """渲染功能设置"""
        st.markdown("### 🔧 功能设置")
        
        # 文件上传设置
        max_file_size = st.slider(
            "📄 最大文件大小 (MB)",
            min_value=1,
            max_value=100,
            value=self.config.get("max_file_size", 50),
            step=5,
            help="限制上传文件的最大大小"
        )
        self.config.set("max_file_size", max_file_size)
        
        # 文档数量限制
        max_documents = st.slider(
            "📚 最大文档数量",
            min_value=5,
            max_value=50,
            value=self.config.get("max_documents", 20),
            step=5,
            help="同时保存的最大文档数量"
        )
        self.config.set("max_documents", max_documents)
        
        # 查询限制设置
        max_daily_queries = st.number_input(
            "📈 每日最大查询次数",
            min_value=50,
            max_value=2000,
            value=self.config.get("max_daily_queries", 500),
            step=50,
            help="防止过度使用的安全限制"
        )
        self.config.set("max_daily_queries", max_daily_queries)
        
        # 消息长度限制
        max_message_length = st.number_input(
            "📝 最大消息长度",
            min_value=500,
            max_value=10000,
            value=self.config.get("max_message_length", 5000),
            step=500,
            help="单条消息的最大字符数"
        )
        self.config.set("max_message_length", max_message_length)
        
        # 对话历史限制
        max_conversations = st.number_input(
            "💬 最大对话数量",
            min_value=100,
            max_value=5000,
            value=self.config.get("max_conversations", 1000),
            step=100,
            help="保存的最大对话记录数量"
        )
        self.config.set("max_conversations", max_conversations)
        
        # 功能开关
        st.markdown("**🎛️ 功能开关:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_auto_analysis = st.checkbox(
                "自动分析上传文档",
                value=True,
                help="上传文档后自动进行内容分析"
            )
            
            enable_context_search = st.checkbox(
                "启用上下文检索",
                value=True,
                help="在回答问题时检索相关文档内容"
            )
        
        with col2:
            enable_file_preview = st.checkbox(
                "显示文件预览",
                value=True,
                help="上传文件时显示内容预览"
            )
            
            enable_export_function = st.checkbox(
                "启用导出功能",
                value=False,
                help="允许导出对话记录和文档"
            )
    
    def _render_ai_model_settings(self):
        """渲染AI模型设置"""
        st.markdown("### 🤖 AI模型设置")
        
        # 尝试导入AI模型管理器
        try:
            from ai_models import render_model_selector, render_api_key_manager
            
            # 获取当前用户ID（这里需要根据您的用户管理系统调整）
            user_id = st.session_state.get("user_id", "default_user")
            
            # 模型选择器
            st.markdown("**🧠 选择AI模型:**")
            selected_model = render_model_selector(user_id)
            
            if selected_model:
                st.session_state.selected_ai_model = selected_model
            
            st.markdown("---")
            
            # API密钥管理
            render_api_key_manager(user_id)
            
            st.markdown("---")
            
            # 模型参数设置
            st.markdown("**⚙️ 模型参数:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                temperature = st.slider(
                    "🌡️ 创造性 (Temperature)",
                    min_value=0.0,
                    max_value=2.0,
                    value=st.session_state.get("ai_temperature", 0.7),
                    step=0.1,
                    help="控制AI回答的创造性，值越高越有创意"
                )
                st.session_state.ai_temperature = temperature
            
            with col2:
                max_tokens = st.slider(
                    "📝 最大输出长度",
                    min_value=100,
                    max_value=8192,
                    value=st.session_state.get("ai_max_tokens", 2048),
                    step=100,
                    help="控制AI回答的最大长度"
                )
                st.session_state.ai_max_tokens = max_tokens
            
            # 显示当前设置
            if temperature <= 0.3:
                st.info("🎯 保守模式 - 回答更加准确和一致")
            elif temperature <= 0.7:
                st.success("⚖️ 平衡模式 - 准确性和创造性并重")
            elif temperature <= 1.2:
                st.warning("🎨 创意模式 - 回答更加多样和创新")
            else:
                st.error("🌟 极限模式 - 高度创意但可能不稳定")
        
        except ImportError:
            st.error("❌ AI模型功能不可用")
            st.info("💡 请确保已正确安装相关依赖包")
        
        except Exception as e:
            st.error(f"❌ AI模型设置出错: {str(e)}")
            st.info("💡 请检查API配置或联系管理员")
    
    def _render_action_buttons_mobile(self):
        """渲染移动端操作按钮"""
        st.markdown("---")
        st.markdown("### 🎛️ 系统操作")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ 清空对话", use_container_width=True, type="secondary"):
                SessionManager.clear_messages()
                st.success("✅ 对话记录已清空")
                st.rerun()
            
            if st.button("🔄 重置设置", use_container_width=True, type="secondary"):
                self.config.reset()
                st.success("✅ 设置已重置")
                st.rerun()
        
        with col2:
            if st.button("📄 删除文档", use_container_width=True, type="secondary"):
                st.session_state.uploaded_documents = {}
                st.success("✅ 所有文档已删除")
                st.rerun()
            
            if st.button("❌ 关闭设置", use_container_width=True, type="primary"):
                st.session_state.show_settings = False
                st.rerun()
    
    def _render_action_buttons_desktop(self):
        """渲染桌面端操作按钮"""
        st.markdown("---")
        st.markdown("### 🎛️ 系统操作")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🗑️ 清空对话", use_container_width=True, type="secondary"):
                SessionManager.clear_messages()
                st.success("✅ 对话记录已清空")
                st.rerun()
        
        with col2:
            if st.button("📄 删除文档", use_container_width=True, type="secondary"):
                st.session_state.uploaded_documents = {}
                st.success("✅ 所有文档已删除")
                st.rerun()
        
        with col3:
            if st.button("🔄 重置设置", use_container_width=True, type="secondary"):
                self.config.reset()
                st.success("✅ 设置已重置")
                st.rerun()
        
        with col4:
            if st.button("❌ 关闭设置", use_container_width=True, type="primary"):
                st.session_state.show_settings = False
                st.rerun()

# 创建设置面板实例
settings_panel = SettingsPanel()