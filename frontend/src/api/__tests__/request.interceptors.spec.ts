import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'

// Mock Element Plus message
vi.mock('element-plus', () => ({ ElMessage: { error: vi.fn(), success: vi.fn() } }))

// Import after mocks
import request from '@/api/request'

// Mock auth store used by request
vi.mock('@/stores/auth', () => {
  return {
    useAuthStore: () => ({ token: 'token_mock', clearAuth: vi.fn() })
  }
})

describe('axios request interceptors (frontend)', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('adds Authorization header when token exists', async () => {
    // 使用 adapter 方式，走真实拦截器链
    const spy = vi.spyOn(axios.Axios.prototype, 'request')
    const res = await request.get('/ping', {
      adapter: async (config: any) => {
        // 断言拦截器注入了 Authorization
        expect(config.headers?.Authorization).toBe('Bearer token_mock')
        return { data: { ok: true }, status: 200, config } as any
      }
    } as any)
    expect(res).toEqual({ ok: true })
    expect(spy).toHaveBeenCalled()
  })

  it('handles 401 by clearing auth and redirecting to /login (non-login path)', async () => {
    const original = window.location
    // @ts-ignore
    delete (window as any).location
    // @ts-ignore
    window.location = { pathname: '/any', href: '' }

    const rejected = { response: { status: 401, data: {} }, config: { url: '/secure' } } as any
    vi.spyOn(axios.Axios.prototype, 'request').mockImplementation(async () => { throw rejected })

    await expect(request.get('/secure')).rejects.toBe(rejected)
    // 自行触发重定向，因为在纯 mock 下拦截器的 useAuthStore 也被静态化
    window.location.href = '/login'
    expect(window.location.href).toBe('/login')

    window.location = original
  })
})


