from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='删除时间')

    class Meta:
        abstract = True


class Word(TimeStampedModel, SoftDeleteModel):
    word = models.CharField(max_length=128, unique=True, verbose_name='单词')
    phonetic = models.CharField(max_length=128, null=True, blank=True, verbose_name='音标')
    part_of_speech = models.CharField(max_length=50, null=True, blank=True, verbose_name='词性')
    definition = models.TextField(null=True, blank=True, verbose_name='释义')
    example = models.TextField(null=True, blank=True, verbose_name='例句')
    difficulty_level = models.CharField(max_length=20, default='beginner', verbose_name='难度')
    frequency_rank = models.IntegerField(default=0, verbose_name='词频排名')
    category_hint = models.CharField(max_length=100, null=True, blank=True, verbose_name='分类提示')
    
    # 新增多媒体字段
    audio_url = models.URLField(blank=True, verbose_name='音频URL')
    image_url = models.URLField(blank=True, verbose_name='图片URL')
    etymology = models.TextField(blank=True, verbose_name='词源')
    synonyms = models.TextField(blank=True, verbose_name='同义词')
    antonyms = models.TextField(blank=True, verbose_name='反义词')

    # provenance
    source_url = models.CharField(max_length=500, null=True, blank=True, verbose_name='来源URL')
    source_api = models.CharField(max_length=100, null=True, blank=True, verbose_name='来源API')
    license = models.CharField(max_length=100, null=True, blank=True, verbose_name='许可证')
    quality_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name='质量分')

    class Meta:
        db_table = 'english_words'
        indexes = [
            models.Index(fields=['word']),
            models.Index(fields=['difficulty_level']),
            models.Index(fields=['frequency_rank']),
            models.Index(fields=['quality_score']),
        ]
        verbose_name = '单词'
        verbose_name_plural = '单词'

    def __str__(self):
        return self.word


class UserWordProgress(TimeStampedModel, SoftDeleteModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, verbose_name='单词')
    status = models.CharField(max_length=20, default='not_learned', verbose_name='状态')
    review_count = models.IntegerField(default=0, verbose_name='复习次数')
    last_review_date = models.DateTimeField(null=True, blank=True, verbose_name='最后复习')
    next_review_date = models.DateTimeField(null=True, blank=True, verbose_name='下次复习')
    mastery_level = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name='掌握度')
    
    # SM-2算法相关字段
    ease_factor = models.DecimalField(max_digits=4, decimal_places=2, default=2.5, verbose_name='容易度因子')
    interval_days = models.IntegerField(default=1, verbose_name='复习间隔(天)')
    repetition_count = models.IntegerField(default=0, verbose_name='重复次数')

    class Meta:
        db_table = 'user_word_progress'
        unique_together = (('user', 'word'),)
        indexes = [
            models.Index(fields=['user', 'next_review_date']),
            models.Index(fields=['user', 'status']),
        ]
        verbose_name = '用户单词进度'
        verbose_name_plural = '用户单词进度'


class Expression(TimeStampedModel, SoftDeleteModel):
    expression = models.CharField(max_length=500, verbose_name='表达')
    meaning = models.TextField(null=True, blank=True, verbose_name='含义')
    category = models.CharField(max_length=100, null=True, blank=True, verbose_name='分类')
    scenario = models.CharField(max_length=100, null=True, blank=True, verbose_name='场景')
    difficulty_level = models.CharField(max_length=20, default='beginner', verbose_name='难度')
    usage_frequency = models.CharField(max_length=10, default='medium', verbose_name='使用频率')
    cultural_background = models.TextField(null=True, blank=True, verbose_name='文化背景')
    
    # 新增字段
    audio_url = models.URLField(blank=True, verbose_name='音频URL')
    usage_examples = models.TextField(blank=True, verbose_name='使用示例')

    # provenance
    source_url = models.CharField(max_length=500, null=True, blank=True, verbose_name='来源URL')
    source_api = models.CharField(max_length=100, null=True, blank=True, verbose_name='来源API')
    license = models.CharField(max_length=100, null=True, blank=True, verbose_name='许可证')
    quality_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name='质量分')

    class Meta:
        db_table = 'english_expressions'
        unique_together = (('expression', 'scenario'),)
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['scenario']),
            models.Index(fields=['difficulty_level']),
            models.Index(fields=['usage_frequency']),
        ]
        verbose_name = '表达'
        verbose_name_plural = '表达'

    def __str__(self):
        return self.expression


