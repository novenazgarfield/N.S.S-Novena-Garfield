"""
RAG系统在线演示版本
适用于无GPU环境的在线运行
"""
import streamlit as st
import sys
import os
from pathlib import Path
import json
import sqlite3
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

# 设置环境变量
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# 页面配置
st.set_page_config(
    page_title="🧬 RAG智能问答系统 - 在线演示",
    page_icon="🤖",
    layout="wide"
)

# 初始化session state
def init_session_state():
    """初始化session state"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'current_task' not in st.session_state:
        st.session_state.current_task = "在线演示"
    
    if 'api_type' not in st.session_state:
        st.session_state.api_type = "演示模式"

def create_demo_database():
    """创建演示数据库"""
    db_path = "/tmp/demo_chat.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            task_name TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    
    return db_path

def save_message(role, content, task_name):
    """保存消息到数据库"""
    try:
        db_path = create_demo_database()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_messages (role, content, timestamp, task_name)
            VALUES (?, ?, ?, ?)
        ''', (role, content, datetime.now().isoformat(), task_name))
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"保存消息失败: {e}")

def get_chat_history(task_name, limit=10):
    """获取聊天历史"""
    try:
        db_path = create_demo_database()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, timestamp FROM chat_messages
            WHERE task_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (task_name, limit))
        
        messages = cursor.fetchall()
        conn.close()
        
        return list(reversed(messages))  # 最新的在下面
    except Exception as e:
        st.error(f"获取历史失败: {e}")
        return []

def simulate_rag_response(question, task_name):
    """模拟RAG回答"""
    
    # 模拟文档检索
    mock_documents = [
        "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
        "机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。",
        "深度学习是机器学习的一个分支，使用神经网络来模拟人脑的学习过程。",
        "自然语言处理(NLP)是人工智能的一个领域，专注于计算机与人类语言之间的交互。"
    ]
    
    # 简单的关键词匹配
    relevant_docs = []
    keywords = question.lower().split()
    
    for doc in mock_documents:
        for keyword in keywords:
            if keyword in doc.lower():
                relevant_docs.append(doc)
                break
    
    if not relevant_docs:
        relevant_docs = mock_documents[:2]  # 默认返回前两个
    
    # 构建回答
    context = "\n".join(relevant_docs)
    
    # 模拟智能回答
    if "人工智能" in question or "AI" in question:
        answer = f"""基于检索到的文档内容，我来回答您的问题：

{question}

**相关信息：**
{context}

**详细回答：**
人工智能(AI)是一个快速发展的技术领域，它包含了多个子领域如机器学习、深度学习和自然语言处理等。AI系统能够执行传统上需要人类智能才能完成的任务，如图像识别、语言理解、决策制定等。

**应用场景：**
- 智能问答系统（如当前系统）
- 图像和语音识别
- 自动驾驶
- 医疗诊断辅助
- 金融风险评估

这是一个演示回答，在实际部署中，系统会：
1. 从您上传的文档中检索相关内容
2. 使用配置的LLM模型生成更准确的回答
3. 结合历史对话上下文提供个性化回答"""

    elif "机器学习" in question or "ML" in question:
        answer = f"""关于机器学习的问题：

{question}

**检索到的相关内容：**
{context}

**回答：**
机器学习是AI的核心技术之一，它让计算机能够从数据中学习模式，而不需要明确的编程指令。

**主要类型：**
- **监督学习**：使用标记数据训练模型
- **无监督学习**：从未标记数据中发现模式
- **强化学习**：通过试错学习最优策略

**常见算法：**
- 线性回归、逻辑回归
- 决策树、随机森林
- 支持向量机(SVM)
- 神经网络

在实际系统中，这些回答会基于您上传的专业文档生成，提供更准确和专业的内容。"""

    else:
        answer = f"""感谢您的问题："{question}"

**模拟检索结果：**
{context}

**回答：**
这是一个演示回答。在完整的RAG系统中，会执行以下步骤：

1. **文档检索**：从向量数据库中搜索与您问题最相关的文档片段
2. **上下文构建**：结合检索到的文档和历史对话构建上下文
3. **智能生成**：使用大语言模型基于上下文生成准确回答

