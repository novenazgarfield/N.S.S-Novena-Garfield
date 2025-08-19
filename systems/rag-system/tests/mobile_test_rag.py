import streamlit as st
import time
import datetime
import hashlib

# 页面配置
st.set_page_config(
    page_title="💬 RAG智能对话 - 测试版",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 简化的系统配置
SYSTEM_CONFIG = {
    "system_name": "RAG智能对话",
    "version": "v3.2-Test",
    "admin_password": "rag2024",
    "max_file_size": 50,
    "max_daily_queries": 500,
    "max_message_length": 5000,
    "chat_speed": 1.0,
    "theme_mode": "light"
}

def check_password():
    """检查密码"""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    if st.session_state.password_correct:
        return True
    
    st.markdown("# 🔐 访问验证")
    password = st.text_input("请输入访问密码", type="password")
    
    if st.button("🚀 进入系统"):
        if password == SYSTEM_CONFIG["admin_password"]:
            st.session_state.password_correct = True
            st.success("✅ 验证成功！")
            st.rerun()
        else:
            st.error("❌ 密码错误")
    
    st.info("💡 提示：密码是 rag2024")
    return False

def init_session_state():
    """初始化会话状态"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 您好！我是RAG智能对话助手。\n\n✨ **我可以帮您：**\n• 💬 智能问答对话\n• 📄 分析上传的文档\n• 🔍 检索相关信息\n\n请开始我们的对话吧！",
                "timestamp": datetime.datetime.now().strftime("%H:%M")
            }
        ]
    
    if "uploaded_documents" not in st.session_state:
        st.session_state.uploaded_documents = {}
    
    if "query_count" not in st.session_state:
        st.session_state.query_count = 0
    
    if "show_settings" not in st.session_state:
        st.session_state.show_settings = False

def generate_response(prompt, context=""):
    """生成AI回答"""
    responses = {
        "你好": "您好！很高兴与您对话。我是RAG智能助手，可以帮您解答问题和分析文档。",
        "什么是RAG": "RAG（检索增强生成）是一种AI技术，结合了信息检索和文本生成。它先从知识库中检索相关信息，然后基于检索结果生成准确的回答。",
        "如何使用": "使用很简单！您可以：\n1. 💬 直接输入问题进行对话\n2. 📄 上传文档进行分析\n3. ⚙️ 点击设置按钮调整参数",
        "分析文档": "请先上传文档，我就可以为您分析文档内容了。支持PDF、Word、PPT等多种格式。"
    }
    
    # 检查是否有匹配的预设回答
    for key, value in responses.items():
        if key in prompt:
            return value
    
    # 如果有文档上下文
    if context:
        return f"基于您上传的文档，我分析如下：\n\n{context[:500]}...\n\n这是文档的主要内容概述。您想了解文档的哪个具体方面？"
    
    # 默认回答
    return f"感谢您的问题：「{prompt}」\n\n这是一个很有意思的话题。基于RAG技术，我正在为您检索相关信息并生成回答。\n\n💡 **提示：** 您可以上传相关文档，我能提供更准确的分析。"

def display_chat_messages():
    """显示聊天消息"""
    st.markdown("### 💬 对话记录")
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div style="background: #e3f2fd; padding: 10px; border-radius: 10px; margin: 10px 0; margin-left: 20%;">
                <strong>👤 您</strong> {message.get('timestamp', '')}
                <br>{message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: #f5f5f5; padding: 10px; border-radius: 10px; margin: 10px 0; margin-right: 20%;">
                <strong>🤖 AI助手</strong> {message.get('timestamp', '')}
                <br>{message['content']}
            </div>
            """, unsafe_allow_html=True)

def show_settings_panel():
    """显示设置面板"""
    st.markdown("## ⚙️ 系统设置")
    
    tab1, tab2 = st.tabs(["⚡ 性能", "📊 信息"])
    
    with tab1:
        st.markdown("### ⚡ 性能设置")
        
        chat_speed = st.slider(
            "🤖 AI回答速度",
            min_value=0.1,
            max_value=5.0,
            value=SYSTEM_CONFIG["chat_speed"],
            step=0.1,
            help="数值越小回答越快"
        )
        SYSTEM_CONFIG["chat_speed"] = chat_speed
        
        if chat_speed <= 0.5:
            st.info("⚡ 极快模式")
        elif chat_speed <= 1.5:
            st.info("🚀 快速模式")
        else:
            st.info("🐢 正常模式")
    
    with tab2:
        st.markdown("### 📊 系统信息")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💬 对话", len(st.session_state.messages)//2)
        with col2:
            st.metric("📄 文档", len(st.session_state.uploaded_documents))
        with col3:
            st.metric("📈 查询", st.session_state.query_count)
    
    if st.button("❌ 关闭设置", type="primary"):
        st.session_state.show_settings = False
        st.rerun()

