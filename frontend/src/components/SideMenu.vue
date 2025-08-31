<template>
  <div class="sidebar bg-light border-end" style="width: 250px; min-height: calc(100vh - 56px);">
    <div class="p-3">
      <h6 class="text-muted mb-3">导航菜单</h6>
      
      <!-- 主页 -->
      <div class="mb-4">
        <nav class="nav flex-column">
          <router-link class="nav-link" to="/" :class="{ active: $route.path === '/' }">
            <el-icon class="me-2"><House /></el-icon>首页
          </router-link>
        </nav>
      </div>

      <!-- 博客模块 -->
      <div class="mb-4">
        <h6 class="sidebar-heading text-muted">📝 博客管理</h6>
        <nav class="nav flex-column">
          <router-link class="nav-link" to="/articles" :class="{ active: $route.path === '/articles' }">
            <el-icon class="me-2"><Document /></el-icon>文章列表
          </router-link>
          <router-link class="nav-link" to="/articles/create" :class="{ active: $route.path === '/articles/create' }" v-if="authStore.isAuthenticated">
            <el-icon class="me-2"><Edit /></el-icon>写文章
          </router-link>
          <router-link class="nav-link" to="/categories" :class="{ active: $route.path === '/categories' }">
            <el-icon class="me-2"><Folder /></el-icon>分类管理
          </router-link>
        </nav>
      </div>

      <!-- 英语学习模块 -->
      <div class="mb-4">
        <h6 class="sidebar-heading text-muted">📚 英语学习</h6>
        <nav class="nav flex-column">
          <router-link class="nav-link" to="/english/dashboard" :class="{ active: $route.path === '/english/dashboard' }">
            <el-icon class="me-2"><DataBoard /></el-icon>学习仪表板
          </router-link>
          <router-link class="nav-link" to="/english/typing-practice" :class="{ active: $route.path === '/english/typing-practice' }">
            <el-icon class="me-2"><Trophy /></el-icon>智能练习
          </router-link>
          <router-link class="nav-link" to="/english/pronunciation" :class="{ active: $route.path === '/english/pronunciation' }">
            <el-icon class="me-2"><Microphone /></el-icon>发音练习
          </router-link>
          <router-link class="nav-link" to="/english/words" :class="{ active: $route.path.startsWith('/english/words') }">
            <el-icon class="me-2"><Notebook /></el-icon>单词学习
          </router-link>
          <router-link class="nav-link" to="/english/expressions" :class="{ active: $route.path.startsWith('/english/expressions') }">
            <el-icon class="me-2"><ChatDotRound /></el-icon>地道表达
          </router-link>
          <router-link class="nav-link" to="/english/news-dashboard" :class="{ active: $route.path.startsWith('/english/news') }" @click="handleNewsClick">
            <el-icon class="me-2"><Notification /></el-icon>英语新闻
          </router-link>
          <router-link class="nav-link" to="/english/api-integration" :class="{ active: $route.path === '/english/api-integration' }">
            <el-icon class="me-2"><Connection /></el-icon>API集成
          </router-link>
          <router-link class="nav-link" to="/english/ai-config" :class="{ active: $route.path === '/english/ai-config' }">
            <el-icon class="me-2"><Setting /></el-icon>AI配置管理
          </router-link>
        </nav>
      </div>

      <!-- 文章分类 -->
      <div class="mb-4" v-if="categories.length > 0">
        <h6 class="sidebar-heading text-muted">📂 文章分类</h6>
        <nav class="nav flex-column">
          <router-link class="nav-link sub-item" :to="`/articles?category=${category.id}`" v-for="category in categories" :key="category.id">
            <el-icon class="me-2"><Folder /></el-icon>{{ category.name }}
            <span class="badge bg-secondary ms-auto">{{ category.article_count }}</span>
          </router-link>
        </nav>
      </div>

      <!-- 用户功能 -->
      <div class="mb-4" v-if="authStore.isAuthenticated">
        <h6 class="sidebar-heading text-muted">👤 个人中心</h6>
        <nav class="nav flex-column">
          <router-link class="nav-link" to="/user/profile" :class="{ active: $route.path === '/user/profile' }">
            <el-icon class="me-2"><User /></el-icon>个人资料
          </router-link>
          <router-link class="nav-link" to="/user/articles" :class="{ active: $route.path === '/user/articles' }">
            <el-icon class="me-2"><DocumentCopy /></el-icon>我的文章
          </router-link>
        </nav>
      </div>

      <!-- 系统信息 -->
      <div class="mt-auto pt-4 border-top">
        <small class="text-muted">
          <div>注册用户: {{ stats.total_users || 0 }}</div>
          <div>文章总数: {{ stats.total_articles || 0 }}</div>
        </small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { categoriesAPI } from '@/api/categories'
import { homeAPI } from '@/api/home'
import { House, Document, Edit, Folder, User, DocumentCopy, DataBoard, Trophy, Notebook, ChatDotRound, Notification, Microphone, Connection, Setting } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const categories = ref([])
const stats = ref({
  total_articles: 0,
  total_users: 0
})

// 处理英语新闻点击
const handleNewsClick = () => {
  console.log('英语新闻链接被点击')
  console.log('当前路由:', window.location.pathname)
  console.log('目标路由: /english/news-dashboard')
}

// 获取分类数据（兼容多种返回结构）
const fetchCategories = async () => {
  try {
    const res = await categoriesAPI.getCategories()
    console.log('分类数据:', res)
    const list = Array.isArray(res)
      ? res
      : (Array.isArray(res?.results)
        ? res.results
        : (Array.isArray(res?.data)
          ? res.data
          : []))
    categories.value = list.filter(cat => (cat?.status ?? 'active') === 'active')
    console.log('过滤后的分类:', categories.value.length)
  } catch (error) {
    console.error('获取分类数据失败:', error)
    categories.value = []
  }
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const data = await homeAPI.getStats()
    stats.value = data
    console.log('侧边栏统计数据:', stats.value)
  } catch (error) {
    console.error('获取统计数据失败:', error)
    stats.value = {
      total_articles: 0,
      total_users: 0
    }
  }
}

onMounted(() => {
  fetchCategories()
  fetchStats()
})
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 64px;
  left: 0;
  height: calc(100vh - 64px);
  overflow-y: auto;
  z-index: 100;
}

.sidebar-heading {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.nav-link {
  color: #6c757d;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  margin-bottom: 0.25rem;
  transition: all 0.15s ease-in-out;
}

.nav-link:hover {
  color: #0d6efd;
  background-color: #e7f1ff;
}

.nav-link.active {
  color: #0d6efd;
  background-color: #e7f1ff;
  font-weight: 600;
}

.badge {
  font-size: 0.7rem;
}

.sub-item {
  font-size: 0.85rem;
  padding-left: 1rem;
  color: #8c959f !important;
}

.sub-item:hover {
  color: #0d6efd !important;
  background-color: #f8f9fa;
}

.sidebar-heading {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
</style>