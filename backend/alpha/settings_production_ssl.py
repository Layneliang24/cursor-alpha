"""
生产环境SSL安全配置
基于settings.py的SSL增强配置
"""
import os
from .settings import *

# 强制HTTPS重定向
SECURE_SSL_REDIRECT = True

# HSTS配置 - 严格传输安全
SECURE_HSTS_SECONDS = 31536000  # 1年
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie安全配置
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# 代理配置 - 信任反向代理的SSL头
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# 其他安全设置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# 允许的主机（生产环境需要配置实际域名）
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    # 添加实际的生产域名
    # 'yourdomain.com',
    # 'www.yourdomain.com',
]

# SSL证书路径配置
SSL_CERT_DIR = os.environ.get('SSL_CERT_DIR', '/etc/ssl/certs')
SSL_KEY_DIR = os.environ.get('SSL_KEY_DIR', '/etc/ssl/private')
SSL_DOMAINS = os.environ.get('SSL_DOMAINS', 'localhost').split(',')

# 数据库连接加密（如果支持）
if 'default' in DATABASES:
    DATABASES['default']['OPTIONS'] = DATABASES['default'].get('OPTIONS', {})
    # MySQL SSL配置
    if DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
        DATABASES['default']['OPTIONS'].update({
            'ssl_disabled': False,
            'ssl_verify_cert': True,
            'ssl_verify_identity': True,
        })
    # PostgreSQL SSL配置
    elif DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
        DATABASES['default']['OPTIONS'].update({
            'sslmode': 'require',
        })

# Redis连接加密（如果使用Redis）
if 'default' in CACHES and 'redis' in CACHES['default']['LOCATION']:
    # Redis SSL配置
    CACHES['default']['OPTIONS'] = CACHES['default'].get('OPTIONS', {})
    CACHES['default']['OPTIONS'].update({
        'CONNECTION_POOL_KWARGS': {
            'ssl_cert_reqs': 'required',
            'ssl_check_hostname': True,
        }
    })

# 邮件SSL配置
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False  # 如果使用465端口则设为True
EMAIL_PORT = 587  # TLS端口，SSL端口为465

# 日志配置 - 增强安全日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'security': {
            'format': '[SECURITY] {levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/security.log',
            'formatter': 'security',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps.common.ssl_config': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.ai.views': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# API密钥安全配置
API_KEY_SECURITY = {
    'require_https': True,
    'log_access': True,
    'mask_in_logs': True,
    'rotation_days': 90,  # 建议90天轮换密钥
}

# 证书监控配置
CERTIFICATE_MONITORING = {
    'check_interval_hours': 24,  # 每24小时检查一次
    'warning_days': 30,  # 30天内过期发出警告
    'critical_days': 7,   # 7天内过期发出紧急警告
    'auto_renew': False,  # 是否自动续期（需要配置）
}

# 安全中间件配置
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 在最前面添加SSL重定向中间件
    *MIDDLEWARE
]

# 如果使用Celery，添加SSL配置
if 'CELERY_BROKER_URL' in globals():
    if CELERY_BROKER_URL.startswith('redis://'):
        # Redis broker SSL配置
        CELERY_BROKER_USE_SSL = {
            'ssl_cert_reqs': 'required',
            'ssl_check_hostname': True,
        }
        CELERY_RESULT_BACKEND_USE_SSL = CELERY_BROKER_USE_SSL

# 开发环境自签名证书支持
if DEBUG:
    # 开发环境可以使用自签名证书
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # 降低HSTS要求
    SECURE_HSTS_SECONDS = 0
    SECURE_SSL_REDIRECT = False
    
    # 允许HTTP cookie（开发环境）
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# 生产环境额外检查
if not DEBUG:
    # 确保SECRET_KEY在生产环境中是安全的
    if SECRET_KEY == 'django-insecure-default-key':
        raise ValueError('生产环境必须设置安全的SECRET_KEY')
    
    # 确保数据库密码不为空
    if not DATABASES['default'].get('PASSWORD'):
        raise ValueError('生产环境数据库必须设置密码')
    
    # 确保配置了实际域名
    if ALLOWED_HOSTS == ['*'] or 'localhost' in ALLOWED_HOSTS:
        import warnings
        warnings.warn('生产环境应配置具体的ALLOWED_HOSTS')

# 健康检查端点配置
HEALTH_CHECK_SSL_REQUIRED = True

# API版本和SSL要求
API_SSL_REQUIRED_VERSIONS = ['v1', 'v2']  # 需要SSL的API版本

print("✅ SSL安全配置已加载")
print(f"   - SSL重定向: {'启用' if SECURE_SSL_REDIRECT else '禁用'}")
print(f"   - HSTS: {'启用' if SECURE_HSTS_SECONDS > 0 else '禁用'}")
print(f"   - 安全Cookie: {'启用' if SESSION_COOKIE_SECURE else '禁用'}")
print(f"   - 允许的主机: {ALLOWED_HOSTS}")
