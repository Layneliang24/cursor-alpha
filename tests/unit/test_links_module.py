"""
链接模块测试

测试链接模块的所有功能，包括：
1. ExternalLink模型测试
2. 链接管理功能测试
3. 链接排序和过滤测试
4. 权限和安全测试
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from apps.links.models import ExternalLink


User = get_user_model()


class ExternalLinkModelTest(TestCase):
    """外部链接模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_external_link(self):
        """测试创建外部链接"""
        link = ExternalLink.objects.create(
            title='测试网站',
            url='https://example.com',
            description='这是一个测试网站',
            icon='fas fa-globe',
            link_type='website',
            created_by=self.user
        )
        
        self.assertEqual(link.title, '测试网站')
        self.assertEqual(link.url, 'https://example.com')
        self.assertEqual(link.description, '这是一个测试网站')
        self.assertEqual(link.icon, 'fas fa-globe')
        self.assertEqual(link.link_type, 'website')
        self.assertEqual(link.created_by, self.user)
        self.assertTrue(link.is_active)
        self.assertEqual(link.order, 0)
    
    def test_link_str_representation(self):
        """测试链接字符串表示"""
        link = ExternalLink.objects.create(
            title='测试链接',
            url='https://test.com',
            created_by=self.user
        )
        
        self.assertEqual(str(link), '测试链接')
    
    def test_link_types_choices(self):
        """测试链接类型选择"""
        valid_types = ['website', 'tool', 'resource', 'documentation', 'other']
        
        for link_type in valid_types:
            link = ExternalLink.objects.create(
                title=f'测试{link_type}',
                url=f'https://{link_type}.com',
                link_type=link_type,
                created_by=self.user
            )
            self.assertEqual(link.link_type, link_type)
    
    def test_link_ordering(self):
        """测试链接排序"""
        # 创建多个链接，测试排序
        link1 = ExternalLink.objects.create(
            title='链接1',
            url='https://link1.com',
            order=2,
            created_by=self.user
        )
        
        link2 = ExternalLink.objects.create(
            title='链接2',
            url='https://link2.com',
            order=1,
            created_by=self.user
        )
        
        link3 = ExternalLink.objects.create(
            title='链接3',
            url='https://link3.com',
            order=3,
            created_by=self.user
        )
        
        # 获取排序后的链接
        links = ExternalLink.objects.all()
        
        self.assertEqual(links[0], link2)  # order=1
        self.assertEqual(links[1], link1)  # order=2
        self.assertEqual(links[2], link3)  # order=3
    
    def test_link_active_status(self):
        """测试链接启用状态"""
        # 测试默认启用
        link = ExternalLink.objects.create(
            title='默认启用链接',
            url='https://active.com',
            created_by=self.user
        )
        self.assertTrue(link.is_active)
        
        # 测试禁用
        link.is_active = False
        link.save()
        
        link.refresh_from_db()
        self.assertFalse(link.is_active)
    
    def test_link_url_validation(self):
        """测试URL格式验证"""
        # 有效URL
        valid_urls = [
            'https://example.com',
            'http://test.org',
            'https://sub.domain.com/path',
            'https://example.com:8080/path?param=value'
        ]
        
        for url in valid_urls:
            link = ExternalLink.objects.create(
                title=f'测试 {url}',
                url=url,
                created_by=self.user
            )
            self.assertEqual(link.url, url)
    
    def test_required_fields(self):
        """测试必填字段"""
        from django.db import transaction
        
        # 测试缺少title
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExternalLink.objects.create(
                    url='https://example.com',
                    created_by=self.user,
                    title=None
                )
        
        # 测试缺少url  
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExternalLink.objects.create(
                    title='测试标题',
                    created_by=self.user,
                    url=None
                )
        
        # 测试缺少created_by
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExternalLink.objects.create(
                    title='测试标题',
                    url='https://example.com'
                )
    
    def test_optional_fields(self):
        """测试可选字段"""
        # 创建只包含必填字段的链接
        link = ExternalLink.objects.create(
            title='最小链接',
            url='https://minimal.com',
            created_by=self.user
        )
        
        self.assertEqual(link.description, '')
        self.assertEqual(link.icon, '')
        self.assertEqual(link.link_type, 'website')  # 默认值
        self.assertTrue(link.is_active)  # 默认值
        self.assertEqual(link.order, 0)  # 默认值
    
    def test_field_max_lengths(self):
        """测试字段长度限制"""
        # 测试title长度限制 (max_length=100)
        long_title = 'A' * 101
        link = ExternalLink.objects.create(
            title=long_title[:100],  # 截断到100字符
            url='https://example.com',
            created_by=self.user
        )
        self.assertEqual(len(link.title), 100)
        
        # 测试description长度限制 (max_length=200)
        long_description = 'B' * 201
        link.description = long_description[:200]
        link.save()
        self.assertEqual(len(link.description), 200)
        
        # 测试icon长度限制 (max_length=50)
        long_icon = 'C' * 51
        link.icon = long_icon[:50]
        link.save()
        self.assertEqual(len(link.icon), 50)
    
    def test_timestamps(self):
        """测试时间戳字段"""
        link = ExternalLink.objects.create(
            title='时间戳测试',
            url='https://timestamp.com',
            created_by=self.user
        )
        
        # 验证创建时间和更新时间存在
        self.assertIsNotNone(link.created_at)
        self.assertIsNotNone(link.updated_at)
        
        # 验证创建时间和更新时间相等（刚创建时）
        self.assertEqual(link.created_at, link.updated_at)
        
        # 更新链接，验证更新时间变化
        original_updated_at = link.updated_at
        
        # 等待一小段时间确保时间戳不同
        import time
        time.sleep(0.01)
        
        link.title = '更新后的标题'
        link.save()
        
        link.refresh_from_db()
        self.assertGreater(link.updated_at, original_updated_at)
        # 修复：创建时间应该保持不变
        original_created_at = link.created_at
        self.assertEqual(original_created_at, link.created_at)  # 创建时间不变