**当前演示模式特点：**
- ✅ 完整的用户界面
- ✅ 对话历史记录
- ✅ 任务管理功能
- ⚠️ 使用模拟的文档检索
- ⚠️ 使用模板化的回答生成

**要启用完整功能，请：**
1. 在本地环境部署系统
2. 配置LLM API（魔搭、OpenAI等）
3. 上传您的专业文档
4. 享受真正的智能问答体验！"""

    return answer, len(relevant_docs)

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.header("🔧 系统控制")
        
        # 系统状态
        st.subheader("📊 系统状态")
        st.success("✅ 在线演示模式")
        st.info("🤖 模拟API: 演示模式")
        st.warning("⚠️ 需要本地部署以启用完整功能")
        
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
            if st.button("🔄 刷新页面", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🗑️ 清除历史", use_container_width=True):
                st.session_state.messages = []
                st.success("✅ 历史已清除")
        
        st.divider()
        
        # 功能说明
        with st.expander("ℹ️ 功能说明", expanded=False):
            st.markdown("""
**当前演示功能：**
- ✅ 完整UI界面
- ✅ 对话历史记录
- ✅ 任务分类管理
- ✅ 模拟智能问答

**完整版功能：**
- 🚀 多API支持
- 🚀 文档上传处理
- 🚀 向量检索
- 🚀 3090+4060分布式
- 🚀 智能记忆系统

**部署指南：**
访问GitHub仓库查看详细部署文档
            """)
        
        st.divider()
        
        # 链接
        st.subheader("🔗 相关链接")
        st.markdown("""
