from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConversationViewSet, AIServiceViewSet, LoadBalancerViewSet, 
    HealthMonitorViewSet, DegradationViewSet
)
from .conversation.views import ConversationViewSet as ConversationManagementViewSet

router = DefaultRouter()
router.register(r'ai/conversations', ConversationViewSet, basename='ai-conversations')
router.register(r'ai/conversation-management', ConversationManagementViewSet, basename='conversation-management')
router.register(r'ai/services', AIServiceViewSet, basename='ai-services')
router.register(r'ai/load-balancer', LoadBalancerViewSet, basename='load-balancer')
router.register(r'ai/health', HealthMonitorViewSet, basename='health-monitor')
router.register(r'ai/degradation', DegradationViewSet, basename='degradation')

urlpatterns = [
    path('', include(router.urls)),
]


