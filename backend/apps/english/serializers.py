from rest_framework import serializers
from .models import (
    Word,
    UserWordProgress,
    Expression,
    News,
    WordExample,
    LearningPlan,
    PracticeRecord,
    PronunciationRecord,
    LearningStats,
)


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = [
            'id', 'word', 'phonetic', 'part_of_speech', 'definition', 'example',
            'difficulty_level', 'frequency_rank', 'category_hint',
            'audio_url', 'image_url', 'etymology', 'synonyms', 'antonyms',
            'source_url', 'source_api', 'license', 'quality_score',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_difficulty_level(self, value: str) -> str:
        allowed = {'beginner', 'intermediate', 'advanced'}
        if value and value not in allowed:
            raise serializers.ValidationError('Invalid difficulty_level')
        return value


class UserWordProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWordProgress
        fields = [
            'id', 'user', 'word', 'status', 'review_count',
            'last_review_date', 'next_review_date', 'mastery_level',
            'ease_factor', 'interval_days', 'repetition_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'review_count', 'last_review_date', 'created_at', 'updated_at']

    def validate_status(self, value: str) -> str:
        allowed = {'not_learned', 'learning', 'mastered', 'need_review'}
        if value not in allowed:
            raise serializers.ValidationError('Invalid status')
        return value

    def validate_mastery_level(self, value):
        if value is None:
            return value
        if value < 0 or value > 1:
            raise serializers.ValidationError('mastery_level must be in [0,1]')
        return value


class ExpressionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expression
        fields = [
            'id', 'expression', 'meaning', 'category', 'scenario',
            'difficulty_level', 'usage_frequency', 'cultural_background',
            'audio_url', 'usage_examples',
            'source_url', 'source_api', 'license', 'quality_score',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = [
            'id', 'title', 'summary', 'content', 'category',
            'difficulty_level', 'publish_date', 'word_count', 'source',
            'reading_time_minutes', 'key_vocabulary', 'comprehension_questions',
            'source_url', 'license', 'quality_score', 'image_url', 'image_alt',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LearningPlanSerializer(serializers.ModelSerializer):
    """学习计划序列化器"""
    class Meta:
        model = LearningPlan
        fields = [
            'id', 'user', 'name', 'description', 'daily_word_target',
            'daily_expression_target', 'review_frequency', 'is_active',
            'start_date', 'end_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_daily_word_target(self, value):
        if value < 1 or value > 100:
            raise serializers.ValidationError('每日单词目标应在1-100之间')
        return value

    def validate_daily_expression_target(self, value):
        if value < 1 or value > 50:
            raise serializers.ValidationError('每日表达目标应在1-50之间')
        return value


class PracticeRecordSerializer(serializers.ModelSerializer):
    """练习记录序列化器"""
    practice_type_display = serializers.CharField(source='get_practice_type_display', read_only=True)
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    
    class Meta:
        model = PracticeRecord
        fields = [
            'id', 'user', 'practice_type', 'practice_type_display',
            'content_id', 'content_type', 'content_type_display',
            'question', 'user_answer', 'correct_answer', 'is_correct',
            'score', 'time_spent', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def validate_score(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError('得分应在0-100之间')
        return value

    def validate_time_spent(self, value):
        if value < 0:
            raise serializers.ValidationError('用时不能为负数')
        return value


class PronunciationRecordSerializer(serializers.ModelSerializer):
    """发音记录序列化器"""
    class Meta:
        model = PronunciationRecord
        fields = [
            'id', 'user', 'word_id', 'audio_file', 'pronunciation_score',
            'accuracy_score', 'fluency_score', 'feedback', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def validate_pronunciation_score(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError('发音得分应在0-100之间')
        return value

    def validate_accuracy_score(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError('准确度得分应在0-100之间')
        return value

    def validate_fluency_score(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError('流利度得分应在0-100之间')
        return value


class LearningStatsSerializer(serializers.ModelSerializer):
    """学习统计序列化器"""
    class Meta:
        model = LearningStats
        fields = [
            'id', 'user', 'date', 'words_learned', 'words_reviewed',
            'expressions_learned', 'news_read', 'practice_count',
            'study_time_minutes', 'accuracy_rate', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def validate_accuracy_rate(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError('正确率应在0-100之间')
        return value


class WordProgressReviewSerializer(serializers.Serializer):
    """单词复习提交序列化器"""
    word_id = serializers.IntegerField()
    quality = serializers.IntegerField(min_value=0, max_value=5)
    time_spent = serializers.IntegerField(min_value=0)

    def validate_quality(self, value):
        """
        验证质量评分
        0: 完全不记得
        1: 错误答案，正确答案似乎很陌生
        2: 错误答案，但正确答案容易记起
        3: 正确答案，但需要努力回忆
        4: 正确答案，经过犹豫后回忆起
        5: 完美答案
        """
        if value not in range(6):
            raise serializers.ValidationError('质量评分必须在0-5之间')
        return value


class LearningOverviewSerializer(serializers.Serializer):
    """学习概览序列化器"""
    period = serializers.CharField()
    total_stats = serializers.DictField()
    mastery_stats = serializers.DictField()
    daily_data = serializers.ListField()


class PracticeQuestionSerializer(serializers.Serializer):
    """练习题目序列化器"""
    type = serializers.CharField()
    question = serializers.CharField()
    correct_answer = serializers.CharField()
    word_id = serializers.IntegerField(required=False)
    options = serializers.ListField(required=False)


class PracticeSubmissionSerializer(serializers.Serializer):
    """练习提交序列化器"""
    practice_type = serializers.CharField()
    content_id = serializers.IntegerField()
    content_type = serializers.CharField()
    question = serializers.CharField()
    user_answer = serializers.CharField()
    correct_answer = serializers.CharField()
    time_spent = serializers.IntegerField(min_value=0)
