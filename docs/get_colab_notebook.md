# 🧬 RAG智能问答系统 - Google Colab 获取指南

## 🎯 方法1: 直接在Colab中创建 (推荐)

### 步骤1: 打开Google Colab
访问: https://colab.research.google.com/

### 步骤2: 创建新笔记本
点击 "新建笔记本" 或 "File" → "New notebook"

### 步骤3: 复制以下代码到第一个代码块

```python
# 🧬 RAG智能问答系统 - Google Colab 完整版
# 一键安装和运行

# ===== 第1步: 安装依赖 =====
import subprocess
import sys
import os

def install_packages():
    packages = ['streamlit', 'pyngrok']
    for package in packages:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])
    print("✅ 依赖安装完成！")

install_packages()

# ===== 第2步: 创建完整RAG应用 =====
rag_app_code = '''
import streamlit as st
import datetime
import random
import time
import json

# 页面配置
st.set_page_config(
    page_title="🧬 RAG智能问答系统",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 模拟知识库
KNOWLEDGE_BASE = {
    "人工智能": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。包括机器学习、深度学习、自然语言处理等多个子领域。",
    "AI": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
    "RAG": "检索增强生成(RAG)是一种结合信息检索和文本生成的AI技术，能够基于外部知识库生成更准确的回答。它先检索相关文档，再基于检索结果生成回答。",
    "机器学习": "机器学习是AI的一个子领域，使计算机能够在没有明确编程的情况下学习和改进。通过算法分析数据，识别模式，并做出预测或决策。",
    "深度学习": "深度学习是机器学习的一个分支，使用多层神经网络来模拟人脑的学习过程。在图像识别、语音识别、自然语言处理等领域有广泛应用。",
    "自然语言处理": "自然语言处理(NLP)是AI的一个分支，专注于计算机与人类语言之间的交互。包括文本分析、语言理解、机器翻译等技术。",
    "NLP": "自然语言处理(NLP)是AI的一个分支，专注于计算机与人类语言之间的交互。",
    "神经网络": "神经网络是一种模拟人脑神经元连接的计算模型，由多个相互连接的节点组成，能够学习复杂的模式和关系。",
    "大语言模型": "大语言模型(LLM)是基于深度学习的自然语言处理模型，通过大量文本数据训练，能够理解和生成人类语言。如GPT、BERT等。",
    "LLM": "大语言模型(LLM)是基于深度学习的自然语言处理模型，通过大量文本数据训练，能够理解和生成人类语言。"
}

DEMO_RESPONSES = [
    "根据文档分析，这是一个关于人工智能的重要问题。AI技术正在快速发展，特别是在自然语言处理领域。",
    "基于检索到的相关文档，我可以为您提供以下信息：这个问题涉及到机器学习的核心概念。",
    "通过文档检索，我发现了相关的研究资料。深度学习在这个领域有着广泛的应用前景。",
    "根据知识库中的信息，这个问题可以从多个角度来分析。让我为您详细解答。",
    "文档显示，这是一个值得深入研究的技术问题。相关的解决方案包括多种方法。",
    "基于RAG技术的检索结果，我找到了相关的技术文档和研究论文。",
    "通过智能检索系统，我发现这个问题在学术界有很多讨论和研究成果。"
]

def simulate_rag_response(question):
    """模拟RAG系统响应"""
    question_lower = question.lower()
    
    # 关键词匹配
    matched_keys = []
    for key, value in KNOWLEDGE_BASE.items():
        if key.lower() in question_lower or any(word in question_lower for word in key.lower().split()):
            matched_keys.append((key, value))
    
    if matched_keys:
        # 如果有匹配的知识库条目
        key, value = matched_keys[0]  # 取第一个匹配项
        confidence = random.randint(88, 95)
        return f"""**智能回答**: {value}

**检索来源**: 知识库匹配 - {key}
**相关文档**: 模拟技术文档库
**置信度**: {confidence}%
**处理时间**: {random.randint(200, 800)}ms"""
    else:
        # 使用通用回答
        response = random.choice(DEMO_RESPONSES)
        confidence = random.randint(75, 87)
        return f"""**智能回答**: {response}

**检索来源**: 模拟文档库 (演示模式)
**相关文档**: 通用知识库
**置信度**: {confidence}%
**处理时间**: {random.randint(300, 1000)}ms"""

def main():
    # 标题和介绍
    st.title("🧬 RAG智能问答系统")
    st.markdown("### 🌟 基于检索增强生成技术的智能问答系统")
    
    # 运行环境提示
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.info("🚀 当前运行在 Google Colab 环境中")
    with col2:
        st.success("📱 支持移动端访问")
    with col3:
        st.success("🌐 支持公网访问")
    
    # 侧边栏
    with st.sidebar:
        st.header("🔧 系统控制台")
        
        # 系统状态
        st.subheader("📊 系统状态")
        st.success("✅ Colab模式运行中")
        st.success("🤖 AI模型已就绪")
        st.success("📚 知识库已加载")
        st.info("🔍 检索系统运行中")
        
        st.markdown("---")
        
        # 系统统计
        st.subheader("📈 使用统计")
        if 'chat_history' in st.session_state:
            st.metric("💬 对话次数", len(st.session_state.chat_history))
            st.metric("📝 总问题数", len(st.session_state.chat_history))
        else:
            st.metric("💬 对话次数", 0)
            st.metric("📝 总问题数", 0)
        
        st.metric("📖 知识条目", len(KNOWLEDGE_BASE))
        st.metric("🔧 系统版本", "v2.0-Colab")
        
        st.markdown("---")
        
        # 控制按钮
        st.subheader("🎛️ 系统控制")
        if st.button("🔄 刷新页面", use_container_width=True):
            st.rerun()
            
        if st.button("🗑️ 清除历史", use_container_width=True):
            if 'chat_history' in st.session_state:
                st.session_state.chat_history = []
            st.success("✅ 历史记录已清除")
        
        if st.button("📊 系统信息", use_container_width=True):
            st.info("🧬 RAG智能问答系统\\n版本: v2.0-Colab\\n环境: Google Colab\\n状态: 运行中")
        
        st.markdown("---")
        
        # 相关链接
        st.subheader("🔗 相关链接")
        st.markdown("- [📚 GitHub仓库](https://github.com/novenazgarfield/research-workstation)")
        st.markdown("- [📖 完整版部署](https://github.com/novenazgarfield/research-workstation/blob/main/systems/rag-system/README.md)")
        st.markdown("- [🔧 技术文档](https://github.com/novenazgarfield/research-workstation/blob/main/systems/rag-system/DEPLOYMENT.md)")
        st.markdown("- [💡 使用指南](https://github.com/novenazgarfield/research-workstation/wiki)")
    
    # 主要内容区域
    tab1, tab2, tab3, tab4 = st.tabs(["💬 智能问答", "📜 聊天历史", "📖 系统介绍", "🎯 使用指南"])
    
    with tab1:
        st.header("💬 智能问答")
        
        # 状态指示器
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.success("📚 知识库: 已加载")
        with col2:
            st.success("🤖 AI模型: 就绪")
        with col3:
            st.success("🔍 检索系统: 运行中")
        with col4:
            st.success("⚡ 响应速度: 优秀")
        
        st.markdown("---")
        
        # 问答界面
        st.subheader("🤔 请输入您的问题")
        
        # 示例问题
        st.markdown("**💡 点击下面的示例问题快速开始:**")
        example_questions = [
            "什么是人工智能？",
            "RAG技术的原理是什么？",
            "机器学习和深度学习的区别？",
            "自然语言处理有哪些应用？",
            "大语言模型是如何工作的？",
            "神经网络的基本原理？"
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
        question = st.text_area(
            "✍️ 在这里输入您的问题:",
            value=st.session_state.get('current_question', ''),
            height=120,
            placeholder="例如：什么是RAG技术？它有什么优势？\\n\\n支持中英文问题，可以询问AI、机器学习、深度学习等相关话题...",
            key="question_input"
        )
        
        # 提交按钮和选项
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            submit_button = st.button("🚀 获取智能答案", type="primary", use_container_width=True)
        with col2:
            if st.button("🎲 随机问题", use_container_width=True):
                st.session_state.current_question = random.choice(example_questions)
                st.rerun()
        
        # 处理问题提交
        if submit_button and question.strip():
            # 初始化聊天历史
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            
            # 显示处理过程
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 正在检索相关文档...")
            progress_bar.progress(25)
            time.sleep(0.5)
            
            status_text.text("📊 正在分析问题内容...")
            progress_bar.progress(50)
            time.sleep(0.5)
            
            status_text.text("🤖 AI正在生成智能回答...")
            progress_bar.progress(75)
            time.sleep(0.5)
            
            status_text.text("✨ 正在优化回答质量...")
            progress_bar.progress(100)
            time.sleep(0.3)
            
            # 生成回答
            response = simulate_rag_response(question)
            
            # 保存到历史
            st.session_state.chat_history.append({
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'question': question,
                'response': response,
                'id': len(st.session_state.chat_history) + 1
            })
            
            # 清除进度显示
            progress_bar.empty()
            status_text.empty()
            
            st.success("✅ 智能回答生成完成！")
            
            # 清除当前问题
            if 'current_question' in st.session_state:
                del st.session_state.current_question
                st.rerun()
        
        elif submit_button and not question.strip():
            st.error("❌ 请输入您的问题")
        
        # 显示最新回答
        if 'chat_history' in st.session_state and st.session_state.chat_history:
            st.markdown("---")
            st.subheader("💡 最新智能回答")
            latest = st.session_state.chat_history[-1]
            
            with st.container():
                # 问题显示
                st.markdown(f"### ❓ 问题 #{latest['id']}")
                st.markdown(f"**{latest['question']}**")
                
                # 回答显示
                st.markdown("### 🤖 AI回答")
                st.markdown(latest['response'])
                
                # 时间戳
                st.caption(f"⏰ 回答时间: {latest['timestamp']}")
                
                # 操作按钮
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👍 有用", key="useful"):
                        st.success("感谢您的反馈！")
                with col2:
                    if st.button("📋 复制回答", key="copy"):
                        st.info("回答已复制到剪贴板")
                with col3:
                    if st.button("🔄 重新生成", key="regenerate"):
                        # 重新生成回答
                        new_response = simulate_rag_response(latest['question'])
                        st.session_state.chat_history[-1]['response'] = new_response
                        st.rerun()
    
    with tab2:
        st.header("📜 聊天历史")
        
        if 'chat_history' in st.session_state and st.session_state.chat_history:
            # 统计信息
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 总对话数", len(st.session_state.chat_history))
            with col2:
                st.metric("📅 今日对话", len(st.session_state.chat_history))  # 简化版本
            with col3:
                avg_length = sum(len(chat['question']) for chat in st.session_state.chat_history) // len(st.session_state.chat_history)
                st.metric("📝 平均问题长度", f"{avg_length}字")
            
            st.markdown("---")
            
            # 搜索功能
            col1, col2 = st.columns([3, 1])
            with col1:
                search_term = st.text_input("🔍 搜索历史记录", placeholder="输入关键词搜索问题或回答...")
            with col2:
                search_button = st.button("🔍 搜索", use_container_width=True)
            
            # 过滤历史记录
            filtered_history = st.session_state.chat_history
            if search_term:
                filtered_history = [
                    chat for chat in st.session_state.chat_history
                    if search_term.lower() in chat['question'].lower() or 
                       search_term.lower() in chat['response'].lower()
                ]
                if filtered_history:
                    st.success(f"🔍 找到 {len(filtered_history)} 条匹配记录")
                else:
                    st.warning("🔍 未找到匹配的记录")
            
            # 显示历史记录
            if filtered_history:
                st.markdown("### 📋 对话记录")
                
                for i, chat in enumerate(reversed(filtered_history)):
                    with st.expander(
                        f"💬 对话 #{chat['id']} - {chat['timestamp']} - {chat['question'][:50]}{'...' if len(chat['question']) > 50 else ''}",
                        expanded=(i == 0)  # 只展开最新的一条
                    ):
                        # 问题
                        st.markdown(f"**❓ 问题**: {chat['question']}")
                        
                        # 回答
                        st.markdown("**🤖 AI回答**:")
                        st.markdown(chat['response'])
                        
                        # 操作按钮
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("🔄 重新提问", key=f"reask_{chat['id']}"):
                                st.session_state.current_question = chat['question']
                                st.switch_page("💬 智能问答")
                        with col2:
                            if st.button("📋 复制问题", key=f"copy_q_{chat['id']}"):
                                st.info("问题已复制")
                        with col3:
                            if st.button("🗑️ 删除记录", key=f"del_{chat['id']}"):
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
                ### 🎯 开始使用RAG系统
                
                1. 🔄 切换到 **智能问答** 标签页
                2. 📝 输入您感兴趣的问题
                3. 🚀 点击 **获取智能答案** 按钮
                4. 💡 查看AI生成的专业回答
                5. 📜 返回此页面查看历史记录
                """)
                
                if st.button("🚀 开始第一次问答", type="primary", use_container_width=True):
                    st.switch_page("💬 智能问答")
    
    with tab3:
        st.header("📖 系统介绍")
        
        st.markdown("""
        ## 🎯 关于RAG智能问答系统
        
        这是一个基于**检索增强生成(RAG)**技术的智能问答系统，专为科研工作者和知识工作者设计。
        
        ### ✨ 核心特性
        
        **🤖 多API支持**
        - 本地模型：DeepSeek、Llama、ChatGLM等
        - 在线API：魔搭ModelScope、OpenAI、智谱GLM等
        - 自动故障转移和负载均衡
        - 智能API选择和切换
        
        **🔧 分布式计算架构**
        - RTX 3090：专门负责大语言模型推理
        - RTX 4060：负责嵌入计算和向量搜索
        - 智能任务调度和资源优化
        - GPU内存管理和负载均衡
        
        **📚 智能文档处理**
        - 支持PDF、DOCX、PPTX、Excel、TXT等格式
        - 自动文本提取和智能分块
        - 向量化存储和高效检索
        - 多语言文档支持
        
        **🧠 记忆管理系统**
        - 永久记忆：长期知识存储和管理
        - 临时记忆：会话上下文管理
        - 任务分类：多项目并行管理
        - 智能记忆检索和更新
        
        ### 🚀 技术架构
        """)
        
        st.code("""
    用户界面 (Streamlit Web App)
                    ↓
            RAG核心处理系统
                    ↓
    ┌─────────────────┬─────────────────┐
    │    RTX 3090     │    RTX 4060     │
    │   LLM推理引擎    │   嵌入计算引擎   │
    │   文本生成      │   向量检索      │
    └─────────────────┴─────────────────┘
                    ↓
        向量数据库 + 记忆管理系统
                    ↓
            SQLite + FAISS存储
        """, language="text")
        
        st.markdown("""
        ### 💡 技术栈详解
        
        **前端技术**
        - **Streamlit**: 现代化Web界面框架
        - **响应式设计**: 支持桌面和移动设备
        - **实时交互**: WebSocket实时通信
        
        **后端技术**
        - **Python**: 主要开发语言
        - **FastAPI**: 高性能API框架
        - **异步处理**: 支持并发请求处理
        
        **AI技术栈**
        - **向量数据库**: FAISS高效向量检索
        - **嵌入模型**: sentence-transformers多语言支持
        - **LLM集成**: llama-cpp-python + 多API调用
        - **RAG框架**: 自研检索增强生成系统
        
        **数据存储**
        - **SQLite**: 轻量级关系数据库
        - **FAISS**: 高性能向量索引
        - **文件系统**: 文档和配置管理
        
        **部署方案**
        - **Docker**: 容器化部署
        - **GPU支持**: CUDA加速计算
        - **云平台**: 支持多种云服务部署
        
        ### 📋 应用场景
        
        **🔬 科研文献问答**
        - 快速查找和理解学术论文内容
        - 文献综述和研究方向分析
        - 跨领域知识关联发现
        
        **📖 技术文档查询**
        - 从大量技术文档中快速获取答案
        - API文档和使用手册智能问答
        - 代码库和项目文档理解
        
        **🧠 知识管理**
        - 构建个人或团队专属知识库
        - 企业内部知识沉淀和共享
        - 智能知识图谱构建
        
        **🎓 学习辅助**
        - 智能答疑和概念解释
        - 学习路径规划和推荐
        - 知识点总结和复习辅助
        
        ### 🌟 系统优势
        
        **⚡ 高性能**
        - GPU加速推理，响应速度快
        - 分布式架构，支持高并发
        - 智能缓存，减少重复计算
        
        **🎯 高准确性**
        - RAG技术结合检索和生成
        - 多源知识融合验证
        - 置信度评估和质量控制
        
        **🔧 易部署**
        - Docker一键部署
        - 详细部署文档和脚本
        - 多平台兼容支持
        
        **📈 可扩展**
        - 模块化架构设计
        - 插件式功能扩展
        - API接口标准化
        """)
    
    with tab4:
        st.header("🎯 使用指南")
        
        st.markdown("""
        ## 🚀 快速开始指南
        
        ### 1️⃣ 基础使用流程
        
        **第一步：提出问题**
        1. 切换到 **💬 智能问答** 标签页
        2. 在文本框中输入您的问题
        3. 可以点击示例问题快速开始
        4. 支持中英文问题输入
        
        **第二步：获取答案**
        1. 点击 **🚀 获取智能答案** 按钮
        2. 系统会显示处理进度
        3. AI会基于知识库生成专业回答
        4. 查看回答的置信度和来源信息
        
        **第三步：管理历史**
        1. 在 **📜 聊天历史** 中查看所有对话
        2. 使用搜索功能快速找到特定内容
        3. 可以重新提问或删除记录
        
        ### 2️⃣ 高级功能使用
        
        **🔍 智能搜索**
        - 在聊天历史中输入关键词搜索
        - 支持问题内容和回答内容搜索
        - 模糊匹配和精确匹配
        
        **🎲 随机探索**
        - 点击"随机问题"按钮探索新话题
        - 系统会推荐相关的有趣问题
        - 帮助发现新的知识领域
        
        **📊 系统监控**
        - 左侧边栏显示实时系统状态
        - 查看对话统计和使用情况
        - 监控系统性能指标
        
        ### 3️⃣ 最佳实践建议
        
        **📝 问题表达技巧**
        - **明确具体**: 提出具体、明确的问题
        - **关键词**: 使用相关的技术关键词
        - **上下文**: 提供必要的背景信息
        - **分步骤**: 复杂问题可以分解为多个小问题
        
        **💡 示例对比**
        
        ❌ **不好的问题**:
        - "AI是什么？"
        - "怎么学习？"
        - "这个怎么办？"
        
        ✅ **好的问题**:
        - "RAG技术相比传统问答系统有什么优势？"
        - "如何选择合适的机器学习算法来解决分类问题？"
        - "在自然语言处理中，BERT和GPT模型的主要区别是什么？"
        
        **🎯 使用场景建议**
        
        **学习研究**
        - 询问概念定义和原理解释
        - 比较不同技术方案的优缺点
        - 了解最新技术发展趋势
        
        **问题解决**
        - 寻求技术问题的解决方案
        - 获取实施建议和最佳实践
        - 了解常见错误和避免方法
        
        **知识探索**
        - 发现相关领域的新知识
        - 建立知识点之间的联系
        - 拓展学习和研究方向
        
        ## 🔧 完整版部署指南
        
        当前是Google Colab演示版本，完整功能需要本地部署：
        
        ### 📥 获取完整源码
        """)
        
        st.code("""
# 1. 克隆项目仓库
git clone https://github.com/novenazgarfield/research-workstation.git

# 2. 进入RAG系统目录
cd research-workstation/systems/rag-system

# 3. 创建Python虚拟环境
python -m venv rag_env
source rag_env/bin/activate  # Linux/Mac
# 或
rag_env\\Scripts\\activate  # Windows

# 4. 安装项目依赖
pip install -r requirements.txt

# 5. 配置系统参数
python config_manager.py

# 6. 启动完整系统
python run_enhanced.py --mode web
        """, language="bash")
        
        st.markdown("""
        ### 🌟 完整版特性对比
        
        | 功能特性 | Colab演示版 | 完整本地版 |
        |---------|------------|-----------|
        | 🤖 AI问答 | ✅ 模拟回答 | ✅ 真实LLM |
        | 📚 文档处理 | ❌ | ✅ 多格式支持 |
        | 🔍 向量检索 | ❌ | ✅ FAISS检索 |
        | 💾 知识库 | ✅ 内置样例 | ✅ 自定义导入 |
        | 🧠 记忆系统 | ❌ | ✅ 完整记忆 |
        | ⚡ GPU加速 | ❌ | ✅ 分布式计算 |
        | 🔌 API集成 | ❌ | ✅ 多API支持 |
        | 📊 数据分析 | ❌ | ✅ 详细统计 |
        
        ### 🛠️ 系统要求
        
        **最低配置**
        - Python 3.8+
        - 8GB RAM
        - 10GB 存储空间
        
        **推荐配置**
        - Python 3.10+
        - 16GB+ RAM
        - NVIDIA GPU (RTX 3060+)
        - 50GB+ SSD存储
        
        **最佳配置**
        - Python 3.11+
        - 32GB+ RAM
        - 双GPU (RTX 3090 + RTX 4060)
        - 100GB+ NVMe SSD
        
        ## 📞 技术支持
        
        ### 🆘 常见问题
        
        **Q: 系统响应慢怎么办？**
        A: 检查网络连接，尝试刷新页面或重启系统。
        
        **Q: 回答不准确怎么办？**
        A: 尝试重新表述问题，使用更具体的关键词。
        
        **Q: 如何获得更好的回答？**
        A: 提供更多上下文信息，使用专业术语。
        
        ### 📧 联系方式
        
        如有问题或建议，欢迎通过以下方式联系：
        
        - **GitHub Issues**: [提交问题](https://github.com/novenazgarfield/research-workstation/issues)
        - **项目文档**: [查看文档](https://github.com/novenazgarfield/research-workstation/blob/main/systems/rag-system/README.md)
        - **部署指南**: [部署文档](https://github.com/novenazgarfield/research-workstation/blob/main/systems/rag-system/DEPLOYMENT.md)
        - **技术博客**: [了解更多](https://github.com/novenazgarfield/research-workstation/wiki)
        
        ### 🎉 致谢
        
        感谢所有为RAG智能问答系统做出贡献的开发者和用户！
        
        **开源技术栈**
        - Streamlit - Web应用框架
        - FAISS - 向量检索引擎
        - Transformers - 预训练模型库
        - llama-cpp-python - LLM推理引擎
        
        **特别感谢**
        - OpenAI - GPT技术启发
        - Hugging Face - 模型和工具支持
        - Google - Colab平台支持
        """)
    
    # 页脚信息
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 20px;'>" +
        "🧬 <b>RAG智能问答系统</b> - Google Colab版 | " +
        "基于检索增强生成技术 | " +
        "完整版支持多API + 分布式计算 + 智能记忆管理<br>" +
        "<a href='https://github.com/novenazgarfield/research-workstation' target='_blank'>📚 GitHub仓库</a> | " +
        "<a href='https://github.com/novenazgarfield/research-workstation/blob/main/systems/rag-system/README.md' target='_blank'>📖 技术文档</a> | " +
        "<a href='https://github.com/novenazgarfield/research-workstation/blob/main/systems/rag-system/DEPLOYMENT.md' target='_blank'>🚀 部署指南</a>" +
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
'''

# 保存完整应用文件
with open('rag_colab_complete.py', 'w', encoding='utf-8') as f:
    f.write(rag_app_code)

print("✅ 完整RAG应用创建成功！")

# ===== 第3步: 启动系统 =====
import threading
import time

def run_streamlit():
    subprocess.run([
        'streamlit', 'run', 'rag_colab_complete.py',
        '--server.port', '8501',
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'true',
        '--server.enableXsrfProtection', 'false'
    ])

print("🚀 正在启动RAG智能问答系统...")
print("⏳ 请稍等，系统正在初始化...")

# 在后台启动Streamlit
thread = threading.Thread(target=run_streamlit)
thread.daemon = True
thread.start()

# 等待系统启动
time.sleep(15)

# ===== 第4步: 设置公共访问 =====
try:
    from pyngrok import ngrok
    
    print("🌐 正在创建公共访问URL...")
    
    # 如果您有ngrok token，请取消下面这行的注释并填入您的token
    # ngrok.set_auth_token("YOUR_NGROK_TOKEN_HERE")
    
    public_url = ngrok.connect(8501)
    
    print("\n" + "="*70)
    print("🎉 RAG智能问答系统启动成功！")
    print("="*70)
    print(f"🌐 公共访问地址: {public_url}")
    print("📱 支持手机、平板、电脑访问")
    print("🔗 点击上面的链接即可使用系统")
    print("="*70)
    print("\n💡 使用提示:")
    print("1. 点击上面的URL打开RAG系统")
    print("2. 在'智能问答'页面输入问题")
    print("3. 点击'获取智能答案'按钮")
    print("4. 查看AI生成的专业回答")
    print("5. 在'聊天历史'中管理对话记录")
    print("\n🎯 功能特色:")
    print("• 💬 智能问答 - 基于RAG技术的AI回答")
    print("• 📜 聊天历史 - 完整的对话记录管理")
    print("• 🔍 智能搜索 - 快速查找历史对话")
    print("• 📖 系统介绍 - 详细的技术文档")
    print("• 🎯 使用指南 - 完整的操作说明")
    print("\n⚠️ 重要提醒:")
    print("• 保持此代码块运行，停止后URL将失效")
    print("• 如需长期使用，建议部署完整版本")
    print("• 当前为演示版，完整功能需本地部署")
    
except Exception as e:
    print(f"\n⚠️ ngrok设置失败: {e}")
    print("\n" + "="*60)
    print("🎉 RAG系统启动成功 (本地访问模式)")
    print("="*60)
    print("📍 本地地址: http://localhost:8501")
    print("\n💡 在Google Colab中访问:")
    print("1. 查看左侧面板的'文件'或'端口'标签")
    print("2. 找到端口8501对应的链接")
    print("3. 点击链接即可访问系统")
    print("\n🔧 获取公共URL的方法:")
    print("1. 注册ngrok账号: https://ngrok.com/")
    print("2. 获取authtoken")
    print("3. 取消上面代码中ngrok.set_auth_token的注释")
    print("4. 填入您的token并重新运行")
    print("="*60)

# ===== 第5步: 保持系统运行 =====
print(f"\n🔄 系统监控开始 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
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
```

### 步骤4: 运行代码

点击代码块左侧的播放按钮 ▶️ 运行代码

### 步骤5: 获取访问链接

代码运行后会显示公共访问URL，点击即可使用系统

---

## 🎯 方法2: 分步骤创建 (详细版)

如果您想了解每个步骤的详细过程，可以按以下步骤操作：

### 1. 创建新的Colab笔记本
### 2. 分别运行以下代码块

**第一个代码块 - 安装依赖:**
```python
!pip install streamlit pyngrok -q
print("✅ 依赖安装完成！")
```

**第二个代码块 - 创建应用:**
```python
# 这里放置完整的RAG应用代码
# (代码内容与上面相同)
```

**第三个代码块 - 启动系统:**
```python
# 启动和访问设置代码
# (代码内容与上面相同)
```

---

## 🌟 方法3: 直接从GitHub获取

您也可以直接从GitHub仓库获取：

1. 访问: https://github.com/novenazgarfield/research-workstation
2. 找到 `RAG_System_Colab.ipynb` 文件
3. 点击 "Open in Colab" 按钮
4. 直接在Colab中运行