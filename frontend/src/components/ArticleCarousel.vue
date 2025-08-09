<template>
  <div class="article-carousel">
    <div v-if="loading" class="carousel-loading">
      <el-skeleton animated>
        <template #template>
          <div style="height: 300px; background: #f5f5f5; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
            <el-skeleton-item variant="text" style="width: 200px; height: 30px;" />
          </div>
        </template>
      </el-skeleton>
    </div>
    
    <div v-else-if="articles.length === 0" class="no-articles">
      <div class="empty-state">
        <el-icon style="font-size: 3rem; color: #c0c4cc;"><Document /></el-icon>
        <p class="mt-3 text-muted">暂无热门文章</p>
        <p class="debug-info">调试: loading={{ loading }}, articles.length={{ articles.length }}</p>
        <button @click="fetchPopularArticles" class="retry-btn">重新加载</button>
      </div>
    </div>
    
    <div v-else class="carousel-wrapper">
      <!-- 自定义轮播组件 -->
      <div class="custom-carousel">
        <div class="carousel-container">
          <div 
            v-for="(article, index) in articles" 
            :key="article.id"
            class="carousel-slide"
            :class="{ active: currentSlide === index }"
            @click="goToArticle(article.id)"
          >
            <div 
              class="carousel-content"
              :style="{ 
                background: getArticleImage(article),
                minHeight: '220px',
                height: '220px',
                width: '100%',
                display: 'block'
              }"
            >
              <div class="carousel-overlay">
                <div class="carousel-info">
                  <span class="category-badge">{{ article.category?.name || '未分类' }}</span>
                  <h3 class="article-title">{{ article.title }}</h3>
                  <p class="article-summary">{{ article.summary || (article.content && article.content.substring(0, 80) + '...') || '暂无摘要' }}</p>
                  <div class="article-meta">
                    <span class="author">
                      <el-icon><User /></el-icon>
                      {{ article.author?.first_name || article.author?.username }}
                    </span>
                    <span class="views">
                      <el-icon><View /></el-icon>
                      {{ article.views || 0 }}
                    </span>
                    <span class="date">
                      <el-icon><Clock /></el-icon>
                      {{ formatDate(article.created_at) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 导航按钮 -->
        <button class="carousel-btn prev-btn" @click="prevSlide" v-if="articles.length > 1">
          <el-icon><ArrowLeft /></el-icon>
        </button>
        <button class="carousel-btn next-btn" @click="nextSlide" v-if="articles.length > 1">
          <el-icon><ArrowRight /></el-icon>
        </button>
        
        <!-- 指示器 -->
        <div class="carousel-indicators" v-if="articles.length > 1">
          <button 
            v-for="(article, index) in articles" 
            :key="index"
            class="indicator"
            :class="{ active: currentSlide === index }"
            @click="goToSlide(index)"
          ></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { homeAPI } from '@/api/home'
import { User, View, Clock, Document, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()
const articles = ref([])
const loading = ref(true)
const currentSlide = ref(0)
let autoPlayTimer = null

const getArticleImage = (article) => {
  // 如果文章有封面图，使用封面图
  if (article.cover_image) {
    return article.cover_image
  }
  
  // 使用渐变背景，避免外部图片加载问题
  const gradients = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
  ]
  
  return gradients[article.id % gradients.length]
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

const goToArticle = (id) => {
  router.push(`/articles/${id}`)
}

// 轮播控制函数
const nextSlide = () => {
  currentSlide.value = (currentSlide.value + 1) % articles.value.length
}

const prevSlide = () => {
  currentSlide.value = currentSlide.value === 0 ? articles.value.length - 1 : currentSlide.value - 1
}

const goToSlide = (index) => {
  currentSlide.value = index
}

// 自动播放
const startAutoPlay = () => {
  if (articles.value.length > 1) {
    autoPlayTimer = setInterval(nextSlide, 5000)
  }
}

const stopAutoPlay = () => {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer)
    autoPlayTimer = null
  }
}

const fetchPopularArticles = async () => {
  try {
    loading.value = true
    console.log('🚀 轮播组件：开始获取热门文章...')
    
    // 直接使用axios，绕过可能的封装问题
    const axios = (await import('axios')).default
    
    const response = await axios.get('http://127.0.0.1:8000/api/v1/articles/', {
      params: {
        page_size: 5,
        ordering: '-views'
      }
    })
    
    console.log('📦 轮播组件：原始响应:', response.status)
    console.log('📊 轮播组件：响应数据:', response.data)
    
    if (response.data && response.data.results) {
      // 只选择已发布的文章
      const publishedArticles = response.data.results.filter(article => 
        article.status === 'published'
      )
      
      articles.value = publishedArticles
      console.log('✅ 轮播组件：设置文章数量:', articles.value.length)
      
      if (articles.value.length > 0) {
        console.log('🎯 轮播组件：第一篇文章:', articles.value[0].title)
        console.log('🖼️ 轮播组件：第一篇文章背景:', getArticleImage(articles.value[0]))
        console.log('📋 轮播组件：文章数据:', articles.value[0])
        // 启动自动播放
        startAutoPlay()
      }
    } else {
      console.warn('⚠️ 轮播组件：响应格式不正确')
      articles.value = []
    }
    
  } catch (error) {
    console.error('❌ 轮播组件：获取热门文章失败:', error)
    articles.value = []
  } finally {
    loading.value = false
    console.log('🏁 轮播组件：加载完成')
  }
}

onMounted(() => {
  fetchPopularArticles()
})

onUnmounted(() => {
  stopAutoPlay()
})
</script>

<style scoped>
.article-carousel {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.debug-info {
  background: #f0f0f0;
  padding: 5px 10px;
  margin: 5px 0;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

.articles-debug {
  background: #e8f5e8;
  padding: 10px;
  margin: 10px 0;
  border-radius: 4px;
  border: 1px solid #4CAF50;
}

.debug-article {
  margin: 2px 0;
  font-size: 12px;
  color: #2e7d32;
}

.retry-btn {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.retry-btn:hover {
  background: #337ab7;
}

.carousel-wrapper {
  width: 100%;
}

.main-carousel {
  width: 100%;
  height: 300px !important;
}

.main-carousel .el-carousel__container {
  height: 300px !important;
}

.main-carousel .el-carousel__item {
  height: 300px !important;
}

/* 自定义轮播样式 */
.custom-carousel {
  position: relative;
  width: 100%;
  height: 220px;
  overflow: hidden;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.carousel-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.carousel-slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 0.5s ease-in-out;
}

.carousel-slide.active {
  opacity: 1;
}

.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10;
  font-size: 14px;
}

.carousel-btn:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-50%) scale(1.1);
}

.prev-btn {
  left: 12px;
}

.next-btn {
  right: 12px;
}

.carousel-indicators {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
  z-index: 10;
}

.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s ease;
}

