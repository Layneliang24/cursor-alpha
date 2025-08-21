#!/usr/bin/env python3
"""
模型字段修复验证测试
采用测试驱动开发方式，确保测试逻辑符合产品功能设计
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.english.models import (
    Word, Expression, News, TypingWord, Dictionary,
    UserWordProgress, WordCategory, WordTag
)

User = get_user_model()


class ModelFieldsValidationTest(TestCase):
    """模型字段验证测试 - 确保测试使用的字段与模型定义一致"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试分类
        self.category = WordCategory.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        # 创建测试词库
        self.dictionary = Dictionary.objects.create(
            name='Test Dictionary',
            description='Test dictionary description',
            category='test',
            total_words=100
        )
    
    def test_word_model_correct_fields(self):
        """测试Word模型使用正确的字段"""
        # 使用正确的字段创建Word对象
        word = Word.objects.create(
            word='test',
            phonetic='/test/',
            definition='A test word.',  # 正确字段：definition
            difficulty_level='beginner',  # 正确字段：difficulty_level
            category_hint='test category'  # 正确字段：category_hint
        )
        
        # 验证对象创建成功
        self.assertEqual(word.word, 'test')
        self.assertEqual(word.definition, 'A test word.')
        self.assertEqual(word.difficulty_level, 'beginner')
        self.assertEqual(word.category_hint, 'test category')
        
        # 验证错误字段不存在
        with self.assertRaises(AttributeError):
            _ = word.meaning  # 错误字段：meaning
        with self.assertRaises(AttributeError):
            _ = word.difficulty  # 错误字段：difficulty
        with self.assertRaises(AttributeError):
            _ = word.category  # 错误字段：category
    
    def test_expression_model_correct_fields(self):
        """测试Expression模型使用正确的字段"""
        # 使用正确的字段创建Expression对象
        expression = Expression.objects.create(
            expression='break the ice',
            meaning='To initiate conversation.',
            difficulty_level='intermediate',  # 正确字段：difficulty_level
            category='idiom'
        )
        
        # 验证对象创建成功
        self.assertEqual(expression.expression, 'break the ice')
        self.assertEqual(expression.meaning, 'To initiate conversation.')
        self.assertEqual(expression.difficulty_level, 'intermediate')
        
        # 验证错误字段不存在
        with self.assertRaises(AttributeError):
            _ = expression.difficulty  # 错误字段：difficulty
    
    def test_news_model_correct_fields(self):
        """测试News模型使用正确的字段"""
        # 使用正确的字段创建News对象
        news = News.objects.create(
            title='Test News',
            content='Test news content.',
            source='test_source',  # 正确字段：source
            difficulty_level='intermediate',  # 正确字段：difficulty_level
            category='technology'
        )
        
        # 验证对象创建成功
        self.assertEqual(news.title, 'Test News')
        self.assertEqual(news.source, 'test_source')
        self.assertEqual(news.difficulty_level, 'intermediate')
        
        # 验证错误字段不存在
        with self.assertRaises(AttributeError):
            _ = news.source_name  # 错误字段：source_name
        with self.assertRaises(AttributeError):
            _ = news.difficulty  # 错误字段：difficulty
    
    def test_typing_word_model_correct_fields(self):
        """测试TypingWord模型使用正确的字段"""
        # 使用正确的字段创建TypingWord对象
        typing_word = TypingWord.objects.create(
            word='test',
            translation='测试',  # 正确字段：translation
            phonetic='/test/',
            difficulty='intermediate',  # 正确字段：difficulty
            dictionary=self.dictionary,
            chapter=1
        )
        
        # 验证对象创建成功
        self.assertEqual(typing_word.word, 'test')
        self.assertEqual(typing_word.translation, '测试')
        self.assertEqual(typing_word.difficulty, 'intermediate')
        
        # 验证错误字段不存在
        with self.assertRaises(AttributeError):
            _ = typing_word.meaning  # 错误字段：meaning
        with self.assertRaises(AttributeError):
            _ = typing_word.example  # 错误字段：example


