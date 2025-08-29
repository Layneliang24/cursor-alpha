"""
地道表达模块安全控制
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.contrib.auth.models import Group
from django.core.cache import cache
import hashlib
import time
from datetime import datetime, timedelta
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EnglishLearnerPermission(BasePermission):
    """地道表达学习者权限 - 认证用户可访问学习功能"""
    
    def has_permission(self, request, view):
        # 读取操作允许所有认证用户
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        
        # 写操作需要认证且账户活跃
        user = request.user
        return (user and user.is_authenticated and user.is_active)


class EnglishContentManagerPermission(BasePermission):
    """地道表达内容管理权限 - 管理员或内容管理员可管理表达式"""
    
    def has_permission(self, request, view):
        # 读取允许认证用户
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        
        user = request.user
        if not (user and user.is_authenticated):
            return False
            
        # Django管理员
        if user.is_staff or user.is_superuser:
            return True
            
        # 内容管理员组
        try:
            return user.groups.filter(name__in=['内容管理员', '管理员']).exists()
        except Exception:
            return False


class EnglishAdminPermission(BasePermission):
    """地道表达管理员权限 - 系统配置和高级管理"""
    
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
            
        # Django超级管理员
        if user.is_superuser:
            return True
            
        # 英语模块管理员组
        try:
            return user.groups.filter(name='英语模块管理员').exists()
        except Exception:
            return False


class UserProgressOwnerPermission(BasePermission):
    """用户学习进度权限 - 只能访问自己的学习进度"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        # 管理员可访问所有用户进度
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        # 用户只能访问自己的进度
        return obj.user == request.user


class EnglishAPIThrottle(UserRateThrottle):
    """地道表达API限流 - 更严格的限制"""
    scope = 'english_api'
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return f'throttle_{self.scope}_{ident}'


class EnglishCrawlerThrottle(UserRateThrottle):
    """爬虫API限流 - 最严格限制"""
    scope = 'english_crawler'
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return f'throttle_{self.scope}_{ident}'


class APIKeyAuthentication:
    """API密钥认证"""
    
    @staticmethod
    def generate_api_key(user):
        """为用户生成API密钥"""
        timestamp = str(int(time.time()))
        user_id = str(user.id)
        raw_key = f"{user_id}_{timestamp}_{user.username}"
        api_key = hashlib.sha256(raw_key.encode()).hexdigest()
        
        # 存储到缓存，设置过期时间
        cache_key = f"api_key_{api_key}"
        cache.set(cache_key, {
            'user_id': user.id,
            'username': user.username,
            'created_at': timestamp,
            'last_used': timestamp
        }, timeout=86400 * 30)  # 30天过期
        
        # 维护用户密钥索引
        user_keys_index = cache.get(f"user_api_keys_{user.id}", [])
        user_keys_index.append(api_key)
        cache.set(f"user_api_keys_{user.id}", user_keys_index, timeout=86400 * 30)
        
        return api_key
    
    @staticmethod
    def validate_api_key(api_key):
        """验证API密钥"""
        cache_key = f"api_key_{api_key}"
        key_data = cache.get(cache_key)
        
        if not key_data:
            return None
            
        # 更新最后使用时间
        key_data['last_used'] = str(int(time.time()))
        cache.set(cache_key, key_data, timeout=86400 * 30)
        
        return key_data
    
    @staticmethod
    def revoke_api_key(api_key):
        """撤销API密钥"""
        cache_key = f"api_key_{api_key}"
        key_data = cache.get(cache_key)
        
        if key_data:
            # 从用户密钥索引中移除
            user_id = key_data.get('user_id')
            if user_id:
                user_keys_index = cache.get(f"user_api_keys_{user_id}", [])
                if api_key in user_keys_index:
                    user_keys_index.remove(api_key)
                    cache.set(f"user_api_keys_{user_id}", user_keys_index, timeout=86400 * 30)
        
        cache.delete(cache_key)


