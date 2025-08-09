from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ExternalLink(models.Model):
    """外部链接模型"""
    LINK_TYPES = [
        ('website', '网站'),
        ('tool', '工具'),
        ('resource', '资源'),
        ('documentation', '文档'),
        ('other', '其他'),
    ]
    
    title = models.CharField(max_length=100, verbose_name='链接标题')
    url = models.URLField(verbose_name='链接地址')
    description = models.TextField(max_length=200, blank=True, verbose_name='描述')
    icon = models.CharField(max_length=50, blank=True, verbose_name='图标')
    link_type = models.CharField(max_length=20, choices=LINK_TYPES, default='website', verbose_name='链接类型')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    order = models.PositiveIntegerField(default=0, verbose_name='排序')
    
    # 管理信息
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '外部链接'
        verbose_name_plural = '外部链接'
        ordering = ['order', '-created_at']
        
    def __str__(self):
        return self.title
