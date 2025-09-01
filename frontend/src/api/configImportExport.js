import request from '@/api/request'

/**
 * 配置导入导出API
 */
export const configImportExportAPI = {
  /**
   * 导出配置
   * @param {string} format - 导出格式 (json/yaml)
   * @returns {Promise} 配置文件
   */
  exportConfig(format = 'json') {
    return request({
      url: `/api/v1/ai/config/export/`,
      method: 'get',
      params: { format },
      responseType: 'blob'
    })
  },

  /**
   * 导入配置
   * @param {FormData} formData - 包含配置文件的FormData
   * @returns {Promise} 导入结果
   */
  importConfig(formData) {
    return request({
      url: `/api/v1/ai/config/import/`,
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 验证配置
   * @param {FormData} formData - 包含配置文件的FormData
   * @returns {Promise} 验证结果
   */
  validateConfig(formData) {
    return request({
      url: `/api/v1/ai/config/import/`,
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 获取配置模板列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 模板列表
   */
  getTemplates(params = {}) {
    return request({
      url: '/api/v1/ai/config/templates/',
      method: 'get',
      params
    })
  },

  /**
   * 创建配置模板
   * @param {Object} data - 模板数据
   * @returns {Promise} 创建的模板
   */
  createTemplate(data) {
    return request({
      url: '/api/v1/ai/config/templates/',
      method: 'post',
      data
    })
  },

  /**
   * 更新配置模板
   * @param {number} id - 模板ID
   * @param {Object} data - 模板数据
   * @returns {Promise} 更新的模板
   */
  updateTemplate(id, data) {
    return request({
      url: `/api/v1/ai/config/templates/${id}/`,
      method: 'put',
      data
    })
  },

  /**
   * 删除配置模板
   * @param {number} id - 模板ID
   * @returns {Promise} 删除结果
   */
  deleteTemplate(id) {
    return request({
      url: `/api/v1/ai/config/templates/${id}/`,
      method: 'delete'
    })
  },

  /**
   * 应用配置模板
   * @param {number} id - 模板ID
   * @returns {Promise} 应用结果
   */
  applyTemplate(id) {
    return request({
      url: `/api/v1/ai/config/templates/${id}/apply/`,
      method: 'post'
    })
  },

  /**
   * 获取配置版本列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 版本列表
   */
  getVersions(params = {}) {
    return request({
      url: '/api/v1/ai/config/versions/',
      method: 'get',
      params
    })
  },

  /**
   * 获取配置版本详情
   * @param {number} id - 版本ID
   * @returns {Promise} 版本详情
   */
  getVersion(id) {
    return request({
      url: `/api/v1/ai/config/versions/${id}/`,
      method: 'get'
    })
  },

  /**
   * 回滚到指定版本
   * @param {number} id - 版本ID
   * @returns {Promise} 回滚结果
   */
  rollbackVersion(id) {
    return request({
      url: `/api/v1/ai/config/versions/${id}/rollback/`,
      method: 'post'
    })
  }
}

export default configImportExportAPI
