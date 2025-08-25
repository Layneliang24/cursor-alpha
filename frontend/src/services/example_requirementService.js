import { ref } from 'vue'
import api from '@/api'

/**
 * 需求 example_requirement 服务
 * 暂无描述
 */
export function useExampleRequirementService() {
  const loading = ref(false)
  const error = ref(null)
  
  /**
   * 获取列表
   */
  const getList = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      const response = await api.get('/example_requirement/', { params })
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 获取详情
   */
  const getDetail = async (id) => {
    try {
      loading.value = true
      error.value = null
      const response = await api.get(`/example_requirement/${id}/`)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 创建
   */
  const create = async (data) => {
    try {
      loading.value = true
      error.value = null
      const response = await api.post('/example_requirement/', data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 更新
   */
  const update = async (id, data) => {
    try {
      loading.value = true
      error.value = null
      const response = await api.put(`/example_requirement/${id}/`, data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 删除
   */
  const remove = async (id) => {
    try {
      loading.value = true
      error.value = null
      await api.delete(`/example_requirement/${id}/`)
      return true
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 切换激活状态
   */
  const toggleActive = async (id) => {
    try {
      loading.value = true
      error.value = null
      const response = await api.post(`/example_requirement/${id}/toggle_active/`)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    loading,
    error,
    getList,
    getDetail,
    create,
    update,
    remove,
    toggleActive
  }
}

export default useExampleRequirementService
