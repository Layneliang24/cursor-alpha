"""
AI配置管理序列化器
"""

import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .config_models import (
    AIProvider, APIKey, AIModel, PromptTemplate, ModelConfig, TokenUsage,
    FailoverStrategy, FailoverRule, UsageQuota
)
from apps.common.security import (
    InputValidator, PROVIDER_NAME_VALIDATOR, MODEL_NAME_VALIDATOR
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
    
    def validate_provider_type(self, value):
        """验证提供商类型"""
        return InputValidator.validate_provider_type(value)
    
    def validate_display_name(self, value):
        """验证显示名称"""
        if not value or not isinstance(value, str):
            raise serializers.ValidationError("显示名称不能为空")
        
        value = value.strip()
        if len(value) < 2 or len(value) > 100:
            raise serializers.ValidationError("显示名称长度必须在2-100字符之间")
        
        # 使用安全字符串验证器
        try:
            InputValidator.SAFE_STRING_VALIDATOR(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        return value
    
    def validate_base_url(self, value):
        """验证API端点"""
        if value:
            return InputValidator.validate_api_endpoint(value)
        return value


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
    
    def validate_name(self, value):
        """验证密钥名称"""
        if not value or not isinstance(value, str):
            raise serializers.ValidationError("密钥名称不能为空")
        
        value = value.strip()
        if len(value) < 2 or len(value) > 100:
            raise serializers.ValidationError("密钥名称长度必须在2-100字符之间")
        
        # 使用安全字符串验证器
        try:
            InputValidator.SAFE_STRING_VALIDATOR(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        return value
    
    def validate_raw_key(self, value):
        """验证原始API密钥"""
        if not value or not isinstance(value, str):
            raise serializers.ValidationError("API密钥不能为空")
        
        value = value.strip()
        if len(value) < 10 or len(value) > 500:
            raise serializers.ValidationError("API密钥长度必须在10-500字符之间")
        
        # 检查密钥格式（基本安全检查）
        if not re.match(r'^[a-zA-Z0-9\-_.]+$', value):
            raise serializers.ValidationError("API密钥格式不正确")
        
        return value
    
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
    
    def validate_model_id(self, value):
        """验证模型ID"""
        return InputValidator.validate_model_name(value)
    
    def validate_display_name(self, value):
        """验证显示名称"""
        if not value or not isinstance(value, str):
            raise serializers.ValidationError("显示名称不能为空")
        
        value = value.strip()
        if len(value) < 2 or len(value) > 100:
            raise serializers.ValidationError("显示名称长度必须在2-100字符之间")
        
        try:
            InputValidator.SAFE_STRING_VALIDATOR(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        return value


class PromptTemplateSerializer(serializers.ModelSerializer):
    """系统提示模板序列化器"""
    
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = PromptTemplate
        fields = [
            'id', 'name', 'description', 'content', 'category',
            'is_public', 'is_system', 'is_active', 'usage_count',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'usage_count', 'created_by_name', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """验证模板名称"""
        if not value or not isinstance(value, str):
            raise serializers.ValidationError("模板名称不能为空")
        
        value = value.strip()
        if len(value) < 2 or len(value) > 100:
            raise serializers.ValidationError("模板名称长度必须在2-100字符之间")
        
        try:
            InputValidator.SAFE_STRING_VALIDATOR(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        return value
    
    def validate_content(self, value):
        """验证模板内容"""
        if not value or not isinstance(value, str):
            raise serializers.ValidationError("模板内容不能为空")
        
        value = value.strip()
        if len(value) < 5 or len(value) > 10000:
            raise serializers.ValidationError("模板内容长度必须在5-10000字符之间")
        
        return value
    
    def create(self, validated_data):
        """创建模板时设置创建者"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ModelConfigSerializer(serializers.ModelSerializer):
    """模型配置序列化器"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    provider_name = serializers.CharField(source='provider.display_name', read_only=True)
    template_name = serializers.CharField(source='prompt_template.name', read_only=True)
    context_window = serializers.SerializerMethodField()
    
    class Meta:
        model = ModelConfig
        fields = [
            'id', 'user', 'user_name', 'provider', 'provider_name', 'model',
            'config_name', 'temperature', 'max_tokens', 'top_p',
            'frequency_penalty', 'presence_penalty', 'prompt_template',
            'template_name', 'system_prompt_template', 'advanced_params',
            'context_window', 'is_default', 'is_active',
            'created_at', 'updated_at', 'last_used'
        ]
        read_only_fields = [
            'id', 'user_name', 'provider_name', 'template_name', 
            'context_window', 'created_at', 'updated_at', 'last_used'
        ]
    
    def get_context_window(self, obj):
        """获取模型上下文窗口"""
        try:
            # 尝试从AIModel表获取max_tokens
            ai_model = AIModel.objects.filter(
                provider=obj.provider,
                model_id=obj.model
            ).first()
            return ai_model.max_tokens if ai_model else 4096
        except:
            return 4096  # 默认值
    
    def validate_config_name(self, value):
        """验证配置名称"""
        if not value or not isinstance(value, str):
            raise serializers.ValidationError("配置名称不能为空")
        
        value = value.strip()
        if len(value) < 2 or len(value) > 100:
            raise serializers.ValidationError("配置名称长度必须在2-100字符之间")
        
        try:
            InputValidator.SAFE_STRING_VALIDATOR(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        return value
    
    def validate_temperature(self, value):
        """验证温度参数"""
        if value is not None:
            if not isinstance(value, (int, float)) or value < 0 or value > 2:
                raise serializers.ValidationError("temperature必须在0.0-2.0之间")
        return value
    
    def validate_max_tokens(self, value):
        """验证最大token数"""
        if value is not None:
            if not isinstance(value, int) or value < 1:
                raise serializers.ValidationError("max_tokens必须大于0")
            
            # 获取模型上下文窗口进行验证
            provider = self.initial_data.get('provider')
            model = self.initial_data.get('model')
            
            if provider and model:
                try:
                    ai_model = AIModel.objects.filter(
                        provider_id=provider,
                        model_id=model
                    ).first()
                    
                    if ai_model:
                        # 获取保留Token数（默认256）
                        advanced_params = self.initial_data.get('advanced_params', {})
                        reserved_tokens = advanced_params.get('reserved_tokens', 256)
                        
                        if not isinstance(reserved_tokens, int) or reserved_tokens < 0:
                            reserved_tokens = 256
                        
                        max_allowed = ai_model.max_tokens - reserved_tokens
                        if value > max_allowed:
                            raise serializers.ValidationError(
                                f"max_tokens不能超过{max_allowed}（模型上下文窗口{ai_model.max_tokens} - 保留Token{reserved_tokens}）"
                            )
                except:
                    pass  # 如果验证失败，不阻塞保存
        
        return value
    
    def validate_top_p(self, value):
        """验证top_p参数"""
        if value is not None:
            if not isinstance(value, (int, float)) or value <= 0 or value > 1:
                raise serializers.ValidationError("top_p必须在(0,1]之间")
        return value
    
    def validate_frequency_penalty(self, value):
        """验证频率惩罚"""
        if value is not None:
            if not isinstance(value, (int, float)) or value < -2 or value > 2:
                raise serializers.ValidationError("frequency_penalty必须在-2.0到2.0之间")
        return value
    
    def validate_presence_penalty(self, value):
        """验证存在惩罚"""
        if value is not None:
            if not isinstance(value, (int, float)) or value < -2 or value > 2:
                raise serializers.ValidationError("presence_penalty必须在-2.0到2.0之间")
        return value
    
    def validate_advanced_params(self, value):
        """验证高级参数"""
        if not value:
            return value
        
        if not isinstance(value, dict):
            raise serializers.ValidationError("advanced_params必须是字典格式")
        
        # 验证保留Token数
        if 'reserved_tokens' in value:
            reserved_tokens = value['reserved_tokens']
            if not isinstance(reserved_tokens, int) or reserved_tokens < 0:
                raise serializers.ValidationError("reserved_tokens必须是非负整数")
        
        # 验证种子值
        if 'seed' in value:
            seed = value['seed']
            if seed is not None and (not isinstance(seed, int) or seed < 0):
                raise serializers.ValidationError("seed必须是非负整数或null")
        
        # 验证停止词
        if 'stop_words' in value:
            stop_words = value['stop_words']
            if stop_words is not None:
                if not isinstance(stop_words, list):
                    raise serializers.ValidationError("stop_words必须是字符串数组")
                if len(stop_words) > 10:
                    raise serializers.ValidationError("stop_words最多包含10个停止词")
                for word in stop_words:
                    if not isinstance(word, str) or len(word) > 20:
                        raise serializers.ValidationError("每个停止词长度不能超过20字符")
        
        # 验证logit_bias
        if 'logit_bias' in value:
            logit_bias = value['logit_bias']
            if logit_bias is not None:
                if not isinstance(logit_bias, dict):
                    raise serializers.ValidationError("logit_bias必须是字典格式")
                if len(logit_bias) > 100:
                    raise serializers.ValidationError("logit_bias最多包含100个键值对")
                for token_id, bias in logit_bias.items():
                    if not isinstance(bias, (int, float)) or bias < -100 or bias > 100:
                        raise serializers.ValidationError("logit_bias值必须在-100到100之间")
        
        return value
    
    def create(self, validated_data):
        """创建配置时设置用户"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """更新配置时处理模板关联"""
        # 如果选择了模板，同步模板内容
        if 'prompt_template' in validated_data and validated_data['prompt_template']:
            template = validated_data['prompt_template']
            validated_data['system_prompt_template'] = template.content
            template.increment_usage()  # 增加使用次数
        
        return super().update(instance, validated_data)


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
