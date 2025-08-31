<!--
安全输入组件
提供输入验证、XSS防护和长度限制功能
-->
<template>
  <div class="secure-input">
    <el-input
      v-model="inputValue"
      :type="inputType"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :maxlength="maxLength"
      :show-word-limit="showWordLimit"
      :clearable="clearable"
      :size="size"
      :prefix-icon="prefixIcon"
      :suffix-icon="suffixIcon"
      :rows="rows"
      :autosize="autosize"
      :show-password="showPassword"
      :validate-event="false"
      @input="handleInput"
      @change="handleChange"
      @blur="handleBlur"
      @focus="handleFocus"
      :class="[
        { 'is-danger': hasXSSRisk },
        { 'is-warning': hasLengthWarning }
      ]"
    />
    
    <!-- XSS风险警告 -->
    <div v-if="hasXSSRisk" class="security-warning xss-warning">
      <el-icon><WarningFilled /></el-icon>
      <span>检测到潜在的安全风险内容，已自动清理</span>
    </div>
    
    <!-- 长度警告 -->
    <div v-if="hasLengthWarning" class="security-warning length-warning">
      <el-icon><InfoFilled /></el-icon>
      <span>内容长度已达到上限的 {{ lengthUsagePercent }}%</span>
    </div>
    
    <!-- 自定义错误提示 */
    <div v-if="errorMessage" class="security-warning error-message">
      <el-icon><CircleCloseFilled /></el-icon>
      <span>{{ errorMessage }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, type PropType } from 'vue'
import { ElInput, ElIcon } from 'element-plus'
import { WarningFilled, InfoFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { sanitizeUserInput, containsXSSVectors, SECURITY_CONFIG } from '@/utils/security'

/**
 * 输入类型枚举
 */
type InputType = 'text' | 'textarea' | 'password' | 'email' | 'url' | 'number'

/**
 * 安全规则配置
 */
interface SecurityRule {
  /** 最大长度 */
  maxLength?: number
  /** 是否允许HTML标签 */
  allowHTML?: boolean
  /** 自定义验证函数 */
  validator?: (value: string) => string | null
  /** 是否启用XSS检测 */
  enableXSSDetection?: boolean
}

/**
 * 组件属性
 */
interface Props {
  /** 输入值 */
  modelValue: string
  /** 输入类型 */
  type?: InputType
  /** 占位符 */
  placeholder?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 是否只读 */
  readonly?: boolean
  /** 是否可清空 */
  clearable?: boolean
  /** 尺寸 */
  size?: 'large' | 'default' | 'small'
  /** 前缀图标 */
  prefixIcon?: string
  /** 后缀图标 */
  suffixIcon?: string
  /** 文本域行数 */
  rows?: number
  /** 自适应高度 */
  autosize?: boolean | object
  /** 是否显示密码 */
  showPassword?: boolean
  /** 是否显示字数统计 */
  showWordLimit?: boolean
  /** 安全规则 */
  securityRule?: SecurityRule
  /** 自定义错误消息 */
  customError?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  type: 'text',
  placeholder: '',
  disabled: false,
  readonly: false,
  clearable: false,
  size: 'default',
  prefixIcon: '',
  suffixIcon: '',
  rows: 2,
  autosize: false,
  showPassword: false,
  showWordLimit: false,
  securityRule: () => ({}),
  customError: ''
})

/**
 * 组件事件
 */
const emit = defineEmits<{
  'update:modelValue': [value: string]
  'input': [value: string]
  'change': [value: string]
  'blur': [event: FocusEvent]
  'focus': [event: FocusEvent]
  'xss-detected': [originalValue: string, cleanedValue: string]
  'length-exceeded': [value: string, maxLength: number]
  'validation-error': [error: string]
}>()

// 内部输入值
const inputValue = ref(props.modelValue)
const hasXSSRisk = ref(false)
const hasLengthWarning = ref(false)
const errorMessage = ref(props.customError)

// 计算属性
const inputType = computed(() => {
  return props.type === 'textarea' ? 'textarea' : props.type
})

