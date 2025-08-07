#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.categories.models import Category, Tag
from apps.articles.models import Article

User = get_user_model()

def create_test_data():
    print("创建测试数据...")
    
    # 创建测试用户
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@alpha.com',
            'first_name': '测试',
            'last_name': '用户'
        }
    )
    if created:
        user.set_password('test123')
        user.save()
        print("✅ 创建测试用户")
    
    # 创建分类
    category, created = Category.objects.get_or_create(
        name='技术分享',
        defaults={'slug': 'tech', 'description': '技术相关文章'}
    )
    if created:
        print("✅ 创建分类")
    
    # 创建标签
    tag, created = Tag.objects.get_or_create(
        name='Python',
        defaults={'slug': 'python'}
    )
    if created:
        print("✅ 创建标签")
    
    # 创建测试文章
    article, created = Article.objects.get_or_create(
        title='Django REST Framework 入门指南',
        defaults={
            'content': '这是一个关于DRF的入门指南...',
            'summary': 'DRF入门教程',
            'author': user,
            'category': category,
            'status': 'published'
        }
    )
    if created:
        article.tags.add(tag)
        print("✅ 创建测试文章")
    
    print("🎉 测试数据创建完成！")

if __name__ == '__main__':
    create_test_data() 