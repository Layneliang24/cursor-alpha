from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WordViewSet, UserWordProgressViewSet, ExpressionViewSet, NewsViewSet,
    LearningPlanViewSet, PracticeRecordViewSet, PronunciationRecordViewSet,
    LearningStatsViewSet, 
    TypingPracticeViewSet, DictionaryViewSet, TypingWordViewSet,
    DataAnalysisViewSet, ai_chat
)
from .analytics_views import (
    progress_trend, mastery_distribution, time_analysis,
    efficiency_analysis, learning_insights
)
from .report_views import LearningReportViewSet, LearningGoalViewSet

router = DefaultRouter()
router.register(r'english/words', WordViewSet, basename='english-words')
router.register(r'english/progress', UserWordProgressViewSet, basename='english-progress')
router.register(r'english/expressions', ExpressionViewSet, basename='english-expressions')
router.register(r'english/news', NewsViewSet, basename='english-news')
router.register(r'english/plans', LearningPlanViewSet, basename='english-plans')
router.register(r'english/practice', PracticeRecordViewSet, basename='english-practice')
router.register(r'english/pronunciation', PronunciationRecordViewSet, basename='english-pronunciation')
router.register(r'english/stats', LearningStatsViewSet, basename='english-stats')
router.register(r'english/typing-practice', TypingPracticeViewSet, basename='typing-practice')
router.register(r'english/dictionaries', DictionaryViewSet, basename='english-dictionaries')
router.register(r'english/typing-words', TypingWordViewSet, basename='english-typing-words')
router.register(r'english/data-analysis', DataAnalysisViewSet, basename='english-data-analysis')
router.register(r'english/reports', LearningReportViewSet, basename='english-reports')
router.register(r'english/goals', LearningGoalViewSet, basename='english-goals')

# 分析API路由
analytics_patterns = [
    path('analytics/progress-trend/', progress_trend, name='analytics-progress-trend'),
    path('analytics/mastery-distribution/', mastery_distribution, name='analytics-mastery-distribution'),
    path('analytics/time-analysis/', time_analysis, name='analytics-time-analysis'),
    path('analytics/efficiency-analysis/', efficiency_analysis, name='analytics-efficiency-analysis'),
    path('analytics/learning-insights/', learning_insights, name='analytics-learning-insights'),
]

# AI聊天路由
ai_patterns = [
    path('english/ai/chat/', ai_chat, name='ai-chat'),
]

urlpatterns = router.urls + analytics_patterns + ai_patterns
