#!/usr/bin/env python3
"""认证辅助模块 - 提供自动登录和token管理功能"""

import os
import sys
import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.alpha.settings')

try:
    import django
    django.setup()
    
    from django.contrib.auth import get_user_model
    from django.test import Client
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken
    
    User = get_user_model()
    
except ImportError as e:
    print(f"⚠️  Django导入失败: {e}")
    User = None

class AuthHelper:
    """认证辅助类"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.user = None
        self.client = APIClient() if 'APIClient' in globals() else None
        
    def create_test_user(self, username: str = "testuser", email: str = "test@example.com", password: str = "testpass123"):
        """创建测试用户"""
        if not User:
            print("❌ Django未正确初始化，无法创建用户")
            return None
            
        try:
            user = User.objects.get(username=username)
            print(f"✅ 使用现有用户: {username}")
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=True
            )
            print(f"✅ 创建新用户: {username}")
        
        self.user = user
        return user
    
    def login_and_get_token(self, username: str = "testuser", password: str = "testpass123") -> Optional[str]:
        """登录并获取token"""
        if not User:
            print("❌ Django未正确初始化，无法登录")
            return None
            
        try:
            # 确保用户存在
            self.create_test_user(username, f"{username}@example.com", password)
            
            # 使用Django REST framework的token认证
            refresh = RefreshToken.for_user(self.user)
            self.token = str(refresh.access_token)
            
            # 设置client的认证头
            if self.client:
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
            
            print(f"✅ 成功获取token: {self.token[:20]}...")
            return self.token
            
        except Exception as e:
            print(f"❌ 登录失败: {e}")
            return None
    
    def get_authenticated_client(self):
        """获取已认证的API客户端"""
        if not self.token:
            self.login_and_get_token()
        return self.client
    
    def make_authenticated_request(self, method: str, url: str, data: Dict[str, Any] = None, **kwargs) -> requests.Response:
        """发送已认证的请求"""
        if not self.token:
            self.login_and_get_token()
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        if data:
            kwargs['json'] = data
        
        response = requests.request(method, f"{self.base_url}{url}", headers=headers, **kwargs)
        return response
    
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return self.token is not None

# 全局认证助手实例
auth_helper = AuthHelper()

def get_auth_helper() -> AuthHelper:
    """获取全局认证助手实例"""
    return auth_helper

def setup_authentication(username: str = "testuser", password: str = "testpass123") -> Optional[str]:
    """设置认证（便捷函数）"""
    return auth_helper.login_and_get_token(username, password)

def get_authenticated_client():
    """获取已认证的客户端（便捷函数）"""
    return auth_helper.get_authenticated_client()
