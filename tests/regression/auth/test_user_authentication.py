# -*- coding: utf-8 -*-
"""
用户认证模块测试
覆盖登录、注册、登出、密码重置等功能
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from datetime import datetime, timedelta

User = get_user_model()


class TestUserAuthenticationAPI(TestCase):
    """用户认证API测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
    
    def test_user_registration_success(self):
        """测试用户注册成功"""
        response = self.client.post('/api/v1/auth/register/', self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['message'], '注册成功')
        
        # 验证用户数据
        user_data = response.data['user']
        self.assertEqual(user_data['username'], 'testuser')
        self.assertEqual(user_data['email'], 'test@example.com')
        self.assertEqual(user_data['first_name'], 'Test')
        self.assertEqual(user_data['last_name'], 'User')
        
        # 验证token
        tokens = response.data['tokens']
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        
        # 验证用户已创建
        user = User.objects.get(username='testuser')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_registration_password_mismatch(self):
        """测试用户注册密码不匹配"""
        invalid_data = self.user_data.copy()
        invalid_data['password_confirm'] = 'wrongpassword'
        
        response = self.client.post('/api/v1/auth/register/', invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_user_registration_duplicate_username(self):
        """测试用户注册重复用户名"""
        # 先创建一个用户
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='testpass123'
        )
        
        response = self.client.post('/api/v1/auth/register/', self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
    
    def test_user_registration_duplicate_email(self):
        """测试用户注册重复邮箱"""
        # 先创建一个用户
        User.objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='testpass123'
        )
        
        response = self.client.post('/api/v1/auth/register/', self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_user_login_success(self):
        """测试用户登录成功"""
        # 先创建用户
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        response = self.client.post('/api/v1/auth/login/', self.login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['message'], '登录成功')
        
        # 验证用户数据
        user_data = response.data['user']
        self.assertEqual(user_data['username'], 'testuser')
        self.assertEqual(user_data['email'], 'test@example.com')
        
        # 验证token
        tokens = response.data['tokens']
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
    
    def test_user_login_invalid_credentials(self):
        """测试用户登录无效凭据"""
        response = self.client.post('/api/v1/auth/login/', self.login_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], '用户名或密码错误')
    
    def test_user_login_missing_fields(self):
        """测试用户登录缺少字段"""
        incomplete_data = {'username': 'testuser'}
        
        response = self.client.post('/api/v1/auth/login/', incomplete_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
    
    def test_user_logout_success(self):
        """测试用户登出成功"""
        # 先创建用户并登录
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        response = self.client.post('/api/v1/auth/logout/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], '登出成功')
    
    def test_user_logout_unauthorized(self):
        """测试用户登出未授权"""
        response = self.client.post('/api/v1/auth/logout/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPasswordResetAPI(TestCase):
    """密码重置API测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_password_reset_request_success(self):
        """测试密码重置请求成功"""
        response = self.client.post('/api/v1/auth/password-reset/', {
            'email': 'test@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], '密码重置邮件已发送')
        
        # 验证邮件已发送
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], 'test@example.com')
    
    def test_password_reset_request_invalid_email(self):
        """测试密码重置请求无效邮箱"""
        response = self.client.post('/api/v1/auth/password-reset/', {
            'email': 'nonexistent@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
        self.assertIn('email', response.data['errors'])
    
    def test_password_reset_confirm_success(self):
        """测试密码重置确认成功"""
        # 生成重置令牌
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        response = self.client.post('/api/v1/auth/password-reset-confirm/', {
            'uid': uid,
            'token': token,
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证密码已更新
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))
    
    def test_password_reset_confirm_password_mismatch(self):
        """测试密码重置确认密码不匹配"""
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        response = self.client.post('/api/v1/auth/password-reset-confirm/', {
            'uid': uid,
            'token': token,
            'new_password': 'newpass123',
            'confirm_password': 'differentpass'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
        self.assertIn('non_field_errors', response.data['errors'])
    
    def test_password_reset_confirm_invalid_token(self):
        """测试密码重置确认无效令牌"""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        response = self.client.post('/api/v1/auth/password-reset-confirm/', {
            'uid': uid,
            'token': 'invalid_token',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
        self.assertIn('non_field_errors', response.data['errors'])


class TestUserProfileAPI(TestCase):
    """用户资料API测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_user_profile(self):
        """测试获取用户资料"""
        response = self.client.get('/api/v1/profiles/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_update_user_profile(self):
        """测试更新用户资料"""
        update_data = {
            'bio': 'This is my bio',
            'website': 'https://example.com'
        }
        
        response = self.client.patch('/api/v1/profiles/me/', update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 检查响应中是否包含更新的数据
        self.assertIn('user', response.data)
        self.assertIn('bio', response.data['user'])
        self.assertIn('website', response.data['user'])
    
    def test_get_user_profile_unauthorized(self):
        """测试获取用户资料未授权"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/v1/profiles/me/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestTokenAuthentication(TestCase):
    """Token认证测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_token_obtain_pair(self):
        """测试获取Token对"""
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_token_refresh(self):
        """测试刷新Token"""
        # 先获取token
        token_response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        refresh_token = token_response.data['refresh']
        
        # 刷新token
        response = self.client.post('/api/v1/auth/token/refresh/', {
            'refresh': refresh_token
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_protected_endpoint_with_token(self):
        """测试使用Token访问受保护端点"""
        # 获取token
        token_response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        access_token = token_response.data['access']
        
        # 使用token访问受保护端点
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/v1/profiles/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestUserAuthenticationIntegration(TestCase):
    """用户认证集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_full_authentication_workflow(self):
        """测试完整认证工作流"""
        # 1. 用户注册
        register_response = self.client.post('/api/v1/auth/register/', self.user_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        
        # 2. 用户登录
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        # 3. 访问受保护资源
        access_token = login_response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        profile_response = self.client.get('/api/v1/profiles/me/')
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        
        # 4. 用户登出
        logout_response = self.client.post('/api/v1/auth/logout/')
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
    
    def test_multiple_user_authentication(self):
        """测试多用户认证"""
        # 创建多个用户
        users = []
        for i in range(3):
            user_data = {
                'username': f'user{i}',
                'email': f'user{i}@example.com',
                'password': 'testpass123',
                'password_confirm': 'testpass123'
            }
            
            register_response = self.client.post('/api/v1/auth/register/', user_data)
            self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
            
            login_response = self.client.post('/api/v1/auth/login/', {
                'username': f'user{i}',
                'password': 'testpass123'
            })
            self.assertEqual(login_response.status_code, status.HTTP_200_OK)
            
            users.append({
                'user_data': user_data,
                'tokens': login_response.data['tokens']
            })
        
        # 验证每个用户都能独立访问
        for user_info in users:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_info["tokens"]["access"]}')
            profile_response = self.client.get('/api/v1/profiles/me/')
            self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
            self.assertEqual(profile_response.data['user']['username'], user_info['user_data']['username'])


class TestUserAuthenticationFrontend(TestCase):
    """用户认证前端模拟测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_login_form_validation(self):
        """测试登录表单验证"""
        # 模拟前端表单验证
        invalid_data_sets = [
            {'username': '', 'password': 'testpass123'},  # 空用户名
            {'username': 'testuser', 'password': ''},     # 空密码
            {'username': '', 'password': ''},             # 都为空
            {'username': 'a' * 151, 'password': 'testpass123'},  # 用户名过长
        ]
        
        for invalid_data in invalid_data_sets:
            with self.subTest(data=invalid_data):
                response = self.client.post('/api/v1/auth/login/', invalid_data)
                self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])
    
    def test_register_form_validation(self):
        """测试注册表单验证"""
        # 模拟前端表单验证
        invalid_data_sets = [
            {**self.user_data, 'username': ''},  # 空用户名
            {**self.user_data, 'email': 'invalid-email'},  # 无效邮箱
            {**self.user_data, 'password': '123'},  # 密码太短
            {**self.user_data, 'password_confirm': 'different'},  # 密码不匹配
        ]
        
        for invalid_data in invalid_data_sets:
            with self.subTest(data=invalid_data):
                response = self.client.post('/api/v1/auth/register/', invalid_data)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_authentication_state_management(self):
        """测试认证状态管理"""
        # 模拟前端状态管理
        # 1. 初始状态 - 未登录
        self.client.force_authenticate(user=None)
        profile_response = self.client.get('/api/v1/profiles/me/')
        self.assertEqual(profile_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 2. 登录状态
        self.client.force_authenticate(user=self.user)
        profile_response = self.client.get('/api/v1/profiles/me/')
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        
        # 3. 登出状态
        self.client.force_authenticate(user=None)
        profile_response = self.client.get('/api/v1/profiles/me/')
        self.assertEqual(profile_response.status_code, status.HTTP_401_UNAUTHORIZED)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
