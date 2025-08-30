import { useSound } from '@vueuse/sound'
import { ref, computed } from 'vue'

/**
 * 通知声音提示Hook
 * 用于在需要用户确认或授权时发出明显的声音提示
 */
export function useNotificationSound () {
  // 声音文件路径
  const notificationSoundSrc = computed(() => '/sounds/beep.wav')
  const confirmSoundSrc = computed(() => '/sounds/correct.wav')
  const alertSoundSrc = computed(() => '/sounds/key-default.wav')

  // 通知声音
  const { play: playNotification, stop: stopNotification } = useSound(notificationSoundSrc, {
    volume: 0.8,
    interrupt: true,
  })

  // 确认声音
  const { play: playConfirm, stop: stopConfirm } = useSound(confirmSoundSrc, {
    volume: 0.6,
    interrupt: true,
  })

  // 警告声音
  const { play: playAlert, stop: stopAlert } = useSound(alertSoundSrc, {
    volume: 0.7,
    interrupt: true,
  })

  // 播放通知声音（用于一般通知）
  const notify = () => {
    console.log('🔔 播放通知声音')
    playNotification()
  }

  // 播放确认声音（用于需要确认的操作）
  const confirm = () => {
    console.log('✅ 播放确认声音')
    playConfirm()
  }

  // 播放警告声音（用于需要授权的操作）
  const alert = () => {
    console.log('⚠️ 播放警告声音')
    playAlert()
  }

  // 播放紧急声音（连续播放多次）
  const urgent = (times = 3) => {
    console.log(`🚨 播放紧急声音 ${times} 次`)
    let count = 0
    const playUrgent = () => {
      if (count < times) {
        playAlert()
        count++
        setTimeout(playUrgent, 500) // 每500ms播放一次
      }
    }
    playUrgent()
  }

  // 停止所有声音
  const stopAll = () => {
    stopNotification()
    stopConfirm()
    stopAlert()
  }

  return {
    notify,
    confirm,
    alert,
    urgent,
    stopAll,
  }
} 