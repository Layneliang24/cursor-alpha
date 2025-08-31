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
  testProviderConnection(id) {
    return request.post(`/ai/providers/${id}/test_connection/`)
  },

  // 测试提供商配置（不保存）
  testProviderConfig(config) {
    return request.post('/ai/providers/test_config/', config)
  },

  // 批量测试提供商
  batchTestProviders(providerIds) {
    return request.post('/ai/providers/bulk_test/', { provider_ids: providerIds })
  },

  // 获取提供商状态
  getProviderStatus() {
    return request.get('/ai/providers/system_health/')
  },

  // API密钥管理
  getAPIKeys(providerId = null) {
    const params = providerId ? { provider: providerId } : {}
    return request.get('/ai/keys/', { params })
  },

  // 创建API密钥
  createAPIKey(data) {
    return request.post('/ai/keys/', data)
  },

  // 更新API密钥
  updateAPIKey(id, data) {
    return request.put(`/ai/keys/${id}/`, data)
  },

  // 删除API密钥
  deleteAPIKey(id) {
    return request.delete(`/ai/keys/${id}/`)
  },

  // AI模型管理
  getModels(providerId = null) {
    const params = providerId ? { provider: providerId } : {}
    return request.get('/ai/models/', { params })
  },

  // 获取可用模型（从提供商API动态加载）
  getAvailableModels(providerId) {
    return request.get(`/ai/providers/${providerId}/available_models/`)
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

  // 测试模型
  testModel(id, config) {
    return request.post(`/ai/models/${id}/test/`, config)
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

  // 设置默认模型配置
  setDefaultModelConfig(id) {
    return request.post(`/ai/model-configs/${id}/set_default/`)
  },

  // 复制模型配置
  duplicateModelConfig(id) {
    return request.post(`/ai/model-configs/${id}/duplicate/`)
  },

  // 获取模型元数据
  getModelsMetadata(providerId) {
    const params = providerId ? { provider_id: providerId } : {}
    return request.get('/ai/model-configs/models_metadata/', { params })
  },

  // 提示模板管理
  getPromptTemplates() {
    return request.get('/ai/prompt-templates/')
  },

  // 创建提示模板
  createPromptTemplate(data) {
    return request.post('/ai/prompt-templates/', data)
  },

  // 更新提示模板
  updatePromptTemplate(id, data) {
    return request.put(`/ai/prompt-templates/${id}/`, data)
  },

  // 删除提示模板
  deletePromptTemplate(id) {
    return request.delete(`/ai/prompt-templates/${id}/`)
  },

  // 获取提示模板分类
  getPromptTemplateCategories() {
    return request.get('/ai/prompt-templates/categories/')
  },

  // Token使用统计
  getTokenUsage(filters = {}) {
    return request.get('/ai/token-usage/', { params: filters })
  },

  // 获取使用统计摘要
  getUsageStatistics(timeRange = '7d') {
    return request.get('/ai/usage-statistics/', {
      params: { time_range: timeRange }
    })
  },

  // 使用配额管理
  getQuotas() {
    return request.get('/ai/quotas/')
  },

  // 创建使用配额
  createUsageQuota(data) {
    return request.post('/ai/quotas/', data)
  },

  // 更新使用配额
  updateQuota(id, data) {
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
    return request.get('/ai/providers/system_health/')
  }
}

export default aiConfigAPI
