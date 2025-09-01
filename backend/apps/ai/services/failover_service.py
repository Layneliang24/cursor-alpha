"""
故障转移服务
负责处理AI服务提供商的故障转移逻辑
"""

import logging
import random
from typing import Optional, Dict, Any, List
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache

from ..models import FailoverStrategy, FailoverRule, AIProvider, AIModel, ProviderHealthStatus

logger = logging.getLogger(__name__)


class FailoverService:
    """故障转移服务"""
    
    def __init__(self, strategy: FailoverStrategy):
        self.strategy = strategy
        self.cache_prefix = f"failover_{strategy.id}"
        self.cache_timeout = 300  # 5分钟缓存
    
    def get_active_provider(self) -> Optional[AIProvider]:
        """获取当前活跃的提供商"""
        # 首先检查主提供商是否健康
        if self.strategy.primary_provider.is_healthy:
            return self.strategy.primary_provider
        
        # 如果主提供商不健康，按优先级查找备用提供商
        active_rules = self.strategy.rules.filter(
            is_active=True
        ).order_by('priority')
        
        for rule in active_rules:
            if rule.fallback_provider.is_healthy:
                return rule.fallback_provider
        
        # 如果没有健康的备用提供商，返回主提供商（让上层处理错误）
        logger.warning(
            f"策略 {self.strategy.name} 没有可用的健康提供商，"
            f"返回主提供商 {self.strategy.primary_provider.display_name}"
        )
        return self.strategy.primary_provider
    
    def get_active_model(self, provider: AIProvider = None) -> Optional[AIModel]:
        """获取当前活跃提供商对应的模型"""
        if provider is None:
            provider = self.get_active_provider()
        
        if provider == self.strategy.primary_provider:
            return self.strategy.primary_model
        
        # 查找对应的备用模型
        rule = self.strategy.rules.filter(
            fallback_provider=provider,
            is_active=True
        ).first()
        
        return rule.fallback_model if rule else None
    
    def should_failover(self, error_type: str = None, response_time: float = None) -> bool:
        """判断是否应该执行故障转移"""
        # 检查错误类型是否触发故障转移
        if error_type:
            # 获取包含此错误类型的规则
            matching_rules = self.strategy.rules.filter(
                is_active=True,
                trigger_errors__contains=[error_type]
            )
            if matching_rules.exists():
                return True
        
        # 检查响应时间是否超过阈值
        if response_time and response_time > self.strategy.timeout_threshold:
            logger.info(
                f"响应时间 {response_time}s 超过阈值 {self.strategy.timeout_threshold}s，"
                f"触发故障转移"
            )
            return True
        
        # 检查错误率
        cache_key = f"{self.cache_prefix}_error_rate"
        error_rate = cache.get(cache_key, 0.0)
        if error_rate > self.strategy.error_rate_threshold:
            logger.info(
                f"错误率 {error_rate} 超过阈值 {self.strategy.error_rate_threshold}，"
                f"触发故障转移"
            )
            return True
        
        return False
    
    def execute_failover(self, reason: str, error_type: str = None) -> Dict[str, Any]:
        """执行故障转移"""
        logger.info(f"开始执行故障转移，策略: {self.strategy.name}，原因: {reason}")
        
        # 获取当前活跃提供商
        current_provider = self.get_active_provider()
        
        # 检查是否在冷却期内
        if self._is_in_cooldown():
            logger.info(f"策略 {self.strategy.name} 在冷却期内，跳过故障转移")
            return {
                'success': False,
                'reason': 'cooldown_period',
                'current_provider': current_provider.display_name if current_provider else None
            }
        
        # 根据策略模式选择下一个提供商
        next_provider = self._select_next_provider()
        
        if next_provider and next_provider != current_provider:
            # 执行切换
            with transaction.atomic():
                self.strategy.active_provider = next_provider
                self.strategy.last_switch_at = timezone.now()
                self.strategy.save()
                
                # 记录审计日志
                self._log_switch(current_provider, next_provider, reason, error_type)
                
                logger.info(
                    f"故障转移成功: {current_provider.display_name if current_provider else 'None'} -> "
                    f"{next_provider.display_name}"
                )
                
                return {
                    'success': True,
                    'previous_provider': current_provider.display_name if current_provider else None,
                    'current_provider': next_provider.display_name,
                    'reason': reason
                }
        else:
            logger.warning(f"没有可用的备用提供商进行故障转移")
            return {
                'success': False,
                'reason': 'no_available_provider',
                'current_provider': current_provider.display_name if current_provider else None
            }
    
    def record_request_result(self, provider: AIProvider, success: bool, 
                            response_time: float = None, error_type: str = None):
        """记录请求结果"""
        # 获取或创建健康状态记录
        health_status, created = ProviderHealthStatus.objects.get_or_create(
            strategy=self.strategy,
            provider=provider,
            defaults={
                'success_count': 0,
                'failure_count': 0,
                'consecutive_failures': 0,
                'consecutive_successes': 0,
                'is_healthy': True,
                'is_available': True
            }
        )
        
        # 记录结果
        if success:
            health_status.record_success(response_time)
            logger.debug(f"记录成功请求: {provider.display_name}")
        else:
            health_status.record_failure(response_time)
            logger.debug(f"记录失败请求: {provider.display_name}")
        
        # 检查是否需要自动切换
        self._check_auto_switch(health_status, error_type)
    
    def _check_auto_switch(self, health_status: ProviderHealthStatus, error_type: str = None):
        """检查是否需要自动切换"""
        current_provider = self.strategy.active_provider
        
        # 检查是否应该故障转移
        if (health_status.should_failover() and 
            health_status.provider == current_provider and
            not self._is_in_cooldown()):
            
            logger.info(
                f"提供商 {current_provider.display_name} 连续失败 {health_status.consecutive_failures} 次，"
                f"达到阈值 {self.strategy.fail_threshold}，触发自动故障转移"
            )
            
            self.execute_failover(
                reason=f"连续失败{health_status.consecutive_failures}次",
                error_type=error_type
            )
        
        # 检查是否应该恢复
        elif (health_status.should_recover() and 
              not self._is_in_cooldown() and
              not self._is_in_jitter_window()):
            
            # 如果是主提供商恢复，直接切换
            if health_status.provider == self.strategy.primary_provider:
                logger.info(
                    f"主提供商 {health_status.provider.display_name} 连续成功 {health_status.consecutive_successes} 次，"
                    f"达到恢复阈值 {self.strategy.recovery_threshold}，恢复主提供商"
                )
                self._switch_to_provider(self.strategy.primary_provider, "主提供商恢复")
            # 如果是备用提供商恢复，检查主提供商是否健康
            elif health_status.provider != self.strategy.primary_provider:
                logger.info(
                    f"备用提供商 {health_status.provider.display_name} 连续成功 {health_status.consecutive_successes} 次，"
                    f"达到恢复阈值 {self.strategy.recovery_threshold}，尝试恢复主提供商"
                )
                
                # 检查主提供商是否健康
                primary_health = self._get_provider_health_status(self.strategy.primary_provider)
                if primary_health and primary_health.is_healthy:
                    self._switch_to_provider(self.strategy.primary_provider, "主提供商恢复")
    
    def _select_next_provider(self) -> Optional[AIProvider]:
        """根据策略模式选择下一个提供商"""
        if self.strategy.strategy_mode == 'priority':
            return self._select_by_priority()
        elif self.strategy.strategy_mode == 'round_robin':
            return self._select_by_round_robin()
        else:
            return self._select_by_priority()  # 默认使用优先级模式
    
    def _select_by_priority(self) -> Optional[AIProvider]:
        """按优先级选择提供商"""
        # 首先尝试主提供商
        if self._is_provider_healthy(self.strategy.primary_provider):
            return self.strategy.primary_provider
        
        # 然后按优先级尝试备用提供商
        rules = self.strategy.rules.filter(is_active=True).order_by('priority')
        for rule in rules:
            if self._is_provider_healthy(rule.fallback_provider):
                return rule.fallback_provider
        
        return None
    
    def _select_by_round_robin(self) -> Optional[AIProvider]:
        """按轮询模式选择提供商"""
        # 获取所有可用的提供商
        available_providers = []
        
        # 添加主提供商
        if self._is_provider_healthy(self.strategy.primary_provider):
            available_providers.append(self.strategy.primary_provider)
        
        # 添加备用提供商
        rules = self.strategy.rules.filter(is_active=True).order_by('priority')
        for rule in rules:
            if self._is_provider_healthy(rule.fallback_provider):
                available_providers.append(rule.fallback_provider)
        
        if not available_providers:
            return None
        
        # 使用缓存记录当前轮询位置
        cache_key = f"{self.cache_prefix}_round_robin_index"
        current_index = cache.get(cache_key, 0)
        
        # 选择下一个提供商
        next_index = (current_index + 1) % len(available_providers)
        cache.set(cache_key, next_index, self.cache_timeout)
        
        return available_providers[next_index]
    
    def _is_provider_healthy(self, provider: AIProvider) -> bool:
        """检查提供商是否健康"""
        health_status = self._get_provider_health_status(provider)
        if health_status:
            return health_status.is_healthy and health_status.is_available
        return provider.is_healthy
    
    def _get_provider_health_status(self, provider: AIProvider) -> Optional[ProviderHealthStatus]:
        """获取提供商健康状态"""
        try:
            return ProviderHealthStatus.objects.get(
                strategy=self.strategy,
                provider=provider
            )
        except ProviderHealthStatus.DoesNotExist:
            return None
    
    def _is_in_cooldown(self) -> bool:
        """检查是否在冷却期内"""
        if not self.strategy.last_switch_at:
            return False
        
        cooldown_end = self.strategy.last_switch_at + timezone.timedelta(seconds=self.strategy.cooldown)
        return timezone.now() < cooldown_end
    
    def _is_in_jitter_window(self) -> bool:
        """检查是否在抖动窗口内"""
        if not self.strategy.last_switch_at:
            return False
        
        # 使用固定的抖动窗口（冷却期 + 抖动窗口）
        jitter_end = self.strategy.last_switch_at + timezone.timedelta(seconds=self.strategy.cooldown + self.strategy.jitter_window)
        return timezone.now() < jitter_end
    
    def _switch_to_provider(self, provider: AIProvider, reason: str):
        """切换到指定提供商"""
        with transaction.atomic():
            previous_provider = self.strategy.active_provider
            self.strategy.active_provider = provider
            self.strategy.last_switch_at = timezone.now()
            self.strategy.save()
            
            # 记录审计日志
            self._log_switch(previous_provider, provider, reason)
            
            logger.info(
                f"切换到提供商: {previous_provider.display_name if previous_provider else 'None'} -> "
                f"{provider.display_name}，原因: {reason}"
            )
    
    def _log_switch(self, from_provider: AIProvider, to_provider: AIProvider, 
                   reason: str, error_type: str = None):
        """记录切换日志"""
        # 这里可以记录到审计日志表或系统日志
        log_data = {
            'strategy_id': self.strategy.id,
            'strategy_name': self.strategy.name,
            'from_provider': from_provider.display_name if from_provider else None,
            'to_provider': to_provider.display_name if to_provider else None,
            'reason': reason,
            'error_type': error_type,
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(f"故障转移切换: {log_data}")
        
        # 可以在这里添加审计日志记录
        # FallbackAuditLog.objects.create(...)
    
    def get_health_summary(self) -> Dict[str, Any]:
        """获取健康状态摘要"""
        health_statuses = ProviderHealthStatus.objects.filter(strategy=self.strategy)
        
        summary = {
            'strategy_id': self.strategy.id,
            'strategy_name': self.strategy.name,
            'active_provider': self.strategy.active_provider.display_name if self.strategy.active_provider else None,
            'providers': []
        }
        
        for health in health_statuses:
            provider_info = {
                'provider_name': health.provider.display_name,
                'is_healthy': health.is_healthy,
                'is_available': health.is_available,
                'success_rate': health.get_success_rate(),
                'consecutive_failures': health.consecutive_failures,
                'consecutive_successes': health.consecutive_successes,
                'avg_response_time': health.avg_response_time,
                'last_heartbeat': health.last_heartbeat_at.isoformat() if health.last_heartbeat_at else None
            }
            summary['providers'].append(provider_info)
        
        return summary


class FailoverManager:
    """故障转移管理器 - 管理多个策略"""
    
    @staticmethod
    def get_user_default_strategy(user) -> Optional[FailoverStrategy]:
        """获取用户的默认故障转移策略"""
        return FailoverStrategy.objects.filter(
            user=user,
            is_active=True,
            is_default=True
        ).first()
    
    @staticmethod
    def get_best_provider_for_user(user, model_name: str = None) -> Optional[AIProvider]:
        """为用户获取最佳提供商"""
        strategy = FailoverManager.get_user_default_strategy(user)
        if not strategy:
            # 如果没有策略，返回第一个健康的提供商
            return AIProvider.objects.filter(
                is_active=True,
                is_healthy=True
            ).first()
        
        service = FailoverService(strategy)
        return service.get_active_provider()
    
    @staticmethod
    def handle_request_error(user, provider: AIProvider, error_type: str, 
                           response_time: float = None) -> Dict[str, Any]:
        """处理请求错误，决定是否需要故障转移"""
        strategy = FailoverManager.get_user_default_strategy(user)
        if not strategy:
            return {'should_failover': False, 'message': '没有配置故障转移策略'}
        
        service = FailoverService(strategy)
        
        # 记录失败
        service.record_failure(provider, error_type, response_time)
        
        # 检查是否需要故障转移
        if service.should_failover(error_type, response_time):
            result = service.execute_failover(
                reason=f"检测到错误: {error_type}",
                error_type=error_type
            )
            return {
                'should_failover': True,
                'failover_result': result
            }
        
        return {'should_failover': False, 'message': '错误未达到故障转移阈值'}
