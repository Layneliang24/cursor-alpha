# -*- coding: utf-8 -*-
"""
AI服务异常定义
统一的异常处理机制
"""


class AIServiceException(Exception):
    """AI服务基础异常"""
    
    def __init__(self, message: str, error_code: str = None, provider: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.provider = provider
    
    def to_dict(self):
        return {
            'error': self.message,
            'error_code': self.error_code,
            'provider': self.provider,
            'type': self.__class__.__name__
        }


class RateLimitException(AIServiceException):
    """API调用频率限制异常"""
    
    def __init__(self, message: str = "API调用频率超限", retry_after: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class AuthenticationException(AIServiceException):
    """API认证失败异常"""
    
    def __init__(self, message: str = "API认证失败，请检查密钥", **kwargs):
        super().__init__(message, **kwargs)


class ModelNotFoundException(AIServiceException):
    """模型不存在异常"""
    
    def __init__(self, model_name: str, **kwargs):
        message = f"模型 {model_name} 不存在或不可用"
        super().__init__(message, **kwargs)
        self.model_name = model_name


class QuotaExceededException(AIServiceException):
    """API配额超限异常"""
    
    def __init__(self, message: str = "API配额已用完", **kwargs):
        super().__init__(message, **kwargs)


class ServiceUnavailableException(AIServiceException):
    """服务不可用异常"""
    
    def __init__(self, message: str = "AI服务暂时不可用", **kwargs):
        super().__init__(message, **kwargs)


class InvalidRequestException(AIServiceException):
    """请求参数无效异常"""
    
    def __init__(self, message: str = "请求参数无效", **kwargs):
        super().__init__(message, **kwargs)


class ResponseParseException(AIServiceException):
    """响应解析异常"""
    
    def __init__(self, message: str = "AI响应解析失败", raw_response: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.raw_response = raw_response


class ContextTooLongException(AIServiceException):
    """上下文过长异常"""
    
    def __init__(self, message: str = "上下文长度超过模型限制", context_length: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.context_length = context_length
