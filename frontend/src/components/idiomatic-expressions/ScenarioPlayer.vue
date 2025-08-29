<template>
  <div class="scenario-player">
    <div class="player-header">
      <h3 class="scenario-title">{{ scenario.scenario_name }}</h3>
      <p class="scenario-description">{{ scenario.description }}</p>
    </div>
    
    <div class="player-content">
      <!-- 音频播放器 -->
      <div class="audio-player">
        <div class="audio-controls">
          <el-button 
            type="primary" 
            :icon="isPlaying ? 'VideoPause' : 'VideoPlay'"
            circle 
            size="large"
            @click="togglePlay"
            :loading="audioLoading"
          />
          
          <div class="time-display">
            <span class="current-time">{{ formatTime(currentTime) }}</span>
            <span class="separator">/</span>
            <span class="total-time">{{ formatTime(duration) }}</span>
          </div>
          
          <el-button 
            type="info" 
            :icon="isMuted ? 'Mute' : 'Microphone'"
            circle
            @click="toggleMute"
          />
        </div>
        
        <div class="progress-container">
          <el-slider
            v-model="progress"
            :max="100"
            :show-tooltip="false"
            @change="handleSeek"
            class="audio-progress"
          />
        </div>
        
        <div class="playback-controls">
          <el-button-group size="small">
            <el-button @click="changeSpeed(0.5)" :type="playbackSpeed === 0.5 ? 'primary' : ''">
              0.5x
            </el-button>
            <el-button @click="changeSpeed(0.75)" :type="playbackSpeed === 0.75 ? 'primary' : ''">
              0.75x
            </el-button>
            <el-button @click="changeSpeed(1)" :type="playbackSpeed === 1 ? 'primary' : ''">
              1x
            </el-button>
            <el-button @click="changeSpeed(1.25)" :type="playbackSpeed === 1.25 ? 'primary' : ''">
              1.25x
            </el-button>
            <el-button @click="changeSpeed(1.5)" :type="playbackSpeed === 1.5 ? 'primary' : ''">
              1.5x
            </el-button>
          </el-button-group>
        </div>
      </div>
      
      <!-- 字幕显示 -->
      <div class="subtitles-container" v-if="showSubtitles">
        <div class="subtitles-content">
          <div 
            v-for="(subtitle, index) in currentSubtitles" 
            :key="index"
            class="subtitle-line"
            :class="{ 
              'active': subtitle.startTime <= currentTime && currentTime <= subtitle.endTime,
              'highlight': subtitle.isExpression 
            }"
            @click="seekToSubtitle(subtitle)"
          >
            <span class="subtitle-text">{{ subtitle.text }}</span>
            <span class="subtitle-translation" v-if="showTranslation">{{ subtitle.translation }}</span>
          </div>
        </div>
        
        <div class="subtitle-controls">
          <el-switch
            v-model="showTranslation"
            active-text="显示翻译"
            inactive-text="隐藏翻译"
          />
          <el-switch
            v-model="autoScroll"
            active-text="自动滚动"
            inactive-text="手动滚动"
          />
        </div>
      </div>
      
      <!-- 表达式高亮 -->
      <div class="expressions-highlight" v-if="highlightedExpressions.length">
        <h4>本段包含的地道表达</h4>
        <div class="expression-tags">
          <el-tag 
            v-for="expr in highlightedExpressions"
            :key="expr.id"
            type="primary"
            @click="highlightExpression(expr)"
            class="expression-tag"
          >
            {{ expr.expression }}
          </el-tag>
        </div>
      </div>
    </div>
    
    <!-- 播放器设置 -->
    <div class="player-settings" v-show="showSettings">
      <el-card>
        <template #header>
          <span>播放设置</span>
        </template>
        
        <el-form label-width="100px">
          <el-form-item label="字幕显示">
            <el-switch v-model="showSubtitles" />
          </el-form-item>
          
          <el-form-item label="自动播放">
            <el-switch v-model="autoPlay" />
          </el-form-item>
          
          <el-form-item label="循环播放">
            <el-switch v-model="loopPlay" />
          </el-form-item>
          
          <el-form-item label="音量">
            <el-slider v-model="volume" :max="100" @change="updateVolume" />
          </el-form-item>
        </el-form>
      </el-card>
    </div>
    
    <!-- 设置按钮 -->
    <div class="settings-toggle">
      <el-button 
        type="text" 
        @click="showSettings = !showSettings"
        :icon="showSettings ? 'ArrowUp' : 'Setting'"
      >
        {{ showSettings ? '隐藏设置' : '播放设置' }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'

// Props
interface Subtitle {
  startTime: number
  endTime: number
  text: string
  translation: string
  isExpression: boolean
}

interface ExpressionHighlight {
  id: number
  expression: string
  startTime: number
  endTime: number
}

interface Scenario {
  id: number
  scenario_name: string
  description: string
  audio_url?: string
  subtitles?: Subtitle[]
  expressions?: ExpressionHighlight[]
}

interface Props {
  scenario: Scenario
  autoPlay?: boolean
  showSubtitles?: boolean
  showTranslation?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  autoPlay: false,
  showSubtitles: true,
  showTranslation: true
})

