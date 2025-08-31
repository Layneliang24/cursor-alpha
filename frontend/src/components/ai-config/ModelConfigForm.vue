<template>
  <div class="model-config-form">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      label-position="top"
      class="config-form"
    >
      <!-- 基础配置 -->
      <div class="form-section">
        <h3 class="section-title">基础配置</h3>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="配置名称" prop="config_name">
              <el-input
                v-model="formData.config_name"
                placeholder="请输入配置名称"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="AI提供商" prop="provider">
              <el-select
                v-model="formData.provider"
                placeholder="请选择AI提供商"
                @change="handleProviderChange"
                style="width: 100%"
              >
                <el-option
                  v-for="provider in providers"
                  :key="provider.id"
                  :label="provider.display_name"
                  :value="provider.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="AI模型" prop="model">
              <el-select
                v-model="formData.model"
                placeholder="请选择AI模型"
                @change="handleModelChange"
                style="width: 100%"
                :disabled="!formData.provider"
              >
                <el-option
                  v-for="model in availableModels"
                  :key="model.model_id"
                  :label="`${model.display_name} (${model.max_tokens?.toLocaleString() || 'N/A'} tokens)`"
                  :value="model.model_id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否默认" prop="is_default">
              <el-switch
                v-model="formData.is_default"
                active-text="默认配置"
                inactive-text="普通配置"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 参数配置 -->
      <div class="form-section">
        <h3 class="section-title">参数配置</h3>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="温度 (Temperature)" prop="temperature">
              <div class="temperature-control">
                <el-slider
                  v-model="formData.temperature"
                  :min="0"
                  :max="2"
                  :step="0.1"
                  show-input
                  :show-input-controls="false"
                  class="temperature-slider"
                />
                <div class="temperature-info">
                  <span class="temp-value">{{ formData.temperature }}</span>
                  <el-tooltip
                    content="控制输出的随机性。较低值(如0.2)使输出更确定，较高值(如0.8)使输出更随机"
                    placement="top"
                  >
                    <i class="el-icon-question"></i>
                  </el-tooltip>
                </div>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大Token数" prop="max_tokens">
              <div class="max-tokens-control">
                <el-input-number
                  v-model="formData.max_tokens"
                  :min="1"
                  :max="maxTokensLimit"
                  :step="100"
                  style="width: 100%"
                  controls-position="right"
                />
                <div class="tokens-info">
                  <span class="tokens-limit">
                    上限: {{ maxTokensLimit?.toLocaleString() || 'N/A' }}
                  </span>
                  <el-button
                    v-if="formData.max_tokens > maxTokensLimit"
                    type="warning"
                    size="small"
                    @click="formData.max_tokens = maxTokensLimit"
                  >
                    修正
                  </el-button>
                </div>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 系统提示模板 -->
      <div class="form-section">
        <h3 class="section-title">系统提示模板</h3>
        
        <el-form-item label="选择模板" prop="prompt_template">
          <div class="template-control">
            <el-select
              v-model="formData.prompt_template"
              placeholder="请选择系统提示模板"
              @change="handleTemplateChange"
              style="width: 100%"
              clearable
            >
              <el-option label="自定义模板" :value="null" />
              <el-option
                v-for="template in promptTemplates"
                :key="template.id"
                :label="template.name"
                :value="template.id"
              >
                <span>{{ template.name }}</span>
                <span class="template-category">{{ template.category }}</span>
              </el-option>
            </el-select>
            <div class="template-actions">
              <el-button
                type="primary"
                size="small"
                @click="showTemplateDialog = true"
              >
                {{ formData.prompt_template ? '编辑模板' : '新建模板' }}
              </el-button>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="模板内容" prop="system_prompt_template">
          <el-input
            v-model="formData.system_prompt_template"
            type="textarea"
            :rows="4"
            placeholder="请输入系统提示模板内容"
            :disabled="!!formData.prompt_template"
          />
        </el-form-item>
      </div>

      <!-- 高级参数 -->
      <div class="form-section">
        <el-collapse v-model="activeCollapse">
          <el-collapse-item title="高级参数" name="advanced">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Top P" prop="advanced_params.top_p">
                  <el-slider
                    v-model="formData.advanced_params.top_p"
                    :min="0.1"
                    :max="1"
                    :step="0.1"
                    show-input
                    :show-input-controls="false"
                  />
                  <div class="param-description">控制词汇选择的多样性</div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="频率惩罚" prop="advanced_params.frequency_penalty">
                  <el-slider
                    v-model="formData.advanced_params.frequency_penalty"
                    :min="-2"
                    :max="2"
                    :step="0.1"
                    show-input
                    :show-input-controls="false"
                  />
                  <div class="param-description">减少重复内容的出现</div>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="存在惩罚" prop="advanced_params.presence_penalty">
                  <el-slider
                    v-model="formData.advanced_params.presence_penalty"
                    :min="-2"
                    :max="2"
                    :step="0.1"
                    show-input
                    :show-input-controls="false"
                  />
                  <div class="param-description">鼓励讨论新话题</div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="随机种子" prop="advanced_params.seed">
                  <el-input-number
                    v-model="formData.advanced_params.seed"
                    :min="0"
                    :max="999999"
                    style="width: 100%"
                    placeholder="留空表示随机"
                  />
                  <div class="param-description">设置随机种子以获得可重复的结果</div>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="保留Token数" prop="advanced_params.reserved_tokens">
                  <el-input-number
                    v-model="formData.advanced_params.reserved_tokens"
                    :min="0"
                    :max="1000"
                    style="width: 100%"
                    @change="updateMaxTokensLimit"
                  />
                  <div class="param-description">为响应保留的Token数量</div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="停止词" prop="advanced_params.stop_words">
                  <el-select
                    v-model="formData.advanced_params.stop_words"
                    multiple
                    filterable
                    allow-create
                    placeholder="输入停止词并按回车"
                    style="width: 100%"
                  />
                  <div class="param-description">遇到这些词时停止生成</div>
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- 操作按钮 -->
      <div class="form-actions">
        <el-button @click="handleReset">重置</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '更新配置' : '保存配置' }}
        </el-button>
      </div>
    </el-form>

    <!-- 模板编辑对话框 -->
    <PromptTemplateDialog
      v-model:visible="showTemplateDialog"
      :template="currentTemplate"
      @success="handleTemplateSuccess"
    />
  </div>
