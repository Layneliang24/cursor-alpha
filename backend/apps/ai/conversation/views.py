"""
对话管理API视图

提供对话创建、管理、流式响应等API接口
"""

import uuid
import logging
from typing import Dict, Any

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import StreamingHttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .manager import conversation_manager
from .streaming import ResponseStreamer

logger = logging.getLogger(__name__)


class ConversationViewSet(viewsets.ViewSet):
    """对话管理API"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="创建新对话",
        description="创建一个新的AI对话会话",
        request={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "对话标题"},
                "system_prompt": {"type": "string", "description": "系统提示词"},
                "metadata": {"type": "object", "description": "元数据"}
            }
        },
        responses={201: {
            "type": "object",
            "properties": {
                "conversation_id": {"type": "string"},
                "title": {"type": "string"},
                "created_at": {"type": "string"}
            }
        }},
        tags=["对话管理"]
    )
    async def create(self, request):
        """创建新对话"""
        try:
            data = request.data
            
            conversation_id = await conversation_manager.create_conversation(
                user=request.user,
                title=data.get('title'),
                system_prompt=data.get('system_prompt'),
                metadata=data.get('metadata', {})
            )
            
            context = await conversation_manager.get_conversation(conversation_id)
            
            return Response({
                'conversation_id': conversation_id,
                'title': context.title,
                'created_at': context.created_at.isoformat()
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"创建对话失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="获取对话列表",
        description="获取用户的对话列表",
        parameters=[
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="限制数量"
            ),
            OpenApiParameter(
                name="offset",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="偏移量"
            ),
            OpenApiParameter(
                name="include_archived",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="包含已归档的对话"
            )
        ],
        responses={200: {
            "type": "object",
            "properties": {
                "conversations": {"type": "array"},
                "total": {"type": "integer"}
            }
        }},
        tags=["对话管理"]
    )
    async def list(self, request):
        """获取对话列表"""
        try:
            limit = int(request.query_params.get('limit', 50))
            offset = int(request.query_params.get('offset', 0))
            include_archived = request.query_params.get('include_archived', 'false').lower() == 'true'
            
            conversations = await conversation_manager.list_conversations(
                user=request.user,
                limit=limit,
                offset=offset
            )
            
            return Response({
                'conversations': conversations,
                'total': len(conversations)
            })
            
        except Exception as e:
            logger.error(f"获取对话列表失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="获取对话详情",
        description="获取指定对话的详细信息",
        parameters=[
            OpenApiParameter(
                name="conversation_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="对话ID"
            )
        ],
        responses={200: {
            "type": "object",
            "properties": {
                "conversation_id": {"type": "string"},
                "title": {"type": "string"},
                "messages": {"type": "array"},
                "stats": {"type": "object"}
            }
        }},
        tags=["对话管理"]
    )
    async def retrieve(self, request, pk=None):
        """获取对话详情"""
        try:
            conversation_id = pk
            context = await conversation_manager.get_conversation(conversation_id)
            
            if not context:
                return Response(
                    {'error': '对话不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 检查权限
            if context.user != request.user:
                return Response(
                    {'error': '权限不足'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 获取统计信息
            stats = await conversation_manager.get_conversation_stats(conversation_id)
            
            return Response({
                'conversation_id': context.conversation_id,
                'title': context.title,
                'created_at': context.created_at.isoformat(),
                'last_activity': context.last_activity.isoformat() if context.last_activity else None,
                'system_prompt': context.system_prompt,
                'messages': [
                    {
                        'role': msg.role.value,
                        'content': msg.content,
                        'timestamp': getattr(msg, 'timestamp', None)
                    }
                    for msg in context.messages
                ],
                'metadata': context.metadata,
                'stats': stats
            })
            
        except Exception as e:
            logger.error(f"获取对话详情失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="发送消息",
        description="向对话发送消息并获取AI响应",
        request={
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "用户消息"},
                "service_name": {"type": "string", "description": "指定AI服务"},
                "streaming": {"type": "boolean", "description": "是否使用流式响应"},
                "max_tokens": {"type": "integer", "description": "最大token数"},
                "temperature": {"type": "number", "description": "温度参数"}
            },
            "required": ["message"]
        },
        responses={200: {
            "type": "object",
            "properties": {
                "response": {"type": "string"},
                "conversation_id": {"type": "string"},
                "tokens_used": {"type": "integer"}
            }
        }},
        tags=["对话管理"]
    )
    @action(detail=True, methods=['post'])
    async def send_message(self, request, pk=None):
        """发送消息"""
        try:
            conversation_id = pk
            data = request.data
            message = data.get('message')
            
            if not message:
                return Response(
                    {'error': '消息不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 检查对话权限
            context = await conversation_manager.get_conversation(conversation_id)
            if not context or context.user != request.user:
                return Response(
                    {'error': '对话不存在或权限不足'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 检查是否使用流式响应
            streaming = data.get('streaming', False)
            
            if streaming:
                # 返回流式响应
                return self._handle_streaming_response(
                    conversation_id, message, data, request.user
                )
            else:
                # 返回完整响应
                return await self._handle_complete_response(
                    conversation_id, message, data
                )
                
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _handle_streaming_response(
        self,
        conversation_id: str,
        message: str,
        data: dict,
        user
    ) -> StreamingHttpResponse:
        """处理流式响应"""
        # 创建流ID
        stream_id = f"{conversation_id}_{uuid.uuid4().hex[:8]}"
        
        async def stream_generator():
            try:
                # 创建流
                streamer = ResponseStreamer()
                await streamer.create_stream(stream_id)
                
                # 获取AI响应流
                response_generator = conversation_manager.generate_response(
                    conversation_id=conversation_id,
                    user_message=message,
                    service_name=data.get('service_name'),
                    streaming=True,
                    max_tokens=data.get('max_tokens'),
                    temperature=data.get('temperature')
                )
                
                # 处理AI流并转换为SSE
                await streamer.process_ai_stream(stream_id, response_generator)
                
                # 生成SSE响应
                async for sse_data in streamer.get_sse_generator(stream_id):
                    yield sse_data
                    
            except Exception as e:
                logger.error(f"流式响应处理失败: {e}")
                error_data = f"data: {{'type': 'error', 'message': '{str(e)}'}}\n\n"
                yield error_data
        
        response = StreamingHttpResponse(
            stream_generator(),
            content_type='text/event-stream'
        )
        
        # 设置SSE头部
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'
        response['Access-Control-Allow-Origin'] = '*'
        
        return response
    
    async def _handle_complete_response(
        self,
        conversation_id: str,
        message: str,
        data: dict
    ) -> Response:
        """处理完整响应"""
        full_response = ""
        service_used = None
        tokens_used = 0
        
        # 获取AI响应
        async for chunk in conversation_manager.generate_response(
            conversation_id=conversation_id,
            user_message=message,
            service_name=data.get('service_name'),
            streaming=False,
            max_tokens=data.get('max_tokens'),
            temperature=data.get('temperature')
        ):
            if chunk.get('type') == 'complete':
                chunk_data = chunk.get('data', {})
                full_response = chunk_data.get('full_response', '')
                service_used = chunk_data.get('service_used')
                tokens_used = chunk_data.get('tokens_used', 0)
                break
            elif chunk.get('type') == 'error':
                return Response(
                    {'error': chunk.get('data', {}).get('message', '未知错误')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response({
            'response': full_response,
            'conversation_id': conversation_id,
            'service_used': service_used,
            'tokens_used': tokens_used
        })
    
    @extend_schema(
        summary="删除对话",
        description="删除指定的对话",
        parameters=[
            OpenApiParameter(
                name="conversation_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="对话ID"
            )
        ],
        responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
        tags=["对话管理"]
    )
    async def destroy(self, request, pk=None):
        """删除对话"""
        try:
            conversation_id = pk
            
            # 检查权限
            context = await conversation_manager.get_conversation(conversation_id)
            if not context or context.user != request.user:
                return Response(
                    {'error': '对话不存在或权限不足'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            success = await conversation_manager.delete_conversation(conversation_id)
            
            if success:
                return Response({'message': '对话已删除'})
            else:
                return Response(
                    {'error': '删除失败'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"删除对话失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="评价对话",
        description="对对话进行评分和反馈",
        request={
            "type": "object",
            "properties": {
                "rating": {"type": "integer", "minimum": 1, "maximum": 5, "description": "评分 (1-5)"},
                "feedback": {"type": "string", "description": "反馈内容"}
            },
            "required": ["rating"]
        },
        responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
        tags=["对话管理"]
    )
    @action(detail=True, methods=['post'])
    async def rate(self, request, pk=None):
        """评价对话"""
        try:
            conversation_id = pk
            data = request.data
            rating = data.get('rating')
            feedback = data.get('feedback')
            
            if not isinstance(rating, int) or not (1 <= rating <= 5):
                return Response(
                    {'error': '评分必须是1-5之间的整数'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 检查权限
            context = await conversation_manager.get_conversation(conversation_id)
            if not context or context.user != request.user:
                return Response(
                    {'error': '对话不存在或权限不足'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            success = await conversation_manager.rate_conversation(
                conversation_id, rating, feedback
            )
            
            if success:
                return Response({'message': '评价已提交'})
            else:
                return Response(
                    {'error': '评价失败'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"评价对话失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="获取对话统计",
        description="获取用户的对话统计信息",
        parameters=[
            OpenApiParameter(
                name="days",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="统计天数"
            )
        ],
        responses={200: {
            "type": "object",
            "properties": {
                "total_conversations": {"type": "integer"},
                "total_messages": {"type": "integer"},
                "avg_quality_score": {"type": "number"}
            }
        }},
        tags=["对话管理"]
    )
    @action(detail=False, methods=['get'])
    async def stats(self, request):
        """获取对话统计"""
        try:
            days = int(request.query_params.get('days', 30))
            
            # 从存储获取统计信息
            stats = await conversation_manager._storage.get_conversation_stats(
                user=request.user,
                days=days
            )
            
            return Response(stats)
            
        except Exception as e:
            logger.error(f"获取对话统计失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
