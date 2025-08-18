"""
英语模块API功能测试
用于验证打字练习相关API是否正常工作
"""

import os
import sys
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from .models import TypingWord, Dictionary, TypingSession, UserTypingStats

User = get_user_model()


class TypingPracticeAPITestCase(TestCase):
    """打字练习API功能测试用例"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试词库
        self.dictionary = Dictionary.objects.create(
            name='CET4_T',
            category='CET4',
            total_words=100,
            chapter_count=4,
            description='CET4测试词库'
        )
        
        # 创建测试单词
        self.word1 = TypingWord.objects.create(
            word='test',
            translation='测试',
            phonetic='test',
            difficulty='beginner',
            dictionary=self.dictionary,
            chapter=1,
            frequency=100
        )
        
        self.word2 = TypingWord.objects.create(
            word='example',
            translation='例子',
            phonetic='ɪɡˈzæmpəl',
            difficulty='intermediate',
            dictionary=self.dictionary,
            chapter=1,
            frequency=50
        )
        
        # 创建用户统计
        self.user_stats = UserTypingStats.objects.create(
            user=self.user,
            total_words_practiced=0,
            total_correct_words=0,
            average_wpm=0.0,
            total_practice_time=0
        )
        
        # 创建API客户端
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_get_typing_words_success(self):
        """测试成功获取打字练习单词"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'category': 'CET4_T',
            'difficulty': 'beginner',
            'chapter': 1,
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应数据: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertTrue(len(response.data) > 0)
        
        # 验证返回的单词数据
        word_data = response.data[0]
        self.assertIn('id', word_data)
        self.assertIn('word', word_data)
        self.assertIn('translation', word_data)
        self.assertIn('phonetic', word_data)
        self.assertIn('difficulty', word_data)
        self.assertIn('chapter', word_data)
    
    def test_get_typing_words_invalid_category(self):
        """测试无效词库类别的错误处理"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'category': 'INVALID_CATEGORY',
            'difficulty': 'beginner',
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        print(f"无效类别API响应状态码: {response.status_code}")
        print(f"无效类别API响应数据: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_typing_words_invalid_difficulty(self):
        """测试无效难度级别的错误处理"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'category': 'CET4_T',
            'difficulty': 'invalid',
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        print(f"无效难度API响应状态码: {response.status_code}")
        print(f"无效难度API响应数据: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_typing_words_with_chapter_filter(self):
        """测试按章节过滤单词"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'category': 'CET4_T',
            'difficulty': 'beginner',
            'chapter': 1,
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        print(f"章节过滤API响应状态码: {response.status_code}")
        print(f"章节过滤API响应数据: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证所有返回的单词都在指定章节
        for word_data in response.data:
            self.assertEqual(word_data['chapter'], 1)
    
    def test_get_typing_words_without_chapter(self):
        """测试不指定章节时获取所有单词"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'category': 'CET4_T',
            'difficulty': 'beginner',
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        print(f"无章节过滤API响应状态码: {response.status_code}")
        print(f"无章节过滤API响应数据: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
    
    def test_get_typing_words_dictionary_not_found(self):
        """测试词库不存在时的错误处理"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'category': 'NONEXISTENT_DICT',
            'difficulty': 'beginner',
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        print(f"词库不存在API响应状态码: {response.status_code}")
        print(f"词库不存在API响应数据: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)


if __name__ == '__main__':
    # 直接运行测试
    import unittest
    unittest.main()

英语模块API功能测试
用于验证打字练习相关API是否正常工作
"""

import os
import sys
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from .models import TypingWord, Dictionary, TypingSession, UserTypingStats

User = get_user_model()


class TypingPracticeAPITestCase(TestCase):
    """打字练习API功能测试用例"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试词库
        self.dictionary = Dictionary.objects.create(
            name='CET4_T',
            category='CET4',
            total_words=100,
            chapter_count=4,
            description='CET4测试词库'
        )
        
        # 创建测试单词
        self.word1 = TypingWord.objects.create(
            word='test',
            translation='测试',
            phonetic='test',
            difficulty='beginner',
            dictionary=self.dictionary,
            chapter=1,
            frequency=100
        )
        
        self.word2 = TypingWord.objects.create(
            word='example',
            translation='例子',
            phonetic='ɪɡˈzæmpəl',
            difficulty='intermediate',
            dictionary=self.dictionary,
            chapter=1,
            frequency=50
        )
        
        # 创建用户统计
        self.user_stats = UserTypingStats.objects.create(
            user=self.user,
            total_words_practiced=0,
            total_correct_words=0,
            average_wpm=0.0,
            total_practice_time=0
        )
        
        # 创建API客户端
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_get_typing_words_success(self):
        """测试成功获取打字练习单词"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'category': 'CET4_T',
            'difficulty': 'beginner',
            'chapter': 1,
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应数据: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertTrue(len(response.data) > 0)
        
        # 验证返回的单词数据
        word_data = response.data[0]
        self.assertIn('id', word_data)
        self.assertIn('word', word_data)
        self.assertIn('translation', word_data)
        self.assertIn('phonetic', word_data)
        self.assertIn('difficulty', word_data)
        self.assertIn('chapter', word_data)
    
    def test_get_typing_words_invalid_category(self):
        """测试无效词库类别的错误处理"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'category': 'INVALID_CATEGORY',
            'difficulty': 'beginner',
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        print(f"无效类别API响应状态码: {response.status_code}")
        print(f"无效类别API响应数据: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_typing_words_invalid_difficulty(self):
        """测试无效难度级别的错误处理"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'category': 'CET4_T',
            'difficulty': 'invalid',
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        print(f"无效难度API响应状态码: {response.status_code}")
        print(f"无效难度API响应数据: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_typing_words_with_chapter_filter(self):
        """测试按章节过滤单词"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'category': 'CET4_T',
            'difficulty': 'beginner',
            'chapter': 1,
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        print(f"章节过滤API响应状态码: {response.status_code}")
        print(f"章节过滤API响应数据: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证所有返回的单词都在指定章节
        for word_data in response.data:
            self.assertEqual(word_data['chapter'], 1)
    
    def test_get_typing_words_without_chapter(self):
        """测试不指定章节时获取所有单词"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'category': 'CET4_T',
            'difficulty': 'beginner',
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        print(f"无章节过滤API响应状态码: {response.status_code}")
        print(f"无章节过滤API响应数据: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
    
    def test_get_typing_words_dictionary_not_found(self):
        """测试词库不存在时的错误处理"""
        url = '/api/v1/english/typing-practice/words/'
        params = {
            'category': 'NONEXISTENT_DICT',
            'difficulty': 'beginner',
            'limit': 5
        }
        
        response = self.client.get(url, params)
        
        print(f"词库不存在API响应状态码: {response.status_code}")
        print(f"词库不存在API响应数据: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)


if __name__ == '__main__':
    # 直接运行测试
    import unittest
    unittest.main()

