import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.english.models import ChapterPracticeRecord, WrongWordRecord, DailyPracticeDuration
from datetime import datetime, date

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


class TestChapterPracticeStatsAPI:
    """测试章节练习统计API"""
    
    @pytest.mark.django_db
    def test_get_chapter_stats_empty(self, authenticated_client):
        """测试获取空的章节练习统计"""
        url = reverse('typing-practice-chapter-stats')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data'] == {}
    
    @pytest.mark.django_db
    def test_get_chapter_stats_with_data(self, authenticated_client, user):
        """测试获取有数据的章节练习统计"""
        # 创建测试数据
        ChapterPracticeRecord.objects.create(
            user=user,
            dictionary_id='toefl',
            chapter_number=1,
            practice_count=3
        )
        ChapterPracticeRecord.objects.create(
            user=user,
            dictionary_id='toefl',
            chapter_number=2,
            practice_count=1
        )
        ChapterPracticeRecord.objects.create(
            user=user,
            dictionary_id='ielts',
            chapter_number=1,
            practice_count=2
        )
        
        url = reverse('typing-practice-chapter-stats')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        expected_data = {
            'toefl': {1: 3, 2: 1},
            'ielts': {1: 2}
        }
        assert response.data['data'] == expected_data
    
    @pytest.mark.django_db
    def test_get_chapter_stats_filtered(self, authenticated_client, user):
        """测试按词典ID过滤章节练习统计"""
        # 创建测试数据
        ChapterPracticeRecord.objects.create(
            user=user,
            dictionary_id='toefl',
            chapter_number=1,
            practice_count=3
        )
        ChapterPracticeRecord.objects.create(
            user=user,
            dictionary_id='ielts',
            chapter_number=1,
            practice_count=2
        )
        
        url = reverse('typing-practice-chapter-stats')
        response = authenticated_client.get(url, {'dictionary_id': 'toefl'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        expected_data = {'toefl': {1: 3}}
        assert response.data['data'] == expected_data
    
    @pytest.mark.django_db
    def test_update_chapter_stats(self, authenticated_client, user):
        """测试更新章节练习统计"""
        url = reverse('typing-practice-update-chapter-stats')
        data = {
            'toefl': {1: 3, 2: 1},
            'ielts': {1: 2}
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        
        # 验证数据是否正确保存
        records = ChapterPracticeRecord.objects.filter(user=user)
        assert records.count() == 3
        
        toefl_ch1 = ChapterPracticeRecord.objects.get(
            user=user, dictionary_id='toefl', chapter_number=1
        )
        assert toefl_ch1.practice_count == 3
        
        ielts_ch1 = ChapterPracticeRecord.objects.get(
            user=user, dictionary_id='ielts', chapter_number=1
        )
        assert ielts_ch1.practice_count == 2


class TestWrongWordsAPI:
    """测试错题记录API"""
    
    @pytest.mark.django_db
    def test_get_wrong_words_empty(self, authenticated_client):
        """测试获取空的错题记录"""
        url = reverse('typing-practice-wrong-words')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data'] == []
    
    @pytest.mark.django_db
    def test_get_wrong_words_with_data(self, authenticated_client, user):
        """测试获取有数据的错题记录"""
        # 创建测试数据
        WrongWordRecord.objects.create(
            user=user,
            word='apple',
            translation='苹果',
            dictionary_id='toefl',
            error_count=2
        )
        WrongWordRecord.objects.create(
            user=user,
            word='banana',
            translation='香蕉',
            dictionary_id='ielts',
            error_count=1
        )
        
        url = reverse('typing-practice-wrong-words')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) == 2
        
        # 验证数据格式
        wrong_words = response.data['data']
        assert wrong_words[0]['word'] in ['apple', 'banana']
        assert wrong_words[0]['error_count'] in [1, 2]
    
    @pytest.mark.django_db
    def test_add_wrong_word_new(self, authenticated_client, user):
        """测试添加新的错题记录"""
        url = reverse('typing-practice-add-wrong-word')
        data = {
            'word': 'apple',
            'translation': '苹果',
            'dictionary_id': 'toefl'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['word'] == 'apple'
        assert response.data['data']['error_count'] == 1
        
        # 验证数据库记录
        record = WrongWordRecord.objects.get(user=user, word='apple')
        assert record.translation == '苹果'
        assert record.dictionary_id == 'toefl'
        assert record.error_count == 1
    
    @pytest.mark.django_db
    def test_add_wrong_word_existing(self, authenticated_client, user):
        """测试添加已存在的错题记录"""
        # 创建现有记录
        WrongWordRecord.objects.create(
            user=user,
            word='apple',
            translation='苹果',
            dictionary_id='toefl',
            error_count=1
        )
        
        url = reverse('typing-practice-add-wrong-word')
        data = {
            'word': 'apple',
            'translation': '苹果',
            'dictionary_id': 'toefl'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['error_count'] == 2
        
        # 验证错误次数已增加
        record = WrongWordRecord.objects.get(user=user, word='apple')
        assert record.error_count == 2
    
    @pytest.mark.django_db
    def test_delete_wrong_word(self, authenticated_client, user):
        """测试删除错题记录"""
        # 创建测试记录
        record = WrongWordRecord.objects.create(
            user=user,
            word='apple',
            translation='苹果',
            dictionary_id='toefl',
            error_count=1
        )
        
        url = reverse('typing-practice-delete-wrong-word')
        response = authenticated_client.delete(url, {'id': record.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        
        # 验证记录已删除
        assert not WrongWordRecord.objects.filter(id=record.id).exists()


class TestDailyDurationAPI:
    """测试每日练习时长API"""
    
    @pytest.mark.django_db
    def test_get_daily_duration_empty(self, authenticated_client):
        """测试获取空的每日练习时长"""
        url = reverse('typing-practice-daily-duration')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['total_duration_minutes'] == 0
        assert response.data['data']['session_count'] == 0
    
    @pytest.mark.django_db
    def test_get_daily_duration_with_data(self, authenticated_client, user):
        """测试获取有数据的每日练习时长"""
        # 创建测试数据
        DailyPracticeDuration.objects.create(
            user=user,
            date=date.today(),
            total_duration_minutes=30,
            session_count=2
        )
        
        url = reverse('typing-practice-daily-duration')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['total_duration_minutes'] == 30
        assert response.data['data']['session_count'] == 2
    
    @pytest.mark.django_db
    def test_update_daily_duration_new(self, authenticated_client, user):
        """测试更新新的每日练习时长"""
        url = reverse('typing-practice-update-daily-duration')
        data = {
            'duration_minutes': 15
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['total_duration_minutes'] == 15
        assert response.data['data']['session_count'] == 1
        
        # 验证数据库记录
        record = DailyPracticeDuration.objects.get(user=user, date=date.today())
        assert record.total_duration_minutes == 15
        assert record.session_count == 1
    
    @pytest.mark.django_db
    def test_update_daily_duration_existing(self, authenticated_client, user):
        """测试更新已存在的每日练习时长"""
        # 创建现有记录
        DailyPracticeDuration.objects.create(
            user=user,
            date=date.today(),
            total_duration_minutes=20,
            session_count=1
        )
        
        url = reverse('typing-practice-update-daily-duration')
        data = {
            'duration_minutes': 10
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['total_duration_minutes'] == 30
        assert response.data['data']['session_count'] == 2
        
        # 验证数据已累加
        record = DailyPracticeDuration.objects.get(user=user, date=date.today())
        assert record.total_duration_minutes == 30
        assert record.session_count == 2


class TestAPIErrorHandling:
    """测试API错误处理"""
    
    @pytest.mark.django_db
    def test_add_wrong_word_missing_fields(self, authenticated_client):
        """测试添加错题记录时缺少必要字段"""
        url = reverse('typing-practice-add-wrong-word')
        data = {
            'word': 'apple'
            # 缺少 translation 和 dictionary_id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
    
    @pytest.mark.django_db
    def test_update_chapter_stats_invalid_data(self, authenticated_client):
        """测试更新章节统计时数据格式错误"""
        url = reverse('typing-practice-update-chapter-stats')
        data = "invalid_data"  # 应该是字典
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
    
    @pytest.mark.django_db
    def test_update_daily_duration_missing_fields(self, authenticated_client):
        """测试更新每日时长时缺少必要字段"""
        url = reverse('typing-practice-update-daily-duration')
        data = {}  # 缺少 duration_minutes
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
    
    @pytest.mark.django_db
    def test_delete_wrong_word_missing_id(self, authenticated_client):
        """测试删除错题记录时缺少ID"""
        url = reverse('typing-practice-delete-wrong-word')
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
    
    @pytest.mark.django_db
    def test_delete_wrong_word_not_found(self, authenticated_client):
        """测试删除不存在的错题记录"""
        url = reverse('typing-practice-delete-wrong-word')
        response = authenticated_client.delete(url, {'id': 999})
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['success'] is False 