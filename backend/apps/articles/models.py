from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class Article(models.Model):
    """文章模型"""
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档'),
    )
    
    title = models.CharField(max_length=200, verbose_name='标题')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='文章别名')
    content = models.TextField(verbose_name='内容')
    summary = models.TextField(max_length=500, blank=True, verbose_name='摘要')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', verbose_name='作者')
    category = models.ForeignKey('categories.Category', on_delete=models.CASCADE, related_name='articles', verbose_name='分类')
    tags = models.ManyToManyField('categories.Tag', blank=True, related_name='articles', verbose_name='标签')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    featured = models.BooleanField(default=False, verbose_name='推荐')
    views = models.PositiveIntegerField(default=0, verbose_name='浏览量')
    likes = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    comments_count = models.PositiveIntegerField(default=0, verbose_name='评论数')
    cover_image = models.ImageField(upload_to='articles/covers/', null=True, blank=True, verbose_name='封面图片')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        app_label = 'articles'
        verbose_name = '文章'
        verbose_name_plural = '文章'
        db_table = 'articles_article'
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """保存时自动生成slug"""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """获取文章详情URL"""
        return reverse('article_detail', kwargs={'slug': self.slug})
    
    def increase_views(self):
        """增加浏览量"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def increase_likes(self):
        """增加点赞数"""
        self.likes += 1
        self.save(update_fields=['likes'])
    
    def decrease_likes(self):
        """减少点赞数"""
        if self.likes > 0:
            self.likes -= 1
            self.save(update_fields=['likes'])
    
    @property
    def reading_time(self):
        """估算阅读时间（分钟）"""
        word_count = len(self.content.split())
        return max(1, word_count // 200)  # 假设每分钟阅读200个单词
    
    @property
    def is_published(self):
        """是否已发布"""
        return self.status == 'published' and self.published_at is not None


class Comment(models.Model):
    """评论模型"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name='文章')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='作者')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='父评论')
    content = models.TextField(verbose_name='评论内容')
    is_approved = models.BooleanField(default=True, verbose_name='是否审核通过')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        db_table = 'articles_comment'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.author.username} 评论了 {self.article.title}"
    
    def save(self, *args, **kwargs):
        """保存时更新文章评论数"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.article.comments_count += 1
            self.article.save(update_fields=['comments_count'])
    
    def delete(self, *args, **kwargs):
        """删除时更新文章评论数"""
        self.article.comments_count = max(0, self.article.comments_count - 1)
        self.article.save(update_fields=['comments_count'])
        super().delete(*args, **kwargs)
    
    @property
    def is_reply(self):
        """是否为回复"""
        return self.parent is not None


class Like(models.Model):
    """点赞模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes', verbose_name='用户')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='article_likes', verbose_name='文章')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '点赞'
        verbose_name_plural = '点赞'
        db_table = 'articles_like'
        unique_together = ['user', 'article']
    
    def __str__(self):
        return f"{self.user.username} 点赞了 {self.article.title}"
    
    def save(self, *args, **kwargs):
        """保存时更新文章点赞数"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.article.increase_likes()
    
    def delete(self, *args, **kwargs):
        """删除时更新文章点赞数"""
        self.article.decrease_likes()
        super().delete(*args, **kwargs)


class Bookmark(models.Model):
    """收藏模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bookmarks', verbose_name='用户')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='article_bookmarks', verbose_name='文章')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        db_table = 'articles_bookmark'
        unique_together = ['user', 'article']
    
    def __str__(self):
        return f"{self.user.username} 收藏了 {self.article.title}"
