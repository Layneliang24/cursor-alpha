import { config } from '@vue/test-utils'
import { vi } from 'vitest'

// 全局配置Vue Test Utils
config.global.stubs = {
  'router-link': true,
  'router-view': true,
  'el-icon': true,
  'el-button': true,
  'el-input': true,
  'el-select': true,
  'el-option': true,
  'el-menu': true,
  'el-menu-item': true,
  'el-sub-menu': true,
  'el-dropdown': true,
  'el-dropdown-menu': true,
  'el-dropdown-item': true,
  'el-avatar': true,
  'el-badge': true,
  'el-tooltip': true,
  'el-popover': true,
  'el-dialog': true,
  'el-drawer': true,
  'el-tabs': true,
  'el-tab-pane': true,
  'el-form': true,
  'el-form-item': true,
  'el-checkbox': true,
  'el-radio': true,
  'el-switch': true,
  'el-slider': true,
  'el-rate': true,
  'el-upload': true,
  'el-progress': true,
  'el-alert': true,
  'el-message': true,
  'el-notification': true,
  'el-loading': true,
  'el-infinite-scroll': true,
  'el-backtop': true,
  'el-page-header': true,
  'el-breadcrumb': true,
  'el-breadcrumb-item': true,
  'el-steps': true,
  'el-step': true,
  'el-timeline': true,
  'el-timeline-item': true,
  'el-card': true,
  'el-divider': true,
  'el-space': true,
  'el-affix': true,
  'el-anchor': true,
  'el-anchor-link': true,
  'el-backdrop': true,
  'el-collapse': true,
  'el-collapse-item': true,
  'el-descriptions': true,
  'el-descriptions-item': true,
  'el-empty': true,
  'el-result': true,
  'el-skeleton': true,
  'el-skeleton-item': true,
  'el-statistic': true,
  'el-tag': true,
  'el-tree': true,
  'el-tree-node': true,
  'el-pagination': true,
  'el-calendar': true,
  'el-date-picker': true,
  'el-time-picker': true,
  'el-cascader': true,
  'el-transfer': true,
  'el-color-picker': true,
  'el-autocomplete': true,
  'el-input-number': true,
  'el-radio-group': true,
  'el-radio-button': true,
  'el-checkbox-group': true,
  'el-checkbox-button': true,
  'el-button-group': true,
  'el-table': true,
  'el-table-column': true,
  'el-table-header': true,
  'el-table-footer': true,
  'el-table-body': true,
  'el-table-column-group': true,
  'el-table-column-header': true,
  'el-table-column-footer': true,
  'el-table-column-body': true,
  'el-table-column-header-cell': true,
  'el-table-column-footer-cell': true,
  'el-table-column-body-cell': true,
  'el-table-column-header-row': true,
  'el-table-column-footer-row': true,
  'el-table-column-body-row': true,
  'el-table-column-header-cell-content': true,
  'el-table-column-footer-cell-content': true,
  'el-table-column-body-cell-content': true,
  'el-table-column-header-cell-text': true,
  'el-table-column-footer-cell-text': true,
  'el-table-column-body-cell-text': true,
  'el-table-column-header-cell-icon': true,
  'el-table-column-footer-cell-icon': true,
  'el-table-column-body-cell-icon': true,
  'el-table-column-header-cell-button': true,
  'el-table-column-footer-cell-button': true,
  'el-table-column-body-cell-button': true,
  'el-table-column-header-cell-input': true,
  'el-table-column-footer-cell-input': true,
  'el-table-column-body-cell-input': true,
  'el-table-column-header-cell-select': true,
  'el-table-column-footer-cell-select': true,
  'el-table-column-body-cell-select': true,
  'el-table-column-header-cell-checkbox': true,
  'el-table-column-footer-cell-checkbox': true,
  'el-table-column-body-cell-checkbox': true,
  'el-table-column-header-cell-radio': true,
  'el-table-column-footer-cell-radio': true,
  'el-table-column-body-cell-radio': true,
  'el-table-column-header-cell-switch': true,
  'el-table-column-footer-cell-switch': true,
  'el-table-column-body-cell-switch': true,
  'el-table-column-header-cell-slider': true,
  'el-table-column-footer-cell-slider': true,
  'el-table-column-body-cell-slider': true,
  'el-table-column-header-cell-rate': true,
  'el-table-column-footer-cell-rate': true,
  'el-table-column-body-cell-rate': true,
  'el-table-column-header-cell-upload': true,
  'el-table-column-footer-cell-upload': true,
  'el-table-column-body-cell-upload': true,
  'el-table-column-header-cell-progress': true,
  'el-table-column-footer-cell-progress': true,
  'el-table-column-body-cell-progress': true,
  'el-table-column-header-cell-alert': true,
  'el-table-column-footer-cell-alert': true,
  'el-table-column-body-cell-alert': true,
  'el-table-column-header-cell-message': true,
  'el-table-column-footer-cell-message': true,
  'el-table-column-body-cell-message': true,
  'el-table-column-header-cell-notification': true,
  'el-table-column-footer-cell-notification': true,
  'el-table-column-body-cell-notification': true,
  'el-table-column-header-cell-loading': true,
  'el-table-column-footer-cell-loading': true,
  'el-table-column-body-cell-loading': true,
  'el-table-column-header-cell-infinite-scroll': true,
  'el-table-column-footer-cell-infinite-scroll': true,
  'el-table-column-body-cell-infinite-scroll': true,
  'el-table-column-header-cell-backtop': true,
  'el-table-column-footer-cell-backtop': true,
  'el-table-column-body-cell-backtop': true,
  'el-table-column-header-cell-page-header': true,
  'el-table-column-footer-cell-page-header': true,
  'el-table-column-body-cell-page-header': true,
  'el-table-column-header-cell-breadcrumb': true,
  'el-table-column-footer-cell-breadcrumb': true,
  'el-table-column-body-cell-breadcrumb': true,
  'el-table-column-header-cell-breadcrumb-item': true,
  'el-table-column-footer-cell-breadcrumb-item': true,
  'el-table-column-body-cell-breadcrumb-item': true,
  'el-table-column-header-cell-steps': true,
  'el-table-column-footer-cell-steps': true,
  'el-table-column-body-cell-steps': true,
  'el-table-column-header-cell-step': true,
  'el-table-column-footer-cell-step': true,
  'el-table-column-body-cell-step': true,
  'el-table-column-header-cell-timeline': true,
  'el-table-column-footer-cell-timeline': true,
  'el-table-column-body-cell-timeline': true,
  'el-table-column-header-cell-timeline-item': true,
  'el-table-column-footer-cell-timeline-item': true,
  'el-table-column-body-cell-timeline-item': true,
  'el-table-column-header-cell-card': true,
  'el-table-column-footer-cell-card': true,
  'el-table-column-body-cell-card': true,
  'el-table-column-header-cell-divider': true,
  'el-table-column-footer-cell-divider': true,
  'el-table-column-body-cell-divider': true,
  'el-table-column-header-cell-space': true,
  'el-table-column-footer-cell-space': true,
  'el-table-column-body-cell-space': true,
  'el-table-column-header-cell-affix': true,
  'el-table-column-footer-cell-affix': true,
  'el-table-column-body-cell-affix': true,
  'el-table-column-header-cell-anchor': true,
  'el-table-column-footer-cell-anchor': true,
  'el-table-column-body-cell-anchor': true,
  'el-table-column-header-cell-anchor-link': true,
  'el-table-column-footer-cell-anchor-link': true,
  'el-table-column-body-cell-anchor-link': true,
  'el-table-column-header-cell-backdrop': true,
  'el-table-column-footer-cell-backdrop': true,
  'el-table-column-body-cell-backdrop': true,
  'el-table-column-header-cell-collapse': true,
  'el-table-column-footer-cell-collapse': true,
  'el-table-column-body-cell-collapse': true,
  'el-table-column-header-cell-collapse-item': true,
  'el-table-column-footer-cell-collapse-item': true,
  'el-table-column-body-cell-collapse-item': true,
  'el-table-column-header-cell-descriptions': true,
  'el-table-column-footer-cell-descriptions': true,
  'el-table-column-body-cell-descriptions': true,
  'el-table-column-header-cell-descriptions-item': true,
  'el-table-column-footer-cell-descriptions-item': true,
  'el-table-column-body-cell-descriptions-item': true,
  'el-table-column-header-cell-empty': true,
  'el-table-column-footer-cell-empty': true,
  'el-table-column-body-cell-empty': true,
  'el-table-column-header-cell-result': true,
  'el-table-column-footer-cell-result': true,
  'el-table-column-body-cell-result': true,
  'el-table-column-header-cell-skeleton': true,
  'el-table-column-footer-cell-skeleton': true,
  'el-table-column-body-cell-skeleton': true,
  'el-table-column-header-cell-skeleton-item': true,
  'el-table-column-footer-cell-skeleton-item': true,
  'el-table-column-body-cell-skeleton-item': true,
  'el-table-column-header-cell-statistic': true,
  'el-table-column-footer-cell-statistic': true,
  'el-table-column-body-cell-statistic': true,
  'el-table-column-header-cell-tag': true,
  'el-table-column-footer-cell-tag': true,
  'el-table-column-body-cell-tag': true,
  'el-table-column-header-cell-tree': true,
  'el-table-column-footer-cell-tree': true,
  'el-table-column-body-cell-tree': true,
  'el-table-column-header-cell-tree-node': true,
  'el-table-column-footer-cell-tree-node': true,
  'el-table-column-body-cell-tree-node': true,
  'el-table-column-header-cell-pagination': true,
  'el-table-column-footer-cell-pagination': true,
  'el-table-column-body-cell-pagination': true,
  'el-table-column-header-cell-calendar': true,
  'el-table-column-footer-cell-calendar': true,
  'el-table-column-body-cell-calendar': true,
  'el-table-column-header-cell-date-picker': true,
  'el-table-column-footer-cell-date-picker': true,
  'el-table-column-body-cell-date-picker': true,
  'el-table-column-header-cell-time-picker': true,
  'el-table-column-footer-cell-time-picker': true,
  'el-table-column-body-cell-time-picker': true,
  'el-table-column-header-cell-cascader': true,
  'el-table-column-footer-cell-cascader': true,
  'el-table-column-body-cell-cascader': true,
  'el-table-column-header-cell-transfer': true,
  'el-table-column-footer-cell-transfer': true,
  'el-table-column-body-cell-transfer': true,
  'el-table-column-header-cell-color-picker': true,
  'el-table-column-footer-cell-color-picker': true,
  'el-table-column-body-cell-color-picker': true,
  'el-table-column-header-cell-autocomplete': true,
  'el-table-column-footer-cell-autocomplete': true,
  'el-table-column-body-cell-autocomplete': true,
  'el-table-column-header-cell-input-number': true,
  'el-table-column-footer-cell-input-number': true,
  'el-table-column-body-cell-input-number': true,
  'el-table-column-header-cell-radio-group': true,
  'el-table-column-footer-cell-radio-group': true,
  'el-table-column-body-cell-radio-group': true,
  'el-table-column-header-cell-radio-button': true,
  'el-table-column-footer-cell-radio-button': true,
  'el-table-column-body-cell-radio-button': true,
  'el-table-column-header-cell-checkbox-group': true,
  'el-table-column-footer-cell-checkbox-group': true,
  'el-table-column-body-cell-checkbox-group': true,
  'el-table-column-header-cell-checkbox-button': true,
  'el-table-column-footer-cell-checkbox-button': true,
  'el-table-column-body-cell-checkbox-button': true,
  'el-table-column-header-cell-button-group': true,
  'el-table-column-footer-cell-button-group': true,
  'el-table-column-body-cell-button-group': true
}

