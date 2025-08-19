"""
RAG系统API集成示例
展示如何在RAG智能问答系统中集成API管理功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api_config import get_user_apis, UserRole

class RAGAPIIntegration:
    """RAG系统API集成类"""
    
    def __init__(self):
        self.system_name = "RAG智能问答系统"
        self.api_endpoints = {
            "chat": "user_chat",
            "advanced_chat": "advanced_chat", 
            "document_upload": "document_upload",
            "batch_process": "batch_processing"
        }
    
    def chat_with_permission(self, user_id: str, user_role: str, message: str, model_provider: str = "openai"):
        """
        带权限检查的聊天功能
        
        Args:
            user_id: 用户ID
            user_role: 用户角色 (guest/user/vip/admin)
            message: 用户消息
            model_provider: 模型提供商 (openai/claude/google)
        
        Returns:
            dict: 聊天结果
        """
        # 根据用户角色选择API端点
        if user_role in ["vip", "admin"]:
            api_endpoint = "advanced_chat"
        else:
            api_endpoint = "user_chat"
        
        # 简化版本：仅检查权限（完整版本需要私有密钥管理）
        from api_config import check_api_access
        
        if not check_api_access(api_endpoint, user_role):
            return {
                "success": False,
                "message": "用户没有权限访问此API"
            }
        
        validation = {"success": True, "api_key": "demo_key", "key_id": "demo_id"}
        
        if not validation["success"]:
            return {
                "success": False,
                "message": validation["message"],
                "usage_info": validation.get("usage_info")
            }
        
        try:
            # 使用验证通过的API密钥调用模型
            api_key = validation["api_key"]
            key_id = validation["key_id"]
            
            # 这里调用实际的AI模型API
            response = self._call_ai_model(api_key, message, model_provider)
            
            # 记录API使用（简化版本）
            print(f"记录用户 {user_id} 使用API")
            
            return {
                "success": True,
                "response": response,
                "usage_info": validation["usage_info"],
                "model_provider": model_provider
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"调用AI模型失败: {str(e)}"
            }
    
    def _call_ai_model(self, api_key: str, message: str, provider: str):
        """调用AI模型API（模拟实现）"""
        # 这里是模拟实现，实际应该调用对应的AI API
        responses = {
            "openai": f"[OpenAI GPT] 针对您的问题「{message}」，我的回答是...",
            "claude": f"[Claude] 关于「{message}」这个问题，我认为...",
            "google": f"[Google Gemini] 您询问的「{message}」，让我来分析一下..."
        }
        
        return responses.get(provider, f"[{provider}] 收到您的消息：{message}")
    
    def get_user_available_features(self, user_role: str):
        """获取用户可用的功能列表"""
        # 获取用户可访问的API
        user_apis = get_user_apis(user_role)
        
        # 映射到RAG系统功能
        available_features = []
        
        for api in user_apis:
            if api["name"] == "user_chat":
                available_features.append({
                    "name": "基础聊天",
                    "description": "与AI进行基础对话",
                    "rate_limit": api["rate_limit"]
                })
            elif api["name"] == "advanced_chat":
                available_features.append({
                    "name": "高级聊天",
                    "description": "使用高级AI模型进行对话",
                    "rate_limit": api["rate_limit"]
                })
        
        return available_features

def demo_rag_integration():
    """演示RAG系统集成"""
    print("🤖 RAG系统API集成演示")
    print("=" * 40)
    
    rag = RAGAPIIntegration()
    
    # 测试不同角色的用户
    test_users = [
        ("user_001", "guest"),
        ("user_002", "user"), 
        ("user_003", "vip"),
        ("user_004", "admin")
    ]
    
    for user_id, role in test_users:
        print(f"\n👤 用户: {user_id} (角色: {role})")
        
        # 获取可用功能
        features = rag.get_user_available_features(role)
        print(f"📋 可用功能 ({len(features)}个):")
        for feature in features:
            print(f"   - {feature['name']}: {feature['description']}")

if __name__ == "__main__":
    demo_rag_integration()