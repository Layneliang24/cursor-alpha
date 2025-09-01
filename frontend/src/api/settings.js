import request from '@/utils/request'

// 用户设置API
export const userSettingsAPI = {
  // 获取用户设置
  getMySettings() {
    return request.get('/api/v1/ai/settings/my_settings/')
  },

  // 更新用户设置
  updateMySettings(data) {
    return request.put('/api/v1/ai/settings/my_settings/', data)
  }
}

// 用户资料API
export const userProfileAPI = {
  // 获取用户资料
  getMyProfile() {
    return request.get('/api/v1/ai/user-profile/my_profile/')
  },

  // 更新用户资料
  updateMyProfile(data) {
    return request.put('/api/v1/ai/user-profile/my_profile/', data)
  },

  // 修改密码
  changePassword(data) {
    return request.post('/api/v1/ai/password/change/', data)
  }
}

// 系统配置API
export const systemConfigAPI = {
  // 获取系统配置列表
  getSystemConfigs(params) {
    return request.get('/api/v1/ai/system-configs/', { params })
  },

  // 按分类获取配置
  getConfigsByCategory(category) {
    return request.get(`/api/v1/ai/system-configs/by_category/?category=${category}`)
  },

  // 获取单个配置
  getSystemConfig(id) {
    return request.get(`/api/v1/ai/system-configs/${id}/`)
  },

  // 创建系统配置
  createSystemConfig(data) {
    return request.post('/api/v1/ai/system-configs/', data)
  },

  // 更新系统配置
  updateSystemConfig(id, data) {
    return request.put(`/api/v1/ai/system-configs/${id}/`, data)
  },

  // 删除系统配置
  deleteSystemConfig(id) {
    return request.delete(`/api/v1/ai/system-configs/${id}/`)
  }
}

// 登录历史API
export const loginHistoryAPI = {
  // 获取登录历史
  getLoginHistory(params) {
    return request.get('/api/v1/ai/login-history/', { params })
  },

  // 获取最近的登录记录
  getRecentLoginHistory(limit = 10) {
    return request.get(`/api/v1/ai/login-history/recent/?limit=${limit}`)
  }
}

// 设备会话API
export const deviceSessionAPI = {
  // 获取设备会话列表
  getDeviceSessions(params) {
    return request.get('/api/v1/ai/device-sessions/', { params })
  },

  // 终止单个会话
  terminateSession(sessionId) {
    return request.post(`/api/v1/ai/device-sessions/${sessionId}/terminate/`)
  },

  // 终止所有会话
  terminateAllSessions() {
    return request.post('/api/v1/ai/device-sessions/terminate_all/')
  }
}
