import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import ConfigManagement from '@/views/english/ConfigManagement.vue'
import ConfigImportExport from '@/components/config/ConfigImportExport.vue'
import ConfigTemplateManager from '@/components/config/ConfigTemplateManager.vue'
import ConfigVersionManager from '@/components/config/ConfigVersionManager.vue'

// Mock components
vi.mock('@/components/config/ConfigImportExport.vue', () => ({
  default: {
    name: 'ConfigImportExport',
    template: '<div class="config-import-export">Import Export Component</div>'
  }
}))

vi.mock('@/components/config/ConfigTemplateManager.vue', () => ({
  default: {
    name: 'ConfigTemplateManager',
    template: '<div class="config-template-manager">Template Manager Component</div>'
  }
}))

vi.mock('@/components/config/ConfigVersionManager.vue', () => ({
  default: {
    name: 'ConfigVersionManager',
    template: '<div class="config-version-manager">Version Manager Component</div>'
  }
}))

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/english/config-management',
      name: 'ConfigManagement',
      component: ConfigManagement
    }
  ]
})

describe('ConfigManagement', () => {
  let wrapper

  beforeEach(async () => {
    await router.push('/english/config-management')
    wrapper = mount(ConfigManagement, {
      global: {
        plugins: [router],
        stubs: {
          'el-page-header': true,
          'el-tabs': true,
          'el-tab-pane': true
        }
      }
    })
  })

  it('应该正确渲染配置管理页面', () => {
    expect(wrapper.find('.config-management').exists()).toBe(true)
    expect(wrapper.find('.page-title').text()).toBe('AI配置管理')
  })

  it('应该包含三个标签页', () => {
    const tabs = wrapper.findAll('.el-tab-pane')
    expect(tabs.length).toBe(3)
  })

  it('应该默认显示导入导出标签页', () => {
    expect(wrapper.vm.activeTab).toBe('import-export')
  })

  it('应该包含配置导入导出组件', () => {
    expect(wrapper.findComponent(ConfigImportExport).exists()).toBe(true)
  })

  it('应该包含配置模板管理组件', () => {
    expect(wrapper.findComponent(ConfigTemplateManager).exists()).toBe(true)
  })

  it('应该包含配置版本管理组件', () => {
    expect(wrapper.findComponent(ConfigVersionManager).exists()).toBe(true)
  })

  it('应该能够切换标签页', async () => {
    await wrapper.setData({ activeTab: 'templates' })
    expect(wrapper.vm.activeTab).toBe('templates')
  })

  it('应该能够返回上一页', async () => {
    const goBackSpy = vi.spyOn(wrapper.vm.$router, 'go')
    await wrapper.vm.goBack()
    expect(goBackSpy).toHaveBeenCalledWith(-1)
  })
})
