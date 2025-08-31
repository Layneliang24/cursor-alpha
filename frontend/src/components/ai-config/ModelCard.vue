<template>
  <el-card 
    class="model-card" 
    :class="{ 
      'is-selected': isSelected,
      'is-favorite': isFavorite,
      'is-inactive': !model.is_active
    }"
    shadow="hover"
    @click="handleCardClick"
  >
    <!-- 卡片头部 -->
    <template #header>
      <div class="card-header">
        <div class="provider-info">
          <img 
            :src="getProviderIcon(model.provider.provider_type)" 
            :alt="model.provider.display_name"
            class="provider-icon"
            @error="handleImageError"
          />
          <span class="provider-name">{{ model.provider.display_name }}</span>
        </div>
        
        <div class="card-actions">
          <el-tooltip content="收藏" placement="top">
            <el-button
              size="small"
              :type="isFavorite ? 'warning' : ''"
              :icon="isFavorite ? StarFilled : Star"
              @click.stop="handleFavorite"
              circle
            />
          </el-tooltip>
          
          <el-checkbox
            :model-value="isSelected"
            @change="handleSelect"
            @click.stop
            size="large"
          />
        </div>
      </div>
    </template>

    <!-- 卡片内容 -->
    <div class="card-content">
      <!-- 模型名称 -->
      <div class="model-name">
        <h4>{{ model.model_name }}</h4>
        <el-tag 
          :type="getModelTypeTag(model.model_type)" 
          size="small"
        >
          {{ formatModelType(model.model_type) }}
        </el-tag>
      </div>

      <!-- 模型描述 -->
      <div class="model-description">
        <p>{{ model.description || '暂无描述' }}</p>
      </div>

      <!-- 性能指标 -->
      <div class="performance-metrics">
        <div class="metric-item">
          <span class="metric-label">性能评分</span>
          <el-rate 
            :model-value="model.performance_score || 0" 
            disabled 
            :max="5"
            size="small"
          />
        </div>
        
        <div class="metric-item">
          <span class="metric-label">最大Token</span>
          <span class="metric-value">{{ formatNumber(model.max_tokens) }}</span>
        </div>
        
        <div class="metric-item">
          <span class="metric-label">响应时间</span>
          <span class="metric-value">{{ model.avg_response_time || 0 }}ms</span>
        </div>
      </div>

      <!-- 价格信息 -->
      <div class="pricing-info">
        <div class="price-item">
          <span class="price-label">输入</span>
          <span class="price-value">${{ formatPrice(model.input_cost_per_token) }}/1K</span>
        </div>
        <div class="price-item">
          <span class="price-label">输出</span>
          <span class="price-value">${{ formatPrice(model.output_cost_per_token) }}/1K</span>
        </div>
      </div>

      <!-- 状态指示器 -->
      <div class="status-indicators">
        <el-tag 
          :type="model.is_active ? 'success' : 'info'" 
          size="small"
          effect="light"
        >
          {{ model.is_active ? '可用' : '禁用' }}
        </el-tag>
        
        <el-tag 
          v-if="model.is_recommended"
          type="warning" 
          size="small"
          effect="light"
        >
          推荐
        </el-tag>
        
        <el-tag 
          v-if="model.is_new"
          type="danger" 
          size="small"
          effect="light"
        >
          新模型
        </el-tag>
      </div>
    </div>

    <!-- 卡片底部操作 -->
    <template #footer>
      <div class="card-footer">
        <el-button 
          type="primary" 
          size="small" 
          @click.stop="handleViewDetails"
          :icon="View"
        >
          查看详情
        </el-button>
        
        <el-button 
          size="small" 
          @click.stop="handleQuickTest"
          :loading="testing"
          :icon="Connection"
        >
          快速测试
        </el-button>
      </div>
    </template>

    <!-- 选中状态覆盖层 -->
    <div v-if="isSelected" class="selection-overlay">
      <div class="selection-badge">
        <el-icon><Check /></el-icon>
        已选中
      </div>
    </div>

    <!-- 收藏状态指示器 -->
    <div v-if="isFavorite" class="favorite-indicator">
      <el-icon><StarFilled /></el-icon>
    </div>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Star,
  StarFilled,
  View,
  Connection,
  Check
} from '@element-plus/icons-vue'
import { useAIConfigStore } from '@/stores/modules/aiConfigStore'

