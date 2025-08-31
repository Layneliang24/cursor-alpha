<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑提供商' : '添加提供商'"
    width="600px"
    :before-close="handleClose"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
      label-position="left"
    >
      <!-- 基本信息 -->
      <div class="form-section">
        <div class="section-title">基本信息</div>
        
        <el-form-item label="提供商类型" prop="provider_type" required>
          <el-select
            v-model="formData.provider_type"
            placeholder="选择AI提供商类型"
            style="width: 100%"
            @change="handleProviderTypeChange"
          >
            <el-option
              v-for="option in providerOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            >
              <div class="provider-option">
                <i :class="option.icon"></i>
                <span>{{ option.label }}</span>
                <el-tag v-if="option.recommended" size="small" type="success">推荐</el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="显示名称" prop="display_name" required>
          <SecureInput
            v-model="formData.display_name"
            placeholder="输入提供商显示名称"
            :security-rule="{
              maxLength: 100,
              enableXSSDetection: true,
              validator: validateDisplayName
            }"
            show-word-limit
            @xss-detected="handleXSSDetected"
          />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <SecureInput
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="输入提供商描述信息（可选）"
            :security-rule="{
              maxLength: 500,
              enableXSSDetection: true
            }"
            show-word-limit
            @xss-detected="handleXSSDetected"
          />
        </el-form-item>
      </div>

      <!-- API配置 -->
      <div class="form-section">
        <div class="section-title">API配置</div>
        
        <el-form-item label="API端点" prop="api_endpoint" required>
          <SecureInput
            v-model="formData.api_endpoint"
            type="url"
            placeholder="输入API端点URL"
            :security-rule="{
              maxLength: 2048,
              enableXSSDetection: true,
              validator: validateURL
            }"
            @xss-detected="handleXSSDetected"
          />
        </el-form-item>

        <el-form-item label="API版本" prop="api_version">
          <el-input
            v-model="formData.api_version"
            placeholder="输入API版本（如：v1）"
          />
        </el-form-item>

        <el-form-item label="请求超时" prop="request_timeout">
          <el-input-number
            v-model="formData.request_timeout"
            :min="1"
            :max="300"
            :step="1"
            controls-position="right"
            style="width: 100%"
          />
          <div class="field-help">请求超时时间（秒），建议30-60秒</div>
        </el-form-item>
      </div>

      <!-- 高级配置 -->
      <div class="form-section">
        <div class="section-title">高级配置</div>
        
        <el-form-item label="最大重试次数" prop="max_retries">
          <el-input-number
            v-model="formData.max_retries"
            :min="0"
            :max="10"
            :step="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="速率限制" prop="rate_limit">
          <el-input-number
            v-model="formData.rate_limit"
            :min="1"
            :max="10000"
            :step="1"
            controls-position="right"
            style="width: 100%"
          />
          <div class="field-help">每分钟最大请求数</div>
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-select v-model="formData.priority" style="width: 100%">
            <el-option label="高优先级" value="high" />
            <el-option label="中优先级" value="medium" />
            <el-option label="低优先级" value="low" />
          </el-select>
        </el-form-item>

        <el-form-item label="启用状态">
          <el-switch
            v-model="formData.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </div>

      <!-- 特定配置 -->
      <div v-if="hasSpecificConfig" class="form-section">
        <div class="section-title">{{ getSpecificConfigTitle() }}</div>
        
        <!-- OpenAI特定配置 -->
        <template v-if="formData.provider_type === 'openai'">
          <el-form-item label="组织ID" prop="config.organization_id">
            <el-input
              v-model="formData.config.organization_id"
              placeholder="输入OpenAI组织ID（可选）"
            />
          </el-form-item>
        </template>

        <!-- Azure特定配置 -->
        <template v-if="formData.provider_type === 'azure'">
          <el-form-item label="部署名称" prop="config.deployment_name" required>
            <el-input
              v-model="formData.config.deployment_name"
              placeholder="输入Azure部署名称"
            />
          </el-form-item>
          <el-form-item label="资源名称" prop="config.resource_name">
            <el-input
              v-model="formData.config.resource_name"
              placeholder="输入Azure资源名称"
            />
          </el-form-item>
        </template>

        <!-- 本地模型配置 -->
        <template v-if="formData.provider_type === 'local'">
          <el-form-item label="模型路径" prop="config.model_path">
            <el-input
              v-model="formData.config.model_path"
              placeholder="输入本地模型文件路径"
            />
          </el-form-item>
          <el-form-item label="GPU设备" prop="config.device">
            <el-select v-model="formData.config.device" style="width: 100%">
              <el-option label="自动选择" value="auto" />
              <el-option label="CPU" value="cpu" />
              <el-option label="CUDA" value="cuda" />
            </el-select>
          </el-form-item>
        </template>
      </div>
    </el-form>

    <!-- 对话框底部操作按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleTestConnection"
          :loading="testing"
          :disabled="!canTest"
        >
          测试连接
        </el-button>
        <el-button 
          type="primary" 
          @click="handleSubmit"
          :loading="submitting"
        >
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useAIConfigStore } from '@/stores/modules/aiConfigStore'
import SecureInput from '@/components/common/SecureInput.vue'
import { sanitizeURL } from '@/utils/security'

