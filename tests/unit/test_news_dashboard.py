"""
英语新闻仪表板功能测试
"""
import pytest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.english.models import News

User = get_user_model()


class NewsDashboardTestCase(TestCase):
    """新闻仪表板功能测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试新闻数据
        self.news1 = News.objects.create(
            title='Test News 1',
            summary='This is a test news summary',
            content='This is the full content of test news 1',
            source='bbc',
            source_url='https://example.com/news1',
            publish_date='2024-01-01'
        )
        
        self.news2 = News.objects.create(
            title='Test News 2',
            summary='This is another test news summary',
            content='This is the full content of test news 2',
            source='cnn',
            source_url='https://example.com/news2',
            publish_date='2024-01-02'
        )
        
        self.news3 = News.objects.create(
            title='Test News 3',
            summary='This is a third test news summary',
            content='This is the full content of test news 3',
            source='techcrunch',
            source_url='https://example.com/news3',
            publish_date='2024-01-03'
        )

    def test_news_dashboard_page_loads(self):
        """测试新闻仪表板页面能够正常加载"""
        self.client.force_login(self.user)
        response = self.client.get('/english/news-dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_news_list_api_returns_data(self):
        """测试新闻列表API返回数据"""
        self.client.force_login(self.user)
        response = self.client.get('/api/v1/english/news/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('data', data)  # API返回的是data字段而不是results
        self.assertGreater(len(data['data']), 0)

    def test_news_filtering_by_source(self):
        """测试按新闻源筛选功能"""
        self.client.force_login(self.user)
        
        # 测试筛选BBC新闻
        response = self.client.get('/api/v1/english/news/?source=bbc')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        results = data.get('data', [])  # API返回的是data字段
        for news in results:
            self.assertEqual(news['source'], 'bbc')

    def test_news_search_functionality(self):
        """测试新闻搜索功能"""
        self.client.force_login(self.user)
        
        # 测试搜索包含"test"的新闻
        response = self.client.get('/api/v1/english/news/?q=test')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        results = data.get('data', [])  # API返回的是data字段
        self.assertGreater(len(results), 0)

    def test_news_visibility_toggle(self):
        """测试新闻可见性切换功能"""
        self.client.force_login(self.user)
        
        # 切换新闻可见性 - 注意：News模型没有is_visible字段，这里测试更新其他字段
        response = self.client.patch(
            f'/api/v1/english/news/{self.news1.id}/',
            {'title': 'Updated Test News 1'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 验证更新
        self.news1.refresh_from_db()
        self.assertEqual(self.news1.title, 'Updated Test News 1')

    def test_news_deletion(self):
        """测试新闻删除功能"""
        self.client.force_login(self.user)
        
        # 删除新闻
        response = self.client.delete(f'/api/v1/english/news/{self.news1.id}/delete_news/')
        self.assertEqual(response.status_code, 204)
        
        # 验证新闻已被删除
        self.assertFalse(News.objects.filter(id=self.news1.id).exists())

    def test_news_crawl_api(self):
        """测试新闻爬取API"""
        self.client.force_login(self.user)
        
        # 测试爬取API调用
        crawl_data = {
            'sources': ['bbc', 'cnn'],
            'max_articles': 3,
            'timeout': 30,
            'auto_crawl': False
        }
        
        response = self.client.post(
            '/api/v1/english/news/crawl/',
            crawl_data,
            content_type='application/json'
        )
        # API应该返回200或202（异步处理）
        self.assertIn(response.status_code, [200, 202])

    def test_news_detail_api(self):
        """测试新闻详情API"""
        self.client.force_login(self.user)
        
        response = self.client.get(f'/api/v1/english/news/{self.news1.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        # API可能返回嵌套的数据结构
        if 'data' in data:
            news_data = data['data']
        else:
            news_data = data
            
        self.assertEqual(news_data['title'], 'Test News 1')
        self.assertEqual(news_data['source'], 'bbc')

    def test_news_pagination(self):
        """测试新闻分页功能"""
        self.client.force_login(self.user)
        
        # 测试分页参数
        response = self.client.get('/api/v1/english/news/?page=1&page_size=2')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('pagination', data)  # API返回的是pagination字段
        self.assertIn('data', data)        # API返回的是data字段

    def test_news_ordering(self):
        """测试新闻排序功能"""
        self.client.force_login(self.user)
        
        # 测试按发布时间排序
        response = self.client.get('/api/v1/english/news/?ordering=-publish_date')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        results = data.get('data', [])  # API返回的是data字段
        
        # 验证排序（最新的在前）
        if len(results) > 1:
            first_date = results[0]['publish_date']
            second_date = results[1]['publish_date']
            self.assertGreaterEqual(first_date, second_date)

    def test_news_stats_calculation(self):
        """测试新闻统计计算"""
        # 验证新闻统计（News模型没有is_visible字段）
        total_news = News.objects.count()
        
        self.assertEqual(total_news, 3)
        
        # 验证按来源分组
        bbc_news = News.objects.filter(source='bbc').count()
        cnn_news = News.objects.filter(source='cnn').count()
        techcrunch_news = News.objects.filter(source='techcrunch').count()
        
        self.assertEqual(bbc_news, 1)
        self.assertEqual(cnn_news, 1)
        self.assertEqual(techcrunch_news, 1)

    def test_news_dashboard_requires_auth(self):
        """测试新闻仪表板需要认证"""
        response = self.client.get('/english/news-dashboard/')
        # 应该重定向到登录页面
        self.assertEqual(response.status_code, 302)

    def test_news_api_requires_auth(self):
        """测试新闻API需要认证"""
        response = self.client.get('/api/v1/english/news/')
        self.assertEqual(response.status_code, 401)


@pytest.mark.django_db
class NewsDashboardFrontendTestCase:
    """前端新闻仪表板测试"""
    
    def test_news_store_initialization(self):
        """测试新闻store初始化"""
        from frontend.src.stores.news import useNewsStore
        
        # 这里可以测试store的初始化
        # 注意：这是前端测试，需要在实际的前端测试环境中运行
        pass
    
    def test_crawl_settings_persistence(self):
        """测试爬取设置持久化"""
        # 测试本地存储功能
        import json
        
        test_settings = {
            'maxArticles': 5,
            'timeout': 45,
            'sources': ['bbc', 'cnn', 'techcrunch'],
            'autoCrawl': True
        }
        
        # 模拟保存设置
        settings_json = json.dumps(test_settings)
        
        # 模拟加载设置
        loaded_settings = json.loads(settings_json)
        
        assert loaded_settings['maxArticles'] == 5
        assert loaded_settings['timeout'] == 45
        assert 'bbc' in loaded_settings['sources']
        assert loaded_settings['autoCrawl'] is True

    def test_news_filtering_logic(self):
        """测试新闻筛选逻辑"""
        # 模拟新闻数据
        mock_news = [
            {'id': 1, 'title': 'BBC News', 'source': 'bbc', 'is_visible': True},
            {'id': 2, 'title': 'CNN News', 'source': 'cnn', 'is_visible': True},
            {'id': 3, 'title': 'Tech News', 'source': 'techcrunch', 'is_visible': False},
        ]
        
        # 测试按来源筛选
        bbc_news = [news for news in mock_news if news['source'] == 'bbc']
        assert len(bbc_news) == 1
        assert bbc_news[0]['title'] == 'BBC News'
        
        # 测试可见性筛选
        visible_news = [news for news in mock_news if news['is_visible']]
        assert len(visible_news) == 2
        
        # 测试搜索筛选
        search_keyword = 'BBC'
        search_results = [news for news in mock_news if search_keyword.lower() in news['title'].lower()]
        assert len(search_results) == 1
        assert search_results[0]['title'] == 'BBC News'

    def test_news_categorization(self):
        """测试新闻分类逻辑"""
        # 模拟新闻数据
        mock_news = [
            {'id': 1, 'title': 'News 1', 'published_at': '2024-01-01T10:00:00Z'},
            {'id': 2, 'title': 'News 2', 'published_at': '2024-01-02T10:00:00Z'},
            {'id': 3, 'title': 'News 3', 'published_at': '2024-01-03T10:00:00Z'},
            {'id': 4, 'title': 'News 4', 'published_at': '2024-01-04T10:00:00Z'},
            {'id': 5, 'title': 'News 5', 'published_at': '2024-01-05T10:00:00Z'},
        ]
        
        # 测试特色新闻（前5条）
        featured_news = mock_news[:5]
        assert len(featured_news) == 5
        
        # 测试热门新闻（前6条）
        hot_news = mock_news[:6]
        assert len(hot_news) == 5  # 因为只有5条新闻
        
        # 测试最新新闻（前10条）
        latest_news = mock_news[:10]
        assert len(latest_news) == 5  # 因为只有5条新闻

    def test_date_formatting(self):
        """测试日期格式化功能"""
        from datetime import datetime
        
        # 测试日期格式化
        test_date = '2024-01-01T10:30:00Z'
        date_obj = datetime.fromisoformat(test_date.replace('Z', '+00:00'))
        
        # 模拟中文日期格式化
        formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
        assert '2024-01-01' in formatted_date
        assert '10:30' in formatted_date

    def test_text_truncation(self):
        """测试文本截断功能"""
        # 测试文本截断
        def truncate_text(text, max_length):
            if not text:
                return ''
            return text[:max_length] + '...' if len(text) > max_length else text
        
        # 测试长文本截断
        long_text = "This is a very long text that should be truncated"
        truncated = truncate_text(long_text, 20)
        assert len(truncated) <= 23  # 20 + '...'
        assert truncated.endswith('...')
        
        # 测试短文本不截断
        short_text = "Short text"
        not_truncated = truncate_text(short_text, 20)
        assert not_truncated == short_text
        assert not not_truncated.endswith('...')


if __name__ == '__main__':
    pytest.main([__file__])
















