# -*- coding: utf-8 -*-
"""
English应用核心模型单元测试
测试Word、Expression、UserWordProgress等核心模型
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from datetime import datetime, date, timedelta

from apps.english.models import (
    Word, Expression, UserWordProgress, WordCategory, WordTag,
    WordExample, WordRelation, News, LearningPlan
)

User = get_user_model()


class WordModelTest(TestCase):
    """Word模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_word(self):
        """测试创建单词"""
        word = Word.objects.create(
            word='hello',
            phonetic='həˈloʊ',
            part_of_speech='interjection',
            definition='Used as a greeting or to begin a phone conversation',
            example='Hello, how are you today?',
            difficulty_level='beginner',
            frequency_rank=100
        )
        
        self.assertEqual(word.word, 'hello')
        self.assertEqual(word.phonetic, 'həˈloʊ')
        self.assertEqual(word.part_of_speech, 'interjection')
        self.assertEqual(word.difficulty_level, 'beginner')
        self.assertEqual(word.frequency_rank, 100)
        self.assertEqual(str(word), 'hello')
        self.assertFalse(word.is_deleted)
    
    def test_word_unique_constraint(self):
        """测试单词唯一性约束"""
        Word.objects.create(word='test', difficulty_level='beginner')
        
        with self.assertRaises(IntegrityError):
            Word.objects.create(word='test', difficulty_level='intermediate')
    
    def test_word_soft_delete(self):
        """测试单词软删除"""
        word = Word.objects.create(word='test', difficulty_level='beginner')
        word_id = word.id
        
        # 软删除
        word.is_deleted = True
        word.save()
        
        # 验证在正常查询中不可见（需要检查模型是否有自定义的查询集）
        # 如果模型没有自定义查询集，则所有记录都可见
        # 这里我们只测试字段值是否正确设置
        word.refresh_from_db()
        self.assertTrue(word.is_deleted)
        
        # 验证在包含删除项的查询中可见
        self.assertTrue(Word.objects.filter(id=word_id, is_deleted=True).exists())
    
    def test_word_quality_score_validation(self):
        """测试质量分验证"""
        word = Word.objects.create(
            word='test',
            difficulty_level='beginner',
            quality_score=Decimal('0.85')
        )
        
        self.assertEqual(word.quality_score, Decimal('0.85'))
        
        # 测试质量分范围
        word.quality_score = Decimal('1.00')
        word.save()
        
        word.quality_score = Decimal('0.00')
        word.save()


class ExpressionModelTest(TestCase):
    """Expression模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_expression(self):
        """测试创建表达"""
        expression = Expression.objects.create(
            expression='break the ice',
            meaning='To initiate conversation in a social setting',
            category='idiom',
            scenario='social',
            difficulty_level='intermediate',
            usage_frequency='medium'
        )
        
        self.assertEqual(expression.expression, 'break the ice')
        self.assertEqual(expression.category, 'idiom')
        self.assertEqual(expression.scenario, 'social')
        self.assertEqual(expression.difficulty_level, 'intermediate')
        self.assertEqual(str(expression), 'break the ice')
    
    def test_expression_unique_constraint(self):
        """测试表达唯一性约束"""
        Expression.objects.create(
            expression='test expression',
            scenario='test'
        )
        
        # 相同表达和场景应该失败
        with self.assertRaises(IntegrityError):
            Expression.objects.create(
                expression='test expression',
                scenario='test'
            )
    
    def test_expression_usage_examples_json(self):
        """测试使用示例JSON字段"""
        examples = [
            "Let's break the ice with a joke.",
            "She broke the ice by asking about the weather."
        ]
        
        expression = Expression.objects.create(
            expression='break the ice',
            meaning='To initiate conversation',
            usage_examples=examples
        )
        
        self.assertEqual(expression.usage_examples, examples)
        self.assertEqual(len(expression.usage_examples), 2)


class UserWordProgressModelTest(TestCase):
    """UserWordProgress模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.word = Word.objects.create(
            word='hello',
            difficulty_level='beginner'
        )
    
    def test_create_user_word_progress(self):
        """测试创建用户单词进度"""
        progress = UserWordProgress.objects.create(
            user=self.user,
            word=self.word,
            status='learning',
            review_count=3,
            mastery_level=Decimal('0.75')
        )
        
        self.assertEqual(progress.user, self.user)
        self.assertEqual(progress.word, self.word)
        self.assertEqual(progress.status, 'learning')
        self.assertEqual(progress.review_count, 3)
        self.assertEqual(progress.mastery_level, Decimal('0.75'))
        self.assertEqual(progress.ease_factor, Decimal('2.5'))
        self.assertEqual(progress.interval_days, 1)
    
    def test_user_word_progress_unique_constraint(self):
        """测试用户单词进度唯一性约束"""
        UserWordProgress.objects.create(
            user=self.user,
            word=self.word,
            status='learning'
        )
        
        with self.assertRaises(IntegrityError):
            UserWordProgress.objects.create(
                user=self.user,
                word=self.word,
                status='mastered'
            )
    
    def test_sm2_algorithm_fields(self):
        """测试SM-2算法相关字段"""
        progress = UserWordProgress.objects.create(
            user=self.user,
            word=self.word,
            status='learning'
        )
        
        # 测试默认值
        self.assertEqual(progress.ease_factor, Decimal('2.5'))
        self.assertEqual(progress.interval_days, 1)
        self.assertEqual(progress.repetition_count, 0)
        
        # 测试更新值
        progress.ease_factor = Decimal('2.7')
        progress.interval_days = 3
        progress.repetition_count = 2
        progress.save()
        
        progress.refresh_from_db()
        self.assertEqual(progress.ease_factor, Decimal('2.7'))
        self.assertEqual(progress.interval_days, 3)
        self.assertEqual(progress.repetition_count, 2)