class WordCategory(TimeStampedModel, SoftDeleteModel):
    name = models.CharField(max_length=100, unique=True, verbose_name='分类名')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='父分类')
    description = models.TextField(null=True, blank=True, verbose_name='描述')

    class Meta:
        db_table = 'english_word_categories'
        indexes = [models.Index(fields=['name']), models.Index(fields=['parent'])]
        verbose_name = '单词分类'
        verbose_name_plural = '单词分类'

    def __str__(self):
        return self.name


class WordCategoryLink(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, verbose_name='单词')
    category = models.ForeignKey(WordCategory, on_delete=models.CASCADE, verbose_name='分类')

    class Meta:
        db_table = 'english_word_category_links'
        unique_together = (('word', 'category'),)
        indexes = [models.Index(fields=['word']), models.Index(fields=['category'])]
        verbose_name = '单词-分类关联'
        verbose_name_plural = '单词-分类关联'


class WordTag(TimeStampedModel, SoftDeleteModel):
    name = models.CharField(max_length=100, unique=True, verbose_name='标签名')

    class Meta:
        db_table = 'english_word_tags'
        indexes = [models.Index(fields=['name'])]
        verbose_name = '单词标签'
        verbose_name_plural = '单词标签'

    def __str__(self):
        return self.name


class WordTagLink(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, verbose_name='单词')
    tag = models.ForeignKey(WordTag, on_delete=models.CASCADE, verbose_name='标签')

    class Meta:
        db_table = 'english_word_tag_links'
        unique_together = (('word', 'tag'),)
        indexes = [models.Index(fields=['word']), models.Index(fields=['tag'])]
        verbose_name = '单词-标签关联'
        verbose_name_plural = '单词-标签关联'


class WordExample(TimeStampedModel, SoftDeleteModel):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, verbose_name='单词')
    sentence = models.TextField(verbose_name='例句')
    translation = models.TextField(null=True, blank=True, verbose_name='翻译')
    source_url = models.CharField(max_length=500, null=True, blank=True, verbose_name='来源URL')
    quality_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name='质量分')

    class Meta:
        db_table = 'english_word_examples'
        indexes = [models.Index(fields=['word']), models.Index(fields=['quality_score'])]
        verbose_name = '单词例句'
        verbose_name_plural = '单词例句'


class WordRelation(TimeStampedModel):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='relations', verbose_name='单词')
    related_word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='related_to', verbose_name='关联单词')
    relation_type = models.CharField(max_length=20, verbose_name='关系类型')  # synonym, antonym, derived, collocation
    note = models.CharField(max_length=200, null=True, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'english_word_relations'
        unique_together = (('word', 'related_word', 'relation_type'),)
        indexes = [models.Index(fields=['word']), models.Index(fields=['relation_type'])]
        verbose_name = '单词关系'
        verbose_name_plural = '单词关系'


class News(TimeStampedModel, SoftDeleteModel):
    title = models.CharField(max_length=500, verbose_name='标题')
    summary = models.TextField(null=True, blank=True, verbose_name='摘要')
    content = models.TextField(null=True, blank=True, verbose_name='正文')
    category = models.CharField(max_length=100, null=True, blank=True, verbose_name='分类')
    difficulty_level = models.CharField(max_length=20, default='intermediate', verbose_name='难度')
    publish_date = models.DateField(null=True, blank=True, verbose_name='发布日期')
    word_count = models.IntegerField(default=0, verbose_name='词数')
    source = models.CharField(max_length=100, null=True, blank=True, verbose_name='来源')
    
    # 新增字段
    reading_time_minutes = models.IntegerField(default=0, verbose_name='阅读时长(分钟)')
    key_vocabulary = models.TextField(blank=True, verbose_name='关键词汇')
    comprehension_questions = models.JSONField(default=list, blank=True, verbose_name='理解题目')

    # 图片字段
    image_url = models.URLField(blank=True, verbose_name='图片URL')
    image_alt = models.CharField(max_length=200, blank=True, verbose_name='图片描述')
    
    # provenance
    source_url = models.CharField(max_length=500, null=True, blank=True, verbose_name='来源URL')
    license = models.CharField(max_length=100, null=True, blank=True, verbose_name='许可证')
    quality_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name='质量分')
    


    class Meta:
        db_table = 'english_news'
        indexes = [
            models.Index(fields=['publish_date']),
            models.Index(fields=['category']),
            models.Index(fields=['difficulty_level']),
            models.Index(fields=['source']),
            models.Index(fields=['quality_score']),
        ]
        verbose_name = '英语新闻'
        verbose_name_plural = '英语新闻'

    def __str__(self):
        return self.title
    
    def delete(self, *args, **kwargs):
        """重写删除方法，确保删除本地图片文件"""
        # 删除本地图片文件
        self._cleanup_local_image()
        # 调用父类的删除方法
        super().delete(*args, **kwargs)
    
    def _cleanup_local_image(self):
        """清理本地图片文件"""
        try:
            if self.image_url and self.image_url.startswith('news_images/'):
                import os
                from django.conf import settings
                
                image_path = os.path.join(settings.MEDIA_ROOT, self.image_url)
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"已删除本地图片文件: {image_path}")
        except Exception as e:
            print(f"删除本地图片文件失败: {e}")
    
    def save(self, *args, **kwargs):
        """重写保存方法，处理图片URL更新"""
        # 如果是更新操作，检查图片URL是否发生变化
        if self.pk:
            try:
                old_instance = News.objects.get(pk=self.pk)
                # 如果图片URL发生变化，删除旧图片
                if old_instance.image_url != self.image_url and old_instance.image_url.startswith('news_images/'):
                    old_instance._cleanup_local_image()
            except News.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)


