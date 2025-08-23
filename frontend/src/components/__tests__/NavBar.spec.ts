import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import NavBar from '../NavBar.vue'

// Mock 路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
    { path: '/login', name: 'login', component: { template: '<div>Login</div>' } },
    { path: '/register', name: 'register', component: { template: '<div>Register</div>' } }
  ]
})

// Mock Pinia store
const pinia = createPinia()

describe('NavBar Component', () => {
  let wrapper: any

  beforeEach(async () => {
    wrapper = mount(NavBar, {
      global: {
        plugins: [router, pinia],
        stubs: {
          'router-link': true,
          'router-view': true
        }
      }
    })
    await router.isReady()
  })

  it('renders navigation bar correctly', () => {
    expect(wrapper.find('.modern-navbar').exists()).toBe(true)
    expect(wrapper.find('.container-fluid').exists()).toBe(true)
  })

  it('displays brand/logo', () => {
    expect(wrapper.find('.navbar-brand').exists()).toBe(true)
  })

  it('has navigation menu items', () => {
    const navItems = wrapper.findAll('.nav-link')
    expect(navItems.length).toBeGreaterThan(0)
  })

  it('has responsive toggle button', () => {
    expect(wrapper.find('.navbar-toggler').exists()).toBe(true)
  })

  it('has user authentication section', () => {
    expect(wrapper.find('.navbar-nav').exists()).toBe(true)
  })

  it('applies correct CSS classes', () => {
    expect(wrapper.classes()).toContain('navbar')
    expect(wrapper.classes()).toContain('navbar-expand-lg')
  })

  it('has proper accessibility attributes', () => {
    const navbar = wrapper.find('.modern-navbar')
    expect(navbar.attributes('role')).toBe('navigation')
  })
})
