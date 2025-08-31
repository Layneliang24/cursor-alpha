<template>
  <el-drawer
    v-model="visible"
    :title="`${model?.model_name || '模型详情'}`"
    direction="rtl"
    size="60%"
    :before-close="handleClose"
  >
    <div class="model-details" v-if="model">
      <!-- 模型基本信息 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <div class="header-actions">
              <el-button
                :type="isFavorite ? 'warning' : ''"
                :icon="isFavorite ? StarFilled : Star"
                @click="handleFavorite"
                size="small"
              >
                {{ isFavorite ? '已收藏' : '收藏' }}
              </el-button>
            </div>
          </div>
        </template>
        
        <div class="basic-info">
          <div class="info-row">
            <div class="info-item">
              <label>提供商</label>
              <div class="provider-info">
                <img 
                  :src="getProviderIcon(model.provider.provider_type)"
                  :alt="model.provider.display_name"
                  class="provider-icon"
                  @error="handleImageError"
                />
                <span>{{ model.provider.display_name }}</span>
              </div>
            </div>
            
            <div class="info-item">
              <label>模型类型</label>
              <el-tag :type="getModelTypeTag(model.model_type)">
                {{ formatModelType(model.model_type) }}
              </el-tag>
            </div>
            
            <div class="info-item">
              <label>状态</label>
              <el-tag :type="model.is_active ? 'success' : 'info'">
                {{ model.is_active ? '可用' : '禁用' }}
              </el-tag>
            </div>
          </div>
          
          <div class="info-row">
            <div class="info-item">
              <label>最大Token</label>
              <span class="value">{{ formatNumber(model.max_tokens) }}</span>
            </div>
            
            <div class="info-item">
              <label>性能评分</label>
              <el-rate 
                :model-value="model.performance_score || 0" 
                disabled 
                :max="5"
                show-score
              />
            </div>
            
            <div class="info-item">
              <label>响应时间</label>
              <span class="value">{{ model.avg_response_time || 0 }}ms</span>
            </div>
          </div>
          
          <div class="info-row" v-if="model.description">
            <div class="info-item full-width">
              <label>模型描述</label>
              <p class="description">{{ model.description }}</p>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 价格信息 -->
      <el-card class="pricing-card" shadow="never">
        <template #header>
          <span>价格信息</span>
        </template>
        
        <div class="pricing-info">
          <div class="price-item">
            <div class="price-type">输入Token</div>
            <div class="price-value">${{ formatPrice(model.input_cost_per_token) }} / 1K tokens</div>
            <div class="price-note">每1000个输入token的价格</div>
          </div>
          
          <div class="price-item">
            <div class="price-type">输出Token</div>
            <div class="price-value">${{ formatPrice(model.output_cost_per_token) }} / 1K tokens</div>
            <div class="price-note">每1000个输出token的价格</div>
          </div>
          
          <div class="price-item total-cost">
            <div class="price-type">预估成本</div>
            <div class="cost-calculator">
              <el-input-number
                v-model="estimateTokens"
                :min="1000"
                :max="1000000"
                :step="1000"
                size="small"
                controls-position="right"
              />
              <span class="cost-result">
                ≈ ${{ calculateEstimatedCost() }}
              </span>
            </div>
            <div class="price-note">基于{{ estimateTokens.toLocaleString() }}个token的预估成本</div>
          </div>
        </div>
      </el-card>

      <!-- 性能指标 -->
      <el-card class="performance-card" shadow="never">
        <template #header>
          <span>性能指标</span>
        </template>
        
        <div class="performance-metrics">
          <div class="metric-item">
            <div class="metric-header">
              <span class="metric-name">处理速度</span>
              <span class="metric-value">{{ model.tokens_per_second || 0 }} tokens/s</span>
            </div>
            <el-progress 
              :percentage="getSpeedPercentage(model.tokens_per_second || 0)"
              :color="getSpeedColor(model.tokens_per_second || 0)"
            />
          </div>
          
          <div class="metric-item">
            <div class="metric-header">
              <span class="metric-name">准确率</span>
              <span class="metric-value">{{ (model.accuracy_score || 0) * 100 }}%</span>
            </div>
            <el-progress 
              :percentage="(model.accuracy_score || 0) * 100"
              color="#67c23a"
            />
          </div>
          
          <div class="metric-item">
            <div class="metric-header">
              <span class="metric-name">稳定性</span>
              <span class="metric-value">{{ (model.reliability_score || 0) * 100 }}%</span>
            </div>
            <el-progress 
              :percentage="(model.reliability_score || 0) * 100"
              color="#409eff"
            />
          </div>
        </div>
      </el-card>

      <!-- 使用统计 -->
      <el-card class="usage-card" shadow="never">
        <template #header>
          <span>使用统计</span>
        </template>
        
        <div class="usage-stats">
          <div class="stat-item">
            <div class="stat-value">{{ formatNumber(model.total_requests || 0) }}</div>
            <div class="stat-label">总请求数</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">{{ formatNumber(model.total_tokens || 0) }}</div>
            <div class="stat-label">总Token数</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">${{ formatPrice(model.total_cost || 0) }}</div>
            <div class="stat-label">总花费</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">{{ model.success_rate || 0 }}%</div>
            <div class="stat-label">成功率</div>
          </div>
        </div>
      </el-card>

      <!-- 快速测试 -->
      <el-card class="test-card" shadow="never">
        <template #header>
          <span>快速测试</span>
        </template>
        
        <div class="test-section">
          <div class="test-input">
            <el-input
              v-model="testPrompt"
              type="textarea"
              :rows="3"
              placeholder="输入测试提示词..."
              maxlength="500"
              show-word-limit
            />
          </div>
          
          <div class="test-controls">
            <el-row :gutter="16">
              <el-col :span="8">
                <label>最大Token数</label>
                <el-input-number
                  v-model="testConfig.maxTokens"
                  :min="1"
                  :max="model.max_tokens || 4000"
                  size="small"
                />
              </el-col>
              
              <el-col :span="8">
                <label>温度参数</label>
                <el-input-number
                  v-model="testConfig.temperature"
                  :min="0"
                  :max="2"
                  :step="0.1"
                  size="small"
                />
              </el-col>
              
              <el-col :span="8">
                <label>Top-p</label>
                <el-input-number
                  v-model="testConfig.topP"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  size="small"
                />
              </el-col>
            </el-row>
          </div>
          
          <div class="test-actions">
            <el-button
              type="primary"
              @click="runTest"
              :loading="testing"
              :disabled="!testPrompt.trim() || !model.is_active"
            >
              运行测试
            </el-button>
            
            <el-button @click="clearTest">
              清空
            </el-button>
          </div>
          
          <div v-if="testResult" class="test-result">
            <div class="result-header">
              <span>测试结果</span>
              <div class="result-meta">
                <span>耗时: {{ testResult.duration }}ms</span>
                <span>Token: {{ testResult.tokens }}个</span>
                <span>成本: ${{ testResult.cost }}</span>
              </div>
            </div>
            
            <div class="result-content">
              <pre>{{ testResult.response }}</pre>
            </div>
          </div>
          
          <div v-if="testError" class="test-error">
            <el-alert
              :title="testError"
              type="error"
              :closable="false"
              show-icon
            />
          </div>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty 
      v-else 
      description="未选择模型"
      :image-size="100"
    />
  </el-drawer>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Star, StarFilled } from '@element-plus/icons-vue'
