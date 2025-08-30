"""
对话管理器

负责对话的创建、维护、上下文管理和流式响应处理
"""

import uuid
import logging
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User

from ..adapters.base import AIMessage, MessageRole, AIResponse
from ..services.manager import ai_service_manager
from .context import ConversationContext, ContextCompressor
from .streaming import ResponseStreamer
from .storage import ConversationStorage
from .quality import QualityAssessor

logger = logging.getLogger(__name__)


@dataclass
class ConversationSettings:
    """对话配置"""
    max_context_length: int = 8000  # 最大上下文长度
    context_compression_ratio: float = 0.7  # 上下文压缩比例
    max_history_turns: int = 50  # 最大历史轮次
    cache_ttl: int = 3600  # 缓存过期时间（秒）
    enable_streaming: bool = True  # 启用流式响应
    enable_quality_assessment: bool = True  # 启用质量评估
    auto_save_interval: int = 300  # 自动保存间隔（秒）


class ConversationManager:
    """
    对话管理器
    
    功能：
    1. 对话创建和管理
    2. 上下文维护和压缩
    3. 流式响应处理
    4. 对话持久化
    5. 质量评估
    """
    
    def __init__(self, settings: Optional[ConversationSettings] = None):
        """初始化对话管理器"""
        self.settings = settings or ConversationSettings()
        self._active_conversations: Dict[str, ConversationContext] = {}
        self._context_compressor = ContextCompressor()
        self._response_streamer = ResponseStreamer()
        self._storage = ConversationStorage()
        self._quality_assessor = QualityAssessor()
        
        # 启动后台任务
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """启动后台任务"""
        try:
            # 检查是否有运行中的事件循环
            loop = asyncio.get_running_loop()
            
            # 定期清理过期对话
            asyncio.create_task(self._cleanup_expired_conversations())
            
            # 定期保存活跃对话
            if self.settings.auto_save_interval > 0:
                asyncio.create_task(self._auto_save_conversations())
                
        except RuntimeError:
            # 没有运行中的事件循环，跳过后台任务
            logger.info("没有运行中的事件循环，跳过后台任务启动")
    
    async def create_conversation(
        self,
        user: Optional[User] = None,
        title: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        创建新对话
        
        Args:
            user: 用户对象
            title: 对话标题
            system_prompt: 系统提示词
            **kwargs: 其他参数
            
        Returns:
            对话ID
        """
        conversation_id = str(uuid.uuid4())
        
        # 创建对话上下文
        context = ConversationContext(
            conversation_id=conversation_id,
            user=user,
            title=title or f"对话 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            system_prompt=system_prompt,
            created_at=datetime.now(),
            **kwargs
        )
        
        # 添加系统消息
        if system_prompt:
            context.add_message(AIMessage(
                role=MessageRole.SYSTEM,
                content=system_prompt
            ))
        
        # 缓存对话
        self._active_conversations[conversation_id] = context
        self._cache_conversation(conversation_id, context)
        
        logger.info(f"创建对话: {conversation_id}")
        return conversation_id
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """
        获取对话上下文
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            对话上下文
        """
        # 优先从内存获取
        if conversation_id in self._active_conversations:
            return self._active_conversations[conversation_id]
        
        # 从缓存获取
        context = self._get_cached_conversation(conversation_id)
        if context:
            self._active_conversations[conversation_id] = context
            return context
        
        # 从存储获取
        context = await self._storage.load_conversation(conversation_id)
        if context:
            self._active_conversations[conversation_id] = context
            self._cache_conversation(conversation_id, context)
            return context
        
        return None
    
    async def add_message(
        self,
        conversation_id: str,
        message: AIMessage,
        compress_if_needed: bool = True
    ) -> bool:
        """
        添加消息到对话
        
        Args:
            conversation_id: 对话ID
            message: 消息对象
            compress_if_needed: 是否在需要时压缩上下文
            
        Returns:
            是否添加成功
        """
        context = await self.get_conversation(conversation_id)
        if not context:
            logger.warning(f"对话 {conversation_id} 不存在")
            return False
        
        # 添加消息
        context.add_message(message)
        context.last_activity = datetime.now()
        
        # 检查是否需要压缩上下文
        if compress_if_needed and self._should_compress_context(context):
            await self._compress_context(context)
        
        # 更新缓存
        self._cache_conversation(conversation_id, context)
        
        return True
    
    async def generate_response(
        self,
        conversation_id: str,
        user_message: str,
        service_name: Optional[str] = None,
        streaming: Optional[bool] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        生成AI响应
        
        Args:
            conversation_id: 对话ID
            user_message: 用户消息
            service_name: 指定服务名称
            streaming: 是否使用流式响应
            **kwargs: 其他参数
            
        Yields:
            响应数据块
        """
        context = await self.get_conversation(conversation_id)
        if not context:
            yield {
                'type': 'error',
                'data': {'message': f'对话 {conversation_id} 不存在'}
            }
            return
        
        # 添加用户消息
        user_msg = AIMessage(role=MessageRole.USER, content=user_message)
        await self.add_message(conversation_id, user_msg)
        
        # 准备消息历史
        messages = context.get_messages_for_ai()
        
        # 确定是否使用流式响应
        use_streaming = streaming if streaming is not None else self.settings.enable_streaming
        
        try:
            if use_streaming:
                # 流式响应
                async for chunk in self._generate_streaming_response(
                    conversation_id, messages, service_name, **kwargs
                ):
                    yield chunk
            else:
                # 非流式响应
                async for chunk in self._generate_complete_response(
                    conversation_id, messages, service_name, **kwargs
                ):
                    yield chunk
                    
        except Exception as e:
            logger.error(f"生成响应失败: {e}")
            yield {
                'type': 'error',
                'data': {'message': str(e)}
            }
    
    async def _generate_streaming_response(
        self,
        conversation_id: str,
        messages: List[AIMessage],
        service_name: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """生成流式响应"""
        context = self._active_conversations[conversation_id]
        
        # 开始响应
        yield {
            'type': 'start',
            'data': {
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        try:
            # 获取流式响应
            full_response = ""
            async for chunk in ai_service_manager.stream_response(
                messages=messages,
                service_name=service_name,
                **kwargs
            ):
                # 处理响应块
                if hasattr(chunk, 'content') and chunk.content:
                    content = chunk.content
                    full_response += content
                    
                    yield {
                        'type': 'content',
                        'data': {
                            'content': content,
                            'accumulated': full_response
                        }
                    }
            
            # 添加助手消息到上下文
            if full_response:
                assistant_msg = AIMessage(
                    role=MessageRole.ASSISTANT,
                    content=full_response
                )
                await self.add_message(conversation_id, assistant_msg, compress_if_needed=False)
                
                # 质量评估
                if self.settings.enable_quality_assessment:
                    quality_score = await self._quality_assessor.assess_response(
                        user_message=messages[-1].content if messages else "",
                        ai_response=full_response,
                        context=context
                    )
                    context.add_quality_score(quality_score)
            
            # 完成响应
            yield {
                'type': 'complete',
                'data': {
                    'full_response': full_response,
                    'message_count': len(context.messages),
                    'token_count': context.estimated_tokens
                }
            }
            
        except Exception as e:
            yield {
                'type': 'error',
                'data': {'message': str(e)}
            }
    
    async def _generate_complete_response(
        self,
        conversation_id: str,
        messages: List[AIMessage],
        service_name: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """生成完整响应"""
        context = self._active_conversations[conversation_id]
        
        yield {
            'type': 'start',
            'data': {
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        try:
            # 获取完整响应
            response = await ai_service_manager.generate_response(
                messages=messages,
                service_name=service_name,
                **kwargs
            )
            
            # 添加助手消息
            assistant_msg = AIMessage(
                role=MessageRole.ASSISTANT,
                content=response.content
            )
            await self.add_message(conversation_id, assistant_msg, compress_if_needed=False)
            
            # 质量评估
            if self.settings.enable_quality_assessment:
                quality_score = await self._quality_assessor.assess_response(
                    user_message=messages[-1].content if messages else "",
                    ai_response=response.content,
                    context=context
                )
                context.add_quality_score(quality_score)
            
            yield {
                'type': 'complete',
                'data': {
                    'full_response': response.content,
                    'service_used': response.model,
                    'tokens_used': response.usage.get('total_tokens', 0) if response.usage else 0,
                    'message_count': len(context.messages),
                    'token_count': context.estimated_tokens
                }
            }
            
        except Exception as e:
            yield {
                'type': 'error',
                'data': {'message': str(e)}
            }
    
    def _should_compress_context(self, context: ConversationContext) -> bool:
        """检查是否需要压缩上下文"""
        return (
            context.estimated_tokens > self.settings.max_context_length or
            len(context.messages) > self.settings.max_history_turns
        )
    
    async def _compress_context(self, context: ConversationContext):
        """压缩对话上下文"""
        try:
            compressed_messages = await self._context_compressor.compress(
                messages=context.messages,
                target_length=int(self.settings.max_context_length * self.settings.context_compression_ratio),
                preserve_system=True,
                preserve_recent=5  # 保留最近5条消息
            )
            
            # 更新上下文
            context.messages = compressed_messages
            context.compression_count += 1
            context.last_compression = datetime.now()
            
            logger.info(f"对话 {context.conversation_id} 上下文已压缩")
            
        except Exception as e:
            logger.error(f"上下文压缩失败: {e}")
    
    def _cache_conversation(self, conversation_id: str, context: ConversationContext):
        """缓存对话上下文"""
        try:
            cache_key = f"conversation:{conversation_id}"
            cache.set(cache_key, context, timeout=self.settings.cache_ttl)
        except Exception as e:
            logger.error(f"缓存对话失败: {e}")
    
    def _get_cached_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """从缓存获取对话"""
        try:
            cache_key = f"conversation:{conversation_id}"
            return cache.get(cache_key)
        except Exception as e:
            logger.error(f"获取缓存对话失败: {e}")
            return None
    
    async def save_conversation(self, conversation_id: str) -> bool:
        """
        保存对话到持久化存储
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            是否保存成功
        """
        context = await self.get_conversation(conversation_id)
        if not context:
            return False
        
        try:
            await self._storage.save_conversation(context)
            context.last_saved = datetime.now()
            logger.info(f"对话 {conversation_id} 已保存")
            return True
            
        except Exception as e:
            logger.error(f"保存对话失败: {e}")
            return False
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        删除对话
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            是否删除成功
        """
        try:
            # 从内存删除
            self._active_conversations.pop(conversation_id, None)
            
            # 从缓存删除
            cache_key = f"conversation:{conversation_id}"
            cache.delete(cache_key)
            
            # 从存储删除
            await self._storage.delete_conversation(conversation_id)
            
            logger.info(f"对话 {conversation_id} 已删除")
            return True
            
        except Exception as e:
            logger.error(f"删除对话失败: {e}")
            return False
    
    async def list_conversations(
        self,
        user: Optional[User] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        列出对话
        
        Args:
            user: 用户对象
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            对话列表
        """
        try:
            return await self._storage.list_conversations(
                user=user,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            logger.error(f"列出对话失败: {e}")
            return []
    
    async def get_conversation_stats(self, conversation_id: str) -> Dict[str, Any]:
        """
        获取对话统计信息
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            统计信息
        """
        context = await self.get_conversation(conversation_id)
        if not context:
            return {}
        
        return {
            'conversation_id': conversation_id,
            'title': context.title,
            'created_at': context.created_at.isoformat(),
            'last_activity': context.last_activity.isoformat() if context.last_activity else None,
            'message_count': len(context.messages),
            'estimated_tokens': context.estimated_tokens,
            'compression_count': context.compression_count,
            'last_compression': context.last_compression.isoformat() if context.last_compression else None,
            'quality_scores': context.quality_scores,
            'avg_quality_score': sum(context.quality_scores) / len(context.quality_scores) if context.quality_scores else None
        }
    
    async def rate_conversation(
        self,
        conversation_id: str,
        rating: int,
        feedback: Optional[str] = None
    ) -> bool:
        """
        评价对话
        
        Args:
            conversation_id: 对话ID
            rating: 评分 (1-5)
            feedback: 反馈内容
            
        Returns:
            是否评价成功
        """
        context = await self.get_conversation(conversation_id)
        if not context:
            return False
        
        try:
            # 记录用户评价
            context.user_rating = rating
            context.user_feedback = feedback
            context.rating_time = datetime.now()
            
            # 保存到存储
            await self.save_conversation(conversation_id)
            
            logger.info(f"对话 {conversation_id} 用户评价: {rating}")
            return True
            
        except Exception as e:
            logger.error(f"评价对话失败: {e}")
            return False
    
    async def _cleanup_expired_conversations(self):
        """清理过期对话"""
        while True:
            try:
                current_time = datetime.now()
                expired_ids = []
                
                for conversation_id, context in self._active_conversations.items():
                    # 检查是否过期
                    if context.last_activity:
                        inactive_time = current_time - context.last_activity
                        if inactive_time > timedelta(seconds=self.settings.cache_ttl):
                            expired_ids.append(conversation_id)
                    else:
                        # 没有活动记录的对话，检查创建时间
                        created_time = current_time - context.created_at
                        if created_time > timedelta(seconds=self.settings.cache_ttl):
                            expired_ids.append(conversation_id)
                
                # 清理过期对话
                for conversation_id in expired_ids:
                    await self.save_conversation(conversation_id)  # 保存后删除
                    del self._active_conversations[conversation_id]
                    logger.info(f"清理过期对话: {conversation_id}")
                
                # 每5分钟检查一次
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"清理过期对话异常: {e}")
                await asyncio.sleep(60)
    
    async def _auto_save_conversations(self):
        """自动保存对话"""
        while True:
            try:
                current_time = datetime.now()
                
                for conversation_id, context in self._active_conversations.items():
                    # 检查是否需要保存
                    if context.last_saved is None:
                        # 从未保存过
                        should_save = True
                    else:
                        # 检查距离上次保存的时间
                        time_since_save = current_time - context.last_saved
                        should_save = time_since_save.total_seconds() >= self.settings.auto_save_interval
                    
                    if should_save and context.last_activity:
                        # 有活动且需要保存
                        time_since_activity = current_time - context.last_activity
                        if time_since_activity.total_seconds() < self.settings.auto_save_interval:
                            # 最近有活动，保存
                            await self.save_conversation(conversation_id)
                
                # 等待保存间隔
                await asyncio.sleep(self.settings.auto_save_interval)
                
            except Exception as e:
                logger.error(f"自动保存对话异常: {e}")
                await asyncio.sleep(60)


# 全局对话管理器实例
conversation_manager = ConversationManager()
