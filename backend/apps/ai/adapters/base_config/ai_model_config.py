"""
AI模型配置类
定义AI模型的基本配置参数和验证规则
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class AIModelConfig(models.Model):
    """
    AI模型配置模型
    存储AI模型的配置参数和元数据
    """
    
    # 基本信息
    name = models.CharField(
        max_length=100,
        verbose_name="模型名称",
        help_text="AI模型的唯一标识名称"
    )
    
    provider = models.CharField(
        max_length=50,
        verbose_name="提供商",
        help_text="AI服务提供商（如OpenAI、Claude、Google等）"
    )
    
    model_id = models.CharField(
        max_length=100,
        verbose_name="模型ID",
        help_text="在提供商系统中的模型标识符"
    )
    
    # 配置参数
    max_tokens = models.IntegerField(
        default=4096,
        verbose_name="最大令牌数",
        help_text="单次请求的最大令牌数量",
        validators=[
            MinValueValidator(1, message="最大令牌数必须大于0"),
            MaxValueValidator(100000, message="最大令牌数不能超过100000")
        ]
    )
    
    temperature = models.FloatField(
        default=0.7,
        verbose_name="温度参数",
        help_text="控制输出的随机性，0.0为确定性，1.0为完全随机",
        validators=[
            MinValueValidator(0.0, message="温度参数不能小于0"),
            MaxValueValidator(2.0, message="温度参数不能大于2")
        ]
    )
    
    top_p = models.FloatField(
        default=1.0,
        verbose_name="Top-P参数",
        help_text="控制词汇选择的多样性",
        validators=[
            MinValueValidator(0.0, message="Top-P参数不能小于0"),
            MaxValueValidator(1.0, message="Top-P参数不能大于1")
        ]
    )
    
    # 状态和可用性
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否激活",
        help_text="该模型配置是否可用"
    )
    
    is_default = models.BooleanField(
        default=False,
        verbose_name="是否默认",
        help_text="是否为默认模型配置"
    )
    
    # 性能和限制
    rate_limit = models.IntegerField(
        default=100,
        verbose_name="速率限制",
        help_text="每分钟允许的请求数量",
        validators=[
            MinValueValidator(1, message="速率限制必须大于0")
        ]
    )
    
    cost_per_1k_tokens = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=0.002,
        verbose_name="每千令牌成本",
        help_text="每1000个令牌的费用（美元）",
        validators=[
            MinValueValidator(0, message="成本不能为负数")
        ]
    )
    
    # 元数据
    description = models.TextField(
        blank=True,
        verbose_name="描述",
        help_text="模型的详细描述和用途说明"
    )
    
    version = models.CharField(
        max_length=20,
        default="1.0.0",
        verbose_name="版本",
        help_text="模型配置的版本号"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )
    
    class Meta:
        verbose_name = "AI模型配置"
        verbose_name_plural = "AI模型配置"
        db_table = "ai_model_config"
        unique_together = [
            ('provider', 'model_id'),
            ('name', 'version')
        ]
        ordering = ['-is_default', '-is_active', 'name']
        indexes = [
            models.Index(fields=['provider', 'model_id']),
            models.Index(fields=['is_active', 'is_default']),
            models.Index(fields=['created_at'])
        ]
    
    def __str__(self):
        return f"{self.provider}:{self.model_id} ({self.name})"
    
    def clean(self):
        """自定义验证逻辑"""
        super().clean()
        
        # 确保只有一个默认配置
        if self.is_default:
            # 检查是否已存在其他默认配置
            existing_default = AIModelConfig.objects.filter(
                is_default=True,
                provider=self.provider
            ).exclude(pk=self.pk)
            
            if existing_default.exists():
                raise ValidationError({
                    'is_default': f"提供商 {self.provider} 已存在默认配置，不能设置多个默认配置"
                })
    
    def save(self, *args, **kwargs):
        """保存前的验证"""
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        """获取完整的模型名称"""
        return f"{self.provider}/{self.model_id}"
    
    @property
    def is_available(self):
        """检查模型是否可用"""
        return self.is_active and self.is_default
    
    def get_cost_estimate(self, token_count):
        """
        估算指定令牌数量的成本
        
        Args:
            token_count (int): 令牌数量
            
        Returns:
            decimal.Decimal: 估算成本
        """
        from decimal import Decimal
        return (Decimal(str(token_count)) / 1000) * self.cost_per_1k_tokens
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'provider': self.provider,
            'model_id': self.model_id,
            'max_tokens': self.max_tokens,
            'temperature': float(self.temperature),
            'top_p': float(self.top_p),
            'is_active': self.is_active,
            'is_default': self.is_default,
            'rate_limit': self.rate_limit,
            'cost_per_1k_tokens': float(self.cost_per_1k_tokens),
            'description': self.description,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_default_config(cls, provider=None):
        """
        获取默认配置
        
        Args:
            provider (str, optional): 指定提供商，如果为None则返回任意提供商的默认配置
            
        Returns:
            AIModelConfig: 默认配置对象，如果不存在则返回None
        """
        queryset = cls.objects.filter(is_default=True, is_active=True)
        
        if provider:
            queryset = queryset.filter(provider=provider)
        
        return queryset.first()
    
    @classmethod
    def get_active_configs(cls, provider=None):
        """
        获取所有激活的配置
        
        Args:
            provider (str, optional): 指定提供商
            
        Returns:
            QuerySet: 激活的配置查询集
        """
        queryset = cls.objects.filter(is_active=True)
        
        if provider:
            queryset = queryset.filter(provider=provider)
        
        return queryset.order_by('-is_default', 'name')

