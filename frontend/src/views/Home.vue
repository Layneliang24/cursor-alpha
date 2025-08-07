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

    <!-- 统计卡片 -->
    <div class="row mb-5 g-4">
      <div class="col-md-3 col-sm-6">
        <div class="card border-0 shadow-sm h-100 stat-card">
          <div class="card-body text-center p-4">
            <div class="text-primary mb-3">
              <el-icon style="font-size: 2.5rem;"><Document /></el-icon>
            </div>
            <h3 class="card-title text-primary mb-2">{{ stats.totalArticles }}</h3>
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
            <h3 class="card-title text-success mb-2">{{ stats.totalUsers }}</h3>
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
            <h3 class="card-title text-warning mb-2">{{ stats.totalViews }}</h3>
            <p class="card-text text-muted mb-0">总浏览量</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 col-sm-6">
        <div class="card border-0 shadow-sm h-100 stat-card">
          <div class="card-body text-center p-4">
            <div class="text-info mb-3">
              <el-icon style="font-size: 2.5rem;"><ChatDotRound /></el-icon>
            </div>
            <h3 class="card-title text-info mb-2">{{ stats.onlineUsers }}</h3>
            <p class="card-text text-muted mb-0">在线用户</p>
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
                    <p class="mb-1 text-muted small">{{ article.summary }}</p>
                    <small class="text-muted">
                      <el-icon class="me-1"><User /></el-icon>{{ article.author }}
                      <el-icon class="ms-3 me-1"><Clock /></el-icon>{{ formatDate(article.created_at) }}
                      <el-icon class="ms-3 me-1"><View /></el-icon>{{ article.views }}
                    </small>
                  </div>
                  <span class="badge bg-primary ms-3">{{ article.category }}</span>
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

        <!-- 系统公告 -->
        <div class="card border-0 shadow-sm h-auto">
          <div class="card-header bg-white border-bottom py-3">
            <h6 class="card-title mb-0">
              <el-icon class="me-2 text-info"><Bell /></el-icon>系统公告
            </h6>
          </div>
          <div class="card-body">
            <div class="alert alert-info border-0 mb-3">
              <small>
                <strong>系统升级通知：</strong>
                系统将于本周末进行维护升级，届时可能会有短暂的服务中断。
              </small>
            </div>
            <div class="alert alert-success border-0 mb-0">
              <small>
                <strong>新功能上线：</strong>
                现在支持Markdown编辑器，让写作更加便捷！
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Document, Edit, Star, User, View, ChatDotRound, Promotion, Clock, PriceTag, Bell } from '@element-plus/icons-vue'

const authStore = useAuthStore()

// 统计数据
const stats = ref({
  totalArticles: 156,
  totalUsers: 89,
  totalViews: 12543,
  onlineUsers: 23
})

// 最新文章
const recentArticles = ref([
  {
    id: 1,
    title: 'Vue 3 Composition API 深度解析',
    summary: '详细介绍Vue 3中Composition API的使用方法和最佳实践...',
    author: '张三',
    category: '技术分享',
    views: 234,
    created_at: '2024-01-15T10:30:00Z'
  },
  {
    id: 2,
    title: 'Python数据分析入门指南',
    summary: '从零开始学习Python数据分析，包含pandas、numpy等库的使用...',
    author: '李四',
    category: '学习笔记',
    views: 189,
    created_at: '2024-01-14T15:20:00Z'
  },
  {
    id: 3,
    title: '微服务架构设计实践',
    summary: '分享在实际项目中微服务架构的设计经验和踩坑记录...',
    author: '王五',
    category: '项目经验',
    views: 156,
    created_at: '2024-01-13T09:15:00Z'
  }
])

// 热门标签
const popularTags = ref([
  { name: 'Vue.js', count: 45 },
  { name: 'Python', count: 38 },
  { name: 'JavaScript', count: 52 },
  { name: 'React', count: 29 },
  { name: 'Node.js', count: 33 },
  { name: 'Docker', count: 21 }
])

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  // 这里可以加载真实数据
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