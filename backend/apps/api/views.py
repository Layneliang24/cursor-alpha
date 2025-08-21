from rest_framework import viewsets, status, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from .pagination import CustomPageNumberPagination
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework_simplejwt.tokens import RefreshToken
from apps.articles.models import Article, Comment, Like, Bookmark
from apps.categories.models import Category, Tag
from .permissions import IsAdminOrReadOnly, DjangoModelPermissionsOrReadOnly, IsAuthorOrAdminOrReadOnly
from apps.users.models import UserProfile
from apps.links.models import ExternalLink
from .serializers import (
    UserSerializer, UserProfileSerializer, CategorySerializer, TagSerializer,
    ArticleSerializer, ArticleCreateSerializer, ArticleUpdateSerializer,
    CommentSerializer, UserRegistrationSerializer, UserLoginSerializer, ExternalLinkSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """分类视图集"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [DjangoModelPermissionsOrReadOnly]
    
    def get_queryset(self):
        """非管理员仅能看到激活分类，管理员可查看全部"""
        base_qs = Category.objects.all()
        user = self.request.user
        if user and user.is_authenticated and (user.is_staff or user.is_superuser):
            return base_qs
        return base_qs.filter(status='active')

    # 缓存 list 响应 60s（不要缓存 get_queryset，需返回 QuerySet）
    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        """获取分类下的文章"""
        category = self.get_object()
        articles = Article.objects.filter(category=category, status='published')
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """标签视图集"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [DjangoModelPermissionsOrReadOnly]


class ArticleViewSet(viewsets.ModelViewSet):
    """文章视图集"""
    # 提升查询性能：一次性取出作者与分类，减少N+1
    queryset = Article.objects.select_related('author', 'category').prefetch_related('tags').filter(status='published').order_by('-created_at')
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    pagination_class = CustomPageNumberPagination
    filterset_fields = ['category', 'author', 'featured']
    search_fields = ['title', 'content', 'summary']
    ordering_fields = ['created_at', 'views', 'likes']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ArticleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ArticleUpdateSerializer
        return ArticleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        # 作者本人可以看到自己的草稿/归档
        author_id = self.request.query_params.get('author')
        if user.is_authenticated and author_id and str(user.id) == str(author_id):
            return Article.objects.select_related('author', 'category').prefetch_related('tags').filter(author=user)
        return qs
    

    
    def perform_create(self, serializer):
        """创建文章时设置作者"""
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞文章"""
        article = self.get_object()
        user = request.user
        
        if Like.objects.filter(user=user, article=article).exists():
            Like.objects.filter(user=user, article=article).delete()
            return Response({'message': '取消点赞'})
        else:
            Like.objects.create(user=user, article=article)
            return Response({'message': '点赞成功'})
    
    @action(detail=True, methods=['post'])
    def bookmark(self, request, pk=None):
        """收藏文章"""
        article = self.get_object()
        user = request.user
        
        if Bookmark.objects.filter(user=user, article=article).exists():
            Bookmark.objects.filter(user=user, article=article).delete()
            return Response({'message': '取消收藏'})
        else:
            Bookmark.objects.create(user=user, article=article)
            return Response({'message': '收藏成功'})
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """获取文章评论"""
        article = self.get_object()
        comments = Comment.objects.filter(article=article, parent=None, is_approved=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """评论视图集"""
    queryset = Comment.objects.filter(is_approved=True)
    serializer_class = CommentSerializer
    # 登录用户可写（发表评论/回复），未登录用户只读；管理员仍可执行所有操作
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        """创建评论时设置作者"""
        serializer.save(author=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class AuthView(APIView):
    """认证视图"""
    permission_classes = [permissions.AllowAny]
    authentication_classes: list = []
    
    def post(self, request):
        """用户登录"""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            
            if user:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': '登录成功',
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                })
            else:
                return Response({'error': '用户名或密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """注册视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """用户注册"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': '注册成功',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """登出视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """用户登出"""
        logout(request)
        return Response({'message': '登出成功'})


class UserProfileViewSet(viewsets.ModelViewSet):
    """用户资料视图集"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """返回所有用户资料，但限制操作权限"""
        return UserProfile.objects.all()
    
    def get_object(self):
        """获取对象时确保用户只能操作自己的资料"""
        from django.shortcuts import get_object_or_404
        try:
            obj = super().get_object()
        except Exception:
            # 如果根据 profile id 未找到, 尝试用 user_id 寻找
            obj = get_object_or_404(UserProfile, user_id=self.kwargs.get(self.lookup_field))

        # 权限检查：只能操作自己的资料，管理员除外
        if (not self.request.user.is_staff and not self.request.user.is_superuser and
                obj.user != self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您只能操作自己的资料")
        return obj

    # 新增端点 /profiles/me/
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """获取或更新当前登录用户的个人资料"""
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(profile, data=request.data, partial=(request.method == 'PATCH'))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """创建用户资料时设置用户"""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """更新用户资料时确保是当前用户"""
        if serializer.instance.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("您只能操作自己的资料")
        serializer.save()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_request(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = serializer.save()
    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = serializer.save()
    return Response(result, status=status.HTTP_200_OK)


class ExternalLinkViewSet(viewsets.ModelViewSet):
    """外部链接视图集"""
    queryset = ExternalLink.objects.all().order_by('order', '-created_at')
    serializer_class = ExternalLinkSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        base_qs = ExternalLink.objects.all().order_by('order', '-created_at')
        user = self.request.user
        if user and user.is_authenticated and (user.is_staff or user.is_superuser):
            return base_qs
        return base_qs.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_image(request):
    """上传图片接口"""
    if 'image' not in request.FILES:
        return Response({'error': '请选择要上传的图片'}, status=status.HTTP_400_BAD_REQUEST)
    
    image = request.FILES['image']
    
    # 验证文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if image.content_type not in allowed_types:
        return Response({'error': '只支持 JPEG、PNG、GIF、WebP 格式的图片'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证文件大小 (5MB)
    if image.size > 5 * 1024 * 1024:
        return Response({'error': '图片大小不能超过5MB'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 生成唯一文件名
        file_extension = os.path.splitext(image.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = f"uploads/images/{unique_filename}"
        
        # 保存文件
        saved_path = default_storage.save(file_path, ContentFile(image.read()))
        
        # 返回完整URL
        image_url = request.build_absolute_uri(f"/media/{saved_path}")
        
        return Response({
            'url': image_url,
            'filename': unique_filename,
            'size': image.size
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': f'上传失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_avatar(request):
    """上传用户头像接口"""
    if 'avatar' not in request.FILES:
        return Response({'error': '请选择要上传的头像'}, status=status.HTTP_400_BAD_REQUEST)
    
    avatar = request.FILES['avatar']
    
    # 验证文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if avatar.content_type not in allowed_types:
        return Response({'error': '只支持 JPEG、PNG、GIF、WebP 格式的头像'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证文件大小 (2MB)
    if avatar.size > 2 * 1024 * 1024:
        return Response({'error': '头像大小不能超过2MB'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 生成唯一文件名
        file_extension = os.path.splitext(avatar.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = f"avatars/{unique_filename}"
        
        # 保存文件
        saved_path = default_storage.save(file_path, ContentFile(avatar.read()))
        
        # 更新用户头像
        user = request.user
        user.avatar = saved_path
        user.save()
        
        # 返回完整URL
        avatar_url = request.build_absolute_uri(f"/media/{saved_path}")
        
        return Response({
            'url': avatar_url,
            'filename': unique_filename,
            'size': avatar.size
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': f'头像上传失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_avatar_url(request):
    """更新用户头像URL接口（用于外部头像链接）"""
    avatar_url = request.data.get('avatar_url')
    
    if not avatar_url:
        return Response({'error': '请提供头像URL'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = request.user
        
        # 清空之前上传的头像文件
        if user.avatar:
            user.avatar = None
        
        # 保存外部头像URL到UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.avatar_url = avatar_url
        profile.save()
        
        user.save()
        
        return Response({
            'url': avatar_url,
            'message': '头像URL更新成功'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': f'头像URL更新失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])  # 不需要认证
def verify_user_identity(request):
    """验证用户身份并返回头像信息"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    print(f"收到身份验证请求: username={username}, password={'*' * len(password) if password else None}")
    
    if not username or not password:
        return Response({'error': '用户名和密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 先检查用户是否存在
        try:
            user_by_username = User.objects.get(username=username)
            print(f"通过用户名找到用户: {user_by_username}")
        except User.DoesNotExist:
            print(f"用户名 {username} 不存在")
            user_by_username = None
        
        try:
            user_by_email = User.objects.get(email=username)
            print(f"通过邮箱找到用户: {user_by_email}")
        except User.DoesNotExist:
            print(f"邮箱 {username} 不存在")
            user_by_email = None
        
        # 验证用户身份 - 支持用户名或邮箱登录
        user = authenticate(username=username, password=password)
        print(f"直接authenticate结果: {user}")
        
        # 如果用户名验证失败，尝试用邮箱验证
        if not user and user_by_email:
            print(f"尝试用邮箱用户的用户名验证: {user_by_email.username}")
            user = authenticate(username=user_by_email.username, password=password)
            print(f"邮箱authenticate结果: {user}")
        
        print(f"最终验证结果: username={username}, user={user}")
        
        if user:
            # 用户身份验证成功，返回头像和基本信息
            avatar_url = user.get_avatar_url()
            if hasattr(user, 'avatar') and user.avatar:
                avatar_url = request.build_absolute_uri(user.avatar.url)
            
            return Response({
                'verified': True,
                'user_info': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'avatar': avatar_url
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'verified': False,
                'error': '用户名或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        return Response({'error': f'验证失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Home page aggregated endpoints
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_home_stats(request):
    """返回首页统计信息"""
    try:
        stats = {
            'users': User.objects.count(),
            'articles': Article.objects.count(),
            'categories': Category.objects.count(),
            'tags': Tag.objects.count(),
        }
        return Response(stats, status=status.HTTP_200_OK)
    except Exception as exc:
        return Response({'error': f'获取统计信息失败: {exc}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_popular_articles(request):
    """返回热门文章列表（按浏览量与点赞数排序）"""
    try:
        limit = int(request.query_params.get('limit', 10))
        popular_qs = (
            Article.objects.filter(status='published')
            .order_by('-views', '-likes', '-created_at')[:limit]
        )
        serializer = ArticleSerializer(popular_qs, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as exc:
        return Response({'error': f'获取热门文章失败: {exc}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_recent_articles(request):
    """返回最近文章列表"""
    try:
        limit = int(request.query_params.get('limit', 10))
        recent_qs = Article.objects.filter(status='published').order_by('-created_at')[:limit]
        serializer = ArticleSerializer(recent_qs, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as exc:
        return Response({'error': f'获取最近文章失败: {exc}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_popular_tags(request):
    """返回热门标签（按文章数量降序）"""
    try:
        limit = int(request.query_params.get('limit', 20))
        tags_qs = Tag.objects.annotate(num_articles=Count('articles')).order_by('-num_articles', 'name')[:limit]
        data = [
            {
                'id': t.id,
                'name': getattr(t, 'name', str(t)),
                'num_articles': getattr(t, 'num_articles', 0),
            }
            for t in tags_qs
        ]
        return Response(data, status=status.HTTP_200_OK)
    except Exception as exc:
        return Response({'error': f'获取热门标签失败: {exc}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