// Props
const props = defineProps({
  model: {
    type: Object,
    required: true
  },
  isSelected: {
    type: Boolean,
    default: false
  },
  isFavorite: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['select', 'favorite', 'view-details', 'quick-test'])

// 存储
const aiConfigStore = useAIConfigStore()

// 响应式数据
const testing = ref(false)

// 方法
const handleCardClick = () => {
  if (!props.model.is_active) {
    ElMessage.warning('该模型当前不可用')
    return
  }
  handleSelect()
}

const handleSelect = () => {
  emit('select', props.model)
}

const handleFavorite = () => {
  emit('favorite', props.model)
}

const handleViewDetails = () => {
  emit('view-details', props.model)
}

const handleQuickTest = async () => {
  if (!props.model.is_active) {
    ElMessage.warning('该模型当前不可用')
    return
  }

  testing.value = true
  try {
    const result = await aiConfigStore.testModel(props.model.id, {
      prompt: "Hello, this is a test message.",
      max_tokens: 50
    })
    
    if (result.success) {
      ElMessage.success('模型测试成功')
    } else {
      ElMessage.error(`模型测试失败: ${result.error}`)
    }
  } catch (error) {
    ElMessage.error('模型测试失败')
    console.error('Quick test error:', error)
  } finally {
    testing.value = false
  }
  
  emit('quick-test', props.model)
}

// 工具函数
const getProviderIcon = (providerType) => {
  const iconMap = {
    'openai': '/icons/openai.png',
    'anthropic': '/icons/anthropic.png',
    'google': '/icons/google.png',
    'azure': '/icons/azure.png',
    'local': '/icons/local.png',
    'chenmoai': '/icons/chenmoai.png',
    'openrouter': '/icons/openrouter.png',
    'siliconflow': '/icons/siliconflow.png'
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
    'image': 'info',
    'audio': 'danger'
  }
  return typeMap[modelType] || ''
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

const formatNumber = (num) => {
  if (!num) return '0'
  return num.toLocaleString()
}

const formatPrice = (price) => {
  if (!price) return '0.000'
  return price.toFixed(3)
}
</script>

<style scoped lang="scss">
.model-card {
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  height: 100%;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  }
  
  &.is-selected {
    border-color: #409EFF;
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
  }
  
  &.is-favorite {
    .favorite-indicator {
      opacity: 1;
    }
  }
  
  &.is-inactive {
    opacity: 0.6;
    cursor: not-allowed;
    
    &:hover {
      transform: none;
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0;
    
    .provider-info {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .provider-icon {
        width: 24px;
        height: 24px;
        border-radius: 4px;
        object-fit: cover;
      }
      
      .provider-name {
        font-size: 12px;
        color: #909399;
        font-weight: 500;
      }
    }
    
    .card-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .card-content {
    padding: 0;
    
    .model-name {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      
      h4 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-right: 8px;
      }
    }
    
    .model-description {
      margin-bottom: 16px;
      
      p {
        margin: 0;
        font-size: 13px;
        color: #606266;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
    
    .performance-metrics {
      margin-bottom: 16px;
      
      .metric-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .metric-label {
          font-size: 12px;
          color: #909399;
        }
        
        .metric-value {
          font-size: 12px;
          color: #303133;
          font-weight: 500;
        }
      }
    }
    
    .pricing-info {
      display: flex;
      justify-content: space-between;
      margin-bottom: 16px;
      padding: 8px;
      background-color: #f8f9fa;
      border-radius: 4px;
      
      .price-item {
        text-align: center;
        flex: 1;
        
        .price-label {
          display: block;
          font-size: 11px;
          color: #909399;
          margin-bottom: 2px;
        }
        
        .price-value {
          font-size: 12px;
          color: #303133;
          font-weight: 600;
        }
      }
    }
    
    .status-indicators {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }
  }

  .card-footer {
    display: flex;
    gap: 8px;
    padding: 0;
    
    .el-button {
      flex: 1;
    }
  }

  .selection-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(64, 158, 255, 0.1);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1;
    
    .selection-badge {
      background-color: #409EFF;
      color: white;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }

  .favorite-indicator {
    position: absolute;
    top: 8px;
    right: 8px;
    color: #f39c12;
    font-size: 16px;
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: 2;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .model-card {
    .card-content {
      .performance-metrics {
        .metric-item {
          font-size: 11px;
        }
      }
      
      .pricing-info {
        .price-item {
          .price-label,
          .price-value {
            font-size: 10px;
          }
        }
      }
    }
    
    .card-footer {
      flex-direction: column;
      gap: 6px;
    }
  }
}
</style>
