"""
📊 Chronicle联邦性能监控器 (Chronicle Federation Performance Monitor)
====================================================================

监控RAG系统与Chronicle联邦的性能指标
- API响应时间监控
- 内存使用监控
- 故障处理性能
- 网络延迟统计

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Chronicle Federation Performance"
"""

import time
import psutil
import asyncio
import statistics
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
import json

from utils.logger import logger

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    timestamp: datetime = field(default_factory=datetime.now)
    api_response_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    network_latency_ms: float = 0.0
    success_rate: float = 1.0
    error_count: int = 0

@dataclass
class PerformanceThresholds:
    """性能阈值配置"""
    max_api_response_time: float = 5.0  # 5秒
    max_memory_usage_mb: float = 500.0  # 500MB
    max_cpu_usage_percent: float = 80.0  # 80%
    max_network_latency_ms: float = 100.0  # 100ms
    min_success_rate: float = 0.95  # 95%

class ChroniclePerformanceMonitor:
    """Chronicle联邦性能监控器"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.thresholds = PerformanceThresholds()
        self.start_time = datetime.now()
        self.total_requests = 0
        self.failed_requests = 0
        self.api_times: deque = deque(maxlen=100)
        self.network_latencies: deque = deque(maxlen=100)
        
        logger.info("📊 Chronicle联邦性能监控器已启动")
    
    def record_api_call(self, response_time: float, success: bool = True):
        """记录API调用性能"""
        self.total_requests += 1
        self.api_times.append(response_time)
        
        if not success:
            self.failed_requests += 1
        
        # 检查性能阈值
        if response_time > self.thresholds.max_api_response_time:
            logger.warning(f"⚠️ API响应时间超阈值: {response_time:.2f}s > {self.thresholds.max_api_response_time}s")
    
    def record_network_latency(self, latency_ms: float):
        """记录网络延迟"""
        self.network_latencies.append(latency_ms)
        
        if latency_ms > self.thresholds.max_network_latency_ms:
            logger.warning(f"⚠️ 网络延迟超阈值: {latency_ms:.2f}ms > {self.thresholds.max_network_latency_ms}ms")
    
    def collect_system_metrics(self) -> PerformanceMetrics:
        """收集系统性能指标"""
        try:
            # 获取当前进程信息
            process = psutil.Process()
            
            # 内存使用
            memory_info = process.memory_info()
            memory_usage_mb = memory_info.rss / 1024 / 1024
            
            # CPU使用率
            cpu_usage = process.cpu_percent()
            
            # API响应时间统计
            avg_api_time = statistics.mean(self.api_times) if self.api_times else 0.0
            
            # 网络延迟统计
            avg_network_latency = statistics.mean(self.network_latencies) if self.network_latencies else 0.0
            
            # 成功率计算
            success_rate = (self.total_requests - self.failed_requests) / max(self.total_requests, 1)
            
            metrics = PerformanceMetrics(
                api_response_time=avg_api_time,
                memory_usage_mb=memory_usage_mb,
                cpu_usage_percent=cpu_usage,
                network_latency_ms=avg_network_latency,
                success_rate=success_rate,
                error_count=self.failed_requests
            )
            
            # 添加到历史记录
            self.metrics_history.append(metrics)
            
            # 检查阈值
            self._check_thresholds(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ 收集系统指标失败: {e}")
            return PerformanceMetrics()
    
    def _check_thresholds(self, metrics: PerformanceMetrics):
        """检查性能阈值"""
        warnings = []
        
        if metrics.memory_usage_mb > self.thresholds.max_memory_usage_mb:
            warnings.append(f"内存使用超阈值: {metrics.memory_usage_mb:.1f}MB")
        
        if metrics.cpu_usage_percent > self.thresholds.max_cpu_usage_percent:
            warnings.append(f"CPU使用超阈值: {metrics.cpu_usage_percent:.1f}%")
        
        if metrics.success_rate < self.thresholds.min_success_rate:
            warnings.append(f"成功率低于阈值: {metrics.success_rate:.1%}")
        
        for warning in warnings:
            logger.warning(f"⚠️ {warning}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.metrics_history:
            return {"status": "no_data", "message": "暂无性能数据"}
        
        recent_metrics = list(self.metrics_history)[-10:]  # 最近10个指标
        
        # 计算统计信息
        avg_api_time = statistics.mean([m.api_response_time for m in recent_metrics])
        avg_memory = statistics.mean([m.memory_usage_mb for m in recent_metrics])
        avg_cpu = statistics.mean([m.cpu_usage_percent for m in recent_metrics])
        avg_latency = statistics.mean([m.network_latency_ms for m in recent_metrics])
        current_success_rate = recent_metrics[-1].success_rate if recent_metrics else 0
        
        # 运行时间
        uptime = datetime.now() - self.start_time
        
        return {
            "status": "operational",
            "uptime_seconds": uptime.total_seconds(),
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "success_rate": current_success_rate,
            "performance": {
                "avg_api_response_time": avg_api_time,
                "avg_memory_usage_mb": avg_memory,
                "avg_cpu_usage_percent": avg_cpu,
                "avg_network_latency_ms": avg_latency
            },
            "thresholds": {
                "api_response_time": self.thresholds.max_api_response_time,
                "memory_usage_mb": self.thresholds.max_memory_usage_mb,
                "cpu_usage_percent": self.thresholds.max_cpu_usage_percent,
                "network_latency_ms": self.thresholds.max_network_latency_ms,
                "min_success_rate": self.thresholds.min_success_rate
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def get_performance_trends(self, minutes: int = 60) -> Dict[str, List[float]]:
        """获取性能趋势数据"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {"message": f"过去{minutes}分钟内无数据"}
        
        return {
            "timestamps": [m.timestamp.isoformat() for m in recent_metrics],
            "api_response_times": [m.api_response_time for m in recent_metrics],
            "memory_usage": [m.memory_usage_mb for m in recent_metrics],
            "cpu_usage": [m.cpu_usage_percent for m in recent_metrics],
            "network_latency": [m.network_latency_ms for m in recent_metrics],
            "success_rates": [m.success_rate for m in recent_metrics]
        }
    
    def export_metrics(self, filepath: str):
        """导出性能指标到文件"""
        try:
            metrics_data = {
                "export_time": datetime.now().isoformat(),
                "summary": self.get_performance_summary(),
                "trends": self.get_performance_trends(minutes=1440),  # 24小时
                "raw_metrics": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "api_response_time": m.api_response_time,
                        "memory_usage_mb": m.memory_usage_mb,
                        "cpu_usage_percent": m.cpu_usage_percent,
                        "network_latency_ms": m.network_latency_ms,
                        "success_rate": m.success_rate,
                        "error_count": m.error_count
                    }
                    for m in self.metrics_history
                ]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 性能指标已导出到: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ 导出性能指标失败: {e}")
    
    async def start_monitoring(self, interval_seconds: int = 30):
        """启动持续监控"""
        logger.info(f"🔄 开始持续性能监控，间隔: {interval_seconds}秒")
        
        try:
            while True:
                metrics = self.collect_system_metrics()
                logger.debug(f"📊 性能指标: 内存={metrics.memory_usage_mb:.1f}MB, "
                           f"CPU={metrics.cpu_usage_percent:.1f}%, "
                           f"API={metrics.api_response_time:.2f}s")
                
                await asyncio.sleep(interval_seconds)
                
        except asyncio.CancelledError:
            logger.info("⏹️ 性能监控已停止")
        except Exception as e:
            logger.error(f"❌ 性能监控异常: {e}")

