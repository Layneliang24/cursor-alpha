"""
AI响应质量评估器

评估AI助教响应的质量，收集用户反馈，优化服务质量
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db import models
from django.db.models import Avg, Count, Sum, F
from django.utils import timezone

logger = logging.getLogger(__name__)


class QualityDimension(Enum):
    """质量评估维度"""
    ACCURACY = "accuracy"           # 准确性
    RELEVANCE = "relevance"         # 相关性
    HELPFULNESS = "helpfulness"     # 有用性
    CLARITY = "clarity"            # 清晰度
    COMPLETENESS = "completeness"   # 完整性
    CREATIVITY = "creativity"       # 创造性
    CULTURAL_SENSITIVITY = "cultural_sensitivity"  # 文化敏感性


@dataclass
class QualityMetrics:
    """质量指标"""
    overall_score: float
    dimension_scores: Dict[QualityDimension, float]
    confidence: float
    feedback_items: List[str]
    

class ResponseQualityRecord(models.Model):
    """响应质量记录模型"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    function_type = models.CharField(max_length=50, db_index=True)
    
    # 请求内容
    user_input = models.TextField()
    ai_response = models.TextField()
    
    # 自动评估分数
    auto_accuracy_score = models.FloatField(null=True, blank=True)
    auto_relevance_score = models.FloatField(null=True, blank=True)
    auto_helpfulness_score = models.FloatField(null=True, blank=True)
    auto_clarity_score = models.FloatField(null=True, blank=True)
    auto_completeness_score = models.FloatField(null=True, blank=True)
    auto_overall_score = models.FloatField(null=True, blank=True)
    
    # 用户反馈
    user_rating = models.IntegerField(null=True, blank=True)  # 1-5星
    user_feedback = models.TextField(blank=True)
    user_thumbs_up = models.BooleanField(null=True, blank=True)
    
    # 元数据
    ai_model = models.CharField(max_length=100)
    ai_provider = models.CharField(max_length=50)
    response_time = models.FloatField(null=True, blank=True)
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # 附加信息
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'ai_response_quality'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['function_type', '-created_at']),
            models.Index(fields=['ai_provider', '-created_at']),
            models.Index(fields=['-created_at']),
        ]


