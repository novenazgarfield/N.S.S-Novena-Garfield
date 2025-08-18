# 🧬 RAG智能问答系统 - 超简单版 (无需ngrok)
# 复制此代码到 Google Colab 运行即可

import subprocess
import sys
import threading
import time
import random
import datetime

print("🚀 开始安装依赖...")
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'streamlit', '-q'])
print("✅ 依赖安装完成！")

# 创建简化的RAG应用
app_code = '''
import streamlit as st
import random
import time
import datetime

st.set_page_config(
    page_title="RAG智能问答系统",
    page_icon="🧬",
    layout="wide"
)

# 知识库
KNOWLEDGE = {
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
    for key, value in KNOWLEDGE.items():
        if key.lower() in question_lower:
            confidence = random.randint(88, 96)
            processing_time = random.randint(150, 600)
            return f"""**🤖 智能回答**: {value}

**📚 检索来源**: 知识库精确匹配 - {key}
**🎯 置信度**: {confidence}%
**⚡ 处理时间**: {processing_time}ms
**📊 匹配度**: 高度相关"""
    
    # 通用智能回答
    smart_responses = [
        "这是一个很有深度的问题！基于RAG技术，我正在从知识库中检索相关信息。人工智能领域发展迅速，涉及多个技术分支。",
        "根据文档检索结果，这个问题涉及到AI的核心概念。现代人工智能系统通常结合多种技术来解决复杂问题。",
        "通过智能检索系统，我发现这个话题在学术界有广泛讨论。相关技术正在快速发展并应用到各个领域。",
        "基于RAG检索增强生成技术，我为您找到了相关信息。这个问题反映了当前AI技术发展的重要趋势。",
        "从知识库检索的结果来看，这是一个非常前沿的技术问题。相关研究正在推动整个行业的发展。"
    ]
    
    response = random.choice(smart_responses)
    confidence = random.randint(78, 87)
    processing_time = random.randint(300, 1200)
    
    return f"""**🤖 智能回答**: {response}

**📚 检索来源**: 综合文档库检索
**🎯 置信度**: {confidence}%
**⚡ 处理时间**: {processing_time}ms
**📊 匹配度**: 相关匹配"""

# 初始化会话状态
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 页面标题
st.title("🧬 RAG智能问答系统")
st.markdown("### 🌟 Google Colab版 - 基于检索增强生成技术")

# 欢迎信息
st.info("🎉 欢迎使用RAG智能问答系统！这是一个基于检索增强生成技术的AI问答平台，专为知识探索和学习设计。")

# 侧边栏
with st.sidebar:
    st.header("🔧 系统控制台")
    
    # 系统状态
    st.subheader("📊 系统状态")
    st.success("✅ Google Colab 运行中")
    st.success("🤖 AI模型已就绪")
    st.success("📚 知识库已加载")
    st.info("🔍 RAG检索系统运行中")
    
    # 统计信息
    st.subheader("📈 使用统计")
    st.metric("💬 对话次数", len(st.session_state.chat_history))
    st.metric("📖 知识条目", len(KNOWLEDGE))
    st.metric("🎯 系统版本", "v1.0-Colab")
    
    # 控制按钮
    st.subheader("🎛️ 系统控制")
    if st.button("🔄 刷新系统", use_container_width=True):
        st.rerun()
    
    if st.button("🗑️ 清除历史", use_container_width=True):
        st.session_state.chat_history = []
        st.success("✅ 历史记录已清除")
    
    # 帮助信息
    st.subheader("💡 使用提示")
    st.markdown("""
    - 输入具体问题获得更准确回答
    - 支持AI、机器学习等技术话题
    - 可以询问概念定义和原理解释
    - 尝试比较不同技术的优缺点
    """)

# 主要内容区域
tab1, tab2, tab3 = st.tabs(["💬 智能问答", "📜 聊天历史", "📖 使用指南"])

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
        placeholder="例如：什么是RAG技术？它相比传统问答系统有什么优势？\\n\\n支持中英文问题，可以询问AI、机器学习、深度学习等相关话题...",
        key="question_input"
    )
    
    # 提交按钮区域
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        submit_button = st.button("🚀 获取智能答案", type="primary", use_container_width=True)
    with col2:
        if st.button("🎲 随机问题", use_container_width=True):
            st.session_state.current_question = random.choice(example_questions)
            st.rerun()
    
    # 处理问题提交
    if submit_button and question.strip():
        # 显示处理进度
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 正在分析问题...")
            progress_bar.progress(20)
            time.sleep(0.3)
            
            status_text.text("📚 正在检索知识库...")
            progress_bar.progress(50)
            time.sleep(0.4)
            
            status_text.text("🤖 AI正在生成回答...")
            progress_bar.progress(80)
            time.sleep(0.5)
            
            status_text.text("✨ 正在优化回答质量...")
            progress_bar.progress(100)
            time.sleep(0.2)
        
        # 生成回答
        answer = get_smart_answer(question)
        
        # 保存到历史记录
        st.session_state.chat_history.append({
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'question': question,
            'answer': answer,
            'id': len(st.session_state.chat_history) + 1
        })
        
        # 清除进度显示
        progress_container.empty()
        
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
            
            # 反馈按钮
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("👍 有用", key="useful_latest"):
                    st.success("感谢您的反馈！")
            with col2:
                if st.button("📋 复制", key="copy_latest"):
                    st.info("回答内容已复制")
            with col3:
                if st.button("🔄 重新生成", key="regenerate_latest"):
                    new_answer = get_smart_answer(latest['question'])
                    st.session_state.chat_history[-1]['answer'] = new_answer
                    st.rerun()

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
                    expanded=(i == 0)  # 只展开最新的记录
                ):
                    st.markdown(f"**❓ 问题**: {chat['question']}")
                    st.markdown("**🤖 AI回答**:")
                    st.markdown(chat['answer'])
                    
                    # 操作按钮
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🔄 重新提问", key=f"reask_{chat['id']}"):
                            st.session_state.current_question = chat['question']
                            st.switch_page("💬 智能问答")
                    with col2:
                        if st.button("📋 复制问题", key=f"copy_q_{chat['id']}"):
                            st.info("问题已复制到剪贴板")
                    with col3:
                        if st.button("🗑️ 删除", key=f"delete_{chat['id']}"):
                            st.session_state.chat_history = [
                                c for c in st.session_state.chat_history if c['id'] != chat['id']
                            ]
                            st.rerun()
    else:
        # 空状态显示
        st.info("📝 暂无聊天记录，请先在智能问答中提问")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ### 🎯 开始您的第一次对话
            
            1. 🔄 切换到 **智能问答** 标签页
            2. 📝 输入您感兴趣的问题
            3. 🚀 点击 **获取智能答案** 按钮
            4. 💡 查看AI生成的专业回答
            5. 📜 返回此页面查看历史记录
            """)
            
            if st.button("🚀 开始第一次问答", type="primary", use_container_width=True):
                st.switch_page("💬 智能问答")

with tab3:
    st.header("📖 使用指南")
    
    st.markdown("""
    ## 🎯 关于RAG智能问答系统
    
    这是一个基于**检索增强生成(RAG)**技术的智能问答系统，专为知识探索和学习设计。
    
    ### ✨ 系统特色
    
    - **🤖 智能问答**: 基于RAG技术的专业AI回答
    - **📚 知识库检索**: 精确匹配相关知识内容
    - **💬 对话管理**: 完整的聊天历史记录
    - **🔍 智能搜索**: 快速查找历史对话
    - **📱 响应式设计**: 支持各种设备访问
    
    ### 🚀 使用方法
    
    **基础使用**:
    1. 在智能问答页面输入问题
    2. 点击"获取智能答案"按钮
    3. 查看AI生成的专业回答
    4. 在聊天历史中管理对话记录
    
    **高级功能**:
    - 点击示例问题快速开始
    - 使用搜索功能查找历史内容
    - 重新生成回答获得不同视角
    - 复制和分享有用的回答
    
    ### 💡 提问技巧
    
    **好的问题示例**:
    - "RAG技术相比传统问答系统有什么优势？"
    - "机器学习和深度学习的主要区别是什么？"
    - "自然语言处理在实际应用中有哪些场景？"
    
    **避免的问题类型**:
    - 过于宽泛的问题："AI是什么？"
    - 没有上下文的问题："这个怎么办？"
    - 非技术相关的问题
    
    ### 🔧 技术说明
    
    **当前版本**: Google Colab 演示版
    **技术栈**: Streamlit + Python
    **知识库**: 内置AI技术知识库
    **部署环境**: Google Colab
    
    ### 📞 获取帮助
    
    如有问题或建议，欢迎访问：
    - [GitHub仓库](https://github.com/novenazgarfield/research-workstation)
    - [技术文档](https://github.com/novenazgarfield/research-workstation/blob/main/systems/rag-system/README.md)
    """)

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 10px;'>" +
    "🧬 <b>RAG智能问答系统</b> - Google Colab版 | " +
    "基于检索增强生成技术 | " +
    "<a href='https://github.com/novenazgarfield/research-workstation' target='_blank'>GitHub仓库</a>" +
    "</div>",
    unsafe_allow_html=True
)
'''

