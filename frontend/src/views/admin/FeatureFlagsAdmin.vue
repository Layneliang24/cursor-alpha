<template>
  <div class="feature-flags-admin">
    <div class="admin-header">
      <h1>特性开关管理</h1>
      <div class="header-actions">
        <button @click="refreshFlags" :disabled="loading" class="refresh-btn">
          <i class="icon-refresh"></i>
          {{ loading ? '刷新中...' : '刷新' }}
        </button>
        <button @click="showCreateModal = true" class="create-btn">
          <i class="icon-plus"></i>
          新建特性开关
        </button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-value">{{ totalFlags }}</div>
        <div class="stat-label">总数</div>
      </div>
      <div class="stat-card enabled">
        <div class="stat-value">{{ enabledFlags }}</div>
        <div class="stat-label">已启用</div>
      </div>
      <div class="stat-card rollout">
        <div class="stat-value">{{ rolloutFlags }}</div>
        <div class="stat-label">灰度中</div>
      </div>
      <div class="stat-card disabled">
        <div class="stat-value">{{ disabledFlags }}</div>
        <div class="stat-label">已禁用</div>
      </div>
    </div>

    <!-- 过滤器 -->
    <div class="filters">
      <div class="filter-group">
        <label>状态:</label>
        <select v-model="filters.status" @change="applyFilters">
          <option value="">全部</option>
          <option value="enabled">已启用</option>
          <option value="disabled">已禁用</option>
          <option value="rollout">灰度发布</option>
          <option value="deprecated">已废弃</option>
        </select>
      </div>
      <div class="filter-group">
        <label>环境:</label>
        <select v-model="filters.environment" @change="applyFilters">
          <option value="">全部</option>
          <option value="development">开发环境</option>
          <option value="staging">测试环境</option>
          <option value="production">生产环境</option>
        </select>
      </div>
      <div class="filter-group">
        <label>搜索:</label>
        <input 
          v-model="filters.search" 
          @input="applyFilters" 
          placeholder="搜索特性开关名称或键"
          class="search-input"
        >
      </div>
    </div>

    <!-- 特性开关列表 -->
    <div class="flags-table-container">
      <table class="flags-table">
        <thead>
          <tr>
            <th>名称</th>
            <th>键</th>
            <th>状态</th>
            <th>目标类型</th>
            <th>灰度百分比</th>
            <th>环境</th>
            <th>更新时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading" class="loading-row">
            <td colspan="8" class="text-center">
              <div class="loading-spinner"></div>
              加载中...
            </td>
          </tr>
          <tr v-else-if="filteredFlags.length === 0" class="empty-row">
            <td colspan="8" class="text-center">
              {{ flags.length === 0 ? '暂无特性开关' : '没有符合条件的特性开关' }}
            </td>
          </tr>
          <tr v-else v-for="flag in filteredFlags" :key="flag.key" class="flag-row">
            <td>
              <div class="flag-name">
                <strong>{{ flag.name }}</strong>
                <div class="flag-description">{{ flag.description }}</div>
              </div>
            </td>
            <td>
              <code class="flag-key">{{ flag.key }}</code>
            </td>
            <td>
              <span class="status-badge" :class="flag.status">
                {{ getStatusText(flag.status) }}
              </span>
            </td>
            <td>
              <span class="target-type">{{ getTargetTypeText(flag.target_type) }}</span>
            </td>
            <td>
              <span v-if="flag.target_type === 'percentage'" class="percentage">
                {{ flag.rollout_percentage }}%
              </span>
              <span v-else class="na">-</span>
            </td>
            <td>
              <div class="environments">
                <span 
                  v-for="env in flag.environments" 
                  :key="env" 
                  class="env-tag"
                  :class="env"
                >
                  {{ env }}
                </span>
              </div>
            </td>
            <td>
              <div class="update-time">
                {{ formatDate(flag.updated_at) }}
              </div>
            </td>
            <td>
              <div class="actions">
                <button 
                  @click="toggleFlag(flag)" 
                  :class="flag.status === 'enabled' ? 'disable-btn' : 'enable-btn'"
                  class="action-btn"
                >
                  {{ flag.status === 'enabled' ? '禁用' : '启用' }}
                </button>
                <button @click="editFlag(flag)" class="action-btn edit-btn">
                  编辑
                </button>
                <button @click="viewStats(flag)" class="action-btn stats-btn">
                  统计
                </button>
                <button @click="deleteFlag(flag)" class="action-btn delete-btn">
                  删除
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div v-if="pagination.total > pagination.pageSize" class="pagination">
      <button 
        @click="changePage(pagination.current - 1)" 
        :disabled="pagination.current === 1"
        class="page-btn"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ pagination.current }} 页，共 {{ Math.ceil(pagination.total / pagination.pageSize) }} 页
      </span>
      <button 
        @click="changePage(pagination.current + 1)" 
        :disabled="pagination.current >= Math.ceil(pagination.total / pagination.pageSize)"
        class="page-btn"
      >
        下一页
      </button>
    </div>

    <!-- 创建/编辑模态框 -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModals">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ showCreateModal ? '新建特性开关' : '编辑特性开关' }}</h3>
          <button @click="closeModals" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveFlag">
            <div class="form-group">
              <label>名称 *</label>
              <input v-model="flagForm.name" required class="form-input">
            </div>
            <div class="form-group">
              <label>键 *</label>
              <input v-model="flagForm.key" required class="form-input" :disabled="showEditModal">
            </div>
            <div class="form-group">
              <label>描述</label>
              <textarea v-model="flagForm.description" class="form-textarea"></textarea>
            </div>
            <div class="form-group">
              <label>状态</label>
              <select v-model="flagForm.status" class="form-select">
                <option value="disabled">禁用</option>
                <option value="enabled">启用</option>
                <option value="rollout">灰度发布</option>
                <option value="deprecated">已废弃</option>
              </select>
            </div>
            <div class="form-group">
              <label>目标类型</label>
              <select v-model="flagForm.target_type" class="form-select">
                <option value="all">所有用户</option>
                <option value="percentage">百分比</option>
                <option value="users">指定用户</option>
                <option value="attributes">用户属性</option>
              </select>
            </div>
            <div v-if="flagForm.target_type === 'percentage'" class="form-group">
              <label>灰度百分比</label>
              <input 
                v-model.number="flagForm.rollout_percentage" 
                type="number" 
                min="0" 
                max="100" 
                class="form-input"
              >
            </div>
            <div class="form-group">
              <label>环境</label>
              <div class="checkbox-group">
                <label class="checkbox-label">
                  <input 
                    type="checkbox" 
                    value="development" 
                    v-model="flagForm.environments"
                  >
                  开发环境
                </label>
                <label class="checkbox-label">
                  <input 
                    type="checkbox" 
                    value="staging" 
                    v-model="flagForm.environments"
                  >
                  测试环境
                </label>
                <label class="checkbox-label">
                  <input 
                    type="checkbox" 
                    value="production" 
                    v-model="flagForm.environments"
                  >
                  生产环境
                </label>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeModals" class="cancel-btn">
                取消
              </button>
              <button type="submit" :disabled="saving" class="save-btn">
                {{ saving ? '保存中...' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 统计模态框 -->
    <div v-if="showStatsModal" class="modal-overlay" @click="closeModals">
      <div class="modal stats-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ currentFlag?.name }} - 使用统计</h3>
          <button @click="closeModals" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div v-if="statsLoading" class="loading-stats">
            <div class="loading-spinner"></div>
            加载统计数据中...
          </div>
          <div v-else-if="stats" class="stats-content">
            <div class="stats-summary">
              <div class="stat-item">
                <div class="stat-number">{{ stats.total_requests }}</div>
                <div class="stat-text">总请求数</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ stats.enabled_requests }}</div>
                <div class="stat-text">启用次数</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ stats.enabled_percentage.toFixed(1) }}%</div>
                <div class="stat-text">启用率</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ stats.unique_users }}</div>
                <div class="stat-text">独立用户</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, reactive } from 'vue'
