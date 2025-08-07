from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from apps.articles.models import Article, Comment, Like, Bookmark
from apps.categories.models import Category, Tag
from apps.users.models import UserProfile
from .serializers import (
    UserSerializer, UserProfileSerializer, CategorySerializer, TagSerializer,
    ArticleSerializer, ArticleCreateSerializer, ArticleUpdateSerializer,
    CommentSerializer, UserRegistrationSerializer, UserLoginSerializer
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
    queryset = Category.objects.filter(status='active')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ArticleViewSet(viewsets.ModelViewSet):
    """文章视图集"""
    queryset = Article.objects.filter(status='published')
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ArticleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ArticleUpdateSerializer
        return ArticleSerializer
    
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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        """创建评论时设置作者"""
        serializer.save(author=self.request.user)


class AuthView(APIView):
    """认证视图"""
    permission_classes = [permissions.AllowAny]
    
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
        """只返回当前用户的资料"""
        return UserProfile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """创建用户资料时设置用户"""
        serializer.save(user=self.request.user)
