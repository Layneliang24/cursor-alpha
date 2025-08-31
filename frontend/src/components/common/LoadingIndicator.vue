<template>
  <div 
    class="loading-indicator" 
    :class="loadingClasses"
    role="status"
    aria-live="polite"
    :aria-label="message || '加载中'"
  >
    <!-- 骨架屏加载 -->
    <div v-if="type === 'skeleton'" class="skeleton-loading">
      <el-skeleton :rows="skeletonRows" animated />
    </div>

    <!-- 卡片骨架屏 -->
    <div v-else-if="type === 'card-skeleton'" class="card-skeleton-loading">
      <el-skeleton animated>
        <template #template>
          <el-skeleton-item variant="image" style="width: 100%; height: 200px;" />
          <div style="padding: 14px;">
            <el-skeleton-item variant="h3" style="width: 50%;" />
            <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 16px;">
              <el-skeleton-item variant="text" style="width: 60%;" />
              <el-skeleton-item variant="button" style="width: 80px;" />
            </div>
          </div>
        </template>
      </el-skeleton>
    </div>

    <!-- 列表骨架屏 -->
    <div v-else-if="type === 'list-skeleton'" class="list-skeleton-loading">
      <div v-for="i in skeletonRows" :key="i" class="list-item-skeleton">
        <el-skeleton animated>
          <template #template>
            <div style="display: flex; align-items: center;">
              <el-skeleton-item variant="circle" style="width: 40px; height: 40px; margin-right: 16px;" />
              <div style="flex: 1;">
                <el-skeleton-item variant="h4" style="width: 40%; margin-bottom: 8px;" />
                <el-skeleton-item variant="text" style="width: 80%;" />
              </div>
            </div>
          </template>
        </el-skeleton>
      </div>
    </div>

    <!-- 打字指示器 -->
    <div v-else-if="type === 'typing'" class="typing-indicator">
      <div class="typing-dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
      <span v-if="message" class="typing-message">{{ message }}</span>
    </div>

    <!-- 进度条加载 -->
    <div v-else-if="type === 'progress'" class="progress-loading">
      <el-progress 
        :percentage="progressValue" 
        :status="progressStatus"
        :stroke-width="strokeWidth"
        :show-text="showProgressText"
      />
      <div v-if="message" class="progress-message">{{ message }}</div>
    </div>

    <!-- 脉冲加载 -->
    <div v-else-if="type === 'pulse'" class="pulse-loading">
      <div class="pulse-circle">
        <div class="pulse-ring"></div>
        <div class="pulse-ring"></div>
        <div class="pulse-ring"></div>
      </div>
      <div v-if="message" class="pulse-message">{{ message }}</div>
    </div>

    <!-- 波浪加载 -->
    <div v-else-if="type === 'wave'" class="wave-loading">
      <div class="wave-container">
        <div class="wave-bar" v-for="i in 5" :key="i" :style="{ animationDelay: `${i * 0.1}s` }"></div>
      </div>
      <div v-if="message" class="wave-message">{{ message }}</div>
    </div>

    <!-- 默认旋转加载 -->
    <div v-else class="spinner-loading">
      <el-icon class="loading-spinner" :size="iconSize">
        <Loading />
      </el-icon>
      <div v-if="message" class="spinner-message">{{ message }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Loading } from '@element-plus/icons-vue'

const props = defineProps({
  // 加载类型
  type: {
    type: String,
    default: 'spinner',
    validator: (value) => [
      'spinner', 'skeleton', 'card-skeleton', 'list-skeleton', 
      'typing', 'progress', 'pulse', 'wave'
    ].includes(value)
  },
  
  // 加载消息
  message: {
    type: String,
    default: ''
  },
  
  // 大小
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  
  // 骨架屏行数
  skeletonRows: {
    type: Number,
    default: 3
  },
  
  // 图标大小
  iconSize: {
    type: [String, Number],
    default: 24
  },
  
  // 进度值
  progress: {
    type: Number,
    default: 0
  },
  
  // 进度状态
  progressStatus: {
    type: String,
    default: '',
    validator: (value) => ['', 'success', 'exception', 'warning'].includes(value)
  },
  
  // 进度条宽度
  strokeWidth: {
    type: Number,
    default: 6
  },
  
  // 是否显示进度文本
  showProgressText: {
    type: Boolean,
    default: true
  },
  
  // 是否居中显示
  center: {
    type: Boolean,
    default: false
  },
  
  // 是否覆盖整个容器
  overlay: {
    type: Boolean,
    default: false
  },
  
  // 背景色
  background: {
    type: String,
    default: 'rgba(255, 255, 255, 0.9)'
  }
})

