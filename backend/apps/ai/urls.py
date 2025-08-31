"""
AI配置管理URL配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AIProviderViewSet, APIKeyViewSet, AIModelViewSet,
    TokenUsageViewSet, UsageQuotaViewSet
)

# 创建DRF路由器
router = DefaultRouter()

# 注册ViewSets
router.register(r'providers', AIProviderViewSet, basename='aiprovider')
router.register(r'keys', APIKeyViewSet, basename='apikey')
router.register(r'models', AIModelViewSet, basename='aimodel')
router.register(r'token-usage', TokenUsageViewSet, basename='tokenusage')
router.register(r'quotas', UsageQuotaViewSet, basename='usagequota')

app_name = 'ai'

urlpatterns = [
    # API路由
    path('', include(router.urls)),
]

# 添加自定义端点（如果需要）
# urlpatterns += [
#     path('custom-endpoint/', custom_view, name='custom-endpoint'),
# ]