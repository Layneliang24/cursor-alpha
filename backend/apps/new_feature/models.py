

根据前端组件中的英语学习相关功能和现有代码结构推测，以下是可能的 `models.py` 设计：

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    learning_plan = models.TextField(blank=True)  # JSON格式的学习计划
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    streak_days = models.IntegerField(default=0)  # 连续学习天数
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Word(models.Model):
    word = models.CharField(max_length=100, unique=True)
    pronunciation = models.CharField(max_length=100, blank=True)
    definition = models.TextField()
    example_sentence = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='words')
    is_common = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.word

class PracticeSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE, null=True, blank=True)  # 可能是随机练习
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    mistakes = models.IntegerField(default=0)
    session_type = models.CharField(max_length=20, choices=[('typing', '打字'), ('vocabulary', '词汇'), ('expression', '表达')])

    def duration(self):
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

class WrongWord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    mistake_count = models.IntegerField(default=1)
    last_practiced = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'word')

class LearningPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_words = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    progress = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    source = models.CharField(max_length=100)
    publish_date = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class UserStatistic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    words_learned = models.IntegerField(default=0)
    practice_time = models.IntegerField(default=0)  # 秒数
    articles_read = models.IntegerField(default=0)
    correct_attempts = models.IntegerField(default=0)
    wrong_attempts = models.IntegerField(default=0)
```

### 主要模型说明：
1. **Profile**：用户扩展信息，包含学习计划、登录IP等
2. **Category**：词汇分类（如语法、商务英语等）
3. **Word**：核心词汇表，包含发音、释义、例句等
4. **PracticeSession**：记录每次练习的详细数据
5. **WrongWord**：错题本功能，跟踪用户错误记录
6. **LearningPlan**：学习计划管理
7. **NewsArticle**：新闻文章管理（对应前端新闻组件）
8. **UserStatistic**：用户学习统计，用于生成图表数据

### 扩展建议：
1. 添加`ManyToManyField`在Word和User之间实现收藏功能
2. 为NewsArticle添加图片字段和SEO字段
3. 在Profile中添加偏好设置字段（如夜间模式开关）
4. 为PracticeSession添加更多练习类型（如听写/翻译）
5. 添加Session中间件自动记录登录IP

这些模型与前端组件中的以下功能对应：
- `TypingPractice.vue` → PracticeSession
- `WordDetail.vue` → Word模型
- `WrongWordsNotebook.vue` → WrongWord
- `LearningChart.vue` → UserStatistic
- `NewsList.vue` → NewsArticle

需要根据实际API接口需求调整字段类型和关系，建议添加以下索引：
```python
class Meta:
    indexes = [
        models.Index(fields=['user', 'created_at']),
    ]
```