</template>

<script>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAIConfigStore } from '@/stores/modules/aiConfigStore'
import PromptTemplateDialog from './PromptTemplateDialog.vue'

export default {
  name: 'ModelConfigForm',
  components: {
    PromptTemplateDialog
  },
  props: {
    config: {
      type: Object,
      default: null
    }
  },
  emits: ['success', 'cancel'],
  setup(props, { emit }) {
    const aiConfigStore = useAIConfigStore()
    const formRef = ref()
    
    // 表单数据
    const formData = reactive({
      config_name: '',
      provider: null,
      model: '',
      temperature: 0.7,
      max_tokens: 1000,
      prompt_template: null,
      system_prompt_template: '',
      is_default: false,
      advanced_params: {
        top_p: 1.0,
        frequency_penalty: 0.0,
        presence_penalty: 0.0,
        seed: null,
        reserved_tokens: 256,
        stop_words: []
      }
    })

    // 状态变量
    const submitting = ref(false)
    const activeCollapse = ref(['advanced'])
    const showTemplateDialog = ref(false)
    const currentTemplate = ref(null)
    
    // 数据源
    const providers = ref([])
    const availableModels = ref([])
    const promptTemplates = ref([])
    
    // 计算属性
    const isEdit = computed(() => !!props.config?.id)
    
    const maxTokensLimit = computed(() => {
      if (!formData.model || !availableModels.value.length) return null
      
      const selectedModel = availableModels.value.find(m => m.model_id === formData.model)
      if (!selectedModel) return null
      
      const contextWindow = selectedModel.max_tokens || 4096
      const reservedTokens = formData.advanced_params.reserved_tokens || 256
      return Math.max(1, contextWindow - reservedTokens)
    })
    
    // 表单验证规则
    const formRules = {
      config_name: [
        { required: true, message: '请输入配置名称', trigger: 'blur' },
        { min: 2, max: 50, message: '配置名称长度在 2 到 50 个字符', trigger: 'blur' }
      ],
      provider: [
        { required: true, message: '请选择AI提供商', trigger: 'change' }
      ],
      model: [
        { required: true, message: '请选择AI模型', trigger: 'change' }
      ],
      temperature: [
        { type: 'number', min: 0, max: 2, message: '温度值必须在 0 到 2 之间', trigger: 'change' }
      ],
      max_tokens: [
        { type: 'number', min: 1, message: '最大Token数必须大于0', trigger: 'change' },
        {
          validator: (rule, value, callback) => {
            if (maxTokensLimit.value && value > maxTokensLimit.value) {
              callback(new Error(`最大Token数不能超过 ${maxTokensLimit.value}`))
            } else {
              callback()
            }
          },
          trigger: 'change'
        }
      ]
    }
    
    // 方法
    const loadProviders = async () => {
      try {
        await aiConfigStore.fetchProviders()
        providers.value = aiConfigStore.providers
      } catch (error) {
        ElMessage.error('加载提供商失败')
        console.error('加载提供商失败:', error)
      }
    }
    
    const loadPromptTemplates = async () => {
      try {
        const response = await aiConfigStore.fetchPromptTemplates()
        promptTemplates.value = response || []
      } catch (error) {
        ElMessage.error('加载提示模板失败')
        console.error('加载提示模板失败:', error)
      }
    }
    
    const handleProviderChange = async (providerId) => {
      formData.model = ''
      availableModels.value = []
      
      if (!providerId) return
      
      try {
        const response = await aiConfigStore.fetchAvailableModels(providerId)
        availableModels.value = response || []
      } catch (error) {
        ElMessage.error('加载模型失败')
        console.error('加载模型失败:', error)
      }
    }
    
    const handleModelChange = () => {
      // 当切换模型时，自动调整max_tokens以确保不超过限制
      if (maxTokensLimit.value && formData.max_tokens > maxTokensLimit.value) {
        formData.max_tokens = maxTokensLimit.value
      }
    }
    
    const updateMaxTokensLimit = () => {
      // 当reserved_tokens变更时，重新计算并调整max_tokens
      if (maxTokensLimit.value && formData.max_tokens > maxTokensLimit.value) {
        formData.max_tokens = maxTokensLimit.value
      }
    }
    
    const handleTemplateChange = (templateId) => {
      if (templateId) {
        const template = promptTemplates.value.find(t => t.id === templateId)
        if (template) {
          formData.system_prompt_template = template.content
          currentTemplate.value = template
        }
      } else {
        formData.system_prompt_template = ''
        currentTemplate.value = null
      }
    }
    
    const handleTemplateSuccess = async (template) => {
      showTemplateDialog.value = false
      await loadPromptTemplates()
      
      if (template.id) {
        formData.prompt_template = template.id
        formData.system_prompt_template = template.content
      }
      
      ElMessage.success('模板操作成功')
    }
    
    const handleSubmit = async () => {
      try {
        const valid = await formRef.value.validate()
        if (!valid) return
        
        submitting.value = true
        
        const submitData = {
          ...formData,
          advanced_params: JSON.stringify(formData.advanced_params)
        }
        
        if (isEdit.value) {
          await aiConfigStore.updateModelConfig(props.config.id, submitData)
          ElMessage.success('配置更新成功')
        } else {
          await aiConfigStore.createModelConfig(submitData)
          ElMessage.success('配置创建成功')
        }
        
        emit('success')
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新配置失败' : '创建配置失败')
        console.error('提交失败:', error)
      } finally {
        submitting.value = false
      }
    }
    
    const handleReset = () => {
      formRef.value.resetFields()
      if (props.config) {
        initializeForm()
      }
    }
    
    const initializeForm = () => {
      if (props.config) {
        Object.assign(formData, {
          config_name: props.config.config_name || '',
          provider: props.config.provider || null,
          model: props.config.model || '',
          temperature: props.config.temperature || 0.7,
          max_tokens: props.config.max_tokens || 1000,
          prompt_template: props.config.prompt_template || null,
          system_prompt_template: props.config.system_prompt_template || '',
          is_default: props.config.is_default || false,
          advanced_params: {
            top_p: 1.0,
            frequency_penalty: 0.0,
            presence_penalty: 0.0,
            seed: null,
            reserved_tokens: 256,
            stop_words: [],
            ...((typeof props.config.advanced_params === 'string') 
              ? JSON.parse(props.config.advanced_params || '{}')
              : (props.config.advanced_params || {}))
          }
        })
        
        // 如果有provider，加载对应的模型
        if (formData.provider) {
          handleProviderChange(formData.provider)
        }
      }
    }
    
    // 监听props变化
    watch(() => props.config, () => {
      initializeForm()
    }, { immediate: true, deep: true })
    
    // 生命周期
    onMounted(async () => {
      await Promise.all([
        loadProviders(),
        loadPromptTemplates()
      ])
      
      if (props.config) {
        initializeForm()
      }
    })
    
    return {
      formRef,
      formData,
      formRules,
      submitting,
      activeCollapse,
      showTemplateDialog,
      currentTemplate,
      providers,
      availableModels,
      promptTemplates,
      isEdit,
      maxTokensLimit,
      handleProviderChange,
      handleModelChange,
      updateMaxTokensLimit,
      handleTemplateChange,
      handleTemplateSuccess,
      handleSubmit,
      handleReset
    }
  }
}
</script>

<style scoped>
.model-config-form {
  max-width: 800px;
  margin: 0 auto;
}

.config-form {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #f0f0f0;
}

.temperature-control {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.temperature-slider {
  flex: 1;
}

.temperature-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 80px;
}

.temp-value {
  font-weight: 600;
  color: #667eea;
  min-width: 30px;
}

.max-tokens-control {
  position: relative;
}

.tokens-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
  font-size: 0.8rem;
}

.tokens-limit {
  color: #666;
}

.template-control {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.template-control .el-select {
  flex: 1;
}

.template-category {
  font-size: 0.8rem;
  color: #999;
  margin-left: 0.5rem;
}

.param-description {
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.25rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #f0f0f0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .config-form {
    padding: 1rem;
  }
  
  .temperature-control {
    flex-direction: column;
    align-items: stretch;
  }
  
  .template-control {
    flex-direction: column;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>
