"""
地道表达服务
提供地道表达相关的业务逻辑
"""

from django.db.models import Q, Count, Avg
from django.utils import timezone
from typing import List, Dict, Optional, Tuple
import logging

from ..models import (
    IdiomaticExpression, ExpressionSource, ExpressionScenario,
    ExpressionScenarioLink, UserExpressionProgress
)

logger = logging.getLogger(__name__)


class IdiomaticExpressionService:
    """地道表达服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_expressions_by_difficulty(self, difficulty_level: str, limit: int = 10) -> List[IdiomaticExpression]:
        """根据难度级别获取地道表达"""
        try:
            expressions = IdiomaticExpression.objects.filter(
                difficulty_level=difficulty_level,
                is_active=True
            ).order_by('?')[:limit]
            return list(expressions)
        except Exception as e:
            self.logger.error(f"获取难度级别 {difficulty_level} 的地道表达失败: {e}")
            return []
    
    def get_expressions_by_type(self, expression_type: str, limit: int = 10) -> List[IdiomaticExpression]:
        """根据类型获取地道表达"""
        try:
            expressions = IdiomaticExpression.objects.filter(
                expression_type=expression_type,
                is_active=True
            ).order_by('?')[:limit]
            return list(expressions)
        except Exception as e:
            self.logger.error(f"获取类型 {expression_type} 的地道表达失败: {e}")
            return []
    
    def search_expressions(self, query: str, limit: int = 20) -> List[IdiomaticExpression]:
        """搜索地道表达"""
        try:
            expressions = IdiomaticExpression.objects.filter(
                Q(expression__icontains=query) |
                Q(meaning__icontains=query) |
                Q(example_sentences__icontains=query),
                is_active=True
            ).order_by('-frequency_score')[:limit]
            return list(expressions)
        except Exception as e:
            self.logger.error(f"搜索地道表达失败: {e}")
            return []
    
    def get_user_progress(self, user_id: int, expression_id: int) -> Optional[UserExpressionProgress]:
        """获取用户学习进度"""
        try:
            return UserExpressionProgress.objects.get(
                user_id=user_id,
                expression_id=expression_id
            )
        except UserExpressionProgress.DoesNotExist:
            return None
        except Exception as e:
            self.logger.error(f"获取用户进度失败: {e}")
            return None
    
    def update_user_progress(self, user_id: int, expression_id: int, 
                           mastery_level: int, is_favorite: bool = False) -> bool:
        """更新用户学习进度"""
        try:
            progress, created = UserExpressionProgress.objects.get_or_create(
                user_id=user_id,
                expression_id=expression_id,
                defaults={
                    'mastery_level': mastery_level,
                    'is_favorite': is_favorite,
                    'last_practiced': timezone.now()
                }
            )
            
            if not created:
                progress.mastery_level = mastery_level
                progress.is_favorite = is_favorite
                progress.last_practiced = timezone.now()
                progress.save()
            
            return True
        except Exception as e:
            self.logger.error(f"更新用户进度失败: {e}")
            return False
    
    def get_recommended_expressions(self, user_id: int, limit: int = 10) -> List[IdiomaticExpression]:
        """获取推荐的地道表达"""
        try:
            # 获取用户已学习的表达ID
            learned_ids = UserExpressionProgress.objects.filter(
                user_id=user_id
            ).values_list('expression_id', flat=True)
            
            # 获取未学习的高频表达
            expressions = IdiomaticExpression.objects.filter(
                is_active=True
            ).exclude(
                id__in=learned_ids
            ).order_by('-frequency_score')[:limit]
            
            return list(expressions)
        except Exception as e:
            self.logger.error(f"获取推荐表达失败: {e}")
            return []
    
    def get_expression_statistics(self) -> Dict[str, int]:
        """获取地道表达统计信息"""
        try:
            stats = {
                'total_expressions': IdiomaticExpression.objects.filter(is_active=True).count(),
                'idioms': IdiomaticExpression.objects.filter(
                    expression_type='idiom', is_active=True
                ).count(),
                'phrasal_verbs': IdiomaticExpression.objects.filter(
                    expression_type='phrasal_verb', is_active=True
                ).count(),
                'collocations': IdiomaticExpression.objects.filter(
                    expression_type='collocation', is_active=True
                ).count(),
                'slang': IdiomaticExpression.objects.filter(
                    expression_type='slang', is_active=True
                ).count(),
            }
            return stats
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return {}
