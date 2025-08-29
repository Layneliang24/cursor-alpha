"""
地道表达API序列化器
"""

from rest_framework import serializers
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from apps.english.models import (
    IdiomaticExpression, ExpressionSource, ExpressionScenario, 
    ExpressionScenarioLink, UserExpressionProgress, AIAssistantConfig
)
from django.contrib.auth import get_user_model
import hashlib
import json

User = get_user_model()


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """支持动态字段的基础序列化器"""
    
    def __init__(self, *args, **kwargs):
        # 提取fields参数
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)
        
        super().__init__(*args, **kwargs)
        
        if fields is not None:
            # 只保留指定字段
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        
        if exclude is not None:
            # 排除指定字段
            for field_name in exclude:
                self.fields.pop(field_name, None)


class CachedSerializerMixin:
    """序列化器缓存混入类"""
    
    def get_cache_key(self, obj):
        """生成缓存键"""
        model_name = obj.__class__.__name__.lower()
        obj_id = obj.id
        updated_at = getattr(obj, 'updated_at', None)
        timestamp = updated_at.timestamp() if updated_at else 0
        
        # 包含字段信息在缓存键中
        fields_hash = hashlib.md5(
            json.dumps(list(self.fields.keys()), sort_keys=True).encode()
        ).hexdigest()[:8]
        
        return f"serializer_{model_name}_{obj_id}_{timestamp}_{fields_hash}"
    
    def to_representation(self, instance):
        """带缓存的序列化"""
        if hasattr(self, 'use_cache') and self.use_cache:
            cache_key = self.get_cache_key(instance)
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data
            
            data = super().to_representation(instance)
            
            # 缓存10分钟
            cache.set(cache_key, data, 600)
            return data
        
        return super().to_representation(instance)


class BatchOperationSerializer(serializers.Serializer):
    """批量操作序列化器"""
    
    def validate(self, data):
        """验证批量操作数据"""
        # 注意：这里的data是单个字典，不是列表
        # 列表验证应该在ViewSet中进行
        return data


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


