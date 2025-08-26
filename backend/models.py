
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ExpressionPractice(models.Model):
    '''地道表达练习记录'''
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    expression = models.ForeignKey('Expression', on_delete=models.CASCADE, verbose_name='表达')
    practice_type = models.CharField(max_length=20, verbose_name='练习类型')
    is_correct = models.BooleanField(verbose_name='是否正确')
    time_spent = models.IntegerField(verbose_name='用时(秒)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '表达练习记录'
        verbose_name_plural = '表达练习记录'
        ordering = ['-created_at']
