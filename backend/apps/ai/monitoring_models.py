"""
监控数据模型

用于存储服务健康状态、性能指标和历史数据
"""

import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

from .config_models import AIProvider


class ServiceHealthStatus(models.TextChoices):
    """服务健康状态"""
    HEALTHY = 'healthy', '健康'
    DEGRADED = 'degraded', '降级'
    UNHEALTHY = 'unhealthy', '不健康'
    UNKNOWN = 'unknown', '未知'


class ServiceHealthRecord(models.Model):
    """服务健康记录"""
    
    # 基础信息
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_name = models.CharField(max_length=100, help_text="服务名称")
    provider = models.ForeignKey(
        AIProvider, 
        on_delete=models.CASCADE, 
        related_name='health_records',
        null=True, blank=True,
        help_text="关联的AI提供商"
    )
    
    # 健康状态
    status = models.CharField(
        max_length=20,
        choices=ServiceHealthStatus.choices,
        default=ServiceHealthStatus.UNKNOWN,
        help_text="健康状态"
    )
    is_healthy = models.BooleanField(default=True, help_text="是否健康")
    
    # 性能指标
    response_time = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="响应时间(秒)"
    )
    error_message = models.TextField(blank=True, help_text="错误信息")
    consecutive_failures = models.IntegerField(default=0, help_text="连续失败次数")
    
    # 检查信息
    check_timestamp = models.DateTimeField(auto_now_add=True, help_text="检查时间")
    check_type = models.CharField(
        max_length=50,
        choices=[
            ('health_check', '健康检查'),
            ('api_call', 'API调用'),
            ('scheduled', '定时检查'),
        ],
        default='health_check',
        help_text="检查类型"
    )
    
    # 额外数据
    metadata = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder,
        help_text="额外的监控数据"
    )
    
    class Meta:
        db_table = 'ai_service_health_records'
        ordering = ['-check_timestamp']
        indexes = [
            models.Index(fields=['service_name', '-check_timestamp']),
            models.Index(fields=['provider', '-check_timestamp']),
            models.Index(fields=['status', '-check_timestamp']),
            models.Index(fields=['-check_timestamp']),  # 用于时间范围查询
        ]
    
    def __str__(self):
        return f"{self.service_name} - {self.status} @ {self.check_timestamp}"
    
    @classmethod
    def cleanup_old_records(cls, days: int = 7):
        """清理旧记录"""
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = cls.objects.filter(check_timestamp__lt=cutoff_date).delete()[0]
        return deleted_count
    
    @classmethod
    def get_latest_status(cls, service_name: str) -> Optional['ServiceHealthRecord']:
        """获取服务的最新状态"""
        return cls.objects.filter(service_name=service_name).first()
    
    @classmethod
    def get_uptime_percentage(cls, service_name: str, hours: int = 24) -> float:
        """计算服务运行时间百分比"""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        records = cls.objects.filter(
            service_name=service_name,
            check_timestamp__gte=cutoff_time
        )
        
        total_count = records.count()
        if total_count == 0:
            return 0.0
        
        healthy_count = records.filter(is_healthy=True).count()
        return (healthy_count / total_count) * 100


class PerformanceMetric(models.Model):
    """性能指标记录"""
    
    # 基础信息
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_name = models.CharField(max_length=100, help_text="服务名称")
    provider = models.ForeignKey(
        AIProvider,
        on_delete=models.CASCADE,
        related_name='performance_metrics',
        null=True, blank=True,
        help_text="关联的AI提供商"
    )
    
    # 时间信息
    timestamp = models.DateTimeField(auto_now_add=True, help_text="记录时间")
    period_start = models.DateTimeField(help_text="统计周期开始时间")
    period_end = models.DateTimeField(help_text="统计周期结束时间")
    
    # 请求统计
    total_requests = models.IntegerField(default=0, help_text="总请求数")
    successful_requests = models.IntegerField(default=0, help_text="成功请求数")
    failed_requests = models.IntegerField(default=0, help_text="失败请求数")
    
    # 响应时间统计
    avg_response_time = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="平均响应时间(秒)"
    )
    min_response_time = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="最小响应时间(秒)"
    )
    max_response_time = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="最大响应时间(秒)"
    )
    p95_response_time = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="95分位响应时间(秒)"
    )
    
    # Token统计
    total_input_tokens = models.BigIntegerField(default=0, help_text="总输入Token数")
    total_output_tokens = models.BigIntegerField(default=0, help_text="总输出Token数")
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=4,
        default=Decimal('0.0000'),
        help_text="总成本(USD)"
    )
    
    # 计算字段
    qps = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="每秒请求数"
    )
    error_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="错误率(%)"
    )
    success_rate = models.FloatField(
        default=100.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="成功率(%)"
    )
    
    # 额外数据
    metadata = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder,
        help_text="额外的性能数据"
    )
    
    class Meta:
        db_table = 'ai_performance_metrics'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['service_name', '-timestamp']),
            models.Index(fields=['provider', '-timestamp']),
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['-timestamp']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['service_name', 'period_start', 'period_end'],
                name='unique_metric_per_service_period'
            )
        ]
    
    def __str__(self):
        return f"{self.service_name} - {self.qps} QPS @ {self.timestamp}"
    
    def save(self, *args, **kwargs):
        """保存时自动计算衍生字段"""
        # 计算QPS
        period_seconds = (self.period_end - self.period_start).total_seconds()
        if period_seconds > 0:
            self.qps = self.total_requests / period_seconds
        
        # 计算错误率和成功率
        if self.total_requests > 0:
            self.error_rate = (self.failed_requests / self.total_requests) * 100
            self.success_rate = (self.successful_requests / self.total_requests) * 100
        
        super().save(*args, **kwargs)
    
    @classmethod
    def cleanup_old_metrics(cls, days: int = 30):
        """清理旧的性能指标"""
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = cls.objects.filter(timestamp__lt=cutoff_date).delete()[0]
        return deleted_count
    
    @classmethod
    def get_service_summary(cls, service_name: str, hours: int = 24) -> Dict[str, Any]:
        """获取服务性能摘要"""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        metrics = cls.objects.filter(
            service_name=service_name,
            timestamp__gte=cutoff_time
        )
        
        if not metrics.exists():
            return {
                'service_name': service_name,
                'period_hours': hours,
                'total_requests': 0,
                'avg_qps': 0.0,
                'avg_response_time': 0.0,
                'avg_error_rate': 0.0,
                'total_cost': 0.0
            }
        
        # 聚合统计
        from django.db.models import Sum, Avg
        aggregated = metrics.aggregate(
            total_requests=Sum('total_requests'),
            avg_qps=Avg('qps'),
            avg_response_time=Avg('avg_response_time'),
            avg_error_rate=Avg('error_rate'),
            total_cost=Sum('total_cost')
        )
        
        return {
            'service_name': service_name,
            'period_hours': hours,
            'total_requests': aggregated['total_requests'] or 0,
            'avg_qps': round(aggregated['avg_qps'] or 0.0, 2),
            'avg_response_time': round(aggregated['avg_response_time'] or 0.0, 3),
            'avg_error_rate': round(aggregated['avg_error_rate'] or 0.0, 2),
            'total_cost': float(aggregated['total_cost'] or 0.0)
        }


