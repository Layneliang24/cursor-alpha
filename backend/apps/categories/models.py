from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    """分类模型"""
    STATUS_CHOICES = (
        ('active', '激活'),
        ('inactive', '未激活'),
    )
    
    name = models.CharField(max_length=100, verbose_name='分类名称')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='分类别名')
    description = models.TextField(blank=True, verbose_name='分类描述')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='父分类')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    order = models.IntegerField(default=0, verbose_name='排序')
    icon = models.CharField(max_length=50, blank=True, verbose_name='图标')
    color = models.CharField(max_length=7, default='#409EFF', verbose_name='颜色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        app_label = 'categories'
        verbose_name = '分类'
        verbose_name_plural = '分类'
        db_table = 'categories_category'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """保存时自动生成slug"""
        if not self.slug:
            # 允许中文 slug
            slug_val = slugify(self.name, allow_unicode=True)
            if not slug_val:
                # 如果仍为空（全部非字母数字），使用随机 uuid 片段确保唯一
                import uuid
                slug_val = uuid.uuid4().hex[:8]
            
            # 检查slug是否已存在，如果存在则添加数字后缀
            original_slug = slug_val
            counter = 1
            while Category.objects.filter(slug=slug_val).exclude(pk=self.pk).exists():
                slug_val = f"{original_slug}-{counter}"
                counter += 1
            
            self.slug = slug_val
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """获取分类详情URL"""
        return reverse('category_detail', kwargs={'slug': self.slug})
    
    @property
    def article_count(self):
        """获取分类下的文章数量"""
        return self.articles.filter(status='published').count()
    
    @property
    def is_root(self):
        """是否为根分类"""
        return self.parent is None
    
    @property
    def level(self):
        """获取分类层级"""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level
    
    def get_children(self):
        """获取子分类"""
        return self.children.filter(status='active').order_by('order', 'name')
    
    def get_ancestors(self):
        """获取所有祖先分类"""
        ancestors = []
        parent = self.parent
        while parent:
            ancestors.append(parent)
            parent = parent.parent
        return list(reversed(ancestors))
    
    def get_descendants(self):
        """获取所有后代分类"""
        descendants = []
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants


class Tag(models.Model):
    """标签模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名称')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='标签别名')
    description = models.TextField(blank=True, verbose_name='标签描述')
    color = models.CharField(max_length=7, default='#67C23A', verbose_name='颜色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        app_label = 'categories'
        verbose_name = '标签'
        verbose_name_plural = '标签'
        db_table = 'categories_tag'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """保存时自动生成slug"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def article_count(self):
        """获取标签下的文章数量"""
        return self.articles.filter(status='published').count()
