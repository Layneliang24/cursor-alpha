#!/usr/bin/env python
import os
import sys
import django
import requests
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.english.views import TypingPracticeViewSet

def test_api_directly():
    """直接测试API"""
    print("=== 直接测试API ===")
    
    # 创建测试用户
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='test_api_user',
        defaults={
            'email': 'test_api_new@example.com',
            'is_active': True
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"创建测试用户: {user.username}")
    else:
        print(f"使用现有用户: {user.username}")
    
    # 创建请求
    factory = RequestFactory()
    request = factory.get('/api/v1/english/typing-practice/words/?category=TOEFL&chapter=1')
    request.user = user
    
    # 测试ViewSet
    viewset = TypingPracticeViewSet()
    viewset.request = request
    
    try:
        response = viewset.words(request)
        print(f"API响应状态: {response.status_code}")
        print(f"API响应数据长度: {len(response.data) if hasattr(response, 'data') else 'N/A'}")
        
        if hasattr(response, 'data') and response.data:
            print(f"第一个单词: {response.data[0] if response.data else 'None'}")
        
    except Exception as e:
        print(f"API测试出错: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")

if __name__ == "__main__":
    test_api_directly()
