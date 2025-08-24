import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTypingStore } from '../typing'

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    warning: vi.fn(),
    error: vi.fn()
  }
}))

// Mock API
vi.mock('@/api/english', () => ({
  englishAPI: {
    getTypingWords: vi.fn(),
    getTypingWordsByDictionary: vi.fn(),
    submitTypingPractice: vi.fn(),
    getTypingStats: vi.fn(),
    getTypingDailyProgress: vi.fn(),
    getDictionaries: vi.fn()
  }
}))

// Mock window functions
Object.defineProperty(window, 'playCorrectSound', {
  value: vi.fn(),
  writable: true
})

Object.defineProperty(window, 'playWrongSound', {
  value: vi.fn(),
  writable: true
})

Object.defineProperty(window, 'playCurrentWordPronunciation', {
  value: vi.fn(),
  writable: true
})

describe('QWERTY Learner 逻辑测试', () => {
  let store: ReturnType<typeof useTypingStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useTypingStore()
  })

  describe('正确率计算 - 照搬 QWERTY Learner 逻辑', () => {
    it('应该基于单词级别计算正确率', () => {
      // 设置测试数据
      store.words = [
        { id: 1, word: 'hello' },
        { id: 2, word: 'world' },
        { id: 3, word: 'test' }
      ]
      
      // 模拟用户完成了3个单词，其中2个有错误但最终完成
      store.correctCount = 3  // 3个单词都完成了
      store.answeredCount = 3 // 3个单词都回答了
      
      // 正确率应该是 100% (3/3)
      expect(store.correctRate).toBe(100)
    })

    it('应该在有错误的情况下仍然显示100%正确率（如果单词完成）', () => {
      // 设置测试数据
      store.words = [
        { id: 1, word: 'hello' },
        { id: 2, word: 'world' }
      ]
      
      // 模拟用户完成了2个单词，但都有按键错误
      store.correctCount = 2  // 2个单词都完成了
      store.answeredCount = 2 // 2个单词都回答了
      
      // 即使有按键错误，正确率仍然是 100% (2/2)
      // 这是 QWERTY Learner 的核心逻辑：关注单词完成，不关注字符错误
      expect(store.correctRate).toBe(100)
    })

         it('应该在部分完成的情况下显示正确的正确率', () => {
       // 设置测试数据
       store.words = [
         { id: 1, word: 'hello' },
         { id: 2, word: 'world' },
         { id: 3, word: 'test' }
       ]
       
       // 模拟用户完成了2个单词，跳过了1个
       store.correctCount = 2  // 2个单词完成
       store.answeredCount = 3 // 3个单词都处理了（包括跳过）
       
       // 正确率应该是 66.67% (2/3)
       expect(store.correctRate).toBe(67)
     })

     it('应该在跳过单词的情况下显示正确的正确率', () => {
       // 设置测试数据
       store.words = [
         { id: 1, word: 'hello' },
         { id: 2, word: 'world' },
         { id: 3, word: 'test' }
       ]
       
       // 模拟用户完成了1个单词，跳过了2个
       store.correctCount = 1  // 1个单词完成
       store.answeredCount = 3 // 3个单词都处理了（包括跳过）
       
       // 正确率应该是 33.33% (1/3)
       expect(store.correctRate).toBe(33)
     })

    it('应该在没有任何单词的情况下显示0%正确率', () => {
      store.correctCount = 0
      store.answeredCount = 0
      
      expect(store.correctRate).toBe(0)
    })
  })

  describe('按键错误记录 - QWERTY Learner 风格', () => {
    it('应该记录目标字符作为错误键（用于热力图）', () => {
      // 初始化单词状态
      store.words = [{ id: 1, word: 'hello' }]
      store.initWordState(store.words[0])
      
      // 用户应该按 'h'，但按了 'x'
      store.handleKeyInput('x')
      
      // 应该记录目标字符 'h' 作为错误键
      expect(store.keyMistakes.h).toBeDefined()
      expect(store.keyMistakes.h).toContain('h')
      expect(store.cumulativeKeyMistakes.h).toContain('h')
    })

    it('应该允许错误后继续输入', () => {
      // 初始化单词状态
      store.words = [{ id: 1, word: 'hello' }]
      store.initWordState(store.words[0])
      
      // 第1个字符错误
      store.handleKeyInput('x') // 应该是 'h'，但按了 'x'
      
      // 第1个字符再次错误
      store.handleKeyInput('y') // 还是应该是 'h'，但按了 'y'
      
      // 第1个字符正确
      store.handleKeyInput('h') // 终于按对了
      
      // 验证错误记录
      expect(store.keyMistakes.h).toHaveLength(2) // 2次错误
      expect(store.cumulativeKeyMistakes.h).toHaveLength(2)
      
      // 验证可以继续输入
      expect(store.wordState.inputWord).toBe('h')
      expect(store.wordState.letterStates[0]).toBe('correct')
    })

    it('应该在单词完成时保持100%正确率（即使有错误）', () => {
      // 初始化单词状态
      store.words = [{ id: 1, word: 'hi' }]
      store.initWordState(store.words[0])
      
      // 第1个字符错误
      store.handleKeyInput('x') // 应该是 'h'，但按了 'x'
      
      // 第1个字符正确
      store.handleKeyInput('h')
      
      // 第2个字符正确
      store.handleKeyInput('i')
      
      // 单词完成，应该触发完成逻辑
      expect(store.wordState.isFinished).toBe(true)
      
      // 正确率应该是 100%（因为单词完成了）
      expect(store.correctRate).toBe(100)
    })
  })

     describe('业务逻辑 - QWERTY Learner 风格', () => {
     it('应该允许跳过单词', () => {
       // 初始化单词状态
       store.words = [{ id: 1, word: 'hello' }]
       store.initWordState(store.words[0])
       
       // 用户输入了部分内容
       store.handleKeyInput('h')
       store.handleKeyInput('e')
       
       // 跳过当前单词
       store.skipWord()
       
       // 应该进入下一个单词
       expect(store.currentWordIndex).toBe(1)
       // 跳过不算正确，但算回答
       expect(store.correctCount).toBe(0)
       expect(store.answeredCount).toBe(1)
       expect(store.correctRate).toBe(0)
     })

     it('应该允许单词完成时存在按键错误', () => {
      // 初始化单词状态
      store.words = [{ id: 1, word: 'hello' }]
      store.initWordState(store.words[0])
      
      // 模拟多次错误后完成
      store.handleKeyInput('x') // 错误
      store.handleKeyInput('h') // 正确
      store.handleKeyInput('y') // 错误
      store.handleKeyInput('e') // 正确
      store.handleKeyInput('z') // 错误
      store.handleKeyInput('l') // 正确
      store.handleKeyInput('l') // 正确
      store.handleKeyInput('o') // 正确
      
      // 单词应该完成
      expect(store.wordState.isFinished).toBe(true)
      expect(store.wordState.inputWord).toBe('hello')
      
      // 即使有3次按键错误，单词完成也算正确
      expect(store.correctCount).toBe(1)
      expect(store.answeredCount).toBe(1)
      expect(store.correctRate).toBe(100)
    })

    it('应该正确统计按键错误用于热力图显示', () => {
      // 初始化单词状态
      store.words = [{ id: 1, word: 'hello' }]
      store.initWordState(store.words[0])
      
      // 模拟错误模式
      store.handleKeyInput('x') // 应该是 'h'
      store.handleKeyInput('h') // 正确
      store.handleKeyInput('y') // 应该是 'e'
      store.handleKeyInput('e') // 正确
      store.handleKeyInput('l') // 正确
      store.handleKeyInput('l') // 正确
      store.handleKeyInput('o') // 正确
      
      // 验证错误记录
      expect(store.keyMistakes.h).toHaveLength(1) // 'h' 键错误1次
      expect(store.keyMistakes.e).toHaveLength(1) // 'e' 键错误1次
      
      // 验证累积记录
      expect(store.cumulativeKeyMistakes.h).toHaveLength(1)
      expect(store.cumulativeKeyMistakes.e).toHaveLength(1)
      
      // 单词完成
      expect(store.wordState.isFinished).toBe(true)
      expect(store.correctRate).toBe(100)
    })
  })
}) 