from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from apps.articles.models import Article, Comment
from apps.categories.models import Category, Tag
from apps.users.models import UserProfile
from apps.links.models import ExternalLink

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    avatar = serializers.SerializerMethodField()
    username = serializers.CharField(required=False)  # 更新时username不是必填的
    groups = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login', 'avatar', 'bio', 'website', 'is_staff', 'is_superuser', 'groups', 'permissions']
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_avatar(self, obj):
        """获取用户头像完整URL"""
        if hasattr(obj, 'avatar') and obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return obj.get_avatar_url()

    def get_groups(self, obj):
        try:
            return list(obj.groups.values_list('name', flat=True))
        except Exception:
            return []

    def get_permissions(self, obj):
        return list(obj.user_permissions.values_list('codename', flat=True))


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""
    article_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


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
    cover_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ['author', 'views', 'likes', 'comments_count', 'created_at', 'updated_at']
    
    def get_cover_image(self, obj):
        """获取封面图片完整URL"""
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return None


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


class PasswordResetRequestSerializer(serializers.Serializer):
    """密码重置请求序列化器"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """验证邮箱是否存在"""
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("该邮箱地址未注册")
        return value
    
    def save(self):
        """发送密码重置邮件"""
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        
        # 生成重置令牌
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # 构建重置链接
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        # 发送邮件
        subject = 'Alpha - 密码重置'
        message = f'''
您好 {user.first_name or user.username}，

您请求重置Alpha账户的密码。请点击以下链接重置您的密码：

{reset_url}

此链接将在24小时内有效。如果您没有请求重置密码，请忽略此邮件。

Alpha团队
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        return {'message': '密码重置邮件已发送'}


class PasswordResetConfirmSerializer(serializers.Serializer):
    """密码重置确认序列化器"""
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=6, max_length=128)
    confirm_password = serializers.CharField()
    
    def validate(self, attrs):
        """验证密码和令牌"""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("两次输入的密码不一致")
        
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("无效的重置链接")
        
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("重置链接已过期或无效")
        
        attrs['user'] = user
        return attrs
    
    def save(self):
        """重置密码"""
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return {'message': '密码重置成功'}


class ExternalLinkSerializer(serializers.ModelSerializer):
    """外部链接序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ExternalLink
        fields = ['id', 'title', 'url', 'description', 'icon', 'link_type', 'is_active', 'order', 'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at'] 