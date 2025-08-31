<template>
  <div class="model-browser">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button-group>
          <el-button
            :type="viewMode === 'grid' ? 'primary' : ''"
            @click="viewMode = 'grid'"
            :icon="Grid"
          >
            网格视图
          </el-button>
          <el-button
            :type="viewMode === 'list' ? 'primary' : ''"
            @click="viewMode = 'list'"
            :icon="List"
          >
            列表视图
          </el-button>
        </el-button-group>
        
        <el-button @click="handleRefresh" :icon="Refresh" :loading="loading">
          刷新
        </el-button>
        
        <el-button 
          v-if="selectedModels.length > 0"
          @click="handleCompare"
          type="success"
          :icon="TrendCharts"
        >
          对比 ({{ selectedModels.length }})
        </el-button>
      </div>
      
      <div class="toolbar-right">
        <SearchFilter 
          @search="handleSearch" 
          @filter="handleFilter"
          :total="filteredModels.length"
        />
      </div>
    </div>

    <!-- 模型列表 -->
    <div class="model-content" v-loading="loading" element-loading-text="加载模型中...">
      <!-- 网格视图 -->
      <div v-if="viewMode === 'grid'" class="grid-view">
        <el-row :gutter="20">
          <el-col 
            v-for="model in paginatedModels" 
            :key="model.id"
            :xs="24" :sm="12" :md="8" :lg="6" :xl="4"
            class="model-col"
          >
            <ModelCard 
              :model="model"
              :is-selected="isModelSelected(model)"
              :is-favorite="isModelFavorite(model)"
              @select="handleModelSelect"
              @favorite="handleModelFavorite"
              @view-details="handleViewDetails"
            />
          </el-col>
        </el-row>
        
        <!-- 无数据提示 -->
        <el-empty 
          v-if="filteredModels.length === 0 && !loading"
          description="没有找到匹配的模型"
          :image-size="100"
        />
      </div>
      
      <!-- 列表视图 -->
      <div v-else class="list-view">
        <el-table
          :data="paginatedModels"
          @selection-change="handleSelectionChange"
          stripe
          border
          height="600"
        >
          <el-table-column type="selection" width="55" />
          
          <el-table-column label="模型" min-width="200">
            <template #default="{ row }">
              <div class="model-info">
                <div class="model-avatar">
                  <img 
                    :src="getProviderIcon(row.provider.provider_type)" 
                    :alt="row.provider.display_name"
                    @error="handleImageError"
                  />
                </div>
                <div class="model-details">
                  <div class="model-name">{{ row.model_name }}</div>
                  <div class="provider-name">{{ row.provider.display_name }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="model_type" label="类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getModelTypeTag(row.model_type)" size="small">
                {{ formatModelType(row.model_type) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="价格" width="150" sortable="custom">
            <template #default="{ row }">
              <div class="price-info">
                <div class="input-price">输入: ${{ row.input_cost_per_token || 0 }}/1K</div>
                <div class="output-price">输出: ${{ row.output_cost_per_token || 0 }}/1K</div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="max_tokens" label="最大Token" width="120" sortable="custom" />
          
          <el-table-column label="性能评分" width="120" sortable="custom">
            <template #default="{ row }">
              <el-rate 
                v-model="row.performance_score" 
                disabled 
                show-score 
                text-color="#ff9900"
                :max="5"
              />
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag 
                :type="row.is_active ? 'success' : 'info'" 
                size="small"
              >
                {{ row.is_active ? '可用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-tooltip content="收藏" placement="top">
                  <el-button
                    size="small"
                    :type="isModelFavorite(row) ? 'warning' : ''"
                    :icon="isModelFavorite(row) ? StarFilled : Star"
                    @click="handleModelFavorite(row)"
                    circle
                  />
                </el-tooltip>
                <el-tooltip content="详情" placement="top">
                  <el-button
                    size="small"
                    type="primary"
                    :icon="View"
                    @click="handleViewDetails(row)"
                    circle
                  />
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 48, 96]"
        :total="filteredModels.length"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 模型对比抽屉 -->
    <ModelComparison
      v-model="showComparison"
      :models="selectedModels"
      @close="showComparison = false"
    />

    <!-- 模型详情抽屉 -->
    <ModelDetails
      v-model="showDetails"
      :model="selectedModel"
      @close="showDetails = false"
      @favorite="handleModelFavorite"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Grid,
  List,
  Refresh,
  TrendCharts,
  Star,
  StarFilled,
  View
} from '@element-plus/icons-vue'
import SearchFilter from './SearchFilter.vue'
import ModelCard from './ModelCard.vue'
import ModelComparison from './ModelComparison.vue'
import ModelDetails from './ModelDetails.vue'
import { useAIConfigStore } from '@/stores/modules/aiConfigStore'
import { useFavoriteStore } from '@/stores/modules/favoriteStore'

// Props
const props = defineProps({
  providerId: {
    type: [String, Number],
    default: null
  }
})

// Emits
const emit = defineEmits(['model-selected', 'models-compared'])

// 存储
const aiConfigStore = useAIConfigStore()
const favoriteStore = useFavoriteStore()

// 响应式数据
const loading = ref(false)
const viewMode = ref('grid') // 'grid' | 'list'
const models = ref([])
const selectedModels = ref([])
const selectedModel = ref(null)
const showComparison = ref(false)
const showDetails = ref(false)

// 搜索和筛选
const searchKeyword = ref('')
const filterOptions = ref({
  modelType: '',
  provider: '',
  priceRange: [0, 100],
  performanceScore: 0,
  isActive: null
})

// 分页
const currentPage = ref(1)
const pageSize = ref(24)

// 计算属性
const filteredModels = computed(() => {
  let filtered = models.value

  // 按提供商筛选
  if (props.providerId) {
    filtered = filtered.filter(model => model.provider.id === props.providerId)
  }

  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(model => 
      model.model_name.toLowerCase().includes(keyword) ||
      model.provider.display_name.toLowerCase().includes(keyword) ||
      (model.description && model.description.toLowerCase().includes(keyword))
    )
  }

  // 筛选条件
  if (filterOptions.value.modelType) {
    filtered = filtered.filter(model => model.model_type === filterOptions.value.modelType)
  }

  if (filterOptions.value.provider) {
    filtered = filtered.filter(model => model.provider.id === filterOptions.value.provider)
  }

  if (filterOptions.value.isActive !== null) {
    filtered = filtered.filter(model => model.is_active === filterOptions.value.isActive)
  }

  // 性能评分筛选
  if (filterOptions.value.performanceScore > 0) {
    filtered = filtered.filter(model => 
      (model.performance_score || 0) >= filterOptions.value.performanceScore
    )
  }

  // 价格区间筛选
  const [minPrice, maxPrice] = filterOptions.value.priceRange
  if (minPrice > 0 || maxPrice < 100) {
    filtered = filtered.filter(model => {
      const inputCost = model.input_cost_per_token || 0
      const outputCost = model.output_cost_per_token || 0
      const avgCost = (inputCost + outputCost) / 2
      return avgCost >= minPrice && avgCost <= maxPrice
    })
  }

  return filtered
})

const paginatedModels = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredModels.value.slice(start, end)
})

