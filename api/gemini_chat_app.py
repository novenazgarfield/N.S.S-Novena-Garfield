"""
Gemini聊天应用
基于Streamlit的简单聊天界面
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(__file__))

from integrations.gemini_integration import GeminiAPIIntegration
from api_config import UserRole

# 页面配置
st.set_page_config(
    page_title="🤖 Gemini AI 聊天助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化Gemini集成
@st.cache_resource
def init_gemini():
    return GeminiAPIIntegration()

def main():
    st.title("🤖 Gemini AI 聊天助手")
    st.markdown("---")
    
    # 侧边栏 - 用户设置
    with st.sidebar:
        st.header("👤 用户设置")
        
        # 用户选择
        user_options = {
            "admin (管理员)": ("admin", "admin"),
            "vip_user (VIP用户)": ("vip_user", "vip"),
            "normal_user (普通用户)": ("normal_user", "user"),
            "guest_user (访客)": ("guest_user", "guest")
        }
        
        selected_user = st.selectbox(
            "选择用户身份",
            options=list(user_options.keys()),
            index=0
        )
        
        user_id, user_role = user_options[selected_user]
        
        st.info(f"当前用户: {user_id}\n角色: {user_role}")
        
        # 模型参数设置
        st.header("⚙️ 模型参数")
        temperature = st.slider("Temperature (创造性)", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.slider("最大输出长度", 100, 4000, 2048, 100)
        
        # 功能选择
        st.header("🛠️ 功能选择")
        feature = st.selectbox(
            "选择功能",
            ["💬 普通对话", "💻 代码生成", "📊 使用统计"]
        )
    
    # 主界面
    gemini = init_gemini()
    
    if feature == "💬 普通对话":
        st.header("💬 与Gemini对话")
        
        # 聊天历史
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # 显示聊天历史
        chat_container = st.container()
        with chat_container:
            for i, (role, message) in enumerate(st.session_state.chat_history):
                if role == "user":
                    st.markdown(f"**👤 您:** {message}")
                else:
                    st.markdown(f"**🤖 Gemini:** {message}")
                st.markdown("---")
        
        # 输入框
        user_input = st.text_area(
            "请输入您的问题:",
            height=100,
            placeholder="例如：请介绍一下人工智能的发展历史..."
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🚀 发送", type="primary"):
                if user_input.strip():
                    # 添加用户消息到历史
                    st.session_state.chat_history.append(("user", user_input))
                    
                    # 调用Gemini API
                    with st.spinner("🤖 Gemini正在思考..."):
                        result = gemini.chat_with_gemini(
                            user_id, user_role, user_input,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                    
                    if result["success"]:
                        # 添加AI回复到历史
                        st.session_state.chat_history.append(("assistant", result["response"]))
                        
                        # 显示使用统计
                        if result.get("usage_info"):
                            usage = result["usage_info"]
                            st.success(f"✅ 回复成功！今日使用: {usage['daily_usage']}/{usage['daily_limit']}")
                        
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
                else:
                    st.warning("请输入问题后再发送")
        
        with col2:
            if st.button("🗑️ 清空历史"):
                st.session_state.chat_history = []
                st.rerun()
    
    elif feature == "💻 代码生成":
        st.header("💻 AI代码生成")
        
        # 代码生成参数
        col1, col2 = st.columns(2)
        
        with col1:
            language = st.selectbox(
                "编程语言",
                ["python", "javascript", "java", "c++", "go", "rust", "html", "css"]
            )
        
        with col2:
            st.info(f"当前用户权限: {user_role}")
            if user_role not in ["vip", "admin"]:
                st.warning("⚠️ 代码生成功能需要VIP或管理员权限")
        
        # 功能描述
        description = st.text_area(
            "请描述您想要生成的代码功能:",
            height=150,
            placeholder="例如：创建一个网页爬虫，可以抓取新闻网站的标题和内容..."
        )
        
        if st.button("🚀 生成代码", type="primary"):
            if description.strip():
                with st.spinner("🤖 Gemini正在生成代码..."):
                    result = gemini.generate_code_with_gemini(
                        user_id, user_role, description, language
                    )
                
                if result["success"]:
                    st.success("✅ 代码生成成功！")
                    
                    # 显示生成的代码
                    st.code(result["code"], language=language)
                    
                    # 下载按钮
                    file_extension = {
                        "python": "py", "javascript": "js", "java": "java",
                        "c++": "cpp", "go": "go", "rust": "rs",
                        "html": "html", "css": "css"
                    }.get(language, "txt")
                    
                    st.download_button(
                        label="📥 下载代码",
                        data=result["code"],
                        file_name=f"generated_code.{file_extension}",
                        mime="text/plain"
                    )
                else:
                    st.error(f"❌ {result['message']}")
            else:
                st.warning("请输入代码功能描述")
    
    elif feature == "📊 使用统计":
        st.header("📊 Gemini使用统计")
        
        # 获取使用统计
        stats = gemini.get_user_gemini_stats(user_id)
        
        if stats:
            for key_id, stat in stats.items():
                st.subheader(f"🔑 API密钥: {key_id}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("今日使用", stat.get("daily_usage", 0))
                
                with col2:
                    st.metric("今日限制", stat.get("daily_limit", 0))
                
                with col3:
                    st.metric("本月使用", stat.get("monthly_usage", 0))
                
                with col4:
                    st.metric("本月限制", stat.get("monthly_limit", 0))
                
                # 使用率进度条
                daily_usage_rate = (stat.get("daily_usage", 0) / max(stat.get("daily_limit", 1), 1)) * 100
                monthly_usage_rate = (stat.get("monthly_usage", 0) / max(stat.get("monthly_limit", 1), 1)) * 100
                
                st.progress(daily_usage_rate / 100, text=f"今日使用率: {daily_usage_rate:.1f}%")
                st.progress(monthly_usage_rate / 100, text=f"本月使用率: {monthly_usage_rate:.1f}%")
                
                st.markdown("---")
        else:
            st.info("暂无使用统计数据")
    
    # 底部信息
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            🤖 Powered by Google Gemini 2.0 Flash | 🔧 API Management System
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()