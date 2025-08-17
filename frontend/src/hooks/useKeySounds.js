import { ref, computed } from 'vue'

// 声音资源路径
const SOUND_URL_PREFIX = '/sounds/'
const KEY_SOUND_URL_PREFIX = SOUND_URL_PREFIX // 键盘音效也在sounds目录下

// 默认声音资源
const defaultKeySound = 'key-default.wav'
const defaultCorrectSound = 'correct.wav'
const defaultWrongSound = 'beep.wav'

export default function useKeySounds() {
  const isKeySoundEnabled = ref(true)
  const isCorrectSoundEnabled = ref(true)
  const isWrongSoundEnabled = ref(true)
  const volume = ref(0.5)
  
  // 音频缓存
  const audioCache = new Map()
  
  // 创建音频实例
  const createAudio = (src) => {
    // 检查缓存
    if (audioCache.has(src)) {
      const cachedAudio = audioCache.get(src)
      // 克隆音频对象，避免重复播放问题
      const clonedAudio = cachedAudio.cloneNode()
      clonedAudio.volume = volume.value
      return clonedAudio
    }
    
    const audio = new Audio(src)
    audio.volume = volume.value
    audio.preload = 'auto'
    
    // 缓存音频对象
    audioCache.set(src, audio)
    
    return audio
  }
  
  // 播放按键声音
  const playKeySound = () => {
    if (!isKeySoundEnabled.value) {
      console.log('键盘音效已禁用')
      return
    }
    
    try {
      const audioSrc = KEY_SOUND_URL_PREFIX + defaultKeySound
      console.log('播放键盘音效:', audioSrc)
      const audio = createAudio(audioSrc)
      audio.currentTime = 0 // 重置播放位置
      audio.play().catch(error => {
        console.warn('播放按键声音失败:', error)
      })
    } catch (error) {
      console.warn('创建按键声音失败:', error)
    }
  }
  
  // 播放正确声音
  const playCorrectSound = () => {
    if (!isCorrectSoundEnabled.value) return
    
    try {
      const audio = createAudio(SOUND_URL_PREFIX + defaultCorrectSound)
      audio.currentTime = 0 // 重置播放位置
      audio.play().catch(error => {
        console.warn('播放正确声音失败:', error)
      })
    } catch (error) {
      console.warn('创建正确声音失败:', error)
    }
  }
  
  // 播放错误声音
  const playWrongSound = () => {
    if (!isWrongSoundEnabled.value) return
    
    try {
      const audio = createAudio(SOUND_URL_PREFIX + defaultWrongSound)
      audio.currentTime = 0 // 重置播放位置
      audio.play().catch(error => {
        console.warn('播放错误声音失败:', error)
      })
    } catch (error) {
      console.warn('创建错误声音失败:', error)
    }
  }
  
  // 设置音量
  const setVolume = (newVolume) => {
    volume.value = Math.max(0, Math.min(1, newVolume))
  }
  
  // 切换按键声音
  const toggleKeySound = () => {
    isKeySoundEnabled.value = !isKeySoundEnabled.value
  }
  
  // 切换正确声音
  const toggleCorrectSound = () => {
    isCorrectSoundEnabled.value = !isCorrectSoundEnabled.value
  }
  
  // 切换错误声音
  const toggleWrongSound = () => {
    isWrongSoundEnabled.value = !isWrongSoundEnabled.value
  }
  
  // 预加载所有音效
  const preloadSounds = () => {
    try {
      // 预加载按键音效
      createAudio(KEY_SOUND_URL_PREFIX + defaultKeySound)
      // 预加载正确音效
      createAudio(SOUND_URL_PREFIX + defaultCorrectSound)
      // 预加载错误音效
      createAudio(SOUND_URL_PREFIX + defaultWrongSound)
      console.log('音效预加载完成')
    } catch (error) {
      console.warn('音效预加载失败:', error)
    }
  }
  
  // 测试音效
  const testSounds = () => {
    console.log('测试音效...')
    playKeySound()
    setTimeout(() => playCorrectSound(), 500)
    setTimeout(() => playWrongSound(), 1000)
  }
  
  return {
    // 播放函数
    playKeySound,
    playCorrectSound,
    playWrongSound,
    
    // 控制函数
    setVolume,
    toggleKeySound,
    toggleCorrectSound,
    toggleWrongSound,
    preloadSounds,
    testSounds,
    
    // 状态
    isKeySoundEnabled: computed(() => isKeySoundEnabled.value),
    isCorrectSoundEnabled: computed(() => isCorrectSoundEnabled.value),
    isWrongSoundEnabled: computed(() => isWrongSoundEnabled.value),
    volume: computed(() => volume.value)
  }
}



