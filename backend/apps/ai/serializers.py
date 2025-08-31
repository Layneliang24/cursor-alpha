"""
AI配置管理序列化器
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .config_models import (
    AIProvider, APIKey, AIModel, ModelConfig, TokenUsage,
    FailoverStrategy, FailoverRule, UsageQuota
)

User = get_user_model()


class AIProviderSerializer(serializers.ModelSerializer):
    """AI提供商序列化器"""
    
    class Meta:
        model = AIProvider
        fields = [
            'id', 'name', 'provider_type', 'display_name', 'description',
            'base_url', 'api_version', 'is_active', 'is_healthy',
            'last_health_check', 'avg_response_time', 'success_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_healthy', 'last_health_check', 'avg_response_time', 'success_rate', 'created_at', 'updated_at']


class APIKeySerializer(serializers.ModelSerializer):
    """API密钥序列化器（安全显示）"""
    
    # 使用masked_key属性进行安全显示
    masked_key = serializers.ReadOnlyField()
    provider_name = serializers.CharField(source='provider.display_name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'key_id', 'masked_key', 'key_prefix',
            'provider', 'provider_name', 'user', 'user_name',
            'is_active', 'is_default', 'is_expired',
            'usage_limit_daily', 'usage_limit_monthly',
            'created_at', 'updated_at', 'last_used', 'expires_at'
        ]
        read_only_fields = [
            'id', 'key_id', 'masked_key', 'key_prefix', 'provider_name', 
            'user_name', 'is_expired', 'created_at', 'updated_at', 'last_used'
        ]
        # 确保encrypted_key永远不在序列化中暴露
        extra_kwargs = {
            'encrypted_key': {'write_only': True},
        }
    
    def get_is_expired(self, obj):
        """获取密钥是否过期"""
        return obj.is_expired()
    
    def create(self, validated_data):
        """创建新的API密钥"""
        # 从请求中获取原始密钥
        raw_key = self.context['request'].data.get('raw_key')
        if not raw_key:
            raise serializers.ValidationError({'raw_key': '必须提供API密钥'})
        
        # 创建密钥对象
        api_key = APIKey.objects.create(**validated_data)
        
        # 设置加密密钥
        api_key.set_key(raw_key)
        api_key.save()
        
        return api_key
    
    def update(self, instance, validated_data):
        """更新API密钥"""
        # 检查是否需要更新密钥
        raw_key = self.context['request'].data.get('raw_key')
        if raw_key:
            instance.set_key(raw_key)
        
        # 更新其他字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class APIKeyCreateSerializer(serializers.Serializer):
    """API密钥创建序列化器"""
    
    name = serializers.CharField(max_length=100)
    provider = serializers.PrimaryKeyRelatedField(queryset=AIProvider.objects.all())
    raw_key = serializers.CharField(max_length=500, write_only=True)
    is_default = serializers.BooleanField(default=False)
    usage_limit_daily = serializers.IntegerField(required=False, allow_null=True)
    usage_limit_monthly = serializers.IntegerField(required=False, allow_null=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    
    def create(self, validated_data):
        """创建API密钥"""
        raw_key = validated_data.pop('raw_key')
        user = self.context['request'].user
        
        # 创建密钥对象
        api_key = APIKey.objects.create(user=user, **validated_data)
        
        # 设置加密密钥
        api_key.set_key(raw_key)
        api_key.save()
        
        return api_key


class AIModelSerializer(serializers.ModelSerializer):
    """AI模型序列化器"""
    
    provider_name = serializers.CharField(source='provider.display_name', read_only=True)
    
    class Meta:
        model = AIModel
        fields = [
            'id', 'provider', 'provider_name', 'model_id', 'display_name', 
            'description', 'max_tokens', 'supports_streaming', 'supports_functions',
            'supports_vision', 'cost_per_1k_input_tokens', 'cost_per_1k_output_tokens',
            'is_active', 'is_recommended', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'provider_name', 'created_at', 'updated_at']


class ModelConfigSerializer(serializers.ModelSerializer):
    """模型配置序列化器"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    model_display_name = serializers.CharField(source='model.display_name', read_only=True)
    
    class Meta:
        model = ModelConfig
        fields = [
            'id', 'user', 'user_name', 'model', 'model_display_name',
            'config_name', 'temperature', 'max_tokens', 'top_p', 'top_k',
            'presence_penalty', 'frequency_penalty', 'custom_parameters',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_name', 'model_display_name', 'created_at', 'updated_at']


class TokenUsageSerializer(serializers.ModelSerializer):
    """Token使用统计序列化器"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    model_display_name = serializers.CharField(source='model.display_name', read_only=True)
    
    class Meta:
        model = TokenUsage
        fields = [
            'id', 'user', 'user_name', 'model', 'model_display_name',
            'request_id', 'input_tokens', 'output_tokens', 'total_tokens',
            'cost', 'currency', 'request_time', 'response_time',
            'created_at'
        ]
        read_only_fields = ['id', 'user_name', 'model_display_name', 'created_at']


class UsageQuotaSerializer(serializers.ModelSerializer):
    """使用配额序列化器"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UsageQuota
        fields = [
            'id', 'user', 'user_name', 'quota_type', 'quota_name',
            'limit_amount', 'used_amount', 'currency', 'reset_period',
            'last_reset', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_name', 'used_amount', 'last_reset', 'created_at', 'updated_at']


class FailoverRuleSerializer(serializers.ModelSerializer):
    """故障转移规则序列化器"""
    
    primary_model_name = serializers.CharField(source='primary_model.display_name', read_only=True)
    fallback_model_name = serializers.CharField(source='fallback_model.display_name', read_only=True)
    
    class Meta:
        model = FailoverRule
        fields = [
            'id', 'strategy', 'primary_model', 'primary_model_name',
            'fallback_model', 'fallback_model_name', 'trigger_condition',
            'max_retries', 'retry_delay', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'primary_model_name', 'fallback_model_name', 'created_at', 'updated_at']


class FailoverStrategySerializer(serializers.ModelSerializer):
    """故障转移策略序列化器"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    rules = FailoverRuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = FailoverStrategy
        fields = [
            'id', 'user', 'user_name', 'strategy_name', 'description',
            'is_active', 'is_default', 'rules', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_name', 'rules', 'created_at', 'updated_at']
