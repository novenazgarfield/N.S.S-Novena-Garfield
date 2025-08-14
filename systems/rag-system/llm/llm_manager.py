"""
LLM管理系统
"""
import subprocess
from typing import Optional, Dict, Any
from llama_cpp import Llama
import tiktoken

from config import ModelConfig
from utils.logger import logger

class LLMManager:
    """LLM管理类"""
    
    def __init__(self):
        self.llm = None
        self.context_size = ModelConfig.LLM_N_CTX
        self.max_tokens = ModelConfig.LLM_MAX_TOKENS
    
    def get_gpu_free_memory(self) -> list:
        """获取GPU空闲显存"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,nounits,noheader'],
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                check=True
            )
            free_mems = [int(x) for x in result.stdout.strip().split('\n')]
            logger.info(f"GPU空闲显存: {free_mems} MB")
            return free_mems
        except Exception as e:
            logger.warning(f"获取显存失败，将使用CPU模式: {e}")
            return []
    
    def calculate_gpu_layers(self) -> int:
        """根据显存自动计算GPU层数"""
        if not ModelConfig.AUTO_GPU_LAYERS:
            return 0
        
        free_mems = self.get_gpu_free_memory()
        
        if not free_mems:
            return 0
        
        max_free_mem = max(free_mems)
        
        if max_free_mem > 24000:
            n_gpu_layers = 30
        elif max_free_mem > 16000:
            n_gpu_layers = 20
        elif max_free_mem > 8000:
            n_gpu_layers = 10
        else:
            n_gpu_layers = 0
        
        logger.info(f"根据显存 {max_free_mem}MB 设置GPU层数: {n_gpu_layers}")
        return n_gpu_layers
    
    def load_model(self) -> Optional[Llama]:
        """加载LLM模型"""
        if ModelConfig.LLM_MODEL_PATH is None:
            logger.warning("LLM模型路径未配置，跳过模型加载")
            return None
            
        if self.llm is None:
            try:
                n_gpu_layers = self.calculate_gpu_layers()
                
                logger.info(f"正在加载LLM模型: {ModelConfig.LLM_MODEL_PATH}")
                logger.info(f"参数: n_ctx={self.context_size}, n_gpu_layers={n_gpu_layers}")
                
                # 这里需要安装llama-cpp-python，暂时跳过
                # self.llm = Llama(
                #     model_path=ModelConfig.LLM_MODEL_PATH,
                #     n_gpu_layers=n_gpu_layers,
                #     n_ctx=self.context_size,
                #     verbose=False  # 减少输出
                # )
                
                logger.warning("LLM模型加载被跳过（llama-cpp-python未安装）")
                return None
                
            except Exception as e:
                logger.error(f"LLM模型加载失败: {e}")
                return None
        
        return self.llm
    
    def count_tokens(self, text: str, encoding_name: str = "cl100k_base") -> int:
        """计算文本的token数量"""
        try:
            encoding = tiktoken.get_encoding(encoding_name)
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Token计数失败，使用估算: {e}")
            # 简单估算：平均每个token约4个字符
            return len(text) // 4
    
    def truncate_context(self, context: str, max_tokens: int) -> str:
        """截断上下文以适应token限制"""
        try:
            current_tokens = self.count_tokens(context)
            
            if current_tokens <= max_tokens:
                return context
            
            # 按句子分割，保留最重要的部分
            sentences = context.split('\n')
            truncated_context = ""
            
            for sentence in sentences:
                test_context = truncated_context + sentence + "\n"
                if self.count_tokens(test_context) > max_tokens:
                    break
                truncated_context = test_context
            
            logger.info(f"上下文已截断: {current_tokens} -> {self.count_tokens(truncated_context)} tokens")
            return truncated_context
            
        except Exception as e:
            logger.error(f"上下文截断失败: {e}")
            # 简单截断
            return context[:max_tokens * 4]
    
    def generate_response(self, prompt: str, max_tokens: int = None, **kwargs) -> str:
        """生成回答"""
        try:
            model = self.load_model()
            
            if model is None:
                # 如果没有LLM模型，返回一个模拟回答
                logger.info("LLM模型未加载，返回模拟回答")
                return "抱歉，LLM模型未配置。这是一个基于检索到的文档内容的模拟回答。请配置LLM模型以获得智能生成的回答。"
            
            max_tokens = max_tokens or self.max_tokens
            
            # 确保prompt不超过上下文限制
            max_prompt_tokens = self.context_size - max_tokens - 100  # 留一些缓冲
            prompt = self.truncate_context(prompt, max_prompt_tokens)
            
            logger.info(f"正在生成回答，最大tokens: {max_tokens}")
            
            # 设置默认参数
            generation_params = {
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
                "stop": ["\n\n", "问题：", "用户：", "助手："],
                **kwargs
            }
            
            # 生成回答
            output = model(prompt, **generation_params)
            
            if output and 'choices' in output and len(output['choices']) > 0:
                answer = output['choices'][0]['text'].strip()
                logger.info(f"回答生成成功，长度: {len(answer)} 字符")
                return answer
            else:
                logger.error("模型输出格式异常")
                return "抱歉，生成回答时出现问题。"
                
        except Exception as e:
            logger.error(f"生成回答失败: {e}")
            return f"抱歉，生成回答时出现错误: {str(e)}"
    
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
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        try:
            info = {
                "model_path": ModelConfig.LLM_MODEL_PATH,
                "context_size": self.context_size,
                "max_tokens": self.max_tokens,
                "model_loaded": self.llm is not None
            }
            
            if self.llm:
                info.update({
                    "actual_context_size": self.llm.context_params.n_ctx,
                    "gpu_layers": getattr(self.llm, 'n_gpu_layers', 0)
                })
            
            return info
            
        except Exception as e:
            logger.error(f"获取模型信息失败: {e}")
            return {"error": str(e)}
    
    def unload_model(self):
        """卸载模型以释放内存"""
        try:
            if self.llm:
                del self.llm
                self.llm = None
                logger.info("LLM模型已卸载")
        except Exception as e:
            logger.error(f"卸载模型失败: {e}")