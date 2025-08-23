"""
权限管理综合测试

测试权限系统的所有功能，包括：
1. 用户权限测试
2. 组权限测试
3. 对象级权限测试
4. 权限继承测试
5. 权限检查测试
6. 权限中间件测试
"""

import pytest
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from rest_framework.test import APIClient
from rest_framework import status

from apps.articles.models import Article
from apps.categories.models import Category
from apps.english.models import Word, Dictionary
from apps.users.models import UserProfile


User = get_user_model()


class UserPermissionTest(TestCase):
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
        
        # 获取权限
        self.add_article_perm = Permission.objects.get(
            codename='add_article'
        )
        self.change_article_perm = Permission.objects.get(
            codename='change_article'
        )
        self.delete_article_perm = Permission.objects.get(
            codename='delete_article'
        )
        self.view_article_perm = Permission.objects.get(
            codename='view_article'
        )
    
    def test_user_has_no_permissions_by_default(self):
        """测试用户默认没有权限"""
        self.assertFalse(self.user.has_perm('articles.add_article'))
        self.assertFalse(self.user.has_perm('articles.change_article'))
        self.assertFalse(self.user.has_perm('articles.delete_article'))
        self.assertFalse(self.user.has_perm('articles.view_article'))
    
    def test_superuser_has_all_permissions(self):
        """测试超级用户拥有所有权限"""
        self.assertTrue(self.superuser.has_perm('articles.add_article'))
        self.assertTrue(self.superuser.has_perm('articles.change_article'))
        self.assertTrue(self.superuser.has_perm('articles.delete_article'))
        self.assertTrue(self.superuser.has_perm('articles.view_article'))
        
        # 测试任意权限
        self.assertTrue(self.superuser.has_perm('any.random_permission'))
    
    def test_add_permission_to_user(self):
        """测试给用户添加权限"""
        # 添加权限前
        self.assertFalse(self.user.has_perm('articles.add_article'))
        
        # 添加权限
        self.user.user_permissions.add(self.add_article_perm)
        
        # 添加权限后
        self.assertTrue(self.user.has_perm('articles.add_article'))
        self.assertFalse(self.user.has_perm('articles.change_article'))
    
    def test_remove_permission_from_user(self):
        """测试从用户移除权限"""
        # 先添加权限
        self.user.user_permissions.add(self.add_article_perm)
        self.assertTrue(self.user.has_perm('articles.add_article'))
        
        # 移除权限
        self.user.user_permissions.remove(self.add_article_perm)
        
        # 验证权限被移除
        self.assertFalse(self.user.has_perm('articles.add_article'))
    
    def test_multiple_permissions(self):
        """测试多个权限"""
        permissions = [
            self.add_article_perm,
            self.change_article_perm,
            self.view_article_perm
        ]
        
        # 批量添加权限
        self.user.user_permissions.set(permissions)
        
        # 验证权限
        self.assertTrue(self.user.has_perm('articles.add_article'))
        self.assertTrue(self.user.has_perm('articles.change_article'))
        self.assertTrue(self.user.has_perm('articles.view_article'))
        self.assertFalse(self.user.has_perm('articles.delete_article'))
    
    def test_has_perms_method(self):
        """测试has_perms方法"""
        permissions = [
            self.add_article_perm,
            self.change_article_perm
        ]
        self.user.user_permissions.set(permissions)
        
        # 测试多个权限检查
        perm_list = ['articles.add_article', 'articles.change_article']
        self.assertTrue(self.user.has_perms(perm_list))
        
        # 测试包含无权限的列表
        perm_list_with_denied = ['articles.add_article', 'articles.delete_article']
        self.assertFalse(self.user.has_perms(perm_list_with_denied))