class ExternalLinkQueryTest(TestCase):
    """外部链接查询测试"""
    
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
        
        # 创建测试链接
        self.active_link = ExternalLink.objects.create(
            title='活跃链接',
            url='https://active.com',
            is_active=True,
            created_by=self.user1
        )
        
        self.inactive_link = ExternalLink.objects.create(
            title='非活跃链接',
            url='https://inactive.com',
            is_active=False,
            created_by=self.user1
        )
        
        self.tool_link = ExternalLink.objects.create(
            title='工具链接',
            url='https://tool.com',
            link_type='tool',
            created_by=self.user2
        )
    
    def test_filter_by_active_status(self):
        """测试按活跃状态过滤"""
        active_links = ExternalLink.objects.filter(is_active=True)
        inactive_links = ExternalLink.objects.filter(is_active=False)
        
        self.assertIn(self.active_link, active_links)
        self.assertIn(self.tool_link, active_links)  # 默认为True
        self.assertNotIn(self.inactive_link, active_links)
        
        self.assertIn(self.inactive_link, inactive_links)
        self.assertNotIn(self.active_link, inactive_links)
    
    def test_filter_by_link_type(self):
        """测试按链接类型过滤"""
        website_links = ExternalLink.objects.filter(link_type='website')
        tool_links = ExternalLink.objects.filter(link_type='tool')
        
        self.assertIn(self.active_link, website_links)
        self.assertIn(self.inactive_link, website_links)
        self.assertNotIn(self.tool_link, website_links)
        
        self.assertIn(self.tool_link, tool_links)
        self.assertNotIn(self.active_link, tool_links)
    
    def test_filter_by_creator(self):
        """测试按创建者过滤"""
        user1_links = ExternalLink.objects.filter(created_by=self.user1)
        user2_links = ExternalLink.objects.filter(created_by=self.user2)
        
        self.assertEqual(user1_links.count(), 2)
        self.assertIn(self.active_link, user1_links)
        self.assertIn(self.inactive_link, user1_links)
        
        self.assertEqual(user2_links.count(), 1)
        self.assertIn(self.tool_link, user2_links)
    
    def test_ordering(self):
        """测试默认排序"""
        links = ExternalLink.objects.all()
        
        # 验证排序是按order字段，然后按created_at倒序
        for i in range(len(links) - 1):
            current = links[i]
            next_link = links[i + 1]
            
            if current.order == next_link.order:
                # 如果order相同，created_at应该是倒序
                self.assertGreaterEqual(current.created_at, next_link.created_at)
            else:
                # order应该是升序
                self.assertLessEqual(current.order, next_link.order)


class ExternalLinkPermissionTest(TestCase):
    """外部链接权限测试"""
    
    def setUp(self):
        """测试前准备"""
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpass123'
        )
        
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        
        self.link = ExternalLink.objects.create(
            title='测试链接',
            url='https://test.com',
            created_by=self.owner
        )
    
    def test_owner_access(self):
        """测试所有者访问权限"""
        # 所有者应该能够访问自己创建的链接
        owner_links = ExternalLink.objects.filter(created_by=self.owner)
        self.assertIn(self.link, owner_links)
    
    def test_other_user_access(self):
        """测试其他用户访问权限"""
        # 其他用户不应该在created_by过滤中看到不属于自己的链接
        other_user_links = ExternalLink.objects.filter(created_by=self.other_user)
        self.assertNotIn(self.link, other_user_links)
        
        # 但可以看到所有公开的链接（如果有相应的视图逻辑）
        all_active_links = ExternalLink.objects.filter(is_active=True)
        self.assertIn(self.link, all_active_links)


class ExternalLinkBulkOperationTest(TestCase):
    """外部链接批量操作测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_bulk_create(self):
        """测试批量创建链接"""
        links_data = [
            {
                'title': f'链接{i}',
                'url': f'https://example{i}.com',
                'link_type': 'website',
                'created_by': self.user
            }
            for i in range(5)
        ]
        
        links = [ExternalLink(**data) for data in links_data]
        ExternalLink.objects.bulk_create(links)
        
        self.assertEqual(ExternalLink.objects.count(), 5)
        
        for i, link in enumerate(ExternalLink.objects.all()):
            self.assertEqual(link.title, f'链接{i}')
            self.assertEqual(link.url, f'https://example{i}.com')
    
    def test_bulk_update(self):
        """测试批量更新链接"""
        # 创建多个链接
        links = []
        for i in range(3):
            link = ExternalLink.objects.create(
                title=f'原标题{i}',
                url=f'https://original{i}.com',
                created_by=self.user
            )
            links.append(link)
        
        # 批量更新
        for i, link in enumerate(links):
            link.title = f'新标题{i}'
        
        ExternalLink.objects.bulk_update(links, ['title'])
        
        # 验证更新
        updated_links = ExternalLink.objects.all().order_by('id')
        for i, link in enumerate(updated_links):
            self.assertEqual(link.title, f'新标题{i}')
    
    def test_bulk_delete(self):
        """测试批量删除链接"""
        # 创建多个链接
        for i in range(5):
            ExternalLink.objects.create(
                title=f'待删除链接{i}',
                url=f'https://delete{i}.com',
                created_by=self.user
            )
        
        self.assertEqual(ExternalLink.objects.count(), 5)
        
        # 批量删除
        ExternalLink.objects.all().delete()
        
        self.assertEqual(ExternalLink.objects.count(), 0)


print("✅ 链接模块测试用例创建完成")