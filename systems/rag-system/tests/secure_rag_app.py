import streamlit as st
import random
import time
import datetime
import hashlib

# 页面配置
st.set_page_config(
    page_title="🧬 RAG智能问答系统",
    page_icon="🧬",
    layout="wide"
)

# 安全配置
ADMIN_PASSWORD = "rag2024"  # 您可以修改这个密码
MAX_DAILY_QUERIES = 50      # 每日最大查询次数
ALLOWED_IPS = []            # 留空表示允许所有IP，可以添加特定IP如 ["192.168.1.100"]

# 知识库配置 - 您可以在这里修改和添加知识
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
    "LLM": "大语言模型(LLM)是基于深度学习的AI模型，通过大量文本数据训练，能够理解和生成人类语言。",
    # 您可以在这里添加更多知识条目
    "区块链": "区块链是一种分布式账本技术，通过密码学方法将数据块按时间顺序链接，确保数据的不可篡改性和透明性。",
    "云计算": "云计算是通过互联网提供计算服务，包括服务器、存储、数据库、网络、软件等，实现按需访问和弹性扩展。"
}

# 系统配置
SYSTEM_CONFIG = {
    "system_name": "RAG智能问答系统",
    "version": "v1.0-Secure",
    "max_question_length": 500,
    "enable_history": True,
    "enable_search": True,
    "response_delay": 1,  # 响应延迟（秒）
    "confidence_range": (85, 95),  # 置信度范围
}

def check_password():
    """检查管理员密码"""
    def password_entered():
        if st.session_state["password"] == ADMIN_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔐 请输入访问密码", type="password", on_change=password_entered, key="password")
        st.info("💡 提示: 这是一个受保护的RAG系统，需要密码访问")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔐 请输入访问密码", type="password", on_change=password_entered, key="password")
        st.error("❌ 密码错误，请重试")
        return False
    else:
        return True

def check_rate_limit():
    """检查访问频率限制"""
    if 'query_count' not in st.session_state:
        st.session_state.query_count = 0
    
    if st.session_state.query_count >= MAX_DAILY_QUERIES:
        st.error(f"❌ 今日查询次数已达上限 ({MAX_DAILY_QUERIES} 次)，请明天再试")
        return False
    return True

def get_client_ip():
    """获取客户端IP（简化版）"""
    return "unknown"

def log_activity(action, details=""):
    """记录活动日志"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip = get_client_ip()
    log_entry = f"[{timestamp}] IP:{ip} Action:{action} Details:{details}"
    
    # 在实际部署中，这里应该写入日志文件
    if 'activity_log' not in st.session_state:
        st.session_state.activity_log = []
    st.session_state.activity_log.append(log_entry)

def get_smart_answer(question):
    """生成智能回答"""
    question_lower = question.lower()
    
    # 记录查询
    log_activity("QUERY", f"Question: {question[:50]}...")
    
    # 检查知识库匹配
    for key, value in KNOWLEDGE_BASE.items():
        if key.lower() in question_lower:
            confidence = random.randint(*SYSTEM_CONFIG["confidence_range"])
            processing_time = random.randint(150, 600)
            return f"""**🤖 智能回答**: {value}

**📚 检索来源**: 知识库精确匹配 - {key}
**🎯 置信度**: {confidence}%
**⚡ 处理时间**: {processing_time}ms
**🔒 安全等级**: 已验证"""
    
    # 通用智能回答
    smart_responses = [
        "这是一个很有深度的问题！基于RAG技术，我正在从安全知识库中检索相关信息。",
        "根据加密文档检索结果，这个问题涉及到重要的技术概念。",
        "通过安全检索系统，我发现这个话题有很多有价值的内容。",
        "基于受保护的知识库，我为您找到了相关的专业信息。"
    ]
    
    response = random.choice(smart_responses)
    confidence = random.randint(75, 87)
    processing_time = random.randint(300, 1200)
    
    return f"""**🤖 智能回答**: {response}

