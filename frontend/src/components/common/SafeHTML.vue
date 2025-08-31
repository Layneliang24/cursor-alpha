<!--
安全HTML渲染组件
用于安全地渲染用户输入的HTML内容，防止XSS攻击
-->
<template>
  <div 
    v-if="safeContent" 
    :class="className"
    v-html="safeContent"
  />
  <div v-else-if="showFallback" :class="className">
    {{ fallbackText || '内容不可用' }}
  </div>
</template>

<script setup lang="ts">
import { computed, type PropType } from 'vue'
import { sanitizeHTML, containsXSSVectors } from '@/utils/security'

/**
 * 组件属性定义
 */
interface Props {
  /** 原始HTML内容 */
  content: string
  /** 是否使用严格模式清理 */
  strict?: boolean
  /** CSS类名 */
  className?: string
  /** 是否显示回退内容 */
  showFallback?: boolean
  /** 回退文本内容 */
  fallbackText?: string
  /** 是否启用XSS检测警告 */
  enableXSSWarning?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  content: '',
  strict: false,
  className: '',
  showFallback: true,
  fallbackText: '内容不可用',
  enableXSSWarning: true
})

/**
 * 发出的事件
 */
const emit = defineEmits<{
  /** 检测到XSS攻击向量时触发 */
  xssDetected: [originalContent: string]
  /** 内容被清理时触发 */
  contentSanitized: [originalContent: string, sanitizedContent: string]
}>()

/**
 * 安全清理后的内容
 */
const safeContent = computed(() => {
  if (!props.content || typeof props.content !== 'string') {
    return ''
  }

  // 检测XSS攻击向量
  if (props.enableXSSWarning && containsXSSVectors(props.content)) {
    console.warn('SafeHTML: 检测到潜在的XSS攻击向量:', props.content)
    emit('xssDetected', props.content)
  }

  // 清理HTML内容
  const sanitized = sanitizeHTML(props.content, props.strict)
  
  // 如果内容被修改，发出事件
  if (sanitized !== props.content) {
    emit('contentSanitized', props.content, sanitized)
  }

  return sanitized
})
</script>

<style scoped>
/* 基础样式重置，防止样式注入攻击 */
:deep(*) {
  max-width: 100%;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

/* 移除潜在危险的CSS属性 */
:deep(script),
:deep(style),
:deep(link[rel="stylesheet"]),
:deep(meta),
:deep(title) {
  display: none !important;
}

/* 限制定位属性，防止UI劫持 */
:deep(*) {
  position: static !important;
}

/* 安全的链接样式 */
:deep(a) {
  color: #409eff;
  text-decoration: none;
  cursor: pointer;
}

:deep(a:hover) {
  text-decoration: underline;
}

/* 代码块样式 */
:deep(code) {
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

:deep(pre) {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  white-space: pre-wrap;
}

:deep(pre code) {
  background: none;
  padding: 0;
}

/* 引用样式 */
:deep(blockquote) {
  border-left: 4px solid #ddd;
  margin: 0;
  padding-left: 16px;
  color: #666;
  font-style: italic;
}

/* 列表样式 */
:deep(ul),
:deep(ol) {
  padding-left: 20px;
}

:deep(li) {
  margin-bottom: 4px;
}
</style>