import { api } from '@/api/index'

export default {
  name: 'FeatureFlagsAdmin',
  
  setup() {
    // 响应式数据
    const flags = ref([])
    const loading = ref(false)
    const saving = ref(false)
    const statsLoading = ref(false)
    const stats = ref(null)
    const currentFlag = ref(null)
    
    // 模态框状态
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showStatsModal = ref(false)
    
    // 过滤器
    const filters = reactive({
      status: '',
      environment: '',
      search: ''
    })
    
    // 分页
    const pagination = reactive({
      current: 1,
      pageSize: 20,
      total: 0
    })
    
    // 表单数据
    const flagForm = reactive({
      name: '',
      key: '',
      description: '',
      status: 'disabled',
      target_type: 'all',
      rollout_percentage: 0,
      environments: ['development']
    })
    
    // 计算属性
    const totalFlags = computed(() => flags.value.length)
    const enabledFlags = computed(() => flags.value.filter(f => f.status === 'enabled').length)
    const rolloutFlags = computed(() => flags.value.filter(f => f.status === 'rollout').length)
    const disabledFlags = computed(() => flags.value.filter(f => f.status === 'disabled').length)
    
    const filteredFlags = computed(() => {
      let result = flags.value
      
      if (filters.status) {
        result = result.filter(f => f.status === filters.status)
      }
      
      if (filters.environment) {
        result = result.filter(f => f.environments.includes(filters.environment))
      }
      
      if (filters.search) {
        const search = filters.search.toLowerCase()
        result = result.filter(f => 
          f.name.toLowerCase().includes(search) || 
          f.key.toLowerCase().includes(search)
        )
      }
      
      return result
    })
    
    // 方法
    const fetchFlags = async () => {
      try {
        loading.value = true
        const response = await api.get('/api/feature-flags/')
        flags.value = response.data.results || response.data
        pagination.total = response.data.count || flags.value.length
      } catch (error) {
        console.error('Failed to fetch feature flags:', error)
      } finally {
        loading.value = false
      }
    }
    
    const refreshFlags = () => {
      fetchFlags()
    }
    
    const applyFilters = () => {
      pagination.current = 1
    }
    
    const changePage = (page) => {
      pagination.current = page
    }
    
    const toggleFlag = async (flag) => {
      try {
        const newStatus = flag.status === 'enabled' ? 'disabled' : 'enabled'
        await api.post(`/api/feature-flags/${flag.key}/toggle/`, {
          status: newStatus
        })
        await fetchFlags()
      } catch (error) {
        console.error('Failed to toggle feature flag:', error)
      }
    }
    
    const editFlag = (flag) => {
      currentFlag.value = flag
      Object.assign(flagForm, {
        name: flag.name,
        key: flag.key,
        description: flag.description,
        status: flag.status,
        target_type: flag.target_type,
        rollout_percentage: flag.rollout_percentage,
        environments: [...flag.environments]
      })
      showEditModal.value = true
    }
    
    const deleteFlag = async (flag) => {
      if (!confirm(`确定要删除特性开关 "${flag.name}" 吗？`)) {
        return
      }
      
      try {
        await api.delete(`/api/feature-flags/${flag.key}/`)
        await fetchFlags()
      } catch (error) {
        console.error('Failed to delete feature flag:', error)
      }
    }
    
    const viewStats = async (flag) => {
      currentFlag.value = flag
      showStatsModal.value = true
      
      try {
        statsLoading.value = true
        const response = await api.get(`/api/feature-flags/${flag.key}/stats/`)
        stats.value = response.data
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      } finally {
        statsLoading.value = false
      }
    }
    
    const saveFlag = async () => {
      try {
        saving.value = true
        
        if (showCreateModal.value) {
          await api.post('/api/feature-flags/', flagForm)
        } else {
          await api.put(`/api/feature-flags/${flagForm.key}/`, flagForm)
        }
        
        await fetchFlags()
        closeModals()
      } catch (error) {
        console.error('Failed to save feature flag:', error)
      } finally {
        saving.value = false
      }
    }
    
    const closeModals = () => {
      showCreateModal.value = false
      showEditModal.value = false
      showStatsModal.value = false
      currentFlag.value = null
      stats.value = null
      
      // 重置表单
      Object.assign(flagForm, {
        name: '',
        key: '',
        description: '',
        status: 'disabled',
        target_type: 'all',
        rollout_percentage: 0,
        environments: ['development']
      })
    }
    
    const getStatusText = (status) => {
      const statusMap = {
        enabled: '已启用',
        disabled: '已禁用',
        rollout: '灰度发布',
        deprecated: '已废弃'
      }
      return statusMap[status] || status
    }
    
    const getTargetTypeText = (targetType) => {
      const typeMap = {
        all: '所有用户',
        percentage: '百分比',
        users: '指定用户',
        attributes: '用户属性'
      }
      return typeMap[targetType] || targetType
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString('zh-CN')
    }
    
    // 生命周期
    onMounted(() => {
      fetchFlags()
    })
    
    return {
      // 响应式数据
      flags,
      loading,
      saving,
      statsLoading,
      stats,
      currentFlag,
      showCreateModal,
      showEditModal,
      showStatsModal,
      filters,
      pagination,
      flagForm,
      
      // 计算属性
      totalFlags,
      enabledFlags,
      rolloutFlags,
      disabledFlags,
      filteredFlags,
      
      // 方法
      refreshFlags,
      applyFilters,
      changePage,
      toggleFlag,
      editFlag,
      deleteFlag,
      viewStats,
      saveFlag,
      closeModals,
      getStatusText,
      getTargetTypeText,
      formatDate
    }
  }
}
</script>

