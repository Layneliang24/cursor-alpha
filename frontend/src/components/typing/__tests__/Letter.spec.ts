import { mount } from '@vue/test-utils'
import Letter from '../Letter.vue'

describe('Letter component', () => {
  it('renders visible letter with correct classes', () => {
    const wrapper = mount(Letter, { props: { letter: 'A', state: 'correct', visible: true, fontSize: 32 } })
    expect(wrapper.text()).toBe('A')
    expect(wrapper.classes()).toContain('letter-base')
    expect(wrapper.classes()).toContain('letter-correct')
    expect((wrapper.element as HTMLElement).style.fontSize).toBe('32px')
  })

  it('renders underscore when not visible', () => {
    const wrapper = mount(Letter, { props: { letter: 'B', visible: false } })
    expect(wrapper.text()).toBe('_')
  })

  it('falls back to normal state for invalid state', () => {
    const wrapper = mount(Letter, { props: { letter: 'C', state: 'invalid' as any } })
    expect(wrapper.classes()).toContain('letter-normal')
  })
})


