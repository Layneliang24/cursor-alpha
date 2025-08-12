from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobPostViewSet

router = DefaultRouter()
router.register(r'jobs', JobPostViewSet, basename='job-posts')

urlpatterns = [
    path('', include(router.urls)),
]


