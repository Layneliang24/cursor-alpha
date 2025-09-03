"""
场景服务
提供学习场景相关的业务逻辑
"""

from django.db.models import Q, Count, Prefetch
from typing import List, Dict, Optional, Tuple
import logging

from ..models import ExpressionScenario, ExpressionScenarioLink, IdiomaticExpression

logger = logging.getLogger(__name__)


class ScenarioService:
    """场景服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_scenarios_by_category(self, category: str, limit: int = 10) -> List[ExpressionScenario]:
        """根据类别获取学习场景"""
        try:
            scenarios = ExpressionScenario.objects.filter(
                category=category,
                is_active=True
            ).prefetch_related('expressions').order_by('-difficulty_level')[:limit]
            return list(scenarios)
        except Exception as e:
            self.logger.error(f"获取类别 {category} 的场景失败: {e}")
            return []
    
    def get_scenarios_by_difficulty(self, difficulty_level: str, limit: int = 10) -> List[ExpressionScenario]:
        """根据难度级别获取学习场景"""
        try:
            scenarios = ExpressionScenario.objects.filter(
                difficulty_level=difficulty_level,
                is_active=True
            ).prefetch_related('expressions').order_by('?')[:limit]
            return list(scenarios)
        except Exception as e:
            self.logger.error(f"获取难度级别 {difficulty_level} 的场景失败: {e}")
            return []
    
    def get_scenario_with_expressions(self, scenario_id: int) -> Optional[Dict[str, any]]:
        """获取场景及其包含的地道表达"""
        try:
            scenario = ExpressionScenario.objects.filter(
                id=scenario_id,
                is_active=True
            ).prefetch_related(
                Prefetch(
                    'expressions',
                    queryset=IdiomaticExpression.objects.filter(is_active=True)
                )
            ).first()
            
            if not scenario:
                return None
            
            expressions = []
            for link in scenario.expressions.all():
                expressions.append({
                    'id': link.id,
                    'expression': link.expression,
                    'meaning': link.meaning,
                    'difficulty_level': link.difficulty_level,
                    'expression_type': link.expression_type
                })
            
            return {
                'id': scenario.id,
                'title': scenario.title,
                'description': scenario.description,
                'category': scenario.category,
                'difficulty_level': scenario.difficulty_level,
                'expressions': expressions
            }
        except Exception as e:
            self.logger.error(f"获取场景详情失败: {e}")
            return None
    
    def search_scenarios(self, query: str, limit: int = 20) -> List[ExpressionScenario]:
        """搜索学习场景"""
        try:
            scenarios = ExpressionScenario.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__icontains=query),
                is_active=True
            ).order_by('-difficulty_level')[:limit]
            return list(scenarios)
        except Exception as e:
            self.logger.error(f"搜索场景失败: {e}")
            return []
    
    def get_scenario_statistics(self) -> Dict[str, int]:
        """获取场景统计信息"""
        try:
            stats = {
                'total_scenarios': ExpressionScenario.objects.filter(is_active=True).count(),
                'beginner_scenarios': ExpressionScenario.objects.filter(
                    difficulty_level='beginner', is_active=True
                ).count(),
                'intermediate_scenarios': ExpressionScenario.objects.filter(
                    difficulty_level='intermediate', is_active=True
                ).count(),
                'advanced_scenarios': ExpressionScenario.objects.filter(
                    difficulty_level='advanced', is_active=True
                ).count(),
            }
            return stats
        except Exception as e:
            self.logger.error(f"获取场景统计失败: {e}")
            return {}
    
    def get_scenarios_by_expression_type(self, expression_type: str, limit: int = 10) -> List[ExpressionScenario]:
        """根据表达类型获取相关场景"""
        try:
            # 通过场景链接表查找包含特定类型表达的场景
            scenario_ids = ExpressionScenarioLink.objects.filter(
                expression__expression_type=expression_type,
                expression__is_active=True
            ).values_list('scenario_id', flat=True).distinct()
            
            scenarios = ExpressionScenario.objects.filter(
                id__in=scenario_ids,
                is_active=True
            ).order_by('-difficulty_level')[:limit]
            
            return list(scenarios)
        except Exception as e:
            self.logger.error(f"根据表达类型获取场景失败: {e}")
            return []
    
    def get_popular_scenarios(self, limit: int = 10) -> List[ExpressionScenario]:
        """获取热门学习场景"""
        try:
            # 根据场景包含的表达数量和使用频率排序
            scenarios = ExpressionScenario.objects.filter(
                is_active=True
            ).annotate(
                expression_count=Count('expressions')
            ).order_by('-expression_count', '-difficulty_level')[:limit]
            
            return list(scenarios)
        except Exception as e:
            self.logger.error(f"获取热门场景失败: {e}")
            return []
    
    def create_custom_scenario(self, user_id: int, title: str, description: str, 
                             category: str, difficulty_level: str, expression_ids: List[int]) -> Optional[int]:
        """创建自定义学习场景"""
        try:
            # 创建场景
            scenario = ExpressionScenario.objects.create(
                title=title,
                description=description,
                category=category,
                difficulty_level=difficulty_level,
                created_by_id=user_id,
                is_custom=True,
                is_active=True
            )
            
            # 添加表达链接
            for expression_id in expression_ids:
                ExpressionScenarioLink.objects.create(
                    scenario=scenario,
                    expression_id=expression_id
                )
            
            return scenario.id
        except Exception as e:
            self.logger.error(f"创建自定义场景失败: {e}")
            return None