class SystemAlert(models.Model):
    """系统告警记录"""
    
    # 告警级别
    class AlertLevel(models.TextChoices):
        INFO = 'info', '信息'
        WARNING = 'warning', '警告'
        ERROR = 'error', '错误'
        CRITICAL = 'critical', '严重'
    
    # 告警状态
    class AlertStatus(models.TextChoices):
        ACTIVE = 'active', '活跃'
        RESOLVED = 'resolved', '已解决'
        ACKNOWLEDGED = 'acknowledged', '已确认'
        SUPPRESSED = 'suppressed', '已抑制'
    
    # 基础信息
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=50, help_text="告警类型")
    level = models.CharField(
        max_length=20,
        choices=AlertLevel.choices,
        default=AlertLevel.WARNING,
        help_text="告警级别"
    )
    status = models.CharField(
        max_length=20,
        choices=AlertStatus.choices,
        default=AlertStatus.ACTIVE,
        help_text="告警状态"
    )
    
    # 告警内容
    title = models.CharField(max_length=200, help_text="告警标题")
    message = models.TextField(help_text="告警详情")
    service_name = models.CharField(max_length=100, blank=True, help_text="相关服务")
    provider = models.ForeignKey(
        AIProvider,
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True, blank=True,
        help_text="关联的AI提供商"
    )
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="解决时间")
    
    # 告警规则
    rule_name = models.CharField(max_length=100, blank=True, help_text="触发的规则名称")
    threshold_value = models.FloatField(null=True, blank=True, help_text="阈值")
    actual_value = models.FloatField(null=True, blank=True, help_text="实际值")
    
    # 额外数据
    metadata = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder,
        help_text="告警相关的额外数据"
    )
    
    class Meta:
        db_table = 'ai_system_alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['level', '-created_at']),
            models.Index(fields=['service_name', '-created_at']),
            models.Index(fields=['provider', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.level.upper()}: {self.title}"
    
    def resolve(self, message: str = ""):
        """解决告警"""
        self.status = self.AlertStatus.RESOLVED
        self.resolved_at = timezone.now()
        if message:
            self.message += f"\n\n解决说明: {message}"
        self.save()
    
    def acknowledge(self, user: Optional['User'] = None):
        """确认告警"""
        self.status = self.AlertStatus.ACKNOWLEDGED
        if user:
            self.metadata['acknowledged_by'] = user.username
        self.metadata['acknowledged_at'] = timezone.now().isoformat()
        self.save()
    
    @classmethod
    def create_alert(
        cls,
        alert_type: str,
        title: str,
        message: str,
        level: str = AlertLevel.WARNING,
        service_name: str = "",
        provider: Optional[AIProvider] = None,
        **metadata
    ) -> 'SystemAlert':
        """创建告警"""
        return cls.objects.create(
            alert_type=alert_type,
            title=title,
            message=message,
            level=level,
            service_name=service_name,
            provider=provider,
            metadata=metadata
        )
    
    @classmethod
    def get_active_alerts(cls) -> models.QuerySet:
        """获取活跃告警"""
        return cls.objects.filter(status=cls.AlertStatus.ACTIVE)
    
    @classmethod
    def cleanup_old_alerts(cls, days: int = 30):
        """清理旧告警"""
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = cls.objects.filter(
            created_at__lt=cutoff_date,
            status__in=[cls.AlertStatus.RESOLVED, cls.AlertStatus.SUPPRESSED]
        ).delete()[0]
        return deleted_count