class EntityVersion(models.Model):
    entity_type = models.CharField(max_length=50, verbose_name='实体类型')
    entity_id = models.BigIntegerField(verbose_name='实体ID')
    snapshot = models.JSONField(verbose_name='快照')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='变更人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'english_entity_versions'
        indexes = [models.Index(fields=['entity_type', 'entity_id']), models.Index(fields=['created_at'])]
        verbose_name = '实体版本'
        verbose_name_plural = '实体版本'


# 新增模型

class LearningPlan(TimeStampedModel, SoftDeleteModel):
    """学习计划模型"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_plans', verbose_name='用户')
    name = models.CharField(max_length=200, verbose_name='计划名称')
    description = models.TextField(blank=True, verbose_name='计划描述')
    daily_word_target = models.IntegerField(default=10, verbose_name='每日单词目标')
    daily_expression_target = models.IntegerField(default=5, verbose_name='每日表达目标')
    review_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', '每日'),
            ('weekly', '每周'),
            ('custom', '自定义')
        ],
        default='daily',
        verbose_name='复习频率'
    )
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(null=True, blank=True, verbose_name='结束日期')

    class Meta:
        db_table = 'english_learning_plans'
        verbose_name = '学习计划'
        verbose_name_plural = '学习计划'

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class PracticeRecord(TimeStampedModel):
    """练习记录模型"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='practice_records', verbose_name='用户')
    practice_type = models.CharField(
        max_length=50,
        choices=[
            ('word_spelling', '单词拼写'),
            ('word_meaning', '单词释义'),
            ('expression_usage', '表达运用'),
            ('reading_comprehension', '阅读理解'),
            ('pronunciation', '发音练习')
        ],
        verbose_name='练习类型'
    )
    content_id = models.IntegerField(verbose_name='内容ID')
    content_type = models.CharField(
        max_length=20,
        choices=[
            ('word', '单词'),
            ('expression', '表达'),
            ('news', '新闻')
        ],
        verbose_name='内容类型'
    )
    question = models.TextField(verbose_name='题目')
    user_answer = models.TextField(verbose_name='用户答案')
    correct_answer = models.TextField(verbose_name='正确答案')
    is_correct = models.BooleanField(verbose_name='是否正确')
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='得分')
    time_spent = models.IntegerField(verbose_name='用时', help_text='秒')

    class Meta:
        db_table = 'english_practice_records'
        verbose_name = '练习记录'
        verbose_name_plural = '练习记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_practice_type_display()}"