- [GitHub仓库](https://github.com/novenazgarfield/research-workstation)
- [部署文档](https://github.com/novenazgarfield/research-workstation/blob/main/systems/rag-system/DEPLOYMENT.md)
- [系统说明](https://github.com/novenazgarfield/research-workstation/blob/main/systems/rag-system/README.md)
        """)

def render_main_content():
    """渲染主要内容"""
    st.title("🧬 RAG智能问答系统 - 在线演示")
    
    # 系统介绍
    st.markdown("""
    欢迎使用RAG智能问答系统在线演示！这是一个功能完整的演示版本，展示了系统的核心界面和交互流程。
    
    **🎯 演示特色：**
    - 完整的用户界面体验
    - 智能对话和历史记录
    - 任务分类管理
    - 模拟的文档检索和回答生成
    """)
    
    # 标签页
    tab1, tab2, tab3 = st.tabs(["💬 智能问答", "📜 聊天历史", "📖 系统介绍"])
    
    with tab1:
        st.header("💬 智能问答")
        
        # 系统状态显示
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("📚 演示文档库已加载")
        
        with col2:
            st.success("🤖 模拟API已就绪")
        
        with col3:
            st.info("🔧 演示模式运行中")
        
        # 问题输入
        question = st.text_area(
            "🤔 请输入您的问题",
            placeholder="例如：什么是人工智能？机器学习有哪些应用？",
            help="在演示模式下，系统会提供模拟的智能回答",
            height=100
        )
        
        # 高级选项
        with st.expander("⚙️ 演示选项", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                show_retrieval = st.checkbox("显示检索过程", True)
                show_context = st.checkbox("显示上下文信息", False)
            
            with col2:
                response_style = st.selectbox("回答风格", ["详细", "简洁", "专业"])
                include_examples = st.checkbox("包含示例", True)
        
        if question and st.button("🔍 获取答案", type="primary"):
            with st.spinner("🤖 正在思考中..."):
                try:
                    # 生成回答
                    answer, doc_count = simulate_rag_response(question, st.session_state.current_task)
                    
                    # 显示回答
                    st.markdown("### 💡 回答：")
                    st.markdown(answer)
                    
                    # 显示检索信息
                    if show_retrieval:
                        with st.expander("📊 检索信息", expanded=False):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("检索文档", doc_count)
                            with col2:
                                st.metric("相关度", "85%")
                            with col3:
                                st.metric("响应时间", "1.2s")
                    
                    # 保存到历史
                    save_message("user", question, st.session_state.current_task)
                    save_message("assistant", answer, st.session_state.current_task)
                    
                    # 添加到session state
                    st.session_state.messages.append({"role": "user", "content": question})
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                    st.success("✅ 回答生成完成！")
                    
                except Exception as e:
                    st.error(f"❌ 生成回答时出错: {e}")
    
    with tab2:
        st.header("📜 聊天历史")
        
        # 历史记录控制
        col1, col2 = st.columns([3, 1])
        
        with col1:
            history_limit = st.slider("显示条数", 5, 50, 20)
        
        with col2:
            if st.button("🔄 刷新历史"):
                st.rerun()
        
        try:
            history = get_chat_history(st.session_state.current_task, history_limit)
            
            if history:
                for i, (role, content, timestamp) in enumerate(history):
                    role_icon = "🧑‍💼" if role == "user" else "🤖"
                    timestamp_str = timestamp[:19] if timestamp else ""
                    
                    with st.container():
                        st.markdown(f"**{role_icon} {role.title()}** `{timestamp_str}`")
                        
                        # 根据角色设置不同的样式
                        if role == "user":
                            st.markdown(f"> {content}")
                        else:
                            st.markdown(content)
                        
                        if i < len(history) - 1:  # 不是最后一条
                            st.divider()
            else:
                st.info("暂无聊天记录，开始您的第一次对话吧！")
                
        except Exception as e:
            st.error(f"获取聊天历史失败: {e}")
    
    with tab3:
        st.header("📖 系统介绍")
        
        st.markdown("""
        ## 🎯 关于RAG智能问答系统
        
        这是一个基于检索增强生成(RAG)技术的智能问答系统，专为科研工作者设计。
        
        ### ✨ 核心特性
        
        **🤖 多API支持**
        - 本地模型：DeepSeek、Llama等
        - 在线API：魔搭、OpenAI、智谱等
        - 自动故障转移和负载均衡
        
        **🔧 分布式计算**
        - RTX 3090：专门负责LLM推理
        - RTX 4060：负责嵌入计算和向量搜索
        - 智能任务调度和资源优化
        
        **📚 智能文档处理**
        - 支持PDF、DOCX、PPTX、Excel等格式
        - 自动文本提取和分块
        - 向量化存储和检索
        
        **🧠 记忆管理系统**
        - 永久记忆：长期知识存储
        - 临时记忆：会话上下文管理
        - 任务分类：多项目并行管理
        
        ### 🚀 部署架构
        
        ```
        用户界面 (Streamlit)
              ↓
        RAG核心系统
              ↓
        ┌─────────────┬─────────────┐
        │   RTX 3090  │   RTX 4060  │
        │  LLM推理    │  嵌入计算    │
        └─────────────┴─────────────┘
              ↓
        向量数据库 + 记忆系统
        ```
        
        ### 📋 使用场景
        
        - **科研文献问答**：快速查找和理解论文内容
        - **技术文档查询**：从大量技术文档中获取答案
        - **知识管理**：构建个人或团队知识库
        - **学习辅助**：智能答疑和知识总结
        
        ### 🔗 获取完整版本
        
        当前是在线演示版本，完整功能需要本地部署：
        
        1. **克隆仓库**：
           ```bash
           git clone https://github.com/novenazgarfield/research-workstation.git
           ```
        
        2. **安装依赖**：
           ```bash
           cd research-workstation/systems/rag-system
           pip install -r requirements.txt
           ```
        
        3. **配置系统**：
           ```bash
           python config_manager.py
           ```
        
        4. **启动系统**：
           ```bash
           python run_enhanced.py --mode web
           ```
        
        ### 💡 技术栈
        
        - **前端**：Streamlit
        - **后端**：Python + FastAPI
        - **向量数据库**：FAISS
        - **嵌入模型**：sentence-transformers
        - **LLM**：llama-cpp-python + API调用
        - **数据库**：SQLite
        - **部署**：Docker + GPU支持
        
        ---
        
        **🎉 感谢使用RAG智能问答系统！**
        
        如有问题或建议，欢迎在GitHub仓库中提出Issue。
        """)

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
        🧬 RAG智能问答系统 - 在线演示版<br>
        完整版支持多API + 分布式计算 + 智能记忆管理<br>
        <a href="https://github.com/novenazgarfield/research-workstation" target="_blank">GitHub仓库</a> | 
        <a href="https://github.com/novenazgarfield/research-workstation/blob/main/systems/rag-system/DEPLOYMENT.md" target="_blank">部署文档</a>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()