import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from .models import AIProvider, TokenUsage, FallbackStrategy
from .services import AIProviderService

User = get_user_model()


class AIStatusConsumer(AsyncWebsocketConsumer):
    """
    WebSocket消费者，用于推送AI服务状态和监控数据
    """
    
    async def connect(self):
        """建立WebSocket连接"""
        # 验证用户身份
        if await self.authenticate_user():
            await self.accept()
            
            # 将用户添加到监控组
            await self.channel_layer.group_add(
                "ai_monitoring",
                self.channel_name
            )
            
            # 发送初始状态
            await self.send_initial_status()
            
            # 启动心跳
            asyncio.create_task(self.heartbeat())
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """断开WebSocket连接"""
        # 从监控组中移除
        await self.channel_layer.group_discard(
            "ai_monitoring",
            self.channel_name
        )
    
    async def receive(self, text_data):
        """接收WebSocket消息"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': asyncio.get_event_loop().time()
                }))
            elif message_type == 'subscribe':
                # 订阅特定类型的更新
                await self.handle_subscription(data)
            elif message_type == 'request_status':
                # 请求当前状态
                await self.send_current_status()
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    async def authenticate_user(self):
        """验证用户身份"""
        try:
            # 从查询参数获取token
            token = self.scope['url_route']['kwargs'].get('token')
            if not token:
                return False
            
            # 验证JWT token
            user = await self.get_user_from_token(token)
            if user and not isinstance(user, AnonymousUser):
                self.scope['user'] = user
                return True
            return False
        except Exception:
            return False
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        """从JWT token获取用户"""
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist):
            return AnonymousUser()
    
    async def send_initial_status(self):
        """发送初始状态"""
        status_data = await self.get_status_data()
        await self.send(text_data=json.dumps({
            'type': 'initial_status',
            'data': status_data
        }))
    
    async def send_current_status(self):
        """发送当前状态"""
        status_data = await self.get_status_data()
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'data': status_data
        }))
    
    @database_sync_to_async
    def get_status_data(self):
        """获取状态数据"""
        try:
            # 获取提供商状态
            providers = AIProvider.objects.all()
            provider_status = []
            
            for provider in providers:
                provider_status.append({
                    'id': provider.id,
                    'name': provider.display_name,
                    'status': provider.status,
                    'is_healthy': provider.is_healthy,
                    'avg_response_time': provider.avg_response_time,
                    'last_check': provider.last_check.isoformat() if provider.last_check else None
                })
            
            # 获取Token使用统计
            token_usage = TokenUsage.objects.filter(
                created_at__gte=asyncio.get_event_loop().time() - 86400  # 最近24小时
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
                    'is_degraded': strategy.is_degraded,
                    'degradation_reason': strategy.degradation_reason
                })
            
            return {
                'providers': provider_status,
                'usage_stats': usage_stats,
                'strategies': strategy_status,
                'timestamp': asyncio.get_event_loop().time()
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': asyncio.get_event_loop().time()
            }
    
    async def handle_subscription(self, data):
        """处理订阅请求"""
        subscription_type = data.get('subscription_type')
        
        if subscription_type == 'provider_status':
            await self.channel_layer.group_add(
                "provider_status",
                self.channel_name
            )
        elif subscription_type == 'token_usage':
            await self.channel_layer.group_add(
                "token_usage",
                self.channel_name
            )
        elif subscription_type == 'fallback_alerts':
            await self.channel_layer.group_add(
                "fallback_alerts",
                self.channel_name
            )
    
    async def heartbeat(self):
        """心跳机制"""
        while True:
            try:
                await asyncio.sleep(30)  # 30秒心跳间隔
                await self.send(text_data=json.dumps({
                    'type': 'heartbeat',
                    'timestamp': asyncio.get_event_loop().time()
                }))
            except Exception:
                break
    
    # 群组消息处理器
    async def provider_status_update(self, event):
        """提供商状态更新"""
        await self.send(text_data=json.dumps({
            'type': 'provider_status_update',
            'data': event['data']
        }))
    
    async def token_usage_update(self, event):
        """Token使用统计更新"""
        await self.send(text_data=json.dumps({
            'type': 'token_usage_update',
            'data': event['data']
        }))
    
    async def fallback_alert(self, event):
        """故障转移告警"""
        await self.send(text_data=json.dumps({
            'type': 'fallback_alert',
            'data': event['data']
        }))


class AIProviderConsumer(AsyncWebsocketConsumer):
    """
    专门用于AI提供商状态监控的WebSocket消费者
    """
    
    async def connect(self):
        """建立连接"""
        if await self.authenticate_user():
            await self.accept()
            await self.channel_layer.group_add(
                "ai_providers",
                self.channel_name
            )
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """断开连接"""
        await self.channel_layer.group_discard(
            "ai_providers",
            self.channel_name
        )
    
    async def authenticate_user(self):
        """验证用户身份"""
        try:
            token = self.scope['url_route']['kwargs'].get('token')
            if not token:
                return False
            
            user = await self.get_user_from_token(token)
            if user and not isinstance(user, AnonymousUser):
                self.scope['user'] = user
                return True
            return False
        except Exception:
            return False
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        """从JWT token获取用户"""
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist):
            return AnonymousUser()
    
    async def provider_health_check(self, event):
        """提供商健康检查结果"""
        await self.send(text_data=json.dumps({
            'type': 'provider_health_check',
            'data': event['data']
        }))
    
    async def provider_status_change(self, event):
        """提供商状态变化"""
        await self.send(text_data=json.dumps({
            'type': 'provider_status_change',
            'data': event['data']
        }))