// 生命周期
onMounted(() => {
  loadModels()
})

// 监听提供商变化
watch(() => props.providerId, () => {
  currentPage.value = 1
})

// 方法
const loadModels = async () => {
  loading.value = true
  try {
    const response = await aiConfigStore.fetchModels()
    models.value = response.data || []
  } catch (error) {
    ElMessage.error('加载模型列表失败')
    console.error('Load models error:', error)
  } finally {
    loading.value = false
  }
}

const handleRefresh = () => {
  loadModels()
}

const handleSearch = (keyword) => {
  searchKeyword.value = keyword
  currentPage.value = 1
}

const handleFilter = (filters) => {
  filterOptions.value = { ...filterOptions.value, ...filters }
  currentPage.value = 1
}

const handleModelSelect = (model) => {
  const index = selectedModels.value.findIndex(m => m.id === model.id)
  if (index > -1) {
    selectedModels.value.splice(index, 1)
  } else {
    if (selectedModels.value.length >= 5) {
      ElMessage.warning('最多只能选择5个模型进行对比')
      return
    }
    selectedModels.value.push(model)
  }
  emit('model-selected', model, selectedModels.value)
}

const handleModelFavorite = (model) => {
  favoriteStore.toggleFavorite('model', model.id)
  ElMessage.success(
    favoriteStore.isFavorite('model', model.id) 
      ? '已添加到收藏' 
      : '已取消收藏'
  )
}