class IdiomaticExpressionListSerializer(DynamicFieldsModelSerializer, CachedSerializerMixin):
    """地道表达列表序列化器（简化版）"""
    scenario_count = serializers.SerializerMethodField()
    use_cache = True  # 启用缓存
    
    class Meta:
        model = IdiomaticExpression
        fields = [
            'id', 'expression', 'meaning', 'expression_type', 
            'formality_level', 'frequency_score', 'scenario_count', 
            'learning_difficulty', 'popularity_score', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_scenario_count(self, obj):
        """获取场景数量（带缓存）"""
        cache_key = f"scenario_count_{obj.id}"
        count = cache.get(cache_key)
        
        if count is None:
            count = obj.scenario_links.count()
            cache.set(cache_key, count, 600)  # 缓存10分钟
        
        return count


class IdiomaticExpressionDetailSerializer(DynamicFieldsModelSerializer, CachedSerializerMixin):
    """地道表达详情序列化器（完整版）"""
    scenarios = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    use_cache = True  # 启用缓存
    
    class Meta:
        model = IdiomaticExpression
        fields = [
            'id', 'expression', 'meaning', 'expression_type', 
            'formality_level', 'frequency_score', 'phonetic_transcription',
            'usage_examples', 'cultural_background', 'metadata',
            'learning_difficulty', 'popularity_score',
            'scenarios', 'user_progress', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_scenarios(self, obj):
        """获取关联场景（带缓存）"""
        cache_key = f"expression_scenarios_{obj.id}"
        scenarios = cache.get(cache_key)
        
        if scenarios is None:
            scenario_links = obj.scenario_links.select_related('scenario').all()
            scenarios = [
                {
                    'id': link.scenario.id,
                    'name': link.scenario.scenario_name,
                    'type': link.scenario.scenario_type,
                    'description': link.scenario.context_description
                }
                for link in scenario_links
            ]
            cache.set(cache_key, scenarios, 600)  # 缓存10分钟
        
        return scenarios
    
    def get_user_progress(self, obj):
        """获取用户学习进度（带缓存）"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            cache_key = f"user_progress_{request.user.id}_{obj.id}"
            progress_data = cache.get(cache_key)
            
            if progress_data is None:
                try:
                    progress = UserExpressionProgress.objects.get(
                        user=request.user,
                        expression=obj
                    )
                    progress_data = {
                        'mastery_level': progress.mastery_level,
                        'last_reviewed': progress.last_reviewed,
                        'review_count': progress.review_count,
                        'is_favorite': progress.is_favorite,
                        'notes': progress.notes
                    }
                    cache.set(cache_key, progress_data, 300)  # 缓存5分钟
                except UserExpressionProgress.DoesNotExist:
                    progress_data = None
                    cache.set(cache_key, progress_data, 60)  # 缓存1分钟
            
            return progress_data
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


class IdiomaticExpressionBatchSerializer(BatchOperationSerializer):
    """地道表达批量操作序列化器"""
    
    def create_batch(self, validated_data):
        """批量创建表达式"""
        expressions = []
        
        with transaction.atomic():
            for item_data in validated_data:
                # 处理场景关联
                scenario_ids = item_data.pop('scenario_ids', [])
                
                # 创建表达式
                expression = IdiomaticExpression.objects.create(**item_data)
                expressions.append(expression)
                
                # 创建场景关联
                if scenario_ids:
                    scenarios = ExpressionScenario.objects.filter(id__in=scenario_ids)
                    for scenario in scenarios:
                        ExpressionScenarioLink.objects.create(
                            expression=expression,
                            scenario=scenario
                        )
        
        return expressions
    
    def update_batch(self, instances, validated_data):
        """批量更新表达式"""
        updated_expressions = []
        
        with transaction.atomic():
            for instance, item_data in zip(instances, validated_data):
                scenario_ids = item_data.pop('scenario_ids', None)
                
                # 更新基本字段
                for attr, value in item_data.items():
                    setattr(instance, attr, value)
                instance.save()
                
                # 更新场景关联
                if scenario_ids is not None:
                    instance.scenario_links.all().delete()
                    scenarios = ExpressionScenario.objects.filter(id__in=scenario_ids)
                    for scenario in scenarios:
                        ExpressionScenarioLink.objects.create(
                            expression=instance,
                            scenario=scenario
                        )
                
                updated_expressions.append(instance)
        
        return updated_expressions


class UserProgressBatchSerializer(BatchOperationSerializer):
    """用户进度批量操作序列化器"""
    
    def update_batch(self, user, progress_updates):
        """批量更新用户学习进度"""
        updated_progress = []
        
        with transaction.atomic():
            for update_data in progress_updates:
                expression_id = update_data.get('expression_id')
                mastery_level = update_data.get('mastery_level')
                is_favorite = update_data.get('is_favorite')
                notes = update_data.get('notes', '')
                
                try:
                    progress = UserExpressionProgress.objects.get(
                        user=user,
                        expression_id=expression_id
                    )
                    
                    # 更新字段
                    if mastery_level is not None:
                        progress.mastery_level = mastery_level
                        progress.last_reviewed = timezone.now()
                        progress.review_count += 1
                    
                    if is_favorite is not None:
                        progress.is_favorite = is_favorite
                    
                    if notes:
                        progress.notes = notes
                    
                    progress.save()
                    updated_progress.append(progress)
                    
                    # 清除相关缓存
                    cache.delete(f"user_progress_{user.id}_{expression_id}")
                    
                except UserExpressionProgress.DoesNotExist:
                    # 如果进度不存在，创建新的
                    if expression_id and mastery_level is not None:
                        try:
                            expression = IdiomaticExpression.objects.get(id=expression_id)
                            progress = UserExpressionProgress.objects.create(
                                user=user,
                                expression=expression,
                                mastery_level=mastery_level,
                                is_favorite=is_favorite or False,
                                notes=notes,
                                review_count=1
                            )
                            updated_progress.append(progress)
                        except IdiomaticExpression.DoesNotExist:
                            continue
        
        return updated_progress


class OptimizedExpressionQueryMixin:
    """优化的表达式查询混入类"""
    
    @classmethod
    def get_optimized_queryset(cls, base_queryset=None):
        """获取优化的查询集"""
        if base_queryset is None:
            base_queryset = IdiomaticExpression.objects.all()
        
        return base_queryset.select_related(
            # 预加载相关数据，减少数据库查询
        ).prefetch_related(
            'scenario_links__scenario',  # 预加载场景数据
            'user_progress_set'  # 预加载用户进度数据
        ).only(
            # 只选择需要的字段，减少数据传输
            'id', 'expression', 'meaning', 'expression_type',
            'formality_level', 'frequency_score', 'phonetic_transcription',
            'usage_examples', 'cultural_background', 'metadata',
            'learning_difficulty', 'popularity_score',
            'created_at', 'updated_at'
        )


class DynamicFieldExpressionSerializer(DynamicFieldsModelSerializer, CachedSerializerMixin, OptimizedExpressionQueryMixin):
    """动态字段表达式序列化器"""
    scenarios = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    use_cache = True
    
    class Meta:
        model = IdiomaticExpression
        fields = [
            'id', 'expression', 'meaning', 'expression_type', 
            'formality_level', 'frequency_score', 'phonetic_transcription',
            'usage_examples', 'cultural_background', 'metadata',
            'learning_difficulty', 'popularity_score',
            'scenarios', 'user_progress', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_scenarios(self, obj):
        """获取关联场景（优化版）"""
        # 如果不需要场景数据，跳过
        if 'scenarios' not in self.fields:
            return []
        
        cache_key = f"expression_scenarios_opt_{obj.id}"
        scenarios = cache.get(cache_key)
        
        if scenarios is None:
            # 使用prefetch_related优化的数据
            scenarios = [
                {
                    'id': link.scenario.id,
                    'name': link.scenario.scenario_name,
                    'type': link.scenario.scenario_type,
                    'description': link.scenario.context_description
                }
                for link in obj.scenario_links.all()
            ]
            cache.set(cache_key, scenarios, 600)
        
        return scenarios
    
    def get_user_progress(self, obj):
        """获取用户学习进度（优化版）"""
        # 如果不需要用户进度，跳过
        if 'user_progress' not in self.fields:
            return None
        
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            cache_key = f"user_progress_opt_{request.user.id}_{obj.id}"
            progress_data = cache.get(cache_key)
            
            if progress_data is None:
                # 尝试从prefetch_related的数据中获取
                user_progress = [
                    p for p in obj.user_progress_set.all() 
                    if p.user_id == request.user.id
                ]
                
                if user_progress:
                    progress = user_progress[0]
                    progress_data = {
                        'mastery_level': progress.mastery_level,
                        'last_reviewed': progress.last_reviewed,
                        'review_count': progress.review_count,
                        'is_favorite': progress.is_favorite,
                        'notes': progress.notes
                    }
                else:
                    progress_data = None
                
                cache.set(cache_key, progress_data, 300)
            
            return progress_data
        return None
