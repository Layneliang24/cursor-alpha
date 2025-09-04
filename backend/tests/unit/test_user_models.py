# -*- coding: utf-8 -*-
"""
Users应用核心模型单元测试
测试User、UserProfile等核心模型
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class UserModelTest(TestCase):
    """User模型测试"""
    
    def test_create_user(self):
        """测试创建普通用户"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(str(user), 'testuser')
    
    def test_create_superuser(self):
        """测试创建超级用户"""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertEqual(superuser.username, 'admin')
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.check_password('adminpass123'))
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
    
    def test_user_unique_username(self):
        """测试用户名唯一性"""
        User.objects.create_user(
            username='testuser',
            email='test1@example.com',
            password='testpass123'
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='testuser',
                email='test2@example.com',
                password='testpass123'
            )
    
    def test_user_unique_email(self):
        """测试邮箱唯一性"""
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='testpass123'
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='user2',
                email='test@example.com',
                password='testpass123'
            )
    
    def test_user_password_validation(self):
        """测试密码验证"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 测试正确密码
        self.assertTrue(user.check_password('testpass123'))
        
        # 测试错误密码
        self.assertFalse(user.check_password('wrongpass'))
    
    def test_user_date_joined(self):
        """测试用户注册时间"""
        before_creation = timezone.now()
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        after_creation = timezone.now()
        
        self.assertIsNotNone(user.date_joined)
        self.assertTrue(before_creation <= user.date_joined <= after_creation)
    
    def test_user_last_login(self):
        """测试用户最后登录时间"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 新用户最后登录时间应该为None
        self.assertIsNone(user.last_login)
        
        # 模拟登录
        user.last_login = timezone.now()
        user.save()
        
        self.assertIsNotNone(user.last_login)
    
    def test_user_is_active(self):
        """测试用户激活状态"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 默认应该是激活状态
        self.assertTrue(user.is_active)
        
        # 测试停用用户
        user.is_active = False
        user.save()
        
        self.assertFalse(user.is_active)
    
    def test_user_string_representation(self):
        """测试用户字符串表示"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(str(user), 'testuser')
        self.assertEqual(repr(user), '<User: testuser>')


