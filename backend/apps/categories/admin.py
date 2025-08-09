from django.contrib import admin
from .models import Category, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'status', 'order', 'article_count', 'parent', 'created_at'
    )
    list_filter = ('status', 'parent')
    search_fields = ('name', 'slug', 'description')
    ordering = ('-order', 'name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'article_count', 'created_at')
    search_fields = ('name', 'slug', 'description')
    ordering = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20
