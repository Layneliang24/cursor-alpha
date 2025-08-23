import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import NavBar from '../NavBar.vue'

describe('NavBar Component', () => {
  let wrapper: any
  let router: any
  let pinia: any

  beforeEach(async () => {
    // 设置 Pinia
    pinia = createPinia()
    setActivePinia(pinia)

    // 设置路由
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } },
        { path: '/articles', component: { template: '<div>Articles</div>' } },
        { path: '/english/news-dashboard', component: { template: '<div>News</div>' } },
        { path: '/english/words', component: { template: '<div>Words</div>' } }
      ]
    })

    wrapper = mount(NavBar, {
      global: {
        plugins: [router, pinia],
        stubs: {
          'el-menu': {
            template: '<nav class="nav-menu el-menu"><slot /></nav>',
            props: ['default-active', 'mode', 'router']
          },
          'el-menu-item': {
            template: '<a class="el-menu-item" :index="index"><slot /></a>',
            props: ['index']
          },
          'el-sub-menu': {
            template: '<div class="el-sub-menu"><slot /><slot name="title" /></div>',
            props: ['index']
          },
          'el-icon': {
            template: '<span class="el-icon"><slot /></span>'
          }
        }
      }
    })
    await router.isReady()
  })

  it('renders navigation bar correctly', () => {
    expect(wrapper.find('.nav-menu').exists()).toBe(true)
    expect(wrapper.find('.el-menu').exists()).toBe(true)
  })

  it('displays brand/logo', () => {
    // NavBar组件通过第一个menu-item显示品牌
    const brandItem = wrapper.find('[index="/"]')
    expect(brandItem.exists()).toBe(true)
    expect(wrapper.text()).toContain('Alpha 技术共享平台')
  })

  it('has navigation menu items', () => {
    const navItems = wrapper.findAll('.el-menu-item')
    expect(navItems.length).toBeGreaterThan(0)
  })

  it('has sub-menu for English learning', () => {
    const subMenu = wrapper.find('.el-sub-menu')
    expect(subMenu.exists()).toBe(true)
    expect(wrapper.text()).toContain('英语学习')
  })

  it('has articles menu item', () => {
    const articlesItem = wrapper.find('[index="/articles"]')
    expect(articlesItem.exists()).toBe(true)
    expect(wrapper.text()).toContain('文章')
  })

  it('applies correct CSS classes', () => {
    expect(wrapper.classes()).toContain('nav-menu')
  })

  it('has proper menu mode', () => {
    const menu = wrapper.find('.el-menu')
    expect(menu.exists()).toBe(true)
  })
})