"""
用户进度服务
提供用户学习进度相关的业务逻辑
"""

from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from typing import List, Dict, Optional, Tuple
import logging

from ..models import UserExpressionProgress, IdiomaticExpression
from apps.users.models import User

logger = logging.getLogger(__name__)


class UserProgressService:
    """用户进度服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_user_overall_progress(self, user_id: int) -> Dict[str, any]:
        """获取用户整体学习进度"""
        try:
            progress_records = UserExpressionProgress.objects.filter(user_id=user_id)
            
            total_expressions = progress_records.count()
            mastered_expressions = progress_records.filter(mastery_level__gte=5).count()
            favorite_expressions = progress_records.filter(is_favorite=True).count()
            
            if total_expressions > 0:
                mastery_rate = (mastered_expressions / total_expressions) * 100
                avg_mastery = progress_records.aggregate(Avg('mastery_level'))['mastery_level__avg'] or 0
            else:
                mastery_rate = 0
                avg_mastery = 0
            
            return {
                'total_expressions': total_expressions,
                'mastered_expressions': mastered_expressions,
                'favorite_expressions': favorite_expressions,
                'mastery_rate': round(mastery_rate, 2),
                'average_mastery': round(avg_mastery, 2)
            }
        except Exception as e:
            self.logger.error(f"获取用户整体进度失败: {e}")
            return {}
    
    def get_user_daily_progress(self, user_id: int, days: int = 7) -> List[Dict[str, any]]:
        """获取用户每日学习进度"""
        try:
            end_date = timezone.now()
            start_date = end_date - timezone.timedelta(days=days)
            
            daily_progress = []
            current_date = start_date
            
            while current_date <= end_date:
                next_date = current_date + timezone.timedelta(days=1)
                
                # 统计当天的学习活动
                day_records = UserExpressionProgress.objects.filter(
                    user_id=user_id,
                    last_practiced__gte=current_date,
                    last_practiced__lt=next_date
                )
                
                daily_progress.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'expressions_practiced': day_records.count(),
                    'new_mastery': day_records.filter(mastery_level__gte=5).count(),
                    'total_time': day_records.aggregate(Sum('practice_time'))['practice_time__sum'] or 0
                })
                
                current_date = next_date
            
            return daily_progress
        except Exception as e:
            self.logger.error(f"获取用户每日进度失败: {e}")
            return []
    
    def get_user_weak_areas(self, user_id: int, limit: int = 5) -> List[Dict[str, any]]:
        """获取用户薄弱领域"""
        try:
            weak_areas = UserExpressionProgress.objects.filter(
                user_id=user_id,
                mastery_level__lt=3
            ).select_related('expression').order_by('mastery_level')[:limit]
            
            result = []
            for progress in weak_areas:
                result.append({
                    'expression_id': progress.expression.id,
                    'expression': progress.expression.expression,
                    'meaning': progress.expression.meaning,
                    'mastery_level': progress.mastery_level,
                    'last_practiced': progress.last_practiced
                })
            
            return result
        except Exception as e:
            self.logger.error(f"获取用户薄弱领域失败: {e}")
            return []
    
    def get_user_strengths(self, user_id: int, limit: int = 5) -> List[Dict[str, any]]:
        """获取用户强项领域"""
        try:
            strengths = UserExpressionProgress.objects.filter(
                user_id=user_id,
                mastery_level__gte=4
            ).select_related('expression').order_by('-mastery_level')[:limit]
            
            result = []
            for progress in strengths:
                result.append({
                    'expression_id': progress.expression.id,
                    'expression': progress.expression.expression,
                    'meaning': progress.expression.meaning,
                    'mastery_level': progress.mastery_level,
                    'last_practiced': progress.last_practiced
                })
            
            return result
        except Exception as e:
            self.logger.error(f"获取用户强项失败: {e}")
            return []
    
    def get_user_learning_path(self, user_id: int) -> Dict[str, any]:
        """获取用户学习路径建议"""
        try:
            # 获取用户当前进度
            current_progress = self.get_user_overall_progress(user_id)
            
            # 根据掌握程度推荐学习内容
            if current_progress.get('mastery_rate', 0) < 30:
                # 初学者：推荐基础表达
                recommended_type = 'basic'
                difficulty = 'beginner'
            elif current_progress.get('mastery_rate', 0) < 60:
                # 中级：推荐常用表达
                recommended_type = 'common'
                difficulty = 'intermediate'
            else:
                # 高级：推荐高级表达
                recommended_type = 'advanced'
                difficulty = 'advanced'
            
            return {
                'current_level': difficulty,
                'recommended_type': recommended_type,
                'next_goals': [
                    f"掌握{difficulty}级别的地道表达",
                    "提高口语表达能力",
                    "扩展词汇量"
                ],
                'estimated_time': "2-3个月"
            }
        except Exception as e:
            self.logger.error(f"获取用户学习路径失败: {e}")
            return {}
    
    def update_user_practice_session(self, user_id: int, expression_ids: List[int], 
                                   practice_time: int, success_rate: float) -> bool:
        """更新用户练习会话"""
        try:
            for expression_id in expression_ids:
                progress, created = UserExpressionProgress.objects.get_or_create(
                    user_id=user_id,
                    expression_id=expression_id,
                    defaults={
                        'mastery_level': 1,
                        'practice_count': 1,
                        'practice_time': practice_time,
                        'success_rate': success_rate,
                        'last_practiced': timezone.now()
                    }
                )
                
                if not created:
                    # 更新现有进度
                    progress.practice_count += 1
                    progress.practice_time += practice_time
                    progress.success_rate = (progress.success_rate + success_rate) / 2
                    progress.last_practiced = timezone.now()
                    
                    # 根据成功率调整掌握程度
                    if success_rate >= 0.8:
                        progress.mastery_level = min(progress.mastery_level + 1, 5)
                    elif success_rate < 0.5:
                        progress.mastery_level = max(progress.mastery_level - 1, 1)
                    
                    progress.save()
            
            return True
        except Exception as e:
            self.logger.error(f"更新用户练习会话失败: {e}")
            return False