class SecurityAuditLogger:
    """安全审计日志记录器"""
    
    @staticmethod
    def log_api_access(request, view_name, action=None, user=None):
        """记录API访问"""
        user = user or request.user
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user.id if user.is_authenticated else None,
            'username': user.username if user.is_authenticated else 'anonymous',
            'ip_address': SecurityAuditLogger._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'method': request.method,
            'path': request.path,
            'view_name': view_name,
            'action': action,
            'query_params': dict(request.GET),
        }
        
        logger.info(f"API_ACCESS: {log_data}")
    
    @staticmethod
    def log_security_event(event_type, user, details, request=None):
        """记录安全事件"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user.id if user else None,
            'username': user.username if user else 'anonymous',
            'ip_address': SecurityAuditLogger._get_client_ip(request) if request else None,
            'details': details,
        }
        
        logger.warning(f"SECURITY_EVENT: {log_data}")
    
    @staticmethod
    def log_permission_denied(request, view_name, reason):
        """记录权限拒绝"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'user_id': request.user.id if request.user.is_authenticated else None,
            'username': request.user.username if request.user.is_authenticated else 'anonymous',
            'ip_address': SecurityAuditLogger._get_client_ip(request),
            'view_name': view_name,
            'reason': reason,
            'path': request.path,
            'method': request.method,
        }
        
        logger.warning(f"PERMISSION_DENIED: {log_data}")
    
    @staticmethod
    def _get_client_ip(request):
        """获取客户端IP地址"""
        if not request:
            return None
            
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityRateLimiter:
    """安全限流器 - 防止暴力破解和DDoS"""
    
    @staticmethod
    def check_login_attempts(ip_address, max_attempts=5, window_minutes=15):
        """检查登录尝试次数"""
        cache_key = f"login_attempts_{ip_address}"
        attempts = cache.get(cache_key, 0)
        
        if attempts >= max_attempts:
            return False, f"IP {ip_address} 登录尝试过多，请{window_minutes}分钟后再试"
        
        return True, None
    
    @staticmethod
    def record_login_attempt(ip_address, success=False, window_minutes=15):
        """记录登录尝试"""
        cache_key = f"login_attempts_{ip_address}"
        
        if success:
            # 成功登录，清除计数
            cache.delete(cache_key)
        else:
            # 失败登录，增加计数
            attempts = cache.get(cache_key, 0)
            cache.set(cache_key, attempts + 1, timeout=window_minutes * 60)
    
    @staticmethod
    def check_api_key_requests(api_key, max_requests=100, window_hours=1):
        """检查API密钥请求频率"""
        cache_key = f"api_requests_{api_key}"
        requests = cache.get(cache_key, 0)
        
        if requests >= max_requests:
            return False, f"API密钥请求过多，请{window_hours}小时后再试"
        
        return True, None
    
    @staticmethod
    def record_api_request(api_key, window_hours=1):
        """记录API请求"""
        cache_key = f"api_requests_{api_key}"
        requests = cache.get(cache_key, 0)
        cache.set(cache_key, requests + 1, timeout=window_hours * 3600)


class ContentSecurityValidator:
    """内容安全验证器"""
    
    # 敏感词列表（示例）
    SENSITIVE_WORDS = [
        'spam', 'hack', 'exploit', 'malware', 'phishing',
        'fraud', 'scam', 'abuse', 'illegal', 'violence'
    ]
    
    @classmethod
    def validate_expression_content(cls, expression_text, meaning_text=""):
        """验证表达式内容安全性"""
        combined_text = f"{expression_text} {meaning_text}".lower()
        
        # 检查敏感词
        for word in cls.SENSITIVE_WORDS:
            if word in combined_text:
                return False, f"内容包含敏感词: {word}"
        
        # 检查长度限制
        if len(expression_text) > 500:
            return False, "表达式过长"
        
        if len(meaning_text) > 2000:
            return False, "释义过长"
        
        return True, None
    
    @classmethod
    def validate_user_input(cls, text, max_length=1000):
        """验证用户输入内容"""
        if not text:
            return True, None
            
        if len(text) > max_length:
            return False, f"内容长度超限(最大{max_length}字符)"
        
        # 基础XSS防护
        dangerous_patterns = ['<script', 'javascript:', 'onclick=', 'onerror=']
        text_lower = text.lower()
        
        for pattern in dangerous_patterns:
            if pattern in text_lower:
                return False, f"内容包含潜在危险代码: {pattern}"
        
        return True, None


class EnglishAPIKeyPermission(BasePermission):
    """API密钥权限验证"""
    
    def has_permission(self, request, view):
        # 检查是否有API密钥
        api_key = request.META.get('HTTP_X_API_KEY') or request.GET.get('api_key')
        
        if not api_key:
            return False
        
        # 验证API密钥
        key_data = APIKeyAuthentication.validate_api_key(api_key)
        if not key_data:
            SecurityAuditLogger.log_security_event(
                'INVALID_API_KEY', 
                None, 
                {'api_key': api_key[:8] + '...', 'ip': SecurityAuditLogger._get_client_ip(request)},
                request
            )
            return False
        
        # 检查请求频率
        allowed, message = SecurityRateLimiter.check_api_key_requests(api_key)
        if not allowed:
            SecurityAuditLogger.log_security_event(
                'API_RATE_LIMIT_EXCEEDED', 
                None, 
                {'api_key': api_key[:8] + '...', 'message': message},
                request
            )
            return False
        
        # 记录请求
        SecurityRateLimiter.record_api_request(api_key)
        
        # 将用户信息添加到请求中
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=key_data['user_id'])
            request.api_key_user = user
        except User.DoesNotExist:
            return False
        
        return True


class EnglishExpressionsThrottle(UserRateThrottle):
    """表达式查询限流"""
    scope = 'english_expressions'


class EnglishLearningThrottle(UserRateThrottle):
    """学习功能限流"""
    scope = 'english_learning'


class EnglishManagementThrottle(UserRateThrottle):
    """管理功能限流"""
    scope = 'english_management'


class EnglishAnonymousThrottle(AnonRateThrottle):
    """匿名用户限流"""
    scope = 'english_anon'
