"""
服务降级管理器

在高负载或服务异常时自动调整服务质量
"""

import time
import threading
import logging
from typing import Dict, Optional, List, Callable, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ServiceLevel(Enum):
    """服务级别"""
    NORMAL = "normal"      # 正常服务
    DEGRADED = "degraded"  # 降级服务
    MINIMAL = "minimal"    # 最小服务
    DISABLED = "disabled"  # 服务停用


@dataclass
class DegradationMetrics:
    """降级指标"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    response_time: float = 0.0
    error_rate: float = 0.0
    active_requests: int = 0
    queue_size: int = 0


@dataclass
class DegradationThresholds:
    """降级阈值配置"""
    # 降级阈值
    degraded_cpu_threshold: float = 80.0  # CPU使用率 %
    degraded_memory_threshold: float = 85.0  # 内存使用率 %
    degraded_response_time: float = 5.0  # 响应时间 秒
    degraded_error_rate: float = 0.1  # 错误率 10%
    degraded_queue_size: int = 100  # 队列大小
    
    # 最小服务阈值
    minimal_cpu_threshold: float = 95.0
    minimal_memory_threshold: float = 95.0
    minimal_response_time: float = 10.0
    minimal_error_rate: float = 0.3  # 30%
    minimal_queue_size: int = 500
    
    # 服务停用阈值
    disabled_cpu_threshold: float = 98.0
    disabled_memory_threshold: float = 98.0
    disabled_error_rate: float = 0.8  # 80%
    disabled_queue_size: int = 1000


class DegradationManager:
    """
    服务降级管理器
    
    监控系统指标，自动调整服务级别
    """
    
    def __init__(self, thresholds: Optional[DegradationThresholds] = None):
        """初始化降级管理器"""
        self.thresholds = thresholds or DegradationThresholds()
        self._current_level = ServiceLevel.NORMAL
        self._forced_level: Optional[ServiceLevel] = None
        self._metrics = DegradationMetrics()
        self._lock = threading.Lock()
        
        # 监控状态
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # 回调函数
        self._on_level_change: List[Callable[[ServiceLevel, ServiceLevel], None]] = []
        
        # 历史记录
        self._level_history: List[Tuple[datetime, ServiceLevel]] = []
        self._metrics_history: List[Tuple[datetime, DegradationMetrics]] = []
        self._max_history_size = 1000
        
        # 启动监控
        self.start_monitoring()
    
    def start_monitoring(self):
        """启动降级监控"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("服务降级监控已启动")
    
    def stop_monitoring(self):
        """停止降级监控"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("服务降级监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self._monitoring:
            try:
                # 收集系统指标
                self._collect_metrics()
                
                # 评估服务级别
                new_level = self._evaluate_service_level()
                
                # 更新服务级别
                if new_level != self._current_level:
                    self._update_service_level(new_level)
                
                time.sleep(10)  # 每10秒检查一次
                
            except Exception as e:
                logger.error(f"降级监控异常: {e}")
                time.sleep(30)
    
    def _collect_metrics(self):
        """收集系统指标"""
        try:
            import psutil
            
            with self._lock:
                # 收集系统指标
                self._metrics.cpu_usage = psutil.cpu_percent(interval=1)
                self._metrics.memory_usage = psutil.virtual_memory().percent
                
                # TODO: 从服务管理器获取AI服务指标
                # self._metrics.response_time = ai_service_manager.get_avg_response_time()
                # self._metrics.error_rate = ai_service_manager.get_error_rate()
                # self._metrics.active_requests = ai_service_manager.get_active_requests()
                # self._metrics.queue_size = ai_service_manager.get_queue_size()
                
                # 记录指标历史
                self._record_metrics_history()
                
        except ImportError:
            # 如果psutil不可用，使用模拟数据
            logger.warning("psutil不可用，使用模拟指标")
            with self._lock:
                self._metrics.cpu_usage = 20.0  # 模拟正常CPU使用率
                self._metrics.memory_usage = 30.0  # 模拟正常内存使用率
        except Exception as e:
            logger.error(f"收集系统指标失败: {e}")
    
    def _record_metrics_history(self):
        """记录指标历史"""
        # 创建指标副本
        metrics_copy = DegradationMetrics(
            cpu_usage=self._metrics.cpu_usage,
            memory_usage=self._metrics.memory_usage,
            response_time=self._metrics.response_time,
            error_rate=self._metrics.error_rate,
            active_requests=self._metrics.active_requests,
            queue_size=self._metrics.queue_size
        )
        
        self._metrics_history.append((datetime.now(), metrics_copy))
        
        # 限制历史记录大小
        if len(self._metrics_history) > self._max_history_size:
            self._metrics_history.pop(0)
    
    def _evaluate_service_level(self) -> ServiceLevel:
        """评估服务级别"""
        # 如果有强制设置，优先使用
        if self._forced_level:
            return self._forced_level
        
        metrics = self._metrics
        thresholds = self.thresholds
        
        # 检查是否需要停用服务
        if (metrics.cpu_usage >= thresholds.disabled_cpu_threshold or
            metrics.memory_usage >= thresholds.disabled_memory_threshold or
            metrics.error_rate >= thresholds.disabled_error_rate or
            metrics.queue_size >= thresholds.disabled_queue_size):
            return ServiceLevel.DISABLED
        
        # 检查是否需要最小服务
        if (metrics.cpu_usage >= thresholds.minimal_cpu_threshold or
            metrics.memory_usage >= thresholds.minimal_memory_threshold or
            metrics.response_time >= thresholds.minimal_response_time or
            metrics.error_rate >= thresholds.minimal_error_rate or
            metrics.queue_size >= thresholds.minimal_queue_size):
            return ServiceLevel.MINIMAL
        
        # 检查是否需要降级服务
        if (metrics.cpu_usage >= thresholds.degraded_cpu_threshold or
            metrics.memory_usage >= thresholds.degraded_memory_threshold or
            metrics.response_time >= thresholds.degraded_response_time or
            metrics.error_rate >= thresholds.degraded_error_rate or
            metrics.queue_size >= thresholds.degraded_queue_size):
            return ServiceLevel.DEGRADED
        
        # 正常服务
        return ServiceLevel.NORMAL
    
    def _update_service_level(self, new_level: ServiceLevel):
        """更新服务级别"""
        with self._lock:
            old_level = self._current_level
            self._current_level = new_level
            
            # 记录级别变化历史
            self._level_history.append((datetime.now(), new_level))
            if len(self._level_history) > self._max_history_size:
                self._level_history.pop(0)
            
            logger.warning(f"服务级别变化: {old_level.value} -> {new_level.value}")
            
            # 触发回调
            self._trigger_level_change_callbacks(old_level, new_level)
    
    def get_current_level(self) -> ServiceLevel:
        """获取当前服务级别"""
        with self._lock:
            return self._current_level
    
    def get_metrics(self) -> Dict[str, any]:
        """获取当前指标"""
        with self._lock:
            return {
                'cpu_usage': round(self._metrics.cpu_usage, 2),
                'memory_usage': round(self._metrics.memory_usage, 2),
                'response_time': round(self._metrics.response_time, 3),
                'error_rate': round(self._metrics.error_rate, 3),
                'active_requests': self._metrics.active_requests,
                'queue_size': self._metrics.queue_size,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_thresholds(self) -> Dict[str, any]:
        """获取降级阈值配置"""
        return {
            'degraded': {
                'cpu_threshold': self.thresholds.degraded_cpu_threshold,
                'memory_threshold': self.thresholds.degraded_memory_threshold,
                'response_time': self.thresholds.degraded_response_time,
                'error_rate': self.thresholds.degraded_error_rate,
                'queue_size': self.thresholds.degraded_queue_size
            },
            'minimal': {
                'cpu_threshold': self.thresholds.minimal_cpu_threshold,
                'memory_threshold': self.thresholds.minimal_memory_threshold,
                'response_time': self.thresholds.minimal_response_time,
                'error_rate': self.thresholds.minimal_error_rate,
                'queue_size': self.thresholds.minimal_queue_size
            },
            'disabled': {
                'cpu_threshold': self.thresholds.disabled_cpu_threshold,
                'memory_threshold': self.thresholds.disabled_memory_threshold,
                'error_rate': self.thresholds.disabled_error_rate,
                'queue_size': self.thresholds.disabled_queue_size
            }
        }
    
    def force_degradation(self, level: ServiceLevel):
        """强制设置降级级别"""
        with self._lock:
            old_level = self._current_level
            self._forced_level = level
            self._current_level = level
            
            logger.warning(f"强制设置服务级别: {level.value}")
            
            # 触发回调
            self._trigger_level_change_callbacks(old_level, level)
    
    def clear_degradation(self):
        """清除强制降级设置"""
        with self._lock:
            self._forced_level = None
            logger.info("清除强制降级设置")
    
    def update_thresholds(self, **kwargs):
        """更新降级阈值"""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self.thresholds, key):
                    setattr(self.thresholds, key, value)
                    logger.info(f"更新降级阈值 {key}: {value}")
    
    def get_level_history(self, hours: int = 24) -> List[Tuple[datetime, ServiceLevel]]:
        """获取服务级别历史"""
        with self._lock:
            if not hours:
                return self._level_history.copy()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            return [
                (timestamp, level) for timestamp, level in self._level_history
                if timestamp > cutoff_time
            ]
    
    def get_metrics_history(self, hours: int = 24) -> List[Tuple[datetime, DegradationMetrics]]:
        """获取指标历史"""
        with self._lock:
            if not hours:
                return self._metrics_history.copy()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            return [
                (timestamp, metrics) for timestamp, metrics in self._metrics_history
                if timestamp > cutoff_time
            ]
    
    def register_level_change_callback(self, callback: Callable[[ServiceLevel, ServiceLevel], None]):
        """注册服务级别变化回调"""
        self._on_level_change.append(callback)
    
    def _trigger_level_change_callbacks(self, old_level: ServiceLevel, new_level: ServiceLevel):
        """触发服务级别变化回调"""
        for callback in self._on_level_change:
            try:
                callback(old_level, new_level)
            except Exception as e:
                logger.error(f"服务级别变化回调异常: {e}")
    
    def get_degradation_recommendations(self) -> List[str]:
        """获取降级建议"""
        recommendations = []
        metrics = self._metrics
        thresholds = self.thresholds
        
        if metrics.cpu_usage >= thresholds.degraded_cpu_threshold:
            recommendations.append(f"CPU使用率过高 ({metrics.cpu_usage:.1f}%)，建议减少并发请求")
        
        if metrics.memory_usage >= thresholds.degraded_memory_threshold:
            recommendations.append(f"内存使用率过高 ({metrics.memory_usage:.1f}%)，建议减少缓存大小")
        
        if metrics.response_time >= thresholds.degraded_response_time:
            recommendations.append(f"响应时间过长 ({metrics.response_time:.1f}s)，建议使用更快的模型")
        
        if metrics.error_rate >= thresholds.degraded_error_rate:
            recommendations.append(f"错误率过高 ({metrics.error_rate:.1%})，建议检查服务配置")
        
        if metrics.queue_size >= thresholds.degraded_queue_size:
            recommendations.append(f"请求队列过长 ({metrics.queue_size})，建议增加服务实例")
        
        return recommendations
    
    def simulate_load(self, duration_seconds: int = 60):
        """模拟高负载场景（用于测试）"""
        logger.info(f"模拟高负载场景 {duration_seconds} 秒")
        
        original_metrics = DegradationMetrics(
            cpu_usage=self._metrics.cpu_usage,
            memory_usage=self._metrics.memory_usage,
            response_time=self._metrics.response_time,
            error_rate=self._metrics.error_rate,
            active_requests=self._metrics.active_requests,
            queue_size=self._metrics.queue_size
        )
        
        # 模拟高负载指标
        with self._lock:
            self._metrics.cpu_usage = 90.0
            self._metrics.memory_usage = 88.0
            self._metrics.response_time = 8.0
            self._metrics.error_rate = 0.15
            self._metrics.active_requests = 150
            self._metrics.queue_size = 200
        
        def restore_metrics():
            time.sleep(duration_seconds)
            with self._lock:
                self._metrics = original_metrics
            logger.info("高负载模拟结束，指标已恢复")
        
        # 在后台恢复指标
        threading.Thread(target=restore_metrics, daemon=True).start()
    
    def get_status_summary(self) -> Dict[str, any]:
        """获取降级状态摘要"""
        with self._lock:
            return {
                'current_level': self._current_level.value,
                'forced_level': self._forced_level.value if self._forced_level else None,
                'metrics': {
                    'cpu_usage': round(self._metrics.cpu_usage, 2),
                    'memory_usage': round(self._metrics.memory_usage, 2),
                    'response_time': round(self._metrics.response_time, 3),
                    'error_rate': round(self._metrics.error_rate, 3),
                    'active_requests': self._metrics.active_requests,
                    'queue_size': self._metrics.queue_size
                },
                'recommendations': self.get_degradation_recommendations(),
                'last_check': datetime.now().isoformat()
            }