class ResponseQualityAssessor:
    """
    AI响应质量评估器
    
    自动评估AI响应质量，收集用户反馈，提供质量分析
    """
    
    def __init__(self):
        """初始化质量评估器"""
        # 评估权重配置
        self.dimension_weights = {
            QualityDimension.ACCURACY: 0.25,
            QualityDimension.RELEVANCE: 0.20,
            QualityDimension.HELPFULNESS: 0.20,
            QualityDimension.CLARITY: 0.15,
            QualityDimension.COMPLETENESS: 0.15,
            QualityDimension.CREATIVITY: 0.05,
        }
        
        # 质量阈值
        self.quality_thresholds = {
            'excellent': 0.9,
            'good': 0.75,
            'acceptable': 0.6,
            'poor': 0.4
        }
        
        logger.info("响应质量评估器已初始化")
    
    async def assess_response(
        self,
        user_input: str,
        ai_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        评估AI响应质量
        
        Args:
            user_input: 用户输入
            ai_response: AI响应
            context: 上下文信息
            
        Returns:
            质量评分 (0-1)
        """
        try:
            # 计算各维度评分
            dimension_scores = {}
            
            dimension_scores[QualityDimension.ACCURACY] = self._assess_accuracy(
                user_input, ai_response, context
            )
            dimension_scores[QualityDimension.RELEVANCE] = self._assess_relevance(
                user_input, ai_response
            )
            dimension_scores[QualityDimension.HELPFULNESS] = self._assess_helpfulness(
                user_input, ai_response
            )
            dimension_scores[QualityDimension.CLARITY] = self._assess_clarity(
                ai_response
            )
            dimension_scores[QualityDimension.COMPLETENESS] = self._assess_completeness(
                user_input, ai_response
            )
            dimension_scores[QualityDimension.CREATIVITY] = self._assess_creativity(
                ai_response
            )
            
            # 计算加权总分
            overall_score = sum(
                score * self.dimension_weights.get(dimension, 0)
                for dimension, score in dimension_scores.items()
            )
            
            # 确保分数在有效范围内
            overall_score = max(0, min(1, overall_score))
            
            logger.debug(f"质量评估完成: {overall_score:.3f}")
            return overall_score
            
        except Exception as e:
            logger.error(f"质量评估失败: {e}")
            return 0.5  # 返回中等分数
    
    def _assess_accuracy(
        self,
        user_input: str,
        ai_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """评估准确性"""
        score = 0.8  # 基础分数
        
        # 检查是否包含明显错误信息
        error_patterns = [
            r'(?i)(sorry|apologize|cannot|unable|don\'t know)',
            r'(?i)(错误|抱歉|不知道|无法|不能)',
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, ai_response):
                score -= 0.2
                break
        
        # 检查是否提供了具体信息
        if len(ai_response) < 50:
            score -= 0.1
        elif re.search(r'[具体例子示例比如举例]', ai_response):
            score += 0.1
        
        return max(0, min(1, score))
    
    def _assess_relevance(self, user_input: str, ai_response: str) -> float:
        """评估相关性"""
        # 提取关键词
        user_keywords = set(re.findall(r'\w+', user_input.lower()))
        response_keywords = set(re.findall(r'\w+', ai_response.lower()))
        
        if not user_keywords:
            return 0.5
        
        # 计算关键词重叠度
        overlap = len(user_keywords & response_keywords)
        relevance = min(overlap / len(user_keywords), 1.0)
        
        # 基础相关性分数
        base_score = 0.3 + relevance * 0.7
        
        # 检查是否回答了问题
        if '?' in user_input or '？' in user_input:
            # 这是一个问题，检查是否有回答指示词
            answer_indicators = [
                '是', '不是', '可以', '不可以', '因为', '由于', '答案',
                'yes', 'no', 'because', 'answer', 'solution'
            ]
            if any(indicator in ai_response.lower() for indicator in answer_indicators):
                base_score += 0.1
        
        return max(0, min(1, base_score))
    
    def _assess_helpfulness(self, user_input: str, ai_response: str) -> float:
        """评估有用性"""
        score = 0.7  # 基础分数
        
        # 检查是否提供了实用建议
        helpful_patterns = [
            r'建议|推荐|可以|试试|方法|步骤',
            r'suggest|recommend|try|method|step|tip'
        ]
        
        for pattern in helpful_patterns:
            if re.search(pattern, ai_response, re.IGNORECASE):
                score += 0.1
                break
        
        # 检查是否提供了具体例子
        example_patterns = [
            r'例如|比如|举例|示例|样例',
            r'example|instance|such as|for example'
        ]
        
        for pattern in example_patterns:
            if re.search(pattern, ai_response, re.IGNORECASE):
                score += 0.1
                break
        
        # 检查是否包含进一步帮助的信息
        if re.search(r'还有|另外|此外|additionally|furthermore|also', ai_response, re.IGNORECASE):
            score += 0.1
        
        return max(0, min(1, score))
    
    def _assess_clarity(self, ai_response: str) -> float:
        """评估清晰度"""
        # 长度评分
        length = len(ai_response)
        if 50 <= length <= 1000:
            length_score = 1.0
        elif length < 50:
            length_score = length / 50
        else:
            length_score = max(0.3, 1000 / length)
        
        # 句子结构评分
        sentences = len(re.findall(r'[.!?。！？]+', ai_response))
        if sentences > 0:
            avg_sentence_length = length / sentences
            if 10 <= avg_sentence_length <= 80:
                structure_score = 1.0
            else:
                structure_score = max(0.3, min(80 / avg_sentence_length, avg_sentence_length / 80))
        else:
            structure_score = 0.5
        
        # 标点符号使用
        punctuation_count = len(re.findall(r'[,.!?;:，。！？；：]', ai_response))
        punctuation_score = min(punctuation_count / max(sentences, 1), 1.0)
        
        # 综合评分
        clarity = length_score * 0.4 + structure_score * 0.4 + punctuation_score * 0.2
        return max(0, min(1, clarity))
    
    def _assess_completeness(self, user_input: str, ai_response: str) -> float:
        """评估完整性"""
        # 检查是否是问题
        is_question = '?' in user_input or '？' in user_input
        
        if is_question:
            # 问题类：检查是否有明确回答
            answer_indicators = [
                '因为', '由于', '答案是', '解释', '说明', 
                'because', 'answer', 'explain', 'reason'
            ]
            has_answer = any(indicator in ai_response.lower() for indicator in answer_indicators)
            
            if has_answer:
                return 0.9
            else:
                # 基于响应长度判断完整性
                return min(0.3 + len(ai_response) / 500, 0.8)
        else:
            # 非问题类：基于响应的全面性
            length_score = min(len(ai_response) / 200, 1.0)
            
            # 检查是否有具体信息
            specific_indicators = [
                '例如', '比如', '具体', '详细', 
                'example', 'specific', 'detail', 'particular'
            ]
            has_specifics = any(indicator in ai_response.lower() for indicator in specific_indicators)
            
            specifics_bonus = 0.2 if has_specifics else 0.0
            return min(length_score + specifics_bonus, 1.0)
    
    def _assess_creativity(self, ai_response: str) -> float:
        """评估创造性"""
        score = 0.5  # 基础分数
        
        # 检查是否有创新性表达
        creative_indicators = [
            '创新', '独特', '新颖', '有趣', '生动',
            'creative', 'unique', 'innovative', 'interesting', 'vivid'
        ]
        
        for indicator in creative_indicators:
            if indicator in ai_response.lower():
                score += 0.1
                break
        
        # 检查是否使用了比喻或类比
        metaphor_patterns = [
            r'就像|好比|类似于|仿佛|如同',
            r'like|similar to|as if|just as|analogous'
        ]
        
        for pattern in metaphor_patterns:
            if re.search(pattern, ai_response, re.IGNORECASE):
                score += 0.2
                break
        
        # 检查是否有多样化的表达
        if len(set(re.findall(r'\w+', ai_response.lower()))) / max(len(ai_response.split()), 1) > 0.7:
            score += 0.1
        
        return max(0, min(1, score))
    
    async def record_quality_assessment(
        self,
        user: User,
        function_type: str,
        user_input: str,
        ai_response: str,
        ai_model: str,
        ai_provider: str,
        auto_scores: Optional[Dict[QualityDimension, float]] = None,
        response_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ResponseQualityRecord:
        """
        记录质量评估结果
        
        Args:
            user: 用户对象
            function_type: 功能类型
            user_input: 用户输入
            ai_response: AI响应
            ai_model: AI模型
            ai_provider: AI提供商
            auto_scores: 自动评分
            response_time: 响应时间
            metadata: 元数据
            
        Returns:
            质量记录对象
        """
        try:
            # 如果没有提供自动评分，进行评估
            if not auto_scores:
                overall_score = await self.assess_response(user_input, ai_response)
                auto_scores = {QualityDimension.ACCURACY: overall_score}
            
            # 创建质量记录
            record = ResponseQualityRecord.objects.create(
                user=user,
                function_type=function_type,
                user_input=user_input,
                ai_response=ai_response,
                ai_model=ai_model,
                ai_provider=ai_provider,
                auto_accuracy_score=auto_scores.get(QualityDimension.ACCURACY),
                auto_relevance_score=auto_scores.get(QualityDimension.RELEVANCE),
                auto_helpfulness_score=auto_scores.get(QualityDimension.HELPFULNESS),
                auto_clarity_score=auto_scores.get(QualityDimension.CLARITY),
                auto_completeness_score=auto_scores.get(QualityDimension.COMPLETENESS),
                auto_overall_score=sum(auto_scores.values()) / len(auto_scores) if auto_scores else 0.5,
                response_time=response_time,
                metadata=metadata or {}
            )
            
            logger.info(f"记录质量评估: 用户{user.id}, 功能{function_type}, 评分{record.auto_overall_score:.3f}")
            return record
            
        except Exception as e:
            logger.error(f"记录质量评估失败: {e}")
            raise
    
    async def record_user_feedback(
        self,
        record_id: int,
        user_rating: Optional[int] = None,
        user_feedback: Optional[str] = None,
        thumbs_up: Optional[bool] = None
    ) -> bool:
        """
        记录用户反馈
        
        Args:
            record_id: 质量记录ID
            user_rating: 用户评分 (1-5)
            user_feedback: 用户反馈文本
            thumbs_up: 点赞/踩
            
        Returns:
            是否成功记录
        """
        try:
            record = ResponseQualityRecord.objects.get(id=record_id)
            
            if user_rating is not None:
                record.user_rating = user_rating
            
            if user_feedback is not None:
                record.user_feedback = user_feedback
            
            if thumbs_up is not None:
                record.user_thumbs_up = thumbs_up
            
            record.save()
            
            logger.info(f"记录用户反馈: 记录{record_id}, 评分{user_rating}")
            return True
            
        except ResponseQualityRecord.DoesNotExist:
            logger.error(f"质量记录不存在: {record_id}")
            return False
        except Exception as e:
            logger.error(f"记录用户反馈失败: {e}")
            return False
    
    async def get_quality_report(
        self,
        user: Optional[User] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取质量报告
        
        Args:
            user: 用户对象（可选，为空则获取全局报告）
            days: 统计天数
            
        Returns:
            质量报告
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # 构建查询
        queryset = ResponseQualityRecord.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        if user:
            queryset = queryset.filter(user=user)
        
        # 基础统计
        total_stats = queryset.aggregate(
            total_responses=Count('id'),
            avg_auto_score=Avg('auto_overall_score'),
            avg_user_rating=Avg('user_rating'),
            thumbs_up_rate=Avg('user_thumbs_up', output_field=models.FloatField()),
            avg_response_time=Avg('response_time')
        )
        
        # 按功能类型统计
        function_stats = list(
            queryset.values('function_type')
            .annotate(
                responses=Count('id'),
                avg_score=Avg('auto_overall_score'),
                avg_rating=Avg('user_rating')
            )
            .order_by('-avg_score')
        )
        
        # 按模型统计
        model_stats = list(
            queryset.values('ai_provider', 'ai_model')
            .annotate(
                responses=Count('id'),
                avg_score=Avg('auto_overall_score'),
                avg_rating=Avg('user_rating')
            )
            .order_by('-avg_score')
        )
        
        # 质量趋势
        daily_trends = list(
            queryset.extra(select={'date': 'DATE(created_at)'})
            .values('date')
            .annotate(
                responses=Count('id'),
                avg_score=Avg('auto_overall_score'),
                avg_rating=Avg('user_rating')
            )
            .order_by('date')
        )
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'total': {
                'responses': total_stats['total_responses'] or 0,
                'avg_auto_score': total_stats['avg_auto_score'] or 0,
                'avg_user_rating': total_stats['avg_user_rating'] or 0,
                'thumbs_up_rate': (total_stats['thumbs_up_rate'] or 0) * 100,
                'avg_response_time': total_stats['avg_response_time'] or 0
            },
            'by_function': function_stats,
            'by_model': model_stats,
            'daily_trends': daily_trends
        }
    
    async def get_low_quality_responses(
        self,
        threshold: float = 0.5,
        days: int = 7,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取低质量响应列表
        
        Args:
            threshold: 质量阈值
            days: 查询天数
            limit: 限制数量
            
        Returns:
            低质量响应列表
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        low_quality_records = ResponseQualityRecord.objects.filter(
            created_at__gte=start_date,
            auto_overall_score__lt=threshold
        ).order_by('auto_overall_score')[:limit]
        
        results = []
        for record in low_quality_records:
            results.append({
                'id': record.id,
                'user_id': record.user.id,
                'function_type': record.function_type,
                'user_input': record.user_input[:200],  # 截取前200字符
                'ai_response': record.ai_response[:200],
                'auto_score': record.auto_overall_score,
                'user_rating': record.user_rating,
                'ai_model': record.ai_model,
                'created_at': record.created_at.isoformat()
            })
        
        return results
