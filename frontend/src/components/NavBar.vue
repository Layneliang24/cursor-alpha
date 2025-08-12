<template>
  <el-menu
    :default-active="activeIndex"
    class="nav-menu"
    mode="horizontal"
    router
  >
    <el-menu-item index="/">
      <el-icon><HomeFilled /></el-icon>
      <span>Alpha 技术共享平台</span>
    </el-menu-item>
    
    <div class="flex-grow" />
    
    <el-menu-item index="/articles">
      <el-icon><Document /></el-icon>
      <span>文章</span>
    </el-menu-item>
    
    <el-menu-item index="/english/words">
      <el-icon><Document /></el-icon>
      <span>英语学习</span>
    </el-menu-item>
    
    <template v-if="!authStore.isAuthenticated">
      <el-menu-item index="/login">
        <el-icon><User /></el-icon>
        <span>登录</span>
      </el-menu-item>
      <el-menu-item index="/register" class="register-menu-item">
        <el-icon><UserFilled /></el-icon>
        <span>注册</span>
      </el-menu-item>
    </template>
    
    <template v-else>
      <el-menu-item index="/articles/create" class="create-menu-item">
        <el-icon><EditPen /></el-icon>
        <span>发布文章</span>
      </el-menu-item>
      
      <el-sub-menu index="user">
        <template #title>
          <el-avatar :size="24" :src="authStore.user?.avatar" style="margin-right: 8px;">
            {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
          </el-avatar>
          <span>{{ authStore.user?.username }}</span>
        </template>
        <el-menu-item index="/user/profile">
          <el-icon><User /></el-icon>
          个人中心
        </el-menu-item>
        <el-menu-item index="/user/articles">
          <el-icon><Document /></el-icon>
          我的文章
        </el-menu-item>
        <el-menu-item @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-menu-item>
      </el-sub-menu>
    </template>
  </el-menu>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeIndex = ref('/')

// 监听路由变化更新激活菜单项
const updateActiveIndex = () => {
  activeIndex.value = route.path
}

onMounted(() => {
  updateActiveIndex()
  // 初始化认证状态
  authStore.initAuth()
})

// 监听路由变化
router.afterEach(() => {
  updateActiveIndex()
})

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await authStore.logout()
    router.push('/')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('退出登录失败:', error)
    }
  }
}
</script>

<style scoped>
.nav-menu {
  height: 60px;
  display: flex;
  align-items: center;
}

.flex-grow {
  flex-grow: 1;
}

.register-menu-item {
  background: #409eff !important;
  color: white !important;
  border-radius: 4px;
  margin: 0 8px;
}

.register-menu-item:hover {
  background: #337ecc !important;
}

.create-menu-item {
  background: #67c23a !important;
  color: white !important;
  border-radius: 4px;
  margin: 0 8px;
}

.create-menu-item:hover {
  background: #529b2e !important;
}

:deep(.el-sub-menu__title) {
  display: flex !important;
  align-items: center !important;
}

:deep(.el-menu-item) {
  display: flex;
  align-items: center;
}

:deep(.el-menu-item i) {
  margin-right: 5px;
}
</style>