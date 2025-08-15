import factory
from apps.categories.models import Category, Tag

class CategoryFactory(factory.django.DjangoModelFactory):
    """分类测试数据工厂"""
    
    class Meta:
        model = Category
    
    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=200)
    status = 'active'
    order = factory.Faker('random_int', min=0, max=100)
    color = factory.Faker('hex_color')

class TagFactory(factory.django.DjangoModelFactory):
    """标签测试数据工厂"""
    
    class Meta:
        model = Tag
    
    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=100)
    color = factory.Faker('hex_color')
