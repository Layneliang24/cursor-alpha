"""
故障转移服务
负责处理AI服务提供商的故障转移逻辑
"""

import logging
from typing import Optional, Dict, Any, List
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache

from ..models import FailoverStrategy, FailoverRule, AIProvider, AIModel

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
        
        # 查找下一个可用的提供商
        next_provider = self._find_next_provider(current_provider, error_type)
        
        if not next_provider:
            logger.error(f"没有找到可用的备用提供商")
            return {
                'success': False,
                'message': '没有可用的备用提供商',
                'current_provider': current_provider.display_name if current_provider else None,
                'next_provider': None
            }
        
        if next_provider == current_provider:
            logger.info(f"当前提供商已是最优选择，无需切换")
            return {
                'success': True,
                'message': '当前提供商已是最优选择',
                'current_provider': current_provider.display_name,
                'next_provider': current_provider.display_name,
                'switched': False
            }
        
        # 执行切换
        result = self._switch_provider(current_provider, next_provider, reason, 'auto_switch')
        
        # 更新统计信息
        self._update_statistics(switched=result['success'])
        
        return result
    
    def manual_switch(self, target_provider: AIProvider = None, reason: str = '',
                     operator=None, dry_run: bool = False) -> Dict[str, Any]:
        """手动切换提供商"""
        logger.info(
            f"开始手动切换提供商，策略: {self.strategy.name}，"
            f"目标: {target_provider.display_name if target_provider else '自动选择'}，"
            f"原因: {reason}，试运行: {dry_run}"
        )
        
        current_provider = self.get_active_provider()
        
        if target_provider is None:
            # 自动选择下一个可用提供商
            target_provider = self._find_next_provider(current_provider)
        
        if not target_provider:
            return {
                'success': False,
                'message': '没有找到可用的目标提供商',
                'current_provider': current_provider.display_name if current_provider else None,
                'target_provider': None
            }
        
        if target_provider == current_provider:
            return {
                'success': True,
                'message': '目标提供商与当前提供商相同，无需切换',
                'current_provider': current_provider.display_name,
                'target_provider': target_provider.display_name,
                'switched': False
            }
        
        if dry_run:
            # 试运行，只返回切换计划
            return {
                'success': True,
                'message': '试运行成功',
                'current_provider': current_provider.display_name,
                'target_provider': target_provider.display_name,
                'dry_run': True,
                'plan': {
                    'from_model': self.get_active_model(current_provider).model_name,
                    'to_model': self.get_active_model(target_provider).model_name,
                    'reason': reason
                }
            }
        
        # 执行实际切换
        result = self._switch_provider(
            current_provider, 
            target_provider, 
            reason, 
            'manual_switch',
            operator
        )
        
        return result
    
    def test_failover(self) -> Dict[str, Any]:
        """测试故障转移策略"""
        logger.info(f"开始测试故障转移策略: {self.strategy.name}")
        
        test_results = {
            'strategy_name': self.strategy.name,
            'primary_provider': {
                'name': self.strategy.primary_provider.display_name,
                'is_healthy': self.strategy.primary_provider.is_healthy,
                'model': self.strategy.primary_model.model_name
            },
            'fallback_rules': [],
            'recommendations': []
        }
        
        # 测试所有备用规则
        for rule in self.strategy.rules.filter(is_active=True).order_by('priority'):
            rule_test = {
                'priority': rule.priority,
                'provider_name': rule.fallback_provider.display_name,
                'model_name': rule.fallback_model.model_name,
                'is_healthy': rule.fallback_provider.is_healthy,
                'trigger_errors': rule.trigger_errors,
                'available': rule.fallback_provider.is_healthy and rule.fallback_provider.is_active
            }
            test_results['fallback_rules'].append(rule_test)
        
        # 生成建议
        healthy_rules = [r for r in test_results['fallback_rules'] if r['available']]
        if not healthy_rules:
            test_results['recommendations'].append(
                "警告: 没有可用的备用提供商，建议添加更多备用规则或检查提供商健康状态"
            )
        
        if not self.strategy.primary_provider.is_healthy:
            if healthy_rules:
                test_results['recommendations'].append(
                    f"主提供商不健康，将自动切换到 {healthy_rules[0]['provider_name']}"
                )
            else:
                test_results['recommendations'].append(
                    "主提供商不健康且没有可用的备用提供商，服务可能中断"
                )
        
        return test_results
    
    def _find_next_provider(self, current_provider: AIProvider, 
                           error_type: str = None) -> Optional[AIProvider]:
        """查找下一个可用的提供商"""
        # 获取所有活跃规则，按优先级排序
        rules = self.strategy.rules.filter(is_active=True).order_by('priority')
        
        # 如果指定了错误类型，优先考虑匹配的规则
        if error_type:
            matching_rules = rules.filter(trigger_errors__contains=[error_type])
            if matching_rules.exists():
                for rule in matching_rules:
                    if (rule.fallback_provider.is_healthy and 
                        rule.fallback_provider.is_active and
                        rule.fallback_provider != current_provider):
                        return rule.fallback_provider
        
        # 按优先级查找可用提供商
        for rule in rules:
            if (rule.fallback_provider.is_healthy and 
                rule.fallback_provider.is_active and
                rule.fallback_provider != current_provider):
                return rule.fallback_provider
        
        # 如果当前不是主提供商且主提供商健康，回退到主提供商
        if (current_provider != self.strategy.primary_provider and
            self.strategy.primary_provider.is_healthy and
            self.strategy.primary_provider.is_active):
            return self.strategy.primary_provider
        
        return None
    
    @transaction.atomic
    def _switch_provider(self, from_provider: AIProvider, to_provider: AIProvider,
                        reason: str, action_type: str, operator=None) -> Dict[str, Any]:
        """执行提供商切换"""
        try:
            # 记录审计日志
            from ..models import FallbackAuditLog
            
            audit_log = FallbackAuditLog.objects.create(
                strategy=self.strategy,
                action_type=action_type,
                from_provider=from_provider.display_name if from_provider else '',
                to_provider=to_provider.display_name,
                reason=reason,
                operator=operator,
                metadata={
                    'from_provider_id': from_provider.id if from_provider else None,
                    'to_provider_id': to_provider.id,
                    'from_model': self.get_active_model(from_provider).model_name if from_provider else '',
                    'to_model': self.get_active_model(to_provider).model_name,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            # 更新相关规则的触发统计
            if action_type == 'auto_switch':
                rule = self.strategy.rules.filter(
                    fallback_provider=to_provider,
                    is_active=True
                ).first()
                if rule:
                    rule.trigger_count += 1
                    rule.last_triggered = timezone.now()
                    rule.save(update_fields=['trigger_count', 'last_triggered'])
            
            logger.info(
                f"提供商切换成功: {from_provider.display_name if from_provider else 'None'} "
                f"-> {to_provider.display_name}"
            )
            
            return {
                'success': True,
                'message': '切换成功',
                'current_provider': from_provider.display_name if from_provider else None,
                'next_provider': to_provider.display_name,
                'switched': True,
                'audit_log_id': audit_log.id,
                'switch_time': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"提供商切换失败: {str(e)}")
            return {
                'success': False,
                'message': f'切换失败: {str(e)}',
                'current_provider': from_provider.display_name if from_provider else None,
                'next_provider': to_provider.display_name,
                'switched': False,
                'error': str(e)
            }
    
    def _update_statistics(self, switched: bool = False):
        """更新统计信息"""
        try:
            self.strategy.total_requests += 1
            if switched:
                self.strategy.fallback_count += 1
            else:
                self.strategy.successful_requests += 1
            
            self.strategy.last_used = timezone.now()
            self.strategy.save(update_fields=[
                'total_requests', 'successful_requests', 'fallback_count', 'last_used'
            ])
            
        except Exception as e:
            logger.error(f"更新统计信息失败: {str(e)}")
    
    def record_success(self, provider: AIProvider, response_time: float = None):
        """记录成功调用"""
        try:
            # 更新提供商健康状态
            provider.update_health_status(True, response_time)
            
            # 更新策略统计
            self.strategy.successful_requests += 1
            self.strategy.total_requests += 1
            self.strategy.last_used = timezone.now()
            self.strategy.save(update_fields=[
                'successful_requests', 'total_requests', 'last_used'
            ])
            
            # 更新相关规则的成功统计
            if provider != self.strategy.primary_provider:
                rule = self.strategy.rules.filter(
                    fallback_provider=provider,
                    is_active=True
                ).first()
                if rule:
                    rule.success_count += 1
                    rule.save(update_fields=['success_count'])
            
            # 更新缓存中的错误率
            self._update_error_rate_cache(success=True)
            
        except Exception as e:
            logger.error(f"记录成功调用失败: {str(e)}")
    
    def record_failure(self, provider: AIProvider, error_type: str = '', 
                      response_time: float = None):
        """记录失败调用"""
        try:
            # 更新提供商健康状态
            provider.update_health_status(False, response_time)
            
            # 更新策略统计
            self.strategy.total_requests += 1
            self.strategy.last_used = timezone.now()
            self.strategy.save(update_fields=['total_requests', 'last_used'])
            
            # 更新缓存中的错误率
            self._update_error_rate_cache(success=False)
            
        except Exception as e:
            logger.error(f"记录失败调用失败: {str(e)}")
    
    def _update_error_rate_cache(self, success: bool):
        """更新错误率缓存"""
        try:
            cache_key = f"{self.cache_prefix}_error_rate"
            
            # 获取当前错误率数据
            error_data = cache.get(cache_key, {'total': 0, 'errors': 0})
            
            error_data['total'] += 1
            if not success:
                error_data['errors'] += 1
            
            # 计算错误率
            error_rate = error_data['errors'] / error_data['total'] if error_data['total'] > 0 else 0
            
            # 更新缓存
            cache.set(cache_key, error_data, self.cache_timeout)
            cache.set(f"{self.cache_prefix}_current_error_rate", error_rate, self.cache_timeout)
            
        except Exception as e:
            logger.error(f"更新错误率缓存失败: {str(e)}")


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
