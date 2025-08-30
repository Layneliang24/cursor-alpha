"""
学习数据分析服务模块

该模块实现了核心的学习分析算法，包括：
- 掌握度计算
- 遗忘曲线分析
- 学习效率评估
- 学习洞察生成
- SM-2间隔重复算法优化
"""

import math
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum

from django.db.models import Count, Avg, Sum, F, Q, Max, Min
from django.db.models.functions import Extract, TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

from ..models import UserExpressionProgress, IdiomaticExpression

User = get_user_model()
logger = logging.getLogger(__name__)


class MasteryLevel(Enum):
    """掌握度等级"""
    UNKNOWN = 0      # 未知
    BEGINNER = 1     # 初学者
    BASIC = 2        # 基础
    INTERMEDIATE = 3 # 中级
    ADVANCED = 4     # 高级
    EXPERT = 5       # 专家


class LearningPhase(Enum):
    """学习阶段"""
    ACQUISITION = "acquisition"      # 习得阶段
    CONSOLIDATION = "consolidation"  # 巩固阶段
    RETENTION = "retention"         # 保持阶段
    MASTERY = "mastery"            # 精通阶段


@dataclass
class LearningInsight:
    """学习洞察数据结构"""
    insight_type: str
    title: str
    description: str
    priority: int  # 1-5, 5为最高优先级
    actionable: bool
    data: Dict[str, Any]


@dataclass
class MasteryAnalysis:
    """掌握度分析结果"""
    expression_id: int
    user_id: int
    mastery_level: MasteryLevel
    confidence_score: float  # 0-1
    learning_phase: LearningPhase
    time_to_mastery: Optional[int]  # 预计掌握时间（天）
    next_review_interval: int  # 下次复习间隔（天）
    difficulty_adjustment: float  # 难度调整系数


@dataclass
class ForgettingCurveData:
    """遗忘曲线数据"""
    expression_id: int
    user_id: int
    retention_rates: List[Tuple[int, float]]  # (天数, 保持率)
    forgetting_rate: float  # 遗忘速率
    half_life: float  # 半衰期（天）
    predicted_retention: Dict[int, float]  # 预测保持率


@dataclass
class LearningEfficiencyMetrics:
    """学习效率指标"""
    user_id: int
    overall_efficiency: float  # 总体效率 0-100
    time_efficiency: float  # 时间效率
    accuracy_efficiency: float  # 准确率效率
    retention_efficiency: float  # 记忆效率
    progress_velocity: float  # 进步速度
    optimal_session_duration: int  # 最佳学习时长（分钟）
    peak_performance_time: str  # 最佳学习时间段


