from django.db import models
from django.conf import settings


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
