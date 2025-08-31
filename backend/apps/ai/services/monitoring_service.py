"""
实时监控服务

提供服务健康监控、性能指标收集和实时数据推送功能
"""

import time
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
from django.core.cache import cache

from ..monitoring_models import (
    ServiceHealthRecord, PerformanceMetric, SystemAlert,
    ServiceHealthStatus
)
from ..config_models import AIProvider, TokenUsage
from .health_monitor import HealthMonitor, ServiceHealth, HealthStatus

logger = logging.getLogger(__name__)


@dataclass
class RealTimeMetrics:
    """实时指标数据结构"""
    service_name: str
    timestamp: datetime
    qps: float = 0.0
    avg_response_time: float = 0.0
    error_rate: float = 0.0
    success_rate: float = 100.0
    active_requests: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ServiceStatus:
    """服务状态摘要"""
    service_name: str
    provider_name: str = ""
    is_healthy: bool = True
    status: str = "healthy"
    response_time: float = 0.0
    uptime_percentage: float = 100.0
    last_check: Optional[datetime] = None
    error_message: str = ""
    metrics: Optional[RealTimeMetrics] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        if self.last_check:
            data['last_check'] = self.last_check.isoformat()
        if self.metrics:
            data['metrics'] = self.metrics.to_dict()
        return data


