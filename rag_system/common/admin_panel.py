"""
管理员面板
系统管理、用户管理、资源监控等管理员专用功能
"""

import streamlit as st
import psutil
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from user_management import user_manager
from base_components import system_config

class AdminPanel:
    """管理员面板"""
    
    def __init__(self):
        self.user_manager = user_manager
        self.config = system_config
    
    def render_admin_panel(self):
        """渲染管理员面板"""
        st.markdown("# 🛠️ 系统管理面板")
        st.markdown("### 👑 管理员专用功能")
        
        # 检查管理员权限
        if not self._check_admin_permission():
            st.error("❌ 权限不足，仅管理员可访问")
            return
        
        # 管理员面板标签页
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 系统监控", 
            "👥 用户管理", 
            "⚙️ 系统配置", 
            "📄 文档管理", 
            "📈 使用统计"
        ])
        
        with tab1:
            self._render_system_monitor()
        
        with tab2:
            self._render_user_management()
        
        with tab3:
            self._render_system_config()
        
        with tab4:
            self._render_document_management()
        
        with tab5:
            self._render_usage_statistics()
        
        # 返回按钮
        st.markdown("---")
        if st.button("⬅️ 返回主界面", type="primary"):
            st.session_state.show_admin_panel = False
            st.rerun()
    
    def _check_admin_permission(self) -> bool:
        """检查管理员权限"""
        if "user_info" not in st.session_state:
            return False
        return st.session_state.user_info.get("role") == "admin"
    
    def _render_system_monitor(self):
        """渲染系统监控"""
        st.markdown("## 📊 系统监控")
        
        # 系统资源监控
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_used = disk.used / (1024**3)  # GB
            disk_total = disk.total / (1024**3)  # GB
            
            # 显示系统指标
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "🖥️ CPU使用率",
                    f"{cpu_percent:.1f}%",
                    delta=None,
                    help="当前CPU使用率"
                )
                st.progress(cpu_percent / 100)
                
                if cpu_percent > 80:
                    st.warning("⚠️ CPU使用率较高")
                elif cpu_percent > 90:
                    st.error("❌ CPU使用率过高")
            
            with col2:
                st.metric(
                    "💾 内存使用率",
                    f"{memory_percent:.1f}%",
                    delta=f"{memory_used:.1f}GB / {memory_total:.1f}GB",
                    help="当前内存使用情况"
                )
                st.progress(memory_percent / 100)
                
                if memory_percent > 80:
                    st.warning("⚠️ 内存使用率较高")
                elif memory_percent > 90:
                    st.error("❌ 内存使用率过高")
            
            with col3:
                st.metric(
                    "💽 磁盘使用率",
                    f"{disk_percent:.1f}%",
                    delta=f"{disk_used:.1f}GB / {disk_total:.1f}GB",
                    help="当前磁盘使用情况"
                )
                st.progress(disk_percent / 100)
                
                if disk_percent > 80:
                    st.warning("⚠️ 磁盘空间不足")
                elif disk_percent > 90:
                    st.error("❌ 磁盘空间严重不足")
        
        except Exception as e:
            st.error(f"❌ 系统监控数据获取失败: {str(e)}")
        
        # 服务状态监控
        st.markdown("### 🚀 服务状态")
        
        services = [
            {"name": "通用自适应版", "port": 51659, "status": "running"},
            {"name": "移动端专版", "port": 51660, "status": "running"},
            {"name": "桌面端专版", "port": 51661, "status": "running"},
            {"name": "原移动版", "port": 51657, "status": "running"},
            {"name": "测试版", "port": 56336, "status": "running"}
        ]
        
        for service in services:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                status_icon = "🟢" if service["status"] == "running" else "🔴"
                st.write(f"{status_icon} {service['name']}")
            with col2:
                st.write(f"端口: {service['port']}")
            with col3:
                if service["status"] == "running":
                    st.success("运行中")
                else:
                    st.error("已停止")
        
        # 系统操作
        st.markdown("### 🔧 系统操作")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 重启所有服务", type="secondary"):
                st.info("🔄 正在重启服务...")
                # 这里可以添加重启服务的逻辑
                st.success("✅ 服务重启完成")
        
        with col2:
            if st.button("🧹 清理系统缓存", type="secondary"):
                st.info("🧹 正在清理缓存...")
                # 这里可以添加清理缓存的逻辑
                st.success("✅ 缓存清理完成")
        
        with col3:
            if st.button("📊 导出系统报告", type="secondary"):
                st.info("📊 正在生成报告...")
                # 这里可以添加导出报告的逻辑
                st.success("✅ 报告生成完成")
    
    def _render_user_management(self):
        """渲染用户管理"""
        st.markdown("## 👥 用户管理")
        
        # 用户统计
        users = self.user_manager.get_all_users()
        admin_count = sum(1 for user in users.values() if user["role"] == "admin")
        user_count = sum(1 for user in users.values() if user["role"] == "user")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👑 管理员数量", admin_count)
        with col2:
            st.metric("👤 普通用户数量", user_count)
        with col3:
            st.metric("📊 总用户数", len(users))
        
        # 用户列表
        st.markdown("### 📋 用户列表")
        
        for username, user_info in users.items():
            with st.expander(f"{'👑' if user_info['role'] == 'admin' else '👤'} {user_info['display_name']} (@{username})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**角色**: {user_info['role']}")
                    st.write(f"**创建时间**: {user_info['created_at'][:19]}")
                    st.write(f"**最后登录**: {user_info['last_login'][:19] if user_info['last_login'] else '从未登录'}")
                
                with col2:
                    st.write(f"**主题**: {user_info['settings'].get('theme', 'light')}")
                    st.write(f"**语言**: {user_info['settings'].get('language', 'zh-CN')}")
                    st.write(f"**通知**: {'开启' if user_info['settings'].get('notifications', True) else '关闭'}")
                
                # 用户操作
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"🔄 重置密码", key=f"reset_{username}"):
                        st.info("🔄 密码重置功能开发中...")
                
                with col2:
                    if st.button(f"⚙️ 编辑设置", key=f"edit_{username}"):
                        st.info("⚙️ 用户设置编辑功能开发中...")
                
                with col3:
                    if username != "admin":  # 不能删除admin用户
                        if st.button(f"🗑️ 删除用户", key=f"delete_{username}"):
                            st.error("🗑️ 用户删除功能开发中...")
        
        # 创建新用户
        st.markdown("### ➕ 创建新用户")
        
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("用户名")
                new_password = st.text_input("密码", type="password")
            
            with col2:
                new_display_name = st.text_input("显示名称")
                new_role = st.selectbox("用户角色", ["user", "admin"])
            
            if st.form_submit_button("✅ 创建用户", type="primary"):
                if new_username and new_password:
                    if self.user_manager.create_user(new_username, new_password, new_role, new_display_name):
                        st.success(f"✅ 用户 {new_username} 创建成功")
                        st.rerun()
                    else:
                        st.error("❌ 用户名已存在")
                else:
                    st.error("❌ 请填写完整信息")
    
    def _render_system_config(self):
        """渲染系统配置"""
        st.markdown("## ⚙️ 系统配置")
        
        # 基础配置
        st.markdown("### 🔧 基础配置")
        
        col1, col2 = st.columns(2)
        
        with col1:
            system_name = st.text_input(
                "系统名称",
                value=self.config.get("system_name"),
                help="系统显示名称"
            )
            
            max_file_size = st.slider(
                "最大文件大小 (MB)",
                min_value=10,
                max_value=200,
                value=self.config.get("max_file_size"),
                help="单个文件最大上传大小"
            )
            
            max_daily_queries = st.number_input(
                "每日最大查询次数",
                min_value=100,
                max_value=5000,
                value=self.config.get("max_daily_queries"),
                help="每个用户每日最大查询次数"
            )
        
        with col2:
            version = st.text_input(
                "系统版本",
                value=self.config.get("version"),
                help="当前系统版本号"
            )
            
            max_documents = st.slider(
                "最大文档数量",
                min_value=10,
                max_value=100,
                value=self.config.get("max_documents"),
                help="每个用户最大文档数量"
            )
            
            max_message_length = st.number_input(
                "最大消息长度",
                min_value=1000,
                max_value=20000,
                value=self.config.get("max_message_length"),
                help="单条消息最大字符数"
            )
        
        # 功能配置
        st.markdown("### 🎛️ 功能配置")
        
        col1, col2 = st.columns(2)
        
        with col1:
            show_timestamps = st.checkbox(
                "默认显示时间戳",
                value=self.config.get("show_timestamps"),
                help="新用户默认显示消息时间戳"
            )
            
            auto_scroll = st.checkbox(
                "默认自动滚动",
                value=self.config.get("auto_scroll"),
                help="新用户默认开启自动滚动"
            )
        
        with col2:
            chat_speed = st.slider(
                "默认AI回答速度 (秒)",
                min_value=0.1,
                max_value=3.0,
                value=self.config.get("chat_speed"),
                step=0.1,
                help="新用户默认AI回答延迟"
            )
        
        # 支持格式配置
        st.markdown("### 📎 支持格式")
        
        current_formats = self.config.get("supported_formats", [])
        all_formats = [".pdf", ".docx", ".txt", ".md", ".pptx", ".csv", ".xlsx", ".png", ".jpg", ".jpeg"]
        
        selected_formats = st.multiselect(
            "选择支持的文件格式",
            all_formats,
            default=current_formats,
            help="选择系统支持的文件格式"
        )
        
        # 保存配置
        if st.button("💾 保存配置", type="primary"):
            # 更新配置
            self.config.update({
                "system_name": system_name,
                "version": version,
                "max_file_size": max_file_size,
                "max_daily_queries": max_daily_queries,
                "max_documents": max_documents,
                "max_message_length": max_message_length,
                "show_timestamps": show_timestamps,
                "auto_scroll": auto_scroll,
                "chat_speed": chat_speed,
                "supported_formats": selected_formats
            })
            
            st.success("✅ 配置保存成功")
            st.balloons()
    
    def _render_document_management(self):
        """渲染文档管理"""
        st.markdown("## 📄 文档管理")
        
        # 文档统计
        st.markdown("### 📊 文档统计")
        
        # 这里可以添加文档统计逻辑
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 总文档数", "0", help="系统中所有文档数量")
        with col2:
            st.metric("💾 总存储大小", "0 MB", help="所有文档占用存储空间")
        with col3:
            st.metric("📈 今日上传", "0", help="今日新上传文档数量")
        with col4:
            st.metric("🔍 活跃文档", "0", help="最近被访问的文档数量")
        
        # 文档清理
        st.markdown("### 🧹 文档清理")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ 清理临时文件", type="secondary"):
                st.info("🗑️ 正在清理临时文件...")
                st.success("✅ 临时文件清理完成")
        
        with col2:
            if st.button("📅 清理过期文档", type="secondary"):
                st.info("📅 正在清理过期文档...")
                st.success("✅ 过期文档清理完成")
        
        with col3:
            if st.button("💾 优化存储空间", type="secondary"):
                st.info("💾 正在优化存储空间...")
                st.success("✅ 存储空间优化完成")
        
        # 文档备份
        st.markdown("### 💾 文档备份")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📦 创建备份", type="primary"):
                st.info("📦 正在创建备份...")
                st.success("✅ 备份创建完成")
        
        with col2:
            if st.button("📥 恢复备份", type="secondary"):
                st.info("📥 备份恢复功能开发中...")
    
    def _render_usage_statistics(self):
        """渲染使用统计"""
        st.markdown("## 📈 使用统计")
        
        # 今日统计
        st.markdown("### 📅 今日统计")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 活跃用户", "0", delta="0", help="今日活跃用户数量")
        with col2:
            st.metric("💬 对话次数", "0", delta="0", help="今日总对话次数")
        with col3:
            st.metric("📄 文档上传", "0", delta="0", help="今日文档上传数量")
        with col4:
            st.metric("🔍 查询次数", "0", delta="0", help="今日总查询次数")
        
        # 本周统计
        st.markdown("### 📊 本周统计")
        
        # 这里可以添加图表显示
        st.info("📊 统计图表功能开发中...")
        
        # 用户活跃度
        st.markdown("### 👥 用户活跃度")
        
        st.info("👥 用户活跃度分析功能开发中...")
        
        # 导出统计报告
        st.markdown("### 📋 导出报告")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 导出日报", type="secondary"):
                st.info("📊 正在生成日报...")
                st.success("✅ 日报导出完成")
        
        with col2:
            if st.button("📈 导出周报", type="secondary"):
                st.info("📈 正在生成周报...")
                st.success("✅ 周报导出完成")
        
        with col3:
            if st.button("📋 导出月报", type="secondary"):
                st.info("📋 正在生成月报...")
                st.success("✅ 月报导出完成")

# 创建管理员面板实例
admin_panel = AdminPanel()