"""
Gemini API集成模块
提供完整的Gemini 2.5 Flash API调用功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import google.generativeai as genai
from api_config import check_api_access
from private_api_manager import get_user_api_key, PrivateAPIManager

class GeminiAPIIntegration:
    """Gemini API集成类"""
    
    def __init__(self):
        self.system_name = "Gemini AI 集成系统"
        self.model_name = "gemini-2.0-flash-exp"  # 使用最新的Gemini 2.0 Flash
        self.private_manager = PrivateAPIManager()
    
    def chat_with_gemini(self, user_id: str, user_role: str, message: str, **kwargs):
        """
        使用Gemini进行对话
        
        Args:
            user_id: 用户ID
            user_role: 用户角色
            message: 用户消息
            **kwargs: 其他参数（temperature, max_tokens等）
        
        Returns:
            dict: 对话结果
        """
        # 检查权限
        api_endpoint = "advanced_chat" if user_role in ["vip", "admin"] else "user_chat"
        
        if not check_api_access(api_endpoint, user_role):
            return {
                "success": False,
                "message": "您没有权限使用此功能",
                "error_code": "PERMISSION_DENIED"
            }
        
        # 获取API密钥
        key_result = get_user_api_key(user_id, "google")
        if not key_result:
            return {
                "success": False,
                "message": "未找到可用的Google API密钥，请先配置",
                "error_code": "NO_API_KEY"
            }
        
        key_id, api_key = key_result
        
        # 检查使用限制
        can_use, limit_info = self.private_manager.check_usage_limit(user_id, key_id)
        if not can_use:
            return {
                "success": False,
                "message": f"已达到使用限制: {limit_info.get('error', '未知错误')}",
                "error_code": "USAGE_LIMIT_EXCEEDED",
                "usage_info": limit_info
            }
        
        try:
            # 配置Gemini API
            genai.configure(api_key=api_key)
            
            # 创建模型
            model = genai.GenerativeModel(self.model_name)
            
            # 设置生成配置
            generation_config = {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.8),
                "top_k": kwargs.get("top_k", 40),
                "max_output_tokens": kwargs.get("max_tokens", 2048),
            }
            
            # 生成回复
            response = model.generate_content(
                message,
                generation_config=generation_config
            )
            
            # 记录使用
            self.private_manager.record_api_usage(user_id, key_id)
            
            return {
                "success": True,
                "response": response.text,
                "model": self.model_name,
                "usage_info": {
                    "daily_usage": limit_info.get("daily_usage", 0) + 1,
                    "daily_limit": limit_info.get("daily_limit", 0),
                    "monthly_usage": limit_info.get("monthly_usage", 0) + 1,
                    "monthly_limit": limit_info.get("monthly_limit", 0)
                },
                "generation_config": generation_config
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Gemini API调用失败: {str(e)}",
                "error_code": "API_CALL_FAILED"
            }
    
    def analyze_image_with_gemini(self, user_id: str, user_role: str, image_path: str, prompt: str = "请描述这张图片"):
        """
        使用Gemini分析图片
        
        Args:
            user_id: 用户ID
            user_role: 用户角色
            image_path: 图片路径
            prompt: 分析提示
        
        Returns:
            dict: 分析结果
        """
        # 检查权限（图片分析需要高级权限）
        if not check_api_access("advanced_chat", user_role):
            return {
                "success": False,
                "message": "图片分析功能需要VIP或管理员权限",
                "error_code": "PERMISSION_DENIED"
            }
        
        # 获取API密钥
        key_result = get_user_api_key(user_id, "google")
        if not key_result:
            return {
                "success": False,
                "message": "未找到可用的Google API密钥",
                "error_code": "NO_API_KEY"
            }
        
        key_id, api_key = key_result
        
        try:
            # 配置Gemini API
            genai.configure(api_key=api_key)
            
            # 创建视觉模型
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # 上传图片
            if os.path.exists(image_path):
                image_file = genai.upload_file(image_path)
                
                # 分析图片
                response = model.generate_content([prompt, image_file])
                
                # 记录使用
                self.private_manager.record_api_usage(user_id, key_id)
                
                return {
                    "success": True,
                    "response": response.text,
                    "image_path": image_path,
                    "prompt": prompt,
                    "model": "gemini-2.0-flash-exp"
                }
            else:
                return {
                    "success": False,
                    "message": f"图片文件不存在: {image_path}",
                    "error_code": "FILE_NOT_FOUND"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"图片分析失败: {str(e)}",
                "error_code": "IMAGE_ANALYSIS_FAILED"
            }
    
    def generate_code_with_gemini(self, user_id: str, user_role: str, description: str, language: str = "python"):
        """
        使用Gemini生成代码
        
        Args:
            user_id: 用户ID
            user_role: 用户角色
            description: 代码描述
            language: 编程语言
        
        Returns:
            dict: 生成结果
        """
        # 检查权限
        if not check_api_access("advanced_chat", user_role):
            return {
                "success": False,
                "message": "代码生成功能需要VIP或管理员权限",
                "error_code": "PERMISSION_DENIED"
            }
        
        # 获取API密钥
        key_result = get_user_api_key(user_id, "google")
        if not key_result:
            return {
                "success": False,
                "message": "未找到可用的Google API密钥",
                "error_code": "NO_API_KEY"
            }
        
        key_id, api_key = key_result
        
        try:
            # 配置Gemini API
            genai.configure(api_key=api_key)
            
            # 创建模型
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # 构建代码生成提示
            prompt = f"""
