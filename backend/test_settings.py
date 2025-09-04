# -*- coding: utf-8 -*-
"""
优化的测试设置文件
用于快速、可靠的测试执行
"""

import os
import sys
from pathlib import Path

# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
os.environ.setdefault('TESTING', 'true')
os.environ.setdefault('DJANGO_TEST_RUNNER', 'django.test.runner.DiscoverRunner')

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# 导入Django设置
from django.conf import settings

# 基本测试配置
DEBUG = False
TESTING = True

# 使用内存数据库进行快速测试
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# 禁用缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# 使用内存邮件后端
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 设置测试媒体目录
MEDIA_ROOT = 'tests/temp_media/'
STATIC_ROOT = 'tests/temp_static/'

# 禁用日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# 禁用迁移
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# 设置时区
USE_TZ = False
TIME_ZONE = 'UTC'

# 禁用密码哈希（加速测试）
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# 禁用CSRF保护（测试环境）
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 禁用静态文件收集
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# 设置测试密钥
SECRET_KEY = 'test-secret-key-for-testing-only'

# 设置自定义用户模型
AUTH_USER_MODEL = 'users.User'

# 设置测试应用 - 添加项目中的应用
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'django_cryptography',
    # 项目应用
    'apps.common',
    'apps.users',
    'apps.ai',
    'apps.english',
    'apps.api',
    'apps.rbac',
    'feature_flags',
    'apps.links',
    'apps.search',
    'apps.todos',
    'apps.jobs',
    'apps.categories',
    'apps.articles',
    'apps.idiomatic_expressions_requirement',
]

# 禁用调试工具栏
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
}

# REST Framework测试配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# 禁用Celery（测试环境）
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# 禁用Redis（测试环境）
REDIS_URL = None

# 设置测试超时
TEST_TIMEOUT = 30

# 禁用外部API调用
MOCK_EXTERNAL_APIS = True

# 设置测试数据目录
TEST_DATA_DIR = 'tests/data/'

# 配置测试报告目录
TEST_REPORTS_DIR = 'tests/reports/'

# 设置测试覆盖率配置
COVERAGE_CONFIG = {
    'source': '.',
    'omit': [
        '*/tests/*',
        '*/migrations/*',
        '*/venv/*',
        '*/env/*',
        '*/__pycache__/*',
        '*/settings/*',
        'manage.py',
        'wsgi.py',
        'asgi.py'
    ]
}

# 添加必要的设置
ROOT_URLCONF = 'alpha.urls'
WSGI_APPLICATION = 'alpha.wsgi.application'

# 设置语言和本地化
LANGUAGE_CODE = 'en-us'
USE_I18N = False
USE_L10N = False

# 设置会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# 设置消息框架
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

# 设置安全设置
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = 'DENY'
