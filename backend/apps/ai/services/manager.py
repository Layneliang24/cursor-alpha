"""
AI服务管理器

负责AI服务的动态管理、热插拔和统一调度
"""

import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading

from django.conf import settings
from django.core.cache import cache

from ..adapters import (
    BaseAIAdapter, AIAdapterFactory, AIProviderType, 
    AIModelConfig, AIResponse, AIMessage, AIServiceException
)
from .load_balancer import LoadBalancer, LoadBalancingStrategy
from .health_monitor import HealthMonitor, ServiceHealth
from .key_manager import APIKeyManager
from .degradation import DegradationManager, ServiceLevel

logger = logging.getLogger(__name__)


@dataclass
class ServiceInstance:
    """AI服务实例配置"""
    provider: AIProviderType
    model: str
    config: AIModelConfig
    adapter: BaseAIAdapter
    weight: int = 1
    enabled: bool = True
    last_used: Optional[datetime] = None
    error_count: int = 0
    success_count: int = 0


class AIServiceManager:
    """
    AI服务管理器
    
    功能：
    1. AI模型的热插拔和动态切换
    2. 负载均衡和故障转移
    3. 服务健康监控
    4. API密钥管理
    5. 服务降级策略
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化管理器"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self._services: Dict[str, ServiceInstance] = {}
        self._load_balancer = LoadBalancer()
        self._health_monitor = HealthMonitor()
        self._key_manager = APIKeyManager()
        self._degradation_manager = DegradationManager()
        self._lock = threading.Lock()
        
        # 初始化服务
        self._initialize_services()
        
        # 启动健康监控
        self._start_health_monitoring()
    
    def _initialize_services(self):
        """从配置初始化AI服务"""
        try:
            # 从Django settings获取AI配置
            ai_config = getattr(settings, 'AI_SERVICES', {})
            
            for service_name, config in ai_config.items():
                try:
                    self._add_service_from_config(service_name, config)
                except Exception as e:
                    logger.error(f"初始化服务 {service_name} 失败: {e}")
                    
            # 如果没有配置，添加默认服务
            if not self._services:
                self._add_default_services()
                
        except Exception as e:
            logger.error(f"初始化AI服务失败: {e}")
            self._add_default_services()
    
    def _add_service_from_config(self, service_name: str, config: dict):
        """从配置添加服务"""
        provider = AIProviderType(config.get('provider', 'openai'))
        model = config.get('model', 'gpt-3.5-turbo')
        
        # 获取API密钥
        api_key = self._key_manager.get_key(provider)
        if not api_key:
            logger.warning(f"服务 {service_name} 缺少API密钥")
            return
        
        # 创建模型配置
        model_config = AIModelConfig(
            model=model,
            api_key=api_key,
            max_tokens=config.get('max_tokens', 4000),
            temperature=config.get('temperature', 0.7),
            top_p=config.get('top_p', 1.0),
            timeout=config.get('timeout', 30)
        )
        
        # 创建适配器
        adapter = AIAdapterFactory.create_adapter(provider, model_config)
        
        # 创建服务实例
        service_instance = ServiceInstance(
            provider=provider,
            model=model,
            config=model_config,
            adapter=adapter,
            weight=config.get('weight', 1),
            enabled=config.get('enabled', True)
        )
        
        self._services[service_name] = service_instance
        logger.info(f"添加AI服务: {service_name} ({provider.value}/{model})")
    
    def _add_default_services(self):
        """添加默认服务配置"""
        default_configs = [
            {
                'name': 'openai-gpt4',
                'provider': 'openai',
                'model': 'gpt-4',
                'weight': 3,
                'enabled': True
            },
            {
                'name': 'openai-gpt35',
                'provider': 'openai', 
                'model': 'gpt-3.5-turbo',
                'weight': 2,
                'enabled': True
            },
            {
                'name': 'claude-sonnet',
                'provider': 'anthropic',
                'model': 'claude-3-sonnet-20240229',
                'weight': 3,
                'enabled': True
            }
        ]
        
        for config in default_configs:
            try:
                self._add_service_from_config(config['name'], config)
            except Exception as e:
                logger.warning(f"添加默认服务 {config['name']} 失败: {e}")
    
    def _start_health_monitoring(self):
        """启动健康监控"""
        def monitor_loop():
            while True:
                try:
                    self._check_all_services_health()
                    time.sleep(60)  # 每分钟检查一次
                except Exception as e:
                    logger.error(f"健康监控异常: {e}")
                    time.sleep(30)
        
        # 在后台线程运行监控
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("AI服务健康监控已启动")
    
    def _check_all_services_health(self):
        """检查所有服务健康状态"""
        for service_name, service in self._services.items():
            if service.enabled:
                try:
                    health = service.adapter.health_check()
                    self._health_monitor.update_health(service_name, health)
                    
                    if not health.is_healthy:
                        logger.warning(f"服务 {service_name} 健康检查失败: {health.error}")
                        self._handle_unhealthy_service(service_name, service)
                        
                except Exception as e:
                    logger.error(f"检查服务 {service_name} 健康状态失败: {e}")
                    self._handle_unhealthy_service(service_name, service)
    
    def _handle_unhealthy_service(self, service_name: str, service: ServiceInstance):
        """处理不健康的服务"""
        service.error_count += 1
        
        # 连续失败超过阈值，暂时禁用服务
        if service.error_count >= 3:
            service.enabled = False
            logger.warning(f"服务 {service_name} 连续失败，已暂时禁用")
            
            # 5分钟后重新启用
            def re_enable():
                time.sleep(300)
                service.enabled = True
                service.error_count = 0
                logger.info(f"服务 {service_name} 已重新启用")
            
            threading.Thread(target=re_enable, daemon=True).start()
    
    async def generate_response(
        self,
        messages: List[AIMessage],
        service_name: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """
        生成AI响应
        
        Args:
            messages: 消息列表
            service_name: 指定服务名称，None时使用负载均衡
            **kwargs: 其他参数
            
        Returns:
            AI响应结果
        """
        # 选择服务
        if service_name:
            service = self._get_service(service_name)
            if not service:
                raise AIServiceException(f"服务 {service_name} 不存在或不可用")
        else:
            service = self._select_best_service()
            if not service:
                raise AIServiceException("没有可用的AI服务")
        
        # 检查服务降级
        current_level = self._degradation_manager.get_current_level()
        if current_level != ServiceLevel.NORMAL:
            kwargs = self._apply_degradation_settings(kwargs, current_level)
        
        try:
            # 生成响应
            response = await service.adapter.generate_response(messages, **kwargs)
            
            # 更新服务统计
            service.success_count += 1
            service.last_used = datetime.now()
            service.error_count = max(0, service.error_count - 1)  # 成功时减少错误计数
            
            return response
            
        except Exception as e:
            # 处理服务错误
            service.error_count += 1
            logger.error(f"服务 {service.provider.value}/{service.model} 生成响应失败: {e}")
            
            # 尝试故障转移
            if not service_name:  # 只有在负载均衡模式下才进行故障转移
                return await self._failover_response(messages, service, **kwargs)
            else:
                raise
    
    async def stream_response(
        self,
        messages: List[AIMessage],
        service_name: Optional[str] = None,
        **kwargs
    ):
        """
        流式生成AI响应
        
        Args:
            messages: 消息列表
            service_name: 指定服务名称，None时使用负载均衡
            **kwargs: 其他参数
            
        Yields:
            AI响应流
        """
        # 选择服务
        if service_name:
            service = self._get_service(service_name)
            if not service:
                raise AIServiceException(f"服务 {service_name} 不存在或不可用")
        else:
            service = self._select_best_service()
            if not service:
                raise AIServiceException("没有可用的AI服务")
        
        # 检查服务降级
        current_level = self._degradation_manager.get_current_level()
        if current_level != ServiceLevel.NORMAL:
            kwargs = self._apply_degradation_settings(kwargs, current_level)
        
        try:
            # 流式响应
            async for chunk in service.adapter.stream_response(messages, **kwargs):
                yield chunk
                
            # 更新服务统计
            service.success_count += 1
            service.last_used = datetime.now()
            service.error_count = max(0, service.error_count - 1)
            
        except Exception as e:
            service.error_count += 1
            logger.error(f"服务 {service.provider.value}/{service.model} 流式响应失败: {e}")
            raise
    
    def _get_service(self, service_name: str) -> Optional[ServiceInstance]:
        """获取指定服务"""
        service = self._services.get(service_name)
        if service and service.enabled:
            return service
        return None
    
    def _select_best_service(self) -> Optional[ServiceInstance]:
        """选择最佳服务（负载均衡）"""
        # 获取可用服务
        available_services = [
            (name, service) for name, service in self._services.items()
            if service.enabled and self._is_service_healthy(name)
        ]
        
        if not available_services:
            return None
        
        # 使用负载均衡器选择服务
        service_weights = {name: service.weight for name, service in available_services}
        selected_name = self._load_balancer.select_service(service_weights)
        
        return self._services[selected_name]
    
    def _is_service_healthy(self, service_name: str) -> bool:
        """检查服务是否健康"""
        health = self._health_monitor.get_health(service_name)
        return health.is_healthy if health else True
    
    async def _failover_response(
        self,
        messages: List[AIMessage],
        failed_service: ServiceInstance,
        **kwargs
    ) -> AIResponse:
        """故障转移处理"""
        logger.warning(f"服务 {failed_service.provider.value}/{failed_service.model} 故障，尝试转移")
        
        # 获取其他可用服务
        available_services = [
            service for name, service in self._services.items()
            if service != failed_service and service.enabled and self._is_service_healthy(name)
        ]
        
        if not available_services:
            raise AIServiceException("所有AI服务都不可用")
        
        # 按权重排序，选择最佳备用服务
        available_services.sort(key=lambda s: s.weight, reverse=True)
        backup_service = available_services[0]
        
        try:
            response = await backup_service.adapter.generate_response(messages, **kwargs)
            logger.info(f"故障转移成功，使用服务: {backup_service.provider.value}/{backup_service.model}")
            
            # 更新统计
            backup_service.success_count += 1
            backup_service.last_used = datetime.now()
            
            return response
            
        except Exception as e:
            logger.error(f"故障转移失败: {e}")
            raise AIServiceException("故障转移失败，所有服务都不可用")
    
    def _apply_degradation_settings(self, kwargs: dict, level: ServiceLevel) -> dict:
        """应用服务降级设置"""
        degraded_kwargs = kwargs.copy()
        
        if level == ServiceLevel.DEGRADED:
            # 降级设置：减少token，提高速度
            degraded_kwargs['max_tokens'] = min(kwargs.get('max_tokens', 4000), 2000)
            degraded_kwargs['temperature'] = min(kwargs.get('temperature', 0.7), 0.3)
            
        elif level == ServiceLevel.MINIMAL:
            # 最小化设置：大幅减少token
            degraded_kwargs['max_tokens'] = min(kwargs.get('max_tokens', 4000), 500)
            degraded_kwargs['temperature'] = 0.1
            
        return degraded_kwargs
    
    def add_service(
        self,
        service_name: str,
        provider: AIProviderType,
        model: str,
        config: Optional[Dict[str, Any]] = None,
        weight: int = 1
    ) -> bool:
        """
        动态添加AI服务
        
        Args:
            service_name: 服务名称
            provider: AI提供商
            model: 模型名称
            config: 模型配置
            weight: 负载均衡权重
            
        Returns:
            是否添加成功
        """
        try:
            with self._lock:
                # 检查服务是否已存在
                if service_name in self._services:
                    logger.warning(f"服务 {service_name} 已存在")
                    return False
                
                # 获取API密钥
                api_key = self._key_manager.get_key(provider)
                if not api_key:
                    logger.error(f"服务 {service_name} 缺少API密钥")
                    return False
                
                # 创建模型配置
                model_config = AIModelConfig(
                    model=model,
                    api_key=api_key,
                    **(config or {})
                )
                
                # 创建适配器
                adapter = AIAdapterFactory.create_adapter(provider, model_config)
                
                # 创建服务实例
                service_instance = ServiceInstance(
                    provider=provider,
                    model=model,
                    config=model_config,
                    adapter=adapter,
                    weight=weight
                )
                
                self._services[service_name] = service_instance
                logger.info(f"成功添加AI服务: {service_name}")
                return True
                
        except Exception as e:
            logger.error(f"添加服务 {service_name} 失败: {e}")
            return False
    
    def remove_service(self, service_name: str) -> bool:
        """
        移除AI服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            是否移除成功
        """
        try:
            with self._lock:
                if service_name not in self._services:
                    logger.warning(f"服务 {service_name} 不存在")
                    return False
                
                del self._services[service_name]
                logger.info(f"成功移除AI服务: {service_name}")
                return True
                
        except Exception as e:
            logger.error(f"移除服务 {service_name} 失败: {e}")
            return False
    
    def enable_service(self, service_name: str) -> bool:
        """启用服务"""
        service = self._services.get(service_name)
        if service:
            service.enabled = True
            logger.info(f"启用服务: {service_name}")
            return True
        return False
    
    def disable_service(self, service_name: str) -> bool:
        """禁用服务"""
        service = self._services.get(service_name)
        if service:
            service.enabled = False
            logger.info(f"禁用服务: {service_name}")
            return True
        return False
    
    def update_service_weight(self, service_name: str, weight: int) -> bool:
        """更新服务权重"""
        service = self._services.get(service_name)
        if service:
            service.weight = weight
            logger.info(f"更新服务 {service_name} 权重: {weight}")
            return True
        return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取所有服务状态"""
        status = {}
        
        for service_name, service in self._services.items():
            health = self._health_monitor.get_health(service_name)
            
            status[service_name] = {
                'provider': service.provider.value,
                'model': service.model,
                'enabled': service.enabled,
                'weight': service.weight,
                'success_count': service.success_count,
                'error_count': service.error_count,
                'last_used': service.last_used.isoformat() if service.last_used else None,
                'health': {
                    'is_healthy': health.is_healthy if health else None,
                    'response_time': health.response_time if health else None,
                    'last_check': health.last_check.isoformat() if health and health.last_check else None,
                    'error': health.error if health else None
                }
            }
        
        return status
    
    def get_load_balancer_stats(self) -> Dict[str, Any]:
        """获取负载均衡统计"""
        return self._load_balancer.get_stats()
    
    def set_load_balancing_strategy(self, strategy: LoadBalancingStrategy):
        """设置负载均衡策略"""
        self._load_balancer.set_strategy(strategy)
        logger.info(f"负载均衡策略已更新: {strategy.value}")
    
    def get_degradation_status(self) -> Dict[str, Any]:
        """获取服务降级状态"""
        return {
            'current_level': self._degradation_manager.get_current_level().value,
            'metrics': self._degradation_manager.get_metrics(),
            'thresholds': self._degradation_manager.get_thresholds()
        }
    
    def force_degradation(self, level: ServiceLevel):
        """强制设置降级级别"""
        self._degradation_manager.force_degradation(level)
        logger.warning(f"强制设置服务降级级别: {level.value}")
    
    def clear_degradation(self):
        """清除降级设置"""
        self._degradation_manager.clear_degradation()
        logger.info("服务降级已清除")


# 全局服务管理器实例
ai_service_manager = AIServiceManager()
