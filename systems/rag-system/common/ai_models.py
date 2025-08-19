"""
AI模型集成模块
支持多种AI模型的统一接口，包括OpenAI、Claude、Gemini等
"""

import os
import sys
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import streamlit as st

# 添加API管理路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'api_management'))

try:
    from config.private_api_manager import PrivateAPIManager, APIProvider, get_user_api_key
    API_MANAGER_AVAILABLE = True
except ImportError:
    API_MANAGER_AVAILABLE = False

# 导入各种AI模型的SDK
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class ModelProvider(Enum):
    """AI模型提供商"""
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    LOCAL = "local"
    DEMO = "demo"

@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    provider: ModelProvider
    model_id: str
    max_tokens: int = 2048
    temperature: float = 0.7
    supports_streaming: bool = True
    supports_images: bool = False
    cost_per_1k_tokens: float = 0.0
    description: str = ""

class AIModelManager:
    """AI模型管理器"""
    
    def __init__(self):
        self.available_models = self._init_available_models()
        self.current_model = None
        self.api_manager = PrivateAPIManager() if API_MANAGER_AVAILABLE else None
    
    def _init_available_models(self) -> Dict[str, ModelConfig]:
        """初始化可用模型"""
        models = {}
        
        # OpenAI模型
        if OPENAI_AVAILABLE:
            models.update({
                "gpt-4": ModelConfig(
                    name="GPT-4",
                    provider=ModelProvider.OPENAI,
                    model_id="gpt-4",
                    max_tokens=4096,
                    temperature=0.7,
                    supports_streaming=True,
                    supports_images=True,
                    cost_per_1k_tokens=0.03,
                    description="OpenAI最强大的模型，适合复杂推理任务"
                ),
                "gpt-3.5-turbo": ModelConfig(
                    name="GPT-3.5 Turbo",
                    provider=ModelProvider.OPENAI,
                    model_id="gpt-3.5-turbo",
                    max_tokens=4096,
                    temperature=0.7,
                    supports_streaming=True,
                    supports_images=False,
                    cost_per_1k_tokens=0.002,
                    description="OpenAI高性价比模型，适合日常对话"
                )
            })
        
        # Claude模型
        if CLAUDE_AVAILABLE:
            models.update({
                "claude-3-opus": ModelConfig(
                    name="Claude-3 Opus",
                    provider=ModelProvider.CLAUDE,
                    model_id="claude-3-opus-20240229",
                    max_tokens=4096,
                    temperature=0.7,
                    supports_streaming=True,
                    supports_images=True,
                    cost_per_1k_tokens=0.015,
                    description="Anthropic最强大的模型，擅长分析和创作"
                ),
                "claude-3-sonnet": ModelConfig(
                    name="Claude-3 Sonnet",
                    provider=ModelProvider.CLAUDE,
                    model_id="claude-3-sonnet-20240229",
                    max_tokens=4096,
                    temperature=0.7,
                    supports_streaming=True,
                    supports_images=True,
                    cost_per_1k_tokens=0.003,
                    description="Anthropic平衡性能和成本的模型"
                )
            })
        
        # Gemini模型
        if GEMINI_AVAILABLE:
            models.update({
                "gemini-2.0-flash": ModelConfig(
                    name="Gemini 2.0 Flash",
                    provider=ModelProvider.GEMINI,
                    model_id="gemini-2.0-flash-exp",
                    max_tokens=8192,
                    temperature=0.7,
                    supports_streaming=True,
                    supports_images=True,
                    cost_per_1k_tokens=0.001,
                    description="Google最新的Gemini模型，速度快，性能强"
                ),
                "gemini-1.5-pro": ModelConfig(
                    name="Gemini 1.5 Pro",
                    provider=ModelProvider.GEMINI,
                    model_id="gemini-1.5-pro",
                    max_tokens=8192,
                    temperature=0.7,
                    supports_streaming=True,
                    supports_images=True,
                    cost_per_1k_tokens=0.002,
                    description="Google Gemini专业版，适合复杂任务"
                )
            })
        
        # 演示模型（总是可用）
        models["demo"] = ModelConfig(
            name="演示模型",
            provider=ModelProvider.DEMO,
            model_id="demo",
            max_tokens=2048,
            temperature=0.7,
            supports_streaming=False,
            supports_images=False,
            cost_per_1k_tokens=0.0,
            description="内置演示模型，无需API密钥"
        )
        
        return models
    
    def get_available_models(self, user_id: str = None) -> Dict[str, ModelConfig]:
        """获取用户可用的模型"""
        if not user_id or not self.api_manager:
            # 只返回演示模型
            return {"demo": self.available_models["demo"]}
        
        available = {"demo": self.available_models["demo"]}
        
        # 检查用户是否有对应的API密钥
        user_keys = self.api_manager.get_user_api_keys(user_id)
        
        for key_info in user_keys:
            if key_info.status.value == "active":
                provider = key_info.provider.value
                
                # 提供商名称映射
                provider_mapping = {
                    "google": "gemini",
                    "openai": "openai", 
                    "anthropic": "claude"
                }
                
                mapped_provider = provider_mapping.get(provider, provider)
                
                # 根据API提供商添加对应模型
                for model_key, model_config in self.available_models.items():
                    if model_config.provider.value == mapped_provider:
                        available[model_key] = model_config
        
        return available
    
    def select_model(self, model_key: str, user_id: str = None) -> bool:
        """选择模型"""
        if model_key not in self.available_models:
            return False
        
        model_config = self.available_models[model_key]
        
        # 检查用户是否有权限使用该模型
        if model_config.provider != ModelProvider.DEMO:
            if not user_id or not self.api_manager:
                return False
            
            # 提供商名称反向映射
            reverse_provider_mapping = {
                "gemini": "google",
                "openai": "openai",
                "claude": "anthropic"
            }
            
            api_provider = reverse_provider_mapping.get(model_config.provider.value, model_config.provider.value)
            
            # 检查是否有可用的API密钥
            api_result = get_user_api_key(user_id, api_provider)
            if not api_result:
                return False
        
        self.current_model = model_config
        return True
    
    def generate_response(self, prompt: str, context: str = "", user_id: str = None, **kwargs) -> str:
        """生成AI回复"""
        if not self.current_model:
            return "❌ 请先选择一个AI模型"
        
        try:
            if self.current_model.provider == ModelProvider.DEMO:
                return self._generate_demo_response(prompt, context)
            elif self.current_model.provider == ModelProvider.OPENAI:
                return self._generate_openai_response(prompt, context, user_id, **kwargs)
            elif self.current_model.provider == ModelProvider.CLAUDE:
                return self._generate_claude_response(prompt, context, user_id, **kwargs)
            elif self.current_model.provider == ModelProvider.GEMINI:
                return self._generate_gemini_response(prompt, context, user_id, **kwargs)
            else:
                return "❌ 不支持的模型类型"
        
        except Exception as e:
            return f"❌ 生成回复时出错: {str(e)}"
    
    def _generate_demo_response(self, prompt: str, context: str = "") -> str:
        """生成演示回复"""
        # 模拟思考时间
        time.sleep(1)
        
        # 基于关键词的简单回复
        if "你好" in prompt or "hello" in prompt.lower():
            return "👋 您好！我是RAG智能助手的演示模式。我可以帮您回答问题和分析文档。"
        
        if "文档" in prompt or "分析" in prompt:
            if context:
                return f"📄 基于您上传的文档，我发现以下要点：\n\n{context[:300]}...\n\n这是文档的主要内容。您想了解哪个具体方面？"
            else:
                return "📄 请先上传文档，我就可以为您分析文档内容了。"
        
        if "RAG" in prompt.upper():
            return """🔍 **RAG（检索增强生成）技术介绍：**

RAG是一种结合了信息检索和文本生成的AI技术：

1. **检索阶段**：从知识库中找到相关信息
2. **增强阶段**：将检索结果作为上下文
3. **生成阶段**：基于上下文生成准确回答

**优势：**
- 提高回答准确性
- 减少幻觉问题
- 支持实时信息更新
- 可解释性强"""
        
        # 默认回复
        return f"""💭 **您的问题：** {prompt}

🤖 **演示模式回复：**
感谢您的提问！这是演示模式的回复。在实际使用中，您可以：

1. 🔑 配置API密钥使用真实的AI模型
2. 📄 上传文档进行智能分析
3. 💬 进行更深入的对话交流

如需使用完整功能，请在设置中配置您的API密钥。"""
    
    def _generate_openai_response(self, prompt: str, context: str = "", user_id: str = None, **kwargs) -> str:
        """生成OpenAI回复"""
        if not OPENAI_AVAILABLE or not user_id or not self.api_manager:
            return "❌ OpenAI功能不可用"
        
        # 获取API密钥
        api_result = get_user_api_key(user_id, "openai")
        if not api_result:
            return "❌ 未找到可用的OpenAI API密钥"
        
        key_id, api_key = api_result
        
        try:
            # 配置OpenAI客户端
            client = openai.OpenAI(api_key=api_key)
            
            # 构建消息
            messages = []
            if context:
                messages.append({
                    "role": "system",
                    "content": f"基于以下文档内容回答用户问题：\n\n{context}"
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # 调用API
            response = client.chat.completions.create(
                model=self.current_model.model_id,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.current_model.max_tokens),
                temperature=kwargs.get('temperature', self.current_model.temperature)
            )
            
            # 记录使用
            self.api_manager.record_api_usage(user_id, key_id)
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"❌ OpenAI API调用失败: {str(e)}"
    
    def _generate_claude_response(self, prompt: str, context: str = "", user_id: str = None, **kwargs) -> str:
        """生成Claude回复"""
        if not CLAUDE_AVAILABLE or not user_id or not self.api_manager:
            return "❌ Claude功能不可用"
        
        # 获取API密钥
        api_result = get_user_api_key(user_id, "claude")
        if not api_result:
            return "❌ 未找到可用的Claude API密钥"
        
        key_id, api_key = api_result
        
        try:
            # 配置Claude客户端
            client = anthropic.Anthropic(api_key=api_key)
            
            # 构建消息内容
            content = prompt
            if context:
                content = f"基于以下文档内容回答问题：\n\n{context}\n\n问题：{prompt}"
            
            # 调用API
            response = client.messages.create(
                model=self.current_model.model_id,
                max_tokens=kwargs.get('max_tokens', self.current_model.max_tokens),
                temperature=kwargs.get('temperature', self.current_model.temperature),
                messages=[{
                    "role": "user",
                    "content": content
                }]
            )
            
            # 记录使用
            self.api_manager.record_api_usage(user_id, key_id)
            
            return response.content[0].text
        
        except Exception as e:
            return f"❌ Claude API调用失败: {str(e)}"
    
    def _generate_gemini_response(self, prompt: str, context: str = "", user_id: str = None, **kwargs) -> str:
        """生成Gemini回复"""
        if not GEMINI_AVAILABLE or not user_id or not self.api_manager:
            return "❌ Gemini功能不可用"
        
        # 获取API密钥
        api_result = get_user_api_key(user_id, "google")
        if not api_result:
            return "❌ 未找到可用的Gemini API密钥"
        
        key_id, api_key = api_result
        
        try:
            # 配置Gemini
            genai.configure(api_key=api_key)
            
            # 创建模型实例
            model = genai.GenerativeModel(self.current_model.model_id)
            
            # 构建提示
            full_prompt = prompt
            if context:
                full_prompt = f"""基于以下文档内容回答用户问题：

文档内容：
{context}

用户问题：{prompt}

请基于文档内容提供准确、详细的回答。如果文档中没有相关信息，请说明并提供一般性的回答。"""
            
            # 配置生成参数
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=kwargs.get('max_tokens', self.current_model.max_tokens),
                temperature=kwargs.get('temperature', self.current_model.temperature),
            )
            
            # 生成回复
            response = model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # 记录使用
            self.api_manager.record_api_usage(user_id, key_id)
            
            return response.text
        
        except Exception as e:
            return f"❌ Gemini API调用失败: {str(e)}"
    
    def get_model_info(self) -> Optional[ModelConfig]:
        """获取当前模型信息"""
        return self.current_model
    
    def get_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """获取用户的API使用统计"""
        if not self.api_manager or not user_id:
            return {}
        
        return self.api_manager.get_usage_statistics(user_id)

