<template>
  <div class="ai-config-container">
    <div class="content-wrapper">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">AI服务配置管理</h1>
        <p class="page-subtitle">配置和管理AI助教服务提供商、API密钥、模型选择等</p>
      </div>

      <!-- 标签页导航 -->
      <div class="tab-navigation">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          @click="activeTab = tab.key"
          class="tab-button"
          :class="{ 'tab-active': activeTab === tab.key }"
        >
          <i :class="tab.icon"></i>
          {{ tab.label }}
        </button>
      </div>

      <!-- 概览页 -->
      <div v-if="activeTab === 'overview'" class="tab-content">
        <div class="overview-grid">
          <!-- 服务状态卡片 -->
          <div class="status-card">
            <div class="card-header">
              <h3 class="card-title">服务状态</h3>
              <div class="status-indicator">
                <div class="status-dot" :class="overallStatus ? 'status-connected' : 'status-disconnected'"></div>
                <span class="status-text">{{ onlineServicesCount }}/{{ totalServicesCount }} 在线</span>
              </div>
            </div>
            <div class="card-content">
              <div class="service-list">
                <div v-for="provider in providers" :key="provider.id" class="service-item">
                  <span class="service-name">{{ provider.display_name }}</span>
                  <div class="service-status">
                    <div class="status-dot" :class="provider.is_healthy ? 'status-connected' : 'status-disconnected'"></div>
                    <span class="service-response-time">{{ provider.avg_response_time || 0 }}ms</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Token消费统计 -->
          <div class="stats-card">
            <div class="card-header">
              <h3 class="card-title">Token消费统计</h3>
              <select v-model="statsTimeRange" class="time-range-select">
                <option value="today">今日</option>
                <option value="week">本周</option>
                <option value="month">本月</option>
              </select>
            </div>
            <div class="card-content">
              <div class="stats-grid">
                <div class="stat-item">
                  <span class="stat-label">总消费</span>
                  <span class="stat-value">${{ totalCost.toFixed(2) }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">总Token</span>
                  <span class="stat-value">{{ totalTokens.toLocaleString() }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">请求次数</span>
                  <span class="stat-value">{{ totalRequests }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 快速操作 -->
          <div class="quick-actions-card">
            <div class="card-header">
              <h3 class="card-title">快速操作</h3>
            </div>
            <div class="card-content">
              <div class="action-grid">
                <button @click="testAllConnections" class="action-btn test-btn" :disabled="testing">
                  <i class="icon-test"></i>
                  {{ testing ? '测试中...' : '测试所有连接' }}
                </button>
                <button @click="refreshProviders" class="action-btn refresh-btn" :disabled="loading">
                  <i class="icon-refresh"></i>
                  {{ loading ? '刷新中...' : '刷新状态' }}
                </button>
                <button @click="exportConfig" class="action-btn export-btn">
                  <i class="icon-export"></i>
                  导出配置
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 提供商管理页 -->
      <div v-if="activeTab === 'providers'" class="tab-content">
        <div class="providers-header">
          <h2>AI服务提供商</h2>
          <button @click="showAddProviderModal = true" class="add-button">
            <i class="icon-plus"></i>
            添加提供商
          </button>
        </div>

        <div class="providers-grid">
          <div v-for="provider in providers" :key="provider.id" class="provider-card">
            <div class="card-header">
              <h3 class="card-title">{{ provider.display_name }}</h3>
              <div class="provider-actions">
                <button @click="editProvider(provider)" class="icon-btn edit-btn">
                  <i class="icon-edit"></i>
                </button>
                <button @click="deleteProvider(provider)" class="icon-btn delete-btn">
                  <i class="icon-delete"></i>
                </button>
              </div>
            </div>
            <div class="card-content">
              <div class="provider-info">
                <div class="info-item">
                  <span class="info-label">类型:</span>
                  <span class="info-value">{{ provider.provider_type }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">状态:</span>
                  <div class="status-indicator">
                    <div class="status-dot" :class="provider.is_healthy ? 'status-connected' : 'status-disconnected'"></div>
                    <span class="status-text">{{ provider.is_healthy ? '健康' : '异常' }}</span>
                  </div>
                </div>
                <div class="info-item">
                  <span class="info-label">响应时间:</span>
                  <span class="info-value">{{ provider.avg_response_time || 0 }}ms</span>
                </div>
                <div class="info-item">
                  <span class="info-label">成功率:</span>
                  <span class="info-value">{{ (provider.success_rate || 0).toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- API密钥管理页 -->
      <div v-if="activeTab === 'keys'" class="tab-content">
        <div class="keys-header">
          <h2>API密钥管理</h2>
          <button @click="showAddKeyModal = true" class="add-button">
            <i class="icon-plus"></i>
            添加密钥
          </button>
        </div>

        <div class="keys-list">
          <div v-for="key in apiKeys" :key="key.id" class="key-card">
            <div class="key-header">
              <div class="key-info">
                <h3 class="key-name">{{ key.name }}</h3>
                <span class="key-provider">{{ key.provider_name }}</span>
              </div>
              <div class="key-actions">
                <span v-if="key.is_default" class="default-badge">默认</span>
                <button @click="editKey(key)" class="icon-btn edit-btn">
                  <i class="icon-edit"></i>
                </button>
                <button @click="deleteKey(key)" class="icon-btn delete-btn">
                  <i class="icon-delete"></i>
                </button>
              </div>
            </div>
            <div class="key-content">
              <div class="key-details">
                <div class="detail-item">
                  <span class="detail-label">密钥:</span>
                  <span class="detail-value masked-key">{{ key.masked_key }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">状态:</span>
                  <div class="status-indicator">
                    <div class="status-dot" :class="key.is_active ? 'status-connected' : 'status-disconnected'"></div>
                    <span class="status-text">{{ key.is_active ? '活跃' : '禁用' }}</span>
                  </div>
                </div>
                <div class="detail-item">
                  <span class="detail-label">过期时间:</span>
                  <span class="detail-value" :class="{ 'text-warning': key.is_expired }">
                    {{ key.expires_at ? formatDate(key.expires_at) : '永不过期' }}
                  </span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">最后使用:</span>
                  <span class="detail-value">{{ key.last_used ? formatDate(key.last_used) : '从未使用' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 模型配置页 -->
      <div v-if="activeTab === 'models'" class="tab-content">
        <div class="models-header">
          <h2>AI模型配置</h2>
          <div class="models-actions">
            <button @click="loadAvailableModels" class="action-btn refresh-btn" :disabled="loadingModels">
              <i class="icon-refresh"></i>
              {{ loadingModels ? '加载中...' : '刷新模型列表' }}
            </button>
            <button @click="showAddModelModal = true" class="add-button">
              <i class="icon-plus"></i>
              添加模型
            </button>
          </div>
        </div>

        <div class="models-grid">
          <div v-for="model in models" :key="model.id" class="model-card">
            <div class="card-header">
              <h3 class="card-title">{{ model.display_name }}</h3>
              <div class="model-badges">
                <span v-if="model.is_recommended" class="badge recommended">推荐</span>
                <span v-if="model.supports_streaming" class="badge feature">流式</span>
                <span v-if="model.supports_vision" class="badge feature">视觉</span>
              </div>
            </div>
            <div class="card-content">
              <p class="model-description">{{ model.description }}</p>
              <div class="model-specs">
                <div class="spec-item">
                  <span class="spec-label">最大Token:</span>
                  <span class="spec-value">{{ model.max_tokens?.toLocaleString() || 'N/A' }}</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">输入成本:</span>
                  <span class="spec-value">${{ model.cost_per_1k_input_tokens || 0 }}/1K</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">输出成本:</span>
                  <span class="spec-value">${{ model.cost_per_1k_output_tokens || 0 }}/1K</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 统计分析页 -->
      <div v-if="activeTab === 'analytics'" class="tab-content">
        <div class="analytics-header">
          <h2>使用统计分析</h2>
          <div class="time-filters">
            <select v-model="analyticsTimeRange" @change="loadAnalytics" class="time-range-select">
              <option value="today">今日</option>
              <option value="week">本周</option>
              <option value="month">本月</option>
              <option value="quarter">本季度</option>
            </select>
          </div>
        </div>

        <div class="analytics-grid">
          <!-- Token使用趋势图 -->
          <div class="chart-card">
            <h3 class="chart-title">Token使用趋势</h3>
            <div class="chart-container">
              <!-- 这里将集成ECharts图表 -->
              <div class="chart-placeholder">
                📊 Token使用趋势图 (待集成ECharts)
              </div>
            </div>
          </div>

          <!-- 提供商分布 -->
          <div class="chart-card">
            <h3 class="chart-title">提供商使用分布</h3>
            <div class="chart-container">
              <div class="chart-placeholder">
                🥧 提供商分布饼图 (待集成ECharts)
              </div>
            </div>
          </div>

          <!-- 成本分析 -->
          <div class="chart-card">
            <h3 class="chart-title">成本分析</h3>
            <div class="chart-container">
              <div class="chart-placeholder">
                💰 成本分析图表 (待集成ECharts)
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 测试结果显示 -->
      <div v-if="testResults.length > 0" class="results-card">
        <h2 class="results-title">操作结果</h2>
        <div class="results-list">
          <div 
            v-for="(result, index) in testResults" 
            :key="index"
            class="result-item"
            :class="result.success ? 'result-success' : 'result-error'"
          >
            <div class="result-content">
              <span class="result-service">{{ result.service }}</span>
              <span class="result-message">{{ result.message }}</span>
            </div>
            <span class="result-status" :class="result.success ? 'result-success' : 'result-error'">
              {{ result.success ? '成功' : '失败' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加提供商模态框 -->
    <div v-if="showAddProviderModal" class="modal-overlay" @click="showAddProviderModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>添加AI服务提供商</h3>
          <button @click="showAddProviderModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">提供商名称</label>
            <input v-model="newProvider.name" type="text" class="form-input" placeholder="例如: OpenAI" />
          </div>
          <div class="form-group">
            <label class="form-label">显示名称</label>
            <input v-model="newProvider.display_name" type="text" class="form-input" placeholder="例如: OpenAI GPT" />
          </div>
          <div class="form-group">
            <label class="form-label">提供商类型</label>
            <select v-model="newProvider.provider_type" class="form-select">
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="google">Google</option>
              <option value="openrouter">OpenRouter</option>
              <option value="chenmoai">ChenmoAI</option>
              <option value="siliconflow">SiliconFlow</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">API基础URL</label>
            <input v-model="newProvider.base_url" type="url" class="form-input" placeholder="https://api.openai.com/v1" />
          </div>
          <div class="form-group">
            <label class="form-label">描述</label>
            <textarea v-model="newProvider.description" class="form-textarea" placeholder="提供商描述"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showAddProviderModal = false" class="btn btn-secondary">取消</button>
          <button @click="addProvider" class="btn btn-primary">添加</button>
        </div>
      </div>
    </div>

    <!-- 添加API密钥模态框 -->
    <div v-if="showAddKeyModal" class="modal-overlay" @click="showAddKeyModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>添加API密钥</h3>
          <button @click="showAddKeyModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">密钥名称</label>
            <input v-model="newKey.name" type="text" class="form-input" placeholder="例如: OpenAI Production Key" />
          </div>
          <div class="form-group">
            <label class="form-label">选择提供商</label>
            <select v-model="newKey.provider" class="form-select">
              <option v-for="provider in providers" :key="provider.id" :value="provider.id">
                {{ provider.display_name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">API密钥</label>
            <input v-model="newKey.raw_key" type="password" class="form-input" placeholder="sk-..." />
          </div>
          <div class="form-group">
            <label class="form-label">过期时间 (可选)</label>
            <input v-model="newKey.expires_at" type="datetime-local" class="form-input" />
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="newKey.is_default" type="checkbox" />
              设为默认密钥
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showAddKeyModal = false" class="btn btn-secondary">取消</button>
          <button @click="addKey" class="btn btn-primary" :disabled="!newKey.name || !newKey.raw_key">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'AIConfig',
  setup() {
    // 响应式数据
    const activeTab = ref('overview')
    const loading = ref(false)
    const testing = ref(false)
    const loadingModels = ref(false)
    
    // 数据状态
    const providers = ref([])
    const apiKeys = ref([])
    const models = ref([])
    const testResults = ref([])
    
    // 统计数据
    const statsTimeRange = ref('today')
    const analyticsTimeRange = ref('week')
    const totalCost = ref(0)
    const totalTokens = ref(0)
    const totalRequests = ref(0)
    
    // 模态框状态
    const showAddProviderModal = ref(false)
    const showAddKeyModal = ref(false)
    const showAddModelModal = ref(false)
    
    // 新增数据表单
    const newProvider = reactive({
      name: '',
      display_name: '',
      provider_type: 'openai',
      base_url: '',
      description: ''
    })
    
    const newKey = reactive({
      name: '',
      provider: null,
      raw_key: '',
      expires_at: '',
      is_default: false
    })
    
    // 标签页配置
    const tabs = [
      { key: 'overview', label: '概览', icon: 'icon-dashboard' },
      { key: 'providers', label: '提供商', icon: 'icon-provider' },
      { key: 'keys', label: 'API密钥', icon: 'icon-key' },
      { key: 'models', label: '模型配置', icon: 'icon-model' },
      { key: 'analytics', label: '统计分析', icon: 'icon-chart' }
    ]
    
    // 计算属性
    const overallStatus = computed(() => {
      return providers.value.some(p => p.is_healthy)
    })
    
    const onlineServicesCount = computed(() => {
      return providers.value.filter(p => p.is_healthy).length
    })
    
    const totalServicesCount = computed(() => {
      return providers.value.length
    })
    
    // 方法
    const loadProviders = async () => {
      try {
        loading.value = true
        // TODO: 调用实际API
        // const response = await aiConfigAPI.getProviders()
        // providers.value = response.data
        
        // 模拟数据
        providers.value = [
          {
            id: 1,
            name: 'openai',
            display_name: 'OpenAI',
            provider_type: 'openai',
            is_healthy: true,
            avg_response_time: 150,
            success_rate: 98.5
          },
          {
            id: 2,
            name: 'anthropic',
            display_name: 'Anthropic',
            provider_type: 'anthropic',
            is_healthy: false,
            avg_response_time: null,
            success_rate: 0
          }
        ]
      } catch (error) {
        ElMessage.error('加载提供商列表失败: ' + error.message)
      } finally {
        loading.value = false
      }
    }
    
    const loadApiKeys = async () => {
      try {
        // TODO: 调用实际API
        // const response = await aiConfigAPI.getApiKeys()
        // apiKeys.value = response.data
        
        // 模拟数据
        apiKeys.value = [
          {
            id: 1,
            name: 'OpenAI Production',
            provider_name: 'OpenAI',
            masked_key: 'sk-proj...abc123',
            is_active: true,
            is_default: true,
            is_expired: false,
            expires_at: '2024-12-31T23:59:59',
            last_used: '2024-08-31T10:30:00'
          }
        ]
      } catch (error) {
        ElMessage.error('加载API密钥失败: ' + error.message)
      }
    }
    
    const loadModels = async () => {
      try {
        // TODO: 调用实际API
        // const response = await aiConfigAPI.getModels()
        // models.value = response.data
        
        // 模拟数据
        models.value = [
          {
            id: 1,
            display_name: 'GPT-4',
            description: '最强大的GPT模型，适合复杂任务',
            max_tokens: 8192,
            supports_streaming: true,
            supports_vision: true,
            is_recommended: true,
            cost_per_1k_input_tokens: 0.03,
            cost_per_1k_output_tokens: 0.06
          }
        ]
      } catch (error) {
        ElMessage.error('加载模型列表失败: ' + error.message)
      }
    }
    
    const testAllConnections = async () => {
      testing.value = true
      testResults.value = []
      
      try {
        for (const provider of providers.value) {
          await new Promise(resolve => setTimeout(resolve, 500)) // 模拟延迟
          const success = Math.random() > 0.3
          
          testResults.value.push({
            service: provider.display_name,
            message: success ? '连接测试成功' : '连接测试失败',
            success
          })
        }
      } finally {
        testing.value = false
      }
    }
    
    const refreshProviders = async () => {
      await loadProviders()
      ElMessage.success('提供商状态已刷新')
    }
    
    const exportConfig = () => {
      const config = {
        providers: providers.value,
        keys: apiKeys.value.map(k => ({ ...k, raw_key: undefined })), // 不导出实际密钥
        models: models.value,
        exportTime: new Date().toISOString()
      }
      
      const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `ai-config-${new Date().toISOString().split('T')[0]}.json`
      a.click()
      URL.revokeObjectURL(url)
      
      ElMessage.success('配置已导出')
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString('zh-CN')
    }
    
    // 生命周期
    onMounted(async () => {
      await Promise.all([
        loadProviders(),
        loadApiKeys(),
        loadModels()
      ])
    })
    
    return {
      // 数据
      activeTab,
      loading,
      testing,
      loadingModels,
      providers,
      apiKeys,
      models,
      testResults,
      statsTimeRange,
      analyticsTimeRange,
      totalCost,
      totalTokens,
      totalRequests,
      
      // 模态框
      showAddProviderModal,
      showAddKeyModal,
      showAddModelModal,
      newProvider,
      newKey,
      
      // 配置
      tabs,
      
      // 计算属性
      overallStatus,
      onlineServicesCount,
      totalServicesCount,
      
      // 方法
      testAllConnections,
      refreshProviders,
      exportConfig,
      formatDate
    }
  }
}
</script>

<style scoped>
/* 基础样式 */
.ai-config-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f4ff 0%, #e6f3ff 100%);
  padding: 2rem 1rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.125rem;
  color: #4a5568;
}

/* 标签页导航 */
.tab-navigation {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  background: white;
  padding: 0.5rem;
  border-radius: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.75rem;
  background: transparent;
  color: #4a5568;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-button:hover {
  background: #f7fafc;
  color: #2d3748;
}

.tab-button.tab-active {
  background: #3182ce;
  color: white;
}

/* 标签页内容 */
.tab-content {
  min-height: 400px;
}

/* 概览页样式 */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.status-card,
.stats-card,
.quick-actions-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.card-content {
  padding: 1.5rem;
}

/* 服务状态样式 */
.service-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 0.5rem;
}

.service-name {
  font-weight: 500;
  color: #2d3748;
}

.service-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.service-response-time {
  font-size: 0.875rem;
  color: #4a5568;
}

/* 统计样式 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: #f7fafc;
  border-radius: 0.5rem;
}

.stat-label {
  display: block;
  font-size: 0.875rem;
  color: #4a5568;
  margin-bottom: 0.25rem;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #1a202c;
}

/* 快速操作样式 */
.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  color: white;
}

.test-btn {
  background: #3182ce;
}

.test-btn:hover:not(:disabled) {
  background: #2c5aa0;
}

.refresh-btn {
  background: #38a169;
}

.refresh-btn:hover:not(:disabled) {
  background: #2f855a;
}

.export-btn {
  background: #805ad5;
}

.export-btn:hover {
  background: #6b46c1;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 提供商页面样式 */
.providers-header,
.keys-header,
.models-header,
.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.providers-header h2,
.keys-header h2,
.models-header h2,
.analytics-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.add-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #3182ce;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.add-button:hover {
  background: #2c5aa0;
}

/* 网格布局 */
.providers-grid,
.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.provider-card,
.model-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 密钥列表样式 */
.keys-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.key-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.key-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.key-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.key-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.key-provider {
  font-size: 0.875rem;
  color: #4a5568;
}

.key-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.default-badge {
  background: #3182ce;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.key-content {
  padding: 1.5rem;
}

.key-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.875rem;
  color: #4a5568;
  font-weight: 500;
}

.detail-value {
  font-size: 0.875rem;
  color: #1a202c;
}

.masked-key {
  font-family: 'Courier New', monospace;
  background: #f7fafc;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.text-warning {
  color: #d69e2e !important;
}

/* 状态指示器 */
.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
}

.status-connected {
  background: #38a169;
  color: #38a169;
}

.status-disconnected {
  background: #e53e3e;
  color: #e53e3e;
}

.status-text {
  font-size: 0.875rem;
  font-weight: 500;
}

/* 图标按钮 */
.icon-btn {
  width: 2rem;
  height: 2rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-btn {
  background: #edf2f7;
  color: #4a5568;
}

.edit-btn:hover {
  background: #e2e8f0;
}

.delete-btn {
  background: #fed7d7;
  color: #e53e3e;
}

.delete-btn:hover {
  background: #feb2b2;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
}

.close-btn {
  width: 2rem;
  height: 2rem;
  border: none;
  background: transparent;
  font-size: 1.5rem;
  cursor: pointer;
  color: #4a5568;
}

.modal-body {
  padding: 1.5rem;
  max-height: 60vh;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

/* 表单样式 */
.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-textarea {
  min-height: 80px;
  resize: vertical;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3182ce;
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
}

/* 按钮样式 */
.btn {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary {
  background: #3182ce;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2c5aa0;
}

.btn-secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.btn-secondary:hover {
  background: #cbd5e0;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 结果显示样式 */
.results-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-top: 2rem;
}

.results-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 1rem;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid;
}

.result-success {
  background: #f0fff4;
  border-color: #9ae6b4;
}

.result-error {
  background: #fed7d7;
  border-color: #feb2b2;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.result-service {
  font-weight: 500;
  color: #1a202c;
}

.result-message {
  font-size: 0.875rem;
  color: #4a5568;
}

.result-status {
  font-size: 0.875rem;
  font-weight: 500;
}

/* 时间选择器 */
.time-range-select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

/* 分析页面样式 */
.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.chart-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.chart-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 1rem;
}

.chart-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  color: #4a5568;
  font-size: 1.125rem;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-config-container {
    padding: 1rem 0.5rem;
  }
  
  .tab-navigation {
    flex-wrap: wrap;
  }
  
  .overview-grid,
  .providers-grid,
  .models-grid,
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .modal-content {
    width: 95%;
    margin: 1rem;
  }
}

/* 图标类（使用CSS类或图标字体） */
.icon-dashboard::before { content: '📊'; }
.icon-provider::before { content: '🏢'; }
.icon-key::before { content: '🔑'; }
.icon-model::before { content: '🤖'; }
.icon-chart::before { content: '📈'; }
.icon-plus::before { content: '+'; }
.icon-edit::before { content: '✏️'; }
.icon-delete::before { content: '🗑️'; }
.icon-test::before { content: '🧪'; }
.icon-refresh::before { content: '🔄'; }
.icon-export::before { content: '📤'; }
</style>
