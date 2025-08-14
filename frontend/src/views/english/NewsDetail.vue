<template>
  <div class="page-container" v-loading="loading">
    <el-page-header @back="goBack" content="新闻详情" />
    
    <article class="news-article">
      <!-- 新闻标题 -->
      <header class="article-header">
        <h1 class="article-title">{{ news?.title }}</h1>
        <div class="article-meta">
          <span class="meta-item">
            <el-icon><Calendar /></el-icon>
            {{ formatDate(news?.publish_date) }}
          </span>
          <span class="meta-item">
            <el-icon><Document /></el-icon>
            {{ news?.source }}
          </span>
          <span class="meta-item">
            <el-icon><Reading /></el-icon>
            {{ news?.word_count }} 词
          </span>
          <span class="meta-item" v-if="news?.difficulty_level">
            <el-tag :type="getDifficultyType(news?.difficulty_level)" size="small">
              {{ getDifficultyLabel(news?.difficulty_level) }}
            </el-tag>
          </span>
        </div>
      </header>
      
      <!-- 新闻图片 -->
      <div v-if="news?.image_url" class="article-image">
        <el-image 
          :src="getImageUrl(news.image_url)" 
          :alt="news.image_alt"
          fit="cover"
          :preview-src-list="[getImageUrl(news.image_url)]"
          :preview-teleported="true"
        />
        <div class="image-caption" v-if="news?.image_alt">{{ news?.image_alt }}</div>
      </div>
      
      <!-- 新闻内容 -->
      <div class="article-content">
        <div class="content-text" v-html="news?.content"></div>
      </div>
    </article>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { englishAPI } from '@/api/english'
import { Calendar, Document, Reading } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const news = ref(null)

const fetchDetail = async () => {
  loading.value = true
  try {
    const id = route.params.id
    const resp = await englishAPI.getNews(id)
    news.value = resp?.data || resp
  } finally {
    loading.value = false
  }
}

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
  
  // 其他情况，尝试作为相对路径处理
  return imageUrl
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 获取难度标签类型
const getDifficultyType = (difficulty) => {
  const types = {
    'beginner': 'success',
    'intermediate': 'warning',
    'advanced': 'danger'
  }
  return types[difficulty] || 'info'
}

// 获取难度标签文本
const getDifficultyLabel = (difficulty) => {
  const labels = {
    'beginner': '初级',
    'intermediate': '中级',
    'advanced': '高级'
  }
  return labels[difficulty] || difficulty
}

const goBack = () => router.back()

onMounted(fetchDetail)
</script>

<style scoped>
.page-container { 
  padding: 24px; 
  max-width: 1100px; 
  margin: 0 auto;
  background: #fff;
}

/* 新闻文章样式 */
.news-article {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

/* 文章头部 */
.article-header {
  padding: 24px 0;
  border-bottom: 1px solid #e9ecef;
  margin-bottom: 24px;
}

.article-title {
  font-size: 1.875rem;
  font-weight: 700;
  line-height: 1.3;
  color: #1a202c;
  margin: 0 0 16px 0;
  word-break: break-word;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
  color: #6b7280;
  font-size: 14px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-item .el-icon {
  font-size: 16px;
}

/* 文章图片 */
.article-image {
  margin: 24px auto;
  text-align: center;
  max-width: 860px; /* 与正文列宽保持一致 */
}

.article-image .el-image {
  width: 100%;
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.article-image .el-image:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.image-caption {
  margin-top: 8px;
  font-size: 13px;
  color: #6b7280;
  font-style: italic;
  text-align: center;
}

/* 文章内容 */
.article-content {
  margin-top: 24px;
}

.content-text {
  font-size: 17px;
  line-height: 1.9;
  color: #374151;
  max-width: 860px;
  margin: 0 auto;
}

.content-text :deep(p) {
  margin-bottom: 16px;
  text-align: justify;
}

.content-text :deep(p:first-child) {
  font-size: 17px;
  font-weight: 500;
  color: #1f2937;
}

.content-text :deep(p:last-child) {
  margin-bottom: 0;
}

.content-text :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  margin: 20px auto;
  display: block;
}

.content-text :deep(a) {
  color: #3b82f6;
  text-decoration: none;
}

.content-text :deep(a:hover) {
  text-decoration: underline;
}

.content-text :deep(strong) {
  font-weight: 600;
  color: #1f2937;
}

.content-text :deep(em) {
  font-style: italic;
}

.content-text :deep(blockquote) {
  border-left: 4px solid #e5e7eb;
  padding-left: 16px;
  margin: 20px 0;
  color: #6b7280;
  font-style: italic;
}

.content-text :deep(ul),
.content-text :deep(ol) {
  margin: 16px 0;
  padding-left: 24px;
}

.content-text :deep(li) {
  margin-bottom: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
  
  .article-header {
    padding: 20px 0;
  }
  
  .article-title {
    font-size: 1.5rem;
  }
  
  .article-meta {
    gap: 12px;
  }
  
  .meta-item {
    font-size: 13px;
  }
  
  .content-text {
    font-size: 15px;
  }
  
  .content-text :deep(p:first-child) {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 12px;
  }
  
  .article-title {
    font-size: 1.375rem;
  }
  
  .article-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .content-text {
    font-size: 14px;
    line-height: 1.7;
  }
}
</style>


