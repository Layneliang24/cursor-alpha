<template>
  <div class="api-integration-container">
    <div class="content-wrapper">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">API集成管理</h1>
        <p class="page-subtitle">配置和管理英语学习相关的第三方API服务</p>
      </div>

      <!-- API服务卡片 -->
      <div class="api-grid">
        <!-- 语音合成API -->
        <div class="api-card">
          <div class="card-header">
            <h2 class="card-title">语音合成 (TTS)</h2>
            <div class="status-indicator">
              <div class="status-dot" :class="ttsStatus ? 'status-connected' : 'status-disconnected'"></div>
              <span class="status-text" :class="ttsStatus ? 'status-connected' : 'status-disconnected'">
                {{ ttsStatus ? '已连接' : '未连接' }}
              </span>
            </div>
          </div>
          
          <div class="card-content">
            <div class="form-group">
              <label class="form-label">API密钥</label>
              <input 
                v-model="ttsConfig.apiKey"
                type="password"
                class="form-input"
                placeholder="输入API密钥"
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">服务提供商</label>
              <select v-model="ttsConfig.provider" class="form-select">
                <option value="google">Google Cloud TTS</option>
                <option value="azure">Microsoft Azure</option>
                <option value="aws">Amazon Polly</option>
                <option value="openai">OpenAI TTS</option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="form-label">语音设置</label>
              <div class="form-row">
                <select v-model="ttsConfig.voice" class="form-select">
                  <option value="en-US">英语 (美国)</option>
                  <option value="en-GB">英语 (英国)</option>
                  <option value="en-AU">英语 (澳大利亚)</option>
                </select>
                <select v-model="ttsConfig.speed" class="form-select">
                  <option value="0.8">慢速</option>
                  <option value="1.0">正常</option>
                  <option value="1.2">快速</option>
                </select>
              </div>
            </div>
            
            <button @click="testTTS" class="test-button tts-button">
              测试语音合成
            </button>
          </div>
        </div>

        <!-- 语音识别API -->
        <div class="api-card">
          <div class="card-header">
            <h2 class="card-title">语音识别 (STT)</h2>
            <div class="status-indicator">
              <div class="status-dot" :class="sttStatus ? 'status-connected' : 'status-disconnected'"></div>
              <span class="status-text" :class="sttStatus ? 'status-connected' : 'status-disconnected'">
                {{ sttStatus ? '已连接' : '未连接' }}
              </span>
            </div>
          </div>
          
          <div class="card-content">
            <div class="form-group">
              <label class="form-label">API密钥</label>
              <input 
                v-model="sttConfig.apiKey"
                type="password"
                class="form-input"
                placeholder="输入API密钥"
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">服务提供商</label>
              <select v-model="sttConfig.provider" class="form-select">
                <option value="google">Google Cloud Speech</option>
                <option value="azure">Microsoft Azure</option>
                <option value="aws">Amazon Transcribe</option>
                <option value="openai">OpenAI Whisper</option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="form-label">识别设置</label>
              <div class="form-row">
                <select v-model="sttConfig.language" class="form-select">
                  <option value="en-US">英语 (美国)</option>
                  <option value="en-GB">英语 (英国)</option>
                  <option value="en-AU">英语 (澳大利亚)</option>
                </select>
                <select v-model="sttConfig.model" class="form-select">
                  <option value="base">基础模型</option>
                  <option value="enhanced">增强模型</option>
                </select>
              </div>
            </div>
            
            <button @click="testSTT" class="test-button stt-button">
              测试语音识别
            </button>
          </div>
        </div>
      </div>

      <!-- 翻译API -->
      <div class="api-card full-width">
        <div class="card-header">
          <h2 class="card-title">翻译服务</h2>
          <div class="status-indicator">
            <div class="status-dot" :class="translateStatus ? 'status-connected' : 'status-disconnected'"></div>
            <span class="status-text" :class="translateStatus ? 'status-connected' : 'status-disconnected'">
              {{ translateStatus ? '已连接' : '未连接' }}
            </span>
          </div>
        </div>
        
        <div class="card-content">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">API密钥</label>
              <input 
                v-model="translateConfig.apiKey"
                type="password"
                class="form-input"
                placeholder="输入API密钥"
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">服务提供商</label>
              <select v-model="translateConfig.provider" class="form-select">
                <option value="google">Google Translate</option>
                <option value="azure">Microsoft Translator</option>
                <option value="deepl">DeepL</option>
                <option value="openai">OpenAI</option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="form-label">目标语言</label>
              <select v-model="translateConfig.targetLanguage" class="form-select">
                <option value="zh-CN">中文 (简体)</option>
                <option value="zh-TW">中文 (繁体)</option>
                <option value="ja">日语</option>
                <option value="ko">韩语</option>
              </select>
            </div>
          </div>
          
          <div class="button-container">
            <button @click="testTranslate" class="test-button translate-button">
              测试翻译服务
            </button>
          </div>
        </div>
      </div>

      <!-- 测试结果 -->
      <div v-if="testResults.length > 0" class="results-card">
        <h2 class="results-title">测试结果</h2>
        <div class="results-list">
          <div 
            v-for="(result, index) in testResults" 
            :key="index"
            class="result-item"
            :class="result.success ? 'result-success' : 'result-error'"
          >
            <div class="result-content">
              <span class="result-service">{{ result.service }}</span>
              <span class="result-message">{{ result.message }}</span>
            </div>
            <span class="result-status" :class="result.success ? 'result-success' : 'result-error'">
              {{ result.success ? '成功' : '失败' }}
            </span>
          </div>
        </div>
      </div>

      <!-- 保存按钮 -->
      <div class="action-buttons">
        <button @click="resetConfig" class="action-button reset-button">
          重置配置
        </button>
        <button @click="saveConfig" class="action-button save-button">
          保存配置
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'

