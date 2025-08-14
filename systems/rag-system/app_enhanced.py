"""
增强版RAG系统Streamlit前端
支持多API切换和分布式计算监控
"""
import streamlit as st
import sys
import os
from pathlib import Path
import json

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

# 设置环境变量
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from config_advanced import SystemConfig, DocumentConfig, APIConfig, ModelConfig
from core.enhanced_rag_system import EnhancedRAGSystem
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
    
    if 'current_api' not in st.session_state:
        st.session_state.current_api = ModelConfig.CURRENT_API

def load_rag_system():
    """加载RAG系统"""
    if st.session_state.rag_system is None:
        with st.spinner("🔄 正在初始化增强版RAG系统..."):
            try:
                st.session_state.rag_system = EnhancedRAGSystem()
                st.session_state.system_initialized = st.session_state.rag_system.initialize_system()
                
                if st.session_state.system_initialized:
                    st.success("✅ 增强版RAG系统初始化成功！")
                else:
                    st.warning("⚠️ RAG系统初始化完成，但部分功能可能不可用")
                    
            except Exception as e:
                st.error(f"❌ RAG系统初始化失败: {e}")
                logger.error(f"RAG系统初始化失败: {e}")
                return False
    
    return st.session_state.rag_system is not None

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.header("🔧 系统控制")
        
        # API选择
        st.subheader("🤖 LLM API 配置")
        
        if st.session_state.rag_system:
            available_apis = st.session_state.rag_system.llm_manager.get_available_providers()
            all_apis = list(APIConfig.API_TYPES.keys())
            
            # API选择器
            current_api = st.selectbox(
                "选择API类型",
                options=all_apis,
                index=all_apis.index(st.session_state.current_api) if st.session_state.current_api in all_apis else 0,
                format_func=lambda x: f"{APIConfig.API_TYPES[x]} {'✅' if x in available_apis else '❌'}"
            )
            
            # 切换API
            if current_api != st.session_state.current_api:
                with st.spinner(f"切换到 {APIConfig.API_TYPES[current_api]}..."):
                    result = st.session_state.rag_system.switch_api(current_api)
                    if result["success"]:
                        st.session_state.current_api = current_api
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])
            
            # 显示当前API状态
            provider_info = st.session_state.rag_system.llm_manager.get_current_provider_info()
            
            if provider_info["available"]:
                st.success(f"✅ 当前: {provider_info['name']}")
            else:
                st.error(f"❌ 当前: {provider_info['name']} (不可用)")
        
        st.divider()
        
        # 任务管理
        st.subheader("📋 任务管理")
        
        task_name = st.text_input(
            "🔑 任务关键词", 
            value=st.session_state.current_task,
            help="用于区分不同的对话任务"
        )
        
        if task_name != st.session_state.current_task:
            st.session_state.current_task = task_name
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 重新初始化", use_container_width=True):
                st.session_state.rag_system = None
                st.session_state.system_initialized = False
                st.rerun()
        
        with col2:
            if st.button("🗑️ 清除任务数据", use_container_width=True):
                if st.session_state.rag_system:
                    try:
                        st.session_state.rag_system.clear_task_data(task_name)
                        st.success("✅ 任务数据已清除")
                    except Exception as e:
                        st.error(f"❌ 清除失败: {e}")
        
        st.divider()
        
        # 系统状态
        if st.session_state.rag_system:
            with st.expander("📊 系统状态", expanded=False):
                status = st.session_state.rag_system.get_system_status()
                
                # LLM状态
                st.write("**🤖 LLM状态:**")
                llm_status = status.get("llm", {})
                current_provider = llm_status.get("current_provider", {})
                st.write(f"- 当前: {current_provider.get('name', 'Unknown')}")
                st.write(f"- 可用: {', '.join(llm_status.get('available_providers', []))}")
                
                # 向量存储状态
                st.write("**🔍 向量存储:**")
                vector_status = status.get("vector_store", {})
                st.write(f"- 向量数: {vector_status.get('total_vectors', 0)}")
                st.write(f"- 文本块: {vector_status.get('total_chunks', 0)}")
                st.write(f"- 嵌入设备: {vector_status.get('embedding_device', 'Unknown')}")
                
                # 内存使用
                memory_usage = vector_status.get("memory_usage", {})
                if memory_usage:
                    st.write("**💾 GPU内存:**")
                    for key, value in memory_usage.items():
                        if isinstance(value, float):
                            st.write(f"- {key}: {value:.2f} GB")
                
                # 记忆系统状态
                st.write("**🧠 记忆系统:**")
                memory_status = status.get("memory", {})
                st.write(f"- 永久记忆: {memory_status.get('permanent_memories', 0)}")
                st.write(f"- 临时任务: {memory_status.get('temporary_tasks', 0)}")
        
        st.divider()
        
        # 系统优化
        if st.button("⚡ 优化系统", use_container_width=True):
            if st.session_state.rag_system:
                with st.spinner("正在优化系统..."):
                    try:
                        st.session_state.rag_system.optimize_system()
                        st.success("✅ 系统优化完成")
                    except Exception as e:
                        st.error(f"❌ 优化失败: {e}")

