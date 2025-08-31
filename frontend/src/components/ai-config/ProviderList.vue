<template>
  <div class="provider-list">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button 
          v-permission="'ai_config.create'"
          type="primary" 
          @click="handleAdd" 
          :icon="Plus"
        >
          添加提供商
        </el-button>
        <el-button 
          v-permission="'ai_config.test'"
          type="success" 
          @click="handleBatchTest" 
          :loading="batchTesting"
          :icon="Connection"
        >
          批量测试
        </el-button>
        <el-button @click="handleRefresh" :icon="Refresh">
          刷新
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-input
          v-model="searchText"
          placeholder="搜索提供商..."
          :prefix-icon="Search"
          clearable
          style="width: 250px"
        />
      </div>
    </div>

    <!-- 提供商列表表格 -->
    <el-table
      :data="filteredProviders"
      v-loading="loading"
      element-loading-text="加载中..."
      stripe
      border
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      
      <el-table-column prop="display_name" label="提供商" min-width="120">
        <template #default="{ row }">
          <div class="provider-info">
            <div class="provider-icon">
              <i :class="getProviderIcon(row.provider_type)"></i>
            </div>
            <div class="provider-details">
              <div class="provider-name">{{ row.display_name }}</div>
              <div class="provider-type">{{ row.provider_type }}</div>
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="api_endpoint" label="API端点" min-width="200">
        <template #default="{ row }">
          <el-text class="api-endpoint" truncated>{{ row.api_endpoint }}</el-text>
        </template>
      </el-table-column>

      <el-table-column label="健康状态" width="120" align="center">
        <template #default="{ row }">
          <el-tag 
            :type="getHealthTagType(row.is_healthy)" 
            :icon="getHealthIcon(row.is_healthy)"
            size="small"
          >
            {{ row.is_healthy ? '健康' : '异常' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="响应时间" width="100" align="center">
        <template #default="{ row }">
          <span class="response-time">
            {{ row.avg_response_time ? `${row.avg_response_time}ms` : '-' }}
          </span>
        </template>
      </el-table-column>

      <el-table-column label="API密钥数" width="100" align="center">
        <template #default="{ row }">
          <el-badge :value="row.api_keys_count" :max="99">
            <el-button size="small" text>密钥</el-button>
          </el-badge>
        </template>
      </el-table-column>

      <el-table-column prop="is_active" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-switch
            v-model="row.is_active"
            @change="handleToggleActive(row)"
            :loading="row.updating"
          />
        </template>
      </el-table-column>

      <el-table-column label="最后更新" width="150">
        <template #default="{ row }">
          <div class="update-time">
            {{ formatTime(row.updated_at) }}
          </div>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-tooltip content="测试连接" placement="top">
              <el-button 
                v-permission="'ai_config.test'"
                size="small" 
                type="success" 
                :icon="Connection"
                @click="handleTest(row)"
                :loading="row.testing"
                circle
              />
            </el-tooltip>
            <el-tooltip content="编辑" placement="top">
              <el-button 
                v-permission="'ai_config.edit'"
                size="small" 
                type="primary" 
                :icon="Edit"
                @click="handleEdit(row)"
                circle
              />
            </el-tooltip>
            <el-tooltip content="删除" placement="top">
              <el-button 
                v-permission="'ai_config.delete'"
                size="small" 
                type="danger" 
                :icon="Delete"
                @click="handleDelete(row)"
                circle
              />
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Connection, 
  Refresh, 
  Search, 
  Edit, 
  Delete,
  SuccessFilled,
  WarningFilled 
} from '@element-plus/icons-vue'
import { useAIConfigStore } from '@/stores/modules/aiConfigStore'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

// 使用Pinia store
const aiConfigStore = useAIConfigStore()

// 响应式数据
const loading = ref(false)
const batchTesting = ref(false)
const searchText = ref('')
const selectedProviders = ref([])
const currentPage = ref(1)
const pageSize = ref(20)

// 计算属性
const filteredProviders = computed(() => {
  const providers = aiConfigStore.providers || []
  if (!searchText.value) {
    return providers
  }
  return providers.filter(provider => 
    provider.display_name.toLowerCase().includes(searchText.value.toLowerCase()) ||
    provider.provider_type.toLowerCase().includes(searchText.value.toLowerCase()) ||
    provider.api_endpoint.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

const total = computed(() => filteredProviders.value.length)

// 事件处理
const emit = defineEmits(['add', 'edit', 'delete'])

// 生命周期
onMounted(() => {
  loadProviders()
})

// 方法
const loadProviders = async () => {
  loading.value = true
  try {
    await aiConfigStore.fetchProviders()
  } catch (error) {
    ElMessage.error('加载提供商列表失败')
    console.error('Load providers error:', error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  emit('add')
}

const handleEdit = (provider) => {
  emit('edit', provider)
}

const handleDelete = async (provider) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除提供商 "${provider.display_name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await aiConfigStore.deleteProvider(provider.id)
    ElMessage.success('删除成功')
    emit('delete', provider)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('Delete provider error:', error)
    }
  }
}

const handleTest = async (provider) => {
  provider.testing = true
  try {
    const result = await aiConfigStore.testProviderConnection(provider.id)
    if (result.is_healthy) {
      ElMessage.success(`${provider.display_name} 连接测试成功`)
    } else {
      ElMessage.error(`${provider.display_name} 连接测试失败: ${result.error}`)
    }
    // 更新提供商状态
    await loadProviders()
  } catch (error) {
    ElMessage.error(`${provider.display_name} 连接测试失败`)
    console.error('Test connection error:', error)
  } finally {
    provider.testing = false
  }
}

const handleBatchTest = async () => {
  if (selectedProviders.value.length === 0) {
    ElMessage.warning('请先选择要测试的提供商')
    return
  }

  batchTesting.value = true
  try {
    const results = await aiConfigStore.batchTestProviders(
      selectedProviders.value.map(p => p.id)
    )
    
    const successCount = results.filter(r => r.is_healthy).length
    const totalCount = results.length
    
    if (successCount === totalCount) {
      ElMessage.success(`批量测试完成，${successCount}/${totalCount} 个提供商连接正常`)
    } else {
      ElMessage.warning(`批量测试完成，${successCount}/${totalCount} 个提供商连接正常`)
    }
    
    // 刷新列表
    await loadProviders()
  } catch (error) {
    ElMessage.error('批量测试失败')
    console.error('Batch test error:', error)
  } finally {
    batchTesting.value = false
  }
}

const handleToggleActive = async (provider) => {
  provider.updating = true
  try {
    await aiConfigStore.updateProvider(provider.id, { is_active: provider.is_active })
    ElMessage.success(`${provider.display_name} 状态更新成功`)
  } catch (error) {
    // 回滚状态
    provider.is_active = !provider.is_active
    ElMessage.error('状态更新失败')
    console.error('Toggle active error:', error)
  } finally {
    provider.updating = false
  }
}

const handleRefresh = () => {
  loadProviders()
}

const handleSelectionChange = (selection) => {
  selectedProviders.value = selection
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 工具函数
const getProviderIcon = (providerType) => {
  const iconMap = {
    'openai': 'fas fa-robot',
    'anthropic': 'fas fa-brain',
    'google': 'fab fa-google',
    'azure': 'fab fa-microsoft',
    'local': 'fas fa-server',
    'chenmoai': 'fas fa-cloud',
    'openrouter': 'fas fa-route',
    'siliconflow': 'fas fa-microchip'
  }
  return iconMap[providerType] || 'fas fa-cog'
}

const getHealthTagType = (isHealthy) => {
  return isHealthy ? 'success' : 'danger'
}

const getHealthIcon = (isHealthy) => {
  return isHealthy ? SuccessFilled : WarningFilled
}

const formatTime = (time) => {
  if (!time) return '-'
  try {
    return formatDistanceToNow(new Date(time), { 
      addSuffix: true,
      locale: zhCN 
    })
  } catch {
    return time
  }
}
</script>

<style scoped lang="scss">
.provider-list {
  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 16px 0;
    
    .toolbar-left {
      display: flex;
      gap: 12px;
    }
  }

  .provider-info {
    display: flex;
    align-items: center;
    gap: 12px;

    .provider-icon {
      width: 32px;
      height: 32px;
      border-radius: 6px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 14px;
    }

    .provider-details {
      .provider-name {
        font-weight: 500;
        color: #303133;
        margin-bottom: 2px;
      }

      .provider-type {
        font-size: 12px;
        color: #909399;
        text-transform: uppercase;
      }
    }
  }

  .api-endpoint {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 12px;
    color: #606266;
  }

  .response-time {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 12px;
    color: #67c23a;
  }

  .update-time {
    font-size: 12px;
    color: #909399;
  }

  .action-buttons {
    display: flex;
    gap: 4px;
  }

  .pagination-wrapper {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}

// 状态指示器样式
.status-connected {
  color: #67c23a;
}

.status-disconnected {
  color: #f56c6c;
}

// Element Plus 表格自定义样式
:deep(.el-table) {
  .el-table__header {
    th {
      background-color: #f8f9fa;
      color: #303133;
      font-weight: 500;
    }
  }
  
  .el-table__row {
    &:hover {
      background-color: #f5f7fa;
    }
  }
}
</style>
