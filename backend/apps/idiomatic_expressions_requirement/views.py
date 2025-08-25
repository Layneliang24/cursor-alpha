from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import IdiomaticExpressionsRequirement
from .serializers import IdiomaticExpressionsRequirementSerializer


class IdiomaticExpressionsRequirementViewSet(viewsets.ModelViewSet):
    """视图集: 需求 idiomatic_expressions_requirement"""
    
    queryset = IdiomaticExpressionsRequirement.objects.all()
    serializer_class = IdiomaticExpressionsRequirementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'created_by']
    
    def get_queryset(self):
        """获取查询集"""
        queryset = super().get_queryset()
        # TODO: 根据需求添加过滤逻辑
        return queryset.filter(is_active=True)
    
    def perform_create(self, serializer):
        """创建时设置创建者"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换激活状态"""
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save()
        return Response({
            'status': 'success',
            'is_active': instance.is_active
        })
    
    # TODO: 根据需求添加自定义动作
