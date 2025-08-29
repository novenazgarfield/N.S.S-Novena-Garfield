"""
🔗 Chronicle联邦治疗装饰器 (Chronicle Federation Healing Decorator)
================================================================

替换原来的@ai_self_healing装饰器，现在RAG系统会向Chronicle中央医院求救
- 保留RAG的"学术大脑"（智能分块和知识图谱）
- 将"工程大脑"（故障记录和自我修复）委托给Chronicle
- 建立RAG与Chronicle之间的"神经连接"

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Chronicle Genesis Federation"
"""

import functools
import asyncio
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime
import inspect

from utils.logger import logger
from core.chronicle_client import (
    get_chronicle_client, 
    chronicle_log_failure, 
    chronicle_request_healing,
    SystemSource, 
    FailureSeverity,
    ChronicleConfig
)

class ChronicleHealingConfig:
    """Chronicle联邦治疗配置"""
    
    def __init__(self,
                 chronicle_url: str = "http://localhost:3000",
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 enable_fallback: bool = True,
                 log_healing_process: bool = True,
                 default_source: SystemSource = SystemSource.RAG_SYSTEM):
        self.chronicle_url = chronicle_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enable_fallback = enable_fallback
        self.log_healing_process = log_healing_process
        self.default_source = default_source
        
        # 初始化Chronicle客户端
        chronicle_config = ChronicleConfig(
            base_url=chronicle_url,
            timeout=30,
            retry_attempts=max_retries,
            retry_delay=retry_delay,
            enable_fallback=enable_fallback
        )
        self.client = get_chronicle_client(chronicle_config)

# 全局配置
_global_config = ChronicleHealingConfig()

def configure_chronicle_healing(**kwargs):
    """配置Chronicle联邦治疗系统"""
    global _global_config
    _global_config = ChronicleHealingConfig(**kwargs)
    logger.info("🔗 Chronicle联邦治疗系统已配置")