class MonitoringService:
    """监控服务主类"""
    
    def __init__(self):
        self.health_monitor = HealthMonitor()
        
        # 实时数据缓存
        self._real_time_data: Dict[str, RealTimeMetrics] = {}
        self._request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # 缓存配置
        self.cache_timeout = 60  # 1分钟
        self.metrics_window = 300  # 5分钟窗口
        
        # 启动健康监控
        self.health_monitor.start_monitoring()
        
        # 注册健康状态变化回调
        self.health_monitor.register_health_change_callback(self._on_health_change)
    
    def _on_health_change(self, service_name: str, health: ServiceHealth):
        """健康状态变化回调"""
        try:
            # 记录到数据库
            provider = self._get_provider_by_service_name(service_name)
            
            ServiceHealthRecord.objects.create(
                service_name=service_name,
                provider=provider,
                status=self._convert_health_status(health.status),
                is_healthy=health.is_healthy,
                response_time=health.response_time,
                error_message=health.error or "",
                consecutive_failures=health.consecutive_failures,
                check_type='health_check'
            )
            
            # 检查是否需要创建告警
            self._check_alert_conditions(service_name, health)
            
        except Exception as e:
            logger.error(f"处理健康状态变化失败: {e}")
    
    def _convert_health_status(self, status: HealthStatus) -> str:
        """转换健康状态枚举"""
        mapping = {
            HealthStatus.HEALTHY: ServiceHealthStatus.HEALTHY,
            HealthStatus.DEGRADED: ServiceHealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY: ServiceHealthStatus.UNHEALTHY,
            HealthStatus.UNKNOWN: ServiceHealthStatus.UNKNOWN,
        }
        return mapping.get(status, ServiceHealthStatus.UNKNOWN)
    
    def _get_provider_by_service_name(self, service_name: str) -> Optional[AIProvider]:
        """根据服务名获取提供商"""
        try:
            # 简单的名称映射
            provider_mapping = {
                'openai': 'openai',
                'anthropic': 'anthropic',
                'claude': 'anthropic',
                'google': 'google',
                'gemini': 'google',
                'chenmoai': 'chenmoai',
                'openrouter': 'openrouter',
            }
            
            for key, provider_type in provider_mapping.items():
                if key in service_name.lower():
                    return AIProvider.objects.filter(
                        provider_type=provider_type,
                        is_active=True
                    ).first()
            
            return None
        except Exception:
            return None
    
    def _check_alert_conditions(self, service_name: str, health: ServiceHealth):
        """检查告警条件"""
        try:
            provider = self._get_provider_by_service_name(service_name)
            
            # 服务不健康告警
            if not health.is_healthy and health.consecutive_failures >= 3:
                SystemAlert.create_alert(
                    alert_type='service_unhealthy',
                    title=f'服务 {service_name} 连续失败',
                    message=f'服务 {service_name} 连续失败 {health.consecutive_failures} 次，错误: {health.error}',
                    level=SystemAlert.AlertLevel.ERROR,
                    service_name=service_name,
                    provider=provider,
                    consecutive_failures=health.consecutive_failures,
                    error_message=health.error
                )
            
            # 响应时间过慢告警
            if health.response_time > 10.0:
                SystemAlert.create_alert(
                    alert_type='slow_response',
                    title=f'服务 {service_name} 响应缓慢',
                    message=f'服务 {service_name} 响应时间 {health.response_time:.2f}s 超过阈值 10s',
                    level=SystemAlert.AlertLevel.WARNING,
                    service_name=service_name,
                    provider=provider,
                    threshold_value=10.0,
                    actual_value=health.response_time
                )
                
        except Exception as e:
            logger.error(f"检查告警条件失败: {e}")
    
    def record_api_call(
        self,
        service_name: str,
        success: bool,
        response_time: float,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0,
        error_message: str = ""
    ):
        """记录API调用"""
        try:
            current_time = timezone.now()
            
            # 更新实时数据
            if service_name not in self._real_time_data:
                self._real_time_data[service_name] = RealTimeMetrics(
                    service_name=service_name,
                    timestamp=current_time
                )
            
            metrics = self._real_time_data[service_name]
            metrics.timestamp = current_time
            metrics.total_requests += 1
            
            if not success:
                metrics.failed_requests += 1
            
            # 更新响应时间历史
            self._response_times[service_name].append(response_time)
            
            # 更新请求历史（用于计算QPS）
            self._request_history[service_name].append({
                'timestamp': current_time.timestamp(),
                'success': success,
                'response_time': response_time
            })
            
            # 计算实时指标
            self._calculate_real_time_metrics(service_name)
            
            # 异步记录到数据库（避免阻塞）
            self._async_record_to_db(
                service_name, success, response_time,
                input_tokens, output_tokens, cost, error_message
            )
            
        except Exception as e:
            logger.error(f"记录API调用失败: {e}")
    
    def _calculate_real_time_metrics(self, service_name: str):
        """计算实时指标"""
        try:
            metrics = self._real_time_data[service_name]
            current_time = time.time()
            window_start = current_time - self.metrics_window
            
            # 获取窗口内的请求
            history = self._request_history[service_name]
            recent_requests = [
                req for req in history 
                if req['timestamp'] > window_start
            ]
            
            if recent_requests:
                # 计算QPS
                time_span = current_time - min(req['timestamp'] for req in recent_requests)
                if time_span > 0:
                    metrics.qps = len(recent_requests) / time_span
                
                # 计算成功率
                successful = sum(1 for req in recent_requests if req['success'])
                metrics.success_rate = (successful / len(recent_requests)) * 100
                metrics.error_rate = 100 - metrics.success_rate
                
                # 计算平均响应时间
                response_times = [req['response_time'] for req in recent_requests]
                metrics.avg_response_time = statistics.mean(response_times)
            
        except Exception as e:
            logger.error(f"计算实时指标失败: {e}")
    
    def _async_record_to_db(
        self,
        service_name: str,
        success: bool,
        response_time: float,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        error_message: str
    ):
        """异步记录到数据库"""
        try:
            # 这里可以使用Celery任务异步处理
            # 目前直接同步处理
            provider = self._get_provider_by_service_name(service_name)
            
            # 记录健康状态
            ServiceHealthRecord.objects.create(
                service_name=service_name,
                provider=provider,
                status=ServiceHealthStatus.HEALTHY if success else ServiceHealthStatus.UNHEALTHY,
                is_healthy=success,
                response_time=response_time,
                error_message=error_message,
                check_type='api_call'
            )
            
        except Exception as e:
            logger.error(f"异步记录到数据库失败: {e}")
    
    def get_service_status(self, service_name: str) -> Optional[ServiceStatus]:
        """获取服务状态"""
        try:
            # 从健康监控器获取状态
            health = self.health_monitor.get_health(service_name)
            if not health:
                return None
            
            # 获取实时指标
            metrics = self._real_time_data.get(service_name)
            
            # 获取运行时间百分比
            uptime = ServiceHealthRecord.get_uptime_percentage(service_name, hours=24)
            
            return ServiceStatus(
                service_name=service_name,
                provider_name=self._get_provider_display_name(service_name),
                is_healthy=health.is_healthy,
                status=health.status.value,
                response_time=health.response_time,
                uptime_percentage=uptime,
                last_check=health.last_check,
                error_message=health.error or "",
                metrics=metrics
            )
            
        except Exception as e:
            logger.error(f"获取服务状态失败: {e}")
            return None
    
    def _get_provider_display_name(self, service_name: str) -> str:
        """获取提供商显示名称"""
        provider = self._get_provider_by_service_name(service_name)
        return provider.display_name if provider else service_name
    
    def get_all_services_status(self) -> List[ServiceStatus]:
        """获取所有服务状态"""
        try:
            all_health = self.health_monitor.get_all_health()
            statuses = []
            
            for service_name in all_health.keys():
                status = self.get_service_status(service_name)
                if status:
                    statuses.append(status)
            
            return statuses
            
        except Exception as e:
            logger.error(f"获取所有服务状态失败: {e}")
            return []
    
    def get_system_overview(self) -> Dict[str, Any]:
        """获取系统概览"""
        try:
            cache_key = "monitoring:system_overview"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
            
            # 健康状态摘要
            health_summary = self.health_monitor.get_health_summary()
            
            # 活跃告警数量
            active_alerts = SystemAlert.get_active_alerts().count()
            critical_alerts = SystemAlert.get_active_alerts().filter(
                level=SystemAlert.AlertLevel.CRITICAL
            ).count()
            
            # 最近24小时性能统计
            now = timezone.now()
            day_ago = now - timedelta(hours=24)
            
            # 总请求数
            total_requests = ServiceHealthRecord.objects.filter(
                check_timestamp__gte=day_ago,
                check_type='api_call'
            ).count()
            
            # 错误率
            failed_requests = ServiceHealthRecord.objects.filter(
                check_timestamp__gte=day_ago,
                check_type='api_call',
                is_healthy=False
            ).count()
            
            error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
            
            # 平均响应时间
            avg_response_time = ServiceHealthRecord.objects.filter(
                check_timestamp__gte=day_ago,
                check_type='api_call'
            ).aggregate(avg_time=Avg('response_time'))['avg_time'] or 0
            
            overview = {
                'timestamp': now.isoformat(),
                'health_summary': health_summary,
                'alerts': {
                    'active': active_alerts,
                    'critical': critical_alerts
                },
                'performance': {
                    'total_requests': total_requests,
                    'error_rate': round(error_rate, 2),
                    'avg_response_time': round(avg_response_time, 3)
                },
                'services': [status.to_dict() for status in self.get_all_services_status()]
            }
            
            # 缓存结果
            cache.set(cache_key, overview, self.cache_timeout)
            return overview
            
        except Exception as e:
            logger.error(f"获取系统概览失败: {e}")
            return {
                'timestamp': timezone.now().isoformat(),
                'error': str(e)
            }
    
    def get_service_metrics_history(
        self,
        service_name: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """获取服务指标历史"""
        try:
            cutoff_time = timezone.now() - timedelta(hours=hours)
            
            # 从数据库获取历史记录
            records = ServiceHealthRecord.objects.filter(
                service_name=service_name,
                check_timestamp__gte=cutoff_time
            ).order_by('check_timestamp')
            
            # 按小时分组聚合
            history = []
            current_hour = None
            hour_data = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'response_times': []
            }
            
            for record in records:
                record_hour = record.check_timestamp.replace(minute=0, second=0, microsecond=0)
                
                if current_hour is None:
                    current_hour = record_hour
                elif record_hour != current_hour:
                    # 完成当前小时的数据
                    if hour_data['total_requests'] > 0:
                        avg_response_time = (
                            sum(hour_data['response_times']) / len(hour_data['response_times'])
                            if hour_data['response_times'] else 0
                        )
                        error_rate = (
                            hour_data['failed_requests'] / hour_data['total_requests'] * 100
                        )
                        
                        history.append({
                            'timestamp': current_hour.isoformat(),
                            'total_requests': hour_data['total_requests'],
                            'error_rate': round(error_rate, 2),
                            'avg_response_time': round(avg_response_time, 3)
                        })
                    
                    # 重置数据
                    current_hour = record_hour
                    hour_data = {
                        'total_requests': 0,
                        'successful_requests': 0,
                        'failed_requests': 0,
                        'response_times': []
                    }
                
                # 累积当前小时数据
                hour_data['total_requests'] += 1
                if record.is_healthy:
                    hour_data['successful_requests'] += 1
                else:
                    hour_data['failed_requests'] += 1
                hour_data['response_times'].append(record.response_time)
            
            # 处理最后一个小时的数据
            if current_hour and hour_data['total_requests'] > 0:
                avg_response_time = (
                    sum(hour_data['response_times']) / len(hour_data['response_times'])
                    if hour_data['response_times'] else 0
                )
                error_rate = (
                    hour_data['failed_requests'] / hour_data['total_requests'] * 100
                )
                
                history.append({
                    'timestamp': current_hour.isoformat(),
                    'total_requests': hour_data['total_requests'],
                    'error_rate': round(error_rate, 2),
                    'avg_response_time': round(avg_response_time, 3)
                })
            
            return history
            
        except Exception as e:
            logger.error(f"获取服务指标历史失败: {e}")
            return []
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """获取活跃告警"""
        try:
            alerts = SystemAlert.get_active_alerts().order_by('-created_at')[:50]
            
            return [
                {
                    'id': str(alert.id),
                    'type': alert.alert_type,
                    'level': alert.level,
                    'title': alert.title,
                    'message': alert.message,
                    'service_name': alert.service_name,
                    'provider': alert.provider.display_name if alert.provider else "",
                    'created_at': alert.created_at.isoformat(),
                    'metadata': alert.metadata
                }
                for alert in alerts
            ]
            
        except Exception as e:
            logger.error(f"获取活跃告警失败: {e}")
            return []
    
    def cleanup_old_data(self, days: int = 7):
        """清理旧数据"""
        try:
            # 清理健康记录
            health_deleted = ServiceHealthRecord.cleanup_old_records(days)
            
            # 清理性能指标
            metrics_deleted = PerformanceMetric.cleanup_old_metrics(days * 4)  # 保留更长时间
            
            # 清理告警
            alerts_deleted = SystemAlert.cleanup_old_alerts(days * 2)
            
            logger.info(f"数据清理完成: 健康记录 {health_deleted}, 性能指标 {metrics_deleted}, 告警 {alerts_deleted}")
            
            return {
                'health_records': health_deleted,
                'performance_metrics': metrics_deleted,
                'alerts': alerts_deleted
            }
            
        except Exception as e:
            logger.error(f"数据清理失败: {e}")
            return {'error': str(e)}
    
    def force_health_check(self, service_name: str = None) -> Dict[str, Any]:
        """强制执行健康检查"""
        try:
            if service_name:
                # 检查特定服务
                health = self.health_monitor.get_health(service_name)
                if health:
                    # 这里应该调用实际的健康检查逻辑
                    # 目前返回当前状态
                    return {
                        'service': service_name,
                        'status': health.status.value,
                        'is_healthy': health.is_healthy,
                        'response_time': health.response_time,
                        'last_check': health.last_check.isoformat() if health.last_check else None
                    }
                else:
                    return {'error': f'服务 {service_name} 未找到'}
            else:
                # 检查所有服务
                all_health = self.health_monitor.get_all_health()
                results = {}
                for name, health in all_health.items():
                    results[name] = {
                        'status': health.status.value,
                        'is_healthy': health.is_healthy,
                        'response_time': health.response_time,
                        'last_check': health.last_check.isoformat() if health.last_check else None
                    }
                return results
                
        except Exception as e:
            logger.error(f"强制健康检查失败: {e}")
            return {'error': str(e)}


# 全局监控服务实例
monitoring_service = MonitoringService()

