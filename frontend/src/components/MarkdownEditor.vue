<template>
  <div class="markdown-editor">
    <div class="editor-container">
      <div class="editor-panel">
        <div class="panel-header">
          <h4>编辑器</h4>
          <div class="editor-tools">
            <el-button size="small" @click="insertText('# ', '')" title="标题1">H1</el-button>
            <el-button size="small" @click="insertText('**', '**')" title="粗体">B</el-button>
            <el-button size="small" @click="insertText('*', '*')" title="斜体">I</el-button>
            <el-button size="small" @click="insertText('~~', '~~')" title="删除线">S</el-button>
            <el-button size="small" @click="insertText('`', '`')" title="行内代码">`</el-button>
            <el-button size="small" @click="insertCodeBlock" title="代码块">```</el-button>
            <el-button size="small" @click="insertText('> ', '')" title="引用">“</el-button>
            <el-button size="small" @click="insertText('- ', '')" title="无序列表">•</el-button>
            <el-button size="small" @click="insertText('1. ', '')" title="有序列表">1.</el-button>
            <el-button size="small" @click="insertLink" title="链接">@</el-button>
            <el-button size="small" @click="insertImage" title="图片">□</el-button>
            <el-button size="small" @click="insertTable" title="表格">☷</el-button>
          </div>
        </div>
        <textarea
          ref="textareaRef"
          v-model="content"
          @input="handleInput"
          @scroll="syncScroll"
          @paste="handlePaste"
          class="markdown-input"
          :placeholder="placeholderText"
        ></textarea>
      </div>
      
      <div class="preview-panel">
        <div class="panel-header">
          <h4>预览</h4>
        </div>
        <div 
          ref="previewRef"
          class="markdown-preview"
          v-html="renderedContent"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import { Rank, Document, ChatLineRound, List, Menu, Link, Picture, Grid } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const textareaRef = ref()
const previewRef = ref()
const content = ref(props.modelValue)

const placeholderText = `请输入Markdown内容...

常用语法提示：
# 一级标题
## 二级标题
**粗体文本**
*斜体文本*
~~删除线~~
\`行内代码\`
> 引用文本
- 无序列表
1. 有序列表
[链接文本](URL)
![图片描述](URL)

提示：可直接粘贴图片！`

// 配置marked
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (err) {}
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true
})

const renderedContent = computed(() => {
  const markdownText = content.value || ''
  return marked(markdownText)
})

const handleInput = () => {
  emit('update:modelValue', content.value)
}

const insertText = (before, after = '') => {
  const textarea = textareaRef.value
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = content.value.substring(start, end)
  
  const newText = content.value.substring(0, start) + 
                  before + selectedText + after + 
                  content.value.substring(end)
  
  content.value = newText
  emit('update:modelValue', content.value)
  
  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(start + before.length, end + before.length)
  })
}

const insertCodeBlock = () => {
  insertText('\n```javascript\n', '\n```\n')
}

const insertLink = () => {
  insertText('[', '](https://)')
}

const insertImage = () => {
  insertText('![', '](https://)')
}

const insertTable = () => {
  const table = `\n| 列1 | 列2 | 列3 |\n|------|------|------|\n| 内容1 | 内容2 | 内容3 |\n| 内容4 | 内容5 | 内容6 |\n`
  insertText(table, '')
}

// 处理粘贴事件
const handlePaste = async (e) => {
  const items = e.clipboardData?.items
  if (!items) return
  
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (item.type.indexOf('image') !== -1) {
      e.preventDefault()
      const file = item.getAsFile()
      if (file) {
        await uploadImage(file)
      }
      break
    }
  }
}

// 上传图片
const uploadImage = async (file) => {
  try {
    // 显示上传中状态
    const imageName = file.name || '粘贴图片'
    const uploadingText = `![${imageName}](上传中...)`
    insertText(uploadingText, '')
    
    // 调用上传API
    const { uploadImage: uploadAPI } = await import('@/api/upload')
    const response = await uploadAPI(file)
    
    // 替换上传中的文本为实际URL
    const currentContent = content.value
    const actualImageText = `![${imageName}](${response.url})`
    content.value = currentContent.replace(uploadingText, actualImageText)
    emit('update:modelValue', content.value)
    
  } catch (error) {
    console.error('图片上传失败:', error)
    
    // 显示上传失败
    const imageName = file.name || '粘贴图片'
    const failedText = `![${imageName}](上传失败)`
    const uploadingText = `![${imageName}](上传中...)`
    const currentContent = content.value
    content.value = currentContent.replace(uploadingText, failedText)
    emit('update:modelValue', content.value)
  }
}

const syncScroll = () => {
  const textarea = textareaRef.value
  const preview = previewRef.value
  if (textarea && preview) {
    const scrollRatio = textarea.scrollTop / (textarea.scrollHeight - textarea.clientHeight)
    preview.scrollTop = scrollRatio * (preview.scrollHeight - preview.clientHeight)
  }
}

// 监听props变化
import { watch } from 'vue'
watch(() => props.modelValue, (newVal) => {
  content.value = newVal
})
</script>

<style scoped>
.markdown-editor {
  width: 100%;
  height: 650px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.editor-container {
  display: flex;
  height: 100%;
}

.editor-panel,
.preview-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.editor-panel {
  border-right: 1px solid #e4e7ed;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  height: 48px;
  box-sizing: border-box;
}

.panel-header h4 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.editor-tools {
  display: flex;
  gap: 1px;
}

.editor-tools .el-button {
  padding: 2px 4px;
  font-size: 11px;
  min-height: 24px;
  min-width: 24px;
  border: 1px solid #ddd;
  background: white;
  font-weight: bold;
}

.editor-tools .el-button:hover {
  background: #f0f0f0;
  border-color: #999;
}

.markdown-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 16px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  background: #fff;
}

.markdown-preview {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #fff;
  font-size: 14px;
  line-height: 1.6;
}

:deep(.markdown-preview h1),
:deep(.markdown-preview h2),
:deep(.markdown-preview h3),
:deep(.markdown-preview h4),
:deep(.markdown-preview h5),
:deep(.markdown-preview h6) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

:deep(.markdown-preview h1) {
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 10px;
}

:deep(.markdown-preview h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 8px;
}

:deep(.markdown-preview p) {
  margin-bottom: 16px;
}

:deep(.markdown-preview code) {
  background: #f6f8fa;
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 85%;
}

:deep(.markdown-preview pre) {
  background: #f6f8fa;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin-bottom: 16px;
}

:deep(.markdown-preview blockquote) {
  border-left: 4px solid #dfe2e5;
  padding-left: 16px;
  color: #6a737d;
  margin: 16px 0;
}

:deep(.markdown-preview ul),
:deep(.markdown-preview ol) {
  padding-left: 24px;
  margin-bottom: 16px;
}

:deep(.markdown-preview table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 16px;
}

:deep(.markdown-preview th),
:deep(.markdown-preview td) {
  border: 1px solid #dfe2e5;
  padding: 8px 12px;
  text-align: left;
}

:deep(.markdown-preview th) {
  background: #f6f8fa;
  font-weight: 600;
}
</style>