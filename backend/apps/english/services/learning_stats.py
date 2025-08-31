"""
学习统计服务
提供学习统计相关的业务逻辑
"""
from datetime import timedelta
from django.utils import timezone
from ..models import LearningStats


class LearningStatsService:
    """学习统计服务类"""
    
    @staticmethod
    def update_daily_stats(user):
        """更新用户每日统计"""
        today = timezone.now().date()
        
        stats, created = LearningStats.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'words_learned': 0,
                'words_reviewed': 0,
                'expressions_learned': 0,
                'news_read': 0,
                'practice_count': 0,
                'study_time_minutes': 0,
                'accuracy_rate': 0.0
            }
        )
        
        # 这里可以添加更多统计逻辑
        return stats
    
    @staticmethod
    def get_learning_overview(user, days=7):
        """获取学习概览"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 获取指定天数内的统计数据
        stats = LearningStats.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).order_by('-date')
        
        # 计算总计数据
        total_words_learned = sum(stat.words_learned for stat in stats)
        total_words_reviewed = sum(stat.words_reviewed for stat in stats)
        total_expressions_learned = sum(stat.expressions_learned for stat in stats)
        total_practice_count = sum(stat.practice_count for stat in stats)
        total_study_time = sum(stat.study_time_minutes for stat in stats)
        
        # 计算平均正确率
        accuracy_rates = [stat.accuracy_rate for stat in stats if stat.accuracy_rate > 0]
        avg_accuracy = sum(accuracy_rates) / len(accuracy_rates) if accuracy_rates else 0
        
        return {
            'days': days,
            'total_words_learned': total_words_learned,
            'total_words_reviewed': total_words_reviewed,
            'total_expressions_learned': total_expressions_learned,
            'total_practice_count': total_practice_count,
            'total_study_time_minutes': total_study_time,
            'average_accuracy_rate': round(avg_accuracy, 2),
            'daily_stats': [
                {
                    'date': stat.date.isoformat(),
                    'words_learned': stat.words_learned,
                    'words_reviewed': stat.words_reviewed,
                    'expressions_learned': stat.expressions_learned,
                    'practice_count': stat.practice_count,
                    'study_time_minutes': stat.study_time_minutes,
                    'accuracy_rate': float(stat.accuracy_rate)
                }
                for stat in stats
            ]
        }
