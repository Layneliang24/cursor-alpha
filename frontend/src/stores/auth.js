import { defineStore } from 'pinia'
import { authAPI } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    isLoggedIn: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    userInfo: (state) => state.user
  },

  actions: {
    // 登录
    async login(credentials) {
      try {
        const response = await authAPI.login(credentials)
        
        this.token = response.tokens.access
        this.refreshToken = response.tokens.refresh
        this.user = response.user
        this.isLoggedIn = true
        
        // 保存到本地存储
        localStorage.setItem('access_token', this.token)
        localStorage.setItem('refresh_token', this.refreshToken)
        localStorage.setItem('user', JSON.stringify(this.user))
        
        return response
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      }
    },

    // 注册
    async register(userData) {
      try {
        const response = await authAPI.register(userData)
        
        this.token = response.tokens.access
        this.refreshToken = response.tokens.refresh
        this.user = response.user
        this.isLoggedIn = true
        
        // 保存到本地存储
        localStorage.setItem('access_token', this.token)
        localStorage.setItem('refresh_token', this.refreshToken)
        localStorage.setItem('user', JSON.stringify(this.user))
        
        ElMessage.success('注册成功！')
        return response
      } catch (error) {
        console.error('注册失败:', error)
        throw error
      }
    },

    // 登出
    async logout() {
      try {
        if (this.token) {
          await authAPI.logout()
        }
      } catch (error) {
        console.error('登出请求失败:', error)
      } finally {
        // 清除状态和本地存储
        this.user = null
        this.token = null
        this.refreshToken = null
        this.isLoggedIn = false
        
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        
        ElMessage.success('已退出登录')
      }
    },

    // 初始化用户状态
    async initAuth() {
      const token = localStorage.getItem('access_token')
      const user = localStorage.getItem('user')
      
      if (token && user) {
        this.token = token
        this.user = JSON.parse(user) 
        this.isLoggedIn = true
        
        try {
          // 验证token是否有效
          await authAPI.getCurrentUser()
        } catch (error) {
          console.log('Token验证失败，清除登录状态')
          // token无效，静默清除登录状态，不显示错误消息
          this.clearAuth()
        }
      }
    },

    // 静默清除认证状态
    clearAuth() {
      this.user = null
      this.token = null
      this.refreshToken = null
      this.isLoggedIn = false
      
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    },

    // 刷新token
    async refreshAccessToken() {
      try {
        if (!this.refreshToken) {
          throw new Error('No refresh token available')
        }
        
        const response = await authAPI.refreshToken(this.refreshToken)
        this.token = response.access
        localStorage.setItem('access_token', this.token)
        
        return response.access
      } catch (error) {
        console.error('刷新token失败:', error)
        this.clearAuth()
        throw error
      }
    }
  }
})