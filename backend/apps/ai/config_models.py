"""
AI配置管理数据库模型

定义AI服务提供商、API密钥、模型配置、Token使用统计等核心模型
"""

import json
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.serializers.json import DjangoJSONEncoder
from cryptography.fernet import Fernet
from django.conf import settings
from django_cryptography.fields import encrypt


class AIProviderType(models.TextChoices):
    """AI服务提供商类型"""
    OPENAI = 'openai', 'OpenAI'
    ANTHROPIC = 'anthropic', 'Anthropic (Claude)'
    GOOGLE = 'google', 'Google (Gemini)'
    AZURE = 'azure', 'Azure OpenAI'
    LOCAL = 'local', 'Local (Ollama)'
    CHENMOAI = 'chenmoai', 'ChenmoAI'
    OPENROUTER = 'openrouter', 'OpenRouter'
    SILICONFLOW = 'siliconflow', 'SiliconFlow'
    CUSTOM = 'custom', 'Custom Provider'


class AIProvider(models.Model):
    """AI服务提供商配置"""
    
    # 基础信息
    name = models.CharField(max_length=100, unique=True, help_text="提供商名称")
    provider_type = models.CharField(
        max_length=20, 
        choices=AIProviderType.choices,
        help_text="提供商类型"
    )
    display_name = models.CharField(max_length=100, help_text="显示名称")
    description = models.TextField(blank=True, help_text="提供商描述")
    
    # API配置
    base_url = models.URLField(help_text="API基础URL")
    api_version = models.CharField(max_length=20, blank=True, help_text="API版本")
    
    # 状态信息
    is_active = models.BooleanField(default=True, help_text="是否启用")
    is_healthy = models.BooleanField(default=False, help_text="健康状态")
    last_health_check = models.DateTimeField(null=True, blank=True)
    health_check_interval = models.IntegerField(default=300, help_text="健康检查间隔(秒)")
    
    # 性能指标
    avg_response_time = models.FloatField(null=True, blank=True, help_text="平均响应时间(秒)")
    success_rate = models.FloatField(null=True, blank=True, help_text="成功率(%)")
    
    # 配置信息
    config_schema = models.JSONField(default=dict, encoder=DjangoJSONEncoder, help_text="配置模式")
    default_config = models.JSONField(default=dict, encoder=DjangoJSONEncoder, help_text="默认配置")
    
    # 限制信息
    rate_limit_per_minute = models.IntegerField(null=True, blank=True, help_text="每分钟请求限制")
    rate_limit_per_day = models.IntegerField(null=True, blank=True, help_text="每日请求限制")
    max_tokens_per_request = models.IntegerField(null=True, blank=True, help_text="单次请求最大Token")
    
    # 成本信息
    cost_per_1k_input_tokens = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True,
        help_text="每1K输入Token成本(USD)"
    )
    cost_per_1k_output_tokens = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True,
        help_text="每1K输出Token成本(USD)"
    )
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'ai_providers'
        ordering = ['name']
        indexes = [
            models.Index(fields=['provider_type', 'is_active']),
            models.Index(fields=['is_active', 'is_healthy']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.provider_type})"
    
    def update_health_status(self, is_healthy: bool, response_time: float = None):
        """更新健康状态"""
        self.is_healthy = is_healthy
        self.last_health_check = datetime.now()
        if response_time is not None:
            # 计算移动平均响应时间
            if self.avg_response_time is None:
                self.avg_response_time = response_time
            else:
                self.avg_response_time = (self.avg_response_time * 0.8) + (response_time * 0.2)
        self.save(update_fields=['is_healthy', 'last_health_check', 'avg_response_time'])


