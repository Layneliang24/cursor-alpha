<template>
  <div class="search-filter">
    <!-- 搜索框 -->
    <div class="search-input">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索模型名称、提供商..."
        :prefix-icon="Search"
        clearable
        style="width: 300px"
        @input="handleSearchInput"
        @clear="handleSearchClear"
      />
    </div>

    <!-- 筛选按钮 -->
    <div class="filter-controls">
      <el-button 
        type="primary" 
        :icon="Filter"
        @click="showFilterPanel = !showFilterPanel"
        :class="{ 'is-active': hasActiveFilters }"
      >
        筛选
        <el-badge 
          v-if="activeFilterCount > 0" 
          :value="activeFilterCount" 
          class="filter-badge"
        />
      </el-button>
      
      <el-button 
        v-if="hasActiveFilters"
        @click="clearAllFilters"
        :icon="Close"
        size="small"
      >
        清空筛选
      </el-button>
      
      <!-- 结果统计 -->
      <div class="result-count">
        找到 <strong>{{ total }}</strong> 个模型
      </div>
    </div>

    <!-- 筛选面板 -->
    <el-collapse-transition>
      <div v-show="showFilterPanel" class="filter-panel">
        <el-card shadow="never">
          <div class="filter-content">
            <!-- 模型类型 -->
            <div class="filter-group">
              <label class="filter-label">模型类型</label>
              <el-select
                v-model="filters.modelType"
                placeholder="选择模型类型"
                clearable
                style="width: 200px"
                @change="handleFilterChange"
              >
                <el-option label="对话模型" value="chat" />
                <el-option label="补全模型" value="completion" />
                <el-option label="嵌入模型" value="embedding" />
                <el-option label="图像模型" value="image" />
                <el-option label="音频模型" value="audio" />
              </el-select>
            </div>

            <!-- 提供商 -->
            <div class="filter-group">
              <label class="filter-label">提供商</label>
              <el-select
                v-model="filters.provider"
                placeholder="选择提供商"
                clearable
                style="width: 200px"
                @change="handleFilterChange"
              >
                <el-option
                  v-for="provider in providers"
                  :key="provider.id"
                  :label="provider.display_name"
                  :value="provider.id"
                />
              </el-select>
            </div>

            <!-- 价格范围 -->
            <div class="filter-group">
              <label class="filter-label">价格范围 ($/1K tokens)</label>
              <el-slider
                v-model="filters.priceRange"
                range
                :min="0"
                :max="100"
                :step="0.1"
                :format-tooltip="formatPriceTooltip"
                style="width: 200px"
                @change="handleFilterChange"
              />
              <div class="price-range-display">
                ${{ filters.priceRange[0].toFixed(2) }} - ${{ filters.priceRange[1].toFixed(2) }}
              </div>
            </div>

            <!-- 性能评分 -->
            <div class="filter-group">
              <label class="filter-label">最低性能评分</label>
              <el-rate
                v-model="filters.performanceScore"
                :max="5"
                @change="handleFilterChange"
                show-text
                :texts="['不限', '1星+', '2星+', '3星+', '4星+', '5星']"
              />
            </div>

            <!-- 状态筛选 -->
            <div class="filter-group">
              <label class="filter-label">状态</label>
              <el-radio-group 
                v-model="filters.status"
                @change="handleFilterChange"
              >
                <el-radio :value="null">全部</el-radio>
                <el-radio :value="true">可用</el-radio>
                <el-radio :value="false">禁用</el-radio>
              </el-radio-group>
            </div>

            <!-- 特殊标签 -->
            <div class="filter-group">
              <label class="filter-label">特殊标签</label>
              <el-checkbox-group 
                v-model="filters.tags"
                @change="handleFilterChange"
              >
                <el-checkbox value="recommended">推荐模型</el-checkbox>
                <el-checkbox value="new">新模型</el-checkbox>
                <el-checkbox value="popular">热门模型</el-checkbox>
                <el-checkbox value="cost_effective">性价比高</el-checkbox>
              </el-checkbox-group>
            </div>

            <!-- 排序选项 -->
            <div class="filter-group">
              <label class="filter-label">排序方式</label>
              <el-select
                v-model="filters.sortBy"
                placeholder="选择排序方式"
                style="width: 200px"
                @change="handleFilterChange"
              >
                <el-option label="默认排序" value="default" />
                <el-option label="性能评分" value="performance" />
                <el-option label="价格从低到高" value="price_asc" />
                <el-option label="价格从高到低" value="price_desc" />
                <el-option label="最大Token数" value="max_tokens" />
                <el-option label="响应时间" value="response_time" />
                <el-option label="最近更新" value="updated_at" />
              </el-select>
            </div>
          </div>

          <!-- 快捷筛选 -->
          <div class="quick-filters">
            <label class="filter-label">快捷筛选</label>
            <div class="quick-filter-tags">
              <el-tag
                v-for="quickFilter in quickFilters"
                :key="quickFilter.key"
                :type="quickFilter.active ? 'primary' : ''"
                :effect="quickFilter.active ? 'dark' : 'plain'"
                @click="handleQuickFilter(quickFilter)"
                class="quick-filter-tag"
              >
                {{ quickFilter.label }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </div>
    </el-collapse-transition>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Filter, Close } from '@element-plus/icons-vue'
