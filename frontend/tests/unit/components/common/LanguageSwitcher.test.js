import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import LanguageSwitcher from '@/components/common/LanguageSwitcher.vue'

// Mock i18n
const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': {
      common: {
        language: '语言'
      }
    },
    'en-US': {
      common: {
        language: 'Language'
      }
    }
  }
})

describe('LanguageSwitcher', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(LanguageSwitcher, {
      global: {
        plugins: [i18n]
      }
    })
  })

  it('should render language switcher', () => {
    expect(wrapper.find('.language-switcher').exists()).toBe(true)
  })

  it('should show current language', () => {
    const currentLang = wrapper.find('.current-language')
    expect(currentLang.exists()).toBe(true)
    expect(currentLang.text()).toContain('中文')
  })

  it('should show language options on click', async () => {
    const trigger = wrapper.find('.language-trigger')
    await trigger.trigger('click')
    
    const dropdown = wrapper.find('.language-dropdown')
    expect(dropdown.exists()).toBe(true)
  })

  it('should have both Chinese and English options', async () => {
    const trigger = wrapper.find('.language-trigger')
    await trigger.trigger('click')
    
    const options = wrapper.findAll('.language-option')
    expect(options).toHaveLength(2)
    
    const optionTexts = options.map(option => option.text())
    expect(optionTexts).toContain('中文')
    expect(optionTexts).toContain('English')
  })

  it('should emit language change event', async () => {
    const trigger = wrapper.find('.language-trigger')
    await trigger.trigger('click')
    
    const englishOption = wrapper.find('.language-option[data-lang="en-US"]')
    await englishOption.trigger('click')
    
    expect(wrapper.emitted('language-change')).toBeTruthy()
    expect(wrapper.emitted('language-change')[0]).toEqual(['en-US'])
  })

  it('should update current language when changed', async () => {
    const trigger = wrapper.find('.language-trigger')
    await trigger.trigger('click')
    
    const englishOption = wrapper.find('.language-option[data-lang="en-US"]')
    await englishOption.trigger('click')
    
    // Wait for Vue to update
    await wrapper.vm.$nextTick()
    
    const currentLang = wrapper.find('.current-language')
    expect(currentLang.text()).toContain('English')
  })

  it('should close dropdown when clicking outside', async () => {
    const trigger = wrapper.find('.language-trigger')
    await trigger.trigger('click')
    
    // Click outside
    document.body.click()
    await wrapper.vm.$nextTick()
    
    const dropdown = wrapper.find('.language-dropdown')
    expect(dropdown.exists()).toBe(false)
  })

  it('should have proper accessibility attributes', () => {
    const trigger = wrapper.find('.language-trigger')
    expect(trigger.attributes('aria-label')).toBe('切换语言')
    expect(trigger.attributes('role')).toBe('button')
  })

  it('should handle keyboard navigation', async () => {
    const trigger = wrapper.find('.language-trigger')
    await trigger.trigger('keydown.enter')
    
    const dropdown = wrapper.find('.language-dropdown')
    expect(dropdown.exists()).toBe(true)
  })
})
