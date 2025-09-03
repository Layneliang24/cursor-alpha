# -*- coding: utf-8 -*-
"""
简化测试设置文件
用于快速验证测试环境配置
"""

import os
import sys
from pathlib import Path

# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
os.environ.setdefault('TESTING', 'true')

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / 'backend'
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

