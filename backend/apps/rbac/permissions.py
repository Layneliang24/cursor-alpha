from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .models import Permission, Role, UserRole, AuditLog
from .services import RBACService
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class RBACPermission(BasePermission):
    """基于RBAC的权限控制"""
    
    def __init__(self, required_permission=None):
        """
        初始化权限检查器
        
        Args:
            required_permission: 所需的权限代码，如 'ai_config.manage'
        """
        self.required_permission = required_permission
    
    def has_permission(self, request, view):
        """检查用户是否有权限访问视图"""
        # 获取用户
        user = request.user
        if not user or not user.is_authenticated:
            # 未认证用户检查访客权限
            return self._check_guest_permission(request, view)
        
        # 获取所需权限
        permission_code = self._get_required_permission(request, view)
        if not permission_code:
            # 如果没有指定权限要求，允许访问
            return True
        
        # 检查用户权限
        rbac_service = RBACService(user)
        has_perm = rbac_service.has_permission(permission_code)
        
        # 记录权限检查日志
        self._log_permission_check(user, permission_code, has_perm, request)
        
        return has_perm
    
    def has_object_permission(self, request, view, obj):
        """检查用户是否有权限访问特定对象"""
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        # 获取所需权限
        permission_code = self._get_required_permission(request, view)
        if not permission_code:
            return True
        
        # 检查基础权限
        rbac_service = RBACService(user)
        if not rbac_service.has_permission(permission_code):
            return False
        
        # 检查对象级权限
        return self._check_object_permission(user, obj, permission_code, request)
    
    def _get_required_permission(self, request, view):
        """获取所需权限代码"""
        # 1. 优先使用初始化时指定的权限
        if self.required_permission:
            return self.required_permission
        
        # 2. 从视图属性获取
        if hasattr(view, 'required_permission'):
            return view.required_permission
        
        # 3. 从视图方法获取
        action = getattr(view, 'action', None)
        if action and hasattr(view, f'{action}_permission'):
            return getattr(view, f'{action}_permission')
        
        # 4. 根据HTTP方法自动推断
        return self._infer_permission_from_method(request, view)
    
    def _infer_permission_from_method(self, request, view):
        """根据HTTP方法推断权限"""
        # 获取资源类型
        resource_type = self._get_resource_type(view)
        if not resource_type:
            return None
        
        # 根据HTTP方法映射到权限动作
        method_action_map = {
            'GET': 'view',
            'POST': 'create',
            'PUT': 'edit',
            'PATCH': 'edit',
            'DELETE': 'delete',
        }
        
        action = method_action_map.get(request.method)
        if action:
            return f"{resource_type}.{action}"
        
        return None
    
    def _get_resource_type(self, view):
        """从视图获取资源类型"""
        # 1. 从视图属性获取
        if hasattr(view, 'resource_type'):
            return view.resource_type
        
        # 2. 从模型获取
        if hasattr(view, 'queryset') and view.queryset is not None:
            model = view.queryset.model
            return model._meta.model_name
        
        # 3. 从视图名称推断
        view_name = view.__class__.__name__.lower()
        if 'viewset' in view_name:
            return view_name.replace('viewset', '')
        if 'view' in view_name:
            return view_name.replace('view', '')
        
        return None
    
    def _check_guest_permission(self, request, view):
        """检查访客权限"""
        # 只允许安全方法（GET, HEAD, OPTIONS）
        if request.method not in SAFE_METHODS:
            return False
        
        # 检查是否有访客角色的权限
        try:
            guest_role = Role.objects.get(name='guest', is_active=True)
            permission_code = self._get_required_permission(request, view)
            if permission_code:
                return guest_role.has_permission(permission_code)
        except Role.DoesNotExist:
            pass
        
        return False
    
    def _check_object_permission(self, user, obj, permission_code, request):
        """检查对象级权限"""
        # 1. 检查是否是对象的所有者
        if hasattr(obj, 'user') and obj.user == user:
            return True
        if hasattr(obj, 'author') and obj.author == user:
            return True
        if hasattr(obj, 'created_by') and obj.created_by == user:
            return True
        
        # 2. 检查是否有管理权限
        rbac_service = RBACService(user)
        resource_type = obj._meta.model_name
        manage_permission = f"{resource_type}.manage"
        if rbac_service.has_permission(manage_permission):
            return True
        
        # 3. 检查特定对象权限（如果实现了ResourcePermission）
        from .models import ResourcePermission
        from django.contrib.contenttypes.models import ContentType
        
        try:
            content_type = ContentType.objects.get_for_model(obj)
            permission = Permission.objects.get(codename=permission_code)
            
            resource_perm = ResourcePermission.objects.filter(
                user=user,
                content_type=content_type,
                object_id=obj.pk,
                permission=permission,
                granted=True
            ).first()
            
            if resource_perm and resource_perm.is_valid():
                return True
        except (Permission.DoesNotExist, ResourcePermission.DoesNotExist):
            pass
        
        return False
    
    def _log_permission_check(self, user, permission_code, has_permission, request):
        """记录权限检查日志"""
        try:
            # 只记录失败的权限检查，避免日志过多
            if not has_permission:
                AuditLog.log_action(
                    user=user,
                    action='permission_denied',
                    resource_type='permission',
                    description=f"用户尝试访问权限: {permission_code}",
                    ip_address=self._get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    request_method=request.method,
                    request_url=request.build_absolute_uri(),
                    success=False,
                    error_message=f"缺少权限: {permission_code}"
                )
        except Exception as e:
            logger.error(f"记录权限检查日志失败: {e}")
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RequirePermission(RBACPermission):
    """要求特定权限的装饰器类"""
    
    def __init__(self, permission_code):
        super().__init__(required_permission=permission_code)


def require_permission(permission_code):
    """权限装饰器工厂函数"""
    return RequirePermission(permission_code)


# 预定义的权限类
class CanManageUsers(RequirePermission):
    def __init__(self):
        super().__init__('user.manage')


class CanManageArticles(RequirePermission):
    def __init__(self):
        super().__init__('article.manage')


class CanManageAIConfig(RequirePermission):
    def __init__(self):
        super().__init__('ai_config.manage')


class CanViewAuditLogs(RequirePermission):
    def __init__(self):
        super().__init__('audit.view')


class CanManageRoles(RequirePermission):
    def __init__(self):
        super().__init__('role.manage')


class IsOwnerOrHasPermission(BasePermission):
    """对象所有者或有权限的用户可以访问"""
    
    def __init__(self, permission_code):
        self.permission_code = permission_code
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # 检查是否是所有者
        if hasattr(obj, 'user') and obj.user == user:
            return True
        if hasattr(obj, 'author') and obj.author == user:
            return True
        if hasattr(obj, 'created_by') and obj.created_by == user:
            return True
        
        # 检查权限
        rbac_service = RBACService(user)
        return rbac_service.has_permission(self.permission_code)
