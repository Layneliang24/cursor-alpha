"""
来源服务
提供数据来源相关的业务逻辑
"""

from django.db.models import Q, Count, Avg
from typing import List, Dict, Optional, Tuple
import logging

from ..models import ExpressionSource, IdiomaticExpression

logger = logging.getLogger(__name__)


class SourceService:
    """来源服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_sources_by_type(self, source_type: str, limit: int = 10) -> List[ExpressionSource]:
        """根据类型获取数据来源"""
        try:
            sources = ExpressionSource.objects.filter(
                source_type=source_type,
                is_active=True
            ).order_by('-reliability_score')[:limit]
            return list(sources)
        except Exception as e:
            self.logger.error(f"获取类型 {source_type} 的来源失败: {e}")
            return []
    
    def get_sources_by_reliability(self, min_score: int = 7, limit: int = 10) -> List[ExpressionSource]:
        """根据可靠性评分获取数据来源"""
        try:
            sources = ExpressionSource.objects.filter(
                reliability_score__gte=min_score,
                is_active=True
            ).order_by('-reliability_score')[:limit]
            return list(sources)
        except Exception as e:
            self.logger.error(f"获取可靠性评分 {min_score} 以上的来源失败: {e}")
            return []
    
    def search_sources(self, query: str, limit: int = 20) -> List[ExpressionSource]:
        """搜索数据来源"""
        try:
            sources = ExpressionSource.objects.filter(
                Q(source_name__icontains=query) |
                Q(description__icontains=query) |
                Q(source_type__icontains=query),
                is_active=True
            ).order_by('-reliability_score')[:limit]
            return list(sources)
        except Exception as e:
            self.logger.error(f"搜索来源失败: {e}")
            return []
    
    def get_source_statistics(self) -> Dict[str, any]:
        """获取来源统计信息"""
        try:
            stats = {
                'total_sources': ExpressionSource.objects.filter(is_active=True).count(),
                'web_sources': ExpressionSource.objects.filter(
                    source_type='web', is_active=True
                ).count(),
                'book_sources': ExpressionSource.objects.filter(
                    source_type='book', is_active=True
                ).count(),
                'academic_sources': ExpressionSource.objects.filter(
                    source_type='academic', is_active=True
                ).count(),
                'average_reliability': ExpressionSource.objects.filter(
                    is_active=True
                ).aggregate(Avg('reliability_score'))['reliability_score__avg'] or 0
            }
            return stats
        except Exception as e:
            self.logger.error(f"获取来源统计失败: {e}")
            return {}
    
    def get_source_with_expressions(self, source_id: int) -> Optional[Dict[str, any]]:
        """获取来源及其包含的地道表达"""
        try:
            source = ExpressionSource.objects.filter(
                id=source_id,
                is_active=True
            ).prefetch_related('expressions').first()
            
            if not source:
                return None
            
            expressions = []
            for expression in source.expressions.all():
                expressions.append({
                    'id': expression.id,
                    'expression': expression.expression,
                    'meaning': expression.meaning,
                    'difficulty_level': expression.difficulty_level,
                    'expression_type': expression.expression_type
                })
            
            return {
                'id': source.id,
                'source_name': source.source_name,
                'source_url': source.source_url,
                'source_type': source.source_type,
                'description': source.description,
                'reliability_score': source.reliability_score,
                'expressions_count': len(expressions),
                'expressions': expressions
            }
        except Exception as e:
            self.logger.error(f"获取来源详情失败: {e}")
            return None
    
    def get_popular_sources(self, limit: int = 10) -> List[ExpressionSource]:
        """获取热门数据来源"""
        try:
            # 根据来源包含的表达数量排序
            sources = ExpressionSource.objects.filter(
                is_active=True
            ).annotate(
                expression_count=Count('expressions')
            ).order_by('-expression_count', '-reliability_score')[:limit]
            
            return list(sources)
        except Exception as e:
            self.logger.error(f"获取热门来源失败: {e}")
            return []
    
    def validate_source_url(self, url: str) -> bool:
        """验证来源URL的有效性"""
        try:
            import re
            # 简单的URL格式验证
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            return bool(url_pattern.match(url))
        except Exception as e:
            self.logger.error(f"验证URL失败: {e}")
            return False
    
    def update_source_reliability(self, source_id: int, new_score: int) -> bool:
        """更新来源可靠性评分"""
        try:
            if not (1 <= new_score <= 10):
                self.logger.error(f"可靠性评分必须在1-10之间: {new_score}")
                return False
            
            source = ExpressionSource.objects.get(id=source_id)
            source.reliability_score = new_score
            source.save()
            
            self.logger.info(f"来源 {source.source_name} 的可靠性评分已更新为 {new_score}")
            return True
        except ExpressionSource.DoesNotExist:
            self.logger.error(f"来源 {source_id} 不存在")
            return False
        except Exception as e:
            self.logger.error(f"更新来源可靠性评分失败: {e}")
            return False
    
    def get_sources_by_expression_count(self, min_count: int = 5, limit: int = 10) -> List[ExpressionSource]:
        """根据包含的表达数量获取来源"""
        try:
            sources = ExpressionSource.objects.filter(
                is_active=True
            ).annotate(
                expression_count=Count('expressions')
            ).filter(
                expression_count__gte=min_count
            ).order_by('-expression_count')[:limit]
            
            return list(sources)
        except Exception as e:
            self.logger.error(f"根据表达数量获取来源失败: {e}")
            return []
