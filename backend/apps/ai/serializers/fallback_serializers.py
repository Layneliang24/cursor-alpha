"""
故障转移策略序列化器
"""

from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from ..models import FailoverStrategy, FailoverRule, AIProvider, AIModel


class FailoverRuleSerializer(serializers.ModelSerializer):
    """故障转移规则序列化器"""
    
    fallback_provider_name = serializers.CharField(source='fallback_provider.display_name', read_only=True)
    fallback_model_name = serializers.CharField(source='fallback_model.model_name', read_only=True)
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = FailoverRule
        fields = [
            'id', 'priority', 'fallback_provider', 'fallback_provider_name',
            'fallback_model', 'fallback_model_name', 'trigger_errors',
            'is_active', 'trigger_count', 'success_count', 'success_rate',
            'last_triggered', 'created_at', 'updated_at'
        ]
        read_only_fields = ['trigger_count', 'success_count', 'last_triggered']
    
    def get_success_rate(self, obj):
        """获取成功率"""
        if obj.trigger_count == 0:
            return 0.0
        return round((obj.success_count / obj.trigger_count) * 100, 2)
    
    def validate(self, attrs):
        """验证规则数据"""
        fallback_provider = attrs.get('fallback_provider')
        fallback_model = attrs.get('fallback_model')
        
        # 验证模型是否属于提供商
        if fallback_provider and fallback_model:
            if fallback_model.provider != fallback_provider:
                raise serializers.ValidationError(
                    f"模型 {fallback_model.model_name} 不属于提供商 {fallback_provider.display_name}"
                )
        
        return attrs


class FailoverStrategyListSerializer(serializers.ModelSerializer):
    """故障转移策略列表序列化器（简化版本）"""
    
    primary_provider_name = serializers.CharField(source='primary_provider.display_name', read_only=True)
    primary_model_name = serializers.CharField(source='primary_model.model_name', read_only=True)
    rule_count = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    fallback_rate = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = FailoverStrategy
        fields = [
            'id', 'name', 'description', 'primary_provider_name', 
            'primary_model_name', 'is_active', 'is_default', 'status',
            'rule_count', 'success_rate', 'fallback_rate', 
            'total_requests', 'last_used', 'created_at'
        ]
    
    def get_rule_count(self, obj):
        """获取规则数量"""
        return obj.rules.filter(is_active=True).count()
    
    def get_success_rate(self, obj):
        """获取成功率"""
        return round(obj.get_success_rate() * 100, 2)
    
    def get_fallback_rate(self, obj):
        """获取故障转移率"""
        return round(obj.get_fallback_rate() * 100, 2)
    
    def get_status(self, obj):
        """获取策略状态"""
        if not obj.is_active:
            return 'inactive'
        
        # 检查主提供商健康状态
        if not obj.primary_provider.is_healthy:
            return 'degraded'
        
        # 检查是否有可用的备用规则
        active_rules = obj.rules.filter(is_active=True).count()
        if active_rules == 0:
            return 'no_fallback'
        
        return 'healthy'


