import { describe, it, expect, vi, beforeEach } from 'vitest'
import { categoriesAPI } from '../categories'

// Mock request module
vi.mock('../request', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

describe('categoriesAPI', () => {
  let mockRequest: any

  beforeEach(async () => {
    const requestModule = await import('../request')
    mockRequest = requestModule.default
    mockRequest.get.mockClear()
    mockRequest.post.mockClear()
    mockRequest.put.mockClear()
    mockRequest.delete.mockClear()
  })

  describe('getCategories', () => {
    it('应该获取分类列表', async () => {
      const mockResponse = [
        { id: 1, name: '技术', slug: 'tech' },
        { id: 2, name: '生活', slug: 'life' }
      ]
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await categoriesAPI.getCategories()

      expect(mockRequest.get).toHaveBeenCalledWith('/categories/')
      expect(result).toEqual(mockResponse)
    })

    it('应该处理获取分类列表失败', async () => {
      const error = new Error('网络错误')
      mockRequest.get.mockRejectedValue(error)

      await expect(categoriesAPI.getCategories()).rejects.toThrow('网络错误')
    })
  })

  describe('getCategory', () => {
    it('应该获取单个分类详情', async () => {
      const mockResponse = {
        data: { id: 1, name: '技术', slug: 'tech', description: '技术相关文章' }
      }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await categoriesAPI.getCategory(1)

      expect(mockRequest.get).toHaveBeenCalledWith('/categories/1/')
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('getCategoryArticles', () => {
    it('应该获取分类下的文章列表', async () => {
      const mockResponse = {
        data: {
          category: { id: 1, name: '技术' },
          articles: [
            { id: 1, title: 'Vue.js 教程', content: '...' },
            { id: 2, title: 'React 入门', content: '...' }
          ]
        }
      }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await categoriesAPI.getCategoryArticles(1)

      expect(mockRequest.get).toHaveBeenCalledWith('/categories/1/articles/', { params: {} })
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('createCategory', () => {
    it('应该创建新分类', async () => {
      const categoryData = { name: '新分类', slug: 'new-category' }
      const mockResponse = {
        data: { id: 3, ...categoryData }
      }
      mockRequest.post.mockResolvedValue(mockResponse)

      const result = await categoriesAPI.createCategory(categoryData)

      expect(mockRequest.post).toHaveBeenCalledWith('/categories/', categoryData)
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('updateCategory', () => {
    it('应该更新分类信息', async () => {
      const updateData = { name: '更新后的分类' }
      const mockResponse = {
        data: { id: 1, ...updateData, slug: 'tech' }
      }
      mockRequest.put.mockResolvedValue(mockResponse)

      const result = await categoriesAPI.updateCategory(1, updateData)

      expect(mockRequest.put).toHaveBeenCalledWith('/categories/1/', updateData)
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('deleteCategory', () => {
    it('应该删除分类', async () => {
      mockRequest.delete.mockResolvedValue({ data: { message: '删除成功' } })

      const result = await categoriesAPI.deleteCategory(1)

      expect(mockRequest.delete).toHaveBeenCalledWith('/categories/1/')
      expect(result).toEqual({ message: '删除成功' })
    })
  })

  describe('getTags', () => {
    it('应该获取标签列表', async () => {
      const mockResponse = {
        data: [
          { id: 1, name: 'Vue.js' },
          { id: 2, name: 'React' },
          { id: 3, name: 'JavaScript' }
        ]
      }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await categoriesAPI.getTags()

      expect(mockRequest.get).toHaveBeenCalledWith('/tags/')
      expect(result).toEqual(mockResponse.data)
    })
  })
})