# 全局模型管理器实例
ai_model_manager = AIModelManager()

def get_ai_model_manager() -> AIModelManager:
    """获取AI模型管理器实例"""
    return ai_model_manager

def render_model_selector(user_id: str = None) -> str:
    """渲染模型选择器"""
    manager = get_ai_model_manager()
    available_models = manager.get_available_models(user_id)
    
    if not available_models:
        st.error("❌ 没有可用的AI模型")
        return None
    
    # 模型选择
    model_options = {}
    for key, config in available_models.items():
        icon = "🤖" if config.provider == ModelProvider.DEMO else "🧠"
        cost_info = f" (${config.cost_per_1k_tokens:.3f}/1K tokens)" if config.cost_per_1k_tokens > 0 else " (免费)"
        model_options[key] = f"{icon} {config.name}{cost_info}"
    
    selected_key = st.selectbox(
        "🤖 选择AI模型",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        help="选择要使用的AI模型"
    )
    
    if selected_key:
        if manager.select_model(selected_key, user_id):
            model_info = manager.get_model_info()
            if model_info:
                st.success(f"✅ 已选择模型: {model_info.name}")
                
                # 显示模型信息
                with st.expander("📊 模型详情", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**提供商**: {model_info.provider.value}")
                        st.write(f"**最大令牌**: {model_info.max_tokens}")
                        st.write(f"**支持流式**: {'✅' if model_info.supports_streaming else '❌'}")
                    with col2:
                        st.write(f"**支持图像**: {'✅' if model_info.supports_images else '❌'}")
                        st.write(f"**成本**: ${model_info.cost_per_1k_tokens:.3f}/1K tokens")
                    
                    st.write(f"**描述**: {model_info.description}")
                
                return selected_key
        else:
            st.error("❌ 模型选择失败，请检查API密钥配置")
    
    return None

def render_api_key_manager(user_id: str):
    """渲染API密钥管理界面"""
    if not API_MANAGER_AVAILABLE:
        st.error("❌ API管理功能不可用")
        return
    
    st.markdown("### 🔑 API密钥管理")
    
    manager = PrivateAPIManager()
    
    # 显示现有密钥
    user_keys = manager.get_user_api_keys(user_id)
    
    if user_keys:
        st.markdown("**📋 您的API密钥:**")
        for key_info in user_keys:
            with st.expander(f"{key_info.provider.value.upper()} - {key_info.key_name}", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**状态**: {key_info.status.value}")
                    st.write(f"**使用次数**: {key_info.usage_count}")
                with col2:
                    st.write(f"**日限制**: {key_info.daily_limit}")
                    st.write(f"**月限制**: {key_info.monthly_limit}")
                with col3:
                    if st.button(f"删除", key=f"delete_{key_info.key_id}"):
                        if manager.remove_api_key(user_id, key_info.key_id):
                            st.success("✅ 密钥已删除")
                            st.rerun()
                        else:
                            st.error("❌ 删除失败")
    
    # 添加新密钥
    st.markdown("**➕ 添加新的API密钥:**")
    
    with st.form("add_api_key"):
        col1, col2 = st.columns(2)
        with col1:
            provider = st.selectbox(
                "提供商",
                options=["openai", "google", "claude"],
                format_func=lambda x: {
                    "openai": "🤖 OpenAI",
                    "google": "🔍 Google (Gemini)",
                    "claude": "🧠 Anthropic (Claude)"
                }[x]
            )
        
        with col2:
            key_name = st.text_input("密钥名称", placeholder="例如：我的OpenAI密钥")
        
        api_key = st.text_input("API密钥", type="password", placeholder="输入您的API密钥")
        
        col1, col2 = st.columns(2)
        with col1:
            daily_limit = st.number_input("日使用限制", min_value=10, max_value=10000, value=1000)
        with col2:
            monthly_limit = st.number_input("月使用限制", min_value=100, max_value=100000, value=30000)
        
        description = st.text_area("描述（可选）", placeholder="描述这个API密钥的用途")
        
        if st.form_submit_button("🔑 添加密钥", type="primary"):
            if not key_name or not api_key:
                st.error("❌ 请填写密钥名称和API密钥")
            else:
                try:
                    from config.private_api_manager import APIProvider
                    provider_enum = APIProvider(provider)
                    key_id = manager.add_api_key(
                        user_id=user_id,
                        provider=provider_enum,
                        key_name=key_name,
                        api_key=api_key,
                        daily_limit=daily_limit,
                        monthly_limit=monthly_limit,
                        description=description
                    )
                    
                    if key_id:
                        st.success(f"✅ API密钥添加成功！ID: {key_id}")
                        st.rerun()
                    else:
                        st.error("❌ 添加失败，可能是密钥名称重复")
                except Exception as e:
                    st.error(f"❌ 添加失败: {str(e)}")

if __name__ == "__main__":
    # 测试代码
    manager = AIModelManager()
    print("可用模型:")
    for key, config in manager.get_available_models().items():
        print(f"- {key}: {config.name} ({config.provider.value})")