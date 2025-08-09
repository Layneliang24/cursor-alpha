from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserViewSet, CategoryViewSet, TagViewSet, ArticleViewSet, CommentViewSet, ExternalLinkViewSet,
    AuthView, RegisterView, LogoutView, UserProfileViewSet, upload_image, upload_avatar, update_avatar_url, verify_user_identity,
    password_reset_request, password_reset_confirm, get_home_stats, get_popular_articles, get_recent_articles, get_popular_tags
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'articles', ArticleViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'external-links', ExternalLinkViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', AuthView.as_view(), name='auth_login'),
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('upload/image/', upload_image, name='upload_image'),
    path('upload/avatar/', upload_avatar, name='upload_avatar'),
    path('update-avatar-url/', update_avatar_url, name='update_avatar_url'),
    path('auth/verify-identity/', verify_user_identity, name='verify_user_identity'),
    path('auth/password-reset/', password_reset_request, name='password_reset_request'),
    path('auth/password-reset-confirm/', password_reset_confirm, name='password_reset_confirm'),
    path('home/stats/', get_home_stats, name='home_stats'),
    path('home/popular-articles/', get_popular_articles, name='popular_articles'),
    path('home/recent-articles/', get_recent_articles, name='recent_articles'),
    path('home/popular-tags/', get_popular_tags, name='popular_tags'),
] 