def chronicle_self_healing(source: SystemSource = None,
                         severity: FailureSeverity = FailureSeverity.MEDIUM,
                         max_retries: int = None,
                         healing_strategy: str = None,
                         enable_transparency: bool = True):
    """
    🏥 Chronicle联邦自我修复装饰器
    
    替换原来的@ai_self_healing，现在会：
    1. 捕获错误
    2. 向Chronicle中央医院报告故障
    3. 请求治疗方案
    4. 根据治疗方案执行修复
    5. 如果Chronicle不可用，使用降级处理
    
    Args:
        source: 系统来源
        severity: 故障严重程度
        max_retries: 最大重试次数
        healing_strategy: 首选治疗策略
        enable_transparency: 启用透明化记录
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            config = _global_config
            retries = max_retries or config.max_retries
            func_source = source or config.default_source
            
            last_error = None
            attempt = 0
            
            # 首先检查Chronicle是否在线
            chronicle_online = await config.client.health_check()
            if not chronicle_online and config.log_healing_process:
                logger.warning("⚠️ Chronicle中央医院离线，将使用降级处理")
            
            while attempt <= retries:
                try:
                    # 透明化记录
                    if enable_transparency and config.log_healing_process:
                        logger.info(f"🔍 执行 {func.__name__} (尝试 {attempt + 1}/{retries + 1})")
                    
                    # 执行原始函数
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    # 成功执行
                    if attempt > 0 and config.log_healing_process:
                        logger.info(f"✅ Chronicle联邦治疗成功: {func.__name__} (尝试 {attempt + 1})")
                    
                    return result
                    
                except Exception as error:
                    last_error = error
                    attempt += 1
                    
                    if config.log_healing_process:
                        logger.warning(f"🚨 {func.__name__} 发生故障: {error}")
                    
                    # 向Chronicle报告故障
                    failure_data = None
                    if chronicle_online:
                        try:
                            failure_data = await chronicle_log_failure(
                                source=func_source,
                                function_name=func.__name__,
                                error=error,
                                context={
                                    'attempt': attempt,
                                    'max_retries': retries,
                                    'args_count': len(args),
                                    'kwargs_keys': list(kwargs.keys()) if kwargs else []
                                },
                                severity=severity
                            )
                        except Exception as chronicle_error:
                            logger.error(f"❌ 向Chronicle报告故障失败: {chronicle_error}")
                    
                    # 如果还有重试机会，请求治疗方案
                    if attempt <= retries:
                        healing_response = None
                        
                        if chronicle_online and failure_data:
                            try:
                                healing_response = await chronicle_request_healing(
                                    source=func_source,
                                    function_name=func.__name__,
                                    error=error,
                                    context={
                                        'attempt': attempt,
                                        'failure_id': failure_data.get('failure_id')
                                    },
                                    healing_strategy=healing_strategy
                                )
                            except Exception as healing_error:
                                logger.error(f"❌ 向Chronicle请求治疗失败: {healing_error}")
                        
                        # 执行治疗方案
                        if healing_response:
                            await _execute_chronicle_healing_plan(healing_response, error, attempt)
                        else:
                            # 降级处理：简单延迟重试
                            if config.enable_fallback:
                                await _execute_fallback_healing(error, attempt, config.retry_delay)
                            else:
                                logger.error(f"❌ 无法获取治疗方案，跳过重试")
                                break
            
            # 所有重试都失败了
            if config.log_healing_process:
                logger.error(f"💀 Chronicle联邦治疗失败: {func.__name__} - 已尝试 {retries + 1} 次")
            
            raise last_error
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 对于同步函数，创建事件循环来处理异步操作
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(async_wrapper(*args, **kwargs))
        
        # 根据函数类型返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

async def _execute_chronicle_healing_plan(healing_response, original_error, attempt):
    """执行Chronicle治疗方案"""
    strategy = healing_response.strategy
    
    if _global_config.log_healing_process:
        logger.info(f"🏥 执行Chronicle治疗方案: {strategy}")
        for recommendation in healing_response.recommendations:
            logger.info(f"   💡 {recommendation}")
    
    if strategy == "retry_simple":
        # 简单重试，等待一段时间
        delay = _global_config.retry_delay * attempt
        await asyncio.sleep(delay)
        
    elif strategy == "ai_analyze_fix":
        # AI分析修复，等待更长时间让AI分析
        delay = _global_config.retry_delay * 2 * attempt
        await asyncio.sleep(delay)
        
    elif strategy == "fallback_mode":
        # 降级模式，短暂等待
        delay = _global_config.retry_delay * 0.5
        await asyncio.sleep(delay)
        
    elif strategy == "emergency_stop":
        # 紧急停止，不再重试
        logger.error("🚨 Chronicle建议紧急停止，终止重试")
        raise original_error
        
    elif strategy == "immune_response":
        # 免疫响应，跳过此次错误
        logger.info("🛡️ Chronicle免疫系统激活，跳过此类故障")
        return
        
    else:
        # 未知策略，使用默认延迟
        await asyncio.sleep(_global_config.retry_delay * attempt)

async def _execute_fallback_healing(error, attempt, base_delay):
    """执行降级治疗方案"""
    logger.info(f"🛡️ 执行降级治疗方案 (尝试 {attempt})")
    
    # 简单的指数退避
    delay = base_delay * (2 ** (attempt - 1))
    await asyncio.sleep(min(delay, 30))  # 最大延迟30秒

# 便捷的装饰器别名，保持与原来的API兼容
ai_self_healing = chronicle_self_healing

# 系统特定的装饰器
def rag_self_healing(**kwargs):
    """RAG系统专用的自我修复装饰器"""
    return chronicle_self_healing(source=SystemSource.RAG_SYSTEM, **kwargs)

def trinity_self_healing(**kwargs):
    """Trinity分块器专用的自我修复装饰器"""
    return chronicle_self_healing(source=SystemSource.TRINITY_CHUNKER, **kwargs)

def memory_nebula_self_healing(**kwargs):
    """记忆星图专用的自我修复装饰器"""
    return chronicle_self_healing(source=SystemSource.MEMORY_NEBULA, **kwargs)

def shields_self_healing(**kwargs):
    """秩序之盾专用的自我修复装饰器"""
    return chronicle_self_healing(source=SystemSource.SHIELDS_OF_ORDER, **kwargs)

def fire_control_self_healing(**kwargs):
    """火控系统专用的自我修复装饰器"""
    return chronicle_self_healing(source=SystemSource.FIRE_CONTROL, **kwargs)

def intelligence_brain_self_healing(**kwargs):
    """中央情报大脑专用的自我修复装饰器"""
    return chronicle_self_healing(source=SystemSource.INTELLIGENCE_BRAIN, **kwargs)

# 健康检查函数
async def check_chronicle_federation_health():
    """检查Chronicle联邦健康状态"""
    client = get_chronicle_client()
    
    try:
        # 检查Chronicle连接
        chronicle_online = await client.health_check()
        
        # 获取健康报告
        health_report = None
        if chronicle_online:
            health_report = await client.get_health_report(source="rag_system")
        
        return {
            "chronicle_online": chronicle_online,
            "connection_status": client.connection_status.value,
            "last_health_check": client.last_health_check,
            "health_report": health_report,
            "federation_status": "connected" if chronicle_online else "disconnected"
        }
        
    except Exception as e:
        logger.error(f"❌ Chronicle联邦健康检查失败: {e}")
        return {
            "chronicle_online": False,
            "connection_status": "error",
            "error": str(e),
            "federation_status": "error"
        }

# 初始化日志
logger.info("🔗 Chronicle联邦治疗系统已加载 - RAG系统现在可以向中央医院求救")