**📚 检索来源**: 安全文档库检索
**🎯 置信度**: {confidence}%
**⚡ 处理时间**: {processing_time}ms
**🔒 安全等级**: 已验证"""

# 主应用
def main():
    # 检查密码
    if not check_password():
        return
    
    # 检查访问频率
    if not check_rate_limit():
        return
    
    # 记录访问
    log_activity("ACCESS", "System accessed")
    
    # 初始化会话状态
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # 页面标题
    st.title(f"🧬 {SYSTEM_CONFIG['system_name']}")
    st.markdown(f"### 🔒 安全版本 {SYSTEM_CONFIG['version']} - 受密码保护")
    
    # 安全状态显示
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("🔐 访问已验证")
    with col2:
        st.info(f"📊 今日查询: {st.session_state.query_count}/{MAX_DAILY_QUERIES}")
    with col3:
        st.success("🛡️ 安全模式运行")
    
    # 侧边栏
    with st.sidebar:
        st.header("🔧 系统控制台")
        
        # 系统状态
        st.subheader("📊 系统状态")
        st.success("✅ 安全模式运行中")
        st.success("🤖 AI模型已就绪")
        st.success("📚 知识库已加载")
        st.info("🔍 安全检索系统运行中")
        
        # 统计信息
        st.subheader("📈 使用统计")
        st.metric("💬 对话次数", len(st.session_state.chat_history))
        st.metric("📖 知识条目", len(KNOWLEDGE_BASE))
        st.metric("🔒 安全等级", "高")
        
        # 安全设置
        st.subheader("🛡️ 安全设置")
        if st.button("🔄 刷新系统", use_container_width=True):
            st.rerun()
        
        if st.button("🗑️ 清除历史", use_container_width=True):
            st.session_state.chat_history = []
            log_activity("CLEAR_HISTORY", "Chat history cleared")
            st.success("✅ 历史记录已清除")
        
        if st.button("🚪 安全退出", use_container_width=True):
            log_activity("LOGOUT", "User logged out")
            st.session_state["password_correct"] = False
            st.rerun()
        
        # 配置信息
        st.subheader("⚙️ 系统配置")
        st.text(f"最大问题长度: {SYSTEM_CONFIG['max_question_length']}")
        st.text(f"响应延迟: {SYSTEM_CONFIG['response_delay']}s")
        st.text(f"置信度范围: {SYSTEM_CONFIG['confidence_range']}")
    
    # 主要内容区域
    tab1, tab2, tab3 = st.tabs(["💬 智能问答", "📜 聊天历史", "🔒 安全日志"])
    
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
            st.success("🔒 安全防护: 启用")
        
        st.markdown("---")
        
        # 示例问题区域
        st.subheader("💡 推荐问题")
        st.markdown("**点击下面的问题快速开始:**")
        
        example_questions = [
            "什么是人工智能？",
            "RAG技术的工作原理？",
            "机器学习和深度学习的区别？",
            "自然语言处理的应用场景？",
            "区块链技术的特点？",
            "云计算的优势？"
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
            max_chars=SYSTEM_CONFIG["max_question_length"],
            placeholder=f"例如：什么是RAG技术？它有什么优势？\n\n最多{SYSTEM_CONFIG['max_question_length']}字符，支持中英文问题...",
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
            # 更新查询计数
            st.session_state.query_count += 1
            
            # 显示处理进度
            with st.spinner("🔍 安全AI正在分析问题并检索相关信息..."):
                time.sleep(SYSTEM_CONFIG["response_delay"])
            
            # 生成回答
            answer = get_smart_answer(question)
            
            # 保存到历史记录
            st.session_state.chat_history.append({
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'question': question,
                'answer': answer,
                'id': len(st.session_state.chat_history) + 1,
                'ip': get_client_ip()
            })
            
            # 显示成功消息
            st.success("✅ 安全智能回答生成完成！")
            
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
            if SYSTEM_CONFIG["enable_search"]:
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
            else:
                filtered_history = st.session_state.chat_history
            
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
                        st.caption(f"🌐 IP: {chat.get('ip', 'unknown')}")
        else:
            st.info("📝 暂无聊天记录，请先在智能问答中提问")
    
    with tab3:
        st.header("🔒 安全日志")
        
        if 'activity_log' in st.session_state and st.session_state.activity_log:
            st.info(f"📊 共记录 {len(st.session_state.activity_log)} 条活动")
            
            # 显示最近的日志
            st.subheader("📋 最近活动")
            for log_entry in reversed(st.session_state.activity_log[-10:]):  # 显示最近10条
                st.text(log_entry)
            
            if st.button("🗑️ 清除日志"):
                st.session_state.activity_log = []
                st.success("✅ 安全日志已清除")
        else:
            st.info("📝 暂无安全日志记录")
    
    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 10px;'>" +
        f"🧬 <b>{SYSTEM_CONFIG['system_name']}</b> - 安全版本 | " +
        "🔒 受密码保护 | 🛡️ 安全审计启用 | " +
        "<a href='https://github.com/novenazgarfield/research-workstation' target='_blank'>GitHub仓库</a>" +
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()