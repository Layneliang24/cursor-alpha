from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from .models import Permission, Role, UserRole, AuditLog, ResourcePermission
import logging
from typing import List, Set, Optional, Dict, Any

logger = logging.getLogger(__name__)
User = get_user_model()


class RBACService:
    """RBAC服务类，提供权限检查和管理功能"""
    
    def __init__(self, user):
        self.user = user
        self._permissions_cache = None
        self._roles_cache = None
    
    def has_permission(self, permission_code: str) -> bool:
        """检查用户是否有指定权限"""
        if not self.user or not self.user.is_authenticated:
            return False
        
        # 超级用户拥有所有权限
        if self.user.is_superuser:
            return True
        
        # 从缓存获取用户权限
        permissions = self.get_user_permissions()
        return permission_code in permissions
    
    def has_any_permission(self, permission_codes: List[str]) -> bool:
        """检查用户是否有任意一个权限"""
        return any(self.has_permission(code) for code in permission_codes)
    
    def has_all_permissions(self, permission_codes: List[str]) -> bool:
        """检查用户是否有所有权限"""
        return all(self.has_permission(code) for code in permission_codes)
    
    def get_user_permissions(self) -> Set[str]:
        """获取用户的所有权限代码"""
        if self._permissions_cache is not None:
            return self._permissions_cache
        
        cache_key = f"user_permissions_{self.user.id}"
        permissions = cache.get(cache_key)
        
        if permissions is None:
            permissions = self._calculate_user_permissions()
            # 缓存5分钟
            cache.set(cache_key, permissions, 300)
        
        self._permissions_cache = permissions
        return permissions
    
    def get_user_roles(self) -> List[Role]:
        """获取用户的所有角色"""
        if self._roles_cache is not None:
            return self._roles_cache
        
        cache_key = f"user_roles_{self.user.id}"
        roles = cache.get(cache_key)
        
        if roles is None:
            # 获取用户的有效角色
            user_roles = UserRole.objects.filter(
                user=self.user,
                is_active=True,
                role__is_active=True
            ).select_related('role')
            
            roles = []
            for user_role in user_roles:
                if user_role.is_valid():
                    roles.append(user_role.role)
            
            # 缓存5分钟
            cache.set(cache_key, roles, 300)
        
        self._roles_cache = roles
        return roles
    
    def _calculate_user_permissions(self) -> Set[str]:
        """计算用户的所有权限"""
        permissions = set()
        
        # 获取用户角色的权限
        roles = self.get_user_roles()
        for role in roles:
            role_permissions = role.get_all_permissions()
            permissions.update(perm.codename for perm in role_permissions)
        
        # 获取直接分配的资源权限
        resource_permissions = ResourcePermission.objects.filter(
            user=self.user,
            granted=True
        ).select_related('permission')
        
        for res_perm in resource_permissions:
            if res_perm.is_valid():
                permissions.add(res_perm.permission.codename)
        
        return permissions
    
    def assign_role(self, role: Role, assigned_by: User = None, 
                   valid_until: timezone.datetime = None) -> UserRole:
        """为用户分配角色"""
        with transaction.atomic():
            # 检查是否已存在
            user_role, created = UserRole.objects.get_or_create(
                user=self.user,
                role=role,
                defaults={
                    'assigned_by': assigned_by,
                    'valid_until': valid_until,
                    'is_active': True
                }
            )
            
            if not created and not user_role.is_active:
                # 重新激活已存在的角色
                user_role.is_active = True
                user_role.assigned_by = assigned_by
                user_role.valid_until = valid_until
                user_role.save()
            
            # 清除缓存
            self.clear_cache()
            
            # 记录审计日志
            AuditLog.log_action(
                user=assigned_by,
                action='assign_role',
                resource_type='user_role',
                resource_id=str(self.user.id),
                resource_name=self.user.username,
                description=f"为用户 {self.user.username} 分配角色 {role.display_name}",
                new_value={'role': role.name, 'user': self.user.username}
            )
            
            return user_role
    
    def remove_role(self, role: Role, removed_by: User = None) -> bool:
        """移除用户角色"""
        try:
            with transaction.atomic():
                user_role = UserRole.objects.get(
                    user=self.user,
                    role=role,
                    is_active=True
                )
                user_role.is_active = False
                user_role.save()
                
                # 清除缓存
                self.clear_cache()
                
                # 记录审计日志
                AuditLog.log_action(
                    user=removed_by,
                    action='remove_role',
                    resource_type='user_role',
                    resource_id=str(self.user.id),
                    resource_name=self.user.username,
                    description=f"移除用户 {self.user.username} 的角色 {role.display_name}",
                    old_value={'role': role.name, 'user': self.user.username}
                )
                
                return True
        except UserRole.DoesNotExist:
            return False
    
    def grant_resource_permission(self, obj, permission: Permission, 
                                granted_by: User = None,
                                expires_at: timezone.datetime = None) -> ResourcePermission:
        """为用户授予特定资源的权限"""
        from django.contrib.contenttypes.models import ContentType
        
        with transaction.atomic():
            content_type = ContentType.objects.get_for_model(obj)
            
            resource_perm, created = ResourcePermission.objects.get_or_create(
                user=self.user,
                content_type=content_type,
                object_id=obj.pk,
                permission=permission,
                defaults={
                    'granted': True,
                    'granted_by': granted_by,
                    'expires_at': expires_at
                }
            )
            
            if not created:
                resource_perm.granted = True
                resource_perm.granted_by = granted_by
                resource_perm.expires_at = expires_at
                resource_perm.save()
            
            # 清除缓存
            self.clear_cache()
            
            # 记录审计日志
            AuditLog.log_action(
                user=granted_by,
                action='grant_permission',
                resource_type=content_type.model,
                resource_id=str(obj.pk),
                resource_name=str(obj),
                description=f"为用户 {self.user.username} 授予权限 {permission.name}",
                new_value={
                    'user': self.user.username,
                    'permission': permission.codename,
                    'resource': str(obj)
                }
            )
            
            return resource_perm
    
    def revoke_resource_permission(self, obj, permission: Permission, 
                                 revoked_by: User = None) -> bool:
        """撤销用户对特定资源的权限"""
        from django.contrib.contenttypes.models import ContentType
        
        try:
            with transaction.atomic():
                content_type = ContentType.objects.get_for_model(obj)
                
                resource_perm = ResourcePermission.objects.get(
                    user=self.user,
                    content_type=content_type,
                    object_id=obj.pk,
                    permission=permission
                )
                
                resource_perm.granted = False
                resource_perm.save()
                
                # 清除缓存
                self.clear_cache()
                
                # 记录审计日志
                AuditLog.log_action(
                    user=revoked_by,
                    action='revoke_permission',
                    resource_type=content_type.model,
                    resource_id=str(obj.pk),
                    resource_name=str(obj),
                    description=f"撤销用户 {self.user.username} 的权限 {permission.name}",
                    old_value={
                        'user': self.user.username,
                        'permission': permission.codename,
                        'resource': str(obj)
                    }
                )
                
                return True
        except ResourcePermission.DoesNotExist:
            return False
    
    def get_accessible_objects(self, model_class, permission_code: str):
        """获取用户可访问的对象列表"""
        # 如果有管理权限，返回所有对象
        manage_permission = f"{model_class._meta.model_name}.manage"
        if self.has_permission(manage_permission):
            return model_class.objects.all()
        
        # 如果没有基础权限，返回空
        if not self.has_permission(permission_code):
            return model_class.objects.none()
        
        # 获取用户拥有的对象（通过所有者关系）
        user_filter = {}
        if hasattr(model_class, 'user'):
            user_filter['user'] = self.user
        elif hasattr(model_class, 'author'):
            user_filter['author'] = self.user
        elif hasattr(model_class, 'created_by'):
            user_filter['created_by'] = self.user
        
        queryset = model_class.objects.filter(**user_filter)
        
        # 添加通过ResourcePermission授权的对象
        from django.contrib.contenttypes.models import ContentType
        try:
            content_type = ContentType.objects.get_for_model(model_class)
            permission = Permission.objects.get(codename=permission_code)
            
            resource_perms = ResourcePermission.objects.filter(
                user=self.user,
                content_type=content_type,
                permission=permission,
                granted=True
            )
            
            authorized_ids = [rp.object_id for rp in resource_perms if rp.is_valid()]
            if authorized_ids:
                additional_objects = model_class.objects.filter(pk__in=authorized_ids)
                queryset = queryset.union(additional_objects)
        
        except (Permission.DoesNotExist, ContentType.DoesNotExist):
            pass
        
        return queryset
    
    def clear_cache(self):
        """清除用户权限缓存"""
        cache_keys = [
            f"user_permissions_{self.user.id}",
            f"user_roles_{self.user.id}"
        ]
        cache.delete_many(cache_keys)
        
        # 清除实例缓存
        self._permissions_cache = None
        self._roles_cache = None
    
    @classmethod
    def clear_all_cache(cls):
        """清除所有用户权限缓存"""
        # 这个方法在角色权限发生变化时调用
        # 由于无法精确知道哪些用户受影响，清除所有相关缓存
        cache.clear()


