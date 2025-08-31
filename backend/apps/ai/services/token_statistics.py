"""
Token统计服务

提供Token使用数据的收集、统计和分析功能
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from decimal import Decimal

from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncDate, TruncHour, TruncWeek, TruncMonth
from django.core.cache import cache
from django.contrib.auth import get_user_model

from ..config_models import TokenUsage, AIProvider, AIModel
from ..monitoring_models import SystemAlert

User = get_user_model()
logger = logging.getLogger(__name__)


@dataclass
class TokenStatistics:
    """Token统计数据结构"""
    period: str
    start_time: datetime
    end_time: datetime
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost: Decimal = Decimal('0.00')
    input_cost: Decimal = Decimal('0.00')
    output_cost: Decimal = Decimal('0.00')
    avg_response_time: float = 0.0
    avg_tokens_per_request: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        data['total_cost'] = float(self.total_cost)
        data['input_cost'] = float(self.input_cost)
        data['output_cost'] = float(self.output_cost)
        return data


@dataclass
class ProviderStatistics:
    """提供商统计数据"""
    provider_id: int
    provider_name: str
    provider_type: str
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: Decimal = Decimal('0.00')
    success_rate: float = 100.0
    avg_response_time: float = 0.0
    most_used_model: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['total_cost'] = float(self.total_cost)
        return data


@dataclass
class ModelStatistics:
    """模型统计数据"""
    model_id: int
    model_name: str
    provider_name: str
    total_requests: int = 0
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost: Decimal = Decimal('0.00')
    avg_tokens_per_request: float = 0.0
    avg_cost_per_request: Decimal = Decimal('0.00')
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['total_cost'] = float(self.total_cost)
        data['avg_cost_per_request'] = float(self.avg_cost_per_request)
        return data


@dataclass
class BudgetAlert:
    """预算告警数据"""
    user_id: int
    username: str
    current_cost: Decimal
    budget_limit: Decimal
    usage_percentage: float
    period: str
    alert_level: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['current_cost'] = float(self.current_cost)
        data['budget_limit'] = float(self.budget_limit)
        return data


class TokenStatisticsService:
    """Token统计服务主类"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5分钟缓存
    
    def get_realtime_statistics(
        self,
        user: Optional[User] = None,
        provider: Optional[AIProvider] = None,
        model: Optional[AIModel] = None
    ) -> TokenStatistics:
        """
        获取实时统计数据（当日）
        
        Args:
            user: 用户过滤
            provider: 提供商过滤
            model: 模型过滤
            
        Returns:
            当日Token统计数据
        """
        try:
            # 当日时间范围
            today = timezone.now().date()
            start_time = timezone.make_aware(datetime.combine(today, datetime.min.time()))
            end_time = timezone.now()
            
            # 构建查询
            queryset = TokenUsage.objects.filter(
                created_at__gte=start_time,
                created_at__lte=end_time
            )
            
            if user:
                queryset = queryset.filter(user=user)
            if provider:
                queryset = queryset.filter(provider=provider)
            if model:
                queryset = queryset.filter(model=model)
            
            # 聚合统计
            stats = queryset.aggregate(
                total_requests=Count('id'),
                successful_requests=Count('id', filter=Q(status='success')),
                total_tokens=Sum('total_tokens'),
                input_tokens=Sum('input_tokens'),
                output_tokens=Sum('output_tokens'),
                total_cost=Sum('total_cost'),
                input_cost=Sum('input_cost'),
                output_cost=Sum('output_cost'),
                avg_response_time=Avg('response_time')
            )
            
            # 处理空值
            for key, value in stats.items():
                if value is None:
                    if 'cost' in key:
                        stats[key] = Decimal('0.00')
                    else:
                        stats[key] = 0
            
            # 计算失败请求数
            failed_requests = stats['total_requests'] - stats['successful_requests']
            
            # 计算平均Token数
            avg_tokens_per_request = (
                stats['total_tokens'] / stats['total_requests']
                if stats['total_requests'] > 0 else 0.0
            )
            
            return TokenStatistics(
                period='today',
                start_time=start_time,
                end_time=end_time,
                total_requests=stats['total_requests'],
                successful_requests=stats['successful_requests'],
                failed_requests=failed_requests,
                total_tokens=stats['total_tokens'] or 0,
                input_tokens=stats['input_tokens'] or 0,
                output_tokens=stats['output_tokens'] or 0,
                total_cost=stats['total_cost'],
                input_cost=stats['input_cost'],
                output_cost=stats['output_cost'],
                avg_response_time=stats['avg_response_time'] or 0.0,
                avg_tokens_per_request=avg_tokens_per_request
            )
            
        except Exception as e:
            logger.error(f"获取实时统计失败: {e}")
            return TokenStatistics(
                period='today',
                start_time=start_time,
                end_time=end_time
            )
    
    def get_historical_statistics(
        self,
        period: str = 'day',
        days: int = 30,
        user: Optional[User] = None,
        provider: Optional[AIProvider] = None,
        model: Optional[AIModel] = None
    ) -> List[TokenStatistics]:
        """
        获取历史统计数据
        
        Args:
            period: 统计周期 ('hour', 'day', 'week', 'month')
            days: 查询天数
            user: 用户过滤
            provider: 提供商过滤
            model: 模型过滤
            
        Returns:
            历史统计数据列表
        """
        try:
            # 时间范围
            end_time = timezone.now()
            start_time = end_time - timedelta(days=days)
            
            # 构建查询
            queryset = TokenUsage.objects.filter(
                created_at__gte=start_time,
                created_at__lte=end_time
            )
            
            if user:
                queryset = queryset.filter(user=user)
            if provider:
                queryset = queryset.filter(provider=provider)
            if model:
                queryset = queryset.filter(model=model)
            
            # 选择截断函数
            trunc_func_map = {
                'hour': TruncHour,
                'day': TruncDate,
                'week': TruncWeek,
                'month': TruncMonth
            }
            
            if period not in trunc_func_map:
                period = 'day'
            
            trunc_func = trunc_func_map[period]
            
            # 按时间分组聚合
            grouped_stats = queryset.annotate(
                period_time=trunc_func('created_at')
            ).values('period_time').annotate(
                total_requests=Count('id'),
                successful_requests=Count('id', filter=Q(status='success')),
                total_tokens=Sum('total_tokens'),
                input_tokens=Sum('input_tokens'),
                output_tokens=Sum('output_tokens'),
                total_cost=Sum('total_cost'),
                input_cost=Sum('input_cost'),
                output_cost=Sum('output_cost'),
                avg_response_time=Avg('response_time')
            ).order_by('period_time')
            
            # 转换为统计对象
            statistics = []
            for stat in grouped_stats:
                period_start = stat['period_time']
                
                # 计算周期结束时间
                if period == 'hour':
                    period_end = period_start + timedelta(hours=1)
                elif period == 'day':
                    period_end = period_start + timedelta(days=1)
                elif period == 'week':
                    period_end = period_start + timedelta(weeks=1)
                elif period == 'month':
                    # 简化处理，假设30天
                    period_end = period_start + timedelta(days=30)
                else:
                    period_end = period_start + timedelta(days=1)
                
                # 处理空值
                for key in ['total_tokens', 'input_tokens', 'output_tokens']:
                    if stat[key] is None:
                        stat[key] = 0
                
                for key in ['total_cost', 'input_cost', 'output_cost']:
                    if stat[key] is None:
                        stat[key] = Decimal('0.00')
                
                if stat['avg_response_time'] is None:
                    stat['avg_response_time'] = 0.0
                
                # 计算失败请求数和平均Token数
                failed_requests = stat['total_requests'] - stat['successful_requests']
                avg_tokens_per_request = (
                    stat['total_tokens'] / stat['total_requests']
                    if stat['total_requests'] > 0 else 0.0
                )
                
                statistics.append(TokenStatistics(
                    period=period,
                    start_time=period_start,
                    end_time=period_end,
                    total_requests=stat['total_requests'],
                    successful_requests=stat['successful_requests'],
                    failed_requests=failed_requests,
                    total_tokens=stat['total_tokens'],
                    input_tokens=stat['input_tokens'],
                    output_tokens=stat['output_tokens'],
                    total_cost=stat['total_cost'],
                    input_cost=stat['input_cost'],
                    output_cost=stat['output_cost'],
                    avg_response_time=stat['avg_response_time'],
                    avg_tokens_per_request=avg_tokens_per_request
                ))
            
            return statistics
            
        except Exception as e:
            logger.error(f"获取历史统计失败: {e}")
            return []
    
    def get_provider_statistics(
        self,
        user: Optional[User] = None,
        days: int = 30
    ) -> List[ProviderStatistics]:
        """
        获取提供商统计数据
        
        Args:
            user: 用户过滤
            days: 查询天数
            
        Returns:
            提供商统计数据列表
        """
        try:
            # 时间范围
            end_time = timezone.now()
            start_time = end_time - timedelta(days=days)
            
            # 构建查询
            queryset = TokenUsage.objects.filter(
                created_at__gte=start_time,
                created_at__lte=end_time
            )
            
            if user:
                queryset = queryset.filter(user=user)
            
            # 按提供商分组统计
            provider_stats = queryset.values(
                'provider__id',
                'provider__display_name',
                'provider__provider_type'
            ).annotate(
                total_requests=Count('id'),
                successful_requests=Count('id', filter=Q(status='success')),
                total_tokens=Sum('total_tokens'),
                total_cost=Sum('total_cost'),
                avg_response_time=Avg('response_time')
            ).order_by('-total_requests')
            
            # 获取每个提供商最常用的模型
            statistics = []
            for stat in provider_stats:
                provider_id = stat['provider__id']
                
                # 查找最常用模型
                most_used_model_query = queryset.filter(
                    provider__id=provider_id
                ).values('model__display_name').annotate(
                    usage_count=Count('id')
                ).order_by('-usage_count').first()
                
                most_used_model = (
                    most_used_model_query['model__display_name']
                    if most_used_model_query else "未知"
                )
                
                # 计算成功率
                success_rate = (
                    stat['successful_requests'] / stat['total_requests'] * 100
                    if stat['total_requests'] > 0 else 0.0
                )
                
                # 处理空值
                for key in ['total_tokens']:
                    if stat[key] is None:
                        stat[key] = 0
                
                for key in ['total_cost']:
                    if stat[key] is None:
                        stat[key] = Decimal('0.00')
                
                if stat['avg_response_time'] is None:
                    stat['avg_response_time'] = 0.0
                
                statistics.append(ProviderStatistics(
                    provider_id=provider_id,
                    provider_name=stat['provider__display_name'],
                    provider_type=stat['provider__provider_type'],
                    total_requests=stat['total_requests'],
                    total_tokens=stat['total_tokens'],
                    total_cost=stat['total_cost'],
                    success_rate=round(success_rate, 2),
                    avg_response_time=round(stat['avg_response_time'], 3),
                    most_used_model=most_used_model
                ))
            
            return statistics
            
        except Exception as e:
            logger.error(f"获取提供商统计失败: {e}")
            return []
    
    def get_model_statistics(
        self,
        user: Optional[User] = None,
        provider: Optional[AIProvider] = None,
        days: int = 30
    ) -> List[ModelStatistics]:
        """
        获取模型统计数据
        
        Args:
            user: 用户过滤
            provider: 提供商过滤
            days: 查询天数
            
        Returns:
            模型统计数据列表
        """
        try:
            # 时间范围
            end_time = timezone.now()
            start_time = end_time - timedelta(days=days)
            
            # 构建查询
            queryset = TokenUsage.objects.filter(
                created_at__gte=start_time,
                created_at__lte=end_time
            )
            
            if user:
                queryset = queryset.filter(user=user)
            if provider:
                queryset = queryset.filter(provider=provider)
            
            # 按模型分组统计
            model_stats = queryset.values(
                'model__id',
                'model__display_name',
                'provider__display_name'
            ).annotate(
                total_requests=Count('id'),
                total_tokens=Sum('total_tokens'),
                input_tokens=Sum('input_tokens'),
                output_tokens=Sum('output_tokens'),
                total_cost=Sum('total_cost'),
                avg_cost=Avg('total_cost')
            ).order_by('-total_requests')
            
            # 转换为统计对象
            statistics = []
            for stat in model_stats:
                # 处理空值
                for key in ['total_tokens', 'input_tokens', 'output_tokens']:
                    if stat[key] is None:
                        stat[key] = 0
                
                for key in ['total_cost', 'avg_cost']:
                    if stat[key] is None:
                        stat[key] = Decimal('0.00')
                
                # 计算平均Token数
                avg_tokens_per_request = (
                    stat['total_tokens'] / stat['total_requests']
                    if stat['total_requests'] > 0 else 0.0
                )
                
                statistics.append(ModelStatistics(
                    model_id=stat['model__id'],
                    model_name=stat['model__display_name'],
                    provider_name=stat['provider__display_name'],
                    total_requests=stat['total_requests'],
                    total_tokens=stat['total_tokens'],
                    input_tokens=stat['input_tokens'],
                    output_tokens=stat['output_tokens'],
                    total_cost=stat['total_cost'],
                    avg_tokens_per_request=round(avg_tokens_per_request, 2),
                    avg_cost_per_request=stat['avg_cost']
                ))
            
            return statistics
            
        except Exception as e:
            logger.error(f"获取模型统计失败: {e}")
            return []
    
    def get_user_summary(self, user: User, days: int = 30) -> Dict[str, Any]:
        """
        获取用户使用摘要
        
        Args:
            user: 用户
            days: 查询天数
            
        Returns:
            用户使用摘要
        """
        try:
            cache_key = f"token_stats:user_summary:{user.id}:{days}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
            
            # 时间范围
            end_time = timezone.now()
            start_time = end_time - timedelta(days=days)
            
            # 基础统计
            basic_stats = TokenUsage.objects.filter(
                user=user,
                created_at__gte=start_time,
                created_at__lte=end_time
            ).aggregate(
                total_requests=Count('id'),
                successful_requests=Count('id', filter=Q(status='success')),
                total_tokens=Sum('total_tokens'),
                total_cost=Sum('total_cost'),
                avg_response_time=Avg('response_time')
            )
            
            # 处理空值
            for key, value in basic_stats.items():
                if value is None:
                    if key == 'total_cost':
                        basic_stats[key] = Decimal('0.00')
                    else:
                        basic_stats[key] = 0
            
            # 今日统计
            today_stats = self.get_realtime_statistics(user=user)
            
            # 最常用的提供商
            top_provider = TokenUsage.objects.filter(
                user=user,
                created_at__gte=start_time,
                created_at__lte=end_time
            ).values(
                'provider__display_name'
            ).annotate(
                usage_count=Count('id')
            ).order_by('-usage_count').first()
            
            # 最常用的模型
            top_model = TokenUsage.objects.filter(
                user=user,
                created_at__gte=start_time,
                created_at__lte=end_time
            ).values(
                'model__display_name'
            ).annotate(
                usage_count=Count('id')
            ).order_by('-usage_count').first()
            
            # 构建摘要
            summary = {
                'user_id': user.id,
                'username': user.username,
                'period_days': days,
                'period_start': start_time.isoformat(),
                'period_end': end_time.isoformat(),
                'total_requests': basic_stats['total_requests'],
                'successful_requests': basic_stats['successful_requests'],
                'success_rate': round(
                    basic_stats['successful_requests'] / basic_stats['total_requests'] * 100
                    if basic_stats['total_requests'] > 0 else 0.0, 2
                ),
                'total_tokens': basic_stats['total_tokens'],
                'total_cost': float(basic_stats['total_cost']),
                'avg_response_time': round(basic_stats['avg_response_time'] or 0.0, 3),
                'today_requests': today_stats.total_requests,
                'today_tokens': today_stats.total_tokens,
                'today_cost': float(today_stats.total_cost),
                'top_provider': top_provider['provider__display_name'] if top_provider else "无",
                'top_model': top_model['model__display_name'] if top_model else "无",
                'timestamp': timezone.now().isoformat()
            }
            
            # 缓存结果
            cache.set(cache_key, summary, self.cache_timeout)
            return summary
            
        except Exception as e:
            logger.error(f"获取用户摘要失败: {e}")
            return {
                'user_id': user.id,
                'username': user.username,
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
    
    def check_budget_alerts(self) -> List[BudgetAlert]:
        """
        检查预算告警
        
        Returns:
            预算告警列表
        """
        try:
            alerts = []
            
            # 获取所有用户的使用配额设置
            from ..config_models import UsageQuota
            
            active_quotas = UsageQuota.objects.filter(is_active=True)
            
            for quota in active_quotas:
                try:
                    # 计算当前周期的使用量
                    current_time = timezone.now()
                    
                    if quota.period_type == 'daily':
                        period_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                        period = 'daily'
                    elif quota.period_type == 'weekly':
                        # 周一开始
                        days_since_monday = current_time.weekday()
                        period_start = (current_time - timedelta(days=days_since_monday)).replace(
                            hour=0, minute=0, second=0, microsecond=0
                        )
                        period = 'weekly'
                    elif quota.period_type == 'monthly':
                        period_start = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                        period = 'monthly'
                    else:
                        continue
                    
                    # 查询当前周期的使用量
                    usage_stats = TokenUsage.objects.filter(
                        user=quota.user,
                        created_at__gte=period_start,
                        created_at__lte=current_time,
                        status='success'
                    ).aggregate(
                        total_cost=Sum('total_cost'),
                        total_tokens=Sum('total_tokens')
                    )
                    
                    current_cost = usage_stats['total_cost'] or Decimal('0.00')
                    current_tokens = usage_stats['total_tokens'] or 0
                    
                    # 检查成本限制
                    if quota.cost_limit and quota.cost_limit > 0:
                        usage_percentage = (current_cost / quota.cost_limit) * 100
                        
                        # 确定告警级别
                        if usage_percentage >= 100:
                            alert_level = 'critical'
                        elif usage_percentage >= 90:
                            alert_level = 'error'
                        elif usage_percentage >= 80:
                            alert_level = 'warning'
                        else:
                            alert_level = None
                        
                        if alert_level:
                            alerts.append(BudgetAlert(
                                user_id=quota.user.id,
                                username=quota.user.username,
                                current_cost=current_cost,
                                budget_limit=quota.cost_limit,
                                usage_percentage=round(usage_percentage, 2),
                                period=period,
                                alert_level=alert_level
                            ))
                    
                    # 检查Token限制
                    if quota.token_limit and quota.token_limit > 0:
                        usage_percentage = (current_tokens / quota.token_limit) * 100
                        
                        # 确定告警级别
                        if usage_percentage >= 100:
                            alert_level = 'critical'
                        elif usage_percentage >= 90:
                            alert_level = 'error'
                        elif usage_percentage >= 80:
                            alert_level = 'warning'
                        else:
                            alert_level = None
                        
                        if alert_level:
                            alerts.append(BudgetAlert(
                                user_id=quota.user.id,
                                username=quota.user.username,
                                current_cost=Decimal(str(current_tokens)),  # 用Token数作为"成本"
                                budget_limit=Decimal(str(quota.token_limit)),
                                usage_percentage=round(usage_percentage, 2),
                                period=period,
                                alert_level=alert_level
                            ))
                            
                except Exception as e:
                    logger.error(f"检查用户 {quota.user.username} 预算告警失败: {e}")
                    continue
            
            return alerts
            
        except Exception as e:
            logger.error(f"检查预算告警失败: {e}")
            return []
    
    def create_budget_alert(self, budget_alert: BudgetAlert):
        """
        创建预算告警
        
        Args:
            budget_alert: 预算告警数据
        """
        try:
            # 检查是否已有相同的活跃告警
            existing_alert = SystemAlert.objects.filter(
                alert_type='budget_exceeded',
                service_name=f"user_{budget_alert.user_id}",
                status=SystemAlert.AlertStatus.ACTIVE,
                metadata__period=budget_alert.period
            ).first()
            
            if existing_alert:
                # 更新现有告警
                existing_alert.message = (
                    f"用户 {budget_alert.username} {budget_alert.period} 预算使用率达到 "
                    f"{budget_alert.usage_percentage}%，当前费用: ${budget_alert.current_cost:.2f}"
                )
                existing_alert.actual_value = float(budget_alert.usage_percentage)
                existing_alert.save()
            else:
                # 创建新告警
                alert_level_mapping = {
                    'warning': SystemAlert.AlertLevel.WARNING,
                    'error': SystemAlert.AlertLevel.ERROR,
                    'critical': SystemAlert.AlertLevel.CRITICAL
                }
                
                SystemAlert.create_alert(
                    alert_type='budget_exceeded',
                    title=f'用户预算告警 - {budget_alert.username}',
                    message=(
                        f"用户 {budget_alert.username} {budget_alert.period} 预算使用率达到 "
                        f"{budget_alert.usage_percentage}%，当前费用: ${budget_alert.current_cost:.2f}"
                    ),
                    level=alert_level_mapping.get(budget_alert.alert_level, SystemAlert.AlertLevel.WARNING),
                    service_name=f"user_{budget_alert.user_id}",
                    threshold_value=80.0,  # 默认阈值
                    actual_value=budget_alert.usage_percentage,
                    period=budget_alert.period,
                    user_id=budget_alert.user_id,
                    current_cost=float(budget_alert.current_cost),
                    budget_limit=float(budget_alert.budget_limit)
                )
                
        except Exception as e:
            logger.error(f"创建预算告警失败: {e}")


# 全局Token统计服务实例
token_statistics_service = TokenStatisticsService()

