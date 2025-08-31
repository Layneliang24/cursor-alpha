<template>
  <div class="error-boundary">
    <slot v-if="!hasError" />
    
    <!-- 错误状态显示 -->
    <div v-else class="error-display">
      <el-result
        :icon="errorIcon"
        :title="errorTitle"
        :sub-title="errorMessage"
        class="error-result"
      >
        <template #extra>
          <div class="error-actions">
            <el-button type="primary" @click="retry" :loading="retrying">
              <el-icon><Refresh /></el-icon>
              重试
            </el-button>
            
            <el-button @click="goHome" v-if="showHomeButton">
              <el-icon><HomeFilled /></el-icon>
              返回首页
            </el-button>
            
            <el-button 
              type="info" 
              text 
              @click="toggleDetails"
              v-if="showDetails && errorDetails"
            >
              {{ showErrorDetails ? '隐藏' : '显示' }}详细信息
            </el-button>
          </div>

          <!-- 错误详情 -->
          <el-collapse-transition>
            <div v-if="showErrorDetails && errorDetails" class="error-details">
              <el-alert
                title="错误详情"
                type="warning"
                :closable="false"
                show-icon
              >
                <div class="error-details-content">
                  <p><strong>错误类型:</strong> {{ errorType }}</p>
                  <p><strong>发生时间:</strong> {{ errorTime }}</p>
                  <p v-if="errorDetails.stack">
                    <strong>堆栈信息:</strong>
                  </p>
                  <pre v-if="errorDetails.stack" class="error-stack">{{ errorDetails.stack }}</pre>
                  <p v-if="errorDetails.componentStack">
                    <strong>组件堆栈:</strong>
                  </p>
                  <pre v-if="errorDetails.componentStack" class="error-stack">{{ errorDetails.componentStack }}</pre>
                </div>
              </el-alert>
            </div>
          </el-collapse-transition>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, HomeFilled } from '@element-plus/icons-vue'

