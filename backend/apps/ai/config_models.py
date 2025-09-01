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
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


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


class PromptTemplate(models.Model):
    """系统提示模板"""
    
    # 基础信息
    name = models.CharField(max_length=100, help_text="模板名称")
    description = models.TextField(blank=True, help_text="模板描述")
    content = models.TextField(help_text="模板内容")
    
    # 分类信息
    category = models.CharField(
        max_length=50, 
        choices=[
            ('general', '通用'),
            ('coding', '代码助手'),
            ('writing', '写作助手'),
            ('analysis', '分析助手'),
            ('translation', '翻译助手'),
            ('creative', '创意助手'),
            ('custom', '自定义'),
        ],
        default='general',
        help_text="模板分类"
    )
    
    # 状态信息
    is_public = models.BooleanField(default=False, help_text="是否为公共模板")
    is_system = models.BooleanField(default=False, help_text="是否为系统内置模板")
    is_active = models.BooleanField(default=True)
    
    # 使用统计
    usage_count = models.IntegerField(default=0, help_text="使用次数")
    
    # 关联信息
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='prompt_templates')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_prompt_templates'
        ordering = ['-is_system', '-usage_count', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_public', 'is_active']),
            models.Index(fields=['created_by', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class ModelConfig(models.Model):
    """模型配置"""
    
    # 关联信息
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='model_configs')
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE, related_name='model_configs')
    model = models.CharField(max_length=100, help_text="模型ID")
    
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
    
    # 系统提示配置
    prompt_template = models.ForeignKey(
        PromptTemplate, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='model_configs',
        help_text="系统提示模板"
    )
    system_prompt_template = models.TextField(blank=True, help_text="系统提示内容")
    
    # 高级参数
    advanced_params = models.JSONField(
        default=dict, 
        encoder=DjangoJSONEncoder, 
        help_text="高级参数 (seed, stop_words, logit_bias, reserved_tokens等)"
    )
    
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
    
    # 自动降级与恢复检测配置
    active_provider = models.ForeignKey(
        AIProvider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='active_strategies',
        help_text="当前活跃的提供商"
    )
    strategy_mode = models.CharField(
        max_length=20,
        choices=[
            ('priority', '优先级模式'),
            ('round_robin', '轮询模式'),
        ],
        default='priority',
        help_text="策略模式"
    )
    
    # 阈值配置
    fail_threshold = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="失败阈值（连续失败次数）"
    )
    recovery_threshold = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="恢复阈值（连续成功次数）"
    )
    cooldown = models.IntegerField(
        default=300,
        validators=[MinValueValidator(0), MaxValueValidator(3600)],
        help_text="冷却时间（秒）"
    )
    jitter_window = models.IntegerField(
        default=60,
        validators=[MinValueValidator(0), MaxValueValidator(300)],
        help_text="抖动窗口（秒）"
    )
    
    # 触发条件
    max_retries = models.IntegerField(default=3, help_text="最大重试次数")
    retry_delay = models.IntegerField(default=1, help_text="重试延迟(秒)")
    timeout_threshold = models.FloatField(default=30.0, help_text="超时阈值(秒)")
    error_rate_threshold = models.FloatField(default=0.5, help_text="错误率阈值(0.0-1.0)")
    
    # 状态信息
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="是否为默认策略")
    last_switch_at = models.DateTimeField(null=True, blank=True, help_text="最后切换时间")
    
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
            models.Index(fields=['active_provider']),
            models.Index(fields=['last_switch_at']),
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
    
    def save(self, *args, **kwargs):
        """保存时设置默认活跃提供商"""
        if not self.active_provider:
            self.active_provider = self.primary_provider
        super().save(*args, **kwargs)


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


class FallbackAuditLog(models.Model):
    """故障转移审计日志"""
    
    ACTION_TYPES = [
        ('auto_switch', '自动切换'),
        ('manual_switch', '手动切换'),
        ('recovery', '恢复'),
        ('health_check', '健康检查'),
    ]
    
    strategy = models.ForeignKey(
        FailoverStrategy,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        verbose_name='故障转移策略'
    )
    
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name='操作类型'
    )
    
    from_provider = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='源提供商'
    )
    
    to_provider = models.CharField(
        max_length=50,
        verbose_name='目标提供商'
    )
    
    reason = models.TextField(
        verbose_name='切换原因'
    )
    
    operator = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='操作者'
    )
    
    metadata = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder,
        verbose_name='元数据',
        help_text='额外的上下文信息'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        db_table = 'ai_fallback_audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['strategy', 'action_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.strategy.name}: {self.from_provider} -> {self.to_provider}"


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


