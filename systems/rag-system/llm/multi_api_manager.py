"""
多API支持的LLM管理器
支持本地模型、魔搭API、OpenAI API等多种接口
"""
import os
import json
import requests
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import subprocess

from config_advanced import ModelConfig, APIConfig, DistributedConfig
from utils.logger import logger

class BaseLLMProvider(ABC):
    """LLM提供者基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """生成回答"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查是否可用"""
        pass

class LocalLLMProvider(BaseLLMProvider):
    """本地LLM提供者（llama-cpp-python）"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.llm = None
        self.device = config.get("device", "cuda:0")
    
    def load_model(self):
        """加载本地模型"""
        if self.llm is None:
            try:
                from llama_cpp import Llama
                
                model_path = self.config.get("model_path")
                if not model_path or not os.path.exists(model_path):
                    logger.error(f"本地模型文件不存在: {model_path}")
                    return None
                
                # 根据设备配置GPU层数
                n_gpu_layers = self.config.get("n_gpu_layers", 0)
                if self.device.startswith("cuda"):
                    n_gpu_layers = self._calculate_gpu_layers()
                
                logger.info(f"正在加载本地模型: {model_path}")
                logger.info(f"设备: {self.device}, GPU层数: {n_gpu_layers}")
                
                self.llm = Llama(
                    model_path=model_path,
                    n_gpu_layers=n_gpu_layers,
                    n_ctx=self.config.get("n_ctx", 4096),
                    verbose=False
                )
                
                logger.info("本地模型加载成功")
                
            except ImportError:
                logger.error("llama-cpp-python未安装，无法使用本地模型")
                return None
            except Exception as e:
                logger.error(f"本地模型加载失败: {e}")
                return None
        
        return self.llm
    
    def _calculate_gpu_layers(self) -> int:
        """根据GPU显存计算层数"""
        try:
            # 获取当前设备的显存信息
            device_id = self.device.split(":")[-1] if ":" in self.device else "0"
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,nounits,noheader', f'--id={device_id}'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
            )
            free_mem = int(result.stdout.strip())
            
            # 根据显存大小设置层数
            if free_mem > 20000:  # 3090 24GB
                return 35
            elif free_mem > 6000:  # 4060 8GB
                return 15
            else:
                return 0
                
        except Exception as e:
            logger.warning(f"无法获取GPU信息，使用默认层数: {e}")
            return self.config.get("n_gpu_layers", 0)
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """生成回答"""
        model = self.load_model()
        if model is None:
            return "本地模型不可用"
        
        try:
            max_tokens = kwargs.get("max_tokens", 1000)
            temperature = kwargs.get("temperature", 0.7)
            
            output = model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=kwargs.get("stop", ["\n\n", "问题：", "用户："]),
                echo=False
            )
            
            if output and 'choices' in output and len(output['choices']) > 0:
                return output['choices'][0]['text'].strip()
            else:
                return "生成回答失败"
                
        except Exception as e:
            logger.error(f"本地模型生成失败: {e}")
            return f"生成回答时出错: {str(e)}"
    
    def is_available(self) -> bool:
        """检查是否可用"""
        model_path = self.config.get("model_path")
        return model_path and os.path.exists(model_path)

class ModelScopeProvider(BaseLLMProvider):
    """魔搭API提供者"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://dashscope.aliyuncs.com/api/v1")
        self.model = config.get("model", "qwen2.5-72b-instruct")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """生成回答"""
        if not self.api_key:
            return "魔搭API密钥未配置"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "input": {
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                "parameters": {
                    "max_tokens": kwargs.get("max_tokens", 1500),
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9)
                }
            }
            
            response = requests.post(
                f"{self.base_url}/services/aigc/text-generation/generation",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "output" in result and "text" in result["output"]:
                    return result["output"]["text"].strip()
                else:
                    logger.error(f"魔搭API响应格式异常: {result}")
                    return "API响应格式异常"
            else:
                logger.error(f"魔搭API请求失败: {response.status_code}, {response.text}")
                return f"API请求失败: {response.status_code}"
                
        except Exception as e:
            logger.error(f"魔搭API调用失败: {e}")
            return f"API调用失败: {str(e)}"
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return bool(self.api_key)

class OpenAIProvider(BaseLLMProvider):
    """OpenAI API提供者"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.model = config.get("model", "gpt-4o-mini")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """生成回答"""
        if not self.api_key:
            return "OpenAI API密钥未配置"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": kwargs.get("max_tokens", 1500),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9)
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    logger.error(f"OpenAI API响应格式异常: {result}")
                    return "API响应格式异常"
            else:
                logger.error(f"OpenAI API请求失败: {response.status_code}, {response.text}")
                return f"API请求失败: {response.status_code}"
                
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            return f"API调用失败: {str(e)}"
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return bool(self.api_key)

class ZhipuProvider(BaseLLMProvider):
    """智谱API提供者"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://open.bigmodel.cn/api/paas/v4")
        self.model = config.get("model", "glm-4-flash")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """生成回答"""
        if not self.api_key:
            return "智谱API密钥未配置"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": kwargs.get("max_tokens", 1500),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9)
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    logger.error(f"智谱API响应格式异常: {result}")
                    return "API响应格式异常"
            else:
                logger.error(f"智谱API请求失败: {response.status_code}, {response.text}")
                return f"API请求失败: {response.status_code}"
                
        except Exception as e:
            logger.error(f"智谱API调用失败: {e}")
            return f"API调用失败: {str(e)}"
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return bool(self.api_key)

