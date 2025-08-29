<template>
  <div class="ai-assistant-chat">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="assistant-info">
        <div class="avatar">
          <el-icon size="24"><Robot /></el-icon>
        </div>
        <div class="info">
          <h3 class="assistant-name">AI英语助教</h3>
          <p class="assistant-status" :class="{ 'online': !loading.ai_response }">
            {{ loading.ai_response ? '正在思考...' : '在线' }}
          </p>
        </div>
      </div>
      
      <div class="chat-actions">
        <el-dropdown @command="handleContextChange">
          <el-button type="text">
            <el-icon><Setting /></el-icon>
            {{ getContextText(currentContext) }}
            <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="general">通用对话</el-dropdown-item>
              <el-dropdown-item command="expression_help">表达解释</el-dropdown-item>
              <el-dropdown-item command="practice">练习对话</el-dropdown-item>
              <el-dropdown-item command="review">复习指导</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        
        <el-button type="text" @click="clearConversation" v-if="messages.length > 0">
          <el-icon><Delete /></el-icon>
          清空对话
        </el-button>
      </div>
    </div>
    
    <!-- 聊天内容区域 -->
    <div class="chat-content" ref="chatContainer">
      <div class="messages-container">
        <!-- 欢迎消息 -->
        <div class="message assistant-message" v-if="messages.length === 0">
          <div class="message-avatar">
            <el-icon><Robot /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-bubble">
              <p>👋 你好！我是你的AI英语助教。</p>
              <p>我可以帮你：</p>
              <ul>
                <li>🔍 解释地道表达的含义和用法</li>
                <li>💬 练习对话场景</li>
                <li>📚 制定个性化学习计划</li>
                <li>🎯 提供学习建议和复习指导</li>
              </ul>
              <p>有什么问题尽管问我吧！</p>
            </div>
          </div>
        </div>
        
        <!-- 对话消息 -->
        <div 
          v-for="message in messages" 
          :key="message.id"
          class="message"
          :class="message.role + '-message'"
        >
          <div class="message-avatar" v-if="message.role === 'assistant'">
            <el-icon><Robot /></el-icon>
          </div>
          
          <div class="message-content">
            <div class="message-bubble">
              <!-- 表达式引用 -->
              <div class="expression-reference" v-if="message.expression_id">
                <el-icon><Link /></el-icon>
                <span>关于表达式 #{{ message.expression_id }}</span>
              </div>
              
              <!-- 消息内容 -->
              <div class="message-text" v-html="formatMessageContent(message.content)"></div>
              
              <!-- 消息时间 -->
              <div class="message-time">
                {{ formatTime(message.timestamp) }}
              </div>
            </div>
          </div>
          
          <div class="message-avatar" v-if="message.role === 'user'">
            <el-icon><User /></el-icon>
          </div>
        </div>
        
        <!-- AI正在输入指示器 -->
        <div class="message assistant-message" v-if="loading.ai_response">
          <div class="message-avatar">
            <el-icon><Robot /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-bubble typing-indicator">
              <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="chat-input">
      <!-- 快捷问题 -->
      <div class="quick-questions" v-if="showQuickQuestions && messages.length === 0">
        <div class="quick-question-label">快速开始：</div>
        <div class="quick-question-buttons">
          <el-button 
            v-for="question in quickQuestions" 
            :key="question.id"
            type="text" 
            size="small"
            @click="sendQuickQuestion(question.text)"
          >
            {{ question.text }}
          </el-button>
        </div>
      </div>
      
      <!-- 表达式上下文 -->
      <div class="expression-context" v-if="contextExpression">
        <div class="context-info">
          <el-icon><InfoFilled /></el-icon>
          <span>当前讨论：{{ contextExpression.expression }}</span>
        </div>
        <el-button type="text" size="small" @click="clearContext">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
      
      <!-- 输入框 -->
      <div class="input-container">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="输入你的问题..."
          @keydown.ctrl.enter="sendMessage"
          @keydown.meta.enter="sendMessage"
          :disabled="loading.ai_response"
          resize="none"
        />
        
        <div class="input-actions">
          <div class="input-hints">
            <span class="hint-text">Ctrl + Enter 发送</span>
          </div>
          
          <div class="action-buttons">
            <el-button 
              type="text" 
              @click="insertTemplate"
              :disabled="loading.ai_response"
            >
              <el-icon><EditPen /></el-icon>
              模板
            </el-button>
            
            <el-button 
              type="primary" 
              @click="sendMessage"
              :loading="loading.ai_response"
              :disabled="!inputMessage.trim()"
            >
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 消息模板选择 -->
    <el-dialog v-model="showTemplateDialog" title="选择消息模板" width="600px">
      <div class="template-list">
        <div 
          v-for="template in messageTemplates" 
          :key="template.id"
          class="template-item"
          @click="selectTemplate(template)"
        >
          <h4>{{ template.title }}</h4>
          <p>{{ template.content }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Robot, User, Setting, ArrowDown, Delete, Link, InfoFilled, 
  Close, EditPen, Promotion 
} from '@element-plus/icons-vue'
import { useLearningStore } from '@/stores/modules/learningStore'
import type { AIConversation, IdiomaticExpression } from '@/stores/modules/learningStore'