import { useAIConfigStore } from '@/stores/modules/aiConfigStore'
import { debounce } from 'lodash-es'

// Props
const props = defineProps({
  total: {
    type: Number,
    default: 0
  }
})

// Emits
const emit = defineEmits(['search', 'filter', 'sort'])

// 存储
const aiConfigStore = useAIConfigStore()

// 响应式数据
const showFilterPanel = ref(false)
const searchKeyword = ref('')
const providers = ref([])

// 筛选条件
const filters = reactive({
  modelType: '',
  provider: '',
  priceRange: [0, 10],
  performanceScore: 0,
  status: null,
  tags: [],
  sortBy: 'default'
})

// 快捷筛选
const quickFilters = ref([
  { key: 'recommended', label: '推荐模型', active: false },
  { key: 'new', label: '新模型', active: false },
  { key: 'chat', label: '对话模型', active: false },
  { key: 'free', label: '免费模型', active: false },
  { key: 'fast', label: '响应快', active: false },
  { key: 'cost_effective', label: '性价比高', active: false }
])

// 计算属性
const hasActiveFilters = computed(() => {
  return (
    filters.modelType ||
    filters.provider ||
    filters.priceRange[0] > 0 ||
    filters.priceRange[1] < 10 ||
    filters.performanceScore > 0 ||
    filters.status !== null ||
    filters.tags.length > 0 ||
    filters.sortBy !== 'default'
  )
})

const activeFilterCount = computed(() => {
  let count = 0
  if (filters.modelType) count++
  if (filters.provider) count++
  if (filters.priceRange[0] > 0 || filters.priceRange[1] < 10) count++
  if (filters.performanceScore > 0) count++
  if (filters.status !== null) count++
  if (filters.tags.length > 0) count++
  if (filters.sortBy !== 'default') count++
  return count
})

// 生命周期
onMounted(() => {
  loadProviders()
})

// 防抖搜索
const debouncedSearch = debounce((keyword) => {
  emit('search', keyword)
}, 300)

// 监听搜索关键词变化
watch(searchKeyword, (newValue) => {
  debouncedSearch(newValue)
})

// 方法
const loadProviders = async () => {
  try {
    const response = await aiConfigStore.fetchProviders()
    providers.value = response.data || []
  } catch (error) {
    console.error('Load providers error:', error)
  }
}

const handleSearchInput = (value) => {
  // 已通过watch处理防抖
}

const handleSearchClear = () => {
  searchKeyword.value = ''
  emit('search', '')
}

const handleFilterChange = () => {
  emit('filter', { ...filters })
  
  // 更新快捷筛选状态
  updateQuickFilterStatus()
}

