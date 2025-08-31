import { ref, computed, onUnmounted } from 'vue'
import { useLoadingStore } from '@/stores/modules/loadingStore'
import { ElLoading, ElMessage } from 'element-plus'

/**
 * 加载状态管理组合式函数
 */
export function useLoading (key = null, options = {}) {
  const loadingStore = useLoadingStore()
  const loadingKey = key || `loading_${Date.now()}_${Math.random()}`
  
  const {
    minTime = 300,
    message = '加载中...',
    global = false,
    autoHide = true,
  } = options

  // 本地加载状态
  const loading = ref(false)
  const loadingMessage = ref(message)
  
  // 加载实例（用于手动控制）
  let loadingInstance = null

  // 计算属性
  const isLoading = computed(() => {
    return global ? loadingStore.globalLoading : (loading.value || loadingStore.isLoading(loadingKey))
  })

  // 显示加载
  const show = (msg = loadingMessage.value) => {
    loadingMessage.value = msg
    loading.value = true
    
    if (global) {
      loadingStore.showGlobalLoading({ text: msg })
    } else {
      loadingStore.showLoading(loadingKey, { message: msg, minTime })
    }
  }

  // 隐藏加载
  const hide = async () => {
    loading.value = false
    
    if (global) {
      loadingStore.hideGlobalLoading()
    } else {
      await loadingStore.hideLoading(loadingKey)
    }
  }

  // 切换加载状态
  const toggle = (msg) => {
    if (isLoading.value) {
      hide()
    } else {
      show(msg)
    }
  }

  // 包装异步函数
  const withLoading = async (asyncFn, loadingOptions = {}) => {
    const { 
      message: loadingMsg = loadingMessage.value,
      onError = null,
      showErrorMessage = true,
      errorMessage = '操作失败',
    } = loadingOptions

    try {
      show(loadingMsg)
      const result = await asyncFn()
      return result
    } catch (error) {
      if (onError) {
        onError(error)
      } else if (showErrorMessage) {
        ElMessage.error(`${errorMessage}: ${error.message || '未知错误'}`)
      }
      throw error
    } finally {
      if (autoHide) {
        await hide()
      }
    }
  }

  // 创建指令式加载
  const createDirectiveLoading = (target, options = {}) => {
    const {
      text = '加载中...',
      spinner = 'el-icon-loading',
      background = 'rgba(255, 255, 255, 0.9)',
      customClass = '',
    } = options

    if (loadingInstance) {
      loadingInstance.close()
    }

    loadingInstance = ElLoading.service({
      target,
      lock: true,
      text,
      spinner,
      background,
      customClass,
    })

    return loadingInstance
  }

  // 关闭指令式加载
  const closeDirectiveLoading = () => {
    if (loadingInstance) {
      loadingInstance.close()
      loadingInstance = null
    }
  }

  // 清理函数
  const cleanup = () => {
    if (isLoading.value) {
      hide()
    }
    closeDirectiveLoading()
  }

  // 组件卸载时自动清理
  onUnmounted(() => {
    cleanup()
  })

  return {
    // 状态
    loading: isLoading,
    loadingMessage,
    
    // 方法
    show,
    hide,
    toggle,
    withLoading,
    createDirectiveLoading,
    closeDirectiveLoading,
    cleanup,
  }
}

/**
 * 页面级加载管理
 */
export function usePageLoading () {
  const loadingStore = useLoadingStore()
  
  const pageLoading = ref(false)
  const pageLoadingMessage = ref('页面加载中...')
  
  // 显示页面加载
  const showPageLoading = (message = '页面加载中...') => {
    pageLoadingMessage.value = message
    pageLoading.value = true
    loadingStore.showGlobalLoading({ text: message })
  }
  
  // 隐藏页面加载
  const hidePageLoading = () => {
    pageLoading.value = false
    loadingStore.hideGlobalLoading()
  }
  
  // 页面加载包装器
  const withPageLoading = async (asyncFn, message) => {
    try {
      showPageLoading(message)
      const result = await asyncFn()
      return result
    } finally {
      hidePageLoading()
    }
  }

  return {
    pageLoading,
    pageLoadingMessage,
    showPageLoading,
    hidePageLoading,
    withPageLoading,
  }
}

/**
 * 批量加载管理
 */