class ProviderHealthStatus(models.Model):
    """提供商健康状态记录"""
    
    # 关联信息
    strategy = models.ForeignKey(
        FailoverStrategy,
        on_delete=models.CASCADE,
        related_name='health_statuses',
        help_text="关联的故障转移策略"
    )
    provider = models.ForeignKey(
        AIProvider,
        on_delete=models.CASCADE,
        related_name='health_statuses',
        help_text="提供商"
    )
    
    # 健康状态计数
    success_count = models.IntegerField(default=0, help_text="成功次数")
    failure_count = models.IntegerField(default=0, help_text="失败次数")
    consecutive_failures = models.IntegerField(default=0, help_text="连续失败次数")
    consecutive_successes = models.IntegerField(default=0, help_text="连续成功次数")
    
    # 时间信息
    last_success_at = models.DateTimeField(null=True, blank=True, help_text="最后成功时间")
    last_failure_at = models.DateTimeField(null=True, blank=True, help_text="最后失败时间")
    last_heartbeat_at = models.DateTimeField(null=True, blank=True, help_text="最后心跳时间")
    
    # 性能指标
    avg_response_time = models.FloatField(null=True, blank=True, help_text="平均响应时间(秒)")
    min_response_time = models.FloatField(null=True, blank=True, help_text="最小响应时间(秒)")
    max_response_time = models.FloatField(null=True, blank=True, help_text="最大响应时间(秒)")
    
    # 状态信息
    is_healthy = models.BooleanField(default=True, help_text="是否健康")
    is_available = models.BooleanField(default=True, help_text="是否可用")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_provider_health_statuses'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['strategy', 'provider']),
            models.Index(fields=['is_healthy', 'is_available']),
            models.Index(fields=['last_heartbeat_at']),
        ]
        unique_together = ['strategy', 'provider']
    
    def __str__(self):
        return f"{self.strategy.name} - {self.provider.display_name}"
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total
    
    def get_total_requests(self) -> int:
        """获取总请求数"""
        return self.success_count + self.failure_count
    
    def record_success(self, response_time: float = None):
        """记录成功请求"""
        self.success_count += 1
        self.consecutive_successes += 1
        self.consecutive_failures = 0
        self.last_success_at = timezone.now()
        self.last_heartbeat_at = timezone.now()
        self.is_healthy = True
        
        # 更新响应时间统计
        if response_time is not None:
            if self.avg_response_time is None:
                self.avg_response_time = response_time
                self.min_response_time = response_time
                self.max_response_time = response_time
            else:
                # 计算移动平均
                total_requests = self.get_total_requests()
                self.avg_response_time = (
                    (self.avg_response_time * (total_requests - 1) + response_time) / total_requests
                )
                self.min_response_time = min(self.min_response_time, response_time)
                self.max_response_time = max(self.max_response_time, response_time)
        
        self.save()
    
    def record_failure(self, response_time: float = None):
        """记录失败请求"""
        self.failure_count += 1
        self.consecutive_failures += 1
        self.consecutive_successes = 0
        self.last_failure_at = timezone.now()
        self.last_heartbeat_at = timezone.now()
        
        # 如果连续失败达到阈值，标记为不健康
        if self.consecutive_failures >= self.strategy.fail_threshold:
            self.is_healthy = False
        
        # 更新响应时间统计
        if response_time is not None:
            if self.avg_response_time is None:
                self.avg_response_time = response_time
                self.min_response_time = response_time
                self.max_response_time = response_time
            else:
                total_requests = self.get_total_requests()
                self.avg_response_time = (
                    (self.avg_response_time * (total_requests - 1) + response_time) / total_requests
                )
                self.min_response_time = min(self.min_response_time, response_time)
                self.max_response_time = max(self.max_response_time, response_time)
        
        self.save()
    
    def should_failover(self) -> bool:
        """判断是否应该故障转移"""
        return (
            self.consecutive_failures >= self.strategy.fail_threshold and
            self.is_available
        )
    
    def should_recover(self) -> bool:
        """判断是否应该恢复"""
        return (
            self.consecutive_successes >= self.strategy.recovery_threshold and
            self.is_healthy
        )
    
    def is_in_cooldown(self) -> bool:
        """判断是否在冷却期内"""
        if not self.strategy.last_switch_at:
            return False
        
        cooldown_end = self.strategy.last_switch_at + timedelta(seconds=self.strategy.cooldown)
        return timezone.now() < cooldown_end
    
    def is_in_jitter_window(self) -> bool:
        """判断是否在抖动窗口内"""
        if not self.strategy.last_switch_at:
            return False
        
        jitter_end = self.strategy.last_switch_at + timedelta(seconds=self.strategy.jitter_window)
        return timezone.now() < jitter_end


