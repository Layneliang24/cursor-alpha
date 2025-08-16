<template>
  <nav class="modern-navbar">
    <div class="container-fluid px-4">
      <!-- Logo -->
      <router-link to="/" class="navbar-brand">
        <div class="logo-container">
          <div class="logo-icon">
            <el-icon><Star /></el-icon>
          </div>
          <span class="logo-text">Alpha</span>
        </div>
      </router-link>

      <!-- 主导航菜单 -->
      <nav class="main-nav">
        <router-link to="/" class="nav-item">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </router-link>
        <!-- 博客模块 -->
        <div class="nav-dropdown" :class="{ active: blogDropdownOpen }" @mouseenter="blogDropdownOpen = true" @mouseleave="blogDropdownOpen = false">
          <div class="nav-item dropdown-trigger" @click="toggleBlogDropdown">
            <el-icon><Document /></el-icon>
            <span>博客</span>
            <el-icon class="dropdown-arrow" :class="{ rotated: blogDropdownOpen }"><ArrowDown /></el-icon>
          </div>
          <div class="dropdown-menu" :class="{ show: blogDropdownOpen }">
            <router-link to="/articles" class="dropdown-item" @click="closeBlogDropdown">
              <el-icon><Document /></el-icon>
              <span>文章列表</span>
            </router-link>
            <router-link to="/categories" class="dropdown-item" @click="closeBlogDropdown">
              <el-icon><Folder /></el-icon>
              <span>分类管理</span>
            </router-link>
            <router-link to="/user/articles" class="dropdown-item" @click="closeBlogDropdown" v-if="authStore.isAuthenticated">
              <el-icon><Edit /></el-icon>
              <span>我的文章</span>
            </router-link>
          </div>
        </div>

        <!-- 英语学习模块 -->
        <div class="nav-dropdown" :class="{ active: englishDropdownOpen }" @mouseenter="englishDropdownOpen = true" @mouseleave="englishDropdownOpen = false">
          <div class="nav-item dropdown-trigger" @click="toggleEnglishDropdown">
            <el-icon><Reading /></el-icon>
            <span>英语学习</span>
            <el-icon class="dropdown-arrow" :class="{ rotated: englishDropdownOpen }"><ArrowDown /></el-icon>
          </div>
          <div class="dropdown-menu" :class="{ show: englishDropdownOpen }">
            <router-link to="/english/dashboard" class="dropdown-item" @click="closeEnglishDropdown">
              <el-icon><DataBoard /></el-icon>
              <span>学习仪表板</span>
            </router-link>
            <router-link to="/english/practice" class="dropdown-item" @click="closeEnglishDropdown">
              <el-icon><Trophy /></el-icon>
              <span>智能练习</span>
            </router-link>
            <router-link to="/english/pronunciation" class="dropdown-item" @click="closeEnglishDropdown">
              <el-icon><Microphone /></el-icon>
              <span>发音练习</span>
            </router-link>
            <router-link to="/english/words" class="dropdown-item" @click="closeEnglishDropdown">
              <el-icon><Notebook /></el-icon>
              <span>单词学习</span>
            </router-link>
            <router-link to="/english/news-dashboard" class="dropdown-item" @click="closeEnglishDropdown">
              <el-icon><Notification /></el-icon>
              <span>英语新闻</span>
            </router-link>
            <router-link to="/english/expressions" class="dropdown-item" @click="closeEnglishDropdown">
              <el-icon><ChatDotRound /></el-icon>
              <span>地道表达</span>
            </router-link>
            <router-link to="/english/api-integration" class="dropdown-item" @click="closeEnglishDropdown">
              <el-icon><Connection /></el-icon>
              <span>API集成</span>
            </router-link>
          </div>
        </div>
        <a
          v-if="isAdminUi"
          href="/admin/"
          class="nav-item"
          target="_blank"
          rel="noopener noreferrer"
          title="Django 后台（管理员可用）"
        >
          <el-icon><Setting /></el-icon>
          <span>后台</span>
        </a>
        <router-link to="/trending" class="nav-item">
          <el-icon><TrendCharts /></el-icon>
          <span>热门</span>
        </router-link>
      </nav>

      <!-- 搜索框 -->
      <div class="search-container">
        <div class="search-box">
          <el-icon class="search-icon"><Search /></el-icon>
          <input 
            type="text" 
            class="search-input" 
            placeholder="搜索文章、用户、标签..."
            v-model="searchQuery"
            @keyup.enter="handleSearch"
            @focus="searchFocused = true"
            @blur="searchFocused = false"
          >
          <button class="search-btn" @click="handleSearch" v-if="searchQuery">
            <el-icon><Right /></el-icon>
          </button>
        </div>
      </div>

      <!-- 用户菜单 -->
      <div class="user-menu">
        <div class="nav-actions" v-if="authStore.isAuthenticated">
          <router-link to="/articles/create" class="action-btn" title="写文章">
            <el-icon><Edit /></el-icon>
          </router-link>
          <router-link v-if="isAdminUi" to="/admin/categories" class="action-btn" title="分类管理">
            <el-icon><Folder /></el-icon>
          </router-link>
          <button class="action-btn" title="通知" @click="showNotifications">
            <el-icon><Bell /></el-icon>
            <span class="notification-badge">3</span>
          </button>
          
          <div class="user-dropdown">
            <button class="user-avatar" data-bs-toggle="dropdown">
              <img :src="userAvatar" alt="头像">
              <span class="user-name">{{ authStore.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </button>
            <ul class="dropdown-menu dropdown-menu-end user-menu-dropdown">
              <li class="dropdown-header">
                <div class="user-info">
                  <img :src="userAvatar" class="user-avatar-large" alt="头像">
                  <div>
                    <div class="user-name-large">{{ authStore.user?.username }}</div>
                    <div class="user-email">{{ authStore.user?.email }}</div>
                  </div>
                </div>
              </li>
              <li><hr class="dropdown-divider"></li>
              <li><router-link class="dropdown-item" to="/user/profile"><el-icon class="me-2"><User /></el-icon>个人资料</router-link></li>
              <li><router-link class="dropdown-item" to="/user/articles"><el-icon class="me-2"><Document /></el-icon>我的文章</router-link></li>
              <li v-if="isAdminUi">
                <router-link class="dropdown-item" to="/admin/categories">
                  <el-icon class="me-2"><Folder /></el-icon>分类管理
                </router-link>
              </li>
              <li><a class="dropdown-item" href="#"><el-icon class="me-2"><Setting /></el-icon>设置</a></li>
              <li><hr class="dropdown-divider"></li>
              <li><a class="dropdown-item text-danger" href="#" @click="handleLogout"><el-icon class="me-2"><SwitchButton /></el-icon>退出登录</a></li>
            </ul>
          </div>
        </div>
        
        <div class="auth-buttons" v-else>
          <router-link class="btn-login" to="/login">登录</router-link>
          <router-link class="btn-register" to="/register">注册</router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Star, Search, Edit, Bell, ArrowDown, User, Document, Setting, SwitchButton, Right, House, Folder, TrendCharts, DataBoard, Reading, Trophy, Notebook, Notification, ChatDotRound, Microphone, Connection } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const searchQuery = ref('')
const searchFocused = ref(false)
const blogDropdownOpen = ref(false)
const englishDropdownOpen = ref(false)

const userAvatar = computed(() => {
  return authStore.user?.avatar || 'https://ui-avatars.com/api/?name=' + (authStore.user?.username || 'User') + '&background=667eea&color=fff&size=32'
})

// 是否显示管理员界面元素：is_staff / is_superuser / 属于“管理员”组
const isAdminUi = computed(() => {
  const user = authStore.user
  if (!user) return false
  if (user.is_staff || user.is_superuser) return true
  if (Array.isArray(user.groups) && user.groups.includes('管理员')) return true
  return false
})

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/search', query: { q: searchQuery.value } })
  }
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

