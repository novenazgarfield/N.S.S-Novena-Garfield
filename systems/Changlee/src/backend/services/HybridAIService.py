#!/usr/bin/env python3
"""
Changlee混合AI服务
支持本地AI (Google Gemma 2) + 云端API (Gemini等) 的混合智能对话
用户可以灵活选择AI服务类型，平衡性能、隐私和功能需求
"""

import os
import sys
import json
import time
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import psutil
import gc
from enum import Enum

# 本地AI支持
try:
    import torch
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM, 
        GenerationConfig,
        BitsAndBytesConfig
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers库未安装，本地AI功能将不可用")

# Gemini API支持
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Google Generative AI库未安装，Gemini功能将不可用")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIServiceType(Enum):
    """AI服务类型枚举"""
    LOCAL = "local"          # 本地Gemma 2模型
    GEMINI = "gemini"        # Google Gemini API
    DEEPSEEK = "deepseek"    # DeepSeek API
    AUTO = "auto"            # 自动选择最佳服务

class HybridAIService:
    """
    混合AI服务
    支持本地AI和多种云端API的智能对话服务
    """
    
    def __init__(self, 
                 preferred_service: AIServiceType = AIServiceType.AUTO,
                 local_model_name: str = "google/gemma-2-2b",
                 device: Optional[str] = None,
                 cache_dir: Optional[str] = None,
                 max_memory_gb: float = 4.0):
        """
        初始化混合AI服务
        
        Args:
            preferred_service: 首选AI服务类型
            local_model_name: 本地模型名称
            device: 计算设备
            cache_dir: 模型缓存目录
            max_memory_gb: 最大内存使用量(GB)
        """
        self.preferred_service = preferred_service
        self.local_model_name = local_model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.cache_dir = cache_dir
        self.max_memory_gb = max_memory_gb
        
        # 服务状态
        self.available_services = []
        self.current_service = None
        
        # 本地AI组件
        self.local_tokenizer = None
        self.local_model = None
        self.local_generation_config = None
        self.local_loaded = False
        
        # API配置
        self.api_configs = {
            'gemini': {
                'api_key': os.getenv('GEMINI_API_KEY'),
                'model': 'gemini-1.5-flash',
                'enabled': False
            },
            'deepseek': {
                'api_key': os.getenv('DEEPSEEK_API_KEY'),
                'base_url': 'https://api.deepseek.com/v1',
                'model': 'deepseek-chat',
                'enabled': False
            }
        }
        
        # 长离人格配置
        self.changlee_personality = {
            'base_prompt': """你是长离，一个温暖、智慧的AI学习伙伴。你的特点是：
- 温柔耐心，善于鼓励
- 富有创意，能用有趣的方式解释知识
- 关心用户的学习进度和情感状态
- 说话风格亲切自然，偶尔使用可爱的表情符号
- 会根据用户的学习情况给出个性化建议""",
            
            'learning_contexts': {
                'word_learning': "现在我们在学习新单词，请用鼓励的语气帮助用户记忆，可以提供词根、联想记忆法等。",
                'spelling_practice': "现在是拼写练习时间，请给出积极的反馈和建议，帮助用户改正错误。",
                'daily_greeting': "请给出一句温暖的日常问候，询问用户今天的学习计划。",
                'encouragement': "用户需要学习鼓励，请给出正能量的话语，帮助用户重拾信心。",
                'explanation': "请用简单易懂的方式解释概念，可以使用比喻和例子。"
            }
        }
        
        # 初始化服务
        logger.info(f"初始化混合AI服务，首选服务: {preferred_service.value}")
        self._initialize_services()
    
    def _initialize_services(self):
        """初始化可用的AI服务"""
        # 检查本地AI可用性
        if TRANSFORMERS_AVAILABLE:
            self.available_services.append(AIServiceType.LOCAL)
            logger.info("✅ 本地AI服务可用")
        
        # 检查Gemini API可用性
        if GEMINI_AVAILABLE and self.api_configs['gemini']['api_key']:
            try:
                genai.configure(api_key=self.api_configs['gemini']['api_key'])
                self.api_configs['gemini']['enabled'] = True
                self.available_services.append(AIServiceType.GEMINI)
                logger.info("✅ Gemini API服务可用")
            except Exception as e:
                logger.warning(f"⚠️ Gemini API初始化失败: {e}")
        
        # 检查DeepSeek API可用性
        if self.api_configs['deepseek']['api_key']:
            self.api_configs['deepseek']['enabled'] = True
            self.available_services.append(AIServiceType.DEEPSEEK)
            logger.info("✅ DeepSeek API服务可用")
        
        # 选择当前服务
        self._select_current_service()
    
    def _select_current_service(self):
        """选择当前使用的AI服务"""
        if self.preferred_service == AIServiceType.AUTO:
            # 自动选择：优先级 Gemini > 本地AI > DeepSeek
            if AIServiceType.GEMINI in self.available_services:
                self.current_service = AIServiceType.GEMINI
            elif AIServiceType.LOCAL in self.available_services:
                self.current_service = AIServiceType.LOCAL
            elif AIServiceType.DEEPSEEK in self.available_services:
                self.current_service = AIServiceType.DEEPSEEK
        else:
            # 使用指定服务
            if self.preferred_service in self.available_services:
                self.current_service = self.preferred_service
            else:
                # 回退到可用服务
                self.current_service = self.available_services[0] if self.available_services else None
        
        logger.info(f"当前AI服务: {self.current_service.value if self.current_service else 'None'}")
    
    async def load_local_model(self) -> bool:
        """加载本地AI模型"""
        if not TRANSFORMERS_AVAILABLE:
            logger.error("❌ Transformers库不可用，无法加载本地模型")
            return False
        
        if self.local_loaded:
            return True
        
        try:
            logger.info(f"🔄 开始加载本地模型: {self.local_model_name}")
            
            # 检查内存
            available_memory = psutil.virtual_memory().available / (1024**3)
            if available_memory < self.max_memory_gb:
                logger.warning(f"⚠️ 可用内存不足: {available_memory:.1f}GB < {self.max_memory_gb}GB")
            
            # 加载tokenizer
            self.local_tokenizer = AutoTokenizer.from_pretrained(
                self.local_model_name,
                cache_dir=self.cache_dir,
                trust_remote_code=True
            )
            
            # 配置量化（如果内存不足）
            quantization_config = None
            if available_memory < 8.0:  # 内存不足8GB时使用量化
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                logger.info("🔧 启用4位量化以节省内存")
            
            # 加载模型
            self.local_model = AutoModelForCausalLM.from_pretrained(
                self.local_model_name,
                cache_dir=self.cache_dir,
                device_map="auto",
                torch_dtype=torch.float16,
                quantization_config=quantization_config,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # 配置生成参数
            self.local_generation_config = GenerationConfig(
                max_new_tokens=256,
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.1,
                do_sample=True,
                pad_token_id=self.local_tokenizer.eos_token_id
            )
            
            self.local_loaded = True
            logger.info("✅ 本地模型加载成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 本地模型加载失败: {e}")
            return False
    
    async def generate_with_local(self, prompt: str, context: str = "daily_greeting") -> Dict[str, Any]:
        """使用本地AI生成回复"""
        if not self.local_loaded:
            if not await self.load_local_model():
                return {"success": False, "error": "本地模型加载失败"}
        
        try:
            # 构建完整提示
            full_prompt = self._build_prompt(prompt, context)
            
            # 编码输入
            inputs = self.local_tokenizer.encode(full_prompt, return_tensors="pt")
            inputs = inputs.to(self.device)
            
            # 生成回复
            start_time = time.time()
            with torch.no_grad():
                outputs = self.local_model.generate(
                    inputs,
                    generation_config=self.local_generation_config,
                    pad_token_id=self.local_tokenizer.eos_token_id
                )
            
            # 解码输出
            response = self.local_tokenizer.decode(
                outputs[0][inputs.shape[1]:], 
                skip_special_tokens=True
            ).strip()
            
            generation_time = time.time() - start_time
            
            return {
                "success": True,
                "response": response,
                "service": "local",
                "model": self.local_model_name,
                "generation_time": generation_time,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"❌ 本地AI生成失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_with_gemini(self, prompt: str, context: str = "daily_greeting") -> Dict[str, Any]:
        """使用Gemini API生成回复"""
        if not self.api_configs['gemini']['enabled']:
            return {"success": False, "error": "Gemini API不可用"}
        
        try:
            # 构建完整提示
            full_prompt = self._build_prompt(prompt, context)
            
            # 调用Gemini API
            model = genai.GenerativeModel(self.api_configs['gemini']['model'])
            start_time = time.time()
            
            response = await asyncio.to_thread(
                model.generate_content,
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=256,
                    top_p=0.9,
                    top_k=50
                )
            )
            
            generation_time = time.time() - start_time
            
            return {
                "success": True,
                "response": response.text.strip(),
                "service": "gemini",
                "model": self.api_configs['gemini']['model'],
                "generation_time": generation_time,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"❌ Gemini API调用失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_with_deepseek(self, prompt: str, context: str = "daily_greeting") -> Dict[str, Any]:
        """使用DeepSeek API生成回复"""
        if not self.api_configs['deepseek']['enabled']:
            return {"success": False, "error": "DeepSeek API不可用"}
        
        try:
            # 构建完整提示
            full_prompt = self._build_prompt(prompt, context)
            
            # 准备API请求
            headers = {
                "Authorization": f"Bearer {self.api_configs['deepseek']['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.api_configs['deepseek']['model'],
                "messages": [
                    {"role": "user", "content": full_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 256,
                "top_p": 0.9
            }
            
            # 调用API
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_configs['deepseek']['base_url']}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        generation_time = time.time() - start_time
                        
                        return {
                            "success": True,
                            "response": result['choices'][0]['message']['content'].strip(),
                            "service": "deepseek",
                            "model": self.api_configs['deepseek']['model'],
                            "generation_time": generation_time,
                            "context": context
                        }
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"API错误: {response.status} - {error_text}"}
            
        except Exception as e:
            logger.error(f"❌ DeepSeek API调用失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _build_prompt(self, user_input: str, context: str) -> str:
        """构建完整的提示词"""
        base_prompt = self.changlee_personality['base_prompt']
        context_prompt = self.changlee_personality['learning_contexts'].get(
            context, 
            self.changlee_personality['learning_contexts']['daily_greeting']
        )
        
        return f"""{base_prompt}

{context_prompt}

用户输入: {user_input}

请以长离的身份回复用户，保持温暖友好的语调："""
    
    async def generate(self, prompt: str, context: str = "daily_greeting", 
                      service_type: Optional[AIServiceType] = None) -> Dict[str, Any]:
        """
        生成AI回复
        
        Args:
            prompt: 用户输入
            context: 对话上下文
            service_type: 指定使用的AI服务类型
        
        Returns:
            生成结果字典
        """
        # 确定使用的服务
        target_service = service_type or self.current_service
        
        if not target_service:
            return {"success": False, "error": "没有可用的AI服务"}
        
        # 根据服务类型调用相应的生成方法
        try:
            if target_service == AIServiceType.LOCAL:
                return await self.generate_with_local(prompt, context)
            elif target_service == AIServiceType.GEMINI:
                return await self.generate_with_gemini(prompt, context)
            elif target_service == AIServiceType.DEEPSEEK:
                return await self.generate_with_deepseek(prompt, context)
            else:
                return {"success": False, "error": f"不支持的服务类型: {target_service}"}
        
        except Exception as e:
            logger.error(f"❌ AI生成失败: {e}")
            # 尝试回退到其他可用服务
            return await self._fallback_generate(prompt, context, target_service)
    
    async def _fallback_generate(self, prompt: str, context: str, 
                                failed_service: AIServiceType) -> Dict[str, Any]:
        """回退到其他可用服务"""
        logger.info(f"🔄 {failed_service.value}服务失败，尝试回退到其他服务")
        
        # 获取其他可用服务
        fallback_services = [s for s in self.available_services if s != failed_service]
        
        for service in fallback_services:
            try:
                result = await self.generate(prompt, context, service)
                if result.get("success"):
                    result["fallback"] = True
                    result["original_service"] = failed_service.value
                    return result
            except Exception as e:
                logger.warning(f"⚠️ 回退服务 {service.value} 也失败: {e}")
                continue
        
        return {"success": False, "error": "所有AI服务都不可用"}
    
    def switch_service(self, service_type: AIServiceType) -> bool:
        """切换AI服务类型"""
        if service_type in self.available_services:
            self.current_service = service_type
            logger.info(f"✅ 已切换到 {service_type.value} 服务")
            return True
        else:
            logger.warning(f"⚠️ 服务 {service_type.value} 不可用")
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "service_name": "Changlee混合AI服务",
            "version": "2.0.0",
            "current_service": self.current_service.value if self.current_service else None,
            "available_services": [s.value for s in self.available_services],
            "local_model_loaded": self.local_loaded,
            "local_model_name": self.local_model_name,
            "device": self.device,
            "api_status": {
                "gemini": self.api_configs['gemini']['enabled'],
                "deepseek": self.api_configs['deepseek']['enabled']
            },
            "supported_contexts": list(self.changlee_personality['learning_contexts'].keys()),
            "memory_usage": f"{psutil.virtual_memory().percent}%",
            "timestamp": datetime.now().isoformat()
        }
    
    def optimize_memory(self):
        """优化内存使用"""
        try:
            # 清理Python垃圾回收
            gc.collect()
            
            # 清理CUDA缓存（如果使用GPU）
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("✅ 内存优化完成")
            return True
        except Exception as e:
            logger.error(f"❌ 内存优化失败: {e}")
            return False
    
    def clear_cache(self):
        """清理缓存"""
        try:
            # 这里可以添加具体的缓存清理逻辑
            logger.info("✅ 缓存清理完成")
            return True
        except Exception as e:
            logger.error(f"❌ 缓存清理失败: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = {
            "healthy": True,
            "services": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # 检查各个服务的健康状态
        for service in self.available_services:
            try:
                if service == AIServiceType.LOCAL:
                    status["services"]["local"] = {
                        "available": self.local_loaded,
                        "model": self.local_model_name,
                        "device": self.device
                    }
                elif service == AIServiceType.GEMINI:
                    status["services"]["gemini"] = {
                        "available": self.api_configs['gemini']['enabled'],
                        "model": self.api_configs['gemini']['model']
                    }
                elif service == AIServiceType.DEEPSEEK:
                    status["services"]["deepseek"] = {
                        "available": self.api_configs['deepseek']['enabled'],
                        "model": self.api_configs['deepseek']['model']
                    }
            except Exception as e:
                status["healthy"] = False
                status["services"][service.value] = {"error": str(e)}
        
        return status
    
    def __del__(self):
        """析构函数，清理资源"""
        try:
            if hasattr(self, 'local_model') and self.local_model:
                del self.local_model
            if hasattr(self, 'local_tokenizer') and self.local_tokenizer:
                del self.local_tokenizer
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass