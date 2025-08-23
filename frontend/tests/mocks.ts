import { vi } from 'vitest'

// 全局mock配置
export function setupGlobalMocks() {
  // Mock marked库
  vi.mock('marked', () => ({
    default: vi.fn((text: string) => `<div>${text}</div>`),
    __esModule: true
  }))

  // Mock highlight.js
  vi.mock('highlight.js', () => ({
    default: {
      getLanguage: vi.fn(() => true),
      highlight: vi.fn(() => ({ value: 'highlighted code' })),
      highlightAuto: vi.fn(() => ({ value: 'auto highlighted code' }))
    },
    __esModule: true
  }))

  // Mock CSS导入
  vi.mock('highlight.js/styles/github.css', () => ({}), { virtual: true })

  // Mock Element Plus 图标
  vi.mock('@element-plus/icons-vue', () => ({
    Rank: { template: '<div class="el-icon-rank">📊</div>' },
    Document: { template: '<div class="el-icon-document">📄</div>' },
    ChatLineRound: { template: '<div class="el-icon-chat">💬</div>' },
    List: { template: '<div class="el-icon-list">📋</div>' },
    Menu: { template: '<div class="el-icon-menu">☰</div>' },
    Link: { template: '<div class="el-icon-link">🔗</div>' },
    Picture: { template: '<div class="el-icon-picture">🖼️</div>' },
    Grid: { template: '<div class="el-icon-grid">⊞</div>' }
  }))

  // Mock Audio API
  global.Audio = vi.fn(() => ({
    play: vi.fn().mockResolvedValue(undefined),
    pause: vi.fn(),
    currentTime: 0,
    duration: 0,
    volume: 1,
    playbackRate: 1,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn()
  }))

  // Mock window对象
  Object.defineProperty(window, 'stopAllPronunciations', {
    value: vi.fn(),
    writable: true
  })

  // Mock console方法
  const consoleSpy = {
    log: vi.spyOn(console, 'log').mockImplementation(() => {}),
    warn: vi.spyOn(console, 'warn').mockImplementation(() => {}),
    error: vi.spyOn(console, 'error').mockImplementation(() => {})
  }

  return { consoleSpy }
}

// 清理mock
export function cleanupMocks() {
  vi.clearAllMocks()
  vi.resetAllMocks()
} 