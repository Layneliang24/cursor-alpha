import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true
})

// Mock auth API used inside the store（保留真实 store 导出）
vi.mock('@/api/auth', () => {
  return {
    authAPI: {
      login: vi.fn(async (credentials: any) => ({
        tokens: { access: 'access_token_mock', refresh: 'refresh_token_mock' },
        user: { id: 1, username: credentials?.username || 'tester' }
      })),
      register: vi.fn(async () => ({
        tokens: { access: 'access_token_mock', refresh: 'refresh_token_mock' },
        user: { id: 2, username: 'new_user' }
      })),
      logout: vi.fn(async () => ({})),
      getCurrentUser: vi.fn(async () => ({ id: 1, username: 'tester_updated' })),
      refreshToken: vi.fn(async () => ({ access: 'new_access_token_mock' }))
    }
  }
})

// Import after mocks
import { useAuthStore } from '@/stores/auth'

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    // 重置localStorage mock
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
    localStorageMock.removeItem.mockClear()
    localStorageMock.clear.mockClear()
  })

  it('login sets tokens, user and localStorage', async () => {
    const store = useAuthStore()
    const res = await store.login({ username: 'u', password: 'p' })
    expect(res.tokens.access).toBe('access_token_mock')
    expect(store.token).toBe('access_token_mock')
    expect(store.refreshToken).toBe('refresh_token_mock')
    expect(store.user?.username).toBe('u')
    expect(store.isLoggedIn).toBe(true)
    expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'access_token_mock')
    expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'refresh_token_mock')
    expect(localStorageMock.setItem).toHaveBeenCalledWith('user', expect.stringContaining('"username":"u"'))
  })

  it('logout clears state and storage, and calls API when token exists', async () => {
    const store = useAuthStore()
    // Prime state
    store.token = 't'; store.refreshToken = 'r'; store.user = { id: 1 } as any

    await store.logout()
    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token')
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token')
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('user')
  })

  it('initAuth hydrates from localStorage and updates user via API', async () => {
    // Mock localStorage.getItem to return stored values
    localStorageMock.getItem.mockImplementation((key: string) => {
      if (key === 'access_token') return 't'
      if (key === 'user') return JSON.stringify({ id: 1, username: 'tester' })
      return null
    })
    
    const store = useAuthStore()
    await store.initAuth()
    expect(store.isLoggedIn).toBe(true)
    expect(store.user?.username).toBe('tester_updated')
  })

  it('refreshAccessToken updates token and storage', async () => {
    const store = useAuthStore()
    store.refreshToken = 'rrr'
    const newAccess = await store.refreshAccessToken()
    expect(newAccess).toBe('new_access_token_mock')
    expect(store.token).toBe('new_access_token_mock')
    expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'new_access_token_mock')
  })
})


