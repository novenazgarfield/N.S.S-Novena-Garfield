"""
🔗 Chronicle中央医院客户端 (Chronicle Central Hospital Client)
===========================================================

RAG系统的"神经连接" - 向Chronicle中央医院求救的接口
- 故障记录接口 (log_failure)
- 治疗请求接口 (request_healing)
- 健康检查接口 (health_check)
- 免疫状态查询 (immunity_check)

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Chronicle Genesis Federation"
"""

import requests
import json
import time
import traceback
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

from utils.logger import logger

class ChronicleConnectionStatus(Enum):
    """Chronicle连接状态"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    TIMEOUT = "timeout"

class SystemSource(Enum):
    """系统来源"""
    RAG_SYSTEM = "rag_system"
    TRINITY_CHUNKER = "trinity_chunker"
    MEMORY_NEBULA = "memory_nebula"
    SHIELDS_OF_ORDER = "shields_of_order"
    FIRE_CONTROL = "fire_control"
    INTELLIGENCE_BRAIN = "intelligence_brain"

class FailureSeverity(Enum):
    """故障严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ChronicleConfig:
    """Chronicle客户端配置"""
    base_url: str = "http://localhost:3000"
    api_key: Optional[str] = None
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    enable_fallback: bool = True
    fallback_log_file: str = "chronicle_fallback.log"

@dataclass
class FailureReport:
    """故障报告"""
    source: SystemSource
    function_name: str
    error_type: str
    error_message: str
    stack_trace: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    severity: FailureSeverity = FailureSeverity.MEDIUM
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class HealingResponse:
    """治疗响应"""
    success: bool
    strategy: str
    message: str
    recommendations: List[str] = field(default_factory=list)
    estimated_success_rate: float = 0.0
    failure_id: Optional[int] = None

