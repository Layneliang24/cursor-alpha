"""
AI配置管理URL配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AIProviderViewSet, APIKeyViewSet, AIModelViewSet, PromptTemplateViewSet,
    ModelConfigViewSet, TokenUsageViewSet, UsageQuotaViewSet, TokenStatisticsViewSet,
    ConfigExportView, ConfigImportView, ConfigTemplateViewSet, ConfigVersionViewSet,
    UserSettingsViewSet, SystemConfigViewSet, LoginHistoryViewSet, 
    DeviceSessionViewSet, UserProfileViewSet, PasswordChangeView
)
from .fallback_views import FailoverStrategyViewSet, ProviderHealthViewSet

# 创建DRF路由器
router = DefaultRouter()

# 注册ViewSets
router.register(r'providers', AIProviderViewSet, basename='aiprovider')
router.register(r'keys', APIKeyViewSet, basename='apikey')
router.register(r'models', AIModelViewSet, basename='aimodel')
router.register(r'prompt-templates', PromptTemplateViewSet, basename='prompttemplate')
router.register(r'model-configs', ModelConfigViewSet, basename='modelconfig')
router.register(r'token-usage', TokenUsageViewSet, basename='tokenusage')
router.register(r'quotas', UsageQuotaViewSet, basename='usagequota')
router.register(r'tokenstatistics', TokenStatisticsViewSet, basename='tokenstatistics')
router.register(r'fallback-strategies', FailoverStrategyViewSet, basename='fallbackstrategy')
router.register(r'provider-health', ProviderHealthViewSet, basename='providerhealth')

# 配置模板路由
router.register(r'config/templates', ConfigTemplateViewSet, basename='config-template')

# 配置版本路由
router.register(r'config/versions', ConfigVersionViewSet, basename='config-version')

# 设置相关路由
router.register(r'settings', UserSettingsViewSet, basename='user-settings')
router.register(r'system-configs', SystemConfigViewSet, basename='system-configs')
router.register(r'login-history', LoginHistoryViewSet, basename='login-history')
router.register(r'device-sessions', DeviceSessionViewSet, basename='device-sessions')
router.register(r'user-profile', UserProfileViewSet, basename='user-profile')

app_name = 'ai'

urlpatterns = [
    # API路由
    path('', include(router.urls)),
]

# 配置导入导出路由
urlpatterns += [
    path('config/export/', ConfigExportView.as_view(), name='config-export'),
    path('config/import/', ConfigImportView.as_view(), name='config-import'),
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
]