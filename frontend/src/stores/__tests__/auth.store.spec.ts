import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'

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
    localStorage.clear()
  })

  it('login sets tokens, user and localStorage', async () => {
    const store = useAuthStore()
    const res = await store.login({ username: 'u', password: 'p' })
    expect(res.tokens.access).toBe('access_token_mock')
    expect(store.token).toBe('access_token_mock')
    expect(store.refreshToken).toBe('refresh_token_mock')
    expect(store.user?.username).toBe('u')
    expect(store.isLoggedIn).toBe(true)
    expect(localStorage.getItem('access_token')).toBe('access_token_mock')
    expect(localStorage.getItem('refresh_token')).toBe('refresh_token_mock')
    expect(localStorage.getItem('user')).toContain('"username":"u"')
  })

  it('logout clears state and storage, and calls API when token exists', async () => {
    const store = useAuthStore()
    // Prime state
    store.token = 't'; store.refreshToken = 'r'; store.user = { id: 1 } as any
    localStorage.setItem('access_token', 't')
    localStorage.setItem('refresh_token', 'r')
    localStorage.setItem('user', JSON.stringify({ id: 1 }))

    await store.logout()
    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
    expect(localStorage.getItem('access_token')).toBeNull()
  })

  it('initAuth hydrates from localStorage and updates user via API', async () => {
    localStorage.setItem('access_token', 't')
    localStorage.setItem('user', JSON.stringify({ id: 1, username: 'tester' }))
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
    expect(localStorage.getItem('access_token')).toBe('new_access_token_mock')
  })
})


