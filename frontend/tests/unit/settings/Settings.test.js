import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import Settings from '@/views/english/Settings.vue'

// Mock components
vi.mock('@/components/settings/UserProfileSettings.vue', () => ({
  default: {
    name: 'UserProfileSettings',
    template: '<div class="user-profile-settings">User Profile Settings</div>'
  }
}))

vi.mock('@/components/settings/PreferenceSettings.vue', () => ({
  default: {
    name: 'PreferenceSettings',
    template: '<div class="preference-settings">Preference Settings</div>'
  }
}))

vi.mock('@/components/settings/SecuritySettings.vue', () => ({
  default: {
    name: 'SecuritySettings',
    template: '<div class="security-settings">Security Settings</div>'
  }
}))

vi.mock('@/components/settings/NotificationSettings.vue', () => ({
  default: {
    name: 'NotificationSettings',
    template: '<div class="notification-settings">Notification Settings</div>'
  }
}))

vi.mock('@/components/settings/SystemSettings.vue', () => ({
  default: {
    name: 'SystemSettings',
    template: '<div class="system-settings">System Settings</div>'
  }
}))

vi.mock('@/components/settings/LoginHistory.vue', () => ({
  default: {
    name: 'LoginHistory',
    template: '<div class="login-history">Login History</div>'
  }
}))

vi.mock('@/components/settings/DeviceManagement.vue', () => ({
  default: {
    name: 'DeviceManagement',
    template: '<div class="device-management">Device Management</div>'
  }
}))

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/english/settings',
      name: 'Settings',
      component: Settings
    }
  ]
})

describe('Settings', () => {
  let wrapper

  beforeEach(async () => {
    await router.push('/english/settings')
    wrapper = mount(Settings, {
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

  it('应该正确渲染设置页面', () => {
    expect(wrapper.find('.settings-page').exists()).toBe(true)
    expect(wrapper.find('.page-title').text()).toBe('系统设置')
  })

  it('应该包含所有设置标签页', () => {
    const tabs = wrapper.findAll('.el-tab-pane')
    expect(tabs.length).toBe(7) // 7个标签页
  })

  it('应该默认选中个人信息标签页', () => {
    expect(wrapper.vm.activeTab).toBe('profile')
  })

  it('应该包含所有设置组件', () => {
    expect(wrapper.findComponent({ name: 'UserProfileSettings' }).exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'PreferenceSettings' }).exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'SecuritySettings' }).exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'NotificationSettings' }).exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'SystemSettings' }).exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'LoginHistory' }).exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'DeviceManagement' }).exists()).toBe(true)
  })

  it('应该能够切换标签页', async () => {
    wrapper.vm.activeTab = 'preferences'
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.activeTab).toBe('preferences')
  })

  it('应该能够返回上一页', async () => {
    const goBackSpy = vi.spyOn(router, 'go')
    await wrapper.vm.goBack()
    expect(goBackSpy).toHaveBeenCalledWith(-1)
  })
})
