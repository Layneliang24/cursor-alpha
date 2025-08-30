"""
AI服务管理API视图

提供AI服务管理、负载均衡、健康监控等API接口
"""

import logging
from typing import Dict, Any

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .services.manager import ai_service_manager
from .services.load_balancer import LoadBalancingStrategy
from .services.degradation import ServiceLevel
from .adapters.base import AIProviderType, AIMessage, MessageRole

logger = logging.getLogger(__name__)


class ConversationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        return Response({
            "success": True,
            "message": "ai placeholder",
            "data": []
        })


class AIServiceViewSet(viewsets.ViewSet):
    """AI服务管理API"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="获取AI服务状态",
        description="获取所有AI服务的状态信息，包括健康状态、负载均衡统计等",
        responses={200: {
            "type": "object",
            "properties": {
                "services": {"type": "object"},
                "load_balancer": {"type": "object"},
                "degradation": {"type": "object"}
            }
        }},
        tags=["AI服务管理"]
    )
    def list(self, request):
        """获取AI服务状态"""
        try:
            return Response({
                'services': ai_service_manager.get_service_status(),
                'load_balancer': ai_service_manager.get_load_balancer_stats(),
                'degradation': ai_service_manager.get_degradation_status()
            })
        except Exception as e:
            logger.error(f"获取AI服务状态失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="添加AI服务",
        description="动态添加新的AI服务实例",
        request={
            "type": "object",
            "properties": {
                "service_name": {"type": "string", "description": "服务名称"},
                "provider": {"type": "string", "enum": [p.value for p in AIProviderType]},
                "model": {"type": "string", "description": "模型名称"},
                "weight": {"type": "integer", "minimum": 1, "description": "负载均衡权重"},
                "config": {"type": "object", "description": "模型配置参数"}
            },
            "required": ["service_name", "provider", "model"]
        },
        responses={201: {"type": "object", "properties": {"message": {"type": "string"}}}},
        tags=["AI服务管理"]
    )
    @action(detail=False, methods=['post'])
    def add_service(self, request):
        """添加AI服务"""
        try:
            data = request.data
            service_name = data.get('service_name')
            provider = AIProviderType(data.get('provider'))
            model = data.get('model')
            weight = data.get('weight', 1)
            config = data.get('config', {})
            
            success = ai_service_manager.add_service(
                service_name=service_name,
                provider=provider,
                model=model,
                config=config,
                weight=weight
            )
            
            if success:
                return Response(
                    {'message': f'服务 {service_name} 添加成功'},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'error': f'服务 {service_name} 添加失败'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"添加AI服务失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="移除AI服务",
        description="移除指定的AI服务实例",
        parameters=[
            OpenApiParameter(
                name="service_name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="服务名称"
            )
        ],
        responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
        tags=["AI服务管理"]
    )
    @action(detail=True, methods=['delete'])
    def remove_service(self, request, pk=None):
        """移除AI服务"""
        try:
            service_name = pk
            success = ai_service_manager.remove_service(service_name)
            
            if success:
                return Response({'message': f'服务 {service_name} 移除成功'})
            else:
                return Response(
                    {'error': f'服务 {service_name} 不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            logger.error(f"移除AI服务失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="启用/禁用AI服务",
        description="启用或禁用指定的AI服务",
        request={
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "description": "是否启用"}
            },
            "required": ["enabled"]
        },
        parameters=[
            OpenApiParameter(
                name="service_name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="服务名称"
            )
        ],
        responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
        tags=["AI服务管理"]
    )
    @action(detail=True, methods=['patch'])
    def toggle_service(self, request, pk=None):
        """启用/禁用AI服务"""
        try:
            service_name = pk
            enabled = request.data.get('enabled', True)
            
            if enabled:
                success = ai_service_manager.enable_service(service_name)
                action_text = "启用"
            else:
                success = ai_service_manager.disable_service(service_name)
                action_text = "禁用"
            
            if success:
                return Response({'message': f'服务 {service_name} {action_text}成功'})
            else:
                return Response(
                    {'error': f'服务 {service_name} 不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            logger.error(f"切换AI服务状态失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="AI对话接口",
        description="与AI助教进行对话，支持负载均衡和故障转移",
        request={
            "type": "object",
            "properties": {
                "messages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string", "enum": ["user", "assistant", "system"]},
                            "content": {"type": "string"}
                        }
                    },
                    "description": "对话消息列表"
                },
                "service_name": {"type": "string", "description": "指定服务名称（可选）"},
                "max_tokens": {"type": "integer", "description": "最大token数"},
                "temperature": {"type": "number", "description": "温度参数"},
                "stream": {"type": "boolean", "description": "是否使用流式响应"}
            },
            "required": ["messages"]
        },
        responses={200: {
            "type": "object",
            "properties": {
                "response": {"type": "string"},
                "service_used": {"type": "string"},
                "tokens_used": {"type": "integer"},
                "response_time": {"type": "number"}
            }
        }},
        tags=["AI对话"]
    )
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """AI对话接口"""
        try:
            data = request.data
            messages_data = data.get('messages', [])
            service_name = data.get('service_name')
            
            # 转换消息格式
            messages = []
            for msg_data in messages_data:
                role = MessageRole(msg_data.get('role', 'user'))
                content = msg_data.get('content', '')
                messages.append(AIMessage(role=role, content=content))
            
            if not messages:
                return Response(
                    {'error': '消息列表不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 准备参数
            kwargs = {}
            if 'max_tokens' in data:
                kwargs['max_tokens'] = data['max_tokens']
            if 'temperature' in data:
                kwargs['temperature'] = data['temperature']
            
            # 生成响应
            import asyncio
            response = asyncio.run(ai_service_manager.generate_response(
                messages=messages,
                service_name=service_name,
                **kwargs
            ))
            
            return Response({
                'response': response.content,
                'service_used': response.model,
                'tokens_used': response.usage.get('total_tokens', 0) if response.usage else 0,
                'response_time': getattr(response, 'response_time', 0)
            })
            
        except Exception as e:
            logger.error(f"AI对话失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoadBalancerViewSet(viewsets.ViewSet):
    """负载均衡管理API"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="获取负载均衡统计",
        description="获取负载均衡器的详细统计信息",
        responses={200: {
            "type": "object",
            "properties": {
                "strategy": {"type": "string"},
                "services": {"type": "object"},
                "total_requests": {"type": "integer"}
            }
        }},
        tags=["负载均衡"]
    )
    def list(self, request):
        """获取负载均衡统计"""
        try:
            return Response(ai_service_manager.get_load_balancer_stats())
        except Exception as e:
            logger.error(f"获取负载均衡统计失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="设置负载均衡策略",
        description="更新负载均衡策略",
        request={
            "type": "object",
            "properties": {
                "strategy": {
                    "type": "string",
                    "enum": [s.value for s in LoadBalancingStrategy],
                    "description": "负载均衡策略"
                }
            },
            "required": ["strategy"]
        },
        responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
        tags=["负载均衡"]
    )
    @action(detail=False, methods=['post'])
    def set_strategy(self, request):
        """设置负载均衡策略"""
        try:
            strategy_value = request.data.get('strategy')
            strategy = LoadBalancingStrategy(strategy_value)
            
            ai_service_manager.set_load_balancing_strategy(strategy)
            
            return Response({'message': f'负载均衡策略已更新: {strategy.value}'})
            
        except ValueError:
            return Response(
                {'error': f'无效的负载均衡策略: {strategy_value}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"设置负载均衡策略失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthMonitorViewSet(viewsets.ViewSet):
    """健康监控API"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="获取健康状态",
        description="获取所有AI服务的健康状态",
        responses={200: {
            "type": "object",
            "properties": {
                "summary": {"type": "object"},
                "services": {"type": "object"}
            }
        }},
        tags=["健康监控"]
    )
    def list(self, request):
        """获取健康状态"""
        try:
            health_monitor = ai_service_manager._health_monitor
            
            return Response({
                'summary': health_monitor.get_health_summary(),
                'services': {
                    name: {
                        'status': health.status.value,
                        'is_healthy': health.is_healthy,
                        'response_time': health.response_time,
                        'last_check': health.last_check.isoformat() if health.last_check else None,
                        'consecutive_failures': health.consecutive_failures,
                        'uptime_percentage': round(health.uptime_percentage, 2),
                        'error': health.error
                    }
                    for name, health in health_monitor.get_all_health().items()
                }
            })
            
        except Exception as e:
            logger.error(f"获取健康状态失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DegradationViewSet(viewsets.ViewSet):
    """服务降级管理API"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="获取降级状态",
        description="获取当前服务降级状态和指标",
        responses={200: {
            "type": "object",
            "properties": {
                "current_level": {"type": "string"},
                "metrics": {"type": "object"},
                "thresholds": {"type": "object"},
                "recommendations": {"type": "array"}
            }
        }},
        tags=["服务降级"]
    )
    def list(self, request):
        """获取降级状态"""
        try:
            degradation_manager = ai_service_manager._degradation_manager
            
            return Response({
                **degradation_manager.get_status_summary(),
                'thresholds': degradation_manager.get_thresholds()
            })
            
        except Exception as e:
            logger.error(f"获取降级状态失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="强制服务降级",
        description="手动设置服务降级级别",
        request={
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "enum": [l.value for l in ServiceLevel],
                    "description": "服务级别"
                }
            },
            "required": ["level"]
        },
        responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
        tags=["服务降级"]
    )
    @action(detail=False, methods=['post'])
    def force_degradation(self, request):
        """强制服务降级"""
        try:
            level_value = request.data.get('level')
            level = ServiceLevel(level_value)
            
            ai_service_manager.force_degradation(level)
            
            return Response({'message': f'服务级别已强制设置为: {level.value}'})
            
        except ValueError:
            return Response(
                {'error': f'无效的服务级别: {level_value}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"强制服务降级失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="清除服务降级",
        description="清除强制设置的服务降级",
        responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
        tags=["服务降级"]
    )
    @action(detail=False, methods=['post'])
    def clear_degradation(self, request):
        """清除服务降级"""
        try:
            ai_service_manager.clear_degradation()
            return Response({'message': '服务降级已清除'})
            
        except Exception as e:
            logger.error(f"清除服务降级失败: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


