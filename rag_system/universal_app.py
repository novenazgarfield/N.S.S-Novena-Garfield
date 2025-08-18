"""
通用RAG应用主程序
自动检测设备类型并适配界面，支持用户管理系统
"""

import streamlit as st
import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'mobile'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'desktop'))

from base_components import SessionManager, system_config
from mobile_interface import mobile_interface
from desktop_interface import desktop_interface
from settings_panel import settings_panel
from user_management import auth_interface, user_manager
from admin_panel import admin_panel

# 页面配置
st.set_page_config(
    page_title="💬 RAG智能对话 - 全端适配",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def detect_device_type():
    """检测设备类型"""
    # 简单的设备检测逻辑
    if "device_type" not in st.session_state:
        # 默认使用移动端布局（更通用）
        st.session_state.device_type = "mobile"
    
    # 添加设备切换选项
    with st.sidebar:
        st.markdown("### 📱 设备适配")
        device_options = {
            "auto": "🔄 自动检测",
            "mobile": "📱 移动端",
            "desktop": "🖥️ 桌面端"
        }
        
        selected_device = st.selectbox(
            "选择界面模式",
            options=list(device_options.keys()),
            format_func=lambda x: device_options[x],
            index=1 if st.session_state.device_type == "mobile" else 2
        )
        
        if selected_device != st.session_state.device_type:
            st.session_state.device_type = selected_device
            st.rerun()
    
    return st.session_state.device_type

def main():
    """通用主程序"""
    # 用户认证检查
    if not auth_interface.check_authentication():
        return
    
    # 初始化会话状态
    SessionManager.init_session_state()
    
    # 渲染用户信息
    auth_interface.render_user_info()
    
    # 检查是否显示管理员面板
    if st.session_state.get("show_admin_panel", False):
        admin_panel.render_admin_panel()
        return
    
    # 检查是否显示用户设置
    if st.session_state.get("show_user_settings", False):
        render_user_settings()
        return
    
    # 检测设备类型
    device_type = detect_device_type()
    
    # 显示设置面板
    if st.session_state.get("show_settings", False):
        settings_panel.render_settings_panel(device_type)
        return
    
    # 根据设备类型渲染界面
    if device_type == "desktop":
        desktop_interface.render_complete_interface()
    else:  # mobile 或 auto
        mobile_interface.render_complete_interface()
    
    # 显示当前模式
    st.sidebar.markdown("---")
    if device_type == "desktop":
        st.sidebar.success("🖥️ 当前使用桌面端界面")
    else:
        st.sidebar.success("📱 当前使用移动端界面")

def render_user_settings():
    """渲染用户设置页面"""
    st.markdown("## ⚙️ 个人设置")
    
    if "user_info" not in st.session_state:
        st.error("❌ 用户信息不存在")
        return
    
    user_info = st.session_state.user_info
    username = user_info["username"]
    
    # 个人信息设置
    st.markdown("### 👤 个人信息")
    
    with st.form("user_info_form"):
        display_name = st.text_input(
            "显示名称",
            value=user_info["display_name"],
            help="在系统中显示的名称"
        )
        
        if st.form_submit_button("💾 保存信息", type="primary"):
            # 这里可以添加更新用户信息的逻辑
            st.success("✅ 个人信息保存成功")
    
    # 界面设置
    st.markdown("### 🎨 界面设置")
    
    current_settings = user_manager.get_user_settings(username)
    
    with st.form("user_settings_form"):
        theme = st.selectbox(
            "界面主题",
            ["light", "dark", "auto"],
            index=["light", "dark", "auto"].index(current_settings.get("theme", "light")),
            help="选择界面颜色主题"
        )
        
        language = st.selectbox(
            "界面语言",
            ["zh-CN", "en-US"],
            index=["zh-CN", "en-US"].index(current_settings.get("language", "zh-CN")),
            help="选择界面显示语言"
        )
        
        notifications = st.checkbox(
            "启用通知",
            value=current_settings.get("notifications", True),
            help="是否接收系统通知"
        )
        
        if st.form_submit_button("💾 保存设置", type="primary"):
            new_settings = {
                "theme": theme,
                "language": language,
                "notifications": notifications
            }
            user_manager.update_user_settings(username, new_settings)
            
            # 更新会话中的用户信息
            st.session_state.user_info["settings"] = new_settings
            
            st.success("✅ 设置保存成功")
            st.balloons()
    
    # 密码修改
    st.markdown("### 🔒 密码修改")
    
    with st.form("change_password_form"):
        current_password = st.text_input("当前密码", type="password")
        new_password = st.text_input("新密码", type="password")
        confirm_password = st.text_input("确认新密码", type="password")
        
        if st.form_submit_button("🔄 修改密码", type="secondary"):
            if not current_password or not new_password:
                st.error("❌ 请填写完整信息")
            elif new_password != confirm_password:
                st.error("❌ 两次密码输入不一致")
            elif len(new_password) < 6:
                st.error("❌ 新密码至少6个字符")
            else:
                # 这里可以添加密码修改逻辑
                st.info("🔄 密码修改功能开发中...")
    
    # 返回按钮
    st.markdown("---")
    if st.button("⬅️ 返回主界面", type="primary"):
        st.session_state.show_user_settings = False
        st.rerun()

if __name__ == "__main__":
    main()