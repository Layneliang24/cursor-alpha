import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ScenarioPlayer from '@/components/idiomatic-expressions/ScenarioPlayer.vue'
import { createTestingPinia } from '@pinia/testing'

// Mock Element Plus message
global.ElMessage = {
  error: vi.fn(),
}

// Mock HTML Audio API
class MockAudio {
  constructor (src) {
    this.src = src
    this.currentTime = 0
    this.duration = 120
    this.volume = 0.8
    this.playbackRate = 1
    this.paused = true
    this.muted = false
    this.addEventListener = vi.fn()
    this.removeEventListener = vi.fn()
    this.play = vi.fn().mockResolvedValue(undefined)
    this.pause = vi.fn()
    this.load = vi.fn()
  }
}

global.Audio = MockAudio

describe('ScenarioPlayer', () => {
  let wrapper
  
  const mockScenario = {
    id: 1,
    scenario_name: '商务会议场景',
    description: '学习商务会议中常用的地道表达',
    audio_url: 'https://example.com/audio.mp3',
    subtitles: [
      {
        startTime: 0,
        endTime: 3,
        text: "Let's break the ice with some small talk.",
        translation: '让我们先闲聊几句来打破沉默。',
        isExpression: true,
      },
    ],
    expressions: [
      {
        id: 1,
        expression: 'break the ice',
        startTime: 0,
        endTime: 3,
      },
    ],
  }

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('基础渲染', () => {
    it('应该正确渲染情景播放器', () => {
      wrapper = mount(ScenarioPlayer, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-slider': { template: '<div class="slider"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
            'el-switch': { template: '<input type="checkbox" />' },
            'el-card': { template: '<div><slot name="header" /><slot /></div>' },
            'el-form': { template: '<form><slot /></form>' },
            'el-form-item': { template: '<div><slot /></div>' },
            'el-tag': { template: '<span><slot /></span>' },
          },
        },
        props: {
          scenario: mockScenario,
        },
      })

      expect(wrapper.find('.scenario-player').exists()).toBe(true)
      expect(wrapper.find('.player-header').exists()).toBe(true)
      expect(wrapper.find('.audio-player').exists()).toBe(true)
    })

    it('应该显示情景标题和描述', () => {
      wrapper = mount(ScenarioPlayer, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-slider': { template: '<div class="slider"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
            'el-switch': { template: '<input type="checkbox" />' },
            'el-card': { template: '<div><slot name="header" /><slot /></div>' },
            'el-form': { template: '<form><slot /></form>' },
            'el-form-item': { template: '<div><slot /></div>' },
            'el-tag': { template: '<span><slot /></span>' },
          },
        },
        props: {
          scenario: mockScenario,
        },
      })

      const title = wrapper.find('.scenario-title')
      const description = wrapper.find('.scenario-description')
      
      expect(title.text()).toBe('商务会议场景')
      expect(description.text()).toBe('学习商务会议中常用的地道表达')
    })

    it('应该显示音频控制按钮', () => {
      wrapper = mount(ScenarioPlayer, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-slider': { template: '<div class="slider"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
            'el-switch': { template: '<input type="checkbox" />' },
            'el-card': { template: '<div><slot name="header" /><slot /></div>' },
            'el-form': { template: '<form><slot /></form>' },
            'el-form-item': { template: '<div><slot /></div>' },
            'el-tag': { template: '<span><slot /></span>' },
          },
        },
        props: {
          scenario: mockScenario,
        },
      })

      const audioControls = wrapper.find('.audio-controls')
      expect(audioControls.exists()).toBe(true)
    })

    it('应该显示播放速度控制按钮', () => {
      wrapper = mount(ScenarioPlayer, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-slider': { template: '<div class="slider"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
            'el-switch': { template: '<input type="checkbox" />' },
            'el-card': { template: '<div><slot name="header" /><slot /></div>' },
            'el-form': { template: '<form><slot /></form>' },
            'el-form-item': { template: '<div><slot /></div>' },
            'el-tag': { template: '<span><slot /></span>' },
          },
        },
        props: {
          scenario: mockScenario,
        },
      })

      const playbackControls = wrapper.find('.playback-controls')
      expect(playbackControls.exists()).toBe(true)
    })
  })

  describe('音频控制功能', () => {
    it('初始状态应该是暂停的', () => {
      wrapper = mount(ScenarioPlayer, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-slider': { template: '<div class="slider"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
            'el-switch': { template: '<input type="checkbox" />' },
            'el-card': { template: '<div><slot name="header" /><slot /></div>' },
            'el-form': { template: '<form><slot /></form>' },
            'el-form-item': { template: '<div><slot /></div>' },
            'el-tag': { template: '<span><slot /></span>' },
          },
        },
        props: {
          scenario: mockScenario,
        },
      })

      expect(wrapper.vm.isPlaying).toBe(false)
    })

    it('应该正确格式化时间', () => {
      wrapper = mount(ScenarioPlayer, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-slider': { template: '<div class="slider"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
            'el-switch': { template: '<input type="checkbox" />' },
            'el-card': { template: '<div><slot name="header" /><slot /></div>' },
            'el-form': { template: '<form><slot /></form>' },
            'el-form-item': { template: '<div><slot /></div>' },
            'el-tag': { template: '<span><slot /></span>' },
          },
        },
        props: {
          scenario: mockScenario,
        },
      })

      expect(wrapper.vm.formatTime(0)).toBe('00:00')
      expect(wrapper.vm.formatTime(65)).toBe('01:05')
      expect(wrapper.vm.formatTime(3661)).toBe('61:01')
    })
  })

  describe('字幕功能', () => {
    it('应该显示字幕容器', () => {
      wrapper = mount(ScenarioPlayer, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-slider': { template: '<div class="slider"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
            'el-switch': { template: '<input type="checkbox" />' },
            'el-card': { template: '<div><slot name="header" /><slot /></div>' },
            'el-form': { template: '<form><slot /></form>' },
            'el-form-item': { template: '<div><slot /></div>' },
            'el-tag': { template: '<span><slot /></span>' },
          },
        },
        props: {
          scenario: mockScenario,
          showSubtitles: true,
        },
      })

      const subtitlesContainer = wrapper.find('.subtitles-container')
      expect(subtitlesContainer.exists()).toBe(true)
    })

    it('应该渲染字幕行', () => {
      wrapper = mount(ScenarioPlayer, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-slider': { template: '<div class="slider"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
            'el-switch': { template: '<input type="checkbox" />' },
            'el-card': { template: '<div><slot name="header" /><slot /></div>' },
            'el-form': { template: '<form><slot /></form>' },
            'el-form-item': { template: '<div><slot /></div>' },
            'el-tag': { template: '<span><slot /></span>' },
          },
        },
        props: {
          scenario: mockScenario,
          showSubtitles: true,
        },
      })

      const subtitleLines = wrapper.findAll('.subtitle-line')
      expect(subtitleLines.length).toBeGreaterThan(0)
    })
  })

  describe('表达式高亮功能', () => {
    it('应该显示高亮表达式区域', () => {
      wrapper = mount(ScenarioPlayer, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-slider': { template: '<div class="slider"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
            'el-switch': { template: '<input type="checkbox" />' },
            'el-card': { template: '<div><slot name="header" /><slot /></div>' },
            'el-form': { template: '<form><slot /></form>' },
            'el-form-item': { template: '<div><slot /></div>' },
            'el-tag': { template: '<span><slot /></span>' },
          },
        },
        props: {
          scenario: mockScenario,
        },
      })

      const expressionsHighlight = wrapper.find('.expressions-highlight')
      expect(expressionsHighlight.exists()).toBe(true)
    })

    it('应该显示表达式标签', () => {
      wrapper = mount(ScenarioPlayer, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-slider': { template: '<div class="slider"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
            'el-switch': { template: '<input type="checkbox" />' },
            'el-card': { template: '<div><slot name="header" /><slot /></div>' },
            'el-form': { template: '<form><slot /></form>' },
            'el-form-item': { template: '<div><slot /></div>' },
            'el-tag': { template: '<span><slot /></span>' },
          },
        },
        props: {
          scenario: mockScenario,
        },
      })

      const expressionTags = wrapper.findAll('.expression-tag')
      expect(expressionTags.length).toBeGreaterThan(0)
    })
  })

  describe('计算属性', () => {
    it('currentSubtitles应该返回正确的字幕列表', () => {
      wrapper = mount(ScenarioPlayer, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-slider': { template: '<div class="slider"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
            'el-switch': { template: '<input type="checkbox" />' },
            'el-card': { template: '<div><slot name="header" /><slot /></div>' },
            'el-form': { template: '<form><slot /></form>' },
            'el-form-item': { template: '<div><slot /></div>' },
            'el-tag': { template: '<span><slot /></span>' },
          },
        },
        props: {
          scenario: mockScenario,
        },
      })

      expect(wrapper.vm.currentSubtitles).toEqual(mockScenario.subtitles)
    })

    it('highlightedExpressions应该返回正确的表达式列表', () => {
      wrapper = mount(ScenarioPlayer, {
        global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })],
          stubs: {
            'el-button': { template: '<button><slot /></button>' },
            'el-icon': { template: '<span><slot /></span>' },
            'el-slider': { template: '<div class="slider"></div>' },
            'el-button-group': { template: '<div><slot /></div>' },
            'el-switch': { template: '<input type="checkbox" />' },
            'el-card': { template: '<div><slot name="header" /><slot /></div>' },
            'el-form': { template: '<form><slot /></form>' },
            'el-form-item': { template: '<div><slot /></div>' },
            'el-tag': { template: '<span><slot /></span>' },
          },
        },
        props: {
          scenario: mockScenario,
        },
      })

      expect(wrapper.vm.highlightedExpressions).toEqual(mockScenario.expressions)
    })
  })
})
