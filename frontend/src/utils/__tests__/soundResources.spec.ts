import { describe, it, expect } from 'vitest'
import { generateWordSoundSrc, defaultSounds, keySoundResources, hintSoundResources, SOUND_URL_PREFIX } from '@/utils/soundResources'

describe('soundResources', () => {
  it('generateWordSoundSrc returns correct youdao url (us default)', () => {
    const url = generateWordSoundSrc('hello')
    expect(url).toContain('dictvoice?audio=hello')
    expect(url).toContain('type=2')
  })

  it('generateWordSoundSrc returns uk url when specified', () => {
    const url = generateWordSoundSrc('world', 'uk')
    expect(url).toContain('dictvoice?audio=world')
    expect(url).toContain('type=1')
  })

  it('defaultSounds and resources exported correctly', () => {
    expect(defaultSounds.keySound).toContain('/sounds/')
    expect(Array.isArray(keySoundResources)).toBe(true)
    expect(Array.isArray(hintSoundResources)).toBe(true)
    expect(SOUND_URL_PREFIX).toBe('/sounds/')
  })
})