// Props & Emits
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  provider: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'success'])

// Store
const aiConfigStore = useAIConfigStore()

// Refs
const formRef = ref()
const testing = ref(false)
const submitting = ref(false)

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const isEdit = computed(() => !!props.provider?.id)

const hasSpecificConfig = computed(() => {
  return ['openai', 'azure', 'local'].includes(formData.value.provider_type)
})

const canTest = computed(() => {
  return formData.value.provider_type && 
         formData.value.api_endpoint && 
         formData.value.display_name
})

// 表单数据
const formData = ref({
  provider_type: '',
  display_name: '',
  description: '',
  api_endpoint: '',
  api_version: 'v1',
  request_timeout: 30,
  max_retries: 3,
  rate_limit: 60,
  priority: 'medium',
  is_active: true,
  config: {}
})

// 表单验证规则
const formRules = {
  provider_type: [
    { required: true, message: '请选择提供商类型', trigger: 'change' }
  ],
  display_name: [
    { required: true, message: '请输入显示名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在2到100个字符', trigger: 'blur' }
  ],
  api_endpoint: [
    { required: true, message: '请输入API端点', trigger: 'blur' },
    { 
      pattern: /^https?:\/\/.+/, 
      message: '请输入有效的URL地址', 
      trigger: 'blur' 
    }
  ]
}

// 提供商选项
const providerOptions = [
  {
    value: 'openai',
    label: 'OpenAI',
    icon: 'fas fa-robot',
    recommended: true
  },
  {
    value: 'anthropic',
    label: 'Anthropic (Claude)',
    icon: 'fas fa-brain',
    recommended: true
  },
  {
    value: 'google',
    label: 'Google (Gemini)',
    icon: 'fab fa-google'
  },
  {
    value: 'azure',
    label: 'Azure OpenAI',
    icon: 'fab fa-microsoft'
  },
  {
    value: 'openrouter',
    label: 'OpenRouter',
    icon: 'fas fa-route'
  },
  {
    value: 'siliconflow',
    label: 'SiliconFlow',
    icon: 'fas fa-microchip'
  },
  {
    value: 'chenmoai',
    label: 'ChenmoAI',
    icon: 'fas fa-cloud'
  },
  {
    value: 'local',
    label: '本地模型',
    icon: 'fas fa-server'
  }
]

// 监听props变化
watch(() => props.provider, (newProvider) => {
  if (newProvider) {
    // 编辑模式，填充表单数据
    formData.value = {
      ...formData.value,
      ...newProvider,
      config: newProvider.config || {}
    }
  } else {
    // 新增模式，重置表单
    resetForm()
  }
}, { immediate: true, deep: true })

// 监听对话框显示状态
watch(visible, (newVisible) => {
  if (newVisible && formRef.value) {
    nextTick(() => {
      formRef.value.clearValidate()
    })
  }
})

// 方法
const resetForm = () => {
  formData.value = {
    provider_type: '',
    display_name: '',
    description: '',
    api_endpoint: '',
    api_version: 'v1',
    request_timeout: 30,
    max_retries: 3,
    rate_limit: 60,
    priority: 'medium',
    is_active: true,
    config: {}
  }
}

