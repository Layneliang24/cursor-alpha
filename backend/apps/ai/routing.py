from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # AI状态监控WebSocket
    re_path(r'ws/ai/status/(?P<token>[^/]+)/$', consumers.AIStatusConsumer.as_asgi()),
    
    # AI提供商监控WebSocket
    re_path(r'ws/ai/providers/(?P<token>[^/]+)/$', consumers.AIProviderConsumer.as_asgi()),
]
