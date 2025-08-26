

```python
from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Word, UserProgress, WrongWord
from .serializers import (
    WordSerializer, 
    UserProgressSerializer, 
    WrongWordSerializer, 
    UserSerializer
)

# 认证相关视图
class CustomObtainAuthToken(ObtainAuthToken):
    """自定义令牌认证视图"""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

class UserRegistrationView(generics.CreateAPIView):
    """用户注册视图"""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        Token.objects.create(user=user)

# 词汇相关视图
class WordViewSet(viewsets.ModelViewSet):
    """单词管理视图集"""
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

# 学习进度视图
class UserProgressViewSet(viewsets.ModelViewSet):
    """用户练习记录视图集"""
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 错题本视图
class WrongWordViewSet(viewsets.ModelViewSet):
    """错题本视图集"""
    queryset = WrongWord.objects.all()
    serializer_class = WrongWordSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 用户统计视图
class UserStatsView(generics.GenericAPIView):
    """用户学习统计视图"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # 获取最近7天的练习记录
        progress = UserProgress.objects.filter(
            user=user
        ).order_by('-timestamp')[:7]
        
        stats = []
        for p in progress:
            stats.append({
                'date': p.timestamp.date().isoformat(),
                'correct': p.correct,
                'word': p.word.word if p.word else 'N/A'
            })
        return Response(stats)
```

### 代码说明：

1. **认证相关视图**
   - **CustomObtainAuthToken**：扩展DRF的默认Token认证视图，返回用户令牌
   - **UserRegistrationView**：处理用户注册请求，创建用户并自动生成认证令牌

2. **核心业务视图**
   - **WordViewSet**：管理单词数据的增删改查（需关联单词模型）
   - **UserProgressViewSet**：记录用户练习过程中的正确/错误记录
   - **WrongWordViewSet**：管理用户的错题记录，仅允许查看和操作自己的错题

3. **统计视图**
   - **UserStatsView**：返回用户最近7天的练习统计数据，包含日期、正确性及对应单词

### 使用注意事项：
1. 需要先定义对应的模型（Word, UserProgress, WrongWord）和序列化器
2. 需要在`settings.py`中配置：
   ```python
   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'rest_framework.authentication.TokenAuthentication',
       ],
       'DEFAULT_PERMISSION_CLASSES': [
           'rest_framework.permissions.IsAuthenticated',
       ]
   }
   ```
3. 需要运行`python manage.py migrate`创建auth_token表
4. 前端需要携带`Authorization: Token <用户令牌>`请求头进行认证

### 扩展建议：
- 添加分页支持
- 添加权限细化（如管理员权限）
- 添加错误处理和验证
- 添加缓存机制
- 添加学习计划相关API
- 添加打字练习的实时反馈API
- 添加发音评估API（需要集成语音识别）