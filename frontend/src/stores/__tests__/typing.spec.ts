import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTypingStore } from '../typing'

// Mock API
vi.mock('@/api/english', () => ({
  englishAPI: {
    submitTypingPractice: vi.fn(),
    getTypingStats: vi.fn(),
    getTypingDailyProgress: vi.fn(),
    getTypingWords: vi.fn(),
    getTypingWordsByDictionary: vi.fn(),
    getDictionaries: vi.fn()
  }
}))

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  }
}))

describe('Typing Store', () => {
  let store: any

  beforeEach(() => {
    const pinia = createPinia()
    setActivePinia(pinia)
    store = useTypingStore()
    
    // 清理所有 mock
    vi.clearAllMocks()
    
    // Mock window 对象
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
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('按键错误记录', () => {
    it('应该正确记录按键错误', async () => {
      // 模拟单词状态
      store.wordState.displayWord = 'hello'
      store.wordState.inputWord = ''
      store.wordState.letterStates = new Array(5).fill('normal')
      
      // 模拟输入错误按键 'x'，但应该按 'h'
      store.handleKeyInput('x')
      
      // 验证按键错误被记录（应该记录目标字符 'h'，而不是用户按的 'x'）
      expect(store.keyMistakes.h).toBeDefined()
      expect(store.keyMistakes.h).toContain('h')
      
      // 新逻辑：错误后先显示错误状态，然后延迟重置
      // 立即检查：应该显示错误状态
      expect(store.wordState.hasWrong).toBe(true)
      // 只有敲错的字母位置显示为错误状态，其他字母保持正常状态
      expect(store.wordState.letterStates[0]).toBe('wrong') // 第0个位置（'h'）应该显示为错误
      expect(store.wordState.letterStates.slice(1)).toEqual(new Array(4).fill('normal')) // 其他位置保持正常
      expect(store.wordState.shake).toBe(true)
      
      // 等待延迟重置完成
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 延迟后检查：状态应该被重置
      expect(store.wordState.hasWrong).toBe(false)
      expect(store.wordState.inputWord).toBe('')
      expect(store.wordState.letterStates).toEqual(new Array(5).fill('normal'))
      expect(store.wordState.shake).toBe(false)
    })

    it('应该记录多个按键错误', () => {
      // 模拟单词状态
      store.wordState.displayWord = 'hello'
      store.wordState.inputWord = ''
      store.wordState.letterStates = new Array(5).fill('normal')
      
      // 模拟多次输入错误，但每次都在同一个位置
      // 第1个字符应该是 'h'，用户按了 'x'
      store.handleKeyInput('x')
      // 第1个字符还是 'h'，用户又按了 'y'
      store.handleKeyInput('y')
      // 第1个字符还是 'h'，用户又按了 'z'
      store.handleKeyInput('z')
      
      // 验证多个按键错误被记录（记录目标字符）
      expect(store.keyMistakes.h).toContain('h')
      expect(store.keyMistakes.h).toHaveLength(3) // 3次错误都在同一个字符上
    })

    it('应该计算正确的错误总数', () => {
      // 模拟按键错误
      store.keyMistakes = {
        'x': ['x', 'x'],
        'y': ['y'],
        'z': ['z', 'z', 'z']
      }
      
      // 验证错误总数计算
      const totalErrors = (Object.values(store.keyMistakes) as string[][]).reduce(
        (total: number, mistakes: string[]) => total + mistakes.length, 
        0
      )
      expect(totalErrors).toBe(6)
    })

    it('重置练习时应该清空按键错误记录', () => {
      // 模拟按键错误
      store.keyMistakes = {
        'x': ['x', 'x'],
        'y': ['y']
      }
      
      // 重置练习
      store.resetPractice()
      
      // 验证按键错误记录被清空
      expect(store.keyMistakes).toEqual({})
    })
  })

  describe('数据提交', () => {
    it('提交数据时应该包含按键错误信息', async () => {
      // 模拟按键错误
      store.keyMistakes = {
        'x': ['x', 'x'],
        'y': ['y']
      }
      
      // 模拟当前单词
      store.words = [{ id: 1, word: 'hello' }]
      store.currentWordIndex = 0
      store.wordStartTime = Date.now()
      
      // Mock API 响应
      const { englishAPI } = await import('@/api/english')
      englishAPI.submitTypingPractice.mockResolvedValue({ success: true })
      
      // 提交数据
      await store.submitWordResult()
      
      // 验证API调用包含按键错误数据
      expect(englishAPI.submitTypingPractice).toHaveBeenCalledWith(
        expect.objectContaining({
          mistakes: { 'x': ['x', 'x'], 'y': ['y'] },
          wrong_count: 3
        })
      )
    })
  })
}) 