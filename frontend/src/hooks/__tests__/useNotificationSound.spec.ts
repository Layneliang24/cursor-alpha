import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useNotificationSound } from '../useNotificationSound'

// Mock @vueuse/sound
const mockPlay = vi.fn()
const mockStop = vi.fn()

vi.mock('@vueuse/sound', () => ({
  useSound: vi.fn(() => ({
    play: mockPlay,
    stop: mockStop
  }))
}))

describe('useNotificationSound', () => {
  let notificationSound: ReturnType<typeof useNotificationSound>

  beforeEach(() => {
    vi.clearAllMocks()
    notificationSound = useNotificationSound()
  })

  describe('notify', () => {
    it('应该播放通知声音', () => {
      notificationSound.notify()
      expect(mockPlay).toHaveBeenCalledTimes(1)
    })
  })

  describe('confirm', () => {
    it('应该播放确认声音', () => {
      notificationSound.confirm()
      expect(mockPlay).toHaveBeenCalledTimes(1)
    })
  })

  describe('alert', () => {
    it('应该播放警告声音', () => {
      notificationSound.alert()
      expect(mockPlay).toHaveBeenCalledTimes(1)
    })
  })

  describe('urgent', () => {
    it('应该连续播放多次警告声音', () => {
      vi.useFakeTimers()
      notificationSound.urgent(3)
      
      expect(mockPlay).toHaveBeenCalledTimes(1)
      
      vi.advanceTimersByTime(500)
      expect(mockPlay).toHaveBeenCalledTimes(2)
      
      vi.advanceTimersByTime(500)
      expect(mockPlay).toHaveBeenCalledTimes(3)
      
      vi.advanceTimersByTime(500)
      expect(mockPlay).toHaveBeenCalledTimes(3) // 不再增加
      
      vi.useRealTimers()
    })

    it('应该使用默认次数3次', () => {
      vi.useFakeTimers()
      notificationSound.urgent()
      
      expect(mockPlay).toHaveBeenCalledTimes(1)
      
      vi.advanceTimersByTime(1500) // 3次 * 500ms
      expect(mockPlay).toHaveBeenCalledTimes(3)
      
      vi.useRealTimers()
    })
  })

  describe('stopAll', () => {
    it('应该停止所有声音', () => {
      notificationSound.stopAll()
      expect(mockStop).toHaveBeenCalledTimes(3) // 三个声音都停止
    })
  })
}) 