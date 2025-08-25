import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Union
from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from .models import FeatureFlag, FeatureFlagHistory, FeatureFlagUsage


logger = logging.getLogger(__name__)


class FeatureFlagService:
    """特性开关服务类"""
    
    CACHE_PREFIX = 'feature_flag:'
    CACHE_TIMEOUT = 300  # 5分钟缓存
    
    def __init__(self):
        self.environment = getattr(settings, 'ENVIRONMENT', 'development')
    
    def is_enabled(self, 
                   flag_key: str, 
                   user: Optional[User] = None, 
                   context: Optional[Dict[str, Any]] = None,
                   default: bool = False) -> bool:
        """检查特性开关是否启用"""
        try:
            flag = self._get_feature_flag(flag_key)
            if not flag:
                logger.warning(f"Feature flag '{flag_key}' not found")
                return default
            
            # 检查基本状态
            if not flag.is_active():
                self._record_usage(flag, user, False, default, context)
                return default
            
            # 评估用户是否匹配
            is_match = self._evaluate_user_match(flag, user, context)
            value = flag.value if is_match else default
            
            # 记录使用情况
            self._record_usage(flag, user, is_match, value, context)
            
            return bool(value) if isinstance(value, bool) else is_match
            
        except Exception as e:
            logger.error(f"Error evaluating feature flag '{flag_key}': {e}")
            return default
    
    def get_value(self, 
                  flag_key: str, 
                  user: Optional[User] = None, 
                  context: Optional[Dict[str, Any]] = None,
                  default: Any = None) -> Any:
        """获取特性开关的值"""
        try:
            flag = self._get_feature_flag(flag_key)
            if not flag:
                logger.warning(f"Feature flag '{flag_key}' not found")
                return default
            
            # 检查基本状态
            if not flag.is_active():
                self._record_usage(flag, user, False, default, context)
                return default
            
            # 评估用户是否匹配
            is_match = self._evaluate_user_match(flag, user, context)
            value = flag.value if is_match else default
            
            # 记录使用情况
            self._record_usage(flag, user, is_match, value, context)
            
            return value
            
        except Exception as e:
            logger.error(f"Error getting feature flag value '{flag_key}': {e}")
            return default
    
    def get_all_flags(self, 
                      user: Optional[User] = None, 
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """获取所有特性开关的状态"""
        flags = {}
        
        try:
            active_flags = FeatureFlag.objects.filter(
                status__in=[FeatureFlag.Status.ENABLED, FeatureFlag.Status.ROLLOUT]
            )
            
            for flag in active_flags:
                if flag.is_active():
                    is_match = self._evaluate_user_match(flag, user, context)
                    flags[flag.key] = flag.value if is_match else False
                    
                    # 记录使用情况
                    self._record_usage(flag, user, is_match, flags[flag.key], context)
                    
        except Exception as e:
            logger.error(f"Error getting all feature flags: {e}")
        
        return flags
    
    def _get_feature_flag(self, flag_key: str) -> Optional[FeatureFlag]:
        """获取特性开关（带缓存）"""
        cache_key = f"{self.CACHE_PREFIX}{flag_key}"
        flag = cache.get(cache_key)
        
        if flag is None:
            try:
                flag = FeatureFlag.objects.get(key=flag_key)
                cache.set(cache_key, flag, self.CACHE_TIMEOUT)
            except FeatureFlag.DoesNotExist:
                cache.set(cache_key, 'NOT_FOUND', self.CACHE_TIMEOUT)
                return None
        
        return flag if flag != 'NOT_FOUND' else None
    
    def _evaluate_user_match(self, 
                            flag: FeatureFlag, 
                            user: Optional[User] = None, 
                            context: Optional[Dict[str, Any]] = None) -> bool:
        """评估用户是否匹配特性开关条件"""
        context = context or {}
        
        # 检查环境限制
        if flag.environments and self.environment not in flag.environments:
            return False
        
        # 根据目标类型进行匹配
        if flag.target_type == FeatureFlag.TargetType.ALL:
            return True
        
        elif flag.target_type == FeatureFlag.TargetType.PERCENTAGE:
            return self._match_percentage(flag, user)
        
        elif flag.target_type == FeatureFlag.TargetType.USER_LIST:
            return self._match_user_list(flag, user)
        
        elif flag.target_type == FeatureFlag.TargetType.USER_ATTRIBUTE:
            return self._match_user_attributes(flag, user, context)
        
        elif flag.target_type == FeatureFlag.TargetType.ENVIRONMENT:
            return self.environment in flag.environments
        
        return False
    
    def _match_percentage(self, flag: FeatureFlag, user: Optional[User] = None) -> bool:
        """基于百分比的用户匹配"""
        if flag.rollout_percentage == 0:
            return False
        if flag.rollout_percentage == 100:
            return True
        
        # 使用用户ID或会话ID生成一致的哈希
        identifier = str(user.id) if user else 'anonymous'
        hash_input = f"{flag.key}:{identifier}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        percentage = (hash_value % 100) + 1
        
        return percentage <= flag.rollout_percentage
    
    def _match_user_list(self, flag: FeatureFlag, user: Optional[User] = None) -> bool:
        """基于用户列表的匹配"""
        if not user or not flag.target_users:
            return False
        
        return user.id in flag.target_users
    
    def _match_user_attributes(self, 
                              flag: FeatureFlag, 
                              user: Optional[User] = None, 
                              context: Optional[Dict[str, Any]] = None) -> bool:
        """基于用户属性的匹配"""
        if not flag.user_attributes:
            return True
        
        user_data = self._get_user_data(user, context)
        
        for attr_name, conditions in flag.user_attributes.items():
            if not self._evaluate_condition(user_data.get(attr_name), conditions):
                return False
        
        return True
    
    def _get_user_data(self, user: Optional[User] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """获取用户数据用于属性匹配"""
        data = context.copy() if context else {}
        
        if user:
            data.update({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            })
            
            # 添加用户profile信息（如果存在）
            if hasattr(user, 'profile'):
                profile = user.profile
                data.update({
                    'age': getattr(profile, 'age', None),
                    'country': getattr(profile, 'country', None),
                    'language': getattr(profile, 'language', None),
                })
        
        return data
    
    def _evaluate_condition(self, value: Any, conditions: Dict[str, Any]) -> bool:
        """评估单个条件"""
        for operator, expected in conditions.items():
            if operator == 'eq' and value != expected:
                return False
            elif operator == 'ne' and value == expected:
                return False
            elif operator == 'in' and value not in expected:
                return False
            elif operator == 'not_in' and value in expected:
                return False
            elif operator == 'gt' and (value is None or value <= expected):
                return False
            elif operator == 'gte' and (value is None or value < expected):
                return False
            elif operator == 'lt' and (value is None or value >= expected):
                return False
            elif operator == 'lte' and (value is None or value > expected):
                return False
            elif operator == 'contains' and (value is None or expected not in str(value)):
                return False
            elif operator == 'starts_with' and (value is None or not str(value).startswith(expected)):
                return False
            elif operator == 'ends_with' and (value is None or not str(value).endswith(expected)):
                return False
        
        return True
    
    def _record_usage(self, 
                     flag: FeatureFlag, 
                     user: Optional[User] = None, 
                     is_enabled: bool = False, 
                     value: Any = None, 
                     context: Optional[Dict[str, Any]] = None):
        """记录特性开关使用情况"""
        try:
            # 在生产环境中可能需要异步处理以避免性能影响
            FeatureFlagUsage.objects.create(
                feature_flag=flag,
                user=user,
                is_enabled=is_enabled,
                value_returned=value,
                context=context or {},
                environment=self.environment,
            )
        except Exception as e:
            logger.error(f"Error recording feature flag usage: {e}")
    
    def update_flag(self, 
                   flag_key: str, 
                   updates: Dict[str, Any], 
                   user: Optional[User] = None, 
                   reason: str = '') -> bool:
        """更新特性开关"""
        try:
            flag = FeatureFlag.objects.get(key=flag_key)
            old_data = {
                'status': flag.status,
                'rollout_percentage': flag.rollout_percentage,
                'target_type': flag.target_type,
                'value': flag.value,
            }
            
            # 更新字段
            for field, value in updates.items():
                if hasattr(flag, field):
                    setattr(flag, field, value)
            
            flag.updated_by = user
            flag.save()
            
            # 记录变更历史
            FeatureFlagHistory.objects.create(
                feature_flag=flag,
                action='update',
                old_value=old_data,
                new_value=updates,
                reason=reason,
                changed_by=user,
                environment=self.environment,
            )
            
            # 清除缓存
            cache_key = f"{self.CACHE_PREFIX}{flag_key}"
            cache.delete(cache_key)
            
            logger.info(f"Feature flag '{flag_key}' updated by {user}")
            return True
            
        except FeatureFlag.DoesNotExist:
            logger.error(f"Feature flag '{flag_key}' not found")
            return False
        except Exception as e:
            logger.error(f"Error updating feature flag '{flag_key}': {e}")
            return False
    
    def create_flag(self, 
                   flag_data: Dict[str, Any], 
                   user: Optional[User] = None) -> Optional[FeatureFlag]:
        """创建新的特性开关"""
        try:
            flag = FeatureFlag.objects.create(
                created_by=user,
                updated_by=user,
                **flag_data
            )
            
            # 记录创建历史
            FeatureFlagHistory.objects.create(
                feature_flag=flag,
                action='create',
                new_value=flag_data,
                changed_by=user,
                environment=self.environment,
            )
            
            logger.info(f"Feature flag '{flag.key}' created by {user}")
            return flag
            
        except Exception as e:
            logger.error(f"Error creating feature flag: {e}")
            return None
    
    def delete_flag(self, flag_key: str, user: Optional[User] = None, reason: str = '') -> bool:
        """删除特性开关"""
        try:
            flag = FeatureFlag.objects.get(key=flag_key)
            
            # 记录删除历史
            FeatureFlagHistory.objects.create(
                feature_flag=flag,
                action='delete',
                reason=reason,
                changed_by=user,
                environment=self.environment,
            )
            
            flag.delete()
            
            # 清除缓存
            cache_key = f"{self.CACHE_PREFIX}{flag_key}"
            cache.delete(cache_key)
            
            logger.info(f"Feature flag '{flag_key}' deleted by {user}")
            return True
            
        except FeatureFlag.DoesNotExist:
            logger.error(f"Feature flag '{flag_key}' not found")
            return False
        except Exception as e:
            logger.error(f"Error deleting feature flag '{flag_key}': {e}")
            return False
    
    def get_usage_stats(self, flag_key: str, days: int = 7) -> Dict[str, Any]:
        """获取特性开关使用统计"""
        try:
            flag = FeatureFlag.objects.get(key=flag_key)
            start_date = timezone.now() - timezone.timedelta(days=days)
            
            usage_records = FeatureFlagUsage.objects.filter(
                feature_flag=flag,
                accessed_at__gte=start_date
            )
            
            total_requests = usage_records.count()
            enabled_requests = usage_records.filter(is_enabled=True).count()
            unique_users = usage_records.filter(user__isnull=False).values('user').distinct().count()
            
            return {
                'total_requests': total_requests,
                'enabled_requests': enabled_requests,
                'disabled_requests': total_requests - enabled_requests,
                'enabled_percentage': (enabled_requests / total_requests * 100) if total_requests > 0 else 0,
                'unique_users': unique_users,
                'period_days': days,
            }
            
        except FeatureFlag.DoesNotExist:
            return {}
        except Exception as e:
            logger.error(f"Error getting usage stats for '{flag_key}': {e}")
            return {}


# 全局实例
feature_flag_service = FeatureFlagService()