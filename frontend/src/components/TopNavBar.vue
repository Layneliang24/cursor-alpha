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
              <li><router-link class="dropdown-item" to="/profile"><el-icon class="me-2"><User /></el-icon>个人资料</router-link></li>
              <li><router-link class="dropdown-item" to="/user/articles"><el-icon class="me-2"><Document /></el-icon>我的文章</router-link></li>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Star, Search, Edit, Bell, ArrowDown, User, Document, Setting, SwitchButton, Right } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const searchQuery = ref('')
const searchFocused = ref(false)

const userAvatar = computed(() => {
  return authStore.user?.avatar || 'https://ui-avatars.com/api/?name=' + (authStore.user?.username || 'User') + '&background=667eea&color=fff&size=32'
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

const showNotifications = () => {
  // 显示通知列表
  console.log('显示通知')
}
</script>

<style scoped>
.modern-navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.75rem 0;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.container-fluid {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
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
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}

.search-container {
  flex: 1;
  max-width: 500px;
  margin: 0 2rem;
}

.search-box {
  position: relative;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 25px;
  padding: 0.5rem 1rem;
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
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 10px;
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
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 20px;
  padding: 0.4rem 0.75rem;
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
  z-index: 9999 !important;
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
  padding: 0.5rem 1.25rem;
  border-radius: 20px;
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
}
</style>