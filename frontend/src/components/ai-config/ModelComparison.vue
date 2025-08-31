<template>
  <el-drawer
    v-model="visible"
    title="模型对比分析"
    direction="rtl"
    size="80%"
    :before-close="handleClose"
  >
    <template #header>
      <div class="drawer-header">
        <h3>模型对比分析</h3>
        <div class="header-actions">
          <el-button @click="handleExport" :icon="Download">
            导出对比
          </el-button>
          <el-button @click="handleClearAll" :icon="Delete">
            清空选择
          </el-button>
        </div>
      </div>
    </template>

    <div class="comparison-content" v-if="models.length > 0">
      <!-- 模型选择器 -->
      <div class="model-selector">
        <div class="selected-models">
          <div
            v-for="(model, index) in models"
            :key="model.id"
            class="model-chip"
          >
            <div class="chip-content">
              <img 
                :src="getProviderIcon(model.provider.provider_type)"
                :alt="model.provider.display_name"
                class="provider-icon"
                @error="handleImageError"
              />
              <span class="model-name">{{ model.model_name }}</span>
              <el-button
                size="small"
                type="danger"
                :icon="Close"
                circle
                @click="removeModel(index)"
              />
            </div>
          </div>
        </div>
        
        <el-text v-if="models.length < 5" type="info" size="small">
          最多可选择5个模型进行对比
        </el-text>
      </div>

      <!-- 对比表格 -->
      <div class="comparison-table">
        <el-table
          :data="comparisonData"
          border
          stripe
          height="600"
          :header-cell-style="{ backgroundColor: '#f8f9fa', fontWeight: 'bold' }"
        >
          <el-table-column prop="attribute" label="对比项目" width="150" fixed="left">
            <template #default="{ row }">
              <div class="attribute-cell">
                <el-icon v-if="row.icon" class="attribute-icon">
                  <component :is="row.icon" />
                </el-icon>
                <span>{{ row.label }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column
            v-for="(model, index) in models"
            :key="model.id"
            :label="model.model_name"
            :width="180"
          >
            <template #header>
              <div class="model-header">
                <img 
                  :src="getProviderIcon(model.provider.provider_type)"
                  :alt="model.provider.display_name"
                  class="provider-icon-small"
                />
                <div class="model-info">
                  <div class="model-name">{{ model.model_name }}</div>
                  <div class="provider-name">{{ model.provider.display_name }}</div>
                </div>
              </div>
            </template>
            
            <template #default="{ row }">
              <div class="value-cell">
                <!-- 根据不同的属性类型渲染不同的内容 -->
                <component 
                  :is="getCellComponent(row.attribute)"
                  :value="getModelValue(model, row.attribute)"
                  :model="model"
                  :attribute="row.attribute"
                />
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 性能对比图表 -->
      <div class="comparison-charts">
        <el-row :gutter="20">
          <!-- 雷达图 - 综合性能 -->
          <el-col :span="12">
            <el-card title="综合性能对比">
              <template #header>
                <span>综合性能对比</span>
              </template>
              <PerformanceRadarChart :models="models" />
            </el-card>
          </el-col>
          
          <!-- 柱状图 - 价格对比 -->
          <el-col :span="12">
            <el-card title="价格对比">
              <template #header>
                <span>价格对比 ($/1K tokens)</span>
              </template>
              <PriceComparisonChart :models="models" />
            </el-card>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" style="margin-top: 20px;">
          <!-- 响应时间对比 -->
          <el-col :span="12">
            <el-card title="响应时间对比">
              <template #header>
                <span>响应时间对比 (ms)</span>
              </template>
              <ResponseTimeChart :models="models" />
            </el-card>
          </el-col>
          
          <!-- Token限制对比 -->
          <el-col :span="12">
            <el-card title="Token限制对比">
              <template #header>
                <span>最大Token数对比</span>
              </template>
              <TokenLimitChart :models="models" />
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 推荐建议 -->
      <div class="recommendations">
        <el-card title="智能推荐">
          <template #header>
            <span>基于对比结果的推荐</span>
          </template>
          <div class="recommendation-list">
            <div
              v-for="recommendation in recommendations"
              :key="recommendation.type"
              class="recommendation-item"
            >
              <div class="recommendation-header">
                <el-tag :type="recommendation.tagType" size="small">
                  {{ recommendation.title }}
                </el-tag>
              </div>
              <div class="recommendation-content">
                <div class="recommended-model">
                  <img 
                    :src="getProviderIcon(recommendation.model.provider.provider_type)"
                    :alt="recommendation.model.provider.display_name"
                    class="provider-icon-small"
                  />
                  <span class="model-name">{{ recommendation.model.model_name }}</span>
                </div>
                <div class="recommendation-reason">
                  {{ recommendation.reason }}
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty 
      v-else 
      description="请先选择要对比的模型"
      :image-size="100"
    />
  </el-drawer>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Download,
  Delete,
  Close,
  Money,
  Timer,
  TrendCharts,
  Star,
  Setting
} from '@element-plus/icons-vue'
import PerformanceRadarChart from './charts/PerformanceRadarChart.vue'
import PriceComparisonChart from './charts/PriceComparisonChart.vue'
import ResponseTimeChart from './charts/ResponseTimeChart.vue'
import TokenLimitChart from './charts/TokenLimitChart.vue'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  models: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'close', 'remove-model'])