// 响应式进度值
const progressValue = ref(props.progress)

// 监听进度变化
watch(() => props.progress, (newValue) => {
  progressValue.value = newValue
})

// 计算样式类
const loadingClasses = computed(() => {
  return {
    [`loading-${props.size}`]: true,
    'loading-center': props.center,
    'loading-overlay': props.overlay
  }
})

// 自动递增进度（当进度类型且没有传入具体进度时）
if (props.type === 'progress' && props.progress === 0) {
  const incrementProgress = () => {
    if (progressValue.value < 90) {
      progressValue.value += Math.random() * 10
      setTimeout(incrementProgress, 500 + Math.random() * 500)
    }
  }
  incrementProgress()
}
</script>

<style scoped>
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60px;
}

.loading-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: v-bind(background);
  z-index: 1000;
}

/* 尺寸变体 */
.loading-small {
  min-height: 40px;
  font-size: 12px;
}

.loading-medium {
  min-height: 60px;
  font-size: 14px;
}

.loading-large {
  min-height: 80px;
  font-size: 16px;
}

/* 旋转加载器 */
.spinner-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.loading-spinner {
  animation: spin 1s linear infinite;
  color: var(--el-color-primary);
}

.spinner-message {
  color: var(--el-text-color-regular);
  font-size: inherit;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 骨架屏 */
.skeleton-loading,
.card-skeleton-loading,
.list-skeleton-loading {
  width: 100%;
}

.list-item-skeleton {
  margin-bottom: 16px;
}

.list-item-skeleton:last-child {
  margin-bottom: 0;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--el-color-primary);
  animation: typing 1.4s infinite ease-in-out;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1.2);
    opacity: 1;
  }
}

.typing-message {
  color: var(--el-text-color-regular);
  font-size: inherit;
}

/* 进度加载器 */
.progress-loading {
  width: 100%;
  max-width: 300px;
}

.progress-message {
  text-align: center;
  margin-top: 8px;
  color: var(--el-text-color-regular);
  font-size: inherit;
}

/* 脉冲加载器 */
.pulse-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.pulse-circle {
  position: relative;
  width: 40px;
  height: 40px;
}

.pulse-ring {
  position: absolute;
  border: 2px solid var(--el-color-primary);
  border-radius: 50%;
  width: 100%;
  height: 100%;
  animation: pulse 1.25s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
}

.pulse-ring:nth-child(2) { animation-delay: -0.4s; }
.pulse-ring:nth-child(3) { animation-delay: -0.8s; }

@keyframes pulse {
  0% {
    transform: scale(0);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
}

.pulse-message {
  color: var(--el-text-color-regular);
  font-size: inherit;
}

/* 波浪加载器 */
.wave-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.wave-container {
  display: flex;
  gap: 4px;
  align-items: end;
  height: 30px;
}

.wave-bar {
  width: 4px;
  height: 10px;
  background-color: var(--el-color-primary);
  border-radius: 2px;
  animation: wave 1.2s infinite ease-in-out;
}

@keyframes wave {
  0%, 40%, 100% {
    transform: scaleY(0.4);
  }
  20% {
    transform: scaleY(1);
  }
}

.wave-message {
  color: var(--el-text-color-regular);
  font-size: inherit;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .loading-indicator {
    min-height: 50px;
  }
  
  .loading-small { min-height: 35px; }
  .loading-medium { min-height: 50px; }
  .loading-large { min-height: 65px; }
  
  .pulse-circle {
    width: 30px;
    height: 30px;
  }
  
  .wave-container {
    height: 25px;
  }
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .loading-overlay {
    background: rgba(0, 0, 0, 0.8);
  }
}
</style>
