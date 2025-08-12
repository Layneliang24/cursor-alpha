from django.contrib import admin
from .models import (
    Word, UserWordProgress, Expression, News,
    LearningPlan, PracticeRecord, PronunciationRecord, LearningStats,
    WordCategory, WordCategoryLink, WordTag, WordTagLink,
    WordExample, WordRelation, EntityVersion
)


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['word', 'phonetic', 'part_of_speech', 'difficulty_level', 'frequency_rank', 'quality_score', 'created_at']
    list_filter = ['difficulty_level', 'part_of_speech', 'created_at']
    search_fields = ['word', 'definition', 'example']
    ordering = ['word']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('word', 'phonetic', 'part_of_speech', 'definition', 'example')
        }),
        ('分类与难度', {
            'fields': ('difficulty_level', 'frequency_rank', 'category_hint')
        }),
        ('多媒体', {
            'fields': ('audio_url', 'image_url', 'etymology', 'synonyms', 'antonyms')
        }),
        ('来源信息', {
            'fields': ('source_url', 'source_api', 'license', 'quality_score')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(UserWordProgress)
class UserWordProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'word', 'status', 'mastery_level', 'review_count', 'next_review_date']
    list_filter = ['status', 'created_at', 'next_review_date']
    search_fields = ['user__username', 'word__word']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'word', 'status', 'mastery_level')
        }),
        ('复习信息', {
            'fields': ('review_count', 'last_review_date', 'next_review_date')
        }),
        ('SM-2算法', {
            'fields': ('ease_factor', 'interval_days', 'repetition_count')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Expression)
class ExpressionAdmin(admin.ModelAdmin):
    list_display = ['expression', 'meaning', 'category', 'scenario', 'difficulty_level', 'usage_frequency']
    list_filter = ['difficulty_level', 'usage_frequency', 'category', 'scenario']
    search_fields = ['expression', 'meaning']
    ordering = ['expression']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'category', 'difficulty_level', 'publish_date', 'word_count']
    list_filter = ['source', 'category', 'difficulty_level', 'publish_date']
    search_fields = ['title', 'summary', 'content']
    ordering = ['-publish_date']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'summary', 'content')
        }),
        ('分类与属性', {
            'fields': ('source', 'category', 'difficulty_level', 'publish_date', 'word_count')
        }),
        ('学习增强', {
            'fields': ('reading_time_minutes', 'key_vocabulary', 'comprehension_questions')
        }),
        ('来源信息', {
            'fields': ('source_url', 'license', 'quality_score')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(LearningPlan)
class LearningPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'daily_word_target', 'daily_expression_target', 'is_active', 'start_date']
    list_filter = ['is_active', 'review_frequency', 'start_date']
    search_fields = ['user__username', 'name', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PracticeRecord)
class PracticeRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'practice_type', 'content_type', 'is_correct', 'score', 'time_spent', 'created_at']
    list_filter = ['practice_type', 'content_type', 'is_correct', 'created_at']
    search_fields = ['user__username', 'question', 'user_answer']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(PronunciationRecord)
class PronunciationRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'word_id', 'pronunciation_score', 'accuracy_score', 'fluency_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(LearningStats)
class LearningStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'words_learned', 'words_reviewed', 'practice_count', 'accuracy_rate']
    list_filter = ['date']
    search_fields = ['user__username']
    ordering = ['-date']
    readonly_fields = ['created_at']


@admin.register(WordCategory)
class WordCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(WordTag)
class WordTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(WordExample)
class WordExampleAdmin(admin.ModelAdmin):
    list_display = ['word', 'sentence', 'quality_score', 'created_at']
    list_filter = ['quality_score', 'created_at']
    search_fields = ['word__word', 'sentence', 'translation']
    ordering = ['-quality_score']


@admin.register(WordRelation)
class WordRelationAdmin(admin.ModelAdmin):
    list_display = ['word', 'related_word', 'relation_type', 'created_at']
    list_filter = ['relation_type', 'created_at']
    search_fields = ['word__word', 'related_word__word']
    ordering = ['word']


@admin.register(EntityVersion)
class EntityVersionAdmin(admin.ModelAdmin):
    list_display = ['entity_type', 'entity_id', 'changed_by', 'created_at']
    list_filter = ['entity_type', 'created_at']
    search_fields = ['entity_type', 'changed_by__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


# 内联管理
class WordCategoryLinkInline(admin.TabularInline):
    model = WordCategoryLink
    extra = 1


class WordTagLinkInline(admin.TabularInline):
    model = WordTagLink
    extra = 1


class WordExampleInline(admin.TabularInline):
    model = WordExample
    extra = 1
    fields = ['sentence', 'translation', 'quality_score']


class WordRelationInline(admin.TabularInline):
    model = WordRelation
    fk_name = 'word'
    extra = 1
    fields = ['related_word', 'relation_type', 'note']


# 将内联添加到Word管理页面
WordAdmin.inlines = [WordCategoryLinkInline, WordTagLinkInline, WordExampleInline, WordRelationInline]
