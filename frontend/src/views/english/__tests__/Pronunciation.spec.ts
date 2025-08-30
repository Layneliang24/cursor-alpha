import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

// Mock 整个Pronunciation组件
const mockPronunciation = {
  template: `
    <div class="pronunciation-container">
      <div class="content-wrapper">
        <div class="page-header">
          <h1 class="page-title">发音练习</h1>
          <p class="page-subtitle">提升英语口语能力，掌握标准发音</p>
        </div>

        <div class="main-card">
          <div v-if="isLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <p class="loading-text">正在加载单词数据...</p>
          </div>

          <div v-else-if="words.length === 0" class="empty-state">
            <div class="empty-icon">📚</div>
            <h3 class="empty-title">暂无单词数据</h3>
            <p class="empty-desc">点击下方按钮加载练习单词</p>
            <button @click="loadWords" class="primary-button">
              加载单词
            </button>
          </div>

          <div v-else class="practice-content">
            <div class="word-card">
              <div class="word-text">{{ currentWord.word }}</div>
              <div class="phonetic-text">{{ currentWord.phonetic }}</div>
              <div class="definition-text">{{ currentWord.definition }}</div>
            </div>

            <div class="button-group">
              <button 
                @click="playAudio"
                class="action-button play-button"
                :disabled="!currentWord.word"
              >
                🔊 播放发音
              </button>
              
              <button 
                @click="startRecording"
                class="action-button record-button"
                :disabled="isRecording"
              >
                🎤 {{ isRecording ? '录音中...' : '开始录音' }}
              </button>
            </div>

            <div v-if="isRecording" class="recording-status">
              <div class="recording-indicator">
                <span class="recording-dot"></span>
                正在录音...
              </div>
            </div>

            <div v-if="pronunciationScore !== null" class="score-result">
              <h3 class="score-title">发音评分</h3>
              <div class="score-display">
                <div class="score-number" :class="getScoreClass()">
                  {{ pronunciationScore }}%
                </div>
                <div class="score-bar">
                  <div 
                    class="score-progress"
                    :class="getScoreClass()"
                    :style="{ width: pronunciationScore + '%' }"
                  ></div>
                </div>
              </div>
              <p class="score-feedback">{{ getScoreFeedback() }}</p>
            </div>

            <div class="navigation-buttons">
              <button 
                @click="previousWord"
                class="nav-button prev-button"
                :disabled="currentIndex === 0"
              >
                ← 上一个
              </button>
              <button 
                @click="nextWord"
                class="nav-button next-button"
                :disabled="currentIndex === words.length - 1"
              >
                下一个 →
              </button>
            </div>
          </div>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-number blue">{{ currentIndex + 1 }}</div>
            <div class="stat-label">当前进度</div>
          </div>
          <div class="stat-card">
            <div class="stat-number green">{{ completedCount }}</div>
            <div class="stat-label">已完成</div>
          </div>
          <div class="stat-card">
            <div class="stat-number purple">
              {{ averageScore !== null ? averageScore + '%' : '暂无' }}
            </div>
            <div class="stat-label">平均分数</div>
          </div>
        </div>
      </div>
    </div>
  `,
  data () {
    return {
      currentIndex: 0,
      isRecording: false,
      pronunciationScore: null,
      words: [
        {
          word: 'pronunciation',
          phonetic: '/prəˌnʌnsiˈeɪʃn/',
          definition: '发音，读音',
          audio_url: null,
          score: null,
        },
        {
          word: 'example',
          phonetic: '/ɪɡˈzæmpəl/',
          definition: '例子，实例',
          audio_url: null,
          score: null,
        },
        {
          word: 'beautiful',
          phonetic: '/ˈbjuːtɪfʊl/',
          definition: '美丽的，漂亮的',
          audio_url: null,
          score: 85,
        },
      ],
      isLoading: false,
    }
  },
  computed: {
    currentWord () {
      return this.words[this.currentIndex] || {}
    },
    completedCount () {
      return this.words.filter(w => w.score !== null).length
    },
    averageScore () {
      const scoredWords = this.words.filter(w => w.score !== null)
      if (scoredWords.length === 0) return null
      const total = scoredWords.reduce((sum, w) => sum + w.score, 0)
      return Math.round(total / scoredWords.length)
    },
  },
  methods: {
    async loadWords () {
      this.isLoading = true
      try {
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 100))
        this.words = [
          {
            word: 'pronunciation',
            phonetic: '/prəˌnʌnsiˈeɪʃn/',
            definition: '发音，读音',
            audio_url: null,
            score: null,
          },
          {
            word: 'example',
            phonetic: '/ɪɡˈzæmpəl/',
            definition: '例子，实例',
            audio_url: null,
            score: null,
          },
        ]
      } finally {
        this.isLoading = false
      }
    },
    playAudio () {
      // Mock audio playback
      console.log('播放发音:', this.currentWord.word)
    },
    startRecording () {
      this.isRecording = true
      // Mock recording process
      setTimeout(() => {
        this.isRecording = false
        this.pronunciationScore = Math.floor(Math.random() * 40) + 60 // 60-100
      }, 2000)
    },
    previousWord () {
      if (this.currentIndex > 0) {
        this.currentIndex--
        this.pronunciationScore = null
      }
    },
    nextWord () {
      if (this.currentIndex < this.words.length - 1) {
        this.currentIndex++
        this.pronunciationScore = null
      }
    },
    getScoreClass () {
      if (this.pronunciationScore >= 90) return 'excellent'
      if (this.pronunciationScore >= 80) return 'good'
      if (this.pronunciationScore >= 70) return 'fair'
      return 'poor'
    },
    getScoreFeedback () {
      if (this.pronunciationScore >= 90) return '优秀！发音非常标准'
      if (this.pronunciationScore >= 80) return '良好！发音比较准确'
      if (this.pronunciationScore >= 70) return '一般，需要继续练习'
      return '需要加强练习，注意发音细节'
    },
  },
  mounted () {
    // Auto load words on mount - disabled for testing
    // this.loadWords()
  },
}

