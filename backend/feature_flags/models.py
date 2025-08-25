from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json


class FeatureFlag(models.Model):
    """特性开关模型"""
    
    class Status(models.TextChoices):
        DISABLED = 'disabled', '禁用'
        ENABLED = 'enabled', '启用'
        ROLLOUT = 'rollout', '灰度发布'
        DEPRECATED = 'deprecated', '已废弃'
    
    class TargetType(models.TextChoices):
        ALL = 'all', '所有用户'
        PERCENTAGE = 'percentage', '百分比用户'
        USER_LIST = 'user_list', '指定用户列表'
        USER_ATTRIBUTE = 'user_attribute', '用户属性'
        ENVIRONMENT = 'environment', '环境'
    
    # 基本信息
    name = models.CharField(max_length=100, unique=True, verbose_name='特性名称')
    key = models.CharField(max_length=100, unique=True, verbose_name='特性键值')
    description = models.TextField(blank=True, verbose_name='描述')
    
    # 状态管理
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DISABLED,
        verbose_name='状态'
    )
    
    # 目标用户配置
    target_type = models.CharField(
        max_length=20,
        choices=TargetType.choices,
        default=TargetType.ALL,
        verbose_name='目标类型'
    )
    
    # 灰度发布百分比 (0-100)
    rollout_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='灰度百分比'
    )
    
    # 目标用户列表 (JSON格式存储用户ID列表)
    target_users = models.JSONField(
        default=list,
        blank=True,
        verbose_name='目标用户列表'
    )
    
    # 用户属性条件 (JSON格式存储条件)
    user_attributes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='用户属性条件'
    )
    
    # 环境限制
    environments = models.JSONField(
        default=list,
        blank=True,
        verbose_name='环境列表'
    )
    
    # 特性值 (JSON格式，支持复杂配置)
    value = models.JSONField(
        default=bool,
        verbose_name='特性值'
    )
    
    # 时间管理
    start_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='开始时间'
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='结束时间'
    )
    
    # 元数据
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_feature_flags',
        verbose_name='创建者'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_feature_flags',
        verbose_name='更新者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 版本控制
    version = models.IntegerField(default=1, verbose_name='版本号')
    
    class Meta:
        db_table = 'feature_flags'
        verbose_name = '特性开关'
        verbose_name_plural = '特性开关'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['status']),
            models.Index(fields=['target_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.key})"
    
    def is_active(self):
        """检查特性开关是否处于活跃状态"""
        if self.status == self.Status.DISABLED:
            return False
        
        now = timezone.now()
        
        # 检查时间范围
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        
        return self.status in [self.Status.ENABLED, self.Status.ROLLOUT]
    
    def save(self, *args, **kwargs):
        """保存时自动更新版本号"""
        if self.pk:
            self.version += 1
        super().save(*args, **kwargs)


class FeatureFlagHistory(models.Model):
    """特性开关变更历史"""
    
    feature_flag = models.ForeignKey(
        FeatureFlag,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='特性开关',
        null=True,
        blank=True
    )
    
    # 变更信息
    action = models.CharField(max_length=50, verbose_name='操作类型')
    old_value = models.JSONField(null=True, blank=True, verbose_name='旧值')
    new_value = models.JSONField(null=True, blank=True, verbose_name='新值')
    reason = models.TextField(blank=True, verbose_name='变更原因')
    
    # 操作者信息
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='操作者'
    )
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='变更时间')
    
    # 环境信息
    environment = models.CharField(max_length=50, blank=True, verbose_name='环境')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    
    class Meta:
        db_table = 'feature_flag_history'
        verbose_name = '特性开关历史'
        verbose_name_plural = '特性开关历史'
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['feature_flag', '-changed_at']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.feature_flag.key} - {self.action} at {self.changed_at}"


class FeatureFlagUsage(models.Model):
    """特性开关使用统计"""
    
    feature_flag = models.ForeignKey(
        FeatureFlag,
        on_delete=models.CASCADE,
        related_name='usage_stats',
        verbose_name='特性开关',
        null=True,
        blank=True
    )
    
    # 统计信息
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feature_flag_usage',
        verbose_name='用户',
        help_text='访问的用户'
    )
    session_id = models.CharField(max_length=100, blank=True, verbose_name='会话ID')
    
    # 使用详情
    is_enabled = models.BooleanField(verbose_name='是否启用')
    value_returned = models.JSONField(verbose_name='返回值')
    
    # 上下文信息
    context = models.JSONField(default=dict, blank=True, verbose_name='上下文')
    environment = models.CharField(max_length=50, blank=True, verbose_name='环境')
    
    # 时间和位置
    accessed_at = models.DateTimeField(auto_now_add=True, verbose_name='访问时间')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    
    class Meta:
        db_table = 'feature_flag_usage'
        verbose_name = '特性开关使用记录'
        verbose_name_plural = '特性开关使用记录'
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['feature_flag', '-accessed_at']),
            models.Index(fields=['user', '-accessed_at']),
            models.Index(fields=['is_enabled']),
        ]
    
    def __str__(self):
        return f"{self.feature_flag.key} - {self.user} at {self.accessed_at}"