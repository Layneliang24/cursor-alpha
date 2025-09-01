import { describe, it, expect } from 'vitest'
import { formatDate, formatDateTime, formatRelativeTime, parseDate } from '@/utils/dateUtils'

describe('Date Utils', () => {
  const testDate = new Date('2024-01-15T10:30:00Z')
  const now = new Date('2024-01-15T12:00:00Z')

  describe('formatDate', () => {
    it('should format date correctly', () => {
      const result = formatDate(testDate)
      expect(result).toBe('2024-01-15')
    })

    it('should handle string date input', () => {
      const result = formatDate('2024-01-15T10:30:00Z')
      expect(result).toBe('2024-01-15')
    })

    it('should handle null input', () => {
      const result = formatDate(null)
      expect(result).toBe('')
    })

    it('should handle invalid date input', () => {
      const result = formatDate('invalid-date')
      expect(result).toBe('')
    })
  })

  describe('formatDateTime', () => {
    it('should format date and time correctly', () => {
      const result = formatDateTime(testDate)
      expect(result).toMatch(/2024-01-15 \d{2}:\d{2}:\d{2}/)
    })

    it('should handle string date input', () => {
      const result = formatDateTime('2024-01-15T10:30:00Z')
      expect(result).toMatch(/2024-01-15 \d{2}:\d{2}:\d{2}/)
    })

    it('should handle null input', () => {
      const result = formatDateTime(null)
      expect(result).toBe('')
    })
  })

  describe('formatRelativeTime', () => {
    beforeEach(() => {
      // Mock current time
      vi.useFakeTimers()
      vi.setSystemTime(now)
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should format relative time for recent dates', () => {
      const recentDate = new Date('2024-01-15T11:55:00Z') // 5 minutes ago
      const result = formatRelativeTime(recentDate)
      expect(result).toBe('5分钟前')
    })

    it('should format relative time for hours ago', () => {
      const hoursAgo = new Date('2024-01-15T09:00:00Z') // 3 hours ago
      const result = formatRelativeTime(hoursAgo)
      expect(result).toBe('3小时前')
    })

    it('should format relative time for days ago', () => {
      const daysAgo = new Date('2024-01-13T12:00:00Z') // 2 days ago
      const result = formatRelativeTime(daysAgo)
      expect(result).toBe('2天前')
    })

    it('should format relative time for future dates', () => {
      const futureDate = new Date('2024-01-16T12:00:00Z') // 1 day later
      const result = formatRelativeTime(futureDate)
      expect(result).toBe('1天后')
    })

    it('should handle null input', () => {
      const result = formatRelativeTime(null)
      expect(result).toBe('')
    })
  })

  describe('parseDate', () => {
    it('should parse valid date string', () => {
      const result = parseDate('2024-01-15')
      expect(result).toBeInstanceOf(Date)
      expect(result.getFullYear()).toBe(2024)
      expect(result.getMonth()).toBe(0) // January
      expect(result.getDate()).toBe(15)
    })

    it('should parse ISO date string', () => {
      const result = parseDate('2024-01-15T10:30:00Z')
      expect(result).toBeInstanceOf(Date)
    })

    it('should handle null input', () => {
      const result = parseDate(null)
      expect(result).toBeNull()
    })

    it('should handle invalid date string', () => {
      const result = parseDate('invalid-date')
      expect(result).toBeNull()
    })

    it('should handle empty string', () => {
      const result = parseDate('')
      expect(result).toBeNull()
    })
  })

  describe('Edge Cases', () => {
    it('should handle different date formats', () => {
      const formats = [
        '2024-01-15',
        '2024/01/15',
        '15/01/2024',
        '2024-01-15T10:30:00Z',
        '2024-01-15T10:30:00.000Z'
      ]

      formats.forEach(format => {
        const parsed = parseDate(format)
        if (parsed) {
          expect(parsed).toBeInstanceOf(Date)
        }
      })
    })

    it('should handle timezone differences', () => {
      const utcDate = new Date('2024-01-15T10:30:00Z')
      const localDate = new Date('2024-01-15T10:30:00')
      
      const utcFormatted = formatDate(utcDate)
      const localFormatted = formatDate(localDate)
      
      // Both should format to the same date string
      expect(utcFormatted).toBe(localFormatted)
    })
  })
})
