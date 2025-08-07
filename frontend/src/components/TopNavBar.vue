<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container-fluid">
      <!-- Logo -->
      <a class="navbar-brand fw-bold" href="/">
        <i class="el-icon-star-on me-2"></i>Alpha系统
      </a>

      <!-- 搜索框 -->
      <div class="d-flex flex-grow-1 mx-4">
        <div class="input-group" style="max-width: 500px;">
          <input 
            type="text" 
            class="form-control" 
            placeholder="搜索文章、用户..."
            v-model="searchQuery"
            @keyup.enter="handleSearch"
          >
          <button class="btn btn-outline-light" type="button" @click="handleSearch">
            <i class="el-icon-search"></i>
          </button>
        </div>
      </div>

      <!-- 用户菜单 -->
      <div class="navbar-nav">
        <div class="nav-item dropdown" v-if="authStore.isAuthenticated">
          <a class="nav-link dropdown-toggle d-flex align-items-center" href="#" role="button" data-bs-toggle="dropdown">
            <img :src="userAvatar" class="rounded-circle me-2" width="32" height="32" alt="头像">
            {{ authStore.user?.username }}
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><router-link class="dropdown-item" to="/profile">个人资料</router-link></li>
            <li><router-link class="dropdown-item" to="/user/articles">我的文章</router-link></li>
            <li><hr class="dropdown-divider"></li>
            <li><a class="dropdown-item" href="#" @click="handleLogout">退出登录</a></li>
          </ul>
        </div>
        <div class="nav-item" v-else>
          <router-link class="btn btn-outline-light me-2" to="/login">登录</router-link>
          <router-link class="btn btn-light" to="/register">注册</router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const searchQuery = ref('')

const userAvatar = computed(() => {
  return authStore.user?.avatar || 'https://via.placeholder.com/32x32?text=U'
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
</script>

<style scoped>
.navbar-brand {
  font-size: 1.5rem;
}
</style>