class ModelFieldMappingTest(TestCase):
    """模型字段映射测试 - 验证字段映射的正确性"""
    
    def test_word_field_mapping(self):
        """测试Word模型字段映射"""
        # 正确的字段映射
        correct_mapping = {
            'definition': '释义',  # 正确
            'difficulty_level': '难度',  # 正确
            'category_hint': '分类提示',  # 正确
        }
        
        # 错误的字段映射（测试中使用的）
        incorrect_mapping = {
            'meaning': '含义',  # 错误 - 应该用 definition
            'difficulty': '难度',  # 错误 - 应该用 difficulty_level
            'category': '分类',  # 错误 - 应该用 category_hint
        }
        
        # 验证Word模型有正确的字段
        word_fields = [field.name for field in Word._meta.get_fields()]
        
        for correct_field in correct_mapping.keys():
            self.assertIn(correct_field, word_fields, 
                         f"Word模型应该包含字段: {correct_field}")
        
        for incorrect_field in incorrect_mapping.keys():
            self.assertNotIn(incorrect_field, word_fields,
                           f"Word模型不应该包含字段: {incorrect_field}")
    
    def test_expression_field_mapping(self):
        """测试Expression模型字段映射"""
        # 正确的字段映射
        correct_mapping = {
            'difficulty_level': '难度',  # 正确
        }
        
        # 错误的字段映射
        incorrect_mapping = {
            'difficulty': '难度',  # 错误 - 应该用 difficulty_level
        }
        
        # 验证Expression模型有正确的字段
        expression_fields = [field.name for field in Expression._meta.get_fields()]
        
        for correct_field in correct_mapping.keys():
            self.assertIn(correct_field, expression_fields,
                         f"Expression模型应该包含字段: {correct_field}")
        
        for incorrect_field in incorrect_mapping.keys():
            self.assertNotIn(incorrect_field, expression_fields,
                           f"Expression模型不应该包含字段: {incorrect_field}")
    
    def test_news_field_mapping(self):
        """测试News模型字段映射"""
        # 正确的字段映射
        correct_mapping = {
            'source': '来源',  # 正确
            'difficulty_level': '难度',  # 正确
        }
        
        # 错误的字段映射
        incorrect_mapping = {
            'source_name': '来源名称',  # 错误 - 应该用 source
            'difficulty': '难度',  # 错误 - 应该用 difficulty_level
        }
        
        # 验证News模型有正确的字段
        news_fields = [field.name for field in News._meta.get_fields()]
        
        for correct_field in correct_mapping.keys():
            self.assertIn(correct_field, news_fields,
                         f"News模型应该包含字段: {correct_field}")
        
        for incorrect_field in incorrect_mapping.keys():
            self.assertNotIn(incorrect_field, news_fields,
                           f"News模型不应该包含字段: {incorrect_field}")
    
    def test_typing_word_field_mapping(self):
        """测试TypingWord模型字段映射"""
        # 正确的字段映射
        correct_mapping = {
            'translation': '翻译',  # 正确
            'difficulty': '难度',  # 正确
        }
        
        # 错误的字段映射
        incorrect_mapping = {
            'meaning': '含义',  # 错误 - 应该用 translation
            'example': '例句',  # 错误 - 模型中没有这个字段
        }
        
        # 验证TypingWord模型有正确的字段
        typing_word_fields = [field.name for field in TypingWord._meta.get_fields()]
        
        for correct_field in correct_mapping.keys():
            self.assertIn(correct_field, typing_word_fields,
                         f"TypingWord模型应该包含字段: {correct_field}")
        
        for incorrect_field in incorrect_mapping.keys():
            self.assertNotIn(incorrect_field, typing_word_fields,
                           f"TypingWord模型不应该包含字段: {incorrect_field}")


class ModelFieldUsageTest(TestCase):
    """模型字段使用测试 - 验证实际使用场景"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.dictionary = Dictionary.objects.create(
            name='Test Dictionary',
            category='test',
            total_words=100
        )
    
    def test_word_creation_with_correct_fields(self):
        """测试使用正确字段创建Word对象"""
        word = Word.objects.create(
            word='hello',
            phonetic='/həˈloʊ/',
            definition='Used as a greeting or to begin a phone conversation.',
            difficulty_level='beginner',
            category_hint='greeting'
        )
        
        # 验证创建成功
        self.assertIsNotNone(word.id)
        self.assertEqual(word.word, 'hello')
        self.assertEqual(word.definition, 'Used as a greeting or to begin a phone conversation.')
        self.assertEqual(word.difficulty_level, 'beginner')
        self.assertEqual(word.category_hint, 'greeting')
    
    def test_expression_creation_with_correct_fields(self):
        """测试使用正确字段创建Expression对象"""
        expression = Expression.objects.create(
            expression='piece of cake',
            meaning='Something that is very easy to do.',
            difficulty_level='intermediate',
            category='idiom'
        )
        
        # 验证创建成功
        self.assertIsNotNone(expression.id)
        self.assertEqual(expression.expression, 'piece of cake')
        self.assertEqual(expression.meaning, 'Something that is very easy to do.')
        self.assertEqual(expression.difficulty_level, 'intermediate')
    
    def test_news_creation_with_correct_fields(self):
        """测试使用正确字段创建News对象"""
        news = News.objects.create(
            title='Test News Title',
            content='This is test news content.',
            source='bbc',
            difficulty_level='intermediate',
            category='technology'
        )
        
        # 验证创建成功
        self.assertIsNotNone(news.id)
        self.assertEqual(news.title, 'Test News Title')
        self.assertEqual(news.source, 'bbc')
        self.assertEqual(news.difficulty_level, 'intermediate')
    
    def test_typing_word_creation_with_correct_fields(self):
        """测试使用正确字段创建TypingWord对象"""
        typing_word = TypingWord.objects.create(
            word='python',
            translation='蟒蛇；Python编程语言',
            phonetic='/ˈpaɪθən/',
            difficulty='intermediate',
            dictionary=self.dictionary,
            chapter=1
        )
        
        # 验证创建成功
        self.assertIsNotNone(typing_word.id)
        self.assertEqual(typing_word.word, 'python')
        self.assertEqual(typing_word.translation, '蟒蛇；Python编程语言')
        self.assertEqual(typing_word.difficulty, 'intermediate')


if __name__ == '__main__':
    pytest.main([__file__])
