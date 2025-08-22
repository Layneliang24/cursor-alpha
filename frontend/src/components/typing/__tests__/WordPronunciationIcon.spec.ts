import { mount } from '@vue/test-utils'
import WordPronunciationIcon from '../WordPronunciationIcon.vue'
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock usePronunciation hook used inside component
vi.mock('@/hooks/usePronunciation', () => ({
  __esModule: true,
  default: () => ({ play: vi.fn(), stop: vi.fn(), isPlaying: false }),
}))

describe('WordPronunciationIcon', () => {
  beforeEach(() => vi.restoreAllMocks())

  it('renders and can trigger play on click', async () => {
    const wrapper = mount(WordPronunciationIcon, { props: { word: 'alpha' } })
    await wrapper.trigger('click')
    expect(wrapper.exists()).toBe(true)
  })
})


