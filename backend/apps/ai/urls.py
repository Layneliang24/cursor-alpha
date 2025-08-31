"""
AI配置管理URL配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.ai.views import (
    AIProviderViewSet, APIKeyViewSet, AIModelViewSet,
    PromptTemplateViewSet, ModelConfigViewSet,
    TokenUsageViewSet, UsageQuotaViewSet, ModelDiscoveryViewSet,
    MonitoringViewSet, TokenStatisticsViewSet
)
from .views.fallback_views import FailoverStrategyViewSet, ProviderHealthViewSet

# 创建DRF路由器
router = DefaultRouter()

# 注册ViewSets
router.register(r'providers', AIProviderViewSet, basename='aiprovider')
router.register(r'keys', APIKeyViewSet, basename='apikey')
router.register(r'models', AIModelViewSet, basename='aimodel')
router.register(r'prompt-templates', PromptTemplateViewSet, basename='prompttemplate')
router.register(r'model-configs', ModelConfigViewSet, basename='modelconfig')
router.register(r'model-discovery', ModelDiscoveryViewSet, basename='modeldiscovery')
router.register(r'monitoring', MonitoringViewSet, basename='monitoring')
router.register(r'token-usage', TokenUsageViewSet, basename='tokenusage')
router.register(r'token-statistics', TokenStatisticsViewSet, basename='tokenstatistics')
router.register(r'quotas', UsageQuotaViewSet, basename='usagequota')
router.register(r'fallback-strategies', FailoverStrategyViewSet, basename='fallbackstrategy')
router.register(r'provider-health', ProviderHealthViewSet, basename='providerhealth')

app_name = 'ai'

urlpatterns = [
    # API路由
    path('', include(router.urls)),
]

# 添加自定义端点（如果需要）
# urlpatterns += [
#     path('custom-endpoint/', custom_view, name='custom-endpoint'),
# ]