class UserProfileTest(TestCase):
    """用户资料测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """测试用户资料创建"""
        # 检查用户资料是否自动创建
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsNotNone(self.user.profile)
    
    def test_user_profile_fields(self):
        """测试用户资料字段"""
        profile = self.user.profile
        
        # 测试默认值
        self.assertEqual(self.user.bio, '')
        self.assertEqual(profile.avatar_url, '')
        self.assertEqual(profile.skills, '')
        self.assertEqual(profile.location, '')
        self.assertEqual(self.user.website, '')
        self.assertEqual(profile.company, '')
        self.assertEqual(profile.position, '')
        self.assertEqual(profile.phone, '')
        self.assertEqual(profile.github, '')
    
    def test_user_profile_update(self):
        """测试用户资料更新"""
        profile = self.user.profile
        
        # 更新资料
        profile.skills = 'Test Skills'
        profile.location = 'Beijing, China'
        profile.company = 'Test Company'
        profile.save()
        
        # 刷新数据
        profile.refresh_from_db()
        
        self.assertEqual(profile.skills, 'Test Skills')
        self.assertEqual(profile.location, 'Beijing, China')
        self.assertEqual(profile.company, 'Test Company')
    
    def test_user_profile_avatar(self):
        """测试用户头像"""
        profile = self.user.profile
        
        # 设置头像URL
        profile.avatar_url = 'https://example.com/avatar.jpg'
        profile.save()
        
        profile.refresh_from_db()
        self.assertEqual(profile.avatar_url, 'https://example.com/avatar.jpg')
    
    def test_user_profile_phone(self):
        """测试用户手机号"""
        profile = self.user.profile
        
        # 设置手机号
        profile.phone = '13800138000'
        profile.save()
        
        profile.refresh_from_db()
        self.assertEqual(profile.phone, '13800138000')
    
    def test_user_profile_company(self):
        """测试用户公司"""
        profile = self.user.profile
        
        # 测试有效公司值
        valid_companies = ['', 'Test Company', 'Another Company']
        
        for company in valid_companies:
            profile.company = company
            profile.save()
            
            profile.refresh_from_db()
            self.assertEqual(profile.company, company)
    
    def test_user_profile_linkedin(self):
        """测试用户LinkedIn"""
        profile = self.user.profile
        
        # 测试有效LinkedIn值
        valid_linkedins = ['', 'https://linkedin.com/in/test', 'https://linkedin.com/in/another']
        
        for linkedin in valid_linkedins:
            profile.linkedin = linkedin
            profile.save()
            
            profile.refresh_from_db()
            self.assertEqual(profile.linkedin, linkedin)
    
    def test_user_profile_twitter(self):
        """测试用户Twitter"""
        profile = self.user.profile
        
        # 测试有效Twitter值
        valid_twitters = ['', 'https://twitter.com/test', 'https://twitter.com/another']
        
        for twitter in valid_twitters:
            profile.twitter = twitter
            profile.save()
            
            profile.refresh_from_db()
            self.assertEqual(profile.twitter, twitter)


class UserAuthenticationTest(TestCase):
    """用户认证测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_login(self):
        """测试用户登录"""
        from django.contrib.auth import authenticate
        
        # 测试正确凭据
        authenticated_user = authenticate(
            username='testuser',
            password='testpass123'
        )
        
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user, self.user)
        
        # 测试错误密码
        wrong_user = authenticate(
            username='testuser',
            password='wrongpass'
        )
        
        self.assertIsNone(wrong_user)
        
        # 测试错误用户名
        wrong_user = authenticate(
            username='wronguser',
            password='testpass123'
        )
        
        self.assertIsNone(wrong_user)
    
    def test_user_password_change(self):
        """测试用户密码修改"""
        # 修改密码
        self.user.set_password('newpass123')
        self.user.save()
        
        # 验证新密码
        self.assertTrue(self.user.check_password('newpass123'))
        
        # 验证旧密码失效
        self.assertFalse(self.user.check_password('testpass123'))
    
    def test_user_password_reset(self):
        """测试用户密码重置"""
        # 生成密码重置令牌
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        # 验证令牌
        self.assertTrue(default_token_generator.check_token(self.user, token))
        
        # 验证无效令牌
        self.assertFalse(default_token_generator.check_token(self.user, 'invalid_token'))


class UserPermissionsTest(TestCase):
    """用户权限测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
    
    def test_user_permissions(self):
        """测试用户权限"""
        # 普通用户权限
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        
        # 超级用户权限
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_superuser)
    
    def test_user_staff_status(self):
        """测试用户员工状态"""
        # 设置为员工
        self.user.is_staff = True
        self.user.save()
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)
        
        # 取消员工状态
        self.user.is_staff = False
        self.user.save()
        
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)


@pytest.mark.django_db
class TestUserIntegration(TestCase):
    """用户模型集成测试"""
    
    def test_user_profile_relationship(self):
        """测试用户与资料的关系"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 验证用户资料自动创建
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsNotNone(user.profile)
        
        # 验证用户资料字段
        profile = user.profile
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.skills, '')
    
    def test_user_deletion_cascade(self):
        """测试用户删除级联"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        user_id = user.id
        profile_id = user.profile.id
        
        # 删除用户
        user.delete()
        
        # 验证用户资料也被删除
        from apps.users.models import UserProfile
        self.assertFalse(UserProfile.objects.filter(id=profile_id).exists())
    
    def test_user_creation_workflow(self):
        """测试用户创建工作流"""
        # 创建用户
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 验证用户状态
        self.assertTrue(user.is_active)
        self.assertIsNotNone(user.date_joined)
        self.assertIsNone(user.last_login)
        
        # 验证用户资料
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.user, user)
    
    def test_user_update_workflow(self):
        """测试用户更新工作流"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 更新用户信息
        user.first_name = 'Test'
        user.last_name = 'User'
        user.save()
        
        # 更新用户资料
        profile = user.profile
        user.bio = 'Test bio'
        user.save()  # 保存用户更改
        profile.skills = 'Test skills'
        profile.save()
        
        # 验证更新
        user.refresh_from_db()
        profile.refresh_from_db()
        
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(profile.skills, 'Test skills')
        self.assertEqual(user.bio, 'Test bio')
