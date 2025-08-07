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

  // 获取标签列表
  getTags() {
    return request.get('/tags/')
  }
}