.indicator.active {
  background: rgba(255, 255, 255, 0.9);
  transform: scale(1.3);
}

.carousel-item {
  cursor: pointer;
}

.carousel-content {
  position: relative;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  transition: transform 0.3s ease;
}

.carousel-content:hover {
  transform: scale(1.02);
}

.carousel-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    180deg,
    rgba(0, 0, 0, 0.1) 0%,
    rgba(0, 0, 0, 0.4) 60%,
    rgba(0, 0, 0, 0.8) 100%
  );
  display: flex;
  align-items: flex-end;
  padding: 1.5rem;
}

.carousel-info {
  color: white;
  max-width: 75%;
  line-height: 1.4;
}

.category-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  color: white;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
  margin-bottom: 0.4rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.article-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.4rem 0;
  line-height: 1.3;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-summary {
  font-size: 0.85rem;
  margin: 0 0 0.6rem 0;
  opacity: 0.9;
  line-height: 1.4;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  opacity: 0.85;
  flex-wrap: wrap;
}

.article-meta span {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.article-meta .el-icon {
  font-size: 0.9rem;
}

:deep(.el-carousel__container) {
  border-radius: 12px;
}

:deep(.el-carousel__indicator) {
  background-color: rgba(255, 255, 255, 0.4);
  border-radius: 3px;
}

:deep(.el-carousel__indicator.is-active) {
  background-color: rgba(255, 255, 255, 0.8);
}

:deep(.el-carousel__arrow) {
  background-color: rgba(0, 0, 0, 0.5);
  border: none;
  color: white;
}

:deep(.el-carousel__arrow:hover) {
  background-color: rgba(0, 0, 0, 0.7);
}

.carousel-loading,
.no-articles {
  height: 300px;
  border-radius: 12px;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 12px;
  border: 2px dashed #dee2e6;
}

.empty-state p {
  margin: 0;
  font-size: 1rem;
}

@media (max-width: 768px) {
  .carousel-overlay {
    padding: 1rem;
  }
  
  .carousel-info {
    max-width: 90%;
  }
  
  .article-title {
    font-size: 1.2rem;
  }
  
  .article-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