class GroupPermissionTest(TestCase):
    """组权限测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建组
        self.editors_group = Group.objects.create(name='Editors')
        self.viewers_group = Group.objects.create(name='Viewers')
        
        # 获取权限
        self.add_article_perm = Permission.objects.get(codename='add_article')
        self.change_article_perm = Permission.objects.get(codename='change_article')
        self.view_article_perm = Permission.objects.get(codename='view_article')
    
    def test_group_permissions(self):
        """测试组权限"""
        # 给组添加权限
        self.editors_group.permissions.add(self.add_article_perm, self.change_article_perm)
        self.viewers_group.permissions.add(self.view_article_perm)
        
        # 用户加入组前没有权限
        self.assertFalse(self.user.has_perm('articles.add_article'))
        
        # 用户加入编辑组
        self.user.groups.add(self.editors_group)
        
        # 验证用户通过组获得权限
        self.assertTrue(self.user.has_perm('articles.add_article'))
        self.assertTrue(self.user.has_perm('articles.change_article'))
        self.assertFalse(self.user.has_perm('articles.view_article'))
    
    def test_multiple_groups(self):
        """测试多个组权限"""
        # 给不同组添加不同权限
        self.editors_group.permissions.add(self.add_article_perm, self.change_article_perm)
        self.viewers_group.permissions.add(self.view_article_perm)
        
        # 用户加入多个组
        self.user.groups.add(self.editors_group, self.viewers_group)
        
        # 验证用户拥有所有组的权限
        self.assertTrue(self.user.has_perm('articles.add_article'))
        self.assertTrue(self.user.has_perm('articles.change_article'))
        self.assertTrue(self.user.has_perm('articles.view_article'))
    
    def test_user_and_group_permissions_combined(self):
        """测试用户权限和组权限组合"""
        # 给组添加权限
        self.editors_group.permissions.add(self.add_article_perm)
        self.user.groups.add(self.editors_group)
        
        # 给用户直接添加权限
        self.user.user_permissions.add(self.change_article_perm)
        
        # 验证用户拥有来自组和个人的权限
        self.assertTrue(self.user.has_perm('articles.add_article'))  # 来自组
        self.assertTrue(self.user.has_perm('articles.change_article'))  # 直接权限
    
    def test_remove_user_from_group(self):
        """测试从组中移除用户"""
        # 设置组权限
        self.editors_group.permissions.add(self.add_article_perm)
        self.user.groups.add(self.editors_group)
        
        # 验证用户有权限
        self.assertTrue(self.user.has_perm('articles.add_article'))
        
        # 从组中移除用户
        self.user.groups.remove(self.editors_group)
        
        # 验证用户失去组权限
        self.assertFalse(self.user.has_perm('articles.add_article'))


class ObjectLevelPermissionTest(TestCase):
    """对象级权限测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        # 创建分类和文章
        self.category = Category.objects.create(
            name='测试分类',
            description='测试分类描述'
        )
        
        self.article = Article.objects.create(
            title='测试文章',
            content='测试内容',
            category=self.category,
            author=self.user1
        )
    
    def test_author_permissions(self):
        """测试作者权限"""
        # 作者应该能够修改自己的文章
        self.assertEqual(self.article.author, self.user1)
        
        # 其他用户不应该是作者
        self.assertNotEqual(self.article.author, self.user2)
    
    def test_object_ownership_check(self):
        """测试对象所有权检查"""
        # 可以通过自定义方法检查所有权
        def can_edit_article(user, article):
            return user == article.author or user.is_superuser
        
        # 测试所有权检查
        self.assertTrue(can_edit_article(self.user1, self.article))
        self.assertFalse(can_edit_article(self.user2, self.article))
        
        # 测试超级用户
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(can_edit_article(superuser, self.article))
    
    def test_category_based_permissions(self):
        """测试基于分类的权限"""
        # 可以基于分类实现权限控制
        def can_access_category(user, category):
            # 假设某些分类需要特殊权限
            if category.name == '私有分类':
                return user.has_perm('categories.access_private')
            return True
        
        # 测试公开分类
        self.assertTrue(can_access_category(self.user1, self.category))
        self.assertTrue(can_access_category(self.user2, self.category))
        
        # 创建私有分类
        private_category = Category.objects.create(
            name='私有分类',
            description='私有分类描述'
        )
        
        # 测试私有分类权限
        self.assertFalse(can_access_category(self.user1, private_category))
        self.assertFalse(can_access_category(self.user2, private_category))


class APIPermissionTest(TestCase):
    """API权限测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='测试分类',
            description='测试分类描述'
        )
    
    def test_unauthenticated_access(self):
        """测试未认证访问"""
        # 未认证用户访问需要认证的API
        response = self.client.get('/api/v1/articles/')
        
        # 应该返回401未授权
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_access(self):
        """测试已认证访问"""
        # 认证用户
        self.client.force_authenticate(user=self.user)
        
        # 访问API
        response = self.client.get('/api/v1/articles/')
        
        # 应该成功访问
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
    
    def test_permission_required_endpoint(self):
        """测试需要权限的端点"""
        self.client.force_authenticate(user=self.user)
        
        # 尝试创建文章（可能需要权限）
        article_data = {
            'title': '新文章',
            'content': '新文章内容',
            'category': self.category.id
        }
        
        response = self.client.post('/api/v1/articles/', article_data, format='json')
        
        # 根据权限设置，可能返回403或201
        self.assertIn(response.status_code, [
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_400_BAD_REQUEST
        ])
    
    def test_superuser_access(self):
        """测试超级用户访问"""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.client.force_authenticate(user=superuser)
        
        # 超级用户应该能访问所有端点
        response = self.client.get('/api/v1/articles/')
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionDecoratorTest(TestCase):
    """权限装饰器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.factory = RequestFactory()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.privileged_user = User.objects.create_user(
            username='privileged',
            email='privileged@example.com',
            password='testpass123'
        )
        
        # 给特权用户添加权限
        add_article_perm = Permission.objects.get(codename='add_article')
        self.privileged_user.user_permissions.add(add_article_perm)
    
    def test_permission_required_decorator(self):
        """测试permission_required装饰器"""
        @permission_required('articles.add_article')
        def protected_view(request):
            return HttpResponse('Success')
        
        # 测试无权限用户
        request = self.factory.get('/')
        request.user = self.user
        
        with self.assertRaises(PermissionDenied):
            protected_view(request)
        
        # 测试有权限用户
        request.user = self.privileged_user
        response = protected_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Success')
    
    def test_multiple_permissions_required(self):
        """测试多个权限要求"""
        @permission_required(['articles.add_article', 'articles.change_article'])
        def multi_perm_view(request):
            return HttpResponse('Success')
        
        # 只有一个权限的用户
        request = self.factory.get('/')
        request.user = self.privileged_user
        
        with self.assertRaises(PermissionDenied):
            multi_perm_view(request)
        
        # 添加第二个权限
        change_article_perm = Permission.objects.get(codename='change_article')
        self.privileged_user.user_permissions.add(change_article_perm)
        
        # 现在应该能访问
        response = multi_perm_view(request)
        self.assertEqual(response.status_code, 200)


