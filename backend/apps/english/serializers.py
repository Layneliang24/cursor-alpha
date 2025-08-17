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
    TypingSession,
    UserTypingStats,
    TypingWord,
)


class WordSerializer(serializers.ModelSerializer):
    """单词序列化器"""
    
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


class TypingWordSerializer(serializers.ModelSerializer):
    """打字练习单词序列化器"""
    
    class Meta:
        model = TypingWord
        fields = ['id', 'word', 'translation', 'phonetic', 'difficulty', 'category', 'frequency']


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
    # 格式化发布日期，只显示日期不显示时间
    publish_date = serializers.DateField(format='%Y-%m-%d', read_only=True)
    
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
    class Meta:
        model = PracticeRecord
        fields = [
            'id', 'user', 'content_id', 'content_type', 'practice_type', 
            'question', 'user_answer', 'correct_answer', 'is_correct',
            'score', 'time_spent', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class PronunciationRecordSerializer(serializers.ModelSerializer):
    """发音记录序列化器"""
    class Meta:
        model = PronunciationRecord
        fields = [
            'id', 'user', 'word_id', 'audio_file', 'pronunciation_score', 
            'accuracy_score', 'fluency_score', 'feedback', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


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


class WordExampleSerializer(serializers.ModelSerializer):
    """单词例句序列化器"""
    class Meta:
        model = WordExample
        fields = [
            'id', 'word', 'example', 'translation', 'source',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReviewQuestionSerializer(serializers.ModelSerializer):
    """复习题目序列化器"""
    class Meta:
        model = PracticeRecord
        fields = [
            'id', 'user', 'content_id', 'content_type', 'practice_type', 
            'question', 'user_answer', 'correct_answer', 'is_correct',
            'score', 'time_spent', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class ReviewAnswerSerializer(serializers.Serializer):
    """复习答案序列化器"""
    word_id = serializers.IntegerField()
    practice_type = serializers.CharField()
    is_correct = serializers.BooleanField()
    correct_answer = serializers.CharField()
    time_spent = serializers.IntegerField(min_value=0)


class TypingSessionSerializer(serializers.ModelSerializer):
    """打字练习会话序列化器"""
    word = TypingWordSerializer(read_only=True)
    word_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = TypingSession
        fields = ['id', 'word', 'word_id', 'is_correct', 'typing_speed', 'response_time', 'session_date', 'created_at']
        read_only_fields = ['session_date', 'created_at']


class UserTypingStatsSerializer(serializers.ModelSerializer):
    """用户打字统计序列化器"""
    accuracy = serializers.ReadOnlyField()
    
    class Meta:
        model = UserTypingStats
        fields = [
            'total_words_practiced', 'total_correct_words', 'average_wpm', 
            'total_practice_time', 'last_practice_date', 'accuracy'
        ]
        read_only_fields = fields
