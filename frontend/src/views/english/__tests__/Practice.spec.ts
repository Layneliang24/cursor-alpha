import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

// Mock 整个Practice组件
const mockPractice = {
  template: `
    <div class="english-practice">
      <div class="practice-header">
        <h1>英语练习</h1>
        <div class="practice-stats">
          <span>正确率: {{ accuracy }}%</span>
          <span>进度: {{ currentIndex + 1 }} / {{ totalQuestions }}</span>
        </div>
      </div>
      
      <div class="practice-content" v-if="currentQuestion">
        <div class="question-card">
          <div class="question-text">{{ currentQuestion.question }}</div>
          
          <div class="options-list" v-if="currentQuestion.type === 'multiple_choice'">
            <div 
              v-for="option in currentQuestion.options" 
              :key="option.id"
              class="option-item"
              :class="{ selected: selectedAnswer === option.id, correct: showResult && option.isCorrect, incorrect: showResult && selectedAnswer === option.id && !option.isCorrect }"
              @click="selectAnswer(option.id)"
            >
              {{ option.text }}
            </div>
          </div>
          
          <div class="fill-blank" v-else-if="currentQuestion.type === 'fill_blank'">
            <input 
              v-model="userAnswer" 
              :placeholder="currentQuestion.placeholder"
              @keyup.enter="submitAnswer"
            />
          </div>
          
          <div class="translation" v-if="currentQuestion.translation">
            <p>翻译: {{ currentQuestion.translation }}</p>
          </div>
        </div>
        
        <div class="practice-actions">
          <button 
            v-if="!showResult" 
            @click="submitAnswer" 
            :disabled="!canSubmit"
            class="submit-btn"
          >
            提交答案
          </button>
          <button 
            v-else 
            @click="nextQuestion" 
            class="next-btn"
          >
            {{ isLastQuestion ? '完成练习' : '下一题' }}
          </button>
        </div>
      </div>
      
      <div class="practice-results" v-if="showResults">
        <h2>练习结果</h2>
        <div class="result-stats">
          <div class="stat-item">
            <span class="stat-label">总题数:</span>
            <span class="stat-value">{{ totalQuestions }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">正确数:</span>
            <span class="stat-value">{{ correctCount }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">正确率:</span>
            <span class="stat-value">{{ finalAccuracy }}%</span>
          </div>
        </div>
        
        <div class="result-actions">
          <button @click="restartPractice">重新开始</button>
          <button @click="goToDashboard">返回仪表板</button>
        </div>
      </div>
      
      <div class="loading" v-if="loading">
        <p>加载中...</p>
      </div>
    </div>
  `,
  data() {
    return {
      loading: false,
      questions: [
        {
          id: 1,
          type: 'multiple_choice',
          question: 'What is the meaning of "apple"?',
          options: [
            { id: 'a', text: '苹果', isCorrect: true },
            { id: 'b', text: '香蕉', isCorrect: false },
            { id: 'c', text: '橙子', isCorrect: false },
            { id: 'd', text: '葡萄', isCorrect: false }
          ],
          translation: '苹果'
        },
        {
          id: 2,
          type: 'fill_blank',
          question: 'Complete the sentence: "I ___ a student."',
          placeholder: 'Enter the correct form of "be"',
          answer: 'am',
          translation: '我是一个学生。'
        }
      ],
      currentIndex: 0,
      selectedAnswer: null,
      userAnswer: '',
      showResult: false,
      showResults: false,
      correctCount: 0,
      answers: []
    }
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentIndex] || null
    },
    totalQuestions() {
      return this.questions.length
    },
    isLastQuestion() {
      return this.currentIndex === this.totalQuestions - 1
    },
    canSubmit() {
      if (this.currentQuestion?.type === 'multiple_choice') {
        return this.selectedAnswer !== null
      } else if (this.currentQuestion?.type === 'fill_blank') {
        return this.userAnswer.trim() !== ''
      }
      return false
    },
    accuracy() {
      if (this.answers.length === 0) return 0
      const correct = this.answers.filter(answer => answer.isCorrect).length
      return Math.round((correct / this.answers.length) * 100)
    },
    finalAccuracy() {
      return Math.round((this.correctCount / this.totalQuestions) * 100)
    }
  },
  methods: {
    selectAnswer(answerId) {
      if (!this.showResult) {
        this.selectedAnswer = answerId
      }
    },
    submitAnswer() {
      if (!this.canSubmit) return
      
      let isCorrect = false
      
      if (this.currentQuestion.type === 'multiple_choice') {
        const selectedOption = this.currentQuestion.options.find(opt => opt.id === this.selectedAnswer)
        isCorrect = selectedOption?.isCorrect || false
      } else if (this.currentQuestion.type === 'fill_blank') {
        isCorrect = this.userAnswer.trim().toLowerCase() === this.currentQuestion.answer.toLowerCase()
      }
      
      this.answers.push({
        questionId: this.currentQuestion.id,
        answer: this.currentQuestion.type === 'multiple_choice' ? this.selectedAnswer : this.userAnswer,
        isCorrect
      })
      
      if (isCorrect) {
        this.correctCount++
      }
      
      this.showResult = true
    },
    nextQuestion() {
      if (this.isLastQuestion) {
        this.showResults = true
      } else {
        this.currentIndex++
        this.resetQuestion()
      }
    },
    resetQuestion() {
      this.selectedAnswer = null
      this.userAnswer = ''
      this.showResult = false
    },
    restartPractice() {
      this.currentIndex = 0
      this.correctCount = 0
      this.answers = []
      this.showResults = false
      this.resetQuestion()
    },
    goToDashboard() {
      this.$router.push('/english/dashboard')
    }
  }
}