// Emits
const emit = defineEmits<{
  expressionClick: [expression: ExpressionHighlight]
  playStateChange: [isPlaying: boolean]
  progressUpdate: [progress: number]
}>()

// 状态
const audio = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const isMuted = ref(false)
const audioLoading = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const progress = ref(0)
const playbackSpeed = ref(1)
const volume = ref(80)
const showSettings = ref(false)
const showSubtitles = ref(props.showSubtitles)
const showTranslation = ref(props.showTranslation)
const autoPlay = ref(props.autoPlay)
const loopPlay = ref(false)
const autoScroll = ref(true)

// 计算属性
const currentSubtitles = computed(() => {
  return props.scenario.subtitles || []
})

const highlightedExpressions = computed(() => {
  return props.scenario.expressions || []
})

const activeSubtitle = computed(() => {
  return currentSubtitles.value.find(
    subtitle => subtitle.startTime <= currentTime.value && currentTime.value <= subtitle.endTime
  )
})

// 方法
const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const initializeAudio = () => {
  if (!props.scenario.audio_url) return
  
  audio.value = new Audio(props.scenario.audio_url)
  
  // 音频事件监听
  audio.value.addEventListener('loadedmetadata', () => {
    duration.value = audio.value!.duration
  })
  
  audio.value.addEventListener('timeupdate', () => {
    currentTime.value = audio.value!.currentTime
    progress.value = (currentTime.value / duration.value) * 100
  })
  
  audio.value.addEventListener('ended', () => {
    isPlaying.value = false
    if (loopPlay.value) {
      audio.value!.currentTime = 0
      audio.value!.play()
      isPlaying.value = true
    }
  })
  
  audio.value.addEventListener('error', (e) => {
    console.error('音频加载失败:', e)
    ElMessage.error('音频加载失败，请检查网络连接')
    audioLoading.value = false
  })
  
  audio.value.addEventListener('canplay', () => {
    audioLoading.value = false
    if (autoPlay.value) {
      togglePlay()
    }
  })
  
  // 设置初始音量
  audio.value.volume = volume.value / 100
}

const togglePlay = async () => {
  if (!audio.value) return
  
  try {
    if (isPlaying.value) {
      audio.value.pause()
      isPlaying.value = false
    } else {
      audioLoading.value = true
      await audio.value.play()
      isPlaying.value = true
    }
    
    emit('playStateChange', isPlaying.value)
  } catch (error) {
    console.error('播放控制失败:', error)
    ElMessage.error('播放失败，请重试')
    audioLoading.value = false
  }
}

const toggleMute = () => {
  if (!audio.value) return
  
  isMuted.value = !isMuted.value
  audio.value.muted = isMuted.value
}

const handleSeek = (value: number) => {
  if (!audio.value || !duration.value) return
  
  const seekTime = (value / 100) * duration.value
  audio.value.currentTime = seekTime
  currentTime.value = seekTime
}

