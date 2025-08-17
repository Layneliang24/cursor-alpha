<template>
  <button 
    @click="playSound" 
    :class="['sound-icon', { 'playing': isPlaying }]"
    :title="`播放 ${word} 的发音`"
  >
    🔊
  </button>
</template>

<script>
import { computed, onUnmounted, onMounted } from 'vue'
import { useSound } from '@vueuse/sound'

// 发音源：有道词典API
const pronunciationApi = 'https://dict.youdao.com/dictvoice?audio='

// 生成发音URL（参考qwerty learner）
function generateWordSoundSrc(word, pronunciationType = 'us') {
  if (!word) return ''
  
  // 有道词典API
  const type = pronunciationType === 'uk' ? '1' : '2'
  return `${pronunciationApi}${encodeURIComponent(word)}&type=${type}`
}

export default {
  name: 'WordPronunciationIcon',
  props: {
    word: {
      type: String,
      required: true
    },
    pronunciationType: {
      type: String,
      default: 'us'
    }
  },
  setup(props) {
    // 为当前单词创建独立的发音实例
    const soundSrc = computed(() => generateWordSoundSrc(props.word, props.pronunciationType))
    
    const { play, stop, sound, isPlaying } = useSound(soundSrc, {
      html5: true,
      format: ['mp3'],
      volume: 1.0,
      playbackRate: 1.0,
      interrupt: false, // 不允许重叠播放
    })

    // 播放发音（参考qwerty learner的playSound逻辑）
    const playSound = () => {
      console.log('WordPronunciationIcon playSound called, word:', props.word)
      console.log('soundSrc:', soundSrc.value)
      console.log('sound.value:', sound.value)
      
      // 全局发音管理：停止其他所有发音
      if (window.stopAllPronunciations) {
        window.stopAllPronunciations()
      }
      
      // 测试有道词典API是否可用
      if (soundSrc.value) {
        console.log('测试有道词典API:', soundSrc.value)
        
        // 直接使用Audio测试
        const testAudio = new Audio(soundSrc.value)
        testAudio.play().then(() => {
          console.log('有道词典API测试成功')
        }).catch((error) => {
          console.error('有道词典API测试失败:', error)
        })
      }
      
      if (sound.value) {
        console.log('使用@vueuse/sound播放发音')
        // 先停止当前播放，再播放新发音
        stop()
        // 延迟一点确保停止完成
        setTimeout(() => {
          play()
        }, 50)
      } else {
        console.log('sound.value is null，@vueuse/sound不可用')
      }
    }

    // 组件挂载时触发事件
    onMounted(() => {
      console.log('WordPronunciationIcon mounted, word:', props.word, 'soundSrc:', soundSrc.value)
    })

    // 组件卸载时清理资源（参考qwerty learner的useEffect清理逻辑）
    onUnmounted(() => {
      if (sound.value) {
        stop()
        // 如果sound有unload方法，调用它
        if (typeof sound.value.unload === 'function') {
          sound.value.unload()
        }
      }
    })

    return {
      playSound,
      isPlaying
    }
  }
}
</script>

<style scoped>
.sound-icon {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s ease;
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  width: 48px;
}

.sound-icon:hover {
  background: #f0f9ff;
  transform: scale(1.1);
}

.sound-icon:active {
  transform: scale(0.95);
}

.sound-icon.playing {
  color: #10b981;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}
</style>
