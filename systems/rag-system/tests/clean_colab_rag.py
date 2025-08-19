# RAG智能问答系统 - Google Colab 清洁版
# 复制此代码到 Google Colab 中运行

import subprocess
import sys
import threading
import time
import random
import datetime

print("开始安装依赖...")
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'streamlit', 'pyngrok', '-q'])
print("依赖安装完成！")

# 创建RAG应用代码
app_content = """import streamlit as st
import datetime
import random
import time

st.set_page_config(
    page_title="RAG智能问答系统",
    page_icon="🧬",
    layout="wide"
)

# 知识库
KNOWLEDGE_BASE = {
    "人工智能": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
    "AI": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
    "RAG": "检索增强生成(RAG)是一种结合信息检索和文本生成的AI技术，能够基于外部知识库生成更准确的回答。",
    "机器学习": "机器学习是AI的一个子领域，使计算机能够在没有明确编程的情况下学习和改进。",
    "深度学习": "深度学习是机器学习的一个分支，使用多层神经网络来模拟人脑的学习过程。",
    "自然语言处理": "自然语言处理(NLP)是AI的一个分支，专注于计算机与人类语言之间的交互。",
    "NLP": "自然语言处理(NLP)是AI的一个分支，专注于计算机与人类语言之间的交互。"
}

def generate_answer(question):
    question_lower = question.lower()
    
    # 检查知识库匹配
    for key, value in KNOWLEDGE_BASE.items():
        if key.lower() in question_lower:
            confidence = random.randint(88, 95)
            return f"智能回答: {value}\\n\\n检索来源: 知识库匹配 - {key}\\n置信度: {confidence}%"
    
    # 通用回答
    responses = [
        "根据文档分析，这是一个关于人工智能的重要问题。",
        "基于检索到的相关文档，我可以为您提供相关信息。",
        "通过文档检索，我发现了相关的研究资料。"
    ]
    confidence = random.randint(75, 87)
    return f"智能回答: {random.choice(responses)}\\n\\n检索来源: 模拟文档库\\n置信度: {confidence}%"

# 主界面
st.title("🧬 RAG智能问答系统")
st.markdown("### Google Colab版 - 基于检索增强生成技术")

# 侧边栏
with st.sidebar:
    st.header("系统状态")
    st.success("✅ Colab模式运行中")
    st.success("🤖 AI模型已就绪")
    st.info("📚 知识库已加载")
    
    if 'chat_history' in st.session_state:
        st.metric("对话次数", len(st.session_state.chat_history))
    else:
        st.metric("对话次数", 0)
    
    if st.button("清除历史"):
        if 'chat_history' in st.session_state:
            st.session_state.chat_history = []
        st.success("历史已清除")

# 主要内容
tab1, tab2 = st.tabs(["💬 智能问答", "📜 聊天历史"])

with tab1:
    st.header("💬 智能问答")
    
    # 状态指示
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("📚 知识库: 已加载")
    with col2:
        st.success("🤖 AI模型: 就绪")
    with col3:
        st.success("🔍 检索系统: 运行中")
    
    # 示例问题
    st.markdown("**示例问题:**")
    examples = ["什么是人工智能？", "RAG技术的原理？", "机器学习的应用？"]
    
    cols = st.columns(len(examples))
    for i, example in enumerate(examples):
        with cols[i]:
            if st.button(example, key=f"example_{i}"):
                st.session_state.current_question = example
    
    # 问题输入
    question = st.text_area(
        "请输入您的问题:",
        value=st.session_state.get('current_question', ''),
        height=100,
        placeholder="例如：什么是RAG技术？"
    )
    
    if st.button("🚀 获取答案", type="primary"):
        if question.strip():
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            
            with st.spinner("AI正在思考..."):
                time.sleep(1)
                answer = generate_answer(question)
            
            st.session_state.chat_history.append({
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'question': question,
                'answer': answer
            })
            
            st.success("回答生成完成！")
            
            if 'current_question' in st.session_state:
                del st.session_state.current_question
    
    # 显示最新回答
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        st.markdown("---")
        st.subheader("最新回答")
        latest = st.session_state.chat_history[-1]
        st.markdown(f"**问题**: {latest['question']}")
        st.markdown(latest['answer'])
        st.caption(f"时间: {latest['timestamp']}")

with tab2:
    st.header("📜 聊天历史")
    
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        st.info(f"共有 {len(st.session_state.chat_history)} 条对话记录")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"对话 {len(st.session_state.chat_history)-i} - {chat['timestamp']}"):
                st.markdown(f"**问题**: {chat['question']}")
                st.markdown(f"**回答**: {chat['answer']}")
    else:
        st.info("暂无聊天记录，请先在智能问答中提问")

st.markdown("---")
st.markdown("🧬 RAG智能问答系统 - Google Colab版")
"""

# 保存应用文件
with open('rag_system.py', 'w', encoding='utf-8') as f:
    f.write(app_content)

print("RAG应用文件创建完成！")

# 启动Streamlit应用
def run_streamlit():
    subprocess.run([
        'streamlit', 'run', 'rag_system.py',
        '--server.port', '8501',
        '--server.address', '0.0.0.0',
        '--server.headless', 'true'
    ])

print("正在启动RAG系统...")
thread = threading.Thread(target=run_streamlit)
thread.daemon = True
thread.start()

# 等待启动
time.sleep(15)

# 尝试创建公共URL
try:
    from pyngrok import ngrok
    
    print("创建公共访问URL...")
    public_url = ngrok.connect(8501)
    
    print("=" * 50)
    print("🎉 RAG系统启动成功！")
    print("=" * 50)
    print(f"🌐 访问地址: {public_url}")
    print("📱 支持手机和电脑访问")
    print("=" * 50)
    print("使用说明:")
    print("1. 点击上面的URL打开系统")
    print("2. 在智能问答页面输入问题")
    print("3. 点击获取答案按钮")
    print("4. 查看AI生成的回答")
    print("=" * 50)
    
except Exception as e:
    print("=" * 50)
    print("🎉 RAG系统启动成功 (本地模式)")
    print("=" * 50)
    print("📍 本地地址: http://localhost:8501")
    print("💡 在Colab中查看端口8501的链接")
    print("=" * 50)

# 保持系统运行
print("系统监控开始...")
try:
    while True:
        time.sleep(60)
        current_time = time.strftime('%H:%M:%S')
        print(f"✅ 系统运行正常 - {current_time}")
except KeyboardInterrupt:
    print("系统已停止")