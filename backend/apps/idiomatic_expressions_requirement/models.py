from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


class IdiomaticExpressionsRequirement(models.Model):
    """模型: 需求 idiomatic_expressions_requirement"""
    
    # TODO: 根据需求添加字段
    # 需求描述: 暂无描述
    
    name = models.CharField(max_length=255, verbose_name='名称')
    description = models.TextField(blank=True, verbose_name='描述')
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='idiomatic_expressions_requirement_created',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    class Meta:
        verbose_name = '需求 idiomatic_expressions_requirement'
        verbose_name_plural = '需求 idiomatic_expressions_requirement'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
