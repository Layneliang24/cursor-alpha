# 新闻图片保存功能总结

> 本文档记录新闻图片保存功能的实现和问题分析

## 📁 图片保存位置

### 1. 本地保存目录
新闻图片保存在以下目录：
```
backend/media/news_images/
```

### 2. 目录结构
```
backend/
├── media/
│   ├── news_images/          # 新闻图片目录
│   │   ├── bad09217_d393df5a.jpg
│   │   └── ...
│   └── uploads/              # 其他上传文件
```

### 3. 文件命名规则
图片文件使用以下命名规则：
- 格式：`{title_hash}_{url_hash}.{extension}`
- 示例：`bad09217_d393df5a.jpg`
- 说明：
  - `title_hash`：新闻标题的MD5哈希值前8位
  - `url_hash`：图片URL的MD5哈希值前8位
  - `extension`：原始文件扩展名（.jpg, .png等）

## 🔧 技术实现

### 1. 图片下载功能
位置：`backend/apps/english/fundus_crawler.py`

```python
def _download_and_save_image(self, image_url: str, news_title: str) -> str:
    """下载并保存图片到本地"""
    if not image_url:
        return ""
    
    try:
        # 创建图片保存目录
        image_dir = os.path.join(settings.MEDIA_ROOT, 'news_images')
        os.makedirs(image_dir, exist_ok=True)
        
        # 生成文件名
        title_hash = hashlib.md5(news_title.encode()).hexdigest()[:8]
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
        filename = f"{title_hash}_{url_hash}{file_extension}"
        
        # 下载并保存图片
        response = requests.get(image_url, headers=headers, timeout=10)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return f'news_images/{filename}'
    except Exception as e:
        logger.warning(f"图片下载失败 {image_url}: {str(e)}")
        return ""
```

### 2. 数据库字段
位置：`backend/apps/english/models.py`

```python
class News(models.Model):
    # ... 其他字段
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='图片URL')
    image_alt = models.CharField(max_length=200, blank=True, null=True, verbose_name='图片描述')
```

### 3. 前端访问配置
位置：`frontend/vite.config.js`

```javascript
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true,
    rewrite: (path) => {
      // 如果是媒体文件，去掉/api前缀
      if (path.startsWith('/api/media/')) {
        return path.replace('/api', '')
      }
      return path
    }
  }
}
```

### 4. 前端图片URL处理
位置：`frontend/src/views/english/NewsDetail.vue`

```javascript
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return ''
  
  // 如果是本地保存的图片路径（以news_images/开头）
  if (imageUrl.startsWith('news_images/')) {
    // 使用代理配置，通过/api前缀访问后端
    return `/api/media/${imageUrl}`
  }
  
  // 如果是完整的URL，直接返回
  if (imageUrl.startsWith('http')) {
    return imageUrl
  }
  
  return imageUrl
}
```

## 🚨 当前问题

### 1. 问题描述
用户反映看不到新闻图片，经过分析发现：
- 图片文件确实保存在 `backend/media/news_images/` 目录中
- 但是数据库中大部分新闻的 `image_url` 字段仍然是外部链接
- 只有少数新闻的图片被正确下载到本地

### 2. 问题原因
在 `backend/apps/english/views.py` 的爬取逻辑中：
- 直接保存了 `article.image_url`（外部链接）
- 没有调用 `fundus_crawler.py` 中的 `save_news_to_db` 方法
- 因此图片下载功能没有被触发

### 3. 修复方案
已修改 `backend/apps/english/views.py` 中的爬取逻辑：

```python
# 修改前：直接保存外部链接
news = News.objects.create(
    # ...
    image_url=article.image_url,  # 直接保存外部链接
)

# 修改后：使用save_news_to_db方法处理图片下载
fundus_service = get_fundus_service()
fundus_items = []
for article in articles:
    fundus_item = fundus_service.FundusNewsItem(
        # ...
        image_url=article.image_url,
    )
    fundus_items.append(fundus_item)

# 使用save_news_to_db方法，它会自动处理图片下载
items_saved = fundus_service.save_news_to_db(fundus_items)
```

## 📊 访问路径

### 1. 本地开发环境
- **图片文件路径**：`backend/media/news_images/filename.jpg`
- **HTTP访问路径**：`http://localhost:8000/media/news_images/filename.jpg`
- **前端访问路径**：`/api/media/news_images/filename.jpg`

### 2. 生产环境
- 需要配置Web服务器（如Nginx）来服务media文件
- 或者使用CDN服务

## 🧪 测试验证

### 1. 检查图片文件
```bash
# 检查media目录
dir backend\media\news_images

# 检查图片文件大小
dir backend\media\news_images\*.jpg
```

### 2. 测试HTTP访问
```bash
# 测试图片是否能通过HTTP访问
curl http://localhost:8000/media/news_images/bad09217_d393df5a.jpg
```

### 3. 检查数据库
```sql
-- 查看有图片的新闻
SELECT id, title, image_url FROM english_news WHERE image_url IS NOT NULL AND image_url != '';
```

## 🔄 后续步骤

### 1. 立即修复
- ✅ 已修复 `views.py` 中的爬取逻辑
- ✅ 确保新爬取的新闻图片会被正确下载到本地

### 2. 历史数据修复
- 可以考虑为现有的外部图片URL创建下载任务
- 批量更新数据库中的图片URL

### 3. 监控和优化
- 监控图片下载成功率
- 优化图片文件大小和格式
- 考虑添加图片压缩功能

## 📝 注意事项

1. **文件权限**：确保 `media` 目录有写入权限
2. **磁盘空间**：定期清理不需要的图片文件
3. **网络超时**：图片下载有10秒超时限制
4. **重复处理**：相同图片不会重复下载
5. **错误处理**：下载失败时会保留原始外部链接

---

**文档创建时间**：2025-08-16  
**问题状态**：✅ 已修复  
**测试状态**：🔄 待验证




