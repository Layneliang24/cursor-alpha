import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import websocketService from '../websocket'

// Mock WebSocket
global.WebSocket = vi.fn()

// Mock auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    token: 'mock-jwt-token',
    isLoggedIn: true,
    user: { id: 1, username: 'testuser' }
  })
}))

describe('WebSocketService', () => {
  let mockSocket

  beforeEach(() => {
    setActivePinia(createPinia())
    
    // 创建模拟WebSocket
    mockSocket = {
      readyState: 1, // WebSocket.OPEN
      send: vi.fn(),
      close: vi.fn(),
      onopen: null,
      onmessage: null,
      onclose: null,
      onerror: null
    }
    
    global.WebSocket.mockImplementation(() => mockSocket)
  })

  afterEach(() => {
    vi.clearAllMocks()
    websocketService.disconnect()
  })

  it('应该能够连接到WebSocket服务器', async () => {
    const connectPromise = websocketService.connect()
    
    // 模拟连接成功
    mockSocket.onopen()
    
    await connectPromise
    
    expect(websocketService.isConnected).toBe(true)
    expect(global.WebSocket).toHaveBeenCalledWith(
      'ws://localhost:8000/ws/ai/status/mock-jwt-token/'
    )
  })

  it('应该能够发送消息', async () => {
    const connectPromise = websocketService.connect()
    mockSocket.onopen()
    await connectPromise
    
    const testMessage = { type: 'test', data: 'hello' }
    websocketService.send(testMessage)
    
    expect(mockSocket.send).toHaveBeenCalledWith(JSON.stringify(testMessage))
  })

  it('应该能够处理连接断开', async () => {
    const connectPromise = websocketService.connect()
    mockSocket.onopen()
    await connectPromise
    
    // 模拟连接断开
    mockSocket.onclose({ code: 1000, reason: 'Normal closure' })
    
    expect(websocketService.isConnected).toBe(false)
  })

  it('应该能够断开连接', async () => {
    const connectPromise = websocketService.connect()
    mockSocket.onopen()
    await connectPromise
    
    websocketService.disconnect()
    
    expect(mockSocket.close).toHaveBeenCalled()
    expect(websocketService.isConnected).toBe(false)
  })

  it('应该返回正确的连接状态', () => {
    const status = websocketService.getConnectionStatus()
    
    expect(status).toEqual({
      isConnected: false,
      reconnectAttempts: 0,
      maxReconnectAttempts: 10
    })
  })
})