class FailoverStrategyDetailSerializer(serializers.ModelSerializer):
    """故障转移策略详细序列化器"""
    
    primary_provider_name = serializers.CharField(source='primary_provider.display_name', read_only=True)
    primary_model_name = serializers.CharField(source='primary_model.model_name', read_only=True)
    rules = FailoverRuleSerializer(many=True, read_only=True)
    success_rate = serializers.SerializerMethodField()
    fallback_rate = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    available_providers = serializers.SerializerMethodField()
    
    class Meta:
        model = FailoverStrategy
        fields = [
            'id', 'name', 'description', 'primary_provider', 'primary_provider_name',
            'primary_model', 'primary_model_name', 'max_retries', 'retry_delay',
            'timeout_threshold', 'error_rate_threshold', 'is_active', 'is_default',
            'total_requests', 'successful_requests', 'fallback_count',
            'success_rate', 'fallback_rate', 'status', 'rules', 'available_providers',
            'last_used', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_requests', 'successful_requests', 'fallback_count', 'last_used']
    
    def get_success_rate(self, obj):
        """获取成功率"""
        return round(obj.get_success_rate() * 100, 2)
    
    def get_fallback_rate(self, obj):
        """获取故障转移率"""
        return round(obj.get_fallback_rate() * 100, 2)
    
    def get_status(self, obj):
        """获取策略状态"""
        if not obj.is_active:
            return {
                'status': 'inactive',
                'message': '策略已禁用'
            }
        
        # 检查主提供商健康状态
        if not obj.primary_provider.is_healthy:
            return {
                'status': 'degraded',
                'message': f'主提供商 {obj.primary_provider.display_name} 不健康'
            }
        
        # 检查是否有可用的备用规则
        active_rules = obj.rules.filter(is_active=True)
        if not active_rules.exists():
            return {
                'status': 'no_fallback',
                'message': '没有可用的备用规则'
            }
        
        # 检查备用提供商健康状态
        unhealthy_providers = []
        for rule in active_rules:
            if not rule.fallback_provider.is_healthy:
                unhealthy_providers.append(rule.fallback_provider.display_name)
        
        if unhealthy_providers:
            return {
                'status': 'partial_fallback',
                'message': f'部分备用提供商不健康: {", ".join(unhealthy_providers)}'
            }
        
        return {
            'status': 'healthy',
            'message': '策略运行正常'
        }
    
    def get_available_providers(self, obj):
        """获取可用的提供商列表"""
        # 获取所有活跃的提供商
        all_providers = AIProvider.objects.filter(is_active=True)
        
        # 排除已经是主提供商的
        available = all_providers.exclude(id=obj.primary_provider.id)
        
        return [
            {
                'id': p.id,
                'name': p.display_name,
                'provider_type': p.provider_type,
                'is_healthy': p.is_healthy,
                'models': [
                    {'id': m.id, 'name': m.model_name, 'is_active': m.is_active}
                    for m in p.models.filter(is_active=True)
                ]
            }
            for p in available
        ]


class FailoverStrategyCreateUpdateSerializer(serializers.ModelSerializer):
    """故障转移策略创建/更新序列化器"""
    
    rules_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="故障转移规则列表"
    )
    
    class Meta:
        model = FailoverStrategy
        fields = [
            'name', 'description', 'primary_provider', 'primary_model',
            'max_retries', 'retry_delay', 'timeout_threshold', 'error_rate_threshold',
            'is_active', 'is_default', 'rules_data'
        ]
    
    def validate_primary_model(self, value):
        """验证主模型"""
        primary_provider = self.initial_data.get('primary_provider')
        if primary_provider and value.provider_id != int(primary_provider):
            raise serializers.ValidationError(
                f"模型 {value.model_name} 不属于选择的主提供商"
            )
        return value
    
    def validate_rules_data(self, value):
        """验证规则数据"""
        if not value:
            return value
        
        priorities = []
        for rule_data in value:
            priority = rule_data.get('priority')
            if priority in priorities:
                raise serializers.ValidationError(f"优先级 {priority} 重复")
            priorities.append(priority)
            
            # 验证必需字段
            required_fields = ['priority', 'fallback_provider', 'fallback_model']
            for field in required_fields:
                if field not in rule_data:
                    raise serializers.ValidationError(f"规则缺少必需字段: {field}")
            
            # 验证提供商和模型匹配
            try:
                provider = AIProvider.objects.get(id=rule_data['fallback_provider'])
                model = AIModel.objects.get(id=rule_data['fallback_model'])
                if model.provider != provider:
                    raise serializers.ValidationError(
                        f"模型 {model.model_name} 不属于提供商 {provider.display_name}"
                    )
            except (AIProvider.DoesNotExist, AIModel.DoesNotExist) as e:
                raise serializers.ValidationError(f"无效的提供商或模型ID: {e}")
        
        return value
    
    def validate(self, attrs):
        """验证整体数据"""
        # 检查是否设置为默认策略
        if attrs.get('is_default', False):
            user = self.context['request'].user
            # 检查是否已有默认策略
            existing_default = FailoverStrategy.objects.filter(
                user=user, 
                is_default=True
            ).exclude(id=self.instance.id if self.instance else None)
            
            if existing_default.exists():
                raise serializers.ValidationError(
                    "已存在默认策略，请先取消其他策略的默认设置"
                )
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """创建故障转移策略"""
        rules_data = validated_data.pop('rules_data', [])
        user = self.context['request'].user
        
        # 创建策略
        strategy = FailoverStrategy.objects.create(
            user=user,
            **validated_data
        )
        
        # 创建规则
        self._create_rules(strategy, rules_data)
        
        return strategy
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """更新故障转移策略"""
        rules_data = validated_data.pop('rules_data', None)
        
        # 更新策略基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 更新规则
        if rules_data is not None:
            # 删除现有规则
            instance.rules.all().delete()
            # 创建新规则
            self._create_rules(instance, rules_data)
        
        return instance
    
    def _create_rules(self, strategy, rules_data):
        """创建故障转移规则"""
        for rule_data in rules_data:
            FailoverRule.objects.create(
                strategy=strategy,
                priority=rule_data['priority'],
                fallback_provider_id=rule_data['fallback_provider'],
                fallback_model_id=rule_data['fallback_model'],
                trigger_errors=rule_data.get('trigger_errors', []),
                is_active=rule_data.get('is_active', True)
            )


