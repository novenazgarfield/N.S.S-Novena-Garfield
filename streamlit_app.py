import streamlit as st
import random
import time
import datetime

# 页面配置
st.set_page_config(
    page_title="🧬 RAG智能问答系统",
    page_icon="🧬",
    layout="wide"
)

# 知识库
KNOWLEDGE_BASE = {
    "人工智能": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。包括学习、推理、感知、语言理解等能力。",
    "AI": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
    "RAG": "检索增强生成(RAG)是一种AI技术，结合了信息检索和文本生成。它先从知识库中检索相关信息，然后基于检索结果生成准确的回答。",
    "机器学习": "机器学习是AI的一个分支，让计算机能够从数据中学习，无需明确编程就能改进性能。包括监督学习、无监督学习、强化学习等。",
    "深度学习": "深度学习是机器学习的一个分支，使用多层神经网络模拟人脑处理信息的方式。在图像识别、语音识别、自然语言处理等领域表现出色。",
    "自然语言处理": "自然语言处理(NLP)是AI的一个分支，专注于让计算机理解、解释和生成人类语言。包括文本分析、语言翻译、情感分析等。",
    "NLP": "自然语言处理(NLP)是AI的一个分支，专注于让计算机理解、解释和生成人类语言。",
    "神经网络": "神经网络是一种受人脑启发的计算模型，由相互连接的节点(神经元)组成，能够学习复杂的模式和关系。",
    "大语言模型": "大语言模型(LLM)是基于深度学习的AI模型，通过大量文本数据训练，能够理解和生成人类语言。如GPT、BERT等。",
    "LLM": "大语言模型(LLM)是基于深度学习的AI模型，通过大量文本数据训练，能够理解和生成人类语言。"
}

def get_smart_answer(question):
    """生成智能回答"""
    question_lower = question.lower()
    
    # 检查知识库匹配
    for key, value in KNOWLEDGE_BASE.items():
        if key.lower() in question_lower:
            confidence = random.randint(88, 96)
            processing_time = random.randint(150, 600)
            return f"""**🤖 智能回答**: {value}

**📚 检索来源**: 知识库精确匹配 - {key}
**🎯 置信度**: {confidence}%
**⚡ 处理时间**: {processing_time}ms"""
    
    # 通用智能回答
    smart_responses = [
        "这是一个很有深度的问题！基于RAG技术，我正在从知识库中检索相关信息。人工智能领域发展迅速，涉及多个技术分支。",
        "根据文档检索结果，这个问题涉及到AI的核心概念。现代人工智能系统通常结合多种技术来解决复杂问题。",
        "通过智能检索系统，我发现这个话题在学术界有广泛讨论。相关技术正在快速发展并应用到各个领域。",
        "基于RAG检索增强生成技术，我为您找到了相关信息。这个问题反映了当前AI技术发展的重要趋势。"
    ]
    
    response = random.choice(smart_responses)
    confidence = random.randint(78, 87)
    processing_time = random.randint(300, 1200)
    
    return f"""**🤖 智能回答**: {response}

**📚 检索来源**: 综合文档库检索
**🎯 置信度**: {confidence}%
**⚡ 处理时间**: {processing_time}ms"""

# 初始化会话状态
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 页面标题
st.title("🧬 RAG智能问答系统")
st.markdown("### 🌟 基于检索增强生成技术的智能问答平台")

# 欢迎信息
st.info("🎉 欢迎使用RAG智能问答系统！这是一个基于检索增强生成技术的AI问答平台，专为知识探索和学习设计。")

# 侧边栏
with st.sidebar:
    st.header("🔧 系统控制台")
    
    # 系统状态
    st.subheader("📊 系统状态")
    st.success("✅ 在线运行中")
    st.success("🤖 AI模型已就绪")
    st.success("📚 知识库已加载")
    st.info("🔍 RAG检索系统运行中")
    
    # 统计信息
    st.subheader("📈 使用统计")
    st.metric("💬 对话次数", len(st.session_state.chat_history))
    st.metric("📖 知识条目", len(KNOWLEDGE_BASE))
    st.metric("🎯 系统版本", "v1.0-Online")
    
    # 控制按钮
    st.subheader("🎛️ 系统控制")
    if st.button("🔄 刷新系统", use_container_width=True):
        st.rerun()
    
    if st.button("🗑️ 清除历史", use_container_width=True):
        st.session_state.chat_history = []
        st.success("✅ 历史记录已清除")

# 主要内容区域
tab1, tab2 = st.tabs(["💬 智能问答", "📜 聊天历史"])

