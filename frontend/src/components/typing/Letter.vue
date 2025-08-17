<template>
  <span
    :class="letterClass"
    :style="{ fontSize: fontSize + 'px' }"
  >
    {{ displayLetter }}
  </span>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'Letter',
  props: {
    letter: {
      type: String,
      required: true
    },
    state: {
      type: String,
      default: 'normal',
      validator: (value) => ['normal', 'correct', 'wrong'].includes(value)
    },
    visible: {
      type: Boolean,
      default: true
    },
    fontSize: {
      type: Number,
      default: 48
    }
  },
  setup(props) {
    // 字母状态对应的CSS类
    const stateClassMap = {
      normal: 'letter-normal',
      correct: 'letter-correct',
      wrong: 'letter-wrong'
    }
    
    // 计算显示的字母
    const displayLetter = computed(() => {
      return props.visible ? props.letter : '_'
    })
    
    // 计算CSS类
    const letterClass = computed(() => {
      console.log('Letter state:', props.state, 'for letter:', props.letter)
      const baseClass = 'letter-base'
      const stateClass = stateClassMap[props.state] || stateClassMap.normal
      return `${baseClass} ${stateClass}`
    })
    
    return {
      displayLetter,
      letterClass
    }
  }
}
</script>

<style scoped>
/* 字母基础样式 */
.letter-base {
  display: inline-block;
  margin: 0;
  padding: 0;
  font-family: monospace;
  font-weight: normal;
  padding-right: 8px;
  transition: all 0.2s ease;
}

/* 字母状态样式 */
.letter-normal {
  color: #9ca3af;
}

.letter-correct {
  color: #16a34a;
  animation: correctPulse 0.3s ease;
}

.letter-wrong {
  color: #dc2626;
  animation: wrongShake 0.3s ease;
}

/* 正确状态动画 */
@keyframes correctPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

/* 错误状态动画 */
@keyframes wrongShake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-2px); }
  75% { transform: translateX(2px); }
}
</style>
