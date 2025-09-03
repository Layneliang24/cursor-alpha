"""
数据分析服务
处理用户英语学习数据的统计、分析和可视化
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from django.db import models
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings

# 配置日志
logger = logging.getLogger(__name__)


class DataAnalysisService:
    """
    数据分析服务类
    提供英语学习数据的统计、分析和报告功能
    """
    
    def __init__(self):
        """初始化数据分析服务"""
        self.logger = logger
        self.logger.info("DataAnalysisService initialized")
    
    def get_user_learning_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        获取用户学习数据摘要
        
        Args:
            user_id (int): 用户ID
            days (int): 统计天数，默认30天
            
        Returns:
            Dict[str, Any]: 学习数据摘要
        """
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # 获取用户学习会话数据
            sessions = self._get_user_sessions(user_id, start_date, end_date)
            
            # 计算统计数据
            summary = {
                'user_id': user_id,
                'period_days': days,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_sessions': len(sessions),
                'total_words_typed': sum(session.get('words_typed', 0) for session in sessions),
                'total_time_spent': sum(session.get('duration_minutes', 0) for session in sessions),
                'average_accuracy': self._calculate_average_accuracy(sessions),
                'average_speed': self._calculate_average_speed(sessions),
                'learning_streak': self._calculate_learning_streak(user_id, days),
                'improvement_rate': self._calculate_improvement_rate(user_id, days),
                'top_chapters': self._get_top_chapters(user_id, days),
                'weak_areas': self._identify_weak_areas(user_id, days)
            }
            
            self.logger.info(f"Generated learning summary for user {user_id}")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating learning summary for user {user_id}: {e}")
            return {
                'error': str(e),
                'user_id': user_id,
                'period_days': days
            }
    
    def get_learning_progress(self, user_id: int, chapter_id: Optional[int] = None) -> Dict[str, Any]:
        """
        获取学习进度数据
        
        Args:
            user_id (int): 用户ID
            chapter_id (int, optional): 章节ID，如果为None则返回所有章节
            
        Returns:
            Dict[str, Any]: 学习进度数据
        """
        try:
            if chapter_id:
                progress = self._get_chapter_progress(user_id, chapter_id)
            else:
                progress = self._get_all_chapters_progress(user_id)
            
            self.logger.info(f"Retrieved learning progress for user {user_id}")
            return progress
            
        except Exception as e:
            self.logger.error(f"Error retrieving learning progress for user {user_id}: {e}")
            return {'error': str(e)}
    
    def generate_learning_report(self, user_id: int, report_type: str = 'comprehensive') -> Dict[str, Any]:
        """
        生成学习报告
        
        Args:
            user_id (int): 用户ID
            report_type (str): 报告类型 ('comprehensive', 'performance', 'progress')
            
        Returns:
            Dict[str, Any]: 学习报告
        """
        try:
            if report_type == 'comprehensive':
                report = self._generate_comprehensive_report(user_id)
            elif report_type == 'performance':
                report = self._generate_performance_report(user_id)
            elif report_type == 'progress':
                report = self._generate_progress_report(user_id)
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            self.logger.info(f"Generated {report_type} report for user {user_id}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating {report_type} report for user {user_id}: {e}")
            return {'error': str(e)}
    
    def analyze_learning_patterns(self, user_id: int) -> Dict[str, Any]:
        """
        分析学习模式
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            Dict[str, Any]: 学习模式分析结果
        """
        try:
            patterns = {
                'user_id': user_id,
                'preferred_learning_times': self._analyze_learning_times(user_id),
                'session_duration_patterns': self._analyze_session_durations(user_id),
                'accuracy_trends': self._analyze_accuracy_trends(user_id),
                'speed_trends': self._analyze_speed_trends(user_id),
                'chapter_preferences': self._analyze_chapter_preferences(user_id),
                'learning_consistency': self._analyze_learning_consistency(user_id)
            }
            
            self.logger.info(f"Analyzed learning patterns for user {user_id}")
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing learning patterns for user {user_id}: {e}")
            return {'error': str(e)}
    
    def get_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取个性化学习建议
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            List[Dict[str, Any]]: 学习建议列表
        """
        try:
            recommendations = []
            
            # 基于弱项的建议
            weak_areas = self._identify_weak_areas(user_id, 30)
            for area in weak_areas:
                recommendations.append({
                    'type': 'weak_area_focus',
                    'priority': 'high',
                    'title': f"加强{area['name']}练习",
                    'description': f"您在{area['name']}方面的准确率较低，建议增加练习时间",
                    'action': f"完成{area['name']}相关练习",
                    'estimated_effort': '15-20分钟'
                })
            
            # 基于学习习惯的建议
            consistency = self._analyze_learning_consistency(user_id)
            if consistency['days_without_practice'] > 3:
                recommendations.append({
                    'type': 'consistency_improvement',
                    'priority': 'medium',
                    'title': "保持学习连续性",
                    'description': "连续学习有助于巩固记忆，建议每天保持练习",
                    'action': "制定每日学习计划",
                    'estimated_effort': '10-15分钟'
                })
            
            # 基于进度的建议
            progress = self._get_all_chapters_progress(user_id)
            if progress['completed_chapters'] < progress['total_chapters'] * 0.5:
                recommendations.append({
                    'type': 'progress_encouragement',
                    'priority': 'low',
                    'title': "继续推进学习进度",
                    'description': "您已完成部分章节，继续学习新内容有助于扩展词汇量",
                    'action': "尝试新的章节内容",
                    'estimated_effort': '20-30分钟'
                })
            
            self.logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations for user {user_id}: {e}")
            return [{'error': str(e)}]
    
    # 私有方法 - 数据获取和分析
    
    def _get_user_sessions(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """获取用户学习会话数据"""
        try:
            # 这里应该从实际的数据库模型获取数据
            # 由于模型可能不存在，返回模拟数据
            return [
                {
                    'id': 1,
                    'words_typed': 150,
                    'duration_minutes': 25,
                    'accuracy': 0.85,
                    'speed_wpm': 60,
                    'chapter_id': 1,
                    'created_at': start_date + timedelta(hours=1)
                },
                {
                    'id': 2,
                    'words_typed': 200,
                    'duration_minutes': 30,
                    'accuracy': 0.90,
                    'speed_wpm': 65,
                    'chapter_id': 2,
                    'created_at': start_date + timedelta(hours=3)
                }
            ]
        except Exception as e:
            self.logger.error(f"Error getting user sessions: {e}")
            return []
    
    def _calculate_average_accuracy(self, sessions: List[Dict[str, Any]]) -> float:
        """计算平均准确率"""
        if not sessions:
            return 0.0
        
        total_accuracy = sum(session.get('accuracy', 0) for session in sessions)
        return round(total_accuracy / len(sessions), 3)
    
    def _calculate_average_speed(self, sessions: List[Dict[str, Any]]) -> float:
        """计算平均速度（每分钟单词数）"""
        if not sessions:
            return 0.0
        
        total_speed = sum(session.get('speed_wpm', 0) for session in sessions)
        return round(total_speed / len(sessions), 1)
    
    def _calculate_learning_streak(self, user_id: int, days: int) -> int:
        """计算学习连续天数"""
        try:
            # 模拟计算连续天数
            return 5  # 示例值
        except Exception as e:
            self.logger.error(f"Error calculating learning streak: {e}")
            return 0
    
    def _calculate_improvement_rate(self, user_id: int, days: int) -> float:
        """计算改进率"""
        try:
            # 模拟计算改进率
            return 0.15  # 15%的改进率
        except Exception as e:
            self.logger.error(f"Error calculating improvement rate: {e}")
            return 0.0
    
    def _get_top_chapters(self, user_id: int, days: int) -> List[Dict[str, Any]]:
        """获取表现最好的章节"""
        try:
            return [
                {'chapter_id': 1, 'name': '基础词汇', 'accuracy': 0.92, 'speed': 70},
                {'chapter_id': 2, 'name': '日常对话', 'accuracy': 0.88, 'speed': 65}
            ]
        except Exception as e:
            self.logger.error(f"Error getting top chapters: {e}")
            return []
    
    def _identify_weak_areas(self, user_id: int, days: int) -> List[Dict[str, Any]]:
        """识别薄弱环节"""
        try:
            return [
                {'chapter_id': 3, 'name': '商务英语', 'accuracy': 0.75, 'speed': 55},
                {'chapter_id': 4, 'name': '学术写作', 'accuracy': 0.70, 'speed': 50}
            ]
        except Exception as e:
            self.logger.error(f"Error identifying weak areas: {e}")
            return []
    
    def _get_chapter_progress(self, user_id: int, chapter_id: int) -> Dict[str, Any]:
        """获取特定章节的进度"""
        try:
            return {
                'chapter_id': chapter_id,
                'user_id': user_id,
                'completed_lessons': 8,
                'total_lessons': 12,
                'completion_rate': 0.67,
                'average_accuracy': 0.85,
                'average_speed': 65,
                'last_practice_date': timezone.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting chapter progress: {e}")
            return {'error': str(e)}
    
    def _get_all_chapters_progress(self, user_id: int) -> Dict[str, Any]:
        """获取所有章节的进度"""
        try:
            return {
                'user_id': user_id,
                'total_chapters': 10,
                'completed_chapters': 6,
                'in_progress_chapters': 2,
                'not_started_chapters': 2,
                'overall_completion_rate': 0.60,
                'chapters': [
                    {'id': 1, 'name': '基础词汇', 'status': 'completed', 'progress': 1.0},
                    {'id': 2, 'name': '日常对话', 'status': 'completed', 'progress': 1.0},
                    {'id': 3, 'name': '商务英语', 'status': 'in_progress', 'progress': 0.67},
                    {'id': 4, 'name': '学术写作', 'status': 'not_started', 'progress': 0.0}
                ]
            }
        except Exception as e:
            self.logger.error(f"Error getting all chapters progress: {e}")
            return {'error': str(e)}
    
    def _analyze_learning_times(self, user_id: int) -> Dict[str, Any]:
        """分析学习时间偏好"""
        try:
            return {
                'preferred_hours': [9, 10, 14, 15, 20, 21],
                'peak_hours': [10, 20],
                'average_session_start_time': '14:30',
                'weekend_activity': True,
                'weekday_activity': True
            }
        except Exception as e:
            self.logger.error(f"Error analyzing learning times: {e}")
            return {}
    
    def _analyze_session_durations(self, user_id: int) -> Dict[str, Any]:
        """分析学习会话时长模式"""
        try:
            return {
                'average_duration': 25,
                'most_common_duration': 30,
                'duration_distribution': {
                    'short': 0.2,    # < 15分钟
                    'medium': 0.6,   # 15-30分钟
                    'long': 0.2      # > 30分钟
                }
            }
        except Exception as e:
            self.logger.error(f"Error analyzing session durations: {e}")
            return {}
    
    def _analyze_accuracy_trends(self, user_id: int) -> Dict[str, Any]:
        """分析准确率趋势"""
        try:
            return {
                'trend': 'improving',
                'weekly_averages': [0.75, 0.78, 0.82, 0.85, 0.88],
                'improvement_rate': 0.15,
                'consistency_score': 0.8
            }
        except Exception as e:
            self.logger.error(f"Error analyzing accuracy trends: {e}")
            return {}
    
    def _analyze_speed_trends(self, user_id: int) -> Dict[str, Any]:
        """分析速度趋势"""
        try:
            return {
                'trend': 'improving',
                'weekly_averages': [45, 48, 52, 55, 58],
                'improvement_rate': 0.12,
                'consistency_score': 0.75
            }
        except Exception as e:
            self.logger.error(f"Error analyzing speed trends: {e}")
            return {}
    
    def _analyze_chapter_preferences(self, user_id: int) -> Dict[str, Any]:
        """分析章节偏好"""
        try:
            return {
                'favorite_chapters': [1, 2, 5],
                'least_favorite_chapters': [4, 7],
                'preference_pattern': 'vocabulary_focused',
                'difficulty_preference': 'medium'
            }
        except Exception as e:
            self.logger.error(f"Error analyzing chapter preferences: {e}")
            return {}
    
    def _analyze_learning_consistency(self, user_id: int) -> Dict[str, Any]:
        """分析学习一致性"""
        try:
            return {
                'days_without_practice': 2,
                'weekly_consistency': 0.85,
                'monthly_consistency': 0.78,
                'best_streak': 12,
                'current_streak': 5
            }
        except Exception as e:
            self.logger.error(f"Error analyzing learning consistency: {e}")
            return {}
    
    def _generate_comprehensive_report(self, user_id: int) -> Dict[str, Any]:
        """生成综合报告"""
        try:
            summary = self.get_user_learning_summary(user_id, 30)
            patterns = self.analyze_learning_patterns(user_id)
            recommendations = self.get_recommendations(user_id)
            
            return {
                'report_type': 'comprehensive',
                'user_id': user_id,
                'generated_at': timezone.now().isoformat(),
                'summary': summary,
                'patterns': patterns,
                'recommendations': recommendations,
                'insights': self._generate_insights(summary, patterns)
            }
        except Exception as e:
            self.logger.error(f"Error generating comprehensive report: {e}")
            return {'error': str(e)}
    
    def _generate_performance_report(self, user_id: int) -> Dict[str, Any]:
        """生成性能报告"""
        try:
            summary = self.get_user_learning_summary(user_id, 30)
            patterns = self.analyze_learning_patterns(user_id)
            
            return {
                'report_type': 'performance',
                'user_id': user_id,
                'generated_at': timezone.now().isoformat(),
                'performance_metrics': {
                    'accuracy': summary.get('average_accuracy', 0),
                    'speed': summary.get('average_speed', 0),
                    'consistency': patterns.get('learning_consistency', {}).get('weekly_consistency', 0),
                    'improvement': summary.get('improvement_rate', 0)
                },
                'trends': {
                    'accuracy_trend': patterns.get('accuracy_trends', {}),
                    'speed_trend': patterns.get('speed_trends', {})
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {'error': str(e)}
    
    def _generate_progress_report(self, user_id: int) -> Dict[str, Any]:
        """生成进度报告"""
        try:
            progress = self._get_all_chapters_progress(user_id)
            
            return {
                'report_type': 'progress',
                'user_id': user_id,
                'generated_at': timezone.now().isoformat(),
                'progress_overview': progress,
                'completion_forecast': self._estimate_completion_forecast(user_id),
                'next_milestones': self._identify_next_milestones(user_id)
            }
        except Exception as e:
            self.logger.error(f"Error generating progress report: {e}")
            return {'error': str(e)}
    
    def _generate_insights(self, summary: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """生成洞察信息"""
        insights = []
        
        # 基于准确率的洞察
        if summary.get('average_accuracy', 0) > 0.9:
            insights.append("您的准确率表现优秀，继续保持！")
        elif summary.get('average_accuracy', 0) < 0.8:
            insights.append("建议增加练习时间以提高准确率")
        
        # 基于学习一致性的洞察
        consistency = patterns.get('learning_consistency', {})
        if consistency.get('weekly_consistency', 0) > 0.8:
            insights.append("您的学习习惯非常规律，这是成功的关键")
        elif consistency.get('days_without_practice', 0) > 5:
            insights.append("连续多天未练习，建议重新建立学习习惯")
        
        # 基于改进率的洞察
        if summary.get('improvement_rate', 0) > 0.1:
            insights.append("您的学习进步明显，继续保持当前的学习方法")
        
        return insights
    
    def _estimate_completion_forecast(self, user_id: int) -> Dict[str, Any]:
        """估算完成时间预测"""
        try:
            return {
                'estimated_completion_days': 45,
                'estimated_completion_date': (timezone.now() + timedelta(days=45)).isoformat(),
                'confidence_level': 'medium',
                'assumptions': [
                    '保持当前学习频率',
                    '平均每天练习20分钟',
                    '准确率稳定在85%以上'
                ]
            }
        except Exception as e:
            self.logger.error(f"Error estimating completion forecast: {e}")
            return {}
    
    def _identify_next_milestones(self, user_id: int) -> List[Dict[str, Any]]:
        """识别下一个里程碑"""
        try:
            return [
                {
                    'milestone': '完成第5章',
                    'description': '掌握商务英语基础词汇',
                    'estimated_effort': '2-3小时',
                    'prerequisites': ['完成第4章', '准确率达到80%']
                },
                {
                    'milestone': '达到100 WPM',
                    'description': '提升打字速度到每分钟100个单词',
                    'estimated_effort': '1-2周',
                    'prerequisites': ['保持当前练习频率', '专注速度训练']
                }
            ]
        except Exception as e:
            self.logger.error(f"Error identifying next milestones: {e}")
            return []

