import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import ScenarioPlayer from '@/components/idiomatic-expressions/ScenarioPlayer.vue'
import { commonMountOptions, testUtils } from '../../setup.js'

// Mock Element Plus message
vi.mock('element-plus', () => ({
  ElMessage: {
    error: vi.fn(),
  },
}))

// Mock HTML Audio API
class MockAudio {
  constructor (src) {
    this.src = src
    this.currentTime = 0
    this.duration = 120 // 2 minutes
    this.volume = 0.8
    this.playbackRate = 1
    this.paused = true
    this.muted = false
    this.addEventListener = vi.fn()
    this.removeEventListener = vi.fn()
    this.play = vi.fn().mockResolvedValue(undefined)
    this.pause = vi.fn()
    this.load = vi.fn()
    
    // 模拟事件监听器存储
    this.eventListeners = {}
  }
  
  addEventListener (event, handler) {
    if (!this.eventListeners[event]) {
      this.eventListeners[event] = []
    }
    this.eventListeners[event].push(handler)
  }
  
  removeEventListener (event, handler) {
    if (this.eventListeners[event]) {
      const index = this.eventListeners[event].indexOf(handler)
      if (index > -1) {
        this.eventListeners[event].splice(index, 1)
      }
    }
  }
  
  dispatchEvent (event) {
    const eventType = event.type || event
    if (this.eventListeners[eventType]) {
      this.eventListeners[eventType].forEach(handler => handler(event))
    }
  }
}

global.Audio = MockAudio

