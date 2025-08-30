"""
AI调用成本监控系统

监控API调用成本、token使用量，提供成本分析和预警功能
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.cache import cache
from django.db import models
from django.db.models import Sum, Avg, Count, F
from django.utils import timezone

from ..adapters.base import AIResponse, AIProviderType

logger = logging.getLogger(__name__)


@dataclass
class CostRecord:
    """成本记录数据"""
    user_id: int
    function_type: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: Decimal
    timestamp: datetime
    response_time: float
    success: bool


class AIUsageRecord(models.Model):
    """AI使用记录模型"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    function_type = models.CharField(max_length=50, db_index=True)
    provider = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    
    # Token使用统计
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    
    # 成本信息
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    currency = models.CharField(max_length=3, default='USD')
    
    # 性能指标
    response_time = models.FloatField(null=True, blank=True)
    success = models.BooleanField(default=True)
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # 附加信息
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'ai_usage_records'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['function_type', '-created_at']),
            models.Index(fields=['provider', '-created_at']),
            models.Index(fields=['-created_at']),
        ]


class CostAlert(models.Model):
    """成本预警模型"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    alert_type = models.CharField(max_length=50)  # daily, weekly, monthly, threshold
    threshold_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # 预警配置
    is_active = models.BooleanField(default=True)
    notification_sent = models.BooleanField(default=False)
    
    # 时间信息
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 附加信息
    message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'ai_cost_alerts'
        ordering = ['-created_at']


class CostMonitor:
    """
    AI成本监控器
    
    监控API调用成本、token使用量，提供成本分析和预警功能
    """
    
    def __init__(self):
        """初始化成本监控器"""
        # 成本配置
        self.cost_rates = self._load_cost_rates()
        
        # 预警配置
        self.alert_thresholds = getattr(settings, 'AI_COST_ALERT_THRESHOLDS', {
            'daily_limit': 10.0,      # 每日成本限制
            'weekly_limit': 50.0,     # 每周成本限制
            'monthly_limit': 200.0,   # 每月成本限制
            'user_daily_limit': 2.0,  # 用户每日限制
        })
        
        # 缓存配置
        self.cache_timeout = 300  # 5分钟缓存
        
        logger.info("AI成本监控器已初始化")
    
    def _load_cost_rates(self) -> Dict[str, Dict[str, float]]:
        """加载成本费率配置"""
        return getattr(settings, 'AI_COST_RATES', {
            'openai': {
                'gpt-4': {'input': 0.03, 'output': 0.06},
                'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
                'gpt-3.5-turbo': {'input': 0.001, 'output': 0.002},
            },
            'anthropic': {
                'claude-3-opus': {'input': 0.015, 'output': 0.075},
                'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
                'claude-3-haiku': {'input': 0.00025, 'output': 0.00125},
            },
            'google': {
                'gemini-pro': {'input': 0.001, 'output': 0.002},
                'gemini-pro-vision': {'input': 0.002, 'output': 0.004},
            }
        })
    
    async def calculate_cost(self, response: AIResponse) -> Decimal:
        """
        计算AI响应成本
        
        Args:
            response: AI响应对象
            
        Returns:
            成本金额（美元）
        """
        if not response.usage:
            return Decimal('0')
        
        provider = response.provider.lower()
        model = response.model.lower()
        
        # 获取费率
        provider_rates = self.cost_rates.get(provider, {})
        model_rates = provider_rates.get(model, {'input': 0, 'output': 0})
        
        # 计算成本
        input_tokens = response.usage.get('prompt_tokens', 0)
        output_tokens = response.usage.get('completion_tokens', 0)
        
        input_cost = (input_tokens / 1000) * model_rates['input']
        output_cost = (output_tokens / 1000) * model_rates['output']
        
        total_cost = Decimal(str(input_cost + output_cost))
        
        logger.debug(f"成本计算: {provider}/{model}, 输入: {input_tokens}, 输出: {output_tokens}, 成本: ${total_cost}")
        return total_cost
    
    async def record_usage(
        self,
        user: User,
        function_type: str,
        cost: Decimal,
        tokens: int,
        response: AIResponse
    ) -> AIUsageRecord:
        """
        记录AI使用情况
        
        Args:
            user: 用户对象
            function_type: 功能类型
            cost: 成本
            tokens: token数量
            response: AI响应对象
            
        Returns:
            使用记录
        """
        try:
            # 创建使用记录
            usage_record = AIUsageRecord.objects.create(
                user=user,
                function_type=function_type,
                provider=response.provider,
                model=response.model,
                input_tokens=response.usage.get('prompt_tokens', 0) if response.usage else 0,
                output_tokens=response.usage.get('completion_tokens', 0) if response.usage else 0,
                total_tokens=tokens,
                cost=cost,
                response_time=response.response_time,
                success=response.finish_reason != 'error',
                metadata={
                    'finish_reason': response.finish_reason,
                    'function_type': function_type,
                }
            )
            
            # 检查预警
            await self._check_cost_alerts(user, cost)
            
            # 更新缓存统计
            await self._update_cache_statistics(user, cost, tokens)
            
            logger.info(f"记录AI使用: 用户{user.id}, 功能{function_type}, 成本${cost}")
            return usage_record
            
        except Exception as e:
            logger.error(f"记录AI使用失败: {e}")
            raise
    
    async def get_user_statistics(self, user: User, days: int = 30) -> Dict[str, Any]:
        """
        获取用户使用统计
        
        Args:
            user: 用户对象
            days: 统计天数
            
        Returns:
            统计信息
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # 基础统计
        queryset = AIUsageRecord.objects.filter(
            user=user,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # 总体统计
        total_stats = queryset.aggregate(
            total_requests=Count('id'),
            total_cost=Sum('cost'),
            total_tokens=Sum('total_tokens'),
            avg_response_time=Avg('response_time'),
            success_rate=Avg('success', output_field=models.FloatField())
        )
        
        # 按功能统计
        function_stats = list(
            queryset.values('function_type')
            .annotate(
                requests=Count('id'),
                cost=Sum('cost'),
                tokens=Sum('total_tokens'),
                avg_response_time=Avg('response_time')
            )
            .order_by('-cost')
        )
        
        # 按日期统计
        daily_stats = list(
            queryset.extra(select={'date': 'DATE(created_at)'})
            .values('date')
            .annotate(
                requests=Count('id'),
                cost=Sum('cost'),
                tokens=Sum('total_tokens')
            )
            .order_by('date')
        )
        
        # 按模型统计
        model_stats = list(
            queryset.values('provider', 'model')
            .annotate(
                requests=Count('id'),
                cost=Sum('cost'),
                tokens=Sum('total_tokens')
            )
            .order_by('-cost')
        )
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'total': {
                'requests': total_stats['total_requests'] or 0,
                'cost': float(total_stats['total_cost'] or 0),
                'tokens': total_stats['total_tokens'] or 0,
                'avg_response_time': total_stats['avg_response_time'] or 0,
                'success_rate': (total_stats['success_rate'] or 0) * 100
            },
            'by_function': function_stats,
            'by_date': daily_stats,
            'by_model': model_stats
        }
    
    async def get_system_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        获取系统整体统计
        
        Args:
            days: 统计天数
            
        Returns:
            系统统计信息
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        queryset = AIUsageRecord.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # 总体统计
        total_stats = queryset.aggregate(
            total_requests=Count('id'),
            total_cost=Sum('cost'),
            total_tokens=Sum('total_tokens'),
            unique_users=Count('user', distinct=True),
            avg_response_time=Avg('response_time'),
            success_rate=Avg('success', output_field=models.FloatField())
        )
        
        # 成本预警统计
        alert_stats = CostAlert.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).aggregate(
            total_alerts=Count('id'),
            active_alerts=Count('id', filter=models.Q(is_active=True)),
            triggered_alerts=Count('id', filter=models.Q(notification_sent=True))
        )
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'total': {
                'requests': total_stats['total_requests'] or 0,
                'cost': float(total_stats['total_cost'] or 0),
                'tokens': total_stats['total_tokens'] or 0,
                'unique_users': total_stats['unique_users'] or 0,
                'avg_response_time': total_stats['avg_response_time'] or 0,
                'success_rate': (total_stats['success_rate'] or 0) * 100
            },
            'alerts': alert_stats
        }
    
    async def _check_cost_alerts(self, user: User, cost: Decimal):
        """检查成本预警"""
        now = timezone.now()
        
        # 检查用户日限制
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_cost = AIUsageRecord.objects.filter(
            user=user,
            created_at__gte=today_start
        ).aggregate(total=Sum('cost'))['total'] or 0
        
        daily_limit = self.alert_thresholds['user_daily_limit']
        if today_cost >= daily_limit:
            await self._create_cost_alert(
                user=user,
                alert_type='user_daily_limit',
                threshold_amount=daily_limit,
                current_amount=today_cost,
                period_start=today_start,
                period_end=today_start + timedelta(days=1),
                message=f"用户日消费已达${today_cost:.2f}，超过限制${daily_limit:.2f}"
            )
        
        # 检查系统日限制（管理员预警）
        system_today_cost = AIUsageRecord.objects.filter(
            created_at__gte=today_start
        ).aggregate(total=Sum('cost'))['total'] or 0
        
        system_daily_limit = self.alert_thresholds['daily_limit']
        if system_today_cost >= system_daily_limit:
            await self._create_cost_alert(
                user=None,  # 系统级预警
                alert_type='system_daily_limit',
                threshold_amount=system_daily_limit,
                current_amount=system_today_cost,
                period_start=today_start,
                period_end=today_start + timedelta(days=1),
                message=f"系统日消费已达${system_today_cost:.2f}，超过限制${system_daily_limit:.2f}"
            )
    
    async def _create_cost_alert(
        self,
        alert_type: str,
        threshold_amount: float,
        current_amount: float,
        period_start: datetime,
        period_end: datetime,
        message: str,
        user: User = None
    ):
        """创建成本预警"""
        try:
            # 检查是否已存在相同预警
            existing_alert = CostAlert.objects.filter(
                user=user,
                alert_type=alert_type,
                period_start=period_start,
                is_active=True
            ).first()
            
            if existing_alert:
                # 更新现有预警
                existing_alert.current_amount = current_amount
                existing_alert.message = message
                existing_alert.save()
            else:
                # 创建新预警
                alert = CostAlert.objects.create(
                    user=user,
                    alert_type=alert_type,
                    threshold_amount=threshold_amount,
                    current_amount=current_amount,
                    period_start=period_start,
                    period_end=period_end,
                    message=message
                )
                
                # 发送通知（TODO: 实现通知机制）
                await self._send_cost_alert_notification(alert)
                
                logger.warning(f"成本预警触发: {alert_type}, 当前: ${current_amount:.2f}, 限制: ${threshold_amount:.2f}")
                
        except Exception as e:
            logger.error(f"创建成本预警失败: {e}")
    
    async def _send_cost_alert_notification(self, alert: CostAlert):
        """发送成本预警通知"""
        # TODO: 实现邮件、短信、Webhook等通知方式
        logger.info(f"发送成本预警通知: {alert.alert_type} - {alert.message}")
        
        # 标记已发送
        alert.notification_sent = True
        alert.save()
    
    async def _update_cache_statistics(self, user: User, cost: Decimal, tokens: int):
        """更新缓存统计"""
        today = timezone.now().date().isoformat()
        
        # 用户今日统计
        user_key = f"user_cost_today:{user.id}:{today}"
        current_cost = cache.get(user_key, 0)
        cache.set(user_key, current_cost + float(cost), self.cache_timeout)
        
        # 系统今日统计
        system_key = f"system_cost_today:{today}"
        current_system_cost = cache.get(system_key, 0)
        cache.set(system_key, current_system_cost + float(cost), self.cache_timeout)
    
    async def get_cached_daily_cost(self, user: User = None) -> float:
        """获取缓存的日消费"""
        today = timezone.now().date().isoformat()
        
        if user:
            key = f"user_cost_today:{user.id}:{today}"
        else:
            key = f"system_cost_today:{today}"
        
        return cache.get(key, 0.0)
    
    async def is_cost_limit_exceeded(self, user: User) -> bool:
        """检查是否超过成本限制"""
        daily_cost = await self.get_cached_daily_cost(user)
        limit = self.alert_thresholds['user_daily_limit']
        return daily_cost >= limit