const maxLength = computed(() => {
  const rule = props.securityRule
  if (rule?.maxLength) {
    return rule.maxLength
  }
  
  // 根据输入类型设置默认最大长度
  switch (props.type) {
    case 'email':
      return SECURITY_CONFIG.MAX_INPUT_LENGTH.EMAIL
    case 'url':
      return SECURITY_CONFIG.MAX_INPUT_LENGTH.URL
    case 'textarea':
      return SECURITY_CONFIG.MAX_INPUT_LENGTH.CONTENT
    default:
      return SECURITY_CONFIG.MAX_INPUT_LENGTH.TITLE
  }
})

const lengthUsagePercent = computed(() => {
  return Math.round((inputValue.value.length / maxLength.value) * 100)
})

/**
 * 监听外部值变化
 */
watch(() => props.modelValue, (newValue) => {
  inputValue.value = newValue
}, { immediate: true })

watch(() => props.customError, (newError) => {
  errorMessage.value = newError
})

/**
 * 安全验证函数
 */
const validateSecurity = (value: string): string => {
  const rule = props.securityRule
  hasXSSRisk.value = false
  hasLengthWarning.value = false
  errorMessage.value = ''
  
  if (!value) {
    return value
  }
  
  // XSS检测
  if (rule?.enableXSSDetection !== false && containsXSSVectors(value)) {
    hasXSSRisk.value = true
    const cleanedValue = sanitizeUserInput(value, maxLength.value)
    emit('xss-detected', value, cleanedValue)
    return cleanedValue
  }
  
  // 长度检查
  if (value.length > maxLength.value) {
    emit('length-exceeded', value, maxLength.value)
    return value.substring(0, maxLength.value)
  }
  
  // 长度警告
  if (value.length > maxLength.value * 0.8) {
    hasLengthWarning.value = true
  }
  
  // 自定义验证
  if (rule?.validator) {
    const validationError = rule.validator(value)
    if (validationError) {
      errorMessage.value = validationError
      emit('validation-error', validationError)
    }
  }
  
  // 基础清理
  return rule?.allowHTML ? value : sanitizeUserInput(value, maxLength.value)
}

/**
 * 事件处理函数
 */
const handleInput = (value: string) => {
  const cleanedValue = validateSecurity(value)
  inputValue.value = cleanedValue
  emit('update:modelValue', cleanedValue)
  emit('input', cleanedValue)
}

const handleChange = (value: string) => {
  const cleanedValue = validateSecurity(value)
  emit('change', cleanedValue)
}

const handleBlur = (event: FocusEvent) => {
  const cleanedValue = validateSecurity(inputValue.value)
  if (cleanedValue !== inputValue.value) {
    inputValue.value = cleanedValue
    emit('update:modelValue', cleanedValue)
  }
  emit('blur', event)
}

const handleFocus = (event: FocusEvent) => {
  emit('focus', event)
}
</script>

<style scoped>
.secure-input {
  position: relative;
}

.security-warning {
  display: flex;
  align-items: center;
  margin-top: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.4;
}

.security-warning .el-icon {
  margin-right: 4px;
  font-size: 14px;
}

.xss-warning {
  background-color: #fef0f0;
  border: 1px solid #fbc4c4;
  color: #f56c6c;
}

.length-warning {
  background-color: #fdf6ec;
  border: 1px solid #f5dab1;
  color: #e6a23c;
}

.error-message {
  background-color: #fef0f0;
  border: 1px solid #fbc4c4;
  color: #f56c6c;
}

/* Element Plus 样式覆盖 */
:deep(.el-input.is-danger .el-input__wrapper) {
  border-color: #f56c6c !important;
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.el-input.is-warning .el-input__wrapper) {
  border-color: #e6a23c !important;
  box-shadow: 0 0 0 1px #e6a23c inset !important;
}

:deep(.el-textarea.is-danger .el-textarea__inner) {
  border-color: #f56c6c !important;
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.el-textarea.is-warning .el-textarea__inner) {
  border-color: #e6a23c !important;
  box-shadow: 0 0 0 1px #e6a23c inset !important;
}
</style>