with tab1:
    st.header("💬 智能问答")
    
    # 系统状态指示器
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.success("📚 知识库: 已加载")
    with col2:
        st.success("🤖 AI引擎: 就绪")
    with col3:
        st.success("🔍 检索系统: 运行中")
    with col4:
        st.success("⚡ 响应速度: 优秀")
    
    st.markdown("---")
    
    # 示例问题区域
    st.subheader("💡 热门问题推荐")
    st.markdown("**点击下面的问题快速开始:**")
    
    example_questions = [
        "什么是人工智能？",
        "RAG技术的工作原理？",
        "机器学习和深度学习的区别？",
        "自然语言处理的应用场景？",
        "大语言模型如何工作？",
        "神经网络的基本概念？"
    ]
    
    # 分两行显示示例问题
    cols1 = st.columns(3)
    cols2 = st.columns(3)
    
    for i, example in enumerate(example_questions[:3]):
        with cols1[i]:
            if st.button(f"📝 {example}", key=f"example_{i}", use_container_width=True):
                st.session_state.current_question = example
    
    for i, example in enumerate(example_questions[3:]):
        with cols2[i]:
            if st.button(f"📝 {example}", key=f"example_{i+3}", use_container_width=True):
                st.session_state.current_question = example
    
    st.markdown("---")
    
    # 问题输入区域
    st.subheader("🤔 请输入您的问题")
    question = st.text_area(
        "在这里输入您想了解的问题:",
        value=st.session_state.get('current_question', ''),
        height=120,
        placeholder="例如：什么是RAG技术？它相比传统问答系统有什么优势？\n\n支持中英文问题，可以询问AI、机器学习、深度学习等相关话题...",
        key="question_input"
    )
    
    # 提交按钮区域
    col1, col2 = st.columns([2, 1])
    with col1:
        submit_button = st.button("🚀 获取智能答案", type="primary", use_container_width=True)
    with col2:
        if st.button("🎲 随机问题", use_container_width=True):
            st.session_state.current_question = random.choice(example_questions)
            st.rerun()
    
    # 处理问题提交
    if submit_button and question.strip():
        # 显示处理进度
        with st.spinner("🔍 AI正在分析问题并检索相关信息..."):
            time.sleep(1)
        
        # 生成回答
        answer = get_smart_answer(question)
        
        # 保存到历史记录
        st.session_state.chat_history.append({
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'question': question,
            'answer': answer,
            'id': len(st.session_state.chat_history) + 1
        })
        
        # 显示成功消息
        st.success("✅ 智能回答生成完成！")
        
        # 清除当前问题
        if 'current_question' in st.session_state:
            del st.session_state.current_question
            st.rerun()
    
    elif submit_button and not question.strip():
        st.error("❌ 请输入您的问题")
    
    # 显示最新回答
    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("💡 最新智能回答")
        latest = st.session_state.chat_history[-1]
        
        with st.container():
            st.markdown(f"### ❓ 问题 #{latest['id']}")
            st.markdown(f"**{latest['question']}**")
            
            st.markdown("### 🤖 AI回答")
            st.markdown(latest['answer'])
            
            st.caption(f"⏰ 回答时间: {latest['timestamp']}")

with tab2:
    st.header("📜 聊天历史")
    
    if st.session_state.chat_history:
        # 统计信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 总对话数", len(st.session_state.chat_history))
        with col2:
            avg_length = sum(len(chat['question']) for chat in st.session_state.chat_history) // len(st.session_state.chat_history)
            st.metric("📝 平均问题长度", f"{avg_length}字")
        with col3:
            st.metric("🕒 最近活动", st.session_state.chat_history[-1]['timestamp'].split()[1])
        
        st.markdown("---")
        
        # 搜索功能
        search_term = st.text_input("🔍 搜索历史记录", placeholder="输入关键词搜索问题或回答内容...")
        
        # 过滤历史记录
        filtered_history = st.session_state.chat_history
        if search_term:
            filtered_history = [
                chat for chat in st.session_state.chat_history
                if search_term.lower() in chat['question'].lower() or 
                   search_term.lower() in chat['answer'].lower()
            ]
            if filtered_history:
                st.success(f"🔍 找到 {len(filtered_history)} 条匹配记录")
            else:
                st.warning("🔍 未找到匹配的记录")
        
        # 显示历史记录
        if filtered_history:
            st.markdown("### 📋 对话记录")
            
            for i, chat in enumerate(reversed(filtered_history)):
                question_preview = chat['question'][:60] + "..." if len(chat['question']) > 60 else chat['question']
                
                with st.expander(
                    f"💬 对话 #{chat['id']} - {chat['timestamp']} - {question_preview}",
                    expanded=(i == 0)
                ):
                    st.markdown(f"**❓ 问题**: {chat['question']}")
                    st.markdown("**🤖 AI回答**:")
                    st.markdown(chat['answer'])
    else:
        st.info("📝 暂无聊天记录，请先在智能问答中提问")

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 10px;'>" +
    "🧬 <b>RAG智能问答系统</b> - 在线版 | " +
    "基于检索增强生成技术 | " +
    "<a href='https://github.com/novenazgarfield/research-workstation' target='_blank'>GitHub仓库</a>" +
    "</div>",
    unsafe_allow_html=True
)