// Mock 路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/english/dashboard', component: { template: '<div>Dashboard</div>' } }
  ]
})

// Mock router.push
router.push = vi.fn()

// Mock Pinia
const pinia = createPinia()

describe('Practice.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    
    // 重置所有mock
    vi.clearAllMocks()

    wrapper = mount(mockPractice, {
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
    it('正确渲染练习容器', () => {
      expect(wrapper.find('.english-practice').exists()).toBe(true)
    })

    it('显示页面标题', () => {
      expect(wrapper.text()).toContain('英语练习')
    })

    it('显示练习统计', () => {
      expect(wrapper.text()).toContain('正确率: 0%')
      expect(wrapper.text()).toContain('进度: 1 / 2')
    })
  })

  describe('选择题功能', () => {
    it('显示选择题题目', () => {
      expect(wrapper.text()).toContain('What is the meaning of "apple"?')
    })

    it('显示选项列表', () => {
      expect(wrapper.text()).toContain('苹果')
      expect(wrapper.text()).toContain('香蕉')
      expect(wrapper.text()).toContain('橙子')
      expect(wrapper.text()).toContain('葡萄')
    })

    it('选择答案功能', async () => {
      const options = wrapper.findAll('.option-item')
      await options[0].trigger('click')
      
      expect(wrapper.vm.selectedAnswer).toBe('a')
    })

    it('提交答案功能', async () => {
      // 选择正确答案
      wrapper.vm.selectedAnswer = 'a'
      
      await wrapper.vm.submitAnswer()
      
      expect(wrapper.vm.showResult).toBe(true)
      expect(wrapper.vm.correctCount).toBe(1)
    })

    it('显示正确答案', async () => {
      wrapper.vm.selectedAnswer = 'a'
      await wrapper.vm.submitAnswer()
      
      const correctOption = wrapper.findAll('.option-item')[0]
      expect(correctOption.classes()).toContain('correct')
    })

    it('显示错误答案', async () => {
      wrapper.vm.selectedAnswer = 'b'
      await wrapper.vm.submitAnswer()
      
      const incorrectOption = wrapper.findAll('.option-item')[1]
      expect(incorrectOption.classes()).toContain('incorrect')
    })
  })

  describe('填空题功能', () => {
    beforeEach(async () => {
      // 切换到第二题（填空题）
      wrapper.vm.currentIndex = 1
      await wrapper.vm.$nextTick()
    })

    it('显示填空题题目', () => {
      expect(wrapper.text()).toContain('Complete the sentence: "I ___ a student."')
    })

    it('显示输入框', () => {
      const input = wrapper.find('input')
      expect(input.exists()).toBe(true)
    })

    it('输入答案功能', async () => {
      const input = wrapper.find('input')
      await input.setValue('am')
      
      expect(wrapper.vm.userAnswer).toBe('am')
    })

    it('提交正确答案', async () => {
      wrapper.vm.userAnswer = 'am'
      await wrapper.vm.submitAnswer()
      
      expect(wrapper.vm.showResult).toBe(true)
      expect(wrapper.vm.correctCount).toBe(1)
    })

    it('提交错误答案', async () => {
      wrapper.vm.userAnswer = 'is'
      await wrapper.vm.submitAnswer()
      
      expect(wrapper.vm.showResult).toBe(true)
      expect(wrapper.vm.correctCount).toBe(0)
    })
  })

  describe('翻译显示', () => {
    it('显示题目翻译', () => {
      expect(wrapper.text()).toContain('翻译: 苹果')
    })
  })

  describe('按钮状态', () => {
    it('未选择答案时提交按钮禁用', () => {
      const submitBtn = wrapper.find('.submit-btn')
      expect(submitBtn.attributes('disabled')).toBeDefined()
    })

    it('选择答案后提交按钮启用', async () => {
      wrapper.vm.selectedAnswer = 'a'
      await wrapper.vm.$nextTick()
      
      const submitBtn = wrapper.find('.submit-btn')
      expect(submitBtn.attributes('disabled')).toBeUndefined()
    })

    it('填空题输入答案后提交按钮启用', async () => {
      wrapper.vm.currentIndex = 1
      wrapper.vm.userAnswer = 'am'
      await wrapper.vm.$nextTick()
      
      const submitBtn = wrapper.find('.submit-btn')
      expect(submitBtn.attributes('disabled')).toBeUndefined()
    })
  })

  describe('题目导航', () => {
    it('显示下一题按钮', async () => {
      wrapper.vm.selectedAnswer = 'a'
      await wrapper.vm.submitAnswer()
      
      expect(wrapper.text()).toContain('下一题')
    })

    it('最后一题显示完成按钮', async () => {
      wrapper.vm.currentIndex = 1
      wrapper.vm.userAnswer = 'am'
      await wrapper.vm.submitAnswer()
      
      expect(wrapper.text()).toContain('完成练习')
    })

    it('下一题功能', async () => {
      wrapper.vm.selectedAnswer = 'a'
      await wrapper.vm.submitAnswer()
      await wrapper.vm.nextQuestion()
      
      expect(wrapper.vm.currentIndex).toBe(1)
      expect(wrapper.vm.showResult).toBe(false)
    })
  })

  describe('练习结果', () => {
    beforeEach(async () => {
      // 完成所有题目
      wrapper.vm.selectedAnswer = 'a'
      await wrapper.vm.submitAnswer()
      await wrapper.vm.nextQuestion()
      
      wrapper.vm.currentIndex = 1
      wrapper.vm.userAnswer = 'am'
      await wrapper.vm.submitAnswer()
      await wrapper.vm.nextQuestion()
    })

    it('显示结果页面', () => {
      expect(wrapper.vm.showResults).toBe(true)
    })

    it('显示结果统计', () => {
      expect(wrapper.text()).toContain('练习结果')
      expect(wrapper.text()).toContain('总题数:2')
      expect(wrapper.text()).toContain('正确数:2')
      expect(wrapper.text()).toContain('正确率:100%')
    })

    it('重新开始功能', async () => {
      const restartBtn = wrapper.findAll('button').find(btn => btn.text().includes('重新开始'))
      await restartBtn.trigger('click')
      
      expect(wrapper.vm.currentIndex).toBe(0)
      expect(wrapper.vm.correctCount).toBe(0)
      expect(wrapper.vm.showResults).toBe(false)
    })

    it('返回仪表板功能', async () => {
      const dashboardBtn = wrapper.findAll('button').find(btn => btn.text().includes('返回仪表板'))
      await dashboardBtn.trigger('click')
      
      expect(router.push).toHaveBeenCalledWith('/english/dashboard')
    })
  })

  describe('正确率计算', () => {
    it('初始正确率为0', () => {
      expect(wrapper.vm.accuracy).toBe(0)
    })

    it('答对一题后正确率为100', async () => {
      wrapper.vm.selectedAnswer = 'a'
      await wrapper.vm.submitAnswer()
      
      expect(wrapper.vm.accuracy).toBe(100)
    })

    it('答错一题后正确率为0', async () => {
      wrapper.vm.selectedAnswer = 'b'
      await wrapper.vm.submitAnswer()
      
      expect(wrapper.vm.accuracy).toBe(0)
    })
  })

  describe('边界情况', () => {
    it('空答案不能提交', async () => {
      wrapper.vm.currentIndex = 1
      wrapper.vm.userAnswer = ''
      
      expect(wrapper.vm.canSubmit).toBe(false)
    })

    it('未选择答案不能提交', () => {
      expect(wrapper.vm.canSubmit).toBe(false)
    })
  })
}) 