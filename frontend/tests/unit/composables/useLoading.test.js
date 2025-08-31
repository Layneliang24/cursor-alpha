import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { nextTick } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import { useLoading, usePageLoading, useBatchLoading, useStepLoading } from '@/composables/useLoading'
import { useLoadingStore } from '@/stores/modules/loadingStore'

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElLoading: {
    service: vi.fn().mockReturnValue({
      close: vi.fn(),
    }),
  },
  ElMessage: {
    error: vi.fn(),
  },
}))

describe('useLoading', () => {
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('基础加载功能', () => {
    it('应该初始化加载状态', () => {
      const { loading, show, hide } = useLoading('test-key')

      expect(loading.value).toBe(false)
      expect(typeof show).toBe('function')
      expect(typeof hide).toBe('function')
    })

    it('应该显示和隐藏加载状态', async () => {
      const { loading, show, hide } = useLoading('test-key')

      expect(loading.value).toBe(false)

      show('测试加载')
      await nextTick()
      expect(loading.value).toBe(true)

      await hide()
      expect(loading.value).toBe(false)
    })

    it('应该支持切换加载状态', async () => {
      const { loading, toggle } = useLoading('test-key')

      expect(loading.value).toBe(false)

      toggle('测试消息')
      await nextTick()
      expect(loading.value).toBe(true)

      toggle()
      await nextTick()
      expect(loading.value).toBe(false)
    })

    it('应该支持全局加载模式', async () => {
      const { loading, show, hide } = useLoading('test-key', { global: true })
      const loadingStore = useLoadingStore()

      show('全局加载')
      await nextTick()
      expect(loadingStore.globalLoading).toBe(true)

      hide()
      await nextTick()
      expect(loadingStore.globalLoading).toBe(false)
    })
  })

  describe('异步函数包装', () => {
    it('应该包装异步函数并管理加载状态', async () => {
      const { loading, withLoading } = useLoading('test-key')
      
      const asyncFn = vi.fn().mockResolvedValue('success')

      expect(loading.value).toBe(false)

      const promise = withLoading(asyncFn, { message: '执行中...' })
      
      // 加载应该立即开始
      await nextTick()
      expect(loading.value).toBe(true)

      const result = await promise
      
      // 加载应该在完成后结束
      expect(loading.value).toBe(false)
      expect(result).toBe('success')
      expect(asyncFn).toHaveBeenCalled()
    })

    it('应该在异步函数出错时隐藏加载状态', async () => {
      const { loading, withLoading } = useLoading('test-key')
      
      const error = new Error('测试错误')
      const asyncFn = vi.fn().mockRejectedValue(error)

      try {
        await withLoading(asyncFn)
      } catch (e) {
        expect(e).toBe(error)
      }

      expect(loading.value).toBe(false)
    })

    it('应该支持自定义错误处理', async () => {
      const { withLoading } = useLoading('test-key')
      
      const error = new Error('测试错误')
      const asyncFn = vi.fn().mockRejectedValue(error)
      const onError = vi.fn()

      try {
        await withLoading(asyncFn, { onError })
      } catch (e) {
        // 错误应该被重新抛出
        expect(e).toBe(error)
      }

      expect(onError).toHaveBeenCalledWith(error)
    })

    it('应该支持禁用错误消息', async () => {
      const { withLoading } = useLoading('test-key')
      
      const error = new Error('测试错误')
      const asyncFn = vi.fn().mockRejectedValue(error)

      try {
        await withLoading(asyncFn, { showErrorMessage: false })
      } catch (e) {
        expect(e).toBe(error)
      }

      // ElMessage.error 不应该被调用
      const { ElMessage } = await import('element-plus')
      expect(ElMessage.error).not.toHaveBeenCalled()
    })
  })

  describe('清理功能', () => {
    it('应该在组件卸载时清理加载状态', () => {
      const { cleanup, loading, show } = useLoading('test-key')

      show('测试加载')
      expect(loading.value).toBe(true)

      cleanup()
      expect(loading.value).toBe(false)
    })
  })
})

describe('usePageLoading', () => {
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
  })

  it('应该管理页面级加载状态', async () => {
    const { pageLoading, showPageLoading, hidePageLoading } = usePageLoading()
    const loadingStore = useLoadingStore()

    expect(pageLoading.value).toBe(false)
    expect(loadingStore.globalLoading).toBe(false)

    showPageLoading('页面加载中...')
    await nextTick()
    expect(pageLoading.value).toBe(true)
    expect(loadingStore.globalLoading).toBe(true)

    hidePageLoading()
    await nextTick()
    expect(pageLoading.value).toBe(false)
    expect(loadingStore.globalLoading).toBe(false)
  })

  it('应该包装页面级异步操作', async () => {
    const { pageLoading, withPageLoading } = usePageLoading()
    
    const asyncFn = vi.fn().mockResolvedValue('页面数据')

    expect(pageLoading.value).toBe(false)

    const promise = withPageLoading(asyncFn, '加载页面数据...')
    
    await nextTick()
    expect(pageLoading.value).toBe(true)

    const result = await promise
    
    expect(pageLoading.value).toBe(false)
    expect(result).toBe('页面数据')
  })
})

