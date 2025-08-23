import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import FooterComponent from '../FooterComponent.vue'

describe('FooterComponent', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = mount(FooterComponent)
  })

  it('renders footer correctly', () => {
    expect(wrapper.find('footer').exists()).toBe(true)
  })

  it('displays copyright information', () => {
    expect(wrapper.text()).toContain('©')
    expect(wrapper.text()).toContain('2024')
  })

  it('has proper CSS classes', () => {
    expect(wrapper.classes()).toContain('footer')
  })

  it('has proper semantic structure', () => {
    expect(wrapper.find('footer').exists()).toBe(true)
  })

  it('displays company or project name', () => {
    expect(wrapper.text()).toContain('Alpha')
  })
})
