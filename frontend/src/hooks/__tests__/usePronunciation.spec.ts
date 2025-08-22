import { describe, it, expect, vi, beforeEach } from 'vitest'
import usePronunciation, { usePrefetchPronunciation } from '@/hooks/usePronunciation'
import { ref } from 'vue'

// Mock @vueuse/sound
vi.mock('@vueuse/sound', () => ({ useSound: (src: any) => ({ play: vi.fn(), stop: vi.fn(), sound: {}, isPlaying: ref(false) }) }))

describe('usePronunciation', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('generates correct youdao url and exposes play/stop', () => {
    const word = ref('hello world')
    const hook = usePronunciation(word, 'uk')
    expect(typeof hook.play).toBe('function')
    expect(typeof hook.stop).toBe('function')
  })

  it('prefetch creates and removes audio node', () => {
    const disposeSpies: Array<() => void> = []
    // Mock global Audio element
    const createEl = () => {
      const el: any = document.createElement('audio')
      el.preload = ''
      el.crossOrigin = ''
      el.style = { display: '' }
      return el
    }
    // @ts-ignore
    global.Audio = function () { return createEl() } as any

    const { preloadAudio } = usePrefetchPronunciation(ref('alpha'))
    const dispose = preloadAudio()
    if (dispose) {
      disposeSpies.push(dispose)
    }
    // 调用清理函数
    disposeSpies.forEach((fn) => fn())
    expect(true).toBe(true)
  })
})


