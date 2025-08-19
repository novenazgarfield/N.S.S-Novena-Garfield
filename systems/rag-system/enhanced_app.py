#!/usr/bin/env python3
"""
🤖 长离的智能RAG系统 - 增强版
整合了两个RAG系统的优秀功能，为桌宠系统提供更强大的支持
"""

import streamlit as st
import sys
from pathlib import Path
import importlib.util

# 添加路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "enhanced"))

def check_enhanced_modules():
    """检查增强模块是否可用"""
    modules_status = {}
    
    # 检查核心模块
    try:
        from core.rag_system import RAGSystem
        modules_status['core'] = True
    except ImportError as e:
        modules_status['core'] = False
        st.sidebar.warning(f"核心模块未加载: {e}")
    
    # 检查记忆模块
    try:
        from memory.memory_manager import MemoryManager
        modules_status['memory'] = True
    except ImportError as e:
        modules_status['memory'] = False
        st.sidebar.warning(f"记忆模块未加载: {e}")
    
    # 检查数据库模块
    try:
        from database.chat_db import ChatDB
        modules_status['database'] = True
    except ImportError as e:
        modules_status['database'] = False
        st.sidebar.warning(f"数据库模块未加载: {e}")
    
    # 检查工具模块
    try:
        from utils.logger import Logger
        modules_status['utils'] = True
    except ImportError as e:
        modules_status['utils'] = False
        st.sidebar.warning(f"工具模块未加载: {e}")
    
    return modules_status

def load_universal_app():
    """加载通用RAG应用"""
    try:
        # 导入通用应用的主函数
        spec = importlib.util.spec_from_file_location("universal_app", current_dir / "universal_app.py")
        universal_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(universal_module)
        
        # 调用主函数
        if hasattr(universal_module, 'main'):
            universal_module.main()
        else:
            st.error("通用应用主函数未找到")
    except Exception as e:
        st.error(f"加载通用应用失败: {e}")

def enhanced_mode():
    """增强模式界面"""
    st.header("🚀 增强模式")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧠 智能功能")
        if st.button("🤖 高级RAG问答", use_container_width=True):
            st.info("高级RAG问答功能开发中...")
        
        if st.button("📚 文档深度分析", use_container_width=True):
            st.info("文档深度分析功能开发中...")
        
        if st.button("🔍 智能检索增强", use_container_width=True):
            st.info("智能检索增强功能开发中...")
    
    with col2:
        st.subheader("💾 数据管理")
        if st.button("📊 对话历史管理", use_container_width=True):
            st.info("对话历史管理功能开发中...")
        
        if st.button("🧠 记忆系统管理", use_container_width=True):
            st.info("记忆系统管理功能开发中...")
        
        if st.button("⚙️ 系统配置管理", use_container_width=True):
            st.info("系统配置管理功能开发中...")

def memory_mode():
    """记忆模式界面"""
    st.header("🧠 记忆模式")
    
    st.info("🔧 记忆模式功能正在开发中...")
    
    # 显示记忆系统状态
    st.subheader("📊 记忆系统状态")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("记忆条目", "0", "0")
    with col2:
        st.metric("活跃记忆", "0", "0")
    with col3:
        st.metric("记忆容量", "0%", "0%")

def database_mode():
    """数据库模式界面"""
    st.header("💾 数据库模式")
    
    st.info("🔧 数据库模式功能正在开发中...")
    
    # 显示数据库状态
    st.subheader("📊 数据库状态")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("对话记录", "0", "0")
    with col2:
        st.metric("文档数量", "0", "0")
    with col3:
        st.metric("存储使用", "0%", "0%")

def main():
    """主函数"""
    st.set_page_config(
        page_title="🤖 长离的智能RAG系统 - 增强版",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 主标题
    st.title("🤖 长离的智能RAG系统 - 增强版")
    st.markdown("---")
    
    # 侧边栏
    st.sidebar.title("🎛️ 功能控制台")
    
    # 检查增强模块状态
    modules_status = check_enhanced_modules()
    
    # 显示模块状态
    st.sidebar.subheader("📦 模块状态")
    for module, status in modules_status.items():
        if status:
            st.sidebar.success(f"✅ {module.title()} 模块")
        else:
            st.sidebar.error(f"❌ {module.title()} 模块")
    
    # 功能模式选择
    st.sidebar.subheader("🎯 功能模式")
    mode = st.sidebar.selectbox(
        "选择功能模式",
        [
            "🌐 通用模式",
            "🚀 增强模式", 
            "🧠 记忆模式",
            "💾 数据库模式"
        ],
        index=0
    )
    
    # 系统信息
    st.sidebar.subheader("ℹ️ 系统信息")
    st.sidebar.info(f"""
    **版本**: 增强版 v1.0
    **状态**: {'🟢 正常运行' if any(modules_status.values()) else '🟡 基础模式'}
    **模式**: {mode}
    **端口**: 51658
    """)
    
    # 根据选择的模式显示相应界面
    if mode == "🌐 通用模式":
        st.info("🌐 通用模式 - 使用原有的完整RAG功能")
        load_universal_app()
    elif mode == "🚀 增强模式":
        enhanced_mode()
    elif mode == "🧠 记忆模式":
        memory_mode()
    elif mode == "💾 数据库模式":
        database_mode()
    
    # 页脚信息
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        🐱 长离的智能RAG系统 - 增强版 | 
        整合了模块化架构和通用功能 | 
        为桌宠系统提供强大的AI支持
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()