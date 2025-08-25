<template>
  <div class="feature-flag-wrapper">
    <!-- 开发环境下的特性开关调试面板 -->
    <div v-if="isDevelopment && showDebugPanel" class="feature-flag-debug-panel">
      <div class="debug-header">
        <h3>特性开关调试面板</h3>
        <button @click="toggleDebugPanel" class="close-btn">×</button>
      </div>
      
      <div class="debug-content">
        <div class="debug-info">
          <p><strong>环境:</strong> {{ environment }}</p>
          <p><strong>加载状态:</strong> 
            <span :class="loadingStateClass">{{ loadingStateText }}</span>
          </p>
          <p><strong>特性开关数量:</strong> {{ flagCount }}</p>
        </div>
        
        <div class="debug-actions">
          <button @click="refreshFlags" :disabled="loading" class="refresh-btn">
            {{ loading ? '刷新中...' : '刷新特性开关' }}
          </button>
          <button @click="clearCache" class="clear-cache-btn">
            清除缓存
          </button>
        </div>
        
        <div class="flags-list">
          <h4>特性开关列表</h4>
          <div v-if="Object.keys(flags).length === 0" class="no-flags">
            暂无特性开关
          </div>
          <div v-else class="flag-items">
            <div 
              v-for="(flag, key) in flags" 
              :key="key" 
              class="flag-item"
              :class="{ 'flag-enabled': flag.enabled }"
            >
              <div class="flag-info">
                <div class="flag-key">{{ key }}</div>
                <div class="flag-name">{{ flag.name }}</div>
                <div class="flag-description">{{ flag.description }}</div>
              </div>
              <div class="flag-status">
                <span class="status-badge" :class="flag.enabled ? 'enabled' : 'disabled'">
                  {{ flag.enabled ? '启用' : '禁用' }}
                </span>
                <div v-if="flag.value && Object.keys(flag.value).length > 0" class="flag-value">
                  <small>值: {{ JSON.stringify(flag.value) }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 特性开关内容插槽 -->
    <div v-if="shouldShow" class="feature-content">
      <slot :flag="currentFlag" :enabled="isEnabled" :value="flagValue"></slot>
    </div>
    
    <!-- 备用内容插槽 -->
    <div v-else-if="$slots.fallback" class="fallback-content">
      <slot name="fallback"></slot>
    </div>
  </div>
</template>

<script>
import { computed, ref, onMounted } from 'vue'
import { useFeatureFlags } from '@/services/featureFlags'

export default {
  name: 'FeatureFlag',
  props: {
    // 特性开关键
    flag: {
      type: String,
      required: true
    },
    // 默认值
    defaultValue: {
      type: Boolean,
      default: false
    },
    // 是否显示调试面板（仅开发环境）
    debug: {
      type: Boolean,
      default: false
    },
    // 反转逻辑（当特性开关禁用时显示内容）
    invert: {
      type: Boolean,
      default: false
    }
  },
  
  setup(props) {
    const {
      flags,
      loading,
      error,
      initialized,
      isEnabled,
      getValue,
      refresh,
      clearCache
    } = useFeatureFlags()
    
    const showDebugPanel = ref(false)
    
    // 计算属性
    const isDevelopment = computed(() => {
      return import.meta.env.MODE === 'development'
    })
    
    const environment = computed(() => {
      return import.meta.env.MODE || 'development'
    })
    
    const currentFlag = computed(() => {
      return flags[props.flag]
    })
    
    const isEnabledValue = computed(() => {
      return isEnabled(props.flag, props.defaultValue)
    })
    
    const shouldShow = computed(() => {
      return props.invert ? !isEnabledValue.value : isEnabledValue.value
    })
    
    const flagValue = computed(() => {
      return getValue(props.flag, null)
    })
    
    const flagCount = computed(() => {
      return Object.keys(flags).length
    })
    
    const loadingStateClass = computed(() => {
      if (loading.value) return 'loading'
      if (error.value) return 'error'
      if (initialized.value) return 'success'
      return 'pending'
    })
    
    const loadingStateText = computed(() => {
      if (loading.value) return '加载中'
      if (error.value) return `错误: ${error.value}`
      if (initialized.value) return '已加载'
      return '未初始化'
    })
    
    // 方法
    const toggleDebugPanel = () => {
      showDebugPanel.value = !showDebugPanel.value
    }
    
    const refreshFlags = async () => {
      try {
        await refresh()
      } catch (err) {
        console.error('Failed to refresh feature flags:', err)
      }
    }
    
    const clearCacheHandler = () => {
      clearCache()
      refreshFlags()
    }
    
    // 生命周期
    onMounted(() => {
      if (props.debug && isDevelopment.value) {
        showDebugPanel.value = true
      }
    })
    
    return {
      // 响应式数据
      flags,
      loading,
      error,
      initialized,
      showDebugPanel,
      
      // 计算属性
      isDevelopment,
      environment,
      currentFlag,
      isEnabled: isEnabledValue,
      shouldShow,
      flagValue,
      flagCount,
      loadingStateClass,
      loadingStateText,
      
      // 方法
      toggleDebugPanel,
      refreshFlags,
      clearCache: clearCacheHandler
    }
  }
}
</script>

<style scoped>
.feature-flag-wrapper {
  position: relative;
}

.feature-flag-debug-panel {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 400px;
  max-height: 80vh;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.debug-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #495057;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #495057;
}

.debug-content {
  padding: 16px;
  max-height: calc(80vh - 60px);
  overflow-y: auto;
}

.debug-info {
  margin-bottom: 16px;
}

.debug-info p {
  margin: 4px 0;
  font-size: 12px;
  color: #6c757d;
}

.debug-info strong {
  color: #495057;
}

.loading {
  color: #007bff;
}

.error {
  color: #dc3545;
}

.success {
  color: #28a745;
}

.pending {
  color: #ffc107;
}

.debug-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.refresh-btn,
.clear-cache-btn {
  padding: 6px 12px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: #fff;
  color: #495057;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover,
.clear-cache-btn:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.flags-list h4 {
  margin: 0 0 12px 0;
  font-size: 13px;
  font-weight: 600;
  color: #495057;
}

.no-flags {
  text-align: center;
  color: #6c757d;
  font-size: 12px;
  padding: 20px;
}

.flag-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.flag-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 8px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: #f8f9fa;
  transition: all 0.2s;
}

.flag-item.flag-enabled {
  border-color: #28a745;
  background: #d4edda;
}

.flag-info {
  flex: 1;
  min-width: 0;
}

.flag-key {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  color: #495057;
  margin-bottom: 2px;
}

.flag-name {
  font-size: 12px;
  font-weight: 500;
  color: #212529;
  margin-bottom: 2px;
}

.flag-description {
  font-size: 11px;
  color: #6c757d;
  line-height: 1.3;
}

.flag-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.status-badge {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.enabled {
  background: #28a745;
  color: white;
}

.status-badge.disabled {
  background: #6c757d;
  color: white;
}

.flag-value {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 10px;
  color: #495057;
  max-width: 120px;
  word-break: break-all;
}

.feature-content,
.fallback-content {
  /* 继承父容器样式 */
}

/* 响应式设计 */
@media (max-width: 768px) {
  .feature-flag-debug-panel {
    width: calc(100vw - 40px);
    right: 20px;
    left: 20px;
  }
}
</style>