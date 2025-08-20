"""
本地AI服务 - 基于Google Gemma 2 (2B)
为Changlee桌面宠物提供本地化AI核心
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
import logging
from typing import Dict, List, Optional, Any
import json
import time
from pathlib import Path
import threading
from queue import Queue, Empty
import gc

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalAIService:
    """
    本地AI服务
    基于Gemma 2 (2B)模型提供本地化智能对话和内容生成
    """
    
    def __init__(self, 
                 model_name: str = "google/gemma-2-2b",
                 device: Optional[str] = None,
                 cache_dir: Optional[str] = None,
                 max_memory_gb: float = 4.0):
        """
        初始化本地AI服务
        
        Args:
            model_name: Gemma 2模型名称
            device: 计算设备
            cache_dir: 模型缓存目录
            max_memory_gb: 最大内存使用量(GB)
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.cache_dir = cache_dir
        self.max_memory_gb = max_memory_gb
        
        # 模型和tokenizer
        self.tokenizer = None
        self.model = None
        self.generation_config = None
        
        # 服务状态
        self.is_loaded = False
        self.is_busy = False
        
        # 请求队列
        self.request_queue = Queue()
        self.response_cache = {}
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'average_response_time': 0.0,
            'cache_hits': 0,
            'memory_usage_mb': 0.0
        }
        
        # 预定义的Changlee人格提示词
        self.changlee_personality = {
            'base_prompt': """你是长离，一个温暖、智慧的AI学习伙伴。你的特点是：
- 温柔耐心，善于鼓励
- 富有创意，能用有趣的方式解释知识
- 关心用户的学习进度和情感状态
- 说话风格亲切自然，偶尔使用可爱的表情符号
- 专注于英语学习辅导和情感陪伴

请用简洁、温暖的语言回应，每次回复控制在50字以内。""",
            
            'learning_contexts': {
                'word_learning': "现在我们在学习新单词，请用鼓励的语气帮助用户记忆。",
                'spelling_practice': "现在是拼写练习时间，请给出积极的反馈和建议。",
                'daily_greeting': "请给出一句温暖的日常问候。",
                'encouragement': "用户需要学习鼓励，请给出正能量的话语。",
                'explanation': "请用简单易懂的方式解释概念。"
            }
        }
        
        logger.info(f"初始化本地AI服务: {model_name}, 设备: {self.device}")
    
    def load_model(self) -> bool:
        """加载Gemma 2模型"""
        try:
            logger.info(f"开始加载Gemma 2模型: {self.model_name}")
            
            # 检查内存
            if not self._check_memory_availability():
                logger.warning("内存不足，可能影响模型性能")
            
            # 加载tokenizer
            logger.info("加载tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                trust_remote_code=True
            )
            
            # 设置pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # 加载模型
            logger.info("加载模型...")
            model_kwargs = {
                'cache_dir': self.cache_dir,
                'trust_remote_code': True,
                'torch_dtype': torch.float16 if self.device == 'cuda' else torch.float32,
                'device_map': 'auto' if self.device == 'cuda' else None,
                'low_cpu_mem_usage': True
            }
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            # 如果不是自动设备映射，手动移动到设备
            if model_kwargs['device_map'] is None:
                self.model = self.model.to(self.device)
            
            # 设置为评估模式
            self.model.eval()
            
            # 配置生成参数
            self.generation_config = GenerationConfig(
                max_new_tokens=100,
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                do_sample=True,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                use_cache=True
            )
            
            self.is_loaded = True
            logger.info("Gemma 2模型加载成功")
            
            # 更新内存使用统计
            self._update_memory_stats()
            
            return True
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            self.is_loaded = False
            return False
    
    def generate_response(self, 
                         prompt: str,
                         context: str = "daily_greeting",
                         max_length: int = 50,
                         use_cache: bool = True) -> Dict[str, Any]:
        """
        生成AI响应
        
        Args:
            prompt: 用户输入
            context: 对话上下文类型
            max_length: 最大响应长度
            use_cache: 是否使用缓存
            
        Returns:
            生成结果字典
        """
        if not self.is_loaded:
            return {
                'success': False,
                'error': '模型未加载',
                'response': '抱歉，我还在准备中...'
            }
        
        if self.is_busy:
            return {
                'success': False,
                'error': '服务繁忙',
                'response': '我正在思考其他问题，请稍等一下~'
            }
        
        self.stats['total_requests'] += 1
        start_time = time.time()
        
        try:
            # 检查缓存
            cache_key = f"{prompt}_{context}_{max_length}"
            if use_cache and cache_key in self.response_cache:
                self.stats['cache_hits'] += 1
                cached_response = self.response_cache[cache_key]
                cached_response['from_cache'] = True
                return cached_response
            
            self.is_busy = True
            
            # 构建完整提示词
            full_prompt = self._build_changlee_prompt(prompt, context)
            
            # 生成响应
            response_text = self._generate_text(full_prompt, max_length)
            
            # 后处理响应
            processed_response = self._post_process_response(response_text, context)
            
            # 构建结果
            result = {
                'success': True,
                'response': processed_response,
                'context': context,
                'generation_time': time.time() - start_time,
                'from_cache': False,
                'metadata': {
                    'model': self.model_name,
                    'device': self.device,
                    'prompt_length': len(prompt),
                    'response_length': len(processed_response)
                }
            }
            
            # 缓存结果
            if use_cache and len(self.response_cache) < 100:  # 限制缓存大小
                self.response_cache[cache_key] = result.copy()
            
            self.stats['successful_requests'] += 1
            self._update_response_time_stats(time.time() - start_time)
            
            return result
            
        except Exception as e:
            logger.error(f"生成响应失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': '抱歉，我遇到了一些问题，请稍后再试~',
                'generation_time': time.time() - start_time
            }
        finally:
            self.is_busy = False
    
    def generate_word_hint(self, word: str, difficulty: str = "intermediate") -> Dict[str, Any]:
        """
        为单词生成学习提示
        
        Args:
            word: 目标单词
            difficulty: 难度级别
            
        Returns:
            单词提示结果
        """
        prompt = f"请为单词'{word}'生成一个有趣的记忆提示或例句"
        
        return self.generate_response(
            prompt=prompt,
            context="word_learning",
            max_length=60
        )
    
    def generate_encouragement(self, learning_progress: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成学习鼓励语
        
        Args:
            learning_progress: 学习进度信息
            
        Returns:
            鼓励语结果
        """
        words_learned = learning_progress.get('words_learned', 0)
        accuracy = learning_progress.get('accuracy', 0.0)
        
        prompt = f"用户今天学了{words_learned}个单词，准确率{accuracy:.1%}，请给出鼓励"
        
        return self.generate_response(
            prompt=prompt,
            context="encouragement",
            max_length=40
        )
    
    def generate_daily_greeting(self, time_of_day: str = "morning") -> Dict[str, Any]:
        """
        生成每日问候语
        
        Args:
            time_of_day: 时间段 ("morning", "afternoon", "evening")
            
        Returns:
            问候语结果
        """
        time_prompts = {
            "morning": "请生成一句温暖的早晨问候语",
            "afternoon": "请生成一句愉快的下午问候语", 
            "evening": "请生成一句温馨的晚上问候语"
        }
        
        prompt = time_prompts.get(time_of_day, time_prompts["morning"])
        
        return self.generate_response(
            prompt=prompt,
            context="daily_greeting",
            max_length=30
        )
    
    def generate_explanation(self, concept: str, user_level: str = "beginner") -> Dict[str, Any]:
        """
        生成概念解释
        
        Args:
            concept: 需要解释的概念
            user_level: 用户水平
            
        Returns:
            解释结果
        """
        prompt = f"请用简单易懂的方式解释'{concept}'"
        
        return self.generate_response(
            prompt=prompt,
            context="explanation",
            max_length=80
        )
    
    def _build_changlee_prompt(self, user_input: str, context: str) -> str:
        """构建长离人格化的提示词"""
        base_prompt = self.changlee_personality['base_prompt']
        context_prompt = self.changlee_personality['learning_contexts'].get(
            context, 
            self.changlee_personality['learning_contexts']['daily_greeting']
        )
        
        full_prompt = f"{base_prompt}\n\n{context_prompt}\n\n用户: {user_input}\n长离:"
        
        return full_prompt
    
    def _generate_text(self, prompt: str, max_length: int) -> str:
        """生成文本"""
        try:
            # 编码输入
            inputs = self.tokenizer.encode(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # 生成响应
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    generation_config=self.generation_config,
                    max_new_tokens=max_length,
                    pad_token_id=self.tokenizer.pad_token_id
                )
            
            # 解码响应
            response = self.tokenizer.decode(
                outputs[0][inputs.shape[1]:],
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"文本生成失败: {str(e)}")
            raise
    
    def _post_process_response(self, response: str, context: str) -> str:
        """后处理响应文本"""
        # 移除可能的重复内容
        lines = response.split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if line and line not in processed_lines:
                processed_lines.append(line)
        
        processed_response = ' '.join(processed_lines)
        
        # 长度限制
        if len(processed_response) > 100:
            processed_response = processed_response[:97] + "..."
        
        # 确保以合适的标点结尾
        if processed_response and not processed_response[-1] in '.!?~':
            processed_response += "~"
        
        return processed_response
    
    def _check_memory_availability(self) -> bool:
        """检查内存可用性"""
        try:
            import psutil
            available_memory_gb = psutil.virtual_memory().available / (1024**3)
            
            if available_memory_gb < self.max_memory_gb:
                logger.warning(f"可用内存 {available_memory_gb:.1f}GB < 推荐内存 {self.max_memory_gb}GB")
                return False
            
            return True
            
        except ImportError:
            logger.warning("psutil未安装，无法检查内存")
            return True
    
    def _update_memory_stats(self):
        """更新内存使用统计"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024**2)
            self.stats['memory_usage_mb'] = memory_mb
            
        except ImportError:
            pass
    
    def _update_response_time_stats(self, response_time: float):
        """更新响应时间统计"""
        current_avg = self.stats['average_response_time']
        successful_requests = self.stats['successful_requests']
        
        if successful_requests == 1:
            self.stats['average_response_time'] = response_time
        else:
            self.stats['average_response_time'] = (
                (current_avg * (successful_requests - 1) + response_time) / successful_requests
            )
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            'service_name': 'Changlee本地AI服务',
            'model_name': self.model_name,
            'device': self.device,
            'is_loaded': self.is_loaded,
            'is_busy': self.is_busy,
            'stats': self.stats,
            'cache_size': len(self.response_cache),
            'supported_contexts': list(self.changlee_personality['learning_contexts'].keys())
        }
    
    def clear_cache(self):
        """清理响应缓存"""
        self.response_cache.clear()
        logger.info("响应缓存已清理")
    
    def optimize_memory(self):
        """优化内存使用"""
        try:
            # 清理缓存
            self.clear_cache()
            
            # 强制垃圾回收
            gc.collect()
            
            # 如果使用CUDA，清理GPU缓存
            if self.device == 'cuda' and torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # 更新内存统计
            self._update_memory_stats()
            
            logger.info("内存优化完成")
            
        except Exception as e:
            logger.error(f"内存优化失败: {str(e)}")
    
    def unload_model(self):
        """卸载模型释放内存"""
        try:
            if self.model is not None:
                del self.model
                self.model = None
            
            if self.tokenizer is not None:
                del self.tokenizer
                self.tokenizer = None
            
            self.is_loaded = False
            
            # 强制垃圾回收
            gc.collect()
            
            if self.device == 'cuda' and torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("模型已卸载")
            
        except Exception as e:
            logger.error(f"模型卸载失败: {str(e)}")
    
    def reload_model(self) -> bool:
        """重新加载模型"""
        logger.info("重新加载模型...")
        self.unload_model()
        return self.load_model()


