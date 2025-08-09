import request from './request'

// 分类相关API
export const categoriesAPI = {
  // 获取分类列表
  getCategories() {
    return request.get('/categories/')
  },

  // 获取分类详情
  getCategory(id) {
    return request.get(`/categories/${id}/`)
  },

  // 获取分类下的文章
  getCategoryArticles(id, params = {}) {
    return request.get(`/categories/${id}/articles/`, { params })
  },

  // 创建分类
  createCategory(data) {
    return request.post('/categories/', data)
  },

  // 更新分类
  updateCategory(id, data) {
    return request.put(`/categories/${id}/`, data)
  },

  // 删除分类
  deleteCategory(id) {
    return request.delete(`/categories/${id}/`)
  },

  // 获取标签列表
  getTags() {
    return request.get('/tags/')
  }
}