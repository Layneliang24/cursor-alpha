import request from './request'

// 文章相关API
export const articlesAPI = {
  // 获取文章列表
  getArticles(params = {}) {
    return request.get('/articles/', { params })
  },

  // 获取文章详情
  getArticle(id) {
    return request.get(`/articles/${id}/`)
  },

  // 创建文章
  createArticle(data) {
    return request.post('/articles/', data)
  },

  // 更新文章
  updateArticle(id, data) {
    return request.put(`/articles/${id}/`, data)
  },

  // 删除文章
  deleteArticle(id) {
    return request.delete(`/articles/${id}/`)
  },

  // 点赞文章
  likeArticle(id) {
    return request.post(`/articles/${id}/like/`)
  },

  // 收藏文章
  bookmarkArticle(id) {
    return request.post(`/articles/${id}/bookmark/`)
  },

  // 获取文章评论
  getComments(articleId) {
    return request.get(`/articles/${articleId}/comments/`)
  },

  // 发表评论
  createComment(data) {
    return request.post('/comments/', data)
  }
}