from rest_framework import serializers
from .models import ExampleRequirement


class ExampleRequirementSerializer(serializers.ModelSerializer):
    """序列化器: 需求 example_requirement"""
    
    created_by_name = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    
    class Meta:
        model = ExampleRequirement
        fields = [
            'id', 'name', 'description', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """验证名称"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError('名称至少需要2个字符')
        return value.strip()
    
    # TODO: 根据需求添加自定义验证逻辑
