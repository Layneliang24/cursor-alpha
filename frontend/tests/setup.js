import { vi } from 'vitest'
import { config } from '@vue/test-utils'

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: vi.fn(),
  ElMessageBox: {
    confirm: vi.fn(),
    alert: vi.fn(),
    prompt: vi.fn()
  },
  ElNotification: vi.fn(),
  ElLoading: {
    service: vi.fn()
  },
  ElInput: {
    name: 'ElInput',
    template: '<input />'
  },
  ElButton: {
    name: 'ElButton',
    template: '<button />'
  },
  ElTabs: {
    name: 'ElTabs',
    template: '<div class="el-tabs"><slot /></div>'
  },
  ElTabPane: {
    name: 'ElTabPane',
    template: '<div class="el-tab-pane"><slot /></div>'
  },
  ElTable: {
    name: 'ElTable',
    template: '<table class="el-table"><slot /></table>'
  },
  ElTableColumn: {
    name: 'ElTableColumn',
    template: '<td class="el-table-column"><slot /></td>'
  },
  ElDialog: {
    name: 'ElDialog',
    template: '<div class="el-dialog"><slot /></div>'
  },
  ElForm: {
    name: 'ElForm',
    template: '<form class="el-form"><slot /></form>'
  },
  ElFormItem: {
    name: 'ElFormItem',
    template: '<div class="el-form-item"><slot /></div>'
  },
  ElSelect: {
    name: 'ElSelect',
    template: '<select class="el-select"><slot /></select>'
  },
  ElOption: {
    name: 'ElOption',
    template: '<option class="el-option"><slot /></option>'
  },
  ElDatePicker: {
    name: 'ElDatePicker',
    template: '<input type="date" class="el-date-picker" />'
  },
  ElSwitch: {
    name: 'ElSwitch',
    template: '<input type="checkbox" class="el-switch" />'
  },
  ElCheckbox: {
    name: 'ElCheckbox',
    template: '<input type="checkbox" class="el-checkbox" />'
  },
  ElRadio: {
    name: 'ElRadio',
    template: '<input type="radio" class="el-radio" />'
  },
  ElRadioGroup: {
    name: 'ElRadioGroup',
    template: '<div class="el-radio-group"><slot /></div>'
  },
  ElCard: {
    name: 'ElCard',
    template: '<div class="el-card"><slot /></div>'
  },
  ElRow: {
    name: 'ElRow',
    template: '<div class="el-row"><slot /></div>'
  },
  ElCol: {
    name: 'ElCol',
    template: '<div class="el-col"><slot /></div>'
  },
  ElDivider: {
    name: 'ElDivider',
    template: '<hr class="el-divider" />'
  },
  ElProgress: {
    name: 'ElProgress',
    template: '<div class="el-progress"><slot /></div>'
  },
  ElTag: {
    name: 'ElTag',
    template: '<span class="el-tag"><slot /></span>'
  },
  ElBadge: {
    name: 'ElBadge',
    template: '<div class="el-badge"><slot /></div>'
  },
  ElAvatar: {
    name: 'ElAvatar',
    template: '<div class="el-avatar"><slot /></div>'
  },
  ElDropdown: {
    name: 'ElDropdown',
    template: '<div class="el-dropdown"><slot /></div>'
  },
  ElDropdownMenu: {
    name: 'ElDropdownMenu',
    template: '<ul class="el-dropdown-menu"><slot /></ul>'
  },
  ElDropdownItem: {
    name: 'ElDropdownItem',
    template: '<li class="el-dropdown-item"><slot /></li>'
  },
  ElMenu: {
    name: 'ElMenu',
    template: '<ul class="el-menu"><slot /></ul>'
  },
  ElMenuItem: {
    name: 'ElMenuItem',
    template: '<li class="el-menu-item"><slot /></li>'
  },
  ElSubmenu: {
    name: 'ElSubmenu',
    template: '<li class="el-submenu"><slot /></li>'
  },
  ElBreadcrumb: {
    name: 'ElBreadcrumb',
    template: '<nav class="el-breadcrumb"><slot /></nav>'
  },
  ElBreadcrumbItem: {
    name: 'ElBreadcrumbItem',
    template: '<span class="el-breadcrumb-item"><slot /></span>'
  },
  ElPagination: {
    name: 'ElPagination',
    template: '<div class="el-pagination"><slot /></div>'
  },
  ElTooltip: {
    name: 'ElTooltip',
    template: '<div class="el-tooltip"><slot /></div>'
  },
  ElPopover: {
    name: 'ElPopover',
    template: '<div class="el-popover"><slot /></div>'
  },
  ElDrawer: {
    name: 'ElDrawer',
    template: '<div class="el-drawer"><slot /></div>'
  },
  ElUpload: {
    name: 'ElUpload',
    template: '<div class="el-upload"><slot /></div>'
  },
  ElCascader: {
    name: 'ElCascader',
    template: '<div class="el-cascader"><slot /></div>'
  },
  ElTimePicker: {
    name: 'ElTimePicker',
    template: '<input type="time" class="el-time-picker" />'
  },
  ElRate: {
    name: 'ElRate',
    template: '<div class="el-rate"><slot /></div>'
  },
  ElSlider: {
    name: 'ElSlider',
    template: '<input type="range" class="el-slider" />'
  },
  ElTransfer: {
    name: 'ElTransfer',
    template: '<div class="el-transfer"><slot /></div>'
  },
  ElTree: {
    name: 'ElTree',
    template: '<div class="el-tree"><slot /></div>'
  },
  ElCalendar: {
    name: 'ElCalendar',
    template: '<div class="el-calendar"><slot /></div>'
  },
  ElImage: {
    name: 'ElImage',
    template: '<img class="el-image" />'
  },
  ElBacktop: {
    name: 'ElBacktop',
    template: '<div class="el-backtop"><slot /></div>'
  },
  ElPageHeader: {
    name: 'ElPageHeader',
    template: '<div class="el-page-header"><slot /></div>'
  },
  ElInfiniteScroll: {
    name: 'ElInfiniteScroll',
    template: '<div class="el-infinite-scroll"><slot /></div>'
  },
  ElColorPicker: {
    name: 'ElColorPicker',
    template: '<input type="color" class="el-color-picker" />'
  },
  ElLink: {
    name: 'ElLink',
    template: '<a class="el-link"><slot /></a>'
  },
  ElDivider: {
    name: 'ElDivider',
    template: '<hr class="el-divider" />'
  },
  ElSpace: {
    name: 'ElSpace',
    template: '<div class="el-space"><slot /></div>'
  },
  ElAffix: {
    name: 'ElAffix',
    template: '<div class="el-affix"><slot /></div>'
  },
  ElSkeleton: {
    name: 'ElSkeleton',
    template: '<div class="el-skeleton"><slot /></div>'
  },
  ElSkeletonItem: {
    name: 'ElSkeletonItem',
    template: '<div class="el-skeleton-item"><slot /></div>'
  },
  ElEmpty: {
    name: 'ElEmpty',
    template: '<div class="el-empty"><slot /></div>'
  },
  ElDescriptions: {
    name: 'ElDescriptions',
    template: '<div class="el-descriptions"><slot /></div>'
  },
  ElDescriptionsItem: {
    name: 'ElDescriptionsItem',
    template: '<div class="el-descriptions-item"><slot /></div>'
  },
  ElResult: {
    name: 'ElResult',
    template: '<div class="el-result"><slot /></div>'
  },
  ElTimeline: {
    name: 'ElTimeline',
    template: '<div class="el-timeline"><slot /></div>'
  },
  ElTimelineItem: {
    name: 'ElTimelineItem',
    template: '<div class="el-timeline-item"><slot /></div>'
  },
  ElSteps: {
    name: 'ElSteps',
    template: '<div class="el-steps"><slot /></div>'
  },
  ElStep: {
    name: 'ElStep',
    template: '<div class="el-step"><slot /></div>'
  },
  ElCarousel: {
    name: 'ElCarousel',
    template: '<div class="el-carousel"><slot /></div>'
  },
  ElCarouselItem: {
    name: 'ElCarouselItem',
    template: '<div class="el-carousel-item"><slot /></div>'
  },
  ElCollapse: {
    name: 'ElCollapse',
    template: '<div class="el-collapse"><slot /></div>'
  },
  ElCollapseItem: {
    name: 'ElCollapseItem',
    template: '<div class="el-collapse-item"><slot /></div>'
  },
  ElTabs: {
    name: 'ElTabs',
    template: '<div class="el-tabs"><slot /></div>'
  },
  ElTabPane: {
    name: 'ElTabPane',
    template: '<div class="el-tab-pane"><slot /></div>'
  }
}))

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key) => key,
    locale: { value: 'zh-CN' },
    locales: ['zh-CN', 'en-US']
  }),
  createI18n: vi.fn()
}))

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      patch: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    })),
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    patch: vi.fn()
  }
}))