// Props
interface Props {
  contextExpression?: IdiomaticExpression
  conversationId?: string
  autoFocus?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  autoFocus: true
})

// Emits
const emit = defineEmits<{
  messagesSent: [message: string]
  contextChange: [context: string]
  expressionSelect: [expressionId: number]
}>()

// Store
const learningStore = useLearningStore()

// 状态
const inputMessage = ref('')
const currentContext = ref<AIConversation['context']>('general')
const showQuickQuestions = ref(true)
const showTemplateDialog = ref(false)
const chatContainer = ref<HTMLElement>()

// 计算属性
const { loading, currentConversation } = learningStore

const messages = computed(() => {
  return currentConversation.value?.messages || []
})

const contextExpression = computed(() => props.contextExpression)

// 快捷问题配置
const quickQuestions = ref([
  { id: 1, text: '帮我解释一个表达式', context: 'expression_help' },
  { id: 2, text: '我想练习对话', context: 'practice' },
  { id: 3, text: '制定学习计划', context: 'general' },
  { id: 4, text: '复习指导', context: 'review' }
])

// 消息模板
const messageTemplates = ref([
  {
    id: 1,
    title: '请求详细解释',
    content: '请详细解释这个表达式的含义、用法和使用场景，并给出几个实际例句。'
  },
  {
    id: 2,
    title: '比较相似表达',
    content: '这个表达式和其他类似表达有什么区别？什么情况下使用更合适？'
  },
  {
    id: 3,
    title: '练习对话',
    content: '我们来练习一段包含这个表达式的对话吧，你扮演对话伙伴。'
  },
  {
    id: 4,
    title: '学习建议',
    content: '基于我的学习进度，你能给我一些个性化的学习建议吗？'
  },
  {
    id: 5,
    title: '制定计划',
    content: '帮我制定一个针对性的学习计划，重点提升我的薄弱环节。'
  }
])