const handleViewDetails = (model) => {
  selectedModel.value = model
  showDetails.value = true
}

const handleCompare = () => {
  if (selectedModels.value.length < 2) {
    ElMessage.warning('请至少选择2个模型进行对比')
    return
  }
  showComparison.value = true
  emit('models-compared', selectedModels.value)
}

const handleSelectionChange = (selection) => {
  selectedModels.value = selection
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

const isModelSelected = (model) => {
  return selectedModels.value.some(m => m.id === model.id)
}

const isModelFavorite = (model) => {
  return favoriteStore.isFavorite('model', model.id)
}

// 工具函数
const getProviderIcon = (providerType) => {
  const iconMap = {
    'openai': '/icons/openai.png',
    'anthropic': '/icons/anthropic.png',
    'google': '/icons/google.png',
    'azure': '/icons/azure.png',
    'local': '/icons/local.png'
  }
  return iconMap[providerType] || '/icons/default.png'
}

const handleImageError = (event) => {
  event.target.src = '/icons/default.png'
}

const getModelTypeTag = (modelType) => {
  const typeMap = {
    'chat': 'primary',
    'completion': 'success',
    'embedding': 'warning',
    'image': 'info'
  }
  return typeMap[modelType] || ''
}

const formatModelType = (modelType) => {
  const typeMap = {
    'chat': '对话',
    'completion': '补全',
    'embedding': '嵌入',
    'image': '图像'
  }
  return typeMap[modelType] || modelType
}

// 暴露给父组件的方法
defineExpose({
  loadModels,
  clearSelection: () => {
    selectedModels.value = []
  },
  getSelectedModels: () => selectedModels.value
})
</script>

<style scoped lang="scss">
.model-browser {
  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding: 16px 0;
    
    .toolbar-left {
      display: flex;
      align-items: center;
      gap: 16px;
    }
  }

  .model-content {
    min-height: 400px;
    
    .grid-view {
      .model-col {
        margin-bottom: 20px;
      }
    }
    
    .list-view {
      .model-info {
        display: flex;
        align-items: center;
        gap: 12px;
        
        .model-avatar {
          width: 32px;
          height: 32px;
          border-radius: 6px;
          overflow: hidden;
          
          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }
        }
        
        .model-details {
          .model-name {
            font-weight: 500;
            color: #303133;
            margin-bottom: 2px;
          }
          
          .provider-name {
            font-size: 12px;
            color: #909399;
          }
        }
      }
      
      .price-info {
        font-size: 12px;
        
        .input-price {
          color: #67c23a;
          margin-bottom: 2px;
        }
        
        .output-price {
          color: #e6a23c;
        }
      }
      
      .action-buttons {
        display: flex;
        gap: 4px;
      }
    }
  }

  .pagination-wrapper {
    margin-top: 24px;
    display: flex;
    justify-content: center;
  }
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

// 响应式设计
@media (max-width: 768px) {
  .model-browser {
    .toolbar {
      flex-direction: column;
      gap: 16px;
      align-items: stretch;
      
      .toolbar-left,
      .toolbar-right {
        justify-content: center;
      }
    }
    
    .pagination-wrapper {
      :deep(.el-pagination) {
        justify-content: center;
        
        .el-pagination__sizes,
        .el-pagination__jump {
          display: none;
        }
      }
    }
  }
}
</style>
