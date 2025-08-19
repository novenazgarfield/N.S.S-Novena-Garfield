"""
用户管理系统
支持管理员和普通用户的分离管理
"""

import streamlit as st
import hashlib
import json
import os
import secrets
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class UserManager:
    """用户管理器"""
    
    def __init__(self):
        self.users_file = "/workspace/rag_system/config/users.json"
        self.sessions_file = "/workspace/rag_system/config/sessions.json"
        self.ensure_config_dir()
        self.init_default_users()
    
    def ensure_config_dir(self):
        """确保配置目录存在"""
        config_dir = os.path.dirname(self.users_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
    
    def init_default_users(self):
        """初始化默认用户"""
        if not os.path.exists(self.users_file):
            default_users = {
                "admin": {
                    "password_hash": self._hash_password("admin123"),
                    "role": "admin",
                    "display_name": "系统管理员",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "settings": {
                        "theme": "light",
                        "language": "zh-CN",
                        "notifications": True
                    }
                },
                "user": {
                    "password_hash": self._hash_password("user123"),
                    "role": "user",
                    "display_name": "普通用户",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "settings": {
                        "theme": "light",
                        "language": "zh-CN",
                        "notifications": True
                    }
                }
            }
            self._save_users(default_users)
    
    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_users(self) -> Dict:
        """加载用户数据"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_users(self, users: Dict):
        """保存用户数据"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def _load_sessions(self) -> Dict:
        """加载会话数据"""
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_sessions(self, sessions: Dict):
        """保存会话数据"""
        with open(self.sessions_file, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
    
    def create_session_token(self, username: str) -> str:
        """创建会话令牌"""
        token = secrets.token_urlsafe(32)
        sessions = self._load_sessions()
        
        # 清理过期的会话
        self._cleanup_expired_sessions()
        
        # 创建新会话
        sessions[token] = {
            "username": username,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),  # 7天有效期
            "last_activity": datetime.now().isoformat()
        }
        
        self._save_sessions(sessions)
        return token
    
    def validate_session_token(self, token: str) -> Optional[str]:
        """验证会话令牌"""
        if not token:
            return None
            
        sessions = self._load_sessions()
        if token not in sessions:
            return None
            
        session = sessions[token]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        # 检查是否过期
        if datetime.now() > expires_at:
            del sessions[token]
            self._save_sessions(sessions)
            return None
        
        # 更新最后活动时间
        session["last_activity"] = datetime.now().isoformat()
        sessions[token] = session
        self._save_sessions(sessions)
        
        return session["username"]
    
    def revoke_session_token(self, token: str):
        """撤销会话令牌"""
        sessions = self._load_sessions()
        if token in sessions:
            del sessions[token]
            self._save_sessions(sessions)
    
    def _cleanup_expired_sessions(self):
        """清理过期的会话"""
        sessions = self._load_sessions()
        current_time = datetime.now()
        expired_tokens = []
        
        for token, session in sessions.items():
            expires_at = datetime.fromisoformat(session["expires_at"])
            if current_time > expires_at:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del sessions[token]
        
        if expired_tokens:
            self._save_sessions(sessions)
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """用户认证"""
        users = self._load_users()
        if username in users:
            user = users[username]
            if user["password_hash"] == self._hash_password(password):
                # 更新最后登录时间
                user["last_login"] = datetime.now().isoformat()
                users[username] = user
                self._save_users(users)
                return {
                    "username": username,
                    "role": user["role"],
                    "display_name": user["display_name"],
                    "settings": user["settings"]
                }
        return None
    
    def create_user(self, username: str, password: str, role: str = "user", display_name: str = None) -> bool:
        """创建用户"""
        users = self._load_users()
        if username in users:
            return False
        
        users[username] = {
            "password_hash": self._hash_password(password),
            "role": role,
            "display_name": display_name or username,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "settings": {
                "theme": "light",
                "language": "zh-CN",
                "notifications": True
            }
        }
        self._save_users(users)
        return True
    
    def update_user_settings(self, username: str, settings: Dict):
        """更新用户设置"""
        users = self._load_users()
        if username in users:
            users[username]["settings"].update(settings)
            self._save_users(users)
    
    def get_user_settings(self, username: str) -> Dict:
        """获取用户设置"""
        users = self._load_users()
        if username in users:
            return users[username]["settings"]
        return {}
    
    def is_admin(self, username: str) -> bool:
        """检查是否为管理员"""
        users = self._load_users()
        return users.get(username, {}).get("role") == "admin"
    
    def get_all_users(self) -> Dict:
        """获取所有用户（仅管理员）"""
        return self._load_users()
    
    def update_display_name(self, username: str, display_name: str) -> bool:
        """更新用户显示名称"""
        users = self._load_users()
        if username in users:
            users[username]["display_name"] = display_name
            self._save_users(users)
            return True
        return False
    
    def change_password(self, username: str, current_password: str, new_password: str) -> bool:
        """修改用户密码"""
        users = self._load_users()
        if username in users:
            # 验证当前密码
            if self._verify_password(current_password, users[username]["password_hash"]):
                # 更新密码
                users[username]["password_hash"] = self._hash_password(new_password)
                self._save_users(users)
                return True
        return False

class AuthInterface:
    """认证界面"""
    
    def __init__(self):
        self.user_manager = UserManager()
    
    def check_persistent_login(self) -> bool:
        """检查持久化登录"""
        # 尝试从URL参数获取令牌
        try:
            query_params = st.query_params
            token = query_params.get('token', None)
        except:
            token = None
        
        # 如果URL中没有令牌，尝试从session_state获取
        if not token:
            token = st.session_state.get('session_token')
        
        if token:
            username = self.user_manager.validate_session_token(token)
            if username:
                # 获取用户信息
                users = self.user_manager._load_users()
                if username in users:
                    user = users[username]
                    user_info = {
                        "username": username,
                        "role": user["role"],
                        "display_name": user["display_name"],
                        "settings": user["settings"]
                    }
                    st.session_state.user_info = user_info
                    st.session_state.logged_in = True
                    st.session_state.session_token = token
                    
                    # 如果令牌来自URL，清除URL参数并重新加载
                    if query_params.get('token'):
                        st.query_params.clear()
                        st.rerun()
                    
                    return True
        
        return False
    
    def render_login_page(self) -> Optional[Dict]:
        """渲染登录页面"""
        
        # 添加登录页面专用CSS
        st.markdown("""
        <style>
        .main .block-container {
            max-width: 500px;
            margin: 0 auto;
            padding-top: 3rem;
        }
        .stForm {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }
        /* 统一输入框样式 */
        .stTextInput > div > div {
            position: relative !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }
        .stTextInput > div > div > input {
            border-radius: 8px !important;
            border: 1px solid #ddd !important;
            padding: 12px 16px !important;
            font-size: 1rem !important;
            outline: none !important;
            box-shadow: none !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #ff6b6b !important;
            box-shadow: 0 0 0 1px #ff6b6b !important;
            outline: none !important;
        }
        /* 移除Streamlit默认的焦点样式 */
        .stTextInput > div > div > input:focus-visible {
            outline: none !important;
        }
        /* 密码输入框特殊处理 */
        .stTextInput > div > div > input[type="password"] {
            padding-right: 45px !important;
        }
        /* 密码显示/隐藏按钮样式 */
        .stTextInput button {
            position: absolute !important;
            right: 8px !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            border: none !important;
            background: transparent !important;
            color: #666 !important;
            font-size: 0.9rem !important;
            padding: 4px 6px !important;
            border-radius: 4px !important;
            cursor: pointer !important;
            z-index: 10 !important;
            height: auto !important;
            min-height: auto !important;
            width: auto !important;
        }
        .stTextInput button:hover {
            background-color: rgba(0,0,0,0.05) !important;
            color: #333 !important;
        }
        /* 确保输入框容器正确对齐 */
        .stTextInput > div {
            width: 100% !important;
        }
        .stButton > button {
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 1rem;
        }
        .stCheckbox {
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('# 🔐 RAG智能对话系统')
        
        # 登录表单
        with st.form("login_form"):
            st.markdown("### 用户登录")
            
            username = st.text_input("👤 用户名", placeholder="请输入用户名")
            password = st.text_input("🔒 密码", type="password", placeholder="请输入密码")
            
            # 自动登录选项
            enable_auto_login = st.checkbox("🔒 下次自动登录（7天有效）", value=False, help="勾选后，7天内无需重复登录")
            
            col1, col2 = st.columns(2)
            with col1:
                login_btn = st.form_submit_button("🚀 登录", use_container_width=True, type="primary")
            with col2:
                register_btn = st.form_submit_button("📝 注册", use_container_width=True)
            
            if login_btn and username and password:
                user_info = self.user_manager.authenticate(username, password)
                if user_info:
                    st.session_state.user_info = user_info
                    st.session_state.logged_in = True
                    
                    # 检查是否启用自动登录
                    if enable_auto_login:
                        # 创建会话令牌
                        token = self.user_manager.create_session_token(username)
                        st.session_state.session_token = token
                        st.success(f"✅ 欢迎回来，{user_info['display_name']}！已启用自动登录（7天有效）")
                    else:
                        st.success(f"✅ 欢迎回来，{user_info['display_name']}！")
                    
                    st.rerun()
                else:
                    st.error("❌ 用户名或密码错误")
            
            if register_btn:
                st.session_state.show_register = True
                st.rerun()
        
        return None
    
    def render_register_page(self):
        """渲染注册页面"""
        st.markdown("## 📝 用户注册")
        
        with st.form("register_form"):
            username = st.text_input("👤 用户名", placeholder="请输入用户名（3-20字符）")
            display_name = st.text_input("📛 显示名称", placeholder="请输入显示名称")
            password = st.text_input("🔒 密码", type="password", placeholder="请输入密码（6位以上）")
            confirm_password = st.text_input("🔒 确认密码", type="password", placeholder="请再次输入密码")
            
            col1, col2 = st.columns(2)
            with col1:
                register_btn = st.form_submit_button("✅ 注册", use_container_width=True, type="primary")
            with col2:
                back_btn = st.form_submit_button("⬅️ 返回登录", use_container_width=True)
            
            if register_btn:
                if not username or len(username) < 3:
                    st.error("❌ 用户名至少3个字符")
                elif not password or len(password) < 6:
                    st.error("❌ 密码至少6个字符")
                elif password != confirm_password:
                    st.error("❌ 两次密码输入不一致")
                else:
                    if self.user_manager.create_user(username, password, "user", display_name or username):
                        st.success("✅ 注册成功！请返回登录")
                        st.balloons()
                    else:
                        st.error("❌ 用户名已存在")
            
            if back_btn:
                st.session_state.show_register = False
                st.rerun()
    
    def check_authentication(self) -> bool:
        """检查用户认证状态"""
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
        
        if "show_register" not in st.session_state:
            st.session_state.show_register = False
        
        # 如果未登录，先检查持久化登录
        if not st.session_state.logged_in:
            if self.check_persistent_login():
                return True

        if not st.session_state.logged_in:
            if st.session_state.show_register:
                self.render_register_page()
            else:
                self.render_login_page()
            return False
        
        return True
    
    def render_user_info(self):
        """渲染用户信息"""
        if "user_info" in st.session_state:
            user_info = st.session_state.user_info
            
            with st.sidebar:
                st.markdown("---")
                st.markdown("### 👤 用户信息")
                

                
                # 快捷操作
                st.markdown("### ⚡ 快捷操作")
                
                if st.button("⚙️ 个人设置", use_container_width=True):
                    st.session_state.show_user_settings = True
                    st.rerun()
                
                if user_info["role"] == "admin":
                    if st.button("🛠️ 系统管理", use_container_width=True):
                        st.session_state.show_admin_panel = True
                        st.rerun()
                
                if st.button("🚪 退出登录", use_container_width=True, type="secondary"):
                    # 撤销会话令牌
                    token = st.session_state.get('session_token')
                    if token:
                        self.user_manager.revoke_session_token(token)
                    
                    # 清除会话状态
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()

# 创建全局实例
user_manager = UserManager()
auth_interface = AuthInterface()