const props = defineProps({
  // 是否显示返回首页按钮
  showHomeButton: {
    type: Boolean,
    default: true
  },
  
  // 是否显示错误详情
  showDetails: {
    type: Boolean,
    default: process.env.NODE_ENV === 'development'
  },
  
  // 自定义错误消息
  fallbackMessage: {
    type: String,
    default: '页面出现了一些问题'
  },
  
  // 重试回调
  onRetry: {
    type: Function,
    default: null
  },
  
  // 错误回调
  onError: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['error', 'retry'])

const router = useRouter()

// 错误状态
const hasError = ref(false)
const errorDetails = ref(null)
const errorTime = ref('')
const retrying = ref(false)
const showErrorDetails = ref(false)

// 计算属性
const errorIcon = computed(() => {
  if (!errorDetails.value) return 'warning'
  
  const error = errorDetails.value
  if (error.name === 'ChunkLoadError' || error.message?.includes('Loading chunk')) {
    return 'refresh'
  }
  if (error.name === 'NetworkError' || error.message?.includes('Network')) {
    return 'connection'
  }
  return 'warning'
})

const errorTitle = computed(() => {
  if (!errorDetails.value) return '出现错误'
  
  const error = errorDetails.value
  if (error.name === 'ChunkLoadError' || error.message?.includes('Loading chunk')) {
    return '资源加载失败'
  }
  if (error.name === 'NetworkError' || error.message?.includes('Network')) {
    return '网络连接错误'
  }
  if (error.name === 'TypeError') {
    return '组件错误'
  }
  return '页面错误'
})

const errorMessage = computed(() => {
  if (!errorDetails.value) return props.fallbackMessage
  
  const error = errorDetails.value
  if (error.name === 'ChunkLoadError' || error.message?.includes('Loading chunk')) {
    return '页面资源加载失败，可能是网络问题或版本更新导致的'
  }
  if (error.name === 'NetworkError' || error.message?.includes('Network')) {
    return '网络连接不稳定，请检查网络后重试'
  }
  if (error.name === 'TypeError' && error.message?.includes('Cannot read property')) {
    return '页面数据加载异常，请重试'
  }
  
  return error.message || props.fallbackMessage
})

const errorType = computed(() => {
  return errorDetails.value?.name || 'Unknown'
})

// 方法
const captureError = (error, errorInfo) => {
  hasError.value = true
  errorTime.value = new Date().toLocaleString()
  
  errorDetails.value = {
    name: error.name,
    message: error.message,
    stack: error.stack,
    componentStack: errorInfo
  }

  // 发送错误事件
  emit('error', { error, errorInfo })
  
  // 调用错误回调
  if (props.onError) {
    props.onError(error, errorInfo)
  }

  // 记录错误日志
  logError(error, errorInfo)
}

const retry = async () => {
  retrying.value = true
  
  try {
    // 调用自定义重试回调
    if (props.onRetry) {
      await props.onRetry()
    } else {
      // 默认重试：重新加载页面
      await nextTick()
      window.location.reload()
    }
    
    // 如果没有重新加载页面，则重置错误状态
    resetError()
    
    emit('retry')
    ElMessage.success('重试成功')
    
  } catch (error) {
    ElMessage.error('重试失败: ' + error.message)
  } finally {
    retrying.value = false
  }
}

const resetError = () => {
  hasError.value = false
  errorDetails.value = null
  showErrorDetails.value = false
}

const goHome = () => {
  router.push('/')
}

const toggleDetails = () => {
  showErrorDetails.value = !showErrorDetails.value
}

const logError = (error, errorInfo) => {
  const logData = {
    timestamp: new Date().toISOString(),
    error: {
      name: error.name,
      message: error.message,
      stack: error.stack
    },
    errorInfo,
    userAgent: navigator.userAgent,
    url: window.location.href,
    userId: localStorage.getItem('userId') || 'anonymous'
  }

  // 开发环境输出到控制台
  if (process.env.NODE_ENV === 'development') {
    console.group('🚨 Error Boundary Caught Error')
    console.error('Error:', error)
    console.error('Error Info:', errorInfo)
    console.error('Log Data:', logData)
    console.groupEnd()
  }

  // 生产环境发送到错误监控服务
  if (process.env.NODE_ENV === 'production') {
    sendErrorToService(logData)
  }
}

const sendErrorToService = async (logData) => {
  try {
    // 这里可以集成错误监控服务
    // await fetch('/api/errors', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify(logData)
    // })
  } catch (error) {
    console.warn('Failed to send error to service:', error)
  }
}

// 全局错误处理器
const handleGlobalError = (event) => {
  if (!hasError.value) {
    captureError(event.error, 'Global Error Handler')
  }
}

const handleUnhandledRejection = (event) => {
  if (!hasError.value) {
    const error = new Error(event.reason)
    error.name = 'UnhandledPromiseRejection'
    captureError(error, 'Unhandled Promise Rejection')
  }
}

// 生命周期
onMounted(() => {
  // 监听全局错误
  window.addEventListener('error', handleGlobalError)
  window.addEventListener('unhandledrejection', handleUnhandledRejection)
})

onUnmounted(() => {
  // 清理事件监听器
  window.removeEventListener('error', handleGlobalError)
  window.removeEventListener('unhandledrejection', handleUnhandledRejection)
})

// 暴露方法给父组件
defineExpose({
  captureError,
  resetError,
  hasError: hasError.value
})
</script>

<style scoped>
.error-boundary {
  width: 100%;
  height: 100%;
  min-height: 200px;
}

.error-display {
  padding: 20px;
  text-align: center;
}

.error-result {
  background: transparent;
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.error-details {
  max-width: 800px;
  margin: 0 auto;
  text-align: left;
}

.error-details-content {
  font-size: 14px;
  line-height: 1.6;
}

.error-details-content p {
  margin: 8px 0;
}

.error-stack {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.4;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .error-actions .el-button {
    width: 200px;
  }
  
  .error-details {
    padding: 0 10px;
  }
  
  .error-stack {
    font-size: 11px;
  }
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .error-stack {
    background: #2d2d2d;
    color: #e4e7ed;
    border-color: #4c4d4f;
  }
}
</style>
