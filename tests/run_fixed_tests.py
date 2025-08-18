#!/usr/bin/env python
"""
修复后的测试运行脚本
用于验证模型字段修复效果
"""

import os
import sys
import django
from django.conf import settings

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_settings_mysql')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.english.models import Word, News, Dictionary, TypingWord
from apps.users.models import UserProfile

User = get_user_model()


class FixedModelTests(TestCase):
    """修复后的模型测试"""
    
    def test_word_model_fields(self):
        """测试Word模型字段"""
        word = Word.objects.create(
            word='test',
            phonetic='/test/',
            definition='A test definition.',
            difficulty_level='intermediate'
        )
        
        self.assertEqual(word.word, 'test')
        self.assertEqual(word.phonetic, '/test/')
        self.assertEqual(word.definition, 'A test definition.')
        print("✅ Word模型字段测试通过")
    
    def test_news_model_fields(self):
        """测试News模型字段"""
        news = News.objects.create(
            title='Test News',
            content='Test news content.',
            source='test_source',
            source_url='https://example.com/test',
            difficulty_level='intermediate'
        )
        
        self.assertEqual(news.title, 'Test News')
        self.assertEqual(news.source_url, 'https://example.com/test')
        print("✅ News模型字段测试通过")
    
    def test_typing_word_model_fields(self):
        """测试TypingWord模型字段"""
        dictionary = Dictionary.objects.create(
            name='CET4_T',
            description='CET4词汇库',
            category='CET4',
            language='en',
            total_words=1000,
            chapter_count=10
        )
        
        typing_word = TypingWord.objects.create(
            word='test',
            translation='测试',
            phonetic='test',
            difficulty='beginner',
            dictionary=dictionary,
            chapter=1,
            frequency=100
        )
        
        self.assertEqual(typing_word.word, 'test')
        self.assertEqual(typing_word.dictionary, dictionary)
        print("✅ TypingWord模型字段测试通过")
    
    def test_user_profile_model_fields(self):
        """测试UserProfile模型字段"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        profile = UserProfile.objects.create(
            user=user,
            bio='测试用户简介'
        )
        
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.avatar_url, '')  # 默认为空字符串
        print("✅ UserProfile模型字段测试通过")


if __name__ == '__main__':
    import unittest
    
    # 运行测试
    unittest.main(verbosity=2) 