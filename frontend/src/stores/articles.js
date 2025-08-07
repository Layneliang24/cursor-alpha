import { defineStore } from 'pinia'
import { articlesAPI } from '@/api/articles'
import { ElMessage } from 'element-plus'

export const useArticlesStore = defineStore('articles', {
  state: () => ({
    articles: [],
    currentArticle: null,
    loading: false,
    pagination: {
      current: 1,
      pageSize: 20,
      total: 0
    }
  }),

  getters: {
    getArticleById: (state) => (id) => {
      return state.articles.find(article => article.id === id)
    }
  },

  actions: {
    // 获取文章列表
    async fetchArticles(params = {}) {
      this.loading = true
      try {
        const response = await articlesAPI.getArticles({
          page: this.pagination.current,
          page_size: this.pagination.pageSize,
          ...params
        })
        
        this.articles = response.results
        this.pagination.total = response.count
        
        return response
      } catch (error) {
        console.error('获取文章列表失败:', error)
        ElMessage.error('获取文章列表失败')
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取文章详情
    async fetchArticle(id) {
      this.loading = true
      try {
        const article = await articlesAPI.getArticle(id)
        this.currentArticle = article
        return article
      } catch (error) {
        console.error('获取文章详情失败:', error)
        ElMessage.error('获取文章详情失败')
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建文章
    async createArticle(articleData) {
      try {
        const article = await articlesAPI.createArticle(articleData)
        this.articles.unshift(article)
        ElMessage.success('文章发布成功！')
        return article
      } catch (error) {
        console.error('创建文章失败:', error)
        ElMessage.error('发布文章失败')
        throw error
      }
    },

    // 更新文章
    async updateArticle(id, articleData) {
      try {
        const article = await articlesAPI.updateArticle(id, articleData)
        const index = this.articles.findIndex(a => a.id === id)
        if (index !== -1) {
          this.articles[index] = article
        }
        if (this.currentArticle && this.currentArticle.id === id) {
          this.currentArticle = article
        }
        ElMessage.success('文章更新成功！')
        return article
      } catch (error) {
        console.error('更新文章失败:', error)
        ElMessage.error('更新文章失败')
        throw error
      }
    },

    // 删除文章
    async deleteArticle(id) {
      try {
        await articlesAPI.deleteArticle(id)
        this.articles = this.articles.filter(a => a.id !== id)
        if (this.currentArticle && this.currentArticle.id === id) {
          this.currentArticle = null
        }
        ElMessage.success('文章删除成功！')
      } catch (error) {
        console.error('删除文章失败:', error)
        ElMessage.error('删除文章失败')
        throw error
      }
    },

    // 点赞文章
    async likeArticle(id) {
      try {
        const response = await articlesAPI.likeArticle(id)
        ElMessage.success(response.message)
        // 重新获取文章详情以更新点赞数
        if (this.currentArticle && this.currentArticle.id === id) {
          await this.fetchArticle(id)
        }
      } catch (error) {
        console.error('点赞失败:', error)
        throw error
      }
    },

    // 收藏文章
    async bookmarkArticle(id) {
      try {
        const response = await articlesAPI.bookmarkArticle(id)
        ElMessage.success(response.message)
      } catch (error) {
        console.error('收藏失败:', error)
        throw error
      }
    }
  }
})