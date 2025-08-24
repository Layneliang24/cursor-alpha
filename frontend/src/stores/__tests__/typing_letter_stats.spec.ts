import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTypingStore } from '../typing'

describe('Typing Store - 字母级别统计', () => {
  let store: ReturnType<typeof useTypingStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useTypingStore()
    
    // 模拟单词数据
    store.words = [
      { id: 1, word: 'hello', phonetic: 'həˈloʊ', translation: '你好' },
      { id: 2, word: 'world', phonetic: 'wɜːrld', translation: '世界' }
    ]
  })

  describe('字母级别统计初始化', () => {
    it('应该正确初始化字母统计变量', () => {
      expect(store.letterStats.totalInputLetters).toBe(0)
      expect(store.letterStats.totalCorrectLetters).toBe(0)
      expect(store.letterStats.totalWrongLetters).toBe(0)
      expect(store.letterStats.currentWordInputLetters).toBe(0)
      expect(store.letterStats.currentWordCorrectLetters).toBe(0)
      expect(store.letterStats.currentWordWrongLetters).toBe(0)
    })

    it('应该正确初始化字母级别计算属性', () => {
      expect(store.totalInputLetters).toBe(0)
      expect(store.totalCorrectLetters).toBe(0)
      expect(store.totalWrongLetters).toBe(0)
      expect(store.currentWordInputLetters).toBe(0)
      expect(store.currentWordCorrectLetters).toBe(0)
      expect(store.currentWordWrongLetters).toBe(0)
    })
  })

  describe('正确输入字母统计', () => {
    it('应该正确记录正确输入的字母', () => {
      // 初始化单词状态
      store.initWordState(store.words[0])
      
      // 模拟正确输入 'h'
      store.handleKeyInput('h')
      
      // 验证统计
      expect(store.letterStats.totalInputLetters).toBe(1)
      expect(store.letterStats.totalCorrectLetters).toBe(1)
      expect(store.letterStats.currentWordInputLetters).toBe(1)
      expect(store.letterStats.currentWordCorrectLetters).toBe(1)
      expect(store.letterStats.totalWrongLetters).toBe(0)
      expect(store.letterStats.currentWordWrongLetters).toBe(0)
    })

    it('应该正确记录多个正确输入的字母', () => {
      // 初始化单词状态
      store.initWordState(store.words[0])
      
      // 模拟正确输入 'h', 'e', 'l'
      store.handleKeyInput('h')
      store.handleKeyInput('e')
      store.handleKeyInput('l')
      
      // 验证统计
      expect(store.letterStats.totalInputLetters).toBe(3)
      expect(store.letterStats.totalCorrectLetters).toBe(3)
      expect(store.letterStats.currentWordInputLetters).toBe(3)
      expect(store.letterStats.currentWordCorrectLetters).toBe(3)
    })
  })

  describe('错误输入字母统计', () => {
    it('应该正确记录错误输入的字母', async () => {
      // 初始化单词状态
      store.initWordState(store.words[0])
      
      // 模拟错误输入 'x'（应该是 'h'）
      store.handleKeyInput('x')
      
      // 立即检查：应该记录错误
      expect(store.letterStats.totalInputLetters).toBe(1)
      expect(store.letterStats.totalWrongLetters).toBe(1)
      expect(store.letterStats.currentWordInputLetters).toBe(1)
      expect(store.letterStats.currentWordWrongLetters).toBe(1)
      expect(store.letterStats.totalCorrectLetters).toBe(0)
      expect(store.letterStats.currentWordCorrectLetters).toBe(0)
      
      // 等待延迟重置完成
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 延迟后检查：当前单词统计应该被重置
      expect(store.letterStats.currentWordInputLetters).toBe(0)
      expect(store.letterStats.currentWordCorrectLetters).toBe(0)
      expect(store.letterStats.currentWordWrongLetters).toBe(0)
      
      // 但总统计应该保持不变
      expect(store.letterStats.totalInputLetters).toBe(1)
      expect(store.letterStats.totalWrongLetters).toBe(1)
    })
  })

  describe('正确率计算', () => {
    it('应该基于字母级别计算正确率', () => {
      // 初始化单词状态
      store.initWordState(store.words[0])
      
      // 模拟输入：3个正确，1个错误
      store.handleKeyInput('h') // 正确
      store.handleKeyInput('e') // 正确
      store.handleKeyInput('l') // 正确
      store.handleKeyInput('x') // 错误（应该是 'l'）
      
      // 正确率 = (4 - 1) / 4 * 100 = 75%
      expect(store.letterAccuracy).toBe(75)
    })

    it('应该在没有输入时返回0%', () => {
      expect(store.letterAccuracy).toBe(0)
    })

    it('应该在全部正确时返回100%', () => {
      // 初始化单词状态
      store.initWordState(store.words[0])
      
      // 模拟全部正确输入
      store.handleKeyInput('h')
      store.handleKeyInput('e')
      store.handleKeyInput('l')
      store.handleKeyInput('l')
      store.handleKeyInput('o')
      
      expect(store.letterAccuracy).toBe(100)
    })
  })

  describe('统计重置', () => {
    it('应该正确重置所有字母统计', () => {
      // 初始化单词状态并输入一些字母
      store.initWordState(store.words[0])
      store.handleKeyInput('h')
      store.handleKeyInput('e')
      store.handleKeyInput('x') // 错误
      
      // 验证有数据
      expect(store.letterStats.totalInputLetters).toBeGreaterThan(0)
      expect(store.letterStats.totalWrongLetters).toBeGreaterThan(0)
      
      // 重置练习
      store.resetPractice()
      
      // 验证所有统计都被重置
      expect(store.letterStats.totalInputLetters).toBe(0)
      expect(store.letterStats.totalCorrectLetters).toBe(0)
      expect(store.letterStats.totalWrongLetters).toBe(0)
      expect(store.letterStats.currentWordInputLetters).toBe(0)
      expect(store.letterStats.currentWordCorrectLetters).toBe(0)
      expect(store.letterStats.currentWordWrongLetters).toBe(0)
    })

    it('应该在切换单词时重置当前单词统计', () => {
      // 初始化第一个单词并输入
      store.initWordState(store.words[0])
      store.handleKeyInput('h')
      store.handleKeyInput('e')
      
      // 验证当前单词统计
      expect(store.letterStats.currentWordInputLetters).toBe(2)
      expect(store.letterStats.currentWordCorrectLetters).toBe(2)
      
      // 初始化第二个单词
      store.initWordState(store.words[1])
      
      // 验证当前单词统计被重置
      expect(store.letterStats.currentWordInputLetters).toBe(0)
      expect(store.letterStats.currentWordCorrectLetters).toBe(0)
      expect(store.letterStats.currentWordWrongLetters).toBe(0)
      
      // 但总统计应该保持不变
      expect(store.letterStats.totalInputLetters).toBe(2)
      expect(store.letterStats.totalCorrectLetters).toBe(2)
    })
  })

  describe('WPM计算', () => {
    it('应该基于字母级别计算WPM', () => {
      // 模拟会话时间
      store.sessionTime = 60 // 1分钟
      
      // 模拟输入字母
      store.letterStats.totalInputLetters = 25 // 总输入字母数
      store.letterStats.totalCorrectLetters = 25 // 5个单词（每5个字母算一个单词）
      

      
      // WPM = 5个单词 / 1分钟 = 5
      expect(store.averageWPM).toBe(5)
    })
  })
}) 