<style scoped>
.feature-flags-admin {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.admin-header h1 {
  margin: 0;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.refresh-btn,
.create-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.refresh-btn {
  background: #f8f9fa;
  color: #495057;
  border: 1px solid #dee2e6;
}

.refresh-btn:hover {
  background: #e9ecef;
}

.create-btn {
  background: #007bff;
  color: white;
}

.create-btn:hover {
  background: #0056b3;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
  border-left: 4px solid #dee2e6;
}

.stat-card.enabled {
  border-left-color: #28a745;
}

.stat-card.rollout {
  border-left-color: #ffc107;
}

.stat-card.disabled {
  border-left-color: #6c757d;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 8px;
}

.stat-label {
  color: #6c757d;
  font-size: 14px;
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 500;
  color: #495057;
}

.filter-group select,
.search-input {
  padding: 6px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
}

.search-input {
  min-width: 200px;
}

.flags-table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.flags-table {
  width: 100%;
  border-collapse: collapse;
}

.flags-table th {
  background: #f8f9fa;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 1px solid #dee2e6;
}

.flags-table td {
  padding: 12px;
  border-bottom: 1px solid #f1f3f4;
}

.flag-name strong {
  color: #2c3e50;
}

.flag-description {
  font-size: 12px;
  color: #6c757d;
  margin-top: 4px;
}

.flag-key {
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.enabled {
  background: #d4edda;
  color: #155724;
}

.status-badge.disabled {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.rollout {
  background: #fff3cd;
  color: #856404;
}

.status-badge.deprecated {
  background: #e2e3e5;
  color: #383d41;
}

.environments {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.env-tag {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
}

.env-tag.development {
  background: #cce5ff;
  color: #004085;
}

.env-tag.staging {
  background: #ffe6cc;
  color: #8a4100;
}

.env-tag.production {
  background: #ffcccc;
  color: #850000;
}

.actions {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 3px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.enable-btn {
  background: #28a745;
  color: white;
}

.disable-btn {
  background: #dc3545;
  color: white;
}

.edit-btn {
  background: #007bff;
  color: white;
}

.stats-btn {
  background: #17a2b8;
  color: white;
}

.delete-btn {
  background: #6c757d;
  color: white;
}

.action-btn:hover {
  opacity: 0.8;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #6c757d;
  font-size: 14px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #dee2e6;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6c757d;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #495057;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.checkbox-group {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: normal;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.cancel-btn,
.save-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn {
  background: #6c757d;
  color: white;
}

.save-btn {
  background: #007bff;
  color: white;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  display: inline-block;
  margin-right: 8px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.text-center {
  text-align: center;
}

.loading-row td,
.empty-row td {
  padding: 40px 12px;
  color: #6c757d;
}

.stats-modal {
  max-width: 800px;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 4px;
}

.stat-text {
  font-size: 12px;
  color: #6c757d;
}

.loading-stats {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .feature-flags-admin {
    padding: 16px;
  }
  
  .admin-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .filters {
    flex-direction: column;
  }
  
  .flags-table-container {
    overflow-x: auto;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .modal {
    width: 95%;
    margin: 20px;
  }
}
</style>