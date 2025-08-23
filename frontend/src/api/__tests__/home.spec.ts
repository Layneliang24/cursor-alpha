import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { homeAPI, linksAPI } from '../home'
import request from '../request'

// Mock request模块
vi.mock('../request', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

// Mock axios (用于fallback)
vi.mock('axios', () => ({
  default: {
    get: vi.fn()
  }
}))

describe('home.js API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('homeAPI', () => {
    describe('getStats', () => {
      it('成功获取统计数据', async () => {
        const mockStats = {
          total_articles: 100,
          total_users: 50,
          total_views: 1000,
          active_categories: 8
        }
        
        vi.mocked(request.get).mockResolvedValue(mockStats)
        
        const result = await homeAPI.getStats()
        
        expect(request.get).toHaveBeenCalledWith('/home/stats/')
        expect(result).toEqual(mockStats)
      })

      it('API调用失败时抛出错误', async () => {
        const mockError = new Error('Network error')
        vi.mocked(request.get).mockRejectedValue(mockError)
        
        await expect(homeAPI.getStats()).rejects.toThrow('Network error')
        expect(request.get).toHaveBeenCalledWith('/home/stats/')
      })

      it('API调用失败时记录错误日志', async () => {
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
        const mockError = new Error('API error')
        vi.mocked(request.get).mockRejectedValue(mockError)
        
        try {
          await homeAPI.getStats()
        } catch (error) {
          // 预期会抛出错误
        }
        
        expect(consoleSpy).toHaveBeenCalledWith('Stats API error:', mockError)
        consoleSpy.mockRestore()
      })
    })

    describe('getPopularArticles', () => {
      it('成功获取热门文章', async () => {
        const mockArticles = [
          { id: 1, title: '热门文章1', views: 1000 },
          { id: 2, title: '热门文章2', views: 800 }
        ]
        
        vi.mocked(request.get).mockResolvedValue(mockArticles)
        
        const result = await homeAPI.getPopularArticles()
        
        expect(request.get).toHaveBeenCalledWith('/home/popular-articles/')
        expect(result).toEqual(mockArticles)
      })

      it('主API失败时使用fallback API', async () => {
        const mockError = new Error('Primary API failed')
        const fallbackArticles = [
          { id: 3, title: 'Fallback文章1', views: 600 },
          { id: 4, title: 'Fallback文章2', views: 500 }
        ]
        
        // 主API失败
        vi.mocked(request.get)
          .mockRejectedValueOnce(mockError)
          .mockResolvedValueOnce({ results: fallbackArticles })
        
        const result = await homeAPI.getPopularArticles()
        
        expect(request.get).toHaveBeenCalledWith('/home/popular-articles/')
        expect(request.get).toHaveBeenCalledWith('/articles/', {
          params: { page_size: 5, ordering: '-views' }
        })
        expect(result).toEqual(fallbackArticles)
      })

      it('主API和fallback API都失败时抛出原始错误', async () => {
        const primaryError = new Error('Primary API failed')
        const fallbackError = new Error('Fallback API failed')
        
        vi.mocked(request.get)
          .mockRejectedValueOnce(primaryError)
          .mockRejectedValueOnce(fallbackError)
        
        await expect(homeAPI.getPopularArticles()).rejects.toThrow('Primary API failed')
        
        expect(request.get).toHaveBeenCalledWith('/home/popular-articles/')
        expect(request.get).toHaveBeenCalledWith('/articles/', {
          params: { page_size: 5, ordering: '-views' }
        })
      })

      it('fallback API返回空结果时处理正确', async () => {
        vi.mocked(request.get)
          .mockRejectedValueOnce(new Error('Primary API failed'))
          .mockResolvedValueOnce({ results: [] })
        
        const result = await homeAPI.getPopularArticles()
        
        expect(result).toEqual([])
      })

      it('fallback API返回无results字段时处理正确', async () => {
        vi.mocked(request.get)
          .mockRejectedValueOnce(new Error('Primary API failed'))
          .mockResolvedValueOnce([])
        
        const result = await homeAPI.getPopularArticles()
        
        expect(result).toEqual([])
      })

      it('API调用失败时记录错误日志', async () => {
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
        const mockError = new Error('API error')
        vi.mocked(request.get).mockRejectedValue(mockError)
        
        try {
          await homeAPI.getPopularArticles()
        } catch (error) {
          // 预期会抛出错误
        }
        
        expect(consoleSpy).toHaveBeenCalledWith('Popular articles API error:', mockError)
        consoleSpy.mockRestore()
      })
    })

    describe('getRecentArticles', () => {
      it('成功获取最新文章', async () => {
        const mockArticles = [
          { id: 1, title: '最新文章1', created_at: '2024-01-15T10:00:00Z' },
          { id: 2, title: '最新文章2', created_at: '2024-01-14T15:30:00Z' }
        ]
        
        vi.mocked(request.get).mockResolvedValue(mockArticles)
        
        const result = await homeAPI.getRecentArticles()
        
        expect(request.get).toHaveBeenCalledWith('/home/recent-articles/')
        expect(result).toEqual(mockArticles)
      })

      it('主API失败时使用fallback API', async () => {
        const mockError = new Error('Primary API failed')
        const fallbackArticles = [
          { id: 3, title: 'Fallback最新文章1', created_at: '2024-01-13T12:00:00Z' }
        ]
        
        // 主API失败
        vi.mocked(request.get)
          .mockRejectedValueOnce(mockError)
          .mockResolvedValueOnce({ results: fallbackArticles })
        
        const result = await homeAPI.getRecentArticles()
        
        expect(request.get).toHaveBeenCalledWith('/home/recent-articles/')
        expect(request.get).toHaveBeenCalledWith('/articles/', {
          params: { page_size: 6, ordering: '-created_at' }
        })
        expect(result).toEqual(fallbackArticles)
      })

      it('主API和fallback API都失败时抛出原始错误', async () => {
        const primaryError = new Error('Primary API failed')
        const fallbackError = new Error('Fallback API failed')
        
        vi.mocked(request.get)
          .mockRejectedValueOnce(primaryError)
          .mockRejectedValueOnce(fallbackError)
        
        await expect(homeAPI.getRecentArticles()).rejects.toThrow('Primary API failed')
        
        expect(request.get).toHaveBeenCalledWith('/home/recent-articles/')
        expect(request.get).toHaveBeenCalledWith('/articles/', {
          params: { page_size: 6, ordering: '-created_at' }
        })
      })

      it('fallback API返回空结果时处理正确', async () => {
        vi.mocked(request.get)
          .mockRejectedValueOnce(new Error('Primary API failed'))
          .mockResolvedValueOnce({ results: [] })
        
        const result = await homeAPI.getRecentArticles()
        
        expect(result).toEqual([])
      })

      it('fallback API返回无results字段时处理正确', async () => {
        vi.mocked(request.get)
          .mockRejectedValueOnce(new Error('Primary API failed'))
          .mockResolvedValueOnce([])
        
        const result = await homeAPI.getRecentArticles()
        
        expect(result).toEqual([])
      })

      it('API调用失败时记录错误日志', async () => {
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
        const mockError = new Error('API error')
        vi.mocked(request.get).mockRejectedValue(mockError)
        
        try {
          await homeAPI.getRecentArticles()
        } catch (error) {
          // 预期会抛出错误
        }
        
        expect(consoleSpy).toHaveBeenCalledWith('Recent articles API error:', mockError)
        consoleSpy.mockRestore()
      })
    })

    describe('getPopularTags', () => {
      it('成功获取热门标签', async () => {
        const mockTags = [
          { name: 'Vue.js', count: 25 },
          { name: 'React', count: 18 },
          { name: 'Python', count: 32 }
        ]
        
        vi.mocked(request.get).mockResolvedValue(mockTags)
        
        const result = await homeAPI.getPopularTags()
        
        expect(request.get).toHaveBeenCalledWith('/home/popular-tags/')
        expect(result).toEqual(mockTags)
      })

      it('API调用失败时返回空数组', async () => {
        const mockError = new Error('API error')
        vi.mocked(request.get).mockRejectedValue(mockError)
        
        const result = await homeAPI.getPopularTags()
        
        expect(request.get).toHaveBeenCalledWith('/home/popular-tags/')
        expect(result).toEqual([])
      })

      it('API调用失败时记录错误日志', async () => {
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
        const mockError = new Error('API error')
        vi.mocked(request.get).mockRejectedValue(mockError)
        
        await homeAPI.getPopularTags()
        
        expect(consoleSpy).toHaveBeenCalledWith('Popular tags API error:', mockError)
        consoleSpy.mockRestore()
      })
    })
  })

  describe('linksAPI', () => {
    describe('getLinks', () => {
      it('成功获取外链列表', async () => {
        const mockLinks = [
          { id: 1, name: 'GitHub', url: 'https://github.com' },
          { id: 2, name: 'Stack Overflow', url: 'https://stackoverflow.com' }
        ]
        
        vi.mocked(request.get).mockResolvedValue({ results: mockLinks })
        
        const result = await linksAPI.getLinks()
        
        expect(request.get).toHaveBeenCalledWith('external-links/')
        expect(result).toEqual(mockLinks)
      })

      it('API返回无results字段时返回原始响应', async () => {
        const mockLinks = [
          { id: 1, name: 'GitHub', url: 'https://github.com' }
        ]
        
        vi.mocked(request.get).mockResolvedValue(mockLinks)
        
        const result = await linksAPI.getLinks()
        
        expect(request.get).toHaveBeenCalledWith('external-links/')
        expect(result).toEqual(mockLinks)
      })

      it('API返回空结果时处理正确', async () => {
        vi.mocked(request.get).mockResolvedValue({ results: [] })
        
        const result = await linksAPI.getLinks()
        
        expect(result).toEqual([])
      })
    })

    describe('createLink', () => {
      it('成功创建外链', async () => {
        const linkData = {
          name: 'New Link',
          url: 'https://example.com',
          description: 'A new external link'
        }
        
        const mockResponse = { id: 3, ...linkData }
        vi.mocked(request.post).mockResolvedValue(mockResponse)
        
        const result = await linksAPI.createLink(linkData)
        
        expect(request.post).toHaveBeenCalledWith('external-links/', linkData)
        expect(result).toEqual(mockResponse)
      })
    })

    describe('updateLink', () => {
      it('成功更新外链', async () => {
        const linkId = 1
        const updateData = {
          name: 'Updated Link',
          url: 'https://updated-example.com'
        }
        
        const mockResponse = { id: linkId, ...updateData }
        vi.mocked(request.put).mockResolvedValue(mockResponse)
        
        const result = await linksAPI.updateLink(linkId, updateData)
        
        expect(request.put).toHaveBeenCalledWith(`external-links/${linkId}/`, updateData)
        expect(result).toEqual(mockResponse)
      })
    })

    describe('deleteLink', () => {
      it('成功删除外链', async () => {
        const linkId = 1
        
        vi.mocked(request.delete).mockResolvedValue({})
        
        const result = await linksAPI.deleteLink(linkId)
        
        expect(request.delete).toHaveBeenCalledWith(`external-links/${linkId}/`)
        expect(result).toEqual({})
      })
    })
  })

  describe('错误处理边界情况', () => {
    it('处理网络超时错误', async () => {
      const timeoutError = new Error('Request timeout')
      timeoutError.name = 'TimeoutError'
      
      vi.mocked(request.get).mockRejectedValue(timeoutError)
      
      await expect(homeAPI.getStats()).rejects.toThrow('Request timeout')
    })

    it('处理HTTP状态码错误', async () => {
      const httpError = new Error('HTTP 500 Internal Server Error')
      httpError.response = { status: 500, data: 'Internal Server Error' }
      
      vi.mocked(request.get).mockRejectedValue(httpError)
      
      await expect(homeAPI.getStats()).rejects.toThrow('HTTP 500 Internal Server Error')
    })

    it('处理JSON解析错误', async () => {
      const jsonError = new Error('Unexpected token < in JSON at position 0')
      jsonError.name = 'SyntaxError'
      
      vi.mocked(request.get).mockRejectedValue(jsonError)
      
      await expect(homeAPI.getStats()).rejects.toThrow('Unexpected token < in JSON at position 0')
    })
  })

  describe('API参数验证', () => {
    it('getPopularArticles使用正确的fallback参数', async () => {
      vi.mocked(request.get)
        .mockRejectedValueOnce(new Error('Primary API failed'))
        .mockResolvedValueOnce({ results: [] })
      
      await homeAPI.getPopularArticles()
      
      expect(request.get).toHaveBeenCalledWith('/articles/', {
        params: { page_size: 5, ordering: '-views' }
      })
    })

    it('getRecentArticles使用正确的fallback参数', async () => {
      vi.mocked(request.get)
        .mockRejectedValueOnce(new Error('Primary API failed'))
        .mockResolvedValueOnce({ results: [] })
      
      await homeAPI.getRecentArticles()
      
      expect(request.get).toHaveBeenCalledWith('/articles/', {
        params: { page_size: 6, ordering: '-created_at' }
      })
    })
  })
}) 