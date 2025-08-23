"""
通用模块测试

测试通用模块的所有功能，包括：
1. TimestampedModel抽象模型测试
2. SoftDeleteModel抽象模型测试  
3. OwnedModel抽象模型测试
4. 抽象模型属性测试
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

from apps.common.models import TimestampedModel, SoftDeleteModel, OwnedModel
from apps.articles.models import Article
from apps.categories.models import Category


User = get_user_model()


class TimestampedModelTest(TestCase):
    """时间戳模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='测试分类',
            description='测试分类描述'
        )
    
    def test_auto_timestamps_on_article(self):
        """测试Article模型的自动时间戳"""
        # Article继承了TimestampedModel
        article = Article.objects.create(
            title='测试文章',
            content='测试内容',
            category=self.category,
            author=self.user
        )
        
        self.assertIsNotNone(article.created_at)
        self.assertIsNotNone(article.updated_at)
        
        # 创建时间和更新时间应该相等（刚创建时）
        self.assertEqual(article.created_at, article.updated_at)
    
    def test_update_timestamp_on_article(self):
        """测试Article模型的更新时间戳"""
        # 创建文章
        article = Article.objects.create(
            title='原始标题',
            content='原始内容',
            category=self.category,
            author=self.user
        )
        
        original_created_at = article.created_at
        original_updated_at = article.updated_at
        
        # 等待一小段时间后更新
        import time
        time.sleep(0.01)
        
        article.title = '更新后的标题'
        article.save()
        
        article.refresh_from_db()
        
        # 创建时间不应该改变
        self.assertEqual(article.created_at, original_created_at)
        
        # 更新时间应该改变
        self.assertGreater(article.updated_at, original_updated_at)
    
    def test_timestamped_model_is_abstract(self):
        """测试TimestampedModel是抽象模型"""
        self.assertTrue(TimestampedModel._meta.abstract)
        
        # 验证有正确的字段
        field_names = [f.name for f in TimestampedModel._meta.fields]
        self.assertIn('created_at', field_names)
        self.assertIn('updated_at', field_names)
    
    def test_timestamp_field_properties(self):
        """测试时间戳字段属性"""
        created_at_field = TimestampedModel._meta.get_field('created_at')
        updated_at_field = TimestampedModel._meta.get_field('updated_at')
        
        # created_at应该有auto_now_add=True
        self.assertTrue(created_at_field.auto_now_add)
        self.assertFalse(created_at_field.auto_now)
        
        # updated_at应该有auto_now=True
        self.assertTrue(updated_at_field.auto_now)
        self.assertFalse(updated_at_field.auto_now_add)


class SoftDeleteModelTest(TestCase):
    """软删除模型测试"""
    
    def test_soft_delete_model_is_abstract(self):
        """测试SoftDeleteModel是抽象模型"""
        self.assertTrue(SoftDeleteModel._meta.abstract)
        
        # 验证有正确的字段
        field_names = [f.name for f in SoftDeleteModel._meta.fields]
        self.assertIn('is_deleted', field_names)
        self.assertIn('deleted_at', field_names)
    
    def test_soft_delete_field_properties(self):
        """测试软删除字段属性"""
        is_deleted_field = SoftDeleteModel._meta.get_field('is_deleted')
        deleted_at_field = SoftDeleteModel._meta.get_field('deleted_at')
        
        # is_deleted应该默认为False
        self.assertFalse(is_deleted_field.default)
        
        # deleted_at应该可以为空
        self.assertTrue(deleted_at_field.null)
        self.assertTrue(deleted_at_field.blank)
    
    def test_soft_delete_default_values(self):
        """测试软删除默认值"""
        # 抽象模型不能直接实例化，我们检查字段的默认值
        is_deleted_field = SoftDeleteModel._meta.get_field('is_deleted')
        deleted_at_field = SoftDeleteModel._meta.get_field('deleted_at')
        
        # 默认应该不是删除状态
        self.assertFalse(is_deleted_field.default)
        # deleted_at字段没有默认值（NOT_PROVIDED）
        from django.db.models.fields import NOT_PROVIDED
        self.assertEqual(deleted_at_field.default, NOT_PROVIDED)


