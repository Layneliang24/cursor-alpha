import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import ConfigImportExport from '@/components/config/ConfigImportExport.vue'
import { configImportExportAPI } from '@/api/configImportExport'

// Mock API
vi.mock('@/api/configImportExport', () => ({
  configImportExportAPI: {
    exportConfig: vi.fn(),
    importConfig: vi.fn(),
    validateConfig: vi.fn()
  }
}))

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn()
  },
  ElMessageBox: {
    confirm: vi.fn()
  }
}))

// Mock FileReader
global.FileReader = vi.fn(() => ({
  readAsText: vi.fn(),
  onload: null,
  onerror: null,
  result: null
}))

// Mock URL.createObjectURL and URL.revokeObjectURL
global.URL.createObjectURL = vi.fn(() => 'mock-url')
global.URL.revokeObjectURL = vi.fn()

// Mock document.createElement
const mockLink = {
  href: '',
  download: '',
  click: vi.fn()
}
document.createElement = vi.fn(() => mockLink)
document.body.appendChild = vi.fn()
document.body.removeChild = vi.fn()

describe('ConfigImportExport', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(ConfigImportExport, {
      global: {
        plugins: []
      }
    })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  describe('导出配置', () => {
    it('应该能够导出JSON格式的配置', async () => {
      const mockResponse = { data: '{"test": "data"}' }
      configImportExportAPI.exportConfig.mockResolvedValue(mockResponse)

      await wrapper.vm.exportConfig()

      expect(configImportExportAPI.exportConfig).toHaveBeenCalledWith('json')
      expect(ElMessage.success).toHaveBeenCalledWith('配置导出成功')
    })

    it('应该能够导出YAML格式的配置', async () => {
      wrapper.vm.exportForm.format = 'yaml'
      const mockResponse = { data: 'test: data' }
      configImportExportAPI.exportConfig.mockResolvedValue(mockResponse)

      await wrapper.vm.exportConfig()

      expect(configImportExportAPI.exportConfig).toHaveBeenCalledWith('yaml')
    })

    it('应该在导出失败时显示错误信息', async () => {
      const error = new Error('导出失败')
      configImportExportAPI.exportConfig.mockRejectedValue(error)

      await wrapper.vm.exportConfig()

      expect(ElMessage.error).toHaveBeenCalledWith('导出配置失败: 导出失败')
    })
  })

  describe('文件验证', () => {
    it('应该验证文件格式', () => {
      const validFile = { name: 'test.json', size: 1024 }
      const invalidFile = { name: 'test.txt', size: 1024 }

      expect(wrapper.vm.beforeFileUpload(validFile)).toBe(false)
      expect(wrapper.vm.beforeFileUpload(invalidFile)).toBe(false)
      expect(ElMessage.error).toHaveBeenCalledWith('只能上传JSON/YAML格式的文件!')
    })

    it('应该验证文件大小', () => {
      const largeFile = { name: 'test.json', size: 11 * 1024 * 1024 }

      wrapper.vm.beforeFileUpload(largeFile)

      expect(ElMessage.error).toHaveBeenCalledWith('文件大小不能超过10MB!')
    })
  })

  describe('配置验证', () => {
    it('应该能够验证配置文件', async () => {
      const mockFile = { raw: new Blob(['{"test": "data"}']) }
      wrapper.vm.selectedFile = mockFile

      const mockResponse = { data: { message: '验证通过' } }
      configImportExportAPI.validateConfig.mockResolvedValue(mockResponse)

      // Mock FileReader
      const mockFileReader = {
        readAsText: vi.fn(),
        onload: null,
        result: '{"test": "data"}'
      }
      global.FileReader.mockImplementation(() => mockFileReader)

      await wrapper.vm.validateConfig()

      expect(configImportExportAPI.validateConfig).toHaveBeenCalled()
      expect(ElMessage.success).toHaveBeenCalledWith('配置验证通过')
    })

    it('应该在验证失败时显示错误信息', async () => {
      const mockFile = { raw: new Blob(['invalid json']) }
      wrapper.vm.selectedFile = mockFile

      const error = new Error('验证失败')
      configImportExportAPI.validateConfig.mockRejectedValue(error)

      await wrapper.vm.validateConfig()

      expect(ElMessage.error).toHaveBeenCalledWith('配置验证失败: 验证失败')
    })
  })

  describe('配置导入', () => {
    it('应该能够导入配置文件', async () => {
      const mockFile = { raw: new Blob(['{"test": "data"}']) }
      wrapper.vm.selectedFile = mockFile

      ElMessageBox.confirm.mockResolvedValue()
      const mockResponse = { 
        data: { 
          message: '导入成功',
          import_result: { providers_imported: 1, strategies_imported: 1 }
        } 
      }
      configImportExportAPI.importConfig.mockResolvedValue(mockResponse)

      await wrapper.vm.importConfig()

      expect(configImportExportAPI.importConfig).toHaveBeenCalled()
      expect(ElMessage.success).toHaveBeenCalledWith('配置导入成功')
    })

    it('应该在用户取消时停止导入', async () => {
      ElMessageBox.confirm.mockRejectedValue('cancel')

      await wrapper.vm.importConfig()

      expect(configImportExportAPI.importConfig).not.toHaveBeenCalled()
    })

    it('应该在导入失败时显示错误信息', async () => {
      const mockFile = { raw: new Blob(['{"test": "data"}']) }
      wrapper.vm.selectedFile = mockFile

      ElMessageBox.confirm.mockResolvedValue()
      const error = new Error('导入失败')
      configImportExportAPI.importConfig.mockRejectedValue(error)

      await wrapper.vm.importConfig()

      expect(ElMessage.error).toHaveBeenCalledWith('导入配置失败: 导入失败')
    })
  })

  describe('文件内容读取', () => {
    it('应该能够读取JSON文件内容', async () => {
      const mockFile = new Blob(['{"test": "data"}'])
      const mockFileReader = {
        readAsText: vi.fn(),
        onload: null,
        result: '{"test": "data"}'
      }
      global.FileReader.mockImplementation(() => mockFileReader)

      const result = await wrapper.vm.readFileContent(mockFile)

      expect(result).toEqual({ test: 'data' })
    })

    it('应该在读取失败时抛出错误', async () => {
      const mockFile = new Blob(['invalid json'])
      const mockFileReader = {
        readAsText: vi.fn(),
        onload: null,
        result: 'invalid json'
      }
      global.FileReader.mockImplementation(() => mockFileReader)

      await expect(wrapper.vm.readFileContent(mockFile)).rejects.toThrow()
    })
  })

  describe('日期时间格式化', () => {
    it('应该能够格式化日期时间', () => {
      const dateStr = '2023-12-01T10:30:00Z'
      const result = wrapper.vm.formatDateTime(dateStr)

      expect(result).toMatch(/2023\/12\/1/)
    })

    it('应该处理空日期时间', () => {
      const result = wrapper.vm.formatDateTime('')

      expect(result).toBe('')
    })
  })
})
