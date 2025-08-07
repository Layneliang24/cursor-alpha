from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.articles.models import Article, Comment
from apps.categories.models import Category, Tag
from apps.users.models import UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""
    article_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器"""
    article_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Tag
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['author', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        """获取回复"""
        replies = Comment.objects.filter(parent=obj, is_approved=True)
        return CommentSerializer(replies, many=True).data


class ArticleSerializer(serializers.ModelSerializer):
    """文章序列化器"""
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.ReadOnlyField()
    reading_time = serializers.ReadOnlyField()
    
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ['author', 'views', 'likes', 'comments_count', 'created_at', 'updated_at']


class ArticleCreateSerializer(serializers.ModelSerializer):
    """文章创建序列化器"""
    class Meta:
        model = Article
        fields = ['title', 'content', 'summary', 'category', 'tags', 'status', 'featured']


class ArticleUpdateSerializer(serializers.ModelSerializer):
    """文章更新序列化器"""
    class Meta:
        model = Article
        fields = ['title', 'content', 'summary', 'category', 'tags', 'status', 'featured']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("密码不匹配")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField() 