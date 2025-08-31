from django.apps import AppConfig


class RbacConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rbac'
    verbose_name = '角色权限管理'
    
    def ready(self):
        # 导入信号处理器
        try:
            import apps.rbac.signals  # noqa
        except ImportError:
            pass
