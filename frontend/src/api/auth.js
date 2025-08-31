import request from './request'

// 认证相关API
export const authAPI = {
  // 用户登录
  login (data) {
    return request.post('/auth/login/', data)
  },

  // 用户注册
  register (data) {
    return request.post('/auth/register/', data)
  },

  // 用户登出
  logout () {
    return request.post('/auth/logout/')
  },

  // 刷新Token
  refreshToken (refreshToken) {
    return request.post('/auth/token/refresh/', { refresh: refreshToken })
  },

  // 获取当前用户信息
  getCurrentUser () {
    return request.get('/users/me/')
  },

  // 验证用户身份（用于登录页面显示头像）
  verifyUserIdentity (data) {
    // 使用配置好的request实例，不需要认证但需要正确的CORS配置
    return request.post('/auth/verify-identity/', data)
  },

  // 请求密码重置
  requestPasswordReset (email) {
    return request.post('/auth/password-reset/', { email })
  },

  // 确认密码重置
  confirmPasswordReset (data) {
    return request.post('/auth/password-reset-confirm/', data)
  },
}