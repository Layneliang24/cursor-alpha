import request from './request'

// 用户相关API  
export const usersAPI = {
  // 获取用户信息
  getUser(id) {
    return request.get(`/users/${id}/`)
  },

  // 更新用户信息
  updateUser(id, data) {
    return request.put(`/users/${id}/`, data)
  },

  // 获取当前登录用户资料（推荐）
  getMyProfile() {
    return request.get(`/profiles/me/`)
  },
  // 兼容旧版：按 id 获取（可能是 profile_id 或 user_id，后端已做兼容）
  getUserProfile(id) {
    return request.get(`/profiles/${id}/`)
  },

  // 更新当前登录用户资料（推荐）
  updateMyProfile(data) {
    return request.put(`/profiles/me/`, data)
  },
  // 兼容旧版：按 id 更新
  updateUserProfile(id, data) {
    return request.put(`/profiles/${id}/`, data)
  },

  // 创建用户资料
  createUserProfile(data) {
    return request.post('/profiles/', data)
  },

  // 获取用户文章
  getUserArticles(userId, params = {}) {
    return request.get('/articles/', { 
      params: { 
        author: userId,
        ...params 
      } 
    })
  }
}