class RoleService:
    """角色管理服务"""
    
    @staticmethod
    def create_role(name: str, display_name: str, description: str = '',
                   permissions: List[str] = None, level: int = 1,
                   created_by: User = None) -> Role:
        """创建角色"""
        with transaction.atomic():
            role = Role.objects.create(
                name=name,
                display_name=display_name,
                description=description,
                level=level
            )
            
            if permissions:
                perm_objects = Permission.objects.filter(codename__in=permissions)
                role.permissions.set(perm_objects)
            
            # 记录审计日志
            AuditLog.log_action(
                user=created_by,
                action='create_role',
                resource_type='role',
                resource_id=str(role.id),
                resource_name=role.display_name,
                description=f"创建角色 {role.display_name}",
                new_value={
                    'name': role.name,
                    'display_name': role.display_name,
                    'permissions': permissions or []
                }
            )
            
            # 清除所有用户缓存
            RBACService.clear_all_cache()
            
            return role
    
    @staticmethod
    def update_role_permissions(role: Role, permissions: List[str], 
                              updated_by: User = None):
        """更新角色权限"""
        with transaction.atomic():
            old_permissions = list(role.permissions.values_list('codename', flat=True))
            
            perm_objects = Permission.objects.filter(codename__in=permissions)
            role.permissions.set(perm_objects)
            
            # 记录审计日志
            AuditLog.log_action(
                user=updated_by,
                action='update_role_permissions',
                resource_type='role',
                resource_id=str(role.id),
                resource_name=role.display_name,
                description=f"更新角色 {role.display_name} 的权限",
                old_value={'permissions': old_permissions},
                new_value={'permissions': permissions}
            )
            
            # 清除所有用户缓存
            RBACService.clear_all_cache()
    
    @staticmethod
    def get_role_hierarchy() -> Dict[str, Any]:
        """获取角色层级结构"""
        roles = Role.objects.filter(is_active=True).order_by('level', 'name')
        
        hierarchy = {}
        for role in roles:
            hierarchy[role.name] = {
                'id': role.id,
                'name': role.name,
                'display_name': role.display_name,
                'level': role.level,
                'parent': role.parent.name if role.parent else None,
                'permissions': list(role.permissions.values_list('codename', flat=True))
            }
        
        return hierarchy