// 下拉菜单控制方法
const toggleBlogDropdown = () => {
  blogDropdownOpen.value = !blogDropdownOpen.value
  if (blogDropdownOpen.value) {
    englishDropdownOpen.value = false
  }
}

const toggleEnglishDropdown = () => {
  englishDropdownOpen.value = !englishDropdownOpen.value
  if (englishDropdownOpen.value) {
    blogDropdownOpen.value = false
  }
}

const closeBlogDropdown = () => {
  blogDropdownOpen.value = false
}

const closeEnglishDropdown = () => {
  englishDropdownOpen.value = false
}

// 点击外部关闭下拉菜单
const closeAllDropdowns = () => {
  blogDropdownOpen.value = false
  englishDropdownOpen.value = false
}

const showNotifications = () => {
  // 显示通知列表
  console.log('显示通知')
}

// 全局点击事件处理
const handleGlobalClick = (event) => {
  const target = event.target
  // 如果点击的不是下拉菜单相关元素，则关闭所有下拉菜单
  if (!target.closest('.nav-dropdown')) {
    closeAllDropdowns()
  }
}

// 组件挂载和卸载时的事件监听
onMounted(() => {
  document.addEventListener('click', handleGlobalClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleGlobalClick)
})
</script>

<style scoped>
.modern-navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 64px;
}

