import { useNotificationSound } from '../hooks/useNotificationSound'

/**
 * 通知管理器
 * 用于在开发流程中自动触发声音提示
 */
class NotificationManager {
  constructor () {
    this.sound = useNotificationSound()
    this.isEnabled = true
    this.notificationHistory = []
  }

  /**
   * 启用/禁用声音提示
   */
  toggleSound (enabled = null) {
    if (enabled !== null) {
      this.isEnabled = enabled
    } else {
      this.isEnabled = !this.isEnabled
    }
    console.log(`🔊 声音提示已${this.isEnabled ? '启用' : '禁用'}`)
    return this.isEnabled
  }

  /**
   * 记录通知历史
   */
  logNotification (type, message, timestamp = new Date()) {
    this.notificationHistory.push({
      type,
      message,
      timestamp,
      id: Date.now() + Math.random(),
    })
    
    // 保持历史记录在合理范围内
    if (this.notificationHistory.length > 100) {
      this.notificationHistory = this.notificationHistory.slice(-50)
    }
  }

  /**
   * 一般通知（用于信息提示）
   */
  notify (message = '有新通知') {
    if (!this.isEnabled) return
    
    this.logNotification('notify', message)
    this.sound.notify()
    
    console.log(`🔔 通知: ${message}`)
  }

  /**
   * 确认通知（用于需要确认的操作）
   */
  confirm (message = '需要确认操作') {
    if (!this.isEnabled) return
    
    this.logNotification('confirm', message)
    this.sound.confirm()
    
    console.log(`✅ 确认: ${message}`)
  }

  /**
   * 警告通知（用于需要授权的操作）
   */
  alert (message = '需要授权操作') {
    if (!this.isEnabled) return
    
    this.logNotification('alert', message)
    this.sound.alert()
    
    console.log(`⚠️ 警告: ${message}`)
  }

  /**
   * 紧急通知（用于重要操作）
   */
  urgent (message = '紧急操作需要处理', times = 3) {
    if (!this.isEnabled) return
    
    this.logNotification('urgent', message)
    this.sound.urgent(times)
    
    console.log(`🚨 紧急: ${message}`)
  }

  /**
   * 开发流程通知
   */
  developmentFlow = {
    // 需求分析完成
    requirementsAnalyzed: (feature) => {
      this.notify(`需求分析完成: ${feature}`)
    },

    // 需要用户确认
    needsConfirmation: (action, details) => {
      this.confirm(`需要确认: ${action} - ${details}`)
    },

    // 需要用户授权
    needsAuthorization: (action, reason) => {
      this.alert(`需要授权: ${action} - ${reason}`)
    },

    // 重大变更
    majorChange: (change, impact) => {
      this.urgent(`重大变更: ${change} - 影响: ${impact}`)
    },

    // 测试完成
    testsCompleted: (result, count) => {
      if (result === 'success') {
        this.confirm(`测试完成: ${count}个测试全部通过`)
      } else {
        this.alert(`测试失败: ${count}个测试未通过`)
      }
    },

    // 部署准备
    deploymentReady: (environment) => {
      this.urgent(`部署准备就绪: ${environment}环境`, 2)
    },

    // 错误发生
    errorOccurred: (error, context) => {
      this.urgent(`错误发生: ${error} - 上下文: ${context}`, 4)
    },
  }

  /**
   * 获取通知历史
   */
  getHistory (limit = 10) {
    return this.notificationHistory.slice(-limit)
  }

  /**
   * 清除通知历史
   */
  clearHistory () {
    this.notificationHistory = []
  }

  /**
   * 停止所有声音
   */
  stopAll () {
    this.sound.stopAll()
  }
}

// 创建全局实例
const notificationManager = new NotificationManager()

export default notificationManager 