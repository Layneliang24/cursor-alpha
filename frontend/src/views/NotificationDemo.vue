<template>
  <div class="notification-demo">
    <div class="demo-header">
      <h1>🔊 声音提示系统演示</h1>
      <p>用于在开发流程中自动发出声音提示，帮助用户及时了解开发进度和需要确认的操作</p>
    </div>

    <div class="demo-content">
      <!-- 控制面板 -->
      <div class="control-panel">
        <h2>🎛️ 控制面板</h2>
        <div class="controls">
          <el-button 
            :type="isSoundEnabled ? 'success' : 'info'"
            size="large"
            @click="toggleSound"
          >
            <el-icon><Volume /></el-icon>
            {{ isSoundEnabled ? '声音开启' : '声音关闭' }}
          </el-button>
          
          <el-button 
            type="warning" 
            size="large"
            @click="stopAllSounds"
          >
            <el-icon><VideoPause /></el-icon>
            停止所有声音
          </el-button>
          
          <el-button 
            type="danger" 
            size="large"
            @click="clearHistory"
          >
            <el-icon><Delete /></el-icon>
            清除历史
          </el-button>
        </div>
      </div>

      <!-- 测试区域 -->
      <div class="test-section">
        <h2>🧪 测试声音</h2>
        <div class="test-buttons">
          <el-button @click="testNotify" type="info" size="large">
            <el-icon><Bell /></el-icon>
            测试通知
          </el-button>
          <el-button @click="testConfirm" type="success" size="large">
            <el-icon><Check /></el-icon>
            测试确认
          </el-button>
          <el-button @click="testAlert" type="warning" size="large">
            <el-icon><Warning /></el-icon>
            测试警告
          </el-button>
          <el-button @click="testUrgent" type="danger" size="large">
            <el-icon><AlarmClock /></el-icon>
            测试紧急
          </el-button>
        </div>
      </div>

      <!-- 开发流程演示 -->
      <div class="workflow-section">
        <h2>🔄 开发流程演示</h2>
        <div class="workflow-buttons">
          <el-button @click="demoRequirementsAnalysis" type="primary" size="large">
            需求分析演示
          </el-button>
          <el-button @click="demoDevelopment" type="primary" size="large">
            开发过程演示
          </el-button>
          <el-button @click="demoTesting" type="primary" size="large">
            测试过程演示
          </el-button>
          <el-button @click="demoDeployment" type="primary" size="large">
            部署过程演示
          </el-button>
        </div>
      </div>

      <!-- 通知历史 -->
      <div class="history-section">
        <h2>📋 通知历史</h2>
        <div class="history-list">
          <div 
            v-for="notification in notificationHistory" 
            :key="notification.id"
            class="notification-item"
            :class="notification.type"
          >
            <div class="notification-icon">
              <el-icon v-if="notification.type === 'notify'"><Bell /></el-icon>
              <el-icon v-else-if="notification.type === 'confirm'"><Check /></el-icon>
              <el-icon v-else-if="notification.type === 'alert'"><Warning /></el-icon>
              <el-icon v-else-if="notification.type === 'urgent'"><AlarmClock /></el-icon>
            </div>
            <div class="notification-content">
              <div class="notification-message">{{ notification.message }}</div>
              <div class="notification-time">
                {{ formatTime(notification.timestamp) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Bell, Check, Warning, AlarmClock, Volume, VideoPause, Delete } from '@element-plus/icons-vue'
import notificationManager from '../utils/notificationManager'
import developmentFlowHelper from '../utils/developmentFlowHelper'

// 响应式数据
const isSoundEnabled = ref(true)
const notificationHistory = ref([])

// 方法
const toggleSound = () => {
  isSoundEnabled.value = notificationManager.toggleSound()
}

const stopAllSounds = () => {
  notificationManager.stopAll()
}

const clearHistory = () => {
  notificationManager.clearHistory()
  updateHistory()
}

const updateHistory = () => {
  notificationHistory.value = notificationManager.getHistory(20)
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

// 测试方法
const testNotify = () => {
  notificationManager.notify('这是一条测试通知消息')
  updateHistory()
}

const testConfirm = () => {
  notificationManager.confirm('这是一条测试确认消息')
  updateHistory()
}

const testAlert = () => {
  notificationManager.alert('这是一条测试警告消息')
  updateHistory()
}

const testUrgent = () => {
  notificationManager.urgent('这是一条测试紧急消息')
  updateHistory()
}

// 开发流程演示
const demoRequirementsAnalysis = () => {
  developmentFlowHelper.requirementsAnalysis.start('用户积分系统')
  setTimeout(() => {
    developmentFlowHelper.requirementsAnalysis.complete('用户积分系统', '分析完成，包含积分获取、消费、兑换等功能')
  }, 2000)
  updateHistory()
}

const demoDevelopment = () => {
  developmentFlowHelper.development.start('用户积分系统')
  setTimeout(() => {
    developmentFlowHelper.development.complete('用户积分系统')
  }, 2000)
  updateHistory()
}

const demoTesting = () => {
  developmentFlowHelper.testing.start('单元测试')
  setTimeout(() => {
    developmentFlowHelper.testing.complete('单元测试', 'success', 50)
  }, 2000)
  updateHistory()
}

const demoDeployment = () => {
  developmentFlowHelper.deployment.prepare('生产环境')
  setTimeout(() => {
    developmentFlowHelper.deployment.needsAuthorization('数据库迁移', '影响现有数据')
  }, 2000)
  updateHistory()
}

// 生命周期
onMounted(() => {
  updateHistory()
  
  // 定期更新历史记录
  setInterval(updateHistory, 1000)
})
</script>

<style scoped>
.notification-demo {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.demo-header {
  text-align: center;
  margin-bottom: 40px;
}

.demo-header h1 {
  color: #303133;
  margin-bottom: 10px;
}

.demo-header p {
  color: #606266;
  font-size: 16px;
}

.demo-content {
  display: grid;
  gap: 30px;
}

.control-panel,
.test-section,
.workflow-section,
.history-section {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
}

.control-panel h2,
.test-section h2,
.workflow-section h2,
.history-section h2 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 18px;
}

.controls,
.test-buttons,
.workflow-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item:hover {
  background-color: #f5f7fa;
}

.notification-item.notify {
  border-left: 4px solid #409eff;
}

.notification-item.confirm {
  border-left: 4px solid #67c23a;
}

.notification-item.alert {
  border-left: 4px solid #e6a23c;
}

.notification-item.urgent {
  border-left: 4px solid #f56c6c;
}

.notification-icon {
  margin-right: 12px;
  margin-top: 2px;
  color: #909399;
  font-size: 18px;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-message {
  font-size: 14px;
  color: #303133;
  margin-bottom: 6px;
  word-break: break-word;
}

.notification-time {
  font-size: 12px;
  color: #909399;
}

@media (max-width: 768px) {
  .controls,
  .test-buttons,
  .workflow-buttons {
    flex-direction: column;
  }
  
  .controls .el-button,
  .test-buttons .el-button,
  .workflow-buttons .el-button {
    width: 100%;
  }
}
</style> 