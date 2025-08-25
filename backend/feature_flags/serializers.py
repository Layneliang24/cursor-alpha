from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FeatureFlag, FeatureFlagHistory, FeatureFlagUsage


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器（简化版）"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']


class FeatureFlagSerializer(serializers.ModelSerializer):
    """特性开关序列化器"""
    
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = FeatureFlag
        fields = [
            'id', 'name', 'key', 'description', 'status', 'target_type',
            'rollout_percentage', 'target_users', 'user_attributes', 'environments',
            'value', 'start_time', 'end_time', 'created_by', 'updated_by',
            'created_at', 'updated_at', 'version', 'is_active'
        ]
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_at', 'updated_at', 
            'version', 'is_active'
        ]
    
    def get_is_active(self, obj):
        """获取特性开关是否活跃"""
        return obj.is_active()
    
    def validate_key(self, value):
        """验证特性开关键值"""
        if not value:
            raise serializers.ValidationError("特性开关键值不能为空")
        
        # 检查键值格式（只允许字母、数字、下划线、连字符）
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise serializers.ValidationError(
                "特性开关键值只能包含字母、数字、下划线和连字符"
            )
        
        return value
    
    def validate_rollout_percentage(self, value):
        """验证灰度百分比"""
        if not (0 <= value <= 100):
            raise serializers.ValidationError("灰度百分比必须在0-100之间")
        return value
    
    def validate_target_users(self, value):
        """验证目标用户列表"""
        if not isinstance(value, list):
            raise serializers.ValidationError("目标用户列表必须是数组")
        
        # 验证用户ID是否存在
        if value:
            existing_users = User.objects.filter(id__in=value).values_list('id', flat=True)
            invalid_users = set(value) - set(existing_users)
            if invalid_users:
                raise serializers.ValidationError(
                    f"以下用户ID不存在: {list(invalid_users)}"
                )
        
        return value
    
    def validate_environments(self, value):
        """验证环境列表"""
        if not isinstance(value, list):
            raise serializers.ValidationError("环境列表必须是数组")
        
        # 可以添加环境名称的验证逻辑
        valid_environments = ['development', 'staging', 'production']
        invalid_envs = [env for env in value if env not in valid_environments]
        if invalid_envs:
            raise serializers.ValidationError(
                f"无效的环境名称: {invalid_envs}。有效环境: {valid_environments}"
            )
        
        return value
    
    def validate(self, attrs):
        """整体验证"""
        # 验证时间范围
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("开始时间必须早于结束时间")
        
        # 验证目标类型与相关字段的一致性
        target_type = attrs.get('target_type')
        
        if target_type == FeatureFlag.TargetType.PERCENTAGE:
            if attrs.get('rollout_percentage', 0) == 0:
                raise serializers.ValidationError(
                    "百分比目标类型需要设置大于0的灰度百分比"
                )
        
        elif target_type == FeatureFlag.TargetType.USER_LIST:
            if not attrs.get('target_users'):
                raise serializers.ValidationError(
                    "用户列表目标类型需要设置目标用户列表"
                )
        
        elif target_type == FeatureFlag.TargetType.USER_ATTRIBUTE:
            if not attrs.get('user_attributes'):
                raise serializers.ValidationError(
                    "用户属性目标类型需要设置用户属性条件"
                )
        
        elif target_type == FeatureFlag.TargetType.ENVIRONMENT:
            if not attrs.get('environments'):
                raise serializers.ValidationError(
                    "环境目标类型需要设置环境列表"
                )
        
        return attrs


class FeatureFlagCreateSerializer(FeatureFlagSerializer):
    """特性开关创建序列化器"""
    
    class Meta(FeatureFlagSerializer.Meta):
        fields = [
            'name', 'key', 'description', 'status', 'target_type',
            'rollout_percentage', 'target_users', 'user_attributes', 'environments',
            'value', 'start_time', 'end_time'
        ]
    
    def validate_key(self, value):
        """验证键值唯一性"""
        value = super().validate_key(value)
        
        if FeatureFlag.objects.filter(key=value).exists():
            raise serializers.ValidationError("该特性开关键值已存在")
        
        return value


