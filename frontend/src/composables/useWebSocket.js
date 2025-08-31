import { ref, onUnmounted } from 'vue'

/**
 * WebSocket连接管理组合式函数
 */
export function useWebSocketConnection() {
  const connected = ref(false)
  const connecting = ref(false)
  const error = ref(null)
  
  let ws = null
  let reconnectTimer = null
  let heartbeatTimer = null
  let reconnectAttempts = 0
  const maxReconnectAttempts = 5
  const reconnectInterval = 3000 // 3秒
  const heartbeatInterval = 30000 // 30秒
  
  let options = {
    onOpen: null,
    onMessage: null,
    onClose: null,
    onError: null,
    onReconnect: null,
    autoReconnect: true,
    heartbeat: true
  }
  
  /**
   * 连接WebSocket
   * @param {string} url WebSocket URL
   * @param {Object} connectionOptions 连接选项
   */
  const connect = (url, connectionOptions = {}) => {
    if (ws && (ws.readyState === WebSocket.CONNECTING || ws.readyState === WebSocket.OPEN)) {
      console.warn('WebSocket已连接或正在连接中')
      return
    }
    
    options = { ...options, ...connectionOptions }
    connecting.value = true
    error.value = null
    
    try {
      ws = new WebSocket(url)
      
      ws.onopen = (event) => {
        console.log('WebSocket连接已建立')
        connected.value = true
        connecting.value = false
        reconnectAttempts = 0
        
        // 启动心跳
        if (options.heartbeat) {
          startHeartbeat()
        }
        
        // 触发回调
        if (options.onOpen) {
          options.onOpen(event)
        }
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // 处理心跳响应
          if (data.type === 'pong') {
            console.log('收到心跳响应')
            return
          }
          
          // 触发消息回调
          if (options.onMessage) {
            options.onMessage(data, event)
          }
        } catch (err) {
          console.error('解析WebSocket消息失败:', err)
          // 原始消息回调
          if (options.onMessage) {
            options.onMessage(event.data, event)
          }
        }
      }
      
      ws.onclose = (event) => {
        console.log('WebSocket连接已关闭', event.code, event.reason)
        connected.value = false
        connecting.value = false
        
        // 停止心跳
        stopHeartbeat()
        
        // 触发回调
        if (options.onClose) {
          options.onClose(event)
        }
        
        // 自动重连
        if (options.autoReconnect && reconnectAttempts < maxReconnectAttempts) {
          scheduleReconnect(url)
        }
      }
      
      ws.onerror = (event) => {
        console.error('WebSocket错误:', event)
        error.value = event
        connecting.value = false
        
        // 触发回调
        if (options.onError) {
          options.onError(event)
        }
      }
      
    } catch (err) {
      console.error('创建WebSocket连接失败:', err)
      error.value = err
      connecting.value = false
    }
  }
  
  /**
   * 断开连接
   */
  const disconnect = () => {
    if (ws) {
      // 停止自动重连
      options.autoReconnect = false
      clearTimeout(reconnectTimer)
      
      // 停止心跳
      stopHeartbeat()
      
      // 关闭连接
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close(1000, '手动断开连接')
      }
      
      ws = null
    }
    
    connected.value = false
    connecting.value = false
    error.value = null
    reconnectAttempts = 0
  }
  
  /**
   * 发送消息
   * @param {*} message 要发送的消息
   */
  const send = (message) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket未连接，无法发送消息')
      return false
    }
    
    try {
      const data = typeof message === 'string' ? message : JSON.stringify(message)
      ws.send(data)
      return true
    } catch (err) {
      console.error('发送WebSocket消息失败:', err)
      return false
    }
  }
  
  /**
   * 安排重连
   * @param {string} url WebSocket URL
   */
  const scheduleReconnect = (url) => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
    }
    
    reconnectAttempts++
    const delay = Math.min(reconnectInterval * Math.pow(1.5, reconnectAttempts - 1), 30000)
    
    console.log(`${delay / 1000}秒后尝试第${reconnectAttempts}次重连...`)
    
    // 触发重连回调
    if (options.onReconnect) {
      options.onReconnect(reconnectAttempts, delay)
    }
    
    reconnectTimer = setTimeout(() => {
      if (reconnectAttempts <= maxReconnectAttempts) {
        console.log(`开始第${reconnectAttempts}次重连...`)
        connect(url, options)
      } else {
        console.error('达到最大重连次数，停止重连')
        error.value = new Error('连接失败，已达到最大重连次数')
      }
    }, delay)
  }
  
  /**
   * 启动心跳
   */
  const startHeartbeat = () => {
    if (!options.heartbeat) return
    
    stopHeartbeat() // 确保没有重复的定时器
    
    heartbeatTimer = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        send({ type: 'ping', timestamp: Date.now() })
      }
    }, heartbeatInterval)
  }
  
  /**
   * 停止心跳
   */
  const stopHeartbeat = () => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }
  
  /**
   * 手动重连
   * @param {string} url WebSocket URL
   */
  const reconnect = (url) => {
    disconnect()
    reconnectAttempts = 0
    setTimeout(() => {
      connect(url, options)
    }, 1000)
  }
  
  /**
   * 获取连接状态
   */
  const getReadyState = () => {
    if (!ws) return WebSocket.CLOSED
    return ws.readyState
  }
  
  /**
   * 获取连接状态文本
   */
  const getReadyStateText = () => {
    const state = getReadyState()
    const stateMap = {
      [WebSocket.CONNECTING]: '连接中',
      [WebSocket.OPEN]: '已连接',
      [WebSocket.CLOSING]: '关闭中',
      [WebSocket.CLOSED]: '已关闭'
    }
    return stateMap[state] || '未知'
  }
  
  // 组件卸载时自动清理
  onUnmounted(() => {
    disconnect()
  })
  
  return {
    // 状态
    connected,
    connecting,
    error,
    
    // 方法
    connect,
    disconnect,
    send,
    reconnect,
    getReadyState,
    getReadyStateText,
    
    // 只读状态
    reconnectAttempts: () => reconnectAttempts,
    maxReconnectAttempts: () => maxReconnectAttempts
  }
}

/**
 * 简化的WebSocket Hook，用于单一连接
 * @param {string} url WebSocket URL
 * @param {Object} options 连接选项
 */
export function useWebSocket(url, options = {}) {
  const connection = useWebSocketConnection()
  
  // 自动连接
  if (url) {
    connection.connect(url, options)
  }
  
  return connection
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
