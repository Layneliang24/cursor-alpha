<template>
  <div class="sidebar bg-light border-end" style="width: 250px; min-height: calc(100vh - 56px);">
    <div class="p-3">
      <h6 class="text-muted mb-3">导航菜单</h6>
      
      <!-- 主要功能 -->
      <div class="mb-4">
        <h6 class="sidebar-heading text-muted">主要功能</h6>
        <nav class="nav flex-column">
          <router-link class="nav-link" to="/" :class="{ active: $route.path === '/' }">
            <el-icon class="me-2"><House /></el-icon>首页
          </router-link>
          <router-link class="nav-link" to="/articles" :class="{ active: $route.path === '/articles' }">
            <el-icon class="me-2"><Document /></el-icon>文章列表
          </router-link>
          <router-link class="nav-link" to="/articles/create" :class="{ active: $route.path === '/articles/create' }" v-if="authStore.isAuthenticated">
            <el-icon class="me-2"><Edit /></el-icon>写文章
          </router-link>
        </nav>
      </div>

      <!-- 分类 -->
      <div class="mb-4">
        <h6 class="sidebar-heading text-muted">文章分类</h6>
        <nav class="nav flex-column">
          <router-link class="nav-link" :to="`/articles?category=${category.id}`" v-for="category in categories" :key="category.id">
            <el-icon class="me-2"><Folder /></el-icon>{{ category.name }}
            <span class="badge bg-secondary ms-auto">{{ category.article_count }}</span>
          </router-link>
        </nav>
      </div>

      <!-- 用户功能 -->
      <div class="mb-4" v-if="authStore.isAuthenticated">
        <h6 class="sidebar-heading text-muted">个人中心</h6>
        <nav class="nav flex-column">
          <router-link class="nav-link" to="/profile" :class="{ active: $route.path === '/profile' }">
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
          <div>在线用户: {{ onlineUsers }}</div>
          <div>文章总数: {{ totalArticles }}</div>
        </small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { House, Document, Edit, Folder, User, DocumentCopy } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const categories = ref([
  { id: 1, name: '技术分享', article_count: 15 },
  { id: 2, name: '生活随笔', article_count: 8 },
  { id: 3, name: '学习笔记', article_count: 12 },
  { id: 4, name: '项目经验', article_count: 6 }
])
const onlineUsers = ref(23)
const totalArticles = ref(41)

onMounted(() => {
  // 这里可以加载真实的分类数据
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
</style>