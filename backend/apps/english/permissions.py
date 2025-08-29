from rest_framework.permissions import BasePermission, SAFE_METHODS
from .security import (
    EnglishLearnerPermission, EnglishContentManagerPermission, 
    EnglishAdminPermission, UserProgressOwnerPermission,
    SecurityAuditLogger
)


class EnglishAccessPermission(BasePermission):
    """Authenticated users can access english module read endpoints."""

    def has_permission(self, request, view):
        user = request.user
        has_access = bool(user and user.is_authenticated)
        
        if not has_access:
            SecurityAuditLogger.log_permission_denied(
                request, 
                view.__class__.__name__, 
                "未认证用户访问英语模块"
            )
        
        return has_access


class EnglishWordManagePermission(BasePermission):
    """Write operations on words require admin/staff or group '管理员'."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
            
        user = request.user
        if not (user and user.is_authenticated):
            SecurityAuditLogger.log_permission_denied(
                request, 
                view.__class__.__name__, 
                "未认证用户尝试管理操作"
            )
            return False
            
        # 检查权限
        has_permission = False
        if user.is_staff or user.is_superuser:
            has_permission = True
        else:
            try:
                has_permission = user.groups.filter(name='管理员').exists()
            except Exception:
                pass
        
        if not has_permission:
            SecurityAuditLogger.log_permission_denied(
                request, 
                view.__class__.__name__, 
                f"用户{user.username}无管理权限"
            )
        
        return has_permission


# 导出新的权限类供其他模块使用
__all__ = [
    'EnglishAccessPermission',
    'EnglishWordManagePermission', 
    'EnglishLearnerPermission',
    'EnglishContentManagerPermission',
    'EnglishAdminPermission',
    'UserProgressOwnerPermission'
]
