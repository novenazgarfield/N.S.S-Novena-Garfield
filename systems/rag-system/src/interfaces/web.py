"""
Web界面模块
基于原有app.py重构，保持功能完整性
"""
import streamlit as st
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config.config_manager import get_config
from core.rag_system import RAGSystem
from utils.logger import logger

def init_streamlit_config():
    """初始化Streamlit配置"""
    config = get_config()
    web_config = config.interfaces.web
    
    st.set_page_config(
        page_title=web_config.get('title', 'RAG System'),
        page_icon=web_config.get('icon', '📚'),
        layout=web_config.get('layout', 'wide')
    )

def init_session_state():
    """初始化session state"""
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
        st.session_state.system_initialized = False
    
    if 'current_task' not in st.session_state:
        st.session_state.current_task = "默认任务"

def load_rag_system():
    """加载RAG系统"""
    if st.session_state.rag_system is None:
        with st.spinner("🔄 正在初始化RAG系统..."):
            try:
                st.session_state.rag_system = RAGSystem()
                st.session_state.system_initialized = st.session_state.rag_system.initialize_system()
                
                if st.session_state.system_initialized:
                    st.success("✅ RAG系统初始化成功！")
                else:
                    st.warning("⚠️ RAG系统初始化完成，但没有可用文档")
                    
            except Exception as e:
                st.error(f"❌ RAG系统初始化失败: {e}")
                logger.error(f"RAG系统初始化失败: {e}")
                return False
    
    return st.session_state.rag_system is not None

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("🎯 任务管理")
        
        # 任务选择
        task_options = ["默认任务", "学术研究", "技术分析", "文档总结", "问题解答"]
        current_task = st.selectbox(
            "选择任务类型",
            task_options,
            index=task_options.index(st.session_state.current_task) if st.session_state.current_task in task_options else 0
        )
        
        if current_task != st.session_state.current_task:
            st.session_state.current_task = current_task
            st.rerun()
        
        st.divider()
        
        # 系统状态
        st.subheader("📊 系统状态")
        if st.session_state.rag_system:
            st.success("🟢 系统运行中")
            
            # 显示文档数量
            try:
                doc_count = len(st.session_state.rag_system.vector_store.get_all_documents()) if hasattr(st.session_state.rag_system, 'vector_store') else 0
                st.metric("📄 文档数量", doc_count)
            except:
                st.metric("📄 文档数量", "未知")
        else:
            st.error("🔴 系统未初始化")
        
        st.divider()
        
        # 配置信息
        config = get_config()
        st.subheader("⚙️ 配置信息")
        st.text(f"版本: {config.system.version}")
        st.text(f"模式: {'调试' if config.system.debug else '生产'}")
        st.text(f"数据目录: {config.storage.data_dir.name}")

def render_main_content():
    """渲染主要内容"""
    st.title("📚 RAG问答系统")
    
    # 检查系统状态
    if not st.session_state.system_initialized:
        st.warning("⚠️ 系统尚未完全初始化，某些功能可能不可用")
    
    # 文档上传区域
    with st.expander("📁 文档管理", expanded=False):
        uploaded_files = st.file_uploader(
            "上传文档",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt', 'md']
        )
        
        if uploaded_files and st.button("处理上传的文档"):
            process_uploaded_files(uploaded_files)
    
    # 聊天界面
    st.subheader(f"💬 {st.session_state.current_task}")
    
    # 聊天历史
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # 显示聊天历史
    for i, (question, answer) in enumerate(st.session_state.chat_history):
        with st.container():
            st.markdown(f"**🤔 用户:** {question}")
            st.markdown(f"**🤖 助手:** {answer}")
            st.divider()
    
    # 问题输入
    question = st.text_input("请输入您的问题:", key="question_input")
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("🚀 提问", type="primary"):
            if question.strip():
                handle_question(question)
            else:
                st.warning("请输入问题")
    
    with col2:
        if st.button("🗑️ 清空历史"):
            st.session_state.chat_history = []
            st.rerun()

def process_uploaded_files(uploaded_files):
    """处理上传的文件"""
    if not st.session_state.rag_system:
        st.error("RAG系统未初始化")
        return
    
    with st.spinner("正在处理文档..."):
        try:
            for uploaded_file in uploaded_files:
                # 保存文件到临时位置
                config = get_config()
                temp_path = config.storage.library_dir / uploaded_file.name
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # 处理文档
                st.session_state.rag_system.add_document(str(temp_path))
                st.success(f"✅ 已处理文档: {uploaded_file.name}")
                
        except Exception as e:
            st.error(f"文档处理失败: {e}")
            logger.error(f"文档处理失败: {e}")

def handle_question(question):
    """处理用户问题"""
    if not st.session_state.rag_system:
        st.error("RAG系统未初始化")
        return
    
    with st.spinner("正在思考..."):
        try:
            # 调用RAG系统获取答案
            answer = st.session_state.rag_system.query(
                question, 
                task_type=st.session_state.current_task
            )
            
            # 添加到聊天历史
            st.session_state.chat_history.append((question, answer))
            
            # 清空输入框
            st.session_state.question_input = ""
            
            # 重新运行以更新界面
            st.rerun()
            
        except Exception as e:
            st.error(f"查询失败: {e}")
            logger.error(f"查询失败: {e}")

def run_web_app():
    """运行Web应用"""
    # 初始化配置
    init_streamlit_config()
    init_session_state()
    
    # 加载RAG系统
    if load_rag_system():
        # 渲染界面
        render_sidebar()
        render_main_content()
    else:
        st.error("无法启动RAG系统，请检查配置")

def main():
    """主函数 - 用于直接运行此模块"""
    run_web_app()

if __name__ == "__main__":
    main()