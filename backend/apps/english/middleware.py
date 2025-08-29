"""
地道表达模块安全中间件
"""
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from .security import SecurityAuditLogger, SecurityRateLimiter, ContentSecurityValidator
import json
import logging

logger = logging.getLogger(__name__)


class EnglishSecurityMiddleware(MiddlewareMixin):
    """地道表达安全中间件"""
    
    def process_request(self, request):
        """处理请求前的安全检查"""
        # 只对英语模块API进行安全检查
        if not self._is_english_api(request.path):
            return None
        
        # 记录API访问
        view_name = self._extract_view_name(request.path)
        SecurityAuditLogger.log_api_access(request, view_name)
        
        # 检查IP黑名单
        if self._is_blocked_ip(request):
            SecurityAuditLogger.log_security_event(
                'BLOCKED_IP_ACCESS',
                request.user if hasattr(request, 'user') else None,
                {'ip': SecurityAuditLogger._get_client_ip(request), 'path': request.path},
                request
            )
            return JsonResponse({
                'error': 'Access denied',
                'code': 'IP_BLOCKED'
            }, status=403)
        
        # 检查请求大小
        if self._check_request_size(request):
            return JsonResponse({
                'error': 'Request too large',
                'code': 'REQUEST_SIZE_LIMIT'
            }, status=413)
        
        return None
    
    def process_response(self, request, response):
        """处理响应"""
        # 添加安全头
        if self._is_english_api(request.path):
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
    
    def _is_english_api(self, path):
        """判断是否为英语模块API"""
        english_paths = [
            '/api/expressions/',
            '/api/expression-progress/',
            '/api/learning-sessions/',
            '/api/expression-sources/',
            '/api/expression-scenarios/',
            '/api/statistics/',
            '/api/ai-assistant/'
        ]
        return any(path.startswith(ep) for ep in english_paths)
    
    def _extract_view_name(self, path):
        """从路径提取视图名称"""
        path_mapping = {
            '/api/expressions/': 'IdiomaticExpressionViewSet',
            '/api/expression-progress/': 'UserExpressionProgressViewSet',
            '/api/learning-sessions/': 'LearningSessionViewSet',
            '/api/expression-sources/': 'ExpressionSourceViewSet',
            '/api/expression-scenarios/': 'ExpressionScenarioViewSet',
            '/api/statistics/': 'StatisticsViewSet',
            '/api/ai-assistant/': 'AIAssistantViewSet',
        }
        
        for prefix, view_name in path_mapping.items():
            if path.startswith(prefix):
                return view_name
        return 'UnknownView'
    
    def _is_blocked_ip(self, request):
        """检查IP是否被阻止"""
        ip = SecurityAuditLogger._get_client_ip(request)
        if not ip:
            return False
        
        # 检查IP黑名单缓存
        blocked_key = f"blocked_ip_{ip}"
        return cache.get(blocked_key, False)
    
    def _check_request_size(self, request):
        """检查请求大小"""
        if hasattr(request, 'body'):
            # 限制请求体大小为10MB
            max_size = 10 * 1024 * 1024  
            return len(request.body) > max_size
        return False


class EnglishAPIKeyMiddleware(MiddlewareMixin):
    """API密钥认证中间件"""
    
    def process_request(self, request):
        """处理API密钥认证"""
        # 只对特定API路径进行密钥验证
        if not self._requires_api_key(request.path):
            return None
        
        api_key = request.META.get('HTTP_X_API_KEY') or request.GET.get('api_key')
        
        if not api_key:
            return JsonResponse({
                'error': 'API key required',
                'code': 'API_KEY_MISSING'
            }, status=401)
        
        # 验证API密钥
        from .security import APIKeyAuthentication
        key_data = APIKeyAuthentication.validate_api_key(api_key)
        
        if not key_data:
            SecurityAuditLogger.log_security_event(
                'INVALID_API_KEY_ATTEMPT',
                None,
                {'api_key_prefix': api_key[:8] + '...', 'path': request.path},
                request
            )
            return JsonResponse({
                'error': 'Invalid API key',
                'code': 'API_KEY_INVALID'
            }, status=401)
        
        # 将API密钥用户信息添加到请求
        request.api_key_data = key_data
        
        return None
    
    def _requires_api_key(self, path):
        """判断路径是否需要API密钥"""
        # 批量操作和管理功能需要API密钥
        api_key_paths = [
            '/api/expressions/batch_create/',
            '/api/expressions/batch_update/',
            '/api/expression-progress/batch_update_progress/',
            '/api/statistics/overview/',
            '/api/ai-assistant/chat/'
        ]
        return any(path.startswith(akp) for akp in api_key_paths)


class ContentSecurityMiddleware(MiddlewareMixin):
    """内容安全中间件"""
    
    def process_request(self, request):
        """处理内容安全验证"""
        if not self._is_english_api(request.path):
            return None
        
        # 只检查POST和PUT请求的内容
        if request.method not in ['POST', 'PUT', 'PATCH']:
            return None
        
        try:
            if hasattr(request, 'body') and request.body:
                data = json.loads(request.body.decode('utf-8'))
                
                # 验证表达式内容
                if 'expression' in data or 'meaning' in data:
                    expression = data.get('expression', '')
                    meaning = data.get('meaning', '')
                    
                    is_safe, error_msg = ContentSecurityValidator.validate_expression_content(
                        expression, meaning
                    )
                    
                    if not is_safe:
                        SecurityAuditLogger.log_security_event(
                            'UNSAFE_CONTENT_DETECTED',
                            request.user if hasattr(request, 'user') else None,
                            {'error': error_msg, 'expression': expression[:50]},
                            request
                        )
                        return JsonResponse({
                            'error': f'Content validation failed: {error_msg}',
                            'code': 'CONTENT_UNSAFE'
                        }, status=400)
                
                # 验证用户输入字段
                user_input_fields = ['notes', 'feedback', 'comment', 'description']
                for field in user_input_fields:
                    if field in data:
                        is_safe, error_msg = ContentSecurityValidator.validate_user_input(
                            data[field]
                        )
                        if not is_safe:
                            return JsonResponse({
                                'error': f'Input validation failed: {error_msg}',
                                'code': 'INPUT_UNSAFE'
                            }, status=400)
        
        except (json.JSONDecodeError, UnicodeDecodeError):
            # 忽略非JSON请求
            pass
        except Exception as e:
            logger.error(f"Content security check failed: {e}")
        
        return None
    
    def _is_english_api(self, path):
        """判断是否为英语模块API"""
        english_paths = [
            '/api/expressions/',
            '/api/expression-progress/',
            '/api/learning-sessions/',
            '/api/expression-sources/',
            '/api/expression-scenarios/',
            '/api/statistics/',
            '/api/ai-assistant/'
        ]
        return any(path.startswith(ep) for ep in english_paths)
