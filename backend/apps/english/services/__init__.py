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

__all__ = [
    'LearningAnalyticsService',
    'MasteryLevel', 
    'LearningPhase',
    'LearningInsight',
    'MasteryAnalysis',
    'ForgettingCurveData',
    'LearningEfficiencyMetrics'
]
