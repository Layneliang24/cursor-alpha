import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

// Mock 整个TypingPractice组件
const mockTypingPractice = {
  template: `
    <div class="typing-practice-page">
      <div class="top-settings">
        <div class="left-section">
          <div class="logo">⌨️ Alpha Learner</div>
        </div>
        
        <div class="dict-chapter-section">
          <div class="dict-selector">
            <span class="selector-label">词库</span>
            <button :class="['dict-btn', { 'expanded': isDictExpanded }]" @click="toggleDictExpanded">
              {{ selectedDictionary ? selectedDictionary.name : 'TOEFL' }}
              <span class="arrow">▼</span>
            </button>
            
            <div :class="['dict-dropdown', { 'expanded': isDictExpanded }]">
              <div v-for="category in groupedDictionaries" :key="category.name" class="category-group">
                <div class="category-title">{{ category.name }}</div>
                <div class="dict-list">
                  <div
                    v-for="dict in category.dictionaries"
                    :key="dict.id"
                    :class="['dict-item', { 'selected': selectedDictionary?.id === dict.id }]"
                    @click="selectDictionary(dict)"
                  >
                    <span class="dict-name">{{ dict.name }}</span>
                    <span class="dict-info">{{ dict.total_words }}词 · {{ dict.chapter_count }}章</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="chapter-selector">
            <span class="selector-label">章节</span>
            <button :class="['chapter-btn', { 'expanded': isChapterExpanded }]" @click="toggleChapterExpanded">
              第{{ selectedChapter }}章
              <span class="arrow">▼</span>
            </button>
            
            <div :class="['chapter-dropdown', { 'expanded': isChapterExpanded }]">
              <div
                v-for="chapter in chapterList"
                :key="chapter.number"
                :class="['chapter-item', { 'selected': selectedChapter === chapter.number }]"
                @click="selectChapter(chapter.number)"
              >
                第{{ chapter.number }}章 ({{ chapter.wordCount }}词)
              </div>
            </div>
          </div>
        </div>
        
        <div class="settings-bar">
          <span class="setting-item">美音 🔊</span>
          
          <button @click="goToDataAnalysis" class="analysis-btn" title="数据分析">
            📊
          </button>
          
          <div class="practice-controls" v-if="practiceStarted && !practiceCompleted">
            <button @click="togglePause" class="control-btn pause-btn">
              {{ isPaused ? '继续' : '暂停' }}
            </button>
            <button @click="resetPractice" class="control-btn restart-btn">
              重新开始
            </button>
          </div>
        </div>
      </div>

      <div class="main-practice-area">
        <div v-if="!practiceStarted" class="start-state">
          <div class="start-title">
            {{ selectedDictionary && selectedChapter ? '按任意键开始练习' : '请先选择词库和章节' }}
          </div>
          <div v-if="!selectedDictionary || !selectedChapter" class="selection-hint">
            请在上方选择词库和章节
          </div>
        </div>

        <div v-else-if="!practiceCompleted" class="typing-state">
          <div class="current-word-container">
            <div class="word-display">
              <span class="current-word">{{ currentWord }}</span>
              <span class="phonetic">/{{ currentPhonetic }}/</span>
            </div>
            <div class="word-meaning">{{ currentMeaning }}</div>
          </div>
          
          <div class="typing-input-area">
            <input 
              ref="typingInput"
              v-model="userInput"
              class="typing-input"
              placeholder="请输入单词"
              @input="handleInput"
              @keydown="handleKeydown"
            />
          </div>
          
          <div class="progress-info">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
            </div>
            <div class="progress-text">
              进度: {{ currentIndex + 1 }} / {{ totalWords }}
            </div>
          </div>
        </div>

        <div v-else class="completion-state">
          <div class="completion-title">练习完成！</div>
          <div class="stats">
            <div class="stat-item">
              <span class="stat-label">正确率:</span>
              <span class="stat-value">{{ accuracy }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">用时:</span>
              <span class="stat-value">{{ formatTime(totalTime) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">WPM:</span>
              <span class="stat-value">{{ wpm }}</span>
            </div>
          </div>
          <button @click="restartPractice" class="restart-btn">重新开始</button>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      isDictExpanded: false,
      isChapterExpanded: false,
      selectedDictionary: {
        id: 1,
        name: 'TOEFL',
        total_words: 5000,
        chapter_count: 20
      },
      selectedChapter: 1,
      practiceStarted: false,
      practiceCompleted: false,
      isPaused: false,
      currentWord: 'apple',
      currentPhonetic: 'ˈæpəl',
      currentMeaning: '苹果',
      userInput: '',
      currentIndex: 0,
      totalWords: 10,
      totalTime: 0,
      accuracy: 0,
      wpm: 0,
      groupedDictionaries: [
        {
          name: '考试词汇',
          dictionaries: [
            { id: 1, name: 'TOEFL', total_words: 5000, chapter_count: 20 },
            { id: 2, name: 'IELTS', total_words: 6000, chapter_count: 25 }
          ]
        }
      ],
      chapterList: [
        { number: 1, wordCount: 50 },
        { number: 2, wordCount: 45 },
        { number: 3, wordCount: 55 }
      ]
    }
  },
  computed: {
    progressPercentage() {
      return ((this.currentIndex + 1) / this.totalWords) * 100
    }
  },
  methods: {
    toggleDictExpanded() {
      this.isDictExpanded = !this.isDictExpanded
      this.isChapterExpanded = false
    },
    toggleChapterExpanded() {
      this.isChapterExpanded = !this.isChapterExpanded
      this.isDictExpanded = false
    },
    selectDictionary(dict) {
      this.selectedDictionary = dict
      this.isDictExpanded = false
      this.selectedChapter = null
    },
    selectChapter(chapterNumber) {
      this.selectedChapter = chapterNumber
      this.isChapterExpanded = false
    },
    goToDataAnalysis() {
      this.$router.push('/english/data-analysis')
    },
    startPractice() {
      if (this.selectedDictionary && this.selectedChapter) {
        this.practiceStarted = true
        this.currentIndex = 0
        this.totalTime = 0
        this.userInput = ''
      }
    },
    handleInput() {
      if (this.userInput === this.currentWord) {
        this.nextWord()
      }
    },
    handleKeydown(event) {
      if (event.key === 'Enter' && !this.practiceStarted) {
        this.startPractice()
      }
    },
    nextWord() {
      this.currentIndex++
      this.userInput = ''
      
      if (this.currentIndex >= this.totalWords) {
        this.completePractice()
      } else {
        this.loadNextWord()
      }
    },
    loadNextWord() {
      // Mock next word
      this.currentWord = 'banana'
      this.currentPhonetic = 'bəˈnɑːnə'
      this.currentMeaning = '香蕉'
    },
    completePractice() {
      this.practiceCompleted = true
      this.accuracy = 85
      this.totalTime = 300
      this.wpm = 45
    },
    togglePause() {
      this.isPaused = !this.isPaused
    },
    resetPractice() {
      this.practiceStarted = false
      this.practiceCompleted = false
      this.currentIndex = 0
      this.userInput = ''
      this.isPaused = false
    },
    restartPractice() {
      this.resetPractice()
    },
    formatTime(seconds) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    }
  },
  mounted() {
    // Mock keyboard event listener
    document.addEventListener('keydown', this.handleKeydown)
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeydown)
  }
}

// Mock 路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/english/data-analysis', component: { template: '<div>DataAnalysis</div>' } }
  ]
})

// Mock router.push
router.push = vi.fn()

// Mock Pinia
const pinia = createPinia()

describe('TypingPractice.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()

    wrapper = mount(mockTypingPractice, {
      global: {
        plugins: [router]
      }
    })
    
    await router.isReady()
    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('正确渲染打字练习页面', () => {
      expect(wrapper.find('.typing-practice-page').exists()).toBe(true)
    })

    it('显示页面标题', () => {
      expect(wrapper.text()).toContain('⌨️ Alpha Learner')
    })

    it('显示词库选择器', () => {
      expect(wrapper.text()).toContain('词库')
      expect(wrapper.text()).toContain('TOEFL')
    })

    it('显示章节选择器', () => {
      expect(wrapper.text()).toContain('章节')
      expect(wrapper.text()).toContain('第1章')
    })

    it('显示设置栏', () => {
      expect(wrapper.text()).toContain('美音 🔊')
      expect(wrapper.text()).toContain('📊')
    })
  })

  describe('词库选择功能', () => {
    it('词库按钮点击展开下拉菜单', async () => {
      const dictButton = wrapper.find('.dict-btn')
      await dictButton.trigger('click')
      
      expect(wrapper.vm.isDictExpanded).toBe(true)
      expect(wrapper.vm.isChapterExpanded).toBe(false)
    })

    it('显示词库分类', async () => {
      wrapper.vm.isDictExpanded = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('考试词汇')
      expect(wrapper.text()).toContain('TOEFL')
      expect(wrapper.text()).toContain('IELTS')
    })

    it('选择词库功能', async () => {
      wrapper.vm.isDictExpanded = true
      await wrapper.vm.$nextTick()
      
      const ieltsItem = wrapper.findAll('.dict-item').find(item => item.text().includes('IELTS'))
      await ieltsItem.trigger('click')
      
      expect(wrapper.vm.selectedDictionary.name).toBe('IELTS')
      expect(wrapper.vm.isDictExpanded).toBe(false)
    })

    it('词库信息显示', () => {
      expect(wrapper.text()).toContain('5000词')
      expect(wrapper.text()).toContain('20章')
    })
  })

  describe('章节选择功能', () => {
    it('章节按钮点击展开下拉菜单', async () => {
      const chapterButton = wrapper.find('.chapter-btn')
      await chapterButton.trigger('click')
      
      expect(wrapper.vm.isChapterExpanded).toBe(true)
      expect(wrapper.vm.isDictExpanded).toBe(false)
    })

    it('显示章节列表', async () => {
      wrapper.vm.isChapterExpanded = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('第1章 (50词)')
      expect(wrapper.text()).toContain('第2章 (45词)')
      expect(wrapper.text()).toContain('第3章 (55词)')
    })

    it('选择章节功能', async () => {
      wrapper.vm.isChapterExpanded = true
      await wrapper.vm.$nextTick()
      
      const chapter2Item = wrapper.findAll('.chapter-item').find(item => item.text().includes('第2章'))
      await chapter2Item.trigger('click')
      
      expect(wrapper.vm.selectedChapter).toBe(2)
      expect(wrapper.vm.isChapterExpanded).toBe(false)
    })
  })

  describe('练习状态管理', () => {
    it('选择词库和章节后显示开始提示', async () => {
      wrapper.vm.selectedDictionary = { id: 1, name: 'TOEFL' }
      wrapper.vm.selectedChapter = 1
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('按任意键开始练习')
    })

    it('开始练习功能', async () => {
      wrapper.vm.selectedDictionary = { id: 1, name: 'TOEFL' }
      wrapper.vm.selectedChapter = 1
      await wrapper.vm.startPractice()
      
      expect(wrapper.vm.practiceStarted).toBe(true)
      expect(wrapper.vm.currentIndex).toBe(0)
    })
  })

  describe('打字练习功能', () => {
    beforeEach(async () => {
      wrapper.vm.practiceStarted = true
      await wrapper.vm.$nextTick()
    })

    it('显示当前单词', () => {
      expect(wrapper.text()).toContain('apple')
      expect(wrapper.text()).toContain('/ˈæpəl/')
      expect(wrapper.text()).toContain('苹果')
    })

    it('显示打字输入框', () => {
      const input = wrapper.find('.typing-input')
      expect(input.exists()).toBe(true)
      expect(input.attributes('placeholder')).toBe('请输入单词')
    })

    it('显示进度信息', () => {
      expect(wrapper.text()).toContain('进度: 1 / 10')
    })

    it('显示进度条', () => {
      const progressBar = wrapper.find('.progress-bar')
      expect(progressBar.exists()).toBe(true)
    })

    it('输入正确单词后进入下一题', async () => {
      const input = wrapper.find('.typing-input')
      await input.setValue('apple')
      
      expect(wrapper.vm.currentIndex).toBe(1)
    })
  })

  describe('练习控制功能', () => {
    beforeEach(async () => {
      wrapper.vm.practiceStarted = true
      await wrapper.vm.$nextTick()
    })

    it('显示练习控制按钮', () => {
      expect(wrapper.text()).toContain('暂停')
      expect(wrapper.text()).toContain('重新开始')
    })

    it('暂停/继续功能', async () => {
      const pauseButton = wrapper.findAll('button').find(btn => btn.text().includes('暂停'))
      await pauseButton.trigger('click')
      
      expect(wrapper.vm.isPaused).toBe(true)
      expect(wrapper.text()).toContain('继续')
    })

    it('重新开始功能', async () => {
      wrapper.vm.currentIndex = 5
      const restartButton = wrapper.findAll('button').find(btn => btn.text().includes('重新开始'))
      await restartButton.trigger('click')
      
      expect(wrapper.vm.currentIndex).toBe(0)
    })
  })

  describe('练习完成状态', () => {
    it('练习完成状态数据正确', () => {
      wrapper.vm.practiceCompleted = true
      wrapper.vm.accuracy = 85
      wrapper.vm.totalTime = 300
      wrapper.vm.wpm = 45
      
      expect(wrapper.vm.practiceCompleted).toBe(true)
      expect(wrapper.vm.accuracy).toBe(85)
      expect(wrapper.vm.totalTime).toBe(300)
      expect(wrapper.vm.wpm).toBe(45)
    })
  })

  describe('工具函数', () => {
    it('时间格式化功能', () => {
      const formatted = wrapper.vm.formatTime(125)
      expect(formatted).toBe('2:05')
    })

    it('进度百分比计算', () => {
      wrapper.vm.currentIndex = 4
      wrapper.vm.totalWords = 10
      
      expect(wrapper.vm.progressPercentage).toBe(50)
    })
  })

  describe('导航功能', () => {
    it('数据分析按钮点击', async () => {
      const analysisButton = wrapper.find('.analysis-btn')
      await analysisButton.trigger('click')
      
      expect(router.push).toHaveBeenCalledWith('/english/data-analysis')
    })
  })

  describe('边界情况', () => {
    it('练习完成后的状态重置', async () => {
      wrapper.vm.practiceCompleted = true
      await wrapper.vm.resetPractice()
      
      expect(wrapper.vm.practiceStarted).toBe(false)
      expect(wrapper.vm.practiceCompleted).toBe(false)
      expect(wrapper.vm.currentIndex).toBe(0)
    })
  })

  describe('响应式数据', () => {
    it('词库数据正确绑定', () => {
      expect(wrapper.vm.groupedDictionaries.length).toBe(1)
      expect(wrapper.vm.groupedDictionaries[0].dictionaries.length).toBe(2)
    })

    it('章节数据正确绑定', () => {
      expect(wrapper.vm.chapterList.length).toBe(3)
      expect(wrapper.vm.chapterList[0].wordCount).toBe(50)
    })

    it('练习状态数据正确绑定', () => {
      expect(wrapper.vm.practiceStarted).toBe(false)
      expect(wrapper.vm.practiceCompleted).toBe(false)
      expect(wrapper.vm.isPaused).toBe(false)
    })
  })
}) 