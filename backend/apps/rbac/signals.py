from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .models import Permission, Role, UserRole, ResourcePermission
from .services import RBACService

User = get_user_model()


@receiver(post_save, sender=UserRole)
def clear_user_cache_on_role_change(sender, instance, **kwargs):
    """用户角色变化时清除缓存"""
    cache_keys = [
        f"user_permissions_{instance.user.id}",
        f"user_roles_{instance.user.id}"
    ]
    cache.delete_many(cache_keys)


@receiver(post_delete, sender=UserRole)
def clear_user_cache_on_role_delete(sender, instance, **kwargs):
    """用户角色删除时清除缓存"""
    cache_keys = [
        f"user_permissions_{instance.user.id}",
        f"user_roles_{instance.user.id}"
    ]
    cache.delete_many(cache_keys)


@receiver(m2m_changed, sender=Role.permissions.through)
def clear_all_cache_on_role_permissions_change(sender, instance, action, **kwargs):
    """角色权限变化时清除所有用户缓存"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        # 角色权限变化会影响所有拥有该角色的用户
        # 为了简单起见，清除所有缓存
        RBACService.clear_all_cache()


@receiver(post_save, sender=Role)
def clear_all_cache_on_role_change(sender, instance, **kwargs):
    """角色信息变化时清除缓存"""
    if kwargs.get('update_fields') and 'is_active' in kwargs['update_fields']:
        # 角色激活状态变化会影响所有用户
        RBACService.clear_all_cache()


@receiver(post_save, sender=Permission)
def clear_all_cache_on_permission_change(sender, instance, **kwargs):
    """权限信息变化时清除缓存"""
    if kwargs.get('update_fields') and 'is_active' in kwargs['update_fields']:
        # 权限激活状态变化会影响所有用户
        RBACService.clear_all_cache()


@receiver(post_save, sender=ResourcePermission)
def clear_user_cache_on_resource_permission_change(sender, instance, **kwargs):
    """资源权限变化时清除用户缓存"""
    cache_keys = [
        f"user_permissions_{instance.user.id}",
        f"user_roles_{instance.user.id}"
    ]
    cache.delete_many(cache_keys)


@receiver(post_delete, sender=ResourcePermission)
def clear_user_cache_on_resource_permission_delete(sender, instance, **kwargs):
    """资源权限删除时清除用户缓存"""
    cache_keys = [
        f"user_permissions_{instance.user.id}",
        f"user_roles_{instance.user.id}"
    ]
    cache.delete_many(cache_keys)
