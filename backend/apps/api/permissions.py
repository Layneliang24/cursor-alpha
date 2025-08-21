from rest_framework.permissions import BasePermission, SAFE_METHODS, DjangoModelPermissions


class IsAdminOrReadOnly(BasePermission):
    """Allow read for everyone; write only for staff/superuser."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not (user and user.is_authenticated):
            return False
        # Django admin users
        if user.is_staff or user.is_superuser:
            return True
        # Allow members of group "管理员" to write
        try:
            return user.groups.filter(name='管理员').exists()
        except Exception:
            return False


class IsGroupAdminOrDjangoAdmin(BasePermission):
    """Allow write for users in group '管理员' or Django admins; read for everyone."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_staff or user.is_superuser:
            return True
        return user.groups.filter(name='管理员').exists()


class DjangoModelPermissionsOrReadOnly(DjangoModelPermissions):
    """
    基于Django模型权限的权限类，允许所有人读取，但写操作需要具体的模型权限。
    这会检查用户是否有对应模型的具体权限（如 add_category, change_category, delete_category）。
    """
    
    def has_permission(self, request, view):
        # 允许所有人读取
        if request.method in SAFE_METHODS:
            return True
        
        # 对于写操作，检查Django模型权限
        return super().has_permission(request, view)


class IsAuthorOrAdminOrReadOnly(BasePermission):
    """对象级权限：作者本人或管理员可写，其余用户只读"""

    def has_permission(self, request, view):
        # 所有人可读；写操作需要认证
        if request.method in SAFE_METHODS:
            return True
        # 修复：明确要求认证用户才能进行写操作
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何请求
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        # 管理员可写
        if user.is_staff or user.is_superuser:
            return True
        # 如果对象有 author 属性，检查作者
        author = getattr(obj, 'author', None)
        return author == user


