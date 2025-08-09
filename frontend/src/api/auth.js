import request from './request'
import axios from 'axios'

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
  },

  // 验证用户身份（用于登录页面显示头像）
  verifyUserIdentity(data) {
    // 不需要认证的请求，直接使用axios
    return axios.post('http://127.0.0.1:8000/api/v1/auth/verify-identity/', data, {
      headers: {
        'Content-Type': 'application/json',
      }
    }).then(response => response.data)
  },

  // 请求密码重置
  requestPasswordReset(email) {
    return axios.post('http://127.0.0.1:8000/api/v1/auth/password-reset/', { email }, {
      headers: {
        'Content-Type': 'application/json',
      }
    }).then(response => response.data)
  },

  // 确认密码重置
  confirmPasswordReset(data) {
    return axios.post('http://127.0.0.1:8000/api/v1/auth/password-reset-confirm/', data, {
      headers: {
        'Content-Type': 'application/json',
      }
    }).then(response => response.data)
  }
}