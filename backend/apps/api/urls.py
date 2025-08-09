from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserViewSet, CategoryViewSet, TagViewSet, ArticleViewSet, CommentViewSet,
    AuthView, RegisterView, LogoutView, UserProfileViewSet, upload_image, upload_avatar, update_avatar_url, verify_user_identity
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'articles', ArticleViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'profiles', UserProfileViewSet)

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
] 