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
      <span>{{ $t('nav.articles') }}</span>
    </el-menu-item>
    
    <!-- 语言切换器 -->
    <div class="language-switcher-container">
      <LanguageSwitcher />
    </div>
    
          <el-sub-menu index="english">
        <template #title>
          <el-icon><Document /></el-icon>
          <span>{{ $t('nav.englishLearning') }}</span>
        </template>
        <el-menu-item index="/english/news-dashboard">
          <el-icon><Notification /></el-icon>
          {{ $t('nav.newsDashboard') }}
        </el-menu-item>
        <el-menu-item index="/english/words">
          <el-icon><Document /></el-icon>
          {{ $t('nav.wordLearning') }}
        </el-menu-item>
        <el-menu-item index="/english/expressions">
          <el-icon><ChatDotRound /></el-icon>
          {{ $t('nav.expressions') }}
        </el-menu-item>
        <el-menu-item index="/english/news">
          <el-icon><List /></el-icon>
          {{ $t('nav.newsList') }}
        </el-menu-item>
      </el-sub-menu>
    
    <template v-if="!authStore.isAuthenticated">
      <el-menu-item index="/login">
        <el-icon><User /></el-icon>
        <span>{{ $t('nav.login') }}</span>
      </el-menu-item>
      <el-menu-item index="/register" class="register-menu-item">
        <el-icon><UserFilled /></el-icon>
        <span>{{ $t('nav.register') }}</span>
      </el-menu-item>
    </template>
    
    <template v-else>
      <el-menu-item index="/articles/create" class="create-menu-item">
        <el-icon><EditPen /></el-icon>
        <span>{{ $t('nav.createArticle') }}</span>
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
          {{ $t('nav.profile') }}
        </el-menu-item>
        <el-menu-item index="/user/articles">
          <el-icon><Document /></el-icon>
          {{ $t('nav.myArticles') }}
        </el-menu-item>
        <el-menu-item @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          {{ $t('nav.logout') }}
        </el-menu-item>
      </el-sub-menu>
    </template>
  </el-menu>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  HomeFilled, 
  Document, 
  User, 
  UserFilled, 
  EditPen, 
  SwitchButton,
  Notification,
  ChatDotRound,
  List
} from '@element-plus/icons-vue'
import LanguageSwitcher from './common/LanguageSwitcher.vue'

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

const { t } = useI18n()

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      t('confirm.logoutConfirm'),
      t('common.info'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    )
    await authStore.logout()
    router.push('/')
  } catch (error) {
    if (error !== 'cancel') {
      console.error(t('errors.logoutFailed'), error)
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

.language-switcher-container {
  display: flex;
  align-items: center;
  margin: 0 16px;
}
</style>