export default {
  name: 'APIIntegration',
  setup() {
    // 配置状态
    const ttsConfig = reactive({
      apiKey: '',
      provider: 'google',
      voice: 'en-US',
      speed: '1.0'
    })
    
    const sttConfig = reactive({
      apiKey: '',
      provider: 'google',
      language: 'en-US',
      model: 'base'
    })
    
    const translateConfig = reactive({
      apiKey: '',
      provider: 'google',
      targetLanguage: 'zh-CN'
    })
    
    // 连接状态
    const ttsStatus = ref(false)
    const sttStatus = ref(false)
    const translateStatus = ref(false)
    
    // 测试结果
    const testResults = ref([])
    
    // 方法
    const testTTS = async () => {
      try {
        // 模拟API测试
        await new Promise(resolve => setTimeout(resolve, 1000))
        const success = Math.random() > 0.3 // 70%成功率
        
        testResults.value.unshift({
          service: '语音合成 (TTS)',
          message: success ? '语音合成服务连接正常' : 'API密钥无效或服务不可用',
          success
        })
        
        ttsStatus.value = success
      } catch (error) {
        testResults.value.unshift({
          service: '语音合成 (TTS)',
          message: '连接失败：' + error.message,
          success: false
        })
        ttsStatus.value = false
      }
    }
    
    const testSTT = async () => {
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        const success = Math.random() > 0.3
        
        testResults.value.unshift({
          service: '语音识别 (STT)',
          message: success ? '语音识别服务连接正常' : 'API密钥无效或服务不可用',
          success
        })
        
        sttStatus.value = success
      } catch (error) {
        testResults.value.unshift({
          service: '语音识别 (STT)',
          message: '连接失败：' + error.message,
          success: false
        })
        sttStatus.value = false
      }
    }
    
    const testTranslate = async () => {
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        const success = Math.random() > 0.3
        
        testResults.value.unshift({
          service: '翻译服务',
          message: success ? '翻译服务连接正常' : 'API密钥无效或服务不可用',
          success
        })
        
        translateStatus.value = success
      } catch (error) {
        testResults.value.unshift({
          service: '翻译服务',
          message: '连接失败：' + error.message,
          success: false
        })
        translateStatus.value = false
      }
    }
    
    const saveConfig = () => {
      // 保存配置到本地存储
      const config = {
        tts: ttsConfig,
        stt: sttConfig,
        translate: translateConfig
      }
      localStorage.setItem('api-integration-config', JSON.stringify(config))
      
      testResults.value.unshift({
        service: '配置保存',
        message: 'API配置已保存到本地存储',
        success: true
      })
    }
    
    const resetConfig = () => {
      // 重置配置
      Object.assign(ttsConfig, {
        apiKey: '',
        provider: 'google',
        voice: 'en-US',
        speed: '1.0'
      })
      
      Object.assign(sttConfig, {
        apiKey: '',
        provider: 'google',
        language: 'en-US',
        model: 'base'
      })
      
      Object.assign(translateConfig, {
        apiKey: '',
        provider: 'google',
        targetLanguage: 'zh-CN'
      })
      
      testResults.value.unshift({
        service: '配置重置',
        message: '所有配置已重置为默认值',
        success: true
      })
    }
    
    const loadConfig = () => {
      try {
        const saved = localStorage.getItem('api-integration-config')
        if (saved) {
          const config = JSON.parse(saved)
          if (config.tts) Object.assign(ttsConfig, config.tts)
          if (config.stt) Object.assign(sttConfig, config.stt)
          if (config.translate) Object.assign(translateConfig, config.translate)
        }
      } catch (error) {
        console.error('加载配置失败:', error)
      }
    }
    
    // 生命周期
    onMounted(() => {
      loadConfig()
    })
    
    return {
      ttsConfig,
      sttConfig,
      translateConfig,
      ttsStatus,
      sttStatus,
      translateStatus,
      testResults,
      testTTS,
      testSTT,
      testTranslate,
      saveConfig,
      resetConfig
    }
  }
}
</script>

