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
                <div class="status-dot" :class="aiConfigStore.overallHealthy ? 'status-connected' : 'status-disconnected'"></div>
                <span class="status-text">{{ aiConfigStore.onlineProviders }}/{{ aiConfigStore.totalProviders }} 在线</span>
              </div>
            </div>
            <div class="card-content">
              <div class="service-list">
                <div v-for="provider in aiConfigStore.providers" :key="provider.id" class="service-item">
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
              <h3 class="card-title">Token消费</h3>
              <select v-model="statsTimeRange" class="time-range-select">
                <option value="today">今天</option>
                <option value="week">本周</option>
                <option value="month">本月</option>
              </select>
            </div>
            <div class="card-content">
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-value">{{ totalTokens.toLocaleString() }}</div>
                  <div class="stat-label">总Token数</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">${{ totalCost.toFixed(2) }}</div>
                  <div class="stat-label">总费用</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ totalRequests }}</div>
                  <div class="stat-label">请求次数</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 提供商管理页 -->
      <div v-if="activeTab === 'providers'" class="tab-content">
        <ProviderList 
          @add="handleAddProvider"
          @edit="handleEditProvider"
          @delete="handleProviderDeleted"
        />
        
        <!-- 提供商表单对话框 -->
        <ProviderForm
          v-model:visible="showProviderForm"
          :provider="currentProvider"
          @success="handleProviderFormSuccess"
        />
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
          <div v-for="key in aiConfigStore.apiKeys" :key="key.id" class="key-card">
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
                  <span class="detail-value">
                    {{ key.last_used_at ? formatDate(key.last_used_at) : '从未使用' }}
                  </span>
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
          <button @click="showAddModelModal = true" class="add-button">
            <i class="icon-plus"></i>
            添加模型
          </button>
        </div>

        <div class="models-grid">
          <div v-for="model in aiConfigStore.models" :key="model.id" class="model-card">
            <div class="card-header">
              <h3 class="card-title">{{ model.model_name }}</h3>
              <div class="model-actions">
                <button @click="editModel(model)" class="icon-btn edit-btn">
                  <i class="icon-edit"></i>
                </button>
                <button @click="deleteModel(model)" class="icon-btn delete-btn">
                  <i class="icon-delete"></i>
                </button>
              </div>
            </div>
            <div class="card-content">
              <div class="model-info">
                <div class="info-item">
                  <span class="info-label">提供商:</span>
                  <span class="info-value">{{ model.provider_name }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">类型:</span>
                  <span class="info-value">{{ model.model_type }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">上下文长度:</span>
                  <span class="info-value">{{ model.context_length?.toLocaleString() || '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">输入价格:</span>
                  <span class="info-value">${{ model.input_price_per_1k || 0 }}/1K</span>
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
          <select v-model="analyticsTimeRange" class="time-range-select">
            <option value="day">今天</option>
            <option value="week">本周</option>
            <option value="month">本月</option>
            <option value="quarter">本季度</option>
          </select>
        </div>

        <div class="analytics-grid">
          <div class="analytics-card">
            <h3>Token使用趋势</h3>
            <div class="chart-placeholder">
              <p>图表组件待实现</p>
            </div>
          </div>
          
          <div class="analytics-card">
            <h3>费用分析</h3>
            <div class="chart-placeholder">
              <p>费用图表待实现</p>
            </div>
          </div>
          
          <div class="analytics-card">
            <h3>提供商使用分布</h3>
            <div class="chart-placeholder">
              <p>分布图表待实现</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ProviderList from '@/components/ai-config/ProviderList.vue'
import ProviderForm from '@/components/ai-config/ProviderForm.vue'
import { useAIConfigStore } from '@/stores/modules/aiConfigStore'

export default {
  name: 'AIConfig',
  components: {
    ProviderList,
    ProviderForm
  },
  setup() {
    // 使用AI配置store
    const aiConfigStore = useAIConfigStore()
    
    // 响应式数据
    const activeTab = ref('overview')
    
    // 提供商表单相关状态
    const showProviderForm = ref(false)
    const currentProvider = ref(null)
    
    // 统计数据
    const statsTimeRange = ref('today')
    const analyticsTimeRange = ref('week')
    const totalCost = ref(0)
    const totalTokens = ref(0)
    const totalRequests = ref(0)
    
    // 其他模态框状态
    const showAddKeyModal = ref(false)
    const showAddModelModal = ref(false)
    
    // 表单数据
    const newKey = reactive({
      name: '',
      provider: '',
      key: '',
      expires_at: null
    })
    
    // 标签页配置
    const tabs = [
      { key: 'overview', label: '概览', icon: 'icon-dashboard' },
      { key: 'providers', label: '提供商管理', icon: 'icon-server' },
      { key: 'keys', label: 'API密钥', icon: 'icon-key' },
      { key: 'models', label: '模型配置', icon: 'icon-brain' },
      { key: 'analytics', label: '统计分析', icon: 'icon-chart' }
    ]
    
    // 提供商管理相关方法
    const handleAddProvider = () => {
      currentProvider.value = null
      showProviderForm.value = true
    }

    const handleEditProvider = (provider) => {
      currentProvider.value = provider
      showProviderForm.value = true
    }

    const handleProviderDeleted = () => {
      // 提供商删除后的处理，ProviderList组件已经处理了store更新
      ElMessage.success('提供商删除成功')
    }

    const handleProviderFormSuccess = () => {
      // 表单提交成功后的处理
      showProviderForm.value = false
      currentProvider.value = null
    }
    
    // 其他方法（保留原有的API密钥和模型管理方法）
    const editKey = (key) => {
      // TODO: 实现编辑API密钥功能
      console.log('编辑API密钥:', key)
    }

    const deleteKey = async (key) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除API密钥 "${key.name}" 吗？`,
          '确认删除',
          {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning',
          }
        )
        
        await aiConfigStore.deleteAPIKey(key.id)
        ElMessage.success('API密钥删除成功')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除API密钥失败')
        }
      }
    }

    const editModel = (model) => {
      // TODO: 实现编辑模型功能
      console.log('编辑模型:', model)
    }

    const deleteModel = async (model) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除模型 "${model.model_name}" 吗？`,
          '确认删除',
          {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning',
          }
        )
        
        // TODO: 实现删除模型API调用
        ElMessage.success('模型删除成功')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除模型失败')
        }
      }
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString('zh-CN')
    }
    
    // 生命周期
    onMounted(async () => {
      try {
        await aiConfigStore.initializeData()
      } catch (error) {
        ElMessage.error('初始化数据失败')
        console.error('初始化错误:', error)
      }
    })
    
    return {
      // Store
      aiConfigStore,
      
      // 数据
      activeTab,
      statsTimeRange,
      analyticsTimeRange,
      totalCost,
      totalTokens,
      totalRequests,
      
      // 提供商表单状态
      showProviderForm,
      currentProvider,
      
      // 其他模态框
      showAddKeyModal,
      showAddModelModal,
      newKey,
      
      // 配置
      tabs,
      
      // 提供商管理方法
      handleAddProvider,
      handleEditProvider,
      handleProviderDeleted,
      handleProviderFormSuccess,
      
      // 其他方法
      editKey,
      deleteKey,
      editModel,
      deleteModel,
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
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.1rem;
  color: #666;
  margin: 0;
}

/* 标签页导航 */
.tab-navigation {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  background: white;
  padding: 0.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  color: #666;
}

.tab-button:hover {
  background: #f8f9ff;
  color: #667eea;
}

.tab-button.tab-active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

/* 标签页内容 */
.tab-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* 概览页样式 */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.status-card, .stats-card {
  background: #f8f9ff;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e6f3ff;
}

.card-header {
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-connected {
  background: #52c41a;
}

.status-disconnected {
  background: #ff4d4f;
}

.status-text {
  font-size: 0.9rem;
  color: #666;
}

.service-list {
  space-y: 0.75rem;
}

.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e6f3ff;
}

.service-name {
  font-weight: 500;
  color: #333;
}

.service-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.service-response-time {
  font-size: 0.8rem;
  color: #666;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e6f3ff;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

.time-range-select {
  padding: 0.5rem;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  background: white;
  cursor: pointer;
}

/* 其他页面的基础样式 */
.keys-header, .models-header, .analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.keys-header h2, .models-header h2, .analytics-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.add-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.add-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 卡片列表样式 */
.keys-list, .models-grid {
  display: grid;
  gap: 1.5rem;
}

.models-grid {
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
}

.key-card, .model-card {
  background: #f8f9ff;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e6f3ff;
  transition: all 0.3s ease;
}

.key-card:hover, .model-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.key-header, .card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.key-info {
  flex: 1;
}

.key-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.25rem 0;
}

.key-provider {
  font-size: 0.9rem;
  color: #666;
}

.key-actions, .model-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.default-badge {
  background: #52c41a;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.icon-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.edit-btn {
  background: #e6f7ff;
  color: #1890ff;
}

.edit-btn:hover {
  background: #bae7ff;
}

.delete-btn {
  background: #fff2f0;
  color: #ff4d4f;
}

.delete-btn:hover {
  background: #ffccc7;
}

.key-details, .model-info {
  display: grid;
  gap: 0.75rem;
}

.detail-item, .info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label, .info-label {
  font-weight: 500;
  color: #666;
  font-size: 0.9rem;
}

.detail-value, .info-value {
  color: #333;
  font-size: 0.9rem;
}

.masked-key {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  background: #f0f0f0;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.text-warning {
  color: #faad14;
}

/* 统计分析页样式 */
.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.analytics-card {
  background: #f8f9ff;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e6f3ff;
}

.analytics-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 1rem 0;
}

.chart-placeholder {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 8px;
  border: 2px dashed #d9d9d9;
  color: #999;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-config-container {
    padding: 1rem 0.5rem;
  }
  
  .tab-navigation {
    flex-wrap: wrap;
    gap: 0.25rem;
  }
  
  .tab-button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
  
  .overview-grid, .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .models-grid {
    grid-template-columns: 1fr;
  }
}
</style>
