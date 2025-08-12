"""
英语学习模块服务层
包含学习算法、统计分析等业务逻辑
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from django.utils import timezone
from django.db.models import Q, Count, Avg
from .models import (
    Word, UserWordProgress, Expression, News, 
    LearningPlan, PracticeRecord, LearningStats
)


class SM2Algorithm:
    """
    SM-2 间隔重复算法实现
    基于SuperMemo-2算法，用于优化记忆复习间隔
    """
    
    @staticmethod
    def calculate_next_review(
        ease_factor: float,
        interval_days: int,
        repetition_count: int,
        quality: int
    ) -> Tuple[float, int, int]:
        """
        计算下次复习时间
        
        Args:
            ease_factor: 容易度因子 (>=1.3)
            interval_days: 当前间隔天数
            repetition_count: 重复次数
            quality: 回答质量 (0-5)
                0: 完全不记得
                1: 错误答案，正确答案似乎很陌生
                2: 错误答案，但正确答案容易记起
                3: 正确答案，但需要努力回忆
                4: 正确答案，经过犹豫后回忆起
                5: 完美答案
        
        Returns:
            tuple: (new_ease_factor, new_interval_days, new_repetition_count)
        """
        # 更新容易度因子
        new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease_factor = max(1.3, new_ease_factor)  # 最小值1.3
        
        # 如果质量小于3，重置间隔
        if quality < 3:
            new_repetition_count = 0
            new_interval_days = 1
        else:
            new_repetition_count = repetition_count + 1
            
            if new_repetition_count == 1:
                new_interval_days = 1
            elif new_repetition_count == 2:
                new_interval_days = 6
            else:
                new_interval_days = int(interval_days * new_ease_factor)
        
        return new_ease_factor, new_interval_days, new_repetition_count
    
    @staticmethod
    def update_word_progress(user, word, quality: int) -> UserWordProgress:
        """
        更新用户单词学习进度
        
        Args:
            user: 用户实例
            word: 单词实例
            quality: 回答质量 (0-5)
        
        Returns:
            UserWordProgress: 更新后的进度记录
        """
        progress, created = UserWordProgress.objects.get_or_create(
            user=user,
            word=word,
            defaults={
                'status': 'learning',
                'ease_factor': Decimal('2.5'),
                'interval_days': 1,
                'repetition_count': 0,
                'mastery_level': Decimal('0.0')
            }
        )
        
        # 计算新的复习参数
        new_ease_factor, new_interval_days, new_repetition_count = SM2Algorithm.calculate_next_review(
            float(progress.ease_factor),
            progress.interval_days,
            progress.repetition_count,
            quality
        )
        
        # 更新进度记录
        progress.ease_factor = Decimal(str(new_ease_factor))
        progress.interval_days = new_interval_days
        progress.repetition_count = new_repetition_count
        progress.review_count += 1
        progress.last_review_date = timezone.now()
        progress.next_review_date = timezone.now() + timedelta(days=new_interval_days)
        
        # 更新掌握度 (基于质量和重复次数)
        mastery_increase = Decimal(str(quality * 0.1))
        progress.mastery_level = min(
            Decimal('1.0'),
            progress.mastery_level + mastery_increase
        )
        
        # 更新状态
        if progress.mastery_level >= Decimal('0.8') and progress.repetition_count >= 3:
            progress.status = 'mastered'
        elif progress.mastery_level >= Decimal('0.3'):
            progress.status = 'learning'
        else:
            progress.status = 'need_review'
        
        progress.save()
        return progress


class LearningPlanService:
    """学习计划服务"""
    
    @staticmethod
    def get_daily_words(user, plan: LearningPlan, date: Optional[datetime] = None) -> List[Word]:
        """
        获取每日学习单词
        
        Args:
            user: 用户实例
            plan: 学习计划
            date: 指定日期，默认今天
        
        Returns:
            List[Word]: 今日应学习的单词列表
        """
        if date is None:
            date = timezone.now().date()
        
        # 获取需要复习的单词
        review_words = Word.objects.filter(
            userwordprogress__user=user,
            userwordprogress__next_review_date__lte=timezone.now(),
            userwordprogress__status__in=['learning', 'need_review']
        ).order_by('userwordprogress__next_review_date')[:plan.daily_word_target // 2]
        
        # 获取新单词
        learned_word_ids = UserWordProgress.objects.filter(user=user).values_list('word_id', flat=True)
        new_words = Word.objects.exclude(id__in=learned_word_ids).order_by('frequency_rank')[:plan.daily_word_target - len(review_words)]
        
        return list(review_words) + list(new_words)
    
    @staticmethod
    def get_daily_expressions(user, plan: LearningPlan, date: Optional[datetime] = None) -> List[Expression]:
        """获取每日学习表达"""
        if date is None:
            date = timezone.now().date()
        
        return Expression.objects.order_by('?')[:plan.daily_expression_target]


class LearningStatsService:
    """学习统计服务"""
    
    @staticmethod
    def update_daily_stats(user, date: Optional[datetime] = None) -> LearningStats:
        """
        更新每日学习统计
        
        Args:
            user: 用户实例
            date: 统计日期，默认今天
        
        Returns:
            LearningStats: 统计记录
        """
        if date is None:
            date = timezone.now().date()
        
        stats, created = LearningStats.objects.get_or_create(
            user=user,
            date=date,
            defaults={
                'words_learned': 0,
                'words_reviewed': 0,
                'expressions_learned': 0,
                'news_read': 0,
                'practice_count': 0,
                'study_time_minutes': 0,
                'accuracy_rate': Decimal('0.0')
            }
        )
        
        # 统计当日数据
        today_start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        today_end = today_start + timedelta(days=1)
        
        # 统计练习记录
        practice_records = PracticeRecord.objects.filter(
            user=user,
            created_at__gte=today_start,
            created_at__lt=today_end
        )
        
        if practice_records.exists():
            stats.practice_count = practice_records.count()
            stats.accuracy_rate = practice_records.aggregate(
                avg_score=Avg('score')
            )['avg_score'] or Decimal('0.0')
        
        # 统计单词学习
        word_progress = UserWordProgress.objects.filter(
            user=user,
            updated_at__gte=today_start,
            updated_at__lt=today_end
        )
        
        stats.words_learned = word_progress.filter(review_count=1).count()
        stats.words_reviewed = word_progress.filter(review_count__gt=1).count()
        
        stats.save()
        return stats
    
    @staticmethod
    def get_learning_overview(user, days: int = 7) -> Dict:
        """
        获取学习概览数据
        
        Args:
            user: 用户实例
            days: 统计天数
        
        Returns:
            Dict: 学习概览数据
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days - 1)
        
        stats = LearningStats.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        # 总体统计
        total_words_learned = sum(s.words_learned for s in stats)
        total_words_reviewed = sum(s.words_reviewed for s in stats)
        total_practice_count = sum(s.practice_count for s in stats)
        total_study_time = sum(s.study_time_minutes for s in stats)
        
        # 掌握度统计
        mastery_stats = UserWordProgress.objects.filter(user=user).aggregate(
            total_words=Count('id'),
            mastered_words=Count('id', filter=Q(status='mastered')),
            learning_words=Count('id', filter=Q(status='learning')),
            need_review_words=Count('id', filter=Q(status='need_review'))
        )
        
        # 每日数据
        daily_data = []
        for stat in stats:
            daily_data.append({
                'date': stat.date.isoformat(),
                'words_learned': stat.words_learned,
                'words_reviewed': stat.words_reviewed,
                'practice_count': stat.practice_count,
                'study_time_minutes': stat.study_time_minutes,
                'accuracy_rate': float(stat.accuracy_rate)
            })
        
        return {
            'period': f'{start_date} 至 {end_date}',
            'total_stats': {
                'words_learned': total_words_learned,
                'words_reviewed': total_words_reviewed,
                'practice_count': total_practice_count,
                'study_time_minutes': total_study_time,
                'avg_daily_study_time': total_study_time / days if days > 0 else 0
            },
            'mastery_stats': mastery_stats,
            'daily_data': daily_data
        }