// 方法
const getContextText = (context: string) => {
  const map = {
    general: '通用对话',
    expression_help: '表达解释',
    practice: '练习对话',
    review: '复习指导'
  }
  return map[context] || context
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}小时前`
  
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatMessageContent = (content: string) => {
  // 格式化消息内容，支持简单的markdown
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || loading.ai_response) return
  
  try {
    // 如果没有当前对话，创建新对话
    if (!currentConversation.value) {
      learningStore.startAIConversation(
        currentContext.value, 
        contextExpression.value?.id
      )
    }
    
    // 发送消息
    await learningStore.sendAIMessage(
      message, 
      contextExpression.value?.id
    )
    
    // 清空输入
    inputMessage.value = ''
    showQuickQuestions.value = false
    
    // 滚动到底部
    await nextTick()
    scrollToBottom()
    
    emit('messagesSent', message)
    
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送失败，请重试')
  }
}

const sendQuickQuestion = async (questionText: string) => {
  inputMessage.value = questionText
  await sendMessage()
}

const handleContextChange = (context: AIConversation['context']) => {
  currentContext.value = context
  emit('contextChange', context)
  
  // 如果已有对话，提示用户
  if (messages.value.length > 0) {
    ElMessageBox.confirm(
      '切换对话模式将开始新的对话，当前对话将被保存。是否继续？',
      '确认切换',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      startNewConversation()
    }).catch(() => {
      // 用户取消，恢复原来的context
    })
  } else {
    startNewConversation()
  }
}

const startNewConversation = () => {
  learningStore.startAIConversation(
    currentContext.value,
    contextExpression.value?.id
  )
  showQuickQuestions.value = true
}

const clearConversation = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空当前对话吗？此操作不可撤销。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 清空对话
    if (currentConversation.value) {
      currentConversation.value.messages = []
    }
    
    showQuickQuestions.value = true
    ElMessage.success('对话已清空')
    
  } catch {
    // 用户取消
  }
}

const insertTemplate = () => {
  showTemplateDialog.value = true
}

const selectTemplate = (template: any) => {
  inputMessage.value = template.content
  showTemplateDialog.value = false
}

const scrollToBottom = () => {
  if (chatContainer.value) {
    const container = chatContainer.value
    container.scrollTop = container.scrollHeight
  }
}

const clearContext = () => {
  emit('expressionSelect', 0) // 清除表达式上下文
}

// 生命周期
onMounted(() => {
  // 如果指定了对话ID，加载对话
  if (props.conversationId) {
    // 这里可以加载特定对话
  } else if (contextExpression.value) {
    // 如果有表达式上下文，自动开始表达解释对话
    currentContext.value = 'expression_help'
    startNewConversation()
  }
})

// 监听消息变化，自动滚动
watch(
  () => messages.value.length,
  async () => {
    await nextTick()
    scrollToBottom()
  }
)

// 监听表达式上下文变化
watch(
  () => contextExpression.value,
  (newExpression) => {
    if (newExpression && currentContext.value !== 'expression_help') {
      currentContext.value = 'expression_help'
      startNewConversation()
    }
  }
)
</script>

<style scoped>
.ai-assistant-chat {
  display: flex;
  flex-direction: column;
  height: 600px;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  background: white;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  background: #fafafa;
}

.assistant-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.assistant-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin: 0;
}

.assistant-status {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.assistant-status.online {
  color: #67c23a;
}

.chat-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.assistant-message .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.user-message .message-avatar {
  background: linear-gradient(135deg, #409eff 0%, #36cfc9 100%);
  color: white;
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  position: relative;
}

.assistant-message .message-bubble {
  background: #f0f2f5;
  color: #303133;
}

.user-message .message-bubble {
  background: #409eff;
  color: white;
}

.expression-reference {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #e6a23c;
  margin-bottom: 8px;
  padding: 4px 8px;
  background: rgba(230, 162, 60, 0.1);
  border-radius: 6px;
}

.message-text {
  line-height: 1.5;
  word-wrap: break-word;
}

.message-text :deep(ul) {
  margin: 8px 0;
  padding-left: 20px;
}

.message-text :deep(li) {
  margin-bottom: 4px;
}

.message-text :deep(strong) {
  font-weight: 600;
}

.message-text :deep(em) {
  font-style: italic;
}

.message-text :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.user-message .message-text :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
  margin-top: 4px;
  text-align: right;
}

.typing-indicator {
  background: #f0f2f5 !important;
  padding: 16px !important;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #909399;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input {
  border-top: 1px solid #ebeef5;
  padding: 16px;
  background: white;
}

.quick-questions {
  margin-bottom: 12px;
}

.quick-question-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.quick-question-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.expression-context {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #ecf5ff;
  border-radius: 6px;
  margin-bottom: 12px;
}

.context-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #409eff;
}

.input-container {
  position: relative;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.input-hints {
  font-size: 12px;
  color: #909399;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.template-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.template-item {
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.template-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.template-item h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.template-item p {
  margin: 0;
  color: #606266;
  font-size: 13px;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-assistant-chat {
    height: 500px;
  }
  
  .chat-header {
    padding: 12px 16px;
  }
  
  .assistant-name {
    font-size: 14px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .input-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .action-buttons {
    justify-content: flex-end;
  }
}

/* 滚动条样式 */
.chat-content::-webkit-scrollbar,
.template-list::-webkit-scrollbar {
  width: 6px;
}

.chat-content::-webkit-scrollbar-track,
.template-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-content::-webkit-scrollbar-thumb,
.template-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-content::-webkit-scrollbar-thumb:hover,
.template-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