import { useAIConfigStore } from '@/stores/modules/aiConfigStore'
import { useFavoriteStore } from '@/stores/modules/favoriteStore'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  model: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'close', 'favorite'])

// 存储
const aiConfigStore = useAIConfigStore()
const favoriteStore = useFavoriteStore()

// 响应式数据
const visible = ref(props.modelValue)
const estimateTokens = ref(10000)
const testing = ref(false)
const testPrompt = ref('')
const testResult = ref(null)
const testError = ref('')

// 测试配置
const testConfig = ref({
  maxTokens: 100,
  temperature: 0.7,
  topP: 1.0
})

// 监听props变化
watch(() => props.modelValue, (newValue) => {
  visible.value = newValue
})

watch(visible, (newValue) => {
  emit('update:modelValue', newValue)
})

// 计算属性
const isFavorite = computed(() => {
  return props.model ? favoriteStore.isFavorite('model', props.model.id) : false
})

// 方法
const handleClose = () => {
  visible.value = false
  emit('close')
}

const handleFavorite = () => {
  if (!props.model) return
  
  favoriteStore.toggleFavorite('model', props.model.id)
  emit('favorite', props.model)
  
  ElMessage.success(
    favoriteStore.isFavorite('model', props.model.id) 
      ? '已添加到收藏' 
      : '已取消收藏'
  )
}

const calculateEstimatedCost = () => {
  if (!props.model) return '0.000'
  
  const inputCost = (props.model.input_cost_per_token || 0) * (estimateTokens.value / 1000)
  const outputCost = (props.model.output_cost_per_token || 0) * (estimateTokens.value / 1000)
  const totalCost = inputCost + outputCost
  
  return totalCost.toFixed(3)
}

