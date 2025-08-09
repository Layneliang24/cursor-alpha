from django.contrib import admin
from .models import Article, Comment, Like, Bookmark


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'category', 'author', 'status', 'featured', 'views', 'likes', 'comments_count', 'created_at'
    )
    list_filter = ('status', 'featured', 'category', 'tags')
    search_fields = ('title', 'summary', 'content')
    autocomplete_fields = ('author', 'category', 'tags')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 20


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'author', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    search_fields = ('content', 'author__username', 'article__title')
    autocomplete_fields = ('article', 'author', 'parent')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 20


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'article', 'created_at')
    search_fields = ('user__username', 'article__title')
    autocomplete_fields = ('user', 'article')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 20


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'article', 'created_at')
    search_fields = ('user__username', 'article__title')
    autocomplete_fields = ('user', 'article')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 20