class FeatureFlagUpdateSerializer(serializers.ModelSerializer):
    """特性开关更新序列化器"""
    
    class Meta:
        model = FeatureFlag
        fields = [
            'name', 'description', 'status', 'target_type',
            'rollout_percentage', 'target_users', 'user_attributes', 'environments',
            'value', 'start_time', 'end_time'
        ]
    
    def validate_rollout_percentage(self, value):
        """验证灰度百分比"""
        if not (0 <= value <= 100):
            raise serializers.ValidationError("灰度百分比必须在0-100之间")
        return value
    
    def validate_target_users(self, value):
        """验证目标用户列表"""
        if not isinstance(value, list):
            raise serializers.ValidationError("目标用户列表必须是数组")
        
        if value:
            existing_users = User.objects.filter(id__in=value).values_list('id', flat=True)
            invalid_users = set(value) - set(existing_users)
            if invalid_users:
                raise serializers.ValidationError(
                    f"以下用户ID不存在: {list(invalid_users)}"
                )
        
        return value
    
    def validate_environments(self, value):
        """验证环境列表"""
        if not isinstance(value, list):
            raise serializers.ValidationError("环境列表必须是数组")
        
        valid_environments = ['development', 'staging', 'production']
        invalid_envs = [env for env in value if env not in valid_environments]
        if invalid_envs:
            raise serializers.ValidationError(
                f"无效的环境名称: {invalid_envs}。有效环境: {valid_environments}"
            )
        
        return value


class FeatureFlagHistorySerializer(serializers.ModelSerializer):
    """特性开关历史序列化器"""
    
    changed_by = UserSerializer(read_only=True)
    feature_flag_key = serializers.CharField(source='feature_flag.key', read_only=True)
    feature_flag_name = serializers.CharField(source='feature_flag.name', read_only=True)
    
    class Meta:
        model = FeatureFlagHistory
        fields = [
            'id', 'feature_flag_key', 'feature_flag_name', 'action',
            'old_value', 'new_value', 'reason', 'changed_by', 'changed_at',
            'environment', 'ip_address', 'user_agent'
        ]
        read_only_fields = fields


class FeatureFlagUsageSerializer(serializers.ModelSerializer):
    """特性开关使用记录序列化器"""
    
    user = UserSerializer(read_only=True)
    feature_flag_key = serializers.CharField(source='feature_flag.key', read_only=True)
    feature_flag_name = serializers.CharField(source='feature_flag.name', read_only=True)
    
    class Meta:
        model = FeatureFlagUsage
        fields = [
            'id', 'feature_flag_key', 'feature_flag_name', 'user', 'session_id',
            'is_enabled', 'value_returned', 'context', 'environment',
            'accessed_at', 'ip_address', 'user_agent'
        ]
        read_only_fields = fields


class FeatureFlagStatsSerializer(serializers.Serializer):
    """特性开关统计序列化器"""
    
    total_requests = serializers.IntegerField()
    enabled_requests = serializers.IntegerField()
    disabled_requests = serializers.IntegerField()
    enabled_percentage = serializers.FloatField()
    unique_users = serializers.IntegerField()
    period_days = serializers.IntegerField()


class FeatureFlagBatchCheckSerializer(serializers.Serializer):
    """批量检查特性开关序列化器"""
    
    flags = serializers.ListField(
        child=serializers.CharField(),
        help_text="要检查的特性开关键值列表"
    )
    context = serializers.JSONField(
        required=False,
        default=dict,
        help_text="额外的上下文信息"
    )


class FeatureFlagToggleSerializer(serializers.Serializer):
    """特性开关切换序列化器"""
    
    reason = serializers.CharField(
        required=False,
        default="手动切换",
        help_text="切换原因"
    )


class FeatureFlagRolloutSerializer(serializers.Serializer):
    """特性开关灰度发布序列化器"""
    
    percentage = serializers.IntegerField(
        min_value=0,
        max_value=100,
        help_text="灰度发布百分比 (0-100)"
    )
    reason = serializers.CharField(
        required=False,
        default="调整灰度百分比",
        help_text="调整原因"
    )


class FeatureFlagCheckSerializer(serializers.Serializer):
    """特性开关检查序列化器"""
    
    context = serializers.JSONField(
        required=False,
        default=dict,
        help_text="额外的上下文信息"
    )


class FeatureFlagCheckResponseSerializer(serializers.Serializer):
    """特性开关检查响应序列化器"""
    
    key = serializers.CharField()
    enabled = serializers.BooleanField()
    value = serializers.JSONField()
    user_id = serializers.IntegerField()
    timestamp = serializers.DateTimeField()


class FeatureFlagBatchCheckResponseSerializer(serializers.Serializer):
    """批量检查特性开关响应序列化器"""
    
    flags = serializers.DictField(
        child=serializers.BooleanField(),
        help_text="特性开关状态字典"
    )
    user_id = serializers.IntegerField()
    timestamp = serializers.DateTimeField(required=False)