def main():
    """主函数"""
    if not check_password():
        return
    
    init_session_state()
    
    # 标题和设置按钮
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("# 💬 RAG智能对话")
        st.markdown("### 📱 移动端测试版")
    with col2:
        if st.button("⚙️", help="设置"):
            st.session_state.show_settings = not st.session_state.show_settings
            st.rerun()
    
    if st.session_state.show_settings:
        show_settings_panel()
        return
    
    # 显示对话
    display_chat_messages()
    
    # 智能提示（只在开始时显示）
    if len(st.session_state.messages) <= 1:
        with st.expander("💡 试试这些问题", expanded=False):
            col1, col2 = st.columns(2)
            suggestions = ["你好", "什么是RAG？", "如何使用？", "分析文档"]
            
            for i, suggestion in enumerate(suggestions):
                col_idx = i % 2
                with [col1, col2][col_idx]:
                    if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                        st.session_state.temp_message = suggestion
                        st.rerun()
    
    # 处理建议点击
    if hasattr(st.session_state, 'temp_message'):
        prompt = st.session_state.temp_message
        del st.session_state.temp_message
        
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.datetime.now().strftime("%H:%M")
        }
        st.session_state.messages.append(user_message)
        
        with st.spinner("🤔 AI思考中..."):
            time.sleep(SYSTEM_CONFIG["chat_speed"])
            response = generate_response(prompt)
        
        assistant_message = {
            "role": "assistant",
            "content": response,
            "timestamp": datetime.datetime.now().strftime("%H:%M")
        }
        st.session_state.messages.append(assistant_message)
        st.session_state.query_count += 1
        st.rerun()
    
    # 文件上传
    st.markdown("---")
    st.markdown("### 📄 文档上传")
    
    uploaded_file = st.file_uploader(
        "选择文档",
        type=["pdf", "docx", "txt", "md"],
        help="支持PDF、Word、文本等格式"
    )
    
    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.info(f"📄 **{uploaded_file.name}** ({file_size_mb:.2f} MB)")
        
        if st.button("🚀 上传分析", type="primary", use_container_width=True):
            with st.spinner("🔄 处理中..."):
                # 模拟文档处理
                content = f"这是文档 '{uploaded_file.name}' 的内容摘要。文档包含了重要信息，可以用于问答分析。"
                
                doc_id = hashlib.md5(f"{uploaded_file.name}{time.time()}".encode()).hexdigest()[:8]
                st.session_state.uploaded_documents[doc_id] = {
                    "name": uploaded_file.name,
                    "content": content,
                    "upload_time": datetime.datetime.now().strftime("%m-%d %H:%M")
                }
                
                st.success("✅ 上传成功！")
                st.balloons()
                
                # 自动分析
                analysis_message = f"已上传文档 '{uploaded_file.name}'，请分析内容。"
                
                user_message = {
                    "role": "user",
                    "content": analysis_message,
                    "timestamp": datetime.datetime.now().strftime("%H:%M")
                }
                st.session_state.messages.append(user_message)
                
                response = generate_response(analysis_message, content)
                assistant_message = {
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.datetime.now().strftime("%H:%M")
                }
                st.session_state.messages.append(assistant_message)
                st.session_state.query_count += 1
                time.sleep(1)
                st.rerun()
    
    # 已上传文档
    if st.session_state.uploaded_documents:
        st.markdown("### 📋 已上传文档")
        for doc_id, doc_info in st.session_state.uploaded_documents.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"📄 {doc_info['name']}")
                st.caption(f"上传时间: {doc_info['upload_time']}")
            with col2:
                if st.button("🗑️", key=f"del_{doc_id}", help="删除"):
                    del st.session_state.uploaded_documents[doc_id]
                    st.success("✅ 已删除")
                    st.rerun()
    
    # 聊天输入
    st.markdown("---")
    st.markdown("### 💬 开始对话")
    
    if prompt := st.chat_input("💬 输入消息...", max_chars=SYSTEM_CONFIG["max_message_length"]):
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.datetime.now().strftime("%H:%M")
        }
        st.session_state.messages.append(user_message)
        
        with st.spinner("🤔 AI思考中..."):
            time.sleep(SYSTEM_CONFIG["chat_speed"])
            
            context = ""
            if st.session_state.uploaded_documents:
                latest_doc = list(st.session_state.uploaded_documents.values())[-1]
                context = latest_doc["content"]
            
            response = generate_response(prompt, context)
        
        assistant_message = {
            "role": "assistant",
            "content": response,
            "timestamp": datetime.datetime.now().strftime("%H:%M")
        }
        st.session_state.messages.append(assistant_message)
        st.session_state.query_count += 1
        st.rerun()
    
    # 页脚
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #666; font-size: 0.8rem;'>"
        f"💬 {SYSTEM_CONFIG['system_name']} {SYSTEM_CONFIG['version']} | "
        f"📊 查询: {st.session_state.query_count} | "
        f"📄 文档: {len(st.session_state.uploaded_documents)}"
        f"</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()