// 响应式数据
const visible = ref(props.modelValue)

// 监听props变化
watch(() => props.modelValue, (newValue) => {
  visible.value = newValue
})

watch(visible, (newValue) => {
  emit('update:modelValue', newValue)
})

// 对比数据结构
const comparisonData = ref([
  {
    attribute: 'provider',
    label: '提供商',
    icon: Setting
  },
  {
    attribute: 'model_type',
    label: '模型类型',
    icon: TrendCharts
  },
  {
    attribute: 'max_tokens',
    label: '最大Token',
    icon: null
  },
  {
    attribute: 'input_cost',
    label: '输入价格',
    icon: Money
  },
  {
    attribute: 'output_cost',
    label: '输出价格',
    icon: Money
  },
  {
    attribute: 'performance_score',
    label: '性能评分',
    icon: Star
  },
  {
    attribute: 'avg_response_time',
    label: '响应时间',
    icon: Timer
  },
  {
    attribute: 'is_active',
    label: '状态',
    icon: null
  }
])

// 计算属性
const recommendations = computed(() => {
  if (props.models.length < 2) return []

  const recs = []

  // 最佳性价比
  const costEffectiveModel = props.models.reduce((best, current) => {
    const bestScore = (best.performance_score || 0) / ((best.input_cost_per_token || 0.001) + (best.output_cost_per_token || 0.001))
    const currentScore = (current.performance_score || 0) / ((current.input_cost_per_token || 0.001) + (current.output_cost_per_token || 0.001))
    return currentScore > bestScore ? current : best
  })

  recs.push({
    type: 'cost_effective',
    title: '最佳性价比',
    tagType: 'success',
    model: costEffectiveModel,
    reason: '在性能和价格之间达到最佳平衡'
  })

  // 最高性能
  const bestPerformanceModel = props.models.reduce((best, current) => {
    return (current.performance_score || 0) > (best.performance_score || 0) ? current : best
  })

  recs.push({
    type: 'best_performance',
    title: '最高性能',
    tagType: 'warning',
    model: bestPerformanceModel,
    reason: '提供最高的性能评分和处理能力'
  })

  // 最低成本
  const lowestCostModel = props.models.reduce((best, current) => {
    const bestCost = (best.input_cost_per_token || 0) + (best.output_cost_per_token || 0)
    const currentCost = (current.input_cost_per_token || 0) + (current.output_cost_per_token || 0)
    return currentCost < bestCost ? current : best
  })

  recs.push({
    type: 'lowest_cost',
    title: '最低成本',
    tagType: 'info',
    model: lowestCostModel,
    reason: '提供最经济的使用成本'
  })

  // 最快响应
  const fastestModel = props.models.reduce((best, current) => {
    return (current.avg_response_time || Infinity) < (best.avg_response_time || Infinity) ? current : best
  })

  recs.push({
    type: 'fastest',
    title: '最快响应',
    tagType: 'danger',
    model: fastestModel,
    reason: '提供最快的响应时间'
  })

  return recs
})

// 方法
const handleClose = () => {
  visible.value = false
  emit('close')
}

const removeModel = (index) => {
  emit('remove-model', index)
}

const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有选择的模型吗？',
      '确认清空',
      {
        confirmButtonText: '清空',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    emit('remove-model', 'all')
    ElMessage.success('已清空所有选择')
  } catch {
    // 用户取消
  }
}