const changeSpeed = (speed: number) => {
  if (!audio.value) return
  
  playbackSpeed.value = speed
  audio.value.playbackRate = speed
}

const updateVolume = (value: number) => {
  if (!audio.value) return
  
  volume.value = value
  audio.value.volume = value / 100
}

const seekToSubtitle = (subtitle: Subtitle) => {
  if (!audio.value) return
  
  audio.value.currentTime = subtitle.startTime
  currentTime.value = subtitle.startTime
}

const highlightExpression = (expression: ExpressionHighlight) => {
  emit('expressionClick', expression)
  
  // 跳转到表达式出现的时间点
  if (audio.value) {
    audio.value.currentTime = expression.startTime
    currentTime.value = expression.startTime
  }
}

// 生命周期
onMounted(() => {
  initializeAudio()
})

onUnmounted(() => {
  if (audio.value) {
    audio.value.pause()
    audio.value = null
  }
})

// 监听器
watch(() => props.scenario.audio_url, () => {
  if (audio.value) {
    audio.value.pause()
    isPlaying.value = false
  }
  initializeAudio()
})

watch(progress, (newProgress) => {
  emit('progressUpdate', newProgress)
})

// 自动滚动字幕
watch(activeSubtitle, (newSubtitle) => {
  if (autoScroll.value && newSubtitle) {
    const subtitleElement = document.querySelector('.subtitle-line.active')
    if (subtitleElement) {
      subtitleElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }
})
</script>

<style scoped>
.scenario-player {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.player-header {
  text-align: center;
  margin-bottom: 24px;
}

.scenario-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.scenario-description {
  color: #606266;
  font-size: 14px;
}

.audio-player {
  margin-bottom: 24px;
}

.audio-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 16px;
}

.time-display {
  display: flex;
  align-items: center;
  gap: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #606266;
  min-width: 80px;
}

.separator {
  color: #dcdfe6;
}

.progress-container {
  margin-bottom: 12px;
}

.audio-progress {
  width: 100%;
}

.playback-controls {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.subtitles-container {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.subtitles-content {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 12px;
}

.subtitle-line {
  padding: 8px 12px;
  margin-bottom: 4px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.subtitle-line:hover {
  background: #f5f7fa;
}

.subtitle-line.active {
  background: #ecf5ff;
  border-left: 3px solid #409eff;
}

.subtitle-line.highlight {
  background: #fff2e8;
  border-left: 3px solid #e6a23c;
}

.subtitle-line.active.highlight {
  background: #fdf6ec;
  border-left: 3px solid #e6a23c;
}

.subtitle-text {
  display: block;
  font-size: 14px;
  line-height: 1.5;
  color: #303133;
  margin-bottom: 4px;
}

.subtitle-translation {
  display: block;
  font-size: 12px;
  color: #909399;
  font-style: italic;
}

.subtitle-controls {
  display: flex;
  gap: 16px;
  align-items: center;
}

.expressions-highlight {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.expressions-highlight h4 {
  margin-bottom: 12px;
  color: #303133;
  font-size: 16px;
}

.expression-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.expression-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.expression-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.player-settings {
  margin-top: 20px;
}

.settings-toggle {
  text-align: center;
  margin-top: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .scenario-player {
    padding: 16px;
  }
  
  .audio-controls {
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .playback-controls .el-button-group {
    flex-wrap: wrap;
  }
  
  .subtitle-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .expression-tags {
    justify-content: center;
  }
}

/* 滚动条样式 */
.subtitles-content::-webkit-scrollbar {
  width: 6px;
}

.subtitles-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.subtitles-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.subtitles-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 动画效果 */
@keyframes subtitle-highlight {
  0% { background-color: #ecf5ff; }
  50% { background-color: #d9ecff; }
  100% { background-color: #ecf5ff; }
}

.subtitle-line.active {
  animation: subtitle-highlight 2s ease-in-out infinite;
}
</style>
