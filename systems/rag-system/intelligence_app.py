"""
🧠 中央情报大脑 - 主应用程序
============================

基于"大宪章"构建的新一代RAG系统界面
- 三位一体智能分块
- 永恒归档系统
- 深度理解与精准控制

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Genesis"
"""

import streamlit as st
import time
from datetime import datetime
from typing import List, Dict, Any

# 导入新的核心组件
from core.intelligence_brain import IntelligenceBrain
from document.trinity_document_processor import TrinityDocumentProcessor
from llm.llm_manager import LLMManager
from utils.logger import logger

# 页面配置
st.set_page_config(
    page_title="🧠 中央情报大脑",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .status-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    
    .success-card {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .warning-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    
    .error-card {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .atom-result {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_intelligence_brain():
    """初始化中央情报大脑"""
    try:
        llm_manager = LLMManager()
        brain = IntelligenceBrain(llm_manager)
        processor = TrinityDocumentProcessor()
        
        logger.info("中央情报大脑初始化完成")
        return brain, processor, llm_manager
    except Exception as e:
        logger.error(f"中央情报大脑初始化失败: {e}")
        st.error(f"系统初始化失败: {e}")
        return None, None, None

def display_header():
    """显示页面头部"""
    st.markdown("""
    <div class="main-header">
        <h1>🧠 中央情报大脑 (Central Intelligence Brain)</h1>
        <p>基于"大宪章"的新一代RAG系统 - 版本 2.0.0 "Genesis" Chapter 6</p>
        <p><strong>三位一体智能分块 | 永恒归档系统 | 记忆星图构建 | 秩序之盾守护 | 火控系统 | Pantheon灵魂 | 黑匣子记录器 | 免疫系统</strong></p>
    </div>
    """, unsafe_allow_html=True)

def display_brain_status(brain: IntelligenceBrain):
    """显示大脑状态"""
    try:
        status = brain.get_brain_status()
        
        if status["status"] == "operational":
            st.markdown("""
            <div class="success-card">
                <h4>🟢 系统状态：运行正常</h4>
                <p><strong>架构：</strong> 三位一体智能分块 + 记忆星图 + 秩序之盾 + 火控系统 + Pantheon灵魂 + 黑匣子记录器</p>
                <p><strong>版本：</strong> 2.0.0-Genesis-Chapter6</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 显示统计信息
            stats = status.get("statistics", {})
            nebula_stats = status.get("memory_nebula", {}).get("graph_statistics", {})
            shields_stats = status.get("shields_of_order", {})
            fire_control_stats = status.get("fire_control_system", {})
            pantheon_stats = status.get("pantheon_soul", {})
            react_stats = status.get("react_agent", {})
            
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{stats.get('total_documents', 0)}</h3>
                    <p>已归档文档</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{stats.get('total_knowledge_atoms', 0)}</h3>
                    <p>知识原子</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{stats.get('vector_count', 0)}</h3>
                    <p>向量索引</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{nebula_stats.get('total_nodes', 0)}</h3>
                    <p>知识节点</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{nebula_stats.get('total_edges', 0)}</h3>
                    <p>关系连接</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col6:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{"✅" if stats.get('storage_status') == 'operational' else "❌"}</h3>
                    <p>存储状态</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col7:
                shields_status = shields_stats.get('status', 'unknown')
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{"🛡️" if shields_status == 'active' else "❌"}</h3>
                    <p>秩序之盾</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col8:
                fire_control_status = fire_control_stats.get('status', 'unknown')
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{"🎯" if fire_control_status == 'operational' else "❌"}</h3>
                    <p>火控系统</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col9:
                pantheon_status = pantheon_stats.get('pantheon_status', 'unknown')
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{"🌟" if pantheon_status == 'evolving' else "❌"}</h3>
                    <p>Pantheon灵魂</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col10:
                react_status = react_stats.get('agent_status', 'unknown')
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{"🎖️" if react_status == 'operational' else "❌"}</h3>
                    <p>ReAct代理</p>
                </div>
                """, unsafe_allow_html=True)
                
        else:
            st.markdown(f"""
            <div class="error-card">
                <h4>🔴 系统状态：异常</h4>
                <p>错误信息：{status.get('error', '未知错误')}</p>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"获取系统状态失败: {e}")

def document_ingestion_interface(brain: IntelligenceBrain, processor: TrinityDocumentProcessor):
    """文档摄取界面"""
    st.header("📥 文档摄取 - 三位一体智能分块")
    
    st.markdown("""
    <div class="status-card">
        <h4>🔄 处理流程</h4>
        <p><strong>第一层（原子）：</strong> 使用NLTK/spaCy进行句子级精准分割</p>
        <p><strong>第二层（分子）：</strong> 基于换行符的段落级聚合</p>
        <p><strong>第三层（生命体）：</strong> 完整文档级别处理</p>
        <p><strong>永恒烙印：</strong> 自动归档到ChromaDB和SQLite</p>
        <p><strong>记忆星图：</strong> 提取知识三元组并构建关系图谱</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 文件上传
    uploaded_files = st.file_uploader(
        "选择要摄取的文档",
        type=['pdf', 'docx', 'pptx', 'xlsx', 'xls', 'csv', 'txt', 'md', 'py', 'html'],
        accept_multiple_files=True,
        help="支持多种格式的文档，将自动进行三位一体智能分块处理"
    )
    
    if uploaded_files:
        st.write(f"已选择 {len(uploaded_files)} 个文件:")
        for file in uploaded_files:
            st.write(f"- {file.name} ({file.size} bytes)")
        
        if st.button("🚀 开始摄取文档", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # 批量处理文档
                status_text.text("正在解析文档...")
                progress_bar.progress(20)
                
                batch_result = processor.process_documents_batch(uploaded_files)
                progress_bar.progress(50)
                
                if not batch_result["success"]:
                    st.error(f"文档处理失败: {batch_result.get('error', '未知错误')}")
                    return
                
                # 摄取到中央情报大脑
                status_text.text("正在执行三位一体分块...")
                progress_bar.progress(70)
                
                total_atoms = 0
                total_triplets = 0
                successful_ingestions = []
                failed_ingestions = []
                
                for result in batch_result["successful_results"]:
                    status_text.text(f"正在摄取: {result['filename']}")
                    
                    ingestion_result = brain.ingest_document(
                        document_content=result["content"],
                        filename=result["filename"],
                        metadata=result["metadata"]
                    )
                    
                    if ingestion_result["success"]:
                        successful_ingestions.append(ingestion_result)
                        total_atoms += ingestion_result["knowledge_atoms_count"]
                        total_triplets += ingestion_result.get("knowledge_triplets_count", 0)
                    else:
                        failed_ingestions.append(ingestion_result)
                
                progress_bar.progress(100)
                status_text.text("摄取完成！")
                
                # 显示结果
                if successful_ingestions:
                    st.markdown(f"""
                    <div class="success-card">
                        <h4>✅ 摄取成功！</h4>
                        <p><strong>成功处理：</strong> {len(successful_ingestions)} 个文档</p>
                        <p><strong>生成知识原子：</strong> {total_atoms} 个</p>
                        <p><strong>提取知识三元组：</strong> {total_triplets} 个</p>
                        <p><strong>处理时间：</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 显示详细结果
                    with st.expander("📊 详细摄取结果"):
                        for result in successful_ingestions:
                            st.write(f"**{result['filename']}**")
                            st.write(f"- 文档ID: `{result['document_id']}`")
                            st.write(f"- 知识原子: {result['knowledge_atoms_count']} 个")
                            st.write(f"- 知识三元组: {result.get('knowledge_triplets_count', 0)} 个")
                            
                            # 显示记忆星图统计
                            nebula_stats = result.get('memory_nebula_stats', {})
                            if nebula_stats:
                                st.write(f"- 图谱节点: {nebula_stats.get('total_nodes', 0)} 个")
                                st.write(f"- 图谱边: {nebula_stats.get('total_edges', 0)} 个")
                            st.write("---")
                
                if failed_ingestions:
                    st.markdown(f"""
                    <div class="error-card">
                        <h4>❌ 部分摄取失败</h4>
                        <p><strong>失败文档：</strong> {len(failed_ingestions)} 个</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("❌ 失败详情"):
                        for result in failed_ingestions:
                            st.error(f"{result.get('filename', '未知文件')}: {result.get('message', '未知错误')}")
                
            except Exception as e:
                st.error(f"摄取过程中发生错误: {e}")
                logger.error(f"文档摄取失败: {e}")

def intelligence_query_interface(brain: IntelligenceBrain, llm_manager: LLMManager):
    """智能查询界面"""
    st.header("🔍 智能查询 - 深度理解与精准控制")
    
    st.markdown("""
    <div class="status-card">
        <h4>🧠 查询能力</h4>
        <p><strong>深度理解：</strong> 基于知识原子的语义搜索</p>
        <p><strong>精准控制：</strong> 可指定文档范围和相似度阈值</p>
        <p><strong>长期记忆：</strong> 从永恒归档中检索相关知识</p>
        <p><strong>关系图谱：</strong> 基于记忆星图的实体关联查询</p>
        <p><strong>秩序之盾：</strong> 二级精炼与星图导航保护</p>
        <p><strong>🎯 火控系统：</strong> AI注意力精确控制与三段式拨盘</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 🎯 三段式拨盘 - 火控系统核心控件
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
        <h4 style="color: white; margin: 0; text-align: center;">🎯 火控系统 - AI注意力控制</h4>
        <p style="color: #e0e0e0; margin: 0.5rem 0 0 0; text-align: center; font-size: 0.9rem;">
            精确控制AI的注意力范围，实现舰长级别的智能掌控
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 获取可用的搜索范围
    available_scopes = brain.fire_control_system.get_available_scopes()
    
    # 三段式拨盘
    scope_options = []
    scope_labels = []
    scope_help = []
    
    for scope in available_scopes:
        if scope["available"]:
            scope_options.append(scope["value"])
            scope_labels.append(f"{scope['icon']} {scope['label']}")
            scope_help.append(scope["description"])
    
    # 拨盘控件
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_scope = st.selectbox(
            "🎯 选择AI注意力范围",
            options=scope_options,
            format_func=lambda x: next(f"{s['icon']} {s['label']}" for s in available_scopes if s["value"] == x),
            help="控制AI在哪个范围内搜索和思考"
        )
    
    with col2:
        # 显示当前选择的范围信息
        selected_scope_info = next(s for s in available_scopes if s["value"] == search_scope)
        st.markdown(f"""
        <div style="background: #f0f2f6; padding: 0.5rem; border-radius: 5px; text-align: center;">
            <div style="font-size: 2rem;">{selected_scope_info['icon']}</div>
            <div style="font-size: 0.8rem; color: #666;">{selected_scope_info['description']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 目标文档选择（仅当选择"当前文档"时显示）
    target_document_id = None
    if search_scope == "current_document":
        active_docs = brain.fire_control_system.active_documents
        if active_docs:
            doc_options = list(active_docs.keys())
            doc_labels = [f"📄 {active_docs[doc_id].get('title', doc_id)}" for doc_id in doc_options]
            
            target_document_id = st.selectbox(
                "选择目标文档",
                options=doc_options,
                format_func=lambda x: f"📄 {active_docs[x].get('title', x)}",
                help="选择要在其中搜索的具体文档"
            )
        else:
            st.warning("⚠️ 当前没有活跃的文档，请先上传文档或选择其他搜索范围")
            search_scope = "full_database"  # 自动切换到全数据库
    
    # 查询输入
    query = st.text_area(
        "输入您的问题",
        height=100,
        placeholder="请输入您想要查询的问题...",
        help=f"AI将在 {selected_scope_info['label']} 范围内搜索相关信息"
    )
    
    # 查询参数
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        top_k = st.slider("返回结果数量", min_value=1, max_value=20, value=10)
    
    with col2:
        enable_shields = st.checkbox("启用秩序之盾", value=True, help="使用二级精炼和星图导航")
    
    with col3:
        enable_fire_control = st.checkbox("启用火控系统", value=True, help="使用AI注意力精确控制")
    
    with col4:
        generate_answer = st.checkbox("生成智能回答", value=True, help="使用LLM基于检索结果生成回答")
    
    if st.button("🔍 开始查询", type="primary") and query.strip():
        with st.spinner("🎯 火控系统正在锁定目标..."):
            try:
                # 根据是否启用火控系统选择查询方法
                if enable_fire_control:
                    query_result = brain.fire_controlled_query(
                        query=query,
                        search_scope=search_scope,
                        target_id=target_document_id,
                        top_k=top_k,
                        enable_reranking=enable_shields
                    )
                elif enable_shields:
                    query_result = brain.protected_query_intelligence(
                        query=query,
                        top_k=top_k,
                        enable_reranking=True
                    )
                else:
                    query_result = brain.query_intelligence(
                        query=query,
                        top_k=top_k
                    )
                
                if query_result["success"]:
                    results = query_result["results"]
                    
                    # 构建查询完成信息
                    success_info = f"""
                    <div class="success-card">
                        <h4>✅ 查询完成</h4>
                        <p><strong>找到相关知识原子：</strong> {len(results)} 个</p>
                        <p><strong>查询时间：</strong> {query_result.get('query_time', 'N/A')}</p>
                    """
                    
                    # 如果启用了火控系统，显示火控信息
                    if enable_fire_control and query_result.get("fire_control_active"):
                        success_info += f"""
                        <p><strong>🎯 火控系统：</strong> 已激活</p>
                        <p><strong>注意力范围：</strong> {query_result.get('search_scope', 'unknown')}</p>
                        <p><strong>目标锁定：</strong> {query_result.get('target_id', '全范围') or '全范围'}</p>
                        <p><strong>处理时间：</strong> {query_result.get('processing_time', 0):.2f}s</p>
                        """
                    # 如果启用了秩序之盾，显示额外信息
                    elif enable_shields and query_result.get("shields_protection"):
                        complexity = query_result.get("complexity_analysis", {})
                        success_info += f"""
                        <p><strong>🛡️ 秩序之盾：</strong> 已激活</p>
                        <p><strong>查询复杂度：</strong> {complexity.get('complexity_level', 'unknown')}</p>
                        <p><strong>检索策略：</strong> {query_result.get('retrieval_strategy', 'unknown')}</p>
                        <p><strong>处理时间：</strong> {query_result.get('processing_time', 0):.2f}s</p>
                        """
                    
                    success_info += "</div>"
                    st.markdown(success_info, unsafe_allow_html=True)
                    
                    # 显示搜索结果
                    st.subheader("🔬 相关知识原子")
                    
                    for i, result in enumerate(results):
                        # 处理不同的结果格式
                        if enable_fire_control and query_result.get("fire_control_active"):
                            # 火控系统结果格式
                            final_score = result.get("final_score", result.get("similarity_score", 0))
                            rerank_score = result.get("rerank_score")
                            initial_score = result.get("initial_score", final_score)
                            content = result["content"]
                            metadata = result.get("metadata", {})
                            relevance_explanation = result.get("relevance_explanation", f"火控系统评分: {final_score:.4f}")
                            source_info = f"来源: {metadata.get('source', query_result.get('search_scope', 'unknown'))}"
                        elif enable_shields and query_result.get("shields_protection"):
                            # 秩序之盾结果格式
                            final_score = result.get("final_score", result.get("similarity_score", 0))
                            rerank_score = result.get("rerank_score")
                            initial_score = result.get("initial_score", 0)
                            content = result["content"]
                            metadata = result.get("metadata", {})
                            relevance_explanation = result.get("relevance_explanation", "")
                            source_info = f"文档ID: {metadata.get('document_id', 'N/A')}"
                        else:
                            # 标准结果格式
                            final_score = result["similarity_score"]
                            rerank_score = None
                            initial_score = final_score
                            content = result["content"]
                            metadata = result["metadata"]
                            relevance_explanation = f"向量相似度: {final_score:.4f}"
                            source_info = f"文档ID: {metadata.get('document_id', 'N/A')}"
                        
                        # 根据最终分数设置颜色
                        if final_score >= 0.8:
                            color = "#4caf50"  # 绿色
                        elif final_score >= 0.6:
                            color = "#ff9800"  # 橙色
                        else:
                            color = "#f44336"  # 红色
                        
                        # 构建分数显示
                        score_display = f"分数: {final_score:.3f}"
                        if rerank_score is not None:
                            score_display = f"重排序: {rerank_score:.3f}"
                        
                        st.markdown(f"""
                        <div class="atom-result">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong>知识原子 #{i+1}</strong>
                                <span style="background: {color}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">
                                    {score_display}
                                </span>
                            </div>
                            <p>{content}</p>
                            <small style="color: #666;">
                                {source_info} | 
                                段落: {metadata.get('paragraph_id', 'N/A')} | 
                                句子: {metadata.get('sentence_id', 'N/A')}
                            </small>
                            {f'<small style="color: #888;"><br>{relevance_explanation}</small>' if relevance_explanation else ''}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 生成智能回答
                    if generate_answer and results:
                        st.subheader("🤖 智能回答")
                        
                        with st.spinner("正在生成智能回答..."):
                            try:
                                context = query_result["context"]
                                prompt = llm_manager.build_prompt(query, context)
                                answer = llm_manager.generate_response(prompt)
                                
                                st.markdown(f"""
                                <div class="success-card">
                                    <h4>💡 AI回答</h4>
                                    <p>{answer}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                            except Exception as e:
                                st.error(f"生成回答失败: {e}")
                
                else:
                    st.markdown(f"""
                    <div class="warning-card">
                        <h4>⚠️ 未找到相关信息</h4>
                        <p>{query_result['message']}</p>
                        <p>建议：尝试使用不同的关键词或上传相关文档</p>
                    </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"查询过程中发生错误: {e}")
                logger.error(f"智能查询失败: {e}")

def knowledge_graph_interface(brain: IntelligenceBrain):
    """知识图谱查询界面"""
    st.header("🌌 记忆星图 - 知识关联探索")
    
    st.markdown("""
    <div class="status-card">
        <h4>🌐 图谱能力</h4>
        <p><strong>实体关联：</strong> 发现知识实体间的关联关系</p>
        <p><strong>关系追踪：</strong> 追踪知识三元组的传播路径</p>
        <p><strong>深度探索：</strong> 多层次的关系网络分析</p>
        <p><strong>权重管理：</strong> 基于出现频率的关系权重</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 实体查询输入
    entity_query = st.text_input(
        "输入要探索的实体",
        placeholder="例如：人工智能、机器学习、深度学习...",
        help="输入一个实体名称，系统将查找与其相关的所有实体和关系"
    )
    
    # 查询参数
    col1, col2 = st.columns(2)
    
    with col1:
        max_depth = st.slider("关系探索深度", min_value=1, max_value=3, value=2, 
                             help="设置关系探索的最大深度")
    
    with col2:
        show_graph_stats = st.checkbox("显示图谱统计", value=True, 
                                      help="显示知识图谱的详细统计信息")
    
    if st.button("🔍 探索关系网络", type="primary") and entity_query.strip():
        with st.spinner("正在探索知识关系网络..."):
            try:
                # 执行知识图谱查询
                graph_result = brain.query_knowledge_graph(
                    entity=entity_query.strip(),
                    max_depth=max_depth
                )
                
                if graph_result["success"]:
                    graph_relations = graph_result.get("graph_relations", [])
                    vector_matches = graph_result.get("vector_matches", [])
                    
                    st.markdown(f"""
                    <div class="success-card">
                        <h4>✅ 关系探索完成</h4>
                        <p><strong>目标实体：</strong> {entity_query}</p>
                        <p><strong>发现关联实体：</strong> {len(graph_relations)} 个</p>
                        <p><strong>向量匹配：</strong> {len(vector_matches)} 个</p>
                        <p><strong>探索时间：</strong> {graph_result['query_time']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 显示关系网络
                    if graph_relations:
                        st.subheader("🕸️ 关系网络")
                        
                        for i, relation in enumerate(graph_relations):
                            entity_name = relation["entity"]
                            depth = relation["depth"]
                            path = relation.get("path", [])
                            
                            # 根据深度设置颜色
                            if depth == 1:
                                color = "#4caf50"  # 绿色 - 直接关联
                            elif depth == 2:
                                color = "#ff9800"  # 橙色 - 二度关联
                            else:
                                color = "#f44336"  # 红色 - 三度关联
                            
                            st.markdown(f"""
                            <div class="atom-result">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                    <strong>关联实体 #{i+1}: {entity_name}</strong>
                                    <span style="background: {color}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">
                                        {depth}度关联
                                    </span>
                                </div>
                                <p><strong>关联路径：</strong> {' → '.join(path)}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # 显示向量匹配结果
                    if vector_matches:
                        st.subheader("🔬 语义匹配")
                        
                        for i, match in enumerate(vector_matches):
                            similarity_score = match["similarity_score"]
                            content = match["content"]
                            metadata = match["metadata"]
                            
                            # 根据相似度设置颜色
                            if similarity_score >= 0.8:
                                color = "#4caf50"  # 绿色
                            elif similarity_score >= 0.6:
                                color = "#ff9800"  # 橙色
                            else:
                                color = "#f44336"  # 红色
                            
                            st.markdown(f"""
                            <div class="atom-result">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                    <strong>语义匹配 #{i+1}</strong>
                                    <span style="background: {color}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">
                                        相似度: {similarity_score:.3f}
                                    </span>
                                </div>
                                <p>{content}</p>
                                <small style="color: #666;">
                                    文档ID: {metadata.get('document_id', 'N/A')} | 
                                    段落: {metadata.get('paragraph_id', 'N/A')}
                                </small>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # 显示图谱统计信息
                    if show_graph_stats:
                        st.subheader("📊 图谱统计")
                        
                        try:
                            status = brain.get_brain_status()
                            nebula_stats = status.get("memory_nebula", {}).get("graph_statistics", {})
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("总节点数", nebula_stats.get("total_nodes", 0))
                            
                            with col2:
                                st.metric("总边数", nebula_stats.get("total_edges", 0))
                            
                            with col3:
                                st.metric("图密度", f"{nebula_stats.get('density', 0):.4f}")
                            
                            with col4:
                                connectivity = "是" if nebula_stats.get("is_connected", False) else "否"
                                st.metric("连通性", connectivity)
                                
                        except Exception as e:
                            st.error(f"获取图谱统计失败: {e}")
                
                else:
                    st.markdown(f"""
                    <div class="warning-card">
                        <h4>⚠️ 未找到相关关系</h4>
                        <p>{graph_result.get('message', '未知错误')}</p>
                        <p>建议：尝试使用不同的实体名称或确保已上传相关文档</p>
                    </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"关系探索过程中发生错误: {e}")
                logger.error(f"知识图谱查询失败: {e}")

def shields_of_order_interface(brain: IntelligenceBrain):
    """秩序之盾界面"""
    st.header("🛡️ 秩序之盾 - 知识守护与防腐烂机制")
    
    st.markdown("""
    <div class="status-card">
        <h4>🛡️ 秩序之盾能力</h4>
        <p><strong>二级精炼：</strong> Cross-Encoder模型重排序，提升检索精度</p>
        <p><strong>星图导航：</strong> 宏观到微观的分层检索策略</p>
        <p><strong>复杂度分析：</strong> 智能查询复杂度评估与策略选择</p>
        <p><strong>防腐烂机制：</strong> 对抗信息熵，确保高质量结果</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 获取秩序之盾状态
    try:
        shields_status = brain.shields_of_order.get_shields_status()
        
        if shields_status["status"] == "active":
            st.markdown("""
            <div class="success-card">
                <h4>🟢 秩序之盾状态：激活</h4>
                <p><strong>版本：</strong> 2.0.0-Genesis-Chapter3</p>
                <p><strong>防护等级：</strong> 最高</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 显示组件状态
            components = shields_status.get("components", {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                reranker_status = components.get("cross_encoder_reranker", {})
                status_icon = "✅" if reranker_status.get("status") == "operational" else "❌"
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{status_icon}</h3>
                    <p>重排序器</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                summarizer_status = components.get("document_summarizer", {})
                status_icon = "✅" if summarizer_status.get("status") == "operational" else "❌"
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{status_icon}</h3>
                    <p>文档摘要器</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                analyzer_status = components.get("query_complexity_analyzer", {})
                status_icon = "✅" if analyzer_status.get("status") == "operational" else "❌"
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{status_icon}</h3>
                    <p>复杂度分析器</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                retriever_status = components.get("hierarchical_retriever", {})
                status_icon = "✅" if retriever_status.get("status") == "operational" else "❌"
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{status_icon}</h3>
                    <p>分层检索器</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 组件详细信息
            with st.expander("🔧 组件详细信息"):
                st.json(components)
            
        else:
            st.markdown(f"""
            <div class="error-card">
                <h4>🔴 秩序之盾状态：异常</h4>
                <p>错误信息：{shields_status.get('error', '未知错误')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"获取秩序之盾状态失败: {e}")
    
    # 测试查询界面
    st.subheader("🧪 秩序之盾测试")
    
    test_query = st.text_input(
        "输入测试查询",
        placeholder="例如：人工智能与机器学习的关系是什么？",
        help="测试秩序之盾的防护效果"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        test_top_k = st.slider("测试结果数量", min_value=1, max_value=10, value=5)
    
    with col2:
        show_analysis = st.checkbox("显示复杂度分析", value=True)
    
    if st.button("🛡️ 测试秩序之盾", type="primary") and test_query.strip():
        with st.spinner("秩序之盾正在分析和保护..."):
            try:
                # 执行受保护查询
                test_result = brain.protected_query_intelligence(
                    query=test_query,
                    top_k=test_top_k,
                    enable_reranking=True
                )
                
                if test_result["success"]:
                    st.markdown(f"""
                    <div class="success-card">
                        <h4>✅ 秩序之盾测试完成</h4>
                        <p><strong>查询：</strong> {test_query}</p>
                        <p><strong>结果数量：</strong> {len(test_result['results'])} 个</p>
                        <p><strong>处理时间：</strong> {test_result.get('processing_time', 0):.2f}s</p>
                        <p><strong>检索策略：</strong> {test_result.get('retrieval_strategy', 'unknown')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 显示复杂度分析
                    if show_analysis:
                        complexity = test_result.get("complexity_analysis", {})
                        if complexity:
                            st.subheader("📊 查询复杂度分析")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("复杂度等级", complexity.get("complexity_level", "unknown"))
                            
                            with col2:
                                st.metric("置信度", f"{complexity.get('confidence', 0):.2f}")
                            
                            with col3:
                                hierarchical = "是" if complexity.get("requires_hierarchical", False) else "否"
                                st.metric("需要分层检索", hierarchical)
                            
                            # 详细分析
                            with st.expander("📋 详细分析"):
                                analysis_details = complexity.get("analysis_details", {})
                                st.json(analysis_details)
                    
                    # 显示测试结果
                    st.subheader("🔬 测试结果")
                    
                    for i, result in enumerate(test_result["results"]):
                        final_score = result.get("final_score", 0)
                        rerank_score = result.get("rerank_score")
                        initial_score = result.get("initial_score", 0)
                        
                        # 根据分数设置颜色
                        if final_score >= 0.8:
                            color = "#4caf50"
                        elif final_score >= 0.6:
                            color = "#ff9800"
                        else:
                            color = "#f44336"
                        
                        score_info = f"最终分数: {final_score:.3f}"
                        if rerank_score is not None:
                            score_info += f" (重排序: {rerank_score:.3f}, 初始: {initial_score:.3f})"
                        
                        st.markdown(f"""
                        <div class="atom-result">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong>测试结果 #{i+1}</strong>
                                <span style="background: {color}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">
                                    {score_info}
                                </span>
                            </div>
                            <p>{result['content']}</p>
                            <small style="color: #666;">
                                检索级别: {result.get('retrieval_level', 'unknown')} | 
                                来源: {result.get('source_document', 'N/A')}
                            </small>
                            <small style="color: #888;"><br>{result.get('relevance_explanation', '')}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                else:
                    st.markdown(f"""
                    <div class="error-card">
                        <h4>❌ 秩序之盾测试失败</h4>
                        <p>{test_result.get('message', '未知错误')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"秩序之盾测试失败: {e}")
                logger.error(f"秩序之盾测试失败: {e}")

def main():
    """主函数"""
    # 显示页面头部
    display_header()
    
    # 初始化系统
    brain, processor, llm_manager = initialize_intelligence_brain()
    
    if brain is None:
        st.error("系统初始化失败，请检查配置和依赖")
        return
    
    # 侧边栏
    with st.sidebar:
        st.header("🎛️ 控制面板")
        
        # 显示系统状态
        st.subheader("📊 系统状态")
        display_brain_status(brain)
        
        # 功能选择
        st.subheader("🔧 功能选择")
        selected_function = st.radio(
            "选择功能",
            ["📥 文档摄取", "🔍 智能查询", "🌌 记忆星图", "🛡️ 秩序之盾", "🎯 火控系统", "🏥 Chronicle联邦", "📊 性能监控", "🛡️ 系统工程日志"],
            help="选择要使用的功能模块"
        )
        
        # 系统信息
        st.subheader("ℹ️ 系统信息")
        st.info("""
        **中央情报大脑 v2.0.0-Chronicle-Federation**
        
        🔹 三位一体智能分块
        🔹 永恒归档系统  
        🔹 记忆星图构建
        🔹 知识关系提取
        🔹 秩序之盾守护
        🔹 二级精炼机制
        🔹 星图导航策略
        🔹 深度理解能力
        🔹 精准控制机制
        🏥 Chronicle联邦治疗
        
        基于"Chronicle联邦"架构
        """)
    
    # 主内容区域
    if selected_function == "📥 文档摄取":
        document_ingestion_interface(brain, processor)
    elif selected_function == "🔍 智能查询":
        intelligence_query_interface(brain, llm_manager)
    elif selected_function == "🌌 记忆星图":
        knowledge_graph_interface(brain)
    elif selected_function == "🛡️ 秩序之盾":
        shields_of_order_interface(brain)
    elif selected_function == "🎯 火控系统":
        fire_control_system_interface(brain)
    elif selected_function == "🏥 Chronicle联邦":
        chronicle_federation_interface(brain)
    elif selected_function == "📊 性能监控":
        performance_monitoring_interface(brain)
    elif selected_function == "🛡️ 系统工程日志":
        system_engineering_log_interface(brain)

def fire_control_system_interface(brain: IntelligenceBrain):
    """火控系统界面"""
    st.header("🎯 火控系统 - AI注意力的终极掌控")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
        <h4 style="color: white; margin: 0; text-align: center;">🎯 火控系统 - 舰长级AI注意力控制</h4>
        <p style="color: #e0e0e0; margin: 0.5rem 0 0 0; text-align: center;">
            "我们，必须，将对'AI注意力'的最终控制权，牢牢地，掌握在'舰长'的手中。"
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 获取火控系统状态
    fire_control_status = brain.fire_control_system.get_fire_control_status()
    
    if fire_control_status["status"] == "operational":
        st.markdown("""
        <div class="success-card">
            <h4>🟢 火控系统状态：运行正常</h4>
            <p><strong>版本：</strong> 2.0.0-Genesis-Chapter4</p>
            <p><strong>控制级别：</strong> 舰长级精确控制</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 当前注意力目标
        current_target = fire_control_status.get("current_target", {})
        st.subheader("🎯 当前注意力目标")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🎯</h3>
                <p>注意力范围</p>
                <small>{current_target.get('scope', 'unknown')}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📍</h3>
                <p>目标锁定</p>
                <small>{current_target.get('target_id', '全范围') or '全范围'}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            focus_keywords = current_target.get('focus_keywords', [])
            keywords_text = ', '.join(focus_keywords) if focus_keywords else '无'
            st.markdown(f"""
            <div class="metric-card">
                <h3>🔍</h3>
                <p>聚焦关键词</p>
                <small>{keywords_text}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # 系统能力
        st.subheader("⚡ 火控系统能力")
        capabilities = fire_control_status.get("capabilities", [])
        if capabilities:
            cols = st.columns(3)
            for i, capability in enumerate(capabilities):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 0.5rem; border-radius: 5px; margin: 0.2rem 0;">
                        <span style="color: #28a745;">✅</span> {capability}
                    </div>
                    """, unsafe_allow_html=True)
        
        # 可用搜索范围
        st.subheader("🎛️ 三段式拨盘控制")
        available_scopes = brain.fire_control_system.get_available_scopes()
        
        cols = st.columns(len(available_scopes))
        for i, scope in enumerate(available_scopes):
            with cols[i]:
                status_icon = "🟢" if scope["available"] else "🔴"
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{scope['icon']}</h3>
                    <p>{scope['label']}</p>
                    <small>{status_icon} {'可用' if scope['available'] else '不可用'}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # 统计信息
        st.subheader("📊 系统统计")
        statistics = fire_control_status.get("statistics", {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("聊天历史", statistics.get("chat_history_count", 0))
        with col2:
            st.metric("活跃文档", statistics.get("active_documents_count", 0))
        with col3:
            st.metric("当前范围", statistics.get("current_scope", "unknown"))
        
        # 注意力控制测试
        st.subheader("🧪 注意力控制测试")
        
        col1, col2 = st.columns(2)
        with col1:
            test_scope = st.selectbox(
                "选择测试范围",
                options=[s["value"] for s in available_scopes if s["available"]],
                format_func=lambda x: next(f"{s['icon']} {s['label']}" for s in available_scopes if s["value"] == x)
            )
        
        with col2:
            test_target_id = None
            if test_scope == "current_document":
                active_docs = brain.fire_control_system.active_documents
                if active_docs:
                    test_target_id = st.selectbox(
                        "选择目标文档",
                        options=list(active_docs.keys()),
                        format_func=lambda x: f"📄 {active_docs[x].get('title', x)}"
                    )
        
        test_query = st.text_input(
            "输入测试查询",
            placeholder="例如：什么是人工智能？",
            help="测试火控系统的注意力控制能力"
        )
        
        if st.button("🎯 启动火控测试") and test_query:
            with st.spinner("火控系统正在锁定目标..."):
                try:
                    result = brain.fire_controlled_query(
                        query=test_query,
                        search_scope=test_scope,
                        target_id=test_target_id,
                        top_k=5,
                        enable_reranking=True
                    )
                    
                    if result["success"]:
                        st.success(f"✅ 火控测试完成！找到 {len(result['results'])} 个结果")
                        
                        # 显示火控策略
                        strategy = result.get("fire_control_strategy", {})
                        if strategy:
                            st.info(f"""
                            **注意力范围：** {strategy.get('scope', 'unknown')}  
                            **目标锁定：** {strategy.get('target_id', '全范围') or '全范围'}  
                            **检索类型：** {strategy.get('retrieval_type', 'unknown')}  
                            **处理时间：** {result.get('processing_time', 0):.2f}s
                            """)
                        
                        # 显示部分结果
                        if result["results"]:
                            st.subheader("🔬 测试结果预览")
                            for i, res in enumerate(result["results"][:3]):
                                with st.expander(f"结果 {i+1}"):
                                    st.write(res.get("content", "无内容"))
                                    st.caption(f"来源: {res.get('metadata', {}).get('source', 'unknown')}")
                    else:
                        st.error(f"❌ 火控测试失败: {result.get('message', '未知错误')}")
                        
                except Exception as e:
                    st.error(f"❌ 测试过程中发生错误: {str(e)}")
        
        # 神之档位预览
        st.subheader("⚡ 神之档位 - 未来功能预览")
        if fire_control_status.get("configuration", {}).get("god_mode_enabled", False):
            st.success("🔥 神之档位已启用！")
        else:
            st.info("🔮 神之档位功能正在开发中...")
            
        st.markdown("""
        <div style="background: #fff3cd; padding: 1rem; border-radius: 5px; border-left: 4px solid #ffc107;">
            <h5>⚡ 神之档位 - 终极洞察功能</h5>
            <p><strong>当前文档对比全数据库：</strong> 自动发现当前文档的独特见解</p>
            <p><strong>跨文档关联分析：</strong> 智能识别文档间的深层联系</p>
            <p><strong>自动洞察生成：</strong> 基于对比分析生成独特洞察</p>
            <p><strong>智能推理增强：</strong> 结合全库知识进行深度推理</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div class="error-card">
            <h4>🔴 火控系统状态：异常</h4>
            <p>系统检测到火控系统未正常运行，请检查系统配置。</p>
        </div>
        """, unsafe_allow_html=True)

def chronicle_federation_interface(brain: IntelligenceBrain):
    """Chronicle联邦界面"""
    st.header("🏥 Chronicle联邦 - 中央医院治疗系统")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #2c5aa0 0%, #1e3c72 100%); padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
        <h4 style="color: white; margin: 0; text-align: center;">🏥 Chronicle联邦 - RAG系统的中央医院</h4>
        <p style="color: #e0e0e0; margin: 0.5rem 0 0 0; text-align: center;">
            "当RAG系统遇到故障时，它会向Chronicle中央医院求救，获得专业的治疗方案。"
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 检查Chronicle联邦健康状态
    if st.button("🏥 检查Chronicle联邦健康状态"):
        with st.spinner("正在检查Chronicle联邦健康状态..."):
            import asyncio
            try:
                # 创建事件循环来运行异步函数
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                health_result = loop.run_until_complete(brain.check_chronicle_federation_health())
                
                if health_result.get("success"):
                    federation_status = health_result.get("federation_status", {})
                    
                    if federation_status.get("chronicle_online"):
                        st.success("🟢 Chronicle中央医院在线")
                        
                        # 显示连接状态
                        st.markdown("""
                        <div class="success-card">
                            <h4>✅ Chronicle联邦状态：已连接</h4>
                            <p><strong>版本：</strong> 2.0.0-Chronicle-Federation</p>
                            <p><strong>连接状态：</strong> 正常</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 显示健康报告
                        health_report = federation_status.get("health_report")
                        if health_report:
                            st.subheader("📊 Chronicle健康报告")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("故障记录", health_report.get("total_failures", 0))
                            with col2:
                                st.metric("治疗成功", health_report.get("successful_healings", 0))
                            with col3:
                                st.metric("免疫记录", health_report.get("immune_records", 0))
                            with col4:
                                success_rate = health_report.get("healing_success_rate", 0)
                                st.metric("治疗成功率", f"{success_rate:.1%}")
                    else:
                        st.error("🔴 Chronicle中央医院离线")
                        st.warning("⚠️ 系统将使用降级治疗模式")
                else:
                    st.error(f"❌ 健康检查失败: {health_result.get('error')}")
                    
            except Exception as e:
                st.error(f"❌ 健康检查异常: {e}")
    
    # Chronicle治疗统计
    st.subheader("📈 Chronicle治疗统计")
    
    if st.button("📊 获取治疗统计"):
        with st.spinner("正在获取Chronicle治疗统计..."):
            import asyncio
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                stats_result = loop.run_until_complete(brain.get_chronicle_healing_statistics())
                
                if stats_result.get("success"):
                    healing_stats = stats_result.get("healing_statistics", {})
                    
                    if healing_stats:
                        st.success("✅ 治疗统计获取成功")
                        
                        # 显示统计信息
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("总故障数", healing_stats.get("total_failures", 0))
                        with col2:
                            st.metric("治疗成功", healing_stats.get("successful_healings", 0))
                        with col3:
                            st.metric("免疫激活", healing_stats.get("immunity_activations", 0))
                        
                        # 故障类型分布
                        failure_types = healing_stats.get("failure_types", {})
                        if failure_types:
                            st.subheader("🔍 故障类型分布")
                            for error_type, count in failure_types.items():
                                st.write(f"**{error_type}:** {count} 次")
                    else:
                        st.info("📊 暂无治疗统计数据")
                else:
                    st.error(f"❌ 获取治疗统计失败: {stats_result.get('error')}")
                    
            except Exception as e:
                st.error(f"❌ 获取治疗统计异常: {e}")
    
    # 手动故障报告测试
    st.subheader("🚨 手动故障报告测试")
    
    col1, col2 = st.columns(2)
    with col1:
        test_function = st.text_input(
            "函数名称",
            placeholder="例如: ingest_document",
            help="要测试的函数名称"
        )
        test_error_type = st.selectbox(
            "错误类型",
            ["ValueError", "ConnectionError", "TimeoutError", "FileNotFoundError", "MemoryError"],
            help="选择错误类型"
        )
    
    with col2:
        test_error_message = st.text_area(
            "错误信息",
            placeholder="例如: 文档处理失败，内存不足",
            help="描述错误信息"
        )
        test_severity = st.selectbox(
            "严重程度",
            ["low", "medium", "high", "critical"],
            index=1,
            help="选择故障严重程度"
        )
    
    if st.button("🚨 发送测试故障报告") and test_function and test_error_message:
        with st.spinner("正在向Chronicle中央医院发送故障报告..."):
            try:
                from core.chronicle_client import (
                    chronicle_log_failure, 
                    SystemSource, 
                    FailureSeverity
                )
                import asyncio
                
                # 创建模拟异常
                class TestException(Exception):
                    pass
                
                test_exception = TestException(test_error_message)
                severity_map = {
                    "low": FailureSeverity.LOW,
                    "medium": FailureSeverity.MEDIUM,
                    "high": FailureSeverity.HIGH,
                    "critical": FailureSeverity.CRITICAL
                }
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(chronicle_log_failure(
                    source=SystemSource.INTELLIGENCE_BRAIN,
                    function_name=test_function,
                    error=test_exception,
                    context={"test_mode": True, "user_initiated": True},
                    severity=severity_map[test_severity]
                ))
                
                if result:
                    st.success("✅ 故障报告发送成功！")
                    st.info(f"**故障ID:** {result.get('failure_id', 'N/A')}")
                    
                    # 自动请求治疗方案
                    if st.button("🏥 请求治疗方案"):
                        with st.spinner("正在请求治疗方案..."):
                            from core.chronicle_client import chronicle_request_healing
                            
                            healing_result = loop.run_until_complete(chronicle_request_healing(
                                source=SystemSource.INTELLIGENCE_BRAIN,
                                function_name=test_function,
                                error=test_exception,
                                context={"failure_id": result.get('failure_id')}
                            ))
                            
                            if healing_result and healing_result.success:
                                st.success("🏥 治疗方案获取成功！")
                                
                                st.info(f"""
                                **治疗策略:** {healing_result.strategy}  
                                **治疗信息:** {healing_result.message}  
                                **成功率预估:** {healing_result.estimated_success_rate:.1%}
                                """)
                                
                                if healing_result.recommendations:
                                    st.subheader("💡 治疗建议")
                                    for i, rec in enumerate(healing_result.recommendations, 1):
                                        st.write(f"{i}. {rec}")
                            else:
                                st.error("❌ 治疗方案获取失败")
                else:
                    st.error("❌ 故障报告发送失败")
                    
            except Exception as e:
                st.error(f"❌ 测试故障报告异常: {e}")
    
    # Chronicle联邦架构说明
    st.subheader("🏗️ Chronicle联邦架构")
    
    st.markdown("""
    **Chronicle联邦治疗系统架构：**
    
    1. **🚨 故障检测** - RAG系统自动检测故障
    2. **📡 求救信号** - 向Chronicle中央医院发送故障报告
    3. **🏥 中央诊断** - Chronicle分析故障并生成治疗方案
    4. **💊 治疗执行** - RAG系统执行Chronicle提供的治疗方案
    5. **🛡️ 免疫记录** - 成功治疗后建立免疫记录
    
    **权力分离原则：**
    - **RAG系统** 保留"学术大脑"（智能分块、知识图谱）
    - **Chronicle系统** 承担"工程大脑"（故障记录、自我修复）
    - **联邦连接** 通过API实现两系统的神经连接
    """)
    
    # 系统状态总览
    st.subheader("🔍 系统状态总览")
    
    brain_status = brain.get_brain_status()
    if brain_status.get("status") == "operational":
        st.success("🟢 RAG系统状态：运行正常")
        st.info(f"""
        **架构版本:** {brain_status.get('brain_version')}  
        **架构类型:** {brain_status.get('architecture')}  
        **Chronicle联邦:** {brain_status.get('chronicle_federation')}
        """)
    else:
        st.error("🔴 RAG系统状态：异常")

def performance_monitoring_interface(brain: IntelligenceBrain):
    """性能监控界面"""
    st.header("📊 Chronicle联邦性能监控")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
        <h4 style="color: white; margin: 0; text-align: center;">📊 Chronicle联邦性能监控中心</h4>
        <p style="color: #e0e0e0; margin: 0.5rem 0 0 0; text-align: center;">
            "监控RAG系统与Chronicle中央医院的性能指标，确保联邦系统高效运行。"
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        from core.performance_monitor import get_performance_monitor, log_performance_summary
        monitor = get_performance_monitor()
        
        # 实时性能指标
        st.subheader("🔄 实时性能指标")
        
        if st.button("🔄 刷新性能数据"):
            current_metrics = monitor.collect_system_metrics()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "内存使用", 
                    f"{current_metrics.memory_usage_mb:.1f} MB",
                    help="当前RAG系统内存使用量"
                )
            
            with col2:
                st.metric(
                    "CPU使用率", 
                    f"{current_metrics.cpu_usage_percent:.1f}%",
                    help="当前RAG系统CPU使用率"
                )
            
            with col3:
                st.metric(
                    "API响应时间", 
                    f"{current_metrics.api_response_time:.2f}s",
                    help="Chronicle API平均响应时间"
                )
            
            with col4:
                st.metric(
                    "成功率", 
                    f"{current_metrics.success_rate:.1%}",
                    help="Chronicle API调用成功率"
                )
        
        # 性能摘要
        st.subheader("📋 性能摘要")
        
        if st.button("📊 获取性能摘要"):
            summary = monitor.get_performance_summary()
            
            if summary.get("status") == "operational":
                st.success("🟢 系统运行正常")
                
                # 运行统计
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"""
                    **运行统计:**
                    - 运行时间: {summary.get('uptime_seconds', 0):.0f} 秒
                    - 总请求数: {summary.get('total_requests', 0)}
                    - 失败请求: {summary.get('failed_requests', 0)}
                    - 成功率: {summary.get('success_rate', 0):.1%}
                    """)
                
                with col2:
                    perf = summary.get('performance', {})
                    st.info(f"""
                    **平均性能:**
                    - API响应: {perf.get('avg_api_response_time', 0):.2f}s
                    - 内存使用: {perf.get('avg_memory_usage_mb', 0):.1f}MB
                    - CPU使用: {perf.get('avg_cpu_usage_percent', 0):.1f}%
                    - 网络延迟: {perf.get('avg_network_latency_ms', 0):.1f}ms
                    """)
                
                # 性能阈值
                st.subheader("⚠️ 性能阈值")
                thresholds = summary.get('thresholds', {})
                
                threshold_data = {
                    "指标": ["API响应时间", "内存使用", "CPU使用", "网络延迟", "最低成功率"],
                    "当前值": [
                        f"{perf.get('avg_api_response_time', 0):.2f}s",
                        f"{perf.get('avg_memory_usage_mb', 0):.1f}MB",
                        f"{perf.get('avg_cpu_usage_percent', 0):.1f}%",
                        f"{perf.get('avg_network_latency_ms', 0):.1f}ms",
                        f"{summary.get('success_rate', 0):.1%}"
                    ],
                    "阈值": [
                        f"{thresholds.get('api_response_time', 0)}s",
                        f"{thresholds.get('memory_usage_mb', 0)}MB",
                        f"{thresholds.get('cpu_usage_percent', 0)}%",
                        f"{thresholds.get('network_latency_ms', 0)}ms",
                        f"{thresholds.get('min_success_rate', 0):.1%}"
                    ]
                }
                
                st.table(threshold_data)
            else:
                st.warning("⚠️ 暂无性能数据")
        
        # 性能趋势
        st.subheader("📈 性能趋势")
        
        trend_minutes = st.selectbox(
            "选择时间范围",
            [15, 30, 60, 120, 240],
            index=2,
            format_func=lambda x: f"过去{x}分钟",
            help="选择要查看的性能趋势时间范围"
        )
        
        if st.button("📈 查看性能趋势"):
            trends = monitor.get_performance_trends(minutes=trend_minutes)
            
            if "message" in trends:
                st.info(trends["message"])
            else:
                # 显示趋势图表
                import pandas as pd
                
                if trends.get("timestamps"):
                    df = pd.DataFrame({
                        "时间": pd.to_datetime(trends["timestamps"]),
                        "API响应时间(s)": trends["api_response_times"],
                        "内存使用(MB)": trends["memory_usage"],
                        "CPU使用(%)": trends["cpu_usage"],
                        "网络延迟(ms)": trends["network_latency"]
                    })
                    
                    # API响应时间趋势
                    st.line_chart(df.set_index("时间")["API响应时间(s)"])
                    
                    # 系统资源使用趋势
                    col1, col2 = st.columns(2)
                    with col1:
                        st.line_chart(df.set_index("时间")["内存使用(MB)"])
                    with col2:
                        st.line_chart(df.set_index("时间")["CPU使用(%)"])
        
        # 性能优化建议
        st.subheader("💡 性能优化建议")
        
        if st.button("💡 获取优化建议"):
            current_metrics = monitor.collect_system_metrics()
            suggestions = []
            
            if current_metrics.memory_usage_mb > 300:
                suggestions.append("🔧 内存使用较高，建议重启系统或清理缓存")
            
            if current_metrics.cpu_usage_percent > 70:
                suggestions.append("⚡ CPU使用率较高，建议减少并发处理")
            
            if current_metrics.api_response_time > 2.0:
                suggestions.append("🌐 API响应较慢，建议检查Chronicle服务器状态")
            
            if current_metrics.success_rate < 0.9:
                suggestions.append("🚨 成功率较低，建议检查网络连接和服务器状态")
            
            if not suggestions:
                suggestions.append("✅ 系统性能良好，无需优化")
            
            for suggestion in suggestions:
                st.info(suggestion)
        
        # 导出性能数据
        st.subheader("📤 导出性能数据")
        
        if st.button("📤 导出性能报告"):
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                monitor.export_metrics(f.name)
                
                # 读取文件内容
                with open(f.name, 'r', encoding='utf-8') as rf:
                    report_content = rf.read()
                
                st.download_button(
                    label="📥 下载性能报告",
                    data=report_content,
                    file_name=f"chronicle_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                # 清理临时文件
                os.unlink(f.name)
                
                st.success("✅ 性能报告已准备就绪")
        
    except ImportError:
        st.error("❌ 性能监控模块未找到，请检查系统配置")
    except Exception as e:
        st.error(f"❌ 性能监控异常: {e}")

def system_engineering_log_interface(brain: IntelligenceBrain):
    """系统工程日志界面 - 黑匣子与免疫系统"""
    st.header("🛡️ 系统工程日志 - 黑匣子与免疫系统")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
        <h4 style="color: white; margin: 0; text-align: center;">🛡️ 黑匣子记录器 - 失败记忆的永恒化</h4>
        <p style="color: #bdc3c7; margin: 0.5rem 0 0 0; text-align: center;">
            "我们，必须，将每一次'失败'，都视为一次宝贵的'学习'。我们星舰的每一次'创伤'，都必须，成为它未来'装甲'的一部分。"
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 获取黑匣子实例
    from core.black_box import get_black_box, SystemSource, FailureStatus
    black_box = get_black_box()
    
    # 获取故障统计
    failure_stats = black_box.get_failure_statistics()
    immunity_status = black_box.get_immunity_status()
    
    if failure_stats:
        st.markdown("""
        <div class="success-card">
            <h4>🟢 黑匣子状态：运行正常</h4>
            <p><strong>版本：</strong> 2.0.0-Genesis-Chapter6</p>
            <p><strong>记录级别：</strong> 完整故障记忆与免疫系统</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 故障统计概览
        st.subheader("📊 故障统计概览")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总故障数", failure_stats.get("total_failures", 0))
        with col2:
            st.metric("修复成功", failure_stats.get("fixed_failures", 0))
        with col3:
            fix_rate = failure_stats.get("fix_rate", 0)
            st.metric("修复率", f"{fix_rate:.1%}")
        with col4:
            st.metric("故障模式", failure_stats.get("failure_patterns", 0))
        
        # 免疫系统状态
        st.subheader("🛡️ 免疫系统状态")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("免疫记录", immunity_status.get("total_immunities", 0))
        with col2:
            avg_effectiveness = immunity_status.get("average_effectiveness", 0)
            st.metric("平均效果", f"{avg_effectiveness:.1%}")
        with col3:
            health = immunity_status.get("system_health", "unknown")
            health_icon = {"excellent": "🟢", "good": "🟡", "needs_improvement": "🔴"}.get(health, "⚪")
            st.metric("系统健康", f"{health_icon} {health}")
        
        # 按系统分组的故障统计
        system_stats = failure_stats.get("system_statistics", {})
        if system_stats:
            st.subheader("🏗️ 系统故障分析")
            
            # 创建系统故障图表数据
            systems = []
            total_counts = []
            fixed_counts = []
            fix_rates = []
            
            for system, stats in system_stats.items():
                systems.append(system.replace("_", " ").title())
                total_counts.append(stats["total"])
                fixed_counts.append(stats["fixed"])
                fix_rates.append(stats["fix_rate"])
            
            # 显示系统故障表格
            import pandas as pd
            df = pd.DataFrame({
                "系统": systems,
                "总故障": total_counts,
                "已修复": fixed_counts,
                "修复率": [f"{rate:.1%}" for rate in fix_rates]
            })
            
            st.dataframe(df, use_container_width=True)
        
        # 错误类型统计
        error_stats = failure_stats.get("error_type_statistics", {})
        if error_stats:
            st.subheader("🔍 错误类型分析")
            
            # 显示前10个最常见的错误类型
            error_df = pd.DataFrame(list(error_stats.items()), columns=["错误类型", "出现次数"])
            error_df = error_df.sort_values("出现次数", ascending=False).head(10)
            
            st.bar_chart(error_df.set_index("错误类型"))
        
        # 故障记录查看器
        st.subheader("🔍 故障记录查看器 - 法医级分析")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 系统过滤
            system_filter = st.selectbox(
                "过滤系统",
                options=["全部"] + [s.value for s in SystemSource],
                format_func=lambda x: x.replace("_", " ").title() if x != "全部" else x
            )
        
        with col2:
            # 状态过滤
            status_filter = st.selectbox(
                "过滤状态",
                options=["全部"] + [s.value for s in FailureStatus],
                format_func=lambda x: x.replace("_", " ").title() if x != "全部" else x
            )
        
        with col3:
            # 记录数量
            record_limit = st.number_input("显示记录数", min_value=10, max_value=500, value=50)
        
        # 获取故障记录
        system_source = None if system_filter == "全部" else SystemSource(system_filter)
        failure_status = None if status_filter == "全部" else FailureStatus(status_filter)
        
        failure_records = black_box.get_failure_records(
            limit=record_limit,
            source_system=system_source,
            status=failure_status
        )
        
        if failure_records:
            st.subheader(f"📋 故障记录 ({len(failure_records)} 条)")
            
            for i, record in enumerate(failure_records):
                with st.expander(f"🛡️ 故障 {i+1}: {record['function_name']} - {record['error_type']}"):
                    
                    # 基本信息
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        **故障ID:** {record['failure_id']}  
                        **时间:** {record['timestamp']}  
                        **系统:** {record['source_system'].replace('_', ' ').title()}  
                        **函数:** {record['function_name']}  
                        **错误类型:** {record['error_type']}
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **状态:** {record['status'].replace('_', ' ').title()}  
                        **重试次数:** {record['retry_count']}  
                        **修复成功:** {'✅' if record['fix_success'] else '❌'}  
                        **免疫级别:** {record['immunity_level']}
                        """)
                    
                    # 错误信息
                    st.markdown("**错误消息:**")
                    st.error(record['error_message'])
                    
                    # 故障代码
                    if record['faulty_code']:
                        st.markdown("**故障代码:**")
                        st.code(record['faulty_code'], language="python")
                    
                    # AI修复尝试
                    if record['ai_fix_attempted']:
                        st.markdown("**AI修复尝试:**")
                        st.code(record['ai_fix_attempted'], language="python")
                    
                    # 错误堆栈
                    with st.expander("🔍 完整错误堆栈"):
                        st.code(record['error_traceback'], language="text")
                    
                    # 上下文数据
                    if record['context_data']:
                        with st.expander("📋 上下文数据"):
                            st.json(record['context_data'])
        else:
            st.info("📭 暂无符合条件的故障记录")
        
        # 免疫记录查看器
        immunity_records = immunity_status.get("immunity_records", [])
        if immunity_records:
            st.subheader("🛡️ 免疫记录 - 系统装甲")
            
            for i, immunity in enumerate(immunity_records[:10]):  # 显示前10个
                with st.expander(f"🛡️ 免疫 {i+1}: {immunity['error_signature']}"):
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        **免疫ID:** {immunity['immunity_id']}  
                        **错误签名:** {immunity['error_signature']}  
                        **效果评分:** {immunity['effectiveness_score']:.1%}
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **激活次数:** {immunity['activation_count']}  
                        **最后激活:** {immunity['last_activation'] or '从未激活'}  
                        **创建时间:** {immunity['created_at']}
                        """)
        
        # 系统健康建议
        st.subheader("🚀 系统健康建议")
        
        health = immunity_status.get("system_health", "unknown")
        
        if health == "excellent":
            st.success("""
            🎉 **系统健康状况：优秀**
            - 免疫系统运行良好，平均效果超过80%
            - 大部分故障都能被有效修复
            - 系统具备强大的自我修复能力
            """)
        elif health == "good":
            st.info("""
            ✅ **系统健康状况：良好**
            - 免疫系统基本正常，效果在60-80%之间
            - 建议关注重复出现的故障模式
            - 可以考虑优化修复策略
            """)
        else:
            st.warning("""
            ⚠️ **系统健康状况：需要改进**
            - 免疫系统效果低于60%，需要关注
            - 建议分析故障模式，改进修复算法
            - 考虑增加更多的预防性措施
            """)
        
        # 操作按钮
        st.subheader("🔧 系统维护操作")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧹 清理旧记录"):
                st.info("清理功能开发中...")
        
        with col2:
            if st.button("📊 生成报告"):
                st.info("报告生成功能开发中...")
        
        with col3:
            if st.button("🔄 刷新数据"):
                st.rerun()
    
    else:
        st.markdown("""
        <div class="error-card">
            <h4>🔴 黑匣子状态：异常</h4>
            <p>系统检测到黑匣子未正常运行，请检查系统配置。</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()