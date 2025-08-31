/**
 * AI配置管理API接口
 */

import request from './request'

// AI服务提供商API
export const aiConfigAPI = {
  // 获取所有提供商
  getProviders() {
    return request.get('/ai/providers/')
  },

  // 创建提供商
  createProvider(data) {
    return request.post('/ai/providers/', data)
  },

  // 更新提供商
  updateProvider(id, data) {
    return request.put(`/ai/providers/${id}/`, data)
  },

  // 删除提供商
  deleteProvider(id) {
    return request.delete(`/ai/providers/${id}/`)
  },

  // 测试提供商连接
  testProvider(id) {
    return request.post(`/ai/providers/${id}/test/`)
  },

  // API密钥管理
  getApiKeys() {
    return request.get('/ai/keys/')
  },

  // 创建API密钥
  createApiKey(data) {
    return request.post('/ai/keys/', data)
  },

  // 更新API密钥
  updateApiKey(id, data) {
    return request.put(`/ai/keys/${id}/`, data)
  },

  // 删除API密钥
  deleteApiKey(id) {
    return request.delete(`/ai/keys/${id}/`)
  },

  // 测试API密钥
  testApiKey(id) {
    return request.post(`/ai/keys/${id}/test/`)
  },

  // AI模型管理
  getModels() {
    return request.get('/ai/models/')
  },

  // 获取可用模型（从提供商API动态加载）
  loadAvailableModels(providerId) {
    return request.post(`/ai/providers/${providerId}/load-models/`)
  },

  // 创建模型配置
  createModel(data) {
    return request.post('/ai/models/', data)
  },

  // 更新模型配置
  updateModel(id, data) {
    return request.put(`/ai/models/${id}/`, data)
  },

  // 删除模型配置
  deleteModel(id) {
    return request.delete(`/ai/models/${id}/`)
  },

  // 模型配置管理
  getModelConfigs() {
    return request.get('/ai/model-configs/')
  },

  // 创建模型配置
  createModelConfig(data) {
    return request.post('/ai/model-configs/', data)
  },

  // 更新模型配置
  updateModelConfig(id, data) {
    return request.put(`/ai/model-configs/${id}/`, data)
  },

  // 删除模型配置
  deleteModelConfig(id) {
    return request.delete(`/ai/model-configs/${id}/`)
  },

  // Token使用统计
  getTokenUsage(timeRange = 'week') {
    return request.get(`/ai/token-usage/`, {
      params: { time_range: timeRange }
    })
  },

  // 获取使用统计摘要
  getUsageStats(timeRange = 'week') {
    return request.get(`/ai/usage-stats/`, {
      params: { time_range: timeRange }
    })
  },

  // 使用配额管理
  getUsageQuotas() {
    return request.get('/ai/quotas/')
  },

  // 创建使用配额
  createUsageQuota(data) {
    return request.post('/ai/quotas/', data)
  },

  // 更新使用配额
  updateUsageQuota(id, data) {
    return request.put(`/ai/quotas/${id}/`, data)
  },

  // 删除使用配额
  deleteUsageQuota(id) {
    return request.delete(`/ai/quotas/${id}/`)
  },

  // 故障转移策略
  getFailoverStrategies() {
    return request.get('/ai/failover-strategies/')
  },

  // 创建故障转移策略
  createFailoverStrategy(data) {
    return request.post('/ai/failover-strategies/', data)
  },

  // 更新故障转移策略
  updateFailoverStrategy(id, data) {
    return request.put(`/ai/failover-strategies/${id}/`, data)
  },

  // 删除故障转移策略
  deleteFailoverStrategy(id) {
    return request.delete(`/ai/failover-strategies/${id}/`)
  },

  // 系统操作
  testAllConnections() {
    return request.post('/ai/test-all-connections/')
  },

  // 刷新所有提供商状态
  refreshAllProviders() {
    return request.post('/ai/refresh-providers/')
  },

  // 导出配置
  exportConfig() {
    return request.get('/ai/export-config/')
  },

  // 导入配置
  importConfig(configData) {
    return request.post('/ai/import-config/', configData)
  },

  // 获取系统健康状态
  getSystemHealth() {
    return request.get('/ai/system-health/')
  }
}

export default aiConfigAPI
