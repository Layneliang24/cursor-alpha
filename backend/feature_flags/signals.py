from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import FeatureFlag, FeatureFlagHistory
import json

User = get_user_model()


@receiver(post_save, sender=FeatureFlag)
def feature_flag_changed(sender, instance, created, **kwargs):
    """特性开关变更信号处理器"""
    
    # 获取当前请求的用户（如果有的话）
    user = getattr(instance, '_changed_by', None)
    reason = getattr(instance, '_change_reason', '系统自动变更')
    
    if created:
        # 新建特性开关
        FeatureFlagHistory.objects.create(
            feature_flag=instance,
            action=FeatureFlagHistory.Action.CREATED,
            old_value=None,
            new_value=_serialize_flag(instance),
            reason=reason,
            changed_by=user,
            environment=getattr(instance, '_environment', 'unknown')
        )
    else:
        # 更新特性开关
        # 获取旧值（从数据库重新查询）
        try:
            old_instance = FeatureFlag.objects.get(pk=instance.pk)
            old_value = _serialize_flag(old_instance)
        except FeatureFlag.DoesNotExist:
            old_value = None
        
        # 检查是否有实际变更
        new_value = _serialize_flag(instance)
        if old_value != new_value:
            # 确定变更类型
            action = FeatureFlagHistory.Action.UPDATED
            
            # 检查状态变更
            if old_value and old_value.get('status') != new_value.get('status'):
                if new_value.get('status') == FeatureFlag.Status.ENABLED:
                    action = FeatureFlagHistory.Action.ENABLED
                elif new_value.get('status') == FeatureFlag.Status.DISABLED:
                    action = FeatureFlagHistory.Action.DISABLED
                elif new_value.get('status') == FeatureFlag.Status.ROLLOUT:
                    action = FeatureFlagHistory.Action.ROLLOUT_STARTED
            
            FeatureFlagHistory.objects.create(
                feature_flag=instance,
                action=action,
                old_value=old_value,
                new_value=new_value,
                reason=reason,
                changed_by=user,
                environment=getattr(instance, '_environment', 'unknown')
            )


@receiver(post_delete, sender=FeatureFlag)
def feature_flag_deleted(sender, instance, **kwargs):
    """特性开关删除信号处理器"""
    
    user = getattr(instance, '_changed_by', None)
    reason = getattr(instance, '_change_reason', '系统删除')
    
    FeatureFlagHistory.objects.create(
        feature_flag=None,  # 已删除，无法关联
        action=FeatureFlagHistory.Action.DELETED,
        old_value=_serialize_flag(instance),
        new_value=None,
        reason=reason,
        changed_by=user,
        environment=getattr(instance, '_environment', 'unknown'),
        # 保存被删除的特性开关信息
        metadata={
            'deleted_flag_key': instance.key,
            'deleted_flag_name': instance.name,
            'deleted_flag_id': instance.id
        }
    )


def _serialize_flag(flag):
    """序列化特性开关为字典"""
    if not flag:
        return None
    
    return {
        'key': flag.key,
        'name': flag.name,
        'description': flag.description,
        'status': flag.status,
        'target_type': flag.target_type,
        'rollout_percentage': flag.rollout_percentage,
        'target_users': flag.target_users,
        'user_attributes': flag.user_attributes,
        'environments': flag.environments,
        'value': flag.value,
        'start_time': flag.start_time.isoformat() if flag.start_time else None,
        'end_time': flag.end_time.isoformat() if flag.end_time else None,
        'version': flag.version
    }


class FeatureFlagChangeContext:
    """特性开关变更上下文管理器"""
    
    def __init__(self, flag, user=None, reason=None, environment='unknown'):
        self.flag = flag
        self.user = user
        self.reason = reason or '手动变更'
        self.environment = environment
    
    def __enter__(self):
        # 设置变更上下文
        self.flag._changed_by = self.user
        self.flag._change_reason = self.reason
        self.flag._environment = self.environment
        return self.flag
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 清理变更上下文
        if hasattr(self.flag, '_changed_by'):
            delattr(self.flag, '_changed_by')
        if hasattr(self.flag, '_change_reason'):
            delattr(self.flag, '_change_reason')
        if hasattr(self.flag, '_environment'):
            delattr(self.flag, '_environment')


def track_flag_change(flag, user=None, reason=None, environment='unknown'):
    """跟踪特性开关变更的装饰器函数"""
    return FeatureFlagChangeContext(flag, user, reason, environment)