.container-fluid {
  display: flex;
  align-items: center;
  width: 100%;
  height: 100%;
  padding: 0 1.5rem;
}

.navbar-brand {
  text-decoration: none;
  color: white;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  color: white;
}

.logo-text {
  font-size: 1.6rem;
  font-weight: 700;
  color: white;
}

.main-nav {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-left: 3rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  transform: translateY(-1px);
}

.nav-item.router-link-active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.search-container {
  max-width: 400px;
  margin-left: auto;
  margin-right: 2rem;
}

.search-box {
  position: relative;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  padding: 0.6rem 1.2rem;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.search-box:focus-within {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.search-icon {
  color: rgba(255, 255, 255, 0.7);
  margin-right: 0.75rem;
  font-size: 1.1rem;
}

.search-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: white;
  font-size: 0.95rem;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.search-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  padding: 0.25rem;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.search-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.user-menu {
  display: flex;
  align-items: center;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.action-btn {
  position: relative;
  width: 42px;
  height: 42px;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1.1rem;
  transition: all 0.2s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff4757;
  color: white;
  font-size: 0.7rem;
  padding: 0.15rem 0.4rem;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.user-dropdown {
  position: relative;
  z-index: 1001;
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 22px;
  padding: 0.5rem 1rem;
  color: white;
  transition: all 0.2s ease;
  cursor: pointer;
}

.user-avatar:hover {
  background: rgba(255, 255, 255, 0.25);
}

.user-avatar img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  font-weight: 500;
  font-size: 0.9rem;
}

.user-menu-dropdown {
  min-width: 280px;
  border: none;
  border-radius: 15px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  padding: 0;
  margin-top: 0.5rem;
  z-index: 10000 !important;
  position: absolute !important;
}

.dropdown-header {
  padding: 1rem;
  border-bottom: 1px solid #f1f3f4;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar-large {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.user-name-large {
  font-weight: 600;
  font-size: 1rem;
  color: #2c3e50;
}

.user-email {
  font-size: 0.85rem;
  color: #6c757d;
}

.dropdown-item {
  padding: 0.75rem 1rem;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background: #f8f9fa;
}

.auth-buttons {
  display: flex;
  gap: 0.75rem;
}

.btn-login, .btn-register {
  padding: 0.6rem 1.5rem;
  border-radius: 22px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.btn-login {
  color: white;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-login:hover {
  background: rgba(255, 255, 255, 0.25);
  color: white;
  transform: translateY(-1px);
}

.btn-register {
  background: white;
  color: #667eea;
  border: 1px solid white;
}

.btn-register:hover {
  background: #f8f9fa;
  color: #667eea;
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .search-container {
    margin: 0 1rem;
  }
  
  .user-name {
    display: none;
  }
  
  .nav-actions {
  gap: 0.5rem;
}

/* 下拉菜单样式 */
.nav-dropdown {
  position: relative;
}

.dropdown-trigger {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dropdown-arrow {
  font-size: 12px;
  transition: transform 0.3s ease;
}

.dropdown-arrow.rotated,
.nav-dropdown:hover .dropdown-arrow,
.nav-dropdown.active .dropdown-arrow {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 180px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: 1px solid #e4e7ed;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.3s ease;
  z-index: 1000;
  padding: 8px 0;
}

.dropdown-menu.show,
.nav-dropdown:hover .dropdown-menu,
.nav-dropdown.active .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: #606266;
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 14px;
}

.dropdown-item:hover {
  background-color: #f5f7fa;
  color: #409EFF;
  text-decoration: none;
}

.dropdown-item.router-link-active {
  background-color: #ecf5ff;
  color: #409EFF;
  font-weight: 500;
}

.dropdown-item .el-icon {
  font-size: 16px;
}

/* 移动端下拉菜单适配 */
@media (max-width: 768px) {
  .nav-dropdown {
    position: static;
  }
  
  .dropdown-menu {
    position: static;
    opacity: 1;
    visibility: visible;
    transform: none;
    box-shadow: none;
    border: none;
    background: transparent;
    padding: 0;
    margin-left: 20px;
  }
  
  .dropdown-trigger {
    border-bottom: 1px solid #f0f0f0;
    padding-bottom: 8px;
    margin-bottom: 8px;
  }
  
  .dropdown-item {
    padding: 8px 0;
    font-size: 13px;
  }
}
}
</style>