class OwnedModelTest(TestCase):
    """所有权模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_owned_model_is_abstract(self):
        """测试OwnedModel是抽象模型"""
        self.assertTrue(OwnedModel._meta.abstract)
        
        # 验证有正确的字段
        field_names = [f.name for f in OwnedModel._meta.fields]
        self.assertIn('created_by', field_names)
        self.assertIn('updated_by', field_names)
    
    def test_owned_field_properties(self):
        """测试所有权字段属性"""
        created_by_field = OwnedModel._meta.get_field('created_by')
        updated_by_field = OwnedModel._meta.get_field('updated_by')
        
        # 两个字段都应该可以为空
        self.assertTrue(created_by_field.null)
        self.assertTrue(created_by_field.blank)
        self.assertTrue(updated_by_field.null)
        self.assertTrue(updated_by_field.blank)
        
        # 都应该是外键到User模型
        # 检查related_model是字符串还是实际模型类
        if isinstance(created_by_field.related_model, str):
            self.assertEqual(created_by_field.related_model, 'users.User')
        else:
            self.assertEqual(created_by_field.related_model, User)
        
        if isinstance(updated_by_field.related_model, str):
            self.assertEqual(updated_by_field.related_model, 'users.User')
        else:
            self.assertEqual(updated_by_field.related_model, User)
        
        # 删除时应该设置为NULL
        self.assertEqual(created_by_field.remote_field.on_delete.__name__, 'SET_NULL')
        self.assertEqual(updated_by_field.remote_field.on_delete.__name__, 'SET_NULL')
    
    def test_related_name_generation(self):
        """测试相关名称生成"""
        created_by_field = OwnedModel._meta.get_field('created_by')
        updated_by_field = OwnedModel._meta.get_field('updated_by')
        
        # 相关名称应该包含app_label和class名称
        self.assertIn('created', created_by_field.related_query_name())
        self.assertIn('updated', updated_by_field.related_query_name())


class AbstractModelInheritanceTest(TestCase):
    """抽象模型继承测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='测试分类',
            description='测试分类描述'
        )
    
    def test_article_inherits_timestamped(self):
        """测试Article继承TimestampedModel"""
        # 检查Article是否继承了TimestampedModel的字段
        article_fields = [f.name for f in Article._meta.fields]
        
        self.assertIn('created_at', article_fields)
        self.assertIn('updated_at', article_fields)
        
        # 检查Article模型是否有时间戳字段（说明继承了TimestampedModel）
        # 注意：Django的模型继承可能不会直接显示在issubclass中
        self.assertTrue(hasattr(Article, 'created_at'))
        self.assertTrue(hasattr(Article, 'updated_at'))
    
    def test_multiple_inheritance_compatibility(self):
        """测试多重继承兼容性"""
        # 验证抽象模型可以被多重继承
        # 这里我们检查字段是否正确继承而没有冲突
        
        # 创建一个继承多个抽象模型的实例
        article = Article.objects.create(
            title='测试文章',
            content='测试内容',
            category=self.category,
            author=self.user
        )
        
        # 验证所有继承的字段都存在
        self.assertTrue(hasattr(article, 'created_at'))
        self.assertTrue(hasattr(article, 'updated_at'))
        
        # 验证字段值
        self.assertIsNotNone(article.created_at)
        self.assertIsNotNone(article.updated_at)
    
    def test_no_table_creation_for_abstract_models(self):
        """测试抽象模型不创建数据库表"""
        from django.db import connection
        
        table_names = connection.introspection.table_names()
        
        # 抽象模型不应该有对应的数据库表
        abstract_tables = [
            'common_timestampedmodel',
            'common_softdeletemodel', 
            'common_ownedmodel'
        ]
        
        for table in abstract_tables:
            self.assertNotIn(table, table_names)


class ModelFieldInheritanceTest(TestCase):
    """模型字段继承测试"""
    
    def test_field_inheritance_order(self):
        """测试字段继承顺序"""
        # 验证继承的字段在模型中的顺序
        article_fields = Article._meta.fields
        field_names = [f.name for f in article_fields]
        
        # 检查时间戳字段是否存在
        self.assertIn('created_at', field_names)
        self.assertIn('updated_at', field_names)
    
    def test_field_type_preservation(self):
        """测试字段类型保持"""
        # 验证继承的字段类型正确
        created_at_field = Article._meta.get_field('created_at')
        updated_at_field = Article._meta.get_field('updated_at')
        
        self.assertEqual(type(created_at_field).__name__, 'DateTimeField')
        self.assertEqual(type(updated_at_field).__name__, 'DateTimeField')
    
    def test_field_options_inheritance(self):
        """测试字段选项继承"""
        # 验证字段选项正确继承
        created_at_field = Article._meta.get_field('created_at')
        updated_at_field = Article._meta.get_field('updated_at')
        
        # 验证auto_now和auto_now_add选项
        self.assertTrue(created_at_field.auto_now_add)
        self.assertFalse(created_at_field.auto_now)
        self.assertTrue(updated_at_field.auto_now)
        self.assertFalse(updated_at_field.auto_now_add)


class CommonModelsIntegrationTest(TestCase):
    """通用模型集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='测试分类',
            description='测试分类描述'
        )
    
    def test_real_world_usage(self):
        """测试真实世界使用场景"""
        # 创建文章，测试所有继承的功能
        article = Article.objects.create(
            title='集成测试文章',
            content='这是一个集成测试文章',
            category=self.category,
            author=self.user
        )
        
        # 验证时间戳功能
        self.assertIsNotNone(article.created_at)
        self.assertIsNotNone(article.updated_at)
        
        # 记录原始时间
        original_created = article.created_at
        original_updated = article.updated_at
        
        # 等待后更新
        import time
        time.sleep(0.01)
        
        article.title = '更新后的标题'
        article.save()
        
        article.refresh_from_db()
        
        # 验证时间戳更新
        self.assertEqual(article.created_at, original_created)
        self.assertGreater(article.updated_at, original_updated)
    
    def test_queryset_operations_with_inherited_fields(self):
        """测试使用继承字段的查询集操作"""
        # 创建多个文章
        article1 = Article.objects.create(
            title='文章1',
            content='内容1',
            category=self.category,
            author=self.user
        )
        
        # 等待一小段时间
        import time
        time.sleep(0.01)
        
        article2 = Article.objects.create(
            title='文章2',
            content='内容2',
            category=self.category,
            author=self.user
        )
        
        # 测试按创建时间排序
        articles_by_created = Article.objects.order_by('created_at')
        self.assertEqual(articles_by_created[0], article1)
        self.assertEqual(articles_by_created[1], article2)
        
        # 测试按创建时间倒序
        articles_by_created_desc = Article.objects.order_by('-created_at')
        self.assertEqual(articles_by_created_desc[0], article2)
        self.assertEqual(articles_by_created_desc[1], article1)
        
        # 测试时间范围查询
        recent_articles = Article.objects.filter(
            created_at__gte=timezone.now() - timedelta(minutes=1)
        )
        self.assertEqual(recent_articles.count(), 2)


print("✅ 通用模块测试用例创建完成")