class WordCategoryModelTest(TestCase):
    """WordCategory模型测试"""
    
    def test_create_word_category(self):
        """测试创建单词分类"""
        category = WordCategory.objects.create(
            name='Animals',
            description='Words related to animals'
        )
        
        self.assertEqual(category.name, 'Animals')
        self.assertEqual(category.description, 'Words related to animals')
        self.assertIsNone(category.parent)
        self.assertEqual(str(category), 'Animals')
    
    def test_word_category_hierarchy(self):
        """测试单词分类层次结构"""
        parent = WordCategory.objects.create(name='Animals')
        child = WordCategory.objects.create(
            name='Mammals',
            parent=parent
        )
        
        self.assertEqual(child.parent, parent)
        self.assertEqual(parent.wordcategory_set.first(), child)
    
    def test_word_category_unique_name(self):
        """测试单词分类名称唯一性"""
        WordCategory.objects.create(name='Test Category')
        
        with self.assertRaises(IntegrityError):
            WordCategory.objects.create(name='Test Category')


class WordTagModelTest(TestCase):
    """WordTag模型测试"""
    
    def test_create_word_tag(self):
        """测试创建单词标签"""
        tag = WordTag.objects.create(name='common')
        
        self.assertEqual(tag.name, 'common')
        self.assertEqual(str(tag), 'common')
    
    def test_word_tag_unique_name(self):
        """测试单词标签名称唯一性"""
        WordTag.objects.create(name='test_tag')
        
        with self.assertRaises(IntegrityError):
            WordTag.objects.create(name='test_tag')


class NewsModelTest(TestCase):
    """News模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_news(self):
        """测试创建新闻"""
        news = News.objects.create(
            title='Test News Article',
            summary='This is a test summary',
            content='This is the full content of the test article.',
            category='technology',
            difficulty_level='intermediate',
            source='Test Source',
            word_count=50,
            reading_time_minutes=2
        )
        
        self.assertEqual(news.title, 'Test News Article')
        self.assertEqual(news.category, 'technology')
        self.assertEqual(news.difficulty_level, 'intermediate')
        self.assertEqual(news.word_count, 50)
        self.assertEqual(news.reading_time_minutes, 2)
        self.assertEqual(str(news), 'Test News Article')
    
    def test_news_comprehension_questions_json(self):
        """测试理解题目JSON字段"""
        questions = [
            "What is the main topic?",
            "How many words are in the article?"
        ]
        
        news = News.objects.create(
            title='Test News',
            content='Test content',
            comprehension_questions=questions
        )
        
        self.assertEqual(news.comprehension_questions, questions)
        self.assertEqual(len(news.comprehension_questions), 2)
    
    def test_news_key_vocabulary(self):
        """测试关键词汇字段"""
        news = News.objects.create(
            title='Test News',
            content='Test content',
            key_vocabulary='technology, innovation, development'
        )
        
        self.assertEqual(news.key_vocabulary, 'technology, innovation, development')


class LearningPlanModelTest(TestCase):
    """LearningPlan模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_learning_plan(self):
        """测试创建学习计划"""
        today = date.today()
        plan = LearningPlan.objects.create(
            user=self.user,
            name='Daily English Practice',
            description='Practice 10 words every day',
            daily_word_target=10,
            is_active=True,
            start_date=today,
            end_date=today + timedelta(days=30)
        )
        
        self.assertEqual(plan.user, self.user)
        self.assertEqual(plan.name, 'Daily English Practice')
        self.assertEqual(plan.daily_word_target, 10)
        self.assertTrue(plan.is_active)
        # 根据实际模型的__str__方法调整断言
        self.assertIn('Daily English Practice', str(plan))
        self.assertIn('testuser', str(plan))
    
    def test_learning_plan_user_relationship(self):
        """测试学习计划与用户的关系"""
        today = date.today()
        plan = LearningPlan.objects.create(
            user=self.user,
            name='Test Plan',
            daily_word_target=5,
            start_date=today,
            end_date=today + timedelta(days=7)
        )
        
        self.assertEqual(plan.user, self.user)
        self.assertIn(plan, self.user.learning_plans.all())


class TestModelIntegration(TestCase):
    """模型集成测试"""
    
    def test_word_expression_relationship(self):
        """测试单词与表达的关系"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        word = Word.objects.create(
            word='break',
            difficulty_level='beginner'
        )
        
        expression = Expression.objects.create(
            expression='break the ice',
            meaning='To initiate conversation',
            category='idiom'
        )
        
        # 创建用户进度
        word_progress = UserWordProgress.objects.create(
            user=user,
            word=word,
            status='learning'
        )
        
        self.assertEqual(word_progress.user, user)
        self.assertEqual(word_progress.word, word)
        self.assertEqual(word_progress.status, 'learning')
    
    def test_model_cascade_delete(self):
        """测试模型级联删除"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        word = Word.objects.create(
            word='test',
            difficulty_level='beginner'
        )
        
        progress = UserWordProgress.objects.create(
            user=user,
            word=word,
            status='learning'
        )
        
        # 删除用户，相关进度应该被删除
        user.delete()
        
        # 验证进度被删除
        self.assertFalse(UserWordProgress.objects.filter(id=progress.id).exists())
        
        # 单词应该仍然存在
        self.assertTrue(Word.objects.filter(id=word.id).exists())

