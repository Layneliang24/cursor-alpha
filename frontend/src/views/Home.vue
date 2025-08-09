<template>
  <div class="home">
    <!-- 欢迎横幅 -->
    <div class="hero-section text-white rounded mb-4 p-5">
      <div class="row align-items-center">
        <div class="col-md-8">
          <h1 class="display-5 fw-bold mb-3">欢迎来到Alpha系统</h1>
          <p class="lead mb-4">一个现代化的文章管理和分享平台，让知识传播更简单</p>
          <div class="d-flex gap-3">
            <router-link to="/articles" class="btn btn-light btn-lg">
              <el-icon class="me-2"><Document /></el-icon>浏览文章
            </router-link>
            <router-link to="/articles/create" class="btn btn-outline-light btn-lg" v-if="authStore.isAuthenticated">
              <el-icon class="me-2"><Edit /></el-icon>开始写作
            </router-link>
          </div>
        </div>
        <div class="col-md-4 text-center">
          <el-icon style="font-size: 120px; opacity: 0.3;"><Star /></el-icon>
        </div>
      </div>
    </div>

    <!-- 热门文章轮播 -->
    <div class="mb-5">
      <ArticleCarousel />
    </div>

    <!-- 统计卡片 -->
    <div class="row mb-5 g-4">
      <div class="col-md-3 col-sm-6">
        <div class="card border-0 shadow-sm h-100 stat-card">
          <div class="card-body text-center p-4">
            <div class="text-primary mb-3">
              <el-icon style="font-size: 2.5rem;"><Document /></el-icon>
            </div>
            <h3 class="card-title text-primary mb-2">{{ stats.total_articles || 0 }}</h3>
            <p class="card-text text-muted mb-0">文章总数</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 col-sm-6">
        <div class="card border-0 shadow-sm h-100 stat-card">
          <div class="card-body text-center p-4">
            <div class="text-success mb-3">
              <el-icon style="font-size: 2.5rem;"><User /></el-icon>
            </div>
            <h3 class="card-title text-success mb-2">{{ stats.total_users || 0 }}</h3>
            <p class="card-text text-muted mb-0">注册用户</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 col-sm-6">
        <div class="card border-0 shadow-sm h-100 stat-card">
          <div class="card-body text-center p-4">
            <div class="text-warning mb-3">
              <el-icon style="font-size: 2.5rem;"><View /></el-icon>
            </div>
            <h3 class="card-title text-warning mb-2">{{ stats.total_views || 0 }}</h3>
            <p class="card-text text-muted mb-0">总浏览量</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 col-sm-6">
        <div class="card border-0 shadow-sm h-100 stat-card">
          <div class="card-body text-center p-4">
            <div class="text-info mb-3">
              <el-icon style="font-size: 2.5rem;"><Folder /></el-icon>
            </div>
            <h3 class="card-title text-info mb-2">{{ stats.active_categories || 0 }}</h3>
            <p class="card-text text-muted mb-0">活跃分类</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 最新文章 -->
    <div class="row g-4">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-bottom py-3">
            <h5 class="card-title mb-0">
              <el-icon class="me-2 text-danger"><Promotion /></el-icon>最新文章
            </h5>
          </div>
          <div class="card-body p-0">
            <div class="list-group list-group-flush">
              <div 
                v-for="article in recentArticles" 
                :key="article.id"
                class="list-group-item list-group-item-action border-0 py-3"
              >
                <div class="d-flex w-100 justify-content-between align-items-start">
                  <div class="flex-grow-1">
                    <h6 class="mb-1">
                      <router-link :to="`/articles/${article.id}`" class="text-decoration-none">
                        {{ article.title }}
                      </router-link>
                    </h6>
                    <p class="mb-1 text-muted small">{{ article.summary || (article.content && article.content.substring(0, 100) + '...') || '暂无摘要' }}</p>
                    <small class="text-muted">
                      <el-icon class="me-1"><User /></el-icon>{{ article.author?.first_name || article.author?.username || '未知作者' }}
                      <el-icon class="ms-3 me-1"><Clock /></el-icon>{{ formatDate(article.created_at) }}
                      <el-icon class="ms-3 me-1"><View /></el-icon>{{ article.views || 0 }}
                    </small>
                  </div>
                  <span class="badge bg-primary ms-3">{{ article.category?.name || '未分类' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 热门标签和公告 -->
      <div class="col-lg-4">
        <!-- 热门标签 -->
        <div class="card border-0 shadow-sm mb-4 h-auto">
          <div class="card-header bg-white border-bottom py-3">
            <h6 class="card-title mb-0">
              <el-icon class="me-2 text-warning"><PriceTag /></el-icon>热门标签
            </h6>
          </div>
          <div class="card-body">
            <div class="d-flex flex-wrap gap-2">
              <span 
                v-for="tag in popularTags" 
                :key="tag.name"
                class="badge bg-light text-dark border"
                style="cursor: pointer;"
              >
                {{ tag.name }} ({{ tag.count }})
              </span>
            </div>
          </div>
        </div>

        <!-- 友情链接 -->
        <ExternalLinks />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { homeAPI } from '@/api/home'
import ArticleCarousel from '@/components/ArticleCarousel.vue'
import ExternalLinks from '@/components/ExternalLinks.vue'
import { Document, Edit, Star, User, View, Folder, Promotion, Clock, PriceTag } from '@element-plus/icons-vue'

const authStore = useAuthStore()

// 统计数据
const stats = ref({
  total_articles: 0,
  total_users: 0,
  total_views: 0,
  active_categories: 0
})

// 最新文章
const recentArticles = ref([])

// 热门标签
const popularTags = ref([])

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

// 获取统计数据
const fetchStats = async () => {
  try {
    const data = await homeAPI.getStats()
    stats.value = data
  } catch (error) {
    console.error('获取统计数据失败:', error)
    // 使用默认值
    stats.value = {
      total_articles: 0,
      total_users: 0,
      total_views: 0,
      active_categories: 0
    }
  }
}

// 获取最新文章
const fetchRecentArticles = async () => {
  try {
    const data = await homeAPI.getRecentArticles()
    recentArticles.value = data
  } catch (error) {
    console.error('获取最新文章失败:', error)
    // Fallback to articles API
    try {
      const { articlesAPI } = await import('@/api/articles')
      const response = await articlesAPI.getArticles({ 
        page_size: 6, 
        ordering: '-created_at' 
      })
      recentArticles.value = response.results || []
    } catch (fallbackError) {
      console.error('Fallback获取最新文章也失败:', fallbackError)
      recentArticles.value = []
    }
  }
}

// 获取热门标签
const fetchPopularTags = async () => {
  try {
    const data = await homeAPI.getPopularTags()
    popularTags.value = data
  } catch (error) {
    console.error('获取热门标签失败:', error)
    popularTags.value = []
  }
}

onMounted(() => {
  fetchStats()
  fetchRecentArticles()
  fetchPopularTags()
})
</script>

<style scoped>
.home {
  padding: 0;
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px !important;
}

.stat-card {
  transition: all 0.3s ease;
  border-radius: 12px;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}

.card {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1) !important;
}

.list-group-item {
  padding: 1.25rem !important;
  transition: background-color 0.2s ease;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.card-header {
  border-radius: 12px 12px 0 0 !important;
}

.row.g-4 {
  --bs-gutter-x: 1.5rem;
  --bs-gutter-y: 1.5rem;
}
</style>