class PracticeService:
    """练习服务"""
    
    @staticmethod
    def generate_word_spelling_question(word: Word) -> Dict:
        """生成单词拼写题目"""
        return {
            'type': 'word_spelling',
            'question': f"请拼写单词：{word.definition}",
            'correct_answer': word.word,
            'word_id': word.id
        }
    
    @staticmethod
    def generate_word_meaning_question(word: Word) -> Dict:
        """生成单词释义题目"""
        # 这里可以添加选择题逻辑，随机选择其他单词作为干扰项
        return {
            'type': 'word_meaning',
            'question': f"单词 '{word.word}' 的意思是？",
            'correct_answer': word.definition,
            'word_id': word.id
        }
    
    @staticmethod
    def record_practice(user, practice_type: str, content_id: int, 
                       content_type: str, question: str, user_answer: str, 
                       correct_answer: str, time_spent: int) -> PracticeRecord:
        """记录练习结果"""
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
        score = Decimal('100.0') if is_correct else Decimal('0.0')
        
        record = PracticeRecord.objects.create(
            user=user,
            practice_type=practice_type,
            content_id=content_id,
            content_type=content_type,
            question=question,
            user_answer=user_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            score=score,
            time_spent=time_spent
        )
        
        # 如果是单词练习，更新单词进度
        if content_type == 'word' and practice_type in ['word_spelling', 'word_meaning']:
            try:
                word = Word.objects.get(id=content_id)
                quality = 5 if is_correct else 2  # 简化的质量评分
                SM2Algorithm.update_word_progress(user, word, quality)
            except Word.DoesNotExist:
                pass
        
        return record