class FailoverSwitchSerializer(serializers.Serializer):
    """手动切换序列化器"""
    
    target_provider_id = serializers.IntegerField(
        required=False,
        help_text="目标提供商ID，如果不指定则自动选择下一个可用提供商"
    )
    reason = serializers.CharField(
        max_length=500,
        help_text="切换原因"
    )
    dry_run = serializers.BooleanField(
        default=False,
        help_text="是否为试运行（不实际执行切换）"
    )
    
    def validate_target_provider_id(self, value):
        """验证目标提供商"""
        if value:
            try:
                provider = AIProvider.objects.get(id=value, is_active=True)
                return provider
            except AIProvider.DoesNotExist:
                raise serializers.ValidationError("指定的提供商不存在或未启用")
        return None
    
    def validate(self, attrs):
        """验证切换数据"""
        strategy = self.context.get('strategy')
        target_provider = attrs.get('target_provider_id')
        
        if target_provider and strategy:
            # 检查目标提供商是否在故障转移规则中
            if not strategy.rules.filter(
                fallback_provider=target_provider,
                is_active=True
            ).exists():
                raise serializers.ValidationError(
                    f"提供商 {target_provider.display_name} 不在当前策略的备用列表中"
                )
        
        return attrs


class ProviderHealthSerializer(serializers.Serializer):
    """提供商健康状态序列化器"""
    
    provider_id = serializers.CharField()
    provider_name = serializers.CharField()
    status = serializers.CharField()
    is_healthy = serializers.BooleanField()
    avg_response_time = serializers.FloatField(allow_null=True)
    success_rate = serializers.FloatField(allow_null=True)
    last_health_check = serializers.DateTimeField(allow_null=True)
    error_message = serializers.CharField(allow_null=True)
    
    def to_representation(self, instance):
        """自定义序列化输出"""
        if isinstance(instance, AIProvider):
            return {
                'provider_id': str(instance.id),
                'provider_name': instance.display_name,
                'status': 'healthy' if instance.is_healthy else 'unhealthy',
                'is_healthy': instance.is_healthy,
                'avg_response_time': instance.avg_response_time,
                'success_rate': instance.success_rate,
                'last_health_check': instance.last_health_check,
                'error_message': None
            }
        return super().to_representation(instance)
