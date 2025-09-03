#!/usr/bin/env python3
import pytest
import django
from django.test import TestCase

class TestBasicEnvironment(TestCase):
    def test_django_import(self):
        """测试Django是否可以正常导入"""
        assert django.VERSION >= (4, 0)
    
    def test_test_settings(self):
        """测试测试设置是否正确"""
        from django.conf import settings
        assert settings.TESTING == True
        assert settings.DEBUG == False
    
    def test_database_config(self):
        """测试数据库配置"""
        from django.conf import settings
        assert 'default' in settings.DATABASES
        assert 'ENGINE' in settings.DATABASES['default']
