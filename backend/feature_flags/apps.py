from django.apps import AppConfig


class FeatureFlagsConfig(AppConfig):
    """特性开关应用配置"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'feature_flags'
    verbose_name = '特性开关'
    
    def ready(self):
        """应用准备就绪时的初始化"""
        # 导入信号处理器
        from . import signals
        
        # 注册默认特性开关
        self._register_default_flags()
    
    def _register_default_flags(self):
        """注册默认的特性开关"""
        from .models import FeatureFlag
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # 默认特性开关配置
        default_flags = [
            {
                'key': 'new_ui_design',
                'name': '新UI设计',
                'description': '启用新的用户界面设计',
                'status': FeatureFlag.Status.DISABLED,
                'target_type': FeatureFlag.TargetType.PERCENTAGE,
                'rollout_percentage': 0,
                'environments': ['development', 'staging']
            },
            {
                'key': 'advanced_analytics',
                'name': '高级数据分析',
                'description': '启用高级数据分析功能',
                'status': FeatureFlag.Status.DISABLED,
                'target_type': FeatureFlag.TargetType.PERCENTAGE,
                'rollout_percentage': 0,
                'environments': ['development']
            },
            {
                'key': 'social_learning',
                'name': '社交学习',
                'description': '启用社交学习功能',
                'status': FeatureFlag.Status.DISABLED,
                'target_type': FeatureFlag.TargetType.PERCENTAGE,
                'rollout_percentage': 0,
                'environments': ['development']
            },
            {
                'key': 'offline_mode',
                'name': '离线模式',
                'description': '启用离线学习模式',
                'status': FeatureFlag.Status.DISABLED,
                'target_type': FeatureFlag.TargetType.PERCENTAGE,
                'rollout_percentage': 0,
                'environments': ['development', 'staging', 'production']
            },
            {
                'key': 'ai_recommendations',
                'name': 'AI推荐',
                'description': '启用AI学习路径推荐',
                'status': FeatureFlag.Status.DISABLED,
                'target_type': FeatureFlag.TargetType.PERCENTAGE,
                'rollout_percentage': 0,
                'environments': ['development']
            }
        ]
        
        # 创建默认特性开关
        for flag_config in default_flags:
            try:
                flag, created = FeatureFlag.objects.get_or_create(
                    key=flag_config['key'],
                    defaults=flag_config
                )
                if created:
                    print(f"Created default feature flag: {flag_config['key']}")
            except Exception as e:
                # 在应用初始化时可能数据库还未准备好，忽略错误
                pass