请用{language}编程语言生成代码来实现以下功能：

{description}

要求：
1. 代码要清晰易懂，有适当的注释
2. 遵循{language}的最佳实践
3. 包含错误处理
4. 如果需要，提供使用示例

请只返回代码，不要包含其他解释文字。
"""
            
            # 生成代码
            response = model.generate_content(prompt)
            
            # 记录使用
            self.private_manager.record_api_usage(user_id, key_id)
            
            return {
                "success": True,
                "code": response.text,
                "language": language,
                "description": description,
                "model": self.model_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"代码生成失败: {str(e)}",
                "error_code": "CODE_GENERATION_FAILED"
            }
    
    def get_user_gemini_stats(self, user_id: str):
        """获取用户的Gemini使用统计"""
        stats = self.private_manager.get_usage_statistics(user_id)
        
        gemini_stats = {}
        for key_id, stat in stats.items():
            if stat.get('provider') == 'google':
                gemini_stats[key_id] = stat
        
        return gemini_stats

def demo_gemini_integration():
    """演示Gemini集成功能"""
    print("🤖 Gemini API集成演示")
    print("=" * 50)
    
    gemini = GeminiAPIIntegration()
    
    # 测试用户
    test_users = [
        ("admin", "admin"),
        ("vip_user", "vip"),
        ("normal_user", "user"),
        ("guest_user", "guest")
    ]
    
    for user_id, role in test_users:
        print(f"\n👤 用户: {user_id} (角色: {role})")
        
        # 测试基础对话
        print("💬 测试基础对话...")
        chat_result = gemini.chat_with_gemini(
            user_id, role,
            "请用一句话介绍人工智能的发展前景",
            temperature=0.7
        )
        
        if chat_result["success"]:
            print(f"✅ 对话成功")
            print(f"🤖 Gemini回复: {chat_result['response'][:100]}...")
            if chat_result.get("usage_info"):
                usage = chat_result["usage_info"]
                print(f"📊 使用情况: {usage['daily_usage']}/{usage['daily_limit']} (今日)")
        else:
            print(f"❌ 对话失败: {chat_result['message']}")
        
        # 测试代码生成（仅VIP和管理员）
        if role in ["vip", "admin"]:
            print("💻 测试代码生成...")
            code_result = gemini.generate_code_with_gemini(
                user_id, role,
                "创建一个简单的计算器函数，支持加减乘除",
                "python"
            )
            
            if code_result["success"]:
                print(f"✅ 代码生成成功")
                print(f"💻 生成的代码预览: {code_result['code'][:150]}...")
            else:
                print(f"❌ 代码生成失败: {code_result['message']}")

if __name__ == "__main__":
    demo_gemini_integration()