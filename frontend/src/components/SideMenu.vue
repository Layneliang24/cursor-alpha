<template>
  <div class="sidebar bg-light border-end" style="width: 250px; min-height: calc(100vh - 56px);">
    <div class="p-3">
      <h6 class="text-muted mb-3">导航菜单</h6>
      
      <!-- 主要功能 -->
      <div class="mb-4">
        <h6 class="sidebar-heading text-muted">主要功能</h6>
        <nav class="nav flex-column">
          <router-link class="nav-link" to="/" :class="{ active: $route.path === '/' }">
            <i class="el-icon-house me-2"></i>首页
          </router-link>
          <router-link class="nav-link" to="/articles" :class="{ active: $route.path === '/articles' }">
            <i class="el-icon-document me-2"></i>文章列表
          </router-link>
          <router-link class="nav-link" to="/articles/create" :class="{ active: $route.path === '/articles/create' }" v-if="authStore.isAuthenticated">
            <i class="el-icon-edit me-2"></i>写文章
          </router-link>
        </nav>
      </div>

      <!-- 分类 -->
      <div class="mb-4">
        <h6 class="sidebar-heading text-muted">文章分类</h6>
        <nav class="nav flex-column">
          <a class="nav-link" href="#" v-for="category in categories" :key="category.id">
            <i class="el-icon-folder me-2"></i>{{ category.name }}
            <span class="badge bg-secondary ms-auto">{{ category.article_count }}</span>
          </a>
        </nav>
      </div>

      <!-- 用户功能 -->
      <div class="mb-4" v-if="authStore.isAuthenticated">
        <h6 class="sidebar-heading text-muted">个人中心</h6>
        <nav class="nav flex-column">
          <router-link class="nav-link" to="/profile" :class="{ active: $route.path === '/profile' }">
            <i class="el-icon-user me-2"></i>个人资料
          </router-link>
          <router-link class="nav-link" to="/user/articles" :class="{ active: $route.path === '/user/articles' }">
            <i class="el-icon-document-copy me-2"></i>我的文章
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
  position: sticky;
  top: 0;
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