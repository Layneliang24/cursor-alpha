import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

// Mock API
vi.mock('@/api/auth', () => ({
  authAPI: {
    login: vi.fn(),
    logout: vi.fn(),
    verifyUserIdentity: vi.fn(),
    requestPasswordReset: vi.fn(),
  }
}))

describe('Auth Store', () => {
  let store
  let authAPI

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useAuthStore()
    authAPI = require('@/api/auth').authAPI
    
    // Reset mocks
    vi.clearAllMocks()
    
    // Reset localStorage
    localStorage.clear()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      expect(store.isAuthenticated).toBe(false)
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.loading).toBe(false)
    })
  })

  describe('Login', () => {
    it('should login successfully', async () => {
      const loginData = {
        username: 'testuser',
        password: 'password123'
      }
      const mockResponse = {
        token: 'mock-token',
        user: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com'
        }
      }
      
      authAPI.login.mockResolvedValue(mockResponse)

      await store.login(loginData)

      expect(authAPI.login).toHaveBeenCalledWith(loginData)
      expect(store.isAuthenticated).toBe(true)
      expect(store.user).toEqual(mockResponse.user)
      expect(store.token).toBe(mockResponse.token)
      expect(store.loading).toBe(false)
    })

    it('should handle login failure', async () => {
      const loginData = {
        username: 'testuser',
        password: 'wrongpassword'
      }
      const error = new Error('Invalid credentials')
      
      authAPI.login.mockRejectedValue(error)

      await expect(store.login(loginData)).rejects.toThrow('Invalid credentials')
      
      expect(store.isAuthenticated).toBe(false)
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.loading).toBe(false)
    })

    it('should set loading state during login', async () => {
      const loginData = {
        username: 'testuser',
        password: 'password123'
      }
      
      // Create a promise that doesn't resolve immediately
      let resolveLogin
      const loginPromise = new Promise(resolve => {
        resolveLogin = resolve
      })
      authAPI.login.mockReturnValue(loginPromise)

      const loginPromiseResult = store.login(loginData)
      
      // Check loading state
      expect(store.loading).toBe(true)
      
      // Resolve the promise
      resolveLogin({
        token: 'mock-token',
        user: { id: 1, username: 'testuser' }
      })
      
      await loginPromiseResult
      expect(store.loading).toBe(false)
    })
  })

  describe('Logout', () => {
    it('should logout successfully', async () => {
      // Set initial authenticated state
      store.$patch({
        isAuthenticated: true,
        user: { id: 1, username: 'testuser' },
        token: 'mock-token'
      })

      authAPI.logout.mockResolvedValue({})

      await store.logout()

      expect(authAPI.logout).toHaveBeenCalled()
      expect(store.isAuthenticated).toBe(false)
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
    })

    it('should logout even if API call fails', async () => {
      // Set initial authenticated state
      store.$patch({
        isAuthenticated: true,
        user: { id: 1, username: 'testuser' },
        token: 'mock-token'
      })

      authAPI.logout.mockRejectedValue(new Error('Network error'))

      await store.logout()

      expect(store.isAuthenticated).toBe(false)
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
    })
  })

  describe('Token Management', () => {
    it('should save token to localStorage', async () => {
      const loginData = {
        username: 'testuser',
        password: 'password123'
      }
      const mockResponse = {
        token: 'mock-token',
        user: { id: 1, username: 'testuser' }
      }
      
      authAPI.login.mockResolvedValue(mockResponse)

      await store.login(loginData)

      expect(localStorage.getItem('auth_token')).toBe('mock-token')
    })

    it('should load token from localStorage on initialization', () => {
      localStorage.setItem('auth_token', 'saved-token')
      localStorage.setItem('auth_user', JSON.stringify({ id: 1, username: 'testuser' }))

      // Create new store instance
      const newStore = useAuthStore()

      expect(newStore.token).toBe('saved-token')
      expect(newStore.user).toEqual({ id: 1, username: 'testuser' })
      expect(newStore.isAuthenticated).toBe(true)
    })

    it('should clear token from localStorage on logout', async () => {
      // Set initial state
      store.$patch({
        isAuthenticated: true,
        user: { id: 1, username: 'testuser' },
        token: 'mock-token'
      })
      localStorage.setItem('auth_token', 'mock-token')
      localStorage.setItem('auth_user', JSON.stringify({ id: 1, username: 'testuser' }))

      authAPI.logout.mockResolvedValue({})

      await store.logout()

      expect(localStorage.getItem('auth_token')).toBeNull()
      expect(localStorage.getItem('auth_user')).toBeNull()
    })
  })

  describe('User Verification', () => {
    it('should verify user identity', async () => {
      const credentials = {
        username: 'testuser',
        password: 'password123'
      }
      const mockResponse = {
        verified: true,
        user_info: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com'
        }
      }
      
      authAPI.verifyUserIdentity.mockResolvedValue(mockResponse)

      const result = await store.verifyIdentity(credentials)

      expect(authAPI.verifyUserIdentity).toHaveBeenCalledWith(credentials)
      expect(result).toEqual(mockResponse)
    })

    it('should handle verification failure', async () => {
      const credentials = {
        username: 'testuser',
        password: 'wrongpassword'
      }
      const mockResponse = {
        verified: false,
        user_info: null
      }
      
      authAPI.verifyUserIdentity.mockResolvedValue(mockResponse)

      const result = await store.verifyIdentity(credentials)

      expect(result.verified).toBe(false)
      expect(result.user_info).toBeNull()
    })
  })

  describe('Password Reset', () => {
    it('should request password reset', async () => {
      const email = 'test@example.com'
      const mockResponse = { message: 'Reset email sent' }
      
      authAPI.requestPasswordReset.mockResolvedValue(mockResponse)

      const result = await store.requestPasswordReset(email)

      expect(authAPI.requestPasswordReset).toHaveBeenCalledWith(email)
      expect(result).toEqual(mockResponse)
    })

    it('should handle password reset error', async () => {
      const email = 'nonexistent@example.com'
      const error = new Error('User not found')
      
      authAPI.requestPasswordReset.mockRejectedValue(error)

      await expect(store.requestPasswordReset(email)).rejects.toThrow('User not found')
    })
  })

  describe('Getters', () => {
    it('should return user display name', () => {
      store.$patch({
        user: {
          id: 1,
          username: 'testuser',
          first_name: 'Test',
          last_name: 'User'
        }
      })

      expect(store.userDisplayName).toBe('Test User')
    })

    it('should return username when no first/last name', () => {
      store.$patch({
        user: {
          id: 1,
          username: 'testuser'
        }
      })

      expect(store.userDisplayName).toBe('testuser')
    })

    it('should return empty string when no user', () => {
      expect(store.userDisplayName).toBe('')
    })
  })
})
