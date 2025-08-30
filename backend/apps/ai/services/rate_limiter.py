"""
AI服务速率限制系统

实现用户级别和全局级别的API调用限制，防止滥用和成本失控
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class LimitType(Enum):
    """限制类型"""
    USER_PER_MINUTE = "user_per_minute"       # 用户每分钟限制
    USER_PER_HOUR = "user_per_hour"           # 用户每小时限制
    USER_PER_DAY = "user_per_day"             # 用户每日限制
    GLOBAL_PER_MINUTE = "global_per_minute"   # 全局每分钟限制
    GLOBAL_PER_HOUR = "global_per_hour"       # 全局每小时限制
    GLOBAL_PER_DAY = "global_per_day"         # 全局每日限制
    FUNCTION_PER_HOUR = "function_per_hour"   # 功能每小时限制


@dataclass
class RateLimit:
    """速率限制配置"""
    limit_type: LimitType
    max_requests: int
    window_seconds: int
    burst_capacity: Optional[int] = None  # 突发容量
    
    
@dataclass
class LimitResult:
    """限制检查结果"""
    allowed: bool
    remaining: int
    reset_time: datetime
    retry_after: Optional[int] = None
    limit_type: Optional[LimitType] = None
    

class TokenBucket:
    """令牌桶算法实现"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        初始化令牌桶
        
        Args:
            capacity: 桶容量
            refill_rate: 每秒填充速率
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        消费令牌
        
        Args:
            tokens: 消费的令牌数
            
        Returns:
            是否成功消费
        """
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """填充令牌"""
        now = time.time()
        elapsed = now - self.last_refill
        
        # 计算应添加的令牌数
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def get_remaining(self) -> int:
        """获取剩余令牌数"""
        self._refill()
        return int(self.tokens)


class RateLimiter:
    """
    速率限制器
    
    实现用户级别和全局级别的API调用限制
    """
    
    def __init__(self):
        """初始化速率限制器"""
        # 加载限制配置
        self.limits = self._load_rate_limits()
        
        # 令牌桶缓存
        self.token_buckets: Dict[str, TokenBucket] = {}
        
        # 缓存过期时间
        self.cache_timeout = 86400  # 24小时
        
        logger.info("速率限制器已初始化")
    
    def _load_rate_limits(self) -> Dict[LimitType, RateLimit]:
        """加载速率限制配置"""
        default_limits = {
            LimitType.USER_PER_MINUTE: RateLimit(
                LimitType.USER_PER_MINUTE, 10, 60, 15
            ),
            LimitType.USER_PER_HOUR: RateLimit(
                LimitType.USER_PER_HOUR, 100, 3600, 150
            ),
            LimitType.USER_PER_DAY: RateLimit(
                LimitType.USER_PER_DAY, 500, 86400, 750
            ),
            LimitType.GLOBAL_PER_MINUTE: RateLimit(
                LimitType.GLOBAL_PER_MINUTE, 1000, 60, 1500
            ),
            LimitType.GLOBAL_PER_HOUR: RateLimit(
                LimitType.GLOBAL_PER_HOUR, 10000, 3600, 15000
            ),
            LimitType.GLOBAL_PER_DAY: RateLimit(
                LimitType.GLOBAL_PER_DAY, 100000, 86400, 150000
            ),
            LimitType.FUNCTION_PER_HOUR: RateLimit(
                LimitType.FUNCTION_PER_HOUR, 50, 3600, 75
            ),
        }
        
        # 从settings中获取自定义配置
        custom_limits = getattr(settings, 'AI_RATE_LIMITS', {})
        
        for limit_type, config in custom_limits.items():
            if hasattr(LimitType, limit_type):
                limit_enum = getattr(LimitType, limit_type)
                default_limits[limit_enum] = RateLimit(
                    limit_enum,
                    config['max_requests'],
                    config['window_seconds'],
                    config.get('burst_capacity')
                )
        
        return default_limits
    
    async def check_limit(
        self,
        user_id: int,
        action: str,
        window_seconds: int = 3600,
        max_requests: int = 100
    ) -> bool:
        """
        检查速率限制（简化接口）
        
        Args:
            user_id: 用户ID
            action: 操作类型
            window_seconds: 时间窗口（秒）
            max_requests: 最大请求数
            
        Returns:
            是否允许请求
        """
        result = await self.check_all_limits(user_id, action)
        return result.allowed
    
    async def check_all_limits(
        self,
        user_id: int,
        action: str,
        function_type: Optional[str] = None
    ) -> LimitResult:
        """
        检查所有应用的速率限制
        
        Args:
            user_id: 用户ID
            action: 操作类型
            function_type: 功能类型
            
        Returns:
            限制检查结果
        """
        # 按优先级检查各种限制
        checks = [
            (LimitType.USER_PER_MINUTE, f"user:{user_id}"),
            (LimitType.USER_PER_HOUR, f"user:{user_id}"),
            (LimitType.USER_PER_DAY, f"user:{user_id}"),
            (LimitType.GLOBAL_PER_MINUTE, "global"),
            (LimitType.GLOBAL_PER_HOUR, "global"),
            (LimitType.GLOBAL_PER_DAY, "global"),
        ]
        
        # 如果指定了功能类型，也检查功能限制
        if function_type:
            checks.append((LimitType.FUNCTION_PER_HOUR, f"function:{function_type}:{user_id}"))
        
        for limit_type, key_prefix in checks:
            result = await self._check_single_limit(limit_type, key_prefix, action)
            if not result.allowed:
                return result
        
        # 所有检查都通过
        return LimitResult(
            allowed=True,
            remaining=float('inf'),
            reset_time=timezone.now() + timedelta(hours=1)
        )
    
    async def _check_single_limit(
        self,
        limit_type: LimitType,
        key_prefix: str,
        action: str
    ) -> LimitResult:
        """
        检查单个限制
        
        Args:
            limit_type: 限制类型
            key_prefix: 缓存键前缀
            action: 操作类型
            
        Returns:
            限制检查结果
        """
        limit_config = self.limits.get(limit_type)
        if not limit_config:
            return LimitResult(
                allowed=True,
                remaining=float('inf'),
                reset_time=timezone.now() + timedelta(hours=1)
            )
        
        # 生成缓存键
        cache_key = f"rate_limit:{limit_type.value}:{key_prefix}:{action}"
        
        # 使用令牌桶算法
        if limit_config.burst_capacity:
            return await self._check_token_bucket_limit(cache_key, limit_config)
        else:
            # 使用滑动窗口算法
            return await self._check_sliding_window_limit(cache_key, limit_config)
    
    async def _check_token_bucket_limit(
        self,
        cache_key: str,
        limit_config: RateLimit
    ) -> LimitResult:
        """使用令牌桶算法检查限制"""
        # 获取或创建令牌桶
        bucket = self.token_buckets.get(cache_key)
        if not bucket:
            refill_rate = limit_config.max_requests / limit_config.window_seconds
            bucket = TokenBucket(
                capacity=limit_config.burst_capacity or limit_config.max_requests,
                refill_rate=refill_rate
            )
            self.token_buckets[cache_key] = bucket
        
        # 尝试消费令牌
        if bucket.consume():
            return LimitResult(
                allowed=True,
                remaining=bucket.get_remaining(),
                reset_time=timezone.now() + timedelta(seconds=1/bucket.refill_rate),
                limit_type=limit_config.limit_type
            )
        else:
            # 计算重试时间
            retry_after = int(1 / bucket.refill_rate) + 1
            return LimitResult(
                allowed=False,
                remaining=0,
                reset_time=timezone.now() + timedelta(seconds=retry_after),
                retry_after=retry_after,
                limit_type=limit_config.limit_type
            )
    
    async def _check_sliding_window_limit(
        self,
        cache_key: str,
        limit_config: RateLimit
    ) -> LimitResult:
        """使用滑动窗口算法检查限制"""
        now = timezone.now()
        window_start = now - timedelta(seconds=limit_config.window_seconds)
        
        # 获取当前窗口内的请求记录
        requests_data = cache.get(cache_key, [])
        
        # 过滤过期的请求
        valid_requests = [
            req_time for req_time in requests_data
            if datetime.fromisoformat(req_time) > window_start
        ]
        
        # 检查是否超过限制
        if len(valid_requests) >= limit_config.max_requests:
            # 计算最早请求的过期时间
            earliest_request = min(valid_requests)
            reset_time = datetime.fromisoformat(earliest_request) + timedelta(
                seconds=limit_config.window_seconds
            )
            retry_after = int((reset_time - now).total_seconds()) + 1
            
            return LimitResult(
                allowed=False,
                remaining=0,
                reset_time=reset_time,
                retry_after=retry_after,
                limit_type=limit_config.limit_type
            )
        
        # 记录当前请求
        valid_requests.append(now.isoformat())
        cache.set(cache_key, valid_requests, self.cache_timeout)
        
        remaining = limit_config.max_requests - len(valid_requests)
        reset_time = now + timedelta(seconds=limit_config.window_seconds)
        
        return LimitResult(
            allowed=True,
            remaining=remaining,
            reset_time=reset_time,
            limit_type=limit_config.limit_type
        )
    
    async def get_user_limits_status(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户的限制状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            限制状态信息
        """
        status = {}
        
        for limit_type in [LimitType.USER_PER_MINUTE, LimitType.USER_PER_HOUR, LimitType.USER_PER_DAY]:
            result = await self._check_single_limit(
                limit_type, f"user:{user_id}", "status_check"
            )
            
            status[limit_type.value] = {
                'allowed': result.allowed,
                'remaining': result.remaining,
                'reset_time': result.reset_time.isoformat(),
                'max_requests': self.limits[limit_type].max_requests
            }
        
        return status
    
    async def get_global_limits_status(self) -> Dict[str, Any]:
        """
        获取全局限制状态
        
        Returns:
            全局限制状态信息
        """
        status = {}
        
        for limit_type in [LimitType.GLOBAL_PER_MINUTE, LimitType.GLOBAL_PER_HOUR, LimitType.GLOBAL_PER_DAY]:
            result = await self._check_single_limit(
                limit_type, "global", "status_check"
            )
            
            status[limit_type.value] = {
                'allowed': result.allowed,
                'remaining': result.remaining,
                'reset_time': result.reset_time.isoformat(),
                'max_requests': self.limits[limit_type].max_requests
            }
        
        return status
    
    async def reset_user_limits(self, user_id: int) -> bool:
        """
        重置用户的所有限制（管理员功能）
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否成功重置
        """
        try:
            # 清除用户相关的缓存键
            cache_patterns = [
                f"rate_limit:*user:{user_id}:*",
                f"rate_limit:*function:*:{user_id}:*"
            ]
            
            # 注意：这里需要根据实际的缓存后端实现清除逻辑
            # Django的默认缓存API不支持模式匹配删除
            
            # 清除令牌桶
            keys_to_remove = [
                key for key in self.token_buckets.keys()
                if f"user:{user_id}" in key
            ]
            for key in keys_to_remove:
                del self.token_buckets[key]
            
            logger.info(f"重置用户 {user_id} 的速率限制")
            return True
            
        except Exception as e:
            logger.error(f"重置用户限制失败: {e}")
            return False
    
    def add_custom_limit(
        self,
        limit_type: LimitType,
        max_requests: int,
        window_seconds: int,
        burst_capacity: Optional[int] = None
    ):
        """
        添加自定义限制
        
        Args:
            limit_type: 限制类型
            max_requests: 最大请求数
            window_seconds: 时间窗口
            burst_capacity: 突发容量
        """
        self.limits[limit_type] = RateLimit(
            limit_type, max_requests, window_seconds, burst_capacity
        )
        logger.info(f"添加自定义限制: {limit_type.value}")
    
    async def is_user_blocked(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        检查用户是否被阻止
        
        Args:
            user_id: 用户ID
            
        Returns:
            (是否被阻止, 阻止原因)
        """
        # 检查用户是否在黑名单中
        blacklist_key = f"rate_limit:blacklist:user:{user_id}"
        if cache.get(blacklist_key):
            return True, "用户已被加入黑名单"
        
        # 检查是否有活跃的限制违规
        for limit_type in [LimitType.USER_PER_MINUTE, LimitType.USER_PER_HOUR, LimitType.USER_PER_DAY]:
            result = await self._check_single_limit(
                limit_type, f"user:{user_id}", "block_check"
            )
            if not result.allowed and result.retry_after and result.retry_after > 300:  # 超过5分钟
                return True, f"违反{limit_type.value}限制"
        
        return False, None
    
    async def block_user(self, user_id: int, duration_seconds: int = 3600, reason: str = ""):
        """
        阻止用户访问
        
        Args:
            user_id: 用户ID
            duration_seconds: 阻止时长（秒）
            reason: 阻止原因
        """
        blacklist_key = f"rate_limit:blacklist:user:{user_id}"
        blacklist_data = {
            'blocked_at': timezone.now().isoformat(),
            'reason': reason,
            'duration': duration_seconds
        }
        cache.set(blacklist_key, blacklist_data, duration_seconds)
        
        logger.warning(f"用户 {user_id} 已被阻止 {duration_seconds}秒，原因: {reason}")