const handleQuickFilter = (quickFilter) => {
  quickFilter.active = !quickFilter.active
  
  switch (quickFilter.key) {
    case 'recommended':
      if (quickFilter.active) {
        filters.tags.push('recommended')
      } else {
        filters.tags = filters.tags.filter(tag => tag !== 'recommended')
      }
      break
      
    case 'new':
      if (quickFilter.active) {
        filters.tags.push('new')
      } else {
        filters.tags = filters.tags.filter(tag => tag !== 'new')
      }
      break
      
    case 'chat':
      filters.modelType = quickFilter.active ? 'chat' : ''
      break
      
    case 'free':
      if (quickFilter.active) {
        filters.priceRange = [0, 0]
      } else {
        filters.priceRange = [0, 10]
      }
      break
      
    case 'fast':
      filters.sortBy = quickFilter.active ? 'response_time' : 'default'
      break
      
    case 'cost_effective':
      if (quickFilter.active) {
        filters.tags.push('cost_effective')
        filters.sortBy = 'price_asc'
      } else {
        filters.tags = filters.tags.filter(tag => tag !== 'cost_effective')
        filters.sortBy = 'default'
      }
      break
  }
  
  handleFilterChange()
}

const updateQuickFilterStatus = () => {
  quickFilters.value.forEach(quickFilter => {
    switch (quickFilter.key) {
      case 'recommended':
        quickFilter.active = filters.tags.includes('recommended')
        break
      case 'new':
        quickFilter.active = filters.tags.includes('new')
        break
      case 'chat':
        quickFilter.active = filters.modelType === 'chat'
        break
      case 'free':
        quickFilter.active = filters.priceRange[0] === 0 && filters.priceRange[1] === 0
        break
      case 'fast':
        quickFilter.active = filters.sortBy === 'response_time'
        break
      case 'cost_effective':
        quickFilter.active = filters.tags.includes('cost_effective')
        break
    }
  })
}

const clearAllFilters = () => {
  // 重置所有筛选条件
  Object.assign(filters, {
    modelType: '',
    provider: '',
    priceRange: [0, 10],
    performanceScore: 0,
    status: null,
    tags: [],
    sortBy: 'default'
  })
  
  // 重置快捷筛选
  quickFilters.value.forEach(filter => {
    filter.active = false
  })
  
  // 重置搜索关键词
  searchKeyword.value = ''
  
  // 触发筛选变化
  emit('search', '')
  emit('filter', { ...filters })
  
  ElMessage.success('已清空所有筛选条件')
}

const formatPriceTooltip = (value) => {
  return `$${value.toFixed(2)}`
}

// 暴露给父组件的方法
defineExpose({
  clearFilters: clearAllFilters,
  getFilters: () => ({ ...filters }),
  getSearchKeyword: () => searchKeyword.value
})
</script>

<style scoped lang="scss">
.search-filter {
  .search-input {
    margin-bottom: 16px;
  }
  
  .filter-controls {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    
    .el-button.is-active {
      background-color: #409EFF;
      border-color: #409EFF;
      color: white;
    }
    
    .filter-badge {
      :deep(.el-badge__content) {
        background-color: #f56c6c;
        border: none;
      }
    }
    
    .result-count {
      font-size: 14px;
      color: #606266;
      margin-left: auto;
      
      strong {
        color: #409EFF;
      }
    }
  }

  .filter-panel {
    .filter-content {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 24px;
      margin-bottom: 24px;
      
      .filter-group {
        .filter-label {
          display: block;
          font-size: 13px;
          font-weight: 500;
          color: #303133;
          margin-bottom: 8px;
        }
        
        .price-range-display {
          text-align: center;
          font-size: 12px;
          color: #606266;
          margin-top: 8px;
        }
      }
    }
    
    .quick-filters {
      border-top: 1px solid #EBEEF5;
      padding-top: 16px;
      
      .filter-label {
        display: block;
        font-size: 13px;
        font-weight: 500;
        color: #303133;
        margin-bottom: 12px;
      }
      
      .quick-filter-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        
        .quick-filter-tag {
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover {
            transform: translateY(-1px);
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .search-filter {
    .search-input {
      :deep(.el-input) {
        width: 100% !important;
      }
    }
    
    .filter-controls {
      flex-wrap: wrap;
      
      .result-count {
        width: 100%;
        text-align: center;
        margin-left: 0;
        margin-top: 8px;
      }
    }
    
    .filter-panel {
      .filter-content {
        grid-template-columns: 1fr;
        gap: 16px;
        
        .filter-group {
          .el-select,
          .el-slider {
            width: 100% !important;
          }
        }
      }
      
      .quick-filters {
        .quick-filter-tags {
          justify-content: center;
        }
      }
    }
  }
}
</style>