describe('useBatchLoading', () => {
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
  })

  it('应该管理批量加载状态', async () => {
    const { batchLoadings, hasAnyLoading, addLoading, removeLoading } = useBatchLoading()

    expect(hasAnyLoading.value).toBe(false)
    expect(batchLoadings.value.size).toBe(0)

    addLoading('task1', '任务1')
    addLoading('task2', '任务2')
    
    await nextTick()
    expect(hasAnyLoading.value).toBe(true)
    expect(batchLoadings.value.size).toBe(2)

    await removeLoading('task1')
    expect(batchLoadings.value.size).toBe(1)
    expect(hasAnyLoading.value).toBe(true)

    await removeLoading('task2')
    expect(batchLoadings.value.size).toBe(0)
    expect(hasAnyLoading.value).toBe(false)
  })

  it('应该清除所有批量加载', async () => {
    const { batchLoadings, addLoading, clearAllLoading } = useBatchLoading()

    addLoading('task1', '任务1')
    addLoading('task2', '任务2')
    addLoading('task3', '任务3')

    expect(batchLoadings.value.size).toBe(3)

    await clearAllLoading()
    expect(batchLoadings.value.size).toBe(0)
  })

  it('应该执行批量异步操作', async () => {
    const { executeWithBatchLoading } = useBatchLoading()

    const task1 = { fn: vi.fn().mockResolvedValue('结果1'), message: '任务1' }
    const task2 = { fn: vi.fn().mockResolvedValue('结果2'), message: '任务2' }
    const task3 = { fn: vi.fn().mockRejectedValue(new Error('错误3')), message: '任务3' }

    const results = await executeWithBatchLoading([task1, task2, task3])

    expect(results).toHaveLength(3)
    expect(results[0]).toEqual({ success: true, result: '结果1', index: 0 })
    expect(results[1]).toEqual({ success: true, result: '结果2', index: 1 })
    expect(results[2]).toEqual({ success: false, error: expect.any(Error), index: 2 })
  })
})

describe('useStepLoading', () => {
  it('应该管理步骤式加载', async () => {
    const steps = ['步骤1', '步骤2', '步骤3']
    const { 
      currentStep, 
      totalSteps, 
      progress, 
      currentMessage, 
      isComplete,
      nextStep,
      resetSteps, 
    } = useStepLoading(steps)

    expect(currentStep.value).toBe(0)
    expect(totalSteps.value).toBe(3)
    expect(progress.value).toBe(0)
    expect(currentMessage.value).toBe('步骤1')
    expect(isComplete.value).toBe(false)

    nextStep()
    expect(currentStep.value).toBe(1)
    expect(progress.value).toBe(33)
    expect(currentMessage.value).toBe('步骤2')

    nextStep()
    expect(currentStep.value).toBe(2)
    expect(progress.value).toBe(67)

    nextStep()
    expect(currentStep.value).toBe(3)
    expect(progress.value).toBe(100)
    expect(isComplete.value).toBe(true)

    resetSteps(['新步骤1', '新步骤2'])
    expect(currentStep.value).toBe(0)
    expect(totalSteps.value).toBe(2)
    expect(progress.value).toBe(0)
  })

  it('应该执行步骤式异步操作', async () => {
    const { executeSteps, currentStep, isComplete } = useStepLoading()

    const stepFunctions = [
      vi.fn().mockResolvedValue('步骤1结果'),
      vi.fn().mockResolvedValue('步骤2结果'),
      vi.fn().mockResolvedValue('步骤3结果'),
    ]

    expect(currentStep.value).toBe(0)
    expect(isComplete.value).toBe(false)

    const results = await executeSteps(stepFunctions)

    expect(results).toHaveLength(3)
    expect(results[0]).toEqual({ success: true, result: '步骤1结果', step: 0 })
    expect(results[1]).toEqual({ success: true, result: '步骤2结果', step: 1 })
    expect(results[2]).toEqual({ success: true, result: '步骤3结果', step: 2 })
    expect(isComplete.value).toBe(true)
  })

  it('应该在步骤失败时停止执行', async () => {
    const { executeSteps, currentStep } = useStepLoading()

    const stepFunctions = [
      vi.fn().mockResolvedValue('步骤1结果'),
      vi.fn().mockRejectedValue(new Error('步骤2失败')),
      vi.fn().mockResolvedValue('步骤3结果'), // 不应该被执行
    ]

    try {
      await executeSteps(stepFunctions)
    } catch (error) {
      expect(error.message).toBe('步骤2失败')
    }

    expect(currentStep.value).toBe(1) // 停在失败的步骤
    expect(stepFunctions[0]).toHaveBeenCalled()
    expect(stepFunctions[1]).toHaveBeenCalled()
    expect(stepFunctions[2]).not.toHaveBeenCalled() // 第三个步骤不应该执行
  })
})
