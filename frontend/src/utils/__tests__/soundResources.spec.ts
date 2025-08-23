import { describe, it, expect } from 'vitest'
import { 
  SOUND_URL_PREFIX, 
  KEY_SOUND_URL_PREFIX, 
  keySoundResources, 
  hintSoundResources, 
  generateWordSoundSrc, 
  defaultSounds 
} from '../soundResources.js'

describe('Sound Resources', () => {
  describe('常量定义', () => {
    it('定义了正确的声音URL前缀', () => {
      expect(SOUND_URL_PREFIX).toBe('/sounds/')
      expect(KEY_SOUND_URL_PREFIX).toBe('/sounds/keys/')
    })
  })

  describe('按键声音资源', () => {
    it('包含所有按键声音类型', () => {
      expect(keySoundResources).toHaveLength(3)
      
      const keys = keySoundResources.map(resource => resource.key)
      expect(keys).toContain('Default')
      expect(keys).toContain('Mechanical')
      expect(keys).toContain('Soft')
    })

    it('每个按键声音资源都有正确的结构', () => {
      keySoundResources.forEach(resource => {
        expect(resource).toHaveProperty('key')
        expect(resource).toHaveProperty('filename')
        expect(resource).toHaveProperty('name')
        expect(typeof resource.key).toBe('string')
        expect(typeof resource.filename).toBe('string')
        expect(typeof resource.name).toBe('string')
      })
    })

    it('默认按键声音配置正确', () => {
      const defaultKeySound = keySoundResources.find(r => r.key === 'Default')
      expect(defaultKeySound).toBeDefined()
      expect(defaultKeySound?.filename).toBe('key-default.wav')
      expect(defaultKeySound?.name).toBe('默认按键音')
    })

    it('机械键盘声音配置正确', () => {
      const mechanicalKeySound = keySoundResources.find(r => r.key === 'Mechanical')
      expect(mechanicalKeySound).toBeDefined()
      expect(mechanicalKeySound?.filename).toBe('key-mechanical.mp3')
      expect(mechanicalKeySound?.name).toBe('机械键盘音')
    })

    it('轻柔按键声音配置正确', () => {
      const softKeySound = keySoundResources.find(r => r.key === 'Soft')
      expect(softKeySound).toBeDefined()
      expect(softKeySound?.filename).toBe('key-soft.mp3')
      expect(softKeySound?.name).toBe('轻柔按键音')
    })
  })

  describe('提示声音资源', () => {
    it('包含所有提示声音类型', () => {
      expect(hintSoundResources).toHaveLength(3)
      
      const keys = hintSoundResources.map(resource => resource.key)
      expect(keys).toContain('Default')
      expect(keys).toContain('Correct')
      expect(keys).toContain('Wrong')
    })

    it('每个提示声音资源都有正确的结构', () => {
      hintSoundResources.forEach(resource => {
        expect(resource).toHaveProperty('key')
        expect(resource).toHaveProperty('filename')
        expect(resource).toHaveProperty('name')
        expect(typeof resource.key).toBe('string')
        expect(typeof resource.filename).toBe('string')
        expect(typeof resource.name).toBe('string')
      })
    })

    it('默认提示声音配置正确', () => {
      const defaultHintSound = hintSoundResources.find(r => r.key === 'Default')
      expect(defaultHintSound).toBeDefined()
      expect(defaultHintSound?.filename).toBe('hint-default.mp3')
      expect(defaultHintSound?.name).toBe('默认提示音')
    })

    it('正确提示声音配置正确', () => {
      const correctHintSound = hintSoundResources.find(r => r.key === 'Correct')
      expect(correctHintSound).toBeDefined()
      expect(correctHintSound?.filename).toBe('correct.wav')
      expect(correctHintSound?.name).toBe('正确提示音')
    })

    it('错误提示声音配置正确', () => {
      const wrongHintSound = hintSoundResources.find(r => r.key === 'Wrong')
      expect(wrongHintSound).toBeDefined()
      expect(wrongHintSound?.filename).toBe('beep.wav')
      expect(wrongHintSound?.name).toBe('错误提示音')
    })
  })

  describe('generateWordSoundSrc 函数', () => {
    it('生成美式发音URL', () => {
      const word = 'hello'
      const result = generateWordSoundSrc(word, 'us')
      const expected = 'https://dict.youdao.com/dictvoice?audio=hello&type=2'
      expect(result).toBe(expected)
    })

    it('生成英式发音URL', () => {
      const word = 'world'
      const result = generateWordSoundSrc(word, 'uk')
      const expected = 'https://dict.youdao.com/dictvoice?audio=world&type=1'
      expect(result).toBe(expected)
    })

    it('默认生成美式发音URL', () => {
      const word = 'test'
      const result = generateWordSoundSrc(word)
      const expected = 'https://dict.youdao.com/dictvoice?audio=test&type=2'
      expect(result).toBe(expected)
    })

    it('处理包含空格的单词', () => {
      const word = 'hello world'
      const result = generateWordSoundSrc(word, 'us')
      const expected = 'https://dict.youdao.com/dictvoice?audio=hello world&type=2'
      expect(result).toBe(expected)
    })

    it('处理特殊字符', () => {
      const word = 'café'
      const result = generateWordSoundSrc(word, 'uk')
      const expected = 'https://dict.youdao.com/dictvoice?audio=café&type=1'
      expect(result).toBe(expected)
    })

    it('处理数字', () => {
      const word = '123'
      const result = generateWordSoundSrc(word, 'us')
      const expected = 'https://dict.youdao.com/dictvoice?audio=123&type=2'
      expect(result).toBe(expected)
    })
  })

  describe('defaultSounds 配置', () => {
    it('包含所有默认声音路径', () => {
      expect(defaultSounds).toHaveProperty('keySound')
      expect(defaultSounds).toHaveProperty('correctSound')
      expect(defaultSounds).toHaveProperty('wrongSound')
    })

    it('默认声音路径格式正确', () => {
      expect(defaultSounds.keySound).toBe('/sounds/key-default.wav')
      expect(defaultSounds.correctSound).toBe('/sounds/correct.wav')
      expect(defaultSounds.wrongSound).toBe('/sounds/beep.wav')
    })

    it('所有路径都以/sounds/开头', () => {
      Object.values(defaultSounds).forEach(path => {
        expect(path).toMatch(/^\/sounds\//)
      })
    })
  })

  describe('资源完整性', () => {
    it('所有声音文件都有对应的资源定义', () => {
      const allFilenames = [
        ...keySoundResources.map(r => r.filename),
        ...hintSoundResources.map(r => r.filename)
      ]
      
      // 检查defaultSounds中的文件是否在资源定义中
      const keySoundFile = defaultSounds.keySound.split('/').pop()
      const correctSoundFile = defaultSounds.correctSound.split('/').pop()
      const wrongSoundFile = defaultSounds.wrongSound.split('/').pop()
      
      expect(allFilenames).toContain(keySoundFile)
      expect(allFilenames).toContain(correctSoundFile)
      expect(allFilenames).toContain(wrongSoundFile)
    })

    it('资源键名唯一性', () => {
      const allKeys = [
        ...keySoundResources.map(r => r.key),
        ...hintSoundResources.map(r => r.key)
      ]
      
      const uniqueKeys = [...new Set(allKeys)]
      expect(allKeys).toHaveLength(uniqueKeys.length)
    })
  })
})


