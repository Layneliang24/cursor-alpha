#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.articles.models import Article
from django.contrib.auth import get_user_model

User = get_user_model()

print("=== 文章数据检查 ===")
print(f"文章总数: {Article.objects.count()}")
print(f"已发布文章: {Article.objects.filter(status='published').count()}")
print(f"草稿文章: {Article.objects.filter(status='draft').count()}")
print(f"归档文章: {Article.objects.filter(status='archived').count()}")

print("\n=== 最近的文章 ===")
recent_articles = Article.objects.all().order_by('-created_at')[:5]
for article in recent_articles:
    print(f"ID: {article.id}, 标题: {article.title}, 状态: {article.status}, 创建时间: {article.created_at}")

print("\n=== 用户数据检查 ===")
print(f"用户总数: {User.objects.count()}")
users_with_articles = User.objects.filter(articles__isnull=False).distinct()
print(f"有文章的用户数: {users_with_articles.count()}")

print("\n=== 数据库表检查 ===")
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%article%';")
tables = cursor.fetchall()
print(f"文章相关表: {tables}")

# 检查是否有软删除或其他状态
print("\n=== 所有文章状态统计 ===")
from django.db.models import Count
status_counts = Article.objects.values('status').annotate(count=Count('id'))
for item in status_counts:
    print(f"状态 '{item['status']}': {item['count']} 篇")

