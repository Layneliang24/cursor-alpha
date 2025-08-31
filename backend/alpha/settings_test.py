"""
测试环境专用设置
用于CI/CD流水线中的自动化测试
"""

from .settings import *
import os
import sys

# 强制使用测试模式
DEBUG = False
TESTING = True

# 测试数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'alpha_db_test'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'meimei520'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES', time_zone='+08:00'",
        },
        'TEST': {
            'NAME': 'test_alpha_db',
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
            'CREATE_DB': True,
            'DEPENDENCIES': [],
        }
    }
}

# Redis配置（测试环境）
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

# 缓存配置（使用Redis或内存缓存）
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'alpha_test_cache',
        'TIMEOUT': 300,
    }
}

# 如果Redis不可用，回退到本地内存缓存
try:
    from django_redis import get_redis_connection
    get_redis_connection("default").ping()
except:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'test-cache',
            'TIMEOUT': 300,
        }
    }

# 日志配置（简化测试输出）
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# 静态文件配置
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_test')

# 媒体文件配置
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_test')

# 邮件配置（测试模式）
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 安全设置（测试环境放宽）
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True

# 禁用某些中间件以提高测试速度
MIDDLEWARE = [m for m in MIDDLEWARE if 'debug_toolbar' not in m.lower()]

# 密钥配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'test-secret-key-for-ci-cd-pipeline-only')

# 时区设置
USE_TZ = False  # 简化测试环境

# 验证码配置（测试环境可以考虑简化）
CAPTCHA_TEST_MODE = True

# AI服务配置（测试环境使用mock或简化配置）
# 可以在这里添加测试专用的AI服务配置

# Celery配置（如果使用）
CELERY_TASK_ALWAYS_EAGER = True  # 测试环境同步执行任务
CELERY_TASK_EAGER_PROPAGATES = True

# 测试数据库优化
if 'test' in sys.argv:
    # 使用更快的密码哈希算法
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]
    
    # 注释掉禁用迁移的设置，避免表重复创建冲突
    # MIGRATION_MODULES = {
    #     'users': None,
    #     'articles': None,
    #     'categories': None,
    #     'links': None,
    #     'api': None,
    #     'english': None,
    #     'jobs': None,
    #     'todos': None,
    #     'ai': None,
    #     'search': None,
    #     'feature_flags': None,
    # }

# 测试覆盖率配置
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'admin$', 'django_extensions',
]

# API限流配置（测试环境放宽）
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '1000/hour',
    'user': '2000/hour'
}

# 测试环境配置已加载
# 数据库: {DATABASES['default']['NAME']}@{DATABASES['default']['HOST']}
# 缓存: {CACHES['default']['BACKEND']}
# 调试模式: {DEBUG}
