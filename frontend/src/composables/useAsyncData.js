import { ref, computed, onMounted, watch } from 'vue'
import { globalErrorHandler } from '@/utils/errorHandler'

/**
 * 异步数据加载组合式函数
 * @param {Function} asyncFunction - 异步函数
 * @param {Object} options - 配置选项
 */
export function useAsyncData (asyncFunction, options = {}) {
  const {
    immediate = true,        // 是否立即执行
    resetOnExecute = true,   // 执行时是否重置数据
    shallow = true,          // 是否使用浅层响应式
    timeout = 30000,         // 超时时间（毫秒）
    retryCount = 0,          // 自动重试次数
    retryDelay = 1000,       // 重试延迟（毫秒）
    fallbackData = null,     // 失败时的后备数据
    onError = null,          // 错误回调
    onSuccess = null,        // 成功回调
    silent = false,          // 是否静默处理错误
    operation = 'data_fetch', // 操作名称，用于错误处理
  } = options

  // 响应式状态
  const data = ref(null)
  const error = ref(null)
  const loading = ref(false)
  const retrying = ref(false)
  const currentRetryCount = ref(0)

  // 计算属性
  const isReady = computed(() => !loading.value && !error.value && data.value !== null)
  const isEmpty = computed(() => !loading.value && !error.value && !data.value)
  const hasError = computed(() => !!error.value)

  // 执行异步函数
  const execute = async (...args) => {
    if (resetOnExecute) {
      data.value = null
      error.value = null
    }

    loading.value = true
    currentRetryCount.value = 0

    try {
      const result = await executeWithTimeout(asyncFunction, args, timeout)
      
      data.value = result
      error.value = null
      
      // 成功回调
      if (onSuccess) {
        onSuccess(result)
      }

      return result
    } catch (err) {
      await handleError(err, args)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 重试执行
  const retry = async (...args) => {
    if (currentRetryCount.value >= retryCount) {
      throw new Error('重试次数已达上限')
    }

    retrying.value = true
    currentRetryCount.value++

    try {
      // 延迟重试
      if (retryDelay > 0) {
        await sleep(retryDelay * currentRetryCount.value)
      }

      const result = await execute(...args)
      retrying.value = false
      return result
    } catch (err) {
      retrying.value = false
      
      // 如果还有重试次数，继续重试
      if (currentRetryCount.value < retryCount) {
        return retry(...args)
      }
      
      throw err
    }
  }

  // 刷新数据
  const refresh = async (...args) => {
    return execute(...args)
  }

  // 重置状态
  const reset = () => {
    data.value = null
    error.value = null
    loading.value = false
    retrying.value = false
    currentRetryCount.value = 0
  }

  // 处理错误
  const handleError = async (err, args) => {
    error.value = err

    // 使用后备数据
    if (fallbackData !== null) {
      data.value = fallbackData
    }

    // 自动重试
    if (retryCount > 0 && currentRetryCount.value < retryCount) {
      try {
        await retry(...args)
        return
      } catch (retryErr) {
        // 重试失败，继续处理原始错误
      }
    }

    // 错误处理
    if (!silent) {
      globalErrorHandler.handleApiError(err, {
        operation,
        silent: false,
      })
    }

    // 错误回调
    if (onError) {
      onError(err)
    }
  }

  // 立即执行
  if (immediate) {
    onMounted(() => {
      execute()
    })
  }

  return {
    // 状态
    data,
    error,
    loading,
    retrying,
    
    // 计算属性
    isReady,
    isEmpty,
    hasError,
    
    // 方法
    execute,
    retry,
    refresh,
    reset,
    
    // 元数据
    currentRetryCount,
  }
}

/**
 * 分页数据加载组合式函数
 */
export function usePaginatedData (asyncFunction, options = {}) {
  const {
    pageSize = 20,
    immediate = true,
    ...restOptions
  } = options

  const currentPage = ref(1)
  const totalItems = ref(0)
  const totalPages = ref(0)
  const items = ref([])

  // 包装异步函数以支持分页
  const paginatedFunction = async (...args) => {
    const result = await asyncFunction({
      page: currentPage.value,
      pageSize,
      ...args[0],
    })

    // 更新分页信息
    if (result.total !== undefined) {
      totalItems.value = result.total
      totalPages.value = Math.ceil(result.total / pageSize)
    }

    // 更新数据
    if (currentPage.value === 1) {
      items.value = result.data || result.items || result
    } else {
      // 追加数据（无限滚动）
      items.value.push(...(result.data || result.items || result))
    }

    return result
  }

  const asyncData = useAsyncData(paginatedFunction, {
    immediate,
    operation: 'paginated_fetch',
    ...restOptions,
  })

  // 加载下一页
  const loadMore = async () => {
    if (currentPage.value >= totalPages.value) {
      return
    }

    currentPage.value++
    await asyncData.execute()
  }

  // 重置到第一页
  const resetPagination = () => {
    currentPage.value = 1
    items.value = []
    totalItems.value = 0
    totalPages.value = 0
    asyncData.reset()
  }

  // 跳转到指定页
  const goToPage = async (page) => {
    if (page < 1 || page > totalPages.value) {
      return
    }

    currentPage.value = page
    items.value = [] // 清空当前数据
    await asyncData.execute()
  }

  return {
    // 继承基础功能
    ...asyncData,
    
    // 分页特定状态
    currentPage,
    totalItems,
    totalPages,
    items,
    
    // 分页特定方法
    loadMore,
    resetPagination,
    goToPage,
    
    // 计算属性
    hasMore: computed(() => currentPage.value < totalPages.value),
    isFirstPage: computed(() => currentPage.value === 1),
    isLastPage: computed(() => currentPage.value >= totalPages.value),
  }
}

/**
 * 无限滚动数据加载
 */
export function useInfiniteScroll (asyncFunction, options = {}) {
  const paginatedData = usePaginatedData(asyncFunction, {
    immediate: false,
    ...options,
  })

  // 滚动监听
  const setupScrollListener = (element = window) => {
    const handleScroll = () => {
      if (paginatedData.loading.value || !paginatedData.hasMore.value) {
        return
      }

      const scrollElement = element === window ? document.documentElement : element
      const scrollTop = element === window ? scrollElement.scrollTop : element.scrollTop
      const { scrollHeight } = scrollElement
      const clientHeight = element === window ? window.innerHeight : element.clientHeight

      // 距离底部100px时触发加载
      if (scrollTop + clientHeight >= scrollHeight - 100) {
        paginatedData.loadMore()
      }
    }

    element.addEventListener('scroll', handleScroll, { passive: true })

    return () => {
      element.removeEventListener('scroll', handleScroll)
    }
  }

  return {
    ...paginatedData,
    setupScrollListener,
  }
}

/**
 * 搜索数据组合式函数
 */
export function useSearchData (asyncFunction, options = {}) {
  const {
    debounceDelay = 300,
    minLength = 1,
    ...restOptions
  } = options

  const query = ref('')
  const debouncedQuery = ref('')
  let debounceTimer = null

  // 防抖处理
  watch(query, (newQuery) => {
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }

    debounceTimer = setTimeout(() => {
      debouncedQuery.value = newQuery
    }, debounceDelay)
  })

  // 包装搜索函数
  const searchFunction = async (...args) => {
    if (debouncedQuery.value.length < minLength) {
      return []
    }

    return asyncFunction({
      query: debouncedQuery.value,
      ...args[0],
    })
  }

  const asyncData = useAsyncData(searchFunction, {
    immediate: false,
    operation: 'search',
    ...restOptions,
  })

  // 监听搜索查询变化
  watch(debouncedQuery, () => {
    if (debouncedQuery.value.length >= minLength) {
      asyncData.execute()
    } else {
      asyncData.reset()
    }
  })

  // 清空搜索
  const clearSearch = () => {
    query.value = ''
    debouncedQuery.value = ''
    asyncData.reset()
  }

  return {
    ...asyncData,
    query,
    debouncedQuery,
    clearSearch,
    isSearching: computed(() => debouncedQuery.value.length >= minLength),
  }
}

// 工具函数
function executeWithTimeout (fn, args, timeout) {
  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(() => {
      reject(new Error(`操作超时 (${timeout}ms)`))
    }, timeout)

    Promise.resolve(fn(...args))
      .then(resolve)
      .catch(reject)
      .finally(() => {
        clearTimeout(timeoutId)
      })
  })
}

function sleep (ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}
