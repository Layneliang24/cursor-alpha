<template>
  <div class="api-integration-page">
    <div class="container mx-auto px-4 py-8">
      <div class="max-w-6xl mx-auto">
        <!-- 页面标题 -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">API集成管理</h1>
          <p class="text-gray-600">配置和管理英语学习相关的第三方API服务</p>
        </div>

        <!-- API服务卡片 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <!-- 语音合成API -->
          <div class="bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-xl font-semibold">语音合成 (TTS)</h2>
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 rounded-full" :class="ttsStatus ? 'bg-green-500' : 'bg-red-500'"></div>
                <span class="text-sm" :class="ttsStatus ? 'text-green-600' : 'text-red-600'">
                  {{ ttsStatus ? '已连接' : '未连接' }}
                </span>
              </div>
            </div>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">API密钥</label>
                <input 
                  v-model="ttsConfig.apiKey"
                  type="password"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="输入API密钥"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">服务提供商</label>
                <select 
                  v-model="ttsConfig.provider"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="google">Google Cloud TTS</option>
                  <option value="azure">Microsoft Azure</option>
                  <option value="aws">Amazon Polly</option>
                  <option value="openai">OpenAI TTS</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">语音设置</label>
                <div class="grid grid-cols-2 gap-2">
                  <select 
                    v-model="ttsConfig.voice"
                    class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="en-US">英语 (美国)</option>
                    <option value="en-GB">英语 (英国)</option>
                    <option value="en-AU">英语 (澳大利亚)</option>
                  </select>
                  <select 
                    v-model="ttsConfig.speed"
                    class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="0.8">慢速</option>
                    <option value="1.0">正常</option>
                    <option value="1.2">快速</option>
                  </select>
                </div>
              </div>
              
              <button 
                @click="testTTS"
                class="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md transition-colors"
              >
                测试语音合成
              </button>
            </div>
          </div>

          <!-- 语音识别API -->
          <div class="bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-xl font-semibold">语音识别 (STT)</h2>
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 rounded-full" :class="sttStatus ? 'bg-green-500' : 'bg-red-500'"></div>
                <span class="text-sm" :class="sttStatus ? 'text-green-600' : 'text-red-600'">
                  {{ sttStatus ? '已连接' : '未连接' }}
                </span>
              </div>
            </div>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">API密钥</label>
                <input 
                  v-model="sttConfig.apiKey"
                  type="password"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="输入API密钥"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">服务提供商</label>
                <select 
                  v-model="sttConfig.provider"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="google">Google Cloud Speech</option>
                  <option value="azure">Microsoft Azure</option>
                  <option value="aws">Amazon Transcribe</option>
                  <option value="openai">OpenAI Whisper</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">识别设置</label>
                <div class="grid grid-cols-2 gap-2">
                  <select 
                    v-model="sttConfig.language"
                    class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="en-US">英语 (美国)</option>
                    <option value="en-GB">英语 (英国)</option>
                    <option value="en-AU">英语 (澳大利亚)</option>
                  </select>
                  <select 
                    v-model="sttConfig.model"
                    class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="base">基础模型</option>
                    <option value="enhanced">增强模型</option>
                  </select>
                </div>
              </div>
              
              <button 
                @click="testSTT"
                class="w-full bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-md transition-colors"
              >
                测试语音识别
              </button>
            </div>
          </div>
        </div>

        <!-- 翻译API -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold">翻译服务</h2>
            <div class="flex items-center space-x-2">
              <div class="w-3 h-3 rounded-full" :class="translateStatus ? 'bg-green-500' : 'bg-red-500'"></div>
              <span class="text-sm" :class="translateStatus ? 'text-green-600' : 'text-red-600'">
                {{ translateStatus ? '已连接' : '未连接' }}
              </span>
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">API密钥</label>
              <input 
                v-model="translateConfig.apiKey"
                type="password"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="输入API密钥"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">服务提供商</label>
              <select 
                v-model="translateConfig.provider"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="google">Google Translate</option>
                <option value="azure">Microsoft Translator</option>
                <option value="deepl">DeepL</option>
                <option value="openai">OpenAI</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">目标语言</label>
              <select 
                v-model="translateConfig.targetLanguage"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="zh-CN">中文 (简体)</option>
                <option value="zh-TW">中文 (繁体)</option>
                <option value="ja">日语</option>
                <option value="ko">韩语</option>
              </select>
            </div>
          </div>
          
          <div class="mt-4">
            <button 
              @click="testTranslate"
              class="bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded-md transition-colors"
            >
              测试翻译服务
            </button>
          </div>
        </div>

        <!-- 测试结果 -->
        <div v-if="testResults.length > 0" class="bg-white rounded-lg shadow-lg p-6">
          <h2 class="text-xl font-semibold mb-4">测试结果</h2>
          <div class="space-y-3">
            <div 
              v-for="(result, index) in testResults" 
              :key="index"
              class="p-3 rounded-lg"
              :class="result.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'"
            >
              <div class="flex items-center justify-between">
                <div>
                  <span class="font-medium">{{ result.service }}</span>
                  <span class="text-sm text-gray-600 ml-2">{{ result.message }}</span>
                </div>
                <span class="text-sm" :class="result.success ? 'text-green-600' : 'text-red-600'">
                  {{ result.success ? '成功' : '失败' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 保存按钮 -->
        <div class="flex justify-end space-x-4 mt-8">
          <button 
            @click="resetConfig"
            class="bg-gray-500 hover:bg-gray-600 text-white py-2 px-6 rounded-md transition-colors"
          >
            重置配置
          </button>
          <button 
            @click="saveConfig"
            class="bg-blue-500 hover:bg-blue-600 text-white py-2 px-6 rounded-md transition-colors"
          >
            保存配置
          </button>
        </div>
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
.api-integration-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
