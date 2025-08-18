"""
移动端RAG应用主程序
专为移动设备优化的完整应用
"""

import streamlit as st
import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'mobile'))

from base_components import SessionManager, AuthManager, system_config
from mobile_interface import mobile_interface
from settings_panel import settings_panel

# 页面配置
st.set_page_config(
    page_title="💬 RAG智能对话 - 移动端",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    """移动端主程序"""
    # 密码验证
    if not AuthManager.check_password(system_config.get("admin_password")):
        return
    
    # 初始化会话状态
    SessionManager.init_session_state()
    
    # 设置设备类型
    st.session_state.device_type = "mobile"
    
    # 显示设置面板
    if st.session_state.show_settings:
        settings_panel.render_settings_panel("mobile")
        return
    
    # 渲染移动端界面
    mobile_interface.render_complete_interface()

if __name__ == "__main__":
    main()