const runTest = async () => {
  if (!props.model || !testPrompt.value.trim()) return
  
  testing.value = true
  testResult.value = null
  testError.value = ''
  
  try {
    const startTime = Date.now()
    
    const response = await aiConfigStore.testModel(props.model.id, {
      prompt: testPrompt.value,
      max_tokens: testConfig.value.maxTokens,
      temperature: testConfig.value.temperature,
      top_p: testConfig.value.topP
    })
    
    const endTime = Date.now()
    const duration = endTime - startTime
    
    if (response.success) {
      testResult.value = {
        response: response.data.response,
        duration: duration,
        tokens: response.data.tokens_used || 0,
        cost: response.data.cost || 0
      }
      
      ElMessage.success('测试完成')
    } else {
      testError.value = response.error || '测试失败'
    }
  } catch (error) {
    testError.value = error.message || '测试请求失败'
    console.error('Model test error:', error)
  } finally {
    testing.value = false
  }
}

const clearTest = () => {
  testPrompt.value = ''
  testResult.value = null
  testError.value = ''
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

const getSpeedPercentage = (speed) => {
  // 假设最大速度为1000 tokens/s
  return Math.min((speed / 1000) * 100, 100)
}

const getSpeedColor = (speed) => {
  if (speed < 100) return '#f56c6c'
  if (speed < 500) return '#e6a23c'
  return '#67c23a'
}
</script>

<style scoped lang="scss">
.model-details {
  .info-card,
  .pricing-card,
  .performance-card,
  .usage-card,
  .test-card {
    margin-bottom: 24px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  .basic-info {
    .info-row {
      display: flex;
      gap: 24px;
      margin-bottom: 20px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .info-item {
        flex: 1;
        
        &.full-width {
          flex: none;
          width: 100%;
        }
        
        label {
          display: block;
          font-size: 13px;
          color: #909399;
          margin-bottom: 6px;
          font-weight: 500;
        }
        
        .provider-info {
          display: flex;
          align-items: center;
          gap: 8px;
          
          .provider-icon {
            width: 20px;
            height: 20px;
            border-radius: 4px;
          }
        }
        
        .value {
          font-size: 14px;
          color: #303133;
          font-weight: 500;
        }
        
        .description {
          margin: 0;
          font-size: 14px;
          color: #606266;
          line-height: 1.5;
        }
      }
    }
  }

  .pricing-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    
    .price-item {
      text-align: center;
      padding: 20px;
      background-color: #f8f9fa;
      border-radius: 8px;
      
      &.total-cost {
        background-color: #e3f2fd;
      }
      
      .price-type {
        font-size: 13px;
        color: #909399;
        margin-bottom: 8px;
        font-weight: 500;
      }
      
      .price-value {
        font-size: 18px;
        color: #303133;
        font-weight: 600;
        margin-bottom: 4px;
      }
      
      .cost-calculator {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin-bottom: 4px;
        
        .cost-result {
          font-size: 16px;
          color: #409eff;
          font-weight: 600;
        }
      }
      
      .price-note {
        font-size: 11px;
        color: #c0c4cc;
      }
    }
  }

  .performance-metrics {
    .metric-item {
      margin-bottom: 20px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .metric-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        
        .metric-name {
          font-size: 14px;
          color: #303133;
          font-weight: 500;
        }
        
        .metric-value {
          font-size: 13px;
          color: #606266;
          font-weight: 500;
        }
      }
    }
  }

  .usage-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 20px;
    
    .stat-item {
      text-align: center;
      
      .stat-value {
        font-size: 24px;
        color: #303133;
        font-weight: 600;
        margin-bottom: 4px;
      }
      
      .stat-label {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .test-section {
    .test-input {
      margin-bottom: 16px;
    }
    
    .test-controls {
      margin-bottom: 16px;
      
      label {
        display: block;
        font-size: 12px;
        color: #909399;
        margin-bottom: 4px;
      }
    }
    
    .test-actions {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
    }
    
    .test-result {
      border: 1px solid #e4e7ed;
      border-radius: 6px;
      overflow: hidden;
      
      .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        background-color: #f8f9fa;
        border-bottom: 1px solid #e4e7ed;
        
        .result-meta {
          display: flex;
          gap: 16px;
          font-size: 12px;
          color: #606266;
        }
      }
      
      .result-content {
        padding: 16px;
        
        pre {
          margin: 0;
          white-space: pre-wrap;
          word-wrap: break-word;
          font-family: inherit;
          font-size: 14px;
          color: #303133;
          line-height: 1.5;
        }
      }
    }
    
    .test-error {
      margin-top: 12px;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  :deep(.el-drawer) {
    width: 95% !important;
  }
  
  .model-details {
    .basic-info {
      .info-row {
        flex-direction: column;
        gap: 16px;
      }
    }
    
    .pricing-info {
      grid-template-columns: 1fr;
      
      .price-item {
        .cost-calculator {
          flex-direction: column;
          gap: 8px;
        }
      }
    }
    
    .usage-stats {
      grid-template-columns: repeat(2, 1fr);
    }
    
    .test-controls {
      :deep(.el-col) {
        margin-bottom: 12px;
      }
    }
  }
}
</style>
