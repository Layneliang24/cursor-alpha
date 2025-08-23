"""
CI/CD环境测试配置

针对GitHub Actions等CI/CD环境优化的Django设置
"""

import os
from .test_settings_mysql import *

# CI/CD环境标识
CI_ENVIRONMENT = True

# 数据库配置 - 使用环境变量
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])
    DATABASES['default']['TEST'] = {'NAME': 'test_alpha_ci'}
else:
    # 默认使用MySQL测试配置
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'test_alpha_ci',
            'USER': 'root',
            'PASSWORD': 'root',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
            'TEST': {
                'NAME': 'test_alpha_ci',
                'CHARSET': 'utf8mb4',
                'COLLATION': 'utf8mb4_unicode_ci',
            }
        }
    }

# Redis配置 - 使用环境变量
if 'REDIS_URL' in os.environ:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ['REDIS_URL'],
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    # 使用内存缓存作为fallback
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'test-cache',
        }
    }

# 日志配置 - CI环境使用简化日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
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
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# 媒体文件配置
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')
MEDIA_URL = '/media/'

# 邮件配置 - 使用内存后端
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 安全设置 - CI环境可以放宽
SECRET_KEY = 'ci-test-secret-key-not-for-production'
ALLOWED_HOSTS = ['*']
DEBUG = False

# 禁用不必要的中间件以提高测试速度
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# 禁用调试工具栏
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

# 密码验证 - 简化以提高测试速度
AUTH_PASSWORD_VALIDATORS = []

# 时区设置
USE_TZ = True
TIME_ZONE = 'UTC'

# 国际化
USE_I18N = False
USE_L10N = False

# 文件上传
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# 会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# 测试运行器配置
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# 并行测试设置
if os.environ.get('PARALLEL_TESTS', 'false').lower() == 'true':
    # 启用并行测试
    TEST_PARALLEL = True
    TEST_PARALLEL_MIGRATE = True

# CI特定设置
if os.environ.get('GITHUB_ACTIONS'):
    # GitHub Actions特定配置
    GITHUB_ACTIONS = True
    
    # 使用更快的密码哈希算法
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]
    
    # 禁用迁移以加速测试
    class DisableMigrations:
        def __contains__(self, item):
            return True
        
        def __getitem__(self, item):
            return None
    
    # 只在特定情况下禁用迁移
    if os.environ.get('DISABLE_MIGRATIONS', 'false').lower() == 'true':
        MIGRATION_MODULES = DisableMigrations()

# 测试覆盖率配置
COVERAGE_REPORT_HTML_OUTPUT_DIR = 'tests/coverage_html'
COVERAGE_REPORT_XML_OUTPUT_FILE = 'tests/coverage.xml'

# 性能测试配置
PERFORMANCE_TEST_ENABLED = os.environ.get('PERFORMANCE_TEST', 'false').lower() == 'true'

# 外部服务Mock配置
MOCK_EXTERNAL_SERVICES = True

# API限流 - 测试环境放宽限制
REST_FRAMEWORK.update({
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/hour',
        'user': '10000/hour',
        'login': '100/hour',
    }
})

# Celery配置 - 使用同步模式
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 测试数据配置
TEST_DATA_DIR = os.path.join(BASE_DIR, 'tests', 'fixtures')
TEST_MEDIA_DIR = os.path.join(BASE_DIR, 'tests', 'temp_media')

# 确保测试目录存在
os.makedirs(TEST_MEDIA_DIR, exist_ok=True)
os.makedirs(COVERAGE_REPORT_HTML_OUTPUT_DIR, exist_ok=True)

print("✅ CI/CD测试配置加载完成")