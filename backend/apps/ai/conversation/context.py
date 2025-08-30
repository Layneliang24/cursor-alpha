"""
对话上下文管理

处理对话历史、上下文压缩和token估算
"""

import re
import time
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field

from django.contrib.auth.models import User

from ..adapters.base import AIMessage, MessageRole

logger = logging.getLogger(__name__)


@dataclass
class ConversationContext:
    """对话上下文"""
    conversation_id: str
    title: str
    created_at: datetime
    user: Optional[User] = None
    system_prompt: Optional[str] = None
    messages: List[AIMessage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 状态信息
    last_activity: Optional[datetime] = None
    last_saved: Optional[datetime] = None
    last_compression: Optional[datetime] = None
    compression_count: int = 0
    
    # 质量评估
    quality_scores: List[float] = field(default_factory=list)
    user_rating: Optional[int] = None
    user_feedback: Optional[str] = None
    rating_time: Optional[datetime] = None
    
    @property
    def estimated_tokens(self) -> int:
        """估算token数量"""
        total_tokens = 0
        for message in self.messages:
            # 简单的token估算：1个token约等于4个字符
            total_tokens += len(message.content) // 4
        return total_tokens
    
    @property
    def message_count(self) -> int:
        """消息数量"""
        return len(self.messages)
    
    @property
    def user_message_count(self) -> int:
        """用户消息数量"""
        return sum(1 for msg in self.messages if msg.role == MessageRole.USER)
    
    @property
    def assistant_message_count(self) -> int:
        """助手消息数量"""
        return sum(1 for msg in self.messages if msg.role == MessageRole.ASSISTANT)
    
    def add_message(self, message: AIMessage):
        """添加消息"""
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def add_quality_score(self, score: float):
        """添加质量评分"""
        if 0.0 <= score <= 1.0:
            self.quality_scores.append(score)
    
    def get_messages_for_ai(
        self,
        include_system: bool = True,
        max_messages: Optional[int] = None
    ) -> List[AIMessage]:
        """
        获取用于AI的消息列表
        
        Args:
            include_system: 是否包含系统消息
            max_messages: 最大消息数量
            
        Returns:
            消息列表
        """
        messages = self.messages.copy()
        
        if not include_system:
            messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
        
        if max_messages and len(messages) > max_messages:
            # 保留系统消息（如果需要）和最近的消息
            system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
            other_messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
            
            if include_system and system_messages:
                # 保留系统消息和最近的其他消息
                recent_count = max_messages - len(system_messages)
                if recent_count > 0:
                    messages = system_messages + other_messages[-recent_count:]
                else:
                    messages = system_messages[:max_messages]
            else:
                messages = other_messages[-max_messages:]
        
        return messages
    
    def get_recent_messages(self, count: int) -> List[AIMessage]:
        """获取最近的消息"""
        return self.messages[-count:] if count < len(self.messages) else self.messages
    
    def get_messages_by_role(self, role: MessageRole) -> List[AIMessage]:
        """按角色获取消息"""
        return [msg for msg in self.messages if msg.role == role]
    
    def clear_messages(self, keep_system: bool = True):
        """清空消息"""
        if keep_system:
            system_messages = [msg for msg in self.messages if msg.role == MessageRole.SYSTEM]
            self.messages = system_messages
        else:
            self.messages = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'conversation_id': self.conversation_id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user.id if self.user else None,
            'system_prompt': self.system_prompt,
            'messages': [
                {
                    'role': msg.role.value,
                    'content': msg.content,
                    'timestamp': datetime.fromtimestamp(getattr(msg, 'timestamp', time.time())).isoformat()
                }
                for msg in self.messages
            ],
            'metadata': self.metadata,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'last_saved': self.last_saved.isoformat() if self.last_saved else None,
            'last_compression': self.last_compression.isoformat() if self.last_compression else None,
            'compression_count': self.compression_count,
            'quality_scores': self.quality_scores,
            'user_rating': self.user_rating,
            'user_feedback': self.user_feedback,
            'rating_time': self.rating_time.isoformat() if self.rating_time else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """从字典创建"""
        from django.contrib.auth.models import User
        
        # 获取用户
        user = None
        if data.get('user_id'):
            try:
                user = User.objects.get(id=data['user_id'])
            except User.DoesNotExist:
                pass
        
        # 创建消息
        messages = []
        for msg_data in data.get('messages', []):
            message = AIMessage(
                role=MessageRole(msg_data['role']),
                content=msg_data['content']
            )
            if 'timestamp' in msg_data:
                message.timestamp = datetime.fromisoformat(msg_data['timestamp'])
            messages.append(message)
        
        return cls(
            conversation_id=data['conversation_id'],
            title=data['title'],
            created_at=datetime.fromisoformat(data['created_at']),
            user=user,
            system_prompt=data.get('system_prompt'),
            messages=messages,
            metadata=data.get('metadata', {}),
            last_activity=datetime.fromisoformat(data['last_activity']) if data.get('last_activity') else None,
            last_saved=datetime.fromisoformat(data['last_saved']) if data.get('last_saved') else None,
            last_compression=datetime.fromisoformat(data['last_compression']) if data.get('last_compression') else None,
            compression_count=data.get('compression_count', 0),
            quality_scores=data.get('quality_scores', []),
            user_rating=data.get('user_rating'),
            user_feedback=data.get('user_feedback'),
            rating_time=datetime.fromisoformat(data['rating_time']) if data.get('rating_time') else None,
        )


class ContextCompressor:
    """
    上下文压缩器
    
    智能压缩对话历史，在保持重要信息的同时减少token使用
    """
    
    def __init__(self):
        """初始化压缩器"""
        self.compression_strategies = {
            'simple_truncate': self._simple_truncate,
            'smart_summarize': self._smart_summarize,
            'importance_based': self._importance_based_compression,
        }
        self.default_strategy = 'importance_based'
    
    async def compress(
        self,
        messages: List[AIMessage],
        target_length: int,
        strategy: str = None,
        preserve_system: bool = True,
        preserve_recent: int = 5
    ) -> List[AIMessage]:
        """
        压缩消息列表
        
        Args:
            messages: 原始消息列表
            target_length: 目标token长度
            strategy: 压缩策略
            preserve_system: 保留系统消息
            preserve_recent: 保留最近N条消息
            
        Returns:
            压缩后的消息列表
        """
        if not messages:
            return messages
        
        # 选择压缩策略
        strategy = strategy or self.default_strategy
        compress_func = self.compression_strategies.get(strategy, self._importance_based_compression)
        
        try:
            compressed = await compress_func(
                messages, target_length, preserve_system, preserve_recent
            )
            
            logger.info(f"上下文压缩完成: {len(messages)} -> {len(compressed)} 条消息")
            return compressed
            
        except Exception as e:
            logger.error(f"上下文压缩失败: {e}")
            # 回退到简单截断
            return await self._simple_truncate(
                messages, target_length, preserve_system, preserve_recent
            )
    
    async def _simple_truncate(
        self,
        messages: List[AIMessage],
        target_length: int,
        preserve_system: bool,
        preserve_recent: int
    ) -> List[AIMessage]:
        """简单截断策略"""
        if len(messages) <= preserve_recent:
            return messages
        
        # 分离系统消息和其他消息
        system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM] if preserve_system else []
        other_messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
        
        # 保留最近的消息
        recent_messages = other_messages[-preserve_recent:] if preserve_recent > 0 else []
        
        # 组合结果
        result = system_messages + recent_messages
        
        # 检查token长度
        current_tokens = self._estimate_tokens(result)
        if current_tokens <= target_length:
            return result
        
        # 如果仍然超长，进一步截断
        while result and self._estimate_tokens(result) > target_length:
            # 从非系统消息中删除最旧的
            for i, msg in enumerate(result):
                if msg.role != MessageRole.SYSTEM:
                    result.pop(i)
                    break
        
        return result
    
    async def _smart_summarize(
        self,
        messages: List[AIMessage],
        target_length: int,
        preserve_system: bool,
        preserve_recent: int
    ) -> List[AIMessage]:
        """智能摘要策略"""
        # TODO: 实现使用AI进行智能摘要
        # 这里先使用简单截断作为占位符
        return await self._simple_truncate(messages, target_length, preserve_system, preserve_recent)
    
    async def _importance_based_compression(
        self,
        messages: List[AIMessage],
        target_length: int,
        preserve_system: bool,
        preserve_recent: int
    ) -> List[AIMessage]:
        """基于重要性的压缩策略"""
        if len(messages) <= preserve_recent:
            return messages
        
        # 分离不同类型的消息
        system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM] if preserve_system else []
        other_messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
        
        # 计算消息重要性
        message_scores = []
        for i, msg in enumerate(other_messages):
            score = self._calculate_message_importance(msg, i, len(other_messages))
            message_scores.append((score, i, msg))
        
        # 按重要性排序
        message_scores.sort(key=lambda x: x[0], reverse=True)
        
        # 选择重要消息
        selected_messages = []
        current_tokens = self._estimate_tokens(system_messages)
        
        # 首先添加最近的消息
        recent_messages = other_messages[-preserve_recent:] if preserve_recent > 0 else []
        for msg in recent_messages:
            tokens = self._estimate_tokens([msg])
            if current_tokens + tokens <= target_length:
                selected_messages.append(msg)
                current_tokens += tokens
        
        # 添加重要的历史消息
        recent_indices = set(range(len(other_messages) - preserve_recent, len(other_messages)))
        for score, index, msg in message_scores:
            if index not in recent_indices:  # 避免重复添加最近的消息
                tokens = self._estimate_tokens([msg])
                if current_tokens + tokens <= target_length:
                    selected_messages.append(msg)
                    current_tokens += tokens
                else:
                    break
        
        # 按原始顺序排序
        selected_messages.sort(key=lambda msg: other_messages.index(msg))
        
        return system_messages + selected_messages
    
    def _calculate_message_importance(self, message: AIMessage, index: int, total: int) -> float:
        """
        计算消息重要性
        
        Args:
            message: 消息对象
            index: 消息索引
            total: 总消息数
            
        Returns:
            重要性分数 (0-1)
        """
        score = 0.0
        content = message.content.lower()
        
        # 基础分数：角色重要性
        if message.role == MessageRole.SYSTEM:
            score += 0.9
        elif message.role == MessageRole.USER:
            score += 0.6
        elif message.role == MessageRole.ASSISTANT:
            score += 0.7
        
        # 位置权重：最近的消息更重要
        position_weight = (index + 1) / total
        score += position_weight * 0.3
        
        # 内容长度：适中长度的消息可能更重要
        content_length = len(content)
        if 50 <= content_length <= 500:
            score += 0.2
        elif content_length > 500:
            score += 0.1
        
        # 关键词权重
        important_keywords = [
            '问题', '解决', '错误', '重要', '关键', '注意',
            'error', 'important', 'key', 'problem', 'solution'
        ]
        
        for keyword in important_keywords:
            if keyword in content:
                score += 0.1
                break
        
        # 问号权重：问题通常比较重要
        if '?' in content or '？' in content:
            score += 0.1
        
        # 代码块权重：包含代码的消息可能更重要
        if '```' in content or '`' in content:
            score += 0.15
        
        return min(score, 1.0)  # 限制在0-1范围内
    
    def _estimate_tokens(self, messages: List[AIMessage]) -> int:
        """估算token数量"""
        total_tokens = 0
        for message in messages:
            # 简单估算：1个token约等于4个字符
            total_tokens += len(message.content) // 4
        return total_tokens
    
    def get_compression_stats(
        self,
        original_messages: List[AIMessage],
        compressed_messages: List[AIMessage]
    ) -> Dict[str, Any]:
        """获取压缩统计信息"""
        original_count = len(original_messages)
        compressed_count = len(compressed_messages)
        original_tokens = self._estimate_tokens(original_messages)
        compressed_tokens = self._estimate_tokens(compressed_messages)
        
        return {
            'original_message_count': original_count,
            'compressed_message_count': compressed_count,
            'message_reduction_ratio': (original_count - compressed_count) / original_count if original_count > 0 else 0,
            'original_token_count': original_tokens,
            'compressed_token_count': compressed_tokens,
            'token_reduction_ratio': (original_tokens - compressed_tokens) / original_tokens if original_tokens > 0 else 0,
            'compression_efficiency': compressed_tokens / original_tokens if original_tokens > 0 else 0
        }
