from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.core.exceptions import ValidationError
import json

User = get_user_model()


class Permission(models.Model):
    """权限模型"""
    
    class Meta:
        verbose_name = '权限'
        verbose_name_plural = '权限'
        db_table = 'rbac_permission'
        unique_together = [['resource', 'action']]
    
    # 权限标识符（如：user.create, article.edit, ai.manage）
    codename = models.CharField(max_length=100, unique=True, verbose_name='权限代码')
    name = models.CharField(max_length=100, verbose_name='权限名称')
    description = models.TextField(blank=True, verbose_name='权限描述')
    
    # 权限分类
    resource = models.CharField(max_length=50, verbose_name='资源类型', help_text='如：user, article, ai_config')
    action = models.CharField(max_length=50, verbose_name='操作类型', help_text='如：create, read, update, delete, manage')
    
    # 权限级别（用于权限继承）
    level = models.IntegerField(default=1, verbose_name='权限级别', help_text='数值越大权限越高')
    
    # 元数据
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    def __str__(self):
        return f"{self.name} ({self.codename})"
    
    def clean(self):
        """验证权限数据"""
        if not self.codename:
            self.codename = f"{self.resource}.{self.action}"
        
        # 确保codename格式正确
        if '.' not in self.codename:
            raise ValidationError("权限代码必须包含资源和操作，格式：resource.action")


class Role(models.Model):
    """角色模型"""
    
    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
        db_table = 'rbac_role'
    
    # 基本信息
    name = models.CharField(max_length=50, unique=True, verbose_name='角色名称')
    display_name = models.CharField(max_length=100, verbose_name='显示名称')
    description = models.TextField(blank=True, verbose_name='角色描述')
    
    # 角色层级
    level = models.IntegerField(default=1, verbose_name='角色级别', help_text='数值越大权限越高')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='children', verbose_name='父角色')
    
    # 权限关联
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name='权限列表')
    
    # 角色配置
    is_system = models.BooleanField(default=False, verbose_name='系统角色', 
                                   help_text='系统角色不可删除')
    is_default = models.BooleanField(default=False, verbose_name='默认角色',
                                    help_text='新用户的默认角色')
    max_users = models.IntegerField(null=True, blank=True, verbose_name='最大用户数',
                                   help_text='限制该角色的用户数量')
    
    # 元数据
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    def __str__(self):
        return self.display_name
    
    def get_all_permissions(self):
        """获取角色的所有权限（包括继承的权限）"""
        permissions = set(self.permissions.filter(is_active=True))
        
        # 递归获取父角色权限
        if self.parent:
            permissions.update(self.parent.get_all_permissions())
        
        return permissions
    
    def has_permission(self, permission_codename):
        """检查角色是否有指定权限"""
        permissions = self.get_all_permissions()
        return any(perm.codename == permission_codename for perm in permissions)
    
    def clean(self):
        """验证角色数据"""
        # 防止循环继承
        if self.parent:
            parent = self.parent
            while parent:
                if parent == self:
                    raise ValidationError("不能创建循环继承的角色关系")
                parent = parent.parent


class UserRole(models.Model):
    """用户角色关联模型"""
    
    class Meta:
        verbose_name = '用户角色'
        verbose_name_plural = '用户角色'
        db_table = 'rbac_user_role'
        unique_together = [['user', 'role']]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='角色')
    
    # 权限范围限制（可选）
    scope_type = models.CharField(max_length=20, blank=True, verbose_name='权限范围类型',
                                 choices=[
                                     ('', '无限制'),
                                     ('department', '部门'),
                                     ('project', '项目'),
                                     ('custom', '自定义'),
                                 ])
    scope_value = models.CharField(max_length=100, blank=True, verbose_name='权限范围值')
    
    # 时间限制
    valid_from = models.DateTimeField(default=timezone.now, verbose_name='生效时间')
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name='失效时间')
    
    # 元数据
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='assigned_roles', verbose_name='分配者')
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='分配时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    def __str__(self):
        return f"{self.user.username} - {self.role.display_name}"
    
    def is_valid(self):
        """检查角色分配是否有效"""
        if not self.is_active:
            return False
        
        now = timezone.now()
        if self.valid_from > now:
            return False
        
        if self.valid_until and self.valid_until < now:
            return False
        
        return True


class AuditLog(models.Model):
    """审计日志模型"""
    
    class Meta:
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        db_table = 'rbac_audit_log'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['resource_type', 'timestamp']),
        ]
    
    # 操作用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='操作用户')
    username = models.CharField(max_length=150, verbose_name='用户名', help_text='冗余存储，防止用户删除后丢失记录')
    
    # 操作信息
    action = models.CharField(max_length=50, verbose_name='操作类型')
    resource_type = models.CharField(max_length=50, verbose_name='资源类型')
    resource_id = models.CharField(max_length=100, blank=True, verbose_name='资源ID')
    resource_name = models.CharField(max_length=200, blank=True, verbose_name='资源名称')
    
    # 操作详情
    description = models.TextField(verbose_name='操作描述')
    old_value = models.JSONField(null=True, blank=True, verbose_name='变更前的值')
    new_value = models.JSONField(null=True, blank=True, verbose_name='变更后的值')
    
    # 请求信息
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    request_method = models.CharField(max_length=10, blank=True, verbose_name='请求方法')
    request_url = models.URLField(blank=True, verbose_name='请求URL')
    
    # 结果信息
    success = models.BooleanField(default=True, verbose_name='操作是否成功')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    # 时间信息
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    duration = models.FloatField(null=True, blank=True, verbose_name='操作耗时（秒）')
    
    def __str__(self):
        return f"{self.username} - {self.action} - {self.timestamp}"
    
    @classmethod
    def log_action(cls, user, action, resource_type, description, **kwargs):
        """便捷的日志记录方法"""
        return cls.objects.create(
            user=user,
            username=user.username if user else 'anonymous',
            action=action,
            resource_type=resource_type,
            description=description,
            **kwargs
        )


class ResourcePermission(models.Model):
    """资源权限模型（用于细粒度权限控制）"""
    
    class Meta:
        verbose_name = '资源权限'
        verbose_name_plural = '资源权限'
        db_table = 'rbac_resource_permission'
        unique_together = [['user', 'content_type', 'object_id', 'permission']]
    
    # 用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    
    # 资源对象（通用外键）
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='内容类型')
    object_id = models.PositiveIntegerField(verbose_name='对象ID')
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 权限
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name='权限')
    
    # 权限状态
    granted = models.BooleanField(default=True, verbose_name='是否授予权限')
    
    # 元数据
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='granted_permissions', verbose_name='授权者')
    granted_at = models.DateTimeField(auto_now_add=True, verbose_name='授权时间')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='过期时间')
    
    def __str__(self):
        return f"{self.user.username} - {self.permission.name} - {self.content_object}"
    
    def is_valid(self):
        """检查权限是否有效"""
        if not self.granted:
            return False
        
        if self.expires_at and self.expires_at < timezone.now():
            return False
        
        return True