// 设置全局测试环境
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

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

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.sessionStorage = sessionStorageMock

// Mock console methods
global.console = {
  ...console,
  warn: vi.fn(),
  error: vi.fn(),
}

// Mock timers
vi.useFakeTimers()

// 设置Vue Test Utils全局配置
config.global.stubs = {
  'router-link': true,
  'router-view': true,
}

// 导入MSW并启动Mock服务
import { startMockServer } from '../src/mocks/server'

// 在测试环境中启动Mock服务
beforeAll(() => {
  startMockServer()
})

// 清理测试环境
afterAll(() => {
  // 可以在这里添加清理逻辑
})

// 每个测试前重置mocks
beforeEach(() => {
  vi.clearAllMocks()
  vi.clearAllTimers()
})

// 测试工具函数
export const testUtils = {
  // 创建测试用的Pinia实例
  createTestPinia: (options = {}) => {
    return createTestingPinia({
      createSpy: vi.fn,
      stubActions: false,
      ...options,
    })
  },

  // 等待Vue的下一个tick
  nextTick: async () => {
    const { nextTick } = await import('vue')
    await nextTick()
  },

  // 等待指定时间
  sleep: (ms) => new Promise(resolve => setTimeout(resolve, ms)),

  // 触发DOM事件
  triggerEvent: (element, eventType, eventData = {}) => {
    const event = new Event(eventType, { bubbles: true, ...eventData })
    element.dispatchEvent(event)
  },

  // 模拟用户输入
  mockUserInput: async (input, value) => {
    input.value = value
    input.dispatchEvent(new Event('input', { bubbles: true }))
    await testUtils.nextTick()
  },

  // 模拟API响应
  mockApiResponse: (data, status = 200) => {
    global.fetch.mockResolvedValueOnce({
      ok: status >= 200 && status < 300,
      status,
      json: async () => data,
      text: async () => JSON.stringify(data),
    })
  },

  // 模拟API错误
  mockApiError: (error, status = 500) => {
    global.fetch.mockRejectedValueOnce({
      status,
      message: error,
      response: { status, statusText: error },
    })
  },

  // 获取组件的文本内容
  getTextContent: (wrapper) => {
    return wrapper.element.textContent.replace(/\s+/g, ' ').trim()
  },

  // 检查元素是否可见
  isVisible: (element) => {
    const style = window.getComputedStyle(element)
    return style.display !== 'none' && 
           style.visibility !== 'hidden' && 
           style.opacity !== '0'
  },
}

// 导出常用的测试配置
export const commonMountOptions = {
  global: {
    plugins: [ElementPlus, testUtils.createTestPinia()],
    components: config.global.components,
    stubs: {
      // 默认存根一些复杂的组件
      'router-link': true,
      'router-view': true,
      'el-icon': true,
    },
  },
}

// 导出Element Plus相关的测试工具
export const elementPlusUtils = {
  // 等待Element Plus组件渲染完成
  waitForElementPlus: async () => {
    await testUtils.nextTick()
    await testUtils.sleep(100) // Element Plus组件可能需要额外的渲染时间
  },

  // 触发Element Plus表单验证
  triggerFormValidation: async (wrapper) => {
    const form = wrapper.findComponent({ name: 'ElForm' })
    if (form.exists()) {
      await form.vm.validate()
    }
  },

  // 模拟Element Plus消息框
  mockElMessage: () => {
    const ElMessage = {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      info: vi.fn(),
    }
    vi.mock('element-plus', async () => {
      const actual = await vi.importActual('element-plus')
      return {
        ...actual,
        ElMessage,
      }
    })
    return ElMessage
  },
}