// Mock全局对象
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock getComputedStyle
Object.defineProperty(window, 'getComputedStyle', {
  value: () => ({
    getPropertyValue: () => '',
  }),
})

// Mock Element.prototype methods
Element.prototype.scrollIntoView = vi.fn()
Element.prototype.scrollTo = vi.fn()

// Mock HTMLElement.prototype methods
HTMLElement.prototype.focus = vi.fn()
HTMLElement.prototype.blur = vi.fn()
HTMLElement.prototype.click = vi.fn()

// Mock CSS
const mockCSS = {
  supports: vi.fn(() => true),
  escape: vi.fn((str) => str),
}

Object.defineProperty(window, 'CSS', {
  value: mockCSS,
  writable: true,
})

// Mock fetch
global.fetch = vi.fn()

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
})

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
  writable: true,
})

// Mock URL
global.URL.createObjectURL = vi.fn(() => 'mock-url')
global.URL.revokeObjectURL = vi.fn()

// Mock FileReader
global.FileReader = vi.fn().mockImplementation(() => ({
  readAsText: vi.fn(),
  readAsDataURL: vi.fn(),
  readAsArrayBuffer: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  result: null,
  error: null,
  readyState: 0,
}))

// Mock Blob
global.Blob = vi.fn().mockImplementation((content, options) => ({
  size: 0,
  type: options?.type || '',
  arrayBuffer: vi.fn(),
  stream: vi.fn(),
  text: vi.fn(),
  slice: vi.fn(),
}))

// Mock FormData
global.FormData = vi.fn().mockImplementation(() => ({
  append: vi.fn(),
  delete: vi.fn(),
  get: vi.fn(),
  getAll: vi.fn(),
  has: vi.fn(),
  set: vi.fn(),
  forEach: vi.fn(),
  entries: vi.fn(),
  keys: vi.fn(),
  values: vi.fn(),
}))

// Mock console methods in test environment
if (process.env.NODE_ENV === 'test') {
  console.warn = vi.fn()
  console.error = vi.fn()
}

// 设置测试环境变量
process.env.NODE_ENV = 'test'

// Mock Element Plus 组件
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  },
  ElMessageBox: {
    confirm: vi.fn(),
    alert: vi.fn(),
    prompt: vi.fn()
  },
  ElNotification: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  }
}))

// Mock @popperjs/core
vi.mock('@popperjs/core', () => ({
  placements: ['top', 'bottom', 'left', 'right'],
  createPopper: vi.fn(() => ({
    destroy: vi.fn(),
    update: vi.fn()
  }))
}))

// 导出配置
export default config
