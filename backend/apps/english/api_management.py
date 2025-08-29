"""
地道表达API管理功能
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .security import (
    APIKeyAuthentication, SecurityAuditLogger, 
    EnglishAdminPermission, EnglishManagementThrottle
)
from .models import UserExpressionProgress

User = get_user_model()


class APIKeyManagementViewSet(viewsets.GenericViewSet):
    """API密钥管理ViewSet"""
    
    permission_classes = [IsAuthenticated]
    throttle_classes = [EnglishManagementThrottle]
    
    @action(detail=False, methods=['post'])
    def generate_key(self, request):
        """生成API密钥"""
        user = request.user
        
        # 检查用户是否已有活跃密钥
        existing_keys = self._get_user_api_keys(user)
        if len(existing_keys) >= 3:  # 限制每用户最多3个密钥
            return Response({
                'error': '每个用户最多只能拥有3个API密钥',
                'existing_keys_count': len(existing_keys)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 生成新密钥
        api_key = APIKeyAuthentication.generate_api_key(user)
        
        # 记录安全事件
        SecurityAuditLogger.log_security_event(
            'API_KEY_GENERATED',
            user,
            {'api_key_prefix': api_key[:8] + '...'},
            request
        )
        
        return Response({
            'api_key': api_key,
            'created_at': timezone.now().isoformat(),
            'expires_at': (timezone.now() + timedelta(days=30)).isoformat(),
            'note': 'Please save this API key securely. It will not be shown again.'
        })
    
    @action(detail=False, methods=['get'])
    def list_keys(self, request):
        """列出用户的API密钥（不显示完整密钥）"""
        user = request.user
        keys = self._get_user_api_keys(user)
        
        key_list = []
        for key_hash, key_data in keys.items():
            key_list.append({
                'key_prefix': key_hash[:8] + '...',
                'created_at': key_data.get('created_at'),
                'last_used': key_data.get('last_used'),
                'status': 'active'
            })
        
        return Response({
            'api_keys': key_list,
            'total_count': len(key_list),
            'max_allowed': 3
        })
    
    @action(detail=False, methods=['post'])
    def revoke_key(self, request):
        """撤销API密钥"""
        api_key_prefix = request.data.get('key_prefix')
        if not api_key_prefix:
            return Response({
                'error': 'key_prefix参数必需'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        keys = self._get_user_api_keys(user)
        
        # 查找匹配的密钥
        revoked_count = 0
        for key_hash in list(keys.keys()):
            if key_hash.startswith(api_key_prefix.replace('...', '')):
                APIKeyAuthentication.revoke_api_key(key_hash)
                revoked_count += 1
                
                SecurityAuditLogger.log_security_event(
                    'API_KEY_REVOKED',
                    user,
                    {'api_key_prefix': key_hash[:8] + '...'},
                    request
                )
        
        if revoked_count == 0:
            return Response({
                'error': '未找到匹配的API密钥'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'message': f'成功撤销{revoked_count}个API密钥',
            'revoked_count': revoked_count
        })
    
    @action(detail=False, methods=['get'])
    def usage_stats(self, request):
        """获取API使用统计"""
        user = request.user
        
        # 获取用户的API密钥
        keys = self._get_user_api_keys(user)
        
        stats = {
            'total_keys': len(keys),
            'key_usage': []
        }
        
        for key_hash, key_data in keys.items():
            # 获取使用统计
            usage_key = f"api_requests_{key_hash}"
            usage_count = cache.get(usage_key, 0)
            
            stats['key_usage'].append({
                'key_prefix': key_hash[:8] + '...',
                'requests_today': usage_count,
                'last_used': key_data.get('last_used'),
                'created_at': key_data.get('created_at')
            })
        
        return Response(stats)
    
    def _get_user_api_keys(self, user):
        """获取用户的所有API密钥"""
        # 扫描缓存中属于该用户的API密钥
        keys = {}
        
        # 这里简化实现，实际应该有更好的索引机制
        # 在生产环境中，建议使用数据库存储API密钥信息
        cache_pattern = "api_key_*"
        
        # 由于Django缓存不支持模式匹配，这里使用一个变通方法
        # 实际应该在生成密钥时同时维护用户密钥索引
        user_keys_index = cache.get(f"user_api_keys_{user.id}", [])
        
        for key_hash in user_keys_index:
            cache_key = f"api_key_{key_hash}"
            key_data = cache.get(cache_key)
            if key_data and key_data.get('user_id') == user.id:
                keys[key_hash] = key_data
        
        return keys


class SecurityManagementViewSet(viewsets.GenericViewSet):
    """安全管理ViewSet"""
    
    permission_classes = [EnglishAdminPermission]
    throttle_classes = [EnglishManagementThrottle]
    
    @action(detail=False, methods=['get'])
    def security_logs(self, request):
        """获取安全日志（管理员专用）"""
        # 这里简化实现，实际应该从专门的日志存储中读取
        log_type = request.query_params.get('type', 'all')
        limit = min(int(request.query_params.get('limit', 50)), 200)
        
        # 模拟日志数据
        logs = [
            {
                'timestamp': timezone.now().isoformat(),
                'event_type': 'API_ACCESS',
                'user_id': request.user.id,
                'ip_address': '127.0.0.1',
                'details': 'Normal API access'
            }
        ]
        
        return Response({
            'logs': logs[:limit],
            'total_count': len(logs),
            'log_type': log_type
        })
    
    @action(detail=False, methods=['post'])
    def block_ip(self, request):
        """阻止IP地址"""
        ip_address = request.data.get('ip_address')
        reason = request.data.get('reason', 'Manual block')
        duration_hours = int(request.data.get('duration_hours', 24))
        
        if not ip_address:
            return Response({
                'error': 'ip_address参数必需'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 添加到IP黑名单
        blocked_key = f"blocked_ip_{ip_address}"
        cache.set(blocked_key, {
            'reason': reason,
            'blocked_by': request.user.username,
            'blocked_at': timezone.now().isoformat()
        }, timeout=duration_hours * 3600)
        
        SecurityAuditLogger.log_security_event(
            'IP_BLOCKED',
            request.user,
            {'ip': ip_address, 'reason': reason, 'duration_hours': duration_hours},
            request
        )
        
        return Response({
            'message': f'IP {ip_address} 已被阻止 {duration_hours} 小时',
            'ip_address': ip_address,
            'duration_hours': duration_hours
        })
    
    @action(detail=False, methods=['post'])
    def unblock_ip(self, request):
        """解除IP阻止"""
        ip_address = request.data.get('ip_address')
        
        if not ip_address:
            return Response({
                'error': 'ip_address参数必需'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        blocked_key = f"blocked_ip_{ip_address}"
        was_blocked = cache.get(blocked_key) is not None
        cache.delete(blocked_key)
        
        if was_blocked:
            SecurityAuditLogger.log_security_event(
                'IP_UNBLOCKED',
                request.user,
                {'ip': ip_address},
                request
            )
        
        return Response({
            'message': f'IP {ip_address} 阻止状态已解除',
            'was_blocked': was_blocked
        })
    
    @action(detail=False, methods=['get'])
    def system_stats(self, request):
        """系统安全统计"""
        # 获取各种统计数据
        stats = {
            'api_keys_active': self._count_active_api_keys(),
            'blocked_ips': self._count_blocked_ips(),
            'recent_security_events': self._count_recent_security_events(),
            'user_activity': self._get_user_activity_stats()
        }
        
        return Response(stats)
    
    def _count_active_api_keys(self):
        """统计活跃API密钥数量"""
        # 简化实现
        return 0
    
    def _count_blocked_ips(self):
        """统计被阻止的IP数量"""
        # 简化实现
        return 0
    
    def _count_recent_security_events(self):
        """统计最近的安全事件"""
        # 简化实现
        return 0
    
    def _get_user_activity_stats(self):
        """获取用户活动统计"""
        # 简化实现
        return {
            'active_users_today': 0,
            'total_api_requests_today': 0
        }