class MultiAPIManager:
    """多API管理器"""
    
    def __init__(self):
        self.providers = {}
        self.current_provider = None
        self._init_providers()
    
    def _init_providers(self):
        """初始化所有提供者"""
        # 本地模型提供者
        local_config = APIConfig.get_config("local")
        self.providers["local"] = LocalLLMProvider(local_config)
        
        # 魔搭API提供者
        modelscope_config = APIConfig.get_config("modelscope")
        self.providers["modelscope"] = ModelScopeProvider(modelscope_config)
        
        # OpenAI API提供者
        openai_config = APIConfig.get_config("openai")
        self.providers["openai"] = OpenAIProvider(openai_config)
        
        # 智谱API提供者
        zhipu_config = APIConfig.get_config("zhipu")
        self.providers["zhipu"] = ZhipuProvider(zhipu_config)
        
        # 设置当前提供者
        self.switch_provider(ModelConfig.CURRENT_API)
    
    def switch_provider(self, api_type: str):
        """切换API提供者"""
        if api_type in self.providers:
            self.current_provider = self.providers[api_type]
            ModelConfig.switch_api(api_type)
            logger.info(f"已切换到API提供者: {api_type}")
        else:
            logger.error(f"不支持的API类型: {api_type}")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """生成回答"""
        if self.current_provider is None:
            return "未配置API提供者"
        
        if not self.current_provider.is_available():
            # 尝试切换到可用的提供者
            for api_type, provider in self.providers.items():
                if provider.is_available():
                    logger.info(f"当前提供者不可用，自动切换到: {api_type}")
                    self.switch_provider(api_type)
                    break
            else:
                return "没有可用的API提供者"
        
        return self.current_provider.generate_response(prompt, **kwargs)
    
    def get_available_providers(self) -> List[str]:
        """获取可用的提供者列表"""
        available = []
        for api_type, provider in self.providers.items():
            if provider.is_available():
                available.append(api_type)
        return available
    
    def get_current_provider_info(self) -> Dict[str, Any]:
        """获取当前提供者信息"""
        if self.current_provider is None:
            return {"type": "none", "available": False}
        
        current_type = ModelConfig.CURRENT_API
        return {
            "type": current_type,
            "name": APIConfig.API_TYPES.get(current_type, "未知"),
            "available": self.current_provider.is_available(),
            "config": self.current_provider.config
        }
    
    def build_prompt(self, question: str, context: str, system_prompt: str = None) -> str:
        """构建完整的prompt"""
        try:
            default_system_prompt = """你是一个科研知识问答助手，请阅读以下内容，并根据内容用中文回答最后提出的问题。
请确保回答准确、详细且有帮助。如果无法从提供的内容中找到答案，请诚实地说明。"""
            
            system_prompt = system_prompt or default_system_prompt
            
            prompt = f"""{system_prompt}

{context}

问题：{question}

回答："""
            
            return prompt
            
        except Exception as e:
            logger.error(f"构建prompt失败: {e}")
            raise