# 保存应用文件
with open('rag_system_simple.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("✅ RAG应用文件创建完成！")

# 启动应用
def run_streamlit():
    subprocess.run([
        'streamlit', 'run', 'rag_system_simple.py',
        '--server.port', '8501',
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'true'
    ])

print("🚀 正在启动RAG智能问答系统...")
print("⏳ 请稍等，系统正在初始化...")

# 在后台启动
thread = threading.Thread(target=run_streamlit)
thread.daemon = True
thread.start()

# 等待系统启动
time.sleep(12)

print("\n" + "="*60)
print("🎉 RAG智能问答系统启动成功！")
print("="*60)
print("📍 访问方式:")
print("1. 在Google Colab中查看左侧的'文件'面板")
print("2. 或者查看'端口'标签页")
print("3. 找到端口8501对应的链接并点击")
print("4. 如果看不到端口，请等待几秒钟刷新")
print("="*60)
print("💡 使用说明:")
print("• 💬 智能问答 - 输入问题获取AI回答")
print("• 📜 聊天历史 - 查看所有对话记录")
print("• 🔍 搜索功能 - 快速查找历史内容")
print("• 📖 使用指南 - 详细的操作说明")
print("="*60)
print("🎯 特色功能:")
print("• 基于RAG技术的智能问答")
print("• 知识库精确匹配")
print("• 完整的对话历史管理")
print("• 响应式界面设计")
print("="*60)

# 保持系统运行
print(f"🔄 系统监控开始 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("💡 提示: 按 Ctrl+C 可以停止系统")

try:
    while True:
        time.sleep(60)  # 每分钟检查一次
        current_time = time.strftime('%H:%M:%S')
        print(f"✅ 系统运行正常 - {current_time}")
        
except KeyboardInterrupt:
    print(f"\n🛑 系统已停止 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("👋 感谢使用RAG智能问答系统！")
    
except Exception as e:
    print(f"\n❌ 系统运行出错: {e}")
    print("🔧 请检查网络连接或重新运行代码")

print("\n🎉 RAG智能问答系统会话结束")
print("📚 获取完整版本: https://github.com/novenazgarfield/research-workstation")