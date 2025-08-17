from rest_framework.routers import DefaultRouter
from .views import (
    WordViewSet, UserWordProgressViewSet, ExpressionViewSet, NewsViewSet,
    LearningPlanViewSet, PracticeRecordViewSet, PronunciationRecordViewSet,
    LearningStatsViewSet, 
    TypingPracticeViewSet, DictionaryViewSet, TypingWordViewSet,
    DataAnalysisViewSet
)

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

urlpatterns = router.urls


urlpatterns = router.urls