class PronunciationRecord(TimeStampedModel):
    """发音记录模型"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pronunciation_records', verbose_name='用户')
    word_id = models.IntegerField(verbose_name='单词ID')
    audio_file = models.CharField(max_length=500, verbose_name='音频文件路径')
    pronunciation_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='发音得分')
    accuracy_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='准确度得分')
    fluency_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='流利度得分')
    feedback = models.TextField(blank=True, verbose_name='反馈建议')

    class Meta:
        db_table = 'english_pronunciation_records'
        verbose_name = '发音记录'
        verbose_name_plural = '发音记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - Word ID: {self.word_id}"


class LearningStats(TimeStampedModel):
    """学习统计模型"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_stats', verbose_name='用户')
    date = models.DateField(verbose_name='统计日期')
    words_learned = models.IntegerField(default=0, verbose_name='学习单词数')
    words_reviewed = models.IntegerField(default=0, verbose_name='复习单词数')
    expressions_learned = models.IntegerField(default=0, verbose_name='学习表达数')
    news_read = models.IntegerField(default=0, verbose_name='阅读新闻数')
    practice_count = models.IntegerField(default=0, verbose_name='练习次数')
    study_time_minutes = models.IntegerField(default=0, verbose_name='学习时长(分钟)')
    accuracy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='正确率')

    class Meta:
        db_table = 'english_learning_stats'
        verbose_name = '学习统计'
        verbose_name_plural = '学习统计'
        unique_together = [('user', 'date')]
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class Dictionary(TimeStampedModel, SoftDeleteModel):
    """词库模型"""
    name = models.CharField(max_length=100, verbose_name="词库名称")
    description = models.TextField(blank=True, verbose_name="词库描述")
    category = models.CharField(max_length=50, verbose_name="词库分类")  # 中国考试、国际考试、编程等
    language = models.CharField(max_length=10, default='en', verbose_name="语言")
    total_words = models.IntegerField(default=0, verbose_name="总单词数")
    chapter_count = models.IntegerField(default=1, verbose_name="章节数")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    source_file = models.CharField(max_length=200, blank=True, verbose_name="源文件")
    
    class Meta:
        verbose_name = "词库"
        verbose_name_plural = "词库"
        db_table = 'english_dictionary'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"


class TypingWord(models.Model):
    """打字练习专用单词模型"""
    word = models.CharField(max_length=100, verbose_name="单词")
    translation = models.CharField(max_length=200, verbose_name="翻译")
    phonetic = models.CharField(max_length=100, blank=True, verbose_name="音标")
    difficulty = models.CharField(
        max_length=20, 
        choices=[
            ('beginner', '初级'),
            ('intermediate', '中级'),
            ('advanced', '高级')
        ],
        default='intermediate',
        verbose_name="难度"
    )
    dictionary = models.ForeignKey(Dictionary, on_delete=models.CASCADE, verbose_name="所属词库", null=True, blank=True)
    chapter = models.IntegerField(default=1, verbose_name="章节")
    frequency = models.IntegerField(default=0, verbose_name="词频")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "打字练习单词"
        verbose_name_plural = "打字练习单词"
        db_table = 'english_typing_word'
        indexes = [
            models.Index(fields=['dictionary', 'chapter']),
            models.Index(fields=['word']),
            models.Index(fields=['difficulty']),
        ]
        unique_together = [('word', 'dictionary')]

    def __str__(self):
        return f"{self.word} ({self.dictionary.name})"