# 全局性能监控器实例
_performance_monitor = None

def get_performance_monitor() -> ChroniclePerformanceMonitor:
    """获取性能监控器单例"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = ChroniclePerformanceMonitor()
    return _performance_monitor

# 性能监控装饰器
def monitor_performance(func):
    """性能监控装饰器"""
    import functools
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        monitor = get_performance_monitor()
        start_time = time.time()
        success = True
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            raise
        finally:
            end_time = time.time()
            response_time = end_time - start_time
            monitor.record_api_call(response_time, success)
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        monitor = get_performance_monitor()
        start_time = time.time()
        success = True
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            raise
        finally:
            end_time = time.time()
            response_time = end_time - start_time
            monitor.record_api_call(response_time, success)
    
    # 根据函数类型返回相应的包装器
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

# 便捷函数
def log_performance_summary():
    """记录性能摘要"""
    monitor = get_performance_monitor()
    summary = monitor.get_performance_summary()
    
    logger.info("📊 Chronicle联邦性能摘要:")
    logger.info(f"   运行时间: {summary.get('uptime_seconds', 0):.0f}秒")
    logger.info(f"   总请求数: {summary.get('total_requests', 0)}")
    logger.info(f"   成功率: {summary.get('success_rate', 0):.1%}")
    
    perf = summary.get('performance', {})
    logger.info(f"   平均API响应: {perf.get('avg_api_response_time', 0):.2f}s")
    logger.info(f"   平均内存使用: {perf.get('avg_memory_usage_mb', 0):.1f}MB")
    logger.info(f"   平均CPU使用: {perf.get('avg_cpu_usage_percent', 0):.1f}%")

logger.info("📊 Chronicle联邦性能监控器已加载")