import { describe, it, expect, vi, beforeEach } from 'vitest'
import { authAPI } from '../auth'

// Mock request and axios
vi.mock('../request', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn()
  }
}))

vi.mock('axios', () => ({
  default: {
    post: vi.fn()
  }
}))

describe('authAPI', () => {
  let mockRequest: any
  let mockAxios: any

  beforeEach(async () => {
    vi.clearAllMocks()
    mockRequest = (await import('../request')).default
    mockAxios = (await import('axios')).default
  })

  describe('login', () => {
    it('应该成功调用登录API', async () => {
      const loginData = { username: 'testuser', password: 'testpass' }
      const mockResponse = { data: { token: 'test-token' } }
      mockRequest.post.mockResolvedValue(mockResponse)

      const result = await authAPI.login(loginData)

      expect(mockRequest.post).toHaveBeenCalledWith('/auth/login/', loginData)
      expect(result).toEqual(mockResponse)
    })

    it('应该处理登录失败', async () => {
      const loginData = { username: 'testuser', password: 'wrongpass' }
      const mockError = new Error('登录失败')
      mockRequest.post.mockRejectedValue(mockError)

      await expect(authAPI.login(loginData)).rejects.toThrow('登录失败')
      expect(mockRequest.post).toHaveBeenCalledWith('/auth/login/', loginData)
    })
  })

  describe('register', () => {
    it('应该成功调用注册API', async () => {
      const registerData = {
        username: 'newuser',
        email: 'new@example.com',
        first_name: 'New',
        password: 'newpass123',
        password_confirm: 'newpass123'
      }
      const mockResponse = { data: { message: '注册成功' } }
      mockRequest.post.mockResolvedValue(mockResponse)

      const result = await authAPI.register(registerData)

      expect(mockRequest.post).toHaveBeenCalledWith('/auth/register/', registerData)
      expect(result).toEqual(mockResponse)
    })

    it('应该处理注册失败', async () => {
      const registerData = { username: 'existinguser', email: 'existing@example.com' }
      const mockError = new Error('用户名已存在')
      mockRequest.post.mockRejectedValue(mockError)

      await expect(authAPI.register(registerData)).rejects.toThrow('用户名已存在')
      expect(mockRequest.post).toHaveBeenCalledWith('/auth/register/', registerData)
    })
  })

  describe('logout', () => {
    it('应该成功调用登出API', async () => {
      const mockResponse = { data: { message: '登出成功' } }
      mockRequest.post.mockResolvedValue(mockResponse)

      const result = await authAPI.logout()

      expect(mockRequest.post).toHaveBeenCalledWith('/auth/logout/')
      expect(result).toEqual(mockResponse)
    })

    it('应该处理登出失败', async () => {
      const mockError = new Error('登出失败')
      mockRequest.post.mockRejectedValue(mockError)

      await expect(authAPI.logout()).rejects.toThrow('登出失败')
      expect(mockRequest.post).toHaveBeenCalledWith('/auth/logout/')
    })
  })

  describe('refreshToken', () => {
    it('应该成功刷新Token', async () => {
      const refreshToken = 'refresh-token-123'
      const mockResponse = { data: { access: 'new-access-token' } }
      mockRequest.post.mockResolvedValue(mockResponse)

      const result = await authAPI.refreshToken(refreshToken)

      expect(mockRequest.post).toHaveBeenCalledWith('/auth/token/refresh/', { refresh: refreshToken })
      expect(result).toEqual(mockResponse)
    })

    it('应该处理Token刷新失败', async () => {
      const refreshToken = 'invalid-refresh-token'
      const mockError = new Error('Token已过期')
      mockRequest.post.mockRejectedValue(mockError)

      await expect(authAPI.refreshToken(refreshToken)).rejects.toThrow('Token已过期')
      expect(mockRequest.post).toHaveBeenCalledWith('/auth/token/refresh/', { refresh: refreshToken })
    })
  })

  describe('getCurrentUser', () => {
    it('应该成功获取当前用户信息', async () => {
      const mockResponse = { data: { username: 'testuser', email: 'test@example.com' } }
      mockRequest.get.mockResolvedValue(mockResponse)

      const result = await authAPI.getCurrentUser()

      expect(mockRequest.get).toHaveBeenCalledWith('/users/me/')
      expect(result).toEqual(mockResponse)
    })

    it('应该处理获取用户信息失败', async () => {
      const mockError = new Error('未授权')
      mockRequest.get.mockRejectedValue(mockError)

      await expect(authAPI.getCurrentUser()).rejects.toThrow('未授权')
      expect(mockRequest.get).toHaveBeenCalledWith('/users/me/')
    })
  })

  describe('verifyUserIdentity', () => {
    it('应该成功验证用户身份', async () => {
      const identityData = { username: 'testuser', password: 'testpass' }
      const mockResponse = { data: { verified: true, user_info: { username: 'testuser' } } }
      mockAxios.post.mockResolvedValue(mockResponse)

      const result = await authAPI.verifyUserIdentity(identityData)

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/auth/verify-identity/', identityData, {
        headers: { 'Content-Type': 'application/json' }
      })
      expect(result).toEqual(mockResponse.data)
    })

    it('应该处理身份验证失败', async () => {
      const identityData = { username: 'testuser', password: 'wrongpass' }
      const mockError = new Error('用户名或密码错误')
      mockAxios.post.mockRejectedValue(mockError)

      await expect(authAPI.verifyUserIdentity(identityData)).rejects.toThrow('用户名或密码错误')
      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/auth/verify-identity/', identityData, {
        headers: { 'Content-Type': 'application/json' }
      })
    })
  })

  describe('requestPasswordReset', () => {
    it('应该成功请求密码重置', async () => {
      const email = 'test@example.com'
      const mockResponse = { data: { message: '重置邮件已发送' } }
      mockAxios.post.mockResolvedValue(mockResponse)

      const result = await authAPI.requestPasswordReset(email)

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/auth/password-reset/', { email }, {
        headers: { 'Content-Type': 'application/json' }
      })
      expect(result).toEqual(mockResponse.data)
    })

    it('应该处理密码重置请求失败', async () => {
      const email = 'nonexistent@example.com'
      const mockError = new Error('邮箱不存在')
      mockAxios.post.mockRejectedValue(mockError)

      await expect(authAPI.requestPasswordReset(email)).rejects.toThrow('邮箱不存在')
      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/auth/password-reset/', { email }, {
        headers: { 'Content-Type': 'application/json' }
      })
    })
  })

  describe('confirmPasswordReset', () => {
    it('应该成功确认密码重置', async () => {
      const resetData = {
        token: 'reset-token-123',
        password: 'newpassword123',
        password_confirm: 'newpassword123'
      }
      const mockResponse = { data: { message: '密码重置成功' } }
      mockAxios.post.mockResolvedValue(mockResponse)

      const result = await authAPI.confirmPasswordReset(resetData)

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/auth/password-reset-confirm/', resetData, {
        headers: { 'Content-Type': 'application/json' }
      })
      expect(result).toEqual(mockResponse.data)
    })

    it('应该处理密码重置确认失败', async () => {
      const resetData = { token: 'invalid-token', password: 'newpass' }
      const mockError = new Error('Token无效')
      mockAxios.post.mockRejectedValue(mockError)

      await expect(authAPI.confirmPasswordReset(resetData)).rejects.toThrow('Token无效')
      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/auth/password-reset-confirm/', resetData, {
        headers: { 'Content-Type': 'application/json' }
      })
    })
  })
}) 