describe('ScenarioPlayer', () => {
  let wrapper
  
  // Mock scenario data
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
      {
        startTime: 3,
        endTime: 6,
        text: "How's the weather today?",
        translation: '今天天气怎么样？',
        isExpression: false,
      },
      {
        startTime: 6,
        endTime: 10,
        text: "It's raining cats and dogs outside.",
        translation: '外面下着倾盆大雨。',
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
      {
        id: 2,
        expression: 'raining cats and dogs',
        startTime: 6,
        endTime: 10,
      },
    ],
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('基础渲染', () => {
    beforeEach(() => {
      wrapper = mount(ScenarioPlayer, {
        ...commonMountOptions,
        props: {
          scenario: mockScenario,
        },
      })
    })

    it('应该正确渲染情景播放器', () => {
      expect(wrapper.find('.scenario-player').exists()).toBe(true)
      expect(wrapper.find('.player-header').exists()).toBe(true)
      expect(wrapper.find('.audio-player').exists()).toBe(true)
    })

    it('应该显示情景标题和描述', () => {
      const title = wrapper.find('.scenario-title')
      const description = wrapper.find('.scenario-description')
      
      expect(title.text()).toBe('商务会议场景')
      expect(description.text()).toBe('学习商务会议中常用的地道表达')
    })

    it('应该显示音频控制按钮', () => {
      const playButton = wrapper.find('.audio-controls button')
      expect(playButton.exists()).toBe(true)
    })

    it('应该显示时间显示器', () => {
      const timeDisplay = wrapper.find('.time-display')
      expect(timeDisplay.exists()).toBe(true)
      expect(timeDisplay.text()).toContain('00:00')
    })

    it('应该显示进度条', () => {
      const progressSlider = wrapper.findComponent({ name: 'ElSlider' })
      expect(progressSlider.exists()).toBe(true)
    })

    it('应该显示播放速度控制按钮', () => {
      const speedButtons = wrapper.findAll('.playback-controls button')
      expect(speedButtons.length).toBeGreaterThan(0)
      expect(speedButtons[0].text()).toBe('0.5x')
      expect(speedButtons[4].text()).toBe('1.5x')
    })
  })

  describe('音频控制功能', () => {
    beforeEach(() => {
      wrapper = mount(ScenarioPlayer, {
        ...commonMountOptions,
        props: {
          scenario: mockScenario,
        },
      })
    })

    it('初始状态应该是暂停的', () => {
      expect(wrapper.vm.isPlaying).toBe(false)
    })

    it('点击播放按钮应该开始播放', async () => {
      const playButton = wrapper.find('.audio-controls button')
      await playButton.trigger('click')
      
      expect(wrapper.vm.audio.play).toHaveBeenCalled()
    })

    it('播放时再次点击应该暂停', async () => {
      wrapper.vm.isPlaying = true
      await testUtils.nextTick()
      
      const playButton = wrapper.find('.audio-controls button')
      await playButton.trigger('click')
      
      expect(wrapper.vm.audio.pause).toHaveBeenCalled()
    })

    it('应该正确格式化时间', () => {
      expect(wrapper.vm.formatTime(0)).toBe('00:00')
      expect(wrapper.vm.formatTime(65)).toBe('01:05')
      expect(wrapper.vm.formatTime(3661)).toBe('61:01')
    })

    it('切换静音状态应该更新音频', async () => {
      const muteButton = wrapper.findAll('.audio-controls button')[1]
      await muteButton.trigger('click')
      
      expect(wrapper.vm.isMuted).toBe(true)
      expect(wrapper.vm.audio.muted).toBe(true)
    })

    it('改变播放速度应该更新音频播放速度', async () => {
      const speedButton = wrapper.find('button:contains("1.5x")')
      await speedButton.trigger('click')
      
      expect(wrapper.vm.playbackSpeed).toBe(1.5)
      expect(wrapper.vm.audio.playbackRate).toBe(1.5)
    })

    it('调整进度条应该改变播放位置', async () => {
      const progressSlider = wrapper.findComponent({ name: 'ElSlider' })
      
      await progressSlider.vm.$emit('change', 50)
      
      expect(wrapper.vm.audio.currentTime).toBe(60) // 50% of 120 seconds
    })
  })

  describe('字幕功能', () => {
    beforeEach(() => {
      wrapper = mount(ScenarioPlayer, {
        ...commonMountOptions,
        props: {
          scenario: mockScenario,
          showSubtitles: true,
        },
      })
    })

    it('应该显示字幕容器', () => {
      const subtitlesContainer = wrapper.find('.subtitles-container')
      expect(subtitlesContainer.exists()).toBe(true)
    })

    it('应该渲染所有字幕行', () => {
      const subtitleLines = wrapper.findAll('.subtitle-line')
      expect(subtitleLines).toHaveLength(3)
    })

    it('应该显示字幕文本', () => {
      const firstSubtitle = wrapper.findAll('.subtitle-line')[0]
      expect(firstSubtitle.find('.subtitle-text').text()).toBe("Let's break the ice with some small talk.")
    })

    it('显示翻译时应该显示翻译文本', () => {
      const firstSubtitle = wrapper.findAll('.subtitle-line')[0]
      const translation = firstSubtitle.find('.subtitle-translation')
      expect(translation.exists()).toBe(true)
      expect(translation.text()).toBe('让我们先闲聊几句来打破沉默。')
    })

    it('表达式字幕应该有高亮样式', () => {
      const firstSubtitle = wrapper.findAll('.subtitle-line')[0]
      expect(firstSubtitle.classes()).toContain('highlight')
    })

    it('当前时间在字幕时间范围内时应该激活字幕', async () => {
      wrapper.vm.currentTime = 1.5 // 在第一个字幕时间范围内
      await testUtils.nextTick()
      
      const firstSubtitle = wrapper.findAll('.subtitle-line')[0]
      expect(firstSubtitle.classes()).toContain('active')
    })

    it('点击字幕应该跳转到对应时间', async () => {
      const firstSubtitle = wrapper.findAll('.subtitle-line')[0]
      await firstSubtitle.trigger('click')
      
      expect(wrapper.vm.audio.currentTime).toBe(0)
    })

    it('应该能切换翻译显示', async () => {
      const translationSwitch = wrapper.find('input[role="switch"]')
      await translationSwitch.setChecked(false)
      
      expect(wrapper.vm.showTranslation).toBe(false)
    })
  })

  describe('表达式高亮功能', () => {
    beforeEach(() => {
      wrapper = mount(ScenarioPlayer, {
        ...commonMountOptions,
        props: {
          scenario: mockScenario,
        },
      })
    })

    it('应该显示高亮表达式区域', () => {
      const expressionsHighlight = wrapper.find('.expressions-highlight')
      expect(expressionsHighlight.exists()).toBe(true)
    })

    it('应该显示表达式标签', () => {
      const expressionTags = wrapper.findAll('.expression-tag')
      expect(expressionTags).toHaveLength(2)
      expect(expressionTags[0].text()).toBe('break the ice')
      expect(expressionTags[1].text()).toBe('raining cats and dogs')
    })

    it('点击表达式标签应该发出事件', async () => {
      const firstTag = wrapper.findAll('.expression-tag')[0]
      await firstTag.trigger('click')
      
      expect(wrapper.emitted('expressionClick')).toBeTruthy()
      expect(wrapper.emitted('expressionClick')[0][0]).toEqual(mockScenario.expressions[0])
    })

    it('点击表达式标签应该跳转到对应时间', async () => {
      const firstTag = wrapper.findAll('.expression-tag')[0]
      await firstTag.trigger('click')
      
      expect(wrapper.vm.audio.currentTime).toBe(0) // 表达式开始时间
    })
  })

  describe('播放器设置', () => {
    beforeEach(() => {
      wrapper = mount(ScenarioPlayer, {
        ...commonMountOptions,
        props: {
          scenario: mockScenario,
        },
      })
    })

    it('初始状态设置面板应该隐藏', () => {
      expect(wrapper.vm.showSettings).toBe(false)
    })

    it('点击设置按钮应该显示/隐藏设置面板', async () => {
      const settingsButton = wrapper.find('.settings-toggle button')
      await settingsButton.trigger('click')
      
      expect(wrapper.vm.showSettings).toBe(true)
      
      await settingsButton.trigger('click')
      expect(wrapper.vm.showSettings).toBe(false)
    })

    it('应该能调整音量', async () => {
      wrapper.vm.showSettings = true
      await testUtils.nextTick()
      
      const volumeSlider = wrapper.find('.player-settings').findComponent({ name: 'ElSlider' })
      await volumeSlider.vm.$emit('change', 50)
      
      expect(wrapper.vm.volume).toBe(50)
      expect(wrapper.vm.audio.volume).toBe(0.5)
    })

    it('应该能切换自动播放', async () => {
      wrapper.vm.showSettings = true
      await testUtils.nextTick()
      
      const autoPlaySwitch = wrapper.find('.player-settings').findAll('input[role="switch"]')[1]
      await autoPlaySwitch.setChecked(true)
      
      expect(wrapper.vm.autoPlay).toBe(true)
    })

    it('应该能切换循环播放', async () => {
      wrapper.vm.showSettings = true
      await testUtils.nextTick()
      
      const loopSwitch = wrapper.find('.player-settings').findAll('input[role="switch"]')[2]
      await loopSwitch.setChecked(true)
      
      expect(wrapper.vm.loopPlay).toBe(true)
    })
  })

  describe('事件处理', () => {
    beforeEach(() => {
      wrapper = mount(ScenarioPlayer, {
        ...commonMountOptions,
        props: {
          scenario: mockScenario,
        },
      })
    })

    it('播放状态改变时应该发出事件', async () => {
      await wrapper.vm.togglePlay()
      
      expect(wrapper.emitted('playStateChange')).toBeTruthy()
      expect(wrapper.emitted('playStateChange')[0]).toEqual([true])
    })

    it('进度更新时应该发出事件', async () => {
      // 模拟时间更新
      wrapper.vm.audio.currentTime = 30
      wrapper.vm.audio.dispatchEvent({ type: 'timeupdate' })
      
      await testUtils.nextTick()
      
      expect(wrapper.emitted('progressUpdate')).toBeTruthy()
    })

    it('音频加载失败时应该显示错误消息', async () => {
      wrapper.vm.audio.dispatchEvent({ 
        type: 'error', 
        error: new Error('Network error'), 
      })
      
      expect(ElMessage.error).toHaveBeenCalledWith('音频加载失败，请检查网络连接')
    })

    it('音频播放结束时应该停止播放', async () => {
      wrapper.vm.isPlaying = true
      wrapper.vm.audio.dispatchEvent({ type: 'ended' })
      
      expect(wrapper.vm.isPlaying).toBe(false)
    })

    it('启用循环播放时音频结束后应该重新开始', async () => {
      wrapper.vm.isPlaying = true
      wrapper.vm.loopPlay = true
      
      wrapper.vm.audio.dispatchEvent({ type: 'ended' })
      
      expect(wrapper.vm.audio.currentTime).toBe(0)
      expect(wrapper.vm.audio.play).toHaveBeenCalled()
      expect(wrapper.vm.isPlaying).toBe(true)
    })
  })

  describe('生命周期', () => {
    it('组件挂载时应该初始化音频', () => {
      wrapper = mount(ScenarioPlayer, {
        ...commonMountOptions,
        props: {
          scenario: mockScenario,
        },
      })
      
      expect(wrapper.vm.audio).toBeInstanceOf(MockAudio)
      expect(wrapper.vm.audio.src).toBe(mockScenario.audio_url)
    })

    it('自动播放开启时音频准备好后应该开始播放', async () => {
      wrapper = mount(ScenarioPlayer, {
        ...commonMountOptions,
        props: {
          scenario: mockScenario,
          autoPlay: true,
        },
      })
      
      // 模拟音频准备好
      wrapper.vm.audio.dispatchEvent({ type: 'canplay' })
      
      expect(wrapper.vm.audio.play).toHaveBeenCalled()
    })

    it('组件卸载时应该清理音频资源', () => {
      wrapper = mount(ScenarioPlayer, {
        ...commonMountOptions,
        props: {
          scenario: mockScenario,
        },
      })
      
      const pauseSpy = vi.spyOn(wrapper.vm.audio, 'pause')
      
      wrapper.unmount()
      
      expect(pauseSpy).toHaveBeenCalled()
    })
  })

  describe('计算属性', () => {
    beforeEach(() => {
      wrapper = mount(ScenarioPlayer, {
        ...commonMountOptions,
        props: {
          scenario: mockScenario,
        },
      })
    })

    it('currentSubtitles应该返回正确的字幕列表', () => {
      expect(wrapper.vm.currentSubtitles).toEqual(mockScenario.subtitles)
    })

    it('highlightedExpressions应该返回正确的表达式列表', () => {
      expect(wrapper.vm.highlightedExpressions).toEqual(mockScenario.expressions)
    })

    it('activeSubtitle应该返回当前时间对应的字幕', async () => {
      wrapper.vm.currentTime = 1.5
      await testUtils.nextTick()
      
      expect(wrapper.vm.activeSubtitle).toEqual(mockScenario.subtitles[0])
    })

    it('当前时间不在任何字幕范围内时activeSubtitle应该为undefined', async () => {
      wrapper.vm.currentTime = 15
      await testUtils.nextTick()
      
      expect(wrapper.vm.activeSubtitle).toBeUndefined()
    })
  })

  describe('错误处理', () => {
    beforeEach(() => {
      wrapper = mount(ScenarioPlayer, {
        ...commonMountOptions,
        props: {
          scenario: { ...mockScenario, audio_url: undefined },
        },
      })
    })

    it('没有音频URL时不应该创建音频对象', () => {
      expect(wrapper.vm.audio).toBeNull()
    })

    it('音频播放失败时应该处理错误', async () => {
      wrapper = mount(ScenarioPlayer, {
        ...commonMountOptions,
        props: {
          scenario: mockScenario,
        },
      })
      
      wrapper.vm.audio.play.mockRejectedValueOnce(new Error('Play failed'))
      
      await wrapper.vm.togglePlay()
      
      expect(wrapper.vm.isPlaying).toBe(false)
    })
  })

  describe('Props响应', () => {
    it('showSubtitles prop变化时应该更新本地状态', async () => {
      wrapper = mount(ScenarioPlayer, {
        ...commonMountOptions,
        props: {
          scenario: mockScenario,
          showSubtitles: true,
        },
      })
      
      expect(wrapper.vm.showSubtitles).toBe(true)
      
      await wrapper.setProps({ showSubtitles: false })
      
      expect(wrapper.vm.showSubtitles).toBe(false)
    })

    it('showTranslation prop变化时应该更新本地状态', async () => {
      wrapper = mount(ScenarioPlayer, {
        ...commonMountOptions,
        props: {
          scenario: mockScenario,
          showTranslation: true,
        },
      })
      
      expect(wrapper.vm.showTranslation).toBe(true)
      
      await wrapper.setProps({ showTranslation: false })
      
      expect(wrapper.vm.showTranslation).toBe(false)
    })
  })
})
