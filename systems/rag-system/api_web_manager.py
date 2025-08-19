"""
API管理Web界面
提供基于Streamlit的API配置和私有密钥管理界面
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from api_config import APIConfigManager, UserRole, APIType, APIEndpoint
from private_api_manager import PrivateAPIManager, APIProvider, APIKeyStatus, APIKeyInfo

def init_session_state():
    """初始化会话状态"""
    if 'api_manager' not in st.session_state:
        st.session_state.api_manager = APIConfigManager()
    if 'private_manager' not in st.session_state:
        st.session_state.private_manager = PrivateAPIManager()
    if 'current_user' not in st.session_state:
        st.session_state.current_user = "admin"  # 默认管理员用户

def show_api_overview():
    """显示API概览"""
    st.header("📊 API系统概览")
    
    api_manager = st.session_state.api_manager
    private_manager = st.session_state.private_manager
    
    # 获取统计数据
    summary = api_manager.get_api_summary()
    
    # 显示关键指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总API端点", summary['total_endpoints'])
    
    with col2:
        st.metric("活跃端点", summary['active_endpoints'])
    
    with col3:
        total_keys = len(private_manager.api_keys)
        st.metric("私有密钥总数", total_keys)
    
    with col4:
        active_keys = sum(1 for k in private_manager.api_keys.values() if k.status == APIKeyStatus.ACTIVE)
        st.metric("活跃密钥", active_keys)
    
    # API类型分布图
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("API类型分布")
        if summary['by_type']:
            fig = px.pie(
                values=list(summary['by_type'].values()),
                names=list(summary['by_type'].keys()),
                title="API端点类型分布"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("角色权限分布")
        if summary['by_role']:
            fig = px.bar(
                x=list(summary['by_role'].keys()),
                y=list(summary['by_role'].values()),
                title="各角色可访问API数量"
            )
            st.plotly_chart(fig, use_container_width=True)

def show_api_endpoints():
    """显示和管理API端点"""
    st.header("🔗 API端点管理")
    
    api_manager = st.session_state.api_manager
    
    # 显示现有端点
    st.subheader("现有API端点")
    
    endpoints = api_manager.get_all_endpoints()
    if endpoints:
        # 转换为DataFrame显示
        data = []
        for name, endpoint in endpoints.items():
            data.append({
                "名称": endpoint.name,
                "URL": endpoint.url,
                "类型": endpoint.api_type.value,
                "所需角色": ", ".join([role.value for role in endpoint.required_roles]),
                "速率限制": f"{endpoint.rate_limit}/小时",
                "状态": "✅ 活跃" if endpoint.is_active else "❌ 停用",
                "描述": endpoint.description
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        # 编辑端点
        st.subheader("编辑API端点")
        selected_endpoint = st.selectbox("选择要编辑的端点", list(endpoints.keys()))
        
        if selected_endpoint:
            endpoint = endpoints[selected_endpoint]
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_rate_limit = st.number_input("速率限制（每小时）", value=endpoint.rate_limit, min_value=1)
                new_description = st.text_area("描述", value=endpoint.description)
            
            with col2:
                new_status = st.checkbox("启用", value=endpoint.is_active)
                
                if st.button("更新端点", key=f"update_{selected_endpoint}"):
                    success = api_manager.update_endpoint(
                        selected_endpoint,
                        rate_limit=new_rate_limit,
                        description=new_description,
                        is_active=new_status
                    )
                    if success:
                        st.success("端点更新成功！")
                        st.rerun()
                    else:
                        st.error("端点更新失败！")
    
    # 添加新端点
    st.subheader("添加新API端点")
    
    with st.form("add_endpoint"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("端点名称")
            new_url = st.text_input("URL路径")
            new_type = st.selectbox("API类型", [t.value for t in APIType])
        
        with col2:
            new_roles = st.multiselect("所需角色", [r.value for r in UserRole])
            new_rate_limit = st.number_input("速率限制（每小时）", value=100, min_value=1)
            new_description = st.text_area("描述")
        
        if st.form_submit_button("添加端点"):
            if new_name and new_url:
                try:
                    endpoint = APIEndpoint(
                        name=new_name,
                        url=new_url,
                        api_type=APIType(new_type),
                        required_roles=[UserRole(role) for role in new_roles],
                        rate_limit=new_rate_limit,
                        description=new_description
                    )
                    
                    if api_manager.add_endpoint(endpoint):
                        st.success("API端点添加成功！")
                        st.rerun()
                    else:
                        st.error("API端点添加失败！")
                except Exception as e:
                    st.error(f"添加失败: {str(e)}")
            else:
                st.error("请填写端点名称和URL")

def show_private_keys():
    """显示和管理私有API密钥"""
    st.header("🔐 私有API密钥管理")
    
    private_manager = st.session_state.private_manager
    
    # 用户选择
    current_user = st.selectbox(
        "选择用户",
        ["admin", "user_123", "user_456", "test_user"],
        key="user_selector"
    )
    
    # 显示用户的API密钥
    st.subheader(f"用户 {current_user} 的API密钥")
    
    user_keys = private_manager.get_user_api_keys(current_user)
    
    if user_keys:
        # 转换为DataFrame显示
        data = []
        for key in user_keys:
            status_icon = {
                APIKeyStatus.ACTIVE: "✅",
                APIKeyStatus.INACTIVE: "⏸️",
                APIKeyStatus.EXPIRED: "⏰",
                APIKeyStatus.SUSPENDED: "🚫"
            }.get(key.status, "❓")
            
            data.append({
                "密钥名称": key.key_name,
                "提供商": key.provider.value,
                "状态": f"{status_icon} {key.status.value}",
                "使用次数": key.usage_count,
                "日限制": key.daily_limit,
                "月限制": key.monthly_limit,
                "创建时间": datetime.fromtimestamp(key.created_at).strftime("%Y-%m-%d %H:%M"),
                "最后使用": datetime.fromtimestamp(key.last_used).strftime("%Y-%m-%d %H:%M") if key.last_used else "未使用",
                "描述": key.description,
                "密钥ID": key.key_id
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        # 密钥操作
        st.subheader("密钥操作")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_key = st.selectbox("选择密钥", [k.key_id for k in user_keys])
            
        with col2:
            new_status = st.selectbox("新状态", [s.value for s in APIKeyStatus])
            
        with col3:
            if st.button("更新状态"):
                if private_manager.update_api_key_status(current_user, selected_key, APIKeyStatus(new_status)):
                    st.success("状态更新成功！")
                    st.rerun()
                else:
                    st.error("状态更新失败！")
        
        # 删除密钥
        if st.button("🗑️ 删除选中的密钥", type="secondary"):
            if private_manager.remove_api_key(current_user, selected_key):
                st.success("密钥删除成功！")
                st.rerun()
            else:
                st.error("密钥删除失败！")
    
    # 添加新密钥
    st.subheader("添加新API密钥")
    
    with st.form("add_api_key"):
        col1, col2 = st.columns(2)
        
        with col1:
            key_name = st.text_input("密钥名称")
            provider = st.selectbox("API提供商", [p.value for p in APIProvider])
            api_key = st.text_input("API密钥", type="password")
        
        with col2:
            daily_limit = st.number_input("日使用限制", value=100, min_value=1)
            monthly_limit = st.number_input("月使用限制", value=3000, min_value=1)
            description = st.text_area("描述")
        
        if st.form_submit_button("添加密钥"):
            if key_name and api_key:
                key_id = private_manager.add_api_key(
                    user_id=current_user,
                    provider=APIProvider(provider),
                    key_name=key_name,
                    api_key=api_key,
                    daily_limit=daily_limit,
                    monthly_limit=monthly_limit,
                    description=description
                )
                
                if key_id:
                    st.success(f"API密钥添加成功！密钥ID: {key_id}")
                    st.rerun()
                else:
                    st.error("API密钥添加失败！可能是名称重复。")
            else:
                st.error("请填写密钥名称和API密钥")

def show_usage_statistics():
    """显示使用统计"""
    st.header("📈 使用统计")
    
    private_manager = st.session_state.private_manager
    
    # 用户选择
    current_user = st.selectbox(
        "选择用户",
        ["admin", "user_123", "user_456", "test_user"],
        key="stats_user_selector"
    )
    
    # 获取用户统计
    stats = private_manager.get_usage_statistics(current_user)
    
    if stats:
        st.subheader(f"用户 {current_user} 的使用统计")
        
        # 总体统计
        total_usage = sum(stat['total_usage'] for stat in stats.values())
        total_keys = len(stats)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("总使用次数", total_usage)
        
        with col2:
            st.metric("密钥数量", total_keys)
        
        with col3:
            avg_usage = total_usage / total_keys if total_keys > 0 else 0
            st.metric("平均使用次数", f"{avg_usage:.1f}")
        
        # 按密钥显示使用情况
        for key_id, stat in stats.items():
            with st.expander(f"📊 {stat['key_name']} ({stat['provider']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**总使用次数**: {stat['total_usage']}")
                    if stat['last_used']:
                        last_used = datetime.fromtimestamp(stat['last_used'])
                        st.write(f"**最后使用**: {last_used.strftime('%Y-%m-%d %H:%M')}")
                    else:
                        st.write("**最后使用**: 未使用")
                
                with col2:
                    # 显示每日使用情况
                    if stat['daily_usage']:
                        daily_data = stat['daily_usage']
                        dates = list(daily_data.keys())
                        usage = list(daily_data.values())
                        
                        fig = px.line(
                            x=dates,
                            y=usage,
                            title=f"{stat['key_name']} 每日使用趋势",
                            labels={'x': '日期', 'y': '使用次数'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"用户 {current_user} 暂无API密钥使用记录")
    
    # 系统整体统计
    st.subheader("系统整体统计")
    
    all_keys = private_manager.api_keys
    if all_keys:
        # 按提供商统计
        provider_stats = {}
        status_stats = {}
        
        for key_info in all_keys.values():
            provider = key_info.provider.value
            status = key_info.status.value
            
            provider_stats[provider] = provider_stats.get(provider, 0) + 1
            status_stats[status] = status_stats.get(status, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("按提供商分布")
            fig = px.pie(
                values=list(provider_stats.values()),
                names=list(provider_stats.keys()),
                title="API密钥提供商分布"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("按状态分布")
            fig = px.pie(
                values=list(status_stats.values()),
                names=list(status_stats.keys()),
                title="API密钥状态分布"
            )
            st.plotly_chart(fig, use_container_width=True)

def show_permission_test():
    """显示权限测试工具"""
    st.header("🔒 权限测试工具")
    
    api_manager = st.session_state.api_manager
    
    st.subheader("API访问权限测试")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        test_role = st.selectbox("用户角色", [r.value for r in UserRole])
    
    with col2:
        endpoints = list(api_manager.get_all_endpoints().keys())
        test_endpoint = st.selectbox("API端点", endpoints)
    
    with col3:
        if st.button("测试权限"):
            from api_config import check_api_access
            has_permission = check_api_access(test_endpoint, test_role)
            
            if has_permission:
                st.success(f"✅ {test_role} 角色可以访问 {test_endpoint}")
            else:
                st.error(f"❌ {test_role} 角色无法访问 {test_endpoint}")
    
    # 显示各角色可访问的API
    st.subheader("各角色API访问权限")
    
    for role in UserRole:
        with st.expander(f"👤 {role.value.upper()} 角色"):
            accessible_endpoints = api_manager.get_endpoints_by_role(role)
            
            if accessible_endpoints:
                for endpoint in accessible_endpoints:
                    st.write(f"- **{endpoint.name}**: {endpoint.description}")
            else:
                st.write("无可访问的API")

def main():
    """主函数"""
    st.set_page_config(
        page_title="API管理系统",
        page_icon="🔧",
        layout="wide"
    )
    
    st.title("🔧 API管理系统")
    st.markdown("---")
    
    # 初始化会话状态
    init_session_state()
    
    # 侧边栏导航
    st.sidebar.title("📋 导航菜单")
    
    pages = {
        "📊 系统概览": show_api_overview,
        "🔗 API端点管理": show_api_endpoints,
        "🔐 私有密钥管理": show_private_keys,
        "📈 使用统计": show_usage_statistics,
        "🔒 权限测试": show_permission_test
    }
    
    selected_page = st.sidebar.radio("选择页面", list(pages.keys()))
    
    # 显示选中的页面
    pages[selected_page]()
    
    # 侧边栏信息
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ 系统信息")
    st.sidebar.info(
        "**API管理系统 v1.0**\n\n"
        "- 公共API配置管理\n"
        "- 私有API密钥管理\n"
        "- 权限控制和统计\n"
        "- 安全加密存储"
    )

if __name__ == "__main__":
    main()