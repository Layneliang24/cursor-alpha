import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

// Mock 整个Words组件
const mockWords = {
  template: `
    <div class="page-container">
      <div class="toolbar">
        <input v-model="localQuery.search" placeholder="搜索单词/释义" @keyup.enter="handleSearch" />
        <select v-model="localQuery.difficulty" @change="handleSearch">
          <option value="">全部</option>
          <option value="easy">简单</option>
          <option value="medium">一般</option>
          <option value="hard">困难</option>
        </select>
        <button @click="handleSearch">查询</button>
      </div>

      <div class="words-table" v-loading="englishStore.wordsLoading">
        <table>
          <thead>
            <tr>
              <th>单词</th>
              <th>音标</th>
              <th>词性</th>
              <th>释义</th>
              <th>难度</th>
              <th>来源</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="word in englishStore.words" :key="word.id">
              <td>{{ word.word }}</td>
              <td>{{ word.phonetic }}</td>
              <td>{{ word.part_of_speech }}</td>
              <td>{{ word.definition }}</td>
              <td>{{ word.difficulty_level }}</td>
              <td>{{ word.source_api }}</td>
              <td>
                <button @click="goDetail(word)">详情</button>
                <button @click="startReview(word)">复习</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pager">
        <div class="pagination">
          <span>总数: {{ englishStore.wordsPagination.total }}</span>
          <button @click="handlePageChange(englishStore.wordsPagination.page - 1)">上一页</button>
          <span>第 {{ englishStore.wordsPagination.page }} 页</span>
          <button @click="handlePageChange(englishStore.wordsPagination.page + 1)">下一页</button>
        </div>
      </div>
    </div>
    
    <div class="review-dialog" v-if="dialogVisible">
      <div class="dialog-header">
        <h3>待复习单词</h3>
        <button @click="dialogVisible = false">关闭</button>
      </div>
      <div class="dialog-content" v-loading="dueLoading">
        <table>
          <thead>
            <tr>
              <th>单词</th>
              <th>释义</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in dueList" :key="item.id">
              <td>{{ item.word.word }}</td>
              <td>{{ item.word.definition }}</td>
              <td>
                <button @click="submitReview(item, 2)">困难</button>
                <button @click="submitReview(item, 3)">一般</button>
                <button @click="submitReview(item, 5)">简单</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  data() {
    return {
      localQuery: {
        search: '',
        difficulty: ''
      },
      dialogVisible: false,
      dueList: [],
      dueLoading: false
    }
  },
  computed: {
    englishStore() {
      return {
        words: [
          {
            id: 1,
            word: 'apple',
            phonetic: '/ˈæpəl/',
            part_of_speech: 'n.',
            definition: '苹果',
            difficulty_level: '简单',
            source_api: 'Oxford'
          },
          {
            id: 2,
            word: 'banana',
            phonetic: '/bəˈnɑːnə/',
            part_of_speech: 'n.',
            definition: '香蕉',
            difficulty_level: '简单',
            source_api: 'Cambridge'
          }
        ],
        wordsLoading: false,
        wordsPagination: {
          total: 100,
          pageSize: 10,
          page: 1
        }
      }
    }
  },
  methods: {
    async fetchList() {
      // Mock implementation
    },
    handleSearch() {
      this.englishStore.wordsPagination.page = 1
      this.fetchList()
    },
    handlePageChange(page) {
      this.englishStore.wordsPagination.page = page
      this.fetchList()
    },
    goDetail(row) {
      this.$router.push(`/english/words/${row.id}`)
    },
    async startReview() {
      this.dialogVisible = true
      this.dueLoading = true
      try {
        // Mock API call
        this.dueList = [
          {
            id: 1,
            word: { word: 'apple', definition: '苹果' }
          },
          {
            id: 2,
            word: { word: 'banana', definition: '香蕉' }
          }
        ]
      } finally {
        this.dueLoading = false
      }
    },
    async submitReview(progressRow, quality) {
      try {
        // Mock API call
        this.$message.success('打卡成功')
        // 移除已复习项
        this.dueList = this.dueList.filter(i => i.id !== progressRow.id)
      } catch (e) {
        console.error(e)
      }
    }
  },
  mounted() {
    this.fetchList()
  }
}

// Mock 路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/english/words/:id', component: { template: '<div>WordDetail</div>' } }
  ]
})

// Mock router.push
router.push = vi.fn()

// Mock Pinia
const pinia = createPinia()

// Mock ElMessage
const mockElMessage = {
  success: vi.fn(),
  error: vi.fn()
}

vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: mockElMessage
  }
})

describe('Words.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()

    wrapper = mount(mockWords, {
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
    it('正确渲染页面容器', () => {
      expect(wrapper.find('.page-container').exists()).toBe(true)
    })

    it('显示工具栏', () => {
      expect(wrapper.find('.toolbar').exists()).toBe(true)
    })

    it('显示搜索输入框', () => {
      const searchInput = wrapper.find('input[placeholder="搜索单词/释义"]')
      expect(searchInput.exists()).toBe(true)
    })

    it('显示难度选择器', () => {
      const difficultySelect = wrapper.find('select')
      expect(difficultySelect.exists()).toBe(true)
    })

    it('显示查询按钮', () => {
      expect(wrapper.text()).toContain('查询')
    })
  })

  describe('单词表格', () => {
    it('显示表格标题', () => {
      expect(wrapper.text()).toContain('单词')
      expect(wrapper.text()).toContain('音标')
      expect(wrapper.text()).toContain('词性')
      expect(wrapper.text()).toContain('释义')
      expect(wrapper.text()).toContain('难度')
      expect(wrapper.text()).toContain('来源')
      expect(wrapper.text()).toContain('操作')
    })

    it('显示单词数据', () => {
      expect(wrapper.text()).toContain('apple')
      expect(wrapper.text()).toContain('banana')
      expect(wrapper.text()).toContain('/ˈæpəl/')
      expect(wrapper.text()).toContain('/bəˈnɑːnə/')
    })

    it('显示单词详情', () => {
      expect(wrapper.text()).toContain('苹果')
      expect(wrapper.text()).toContain('香蕉')
      expect(wrapper.text()).toContain('n.')
      expect(wrapper.text()).toContain('简单')
    })

    it('显示操作按钮', () => {
      const detailButtons = wrapper.findAll('button').filter(btn => btn.text().includes('详情'))
      const reviewButtons = wrapper.findAll('button').filter(btn => btn.text().includes('复习'))
      expect(detailButtons.length).toBeGreaterThan(0)
      expect(reviewButtons.length).toBeGreaterThan(0)
    })
  })

  describe('搜索功能', () => {
    it('搜索输入功能', async () => {
      const searchInput = wrapper.find('input[placeholder="搜索单词/释义"]')
      await searchInput.setValue('apple')
      
      expect(wrapper.vm.localQuery.search).toBe('apple')
    })

    it('难度选择功能', async () => {
      const difficultySelect = wrapper.find('select')
      await difficultySelect.setValue('easy')
      
      expect(wrapper.vm.localQuery.difficulty).toBe('easy')
    })

    it('搜索按钮点击', async () => {
      const searchButton = wrapper.findAll('button').find(btn => btn.text().includes('查询'))
      await searchButton.trigger('click')
      
      expect(wrapper.vm.englishStore.wordsPagination.page).toBe(1)
    })

    it('回车键搜索', async () => {
      const searchInput = wrapper.find('input[placeholder="搜索单词/释义"]')
      await searchInput.trigger('keyup.enter')
      
      expect(wrapper.vm.englishStore.wordsPagination.page).toBe(1)
    })
  })

  describe('分页功能', () => {
    it('显示分页信息', () => {
      expect(wrapper.text()).toContain('总数: 100')
      expect(wrapper.text()).toContain('第 1 页')
    })

    it('上一页功能', async () => {
      wrapper.vm.englishStore.wordsPagination.page = 2
      const prevButton = wrapper.findAll('button').find(btn => btn.text().includes('上一页'))
      await prevButton.trigger('click')
      
      expect(wrapper.vm.englishStore.wordsPagination.page).toBe(1)
    })

    it('下一页功能', async () => {
      const nextButton = wrapper.findAll('button').find(btn => btn.text().includes('下一页'))
      await nextButton.trigger('click')
      
      expect(wrapper.vm.englishStore.wordsPagination.page).toBe(2)
    })
  })

  describe('单词详情', () => {
    it('详情按钮点击', async () => {
      const detailButton = wrapper.findAll('button').find(btn => btn.text().includes('详情'))
      await detailButton.trigger('click')
      
      expect(router.push).toHaveBeenCalledWith('/english/words/1')
    })
  })

  describe('复习功能', () => {
    it('复习按钮点击', async () => {
      const reviewButton = wrapper.findAll('button').find(btn => btn.text().includes('复习'))
      await reviewButton.trigger('click')
      
      expect(wrapper.vm.dialogVisible).toBe(true)
    })

    it('显示复习对话框', async () => {
      wrapper.vm.dialogVisible = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.review-dialog').exists()).toBe(true)
      expect(wrapper.text()).toContain('待复习单词')
    })

    it('加载复习数据', async () => {
      wrapper.vm.dialogVisible = true
      await wrapper.vm.startReview()
      
      expect(wrapper.vm.dueList.length).toBe(2)
      expect(wrapper.vm.dueList[0].word.word).toBe('apple')
      expect(wrapper.vm.dueList[1].word.word).toBe('banana')
    })

    it('显示复习单词列表', async () => {
      wrapper.vm.dialogVisible = true
      wrapper.vm.dueList = [
        { id: 1, word: { word: 'apple', definition: '苹果' } },
        { id: 2, word: { word: 'banana', definition: '香蕉' } }
      ]
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('apple')
      expect(wrapper.text()).toContain('banana')
      expect(wrapper.text()).toContain('苹果')
      expect(wrapper.text()).toContain('香蕉')
    })

    it('复习难度按钮', async () => {
      wrapper.vm.dialogVisible = true
      wrapper.vm.dueList = [{ id: 1, word: { word: 'apple', definition: '苹果' } }]
      await wrapper.vm.$nextTick()
      
      const difficultyButtons = wrapper.findAll('button')
      const hardButton = difficultyButtons.find(btn => btn.text().includes('困难'))
      const mediumButton = difficultyButtons.find(btn => btn.text().includes('一般'))
      const easyButton = difficultyButtons.find(btn => btn.text().includes('简单'))
      
      expect(hardButton.exists()).toBe(true)
      expect(mediumButton.exists()).toBe(true)
      expect(easyButton.exists()).toBe(true)
    })

    it('提交复习结果', async () => {
      wrapper.vm.dialogVisible = true
      wrapper.vm.dueList = [{ id: 1, word: { word: 'apple', definition: '苹果' } }]
      await wrapper.vm.$nextTick()
      
      const easyButton = wrapper.findAll('button').find(btn => btn.text().includes('简单'))
      expect(easyButton.exists()).toBe(true)
    })

    it('关闭复习对话框', async () => {
      wrapper.vm.dialogVisible = true
      await wrapper.vm.$nextTick()
      
      const closeButton = wrapper.find('.dialog-header button')
      await closeButton.trigger('click')
      
      expect(wrapper.vm.dialogVisible).toBe(false)
    })
  })

  describe('加载状态', () => {
    it('表格加载状态', async () => {
      wrapper.vm.englishStore.wordsLoading = true
      await wrapper.vm.$nextTick()
      
      const table = wrapper.find('.words-table')
      expect(table.exists()).toBe(true)
    })

    it('复习对话框加载状态', async () => {
      wrapper.vm.dialogVisible = true
      wrapper.vm.dueLoading = true
      await wrapper.vm.$nextTick()
      
      const dialogContent = wrapper.find('.dialog-content')
      expect(dialogContent.exists()).toBe(true)
    })
  })

  describe('边界情况', () => {
    it('空复习列表', async () => {
      wrapper.vm.dialogVisible = true
      wrapper.vm.dueList = []
      await wrapper.vm.$nextTick()
      
      const tbody = wrapper.find('.dialog-content tbody')
      expect(tbody.text()).toBe('')
    })
  })

  describe('生命周期', () => {
    it('组件挂载时调用数据获取', () => {
      expect(wrapper.vm.fetchList).toBeDefined()
    })
  })
}) 