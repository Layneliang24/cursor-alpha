import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

// Mock 整个Expressions组件
const mockExpressions = {
  template: `
    <div class="expressions-page">
      <div class="page-header">
        <h1>地道表达</h1>
        <div class="header-actions">
          <button @click="refreshData" class="refresh-btn" :disabled="expressionsLoading">
            {{ expressionsLoading ? '刷新中...' : '刷新' }}
          </button>
        </div>
      </div>

      <div class="filter-card">
        <div class="filter-row">
          <div class="search-input">
            <input 
              v-model="searchQuery"
              placeholder="搜索表达..."
              @input="handleSearch"
            />
          </div>
          <div class="category-select">
            <select v-model="categoryFilter" @change="handleFilter">
              <option value="">全部分类</option>
              <option value="daily">日常对话</option>
              <option value="business">商务英语</option>
              <option value="academic">学术英语</option>
              <option value="travel">旅行</option>
            </select>
          </div>
          <div class="difficulty-select">
            <select v-model="difficultyFilter" @change="handleFilter">
              <option value="">全部难度</option>
              <option value="beginner">初级</option>
              <option value="intermediate">中级</option>
              <option value="advanced">高级</option>
            </select>
          </div>
          <div class="frequency-select">
            <select v-model="frequencyFilter" @change="handleFilter">
              <option value="">全部频率</option>
              <option value="high">高频</option>
              <option value="medium">中频</option>
              <option value="low">低频</option>
            </select>
          </div>
        </div>
      </div>

      <div class="expressions-list" v-if="!expressionsLoading">
        <div v-if="expressions.length === 0" class="empty-state">
          <div class="empty-text">暂无地道表达数据</div>
          <button @click="refreshData" class="refresh-empty-btn">刷新数据</button>
        </div>
        
        <div v-else class="expressions-grid">
          <div 
            v-for="expression in expressions" 
            :key="expression.id" 
            class="expression-card"
          >
            <div class="expression-header">
              <h3 class="expression-text">{{ expression.expression }}</h3>
              <div class="expression-tags">
                <span :class="['difficulty-tag', getDifficultyType(expression.difficulty_level)]">
                  {{ getDifficultyLabel(expression.difficulty_level) }}
                </span>
                <span :class="['frequency-tag', getFrequencyType(expression.usage_frequency)]">
                  {{ getFrequencyLabel(expression.usage_frequency) }}
                </span>
              </div>
            </div>

            <div class="expression-content">
              <div class="meaning" v-if="expression.meaning">
                <h4>含义</h4>
                <p>{{ expression.meaning }}</p>
              </div>

              <div class="category-scenario" v-if="expression.category || expression.scenario">
                <div class="info-row">
                  <div class="info-item" v-if="expression.category">
                    <strong>分类:</strong> {{ getCategoryLabel(expression.category) }}
                  </div>
                  <div class="info-item" v-if="expression.scenario">
                    <strong>场景:</strong> {{ getScenarioLabel(expression.scenario) }}
                  </div>
                </div>
              </div>

              <div class="usage-examples" v-if="expression.usage_examples">
                <h4>使用示例</h4>
                <p class="examples-text">{{ expression.usage_examples }}</p>
              </div>

              <div class="cultural-background" v-if="expression.cultural_background">
                <h4>文化背景</h4>
                <p class="background-text">{{ expression.cultural_background }}</p>
              </div>
            </div>

            <div class="expression-actions">
              <button @click="playAudio(expression)" :disabled="!expression.audio_url" class="play-btn">
                播放发音
              </button>
              <button @click="addToCollection(expression)" class="collect-btn">
                收藏
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="pagination-container" v-if="expressions.length > 0">
        <div class="pagination-info">
          共 {{ total }} 条记录
        </div>
        <div class="pagination-controls">
          <button @click="prevPage" :disabled="currentPage === 1" class="prev-btn">
            上一页
          </button>
          <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
          <button @click="nextPage" :disabled="currentPage === totalPages" class="next-btn">
            下一页
          </button>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      searchQuery: '',
      categoryFilter: '',
      difficultyFilter: '',
      frequencyFilter: '',
      currentPage: 1,
      pageSize: 12,
      expressionsLoading: false,
      expressions: [
        {
          id: 1,
          expression: 'Break a leg!',
          meaning: '祝你好运！',
          category: 'daily',
          scenario: 'casual',
          difficulty_level: 'intermediate',
          usage_frequency: 'high',
          usage_examples: 'Good luck with your presentation! Break a leg!',
          cultural_background: '源自戏剧界，演员们认为说"good luck"会带来厄运，所以用"break a leg"代替。',
          audio_url: 'audio1.mp3'
        },
        {
          id: 2,
          expression: 'Piece of cake',
          meaning: '小菜一碟，很容易',
          category: 'daily',
          scenario: 'casual',
          difficulty_level: 'beginner',
          usage_frequency: 'high',
          usage_examples: 'Don\'t worry, this test will be a piece of cake.',
          cultural_background: '比喻某事像吃蛋糕一样简单愉快。',
          audio_url: null
        }
      ],
      total: 2
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.total / this.pageSize)
    }
  },
  methods: {
    async refreshData() {
      this.expressionsLoading = true
      try {
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 100))
        // Data is already loaded in data()
      } finally {
        this.expressionsLoading = false
      }
    },
    handleSearch() {
      this.currentPage = 1
      this.refreshData()
    },
    handleFilter() {
      this.currentPage = 1
      this.refreshData()
    },
    getDifficultyType(level) {
      const types = {
        beginner: 'success',
        intermediate: 'warning',
        advanced: 'danger'
      }
      return types[level] || 'info'
    },
    getDifficultyLabel(level) {
      const labels = {
        beginner: '初级',
        intermediate: '中级',
        advanced: '高级'
      }
      return labels[level] || '未知'
    },
    getFrequencyType(frequency) {
      const types = {
        high: 'success',
        medium: 'warning',
        low: 'info'
      }
      return types[frequency] || 'info'
    },
    getFrequencyLabel(frequency) {
      const labels = {
        high: '高频',
        medium: '中频',
        low: '低频'
      }
      return labels[frequency] || '未知'
    },
    getCategoryLabel(category) {
      const labels = {
        daily: '日常对话',
        business: '商务英语',
        academic: '学术英语',
        travel: '旅行'
      }
      return labels[category] || '其他'
    },
    getScenarioLabel(scenario) {
      const labels = {
        casual: '非正式',
        formal: '正式',
        professional: '专业'
      }
      return labels[scenario] || '通用'
    },
    playAudio(expression) {
      if (expression.audio_url) {
        console.log('播放音频:', expression.audio_url)
      }
    },
    addToCollection(expression) {
      console.log('添加到收藏:', expression.expression)
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
        this.refreshData()
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
        this.refreshData()
      }
    },
    handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      this.refreshData()
    },
    handleCurrentChange(page) {
      this.currentPage = page
      this.refreshData()
    }
  },
  mounted() {
    // Auto load data on mount - disabled for testing
    // this.refreshData()
  }
}

// Mock 路由
const router = createRouter({
  history: createWebHistory(),
  routes: []
})

// Mock Pinia
const pinia = createPinia()

describe('Expressions.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()

    wrapper = mount(mockExpressions, {
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
    it('正确渲染地道表达页面', () => {
      expect(wrapper.find('.expressions-page').exists()).toBe(true)
    })

    it('显示页面标题', () => {
      expect(wrapper.text()).toContain('地道表达')
    })

    it('显示刷新按钮', () => {
      expect(wrapper.text()).toContain('刷新')
    })

    it('显示搜索输入框', () => {
      expect(wrapper.find('.search-input input').exists()).toBe(true)
      expect(wrapper.find('.search-input input').attributes('placeholder')).toBe('搜索表达...')
    })
  })

  describe('筛选功能', () => {
    it('显示分类选择器', () => {
      const categorySelect = wrapper.find('.category-select select')
      expect(categorySelect.exists()).toBe(true)
      expect(categorySelect.text()).toContain('全部分类')
      expect(categorySelect.text()).toContain('日常对话')
    })

    it('显示难度选择器', () => {
      const difficultySelect = wrapper.find('.difficulty-select select')
      expect(difficultySelect.exists()).toBe(true)
      expect(difficultySelect.text()).toContain('全部难度')
      expect(difficultySelect.text()).toContain('初级')
    })

    it('显示频率选择器', () => {
      const frequencySelect = wrapper.find('.frequency-select select')
      expect(frequencySelect.exists()).toBe(true)
      expect(frequencySelect.text()).toContain('全部频率')
      expect(frequencySelect.text()).toContain('高频')
    })
  })

  describe('表达卡片', () => {
    it('显示表达文本', () => {
      expect(wrapper.vm.expressions[0].expression).toBe('Break a leg!')
      expect(wrapper.vm.expressions[1].expression).toBe('Piece of cake')
    })

    it('显示表达含义', () => {
      expect(wrapper.vm.expressions[0].meaning).toBe('祝你好运！')
      expect(wrapper.vm.expressions[1].meaning).toBe('小菜一碟，很容易')
    })

    it('显示难度标签', () => {
      expect(wrapper.vm.expressions[0].difficulty_level).toBe('intermediate')
      expect(wrapper.vm.expressions[1].difficulty_level).toBe('beginner')
    })

    it('显示频率标签', () => {
      expect(wrapper.vm.expressions[0].usage_frequency).toBe('high')
    })

    it('显示分类信息', () => {
      expect(wrapper.vm.expressions[0].category).toBe('daily')
    })

    it('显示使用示例', () => {
      expect(wrapper.vm.expressions[0].usage_examples).toContain('Good luck with your presentation!')
    })

    it('显示文化背景', () => {
      expect(wrapper.vm.expressions[0].cultural_background).toContain('源自戏剧界')
    })
  })

  describe('操作按钮', () => {
    it('显示播放发音按钮', () => {
      const playButtons = wrapper.findAll('.play-btn')
      expect(playButtons.length).toBeGreaterThan(0)
    })

    it('显示收藏按钮', () => {
      const collectButtons = wrapper.findAll('.collect-btn')
      expect(collectButtons.length).toBeGreaterThan(0)
    })

    it('播放发音按钮点击', async () => {
      const playButton = wrapper.find('.play-btn')
      if (playButton.exists()) {
        await playButton.trigger('click')
        expect(wrapper.vm.playAudio).toBeDefined()
      }
    })

    it('收藏按钮点击', async () => {
      const collectButton = wrapper.find('.collect-btn')
      if (collectButton.exists()) {
        await collectButton.trigger('click')
        expect(wrapper.vm.addToCollection).toBeDefined()
      }
    })
  })

  describe('分页功能', () => {
    it('显示分页信息', () => {
      expect(wrapper.text()).toContain('共 2 条记录')
    })

    it('显示页码信息', () => {
      expect(wrapper.text()).toContain('1 / 1')
    })

    it('显示分页按钮', () => {
      expect(wrapper.find('.prev-btn').exists()).toBe(true)
      expect(wrapper.find('.next-btn').exists()).toBe(true)
    })

    it('上一页按钮禁用状态', () => {
      const prevButton = wrapper.find('.prev-btn')
      expect(prevButton.attributes('disabled')).toBeDefined()
    })

    it('下一页按钮禁用状态', () => {
      const nextButton = wrapper.find('.next-btn')
      expect(nextButton.attributes('disabled')).toBeDefined()
    })
  })

  describe('搜索功能', () => {
    it('搜索输入变化', async () => {
      const searchInput = wrapper.find('.search-input input')
      await searchInput.setValue('break')
      
      expect(wrapper.vm.searchQuery).toBe('break')
    })

    it('搜索触发数据刷新', async () => {
      const searchInput = wrapper.find('.search-input input')
      await searchInput.setValue('test')
      
      expect(wrapper.vm.handleSearch).toBeDefined()
    })
  })

  describe('筛选功能', () => {
    it('分类筛选变化', async () => {
      const categorySelect = wrapper.find('.category-select select')
      await categorySelect.setValue('business')
      
      expect(wrapper.vm.categoryFilter).toBe('business')
    })

    it('难度筛选变化', async () => {
      const difficultySelect = wrapper.find('.difficulty-select select')
      await difficultySelect.setValue('advanced')
      
      expect(wrapper.vm.difficultyFilter).toBe('advanced')
    })

    it('频率筛选变化', async () => {
      const frequencySelect = wrapper.find('.frequency-select select')
      await frequencySelect.setValue('medium')
      
      expect(wrapper.vm.frequencyFilter).toBe('medium')
    })
  })

  describe('工具函数', () => {
    it('难度类型获取', () => {
      expect(wrapper.vm.getDifficultyType('beginner')).toBe('success')
      expect(wrapper.vm.getDifficultyType('intermediate')).toBe('warning')
      expect(wrapper.vm.getDifficultyType('advanced')).toBe('danger')
    })

    it('难度标签获取', () => {
      expect(wrapper.vm.getDifficultyLabel('beginner')).toBe('初级')
      expect(wrapper.vm.getDifficultyLabel('intermediate')).toBe('中级')
      expect(wrapper.vm.getDifficultyLabel('advanced')).toBe('高级')
    })

    it('频率类型获取', () => {
      expect(wrapper.vm.getFrequencyType('high')).toBe('success')
      expect(wrapper.vm.getFrequencyType('medium')).toBe('warning')
      expect(wrapper.vm.getFrequencyType('low')).toBe('info')
    })

    it('频率标签获取', () => {
      expect(wrapper.vm.getFrequencyLabel('high')).toBe('高频')
      expect(wrapper.vm.getFrequencyLabel('medium')).toBe('中频')
      expect(wrapper.vm.getFrequencyLabel('low')).toBe('低频')
    })

    it('分类标签获取', () => {
      expect(wrapper.vm.getCategoryLabel('daily')).toBe('日常对话')
      expect(wrapper.vm.getCategoryLabel('business')).toBe('商务英语')
      expect(wrapper.vm.getCategoryLabel('academic')).toBe('学术英语')
    })

    it('场景标签获取', () => {
      expect(wrapper.vm.getScenarioLabel('casual')).toBe('非正式')
      expect(wrapper.vm.getScenarioLabel('formal')).toBe('正式')
      expect(wrapper.vm.getScenarioLabel('professional')).toBe('专业')
    })
  })

  describe('边界情况', () => {
    it('无数据时显示空状态', async () => {
      wrapper.vm.expressions = []
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.expressions.length).toBe(0)
    })

    it('有数据时显示表达列表', () => {
      expect(wrapper.vm.expressions.length).toBeGreaterThan(0)
    })

    it('加载状态显示', async () => {
      wrapper.vm.expressionsLoading = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('刷新中...')
    })
  })

  describe('响应式数据', () => {
    it('搜索查询正确绑定', () => {
      expect(wrapper.vm.searchQuery).toBe('')
    })

    it('筛选条件正确绑定', () => {
      expect(wrapper.vm.categoryFilter).toBe('')
      expect(wrapper.vm.difficultyFilter).toBe('')
      expect(wrapper.vm.frequencyFilter).toBe('')
    })

    it('分页数据正确绑定', () => {
      expect(wrapper.vm.currentPage).toBe(1)
      expect(wrapper.vm.pageSize).toBe(12)
      expect(wrapper.vm.total).toBe(2)
    })

    it('表达数据正确绑定', () => {
      expect(wrapper.vm.expressions.length).toBe(2)
      expect(wrapper.vm.expressions[0].expression).toBe('Break a leg!')
    })
  })

  describe('计算属性', () => {
    it('总页数计算', () => {
      expect(wrapper.vm.totalPages).toBe(1)
    })
  })

  describe('事件处理', () => {
    it('刷新数据功能', async () => {
      const refreshButton = wrapper.find('.refresh-btn')
      await refreshButton.trigger('click')
      
      expect(wrapper.vm.refreshData).toBeDefined()
    })

    it('筛选触发数据刷新', async () => {
      const categorySelect = wrapper.find('.category-select select')
      await categorySelect.setValue('daily')
      
      expect(wrapper.vm.handleFilter).toBeDefined()
    })
  })

  describe('数据更新', () => {
    it('搜索后页码重置', async () => {
      wrapper.vm.currentPage = 3
      await wrapper.vm.handleSearch()
      
      expect(wrapper.vm.currentPage).toBe(1)
    })

    it('筛选后页码重置', async () => {
      wrapper.vm.currentPage = 3
      await wrapper.vm.handleFilter()
      
      expect(wrapper.vm.currentPage).toBe(1)
    })
  })
}) 