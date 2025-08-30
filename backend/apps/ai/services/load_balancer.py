"""
负载均衡器

实现多种负载均衡算法，用于AI服务的请求分发
"""

import random
import time
import threading
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """负载均衡策略"""
    ROUND_ROBIN = "round_robin"          # 轮询
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"  # 加权轮询
    LEAST_CONNECTIONS = "least_connections"        # 最少连接
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"  # 加权最少连接
    RANDOM = "random"                    # 随机
    WEIGHTED_RANDOM = "weighted_random"  # 加权随机
    RESPONSE_TIME = "response_time"      # 响应时间优先


@dataclass
class ServiceStats:
    """服务统计信息"""
    name: str
    total_requests: int = 0
    active_connections: int = 0
    avg_response_time: float = 0.0
    last_request_time: float = 0.0
    success_rate: float = 1.0
    error_count: int = 0


@dataclass
class LoadBalancerConfig:
    """负载均衡器配置"""
    strategy: LoadBalancingStrategy = LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN
    health_check_interval: int = 60  # 秒
    max_retries: int = 3
    retry_delay: float = 1.0  # 秒
    connection_timeout: float = 30.0  # 秒


class LoadBalancer:
    """
    负载均衡器
    
    支持多种负载均衡算法，自动选择最优服务
    """
    
    def __init__(self, config: Optional[LoadBalancerConfig] = None):
        """初始化负载均衡器"""
        self.config = config or LoadBalancerConfig()
        self._strategy = self.config.strategy
        self._stats: Dict[str, ServiceStats] = {}
        self._round_robin_index = 0
        self._weighted_round_robin_state = {}
        self._lock = threading.Lock()
        
        # 响应时间记录
        self._response_times: Dict[str, List[float]] = defaultdict(list)
        self._max_response_samples = 100  # 保留最近100次响应时间
    
    def select_service(
        self,
        services: Dict[str, int],  # service_name -> weight
        exclude: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        选择服务
        
        Args:
            services: 可用服务及其权重
            exclude: 排除的服务列表
            
        Returns:
            选中的服务名称
        """
        if not services:
            return None
        
        # 过滤排除的服务
        if exclude:
            services = {name: weight for name, weight in services.items() if name not in exclude}
        
        if not services:
            return None
        
        # 根据策略选择服务
        with self._lock:
            if self._strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return self._round_robin_select(list(services.keys()))
            
            elif self._strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_select(services)
            
            elif self._strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return self._least_connections_select(list(services.keys()))
            
            elif self._strategy == LoadBalancingStrategy.WEIGHTED_LEAST_CONNECTIONS:
                return self._weighted_least_connections_select(services)
            
            elif self._strategy == LoadBalancingStrategy.RANDOM:
                return random.choice(list(services.keys()))
            
            elif self._strategy == LoadBalancingStrategy.WEIGHTED_RANDOM:
                return self._weighted_random_select(services)
            
            elif self._strategy == LoadBalancingStrategy.RESPONSE_TIME:
                return self._response_time_select(list(services.keys()))
            
            else:
                # 默认使用加权轮询
                return self._weighted_round_robin_select(services)
    
    def _round_robin_select(self, service_names: List[str]) -> str:
        """轮询选择"""
        if not service_names:
            return None
        
        selected = service_names[self._round_robin_index % len(service_names)]
        self._round_robin_index += 1
        return selected
    
    def _weighted_round_robin_select(self, services: Dict[str, int]) -> str:
        """加权轮询选择"""
        if not services:
            return None
        
        # 初始化权重状态
        for service_name, weight in services.items():
            if service_name not in self._weighted_round_robin_state:
                self._weighted_round_robin_state[service_name] = {
                    'current_weight': 0,
                    'effective_weight': weight,
                    'weight': weight
                }
        
        # 清理不存在的服务
        existing_services = set(services.keys())
        self._weighted_round_robin_state = {
            name: state for name, state in self._weighted_round_robin_state.items()
            if name in existing_services
        }
        
        # 加权轮询算法
        total_weight = 0
        best_service = None
        
        for service_name in services:
            state = self._weighted_round_robin_state[service_name]
            
            # 增加当前权重
            state['current_weight'] += state['effective_weight']
            total_weight += state['effective_weight']
            
            # 选择权重最高的服务
            if best_service is None or state['current_weight'] > self._weighted_round_robin_state[best_service]['current_weight']:
                best_service = service_name
        
        if best_service:
            # 减少选中服务的当前权重
            self._weighted_round_robin_state[best_service]['current_weight'] -= total_weight
        
        return best_service
    
    def _least_connections_select(self, service_names: List[str]) -> str:
        """最少连接选择"""
        if not service_names:
            return None
        
        min_connections = float('inf')
        selected_service = None
        
        for service_name in service_names:
            stats = self._get_service_stats(service_name)
            if stats.active_connections < min_connections:
                min_connections = stats.active_connections
                selected_service = service_name
        
        return selected_service or service_names[0]
    
    def _weighted_least_connections_select(self, services: Dict[str, int]) -> str:
        """加权最少连接选择"""
        if not services:
            return None
        
        min_ratio = float('inf')
        selected_service = None
        
        for service_name, weight in services.items():
            stats = self._get_service_stats(service_name)
            # 连接数与权重的比率
            ratio = stats.active_connections / max(weight, 1)
            
            if ratio < min_ratio:
                min_ratio = ratio
                selected_service = service_name
        
        return selected_service or list(services.keys())[0]
    
    def _weighted_random_select(self, services: Dict[str, int]) -> str:
        """加权随机选择"""
        if not services:
            return None
        
        # 构建权重列表
        choices = []
        weights = []
        
        for service_name, weight in services.items():
            choices.append(service_name)
            weights.append(weight)
        
        # 加权随机选择
        return random.choices(choices, weights=weights)[0]
    
    def _response_time_select(self, service_names: List[str]) -> str:
        """响应时间优先选择"""
        if not service_names:
            return None
        
        min_response_time = float('inf')
        selected_service = None
        
        for service_name in service_names:
            stats = self._get_service_stats(service_name)
            if stats.avg_response_time < min_response_time:
                min_response_time = stats.avg_response_time
                selected_service = service_name
        
        return selected_service or service_names[0]
    
    def _get_service_stats(self, service_name: str) -> ServiceStats:
        """获取服务统计"""
        if service_name not in self._stats:
            self._stats[service_name] = ServiceStats(name=service_name)
        return self._stats[service_name]
    
    def record_request_start(self, service_name: str):
        """记录请求开始"""
        with self._lock:
            stats = self._get_service_stats(service_name)
            stats.active_connections += 1
            stats.total_requests += 1
            stats.last_request_time = time.time()
    
    def record_request_end(
        self,
        service_name: str,
        response_time: float,
        success: bool = True
    ):
        """记录请求结束"""
        with self._lock:
            stats = self._get_service_stats(service_name)
            stats.active_connections = max(0, stats.active_connections - 1)
            
            # 更新响应时间
            response_times = self._response_times[service_name]
            response_times.append(response_time)
            
            # 保持最近的样本数量
            if len(response_times) > self._max_response_samples:
                response_times.pop(0)
            
            # 计算平均响应时间
            stats.avg_response_time = sum(response_times) / len(response_times)
            
            # 更新成功率
            if not success:
                stats.error_count += 1
            
            total_attempts = stats.total_requests
            success_attempts = total_attempts - stats.error_count
            stats.success_rate = success_attempts / total_attempts if total_attempts > 0 else 1.0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取负载均衡统计"""
        with self._lock:
            return {
                'strategy': self._strategy.value,
                'services': {
                    name: {
                        'total_requests': stats.total_requests,
                        'active_connections': stats.active_connections,
                        'avg_response_time': round(stats.avg_response_time, 3),
                        'success_rate': round(stats.success_rate, 3),
                        'error_count': stats.error_count,
                        'last_request_time': stats.last_request_time
                    }
                    for name, stats in self._stats.items()
                }
            }
    
    def set_strategy(self, strategy: LoadBalancingStrategy):
        """设置负载均衡策略"""
        with self._lock:
            self._strategy = strategy
            # 重置状态
            self._round_robin_index = 0
            self._weighted_round_robin_state.clear()
            logger.info(f"负载均衡策略已更新: {strategy.value}")
    
    def reset_stats(self):
        """重置统计信息"""
        with self._lock:
            self._stats.clear()
            self._response_times.clear()
            self._round_robin_index = 0
            self._weighted_round_robin_state.clear()
            logger.info("负载均衡统计已重置")
