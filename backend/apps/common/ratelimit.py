"""
速率限制工具类和装饰器
基于django-ratelimit实现API防护
"""
import logging
from functools import wraps
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class RateLimitConfig:
    """速率限制配置"""
    
    # 不同API端点的速率限制配置
    API_LIMITS = {
        # AI配置相关API - 较低限制
        'ai_config': {
            'rate': '30/m',  # 每分钟30次
            'block': True,
            'methods': ['GET', 'POST', 'PUT', 'DELETE']
        },
        
        # AI提供商测试 - 更严格限制
        'ai_test': {
            'rate': '10/m',  # 每分钟10次
            'block': True,
            'methods': ['POST']
        },
        
        # 用户认证相关 - 严格限制
        'auth': {
            'rate': '20/m',  # 每分钟20次
            'block': True,
            'methods': ['POST']
        },
        
        # 英语学习相关 - 中等限制
        'english_learning': {
            'rate': '100/m',  # 每分钟100次
            'block': True,
            'methods': ['GET', 'POST']
        },
        
        # 数据查询 - 宽松限制
        'data_query': {
            'rate': '200/m',  # 每分钟200次
            'block': True,
            'methods': ['GET']
        },
        
        # 文件上传 - 严格限制
        'file_upload': {
            'rate': '5/m',   # 每分钟5次
            'block': True,
            'methods': ['POST']
        }
    }
    
    # 基于用户角色的限制倍数
    ROLE_MULTIPLIERS = {
        'admin': 5.0,      # 管理员：5倍限制
        'moderator': 3.0,  # 版主：3倍限制
        'editor': 2.0,     # 编辑者：2倍限制
        'user': 1.0,       # 普通用户：基础限制
        'guest': 0.5       # 访客：0.5倍限制
    }

def get_user_rate_key(group, request):
    """获取基于用户的速率限制键"""
    if request.user.is_authenticated:
        # 已认证用户：使用用户ID
        return f"user_{request.user.id}"
    else:
        # 未认证用户：使用IP地址
        return f"ip_{get_client_ip(request)}"

def get_client_ip(request):
    """获取客户端真实IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_role_multiplier(user):
    """获取用户角色对应的速率限制倍数"""
    if not user.is_authenticated:
        return RateLimitConfig.ROLE_MULTIPLIERS['guest']
    
    # 检查用户角色（基于RBAC系统）
    try:
        from apps.rbac.services import RBACService
        user_roles = RBACService.get_user_roles(user)
        
        # 取最高权限角色的倍数
        max_multiplier = RateLimitConfig.ROLE_MULTIPLIERS['user']  # 默认
        for role in user_roles:
            role_name = role.name.lower()
            if role_name in RateLimitConfig.ROLE_MULTIPLIERS:
                multiplier = RateLimitConfig.ROLE_MULTIPLIERS[role_name]
                max_multiplier = max(max_multiplier, multiplier)
        
        return max_multiplier
    except Exception as e:
        logger.warning(f"获取用户角色失败: {str(e)}")
        return RateLimitConfig.ROLE_MULTIPLIERS['user']

def calculate_user_rate_limit(base_rate: str, user) -> str:
    """根据用户角色计算实际速率限制"""
    try:
        # 解析基础速率 (如 "30/m")
        rate_parts = base_rate.split('/')
        if len(rate_parts) != 2:
            return base_rate
        
        count = int(rate_parts[0])
        period = rate_parts[1]
        
        # 获取用户倍数
        multiplier = get_user_role_multiplier(user)
        
        # 计算新的限制
        new_count = int(count * multiplier)
        return f"{new_count}/{period}"
    except Exception as e:
        logger.warning(f"计算用户速率限制失败: {str(e)}")
        return base_rate

# 装饰器工厂函数
def api_ratelimit(limit_type: str = 'data_query', custom_rate: str = None):
    """
    API速率限制装饰器
    
    Args:
        limit_type: 限制类型，对应RateLimitConfig.API_LIMITS中的键
        custom_rate: 自定义速率，格式如 "30/m"
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # 获取限制配置
            if custom_rate:
                rate = custom_rate
            else:
                config = RateLimitConfig.API_LIMITS.get(limit_type, RateLimitConfig.API_LIMITS['data_query'])
                rate = config['rate']
            
            # 根据用户角色调整限制
            user_rate = calculate_user_rate_limit(rate, request.user)
            
            # 应用速率限制
            @ratelimit(
                key=get_user_rate_key,
                rate=user_rate,
                method=ratelimit.ALL,
                block=True
            )
            def limited_view(request, *args, **kwargs):
                return func(self, request, *args, **kwargs)
            
            try:
                return limited_view(request, *args, **kwargs)
            except Ratelimited:
                # 记录速率限制事件
                logger.warning(
                    f"速率限制触发: {get_client_ip(request)} - "
                    f"{request.user.username if request.user.is_authenticated else 'Anonymous'} - "
                    f"{request.method} {request.path}"
                )
                
                # 返回429错误
                if hasattr(self, 'get_serializer'):
                    # DRF ViewSet
                    return Response(
                        {
                            'error': '请求过于频繁，请稍后再试',
                            'detail': f'速率限制: {user_rate}',
                            'retry_after': 60
                        },
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )
                else:
                    # 普通Django视图
                    return JsonResponse(
                        {
                            'error': '请求过于频繁，请稍后再试',
                            'retry_after': 60
                        },
                        status=429
                    )
        
        return wrapper
    return decorator

