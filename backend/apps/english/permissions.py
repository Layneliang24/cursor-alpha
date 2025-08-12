from rest_framework.permissions import BasePermission, SAFE_METHODS


class EnglishAccessPermission(BasePermission):
    """Authenticated users can access english module read endpoints."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class EnglishWordManagePermission(BasePermission):
    """Write operations on words require admin/staff or group '管理员'."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_staff or user.is_superuser:
            return True
        try:
            return user.groups.filter(name='管理员').exists()
        except Exception:
            return False
