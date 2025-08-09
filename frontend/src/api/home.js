import request from './request'
import axios from 'axios'

// 首页相关API
export const homeAPI = {
  // 获取首页统计数据
  async getStats() {
    try {
      const response = await request.get('/home/stats/')
      return response
    } catch (error) {
      console.error('Stats API error:', error)
      throw error
    }
  },

  // 获取热门文章（用于轮播）
  async getPopularArticles() {
    try {
      const response = await request.get('/home/popular-articles/')
      return response
    } catch (error) {
      console.error('Popular articles API error:', error)
      // Fallback to regular articles API
      try {
        const fallback = await request.get('/articles/', { 
          params: { page_size: 5, ordering: '-views' }
        })
        return fallback.results || []
      } catch (fallbackError) {
        console.error('Fallback API also failed:', fallbackError)
        throw error
      }
    }
  },

  // 获取最新文章
  async getRecentArticles() {
    try {
      const response = await request.get('/home/recent-articles/')
      return response
    } catch (error) {
      console.error('Recent articles API error:', error)
      // Fallback to regular articles API
      try {
        const fallback = await request.get('/articles/', { 
          params: { page_size: 6, ordering: '-created_at' }
        })
        return fallback.results || []
      } catch (fallbackError) {
        console.error('Fallback API also failed:', fallbackError)
        throw error
      }
    }
  },

  // 获取热门标签
  async getPopularTags() {
    try {
      const response = await request.get('/home/popular-tags/')
      return response
    } catch (error) {
      console.error('Popular tags API error:', error)
      return []
    }
  }
}

// 外链相关API
export const linksAPI = {
  // 获取外链列表
  getLinks() {
    return request.get('external-links/').then(res => res.results || res)
  },

  // 创建外链
  createLink(data) {
    return request.post('external-links/', data)
  },

  // 更新外链
  updateLink(id, data) {
    return request.put(`external-links/${id}/`, data)
  },

  // 删除外链
  deleteLink(id) {
    return request.delete(`external-links/${id}/`)
  }
}
