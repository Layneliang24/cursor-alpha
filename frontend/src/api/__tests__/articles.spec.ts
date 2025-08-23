import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { articlesAPI } from '../articles'
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

describe('articles.js API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('articlesAPI', () => {
    describe('getArticles', () => {
      it('成功获取文章列表（无参数）', async () => {
        const mockArticles = {
          results: [
            { id: 1, title: '文章1', content: '内容1' },
            { id: 2, title: '文章2', content: '内容2' }
          ],
          count: 2,
          next: null,
          previous: null
        }
        
        vi.mocked(request.get).mockResolvedValue(mockArticles)
        
        const result = await articlesAPI.getArticles()
        
        expect(request.get).toHaveBeenCalledWith('/articles/', { params: {} })
        expect(result).toEqual(mockArticles)
      })

      it('成功获取文章列表（带参数）', async () => {
        const params = {
          page: 1,
          page_size: 10,
          category: '技术',
          search: 'Vue'
        }
        
        const mockArticles = {
          results: [{ id: 1, title: 'Vue.js教程', category: '技术' }],
          count: 1
        }
        
        vi.mocked(request.get).mockResolvedValue(mockArticles)
        
        const result = await articlesAPI.getArticles(params)
        
        expect(request.get).toHaveBeenCalledWith('/articles/', { params })
        expect(result).toEqual(mockArticles)
      })

      it('API调用失败时抛出错误', async () => {
        const mockError = new Error('Network error')
        vi.mocked(request.get).mockRejectedValue(mockError)
        
        await expect(articlesAPI.getArticles()).rejects.toThrow('Network error')
        expect(request.get).toHaveBeenCalledWith('/articles/', { params: {} })
      })

      it('处理空参数对象', async () => {
        const mockArticles = { results: [], count: 0 }
        vi.mocked(request.get).mockResolvedValue(mockArticles)
        
        const result = await articlesAPI.getArticles({})
        
        expect(request.get).toHaveBeenCalledWith('/articles/', { params: {} })
        expect(result).toEqual(mockArticles)
      })
    })

    describe('getArticle', () => {
      it('成功获取文章详情', async () => {
        const articleId = 1
        const mockArticle = {
          id: 1,
          title: '测试文章',
          content: '这是测试文章的内容',
          author: { username: 'testuser' },
          created_at: '2024-01-15T10:00:00Z'
        }
        
        vi.mocked(request.get).mockResolvedValue(mockArticle)
        
        const result = await articlesAPI.getArticle(articleId)
        
        expect(request.get).toHaveBeenCalledWith('/articles/1/')
        expect(result).toEqual(mockArticle)
      })

      it('文章ID为0时正确处理', async () => {
        const mockArticle = { id: 0, title: '特殊文章' }
        vi.mocked(request.get).mockResolvedValue(mockArticle)
        
        const result = await articlesAPI.getArticle(0)
        
        expect(request.get).toHaveBeenCalledWith('/articles/0/')
        expect(result).toEqual(mockArticle)
      })

      it('文章ID为负数时正确处理', async () => {
        const mockArticle = { id: -1, title: '负ID文章' }
        vi.mocked(request.get).mockResolvedValue(mockArticle)
        
        const result = await articlesAPI.getArticle(-1)
        
        expect(request.get).toHaveBeenCalledWith('/articles/-1/')
        expect(result).toEqual(mockArticle)
      })

      it('API调用失败时抛出错误', async () => {
        const articleId = 999
        const mockError = new Error('Article not found')
        vi.mocked(request.get).mockRejectedValue(mockError)
        
        await expect(articlesAPI.getArticle(articleId)).rejects.toThrow('Article not found')
        expect(request.get).toHaveBeenCalledWith('/articles/999/')
      })
    })

    describe('createArticle', () => {
      it('成功创建文章', async () => {
        const articleData = {
          title: '新文章',
          content: '新文章内容',
          summary: '新文章摘要',
          category: 1
        }
        
        const mockResponse = {
          id: 3,
          ...articleData,
          created_at: '2024-01-15T12:00:00Z',
          author: { username: 'currentuser' }
        }
        
        vi.mocked(request.post).mockResolvedValue(mockResponse)
        
        const result = await articlesAPI.createArticle(articleData)
        
        expect(request.post).toHaveBeenCalledWith('/articles/', articleData)
        expect(result).toEqual(mockResponse)
      })

      it('创建文章时包含可选字段', async () => {
        const articleData = {
          title: '完整文章',
          content: '完整内容',
          summary: '完整摘要',
          category: 1,
          tags: ['Vue', 'JavaScript'],
          cover_image: 'https://example.com/cover.jpg',
          featured: true
        }
        
        const mockResponse = { id: 4, ...articleData }
        vi.mocked(request.post).mockResolvedValue(mockResponse)
        
        const result = await articlesAPI.createArticle(articleData)
        
        expect(request.post).toHaveBeenCalledWith('/articles/', articleData)
        expect(result).toEqual(mockResponse)
      })

      it('创建文章失败时抛出错误', async () => {
        const articleData = { title: '', content: '' }
        const mockError = new Error('Validation failed')
        vi.mocked(request.post).mockRejectedValue(mockError)
        
        await expect(articlesAPI.createArticle(articleData)).rejects.toThrow('Validation failed')
        expect(request.post).toHaveBeenCalledWith('/articles/', articleData)
      })

      it('处理空数据对象', async () => {
        const mockResponse = { id: 5, title: '', content: '' }
        vi.mocked(request.post).mockResolvedValue(mockResponse)
        
        const result = await articlesAPI.createArticle({})
        
        expect(request.post).toHaveBeenCalledWith('/articles/', {})
        expect(result).toEqual(mockResponse)
      })
    })

    describe('updateArticle', () => {
      it('成功更新文章', async () => {
        const articleId = 1
        const updateData = {
          title: '更新后的标题',
          content: '更新后的内容'
        }
        
        const mockResponse = {
          id: articleId,
          ...updateData,
          updated_at: '2024-01-15T13:00:00Z'
        }
        
        vi.mocked(request.put).mockResolvedValue(mockResponse)
        
        const result = await articlesAPI.updateArticle(articleId, updateData)
        
        expect(request.put).toHaveBeenCalledWith(`/articles/${articleId}/`, updateData)
        expect(result).toEqual(mockResponse)
      })

      it('部分更新文章字段', async () => {
        const articleId = 2
        const updateData = { title: '只更新标题' }
        
        const mockResponse = {
          id: articleId,
          title: '只更新标题',
          content: '原有内容保持不变',
          summary: '原有摘要保持不变'
        }
        
        vi.mocked(request.put).mockResolvedValue(mockResponse)
        
        const result = await articlesAPI.updateArticle(articleId, updateData)
        
        expect(request.put).toHaveBeenCalledWith(`/articles/${articleId}/`, updateData)
        expect(result).toEqual(mockResponse)
      })

      it('更新文章失败时抛出错误', async () => {
        const articleId = 999
        const updateData = { title: '无效标题' }
        const mockError = new Error('Article not found')
        
        vi.mocked(request.put).mockRejectedValue(mockError)
        
        await expect(articlesAPI.updateArticle(articleId, updateData)).rejects.toThrow('Article not found')
        expect(request.put).toHaveBeenCalledWith(`/articles/${articleId}/`, updateData)
      })

      it('处理空更新数据', async () => {
        const articleId = 3
        const mockResponse = { id: articleId, title: '原标题', content: '原内容' }
        vi.mocked(request.put).mockResolvedValue(mockResponse)
        
        const result = await articlesAPI.updateArticle(articleId, {})
        
        expect(request.put).toHaveBeenCalledWith(`/articles/${articleId}/`, {})
        expect(result).toEqual(mockResponse)
      })
    })

    describe('deleteArticle', () => {
      it('成功删除文章', async () => {
        const articleId = 1
        
        vi.mocked(request.delete).mockResolvedValue({})
        
        const result = await articlesAPI.deleteArticle(articleId)
        
        expect(request.delete).toHaveBeenCalledWith(`/articles/${articleId}/`)
        expect(result).toEqual({})
      })

      it('删除不存在的文章时抛出错误', async () => {
        const articleId = 999
        const mockError = new Error('Article not found')
        
        vi.mocked(request.delete).mockRejectedValue(mockError)
        
        await expect(articlesAPI.deleteArticle(articleId)).rejects.toThrow('Article not found')
        expect(request.delete).toHaveBeenCalledWith(`/articles/${articleId}/`)
      })

      it('删除文章返回成功消息', async () => {
        const articleId = 2
        const mockResponse = { message: 'Article deleted successfully' }
        
        vi.mocked(request.delete).mockResolvedValue(mockResponse)
        
        const result = await articlesAPI.deleteArticle(articleId)
        
        expect(request.delete).toHaveBeenCalledWith(`/articles/${articleId}/`)
        expect(result).toEqual(mockResponse)
      })
    })

    describe('likeArticle', () => {
      it('成功点赞文章', async () => {
        const articleId = 1
        const mockResponse = {
          message: 'Article liked successfully',
          likes_count: 26
        }
        
        vi.mocked(request.post).mockResolvedValue(mockResponse)
        
        const result = await articlesAPI.likeArticle(articleId)
        
        expect(request.post).toHaveBeenCalledWith(`/articles/${articleId}/like/`)
        expect(result).toEqual(mockResponse)
      })

      it('重复点赞文章时正确处理', async () => {
        const articleId = 2
        const mockResponse = {
          message: 'Article already liked',
          likes_count: 15
        }
        
        vi.mocked(request.post).mockResolvedValue(mockResponse)
        
        const result = await articlesAPI.likeArticle(articleId)
        
        expect(request.post).toHaveBeenCalledWith(`/articles/${articleId}/like/`)
        expect(result).toEqual(mockResponse)
      })

      it('点赞失败时抛出错误', async () => {
        const articleId = 999
        const mockError = new Error('Article not found')
        
        vi.mocked(request.post).mockRejectedValue(mockError)
        
        await expect(articlesAPI.likeArticle(articleId)).rejects.toThrow('Article not found')
        expect(request.post).toHaveBeenCalledWith(`/articles/${articleId}/like/`)
      })
    })

    describe('bookmarkArticle', () => {
      it('成功收藏文章', async () => {
        const articleId = 1
        const mockResponse = {
          message: 'Article bookmarked successfully',
          bookmarked: true
        }
        
        vi.mocked(request.post).mockResolvedValue(mockResponse)
        
        const result = await articlesAPI.bookmarkArticle(articleId)
        
        expect(request.post).toHaveBeenCalledWith(`/articles/${articleId}/bookmark/`)
        expect(result).toEqual(mockResponse)
      })

      it('取消收藏文章时正确处理', async () => {
        const articleId = 2
        const mockResponse = {
          message: 'Article unbookmarked successfully',
          bookmarked: false
        }
        
        vi.mocked(request.post).mockResolvedValue(mockResponse)
        
        const result = await articlesAPI.bookmarkArticle(articleId)
        
        expect(request.post).toHaveBeenCalledWith(`/articles/${articleId}/bookmark/`)
        expect(result).toEqual(mockResponse)
      })

      it('收藏失败时抛出错误', async () => {
        const articleId = 999
        const mockError = new Error('Article not found')
        
        vi.mocked(request.post).mockRejectedValue(mockError)
        
        await expect(articlesAPI.bookmarkArticle(articleId)).rejects.toThrow('Article not found')
        expect(request.post).toHaveBeenCalledWith(`/articles/${articleId}/bookmark/`)
      })
    })

    describe('getComments', () => {
      it('成功获取文章评论', async () => {
        const articleId = 1
        const mockComments = [
          {
            id: 1,
            content: '很好的文章！',
            author: { username: 'user1' },
            created_at: '2024-01-15T10:00:00Z'
          },
          {
            id: 2,
            content: '学习了，谢谢分享',
            author: { username: 'user2' },
            created_at: '2024-01-15T11:00:00Z'
          }
        ]
        
        vi.mocked(request.get).mockResolvedValue(mockComments)
        
        const result = await articlesAPI.getComments(articleId)
        
        expect(request.get).toHaveBeenCalledWith(`/articles/${articleId}/comments/`)
        expect(result).toEqual(mockComments)
      })

      it('获取无评论文章时返回空数组', async () => {
        const articleId = 2
        const mockComments = []
        
        vi.mocked(request.get).mockResolvedValue(mockComments)
        
        const result = await articlesAPI.getComments(articleId)
        
        expect(request.get).toHaveBeenCalledWith(`/articles/${articleId}/comments/`)
        expect(result).toEqual([])
      })

      it('获取评论失败时抛出错误', async () => {
        const articleId = 999
        const mockError = new Error('Article not found')
        
        vi.mocked(request.get).mockRejectedValue(mockError)
        
        await expect(articlesAPI.getComments(articleId)).rejects.toThrow('Article not found')
        expect(request.get).toHaveBeenCalledWith(`/articles/${articleId}/comments/`)
      })
    })

    describe('createComment', () => {
      it('成功发表评论', async () => {
        const commentData = {
          article: 1,
          content: '这是一条新评论',
          parent: null
        }
        
        const mockResponse = {
          id: 3,
          ...commentData,
          author: { username: 'currentuser' },
          created_at: '2024-01-15T14:00:00Z'
        }
        
        vi.mocked(request.post).mockResolvedValue(mockResponse)
        
        const result = await articlesAPI.createComment(commentData)
        
        expect(request.post).toHaveBeenCalledWith('/comments/', commentData)
        expect(result).toEqual(mockResponse)
      })

      it('发表回复评论', async () => {
        const commentData = {
          article: 1,
          content: '这是回复评论',
          parent: 1
        }
        
        const mockResponse = {
          id: 4,
          ...commentData,
          author: { username: 'currentuser' },
          created_at: '2024-01-15T15:00:00Z'
        }
        
        vi.mocked(request.post).mockResolvedValue(mockResponse)
        
        const result = await articlesAPI.createComment(commentData)
        
        expect(request.post).toHaveBeenCalledWith('/comments/', commentData)
        expect(result).toEqual(mockResponse)
      })

      it('发表评论失败时抛出错误', async () => {
        const commentData = { article: 1, content: '' }
        const mockError = new Error('Comment content cannot be empty')
        
        vi.mocked(request.post).mockRejectedValue(mockError)
        
        await expect(articlesAPI.createComment(commentData)).rejects.toThrow('Comment content cannot be empty')
        expect(request.post).toHaveBeenCalledWith('/comments/', commentData)
      })

      it('处理空评论内容', async () => {
        const commentData = { article: 1, content: '' }
        const mockResponse = { id: 5, ...commentData }
        vi.mocked(request.post).mockResolvedValue(mockResponse)
        
        const result = await articlesAPI.createComment(commentData)
        
        expect(request.post).toHaveBeenCalledWith('/comments/', commentData)
        expect(result).toEqual(mockResponse)
      })
    })
  })

  describe('错误处理边界情况', () => {
    it('处理网络超时错误', async () => {
      const timeoutError = new Error('Request timeout')
      timeoutError.name = 'TimeoutError'
      
      vi.mocked(request.get).mockRejectedValue(timeoutError)
      
      await expect(articlesAPI.getArticles()).rejects.toThrow('Request timeout')
    })

    it('处理HTTP状态码错误', async () => {
      const httpError = new Error('HTTP 500 Internal Server Error')
      httpError.response = { status: 500, data: 'Internal Server Error' }
      
      vi.mocked(request.get).mockRejectedValue(httpError)
      
      await expect(articlesAPI.getArticles()).rejects.toThrow('HTTP 500 Internal Server Error')
    })

    it('处理JSON解析错误', async () => {
      const jsonError = new Error('Unexpected token < in JSON at position 0')
      jsonError.name = 'SyntaxError'
      
      vi.mocked(request.get).mockRejectedValue(jsonError)
      
      await expect(articlesAPI.getArticles()).rejects.toThrow('Unexpected token < in JSON at position 0')
    })

    it('处理权限错误', async () => {
      const authError = new Error('HTTP 403 Forbidden')
      authError.response = { status: 403, data: 'Permission denied' }
      
      vi.mocked(request.post).mockRejectedValue(authError)
      
      await expect(articlesAPI.createArticle({ title: 'test', content: 'test' })).rejects.toThrow('HTTP 403 Forbidden')
    })
  })

  describe('API参数验证', () => {
    it('getArticles支持所有查询参数', async () => {
      const params = {
        page: 1,
        page_size: 20,
        category: '技术',
        search: 'Vue.js',
        ordering: '-created_at',
        author: 'testuser',
        featured: true,
        tags: 'javascript,vue'
      }
      
      const mockResponse = { results: [], count: 0 }
      vi.mocked(request.get).mockResolvedValue(mockResponse)
      
      await articlesAPI.getArticles(params)
      
      expect(request.get).toHaveBeenCalledWith('/articles/', { params })
    })

    it('createArticle支持所有文章字段', async () => {
      const articleData = {
        title: '完整文章',
        content: '完整内容',
        summary: '完整摘要',
        category: 1,
        tags: ['Vue', 'JavaScript'],
        cover_image: 'https://example.com/cover.jpg',
        featured: true,
        allow_comments: true,
        status: 'published'
      }
      
      const mockResponse = { id: 6, ...articleData }
      vi.mocked(request.post).mockResolvedValue(mockResponse)
      
      const result = await articlesAPI.createArticle(articleData)
      
             expect(request.post).toHaveBeenCalledWith('/articles/', articleData)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('API调用频率和性能', () => {
    it('连续调用相同API时正确处理', async () => {
      const mockResponse = { results: [], count: 0 }
      vi.mocked(request.get).mockResolvedValue(mockResponse)
      
      // 连续调用3次
      await articlesAPI.getArticles()
      await articlesAPI.getArticles()
      await articlesAPI.getArticles()
      
      expect(request.get).toHaveBeenCalledTimes(3)
      expect(request.get).toHaveBeenCalledWith('/articles/', { params: {} })
    })

    it('并发调用不同API时正确处理', async () => {
      const mockArticle = { id: 1, title: 'Test' }
      const mockComments = []
      
      vi.mocked(request.get)
        .mockResolvedValueOnce(mockArticle)
        .mockResolvedValueOnce(mockComments)
      
      // 并发调用
      const [article, comments] = await Promise.all([
        articlesAPI.getArticle(1),
        articlesAPI.getComments(1)
      ])
      
      expect(article).toEqual(mockArticle)
      expect(comments).toEqual(mockComments)
      expect(request.get).toHaveBeenCalledTimes(2)
    })
  })
}) 