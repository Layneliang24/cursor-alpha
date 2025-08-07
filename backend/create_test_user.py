#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.users.models import User

def create_test_user():
    # 创建测试用户
    username = 'testuser'
    email = 'test@example.com'
    password = '123456'
    
    # 检查用户是否已存在
    if User.objects.filter(username=username).exists():
        print(f"用户 {username} 已存在")
        return
    
    # 创建用户
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name='测试',
        last_name='用户'
    )
    
    print(f"创建测试用户成功:")
    print(f"用户名: {username}")
    print(f"密码: {password}")
    print(f"邮箱: {email}")

if __name__ == '__main__':
    create_test_user()