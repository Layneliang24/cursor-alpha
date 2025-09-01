import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import websocketService from '@/services/websocket'

export function useWebSocket() {
  const isConnected = ref(false)
  const connectionStatus = ref('disconnected')
  const reconnectAttempts = ref(0)
  const lastMessage = ref(null)
  const messageHistory = ref([])

  // 连接状态监听器
  const updateConnectionStatus = () => {
    const status = websocketService.getConnectionStatus()
    isConnected.value = status.isConnected
    reconnectAttempts.value = status.reconnectAttempts
    connectionStatus.value = status.isConnected ? 'connected' : 'disconnected'
  }

  // 消息处理器
  const handleMessage = (data) => {
    lastMessage.value = {
      ...data,
      timestamp: new Date().toISOString()
    }
    messageHistory.value.push(lastMessage.value)
    
    // 限制消息历史记录数量
    if (messageHistory.value.length > 100) {
      messageHistory.value = messageHistory.value.slice(-100)
    }
  }

  // 连接WebSocket
  const connect = async () => {
    try {
      connectionStatus.value = 'connecting'
      await websocketService.connect()
      updateConnectionStatus()
      ElMessage.success('WebSocket连接成功')
    } catch (error) {
      console.error('WebSocket连接失败:', error)
      connectionStatus.value = 'error'
      ElMessage.error('WebSocket连接失败')
    }
  }

  // 断开WebSocket
  const disconnect = () => {
    websocketService.disconnect()
    updateConnectionStatus()
    ElMessage.info('WebSocket已断开')
  }

  // 订阅消息类型
  const subscribe = (type, callback) => {
    return websocketService.subscribe(type, callback)
  }

  // 请求状态更新
  const requestStatus = () => {
    websocketService.requestStatus()
  }

  // 发送消息
  const sendMessage = (data) => {
    websocketService.send(data)
  }

  // 清理函数
  const cleanup = () => {
    websocketService.disconnect()
  }

  // 组件挂载时连接
  onMounted(() => {
    connect()
    
    // 定期更新连接状态
    const statusInterval = setInterval(updateConnectionStatus, 1000)
    
    // 组件卸载时清理
    onUnmounted(() => {
      clearInterval(statusInterval)
      cleanup()
    })
  })

  return {
    // 状态
    isConnected,
    connectionStatus,
    reconnectAttempts,
    lastMessage,
    messageHistory,
    
    // 方法
    connect,
    disconnect,
    subscribe,
    requestStatus,
    sendMessage,
    cleanup
  }
}

// 专门用于AI监控的WebSocket组合函数
export function useAIWebSocket() {
  const { isConnected, connectionStatus, subscribe, requestStatus } = useWebSocket()
  
  const providerStatus = ref([])
  const usageStats = ref({})
  const strategyStatus = ref([])
  const alerts = ref([])

  // 订阅AI相关消息
  const subscribeToAIUpdates = () => {
    // 订阅提供商状态更新
    subscribe('provider_status_update', (data) => {
      const index = providerStatus.value.findIndex(p => p.id === data.id)
      if (index > -1) {
        providerStatus.value[index] = data
      } else {
        providerStatus.value.push(data)
      }
    })

    // 订阅Token使用统计更新
    subscribe('token_usage_update', (data) => {
      usageStats.value = data
    })

    // 订阅故障转移告警
    subscribe('fallback_alert', (data) => {
      alerts.value.unshift(data)
      // 限制告警数量
      if (alerts.value.length > 50) {
        alerts.value = alerts.value.slice(0, 50)
      }
      
      // 显示告警消息
      ElMessage.warning(`故障转移告警: ${data.message}`)
    })

    // 订阅状态更新
    subscribe('status_update', (data) => {
      if (data.providers) {
        providerStatus.value = data.providers
      }
      if (data.usage_stats) {
        usageStats.value = data.usage_stats
      }
      if (data.strategies) {
        strategyStatus.value = data.strategies
      }
    })

    // 订阅初始状态
    subscribe('initial_status', (data) => {
      if (data.providers) {
        providerStatus.value = data.providers
      }
      if (data.usage_stats) {
        usageStats.value = data.usage_stats
      }
      if (data.strategies) {
        strategyStatus.value = data.strategies
      }
    })
  }

  // 组件挂载时订阅
  onMounted(() => {
    subscribeToAIUpdates()
  })

  return {
    // 连接状态
    isConnected,
    connectionStatus,
    
    // AI数据
    providerStatus,
    usageStats,
    strategyStatus,
    alerts,
    
    // 方法
    requestStatus
  }
}

/**
 * WebSocket消息类型常量
 */
export const WS_MESSAGE_TYPES = {
  // 心跳
  PING: 'ping',
  PONG: 'pong',
  
  // 监控数据
  METRICS_UPDATE: 'metrics_update',
  STATUS_UPDATE: 'status_update',
  ALARM_NEW: 'alarm_new',
  
  // 系统事件
  SYSTEM_NOTIFICATION: 'system_notification',
  CONNECTION_ACK: 'connection_ack'
}

/**
 * 创建标准化的WebSocket消息
 * @param {string} type 消息类型
 * @param {*} data 消息数据
 * @param {Object} meta 元数据
 */
export function createWSMessage(type, data = null, meta = {}) {
  return {
    type,
    data,
    timestamp: Date.now(),
    ...meta
  }
}
