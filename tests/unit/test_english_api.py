"""
地道表达API测试
"""

import pytest
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch

from apps.english.models import (
    IdiomaticExpression, ExpressionSource, ExpressionScenario,
    ExpressionScenarioLink, UserExpressionProgress
)

User = get_user_model()


class IdiomaticExpressionAPITest(APITestCase):
    """地道表达API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试数据源
        self.source = ExpressionSource.objects.create(
            source_name='Test Dictionary',
            source_url='https://test.com',
            source_type='web',
            reliability_score=8
        )
        
        # 创建测试场景
        self.scenario = ExpressionScenario.objects.create(
            scenario_name='business',
            scenario_type='business',
            context_description='Business scenarios'
        )
        
        # 创建测试表达式
        self.expression = IdiomaticExpression.objects.create(
            expression='break the ice',
            meaning='to start a conversation',
            expression_type='idiom',
            formality_level='neutral',
            frequency_score=8,
            phonetic_transcription='/breɪk ðə aɪs/',
            usage_examples=['Let me break the ice.'],
            cultural_background='Common in social situations'
        )
        
        # 创建场景关联
        ExpressionScenarioLink.objects.create(
            expression=self.expression,
            scenario=self.scenario
        )
    
    def test_list_expressions(self):
        """测试获取表达式列表"""
        url = reverse('idiomaticexpression-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        
        expression_data = response.data['results'][0]
        self.assertEqual(expression_data['expression'], 'break the ice')
        self.assertEqual(expression_data['meaning'], 'to start a conversation')
        self.assertEqual(expression_data['scenario_count'], 1)
    
    def test_retrieve_expression(self):
        """测试获取单个表达式详情"""
        url = reverse('idiomaticexpression-detail', args=[self.expression.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['expression'], 'break the ice')
        self.assertEqual(data['meaning'], 'to start a conversation')
        self.assertEqual(data['phonetic_transcription'], '/breɪk ðə aɪs/')
        self.assertEqual(len(data['usage_examples']), 1)
        self.assertEqual(len(data['scenarios']), 1)
        self.assertEqual(data['scenarios'][0]['name'], 'business')
        self.assertIn('source', data)
        self.assertEqual(data['source']['source_name'], 'Test Dictionary')
    
    def test_create_expression_unauthorized(self):
        """测试未认证用户无法创建表达式"""
        url = reverse('idiomaticexpression-list')
        data = {
            'expression': 'piece of cake',
            'meaning': 'very easy',
            'expression_type': 'idiom',
            'formality_level': 'informal',
            'frequency_score': 7
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_expression_authorized(self):
        """测试认证用户可以创建表达式"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('idiomaticexpression-list')
        data = {
            'expression': 'piece of cake',
            'meaning': 'very easy',
            'expression_type': 'idiom',
            'formality_level': 'informal',
            'frequency_score': 7,
            'source_id': self.source.id,
            'scenario_ids': [self.scenario.id]
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证创建的数据
        created_id = response.data['id']
        expression = IdiomaticExpression.objects.get(id=created_id)
        self.assertEqual(expression.expression, 'piece of cake')
        self.assertEqual(expression.meaning, 'very easy')
        self.assertEqual(expression.source, self.source)
        self.assertEqual(expression.scenario_links.count(), 1)
    
    def test_create_expression_validation(self):
        """测试表达式创建验证"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('idiomaticexpression-list')
        
        # 测试表达式太短
        data = {
            'expression': 'a',
            'meaning': 'test',
            'frequency_score': 5
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expression', response.data)
        
        # 测试含义太短
        data = {
            'expression': 'test expression',
            'meaning': 'a',
            'frequency_score': 5
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('meaning', response.data)
        
        # 测试频率分数超出范围
        data = {
            'expression': 'test expression',
            'meaning': 'test meaning',
            'frequency_score': 11
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('frequency_score', response.data)
    
    def test_update_expression(self):
        """测试更新表达式"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('idiomaticexpression-detail', args=[self.expression.id])
        data = {
            'expression': 'break the ice',
            'meaning': 'to initiate conversation in social situations',
            'frequency_score': 9
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证更新
        self.expression.refresh_from_db()
        self.assertEqual(self.expression.meaning, 'to initiate conversation in social situations')
        self.assertEqual(self.expression.frequency_score, 9)
    
    def test_delete_expression(self):
        """测试删除表达式"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('idiomaticexpression-detail', args=[self.expression.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 验证删除
        self.assertFalse(IdiomaticExpression.objects.filter(id=self.expression.id).exists())
    
    def test_search_expressions(self):
        """测试搜索表达式"""
        url = reverse('idiomaticexpression-search')
        
        # 文本搜索
        response = self.client.get(url, {'q': 'break'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # 类型筛选
        response = self.client.get(url, {'expression_type': 'idiom'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # 正式程度筛选
        response = self.client.get(url, {'formality_level': 'formal'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        
        # 频率分数范围筛选
        response = self.client.get(url, {
            'frequency_score_min': 7,
            'frequency_score_max': 9
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_random_expressions(self):
        """测试随机获取表达式"""
        url = reverse('idiomaticexpression-random')
        response = self.client.get(url, {'limit': 5})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertLessEqual(len(response.data), 5)
    
    def test_popular_expressions(self):
        """测试获取热门表达式"""
        url = reverse('idiomaticexpression-popular')
        response = self.client.get(url, {'limit': 5})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)  # 我们的测试数据频率分数是8，大于7
    
    def test_recent_expressions(self):
        """测试获取最新表达式"""
        url = reverse('idiomaticexpression-recent')
        response = self.client.get(url, {'limit': 5})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
    
    def test_expression_stats(self):
        """测试获取表达式统计"""
        url = reverse('idiomaticexpression-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('total_count', data)
        self.assertIn('by_type', data)
        self.assertIn('by_formality', data)
        self.assertIn('avg_frequency_score', data)
        self.assertIn('by_source', data)
        
        self.assertEqual(data['total_count'], 1)
        self.assertGreater(data['avg_frequency_score'], 0)


class UserExpressionProgressAPITest(APITestCase):
    """用户表达式学习进度API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self.source = ExpressionSource.objects.create(
            source_name='Test Dictionary',
            source_url='https://test.com',
            source_type='web',
            reliability_score=8
        )
        
        self.expression = IdiomaticExpression.objects.create(
            expression='break the ice',
            meaning='to start a conversation',
            expression_type='idiom',
            formality_level='neutral',
            frequency_score=8
        )
        
        self.progress = UserExpressionProgress.objects.create(
            user=self.user,
            expression_id=self.expression.id,
            mastery_level=3,
            review_count=5,
            is_favorite=True,
            notes='Good example for business situations'
        )
    
    def test_list_progress(self):
        """测试获取学习进度列表"""
        url = reverse('userexpressionprogress-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        progress_data = response.data['results'][0]
        self.assertEqual(progress_data['mastery_level'], 3)
        self.assertEqual(progress_data['review_count'], 5)
        self.assertTrue(progress_data['is_favorite'])
        self.assertIn('expression', progress_data)
    
    def test_create_progress(self):
        """测试创建学习进度"""
        # 创建另一个表达式
        expression2 = IdiomaticExpression.objects.create(
            expression='piece of cake',
            meaning='very easy',
            expression_type='idiom',
            formality_level='informal',
            frequency_score=7,
            source=self.source
        )
        
        url = reverse('userexpressionprogress-list')
        data = {
            'expression_id': expression2.id,
            'mastery_level': 2,
            'is_favorite': False,
            'notes': 'Need more practice'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证创建
        progress = UserExpressionProgress.objects.get(
            user=self.user,
            expression=expression2
        )
        self.assertEqual(progress.mastery_level, 2)
        self.assertEqual(progress.notes, 'Need more practice')
    
    def test_update_progress(self):
        """测试更新学习进度"""
        url = reverse('userexpressionprogress-detail', args=[self.progress.id])
        data = {
            'mastery_level': 4,
            'notes': 'Much better now'
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证更新
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.mastery_level, 4)
        self.assertEqual(self.progress.notes, 'Much better now')
    
    def test_favorites(self):
        """测试获取收藏的表达式"""
        url = reverse('userexpressionprogress-favorites')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['is_favorite'])
    
    def test_mark_favorite(self):
        """测试标记/取消收藏"""
        url = reverse('userexpressionprogress-mark-favorite', args=[self.progress.id])
        
        # 取消收藏
        response = self.client.post(url, {'is_favorite': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_favorite'])
        
        # 验证数据库更新
        self.progress.refresh_from_db()
        self.assertFalse(self.progress.is_favorite)
        
        # 重新收藏
        response = self.client.post(url, {'is_favorite': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_favorite'])
    
    def test_update_mastery(self):
        """测试更新掌握程度"""
        url = reverse('userexpressionprogress-update-mastery', args=[self.progress.id])
        
        old_review_count = self.progress.review_count
        
        response = self.client.post(url, {'mastery_level': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mastery_level'], 5)
        self.assertEqual(response.data['review_count'], old_review_count + 1)
        
        # 验证数据库更新
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.mastery_level, 5)
        self.assertEqual(self.progress.review_count, old_review_count + 1)
        self.assertIsNotNone(self.progress.last_reviewed)
    
    def test_progress_stats(self):
        """测试学习统计"""
        url = reverse('userexpressionprogress-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('total_learned', data)
        self.assertIn('favorites_count', data)
        self.assertIn('mastery_distribution', data)
        self.assertIn('avg_mastery_level', data)
        
        self.assertEqual(data['total_learned'], 1)
        self.assertEqual(data['favorites_count'], 1)
        self.assertGreater(data['avg_mastery_level'], 0)
    
    def test_unauthorized_access(self):
        """测试未认证访问"""
        self.client.force_authenticate(user=None)
        
        url = reverse('userexpressionprogress-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LearningSessionAPITest(APITestCase):
    """学习会话API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self.source = ExpressionSource.objects.create(
            source_name='Test Dictionary',
            source_url='https://test.com',
            source_type='web',
            reliability_score=8
        )
        
        # 创建多个表达式
        self.expressions = []
        for i in range(5):
            expr = IdiomaticExpression.objects.create(
                expression=f'test expression {i}',
                meaning=f'test meaning {i}',
                expression_type='idiom',
                formality_level='neutral',
                frequency_score=5 + i,

            )
            self.expressions.append(expr)
        
        # 创建一些学习进度
        UserExpressionProgress.objects.create(
            user=self.user,
            expression_id=self.expressions[0].id,
            mastery_level=2,
            is_favorite=True
        )
        UserExpressionProgress.objects.create(
            user=self.user,
            expression_id=self.expressions[1].id,
            mastery_level=4,
            is_favorite=False
        )
    
    def test_create_review_session(self):
        """测试创建复习会话"""
        url = reverse('learningsession-create-session')
        data = {
            'session_type': 'review',
            'limit': 3
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        result = response.data
        self.assertEqual(result['session_type'], 'review')
        self.assertIn('expressions', result)
        self.assertIn('count', result)
        self.assertLessEqual(result['count'], 3)
    
    def test_create_new_session(self):
        """测试创建新表达式学习会话"""
        url = reverse('learningsession-create-session')
        data = {
            'session_type': 'new',
            'limit': 3
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        result = response.data
        self.assertEqual(result['session_type'], 'new')
        self.assertIn('expressions', result)
        self.assertGreater(result['count'], 0)
    
    def test_create_favorite_session(self):
        """测试创建收藏表达式学习会话"""
        url = reverse('learningsession-create-session')
        data = {
            'session_type': 'favorite',
            'limit': 5
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        result = response.data
        self.assertEqual(result['session_type'], 'favorite')
        self.assertEqual(result['count'], 1)  # 只有一个收藏的表达式
    
    def test_create_random_session(self):
        """测试创建随机学习会话"""
        url = reverse('learningsession-create-session')
        data = {
            'session_type': 'random',
            'limit': 3,
            'expression_types': ['idiom']
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        result = response.data
        self.assertEqual(result['session_type'], 'random')
        self.assertLessEqual(result['count'], 3)
    
    def test_session_validation(self):
        """测试学习会话参数验证"""
        url = reverse('learningsession-create-session')
        
        # 测试无效的会话类型
        data = {'session_type': 'invalid'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 测试超出限制的数量
        data = {
            'session_type': 'random',
            'limit': 100
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ExpressionSourceAPITest(APITestCase):
    """表达式数据源API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.source = ExpressionSource.objects.create(
            source_name='Test Dictionary',
            source_url='https://test.com',
            source_type='web',
            reliability_score=8
        )
    
    def test_list_sources(self):
        """测试获取数据源列表"""
        url = reverse('expressionsource-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        source_data = response.data['results'][0]
        self.assertEqual(source_data['source_name'], 'Test Dictionary')
        self.assertEqual(source_data['source_url'], 'https://test.com')
        self.assertEqual(source_data['reliability_score'], '8.00')
    
    def test_retrieve_source(self):
        """测试获取单个数据源详情"""
        url = reverse('expressionsource-detail', args=[self.source.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['source_name'], 'Test Dictionary')


class ExpressionScenarioAPITest(APITestCase):
    """表达式场景API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.scenario = ExpressionScenario.objects.create(
            scenario_name='business',
            scenario_type='business',
            context_description='Business scenarios'
        )
    
    def test_list_scenarios(self):
        """测试获取场景列表"""
        url = reverse('expressionscenario-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        scenario_data = response.data['results'][0]
        self.assertEqual(scenario_data['scenario_name'], 'business')
        self.assertEqual(scenario_data['context_description'], 'Business scenarios')
    
    def test_retrieve_scenario(self):
        """测试获取单个场景详情"""
        url = reverse('expressionscenario-detail', args=[self.scenario.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['scenario_name'], 'business')


class StatisticsAPITest(APITestCase):
    """统计API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试表达式
        self.expressions = []
        for i in range(5):
            expression = IdiomaticExpression.objects.create(
                expression=f'test expression {i}',
                meaning=f'test meaning {i}',
                expression_type='idiom',
                formality_level='informal',
                frequency_score=7.5,
                usage_examples=[f'Example {i}']
            )
            self.expressions.append(expression)
        
        # 创建用户学习进度
        for i, expression in enumerate(self.expressions):
            UserExpressionProgress.objects.create(
                user=self.user,
                expression=expression,
                mastery_level=i % 6,  # 0-5的掌握度
                review_count=i + 1,
                is_favorite=(i % 2 == 0)
            )
    
    def test_statistics_overview(self):
        """测试统计总览"""
        url = reverse('statistics-overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        # 验证基础统计
        self.assertEqual(data['total_learned'], 5)
        self.assertEqual(data['total_expressions'], 5)
        self.assertEqual(data['learning_progress'], 100.0)
        self.assertEqual(data['favorites_count'], 3)  # 0, 2, 4
        
        # 验证掌握度分布
        self.assertIn('mastery_distribution', data)
        self.assertIsInstance(data['mastery_distribution'], list)
    
    def test_statistics_learning_trend(self):
        """测试学习趋势"""
        url = reverse('statistics-learning-trend')
        response = self.client.get(url, {'days': 7})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertEqual(data['period_days'], 7)
        self.assertIn('daily_stats', data)
        self.assertEqual(len(data['daily_stats']), 7)
    
    def test_statistics_mastery_analysis(self):
        """测试掌握度分析"""
        url = reverse('statistics-mastery-analysis')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertIn('by_expression_type', data)
        self.assertIn('by_formality_level', data)
        self.assertIn('total_analyzed', data)
        self.assertEqual(data['total_analyzed'], 5)
    
    def test_statistics_weak_areas(self):
        """测试薄弱环节分析"""
        url = reverse('statistics-weak-areas')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertIn('weak_expressions', data)
        self.assertIn('need_review', data)
        self.assertIn('difficult_expressions', data)
    
    def test_statistics_authentication_required(self):
        """测试统计接口需要认证"""
        self.client.force_authenticate(user=None)
        url = reverse('statistics-overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AIAssistantAPITest(APITestCase):
    """AI助教API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建AI配置
        from apps.english.models import AIAssistantConfig
        self.ai_config = AIAssistantConfig.objects.create(
            model_name='test-model',
            api_endpoint='https://test-api.com',
            system_prompt='You are a helpful assistant',
            max_tokens=1000,
            temperature=0.7,
            is_active=True
        )
        
        # 创建测试表达式
        self.expression = IdiomaticExpression.objects.create(
            expression='break the ice',
            meaning='to start a conversation',
            expression_type='idiom',
            formality_level='informal',
            frequency_score=8.0,
            usage_examples=['Let me break the ice.']
        )
    
    @patch('apps.api.english_views.AIAssistantViewSet._get_ai_response')
    def test_ai_chat(self, mock_ai_response):
        """测试AI对话"""
        mock_ai_response.return_value = "这是AI助教的回复"
        
        url = reverse('aiassistant-chat')
        data = {
            'message': '你好，我想学习英语表达式',
            'context_type': 'general'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response'], "这是AI助教的回复")
        self.assertEqual(response.data['context_type'], 'general')
        self.assertIn('timestamp', response.data)
    
    def test_ai_chat_empty_message(self):
        """测试AI对话空消息"""
        url = reverse('aiassistant-chat')
        data = {'message': ''}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('apps.api.english_views.AIAssistantViewSet._get_ai_response')
    def test_explain_expression(self, mock_ai_response):
        """测试表达式解释"""
        mock_ai_response.return_value = "这是对表达式的详细解释"
        
        url = reverse('aiassistant-explain-expression')
        data = {
            'expression_id': self.expression.id,
            'question': '这个表达式的来源是什么？'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['expression'], 'break the ice')
        self.assertEqual(response.data['explanation'], "这是对表达式的详细解释")
        self.assertEqual(response.data['question'], '这个表达式的来源是什么？')
    
    def test_explain_expression_invalid_id(self):
        """测试解释不存在的表达式"""
        url = reverse('aiassistant-explain-expression')
        data = {'expression_id': 99999}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('apps.api.english_views.AIAssistantViewSet._get_ai_response')
    def test_practice_dialogue(self, mock_ai_response):
        """测试对话练习"""
        mock_ai_response.return_value = "【场景设定】商务会议\n【对话内容】A: Let me break the ice..."
        
        url = reverse('aiassistant-practice-dialogue')
        data = {
            'expression_id': self.expression.id,
            'scenario': 'business',
            'difficulty': 'medium'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['expression'], 'break the ice')
        self.assertEqual(response.data['scenario'], 'business')
        self.assertEqual(response.data['difficulty'], 'medium')
        self.assertIn('dialogue', response.data)
    
    def test_ai_service_unavailable(self):
        """测试AI服务不可用"""
        # 禁用AI配置
        self.ai_config.is_active = False
        self.ai_config.save()
        
        url = reverse('aiassistant-chat')
        data = {'message': 'test message'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('error', response.data)
    
    def test_ai_authentication_required(self):
        """测试AI接口需要认证"""
        self.client.force_authenticate(user=None)
        url = reverse('aiassistant-chat')
        data = {'message': 'test message'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