class ChronicleClient:
    """Chronicle中央医院客户端"""
    
    def __init__(self, config: ChronicleConfig = None):
        self.config = config or ChronicleConfig()
        self.session = requests.Session()
        self.connection_status = ChronicleConnectionStatus.DISCONNECTED
        self.last_health_check = None
        self.fallback_logger = None
        
        # 设置请求头
        if self.config.api_key:
            self.session.headers.update({
                'X-API-Key': self.config.api_key,
                'Authorization': f'Bearer {self.config.api_key}'
            })
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'RAG-System-Chronicle-Client/2.0.0'
        })
        
        # 初始化降级日志
        if self.config.enable_fallback:
            self._setup_fallback_logging()
        
        logger.info("🔗 Chronicle中央医院客户端已初始化")
    
    def _setup_fallback_logging(self):
        """设置降级日志"""
        try:
            self.fallback_logger = logging.getLogger('chronicle_fallback')
            handler = logging.FileHandler(self.config.fallback_log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.fallback_logger.addHandler(handler)
            self.fallback_logger.setLevel(logging.INFO)
        except Exception as e:
            logger.warning(f"⚠️ 无法设置降级日志: {e}")
    
    async def health_check(self) -> bool:
        """🏥 健康检查 - 检查Chronicle中央医院是否在线"""
        try:
            response = self.session.get(
                f"{self.config.base_url}/health",
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                self.connection_status = ChronicleConnectionStatus.CONNECTED
                self.last_health_check = datetime.now()
                logger.info("🏥 Chronicle中央医院在线")
                return True
            else:
                self.connection_status = ChronicleConnectionStatus.ERROR
                logger.warning(f"⚠️ Chronicle健康检查失败: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            self.connection_status = ChronicleConnectionStatus.TIMEOUT
            logger.warning("⏰ Chronicle健康检查超时")
            return False
        except Exception as e:
            self.connection_status = ChronicleConnectionStatus.ERROR
            logger.error(f"❌ Chronicle健康检查异常: {e}")
            return False
    
    async def log_failure(self, failure_report: FailureReport) -> Optional[Dict[str, Any]]:
        """🚨 记录故障 - 向Chronicle中央医院求救"""
        try:
            # 准备请求数据
            payload = {
                "source": failure_report.source.value,
                "function_name": failure_report.function_name,
                "error_type": failure_report.error_type,
                "error_message": failure_report.error_message,
                "stack_trace": failure_report.stack_trace,
                "context": failure_report.context,
                "severity": failure_report.severity.value
            }
            
            # 发送求救信号
            response = await self._make_request_with_retry(
                'POST',
                '/api/log_failure',
                payload
            )
            
            if response and response.get('success'):
                logger.info(f"🚨 故障已报告给Chronicle: {failure_report.function_name}")
                return response.get('data')
            else:
                logger.error(f"❌ 故障报告失败: {response}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 向Chronicle报告故障时发生异常: {e}")
            
            # 降级处理：记录到本地文件
            if self.config.enable_fallback and self.fallback_logger:
                self._log_to_fallback(failure_report, "log_failure_failed", str(e))
            
            return None
    
    async def request_healing(self, 
                            failure_id: Optional[int] = None,
                            failure_report: Optional[FailureReport] = None,
                            healing_strategy: Optional[str] = None) -> Optional[HealingResponse]:
        """🏥 请求治疗 - 向Chronicle中央医院请求治疗方案"""
        try:
            payload = {}
            
            if failure_id:
                payload["failure_id"] = failure_id
                if healing_strategy:
                    payload["healing_strategy"] = healing_strategy
            elif failure_report:
                payload.update({
                    "source": failure_report.source.value,
                    "function_name": failure_report.function_name,
                    "error_type": failure_report.error_type,
                    "error_message": failure_report.error_message,
                    "context": failure_report.context
                })
                if healing_strategy:
                    payload["healing_strategy"] = healing_strategy
            else:
                logger.error("❌ 请求治疗需要提供failure_id或failure_report")
                return None
            
            # 请求治疗方案
            response = await self._make_request_with_retry(
                'POST',
                '/api/request_healing',
                payload
            )
            
            if response and response.get('success'):
                data = response.get('data', {})
                healing_plan = data.get('healing_plan', {})
                
                healing_response = HealingResponse(
                    success=True,
                    strategy=healing_plan.get('strategy', 'unknown'),
                    message=response.get('message', ''),
                    recommendations=data.get('recommendations', []),
                    estimated_success_rate=data.get('estimated_success_rate', 0.0),
                    failure_id=healing_plan.get('failure_id')
                )
                
                logger.info(f"🏥 收到Chronicle治疗方案: {healing_response.strategy}")
                return healing_response
            else:
                logger.error(f"❌ 治疗请求失败: {response}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 向Chronicle请求治疗时发生异常: {e}")
            
            # 降级处理：返回默认治疗方案
            if self.config.enable_fallback:
                return self._get_fallback_healing_response(failure_report or failure_id)
            
            return None
    
    async def check_immunity(self, immune_signature: str) -> bool:
        """🛡️ 检查免疫状态"""
        try:
            response = await self._make_request_with_retry(
                'GET',
                f'/api/immunity_status?immune_signature={immune_signature}'
            )
            
            if response and response.get('success'):
                data = response.get('data', {})
                is_immune = data.get('is_immune', False)
                logger.info(f"🛡️ 免疫检查结果: {immune_signature} -> {'已免疫' if is_immune else '易感'}")
                return is_immune
            else:
                logger.warning(f"⚠️ 免疫检查失败: {response}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 检查免疫状态时发生异常: {e}")
            return False
    
    async def get_health_report(self, source: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """📊 获取健康报告"""
        try:
            url = '/api/health_report'
            if source:
                url += f'?source={source}'
            
            response = await self._make_request_with_retry('GET', url)
            
            if response and response.get('success'):
                logger.info("📊 获取Chronicle健康报告成功")
                return response.get('data')
            else:
                logger.error(f"❌ 获取健康报告失败: {response}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 获取健康报告时发生异常: {e}")
            return None
    
    async def _make_request_with_retry(self, 
                                     method: str, 
                                     endpoint: str, 
                                     data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """带重试的请求"""
        url = f"{self.config.base_url}{endpoint}"
        
        for attempt in range(self.config.retry_attempts):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=self.config.timeout)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, timeout=self.config.timeout)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    logger.error(f"❌ Chronicle API端点不存在: {endpoint}")
                    return None
                else:
                    logger.warning(f"⚠️ Chronicle API返回错误状态: {response.status_code}")
                    if attempt < self.config.retry_attempts - 1:
                        time.sleep(self.config.retry_delay * (attempt + 1))
                        continue
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ Chronicle API请求超时 (尝试 {attempt + 1}/{self.config.retry_attempts})")
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                return None
            except Exception as e:
                logger.error(f"❌ Chronicle API请求异常: {e}")
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                return None
        
        return None
    
    def _get_fallback_healing_response(self, failure_info) -> HealingResponse:
        """获取降级治疗方案"""
        logger.info("🛡️ 使用降级治疗方案")
        
        return HealingResponse(
            success=True,
            strategy="fallback_mode",
            message="Chronicle不可用，使用本地降级治疗方案",
            recommendations=[
                "Chronicle中央医院暂时不可用",
                "使用本地错误处理机制",
                "建议稍后重试连接Chronicle"
            ],
            estimated_success_rate=0.6
        )
    
    def _log_to_fallback(self, failure_report: FailureReport, action: str, error: str):
        """记录到降级日志"""
        if self.fallback_logger:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "failure_report": {
                    "source": failure_report.source.value,
                    "function_name": failure_report.function_name,
                    "error_type": failure_report.error_type,
                    "error_message": failure_report.error_message,
                    "severity": failure_report.severity.value
                },
                "error": error
            }
            self.fallback_logger.info(json.dumps(log_entry))
    
    def close(self):
        """关闭客户端"""
        if self.session:
            self.session.close()
        logger.info("🔗 Chronicle客户端已关闭")

# 全局客户端实例
_chronicle_client = None

def get_chronicle_client(config: ChronicleConfig = None) -> ChronicleClient:
    """获取Chronicle客户端单例"""
    global _chronicle_client
    if _chronicle_client is None:
        _chronicle_client = ChronicleClient(config)
    return _chronicle_client

# 便捷函数

async def chronicle_log_failure(source: SystemSource,
                              function_name: str,
                              error: Exception,
                              context: Dict[str, Any] = None,
                              severity: FailureSeverity = FailureSeverity.MEDIUM) -> Optional[Dict[str, Any]]:
    """便捷的故障记录函数"""
    client = get_chronicle_client()
    
    failure_report = FailureReport(
        source=source,
        function_name=function_name,
        error_type=type(error).__name__,
        error_message=str(error),
        stack_trace=traceback.format_exc(),
        context=context or {},
        severity=severity
    )
    
    return await client.log_failure(failure_report)

async def chronicle_request_healing(source: SystemSource,
                                  function_name: str,
                                  error: Exception,
                                  context: Dict[str, Any] = None,
                                  healing_strategy: Optional[str] = None) -> Optional[HealingResponse]:
    """便捷的治疗请求函数"""
    client = get_chronicle_client()
    
    failure_report = FailureReport(
        source=source,
        function_name=function_name,
        error_type=type(error).__name__,
        error_message=str(error),
        stack_trace=traceback.format_exc(),
        context=context or {}
    )
    
    return await client.request_healing(failure_report=failure_report, healing_strategy=healing_strategy)

async def chronicle_health_check() -> bool:
    """便捷的健康检查函数"""
    client = get_chronicle_client()
    return await client.health_check()