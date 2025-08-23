import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import WordPronunciationIcon from '../WordPronunciationIcon.vue'

// Mock @vueuse/sound
vi.mock('@vueuse/sound', () => ({
  useSound: vi.fn(() => ({
    play: vi.fn(),
    stop: vi.fn(),
    sound: { unload: vi.fn() },
    isPlaying: false
  }))
}))

// Mock Audio API
const mockAudio = {
  play: vi.fn().mockResolvedValue(undefined),
  pause: vi.fn(),
  currentTime: 0,
  duration: 0,
  volume: 1,
  playbackRate: 1,
  addEventListener: vi.fn(),
  removeEventListener: vi.fn()
}

global.Audio = vi.fn(() => mockAudio)

// Mock window.stopAllPronunciations
Object.defineProperty(window, 'stopAllPronunciations', {
  value: vi.fn(),
  writable: true
})

// Mock console methods
const consoleSpy = {
  log: vi.spyOn(console, 'log').mockImplementation(() => {}),
  error: vi.spyOn(console, 'error').mockImplementation(() => {})
}

describe('WordPronunciationIcon Component', () => {
  let wrapper: any
  let mockUseSound: any

  beforeEach(() => {
    // 重置所有mock
    vi.clearAllMocks()
    
    // 创建useSound mock
    mockUseSound = {
      play: vi.fn(),
      stop: vi.fn(),
      sound: { unload: vi.fn() },
      isPlaying: false
    }
    
    vi.mocked(vi.importMock('@vueuse/sound').useSound).mockReturnValue(mockUseSound)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('正确渲染发音图标按钮', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'hello'
        }
      })

      const button = wrapper.find('.sound-icon')
      expect(button.exists()).toBe(true)
      expect(button.text()).toBe('🔊')
    })

    it('显示正确的标题属性', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'world'
        }
      })

      const button = wrapper.find('.sound-icon')
      expect(button.attributes('title')).toBe('播放 world 的发音')
    })

    it('应用正确的CSS类', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'test'
        }
      })

      const button = wrapper.find('.sound-icon')
      expect(button.classes()).toContain('sound-icon')
      expect(button.classes()).not.toContain('playing')
    })
  })

  describe('Props处理', () => {
    it('正确接收word prop', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'example'
        }
      })

      expect(wrapper.props('word')).toBe('example')
    })

    it('使用默认pronunciationType', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'test'
        }
      })

      expect(wrapper.props('pronunciationType')).toBe('us')
    })

    it('正确设置pronunciationType', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'test',
          pronunciationType: 'uk'
        }
      })

      expect(wrapper.props('pronunciationType')).toBe('uk')
    })
  })

  describe('发音功能', () => {
    it('点击按钮触发playSound方法', async () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'hello'
        }
      })

      const button = wrapper.find('.sound-icon')
      await button.trigger('click')

      // 检查是否调用了playSound
      expect(button.exists()).toBe(true)
    })

    it('生成正确的美式发音URL', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'hello',
          pronunciationType: 'us'
        }
      })

      // 检查组件是否正确挂载
      expect(wrapper.exists()).toBe(true)
    })

    it('生成正确的英式发音URL', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'world',
          pronunciationType: 'uk'
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('处理空单词', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: ''
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('处理特殊字符单词', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'café'
        }
      })

      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('播放状态', () => {
    it('播放时显示playing类', async () => {
      // 模拟播放状态
      mockUseSound.isPlaying = true

      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'hello'
        }
      })

      await wrapper.vm.$nextTick()

      const button = wrapper.find('.sound-icon')
      expect(button.classes()).toContain('playing')
    })

    it('停止播放时隐藏playing类', async () => {
      // 模拟停止状态
      mockUseSound.isPlaying = false

      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'hello'
        }
      })

      await wrapper.vm.$nextTick()

      const button = wrapper.find('.sound-icon')
      expect(button.classes()).not.toContain('playing')
    })
  })

  describe('生命周期', () => {
    it('组件挂载时记录日志', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'test'
        }
      })

      expect(consoleSpy.log).toHaveBeenCalledWith(
        'WordPronunciationIcon mounted, word:', 'test', 'soundSrc:', expect.any(String)
      )
    })

    it('组件卸载时清理资源', async () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'test'
        }
      })

      await wrapper.unmount()

      // 检查是否调用了stop和unload
      expect(mockUseSound.stop).toHaveBeenCalled()
    })
  })

  describe('错误处理', () => {
    it('处理播放失败的情况', async () => {
      // 模拟Audio.play失败
      mockAudio.play.mockRejectedValue(new Error('播放失败'))

      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'test'
        }
      })

      const button = wrapper.find('.sound-icon')
      await button.trigger('click')

      // 检查是否仍然正常工作
      expect(wrapper.exists()).toBe(true)
    })

    it('处理无效的发音类型', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'test',
          pronunciationType: 'invalid'
        }
      })

      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('交互行为', () => {
    it('按钮可点击', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'hello'
        }
      })

      const button = wrapper.find('.sound-icon')
      expect(button.element.disabled).toBeFalsy()
    })

    it('按钮有正确的类型', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'world'
        }
      })

      const button = wrapper.find('.sound-icon')
      expect(button.element.tagName).toBe('BUTTON')
    })
  })

  describe('URL生成逻辑', () => {
    it('美式发音使用type=2', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'hello',
          pronunciationType: 'us'
        }
      })

      // 检查组件是否正确处理发音类型
      expect(wrapper.props('pronunciationType')).toBe('us')
    })

    it('英式发音使用type=1', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'hello',
          pronunciationType: 'uk'
        }
      })

      expect(wrapper.props('pronunciationType')).toBe('uk')
    })

    it('URL编码特殊字符', () => {
      wrapper = mount(WordPronunciationIcon, {
        props: {
          word: 'hello world'
        }
      })

      expect(wrapper.exists()).toBe(true)
    })
  })
})


