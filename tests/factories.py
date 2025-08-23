"""
测试数据工厂
用于生成各种测试数据
"""

import factory
from django.contrib.auth import get_user_model
from apps.english.models import TypingWord, Dictionary, TypingSession, UserTypingStats, Word, Expression, News
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
    
    @factory.post_generation
    def profile(self, create, extracted, **kwargs):
        """禁用自动创建UserProfile"""
        if not create:
            return
        # 不自动创建UserProfile，让测试手动控制


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
    avatar_url = factory.Faker('url')
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


class WordFactory(factory.django.DjangoModelFactory):
    """单词工厂"""
    class Meta:
        model = Word
    
    word = factory.Sequence(lambda n: f'word_{n}')
    phonetic = factory.Sequence(lambda n: f'/word{n}/')
    part_of_speech = factory.Iterator(['noun', 'verb', 'adjective', 'adverb'])
    definition = factory.Faker('text', max_nb_chars=200)
    example = factory.Faker('text', max_nb_chars=300)
    difficulty_level = factory.Iterator(['beginner', 'intermediate', 'advanced'])
    frequency_rank = factory.Faker('random_int', min=1, max=10000)
    category_hint = factory.Faker('word')
    audio_url = factory.Faker('url')
    image_url = factory.Faker('url')
    etymology = factory.Faker('text', max_nb_chars=200)
    synonyms = factory.Faker('text', max_nb_chars=200)
    antonyms = factory.Faker('text', max_nb_chars=200)
    source_url = factory.Faker('url')
    source_api = factory.Faker('word')
    license = factory.Faker('word')
    quality_score = factory.Faker('pydecimal', left_digits=1, right_digits=2, positive=True, min_value=0.0, max_value=1.0)


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


class ExpressionFactory(factory.django.DjangoModelFactory):
    """表达工厂"""
    class Meta:
        model = Expression
    
    expression = factory.Sequence(lambda n: f'expression_{n}')
    meaning = factory.Faker('text', max_nb_chars=200)
    category = factory.Iterator(['idiom', 'phrase', 'collocation'])
    scenario = factory.Iterator(['formal', 'informal', 'business', 'casual'])
    difficulty_level = factory.Iterator(['beginner', 'intermediate', 'advanced'])
    usage_frequency = factory.Iterator(['low', 'medium', 'high'])
    cultural_background = factory.Faker('text', max_nb_chars=200)
    audio_url = factory.Faker('url')
    usage_examples = factory.Faker('text', max_nb_chars=300)
    source_url = factory.Faker('url')
    source_api = factory.Faker('word')
    license = factory.Faker('word')


class NewsFactory(factory.django.DjangoModelFactory):
    """新闻工厂"""
    class Meta:
        model = News
    
    title = factory.Sequence(lambda n: f'News_{n}')
    content = factory.Faker('text', max_nb_chars=2000)
    summary = factory.Faker('text', max_nb_chars=300)
    source = factory.Iterator(['BBC', 'CNN', 'TechCrunch', 'Reuters'])
    url = factory.Faker('url')
    published_date = factory.Faker('date_time_this_year')
    image_url = factory.Faker('url')
    image_alt = factory.Faker('sentence', nb_words=5)
    category = factory.Iterator(['technology', 'business', 'politics', 'sports'])
    difficulty_level = factory.Iterator(['beginner', 'intermediate', 'advanced'])
    reading_time = factory.Faker('random_int', min=1, max=30)
    word_count = factory.Faker('random_int', min=100, max=2000)
    source_url = factory.Faker('url')
    source_api = factory.Faker('word')
    license = factory.Faker('word')


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
    # 修复：使用正确的字段名
    cover_image = factory.Faker('url')  # 修复：应该是cover_image不是featured_image
    views = factory.Faker('random_int', min=0, max=10000)
    likes = factory.Faker('random_int', min=0, max=1000)
    comments_count = factory.Faker('random_int', min=0, max=500)
    
    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """处理多对多字段tags"""
        if not create:
            return
        
        if extracted:
            # 如果提供了tags数据，使用set()方法
            self.tags.set(extracted)
        else:
            # 生成随机tags
            from faker import Faker
            fake = Faker()
            tags = fake.words(nb=3)
            # 这里需要先保存文章，然后设置tags
            # 由于factory的限制，暂时跳过tags设置


class TypingSessionFactory(factory.django.DjangoModelFactory):
    """打字会话工厂"""
    class Meta:
        model = TypingSession
    
    user = factory.SubFactory(UserFactory)
    word = factory.SubFactory(TypingWordFactory)  # 修复：应该是word不是dictionary
    is_correct = factory.Faker('boolean')  # 修复：应该是is_correct
    typing_speed = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True, min_value=10.0, max_value=99.9)  # 修复：应该是typing_speed
    response_time = factory.Faker('pyfloat', left_digits=1, right_digits=2, positive=True, min_value=0.1, max_value=9.99)  # 修复：应该是response_time
    # 修复：移除不存在的字段
    # chapter = factory.Faker('random_int', min=1, max=10)
    # start_time = factory.Faker('date_time_this_month')
    # end_time = factory.Faker('date_time_this_month')
    # total_words = factory.Faker('random_int', min=10, max=100)
    # correct_words = factory.Faker('random_int', min=5, max=95)
    # accuracy = factory.Faker('pydecimal', left_digits=1, right_digits=2, positive=True, min_value=0.01, max_value=0.99)
    # wpm = factory.Faker('pydecimal', left_digits=2, right_digits=1, positive=True, min_value=10.0, max_value=99.9)
    # status = factory.Iterator(['active', 'paused', 'completed', 'abandoned'])


class UserTypingStatsFactory(factory.django.DjangoModelFactory):
    """用户打字统计工厂"""
    class Meta:
        model = UserTypingStats
    
    user = factory.SubFactory(UserFactory)
    # 修复：使用正确的字段名
    total_words_practiced = factory.Faker('random_int', min=1, max=1000)
    total_correct_words = factory.Faker('random_int', min=1, max=1000)
    average_wpm = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True, min_value=10.0, max_value=99.9)
    total_practice_time = factory.Faker('random_int', min=1, max=3600)  # 修复：应该是total_practice_time
    last_practice_date = factory.Faker('date_this_year')
    # 修复：移除不存在的字段
    # date = factory.Faker('date_this_year')
    # total_sessions = factory.Faker('random_int', min=1, max=10)
    # total_words = factory.Faker('random_int', min=1, max=1000)
    # total_correct_words = factory.Faker('random_int', min=1, max=1000)
    # average_accuracy = factory.Faker('pydecimal', left_digits=1, right_digits=2, positive=True, min_value=0.01, max_value=0.99)
    # average_wpm = factory.Faker('pydecimal', left_digits=2, right_digits=1, positive=True, min_value=10.0, max_value=99.9)
    # total_time = factory.Faker('random_int', min=1, max=3600)


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
