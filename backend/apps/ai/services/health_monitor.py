"""
健康监控器

监控AI服务的健康状态，支持自动故障检测和恢复
"""

import time
import threading
import logging
from typing import Dict, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """服务健康信息"""
    service_name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    is_healthy: bool = True
    response_time: float = 0.0
    last_check: Optional[datetime] = None
    error: Optional[str] = None
    consecutive_failures: int = 0
    uptime_percentage: float = 100.0
    
    def update_from_check(self, success: bool, response_time: float, error: Optional[str] = None):
        """从健康检查结果更新状态"""
        self.last_check = datetime.now()
        self.response_time = response_time
        self.error = error
        
        if success:
            self.consecutive_failures = 0
            if response_time < 1.0:
                self.status = HealthStatus.HEALTHY
            elif response_time < 5.0:
                self.status = HealthStatus.DEGRADED
            else:
                self.status = HealthStatus.DEGRADED
            self.is_healthy = True
        else:
            self.consecutive_failures += 1
            self.status = HealthStatus.UNHEALTHY
            self.is_healthy = False


@dataclass
class HealthCheckConfig:
    """健康检查配置"""
    interval: int = 60  # 检查间隔（秒）
    timeout: float = 10.0  # 超时时间（秒）
    failure_threshold: int = 3  # 连续失败阈值
    recovery_threshold: int = 2  # 恢复阈值
    degraded_threshold: float = 2.0  # 降级响应时间阈值（秒）