def sensitive_operation_limit(rate: str = '5/m'):
    """
    敏感操作速率限制装饰器
    用于密钥管理、配置修改等敏感操作
    """
    def decorator(func):
        @wraps(func)
        @ratelimit(
            key=get_user_rate_key,
            rate=rate,
            method=ratelimit.ALL,
            block=True
        )
        def wrapper(request, *args, **kwargs):
            try:
                return func(request, *args, **kwargs)
            except Ratelimited:
                logger.warning(
                    f"敏感操作速率限制: {get_client_ip(request)} - "
                    f"{request.user.username if request.user.is_authenticated else 'Anonymous'} - "
                    f"{func.__name__}"
                )
                
                return Response(
                    {
                        'error': '敏感操作过于频繁，请稍后再试',
                        'detail': f'限制: {rate}',
                        'retry_after': 300  # 5分钟后重试
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
        
        return wrapper
    return decorator

class RateLimitMiddleware:
    """速率限制中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 检查是否为API请求
        if request.path.startswith('/api/'):
            # 记录API请求
            self.log_api_request(request)
            
            # 检查全局速率限制
            if self.is_globally_rate_limited(request):
                return JsonResponse(
                    {'error': '全局请求限制，请稍后再试'},
                    status=429
                )
        
        response = self.get_response(request)
        
        # 添加速率限制相关头
        if hasattr(response, 'status_code') and response.status_code == 429:
            response['Retry-After'] = '60'
            response['X-RateLimit-Limit'] = self.get_rate_limit_for_request(request)
            response['X-RateLimit-Remaining'] = '0'
        
        return response
    
    def log_api_request(self, request):
        """记录API请求"""
        try:
            client_ip = get_client_ip(request)
            user_info = request.user.username if request.user.is_authenticated else 'Anonymous'
            
            logger.info(
                f"API请求: {request.method} {request.path} - "
                f"IP: {client_ip} - User: {user_info}"
            )
        except Exception as e:
            logger.error(f"记录API请求失败: {str(e)}")
    
    def is_globally_rate_limited(self, request):
        """检查全局速率限制"""
        client_ip = get_client_ip(request)
        cache_key = f"global_limit_{client_ip}"
        
        # 每个IP每分钟最多1000次请求
        current_count = cache.get(cache_key, 0)
        if current_count >= 1000:
            return True
        
        # 增加计数
        cache.set(cache_key, current_count + 1, 60)  # 1分钟过期
        return False
    
    def get_rate_limit_for_request(self, request):
        """获取请求的速率限制"""
        # 根据请求路径确定限制类型
        if '/ai/' in request.path:
            if '/test' in request.path:
                return RateLimitConfig.API_LIMITS['ai_test']['rate']
            else:
                return RateLimitConfig.API_LIMITS['ai_config']['rate']
        elif '/auth/' in request.path:
            return RateLimitConfig.API_LIMITS['auth']['rate']
        elif '/english/' in request.path:
            return RateLimitConfig.API_LIMITS['english_learning']['rate']
        else:
            return RateLimitConfig.API_LIMITS['data_query']['rate']

# 常用速率限制装饰器实例
ai_config_limit = api_ratelimit('ai_config')
ai_test_limit = api_ratelimit('ai_test')
auth_limit = api_ratelimit('auth')
english_learning_limit = api_ratelimit('english_learning')
file_upload_limit = api_ratelimit('file_upload')

# 敏感操作限制
sensitive_limit = sensitive_operation_limit('3/m')  # 每分钟3次
critical_limit = sensitive_operation_limit('1/m')   # 每分钟1次