class APIKey(models.Model):
    """API密钥管理"""
    
    # 关联信息
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE, related_name='api_keys')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='api_keys')
    
    # 密钥信息
    name = models.CharField(max_length=100, help_text="密钥名称")
    key_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    encrypted_key = encrypt(models.CharField(max_length=500, help_text="加密后的API密钥"))
    key_prefix = models.CharField(max_length=20, blank=True, help_text="密钥前缀(用于显示)")
    
    # 状态信息
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="是否为默认密钥")
    
    # 使用限制
    usage_limit_daily = models.IntegerField(null=True, blank=True, help_text="每日使用限制")
    usage_limit_monthly = models.IntegerField(null=True, blank=True, help_text="每月使用限制")
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="密钥过期时间")
    
    class Meta:
        db_table = 'ai_api_keys'
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['provider', 'user', 'is_active']),
            models.Index(fields=['is_active', 'is_default']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'user', 'is_default'],
                condition=models.Q(is_default=True),
                name='unique_default_key_per_provider_user'
            )
        ]
    
    def __str__(self):
        return f"{self.name} - {self.provider.display_name}"
    
    def set_key(self, raw_key: str):
        """设置API密钥（自动加密）"""
        self.encrypted_key = raw_key  # django-cryptography自动加密
        self.key_prefix = self._generate_key_prefix(raw_key)
    
    def get_key(self) -> str:
        """获取解密的API密钥"""
        return self.encrypted_key  # django-cryptography自动解密
    
    def _generate_key_prefix(self, raw_key: str) -> str:
        """生成密钥前缀用于显示"""
        if len(raw_key) <= 8:
            return raw_key[:4] + "***"
        return raw_key[:4] + "..." + raw_key[-4:]
    
    @property
    def masked_key(self) -> str:
        """返回掩码显示的密钥"""
        return self.key_prefix if self.key_prefix else "****...****"
    
    def validate_key(self) -> bool:
        """验证API密钥格式是否有效"""
        try:
            key = self.get_key()
            # 基础格式验证
            if not key or len(key) < 10:
                return False
            
            # 根据提供商类型进行特定验证
            if self.provider.provider_type == AIProviderType.OPENAI:
                return key.startswith('sk-') and len(key) >= 40
            elif self.provider.provider_type == AIProviderType.ANTHROPIC:
                return key.startswith('sk-ant-') and len(key) >= 40
            elif self.provider.provider_type == AIProviderType.GOOGLE:
                return len(key) >= 20  # Google API keys vary in format
            elif self.provider.provider_type == AIProviderType.OPENROUTER:
                return key.startswith('sk-or-') and len(key) >= 40
            elif self.provider.provider_type == AIProviderType.CHENMOAI:
                return key.startswith('sk-') and len(key) >= 20
            else:
                return len(key) >= 10  # 通用最小长度验证
        except Exception:
            return False
    
    def is_expired(self) -> bool:
        """检查密钥是否过期"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class AIModel(models.Model):
    """AI模型配置"""
    
    # 基础信息
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE, related_name='models')
    model_id = models.CharField(max_length=100, help_text="模型ID")
    display_name = models.CharField(max_length=100, help_text="显示名称")
    description = models.TextField(blank=True, help_text="模型描述")
    
    # 模型特性
    max_tokens = models.IntegerField(help_text="最大Token数")
    supports_streaming = models.BooleanField(default=True, help_text="是否支持流式响应")
    supports_functions = models.BooleanField(default=False, help_text="是否支持函数调用")
    supports_vision = models.BooleanField(default=False, help_text="是否支持视觉输入")
    
    # 成本信息
    cost_per_1k_input_tokens = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True,
        help_text="每1K输入Token成本(USD)"
    )
    cost_per_1k_output_tokens = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True,
        help_text="每1K输出Token成本(USD)"
    )
    
    # 状态信息
    is_active = models.BooleanField(default=True)
    is_recommended = models.BooleanField(default=False, help_text="是否推荐使用")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_models'
        ordering = ['-is_recommended', 'display_name']
        indexes = [
            models.Index(fields=['provider', 'is_active']),
            models.Index(fields=['is_active', 'is_recommended']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'model_id'],
                name='unique_model_per_provider'
            )
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.provider.display_name})"


class ModelConfig(models.Model):
    """模型配置"""
    
    # 关联信息
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='model_configs')
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='configs')
    
    # 配置信息
    config_name = models.CharField(max_length=100, help_text="配置名称")
    
    # 模型参数
    temperature = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0)],
        help_text="温度参数(0.0-2.0)"
    )
    max_tokens = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1)],
        help_text="最大生成Token数"
    )
    top_p = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Top-p参数(0.0-1.0)"
    )
    frequency_penalty = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-2.0), MaxValueValidator(2.0)],
        help_text="频率惩罚(-2.0-2.0)"
    )
    presence_penalty = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-2.0), MaxValueValidator(2.0)],
        help_text="存在惩罚(-2.0-2.0)"
    )
    
    # 系统提示
    system_prompt = models.TextField(blank=True, help_text="系统提示")
    
    # 其他配置
    custom_config = models.JSONField(default=dict, encoder=DjangoJSONEncoder, help_text="自定义配置")
    
    # 状态信息
    is_default = models.BooleanField(default=False, help_text="是否为默认配置")
    is_active = models.BooleanField(default=True)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ai_model_configs'
        ordering = ['-is_default', '-last_used', '-created_at']
        indexes = [
            models.Index(fields=['user', 'model', 'is_active']),
            models.Index(fields=['is_active', 'is_default']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'model', 'is_default'],
                condition=models.Q(is_default=True),
                name='unique_default_config_per_user_model'
            )
        ]
    
    def __str__(self):
        return f"{self.config_name} - {self.model.display_name}"


class TokenUsage(models.Model):
    """Token使用统计"""
    
    # 关联信息
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='token_usage')
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE, related_name='token_usage')
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='token_usage')
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name='token_usage')
    
    # 请求信息
    request_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    conversation_id = models.CharField(max_length=100, blank=True, help_text="对话ID")
    
    # Token统计
    input_tokens = models.IntegerField(help_text="输入Token数")
    output_tokens = models.IntegerField(help_text="输出Token数")
    total_tokens = models.IntegerField(help_text="总Token数")
    
    # 成本信息
    input_cost = models.DecimalField(max_digits=10, decimal_places=6, help_text="输入成本(USD)")
    output_cost = models.DecimalField(max_digits=10, decimal_places=6, help_text="输出成本(USD)")
    total_cost = models.DecimalField(max_digits=10, decimal_places=6, help_text="总成本(USD)")
    
    # 性能信息
    response_time = models.FloatField(help_text="响应时间(秒)")
    is_streaming = models.BooleanField(default=False, help_text="是否为流式响应")
    
    # 请求状态
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', '成功'),
            ('error', '错误'),
            ('timeout', '超时'),
            ('rate_limit', '限流'),
        ],
        default='success'
    )
    error_message = models.TextField(blank=True, help_text="错误信息")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_token_usage'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['provider', '-created_at']),
            models.Index(fields=['model', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['created_at']),  # 用于时间范围查询
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.model.display_name} - {self.total_tokens} tokens"
    
    def save(self, *args, **kwargs):
        # 自动计算总Token数
        self.total_tokens = self.input_tokens + self.output_tokens
        # 自动计算总成本
        self.total_cost = self.input_cost + self.output_cost
        super().save(*args, **kwargs)


class FailoverStrategy(models.Model):
    """故障转移策略"""
    
    # 基础信息
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='failover_strategies')
    name = models.CharField(max_length=100, help_text="策略名称")
    description = models.TextField(blank=True, help_text="策略描述")
    
    # 主要提供商
    primary_provider = models.ForeignKey(
        AIProvider, 
        on_delete=models.CASCADE, 
        related_name='primary_strategies',
        help_text="主要提供商"
    )
    primary_model = models.ForeignKey(
        AIModel,
        on_delete=models.CASCADE,
        related_name='primary_strategies',
        help_text="主要模型"
    )
    
    # 故障转移配置
    fallback_providers = models.ManyToManyField(
        AIProvider,
        through='FailoverRule',
        related_name='fallback_strategies',
        help_text="备用提供商"
    )
    
    # 触发条件
    max_retries = models.IntegerField(default=3, help_text="最大重试次数")
    retry_delay = models.IntegerField(default=1, help_text="重试延迟(秒)")
    timeout_threshold = models.FloatField(default=30.0, help_text="超时阈值(秒)")
    error_rate_threshold = models.FloatField(default=0.5, help_text="错误率阈值(0.0-1.0)")
    
    # 状态信息
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="是否为默认策略")
    
    # 统计信息
    total_requests = models.IntegerField(default=0)
    successful_requests = models.IntegerField(default=0)
    fallback_count = models.IntegerField(default=0)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ai_failover_strategies'
        ordering = ['-is_default', '-last_used', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['is_active', 'is_default']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_default'],
                condition=models.Q(is_default=True),
                name='unique_default_strategy_per_user'
            )
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    def get_fallback_rate(self) -> float:
        """获取故障转移率"""
        if self.total_requests == 0:
            return 0.0
        return self.fallback_count / self.total_requests


class FailoverRule(models.Model):
    """故障转移规则"""
    
    # 关联信息
    strategy = models.ForeignKey(FailoverStrategy, on_delete=models.CASCADE, related_name='rules')
    fallback_provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE)
    fallback_model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    
    # 规则配置
    priority = models.IntegerField(help_text="优先级(数字越小优先级越高)")
    
    # 触发条件
    trigger_errors = models.JSONField(
        default=list,
        encoder=DjangoJSONEncoder,
        help_text="触发的错误类型列表"
    )
    
    # 状态信息
    is_active = models.BooleanField(default=True)
    
    # 统计信息
    trigger_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ai_failover_rules'
        ordering = ['priority']
        indexes = [
            models.Index(fields=['strategy', 'priority', 'is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['strategy', 'priority'],
                name='unique_priority_per_strategy'
            )
        ]
    
    def __str__(self):
        return f"{self.strategy.name} -> {self.fallback_provider.display_name} (P{self.priority})"


class UsageQuota(models.Model):
    """使用配额管理"""
    
    # 关联信息
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='usage_quotas')
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE, related_name='usage_quotas')
    
    # 配额设置
    quota_type = models.CharField(
        max_length=20,
        choices=[
            ('daily', '每日配额'),
            ('weekly', '每周配额'),
            ('monthly', '每月配额'),
            ('total', '总配额'),
        ],
        default='monthly'
    )
    
    # Token配额
    token_limit = models.IntegerField(help_text="Token限制")
    token_used = models.IntegerField(default=0, help_text="已使用Token")
    
    # 成本配额
    cost_limit = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="成本限制(USD)"
    )
    cost_used = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('0.00'),
        help_text="已使用成本(USD)"
    )
    
    # 请求配额
    request_limit = models.IntegerField(null=True, blank=True, help_text="请求次数限制")
    request_used = models.IntegerField(default=0, help_text="已使用请求次数")
    
    # 状态信息
    is_active = models.BooleanField(default=True)
    is_exceeded = models.BooleanField(default=False, help_text="是否超出配额")
    
    # 时间信息
    period_start = models.DateTimeField(help_text="周期开始时间")
    period_end = models.DateTimeField(help_text="周期结束时间")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_usage_quotas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'provider', 'quota_type']),
            models.Index(fields=['is_active', 'is_exceeded']),
            models.Index(fields=['period_end']),  # 用于清理过期配额
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'provider', 'quota_type', 'period_start'],
                name='unique_quota_per_user_provider_period'
            )
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.provider.display_name} - {self.quota_type}"
    
    def get_token_usage_percentage(self) -> float:
        """获取Token使用百分比"""
        if self.token_limit == 0:
            return 0.0
        return (self.token_used / self.token_limit) * 100
    
    def get_cost_usage_percentage(self) -> float:
        """获取成本使用百分比"""
        if not self.cost_limit or self.cost_limit == 0:
            return 0.0
        return float((self.cost_used / self.cost_limit) * 100)
    
    def get_request_usage_percentage(self) -> float:
        """获取请求使用百分比"""
        if not self.request_limit or self.request_limit == 0:
            return 0.0
        return (self.request_used / self.request_limit) * 100
    
    def check_quota_exceeded(self) -> bool:
        """检查是否超出配额"""
        exceeded = False
        
        if self.token_used >= self.token_limit:
            exceeded = True
        
        if self.cost_limit and self.cost_used >= self.cost_limit:
            exceeded = True
        
        if self.request_limit and self.request_used >= self.request_limit:
            exceeded = True
        
        if exceeded != self.is_exceeded:
            self.is_exceeded = exceeded
            self.save(update_fields=['is_exceeded'])
        
        return exceeded
