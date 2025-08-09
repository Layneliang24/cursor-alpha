import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

// 创建axios实例
const request = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 请求拦截器 - 添加token
request.interceptors.request.use(
  config => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('响应错误:', error)
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          ElMessage.error(data.message || '请求参数错误')
          break
        case 401:
          // 静默处理401错误，避免循环重定向
          const authStore = useAuthStore()
          if (authStore.token) {
            console.log('认证失败，清除登录状态')
            authStore.clearAuth()
            // 只在不是登录页面时才重定向
            if (!window.location.pathname.includes('/login')) {
              window.location.href = '/login'
            }
          }
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 404:
          console.error('404错误详情:', error.config?.url, error.response?.data)
          ElMessage.error(`请求的资源不存在: ${error.config?.url}`)
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data.message || '网络错误，请稍后重试')
      }
    } else {
      ElMessage.error('网络连接失败，请检查网络')
    }
    
    return Promise.reject(error)
  }
)

export default request