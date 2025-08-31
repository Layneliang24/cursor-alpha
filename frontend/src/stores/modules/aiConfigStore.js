import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { aiConfigAPI } from '@/api/aiConfig'

export const useAIConfigStore = defineStore('aiConfig', () => {
  // 状态
  const providers = ref([])
  const apiKeys = ref([])
  const models = ref([])
  const modelConfigs = ref([])
  const promptTemplates = ref([])
  const tokenUsage = ref([])
  const quotas = ref([])
  const loading = ref(false)
  
  // 计算属性
  const activeProviders = computed(() => 
    providers.value.filter(provider => provider.is_active)
  )
  
  const healthyProviders = computed(() => 
    providers.value.filter(provider => provider.is_healthy)
  )
  
  const totalProviders = computed(() => providers.value.length)
  
  const onlineProviders = computed(() => healthyProviders.value.length)
  
  const overallHealthy = computed(() => 
    providers.value.length > 0 && healthyProviders.value.length > 0
  )

  // 提供商相关操作
  const fetchProviders = async () => {
    loading.value = true
    try {
      const response = await aiConfigAPI.getProviders()
      providers.value = response.data.results || response.data || []
      return providers.value
    } catch (error) {
      console.error('获取提供商列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createProvider = async (providerData) => {
    try {
      const response = await aiConfigAPI.createProvider(providerData)
      providers.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('创建提供商失败:', error)
      throw error
    }
  }

  const updateProvider = async (providerId, providerData) => {
    try {
      const response = await aiConfigAPI.updateProvider(providerId, providerData)
      const index = providers.value.findIndex(p => p.id === providerId)
      if (index !== -1) {
        providers.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新提供商失败:', error)
      throw error
    }
  }

  const deleteProvider = async (providerId) => {
    try {
      await aiConfigAPI.deleteProvider(providerId)
      providers.value = providers.value.filter(p => p.id !== providerId)
    } catch (error) {
      console.error('删除提供商失败:', error)
      throw error
    }
  }

  const testProviderConnection = async (providerId) => {
    try {
      const response = await aiConfigAPI.testProviderConnection(providerId)
      
      // 更新提供商健康状态
      const provider = providers.value.find(p => p.id === providerId)
      if (provider) {
        provider.is_healthy = response.data.is_healthy
        provider.avg_response_time = response.data.response_time
        provider.last_checked = new Date().toISOString()
      }
      
      return response.data
    } catch (error) {
      console.error('测试连接失败:', error)
      throw error
    }
  }

  const testProviderConfig = async (providerConfig) => {
    try {
      const response = await aiConfigAPI.testProviderConfig(providerConfig)
      return response.data
    } catch (error) {
      console.error('测试提供商配置失败:', error)
      throw error
    }
  }

  const batchTestProviders = async (providerIds) => {
    try {
      const response = await aiConfigAPI.batchTestProviders(providerIds)
      
      // 更新提供商健康状态
      if (response.data.results) {
        response.data.results.forEach(result => {
          const provider = providers.value.find(p => p.id === result.provider_id)
          if (provider) {
            provider.is_healthy = result.is_healthy
            provider.avg_response_time = result.response_time
            provider.last_checked = new Date().toISOString()
          }
        })
      }
      
      return response.data.results || []
    } catch (error) {
      console.error('批量测试失败:', error)
      throw error
    }
  }

  const getProviderStatus = async () => {
    try {
      const response = await aiConfigAPI.getProviderStatus()
      return response.data
    } catch (error) {
      console.error('获取提供商状态失败:', error)
      throw error
    }
  }

  // API密钥相关操作
  const fetchAPIKeys = async (providerId = null) => {
    try {
      const response = await aiConfigAPI.getAPIKeys(providerId)
      apiKeys.value = response.data.results || response.data || []
      return apiKeys.value
    } catch (error) {
      console.error('获取API密钥列表失败:', error)
      throw error
    }
  }

  const createAPIKey = async (keyData) => {
    try {
      const response = await aiConfigAPI.createAPIKey(keyData)
      apiKeys.value.push(response.data)
      
      // 更新提供商的密钥计数
      const provider = providers.value.find(p => p.id === keyData.provider)
      if (provider) {
        provider.api_keys_count = (provider.api_keys_count || 0) + 1
      }
      
      return response.data
    } catch (error) {
      console.error('创建API密钥失败:', error)
      throw error
    }
  }

  const updateAPIKey = async (keyId, keyData) => {
    try {
      const response = await aiConfigAPI.updateAPIKey(keyId, keyData)
      const index = apiKeys.value.findIndex(k => k.id === keyId)
      if (index !== -1) {
        apiKeys.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新API密钥失败:', error)
      throw error
    }
  }

  const deleteAPIKey = async (keyId) => {
    try {
      const keyToDelete = apiKeys.value.find(k => k.id === keyId)
      await aiConfigAPI.deleteAPIKey(keyId)
      apiKeys.value = apiKeys.value.filter(k => k.id !== keyId)
      
      // 更新提供商的密钥计数
      if (keyToDelete) {
        const provider = providers.value.find(p => p.id === keyToDelete.provider)
        if (provider && provider.api_keys_count > 0) {
          provider.api_keys_count -= 1
        }
      }
    } catch (error) {
      console.error('删除API密钥失败:', error)
      throw error
    }
  }

  // 模型相关操作
  const fetchModels = async (providerId = null) => {
    try {
      const response = await aiConfigAPI.getModels(providerId)
      models.value = response.data.results || response.data || []
      return models.value
    } catch (error) {
      console.error('获取模型列表失败:', error)
      throw error
    }
  }

  const fetchAvailableModels = async (providerId) => {
    try {
      const response = await aiConfigAPI.getAvailableModels(providerId)
      return response.data.models || []
    } catch (error) {
      console.error('获取可用模型失败:', error)
      throw error
    }
  }

  const createModel = async (modelData) => {
    try {
      const response = await aiConfigAPI.createModel(modelData)
      models.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('创建模型失败:', error)
      throw error
    }
  }

  const updateModel = async (modelId, modelData) => {
    try {
      const response = await aiConfigAPI.updateModel(modelId, modelData)
      const index = models.value.findIndex(m => m.id === modelId)
      if (index !== -1) {
        models.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新模型失败:', error)
      throw error
    }
  }

  const deleteModel = async (modelId) => {
    try {
      await aiConfigAPI.deleteModel(modelId)
      models.value = models.value.filter(m => m.id !== modelId)
    } catch (error) {
      console.error('删除模型失败:', error)
      throw error
    }
  }

  const testModel = async (modelId, testConfig) => {
    try {
      // 模拟模型测试API调用
      // 实际项目中应该调用真实的API
      const response = {
        success: true,
        data: {
          response: `这是模型 ${modelId} 的测试响应：${testConfig.prompt}`,
          tokens_used: Math.floor(Math.random() * 100) + 50,
          cost: (Math.random() * 0.01).toFixed(4),
          response_time: Math.floor(Math.random() * 500) + 100
        }
      }
      
      return response
    } catch (error) {
      console.error('测试模型失败:', error)
      throw error
    }
  }

  // 模型配置相关操作
  const fetchModelConfigs = async () => {
    try {
      const response = await aiConfigAPI.getModelConfigs()
      modelConfigs.value = response.data.results || response.data || []
      return modelConfigs.value
    } catch (error) {
      console.error('获取模型配置列表失败:', error)
      throw error
    }
  }

  const createModelConfig = async (configData) => {
    try {
      const response = await aiConfigAPI.createModelConfig(configData)
      modelConfigs.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('创建模型配置失败:', error)
      throw error
    }
  }

  const updateModelConfig = async (configId, configData) => {
    try {
      const response = await aiConfigAPI.updateModelConfig(configId, configData)
      const index = modelConfigs.value.findIndex(c => c.id === configId)
      if (index !== -1) {
        modelConfigs.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新模型配置失败:', error)
      throw error
    }
  }

  const deleteModelConfig = async (configId) => {
    try {
      await aiConfigAPI.deleteModelConfig(configId)
      modelConfigs.value = modelConfigs.value.filter(c => c.id !== configId)
    } catch (error) {
      console.error('删除模型配置失败:', error)
      throw error
    }
  }

  const setDefaultModelConfig = async (configId) => {
    try {
      const response = await aiConfigAPI.setDefaultModelConfig(configId)
      // 更新本地状态：将其他配置的默认状态设为false，当前配置设为true
      modelConfigs.value.forEach(config => {
        config.is_default = config.id === configId
      })
      return response.data
    } catch (error) {
      console.error('设置默认配置失败:', error)
      throw error
    }
  }

  const duplicateModelConfig = async (configId) => {
    try {
      const response = await aiConfigAPI.duplicateModelConfig(configId)
      modelConfigs.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('复制配置失败:', error)
      throw error
    }
  }

  const getModelsMetadata = async (providerId) => {
    try {
      const response = await aiConfigAPI.getModelsMetadata(providerId)
      return response.data.data || []
    } catch (error) {
      console.error('获取模型元数据失败:', error)
      throw error
    }
  }

  // 提示模板相关操作
  const fetchPromptTemplates = async () => {
    try {
      const response = await aiConfigAPI.getPromptTemplates()
      promptTemplates.value = response.data.results || response.data || []
      return promptTemplates.value
    } catch (error) {
      console.error('获取提示模板列表失败:', error)
      throw error
    }
  }

  const createPromptTemplate = async (templateData) => {
    try {
      const response = await aiConfigAPI.createPromptTemplate(templateData)
      promptTemplates.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('创建提示模板失败:', error)
      throw error
    }
  }

  const updatePromptTemplate = async (templateId, templateData) => {
    try {
      const response = await aiConfigAPI.updatePromptTemplate(templateId, templateData)
      const index = promptTemplates.value.findIndex(t => t.id === templateId)
      if (index !== -1) {
        promptTemplates.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新提示模板失败:', error)
      throw error
    }
  }

  const deletePromptTemplate = async (templateId) => {
    try {
      await aiConfigAPI.deletePromptTemplate(templateId)
      promptTemplates.value = promptTemplates.value.filter(t => t.id !== templateId)
    } catch (error) {
      console.error('删除提示模板失败:', error)
      throw error
    }
  }

  const getPromptTemplateCategories = async () => {
    try {
      const response = await aiConfigAPI.getPromptTemplateCategories()
      return response.data.data || []
    } catch (error) {
      console.error('获取模板分类失败:', error)
      throw error
    }
  }

  // Token使用统计相关操作
  const fetchTokenUsage = async (filters = {}) => {
    try {
      const response = await aiConfigAPI.getTokenUsage(filters)
      tokenUsage.value = response.data.results || response.data || []
      return tokenUsage.value
    } catch (error) {
      console.error('获取Token使用统计失败:', error)
      throw error
    }
  }

  const getUsageStatistics = async (timeRange = '7d') => {
    try {
      const response = await aiConfigAPI.getUsageStatistics(timeRange)
      return response.data
    } catch (error) {
      console.error('获取使用统计失败:', error)
      throw error
    }
  }

  // 配额管理相关操作
  const fetchQuotas = async () => {
    try {
      const response = await aiConfigAPI.getQuotas()
      quotas.value = response.data.results || response.data || []
      return quotas.value
    } catch (error) {
      console.error('获取配额列表失败:', error)
      throw error
    }
  }

  const updateQuota = async (quotaId, quotaData) => {
    try {
      const response = await aiConfigAPI.updateQuota(quotaId, quotaData)
      const index = quotas.value.findIndex(q => q.id === quotaId)
      if (index !== -1) {
        quotas.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新配额失败:', error)
      throw error
    }
  }

  // 系统健康检查
  const getSystemHealth = async () => {
    try {
      const response = await aiConfigAPI.getSystemHealth()
      return response.data
    } catch (error) {
      console.error('获取系统健康状态失败:', error)
      throw error
    }
  }

  // 重置状态
  const resetState = () => {
    providers.value = []
    apiKeys.value = []
    models.value = []
    modelConfigs.value = []
    promptTemplates.value = []
    tokenUsage.value = []
    quotas.value = []
    loading.value = false
  }

  // 初始化数据
  const initializeData = async () => {
    try {
      loading.value = true
      await Promise.all([
        fetchProviders(),
        fetchAPIKeys(),
        fetchModels(),
        fetchModelConfigs(),
        fetchPromptTemplates()
      ])
    } catch (error) {
      console.error('初始化数据失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    providers,
    apiKeys,
    models,
    modelConfigs,
    promptTemplates,
    tokenUsage,
    quotas,
    loading,
    
    // 计算属性
    activeProviders,
    healthyProviders,
    totalProviders,
    onlineProviders,
    overallHealthy,
    
    // 提供商操作
    fetchProviders,
    createProvider,
    updateProvider,
    deleteProvider,
    testProviderConnection,
    testProviderConfig,
    batchTestProviders,
    getProviderStatus,
    
    // API密钥操作
    fetchAPIKeys,
    createAPIKey,
    updateAPIKey,
    deleteAPIKey,
    
    // 模型操作
    fetchModels,
    fetchAvailableModels,
    createModel,
    updateModel,
    deleteModel,
    testModel,
    
    // 模型配置操作
    fetchModelConfigs,
    createModelConfig,
    updateModelConfig,
    deleteModelConfig,
    setDefaultModelConfig,
    duplicateModelConfig,
    getModelsMetadata,
    
    // 提示模板操作
    fetchPromptTemplates,
    createPromptTemplate,
    updatePromptTemplate,
    deletePromptTemplate,
    getPromptTemplateCategories,
    
    // Token使用统计操作
    fetchTokenUsage,
    getUsageStatistics,
    
    // 配额管理操作
    fetchQuotas,
    updateQuota,
    
    // 系统操作
    getSystemHealth,
    resetState,
    initializeData
  }
})
