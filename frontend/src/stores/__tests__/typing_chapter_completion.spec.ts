import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTypingStore } from '../typing'

describe('章节完成功能测试', () => {
  let store: ReturnType<typeof useTypingStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useTypingStore()
  })

  describe('章节完成状态管理', () => {
    it('应该正确初始化章节完成状态', () => {
      expect(store.chapterCompleted).toBe(false)
      expect(store.chapterCompletionData).toBeNull()
    })

    it('应该能够标记章节为完成状态', () => {
      const mockCompletionData = {
        accuracy: 85,
        practiceTime: 120,
        wpm: 45,
        wrongWords: ['apple', 'banana'],
        dictionary: 'TOEFL',
        chapter: 1
      }

      store.markChapterCompleted(mockCompletionData)

      expect(store.chapterCompleted).toBe(true)
      expect(store.chapterCompletionData).toEqual(mockCompletionData)
    })

    it('应该能够重置章节完成状态', () => {
      // 先设置完成状态
      store.markChapterCompleted({
        accuracy: 90,
        practiceTime: 100,
        wpm: 50,
        wrongWords: [],
        dictionary: 'TOEFL',
        chapter: 1
      })

      // 重置状态
      store.resetChapterCompletion()

      expect(store.chapterCompleted).toBe(false)
      expect(store.chapterCompletionData).toBeNull()
    })
  })

  describe('章节练习次数统计', () => {
    it('应该正确初始化章节练习次数', () => {
      expect(store.chapterPracticeStats).toEqual({})
    })

    it('应该能够增加章节练习次数', () => {
      store.incrementChapterPracticeCount('test', 1)
      expect(store.getChapterPracticeCount('test', 1)).toBe(1)

      store.incrementChapterPracticeCount('test', 1)
      expect(store.getChapterPracticeCount('test', 1)).toBe(2)
    })

    it('应该能够获取章节练习次数显示文本', () => {
      // 先设置一些测试数据
      store.incrementChapterPracticeCount('test', 1)
      store.incrementChapterPracticeCount('test', 1) // 章节1增加2次
      store.incrementChapterPracticeCount('test', 50)
      store.incrementChapterPracticeCount('test', 999)
      store.incrementChapterPracticeCount('test', 1000)
      store.incrementChapterPracticeCount('test', 1500)
      
      // 测试不同次数范围的显示
      expect(store.getChapterPracticeCountDisplay('test', 0)).toBe('0')
      expect(store.getChapterPracticeCountDisplay('test', 1)).toBe('2') // 章节1有2次练习
      expect(store.getChapterPracticeCountDisplay('test', 50)).toBe('1')
      expect(store.getChapterPracticeCountDisplay('test', 999)).toBe('1')
      expect(store.getChapterPracticeCountDisplay('test', 1000)).toBe('1')
      expect(store.getChapterPracticeCountDisplay('test', 1500)).toBe('1')
    })

    it('应该能够重置特定章节的练习次数', () => {
      store.incrementChapterPracticeCount('test', 1)
      store.incrementChapterPracticeCount('test', 1)
      expect(store.getChapterPracticeCount('test', 1)).toBe(2)

      store.resetChapterPracticeCount('test', 1)
      expect(store.getChapterPracticeCount('test', 1)).toBe(0)
    })
  })

  describe('错题本功能', () => {
    it('应该正确初始化错题本', () => {
      expect(store.wrongWordsNotebook).toEqual([])
    })

    it('应该能够添加错误单词到错题本', () => {
      const wrongWord = {
        word: 'apple',
        translation: '苹果',
        dictionary: 'TOEFL',
        chapter: 1,
        errorCount: 1,
        lastErrorTime: new Date().toISOString()
      }

      store.addWrongWord(wrongWord)

      expect(store.wrongWordsNotebook).toHaveLength(1)
      expect(store.wrongWordsNotebook[0]).toEqual(wrongWord)
    })

    it('应该能够更新已存在单词的错误次数', () => {
      const wrongWord = {
        word: 'apple',
        translation: '苹果',
        dictionary: 'TOEFL',
        chapter: 1,
        errorCount: 1,
        lastErrorTime: new Date().toISOString()
      }

      store.addWrongWord(wrongWord)
      store.addWrongWord(wrongWord)

      expect(store.wrongWordsNotebook).toHaveLength(1)
      expect(store.wrongWordsNotebook[0].errorCount).toBe(2)
    })

    it('应该能够删除错题本中的单词', () => {
      const wrongWord = {
        word: 'apple',
        translation: '苹果',
        dictionary: 'TOEFL',
        chapter: 1,
        errorCount: 1,
        lastErrorTime: new Date().toISOString()
      }

      store.addWrongWord(wrongWord)
      expect(store.wrongWordsNotebook).toHaveLength(1)

      store.removeWrongWord('apple')
      expect(store.wrongWordsNotebook).toHaveLength(0)
    })

    it('应该能够清空错题本', () => {
      const wrongWord1 = {
        word: 'apple',
        translation: '苹果',
        dictionary: 'TOEFL',
        chapter: 1,
        errorCount: 1,
        lastErrorTime: new Date().toISOString()
      }

      const wrongWord2 = {
        word: 'banana',
        translation: '香蕉',
        dictionary: 'TOEFL',
        chapter: 1,
        errorCount: 1,
        lastErrorTime: new Date().toISOString()
      }

      store.addWrongWord(wrongWord1)
      store.addWrongWord(wrongWord2)
      expect(store.wrongWordsNotebook).toHaveLength(2)

      store.clearWrongWordsNotebook()
      expect(store.wrongWordsNotebook).toHaveLength(0)
    })

    it('应该能够获取错题本统计信息', () => {
      const wrongWord1 = {
        word: 'apple',
        translation: '苹果',
        dictionary: 'TOEFL',
        chapter: 1,
        errorCount: 2,
        lastErrorTime: new Date().toISOString()
      }

      const wrongWord2 = {
        word: 'banana',
        translation: '香蕉',
        dictionary: 'CET4',
        chapter: 2,
        errorCount: 1,
        lastErrorTime: new Date().toISOString()
      }

      store.addWrongWord(wrongWord1)
      store.addWrongWord(wrongWord2)

      const stats = store.getWrongWordsNotebookStats()
      expect(stats.totalWords).toBe(2)
      expect(stats.totalErrors).toBe(3)
      expect(stats.dictionaryCount).toBe(2)
    })
  })

  describe('每日练习时长统计', () => {
    it('应该正确初始化每日练习时长', () => {
      expect(store.dailyPracticeDuration).toBe(0)
      expect(store.dailyPracticeSessions).toEqual([])
    })

    it('应该能够记录练习会话时长', () => {
      const sessionDuration = 300 // 5分钟
      store.recordPracticeSession(sessionDuration)

      expect(store.dailyPracticeDuration).toBe(300)
      expect(store.dailyPracticeSessions).toHaveLength(1)
      expect(store.dailyPracticeSessions[0].duration).toBe(300)
    })

    it('应该能够累计多个练习会话的时长', () => {
      store.recordPracticeSession(300) // 5分钟
      store.recordPracticeSession(600) // 10分钟

      expect(store.dailyPracticeDuration).toBe(900)
      expect(store.dailyPracticeSessions).toHaveLength(2)
    })

    it('应该能够获取格式化的练习时长', () => {
      store.recordPracticeSession(3661) // 1小时1分1秒

      const formattedDuration = store.getFormattedDailyPracticeDuration()
      expect(formattedDuration).toBe('1小时1分1秒')
    })

    it('应该能够重置每日练习时长', () => {
      store.recordPracticeSession(300)
      expect(store.dailyPracticeDuration).toBe(300)

      store.resetDailyPracticeDuration()
      expect(store.dailyPracticeDuration).toBe(0)
      expect(store.dailyPracticeSessions).toHaveLength(0)
    })
  })

  describe('章节完成数据生成', () => {
    it('应该能够生成章节完成数据', () => {
      // 模拟练习数据
      store.letterStats.totalInputLetters = 100
      store.letterStats.totalCorrectLetters = 85
      store.letterStats.totalWrongLetters = 15
      store.sessionTime = 120
      store.selectedDictionary = { name: 'TOEFL', id: 1 }
      store.selectedChapter = 1

      const completionData = store.generateChapterCompletionData()

      expect(completionData.accuracy).toBe(85)
      expect(completionData.practiceTime).toBe(120)
      expect(completionData.wpm).toBeGreaterThan(0)
      expect(completionData.dictionary).toBe('TOEFL')
      expect(completionData.chapter).toBe(1)
    })

    it('应该能够计算正确的WPM', () => {
      store.letterStats.totalInputLetters = 100 // 总输入字母数
      store.letterStats.totalCorrectLetters = 100 // 20个单词（每5个字母算一个单词）
      store.sessionTime = 60 // 1分钟

      const completionData = store.generateChapterCompletionData()
      expect(completionData.wpm).toBe(20)
    })
  })
}) 