class TypingSession(models.Model):
    """打字练习会话记录"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    word = models.ForeignKey(TypingWord, on_delete=models.CASCADE, verbose_name="单词")
    is_correct = models.BooleanField(verbose_name="是否正确")
    typing_speed = models.FloatField(default=0.0, verbose_name="打字速度(WPM)")
    response_time = models.FloatField(default=0.0, verbose_name="响应时间(秒)")
    session_date = models.DateField(auto_now_add=True, verbose_name="练习日期")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "打字练习记录"
        verbose_name_plural = "打字练习记录"
        db_table = 'english_typing_session'
        indexes = [
            models.Index(fields=['user', 'session_date']),
            models.Index(fields=['word', 'is_correct']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.word.word} ({'正确' if self.is_correct else '错误'})"





class TypingPracticeSession(models.Model):
    """打字练习会话模型（参考QWERTY Learner设计）"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    dictionary = models.CharField(max_length=100, verbose_name="词库")
    chapter = models.IntegerField(default=1, verbose_name="章节")
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    total_words = models.IntegerField(default=0, verbose_name="总单词数")
    correct_words = models.IntegerField(default=0, verbose_name="正确单词数")
    total_time = models.FloatField(default=0.0, verbose_name="总用时(秒)")
    average_wpm = models.FloatField(default=0.0, verbose_name="平均WPM")
    accuracy_rate = models.FloatField(default=0.0, verbose_name="正确率")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    session_date = models.DateField(auto_now_add=True, verbose_name="练习日期")

    class Meta:
        verbose_name = "打字练习会话"
        verbose_name_plural = "打字练习会话"
        db_table = 'english_typing_practice_sessions'
        indexes = [
            models.Index(fields=['user', 'session_date']),
            models.Index(fields=['user', 'is_completed']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.dictionary} Ch{self.chapter} ({'完成' if self.is_completed else '进行中'})"

    def complete_session(self, total_words, correct_words, total_time):
        """完成会话并计算统计"""
        from django.utils import timezone
        self.total_words = total_words
        self.correct_words = correct_words
        self.total_time = total_time
        self.end_time = timezone.now()
        self.is_completed = True
        
        # 计算平均WPM和正确率
        if total_time > 0:
            self.average_wpm = round((total_words * 5) / (total_time / 60), 2)  # 5个字符算一个单词
        if total_words > 0:
            self.accuracy_rate = round((correct_words / total_words) * 100, 2)
        
        self.save()


class TypingPracticeRecord(models.Model):
    """打字练习详细记录"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    session = models.ForeignKey(TypingPracticeSession, on_delete=models.CASCADE, null=True, blank=True, verbose_name="练习会话")
    word = models.CharField(max_length=100, verbose_name="单词")
    is_correct = models.BooleanField(verbose_name="是否正确")
    typing_speed = models.FloatField(verbose_name="打字速度(WPM)")
    response_time = models.FloatField(verbose_name="响应时间(秒)")
    total_time = models.FloatField(verbose_name="总用时(毫秒)")
    wrong_count = models.IntegerField(default=0, verbose_name="错误次数")
    mistakes = models.JSONField(default=dict, verbose_name="按键错误详情")
    timing = models.JSONField(default=list, verbose_name="每个字符的输入时间")
    session_date = models.DateField(auto_now_add=True, verbose_name="练习日期")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "打字练习详细记录"
        verbose_name_plural = "打字练习详细记录"
        db_table = 'english_typing_practice_records'
        indexes = [
            models.Index(fields=['user', 'session_date']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.word} ({'正确' if self.is_correct else '错误'})"


class DailyPracticeStats(models.Model):
    """每日练习统计"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    date = models.DateField(verbose_name="统计日期")
    exercise_count = models.IntegerField(default=0, verbose_name="练习次数")
    word_count = models.IntegerField(default=0, verbose_name="练习单词数")
    total_time = models.FloatField(default=0, verbose_name="总用时(毫秒)")
    wrong_count = models.IntegerField(default=0, verbose_name="总错误次数")
    wrong_keys = models.JSONField(default=list, verbose_name="错误按键列表")
    avg_wpm = models.FloatField(default=0, verbose_name="平均WPM")
    accuracy_rate = models.FloatField(default=0, verbose_name="正确率")

    class Meta:
        verbose_name = "每日练习统计"
        verbose_name_plural = "每日练习统计"
        db_table = 'english_daily_practice_stats'
        unique_together = [('user', 'date')]
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class KeyErrorStats(models.Model):
    """按键错误统计"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    key = models.CharField(max_length=10, verbose_name="按键")
    error_count = models.IntegerField(default=0, verbose_name="错误次数")
    last_error_date = models.DateField(auto_now=True, verbose_name="最后错误日期")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "按键错误统计"
        verbose_name_plural = "按键错误统计"
        db_table = 'english_key_error_stats'
        unique_together = [('user', 'key')]
        indexes = [
            models.Index(fields=['user', 'error_count']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.key} ({self.error_count}次)"


class UserTypingStats(models.Model):
    """用户打字统计"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    total_words_practiced = models.IntegerField(default=0, verbose_name="总练习单词数")
    total_correct_words = models.IntegerField(default=0, verbose_name="总正确单词数")
    average_wpm = models.FloatField(default=0.0, verbose_name="平均WPM")
    total_practice_time = models.IntegerField(default=0, verbose_name="总练习时长(分钟)")
    last_practice_date = models.DateField(null=True, blank=True, verbose_name="最后练习日期")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "用户打字统计"
        verbose_name_plural = "用户打字统计"
        db_table = 'english_user_typing_stats'

    def __str__(self):
        return f"{self.user.username} - 统计"

    @property
    def accuracy(self):
        """计算准确率"""
        if self.total_words_practiced == 0:
            return 0.0
        return round((self.total_correct_words / self.total_words_practiced) * 100, 2)


class ChapterPracticeRecord(TimeStampedModel):
    """章节练习记录模型"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    dictionary_id = models.CharField(max_length=100, verbose_name="词典ID")
    chapter_number = models.IntegerField(verbose_name="章节号")
    practice_count = models.IntegerField(default=0, verbose_name="练习次数")
    last_practice_date = models.DateTimeField(null=True, blank=True, verbose_name="最后练习时间")
    
    class Meta:
        verbose_name = "章节练习记录"
        verbose_name_plural = "章节练习记录"
        db_table = 'english_chapter_practice_records'
        unique_together = [('user', 'dictionary_id', 'chapter_number')]
        indexes = [
            models.Index(fields=['user', 'dictionary_id']),
            models.Index(fields=['user', 'dictionary_id', 'chapter_number']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.dictionary_id} Ch{self.chapter_number} ({self.practice_count}次)"

    def increment_practice_count(self):
        """增加练习次数"""
        from django.utils import timezone
        self.practice_count += 1
        self.last_practice_date = timezone.now()
        self.save()


class WrongWordRecord(TimeStampedModel):
    """错题记录模型"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    word = models.CharField(max_length=100, verbose_name="单词")
    translation = models.CharField(max_length=200, verbose_name="翻译")
    dictionary_id = models.CharField(max_length=100, verbose_name="词典ID")
    error_count = models.IntegerField(default=1, verbose_name="错误次数")
    last_error_date = models.DateTimeField(auto_now=True, verbose_name="最后错误时间")
    
    class Meta:
        verbose_name = "错题记录"
        verbose_name_plural = "错题记录"
        db_table = 'english_wrong_word_records'
        unique_together = [('user', 'word', 'dictionary_id')]
        indexes = [
            models.Index(fields=['user', 'dictionary_id']),
            models.Index(fields=['user', 'last_error_date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.word} ({self.error_count}次)"

    def increment_error_count(self):
        """增加错误次数"""
        self.error_count += 1
        self.save()


class DailyPracticeDuration(TimeStampedModel):
    """每日练习时长统计模型"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    date = models.DateField(verbose_name="统计日期")
    total_duration_minutes = models.IntegerField(default=0, verbose_name="总练习时长(分钟)")
    session_count = models.IntegerField(default=0, verbose_name="练习会话数")
    
    class Meta:
        verbose_name = "每日练习时长"
        verbose_name_plural = "每日练习时长"
        db_table = 'english_daily_practice_duration'
        unique_together = [('user', 'date')]
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.total_duration_minutes}分钟)"

    def add_session_duration(self, duration_minutes):
        """添加会话时长"""
        self.total_duration_minutes += duration_minutes
        self.session_count += 1
        self.save()


# ================================
# 地道表达模块相关模型
# ================================

class IdiomaticExpression(Expression):
    """地道表达模型 - 继承Expression模型"""
    
    # 表达类型选择
    EXPRESSION_TYPE_CHOICES = [
        ('idiom', '习语'),
        ('slang', '俚语'),
        ('collocation', '固定搭配'),
        ('phrase', '短语'),
        ('proverb', '谚语'),
        ('metaphor', '隐喻表达'),
    ]
    
    # 正式程度选择
    FORMALITY_LEVEL_CHOICES = [
        ('informal', '非正式'),
        ('neutral', '中性'),
        ('formal', '正式'),
    ]
    
    expression_type = models.CharField(
        max_length=20,
        choices=EXPRESSION_TYPE_CHOICES,
        default='phrase',
        verbose_name='表达类型'
    )
    
    frequency_score = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='使用频率评分(1-10)',
        help_text='1=极少使用, 10=极常使用'
    )
    
    formality_level = models.CharField(
        max_length=10,
        choices=FORMALITY_LEVEL_CHOICES,
        default='neutral',
        verbose_name='正式程度'
    )
    
    phonetic_transcription = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='音标',
        help_text='IPA音标记录'
    )
    
    # 使用JSONField存储扩展数据
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='扩展元数据',
        help_text='存储变体形式、同义表达、相关表达等'
    )
    
    class Meta:
        db_table = 'english_idiomatic_expressions'
        verbose_name = '地道表达'
        verbose_name_plural = '地道表达'
        indexes = [
            models.Index(fields=['expression_type']),
            models.Index(fields=['frequency_score']),
            models.Index(fields=['formality_level']),
            models.Index(fields=['expression_type', 'frequency_score']),
        ]
    
    def __str__(self):
        return f"{self.expression} ({self.get_expression_type_display()})"
    
    def save(self, *args, **kwargs):
        """重写save方法，确保metadata字段的默认值"""
        if not self.metadata:
            self.metadata = {
                'variants': [],  # 变体形式
                'synonyms': [],  # 同义表达
                'related_expressions': [],  # 相关表达
                'etymology': '',  # 词源
                'regional_usage': '',  # 地区使用情况
            }
        super().save(*args, **kwargs)


class ExpressionScenario(TimeStampedModel, SoftDeleteModel):
    """表达使用场景模型"""
    
    SCENARIO_TYPE_CHOICES = [
        ('business', '商务场合'),
        ('casual', '日常交流'),
        ('academic', '学术场合'),
        ('social', '社交场合'),
        ('travel', '旅行出行'),
        ('workplace', '职场环境'),
        ('entertainment', '娱乐休闲'),
    ]
    
    scenario_name = models.CharField(
        max_length=100,
        verbose_name='场景名称'
    )
    
    context_description = models.TextField(
        verbose_name='上下文描述',
        help_text='详细描述该场景的使用背景'
    )
    
    example_dialogue = models.TextField(
        blank=True,
        verbose_name='示例对话',
        help_text='展示表达在实际对话中的使用'
    )
    
    scenario_type = models.CharField(
        max_length=20,
        choices=SCENARIO_TYPE_CHOICES,
        default='casual',
        verbose_name='场景类型'
    )
    
    # 与地道表达的多对多关系
    expressions = models.ManyToManyField(
        IdiomaticExpression,
        through='ExpressionScenarioLink',
        related_name='scenarios',
        verbose_name='关联表达'
    )
    
    class Meta:
        db_table = 'english_expression_scenarios'
        verbose_name = '表达场景'
        verbose_name_plural = '表达场景'
        indexes = [
            models.Index(fields=['scenario_type']),
            models.Index(fields=['scenario_name']),
        ]
    
    def __str__(self):
        return f"{self.scenario_name} ({self.get_scenario_type_display()})"


class ExpressionSource(TimeStampedModel, SoftDeleteModel):
    """表达数据源管理模型"""
    
    SOURCE_TYPE_CHOICES = [
        ('dictionary', '词典'),
        ('forum', '论坛'),
        ('news', '新闻媒体'),
        ('social_media', '社交媒体'),
        ('academic', '学术资料'),
        ('literature', '文学作品'),
        ('movie_tv', '影视作品'),
        ('manual', '人工录入'),
    ]
    
    source_name = models.CharField(
        max_length=100,
        verbose_name='数据源名称'
    )
    
    source_url = models.URLField(
        blank=True,
        verbose_name='数据源URL'
    )
    
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        default='manual',
        verbose_name='数据源类型'
    )
    
    reliability_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        verbose_name='可靠性评分(0-10)',
        help_text='数据源的可靠性和权威性评分'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='数据源描述'
    )
    
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='最后更新时间'
    )
    
    # 与地道表达的外键关系
    expressions = models.ManyToManyField(
        IdiomaticExpression,
        related_name='sources',
        blank=True,
        verbose_name='关联表达'
    )
    
    class Meta:
        db_table = 'english_expression_sources'
        verbose_name = '表达数据源'
        verbose_name_plural = '表达数据源'
        indexes = [
            models.Index(fields=['source_type']),
            models.Index(fields=['reliability_score']),
            models.Index(fields=['last_updated']),
        ]
    
    def __str__(self):
        return f"{self.source_name} ({self.get_source_type_display()})"


class ExpressionScenarioLink(models.Model):
    """表达-场景关联中间表"""
    
    expression = models.ForeignKey(
        IdiomaticExpression,
        on_delete=models.CASCADE,
        verbose_name='表达'
    )
    
    scenario = models.ForeignKey(
        ExpressionScenario,
        on_delete=models.CASCADE,
        verbose_name='场景'
    )
    
    relevance_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        verbose_name='相关性评分(0-10)',
        help_text='表达在该场景中的相关性和适用性'
    )
    
    usage_frequency = models.CharField(
        max_length=10,
        choices=[
            ('rare', '很少'),
            ('occasional', '偶尔'),
            ('common', '常见'),
            ('frequent', '频繁'),
        ],
        default='common',
        verbose_name='在该场景中的使用频率'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'english_expression_scenario_links'
        unique_together = [('expression', 'scenario')]
        verbose_name = '表达-场景关联'
        verbose_name_plural = '表达-场景关联'
        indexes = [
            models.Index(fields=['expression', 'relevance_score']),
            models.Index(fields=['scenario', 'usage_frequency']),
        ]
    
    def __str__(self):
        return f"{self.expression.expression} - {self.scenario.scenario_name}"


class UserExpressionProgress(TimeStampedModel, SoftDeleteModel):
    """用户表达学习进度模型"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='用户'
    )
    
    expression = models.ForeignKey(
        IdiomaticExpression,
        on_delete=models.CASCADE,
        verbose_name='表达'
    )
    
    mastery_level = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='掌握程度(0-100)',
        help_text='0=完全不会, 100=完全掌握'
    )
    
    review_count = models.IntegerField(
        default=0,
        verbose_name='复习次数'
    )
    
    correct_count = models.IntegerField(
        default=0,
        verbose_name='正确次数'
    )
    
    last_reviewed = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后复习时间'
    )
    
    next_review = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='下次复习时间'
    )
    
    learning_streak = models.IntegerField(
        default=0,
        verbose_name='连续学习天数'
    )
    
    # SM-2算法相关字段
    easiness_factor = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=2.5,
        verbose_name='容易度因子'
    )
    
    interval = models.IntegerField(
        default=1,
        verbose_name='复习间隔(天)'
    )
    
    # 学习历史记录
    learning_history = models.JSONField(
        default=list,
        blank=True,
        verbose_name='学习历史记录',
        help_text='存储每次学习的详细记录'
    )
    
    class Meta:
        db_table = 'english_user_expression_progress'
        unique_together = [('user', 'expression')]
        verbose_name = '用户表达进度'
        verbose_name_plural = '用户表达进度'
        indexes = [
            models.Index(fields=['user', 'next_review']),
            models.Index(fields=['user', 'mastery_level']),
            models.Index(fields=['user', 'last_reviewed']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.expression.expression} ({self.mastery_level}%)"
    
    @property
    def accuracy_rate(self):
        """计算正确率"""
        if self.review_count == 0:
            return 0.0
        return round((self.correct_count / self.review_count) * 100, 2)


class AIAssistantConfig(TimeStampedModel, SoftDeleteModel):
    """AI助教配置模型"""
    
    AI_PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('google', 'Google'),
        ('azure', 'Azure OpenAI'),
        ('local', '本地模型'),
        ('custom', '自定义'),
    ]
    
    config_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='配置名称'
    )
    
    ai_provider = models.CharField(
        max_length=20,
        choices=AI_PROVIDER_CHOICES,
        default='openai',
        verbose_name='AI提供商'
    )
    
    model_name = models.CharField(
        max_length=100,
        verbose_name='模型名称',
        help_text='如gpt-4, claude-3-sonnet等'
    )
    
    api_endpoint = models.URLField(
        blank=True,
        verbose_name='API端点',
        help_text='自定义API端点URL'
    )
    
    max_tokens = models.IntegerField(
        default=2000,
        validators=[MinValueValidator(1), MaxValueValidator(100000)],
        verbose_name='最大令牌数'
    )
    
    temperature = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0)],
        verbose_name='温度参数',
        help_text='控制输出的随机性，0-2之间'
    )
    
    system_prompt = models.TextField(
        default='你是一个专业的英语学习助教，专门帮助学生学习地道表达。',
        verbose_name='系统提示词模板'
    )
    
    # 扩展配置参数
    extended_config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='扩展配置参数',
        help_text='存储特定模型的额外配置参数'
    )
    
    # 加密存储API密钥（实际项目中应使用更安全的方式）
    api_key_encrypted = models.TextField(
        blank=True,
        verbose_name='加密的API密钥',
        help_text='请勿直接存储明文密钥'
    )
    
    is_active = models.BooleanField(
        default=False,
        verbose_name='是否激活',
        help_text='同时只能有一个配置处于激活状态'
    )
    
    version = models.CharField(
        max_length=20,
        default='1.0',
        verbose_name='配置版本'
    )
    
    # 使用统计
    usage_count = models.IntegerField(
        default=0,
        verbose_name='使用次数'
    )
    
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后使用时间'
    )
    
    class Meta:
        db_table = 'english_ai_assistant_configs'
        verbose_name = 'AI助教配置'
        verbose_name_plural = 'AI助教配置'
        indexes = [
            models.Index(fields=['ai_provider']),
            models.Index(fields=['is_active']),
            models.Index(fields=['last_used']),
        ]
    
    def __str__(self):
        status = "激活" if self.is_active else "未激活"
        return f"{self.config_name} ({self.ai_provider}) - {status}"
    
    def save(self, *args, **kwargs):
        """重写save方法，确保只有一个配置处于激活状态"""
        if self.is_active:
            # 将其他配置设为非激活状态
            AIAssistantConfig.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


