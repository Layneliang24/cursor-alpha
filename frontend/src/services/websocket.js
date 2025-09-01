import { io } from 'socket.io-client'
import { useAuthStore } from '@/stores/auth'

class WebSocketService {
  constructor() {
    this.socket = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 10
    this.reconnectInterval = 5000
    this.heartbeatInterval = null
    this.isConnected = false
    this.listeners = new Map()
  }

  /**
   * 连接到WebSocket服务器
   */
  connect() {
    if (this.socket && this.isConnected) {
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      try {
        const authStore = useAuthStore()
        const token = authStore.token

        if (!token) {
          reject(new Error('No authentication token available'))
          return
        }

        // 创建WebSocket连接
        this.socket = new WebSocket(`ws://localhost:8000/ws/ai/status/${token}/`)

        this.socket.onopen = () => {
          console.log('WebSocket connected')
          this.isConnected = true
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolve()
        }

        this.socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            this.handleMessage(data)
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }

        this.socket.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          this.isConnected = false
          this.stopHeartbeat()
          this.handleReconnect()
        }

        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error)
          reject(error)
        }

      } catch (error) {
        console.error('Error creating WebSocket connection:', error)
        reject(error)
      }
    })
  }

  /**
   * 断开WebSocket连接
   */
  disconnect() {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
    this.isConnected = false
    this.stopHeartbeat()
  }

  /**
   * 处理重连
   */
  handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    setTimeout(() => {
      this.connect().catch(error => {
        console.error('Reconnection failed:', error)
      })
    }, this.reconnectInterval)
  }

  /**
   * 启动心跳机制
   */
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected) {
        this.send({
          type: 'ping',
          timestamp: Date.now()
        })
      }
    }, 30000) // 30秒心跳
  }

  /**
   * 停止心跳机制
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * 发送消息
   */
  send(data) {
    if (this.socket && this.isConnected) {
      this.socket.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket not connected, attempting to reconnect...')
      this.connect()
    }
  }

  /**
   * 处理接收到的消息
   */
  handleMessage(data) {
    const { type, ...payload } = data

    // 触发对应类型的事件监听器
    if (this.listeners.has(type)) {
      this.listeners.get(type).forEach(callback => {
        try {
          callback(payload)
        } catch (error) {
          console.error(`Error in ${type} listener:`, error)
        }
      })
    }

    // 特殊处理心跳响应
    if (type === 'pong') {
      // 心跳响应，可以用于计算延迟
      const latency = Date.now() - payload.timestamp
      console.log(`WebSocket heartbeat latency: ${latency}ms`)
    }
  }

  /**
   * 订阅消息类型
   */
  subscribe(type, callback) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, [])
    }
    this.listeners.get(type).push(callback)

    // 如果是首次订阅，发送订阅请求
    if (this.isConnected) {
      this.send({
        type: 'subscribe',
        subscription_type: type
      })
    }

    // 返回取消订阅的函数
    return () => {
      const callbacks = this.listeners.get(type)
      if (callbacks) {
        const index = callbacks.indexOf(callback)
        if (index > -1) {
          callbacks.splice(index, 1)
        }
        if (callbacks.length === 0) {
          this.listeners.delete(type)
        }
      }
    }
  }

  /**
   * 请求当前状态
   */
  requestStatus() {
    this.send({
      type: 'request_status'
    })
  }

  /**
   * 获取连接状态
   */
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      maxReconnectAttempts: this.maxReconnectAttempts
    }
  }
}

// 创建全局WebSocket服务实例
const websocketService = new WebSocketService()

export default websocketService