class LearningAnalyticsService:
    """学习分析服务类"""
    
    def __init__(self):
        self.logger = logger
        
    def calculate_mastery_level(
        self, 
        user: User, 
        expression: IdiomaticExpression
    ) -> MasteryAnalysis:
        """
        计算表达掌握度
        
        基于以下因素计算掌握度：
        1. 正确率和一致性
        2. 响应时间趋势
        3. 遗忘曲线表现
        4. 学习历史长度
        5. 最近表现稳定性
        """
        try:
            progress = UserExpressionProgress.objects.filter(
                user=user, 
                expression=expression
            ).first()
            
            if not progress:
                return MasteryAnalysis(
                    expression_id=expression.id,
                    user_id=user.id,
                    mastery_level=MasteryLevel.UNKNOWN,
                    confidence_score=0.0,
                    learning_phase=LearningPhase.ACQUISITION,
                    time_to_mastery=None,
                    next_review_interval=1,
                    difficulty_adjustment=1.0
                )
            
            # 计算核心指标
            accuracy_score = self._calculate_accuracy_score(progress)
            consistency_score = self._calculate_consistency_score(progress)
            speed_score = self._calculate_speed_score(progress)
            retention_score = self._calculate_retention_score(progress)
            stability_score = self._calculate_stability_score(progress)
            
            # 综合评分
            weighted_score = (
                accuracy_score * 0.35 +      # 准确率权重最高
                consistency_score * 0.25 +   # 一致性
                retention_score * 0.20 +     # 记忆保持
                speed_score * 0.15 +         # 响应速度
                stability_score * 0.05       # 稳定性
            )
            
            # 确定掌握度等级
            mastery_level = self._determine_mastery_level(weighted_score)
            learning_phase = self._determine_learning_phase(progress, mastery_level)
            
            # 计算置信度
            confidence_score = self._calculate_confidence(progress, weighted_score)
            
            # 预测掌握时间
            time_to_mastery = self._predict_time_to_mastery(progress, mastery_level)
            
            # 计算下次复习间隔（SM-2算法优化）
            next_interval = self._calculate_next_review_interval(progress, mastery_level)
            
            # 难度调整
            difficulty_adjustment = self._calculate_difficulty_adjustment(
                progress, mastery_level
            )
            
            return MasteryAnalysis(
                expression_id=expression.id,
                user_id=user.id,
                mastery_level=mastery_level,
                confidence_score=confidence_score,
                learning_phase=learning_phase,
                time_to_mastery=time_to_mastery,
                next_review_interval=next_interval,
                difficulty_adjustment=difficulty_adjustment
            )
            
        except Exception as e:
            self.logger.error(f"计算掌握度失败: {e}")
            raise
    
    def analyze_forgetting_curve(
        self, 
        user: User, 
        expression: IdiomaticExpression,
        days_back: int = 30
    ) -> ForgettingCurveData:
        """
        分析遗忘曲线
        
        基于艾宾浩斯遗忘曲线理论，分析用户对特定表达的遗忘规律
        """
        try:
            progress = UserExpressionProgress.objects.filter(
                user=user, 
                expression=expression
            ).first()
            
            if not progress or not progress.learning_history:
                return ForgettingCurveData(
                    expression_id=expression.id,
                    user_id=user.id,
                    retention_rates=[],
                    forgetting_rate=0.0,
                    half_life=1.0,
                    predicted_retention={}
                )
            
            # 分析历史学习数据
            learning_history = progress.learning_history
            retention_data = self._extract_retention_data(learning_history, days_back)
            
            if len(retention_data) < 2:
                return ForgettingCurveData(
                    expression_id=expression.id,
                    user_id=user.id,
                    retention_rates=retention_data,
                    forgetting_rate=0.1,
                    half_life=7.0,
                    predicted_retention={}
                )
            
            # 拟合遗忘曲线 R(t) = e^(-t/τ)
            forgetting_rate, half_life = self._fit_forgetting_curve(retention_data)
            
            # 预测未来保持率
            predicted_retention = self._predict_retention_rates(
                forgetting_rate, days_ahead=30
            )
            
            return ForgettingCurveData(
                expression_id=expression.id,
                user_id=user.id,
                retention_rates=retention_data,
                forgetting_rate=forgetting_rate,
                half_life=half_life,
                predicted_retention=predicted_retention
            )
            
        except Exception as e:
            self.logger.error(f"分析遗忘曲线失败: {e}")
            raise
    
    def compute_learning_efficiency(
        self, 
        user: User,
        days_back: int = 30
    ) -> LearningEfficiencyMetrics:
        """
        计算学习效率指标
        
        综合分析用户的学习效率，包括：
        - 时间效率：单位时间内的学习成果
        - 准确率效率：正确率提升速度
        - 记忆效率：长期记忆保持能力
        - 进步速度：掌握新表达的速度
        """
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days_back)
            
            # 获取用户学习数据
            progress_queryset = UserExpressionProgress.objects.filter(
                user=user,
                updated_at__gte=start_date
            )
            
            if not progress_queryset.exists():
                return self._create_default_efficiency_metrics(user.id)
            
            # 计算各项效率指标
            time_efficiency = self._calculate_time_efficiency(progress_queryset)
            accuracy_efficiency = self._calculate_accuracy_efficiency(progress_queryset)
            retention_efficiency = self._calculate_retention_efficiency(progress_queryset)
            progress_velocity = self._calculate_progress_velocity(progress_queryset)
            
            # 计算总体效率
            overall_efficiency = (
                time_efficiency * 0.3 +
                accuracy_efficiency * 0.3 +
                retention_efficiency * 0.25 +
                progress_velocity * 0.15
            )
            
            # 分析最佳学习模式
            optimal_duration = self._analyze_optimal_session_duration(progress_queryset)
            peak_time = self._analyze_peak_performance_time(progress_queryset)
            
            return LearningEfficiencyMetrics(
                user_id=user.id,
                overall_efficiency=round(overall_efficiency, 2),
                time_efficiency=round(time_efficiency, 2),
                accuracy_efficiency=round(accuracy_efficiency, 2),
                retention_efficiency=round(retention_efficiency, 2),
                progress_velocity=round(progress_velocity, 2),
                optimal_session_duration=optimal_duration,
                peak_performance_time=peak_time
            )
            
        except Exception as e:
            self.logger.error(f"计算学习效率失败: {e}")
            raise
    
    def generate_learning_insights(
        self, 
        user: User,
        limit: int = 10
    ) -> List[LearningInsight]:
        """
        生成学习洞察
        
        基于用户学习数据，生成个性化的学习建议和洞察
        """
        try:
            insights = []
            
            # 获取用户最近学习数据
            recent_progress = UserExpressionProgress.objects.filter(
                user=user,
                updated_at__gte=timezone.now() - timedelta(days=30)
            ).select_related('expression')
            
            if not recent_progress.exists():
                return [LearningInsight(
                    insight_type="motivation",
                    title="开始你的学习之旅",
                    description="还没有学习记录，建议开始学习一些基础表达。",
                    priority=5,
                    actionable=True,
                    data={"action": "start_learning"}
                )]
            
            # 分析学习模式
            insights.extend(self._analyze_learning_patterns(recent_progress))
            
            # 分析困难表达
            insights.extend(self._analyze_difficult_expressions(recent_progress))
            
            # 分析学习时间分布
            insights.extend(self._analyze_time_distribution(recent_progress))
            
            # 分析进步趋势
            insights.extend(self._analyze_progress_trends(recent_progress))
            
            # 分析复习需求
            insights.extend(self._analyze_review_needs(user))
            
            # 按优先级排序并限制数量
            insights.sort(key=lambda x: x.priority, reverse=True)
            return insights[:limit]
            
        except Exception as e:
            self.logger.error(f"生成学习洞察失败: {e}")
            raise
    
    def optimize_review_schedule(
        self, 
        user: User,
        target_retention_rate: float = 0.85
    ) -> Dict[str, Any]:
        """
        优化复习计划
        
        基于SM-2算法和个人学习特征，优化复习时间安排
        """
        try:
            # 获取需要复习的表达
            expressions_to_review = self._get_expressions_for_review(user)
            
            optimized_schedule = []
            for expression_id, progress in expressions_to_review.items():
                mastery = self.calculate_mastery_level(user, progress.expression)
                forgetting_curve = self.analyze_forgetting_curve(
                    user, progress.expression
                )
                
                # 计算最优复习时间
                optimal_interval = self._calculate_optimal_review_interval(
                    mastery, forgetting_curve, target_retention_rate
                )
                
                next_review = timezone.now() + timedelta(days=optimal_interval)
                
                optimized_schedule.append({
                    'expression_id': expression_id,
                    'expression_text': progress.expression.expression,
                    'current_mastery': mastery.mastery_level.name,
                    'next_review_date': next_review,
                    'interval_days': optimal_interval,
                    'priority': self._calculate_review_priority(mastery, forgetting_curve)
                })
            
            # 按优先级排序
            optimized_schedule.sort(key=lambda x: x['priority'], reverse=True)
            
            return {
                'total_expressions': len(optimized_schedule),
                'schedule': optimized_schedule,
                'target_retention_rate': target_retention_rate,
                'generated_at': timezone.now()
            }
            
        except Exception as e:
            self.logger.error(f"优化复习计划失败: {e}")
            raise
    
    # ==================== 私有辅助方法 ====================
    
    def _calculate_accuracy_score(self, progress: UserExpressionProgress) -> float:
        """计算准确率得分"""
        if progress.total_attempts == 0:
            return 0.0
        
        accuracy = progress.correct_count / progress.total_attempts
        
        # 考虑连续正确次数的加成
        consistency_bonus = min(progress.consecutive_correct / 10, 0.2)
        
        return min(accuracy + consistency_bonus, 1.0) * 100
    
    def _calculate_consistency_score(self, progress: UserExpressionProgress) -> float:
        """计算一致性得分"""
        if not progress.learning_history:
            return 0.0
        
        # 分析最近10次学习的一致性
        recent_results = []
        for session in progress.learning_history.get('sessions', [])[-10:]:
            if 'correct' in session:
                recent_results.append(session['correct'])
        
        if len(recent_results) < 3:
            return 50.0
        
        # 计算标准差（一致性越高，标准差越小）
        mean_accuracy = sum(recent_results) / len(recent_results)
        variance = sum((x - mean_accuracy) ** 2 for x in recent_results) / len(recent_results)
        std_dev = math.sqrt(variance)
        
        # 转换为0-100分数（标准差越小，分数越高）
        consistency_score = max(0, 100 - std_dev * 100)
        return consistency_score
    
    def _calculate_speed_score(self, progress: UserExpressionProgress) -> float:
        """计算响应速度得分"""
        if progress.average_response_time <= 0:
            return 50.0
        
        # 基于平均响应时间计算分数
        # 假设理想响应时间为2秒，最长接受时间为10秒
        ideal_time = 2.0
        max_time = 10.0
        
        response_time = float(progress.average_response_time)
        
        if response_time <= ideal_time:
            return 100.0
        elif response_time >= max_time:
            return 0.0
        else:
            # 线性递减
            return 100 * (max_time - response_time) / (max_time - ideal_time)
    
    def _calculate_retention_score(self, progress: UserExpressionProgress) -> float:
        """计算记忆保持得分"""
        return float(progress.retention_rate)
    
    def _calculate_stability_score(self, progress: UserExpressionProgress) -> float:
        """计算稳定性得分"""
        if not progress.learning_history:
            return 0.0
        
        sessions = progress.learning_history.get('sessions', [])
        if len(sessions) < 5:
            return 50.0
        
        # 分析最近的学习表现稳定性
        recent_sessions = sessions[-10:]
        correct_rates = []
        
        for session in recent_sessions:
            if 'total' in session and session['total'] > 0:
                rate = session.get('correct', 0) / session['total']
                correct_rates.append(rate)
        
        if len(correct_rates) < 3:
            return 50.0
        
        # 计算趋势稳定性
        trend_stability = 100 - abs(correct_rates[-1] - correct_rates[0]) * 100
        return max(0, min(100, trend_stability))
    
    def _determine_mastery_level(self, weighted_score: float) -> MasteryLevel:
        """根据综合得分确定掌握度等级"""
        if weighted_score >= 90:
            return MasteryLevel.EXPERT
        elif weighted_score >= 75:
            return MasteryLevel.ADVANCED
        elif weighted_score >= 60:
            return MasteryLevel.INTERMEDIATE
        elif weighted_score >= 40:
            return MasteryLevel.BASIC
        elif weighted_score >= 20:
            return MasteryLevel.BEGINNER
        else:
            return MasteryLevel.UNKNOWN
    
    def _determine_learning_phase(
        self, 
        progress: UserExpressionProgress, 
        mastery_level: MasteryLevel
    ) -> LearningPhase:
        """确定学习阶段"""
        if mastery_level == MasteryLevel.EXPERT:
            return LearningPhase.MASTERY
        elif mastery_level in [MasteryLevel.ADVANCED, MasteryLevel.INTERMEDIATE]:
            return LearningPhase.RETENTION
        elif mastery_level == MasteryLevel.BASIC:
            return LearningPhase.CONSOLIDATION
        else:
            return LearningPhase.ACQUISITION
    
    def _calculate_confidence(
        self, 
        progress: UserExpressionProgress, 
        weighted_score: float
    ) -> float:
        """计算置信度"""
        # 基础置信度基于样本数量
        sample_confidence = min(progress.total_attempts / 20, 1.0)
        
        # 基于分数的置信度
        score_confidence = weighted_score / 100
        
        # 基于时间跨度的置信度
        if progress.learning_history:
            sessions = progress.learning_history.get('sessions', [])
            if sessions:
                time_span = len(sessions)
                time_confidence = min(time_span / 10, 1.0)
            else:
                time_confidence = 0.1
        else:
            time_confidence = 0.1
        
        # 综合置信度
        overall_confidence = (
            sample_confidence * 0.4 +
            score_confidence * 0.4 +
            time_confidence * 0.2
        )
        
        return min(overall_confidence, 1.0)
    
    def _predict_time_to_mastery(
        self, 
        progress: UserExpressionProgress, 
        mastery_level: MasteryLevel
    ) -> Optional[int]:
        """预测达到精通所需时间"""
        if mastery_level == MasteryLevel.EXPERT:
            return 0
        
        # 基于当前进度和历史学习速度预测
        if not progress.learning_history:
            return None
        
        sessions = progress.learning_history.get('sessions', [])
        if len(sessions) < 3:
            return None
        
        # 计算学习速度（每天的进步率）
        total_days = (timezone.now() - progress.created_at).days
        if total_days == 0:
            return None
        
        current_score = (progress.correct_count / max(progress.total_attempts, 1)) * 100
        daily_progress = current_score / max(total_days, 1)
        
        if daily_progress <= 0:
            return None
        
        # 预测达到90分（专家级）所需天数
        target_score = 90
        days_needed = max(0, (target_score - current_score) / daily_progress)
        
        return int(days_needed)
    
    def _calculate_next_review_interval(
        self, 
        progress: UserExpressionProgress, 
        mastery_level: MasteryLevel
    ) -> int:
        """计算下次复习间隔（SM-2算法优化版）"""
        # 基础间隔根据掌握度确定
        base_intervals = {
            MasteryLevel.UNKNOWN: 1,
            MasteryLevel.BEGINNER: 1,
            MasteryLevel.BASIC: 3,
            MasteryLevel.INTERMEDIATE: 7,
            MasteryLevel.ADVANCED: 14,
            MasteryLevel.EXPERT: 30
        }
        
        base_interval = base_intervals.get(mastery_level, 1)
        
        # 根据最近表现调整
        if progress.consecutive_correct >= 5:
            multiplier = 1.5
        elif progress.consecutive_correct >= 3:
            multiplier = 1.2
        elif progress.consecutive_correct >= 1:
            multiplier = 1.0
        else:
            multiplier = 0.6
        
        # 根据难度评级调整
        difficulty_factor = progress.difficulty_rating / 3.0  # 标准化到1.0
        final_interval = int(base_interval * multiplier / difficulty_factor)
        
        return max(1, min(final_interval, 90))  # 限制在1-90天之间
    
    def _calculate_difficulty_adjustment(
        self, 
        progress: UserExpressionProgress, 
        mastery_level: MasteryLevel
    ) -> float:
        """计算难度调整系数"""
        base_difficulty = 1.0
        
        # 根据错误率调整
        error_rate = progress.error_rate / 100
        if error_rate > 0.5:
            difficulty_adjustment = 0.8  # 降低难度
        elif error_rate < 0.2:
            difficulty_adjustment = 1.2  # 增加难度
        else:
            difficulty_adjustment = 1.0
        
        # 根据掌握度调整
        mastery_adjustment = {
            MasteryLevel.UNKNOWN: 0.7,
            MasteryLevel.BEGINNER: 0.8,
            MasteryLevel.BASIC: 0.9,
            MasteryLevel.INTERMEDIATE: 1.0,
            MasteryLevel.ADVANCED: 1.1,
            MasteryLevel.EXPERT: 1.2
        }.get(mastery_level, 1.0)
        
        return base_difficulty * difficulty_adjustment * mastery_adjustment
    
    def _extract_retention_data(
        self, 
        learning_history: Dict[str, Any], 
        days_back: int
    ) -> List[Tuple[int, float]]:
        """从学习历史中提取保持率数据"""
        sessions = learning_history.get('sessions', [])
        if not sessions:
            return []
        
        retention_data = []
        current_date = timezone.now()
        
        # 按时间分组计算保持率
        for i, session in enumerate(sessions[-days_back:]):
            if 'date' in session and 'correct' in session and 'total' in session:
                try:
                    session_date = datetime.fromisoformat(session['date'].replace('Z', '+00:00'))
                    days_ago = (current_date - session_date).days
                    
                    if session['total'] > 0:
                        retention_rate = session['correct'] / session['total']
                        retention_data.append((days_ago, retention_rate))
                except (ValueError, TypeError):
                    continue
        
        return sorted(retention_data, key=lambda x: x[0])
    
    def _fit_forgetting_curve(
        self, 
        retention_data: List[Tuple[int, float]]
    ) -> Tuple[float, float]:
        """拟合遗忘曲线参数"""
        if len(retention_data) < 2:
            return 0.1, 7.0
        
        # 简化的指数拟合
        # R(t) = R0 * e^(-t/τ)
        # ln(R(t)) = ln(R0) - t/τ
        
        try:
            x_values = [point[0] for point in retention_data]  # 天数
            y_values = [max(point[1], 0.01) for point in retention_data]  # 保持率（避免log(0)）
            
            # 线性回归拟合 ln(y) = a + b*x
            n = len(retention_data)
            sum_x = sum(x_values)
            sum_y = sum(math.log(y) for y in y_values)
            sum_xy = sum(x * math.log(y) for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)
            
            # 计算斜率和截距
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # 提取参数
            tau = -1 / slope if slope < 0 else 7.0  # 时间常数
            forgetting_rate = 1 / tau
            half_life = tau * math.log(2)
            
            return max(forgetting_rate, 0.01), max(half_life, 1.0)
            
        except (ZeroDivisionError, ValueError):
            return 0.1, 7.0
    
    def _predict_retention_rates(
        self, 
        forgetting_rate: float, 
        days_ahead: int
    ) -> Dict[int, float]:
        """预测未来保持率"""
        predictions = {}
        for day in range(1, days_ahead + 1):
            retention = math.exp(-day * forgetting_rate)
            predictions[day] = max(0.0, min(1.0, retention))
        
        return predictions
    
    def _calculate_time_efficiency(self, progress_queryset) -> float:
        """计算时间效率"""
        total_time = progress_queryset.aggregate(
            total=Sum('study_duration')
        )['total'] or 0
        
        if total_time == 0:
            return 50.0
        
        total_correct = progress_queryset.aggregate(
            correct=Sum('correct_count')
        )['correct'] or 0
        
        # 每小时正确答题数
        efficiency = (total_correct * 3600) / max(total_time, 1)
        
        # 标准化到0-100分
        return min(efficiency * 10, 100)
    
    def _calculate_accuracy_efficiency(self, progress_queryset) -> float:
        """计算准确率效率"""
        avg_accuracy = 0
        count = 0
        
        for progress in progress_queryset:
            if progress.total_attempts > 0:
                accuracy = progress.correct_count / progress.total_attempts
                avg_accuracy += accuracy
                count += 1
        
        if count == 0:
            return 50.0
        
        return (avg_accuracy / count) * 100
    
    def _calculate_retention_efficiency(self, progress_queryset) -> float:
        """计算记忆效率"""
        avg_retention = progress_queryset.aggregate(
            avg=Avg('retention_rate')
        )['avg'] or 50.0
        
        return float(avg_retention)
    
    def _calculate_progress_velocity(self, progress_queryset) -> float:
        """计算进步速度"""
        # 计算掌握度提升速度
        mastery_improvements = 0
        total_expressions = progress_queryset.count()
        
        for progress in progress_queryset:
            if progress.learning_efficiency > 50:  # 假设50为基准线
                mastery_improvements += 1
        
        if total_expressions == 0:
            return 50.0
        
        velocity = (mastery_improvements / total_expressions) * 100
        return velocity
    
    def _analyze_optimal_session_duration(self, progress_queryset) -> int:
        """分析最佳学习时长"""
        # 基于学习效率分析最佳时长
        duration_efficiency = {}
        
        for progress in progress_queryset:
            duration = progress.study_duration
            efficiency = progress.learning_efficiency
            
            # 按时长分组（10分钟间隔）
            duration_group = (duration // 600) * 10  # 转换为分钟并分组
            
            if duration_group not in duration_efficiency:
                duration_efficiency[duration_group] = []
            duration_efficiency[duration_group].append(efficiency)
        
        # 找到效率最高的时长组
        best_duration = 30  # 默认30分钟
        best_efficiency = 0
        
        for duration, efficiencies in duration_efficiency.items():
            avg_efficiency = sum(efficiencies) / len(efficiencies)
            if avg_efficiency > best_efficiency:
                best_efficiency = avg_efficiency
                best_duration = duration
        
        return max(10, min(best_duration, 120))  # 限制在10-120分钟
    
    def _analyze_peak_performance_time(self, progress_queryset) -> str:
        """分析最佳学习时间段"""
        time_performance = {}
        
        for progress in progress_queryset:
            best_time = progress.best_learning_time
            if best_time:
                if best_time not in time_performance:
                    time_performance[best_time] = []
                time_performance[best_time].append(progress.learning_efficiency)
        
        if not time_performance:
            return "morning"  # 默认上午
        
        # 找到效率最高的时间段
        best_time = "morning"
        best_efficiency = 0
        
        for time_period, efficiencies in time_performance.items():
            avg_efficiency = sum(efficiencies) / len(efficiencies)
            if avg_efficiency > best_efficiency:
                best_efficiency = avg_efficiency
                best_time = time_period
        
        return best_time
    
    def _create_default_efficiency_metrics(self, user_id: int) -> LearningEfficiencyMetrics:
        """创建默认效率指标"""
        return LearningEfficiencyMetrics(
            user_id=user_id,
            overall_efficiency=50.0,
            time_efficiency=50.0,
            accuracy_efficiency=50.0,
            retention_efficiency=50.0,
            progress_velocity=50.0,
            optimal_session_duration=30,
            peak_performance_time="morning"
        )
    
    def _analyze_learning_patterns(self, progress_queryset) -> List[LearningInsight]:
        """分析学习模式"""
        insights = []
        
        # 分析学习频率
        total_expressions = progress_queryset.count()
        active_expressions = progress_queryset.filter(
            updated_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        if active_expressions < total_expressions * 0.3:
            insights.append(LearningInsight(
                insight_type="frequency",
                title="学习频率偏低",
                description=f"最近一周只学习了{active_expressions}个表达，建议增加学习频率。",
                priority=4,
                actionable=True,
                data={
                    "current_frequency": active_expressions,
                    "total_expressions": total_expressions,
                    "suggestion": "increase_frequency"
                }
            ))
        
        return insights
    
    def _analyze_difficult_expressions(self, progress_queryset) -> List[LearningInsight]:
        """分析困难表达"""
        insights = []
        
        # 找出错误率高的表达
        difficult_expressions = []
        for progress in progress_queryset:
            if progress.total_attempts >= 5 and progress.error_rate > 50:
                difficult_expressions.append({
                    'expression': progress.expression.expression,
                    'error_rate': progress.error_rate,
                    'attempts': progress.total_attempts
                })
        
        if difficult_expressions:
            insights.append(LearningInsight(
                insight_type="difficulty",
                title="发现困难表达",
                description=f"有{len(difficult_expressions)}个表达错误率较高，建议重点复习。",
                priority=5,
                actionable=True,
                data={
                    "difficult_expressions": difficult_expressions[:5],
                    "total_count": len(difficult_expressions)
                }
            ))
        
        return insights
    
    def _analyze_time_distribution(self, progress_queryset) -> List[LearningInsight]:
        """分析时间分布"""
        insights = []
        
        # 分析学习时间分布
        total_time = sum(p.study_duration for p in progress_queryset)
        if total_time > 0:
            avg_time_per_expression = total_time / progress_queryset.count()
            
            if avg_time_per_expression < 300:  # 少于5分钟
                insights.append(LearningInsight(
                    insight_type="time_allocation",
                    title="学习时间偏短",
                    description="平均每个表达的学习时间较短，建议延长学习时间以提高效果。",
                    priority=3,
                    actionable=True,
                    data={
                        "avg_time": avg_time_per_expression,
                        "suggestion": "increase_study_time"
                    }
                ))
        
        return insights
    
    def _analyze_progress_trends(self, progress_queryset) -> List[LearningInsight]:
        """分析进步趋势"""
        insights = []
        
        # 分析整体进步趋势
        improving_count = progress_queryset.filter(
            learning_efficiency__gte=70
        ).count()
        
        total_count = progress_queryset.count()
        improvement_rate = improving_count / total_count if total_count > 0 else 0
        
        if improvement_rate > 0.7:
            insights.append(LearningInsight(
                insight_type="progress",
                title="学习进展良好",
                description=f"有{improving_count}个表达学习效果良好，继续保持！",
                priority=2,
                actionable=False,
                data={
                    "improvement_rate": improvement_rate,
                    "improving_count": improving_count
                }
            ))
        elif improvement_rate < 0.3:
            insights.append(LearningInsight(
                insight_type="progress",
                title="学习进展缓慢",
                description="学习进展较慢，建议调整学习方法或寻求帮助。",
                priority=5,
                actionable=True,
                data={
                    "improvement_rate": improvement_rate,
                    "suggestion": "adjust_method"
                }
            ))
        
        return insights
    
    def _analyze_review_needs(self, user: User) -> List[LearningInsight]:
        """分析复习需求"""
        insights = []
        
        # 找出需要复习的表达
        expressions_needing_review = UserExpressionProgress.objects.filter(
            user=user,
            last_reviewed__lt=timezone.now() - timedelta(days=7),
            mastery_level__lt=4  # 未达到高级水平
        ).count()
        
        if expressions_needing_review > 5:
            insights.append(LearningInsight(
                insight_type="review",
                title="需要复习",
                description=f"有{expressions_needing_review}个表达需要复习，建议安排复习时间。",
                priority=4,
                actionable=True,
                data={
                    "review_count": expressions_needing_review,
                    "action": "schedule_review"
                }
            ))
        
        return insights
    
    def _get_expressions_for_review(self, user: User) -> Dict[int, UserExpressionProgress]:
        """获取需要复习的表达"""
        return {
            progress.expression.id: progress
            for progress in UserExpressionProgress.objects.filter(
                user=user,
                last_reviewed__lt=timezone.now() - timedelta(days=3)
            ).select_related('expression')
        }
    
    def _calculate_optimal_review_interval(
        self, 
        mastery: MasteryAnalysis,
        forgetting_curve: ForgettingCurveData,
        target_retention: float
    ) -> int:
        """计算最优复习间隔"""
        # 基于遗忘曲线和目标保持率计算
        if forgetting_curve.forgetting_rate <= 0:
            return mastery.next_review_interval
        
        # 计算达到目标保持率的时间
        target_days = -math.log(target_retention) / forgetting_curve.forgetting_rate
        
        # 结合掌握度调整
        mastery_factor = {
            MasteryLevel.UNKNOWN: 0.5,
            MasteryLevel.BEGINNER: 0.6,
            MasteryLevel.BASIC: 0.8,
            MasteryLevel.INTERMEDIATE: 1.0,
            MasteryLevel.ADVANCED: 1.3,
            MasteryLevel.EXPERT: 1.8
        }.get(mastery.mastery_level, 1.0)
        
        optimal_interval = int(target_days * mastery_factor)
        return max(1, min(optimal_interval, 60))
    
    def _calculate_review_priority(
        self, 
        mastery: MasteryAnalysis,
        forgetting_curve: ForgettingCurveData
    ) -> float:
        """计算复习优先级"""
        # 基础优先级（掌握度越低，优先级越高）
        base_priority = 6 - mastery.mastery_level.value
        
        # 遗忘风险调整
        forgetting_risk = forgetting_curve.forgetting_rate * 10
        
        # 置信度调整
        confidence_adjustment = 1 - mastery.confidence_score
        
        priority = base_priority + forgetting_risk + confidence_adjustment
        return max(0, min(10, priority))
