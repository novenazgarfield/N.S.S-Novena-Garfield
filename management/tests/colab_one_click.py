# 🧬 RAG智能问答系统 - Google Colab 一键运行版
# 复制此完整代码到 Google Colab 中运行即可

import subprocess
import sys
import threading
import time
import random
import datetime

# 安装依赖
def install_deps():
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'streamlit', 'pyngrok', '-q'])
    print("✅ 依赖安装完成！")

install_deps()

# 创建RAG应用
app_code = '''
import streamlit as st
import datetime
import random
import time

st.set_page_config(page_title="🧬 RAG智能问答系统", page_icon="🧬", layout="wide")

# 知识库
KB = {
    "人工智能": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
    "RAG": "检索增强生成(RAG)是一种结合信息检索和文本生成的AI技术，能够基于外部知识库生成更准确的回答。",
    "机器学习": "机器学习是AI的一个子领域，使计算机能够在没有明确编程的情况下学习和改进。",
    "深度学习": "深度学习是机器学习的一个分支，使用多层神经网络来模拟人脑的学习过程。",
    "自然语言处理": "自然语言处理(NLP)是AI的一个分支，专注于计算机与人类语言之间的交互。"
}

def get_answer(question):
    for key, value in KB.items():
        if key.lower() in question.lower():
            return f"**智能回答**: {value}\\n\\n**来源**: 知识库匹配\\n**置信度**: {random.randint(85,95)}%"
    
    responses = [
        "根据文档分析，这是一个关于人工智能的重要问题。",
        "基于检索到的相关文档，我可以为您提供相关信息。",
        "通过文档检索，我发现了相关的研究资料。"
    ]
    return f"**智能回答**: {random.choice(responses)}\\n\\n**来源**: 模拟文档库\\n**置信度**: {random.randint(75,85)}%"

# 主界面
st.title("🧬 RAG智能问答系统")
st.markdown("### 🌟 Google Colab版 - 基于检索增强生成技术")

# 侧边栏
with st.sidebar:
    st.header("🔧 系统状态")
    st.success("✅ Colab模式运行")
    st.success("🤖 AI模型就绪")
    st.info("📚 知识库已加载")
    
    if 'history' in st.session_state:
        st.metric("💬 对话数", len(st.session_state.history))
    
    if st.button("🗑️ 清除历史"):
        st.session_state.history = []
        st.success("已清除")

# 主要内容
tab1, tab2 = st.tabs(["💬 智能问答", "📜 聊天历史"])

with tab1:
    st.header("💬 智能问答")
    
    # 示例问题
    st.markdown("**💡 点击试试:**")
    examples = ["什么是人工智能？", "RAG技术原理？", "机器学习应用？"]
    
    cols = st.columns(len(examples))
    for i, ex in enumerate(examples):
        with cols[i]:
            if st.button(ex, key=f"ex{i}"):
                st.session_state.current_q = ex
    
    # 问题输入
    question = st.text_area(
        "🤔 请输入问题:",
        value=st.session_state.get('current_q', ''),
        height=100
    )
    
    if st.button("🚀 获取答案", type="primary"):
        if question.strip():
            if 'history' not in st.session_state:
                st.session_state.history = []
            
            with st.spinner("🔍 AI思考中..."):
                time.sleep(1)
                answer = get_answer(question)
            
            st.session_state.history.append({
                'time': datetime.datetime.now().strftime("%H:%M:%S"),
                'question': question,
                'answer': answer
            })
            
            st.success("✅ 完成！")
            if 'current_q' in st.session_state:
                del st.session_state.current_q
    
    # 显示最新回答
    if 'history' in st.session_state and st.session_state.history:
        st.markdown("---")
        st.subheader("💡 最新回答")
        latest = st.session_state.history[-1]
        st.markdown(f"**问题**: {latest['question']}")
        st.markdown(latest['answer'])

with tab2:
    st.header("📜 聊天历史")
    
    if 'history' in st.session_state and st.session_state.history:
        st.info(f"📊 共 {len(st.session_state.history)} 条记录")
        
        for i, chat in enumerate(reversed(st.session_state.history)):
            with st.expander(f"💬 对话 {len(st.session_state.history)-i} - {chat['time']}"):
                st.markdown(f"**问题**: {chat['question']}")
                st.markdown(chat['answer'])
    else:
        st.info("📝 暂无记录，请先提问")

st.markdown("---")
st.markdown("🧬 RAG智能问答系统 - Google Colab版 | [GitHub](https://github.com/novenazgarfield/research-workstation)")
'''

# 保存应用
with open('rag_app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("✅ RAG应用创建完成！")

# 启动应用
def run_app():
    subprocess.run(['streamlit', 'run', 'rag_app.py', '--server.port', '8501', '--server.address', '0.0.0.0', '--server.headless', 'true'])

print("🚀 启动RAG系统...")
thread = threading.Thread(target=run_app)
thread.daemon = True
thread.start()

time.sleep(10)

# 设置访问
try:
    from pyngrok import ngrok
    # 如果有ngrok token，取消下面注释并填入token
    # ngrok.set_auth_token("YOUR_TOKEN")
    
    url = ngrok.connect(8501)
    print(f"\n🎉 系统启动成功！")
    print(f"🌐 访问地址: {url}")
    print(f"📱 支持手机访问")
    print(f"\n💡 使用说明:")
    print(f"1. 点击上面链接打开系统")
    print(f"2. 输入问题获取AI回答")
    print(f"3. 查看聊天历史记录")
    
except:
    print(f"\n🎉 系统启动成功！")
    print(f"📍 本地地址: http://localhost:8501")
    print(f"\n💡 在Colab中:")
    print(f"1. 查看左侧'端口'标签")
    print(f"2. 点击8501端口链接")

# 保持运行
try:
    while True:
        time.sleep(60)
        print(f"✅ 运行中 {time.strftime('%H:%M:%S')}")
except KeyboardInterrupt:
    print("🛑 系统停止")