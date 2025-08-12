import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: 'Alpha 技术共享平台' }
  },
  {
    path: '/english',
    name: 'English',
    redirect: '/english/words',
    meta: { title: '英语学习' }
  },
  {
    path: '/english/words',
    name: 'EnglishWords',
    component: () => import('@/views/english/Words.vue'),
    meta: { title: '单词学习', requiresAuth: true }
  },
  {
    path: '/english/words/:id',
    name: 'EnglishWordDetail',
    component: () => import('@/views/english/WordDetail.vue'),
    meta: { title: '单词详情', requiresAuth: true }
  },
  {
    path: '/english/expressions',
    name: 'EnglishExpressions',
    component: () => import('@/views/english/Expressions.vue'),
    meta: { title: '地道表达', requiresAuth: true }
  },
  {
    path: '/english/news',
    name: 'EnglishNews',
    component: () => import('@/views/english/NewsList.vue'),
    meta: { title: '英语新闻', requiresAuth: true }
  },
  {
    path: '/english/news/:id',
    name: 'EnglishNewsDetail',
    component: () => import('@/views/english/NewsDetail.vue'),
    meta: { title: '新闻详情', requiresAuth: true }
  },
  {
    path: '/english/dashboard',
    name: 'EnglishDashboard',
    component: () => import('@/views/english/Dashboard.vue'),
    meta: { title: '英语学习仪表板', requiresAuth: true }
  },
  {
    path: '/english/practice',
    name: 'EnglishPractice',
    component: () => import('@/views/english/Practice.vue'),
    meta: { title: '英语练习', requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '用户登录', guest: true }
  },
  {
    path: '/register',
    name: 'Register', 
    component: () => import('@/views/auth/Register.vue'),
    meta: { title: '用户注册', guest: true }
  },
  {
    path: '/reset-password/:uid/:token',
    name: 'PasswordReset',
    component: () => import('@/views/auth/PasswordReset.vue'),
    meta: { title: '重置密码', guest: true }
  },
  {
    path: '/articles',
    name: 'ArticleList',
    component: () => import('@/views/articles/ArticleList.vue'),
    meta: { title: '文章列表' }
  },
  {
    path: '/articles/create',
    name: 'ArticleCreate',
    component: () => import('@/views/articles/ArticleCreate.vue'),
    meta: { title: '发布文章', requiresAuth: true }
  },
  {
    path: '/articles/:id',
    name: 'ArticleDetail',
    component: () => import('@/views/articles/ArticleDetail.vue'),
    meta: { title: '文章详情' }
  },
  {
    path: '/articles/:id/edit',
    name: 'ArticleEdit',
    component: () => import('@/views/articles/ArticleEdit.vue'),
    meta: { title: '编辑文章', requiresAuth: true }
  },
  {
    path: '/categories',
    name: 'CategoryList',
    component: () => import('@/views/categories/CategoryList.vue'),
    meta: { title: '分类列表' }
  },
  {
    path: '/categories/:id',
    name: 'CategoryDetail',
    component: () => import('@/views/categories/CategoryDetail.vue'),
    meta: { title: '分类详情' }
  },
  {
    path: '/user/profile',
    name: 'UserProfile',
    component: () => import('@/views/user/Profile.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  {
    path: '/user/articles',
    name: 'UserArticles',
    component: () => import('@/views/user/UserArticles.vue'),
    meta: { title: '我的文章', requiresAuth: true }
  },
  {
    path: '/admin/categories',
    name: 'CategoryManage',
    component: () => import('@/views/categories/CategoryManage.vue'),
    meta: { title: '分类管理', requiresAuth: true, adminOnly: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  document.title = to.meta.title || 'Alpha 技术共享平台'
  
  // 初始化认证状态
  if (!authStore.isLoggedIn && authStore.token) {
    await authStore.initAuth()
  }
  
  // 检查需要认证的路由
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 管理员专用路由
  if (to.meta.adminOnly) {
    const user = authStore.user
    const inGroup = Array.isArray(user?.groups) && user.groups.includes('管理员')
    if (!user || !(user.is_staff || user.is_superuser || inGroup)) {
      ElMessage.warning('需要管理员权限')
      next({ name: 'Home' })
      return
    }
  }
  
  // 检查游客专用路由（已登录用户不应访问）
  if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'Home' })
    return
  }
  
  next()
})

export default router