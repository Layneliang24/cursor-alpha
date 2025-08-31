import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/modules/userStore'
import { 
  vueErrorHandler, 
  globalUnhandledErrorHandler, 
  globalUnhandledRejectionHandler, 
} from '@/utils/errorHandler'
import { setupApiErrorInterceptor } from '@/utils/apiErrorInterceptor'
import permissionDirective from '@/directives/permission'

const app = createApp(App)

// 设置全局错误处理器
app.config.errorHandler = vueErrorHandler

// 设置全局未捕获错误处理器
window.addEventListener('error', globalUnhandledErrorHandler)
window.addEventListener('unhandledrejection', globalUnhandledRejectionHandler)

// 设置API错误拦截器
setupApiErrorInterceptor()

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(ElementPlus)
app.use(permissionDirective)

// 初始化认证状态
const authStore = useAuthStore()
authStore.initAuth()

// 初始化用户权限状态
const userStore = useUserStore()
userStore.initialize()

app.mount('#app') 