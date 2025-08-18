# -*- coding: utf-8 -*-
"""
MySQL测试专用Django设置
使用独立的MySQL测试数据库，避免与开发数据库冲突
"""

import os
import sys
from pathlib import Path

# 设置环境变量（必须在导入Django之前）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
os.environ.setdefault('TESTING', 'true')

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

# 导入原始设置
from alpha.settings import *

# 强制覆盖数据库设置，使用MySQL测试数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test_alpha_db',  # 测试数据库名
        'USER': 'root',           # MySQL用户名
        'PASSWORD': 'meimei520',  # MySQL密码
        'HOST': 'localhost',      # MySQL主机
        'PORT': '3306',          # MySQL端口
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'autocommit': True,
        },
        'TEST': {
            'NAME': 'test_alpha_db',  # 测试时使用的数据库名
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
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

# 禁用调试工具栏
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
}

# 设置测试环境
TESTING = True
DEBUG = False

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

# 强制使用测试数据库
USE_TZ = False
TIME_ZONE = 'UTC'

# 禁用迁移（避免表创建冲突）
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()