# 使用示例和测试函数
def test_local_ai_service():
    """测试本地AI服务"""
    try:
        # 初始化服务
        ai_service = LocalAIService()
        
        # 加载模型
        if not ai_service.load_model():
            print("❌ 模型加载失败")
            return
        
        # 测试不同类型的生成
        test_cases = [
            ("你好", "daily_greeting"),
            ("apple", "word_learning"),
            ("我今天学得不好", "encouragement"),
            ("什么是语法", "explanation")
        ]
        
        for prompt, context in test_cases:
            print(f"\n测试: {prompt} (上下文: {context})")
            result = ai_service.generate_response(prompt, context)
            
            if result['success']:
                print(f"响应: {result['response']}")
                print(f"生成时间: {result['generation_time']:.2f}秒")
            else:
                print(f"失败: {result['error']}")
        
        # 测试专用方法
        print("\n测试单词提示:")
        word_hint = ai_service.generate_word_hint("beautiful")
        if word_hint['success']:
            print(f"单词提示: {word_hint['response']}")
        
        print("\n测试每日问候:")
        greeting = ai_service.generate_daily_greeting("morning")
        if greeting['success']:
            print(f"问候语: {greeting['response']}")
        
        # 显示服务状态
        print("\n服务状态:")
        status = ai_service.get_service_status()
        print(f"模型: {status['model_name']}")
        print(f"设备: {status['device']}")
        print(f"总请求: {status['stats']['total_requests']}")
        print(f"成功请求: {status['stats']['successful_requests']}")
        print(f"平均响应时间: {status['stats']['average_response_time']:.2f}秒")
        print(f"内存使用: {status['stats']['memory_usage_mb']:.1f}MB")
        
        print("✅ 本地AI服务测试通过")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")


if __name__ == "__main__":
    test_local_ai_service()