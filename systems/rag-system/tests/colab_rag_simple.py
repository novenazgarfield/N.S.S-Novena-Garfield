# 🧬 RAG智能问答系统 - Google Colab 一键运行版
# 复制此代码到 Google Colab 中运行

# 第一步：安装依赖
import subprocess
import sys

def install_packages():
    packages = ['streamlit', 'pyngrok']
    for package in packages:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])
    print("✅ 依赖安装完成！")

install_packages()

# 第二步：创建RAG应用
app_code = '''
import streamlit as st
import datetime
import random
import time

st.set_page_config(
    page_title="🧬 RAG智能问答系统",
    page_icon="🧬",
    layout="wide"
)

# 模拟知识库
KNOWLEDGE_BASE = {
    "人工智能": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
    "RAG": "检索增强生成(RAG)是一种结合信息检索和文本生成的AI技术，能够基于外部知识库生成更准确的回答。",
    "机器学习": "机器学习是AI的一个子领域，使计算机能够在没有明确编程的情况下学习和改进。",
    "深度学习": "深度学习是机器学习的一个分支，使用多层神经网络来模拟人脑的学习过程。",
    "自然语言处理": "自然语言处理(NLP)是AI的一个分支，专注于计算机与人类语言之间的交互。"
}

def simulate_response(question):
    question_lower = question.lower()
    for key, value in KNOWLEDGE_BASE.items():
        if key.lower() in question_lower:
            return f"**智能回答**: {value}\\n\\n**检索来源**: 知识库匹配\\n\\n**置信度**: 92%"
    
    responses = [
        "根据文档分析，这是一个关于人工智能的重要问题。",
        "基于检索到的相关文档，我可以为您提供相关信息。",
        "通过文档检索，我发现了相关的研究资料。"
    ]
    return f"**智能回答**: {random.choice(responses)}\\n\\n**检索来源**: 模拟文档库\\n\\n**置信度**: 85%"

# 主界面
st.title("🧬 RAG智能问答系统")
st.markdown("### 🌟 基于检索增强生成技术 - Google Colab版")

# 侧边栏
with st.sidebar:
    st.header("🔧 系统状态")
    st.success("✅ Colab模式运行中")
    st.success("🤖 AI模型已就绪")
    st.info("📚 知识库已加载")
    
    if 'chat_history' in st.session_state:
        st.metric("💬 对话次数", len(st.session_state.chat_history))
    else:
        st.metric("💬 对话次数", 0)
    
    if st.button("🗑️ 清除历史"):
        st.session_state.chat_history = []
        st.success("历史已清除")

# 主要内容
tab1, tab2 = st.tabs(["💬 智能问答", "📜 聊天历史"])

with tab1:
    st.header("💬 智能问答")
    
    # 示例问题
    st.markdown("**💡 点击试试这些问题:**")
    examples = ["什么是人工智能？", "RAG技术的原理？", "机器学习的应用？"]
    
    cols = st.columns(len(examples))
    for i, example in enumerate(examples):
        with cols[i]:
            if st.button(example, key=f"ex_{i}"):
                st.session_state.current_q = example
    
    # 问题输入
    question = st.text_area(
        "🤔 请输入您的问题:",
        value=st.session_state.get('current_q', ''),
        height=100
    )
    
    if st.button("🚀 获取答案", type="primary"):
        if question.strip():
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            
            with st.spinner("🔍 AI正在思考..."):
                time.sleep(1)
                response = simulate_response(question)
            
            st.session_state.chat_history.append({
                'time': datetime.datetime.now().strftime("%H:%M:%S"),
                'question': question,
                'response': response
            })
            
            st.success("✅ 回答完成！")
            if 'current_q' in st.session_state:
                del st.session_state.current_q
    
    # 显示最新回答
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        st.markdown("---")
        st.subheader("💡 最新回答")
        latest = st.session_state.chat_history[-1]
        st.markdown(f"**❓ 问题**: {latest['question']}")
        st.markdown(latest['response'])

with tab2:
    st.header("📜 聊天历史")
    
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        st.info(f"📊 共 {len(st.session_state.chat_history)} 条记录")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"💬 对话 {len(st.session_state.chat_history)-i} - {chat['time']}"):
                st.markdown(f"**问题**: {chat['question']}")
                st.markdown(chat['response'])
    else:
        st.info("📝 暂无记录，请先提问")

st.markdown("---")
st.markdown("🧬 RAG智能问答系统 - Google Colab版 | [GitHub仓库](https://github.com/novenazgarfield/research-workstation)")
'''

# 保存应用文件
with open('rag_colab_app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("✅ RAG应用创建完成！")

# 第三步：启动应用
import threading
import time

def run_app():
    subprocess.run([
        'streamlit', 'run', 'rag_colab_app.py',
        '--server.port', '8501',
        '--server.address', '0.0.0.0',
        '--server.headless', 'true'
    ])

print("🚀 正在启动RAG智能问答系统...")
thread = threading.Thread(target=run_app)
thread.daemon = True
thread.start()

time.sleep(10)

# 第四步：设置公共访问 (可选)
try:
    from pyngrok import ngrok
    
    # 如果您有ngrok token，请在这里设置
    # ngrok.set_auth_token("YOUR_TOKEN_HERE")
    
    public_url = ngrok.connect(8501)
    
    print("\n" + "="*60)
    print("🎉 RAG智能问答系统启动成功！")
    print("="*60)
    print(f"🌐 公共访问地址: {public_url}")
    print("📱 支持手机和电脑访问")
    print("="*60)
    print("\n💡 使用说明:")
    print("1. 点击上面的URL打开系统")
    print("2. 在智能问答页面输入问题")
    print("3. 点击'获取答案'按钮查看AI回答")
    print("\n⚠️ 保持代码运行，关闭后URL失效")
    
except Exception as e:
    print("\n" + "="*50)
    print("🎉 RAG系统启动成功 (本地模式)")
    print("="*50)
    print("📍 本地地址: http://localhost:8501")
    print("\n💡 在Colab中:")
    print("1. 查看左侧'文件'面板")
    print("2. 或查看'端口'标签页")
    print("3. 点击8501端口链接访问")
    print("="*50)

# 保持运行
try:
    while True:
        time.sleep(60)
        print(f"✅ 系统运行中... {time.strftime('%H:%M:%S')}")
except KeyboardInterrupt:
    print("\n🛑 系统已停止")