"""
地道表达API序列化器
"""

from rest_framework import serializers
from apps.english.models import (
    IdiomaticExpression, ExpressionSource, ExpressionScenario, 
    ExpressionScenarioLink, UserExpressionProgress, AIAssistantConfig
)
from django.contrib.auth import get_user_model

User = get_user_model()


class ExpressionSourceSerializer(serializers.ModelSerializer):
    """表达式数据源序列化器"""
    
    class Meta:
        model = ExpressionSource
        fields = ['id', 'source_name', 'source_url', 'source_type', 'reliability_score', 'created_at']
        read_only_fields = ['id', 'created_at']


class ExpressionScenarioSerializer(serializers.ModelSerializer):
    """表达式场景序列化器"""
    
    class Meta:
        model = ExpressionScenario
        fields = ['id', 'scenario_name', 'scenario_type', 'context_description', 'example_dialogue', 'created_at']
        read_only_fields = ['id', 'created_at']


class IdiomaticExpressionListSerializer(serializers.ModelSerializer):
    """地道表达列表序列化器（简化版）"""
    scenario_count = serializers.SerializerMethodField()
    
    class Meta:
        model = IdiomaticExpression
        fields = [
            'id', 'expression', 'meaning', 'expression_type', 
            'formality_level', 'frequency_score', 'scenario_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_scenario_count(self, obj):
        """获取场景数量"""
        return obj.scenario_links.count()


class IdiomaticExpressionDetailSerializer(serializers.ModelSerializer):
    """地道表达详情序列化器（完整版）"""
    scenarios = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = IdiomaticExpression
        fields = [
            'id', 'expression', 'meaning', 'expression_type', 
            'formality_level', 'frequency_score', 'phonetic_transcription',
            'usage_examples', 'cultural_background', 'metadata',
            'scenarios', 'user_progress', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_scenarios(self, obj):
        """获取关联场景"""
        scenario_links = obj.scenario_links.select_related('scenario').all()
        return [
            {
                'id': link.scenario.id,
                'name': link.scenario.scenario_name,
                'description': link.scenario.description
            }
            for link in scenario_links
        ]
    
    def get_user_progress(self, obj):
        """获取用户学习进度"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserExpressionProgress.objects.get(
                    user=request.user,
                    expression=obj
                )
                return {
                    'mastery_level': progress.mastery_level,
                    'last_reviewed': progress.last_reviewed,
                    'review_count': progress.review_count,
                    'is_favorite': progress.is_favorite
                }
            except UserExpressionProgress.DoesNotExist:
                pass
        return None


class IdiomaticExpressionCreateSerializer(serializers.ModelSerializer):
    """地道表达创建序列化器"""
    source_id = serializers.IntegerField(write_only=True, required=False)
    scenario_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = IdiomaticExpression
        fields = [
            'expression', 'meaning', 'expression_type', 'formality_level',
            'frequency_score', 'phonetic_transcription', 'usage_examples',
            'cultural_background', 'metadata', 'source_id', 'scenario_ids'
        ]
    
    def validate_expression(self, value):
        """验证表达式"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("表达式长度至少为2个字符")
        return value.strip()
    
    def validate_meaning(self, value):
        """验证含义"""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("含义长度至少为3个字符")
        return value.strip()
    
    def validate_frequency_score(self, value):
        """验证频率分数"""
        if value < 1 or value > 10:
            raise serializers.ValidationError("频率分数必须在1-10之间")
        return value
    
    def create(self, validated_data):
        """创建地道表达"""
        source_id = validated_data.pop('source_id', None)
        scenario_ids = validated_data.pop('scenario_ids', [])
        
        # 设置数据源
        if source_id:
            try:
                source = ExpressionSource.objects.get(id=source_id)
                validated_data['source'] = source
            except ExpressionSource.DoesNotExist:
                raise serializers.ValidationError("指定的数据源不存在")
        
        # 创建表达式
        expression = IdiomaticExpression.objects.create(**validated_data)
        
        # 关联场景
        if scenario_ids:
            scenarios = ExpressionScenario.objects.filter(id__in=scenario_ids)
            for scenario in scenarios:
                ExpressionScenarioLink.objects.create(
                    expression=expression,
                    scenario=scenario
                )
        
        return expression


class IdiomaticExpressionUpdateSerializer(serializers.ModelSerializer):
    """地道表达更新序列化器"""
    scenario_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = IdiomaticExpression
        fields = [
            'expression', 'meaning', 'expression_type', 'formality_level',
            'frequency_score', 'phonetic_transcription', 'usage_examples',
            'cultural_background', 'metadata', 'scenario_ids'
        ]
    
    def validate_expression(self, value):
        """验证表达式"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("表达式长度至少为2个字符")
        return value.strip()
    
    def validate_meaning(self, value):
        """验证含义"""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("含义长度至少为3个字符")
        return value.strip()
    
    def validate_frequency_score(self, value):
        """验证频率分数"""
        if value < 1 or value > 10:
            raise serializers.ValidationError("频率分数必须在1-10之间")
        return value
    
    def update(self, instance, validated_data):
        """更新地道表达"""
        scenario_ids = validated_data.pop('scenario_ids', None)
        
        # 更新基本字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 更新场景关联
        if scenario_ids is not None:
            # 清除现有关联
            instance.scenario_links.all().delete()
            
            # 添加新关联
            scenarios = ExpressionScenario.objects.filter(id__in=scenario_ids)
            for scenario in scenarios:
                ExpressionScenarioLink.objects.create(
                    expression=instance,
                    scenario=scenario
                )
        
        return instance


class UserExpressionProgressSerializer(serializers.ModelSerializer):
    """用户表达式学习进度序列化器"""
    expression = IdiomaticExpressionListSerializer(read_only=True)
    expression_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserExpressionProgress
        fields = [
            'id', 'expression', 'expression_id', 'mastery_level', 
            'last_reviewed', 'review_count', 'is_favorite', 
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_mastery_level(self, value):
        """验证掌握程度"""
        if value < 0 or value > 5:
            raise serializers.ValidationError("掌握程度必须在0-5之间")
        return value
    
    def create(self, validated_data):
        """创建学习进度"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class LearningSessionSerializer(serializers.Serializer):
    """学习会话序列化器"""
    session_type = serializers.ChoiceField(
        choices=['review', 'new', 'random', 'favorite'],
        default='review'
    )
    difficulty_level = serializers.ChoiceField(
        choices=['beginner', 'intermediate', 'advanced', 'all'],
        default='all'
    )
    expression_types = serializers.ListField(
        child=serializers.ChoiceField(
            choices=['idiom', 'slang', 'collocation', 'proverb', 'phrase']
        ),
        required=False,
        allow_empty=True
    )
    scenario_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    limit = serializers.IntegerField(min_value=1, max_value=50, default=10)
    
    def validate(self, data):
        """验证学习会话参数"""
        if data['session_type'] == 'favorite':
            # 收藏学习模式不需要其他筛选条件
            pass
        elif data['session_type'] == 'new':
            # 新表达式学习模式
            if not self.context['request'].user.is_authenticated:
                raise serializers.ValidationError("新表达式学习需要登录")
        
        return data


class AIAssistantConfigSerializer(serializers.ModelSerializer):
    """AI助教配置序列化器"""
    
    class Meta:
        model = AIAssistantConfig
        fields = [
            'id', 'config_name', 'model_provider', 'model_name',
            'api_endpoint', 'max_tokens', 'temperature', 'system_prompt',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_temperature(self, value):
        """验证温度参数"""
        if value < 0 or value > 2:
            raise serializers.ValidationError("温度参数必须在0-2之间")
        return value
    
    def validate_max_tokens(self, value):
        """验证最大token数"""
        if value < 1 or value > 8000:
            raise serializers.ValidationError("最大token数必须在1-8000之间")
        return value


class ExpressionSearchSerializer(serializers.Serializer):
    """表达式搜索序列化器"""
    q = serializers.CharField(required=False, allow_blank=True, max_length=200)
    expression_type = serializers.ChoiceField(
        choices=['idiom', 'slang', 'collocation', 'proverb', 'phrase', ''],
        required=False,
        allow_blank=True
    )
    formality_level = serializers.ChoiceField(
        choices=['formal', 'informal', 'neutral', ''],
        required=False,
        allow_blank=True
    )
    frequency_score_min = serializers.IntegerField(min_value=1, max_value=10, required=False)
    frequency_score_max = serializers.IntegerField(min_value=1, max_value=10, required=False)
    scenario_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    source_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    ordering = serializers.ChoiceField(
        choices=['created_at', '-created_at', 'frequency_score', '-frequency_score', 'expression'],
        default='-created_at'
    )
    
    def validate(self, data):
        """验证搜索参数"""
        freq_min = data.get('frequency_score_min')
        freq_max = data.get('frequency_score_max')
        
        if freq_min and freq_max and freq_min > freq_max:
            raise serializers.ValidationError("最小频率分数不能大于最大频率分数")
        
        return data