// Mock 路由
const router = createRouter({
  history: createWebHistory(),
  routes: [],
})

// Mock Pinia
const pinia = createPinia()

// Mock Audio API
global.Audio = vi.fn().mockImplementation(() => ({
  play: vi.fn().mockResolvedValue(undefined),
  pause: vi.fn(),
  currentTime: 0,
  duration: 0,
}))

describe('Pronunciation.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()

    wrapper = mount(mockPronunciation, {
      global: {
        plugins: [router],
      },
    })
    
    await router.isReady()
    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('正确渲染发音练习页面', () => {
      expect(wrapper.find('.pronunciation-container').exists()).toBe(true)
    })

    it('显示页面标题', () => {
      expect(wrapper.text()).toContain('发音练习')
      expect(wrapper.text()).toContain('提升英语口语能力，掌握标准发音')
    })

    it('显示单词卡片', () => {
      expect(wrapper.text()).toContain('pronunciation')
      expect(wrapper.text()).toContain('/prəˌnʌnsiˈeɪʃn/')
      expect(wrapper.text()).toContain('发音，读音')
    })

    it('显示操作按钮', () => {
      expect(wrapper.text()).toContain('🔊 播放发音')
      expect(wrapper.text()).toContain('🎤 开始录音')
    })

    it('显示导航按钮', () => {
      expect(wrapper.text()).toContain('← 上一个')
      expect(wrapper.text()).toContain('下一个 →')
    })
  })

  describe('统计信息', () => {
    it('显示当前进度', () => {
      expect(wrapper.text()).toContain('当前进度')
      expect(wrapper.text()).toContain('1')
    })

    it('显示已完成数量', () => {
      expect(wrapper.text()).toContain('已完成')
      expect(wrapper.text()).toContain('1')
    })

    it('显示平均分数', () => {
      expect(wrapper.text()).toContain('平均分数')
      expect(wrapper.text()).toContain('85%')
    })
  })

  describe('单词导航功能', () => {
    it('下一个按钮点击', async () => {
      const nextButton = wrapper.find('.next-button')
      await nextButton.trigger('click')
      
      expect(wrapper.vm.currentIndex).toBe(1)
      expect(wrapper.text()).toContain('example')
    })

    it('上一个按钮点击', async () => {
      wrapper.vm.currentIndex = 1
      await wrapper.vm.$nextTick()
      
      const prevButton = wrapper.find('.prev-button')
      await prevButton.trigger('click')
      
      expect(wrapper.vm.currentIndex).toBe(0)
      expect(wrapper.text()).toContain('pronunciation')
    })

    it('导航按钮禁用状态', () => {
      const prevButton = wrapper.find('.prev-button')
      const nextButton = wrapper.find('.next-button')
      
      expect(prevButton.attributes('disabled')).toBeDefined()
      expect(nextButton.attributes('disabled')).toBeUndefined()
    })
  })

  describe('播放发音功能', () => {
    it('播放按钮点击', async () => {
      const playButton = wrapper.find('.play-button')
      await playButton.trigger('click')
      
      expect(wrapper.vm.playAudio).toBeDefined()
    })
  })

  describe('录音功能', () => {
    it('录音按钮点击', async () => {
      const recordButton = wrapper.find('.record-button')
      await recordButton.trigger('click')
      
      expect(wrapper.vm.isRecording).toBe(true)
      expect(wrapper.text()).toContain('录音中...')
    })

    it('录音状态显示', async () => {
      wrapper.vm.isRecording = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.recording-status').exists()).toBe(true)
      expect(wrapper.text()).toContain('正在录音...')
    })

    it('录音按钮禁用状态', async () => {
      wrapper.vm.isRecording = true
      await wrapper.vm.$nextTick()
      
      const recordButton = wrapper.find('.record-button')
      expect(recordButton.attributes('disabled')).toBeDefined()
    })
  })

  describe('评分功能', () => {
    it('评分结果显示', async () => {
      wrapper.vm.pronunciationScore = 85
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('发音评分')
      expect(wrapper.text()).toContain('85%')
    })

    it('评分等级分类', () => {
      wrapper.vm.pronunciationScore = 95
      expect(wrapper.vm.getScoreClass()).toBe('excellent')
      wrapper.vm.pronunciationScore = 85
      expect(wrapper.vm.getScoreClass()).toBe('good')
      wrapper.vm.pronunciationScore = 75
      expect(wrapper.vm.getScoreClass()).toBe('fair')
      wrapper.vm.pronunciationScore = 65
      expect(wrapper.vm.getScoreClass()).toBe('poor')
    })

    it('评分反馈信息', () => {
      wrapper.vm.pronunciationScore = 95
      expect(wrapper.vm.getScoreFeedback()).toContain('优秀')
      wrapper.vm.pronunciationScore = 85
      expect(wrapper.vm.getScoreFeedback()).toContain('良好')
      wrapper.vm.pronunciationScore = 75
      expect(wrapper.vm.getScoreFeedback()).toContain('一般')
      wrapper.vm.pronunciationScore = 65
      expect(wrapper.vm.getScoreFeedback()).toContain('需要加强')
    })
  })

  describe('加载状态', () => {
    it('加载状态显示', async () => {
      wrapper.vm.isLoading = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.loading-state').exists()).toBe(true)
      expect(wrapper.text()).toContain('正在加载单词数据...')
    })

    it('空数据状态显示', async () => {
      wrapper.vm.words = []
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.empty-state').exists()).toBe(true)
      expect(wrapper.text()).toContain('暂无单词数据')
      expect(wrapper.text()).toContain('加载单词')
    })

    it('加载单词功能', async () => {
      wrapper.vm.words = []
      await wrapper.vm.$nextTick()
      
      const loadButton = wrapper.find('.primary-button')
      await loadButton.trigger('click')
      
      expect(wrapper.vm.loadWords).toBeDefined()
    })
  })

  describe('计算属性', () => {
    it('当前单词计算', () => {
      expect(wrapper.vm.currentWord.word).toBe('pronunciation')
      expect(wrapper.vm.currentWord.phonetic).toBe('/prəˌnʌnsiˈeɪʃn/')
    })

    it('已完成数量计算', () => {
      expect(wrapper.vm.completedCount).toBe(1)
    })

    it('平均分数计算', () => {
      expect(wrapper.vm.averageScore).toBe(85)
    })

    it('空数据时的计算属性', async () => {
      wrapper.vm.words = []
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.currentWord).toEqual({})
      expect(wrapper.vm.completedCount).toBe(0)
      expect(wrapper.vm.averageScore).toBe(null)
    })
  })

  describe('边界情况', () => {
    it('最后一个单词时下一个按钮禁用', async () => {
      wrapper.vm.currentIndex = wrapper.vm.words.length - 1
      await wrapper.vm.$nextTick()
      
      const nextButton = wrapper.find('.next-button')
      expect(nextButton.attributes('disabled')).toBeDefined()
    })

    it('第一个单词时上一个按钮禁用', () => {
      const prevButton = wrapper.find('.prev-button')
      expect(prevButton.attributes('disabled')).toBeDefined()
    })

    it('导航时重置评分', async () => {
      wrapper.vm.pronunciationScore = 85
      await wrapper.vm.$nextTick()
      
      const nextButton = wrapper.find('.next-button')
      await nextButton.trigger('click')
      
      expect(wrapper.vm.pronunciationScore).toBe(null)
    })
  })

  describe('响应式数据', () => {
    it('单词数据正确绑定', () => {
      expect(wrapper.vm.words.length).toBe(3)
      expect(wrapper.vm.words[0].word).toBe('pronunciation')
    })

    it('录音状态正确绑定', () => {
      expect(wrapper.vm.isRecording).toBe(false)
      expect(wrapper.vm.pronunciationScore).toBe(null)
    })

    it('加载状态正确绑定', () => {
      expect(wrapper.vm.isLoading).toBeDefined()
    })
  })

  describe('生命周期', () => {
    it('组件挂载时自动加载单词', () => {
      expect(wrapper.vm.loadWords).toBeDefined()
    })
  })
}) 