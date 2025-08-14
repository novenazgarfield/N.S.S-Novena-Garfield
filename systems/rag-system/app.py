"""
RAG系统Streamlit前端
"""
import streamlit as st
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from config import SystemConfig, DocumentConfig
from core.rag_system import RAGSystem
from utils.logger import logger

# 页面配置
st.set_page_config(
    page_title=SystemConfig.PAGE_TITLE,
    page_icon=SystemConfig.PAGE_ICON,
    layout="wide"
)

# 初始化session state
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

def main():
    """主函数"""
    st.title(SystemConfig.PAGE_TITLE)
    
    # 初始化
    init_session_state()
    
    # 侧边栏
    with st.sidebar:
        st.header("🔧 系统控制")
        
        # 任务名输入
        task_name = st.text_input(
            "🔑 任务关键词", 
            value=st.session_state.current_task,
            help="用于区分不同的对话任务"
        )
        
        if task_name != st.session_state.current_task:
            st.session_state.current_task = task_name
        
        # 系统状态
        if st.button("🔄 重新初始化系统"):
            st.session_state.rag_system = None
            st.session_state.system_initialized = False
            st.rerun()
        
        # 清除任务数据
        if st.button("🗑️ 清除当前任务数据"):
            if st.session_state.rag_system:
                try:
                    st.session_state.rag_system.clear_task_data(task_name)
                    st.success("✅ 任务数据已清除")
                except Exception as e:
                    st.error(f"❌ 清除失败: {e}")
        
        # 系统统计
        if st.session_state.rag_system:
            with st.expander("📊 系统统计"):
                stats = st.session_state.rag_system.get_system_stats()
                
                if "error" not in stats:
                    st.json(stats)
                else:
                    st.error(f"获取统计失败: {stats['error']}")
    
    # 主界面
    if not load_rag_system():
        st.stop()
    
    rag_system = st.session_state.rag_system
    
    # 文件上传区域
    st.header("📤 文档上传")
    
    uploaded_files = st.file_uploader(
        "上传文献文件",
        accept_multiple_files=True,
        type=[ext[1:] for ext in DocumentConfig.SUPPORTED_EXTENSIONS],  # 去掉点号
        help=f"支持的文件类型: {', '.join(DocumentConfig.SUPPORTED_EXTENSIONS)}"
    )
    
    if uploaded_files:
        # 验证文件类型
        valid_files = []
        invalid_files = []
        
        for file in uploaded_files:
            ext = Path(file.name).suffix.lower()
            if ext in DocumentConfig.SUPPORTED_EXTENSIONS:
                valid_files.append(file)
            else:
                invalid_files.append(file.name)
        
        if invalid_files:
            st.error(f"❌ 不支持的文件类型: {', '.join(invalid_files)}")
        
        if valid_files:
            st.success(f"✅ 准备处理 {len(valid_files)} 个文件: {[f.name for f in valid_files]}")
            
            if st.button("🚀 开始处理文档"):
                with st.spinner("⏳ 正在处理文档..."):
                    result = rag_system.add_documents(valid_files)
                    
                    if result["success"]:
                        st.success(f"✅ {result['message']}")
                        st.info(f"📦 总文本块: {result['total_chunks']}, 总向量: {result['total_vectors']}")
                    else:
                        st.error(f"❌ {result['message']}")
    
    # 问答区域
    st.header("💬 智能问答")
    
    # 检查是否有可用的文档
    if rag_system.vector_store.faiss_index is None or rag_system.vector_store.faiss_index.ntotal == 0:
        st.warning("⚠️ 当前没有可用的文档索引，请上传文档或检查本地文献库")
        st.info("💡 您可以上传文档或在配置中设置本地文献库路径")
    else:
        stats = rag_system.get_system_stats()
        vector_stats = stats.get("vector_store", {})
        st.info(f"📚 当前索引包含 {vector_stats.get('total_vectors', 0)} 个向量，{vector_stats.get('total_chunks', 0)} 个文本块")
    
    # 问题输入
    question = st.text_input(
        "🤔 请输入您的问题",
        placeholder="例如：这篇论文的主要贡献是什么？",
        help="基于已上传的文档内容进行问答"
    )
    
    if question:
        if st.button("🔍 获取答案") or question:
            with st.spinner("🤖 正在思考中..."):
                try:
                    answer = rag_system.search_and_answer(question, task_name)
                    
                    st.markdown("### 💡 回答：")
                    st.markdown(answer)
                    
                except Exception as e:
                    st.error(f"❌ 生成回答时出错: {e}")
                    logger.error(f"生成回答失败: {e}")
    
    # 聊天历史
    with st.expander("📜 聊天历史", expanded=False):
        try:
            history = rag_system.get_chat_history(task_name, limit=20)
            
            if history:
                for msg in reversed(history):  # 最新的在上面
                    role_icon = "🧑‍💼" if msg["role"] == "user" else "🤖"
                    timestamp = msg["timestamp"][:19] if msg["timestamp"] else ""
                    
                    st.markdown(f"**{role_icon} {msg['role'].title()}** `{timestamp}`")
                    st.markdown(f"> {msg['content']}")
                    st.markdown("---")
            else:
                st.info("暂无聊天记录")
                
        except Exception as e:
            st.error(f"获取聊天历史失败: {e}")
    
    # 页脚信息
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        🧬 综合科研工作站 - RAG智能问答系统<br>
        基于 DeepSeek + multilingual-e5 + FAISS
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()