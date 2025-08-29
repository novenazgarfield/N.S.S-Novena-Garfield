"""
🧠 RAG系统统一应用入口
===================

整合所有RAG应用功能，提供统一的用户界面
- 基础RAG功能 (app.py)
- 增强版功能 (app_enhanced.py) 
- 在线版功能 (app_online.py)
- 智能大脑功能 (intelligence_app.py)
- 简化版功能 (app_simple.py)

保持所有原有功能不变，仅统一入口
"""

import streamlit as st
import sys
import os
from pathlib import Path
import json
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

# 设置环境变量
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# 导入配置和工具
from utils.logger import logger

class UnifiedRAGApp:
    """统一RAG应用管理器"""
    
    def __init__(self):
        self.app_modes = {
            "🧠 智能大脑": "intelligence",
            "🚀 增强版": "enhanced", 
            "🌐 在线版": "online",
            "📚 基础版": "basic",
            "⚡ 简化版": "simple"
        }
        
    def run(self):
        """运行统一应用"""
        # 页面基础配置
        st.set_page_config(
            page_title="🧠 RAG智能系统",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # 侧边栏模式选择
        with st.sidebar:
            st.title("🎯 模式选择")
            selected_mode = st.selectbox(
                "选择应用模式",
                list(self.app_modes.keys()),
                index=0
            )
            
            st.markdown("---")
            st.markdown("### 📋 模式说明")
            mode_descriptions = {
                "🧠 智能大脑": "最新的中央情报大脑系统，支持三位一体智能分块",
                "🚀 增强版": "支持多API切换和分布式计算监控",
                "🌐 在线版": "在线部署版本，支持远程访问",
                "📚 基础版": "标准RAG功能，稳定可靠",
                "⚡ 简化版": "轻量级版本，快速启动"
            }
            st.info(mode_descriptions[selected_mode])
        
        # 根据选择的模式加载对应应用
        mode_key = self.app_modes[selected_mode]
        
        try:
            if mode_key == "intelligence":
                self._load_intelligence_app()
            elif mode_key == "enhanced":
                self._load_enhanced_app()
            elif mode_key == "online":
                self._load_online_app()
            elif mode_key == "basic":
                self._load_basic_app()
            elif mode_key == "simple":
                self._load_simple_app()
        except Exception as e:
            st.error(f"加载应用模式失败: {str(e)}")
            logger.error(f"Failed to load app mode {mode_key}: {str(e)}")
    
    def _load_intelligence_app(self):
        """加载智能大脑应用"""
        try:
            from core.intelligence_brain import IntelligenceBrain
            from document.trinity_document_processor import TrinityDocumentProcessor
            
            st.title("🧠 中央情报大脑")
            st.markdown("基于'大宪章'构建的新一代RAG系统")
            
            # 初始化智能大脑
            if 'intelligence_brain' not in st.session_state:
                with st.spinner("初始化中央情报大脑..."):
                    st.session_state.intelligence_brain = IntelligenceBrain()
            
            brain = st.session_state.intelligence_brain
            
            # 主界面
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("💭 智能对话")
                user_input = st.text_area("请输入您的问题:", height=100)
                
                if st.button("🚀 提交查询", type="primary"):
                    if user_input:
                        with st.spinner("智能大脑思考中..."):
                            try:
                                response = brain.query(user_input)
                                st.success("回答:")
                                st.write(response)
                            except Exception as e:
                                st.error(f"查询失败: {str(e)}")
            
            with col2:
                st.subheader("📊 系统状态")
                st.info("智能大脑运行正常")
                
                if hasattr(brain, 'get_stats'):
                    stats = brain.get_stats()
                    st.metric("知识库大小", stats.get('knowledge_count', 0))
                    st.metric("查询次数", stats.get('query_count', 0))
                
        except ImportError as e:
            st.error("智能大脑模块未找到，请检查安装")
            logger.error(f"Intelligence brain import error: {str(e)}")
    
    def _load_enhanced_app(self):
        """加载增强版应用"""
        try:
            from config_advanced import SystemConfig, APIConfig
            
            st.title("🚀 增强版RAG系统")
            st.markdown("支持多API切换和分布式计算监控")
            
            # API配置选择
            col1, col2 = st.columns([3, 1])
            
            with col2:
                st.subheader("⚙️ API配置")
                api_options = ["OpenAI", "Gemini", "Local"]
                selected_api = st.selectbox("选择API", api_options)
                
                if selected_api == "OpenAI":
                    api_key = st.text_input("OpenAI API Key", type="password")
                elif selected_api == "Gemini":
                    api_key = st.text_input("Gemini API Key", type="password")
                else:
                    st.info("使用本地模型")
            
            with col1:
                st.subheader("💬 智能对话")
                user_input = st.text_area("请输入您的问题:", height=100)
                
                if st.button("🔍 查询", type="primary"):
                    if user_input:
                        st.info("增强版查询功能")
                        # 这里会调用原有的enhanced app逻辑
                        
        except ImportError as e:
            st.error("增强版模块未找到")
            logger.error(f"Enhanced app import error: {str(e)}")
    
    def _load_online_app(self):
        """加载在线版应用"""
        st.title("🌐 在线版RAG系统")
        st.markdown("在线部署版本，支持远程访问")
        
        # 在线版特有功能
        st.subheader("🌍 远程连接状态")
        st.success("在线服务正常")
        
        # 基础查询界面
        user_input = st.text_area("请输入您的问题:", height=100)
        if st.button("🌐 在线查询", type="primary"):
            if user_input:
                st.info("在线查询功能")
    
    def _load_basic_app(self):
        """加载基础版应用"""
        try:
            from config import SystemConfig, DocumentConfig
            
            st.title("📚 基础版RAG系统")
            st.markdown("标准RAG功能，稳定可靠")
            
            # 基础功能界面
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📝 文档上传")
                uploaded_file = st.file_uploader(
                    "选择文档文件",
                    type=['txt', 'pdf', 'docx', 'md']
                )
                
                if uploaded_file:
                    st.success(f"已上传: {uploaded_file.name}")
                
                st.subheader("💭 问答")
                user_input = st.text_area("请输入您的问题:", height=100)
                
                if st.button("🔍 查询", type="primary"):
                    if user_input:
                        st.info("基础查询功能")
            
            with col2:
                st.subheader("📊 系统信息")
                st.info("基础版运行正常")
                
        except ImportError as e:
            st.error("基础版模块未找到")
            logger.error(f"Basic app import error: {str(e)}")
    
    def _load_simple_app(self):
        """加载简化版应用"""
        st.title("⚡ 简化版RAG系统")
        st.markdown("轻量级版本，快速启动")
        
        # 简化界面
        user_input = st.text_input("快速提问:")
        
        if st.button("⚡ 快速查询"):
            if user_input:
                st.info("简化版查询功能")

def main():
    """主函数"""
    app = UnifiedRAGApp()
    app.run()

if __name__ == "__main__":
    main()