class AuditService:
    """审计日志服务"""
    
    @staticmethod
    def log_user_action(user: User, action: str, resource_type: str,
                       description: str, request=None, **kwargs):
        """记录用户操作日志"""
        log_data = {
            'user': user,
            'username': user.username if user else 'anonymous',
            'action': action,
            'resource_type': resource_type,
            'description': description,
            **kwargs
        }
        
        if request:
            log_data.update({
                'ip_address': RBACService._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'request_method': request.method,
                'request_url': request.build_absolute_uri()
            })
        
        return AuditLog.objects.create(**log_data)
    
    @staticmethod
    def get_user_activity(user: User, days: int = 30):
        """获取用户活动记录"""
        from datetime import timedelta
        
        since = timezone.now() - timedelta(days=days)
        return AuditLog.objects.filter(
            user=user,
            timestamp__gte=since
        ).order_by('-timestamp')
    
    @staticmethod
    def get_resource_activity(resource_type: str, resource_id: str = None, 
                            days: int = 30):
        """获取资源相关的活动记录"""
        from datetime import timedelta
        
        since = timezone.now() - timedelta(days=days)
        filters = {
            'resource_type': resource_type,
            'timestamp__gte': since
        }
        
        if resource_id:
            filters['resource_id'] = resource_id
        
        return AuditLog.objects.filter(**filters).order_by('-timestamp')
    
    @staticmethod
    def _get_client_ip(request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