class NewsService:
    """新闻服务"""
    
    @staticmethod
    def calculate_reading_difficulty(content: str) -> str:
        """
        计算文章阅读难度
        基于词汇复杂度、句子长度等因素
        """
        if not content:
            return 'intermediate'
        
        words = content.split()
        word_count = len(words)
        sentence_count = content.count('.') + content.count('!') + content.count('?')
        
        if sentence_count == 0:
            avg_sentence_length = word_count
        else:
            avg_sentence_length = word_count / sentence_count
        
        # 简化的难度计算
        if avg_sentence_length < 15 and word_count < 300:
            return 'beginner'
        elif avg_sentence_length > 25 or word_count > 800:
            return 'advanced'
        else:
            return 'intermediate'
    
    @staticmethod
    def extract_key_vocabulary(content: str, limit: int = 10) -> List[str]:
        """
        提取关键词汇
        这里使用简化的方法，实际应用中可以使用NLP库
        """
        if not content:
            return []
        
        # 简化实现：提取长度大于5的单词
        import re
        words = re.findall(r'\b[a-zA-Z]{5,}\b', content.lower())
        word_freq = {}
        
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序，返回前limit个
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:limit]]
    
    @staticmethod
    def generate_comprehension_questions(news: News) -> List[Dict]:
        """
        生成阅读理解题目
        这里提供基础框架，实际实现可能需要NLP技术
        """
        questions = []
        
        if news.content:
            # 示例：基于标题生成问题
            questions.append({
                'question': f"这篇文章的主要话题是什么？",
                'type': 'multiple_choice',
                'options': [
                    news.category or '未知',
                    '体育',
                    '科技',
                    '政治'
                ],
                'correct_answer': news.category or '未知'
            })
            
            # 可以添加更多类型的问题
            if news.summary:
                questions.append({
                    'question': '请概括文章的主要内容',
                    'type': 'text',
                    'reference_answer': news.summary
                })
        
        return questions