class UserSettings(models.Model):
    """用户设置模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    
    # 个人信息设置
    display_name = models.CharField(max_length=100, blank=True, verbose_name='显示名称')
    avatar_url = models.URLField(blank=True, verbose_name='头像URL')
    bio = models.TextField(blank=True, verbose_name='个人简介')
    
    # 偏好设置
    theme = models.CharField(
        max_length=20, 
        choices=[('light', '浅色'), ('dark', '深色'), ('auto', '自动')],
        default='auto',
        verbose_name='主题'
    )
    language = models.CharField(
        max_length=10,
        choices=[('zh-CN', '中文'), ('en-US', 'English')],
        default='zh-CN',
        verbose_name='语言'
    )
    timezone = models.CharField(max_length=50, default='Asia/Shanghai', verbose_name='时区')
    
    # 通知设置
    email_notifications = models.BooleanField(default=True, verbose_name='邮件通知')
    push_notifications = models.BooleanField(default=True, verbose_name='推送通知')
    notification_frequency = models.CharField(
        max_length=20,
        choices=[('immediate', '立即'), ('daily', '每日'), ('weekly', '每周')],
        default='immediate',
        verbose_name='通知频率'
    )
    
    # 安全设置
    two_factor_enabled = models.BooleanField(default=False, verbose_name='双因素认证')
    session_timeout = models.IntegerField(default=30, verbose_name='会话超时(分钟)')
    login_notifications = models.BooleanField(default=True, verbose_name='登录通知')
    
    # 系统设置
    auto_save = models.BooleanField(default=True, verbose_name='自动保存')
    debug_mode = models.BooleanField(default=False, verbose_name='调试模式')
    analytics_enabled = models.BooleanField(default=True, verbose_name='启用分析')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户设置'
        verbose_name_plural = '用户设置'
    
    def __str__(self):
        return f"{self.user.username} 的设置"


class SystemConfig(models.Model):
    """系统配置模型"""
    key = models.CharField(max_length=100, unique=True, verbose_name='配置键')
    value = models.JSONField(verbose_name='配置值')
    description = models.TextField(blank=True, verbose_name='配置描述')
    category = models.CharField(
        max_length=50,
        choices=[
            ('general', '通用'),
            ('security', '安全'),
            ('performance', '性能'),
            ('integration', '集成'),
            ('notification', '通知')
        ],
        default='general',
        verbose_name='配置分类'
    )
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
    
    def __str__(self):
        return f"{self.key}: {self.value}"


class LoginHistory(models.Model):
    """登录历史模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history', verbose_name='用户')
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.TextField(verbose_name='用户代理')
    location = models.CharField(max_length=100, blank=True, verbose_name='登录地点')
    device_type = models.CharField(
        max_length=20,
        choices=[('desktop', '桌面'), ('mobile', '移动'), ('tablet', '平板')],
        verbose_name='设备类型'
    )
    browser = models.CharField(max_length=50, blank=True, verbose_name='浏览器')
    os = models.CharField(max_length=50, blank=True, verbose_name='操作系统')
    success = models.BooleanField(default=True, verbose_name='登录成功')
    login_time = models.DateTimeField(auto_now_add=True, verbose_name='登录时间')
    
    class Meta:
        verbose_name = '登录历史'
        verbose_name_plural = '登录历史'
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


class DeviceSession(models.Model):
    """设备会话模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_sessions', verbose_name='用户')
    session_key = models.CharField(max_length=100, unique=True, verbose_name='会话键')
    device_name = models.CharField(max_length=100, verbose_name='设备名称')
    device_type = models.CharField(
        max_length=20,
        choices=[('desktop', '桌面'), ('mobile', '移动'), ('tablet', '平板')],
        verbose_name='设备类型'
    )
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.TextField(verbose_name='用户代理')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='最后活动时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '设备会话'
        verbose_name_plural = '设备会话'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.device_name}"


class ConfigTemplate(models.Model):
    """配置模板"""
    
    # 基础信息
    name = models.CharField(max_length=100, help_text="模板名称")
    description = models.TextField(blank=True, help_text="模板描述")
    
    # 配置数据
    config_data = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder,
        help_text="配置数据"
    )
    
    # 标签信息
    tags = models.JSONField(
        default=list,
        encoder=DjangoJSONEncoder,
        help_text="标签列表"
    )
    
    # 状态信息
    is_public = models.BooleanField(default=False, help_text="是否为公共模板")
    is_active = models.BooleanField(default=True)
    
    # 关联信息
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='config_templates')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_config_templates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by', 'is_active']),
            models.Index(fields=['is_public', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.created_by.username}"


class ConfigVersion(models.Model):
    """配置版本"""
    
    # 基础信息
    version_name = models.CharField(max_length=100, help_text="版本名称")
    description = models.TextField(blank=True, help_text="版本描述")
    
    # 配置数据
    config_data = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder,
        help_text="配置数据"
    )
    
    # 版本信息
    version_hash = models.CharField(max_length=64, unique=True, help_text="版本哈希")
    parent_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_versions',
        help_text="父版本"
    )
    
    # 状态信息
    is_active = models.BooleanField(default=True)
    
    # 关联信息
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='config_versions')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_config_versions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by', 'is_active']),
            models.Index(fields=['version_hash']),
            models.Index(fields=['parent_version']),
        ]
    
    def __str__(self):
        return f"{self.version_name} - {self.created_by.username}"
    
    def save(self, *args, **kwargs):
        """保存时自动生成版本哈希"""
        if not self.version_hash:
            import hashlib
            config_str = json.dumps(self.config_data, sort_keys=True)
            self.version_hash = hashlib.sha256(config_str.encode()).hexdigest()
        super().save(*args, **kwargs)
