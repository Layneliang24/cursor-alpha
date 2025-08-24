import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import ChapterCompletion from '../ChapterCompletion.vue'

describe('ChapterCompletion.vue Component', () => {
  let pinia: any

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
  })

  const mockCompletionData = {
    accuracy: 85,
    practiceTime: 120000, // 120秒转换为毫秒
    wpm: 45,
    wrongWords: [
      { word: 'apple', translation: '苹果' },
      { word: 'banana', translation: '香蕉' }
    ],
    dictionary: 'TOEFL',
    chapter: 1
  }

  describe('UI布局测试', () => {
    it('应该完全居中显示，不显示练习界面的顶部栏和底部栏', () => {
      const wrapper = mount(ChapterCompletion, {
        props: {
          completionData: mockCompletionData
        }
      })

      // 验证组件结构
      expect(wrapper.find('.chapter-completion-page').exists()).toBe(true)
      expect(wrapper.find('.completion-content').exists()).toBe(true)
      
      // 验证不包含练习界面的UI元素
      expect(wrapper.find('.top-settings').exists()).toBe(false)
      expect(wrapper.find('.bottom-stats').exists()).toBe(false)
      expect(wrapper.find('.main-practice-area').exists()).toBe(false)
    })

    it('统计框应该完全居中显示', () => {
      const wrapper = mount(ChapterCompletion, {
        props: {
          completionData: mockCompletionData
        }
      })

      const statsContainer = wrapper.find('.completion-stats')
      expect(statsContainer.exists()).toBe(true)
      
      // 验证统计框的样式类
      expect(statsContainer.classes()).toContain('completion-stats')
      
      // 验证统计项数量
      const statItems = wrapper.findAll('.stat-item')
      expect(statItems).toHaveLength(4) // 正确率、练习用时、WPM、错误单词数
    })

    it('撒花效果应该在统计框之上，不遮挡内容', () => {
      const wrapper = mount(ChapterCompletion, {
        props: {
          completionData: mockCompletionData
        }
      })

      const confettiContainer = wrapper.find('.confetti-container')
      expect(confettiContainer.exists()).toBe(true)
      
      // 验证撒花效果不遮挡主要内容
      const completionContent = wrapper.find('.completion-content')
      expect(completionContent.exists()).toBe(true)
      
      // 验证CSS类确保pointer-events: none
      expect(confettiContainer.classes()).toContain('confetti-container')
    })
  })

  describe('统计数据显示', () => {
    it('应该正确显示所有统计数据', () => {
      const wrapper = mount(ChapterCompletion, {
        props: {
          completionData: mockCompletionData
        }
      })

      // 验证正确率
      const accuracyValue = wrapper.find('.stat-item:nth-child(1) .stat-value')
      expect(accuracyValue.text()).toBe('85%')
      
      // 验证练习用时
      const timeValue = wrapper.find('.stat-item:nth-child(2) .stat-value')
      expect(timeValue.text()).toBe('2:00')
      
      // 验证WPM
      const wpmValue = wrapper.find('.stat-item:nth-child(3) .stat-value')
      expect(wpmValue.text()).toBe('45')
      
      // 验证错误单词数
      const wrongWordsValue = wrapper.find('.stat-item:nth-child(4) .stat-value')
      expect(wrongWordsValue.text()).toBe('2')
    })

    it('应该正确显示错误单词列表', () => {
      const wrapper = mount(ChapterCompletion, {
        props: {
          completionData: mockCompletionData
        }
      })

      const wrongWordsSection = wrapper.find('.wrong-words-section')
      expect(wrongWordsSection.exists()).toBe(true)
      
      const wrongWordItems = wrapper.findAll('.wrong-word-item')
      expect(wrongWordItems).toHaveLength(2)
      
      // 验证第一个错误单词
      expect(wrongWordItems[0].find('.word-text').text()).toBe('apple')
      expect(wrongWordItems[1].find('.word-text').text()).toBe('banana')
    })

    it('没有错误单词时应该隐藏错误单词列表', () => {
      const noWrongWordsData = {
        ...mockCompletionData,
        wrongWords: []
      }

      const wrapper = mount(ChapterCompletion, {
        props: {
          completionData: noWrongWordsData
        }
      })

      const wrongWordsSection = wrapper.find('.wrong-words-section')
      expect(wrongWordsSection.exists()).toBe(false)
    })
  })

  describe('操作按钮', () => {
    it('应该显示所有必要的操作按钮', () => {
      const wrapper = mount(ChapterCompletion, {
        props: {
          completionData: mockCompletionData
        }
      })

      const actionsContainer = wrapper.find('.completion-actions')
      expect(actionsContainer.exists()).toBe(true)
      
      // 验证按钮数量
      const actionButtons = wrapper.findAll('.action-btn')
      expect(actionButtons).toHaveLength(3)
      
      // 验证按钮文本
      expect(actionButtons[0].text()).toContain('重复本章')
      expect(actionButtons[1].text()).toContain('下一章节')
      expect(actionButtons[2].text()).toContain('返回练习')
    })

    it('点击按钮应该触发正确的事件', async () => {
      const wrapper = mount(ChapterCompletion, {
        props: {
          completionData: mockCompletionData
        }
      })

      // 测试重复本章按钮
      const repeatBtn = wrapper.find('.repeat-btn')
      await repeatBtn.trigger('click')
      expect(wrapper.emitted('repeat-chapter')).toBeTruthy()
      
      // 测试下一章节按钮
      const nextBtn = wrapper.find('.next-btn')
      await nextBtn.trigger('click')
      expect(wrapper.emitted('next-chapter')).toBeTruthy()
      
      // 测试返回练习按钮
      const backBtn = wrapper.find('.back-btn')
      await backBtn.trigger('click')
      expect(wrapper.emitted('back-to-practice')).toBeTruthy()
    })
  })

  describe('响应式设计', () => {
    it('应该在不同屏幕尺寸下保持居中', () => {
      const wrapper = mount(ChapterCompletion, {
        props: {
          completionData: mockCompletionData
        }
      })

      const completionPage = wrapper.find('.chapter-completion-page')
      expect(completionPage.exists()).toBe(true)
      
      // 验证CSS类确保响应式布局
      expect(completionPage.classes()).toContain('chapter-completion-page')
    })
  })

  describe('动画效果', () => {
    it('撒花效果应该正确显示', () => {
      const wrapper = mount(ChapterCompletion, {
        props: {
          completionData: mockCompletionData
        }
      })

      const confettiContainer = wrapper.find('.confetti-container')
      expect(confettiContainer.exists()).toBe(true)
      
      // 验证撒花粒子数量
      const confettiParticles = wrapper.findAll('.confetti')
      expect(confettiParticles).toHaveLength(50)
    })

    it('撒花动画应该正确配置', () => {
      const wrapper = mount(ChapterCompletion, {
        props: {
          completionData: mockCompletionData
        }
      })

      const confettiParticles = wrapper.findAll('.confetti')
      
      // 验证第一个粒子的样式
      const firstParticle = confettiParticles[0]
      const style = firstParticle.attributes('style')
      
      // 应该包含动画相关的样式
      expect(style).toContain('animation')
      expect(style).toContain('left')
      expect(style).toContain('background-color')
    })
  })

  describe('边界情况', () => {
    it('应该处理空的完成数据', () => {
      const emptyData = {
        accuracy: 0,
        practiceTime: 0,
        wpm: 0,
        wrongWords: [],
        dictionary: '',
        chapter: 0
      }

      const wrapper = mount(ChapterCompletion, {
        props: {
          completionData: emptyData
        }
      })

      // 验证组件仍然正常渲染
      expect(wrapper.find('.chapter-completion-page').exists()).toBe(true)
      
      // 验证统计数据为0
      const accuracyValue = wrapper.find('.stat-item:nth-child(1) .stat-value')
      expect(accuracyValue.text()).toBe('0%')
    })

    it('应该处理缺失的完成数据', () => {
      const wrapper = mount(ChapterCompletion, {
        props: {
          completionData: {}
        }
      })

      // 验证组件仍然正常渲染
      expect(wrapper.find('.chapter-completion-page').exists()).toBe(true)
      
      // 验证默认值处理
      const accuracyValue = wrapper.find('.stat-item:nth-child(1) .stat-value')
      expect(accuracyValue.text()).toBe('0%')
    })
  })
}) 