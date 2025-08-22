import { describe, it, expect, vi, beforeEach } from 'vitest'
import router from '@/router'
import { nextTick } from 'vue'

vi.mock('element-plus', () => ({ ElMessage: { warning: vi.fn() } }))

// 部分 mock vue-router：替换为内存历史，避免 I/O 与超时
vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal<any>()
  return {
    ...actual,
    createWebHistory: actual.createMemoryHistory,
  }
})

// Mock 动态视图，避免加载大页面
import { defineComponent } from 'vue'
vi.mock('@/views/english/Dashboard.vue', () => ({ default: defineComponent({ name: 'MockDashboard', template: '<div />' }) }))
vi.mock('@/views/Home.vue', () => ({ default: defineComponent({ name: 'MockHome', template: '<div />' }) }))
vi.mock('@/views/auth/Login.vue', () => ({ default: defineComponent({ name: 'MockLogin', template: '<div />' }) }))

// Mock auth store used in guard
vi.mock('@/stores/auth', () => {
  // 动态返回 store 状态以覆盖不同场景
  const state: any = { token: null, isLoggedIn: false, user: null }
  return {
    useAuthStore: () => ({
      get token() { return state.token },
      set token(v) { state.token = v },
      get isLoggedIn() { return state.isLoggedIn },
      set isLoggedIn(v) { state.isLoggedIn = v },
      get isAuthenticated() { return !!state.token && !!state.user },
      get user() { return state.user },
      set user(v) { state.user = v },
      initAuth: vi.fn(async () => { state.isLoggedIn = !!state.token })
    })
  }
})

describe('router guards', () => {
  beforeEach(async () => {
    // 确保路由处于已就绪状态，定位到首页
    try { await router.replace({ name: 'Home' }) } catch {}
    await nextTick()
  })

  it('redirects unauthenticated user from protected route to login', async () => {
    await router.push({ name: 'EnglishDashboard' }).catch(() => {})
    await nextTick()
    // 未登录应被重定向至登录页
    expect(router.currentRoute.value.name).toBe('Login')
  })

  it('allows access when authenticated', async () => {
    const mod = await import('@/stores/auth')
    const store = mod.useAuthStore()
    store.token = 't'
    store.user = { id: 1 }
    await router.push({ name: 'EnglishDashboard' }).catch(() => {})
    await nextTick()
    expect(router.currentRoute.value.name).toBe('EnglishDashboard')
  })
})