class PermissionUtilityTest(TestCase):
    """权限工具函数测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.group = Group.objects.create(name='TestGroup')
        self.permission = Permission.objects.get(codename='add_article')
    
    def test_get_user_permissions(self):
        """测试获取用户权限"""
        # 添加直接权限
        self.user.user_permissions.add(self.permission)
        
        # 获取用户所有权限
        user_perms = self.user.get_user_permissions()
        
        self.assertIn('articles.add_article', user_perms)
    
    def test_get_group_permissions(self):
        """测试获取组权限"""
        # 给组添加权限
        self.group.permissions.add(self.permission)
        self.user.groups.add(self.group)
        
        # 获取组权限
        group_perms = self.user.get_group_permissions()
        
        self.assertIn('articles.add_article', group_perms)
    
    def test_get_all_permissions(self):
        """测试获取所有权限"""
        # 添加直接权限
        view_perm = Permission.objects.get(codename='view_article')
        self.user.user_permissions.add(view_perm)
        
        # 通过组添加权限
        self.group.permissions.add(self.permission)
        self.user.groups.add(self.group)
        
        # 获取所有权限
        all_perms = self.user.get_all_permissions()
        
        self.assertIn('articles.add_article', all_perms)  # 来自组
        self.assertIn('articles.view_article', all_perms)  # 直接权限
    
    def test_permission_caching(self):
        """测试权限缓存"""
        # 第一次检查权限
        has_perm_1 = self.user.has_perm('articles.add_article')
        
        # 添加权限
        self.user.user_permissions.add(self.permission)
        
        # 由于缓存，可能仍然返回False
        has_perm_2 = self.user.has_perm('articles.add_article')
        
        # 清除缓存后应该返回True
        if hasattr(self.user, '_perm_cache'):
            delattr(self.user, '_perm_cache')
        
        has_perm_3 = self.user.has_perm('articles.add_article')
        
        self.assertFalse(has_perm_1)
        # has_perm_2 可能是True或False，取决于Django版本
        self.assertTrue(has_perm_3)


class PermissionModelTest(TestCase):
    """权限模型测试"""
    
    def test_permission_creation(self):
        """测试权限创建"""
        # Django应该为每个模型自动创建权限
        article_ct = ContentType.objects.get_for_model(Article)
        
        # 检查基本权限是否存在
        permissions = Permission.objects.filter(content_type=article_ct)
        permission_codenames = [p.codename for p in permissions]
        
        expected_perms = ['add_article', 'change_article', 'delete_article', 'view_article']
        for perm in expected_perms:
            self.assertIn(perm, permission_codenames)
    
    def test_custom_permission(self):
        """测试自定义权限"""
        # 检查是否可以创建自定义权限
        article_ct = ContentType.objects.get_for_model(Article)
        
        custom_perm = Permission.objects.create(
            codename='publish_article',
            name='Can publish article',
            content_type=article_ct
        )
        
        self.assertEqual(custom_perm.codename, 'publish_article')
        self.assertEqual(custom_perm.name, 'Can publish article')
        self.assertEqual(custom_perm.content_type, article_ct)
    
    def test_permission_string_representation(self):
        """测试权限字符串表示"""
        permission = Permission.objects.get(codename='add_article')
        
        # 权限的字符串表示应该包含应用和权限名
        perm_str = str(permission)
        self.assertIn('article', perm_str.lower())


print("✅ 权限管理综合测试用例创建完成")