const handleExport = () => {
  // 生成导出数据
  const exportData = {
    comparison_date: new Date().toISOString(),
    models: props.models.map(model => ({
      name: model.model_name,
      provider: model.provider.display_name,
      type: model.model_type,
      max_tokens: model.max_tokens,
      input_cost: model.input_cost_per_token,
      output_cost: model.output_cost_per_token,
      performance_score: model.performance_score,
      response_time: model.avg_response_time,
      is_active: model.is_active
    })),
    recommendations: recommendations.value.map(rec => ({
      type: rec.type,
      title: rec.title,
      model: rec.model.model_name,
      reason: rec.reason
    }))
  }

  // 创建下载链接
  const dataStr = JSON.stringify(exportData, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
  
  const exportFileDefaultName = `model_comparison_${new Date().toISOString().split('T')[0]}.json`
  
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
  
  ElMessage.success('对比数据已导出')
}

const getModelValue = (model, attribute) => {
  switch (attribute) {
    case 'provider':
      return model.provider.display_name
    case 'model_type':
      return formatModelType(model.model_type)
    case 'max_tokens':
      return model.max_tokens || 0
    case 'input_cost':
      return model.input_cost_per_token || 0
    case 'output_cost':
      return model.output_cost_per_token || 0
    case 'performance_score':
      return model.performance_score || 0
    case 'avg_response_time':
      return model.avg_response_time || 0
    case 'is_active':
      return model.is_active
    default:
      return model[attribute] || '-'
  }
}

const getCellComponent = (attribute) => {
  // 返回用于渲染不同类型值的组件名
  switch (attribute) {
    case 'performance_score':
      return 'PerformanceCell'
    case 'input_cost':
    case 'output_cost':
      return 'PriceCell'
    case 'is_active':
      return 'StatusCell'
    case 'max_tokens':
      return 'NumberCell'
    case 'avg_response_time':
      return 'TimeCell'
    default:
      return 'TextCell'
  }
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

const formatModelType = (modelType) => {
  const typeMap = {
    'chat': '对话',
    'completion': '补全',
    'embedding': '嵌入',
    'image': '图像',
    'audio': '音频'
  }
  return typeMap[modelType] || modelType
}
</script>

<!-- 单元格组件 -->
<script>
// 性能评分单元格
const PerformanceCell = {
  props: ['value'],
  template: `
    <el-rate 
      :model-value="value" 
      disabled 
      :max="5"
      size="small"
      show-score
    />
  `
}

// 价格单元格
const PriceCell = {
  props: ['value'],
  template: `
    <span class="price-value">
      ${{ value.toFixed(3) }}/1K
    </span>
  `
}

// 状态单元格
const StatusCell = {
  props: ['value'],
  template: `
    <el-tag 
      :type="value ? 'success' : 'info'" 
      size="small"
    >
      {{ value ? '可用' : '禁用' }}
    </el-tag>
  `
}

// 数字单元格
const NumberCell = {
  props: ['value'],
  template: `
    <span class="number-value">
      {{ value.toLocaleString() }}
    </span>
  `
}

// 时间单元格
const TimeCell = {
  props: ['value'],
  template: `
    <span class="time-value">
      {{ value }}ms
    </span>
  `
}

// 文本单元格
const TextCell = {
  props: ['value'],
  template: `
    <span class="text-value">
      {{ value }}
    </span>
  `
}

export default {
  components: {
    PerformanceCell,
    PriceCell,
    StatusCell,
    NumberCell,
    TimeCell,
    TextCell
  }
}
</script>

<style scoped lang="scss">
.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  
  h3 {
    margin: 0;
    color: #303133;
  }
  
  .header-actions {
    display: flex;
    gap: 8px;
  }
}

.comparison-content {
  .model-selector {
    margin-bottom: 24px;
    
    .selected-models {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 12px;
      
      .model-chip {
        .chip-content {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 12px;
          background-color: #f5f7fa;
          border-radius: 16px;
          border: 1px solid #e4e7ed;
          
          .provider-icon {
            width: 20px;
            height: 20px;
            border-radius: 4px;
          }
          
          .model-name {
            font-size: 13px;
            font-weight: 500;
            color: #303133;
          }
        }
      }
    }
  }
  
  .comparison-table {
    margin-bottom: 32px;
    
    .attribute-cell {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 500;
      
      .attribute-icon {
        color: #409EFF;
      }
    }
    
    .model-header {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .provider-icon-small {
        width: 16px;
        height: 16px;
        border-radius: 2px;
      }
      
      .model-info {
        text-align: left;
        
        .model-name {
          font-size: 12px;
          font-weight: 600;
          color: #303133;
          line-height: 1.2;
        }
        
        .provider-name {
          font-size: 10px;
          color: #909399;
          line-height: 1.2;
        }
      }
    }
    
    .value-cell {
      text-align: center;
      
      .price-value {
        color: #e6a23c;
        font-weight: 500;
      }
      
      .number-value {
        color: #303133;
        font-weight: 500;
      }
      
      .time-value {
        color: #67c23a;
        font-weight: 500;
      }
      
      .text-value {
        color: #606266;
      }
    }
  }
  
  .comparison-charts {
    margin-bottom: 32px;
  }
  
  .recommendations {
    .recommendation-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
      
      .recommendation-item {
        padding: 16px;
        border: 1px solid #e4e7ed;
        border-radius: 8px;
        background-color: #fafafa;
        
        .recommendation-header {
          margin-bottom: 8px;
        }
        
        .recommendation-content {
          .recommended-model {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
            
            .provider-icon-small {
              width: 16px;
              height: 16px;
              border-radius: 2px;
            }
            
            .model-name {
              font-weight: 500;
              color: #303133;
            }
          }
          
          .recommendation-reason {
            font-size: 13px;
            color: #606266;
            line-height: 1.4;
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  :deep(.el-drawer) {
    width: 95% !important;
  }
  
  .comparison-content {
    .comparison-table {
      :deep(.el-table) {
        font-size: 12px;
        
        .el-table__header th,
        .el-table__body td {
          padding: 8px 4px;
        }
      }
    }
    
    .comparison-charts {
      :deep(.el-col) {
        margin-bottom: 16px;
      }
    }
  }
}
</style>
