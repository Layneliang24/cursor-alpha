"""
对话存储管理

处理对话的持久化存储、检索和管理
"""

import json
import time
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.serializers.json import DjangoJSONEncoder

from .context import ConversationContext

logger = logging.getLogger(__name__)


class ConversationModel(models.Model):
    """对话数据模型"""
    
    conversation_id = models.CharField(max_length=255, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    system_prompt = models.TextField(null=True, blank=True)
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    last_saved = models.DateTimeField(null=True, blank=True)
    
    # 对话数据（JSON存储）
    messages_data = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    metadata = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    
    # 统计信息
    message_count = models.IntegerField(default=0)
    estimated_tokens = models.IntegerField(default=0)
    compression_count = models.IntegerField(default=0)
    last_compression = models.DateTimeField(null=True, blank=True)
    
    # 质量评估
    quality_scores = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    avg_quality_score = models.FloatField(null=True, blank=True)
    user_rating = models.IntegerField(null=True, blank=True)
    user_feedback = models.TextField(null=True, blank=True)
    rating_time = models.DateTimeField(null=True, blank=True)
    
    # 状态标记
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'ai_conversations'
        ordering = ['-last_activity', '-created_at']
        indexes = [
            models.Index(fields=['user', '-last_activity']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-last_activity']),
            models.Index(fields=['is_active', 'is_archived']),
        ]
    
    def __str__(self):
        return f"Conversation {self.conversation_id}: {self.title}"
    
    def update_stats(self, context: ConversationContext):
        """更新统计信息"""
        self.message_count = len(context.messages)
        self.estimated_tokens = context.estimated_tokens
        self.compression_count = context.compression_count
        self.last_compression = context.last_compression
        self.quality_scores = context.quality_scores
        self.avg_quality_score = sum(context.quality_scores) / len(context.quality_scores) if context.quality_scores else None
        self.user_rating = context.user_rating
        self.user_feedback = context.user_feedback
        self.rating_time = context.rating_time
        self.last_activity = context.last_activity
        self.last_saved = datetime.now()


class ConversationStorage:
    """
    对话存储管理器
    
    负责对话的持久化存储、检索和管理
    """
    
    def __init__(self):
        """初始化存储管理器"""
        pass
    
    async def save_conversation(self, context: ConversationContext) -> bool:
        """
        保存对话
        
        Args:
            context: 对话上下文
            
        Returns:
            是否保存成功
        """
        try:
            # 准备消息数据
            messages_data = [
                {
                    'role': msg.role.value,
                    'content': msg.content,
                    'timestamp': datetime.fromtimestamp(getattr(msg, 'timestamp', time.time())).isoformat()
                }
                for msg in context.messages
            ]
            
            # 更新或创建数据库记录
            conversation, created = await ConversationModel.objects.aupdate_or_create(
                conversation_id=context.conversation_id,
                defaults={
                    'user': context.user,
                    'title': context.title,
                    'system_prompt': context.system_prompt,
                    'messages_data': messages_data,
                    'metadata': context.metadata,
                    'last_activity': context.last_activity,
                }
            )
            
            # 更新统计信息
            conversation.update_stats(context)
            await conversation.asave()
            
            action = "创建" if created else "更新"
            logger.info(f"{action}对话 {context.conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存对话失败: {e}")
            return False
    
    async def load_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """
        加载对话
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            对话上下文
        """
        try:
            conversation = await ConversationModel.objects.select_related('user').aget(
                conversation_id=conversation_id,
                is_active=True
            )
            
            # 转换为上下文对象
            context = await self._model_to_context(conversation)
            
            logger.info(f"加载对话 {conversation_id}")
            return context
            
        except ConversationModel.DoesNotExist:
            logger.warning(f"对话 {conversation_id} 不存在")
            return None
        except Exception as e:
            logger.error(f"加载对话失败: {e}")
            return None
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        删除对话
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            是否删除成功
        """
        try:
            conversation = await ConversationModel.objects.aget(
                conversation_id=conversation_id
            )
            
            # 软删除：标记为非活跃
            conversation.is_active = False
            await conversation.asave()
            
            logger.info(f"删除对话 {conversation_id}")
            return True
            
        except ConversationModel.DoesNotExist:
            logger.warning(f"对话 {conversation_id} 不存在")
            return False
        except Exception as e:
            logger.error(f"删除对话失败: {e}")
            return False
    
    async def list_conversations(
        self,
        user: Optional[User] = None,
        limit: int = 50,
        offset: int = 0,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """
        列出对话
        
        Args:
            user: 用户对象
            limit: 限制数量
            offset: 偏移量
            include_archived: 是否包含已归档的对话
            
        Returns:
            对话列表
        """
        try:
            queryset = ConversationModel.objects.filter(is_active=True)
            
            if user:
                queryset = queryset.filter(user=user)
            
            if not include_archived:
                queryset = queryset.filter(is_archived=False)
            
            conversations = await queryset.order_by('-last_activity')[offset:offset + limit].aall()
            
            result = []
            async for conversation in conversations:
                result.append({
                    'conversation_id': conversation.conversation_id,
                    'title': conversation.title,
                    'created_at': conversation.created_at.isoformat(),
                    'last_activity': conversation.last_activity.isoformat() if conversation.last_activity else None,
                    'message_count': conversation.message_count,
                    'estimated_tokens': conversation.estimated_tokens,
                    'avg_quality_score': conversation.avg_quality_score,
                    'user_rating': conversation.user_rating,
                    'is_archived': conversation.is_archived
                })
            
            return result
            
        except Exception as e:
            logger.error(f"列出对话失败: {e}")
            return []
    
    async def search_conversations(
        self,
        query: str,
        user: Optional[User] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        搜索对话
        
        Args:
            query: 搜索查询
            user: 用户对象
            limit: 限制数量
            
        Returns:
            搜索结果
        """
        try:
            queryset = ConversationModel.objects.filter(
                is_active=True,
                is_archived=False
            )
            
            if user:
                queryset = queryset.filter(user=user)
            
            # 搜索标题和消息内容
            queryset = queryset.filter(
                models.Q(title__icontains=query) |
                models.Q(messages_data__icontains=query)
            )
            
            conversations = await queryset.order_by('-last_activity')[:limit].aall()
            
            result = []
            async for conversation in conversations:
                result.append({
                    'conversation_id': conversation.conversation_id,
                    'title': conversation.title,
                    'created_at': conversation.created_at.isoformat(),
                    'last_activity': conversation.last_activity.isoformat() if conversation.last_activity else None,
                    'message_count': conversation.message_count,
                    'estimated_tokens': conversation.estimated_tokens,
                    'match_type': 'title' if query.lower() in conversation.title.lower() else 'content'
                })
            
            return result
            
        except Exception as e:
            logger.error(f"搜索对话失败: {e}")
            return []
    
    async def archive_conversation(self, conversation_id: str) -> bool:
        """
        归档对话
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            是否归档成功
        """
        try:
            conversation = await ConversationModel.objects.aget(
                conversation_id=conversation_id,
                is_active=True
            )
            
            conversation.is_archived = True
            await conversation.asave()
            
            logger.info(f"归档对话 {conversation_id}")
            return True
            
        except ConversationModel.DoesNotExist:
            logger.warning(f"对话 {conversation_id} 不存在")
            return False
        except Exception as e:
            logger.error(f"归档对话失败: {e}")
            return False
    
    async def restore_conversation(self, conversation_id: str) -> bool:
        """
        恢复归档的对话
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            是否恢复成功
        """
        try:
            conversation = await ConversationModel.objects.aget(
                conversation_id=conversation_id,
                is_active=True,
                is_archived=True
            )
            
            conversation.is_archived = False
            await conversation.asave()
            
            logger.info(f"恢复对话 {conversation_id}")
            return True
            
        except ConversationModel.DoesNotExist:
            logger.warning(f"归档对话 {conversation_id} 不存在")
            return False
        except Exception as e:
            logger.error(f"恢复对话失败: {e}")
            return False
    
    async def get_conversation_stats(
        self,
        user: Optional[User] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取对话统计
        
        Args:
            user: 用户对象
            days: 统计天数
            
        Returns:
            统计信息
        """
        try:
            since_date = datetime.now() - timedelta(days=days)
            
            queryset = ConversationModel.objects.filter(
                is_active=True,
                created_at__gte=since_date
            )
            
            if user:
                queryset = queryset.filter(user=user)
            
            stats = await queryset.aaggregate(
                total_conversations=models.Count('id'),
                total_messages=models.Sum('message_count'),
                total_tokens=models.Sum('estimated_tokens'),
                avg_quality_score=models.Avg('avg_quality_score'),
                avg_message_count=models.Avg('message_count')
            )
            
            # 获取评分分布
            rating_distribution = {}
            for i in range(1, 6):
                count = await queryset.filter(user_rating=i).acount()
                rating_distribution[str(i)] = count
            
            return {
                **stats,
                'rating_distribution': rating_distribution,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"获取对话统计失败: {e}")
            return {}
    
    async def cleanup_old_conversations(self, days: int = 90) -> int:
        """
        清理旧对话
        
        Args:
            days: 保留天数
            
        Returns:
            清理的对话数量
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 查找需要清理的对话
            old_conversations = ConversationModel.objects.filter(
                is_active=True,
                last_activity__lt=cutoff_date,
                user_rating__isnull=True  # 没有用户评分的对话
            )
            
            count = await old_conversations.acount()
            
            # 标记为非活跃
            await old_conversations.aupdate(is_active=False)
            
            logger.info(f"清理 {count} 个旧对话")
            return count
            
        except Exception as e:
            logger.error(f"清理旧对话失败: {e}")
            return 0
    
    async def _model_to_context(self, conversation: ConversationModel) -> ConversationContext:
        """将数据库模型转换为上下文对象"""
        from ..adapters.base import AIMessage, MessageRole
        
        # 转换消息
        messages = []
        for msg_data in conversation.messages_data:
            message = AIMessage(
                role=MessageRole(msg_data['role']),
                content=msg_data['content']
            )
            if 'timestamp' in msg_data:
                message.timestamp = datetime.fromisoformat(msg_data['timestamp'])
            messages.append(message)
        
        # 创建上下文
        context = ConversationContext(
            conversation_id=conversation.conversation_id,
            title=conversation.title,
            created_at=conversation.created_at,
            user=conversation.user,
            system_prompt=conversation.system_prompt,
            messages=messages,
            metadata=conversation.metadata,
            last_activity=conversation.last_activity,
            last_saved=conversation.last_saved,
            last_compression=conversation.last_compression,
            compression_count=conversation.compression_count,
            quality_scores=conversation.quality_scores,
            user_rating=conversation.user_rating,
            user_feedback=conversation.user_feedback,
            rating_time=conversation.rating_time
        )
        
        return context
