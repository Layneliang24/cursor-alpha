import request from './request'

// 特性开关相关API
export const featureFlagsAPI = {
  // 获取特性开关列表
  getList(params = {}) {
    return request.get('/feature-flags/', { params })
  },

  // 获取特性开关详情
  getDetail(id) {
    return request.get(`/feature-flags/${id}/`)
  },

  // 创建特性开关
  create(data) {
    return request.post('/feature-flags/', data)
  },

  // 更新特性开关
  update(id, data) {
    return request.put(`/feature-flags/${id}/`, data)
  },

  // 删除特性开关
  delete(id) {
    return request.delete(`/feature-flags/${id}/`)
  },

  // 启用特性开关
  enable(id) {
    return request.post(`/feature-flags/${id}/enable/`)
  },

  // 禁用特性开关
  disable(id) {
    return request.post(`/feature-flags/${id}/disable/`)
  },

  // 检查特性开关状态
  check(key, context = {}) {
    return request.post('/feature-flags/check/', { key, context })
  },

  // 批量检查特性开关
  checkMultiple(keys, context = {}) {
    return request.post('/feature-flags/check-multiple/', { keys, context })
  },

  // 获取用户的特性开关
  getUserFlags(context = {}) {
    return request.get('/feature-flags/user-flags/', { params: context })
  },

  // 记录特性开关使用情况
  recordUsage(key, context = {}) {
    return request.post('/feature-flags/record-usage/', { key, context })
  },

  // 获取特性开关统计信息
  getStats(id) {
    return request.get(`/feature-flags/${id}/stats/`)
  },

  // 获取特性开关历史记录
  getHistory(id, params = {}) {
    return request.get(`/feature-flags/${id}/history/`, { params })
  },

  // 获取特性开关使用记录
  getUsage(id, params = {}) {
    return request.get(`/feature-flags/${id}/usage/`, { params })
  }
}