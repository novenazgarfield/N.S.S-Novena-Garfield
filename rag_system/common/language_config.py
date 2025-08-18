"""
语言配置模块
支持中英文界面切换
"""

# 语言配置字典
LANGUAGE_CONFIG = {
    "zh-CN": {
        # 主界面
        "title": "🤖 RAG智能对话",
        "welcome": "欢迎",
        "settings": "设置",
        "admin_panel": "系统管理",
        "logout": "退出",
        "upload_doc": "上传文档",
        "clear_chat": "清空对话",
        
        # 对话相关
        "chat_history": "💬 对话记录",
        "no_messages": "暂无对话消息",
        "start_chat": "开始对话吧！",
        "smart_suggestions": "💡 智能建议",
        "type_message": "输入您的问题...",
        "send": "发送",
        
        # 文档上传
        "upload_document": "📤 上传文档",
        "select_file": "选择文档",
        "file_too_large": "文件过大",
        "upload_success": "上传成功",
        "upload_failed": "上传失败",
        "close": "关闭",
        "cancel": "取消",
        "upload_analyze": "上传分析",
        "view_docs": "查看文档",
        
        # 设置页面
        "personal_info": "👤 个人信息",
        "interface_settings": "🎨 界面设置",
        "function_settings": "⚡ 功能设置",
        "document_management": "📄 文档管理",
        "usage_statistics": "📊 使用统计",
        
        # 个人信息
        "username": "用户名",
        "role": "角色",
        "permissions": "权限",
        "display_name": "显示名称",
        "change_password": "🔒 修改密码",
        "current_password": "当前密码",
        "new_password": "新密码",
        "confirm_password": "确认新密码",
        "save_name": "💾 保存名称",
        "update_password": "🔄 修改密码",
        
        # 界面设置
        "theme": "界面主题",
        "font_size": "字体大小",
        "show_timestamps": "显示消息时间戳",
        "auto_scroll": "自动滚动到新消息",
        "language": "界面语言",
        "save_settings": "💾 保存界面设置",
        
        # 主题选项
        "light_mode": "🌞 浅色模式",
        "dark_mode": "🌙 深色模式",
        "auto_mode": "🔄 自动跟随系统",
        
        # 语言选项
        "chinese": "🇨🇳 简体中文",
        "english": "🇺🇸 English",
        
        # 消息提示
        "success": "✅ 操作成功",
        "error": "❌ 操作失败",
        "info": "💡 提示信息",
        "warning": "⚠️ 警告",
        
        # 文档管理
        "doc_count": "文档数量",
        "file_size_limit": "文件大小限制",
        "daily_queries": "今日查询",
        "uploaded_docs": "📋 已上传文档",
        "no_docs": "暂无上传文档",
        "delete_doc": "🗑️ 删除",
        "delete_all": "🗑️ 删除所有文档",
        "doc_stats": "📊 文档统计",
        
        # 使用统计
        "total_messages": "总消息数",
        "total_queries": "总查询数",
        "docs_uploaded": "已上传文档",
        "storage_used": "存储使用量",
    },
    
    "en-US": {
        # Main interface
        "title": "🤖 RAG AI Chat",
        "welcome": "Welcome",
        "settings": "Settings",
        "admin_panel": "Admin Panel",
        "logout": "Logout",
        "upload_doc": "Upload Doc",
        "clear_chat": "Clear Chat",
        
        # Chat related
        "chat_history": "💬 Chat History",
        "no_messages": "No messages yet",
        "start_chat": "Start chatting!",
        "smart_suggestions": "💡 Smart Suggestions",
        "type_message": "Type your question...",
        "send": "Send",
        
        # Document upload
        "upload_document": "📤 Upload Document",
        "select_file": "Select File",
        "file_too_large": "File too large",
        "upload_success": "Upload successful",
        "upload_failed": "Upload failed",
        "close": "Close",
        "cancel": "Cancel",
        "upload_analyze": "Upload & Analyze",
        "view_docs": "View Documents",
        
        # Settings page
        "personal_info": "👤 Personal Info",
        "interface_settings": "🎨 Interface Settings",
        "function_settings": "⚡ Function Settings",
        "document_management": "📄 Document Management",
        "usage_statistics": "📊 Usage Statistics",
        
        # Personal info
        "username": "Username",
        "role": "Role",
        "permissions": "Permissions",
        "display_name": "Display Name",
        "change_password": "🔒 Change Password",
        "current_password": "Current Password",
        "new_password": "New Password",
        "confirm_password": "Confirm Password",
        "save_name": "💾 Save Name",
        "update_password": "🔄 Update Password",
        
        # Interface settings
        "theme": "Theme",
        "font_size": "Font Size",
        "show_timestamps": "Show Message Timestamps",
        "auto_scroll": "Auto Scroll to New Messages",
        "language": "Interface Language",
        "save_settings": "💾 Save Settings",
        
        # Theme options
        "light_mode": "🌞 Light Mode",
        "dark_mode": "🌙 Dark Mode",
        "auto_mode": "🔄 Auto Follow System",
        
        # Language options
        "chinese": "🇨🇳 简体中文",
        "english": "🇺🇸 English",
        
        # Messages
        "success": "✅ Success",
        "error": "❌ Error",
        "info": "💡 Info",
        "warning": "⚠️ Warning",
        
        # Document management
        "doc_count": "Document Count",
        "file_size_limit": "File Size Limit",
        "daily_queries": "Daily Queries",
        "uploaded_docs": "📋 Uploaded Documents",
        "no_docs": "No documents uploaded",
        "delete_doc": "🗑️ Delete",
        "delete_all": "🗑️ Delete All Documents",
        "doc_stats": "📊 Document Statistics",
        
        # Usage statistics
        "total_messages": "Total Messages",
        "total_queries": "Total Queries",
        "docs_uploaded": "Documents Uploaded",
        "storage_used": "Storage Used",
    }
}

def get_text(key: str, language: str = "zh-CN") -> str:
    """获取指定语言的文本"""
    return LANGUAGE_CONFIG.get(language, LANGUAGE_CONFIG["zh-CN"]).get(key, key)

def get_language_options():
    """获取语言选项"""
    return {
        "zh-CN": "🇨🇳 简体中文",
        "en-US": "🇺🇸 English"
    }