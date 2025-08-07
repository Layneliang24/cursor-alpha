import request from './request'

// 认证相关API
export const authAPI = {
  // 用户登录
  login(data) {
    return request.post('/auth/login/', data)
  },

  // 用户注册
  register(data) {
    return request.post('/auth/register/', data)
  },

  // 用户登出
  logout() {
    return request.post('/auth/logout/')
  },

  // 刷新Token
  refreshToken(refreshToken) {
    return request.post('/auth/token/refresh/', { refresh: refreshToken })
  },

  // 获取当前用户信息
  getCurrentUser() {
    return request.get('/users/me/')
  }
}