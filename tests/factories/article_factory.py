import factory
from apps.articles.models import Article
from .user_factory import UserFactory
from .category_factory import CategoryFactory

class ArticleFactory(factory.django.DjangoModelFactory):
    """文章测试数据工厂"""
    
    class Meta:
        model = Article
    
    title = factory.Faker('sentence')
    content = factory.Faker('text', max_nb_chars=1000)
    summary = factory.Faker('text', max_nb_chars=200)
    author = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    status = 'published'
    featured = False
    views = factory.Faker('random_int', min=0, max=1000)
    likes = factory.Faker('random_int', min=0, max=100)
    comments_count = factory.Faker('random_int', min=0, max=50)

class DraftArticleFactory(ArticleFactory):
    """草稿文章工厂"""
    status = 'draft'

class FeaturedArticleFactory(ArticleFactory):
    """推荐文章工厂"""
    featured = True
