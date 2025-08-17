import { computed, unref } from 'vue'
import { useSound } from '@vueuse/sound'

// 发音源：有道词典API
const pronunciationApi = 'https://dict.youdao.com/dictvoice?audio='

// 生成发音URL（参考qwerty learner）
function generateWordSoundSrc(word, pronunciationType = 'us') {
  const wordStr = unref(word) || ''
  if (!wordStr) return ''
  
  // 有道词典API
  const type = pronunciationType === 'uk' ? '1' : '2'
  return `${pronunciationApi}${encodeURIComponent(wordStr)}&type=${type}`
}

// 使用@vueuse/sound库的发音hook（专门为Vue设计）
export default function usePronunciation(word, pronunciationType = 'us') {
  const soundSrc = computed(() => generateWordSoundSrc(word, pronunciationType))
  
  const { play, stop, sound, isPlaying } = useSound(soundSrc, {
    html5: true,
    format: ['mp3'],
    volume: 1.0,
    playbackRate: 1.0,
    interrupt: false, // 不允许重叠播放，避免重音
  })

  return {
    play,
    stop,
    isPlaying,
    sound
  }
}

// 预加载发音（参考qwerty learner的usePrefetchPronunciationSound）
export function usePrefetchPronunciation(word) {
  const soundSrc = computed(() => generateWordSoundSrc(word, 'us'))
  
  // 预加载音频
  const preloadAudio = () => {
    const src = soundSrc.value
    if (!src) return
    
    const audio = new Audio()
    audio.src = src
    audio.preload = 'auto'
    audio.crossOrigin = 'anonymous'
    audio.style.display = 'none'
    
    document.head.appendChild(audio)
    
    return () => {
      if (document.head.contains(audio)) {
        document.head.removeChild(audio)
      }
    }
  }
  
  return { preloadAudio }
}
