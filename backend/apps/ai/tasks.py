"""
AI监控相关的Celery任务
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from celery import shared_task
from django.utils import timezone
from django.core.cache import cache

from .services.monitoring_service import monitoring_service
from .monitoring_models import ServiceHealthRecord, PerformanceMetric, SystemAlert
from .config_models import AIProvider

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def collect_system_metrics(self):
    """
    收集系统性能指标的定时任务
    每5分钟执行一次
    """
    try:
        logger.info("开始收集系统性能指标")
        
        # 获取所有活跃的AI提供商
        active_providers = AIProvider.objects.filter(is_active=True)
        
        current_time = timezone.now()
        period_start = current_time - timedelta(minutes=5)
        
        metrics_collected = 0
        
        for provider in active_providers:
            try:
                # 收集该提供商的指标
                provider_metrics = _collect_provider_metrics(
                    provider, period_start, current_time
                )
                
                if provider_metrics:
                    # 保存到数据库
                    PerformanceMetric.objects.create(**provider_metrics)
                    metrics_collected += 1
                    
            except Exception as e:
                logger.error(f"收集提供商 {provider.display_name} 指标失败: {e}")
        
        logger.info(f"系统指标收集完成，共收集 {metrics_collected} 个提供商的指标")
        
        return {
            'success': True,
            'metrics_collected': metrics_collected,
            'timestamp': current_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"收集系统指标任务失败: {e}")
        
        # 重试机制
        if self.request.retries < self.max_retries:
            logger.info(f"任务将在 {60 * (self.request.retries + 1)} 秒后重试")
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


def _collect_provider_metrics(
    provider: AIProvider,
    period_start: datetime,
    period_end: datetime
) -> Dict[str, Any]:
    """
    收集单个提供商的指标数据
    
    Args:
        provider: AI提供商实例
        period_start: 统计周期开始时间
        period_end: 统计周期结束时间
        
    Returns:
        指标数据字典，如果没有数据则返回None
    """
    try:
        # 从健康记录中统计API调用数据
        health_records = ServiceHealthRecord.objects.filter(
            provider=provider,
            check_timestamp__gte=period_start,
            check_timestamp__lt=period_end,
            check_type='api_call'
        )
        
        if not health_records.exists():
            return None
        
        # 统计基础指标
        total_requests = health_records.count()
        successful_requests = health_records.filter(is_healthy=True).count()
        failed_requests = total_requests - successful_requests
        
        # 计算响应时间统计
        response_times = list(health_records.values_list('response_time', flat=True))
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # 计算95分位数
            sorted_times = sorted(response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = 0.0
        
        # 从metadata中提取token和成本信息（如果有的话）
        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0.0
        
        for record in health_records:
            if record.metadata:
                total_input_tokens += record.metadata.get('input_tokens', 0)
                total_output_tokens += record.metadata.get('output_tokens', 0)
                total_cost += record.metadata.get('cost', 0.0)
        
        return {
            'service_name': f"{provider.provider_type}-service",
            'provider': provider,
            'period_start': period_start,
            'period_end': period_end,
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'avg_response_time': avg_response_time,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'p95_response_time': p95_response_time,
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'total_cost': total_cost
        }
        
    except Exception as e:
        logger.error(f"收集提供商 {provider.display_name} 指标时发生错误: {e}")
        return None


@shared_task(bind=True)
def perform_health_checks(self):
    """
    执行服务健康检查的定时任务
    每分钟执行一次
    """
    try:
        logger.info("开始执行服务健康检查")
        
        # 获取所有活跃的AI提供商
        active_providers = AIProvider.objects.filter(is_active=True)
        
        checks_performed = 0
        healthy_services = 0
        
        for provider in active_providers:
            try:
                # 执行健康检查（这里简化为检查服务状态）
                service_name = f"{provider.provider_type}-service"
                
                # 获取服务状态
                service_status = monitoring_service.get_service_status(service_name)
                
                if service_status:
                    # 记录健康检查结果
                    ServiceHealthRecord.objects.create(
                        service_name=service_name,
                        provider=provider,
                        status=service_status.status,
                        is_healthy=service_status.is_healthy,
                        response_time=service_status.response_time,
                        check_type='scheduled'
                    )
                    
                    checks_performed += 1
                    if service_status.is_healthy:
                        healthy_services += 1
                        
            except Exception as e:
                logger.error(f"健康检查失败 {provider.display_name}: {e}")
        
        logger.info(f"健康检查完成，检查了 {checks_performed} 个服务，{healthy_services} 个健康")
        
        return {
            'success': True,
            'checks_performed': checks_performed,
            'healthy_services': healthy_services,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"执行健康检查任务失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task(bind=True)
def cleanup_monitoring_data(self):
    """
    清理过期监控数据的定时任务
    每天凌晨执行一次
    """
    try:
        logger.info("开始清理过期监控数据")
        
        # 清理7天前的健康记录
        health_deleted = ServiceHealthRecord.cleanup_old_records(days=7)
        
        # 清理30天前的性能指标
        metrics_deleted = PerformanceMetric.cleanup_old_metrics(days=30)
        
        # 清理已解决的告警（14天前）
        alerts_deleted = SystemAlert.cleanup_old_alerts(days=14)
        
        logger.info(f"数据清理完成: 健康记录 {health_deleted}, 性能指标 {metrics_deleted}, 告警 {alerts_deleted}")
        
        return {
            'success': True,
            'health_records_deleted': health_deleted,
            'metrics_deleted': metrics_deleted,
            'alerts_deleted': alerts_deleted,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"清理监控数据任务失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task(bind=True)
def generate_monitoring_alerts(self):
    """
    生成监控告警的定时任务
    每10分钟执行一次
    """
    try:
        logger.info("开始生成监控告警")
        
        current_time = timezone.now()
        check_period = current_time - timedelta(minutes=10)
        
        alerts_generated = 0
        
        # 检查服务健康状态
        for provider in AIProvider.objects.filter(is_active=True):
            try:
                service_name = f"{provider.provider_type}-service"
                
                # 检查最近的健康记录
                recent_records = ServiceHealthRecord.objects.filter(
                    provider=provider,
                    check_timestamp__gte=check_period
                ).order_by('-check_timestamp')
                
                if recent_records.exists():
                    # 检查连续失败
                    consecutive_failures = 0
                    for record in recent_records[:5]:  # 检查最近5次
                        if not record.is_healthy:
                            consecutive_failures += 1
                        else:
                            break
                    
                    # 连续失败3次以上创建告警
                    if consecutive_failures >= 3:
                        existing_alert = SystemAlert.objects.filter(
                            alert_type='service_unhealthy',
                            service_name=service_name,
                            status=SystemAlert.AlertStatus.ACTIVE
                        ).first()
                        
                        if not existing_alert:
                            SystemAlert.create_alert(
                                alert_type='service_unhealthy',
                                title=f'服务 {service_name} 连续失败',
                                message=f'服务 {service_name} 连续失败 {consecutive_failures} 次',
                                level=SystemAlert.AlertLevel.ERROR,
                                service_name=service_name,
                                provider=provider,
                                consecutive_failures=consecutive_failures
                            )
                            alerts_generated += 1
                    
                    # 检查响应时间过慢
                    from django.db.models import Avg
                    avg_response_time = recent_records.aggregate(
                        avg_time=Avg('response_time')
                    )['avg_time']
                    
                    if avg_response_time and avg_response_time > 5.0:
                        existing_alert = SystemAlert.objects.filter(
                            alert_type='slow_response',
                            service_name=service_name,
                            status=SystemAlert.AlertStatus.ACTIVE
                        ).first()
                        
                        if not existing_alert:
                            SystemAlert.create_alert(
                                alert_type='slow_response',
                                title=f'服务 {service_name} 响应缓慢',
                                message=f'服务 {service_name} 平均响应时间 {avg_response_time:.2f}s 超过阈值',
                                level=SystemAlert.AlertLevel.WARNING,
                                service_name=service_name,
                                provider=provider,
                                threshold_value=5.0,
                                actual_value=avg_response_time
                            )
                            alerts_generated += 1
                            
            except Exception as e:
                logger.error(f"为提供商 {provider.display_name} 生成告警失败: {e}")
        
        logger.info(f"告警生成完成，共生成 {alerts_generated} 个告警")
        
        return {
            'success': True,
            'alerts_generated': alerts_generated,
            'timestamp': current_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"生成监控告警任务失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task(bind=True)
def update_service_metrics_cache(self):
    """
    更新服务指标缓存的定时任务
    每分钟执行一次
    """
    try:
        logger.info("开始更新服务指标缓存")
        
        # 获取系统概览并缓存
        overview = monitoring_service.get_system_overview()
        cache.set('monitoring:system_overview', overview, 60)
        
        # 获取所有服务状态并缓存
        services = monitoring_service.get_all_services_status()
        cache.set('monitoring:all_services', services, 60)
        
        # 获取活跃告警并缓存
        alerts = monitoring_service.get_active_alerts()
        cache.set('monitoring:active_alerts', alerts, 60)
        
        logger.info("服务指标缓存更新完成")
        
        return {
            'success': True,
            'services_count': len(services),
            'alerts_count': len(alerts),
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"更新服务指标缓存任务失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task(bind=True)
def check_budget_alerts_task(self):
    """
    检查预算告警的定时任务
    每小时执行一次
    """
    try:
        logger.info("开始检查用户预算告警")
        
        from .services.token_statistics import token_statistics_service
        
        # 获取所有预算告警
        alerts = token_statistics_service.check_budget_alerts()
        
        alerts_created = 0
        
        # 为每个告警创建系统告警
        for budget_alert in alerts:
            try:
                token_statistics_service.create_budget_alert(budget_alert)
                alerts_created += 1
                logger.info(f"创建预算告警: 用户 {budget_alert.username}, 使用率 {budget_alert.usage_percentage}%")
                
            except Exception as e:
                logger.error(f"创建预算告警失败 {budget_alert.username}: {e}")
        
        logger.info(f"预算告警检查完成，共创建 {alerts_created} 个告警")
        
        return {
            'success': True,
            'total_alerts_checked': len(alerts),
            'alerts_created': alerts_created,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"检查预算告警任务失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task(bind=True)
def update_token_statistics_cache(self):
    """
    更新Token统计缓存的定时任务
    每30分钟执行一次
    """
    try:
        logger.info("开始更新Token统计缓存")
        
        from .services.token_statistics import token_statistics_service
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # 获取活跃用户（最近30天有使用记录）
        recent_users = User.objects.filter(
            token_usage__created_at__gte=timezone.now() - timedelta(days=30)
        ).distinct()
        
        cached_users = 0
        
        for user in recent_users:
            try:
                # 更新用户摘要缓存
                summary = token_statistics_service.get_user_summary(user, days=30)
                
                # 更新实时统计缓存
                realtime_stats = token_statistics_service.get_realtime_statistics(user=user)
                
                cached_users += 1
                
            except Exception as e:
                logger.error(f"更新用户 {user.username} 统计缓存失败: {e}")
                continue
        
        # 更新全局统计缓存
        try:
            # 获取所有提供商统计
            provider_stats = token_statistics_service.get_provider_statistics(days=30)
            cache.set('token_stats:all_providers', provider_stats, 1800)  # 30分钟
            
            # 获取所有模型统计
            model_stats = token_statistics_service.get_model_statistics(days=30)
            cache.set('token_stats:all_models', model_stats, 1800)  # 30分钟
            
        except Exception as e:
            logger.error(f"更新全局统计缓存失败: {e}")
        
        logger.info(f"Token统计缓存更新完成，更新 {cached_users} 个用户缓存")
        
        return {
            'success': True,
            'cached_users': cached_users,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"更新Token统计缓存任务失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task(bind=True)
def periodic_health_check_and_auto_switch(self):
    """周期性健康检查和自动切换任务"""
    from .models import FailoverStrategy, ProviderHealthStatus
    from .services.failover_service import FailoverService
    from .services.health_check_service import HealthCheckService
    
    logger.info("开始执行周期性健康检查和自动切换任务")
    
    health_service = HealthCheckService()
    strategies = FailoverStrategy.objects.filter(is_active=True)
    
    total_strategies = strategies.count()
    processed_strategies = 0
    auto_switches = 0
    
    for strategy in strategies:
        try:
            # 检查策略中的所有提供商
            providers_to_check = [strategy.primary_provider]
            providers_to_check.extend([
                rule.fallback_provider 
                for rule in strategy.rules.filter(is_active=True)
            ])
            
            # 去重
            providers_to_check = list(set(providers_to_check))
            
            # 检查每个提供商的健康状态
            for provider in providers_to_check:
                health_result = health_service.check_provider(provider)
                
                # 更新健康状态记录
                health_status, created = ProviderHealthStatus.objects.get_or_create(
                    strategy=strategy,
                    provider=provider,
                    defaults={
                        'success_count': 0,
                        'failure_count': 0,
                        'consecutive_failures': 0,
                        'consecutive_successes': 0,
                        'is_healthy': True,
                        'is_available': True
                    }
                )
                
                # 记录检查结果
                if health_result['is_healthy']:
                    health_status.record_success(health_result.get('response_time'))
                else:
                    health_status.record_failure(health_result.get('response_time'))
            
            # 创建故障转移服务实例
            failover_service = FailoverService(strategy)
            
            # 检查是否需要自动切换
            current_provider = strategy.active_provider
            if current_provider:
                current_health = ProviderHealthStatus.objects.filter(
                    strategy=strategy,
                    provider=current_provider
                ).first()
                
                if current_health and current_health.should_failover():
                    logger.info(
                        f"策略 {strategy.name} 的当前提供商 {current_provider.display_name} "
                        f"连续失败 {current_health.consecutive_failures} 次，触发自动切换"
                    )
                    
                    result = failover_service.execute_failover(
                        reason=f"周期性检查发现连续失败{current_health.consecutive_failures}次"
                    )
                    
                    if result['success']:
                        auto_switches += 1
                        logger.info(f"自动切换成功: {result}")
            
            processed_strategies += 1
            
        except Exception as e:
            logger.error(f"处理策略 {strategy.name} 时出错: {str(e)}")
            continue
    
    logger.info(
        f"周期性健康检查完成: 处理了 {processed_strategies}/{total_strategies} 个策略，"
        f"执行了 {auto_switches} 次自动切换"
    )
    
    return {
        'total_strategies': total_strategies,
        'processed_strategies': processed_strategies,
        'auto_switches': auto_switches
    }


@shared_task(bind=True)
def cleanup_old_health_records(self):
    """清理旧的健康状态记录"""
    from .models import ProviderHealthStatus
    from django.utils import timezone
    from datetime import timedelta
    
    # 删除30天前的健康状态记录
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count, _ = ProviderHealthStatus.objects.filter(
        updated_at__lt=cutoff_date
    ).delete()
    
    logger.info(f"清理了 {deleted_count} 条旧的健康状态记录")
    
    return {'deleted_count': deleted_count}


@shared_task(bind=True)
def update_provider_health_metrics(self):
    """更新提供商健康指标"""
    from .models import AIProvider, ProviderHealthStatus
    from django.db.models import Avg, Count
    
    logger.info("开始更新提供商健康指标")
    
    # 获取所有活跃的提供商
    providers = AIProvider.objects.filter(is_active=True)
    updated_count = 0
    
    for provider in providers:
        try:
            # 获取该提供商的所有健康状态记录
            health_records = ProviderHealthStatus.objects.filter(provider=provider)
            
            if health_records.exists():
                # 计算平均指标
                avg_metrics = health_records.aggregate(
                    avg_response_time=Avg('avg_response_time'),
                    total_strategies=Count('id')
                )
                
                # 计算整体健康状态
                healthy_count = health_records.filter(is_healthy=True).count()
                total_count = health_records.count()
                overall_health_rate = healthy_count / total_count if total_count > 0 else 0
                
                # 更新提供商指标
                provider.avg_response_time = avg_metrics['avg_response_time']
                provider.success_rate = overall_health_rate * 100  # 转换为百分比
                provider.is_healthy = overall_health_rate > 0.5  # 超过50%的策略认为健康
                provider.save(update_fields=['avg_response_time', 'success_rate', 'is_healthy'])
                
                updated_count += 1
                
        except Exception as e:
            logger.error(f"更新提供商 {provider.display_name} 指标时出错: {str(e)}")
            continue
    
    logger.info(f"更新了 {updated_count} 个提供商的健康指标")
    
    return {'updated_count': updated_count}