<style scoped>
/* 基础样式 */
.api-integration-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f4ff 0%, #e6f3ff 100%);
  padding: 2rem 1rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.125rem;
  color: #4a5568;
}

/* API网格 */
.api-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* API卡片 */
.api-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.api-card.full-width {
  grid-column: 1 / -1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
}

.status-connected {
  background: #38a169;
  color: #38a169;
}

.status-disconnected {
  background: #e53e3e;
  color: #e53e3e;
}

.status-text {
  font-size: 0.875rem;
  font-weight: 500;
}

.card-content {
  padding: 1.5rem;
}

/* 表单样式 */
.form-group {
  margin-bottom: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #3182ce;
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
}

/* 测试按钮 */
.test-button {
  width: 100%;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s;
  color: white;
}

.tts-button {
  background: #3182ce;
}

.tts-button:hover {
  background: #2c5aa0;
}

.stt-button {
  background: #38a169;
}

.stt-button:hover {
  background: #2f855a;
}

.translate-button {
  background: #805ad5;
}

.translate-button:hover {
  background: #6b46c1;
}

.button-container {
  margin-top: 1rem;
}

/* 结果卡片 */
.results-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.results-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 1rem;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid;
}

.result-success {
  background: #f0fff4;
  border-color: #9ae6b4;
}

.result-error {
  background: #fed7d7;
  border-color: #feb2b2;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.result-service {
  font-weight: 500;
  color: #1a202c;
}

.result-message {
  font-size: 0.875rem;
  color: #4a5568;
}

.result-status {
  font-size: 0.875rem;
  font-weight: 500;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.action-button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  color: white;
}

.reset-button {
  background: #718096;
}

.reset-button:hover {
  background: #4a5568;
}

.save-button {
  background: #3182ce;
}

.save-button:hover {
  background: #2c5aa0;
}

/* 响应式 */
@media (max-width: 768px) {
  .api-integration-container {
    padding: 1rem 0.5rem;
  }
  
  .api-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .page-title {
    font-size: 2rem;
  }
}
</style>

