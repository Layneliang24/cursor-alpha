import json
import asyncio
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from .models import AIProvider, TokenUsage, FallbackStrategy


class WebSocketService:
    """
    WebSocket服务类，用于发送实时消息
    """
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def send_provider_status_update(self, provider_id):
        """发送提供商状态更新"""
        try:
            provider = AIProvider.objects.get(id=provider_id)
            data = {
                'id': provider.id,
                'name': provider.display_name,
                'status': provider.status,
                'is_healthy': provider.is_healthy,
                'avg_response_time': provider.avg_response_time,
                'last_check': provider.last_check.isoformat() if provider.last_check else None,
                'timestamp': timezone.now().isoformat()
            }
            
            async_to_sync(self.channel_layer.group_send)(
                "provider_status",
                {
                    "type": "provider_status_update",
                    "data": data
                }
            )
            
            # 同时发送到监控组
            async_to_sync(self.channel_layer.group_send)(
                "ai_monitoring",
                {
                    "type": "provider_status_update",
                    "data": data
                }
            )
        except AIProvider.DoesNotExist:
            pass
    
    def send_token_usage_update(self, usage_data):
        """发送Token使用统计更新"""
        data = {
            'total_tokens': usage_data.get('total_tokens', 0),
            'total_cost': usage_data.get('total_cost', 0),
            'request_count': usage_data.get('request_count', 0),
            'timestamp': timezone.now().isoformat()
        }
        
        async_to_sync(self.channel_layer.group_send)(
            "token_usage",
            {
                "type": "token_usage_update",
                "data": data
            }
        )
        
        # 同时发送到监控组
        async_to_sync(self.channel_layer.group_send)(
            "ai_monitoring",
            {
                "type": "token_usage_update",
                "data": data
            }
        )
    
    def send_fallback_alert(self, strategy_id, alert_type, message):
        """发送故障转移告警"""
        try:
            strategy = FallbackStrategy.objects.get(id=strategy_id)
            data = {
                'strategy_id': strategy.id,
                'strategy_name': strategy.name,
                'alert_type': alert_type,
                'message': message,
                'current_provider': strategy.current_provider.id if strategy.current_provider else None,
                'is_degraded': strategy.is_degraded,
                'degradation_reason': strategy.degradation_reason,
                'timestamp': timezone.now().isoformat()
            }
            
            async_to_sync(self.channel_layer.group_send)(
                "fallback_alerts",
                {
                    "type": "fallback_alert",
                    "data": data
                }
            )
            
            # 同时发送到监控组
            async_to_sync(self.channel_layer.group_send)(
                "ai_monitoring",
                {
                    "type": "fallback_alert",
                    "data": data
                }
            )
        except FallbackStrategy.DoesNotExist:
            pass
    
    def send_provider_health_check(self, provider_id, health_data):
        """发送提供商健康检查结果"""
        data = {
            'provider_id': provider_id,
            'is_healthy': health_data.get('is_healthy', False),
            'response_time': health_data.get('response_time', 0),
            'error_message': health_data.get('error_message', ''),
            'timestamp': timezone.now().isoformat()
        }
        
        async_to_sync(self.channel_layer.group_send)(
            "ai_providers",
            {
                "type": "provider_health_check",
                "data": data
            }
        )
    
    def send_provider_status_change(self, provider_id, old_status, new_status):
        """发送提供商状态变化"""
        data = {
            'provider_id': provider_id,
            'old_status': old_status,
            'new_status': new_status,
            'timestamp': timezone.now().isoformat()
        }
        
        async_to_sync(self.channel_layer.group_send)(
            "ai_providers",
            {
                "type": "provider_status_change",
                "data": data
            }
        )
    
    def broadcast_system_status(self):
        """广播系统整体状态"""
        try:
            # 获取所有提供商状态
            providers = AIProvider.objects.all()
            provider_status = []
            
            for provider in providers:
                provider_status.append({
                    'id': provider.id,
                    'name': provider.display_name,
                    'status': provider.status,
                    'is_healthy': provider.is_healthy,
                    'avg_response_time': provider.avg_response_time
                })
            
            # 获取Token使用统计
            token_usage = TokenUsage.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(hours=24)
            )
            
            usage_stats = {
                'total_tokens': sum(usage.token_count for usage in token_usage),
                'total_cost': sum(usage.cost for usage in token_usage),
                'request_count': token_usage.count()
            }
            
            # 获取故障转移策略状态
            strategies = FallbackStrategy.objects.filter(is_active=True)
            strategy_status = []
            
            for strategy in strategies:
                strategy_status.append({
                    'id': strategy.id,
                    'name': strategy.name,
                    'current_provider': strategy.current_provider.id if strategy.current_provider else None,
                    'is_degraded': strategy.is_degraded
                })
            
            data = {
                'providers': provider_status,
                'usage_stats': usage_stats,
                'strategies': strategy_status,
                'timestamp': timezone.now().isoformat()
            }
            
            # 发送到监控组
            async_to_sync(self.channel_layer.group_send)(
                "ai_monitoring",
                {
                    "type": "status_update",
                    "data": data
                }
            )
            
        except Exception as e:
            # 记录错误但不中断
            print(f"Error broadcasting system status: {e}")


# 全局WebSocket服务实例
websocket_service = WebSocketService()
