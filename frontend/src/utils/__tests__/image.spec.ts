import { describe, it, expect } from 'vitest'
import { getImageUrl, getDefaultAvatarUrl } from '../image.js'

describe('Image Utils', () => {
  describe('getImageUrl', () => {
    it('处理空值或undefined', () => {
      expect(getImageUrl('')).toBe('')
      expect(getImageUrl(null)).toBe('')
      expect(getImageUrl(undefined)).toBe('')
    })

    it('处理完整HTTP URL', () => {
      const httpUrl = 'http://example.com/image.jpg'
      expect(getImageUrl(httpUrl)).toBe(httpUrl)
    })

    it('处理完整HTTPS URL', () => {
      const httpsUrl = 'https://example.com/image.jpg'
      expect(getImageUrl(httpsUrl)).toBe(httpsUrl)
    })

    it('处理相对路径（以/开头）', () => {
      const relativePath = '/image.jpg'
      expect(getImageUrl(relativePath)).toBe('/media/image.jpg')
    })

    it('处理/media/开头的路径', () => {
      const mediaPath = '/media/avatars/user.jpg'
      expect(getImageUrl(mediaPath)).toBe(mediaPath)
    })

    it('处理文件名（不以/开头）', () => {
      const filename = 'avatar.jpg'
      expect(getImageUrl(filename)).toBe('/media/avatar.jpg')
    })

    it('处理复杂路径', () => {
      const complexPath = 'users/avatars/profile.png'
      expect(getImageUrl(complexPath)).toBe('/media/users/avatars/profile.png')
    })

    it('处理带查询参数的URL', () => {
      const urlWithParams = 'https://example.com/image.jpg?size=large&quality=high'
      expect(getImageUrl(urlWithParams)).toBe(urlWithParams)
    })

    it('处理带哈希的URL', () => {
      const urlWithHash = 'https://example.com/image.jpg#section'
      expect(getImageUrl(urlWithHash)).toBe(urlWithHash)
    })

    it('处理不同图片格式', () => {
      const jpgPath = 'photo.jpg'
      const pngPath = 'icon.png'
      const gifPath = 'animation.gif'
      const webpPath = 'image.webp'
      
      expect(getImageUrl(jpgPath)).toBe('/media/photo.jpg')
      expect(getImageUrl(pngPath)).toBe('/media/icon.png')
      expect(getImageUrl(gifPath)).toBe('/media/animation.gif')
      expect(getImageUrl(webpPath)).toBe('/media/image.webp')
    })
  })

  describe('getDefaultAvatarUrl', () => {
    it('返回有效的默认头像URL', () => {
      const avatarUrl = getDefaultAvatarUrl()
      
      expect(avatarUrl).toBeDefined()
      expect(typeof avatarUrl).toBe('string')
      expect(avatarUrl.length).toBeGreaterThan(0)
    })

    it('返回DiceBear API URL', () => {
      const avatarUrl = getDefaultAvatarUrl()
      
      expect(avatarUrl).toContain('api.dicebear.com')
      expect(avatarUrl).toContain('7.x')
      expect(avatarUrl).toContain('initials')
      expect(avatarUrl).toContain('svg')
    })

    it('包含正确的参数', () => {
      const avatarUrl = getDefaultAvatarUrl()
      
      expect(avatarUrl).toContain('seed=User')
      expect(avatarUrl).toContain('backgroundColor=667eea')
      expect(avatarUrl).toContain('textColor=ffffff')
    })

    it('URL格式正确', () => {
      const avatarUrl = getDefaultAvatarUrl()
      
      // 检查是否是有效的URL格式
      expect(avatarUrl).toMatch(/^https:\/\/[^\s]+$/)
    })
  })

  describe('边界情况处理', () => {
    it('处理特殊字符路径', () => {
      const specialPath = 'user@domain.com_avatar.jpg'
      expect(getImageUrl(specialPath)).toBe('/media/user@domain.com_avatar.jpg')
    })

    it('处理数字路径', () => {
      const numericPath = '12345.jpg'
      expect(getImageUrl(numericPath)).toBe('/media/12345.jpg')
    })

    it('处理空字符串路径', () => {
      expect(getImageUrl('')).toBe('')
    })

    it('处理只有空格的路径', () => {
      expect(getImageUrl('   ')).toBe('/media/   ')
    })

    it('处理非常长的路径', () => {
      const longPath = 'a'.repeat(1000) + '.jpg'
      expect(getImageUrl(longPath)).toBe('/media/' + longPath)
    })
  })

  describe('URL构建逻辑', () => {
    it('正确拼接API基础URL', () => {
      // 由于API_BASE_URL为空字符串，所以直接拼接/media/
      const testPath = 'test.jpg'
      const expected = '/media/test.jpg'
      
      expect(getImageUrl(testPath)).toBe(expected)
    })

    it('保持原始路径结构', () => {
      const nestedPath = 'users/profiles/avatar.jpg'
      const expected = '/media/users/profiles/avatar.jpg'
      
      expect(getImageUrl(nestedPath)).toBe(expected)
    })

    it('处理多层嵌套路径', () => {
      const deepPath = 'a/b/c/d/e/f/g/h/image.png'
      const expected = '/media/a/b/c/d/e/f/g/h/image.png'
      
      expect(getImageUrl(deepPath)).toBe(expected)
    })
  })
}) 