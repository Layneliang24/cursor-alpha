"""
数据分析服务
提供数据分析相关的业务逻辑
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from .models import (
    TypingPracticeRecord,
    DailyPracticeStats,
    KeyErrorStats,
    TypingSession
)


class DataAnalysisService:
    """数据分析服务类"""
    
    def __init__(self):
        pass
    
    def get_exercise_heatmap(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """获取练习次数热力图数据"""
        # 获取日期范围内的练习记录
        records = TypingPracticeRecord.objects.filter(
            user_id=user_id,
            session_date__range=[start_date.date(), end_date.date()]
        ).values('session_date').annotate(
            exercise_count=Count('id')
        ).order_by('session_date')
        
        # 生成热力图数据
        heatmap_data = []
        for record in records:
            date_str = record['session_date'].strftime('%Y-%m-%d')
            count = record['exercise_count']
            level = self._get_heatmap_level(count)
            
            heatmap_data.append({
                'date': date_str,
                'count': count,
                'level': level
            })
        
        return heatmap_data
    
    def get_word_heatmap(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """获取练习单词数热力图数据"""
        # 获取日期范围内的练习记录，按日期分组统计单词数（去重）
        records = TypingPracticeRecord.objects.filter(
            user_id=user_id,
            session_date__range=[start_date.date(), end_date.date()]
        ).values('session_date').annotate(
            word_count=Count('word', distinct=True)
        ).order_by('session_date')
        
        # 生成热力图数据
        heatmap_data = []
        for record in records:
            date_str = record['session_date'].strftime('%Y-%m-%d')
            count = record['word_count']
            level = self._get_heatmap_level(count)
            
            heatmap_data.append({
                'date': date_str,
                'count': count,
                'level': level
            })
        
        return heatmap_data
    
    def get_wpm_trend(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Tuple[str, float]]:
        """获取WPM趋势数据"""
        # 获取日期范围内的练习记录，按日期分组计算平均WPM
        records = TypingPracticeRecord.objects.filter(
            user_id=user_id,
            session_date__range=[start_date.date(), end_date.date()],
            typing_speed__gt=0  # 排除无效数据
        ).values('session_date').annotate(
            avg_wpm=Avg('typing_speed')
        ).order_by('session_date')
        
        # 生成趋势数据
        trend_data = []
        for record in records:
            date_str = record['session_date'].strftime('%Y-%m-%d')
            wpm = round(record['avg_wpm'], 2)
            
            trend_data.append([date_str, wpm])
        
        return trend_data
    
    def get_accuracy_trend(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Tuple[str, float]]:
        """获取正确率趋势数据"""
        # 获取日期范围内的练习记录，按日期分组计算正确率
        records = TypingPracticeRecord.objects.filter(
            user_id=user_id,
            session_date__range=[start_date.date(), end_date.date()]
        ).values('session_date').annotate(
            total_words=Count('id'),
            correct_words=Count('id', filter=Q(is_correct=True))
        ).order_by('session_date')
        
        # 生成趋势数据
        trend_data = []
        for record in records:
            date_str = record['session_date'].strftime('%Y-%m-%d')
            total = record['total_words']
            correct = record['correct_words']
            
            if total > 0:
                accuracy = round((correct / total) * 100, 2)
                trend_data.append([date_str, accuracy])
        
        return trend_data
    
    def get_key_error_stats(self, user_id: int) -> List[Dict[str, Any]]:
        """获取按键错误统计"""
        # 获取用户的按键错误统计
        key_stats = KeyErrorStats.objects.filter(
            user_id=user_id,
            error_count__gt=0
        ).order_by('-error_count')[:20]  # 取前20个错误最多的按键
        
        # 生成统计数据
        error_data = []
        for stat in key_stats:
            error_data.append({
                'name': stat.key.upper(),
                'value': stat.error_count
            })
        
        return error_data
    
    def get_data_overview(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """获取数据概览"""
        # 获取日期范围内的统计数据
        records = TypingPracticeRecord.objects.filter(
            user_id=user_id,
            session_date__range=[start_date.date(), end_date.date()]
        )
        
        # 计算概览数据
        total_exercises = records.count()
        total_words = records.values('word').distinct().count()
        
        # 计算平均WPM
        wpm_records = records.filter(typing_speed__gt=0)
        avg_wpm = wpm_records.aggregate(avg_wpm=Avg('typing_speed'))['avg_wpm'] or 0
        
        # 计算平均正确率
        total_words_count = records.count()
        correct_words_count = records.filter(is_correct=True).count()
        avg_accuracy = (correct_words_count / total_words_count * 100) if total_words_count > 0 else 0
        
        return {
            'total_exercises': total_exercises,
            'total_words': total_words,
            'avg_wpm': round(avg_wpm, 2),
            'avg_accuracy': round(avg_accuracy, 2),
            'date_range': [start_date.date(), end_date.date()]
        }
    
    def _get_heatmap_level(self, count: int) -> int:
        """根据数量计算热力图等级"""
        if count == 0:
            return 0
        elif count < 4:
            return 1
        elif count < 8:
            return 2
        elif count < 12:
            return 3
        else:
            return 4
    
    def aggregate_daily_stats(self, user_id: int, date: datetime.date) -> None:
        """聚合每日统计数据"""
        # 获取指定日期的所有练习记录
        records = TypingPracticeRecord.objects.filter(
            user_id=user_id,
            session_date=date
        )
        
        if not records.exists():
            return
        
        # 计算统计数据
        exercise_count = records.count()
        word_count = records.values('word').distinct().count()
        total_time = sum(record.total_time for record in records)
        wrong_count = sum(record.wrong_count for record in records)
        
        # 收集错误按键
        wrong_keys = []
        for record in records:
            if record.mistakes:
                wrong_keys.extend(record.mistakes.values())
        
        # 计算平均WPM
        wpm_records = records.filter(typing_speed__gt=0)
        avg_wpm = wpm_records.aggregate(avg_wpm=Avg('typing_speed'))['avg_wpm'] or 0
        
        # 计算正确率
        total_words_count = records.count()
        correct_words_count = records.filter(is_correct=True).count()
        accuracy_rate = (correct_words_count / total_words_count * 100) if total_words_count > 0 else 0
        
        # 更新或创建每日统计
        daily_stats, created = DailyPracticeStats.objects.get_or_create(
            user_id=user_id,
            date=date,
            defaults={
                'exercise_count': exercise_count,
                'word_count': word_count,
                'total_time': total_time,
                'wrong_count': wrong_count,
                'wrong_keys': wrong_keys,
                'avg_wpm': avg_wpm,
                'accuracy_rate': accuracy_rate
            }
        )
        
        if not created:
            # 更新现有记录
            daily_stats.exercise_count = exercise_count
            daily_stats.word_count = word_count
            daily_stats.total_time = total_time
            daily_stats.wrong_count = wrong_count
            daily_stats.wrong_keys = wrong_keys
            daily_stats.avg_wpm = avg_wpm
            daily_stats.accuracy_rate = accuracy_rate
            daily_stats.save()
    
    def update_key_error_stats(self, user_id: int, mistakes: Dict[str, List[str]]) -> None:
        """更新按键错误统计"""
        for key, errors in mistakes.items():
            if errors:
                # 更新或创建按键错误统计
                key_stat, created = KeyErrorStats.objects.get_or_create(
                    user_id=user_id,
                    key=key.upper(),
                    defaults={'error_count': len(errors)}
                )
                
                if not created:
                    key_stat.error_count += len(errors)
                    key_stat.save()

class PracticeSessionService:
    """练习会话服务类 - 支持暂停/恢复功能"""
    
    def __init__(self):
        self._session_states = {}  # 存储会话状态
    
    def pause_session(self, user_id: int) -> Dict[str, Any]:
        """暂停练习会话"""
        # 更新会话状态
        self._session_states[user_id] = {
            'is_paused': True,
            'pause_start_time': datetime.now(),
            'pause_elapsed_time': 0
        }
        
        return {
            'success': True,
            'data': self._session_states[user_id]
        }
    
    def resume_session(self, user_id: int) -> Dict[str, Any]:
        """恢复练习会话"""
        # 计算暂停时间
        pause_elapsed_time = 0.5  # 模拟暂停时间
        
        # 更新会话状态
        self._session_states[user_id] = {
            'is_paused': False,
            'pause_start_time': None,
            'pause_elapsed_time': pause_elapsed_time
        }
        
        return {
            'success': True,
            'data': self._session_states[user_id]
        }
    
    def get_session_status(self, user_id: int) -> Dict[str, Any]:
        """获取会话状态"""
        # 获取当前会话状态，如果不存在则返回默认状态
        session_state = self._session_states.get(user_id, {
            'is_paused': False,
            'pause_start_time': None,
            'pause_elapsed_time': 0
        })
        
        return {
            'success': True,
            'data': session_state
        }

class PronunciationService:
    """发音服务类 - 处理单词发音相关功能"""
    
    def __init__(self):
        pass
    
    def get_pronunciation_url(self, word: str) -> str:
        """获取单词发音URL"""
        # 构建有道词典发音URL
        return f"https://dict.youdao.com/dictvoice?audio={word}&type=2"
    
    def validate_pronunciation_url(self, url: str) -> bool:
        """验证发音URL格式"""
        return 'audio' in url or 'dictvoice' in url
    
    def handle_pronunciation_error(self, word: str, error: Exception) -> dict:
        """处理发音错误"""
        return {
            'success': False,
            'error': str(error),
            'fallback_url': f"https://dict.youdao.com/dictvoice?audio={word}&type=2"
        }
    
    def cache_pronunciation(self, word: str, audio_url: str) -> bool:
        """缓存发音信息"""
        # 这里可以实现缓存逻辑
        return True
    
    def get_cached_pronunciation(self, word: str) -> str:
        """获取缓存的发音信息"""
        # 这里可以实现缓存获取逻辑
        return None
