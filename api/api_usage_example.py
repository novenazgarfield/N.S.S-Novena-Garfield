"""
API管理模块使用示例
展示如何在RAG系统中使用API配置管理和私有API管理
"""

from api_config import APIConfigManager, UserRole, APIType, check_api_access, get_user_apis
from private_api_manager import PrivateAPIManager, APIProvider, add_user_api_key, get_user_api_key
import time

def demo_api_config_management():
    """演示API配置管理"""
    print("=== API配置管理演示 ===")
    
    # 获取API配置管理器
    api_manager = APIConfigManager()
    
    # 查看API概览
    summary = api_manager.get_api_summary()
    print(f"系统中共有 {summary['total_endpoints']} 个API端点")
    print(f"活跃端点: {summary['active_endpoints']} 个")
    print(f"按类型分布: {summary['by_type']}")
    
    # 测试不同角色的API访问权限
    roles = ['guest', 'user', 'vip', 'admin']
    for role in roles:
        apis = get_user_apis(role)
        print(f"\n{role.upper()} 角色可访问的API ({len(apis)}个):")
        for api in apis[:3]:  # 只显示前3个
            print(f"  - {api['name']}: {api['description']}")
        if len(apis) > 3:
            print(f"  ... 还有 {len(apis) - 3} 个API")
    
    # 测试权限检查
    print(f"\n权限检查测试:")
    test_cases = [
        ('user', 'user_chat', True),
        ('user', 'user_management', False),
        ('admin', 'user_management', True),
        ('guest', 'health_check', True)
    ]
    
    for role, api_name, expected in test_cases:
        result = check_api_access(api_name, role)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {role} 访问 {api_name}: {result}")

def demo_private_api_management():
    """演示私有API管理"""
    print("\n=== 私有API管理演示 ===")
    
    # 获取私有API管理器
    private_manager = PrivateAPIManager()
    
    # 模拟用户添加API密钥
    test_user = "user_12345"
    
    # 添加OpenAI API密钥
    openai_key_id = add_user_api_key(
        user_id=test_user,
        provider="openai",
        key_name="主要OpenAI密钥",
        api_key="sk-proj-example123456789abcdef",
        daily_limit=50,
        monthly_limit=1500,
        description="用于日常聊天的OpenAI API密钥"
    )
    
    if openai_key_id:
        print(f"✅ 成功添加OpenAI API密钥: {openai_key_id}")
    
    # 添加Claude API密钥
    claude_key_id = add_user_api_key(
        user_id=test_user,
        provider="claude",
        key_name="Claude备用密钥",
        api_key="sk-ant-example123456789abcdef",
        daily_limit=30,
        monthly_limit=900,
        description="Claude API备用密钥"
    )
    
    if claude_key_id:
        print(f"✅ 成功添加Claude API密钥: {claude_key_id}")
    
    # 获取用户的API密钥列表
    user_keys = private_manager.get_user_api_keys(test_user)
    print(f"\n用户 {test_user} 的API密钥:")
    for key in user_keys:
        print(f"  - {key.key_name} ({key.provider.value})")
        print(f"    状态: {key.status.value}, 使用次数: {key.usage_count}")
        print(f"    限制: {key.daily_limit}/天, {key.monthly_limit}/月")
    
    # 模拟API使用
    print(f"\n模拟API使用:")
    
    # 获取可用的OpenAI密钥
    openai_result = get_user_api_key(test_user, "openai")
    if openai_result:
        key_id, api_key = openai_result
        print(f"✅ 获取到OpenAI密钥: {api_key[:20]}...")
        
        # 记录使用
        private_manager.record_api_usage(test_user, key_id)
        print(f"✅ 已记录一次使用")
        
        # 检查使用限制
        can_use, limit_info = private_manager.check_usage_limit(test_user, key_id)
        print(f"✅ 使用限制检查: {limit_info}")
    
    # 获取使用统计
    stats = private_manager.get_usage_statistics(test_user)
    print(f"\n使用统计:")
    for key_id, stat in stats.items():
        print(f"  - {stat['key_name']} ({stat['provider']}): {stat['total_usage']} 次使用")

def demo_integrated_usage():
    """演示集成使用场景"""
    print("\n=== 集成使用场景演示 ===")
    
    # 模拟用户请求聊天API
    user_id = "user_12345"
    user_role = "vip"
    api_endpoint = "advanced_chat"
    
    print(f"用户 {user_id} (角色: {user_role}) 请求访问 {api_endpoint}")
    
    # 1. 检查API访问权限
    has_permission = check_api_access(api_endpoint, user_role)
    if not has_permission:
        print("❌ 用户没有权限访问此API")
        return
    
    print("✅ 用户有权限访问此API")
    
    # 2. 获取用户的私有API密钥
    api_key_result = get_user_api_key(user_id, "openai")
    if not api_key_result:
        print("❌ 用户没有可用的OpenAI API密钥")
        return
    
    key_id, api_key = api_key_result
    print(f"✅ 获取到用户的API密钥: {api_key[:20]}...")
    
    # 3. 检查使用限制
    private_manager = PrivateAPIManager()
    can_use, limit_info = private_manager.check_usage_limit(user_id, key_id)
    if not can_use:
        print(f"❌ 已达到使用限制: {limit_info['error']}")
        return
    
    print(f"✅ 使用限制检查通过: 今日已用 {limit_info['daily_usage']}/{limit_info['daily_limit']}")
    
    # 4. 模拟API调用
    print("🚀 开始调用OpenAI API...")
    time.sleep(1)  # 模拟API调用延迟
    
    # 5. 记录使用
    private_manager.record_api_usage(user_id, key_id)
    print("✅ API调用成功，已记录使用次数")
    
    # 6. 返回结果
    print("✅ 聊天请求处理完成")

def demo_admin_operations():
    """演示管理员操作"""
    print("\n=== 管理员操作演示 ===")
    
    api_manager = APIConfigManager()
    private_manager = PrivateAPIManager()
    
    # 管理员查看系统API概览
    summary = api_manager.get_api_summary()
    print("系统API概览:")
    print(f"  总端点数: {summary['total_endpoints']}")
    print(f"  活跃端点: {summary['active_endpoints']}")
    print(f"  按类型分布: {summary['by_type']}")
    
    # 查看所有用户的API密钥统计（管理员权限）
    print(f"\n用户API密钥统计:")
    all_keys = private_manager.api_keys
    user_stats = {}
    
    for key_info in all_keys.values():
        user_id = key_info.user_id
        if user_id not in user_stats:
            user_stats[user_id] = {'count': 0, 'total_usage': 0, 'providers': set()}
        
        user_stats[user_id]['count'] += 1
        user_stats[user_id]['total_usage'] += key_info.usage_count
        user_stats[user_id]['providers'].add(key_info.provider.value)
    
    for user_id, stats in user_stats.items():
        providers = ', '.join(stats['providers'])
        print(f"  用户 {user_id}: {stats['count']} 个密钥, {stats['total_usage']} 次使用, 提供商: {providers}")

if __name__ == "__main__":
    # 运行所有演示
    demo_api_config_management()
    demo_private_api_management()
    demo_integrated_usage()
    demo_admin_operations()
    
    print("\n=== 演示完成 ===")
    print("这些模块可以帮助您:")
    print("1. 管理系统API端点和权限控制")
    print("2. 安全存储和管理用户的私有API密钥")
    print("3. 监控API使用情况和限制")
    print("4. 提供完整的权限验证流程")