#!/usr/bin/env python
"""
统一的文章创建脚本
包含前端开发、后端开发等多个分类的技术文章
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.articles.models import Article
from apps.categories.models import Category
from apps.users.models import User

def create_all_articles():
    """创建所有技术文章"""
    categories = list(Category.objects.all())
    users = list(User.objects.all())
    
    if not categories or not users:
        print("请先创建分类和用户")
        return
    
    print(f"找到 {len(categories)} 个分类，{len(users)} 个用户")
    
    # 从其他脚本导入文章数据
    try:
        from create_detailed_articles import tech_articles as frontend_articles
        from create_backend_articles import backend_articles
        
        all_articles = frontend_articles + backend_articles
        
        created_count = 0
        for article_data in all_articles:
            if Article.objects.filter(title=article_data['title']).exists():
                print(f"文章已存在: {article_data['title']}")
                continue
            
            # 查找对应分类
            category = None
            for cat in categories:
                if cat.name == article_data['category']:
                    category = cat
                    break
            
            if not category:
                category = random.choice(categories)
            
            author = random.choice(users)
            created_at = datetime.now() - timedelta(days=random.randint(1, 30))
            
            article = Article.objects.create(
                title=article_data['title'],
                content=article_data['content'],
                summary=article_data['summary'],
                author=author,
                category=category,
                status='published',
                featured=random.choice([True, False]),
                views=random.randint(100, 1000),
                likes=random.randint(10, 100),
                created_at=created_at,
                updated_at=created_at
            )
            
            created_count += 1
            print(f"创建文章: {article.title}")
        
        print(f"\n总共创建了 {created_count} 篇技术文章")
        
    except ImportError as e:
        print(f"导入文章数据失败: {e}")

if __name__ == '__main__':
    create_all_articles()