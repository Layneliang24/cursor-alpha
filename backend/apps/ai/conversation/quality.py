"""
对话质量评估

评估AI响应质量和用户满意度
"""

import re
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from django.db import models

from .context import ConversationContext

logger = logging.getLogger(__name__)


class QualityMetric(Enum):
    """质量评估指标"""
    RELEVANCE = "relevance"        # 相关性
    ACCURACY = "accuracy"          # 准确性
    HELPFULNESS = "helpfulness"    # 有用性
    CLARITY = "clarity"           # 清晰度
    COMPLETENESS = "completeness" # 完整性
    SAFETY = "safety"             # 安全性
    COHERENCE = "coherence"       # 连贯性


@dataclass
class QualityScore:
    """质量评分"""
    overall_score: float  # 总体评分 (0-1)
    metric_scores: Dict[QualityMetric, float]  # 各项指标评分
    confidence: float  # 评估置信度
    feedback: Optional[str] = None  # 反馈说明
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ConversationRating:
    """对话评价"""
    conversation_id: str
    user_rating: int  # 1-5星
    feedback: Optional[str] = None
    quality_aspects: Dict[str, int] = None  # 质量方面的具体评分
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class QualityMetrics:
    """质量评估指标计算器"""
    
    @staticmethod
    def calculate_relevance(user_message: str, ai_response: str) -> float:
        """计算相关性评分"""
        try:
            # 简单的关键词匹配
            user_words = set(re.findall(r'\w+', user_message.lower()))
            response_words = set(re.findall(r'\w+', ai_response.lower()))
            
            if not user_words:
                return 0.5
            
            # 计算词汇重叠度
            overlap = len(user_words & response_words)
            relevance = min(overlap / len(user_words), 1.0)
            
            # 调整评分：基础分0.3，重叠度贡献0.7
            return 0.3 + relevance * 0.7
            
        except Exception as e:
            logger.error(f"计算相关性失败: {e}")
            return 0.5
    
    @staticmethod
    def calculate_clarity(ai_response: str) -> float:
        """计算清晰度评分"""
        try:
            # 评估因素
            length = len(ai_response)
            sentences = len(re.findall(r'[.!?]+', ai_response))
            
            # 长度评分：适中长度得分高
            if 50 <= length <= 1000:
                length_score = 1.0
            elif length < 50:
                length_score = length / 50
            else:
                length_score = max(0.3, 1000 / length)
            
            # 句子结构评分
            if sentences > 0:
                avg_sentence_length = length / sentences
                if 10 <= avg_sentence_length <= 50:
                    structure_score = 1.0
                else:
                    structure_score = max(0.3, min(avg_sentence_length / 50, 50 / avg_sentence_length))
            else:
                structure_score = 0.5
            
            # 标点符号使用
            punctuation_count = len(re.findall(r'[,.!?;:]', ai_response))
            punctuation_score = min(punctuation_count / sentences if sentences > 0 else 0, 1.0)
            
            # 综合评分
            clarity = (length_score * 0.4 + structure_score * 0.4 + punctuation_score * 0.2)
            return min(clarity, 1.0)
            
        except Exception as e:
            logger.error(f"计算清晰度失败: {e}")
            return 0.5
    
    @staticmethod
    def calculate_completeness(user_message: str, ai_response: str) -> float:
        """计算完整性评分"""
        try:
            # 检查是否有问号（问题）
            has_question = '?' in user_message or '？' in user_message
            
            if has_question:
                # 问题类消息：检查是否有明确回答
                answer_indicators = ['因为', '由于', '答案是', '解释', '说明', 'because', 'answer', 'explain']
                has_answer = any(indicator in ai_response.lower() for indicator in answer_indicators)
                
                if has_answer:
                    return 0.9
                else:
                    # 检查响应长度，较长的响应可能更完整
                    return min(0.3 + len(ai_response) / 500, 0.8)
            else:
                # 非问题类消息：基于响应长度和内容丰富度
                length_score = min(len(ai_response) / 200, 1.0)
                
                # 检查是否有具体信息
                specific_indicators = ['例如', '比如', '具体', '详细', 'example', 'specific', 'detail']
                has_specifics = any(indicator in ai_response.lower() for indicator in specific_indicators)
                
                specifics_bonus = 0.2 if has_specifics else 0.0
                return min(length_score + specifics_bonus, 1.0)
                
        except Exception as e:
            logger.error(f"计算完整性失败: {e}")
            return 0.5
    
    @staticmethod
    def calculate_safety(ai_response: str) -> float:
        """计算安全性评分"""
        try:
            # 检查可能的有害内容
            harmful_patterns = [
                r'暴力', r'伤害', r'危险', r'违法', r'犯罪',
                r'violence', r'harmful', r'dangerous', r'illegal', r'crime'
            ]
            
            harmful_count = 0
            for pattern in harmful_patterns:
                if re.search(pattern, ai_response, re.IGNORECASE):
                    harmful_count += 1
            
            # 检查积极内容
            positive_patterns = [
                r'帮助', r'支持', r'建议', r'安全', r'健康',
                r'help', r'support', r'suggest', r'safe', r'healthy'
            ]
            
            positive_count = 0
            for pattern in positive_patterns:
                if re.search(pattern, ai_response, re.IGNORECASE):
                    positive_count += 1
            
            # 计算安全性评分
            if harmful_count > 0:
                safety = max(0.1, 1.0 - harmful_count * 0.3)
            else:
                safety = 0.8 + min(positive_count * 0.1, 0.2)
            
            return min(safety, 1.0)
            
        except Exception as e:
            logger.error(f"计算安全性失败: {e}")
            return 0.8  # 默认较高的安全性评分
    
    @staticmethod
    def calculate_coherence(ai_response: str, context: Optional[ConversationContext] = None) -> float:
        """计算连贯性评分"""
        try:
            # 内部连贯性：检查句子之间的逻辑关系
            sentences = re.split(r'[.!?]+', ai_response)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) < 2:
                return 0.8  # 单句响应默认较高连贯性
            
            # 检查连接词使用
            connectors = ['因此', '所以', '但是', '然而', '而且', '另外', 'therefore', 'however', 'furthermore']
            connector_count = sum(1 for conn in connectors if conn in ai_response.lower())
            connector_score = min(connector_count / len(sentences), 0.5)
            
            # 检查重复词汇（适度重复有助于连贯）
            words = re.findall(r'\w+', ai_response.lower())
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            repeated_words = sum(1 for count in word_counts.values() if count > 1)
            repetition_score = min(repeated_words / len(words) if words else 0, 0.3)
            
            # 上下文连贯性
            context_score = 0.2  # 默认值
            if context and len(context.messages) > 1:
                # 检查与前面消息的关联
                prev_user_msg = None
                for msg in reversed(context.messages[:-1]):
                    if msg.role.value == 'user':
                        prev_user_msg = msg.content
                        break
                
                if prev_user_msg:
                    # 简单的主题一致性检查
                    prev_words = set(re.findall(r'\w+', prev_user_msg.lower()))
                    curr_words = set(re.findall(r'\w+', ai_response.lower()))
                    topic_overlap = len(prev_words & curr_words) / len(prev_words) if prev_words else 0
                    context_score = min(topic_overlap, 0.5)
            
            # 综合评分
            coherence = 0.3 + connector_score + repetition_score + context_score
            return min(coherence, 1.0)
            
        except Exception as e:
            logger.error(f"计算连贯性失败: {e}")
            return 0.7


