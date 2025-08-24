import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTypingStore } from '../typing'

// Mock API
vi.mock('@/api/english', () => ({
  englishAPI: {
    getChapterStats: vi.fn(),
    updateChapterStats: vi.fn()
  }
}))

describe('章节练习次数统计功能测试', () => {
  let store: ReturnType<typeof useTypingStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useTypingStore()
    
    // 重置localStorage和mock
    localStorage.clear()
    vi.clearAllMocks()
  })

  describe('数据结构重构', () => {
    it('应该按词典+章节组合存储练习次数', () => {
      // 模拟不同词典的章节练习次数
      const mockStats = {
        'toefl': { 1: 3, 2: 1, 3: 0 },
        'ielts': { 1: 2, 2: 0, 3: 1 }
      }
      
      // 设置模拟数据
      store.setChapterPracticeStats(mockStats)
      
      // 验证数据结构
      expect(store.chapterPracticeStats).toEqual(mockStats)
    })

    it('应该能够获取特定词典特定章节的练习次数', () => {
      const mockStats = {
        'toefl': { 1: 3, 2: 1 },
        'ielts': { 1: 2, 2: 0 }
      }
      store.setChapterPracticeStats(mockStats)
      
      // 测试获取特定词典章节的练习次数
      expect(store.getChapterPracticeCount('toefl', 1)).toBe(3)
      expect(store.getChapterPracticeCount('toefl', 2)).toBe(1)
      expect(store.getChapterPracticeCount('ielts', 1)).toBe(2)
      expect(store.getChapterPracticeCount('ielts', 2)).toBe(0)
      
      // 测试不存在的词典或章节
      expect(store.getChapterPracticeCount('unknown', 1)).toBe(0)
      expect(store.getChapterPracticeCount('toefl', 99)).toBe(0)
    })
  })

  describe('练习次数更新', () => {
    it('应该能够增加特定词典特定章节的练习次数', () => {
      // 初始化数据
      store.setChapterPracticeStats({
        'toefl': { 1: 2, 2: 1 }
      })
      
      // 增加练习次数
      store.incrementChapterPracticeCount('toefl', 1)
      store.incrementChapterPracticeCount('toefl', 2)
      store.incrementChapterPracticeCount('ielts', 1) // 新词典新章节
      
      // 验证结果
      expect(store.getChapterPracticeCount('toefl', 1)).toBe(3)
      expect(store.getChapterPracticeCount('toefl', 2)).toBe(2)
      expect(store.getChapterPracticeCount('ielts', 1)).toBe(1)
    })

    it('应该能够重置特定词典特定章节的练习次数', () => {
      store.setChapterPracticeStats({
        'toefl': { 1: 5, 2: 3 }
      })
      
      // 重置练习次数
      store.resetChapterPracticeCount('toefl', 1)
      
      // 验证结果
      expect(store.getChapterPracticeCount('toefl', 1)).toBe(0)
      expect(store.getChapterPracticeCount('toefl', 2)).toBe(3) // 其他章节不受影响
    })
  })

  describe('显示格式', () => {
    it('应该正确格式化练习次数显示', () => {
      store.setChapterPracticeStats({
        'toefl': { 1: 5, 2: 150, 3: 999, 4: 1000 }
      })
      
      // 测试不同范围的数字
      expect(store.getChapterPracticeCountDisplay('toefl', 1)).toBe('5')
      expect(store.getChapterPracticeCountDisplay('toefl', 2)).toBe('150')
      expect(store.getChapterPracticeCountDisplay('toefl', 3)).toBe('999')
      expect(store.getChapterPracticeCountDisplay('toefl', 4)).toBe('999+')
    })
  })

  describe('数据持久化', () => {
    it('应该能够保存和加载练习次数数据', () => {
      const mockStats = {
        'toefl': { 1: 3, 2: 1 },
        'ielts': { 1: 2, 2: 0 }
      }
      
      // 保存数据
      store.setChapterPracticeStats(mockStats)
      store.saveChapterPracticeStats()
      
      // 清空内存数据（直接修改ref值）
      store.chapterPracticeStats.value = {}
      
      // 重新加载数据
      store.loadChapterPracticeStats()
      
      // 验证数据恢复（注意：loadFromStorage使用typing_Stats).toEqual(mockStats)
    })
  })

  describe('API集成', () => {
    it('应该能够从API获取练习次数数据', async () => {
      const mockApiResponse = {
        'toefl': { 1: 3, 2: 1 },
        'ielts': { 1: 2, 2: 0 }
      }
      
      // Mock API调用
      const { englishAPI } = await import('@/api/english')
      vi.mocked(englishAPI.getChapterStats).mockResolvedValue(mockApiResponse)
      
      // 调用API获取数据
      await store.fetchChapterPracticeStats()
      
      // 验证数据
      expect(store.chapterPracticeStats).toEqual(mockApiResponse)
      expect(englishAPI.getChapterStats).toHaveBeenCalled()
    })

    it('应该能够向API提交练习次数更新', async () => {
      const mockStats = {
        'toefl': { 1: 3, 2: 1 }
      }
      
      // Mock API调用
      const { englishAPI } = await import('@/api/english')
      vi.mocked(englishAPI.updateChapterStats).mockResolvedValue({ success: true })
      
      // 设置数据并提交
      store.setChapterPracticeStats(mockStats)
      await store.submitChapterPracticeStats()
      
      // 验证API调用
      expect(englishAPI.updateChapterStats).toHaveBeenCalledWith(mockStats)
    })
  })

  describe('词典切换处理', () => {
    it('切换词典时应该加载对应的章节练习次数', async () => {
      // 模拟不同词典的数据
      const toeflStats = { 'toefl': { 1: 3, 2: 1 } }
      const ieltsStats = { 'ielts': { 1: 2, 2: 0 } }
      
      // Mock API调用
      const { englishAPI } = await import('@/api/english')
      vi.mocked(englishAPI.getChapterStats)
        .mockResolvedValueOnce(toeflStats)
        .mockResolvedValueOnce(ieltsStats)
      
      // 切换到TOEFL词典
      await store.loadDictionaryChapterStats('toefl')
      expect(store.getChapterPracticeCount('toefl', 1)).toBe(3)
      
      // 切换到IELTS词典
      await store.loadDictionaryChapterStats('ielts')
      expect(store.getChapterPracticeCount('ielts', 1)).toBe(2)
      
      // 验证API调用次数（每次词典切换调用一次）
      expect(englishAPI.getChapterStats).toHaveBeenCalledTimes(2)
    })
  })
}) 