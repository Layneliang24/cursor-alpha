import { describe, it, expect, beforeEach, vi } from 'vitest'
import useKeySounds from '@/hooks/useKeySounds'

describe('useKeySounds', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('creates and plays key sound with caching', () => {
    const playSpy = vi.fn(() => Promise.resolve())
    // Mock global Audio
    // @ts-ignore
    global.Audio = function (this: any, src: string) {
      this.src = src
      this.volume = 0
      this.preload = ''
      this.currentTime = 0
      this.play = playSpy
      this.cloneNode = () => ({ currentTime: 0, volume: 0.5, play: playSpy })
    } as any

    const { playKeySound, preloadSounds } = useKeySounds()
    preloadSounds()
    playKeySound()
    expect(playSpy).toHaveBeenCalled()
  })

  it('setVolume clamps value between 0 and 1', () => {
    const { setVolume, volume } = useKeySounds()
    setVolume(2)
    expect(volume.value).toBe(1)
    setVolume(-1)
    expect(volume.value).toBe(0)
  })
})