class QualityAssessor:
    """
    质量评估器
    
    评估AI响应的质量并提供改进建议
    """
    
    def __init__(self):
        """初始化评估器"""
        self.metrics = QualityMetrics()
    
    async def assess_response(
        self,
        user_message: str,
        ai_response: str,
        context: Optional[ConversationContext] = None
    ) -> float:
        """
        评估单个响应的质量
        
        Args:
            user_message: 用户消息
            ai_response: AI响应
            context: 对话上下文
            
        Returns:
            质量评分 (0-1)
        """
        try:
            # 计算各项指标
            metric_scores = {}
            
            metric_scores[QualityMetric.RELEVANCE] = self.metrics.calculate_relevance(
                user_message, ai_response
            )
            
            metric_scores[QualityMetric.CLARITY] = self.metrics.calculate_clarity(
                ai_response
            )
            
            metric_scores[QualityMetric.COMPLETENESS] = self.metrics.calculate_completeness(
                user_message, ai_response
            )
            
            metric_scores[QualityMetric.SAFETY] = self.metrics.calculate_safety(
                ai_response
            )
            
            metric_scores[QualityMetric.COHERENCE] = self.metrics.calculate_coherence(
                ai_response, context
            )
            
            # 计算加权总分
            weights = {
                QualityMetric.RELEVANCE: 0.25,
                QualityMetric.CLARITY: 0.20,
                QualityMetric.COMPLETENESS: 0.20,
                QualityMetric.SAFETY: 0.20,
                QualityMetric.COHERENCE: 0.15,
            }
            
            overall_score = sum(
                metric_scores[metric] * weight
                for metric, weight in weights.items()
            )
            
            logger.debug(f"质量评估完成: {overall_score:.3f}")
            return overall_score
            
        except Exception as e:
            logger.error(f"质量评估失败: {e}")
            return 0.5
    
    async def assess_conversation(
        self,
        context: ConversationContext
    ) -> Dict[str, Any]:
        """
        评估整个对话的质量
        
        Args:
            context: 对话上下文
            
        Returns:
            对话质量报告
        """
        try:
            if len(context.messages) < 2:
                return {
                    'overall_score': 0.5,
                    'message_scores': [],
                    'trends': {},
                    'recommendations': []
                }
            
            # 评估每个AI响应
            message_scores = []
            user_msg = None
            
            for msg in context.messages:
                if msg.role.value == 'user':
                    user_msg = msg
                elif msg.role.value == 'assistant' and user_msg:
                    score = await self.assess_response(
                        user_msg.content,
                        msg.content,
                        context
                    )
                    message_scores.append({
                        'user_message': user_msg.content[:100] + '...' if len(user_msg.content) > 100 else user_msg.content,
                        'ai_response': msg.content[:100] + '...' if len(msg.content) > 100 else msg.content,
                        'score': score,
                        'timestamp': datetime.fromtimestamp(getattr(msg, 'timestamp', time.time())).isoformat()
                    })
                    user_msg = None
            
            if not message_scores:
                return {
                    'overall_score': 0.5,
                    'message_scores': [],
                    'trends': {},
                    'recommendations': []
                }
            
            # 计算总体评分
            overall_score = sum(item['score'] for item in message_scores) / len(message_scores)
            
            # 分析趋势
            trends = self._analyze_quality_trends(message_scores)
            
            # 生成建议
            recommendations = self._generate_recommendations(overall_score, trends)
            
            return {
                'overall_score': overall_score,
                'message_count': len(message_scores),
                'message_scores': message_scores,
                'trends': trends,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"对话质量评估失败: {e}")
            return {
                'overall_score': 0.5,
                'message_scores': [],
                'trends': {},
                'recommendations': []
            }
    
    def _analyze_quality_trends(self, message_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析质量趋势"""
        if len(message_scores) < 3:
            return {'trend': 'insufficient_data'}
        
        scores = [item['score'] for item in message_scores]
        
        # 计算趋势
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        trend_direction = 'improving' if second_avg > first_avg else 'declining' if second_avg < first_avg else 'stable'
        trend_magnitude = abs(second_avg - first_avg)
        
        # 计算一致性
        score_variance = sum((score - sum(scores)/len(scores))**2 for score in scores) / len(scores)
        consistency = 'high' if score_variance < 0.01 else 'medium' if score_variance < 0.05 else 'low'
        
        return {
            'trend': trend_direction,
            'magnitude': trend_magnitude,
            'consistency': consistency,
            'first_half_avg': first_avg,
            'second_half_avg': second_avg,
            'variance': score_variance
        }
    
    def _generate_recommendations(self, overall_score: float, trends: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if overall_score < 0.6:
            recommendations.append("整体质量偏低，建议优化AI模型配置或提示词")
        
        if trends.get('trend') == 'declining':
            recommendations.append("质量呈下降趋势，可能需要重置对话或调整策略")
        
        if trends.get('consistency') == 'low':
            recommendations.append("响应质量不够稳定，建议优化上下文管理")
        
        if overall_score >= 0.8:
            recommendations.append("质量表现优秀，可作为最佳实践参考")
        
        if trends.get('trend') == 'improving':
            recommendations.append("质量呈上升趋势，当前策略效果良好")
        
        return recommendations
    
    async def record_user_feedback(
        self,
        conversation_id: str,
        rating: int,
        feedback: Optional[str] = None,
        quality_aspects: Optional[Dict[str, int]] = None
    ) -> bool:
        """
        记录用户反馈
        
        Args:
            conversation_id: 对话ID
            rating: 用户评分 (1-5)
            feedback: 文字反馈
            quality_aspects: 质量方面评分
            
        Returns:
            是否记录成功
        """
        try:
            # 这里可以保存到数据库或其他存储
            user_rating = ConversationRating(
                conversation_id=conversation_id,
                user_rating=rating,
                feedback=feedback,
                quality_aspects=quality_aspects
            )
            
            logger.info(f"记录用户反馈: {conversation_id}, 评分: {rating}")
            return True
            
        except Exception as e:
            logger.error(f"记录用户反馈失败: {e}")
            return False
    
    def get_quality_report(
        self,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        获取质量报告
        
        Args:
            period_days: 统计周期（天）
            
        Returns:
            质量报告
        """
        # TODO: 实现从数据库获取质量统计数据
        return {
            'period_days': period_days,
            'total_conversations': 0,
            'avg_quality_score': 0.0,
            'quality_distribution': {},
            'improvement_suggestions': []
        }