def render_main_content():
    """渲染主要内容"""
    st.title(SystemConfig.PAGE_TITLE)
    
    # 初始化系统
    if not load_rag_system():
        st.stop()
    
    rag_system = st.session_state.rag_system
    
    # 标签页
    tab1, tab2, tab3 = st.tabs(["📤 文档上传", "💬 智能问答", "📜 聊天历史"])
    
    with tab1:
        st.header("📤 文档上传")
        
        # 文件上传
        uploaded_files = st.file_uploader(
            "上传文献文件",
            accept_multiple_files=True,
            type=[ext[1:] for ext in DocumentConfig.SUPPORTED_EXTENSIONS],
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
                st.success(f"✅ 准备处理 {len(valid_files)} 个文件")
                
                # 显示文件列表
                with st.expander("📋 文件列表", expanded=True):
                    for file in valid_files:
                        st.write(f"- {file.name} ({file.size / 1024:.1f} KB)")
                
                if st.button("🚀 开始处理文档", type="primary"):
                    with st.spinner("⏳ 正在处理文档..."):
                        result = rag_system.add_documents(valid_files)
                        
                        if result["success"]:
                            st.success(f"✅ {result['message']}")
                            
                            # 显示处理结果
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("处理文档数", result['processed_count'])
                            with col2:
                                st.metric("总文本块", result['total_chunks'])
                            with col3:
                                st.metric("总向量数", result['total_vectors'])
                            
                            if 'embedding_device' in result:
                                st.info(f"🔧 处理设备: {result['embedding_device']}")
                        else:
                            st.error(f"❌ {result['message']}")
    
    with tab2:
        st.header("💬 智能问答")
        
        # 检查系统状态
        status = rag_system.get_system_status()
        vector_status = status.get("vector_store", {})
        llm_status = status.get("llm", {})
        
        # 显示系统状态
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_vectors = vector_status.get('total_vectors', 0)
            if total_vectors > 0:
                st.success(f"📚 已索引 {total_vectors} 个向量")
            else:
                st.warning("📚 暂无文档索引")
        
        with col2:
            current_provider = llm_status.get('current_provider', {})
            if current_provider.get('available', False):
                st.success(f"🤖 {current_provider.get('name', 'Unknown')} 可用")
            else:
                st.error(f"🤖 {current_provider.get('name', 'Unknown')} 不可用")
        
        with col3:
            embedding_device = vector_status.get('embedding_device', 'Unknown')
            st.info(f"🔧 计算设备: {embedding_device}")
        
        # 问题输入
        question = st.text_area(
            "🤔 请输入您的问题",
            placeholder="例如：这篇论文的主要贡献是什么？",
            help="基于已上传的文档内容进行问答",
            height=100
        )
        
        # 高级选项
        with st.expander("⚙️ 高级选项", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                max_tokens = st.slider("最大回答长度", 100, 3000, 1500)
                temperature = st.slider("创造性", 0.0, 1.0, 0.7, 0.1)
            
            with col2:
                top_k = st.slider("检索文档数", 1, 20, 10)
                use_memory = st.checkbox("使用历史记忆", True)
        
        if question and st.button("🔍 获取答案", type="primary"):
            with st.spinner("🤖 正在思考中..."):
                try:
                    # 构建参数
                    kwargs = {
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "top_k": top_k
                    }
                    
                    result = rag_system.search_and_answer(
                        question, 
                        st.session_state.current_task,
                        **kwargs
                    )
                    
                    if result["success"]:
                        st.markdown("### 💡 回答：")
                        st.markdown(result["answer"])
                        
                        # 显示检索信息
                        retrieval_info = result.get("retrieval_info", {})
                        if retrieval_info:
                            with st.expander("📊 检索信息", expanded=False):
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("检索文档", retrieval_info.get("retrieved_chunks", 0))
                                with col2:
                                    st.metric("记忆条目", retrieval_info.get("memory_items", 0))
                                with col3:
                                    st.metric("历史对话", retrieval_info.get("history_items", 0))
                        
                        # 显示提供者信息
                        provider_info = result.get("provider_info", {})
                        if provider_info:
                            st.info(f"🤖 回答由 {provider_info.get('name', 'Unknown')} 生成")
                    
                    else:
                        st.error(f"❌ {result.get('answer', '生成回答失败')}")
                        if 'error' in result:
                            st.error(f"错误详情: {result['error']}")
                    
                except Exception as e:
                    st.error(f"❌ 生成回答时出错: {e}")
                    logger.error(f"生成回答失败: {e}")
    
    with tab3:
        st.header("📜 聊天历史")
        
        # 历史记录控制
        col1, col2 = st.columns([3, 1])
        
        with col1:
            history_limit = st.slider("显示条数", 5, 50, 20)
        
        with col2:
            if st.button("🔄 刷新历史"):
                st.rerun()
        
        try:
            history = rag_system.get_chat_history(st.session_state.current_task, history_limit)
            
            if history:
                for i, msg in enumerate(reversed(history)):  # 最新的在上面
                    role_icon = "🧑‍💼" if msg["role"] == "user" else "🤖"
                    timestamp = msg["timestamp"][:19] if msg["timestamp"] else ""
                    
                    with st.container():
                        st.markdown(f"**{role_icon} {msg['role'].title()}** `{timestamp}`")
                        
                        # 根据角色设置不同的样式
                        if msg["role"] == "user":
                            st.markdown(f"> {msg['content']}")
                        else:
                            st.markdown(msg['content'])
                        
                        if i < len(history) - 1:  # 不是最后一条
                            st.divider()
            else:
                st.info("暂无聊天记录")
                
        except Exception as e:
            st.error(f"获取聊天历史失败: {e}")

def main():
    """主函数"""
    # 初始化
    init_session_state()
    
    # 渲染界面
    render_sidebar()
    render_main_content()
    
    # 页脚信息
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        🧬 综合科研工作站 - 增强版RAG智能问答系统<br>
        支持多API切换 + 3090/4060分布式计算 + 智能记忆管理
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()