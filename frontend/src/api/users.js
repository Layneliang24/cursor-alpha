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

  // 获取用户资料
  getUserProfile(id) {
    return request.get(`/profiles/${id}/`)
  },

  // 更新用户资料
  updateUserProfile(id, data) {
    return request.put(`/profiles/${id}/`, data)
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