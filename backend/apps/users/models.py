from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """用户模型"""
    email = models.EmailField(unique=True, verbose_name='邮箱')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    website = models.URLField(blank=True, verbose_name='个人网站')
    is_email_verified = models.BooleanField(default=False, verbose_name='邮箱已验证')
    email_verification_token = models.CharField(max_length=100, blank=True, verbose_name='邮箱验证令牌')
    email_verification_expires = models.DateTimeField(null=True, blank=True, verbose_name='邮箱验证过期时间')
    
    class Meta:
        app_label = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'users_user'
    
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        """获取用户全名"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def get_avatar_url(self):
        """获取头像URL"""
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'


class UserProfile(models.Model):
    """用户详细资料"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    location = models.CharField(max_length=100, blank=True, verbose_name='所在地')
    company = models.CharField(max_length=100, blank=True, verbose_name='公司')
    position = models.CharField(max_length=100, blank=True, verbose_name='职位')
    skills = models.TextField(blank=True, verbose_name='技能标签')
    github = models.URLField(blank=True, verbose_name='GitHub')
    linkedin = models.URLField(blank=True, verbose_name='LinkedIn')
    twitter = models.URLField(blank=True, verbose_name='Twitter')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
        db_table = 'users_user_profile'
    
    def __str__(self):
        return f"{self.user.username}的资料"