class HealthMonitor:
    """
    健康监控器
    
    监控AI服务健康状态，提供故障检测和恢复功能
    """
    
    def __init__(self, config: Optional[HealthCheckConfig] = None):
        """初始化健康监控器"""
        self.config = config or HealthCheckConfig()
        self._health_data: Dict[str, ServiceHealth] = {}
        self._lock = threading.Lock()
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # 回调函数
        self._on_health_change: List[Callable[[str, ServiceHealth], None]] = []
        self._on_service_down: List[Callable[[str], None]] = []
        self._on_service_up: List[Callable[[str], None]] = []
        
        # 历史记录
        self._health_history: Dict[str, List[ServiceHealth]] = {}
        self._max_history_size = 1000
    
    def start_monitoring(self):
        """启动健康监控"""
        if self._monitoring:
            logger.warning("健康监控已在运行")
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("健康监控已启动")
    
    def stop_monitoring(self):
        """停止健康监控"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("健康监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self._monitoring:
            try:
                self._perform_health_checks()
                time.sleep(self.config.interval)
            except Exception as e:
                logger.error(f"健康监控异常: {e}")
                time.sleep(min(self.config.interval, 30))
    
    def _perform_health_checks(self):
        """执行健康检查"""
        # 这里应该调用各个服务的健康检查
        # 由于是在monitor中，我们不直接调用adapter
        # 而是由ServiceManager调用并更新结果
        pass
    
    def update_health(
        self,
        service_name: str,
        health_result: 'HealthCheckResult'
    ):
        """
        更新服务健康状态
        
        Args:
            service_name: 服务名称
            health_result: 健康检查结果
        """
        with self._lock:
            # 获取或创建健康信息
            if service_name not in self._health_data:
                self._health_data[service_name] = ServiceHealth(service_name=service_name)
            
            health = self._health_data[service_name]
            previous_status = health.status
            
            # 更新健康状态
            health.update_from_check(
                success=health_result.is_healthy,
                response_time=health_result.response_time,
                error=health_result.error
            )
            
            # 计算运行时间百分比
            self._update_uptime_percentage(service_name, health)
            
            # 记录历史
            self._record_health_history(service_name, health)
            
            # 触发回调
            if previous_status != health.status:
                self._trigger_health_change_callbacks(service_name, health)
                
                if previous_status == HealthStatus.UNHEALTHY and health.is_healthy:
                    self._trigger_service_up_callbacks(service_name)
                elif health.status == HealthStatus.UNHEALTHY and previous_status != HealthStatus.UNHEALTHY:
                    self._trigger_service_down_callbacks(service_name)
    
    def _update_uptime_percentage(self, service_name: str, health: ServiceHealth):
        """更新运行时间百分比"""
        # 简化实现：基于最近的健康检查历史
        history = self._health_history.get(service_name, [])
        if len(history) < 2:
            return
        
        # 计算最近24小时的运行时间
        now = datetime.now()
        day_ago = now - timedelta(hours=24)
        
        recent_checks = [h for h in history if h.last_check and h.last_check > day_ago]
        if recent_checks:
            healthy_checks = sum(1 for h in recent_checks if h.is_healthy)
            health.uptime_percentage = (healthy_checks / len(recent_checks)) * 100
    
    def _record_health_history(self, service_name: str, health: ServiceHealth):
        """记录健康历史"""
        if service_name not in self._health_history:
            self._health_history[service_name] = []
        
        # 复制当前健康状态
        history_entry = ServiceHealth(
            service_name=health.service_name,
            status=health.status,
            is_healthy=health.is_healthy,
            response_time=health.response_time,
            last_check=health.last_check,
            error=health.error,
            consecutive_failures=health.consecutive_failures,
            uptime_percentage=health.uptime_percentage
        )
        
        self._health_history[service_name].append(history_entry)
        
        # 限制历史记录大小
        if len(self._health_history[service_name]) > self._max_history_size:
            self._health_history[service_name].pop(0)
    
    def get_health(self, service_name: str) -> Optional[ServiceHealth]:
        """获取服务健康状态"""
        with self._lock:
            return self._health_data.get(service_name)
    
    def get_all_health(self) -> Dict[str, ServiceHealth]:
        """获取所有服务健康状态"""
        with self._lock:
            return self._health_data.copy()
    
    def is_service_healthy(self, service_name: str) -> bool:
        """检查服务是否健康"""
        health = self.get_health(service_name)
        return health.is_healthy if health else False
    
    def get_healthy_services(self, service_names: List[str]) -> List[str]:
        """获取健康的服务列表"""
        return [name for name in service_names if self.is_service_healthy(name)]
    
    def get_health_summary(self) -> Dict[str, any]:
        """获取健康状态摘要"""
        with self._lock:
            total_services = len(self._health_data)
            healthy_services = sum(1 for h in self._health_data.values() if h.is_healthy)
            
            avg_response_time = 0.0
            if self._health_data:
                avg_response_time = sum(h.response_time for h in self._health_data.values()) / total_services
            
            return {
                'total_services': total_services,
                'healthy_services': healthy_services,
                'unhealthy_services': total_services - healthy_services,
                'health_percentage': (healthy_services / total_services * 100) if total_services > 0 else 0,
                'avg_response_time': round(avg_response_time, 3),
                'last_check': max(
                    (h.last_check for h in self._health_data.values() if h.last_check),
                    default=None
                )
            }
    
    def get_health_history(
        self,
        service_name: str,
        hours: int = 24
    ) -> List[ServiceHealth]:
        """获取服务健康历史"""
        with self._lock:
            history = self._health_history.get(service_name, [])
            if not hours:
                return history.copy()
            
            # 过滤指定时间范围内的记录
            cutoff_time = datetime.now() - timedelta(hours=hours)
            return [
                h for h in history 
                if h.last_check and h.last_check > cutoff_time
            ]
    
    def register_health_change_callback(self, callback: Callable[[str, ServiceHealth], None]):
        """注册健康状态变化回调"""
        self._on_health_change.append(callback)
    
    def register_service_down_callback(self, callback: Callable[[str], None]):
        """注册服务下线回调"""
        self._on_service_down.append(callback)
    
    def register_service_up_callback(self, callback: Callable[[str], None]):
        """注册服务上线回调"""
        self._on_service_up.append(callback)
    
    def _trigger_health_change_callbacks(self, service_name: str, health: ServiceHealth):
        """触发健康状态变化回调"""
        for callback in self._on_health_change:
            try:
                callback(service_name, health)
            except Exception as e:
                logger.error(f"健康状态变化回调异常: {e}")
    
    def _trigger_service_down_callbacks(self, service_name: str):
        """触发服务下线回调"""
        for callback in self._on_service_down:
            try:
                callback(service_name)
            except Exception as e:
                logger.error(f"服务下线回调异常: {e}")
    
    def _trigger_service_up_callbacks(self, service_name: str):
        """触发服务上线回调"""
        for callback in self._on_service_up:
            try:
                callback(service_name)
            except Exception as e:
                logger.error(f"服务上线回调异常: {e}")
    
    def clear_history(self, service_name: Optional[str] = None):
        """清除健康历史"""
        with self._lock:
            if service_name:
                self._health_history.pop(service_name, None)
                logger.info(f"已清除服务 {service_name} 的健康历史")
            else:
                self._health_history.clear()
                logger.info("已清除所有服务的健康历史")
    
    def force_health_status(self, service_name: str, is_healthy: bool):
        """强制设置服务健康状态（用于测试）"""
        with self._lock:
            if service_name not in self._health_data:
                self._health_data[service_name] = ServiceHealth(service_name=service_name)
            
            health = self._health_data[service_name]
            health.is_healthy = is_healthy
            health.status = HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY
            health.last_check = datetime.now()
            
            logger.info(f"强制设置服务 {service_name} 健康状态: {is_healthy}")