export function useBatchLoading () {
  const loadingStore = useLoadingStore()
  const batchLoadings = ref(new Map())
  
  // 添加批量加载项
  const addLoading = (key, message = '加载中...') => {
    batchLoadings.value.set(key, { message, loading: true })
    loadingStore.showLoading(key, { message })
  }
  
  // 移除批量加载项
  const removeLoading = async (key) => {
    batchLoadings.value.delete(key)
    await loadingStore.hideLoading(key)
  }
  
  // 检查是否有任何加载项
  const hasAnyLoading = computed(() => {
    return Array.from(batchLoadings.value.values()).some(item => item.loading)
  })
  
  // 清除所有加载
  const clearAllLoading = async () => {
    const keys = Array.from(batchLoadings.value.keys())
    batchLoadings.value.clear()
    
    for (const key of keys) {
      await loadingStore.hideLoading(key)
    }
  }
  
  // 批量执行异步操作
  const executeWithBatchLoading = async (tasks) => {
    const results = []
    
    try {
      // 启动所有加载状态
      tasks.forEach((task, index) => {
        addLoading(`batch_${index}`, task.message || `任务 ${index + 1}`)
      })
      
      // 并行执行任务
      const promises = tasks.map(async (task, index) => {
        try {
          const result = await task.fn()
          await removeLoading(`batch_${index}`)
          return { success: true, result, index }
        } catch (error) {
          await removeLoading(`batch_${index}`)
          return { success: false, error, index }
        }
      })
      
      const taskResults = await Promise.allSettled(promises)
      
      // 处理结果
      taskResults.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          results[index] = result.value
        } else {
          results[index] = { success: false, error: result.reason, index }
        }
      })
      
      return results
      
    } finally {
      await clearAllLoading()
    }
  }

  return {
    batchLoadings,
    hasAnyLoading,
    addLoading,
    removeLoading,
    clearAllLoading,
    executeWithBatchLoading,
  }
}

/**
 * 步骤式加载管理
 */
export function useStepLoading (steps = []) {
  const currentStep = ref(0)
  const totalSteps = ref(steps.length)
  const stepMessages = ref(steps)
  
  const progress = computed(() => {
    return totalSteps.value > 0 ? Math.round((currentStep.value / totalSteps.value) * 100) : 0
  })
  
  const currentMessage = computed(() => {
    return stepMessages.value[currentStep.value] || '处理中...'
  })
  
  const isComplete = computed(() => {
    return currentStep.value >= totalSteps.value
  })
  
  // 下一步
  const nextStep = (message) => {
    if (currentStep.value < totalSteps.value) {
      currentStep.value++
      if (message) {
        stepMessages.value[currentStep.value - 1] = message
      }
    }
  }
  
  // 跳转到指定步骤
  const goToStep = (step) => {
    if (step >= 0 && step <= totalSteps.value) {
      currentStep.value = step
    }
  }
  
  // 重置步骤
  const resetSteps = (newSteps = []) => {
    currentStep.value = 0
    if (newSteps.length > 0) {
      stepMessages.value = newSteps
      totalSteps.value = newSteps.length
    }
  }
  
  // 执行步骤式异步操作
  const executeSteps = async (stepFunctions) => {
    resetSteps()
    totalSteps.value = stepFunctions.length
    
    const results = []
    
    for (let i = 0; i < stepFunctions.length; i++) {
      currentStep.value = i
      
      try {
        const result = await stepFunctions[i]()
        results.push({ success: true, result, step: i })
        nextStep()
      } catch (error) {
        results.push({ success: false, error, step: i })
        throw error // 停止执行后续步骤
      }
    }
    
    return results
  }

  return {
    currentStep,
    totalSteps,
    stepMessages,
    progress,
    currentMessage,
    isComplete,
    nextStep,
    goToStep,
    resetSteps,
    executeSteps,
  }
}

/**
 * 智能加载管理（自动检测加载类型）
 */
export function useSmartLoading (options = {}) {
  const {
    fastThreshold = 500,    // 快速操作阈值
    slowThreshold = 3000,   // 慢操作阈值
    autoType = true,         // 自动检测加载类型
  } = options
  
  const loading = useLoading()
  const startTime = ref(0)
  const loadingType = ref('spinner')
  
  // 智能显示加载
  const smartShow = (message) => {
    startTime.value = Date.now()
    
    if (autoType) {
      // 先显示简单的spinner
      loadingType.value = 'spinner'
      loading.show(message)
      
      // 如果加载时间较长，切换到更丰富的加载指示器
      setTimeout(() => {
        if (loading.loading.value) {
          loadingType.value = 'pulse'
        }
      }, slowThreshold)
    } else {
      loading.show(message)
    }
  }
  
  // 智能隐藏加载
  const smartHide = async () => {
    const duration = Date.now() - startTime.value
    
    // 记录加载时间，用于优化
    if (process.env.NODE_ENV === 'development') {
      if (duration > slowThreshold) {
        console.warn(`🐌 慢加载操作: ${duration}ms`)
      }
    }
    
    await loading.hide()
  }
  
  // 智能包装异步函数
  const smartWithLoading = async (asyncFn, message) => {
    try {
      smartShow(message)
      const result = await asyncFn()
      return result
    } finally {
      await smartHide()
    }
  }

  return {
    ...loading,
    loadingType,
    smartShow,
    smartHide,
    smartWithLoading,
  }
}
