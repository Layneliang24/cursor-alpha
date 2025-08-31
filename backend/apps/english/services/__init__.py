"""
English learning services package

This package contains service classes for English learning functionality:
- LearningAnalyticsService: Core learning analytics and insights
"""

from .learning_analytics import (
    LearningAnalyticsService,
    MasteryLevel,
    LearningPhase,
    LearningInsight,
    MasteryAnalysis,
    ForgettingCurveData,
    LearningEfficiencyMetrics
)
from .learning_stats import LearningStatsService

__all__ = [
    'LearningAnalyticsService',
    'LearningStatsService',
    'MasteryLevel', 
    'LearningPhase',
    'LearningInsight',
    'MasteryAnalysis',
    'ForgettingCurveData',
    'LearningEfficiencyMetrics'
]