const handleProviderTypeChange = (type) => {
  // 重置特定配置
  formData.value.config = {}
  
  // 设置默认API端点
  const defaultEndpoints = {
    'openai': 'api.openai.com/v1',
    'anthropic': 'api.anthropic.com/v1',
    'google': 'generativelanguage.googleapis.com/v1',
    'azure': 'your-resource.openai.azure.com',
    'openrouter': 'openrouter.ai/api/v1',
    'siliconflow': 'api.siliconflow.cn/v1',
    'chenmoai': 'api.chenmoai.cn/v1',
    'local': 'localhost:11434/api'
  }
  
  if (defaultEndpoints[type]) {
    formData.value.api_endpoint = defaultEndpoints[type]
  }
  
  // 设置默认显示名称
  const option = providerOptions.find(opt => opt.value === type)
  if (option && !formData.value.display_name) {
    formData.value.display_name = option.label
  }
}

const getSpecificConfigTitle = () => {
  const titles = {
    'openai': 'OpenAI配置',
    'azure': 'Azure配置',
    'local': '本地模型配置'
  }
  return titles[formData.value.provider_type] || '特定配置'
}

const handleTestConnection = async () => {
  // 先验证必填字段
  const requiredFields = ['provider_type', 'display_name', 'api_endpoint']
  for (const field of requiredFields) {
    if (!formData.value[field]) {
      ElMessage.warning('请先填写必填字段')
      return
    }
  }

  testing.value = true
  try {
    const result = await aiConfigStore.testProviderConfig(formData.value)
    if (result.is_healthy) {
      ElMessage.success('连接测试成功！')
    } else {
      ElMessage.error(`连接测试失败: ${result.error || '未知错误'}`)
    }
  } catch (error) {
    ElMessage.error('连接测试失败')
    console.error('Test connection error:', error)
  } finally {
    testing.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.warning('请检查表单填写')
    return
  }

  submitting.value = true
  try {
    if (isEdit.value) {
      await aiConfigStore.updateProvider(props.provider.id, formData.value)
      ElMessage.success('提供商更新成功')
    } else {
      await aiConfigStore.createProvider(formData.value)
      ElMessage.success('提供商创建成功')
    }
    
    emit('success')
    handleClose()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    console.error('Submit error:', error)
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  visible.value = false
  resetForm()
}

// 安全验证函数
const validateDisplayName = (value) => {
  if (!value || value.trim().length === 0) {
    return '显示名称不能为空'
  }
  if (value.length < 2) {
    return '显示名称至少需要2个字符'
  }
  if (!/^[\w\s\u4e00-\u9fa5\-_.()]+$/.test(value)) {
    return '显示名称包含不允许的字符'
  }
  return null
}

const validateURL = (value) => {
  if (!value || value.trim().length === 0) {
    return 'API端点不能为空'
  }
  
  // 添加协议前缀进行验证
  const urlToValidate = value.startsWith('http') ? value : `https://${value}`
  
  try {
    const url = new URL(urlToValidate)
    if (!['http:', 'https:'].includes(url.protocol)) {
      return '仅支持HTTP和HTTPS协议'
    }
    if (!url.hostname || url.hostname.length < 3) {
      return 'URL格式不正确'
    }
    return null
  } catch (error) {
    return 'URL格式不正确'
  }
}

const handleXSSDetected = (originalValue, cleanedValue) => {
  ElMessage.warning('检测到潜在的安全风险内容，已自动清理')
  console.warn('XSS防护:', { originalValue, cleanedValue })
}
</script>

<style scoped lang="scss">
.form-section {
  margin-bottom: 24px;
  
  .section-title {
    font-size: 14px;
    font-weight: 500;
    color: #303133;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #ebeef5;
  }
}

.provider-option {
  display: flex;
  align-items: center;
  gap: 8px;
  
  i {
    width: 16px;
    color: #606266;
  }
  
  span {
    flex: 1;
  }
}

.field-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

// Element Plus 表单样式优化
:deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
}

:deep(.el-input-group__prepend) {
  background-color: #f5f7fa;
  color: #909399;
  border-color: #dcdfe6;
}

:deep(.el-select .el-input) {
  .el-input__inner {
    cursor: pointer;
  }
}

:deep(.el-switch) {
  .el-switch__label {
    color: #606266;
    font-weight: 500;
    
    &.is-active {
      color: #409eff;
    }
  }
}
</style>
