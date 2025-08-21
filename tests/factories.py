"""
测试数据工厂
用于生成各种测试数据
"""

import factory
from django.contrib.auth import get_user_model
from apps.english.models import TypingWord, Dictionary, TypingSession, UserTypingStats
from apps.articles.models import Article
from apps.categories.models import Category
from apps.users.models import UserProfile

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """用户工厂"""
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.Sequence(lambda n: f'user_{n}@test.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    bio = factory.Faker('text', max_nb_chars=200)
    website = factory.Faker('url')


class UserProfileFactory(factory.django.DjangoModelFactory):
    """用户档案工厂"""
    class Meta:
        model = UserProfile
    
    user = factory.SubFactory(UserFactory)
    phone = factory.Faker('phone_number')
    location = factory.Faker('city')
    company = factory.Faker('company')
    position = factory.Faker('job')
    skills = factory.Faker('text', max_nb_chars=300)
    github = factory.Faker('url')
    linkedin = factory.Faker('url')
    twitter = factory.Faker('url')
    
    @factory.post_generation
    def create_profile(self, create, extracted, **kwargs):
        """确保用户档案不会重复创建"""
        if not create:
            return
        # 如果用户已经有档案，不重复创建
        if hasattr(self.user, 'profile'):
            return


class CategoryFactory(factory.django.DjangoModelFactory):
    """分类工厂"""
    class Meta:
        model = Category
    
    name = factory.Sequence(lambda n: f'Category_{n}')
    description = factory.Faker('text', max_nb_chars=200)


class DictionaryFactory(factory.django.DjangoModelFactory):
    """词典工厂"""
    class Meta:
        model = Dictionary
    
    name = factory.Sequence(lambda n: f'Dictionary_{n}')
    description = factory.Faker('text', max_nb_chars=300)
    category = factory.Faker('word')
    language = factory.Iterator(['en', 'zh', 'es', 'fr'])
    total_words = factory.Faker('random_int', min=10, max=1000)
    chapter_count = factory.Faker('random_int', min=1, max=20)


class TypingWordFactory(factory.django.DjangoModelFactory):
    """打字单词工厂"""
    class Meta:
        model = TypingWord
    
    word = factory.Sequence(lambda n: f'word_{n}')
    translation = factory.Sequence(lambda n: f'翻译_{n}')
    phonetic = factory.Sequence(lambda n: f'/word{n}/')
    difficulty = factory.Iterator(['beginner', 'intermediate', 'advanced'])
    dictionary = factory.SubFactory(DictionaryFactory)
    chapter = factory.Faker('random_int', min=1, max=10)
    frequency = factory.Faker('random_int', min=1, max=1000)


class ArticleFactory(factory.django.DjangoModelFactory):
    """文章工厂"""
    class Meta:
        model = Article
    
    title = factory.Sequence(lambda n: f'Article_{n}')
    content = factory.Faker('text', max_nb_chars=2000)
    summary = factory.Faker('text', max_nb_chars=300)
    category = factory.SubFactory(CategoryFactory)
    author = factory.SubFactory(UserFactory)
    status = factory.Iterator(['draft', 'published', 'archived'])


class TypingSessionFactory(factory.django.DjangoModelFactory):
    """打字练习会话工厂"""
    class Meta:
        model = TypingSession
    
    user = factory.SubFactory(UserFactory)
    word = factory.SubFactory(TypingWordFactory)
    is_correct = factory.Faker('boolean')
    typing_speed = factory.Faker('random_int', min=10, max=200)
    response_time = factory.Faker('pyfloat', min_value=0.1, max_value=10.0)


class UserTypingStatsFactory(factory.django.DjangoModelFactory):
    """用户打字统计工厂"""
    class Meta:
        model = UserTypingStats
    
    user = factory.SubFactory(UserFactory)
    total_words_practiced = factory.Faker('random_int', min=0, max=1000)
    total_correct_words = factory.Faker('random_int', min=0, max=1000)
    total_practice_time = factory.Faker('random_int', min=0, max=3600)
    last_practice_date = factory.Faker('date_time_this_year')


# 批量创建工厂
class BatchDataFactory:
    """批量数据工厂"""
    
    @staticmethod
    def create_users(count=10):
        """批量创建用户"""
        return UserFactory.create_batch(count)
    
    @staticmethod
    def create_typing_words(count=50, dictionary=None):
        """批量创建打字单词"""
        if not dictionary:
            dictionary = DictionaryFactory()
        return TypingWordFactory.create_batch(count, dictionary=dictionary)
    
    @staticmethod
    def create_articles(count=20, author=None):
        """批量创建文章"""
        if not author:
            author = UserFactory()
        return ArticleFactory.create_batch(count, author=author)
    
    @staticmethod
    def create_typing_sessions(count=100, user=None, word=None):
        """批量创建打字练习会话"""
        if not user:
            user = UserFactory()
        if not word:
            word = TypingWordFactory()
        return TypingSessionFactory.create_batch(count, user=user, word=word)
    
    @staticmethod
    def create_complete_test_data():
        """创建完整的测试数据集"""
        # 创建基础数据
        users = UserFactory.create_batch(5)
        categories = CategoryFactory.create_batch(3)
        dictionaries = DictionaryFactory.create_batch(2)
        
        # 创建单词
        words = []
        for dictionary in dictionaries:
            words.extend(TypingWordFactory.create_batch(25, dictionary=dictionary))
        
        # 创建文章
        articles = []
        for category in categories:
            for user in users[:2]:  # 前两个用户创建文章
                articles.extend(ArticleFactory.create_batch(3, category=category, author=user))
        
        # 创建练习记录
        sessions = []
        for user in users:
            for word in words[:10]:  # 每个用户练习前10个单词
                sessions.extend(TypingSessionFactory.create_batch(2, user=user, word=word))
        
        return {
            'users': users,
            'categories': categories,
            'dictionaries': dictionaries,
            'words': words,
            'articles': articles,
            'sessions': sessions
        }
