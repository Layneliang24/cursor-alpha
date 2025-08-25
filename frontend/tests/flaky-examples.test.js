/**
 * 前端Flaky测试示例
 * 
 * 这些测试用例故意设计为不稳定，用于演示flaky测试检测机制
 * 注意：这些测试仅用于演示目的，在实际项目中应该避免这样的测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

// 模拟组件
const FlakyComponent = {
  template: `
    <div>
      <button @click="increment" data-testid="increment-btn">{{ count }}</button>
      <div data-testid="status">{{ status }}</div>
    </div>
  `,
  data() {
    return {
      count: 0,
      status: 'ready'
    }
  },
  methods: {
    async increment() {
      this.status = 'loading'
      // 模拟异步操作
      await new Promise(resolve => setTimeout(resolve, Math.random() * 100))
      this.count++
      this.status = 'ready'
    }
  }
}

describe('Flaky Test Examples', () => {
  let wrapper
  
  beforeEach(() => {
    // 重置随机种子（虽然这不会完全消除随机性）
    Math.random = Math.random
  })
  
  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })
  
  it('should pass randomly - 60% success rate', () => {
    // 这个测试有60%的成功率
    const shouldPass = Math.random() < 0.6
    expect(shouldPass).toBe(true)
  })
  
  it('should fail due to timing issues', async () => {
    wrapper = mount(FlakyComponent)
    
    const button = wrapper.find('[data-testid="increment-btn"]')
    await button.trigger('click')
    
    // 这个断言可能因为异步操作的时间而失败
    const startTime = Date.now()
    await nextTick()
    const endTime = Date.now()
    
    // 如果操作时间超过50ms，测试失败
    const duration = endTime - startTime
    expect(duration).toBeLessThan(50) // 这可能会随机失败
  })
  
  it('should fail due to race condition', async () => {
    wrapper = mount(FlakyComponent)
    
    // 同时触发多个点击事件
    const button = wrapper.find('[data-testid="increment-btn"]')
    const promises = []
    
    for (let i = 0; i < 3; i++) {
      promises.push(button.trigger('click'))
    }
    
    await Promise.all(promises)
    await nextTick()
    
    // 由于竞态条件，count可能不是期望的值
    const count = wrapper.vm.count
    
    // 添加随机性来模拟真实的竞态条件
    if (Math.random() < 0.4) { // 40%失败率
      expect(count).toBe(2) // 故意错误的期望值
    } else {
      expect(count).toBe(3)
    }
  })
  
  it('should be stable test', () => {
    // 这个测试应该总是通过
    expect(2 + 2).toBe(4)
    expect('hello'.toUpperCase()).toBe('HELLO')
    expect([1, 2, 3]).toHaveLength(3)
  })
  
  it('should fail due to mock instability', () => {
    // 模拟不稳定的外部依赖
    const mockFetch = vi.fn()
    
    // 70%的时间返回成功响应
    if (Math.random() < 0.7) {
      mockFetch.mockResolvedValue({ ok: true, json: () => ({ data: 'success' }) })
    } else {
      mockFetch.mockRejectedValue(new Error('Network error'))
    }
    
    global.fetch = mockFetch
    
    // 这个测试可能因为mock的随机行为而失败
    return fetch('/api/data')
      .then(response => {
        expect(response.ok).toBe(true)
        return response.json()
      })
      .then(data => {
        expect(data.data).toBe('success')
      })
  })
  
  it('should fail due to DOM timing', async () => {
    wrapper = mount(FlakyComponent)
    
    const button = wrapper.find('[data-testid="increment-btn"]')
    await button.trigger('click')
    
    // 不等待足够的时间就检查状态
    const status = wrapper.find('[data-testid="status"]').text()
    
    // 这可能会因为异步操作还未完成而失败
    if (Math.random() < 0.3) { // 30%失败率
      expect(status).toBe('ready') // 可能还是'loading'
    } else {
      // 等待一下再检查
      await new Promise(resolve => setTimeout(resolve, 150))
      await nextTick()
      expect(wrapper.find('[data-testid="status"]').text()).toBe('ready')
    }
  })
  
  it('should fail due to memory pressure', () => {
    // 模拟内存压力测试
    const largeArray = []
    
    try {
      // 随机决定是否创建大量数据
      if (Math.random() < 0.2) { // 20%的概率
        for (let i = 0; i < 100000; i++) {
          largeArray.push(`data_${i}`.repeat(10))
        }
      }
      
      // 模拟内存不足
      if (largeArray.length > 50000) {
        throw new Error('Out of memory')
      }
      
      expect(true).toBe(true)
    } finally {
      // 清理内存
      largeArray.length = 0
    }
  })
  
  it('should be another stable test', () => {
    // 另一个稳定的测试
    const obj = { name: 'test', value: 42 }
    expect(obj).toHaveProperty('name')
    expect(obj.value).toBeGreaterThan(0)
    expect(Array.isArray([])).toBe(true)
  })
  
  it('should fail due to environment variables', () => {
    // 模拟环境变量依赖
    const originalEnv = process.env.NODE_ENV
    
    try {
      // 随机模拟环境问题
      if (Math.random() < 0.25) { // 25%失败率
        process.env.NODE_ENV = 'invalid'
      }
      
      const validEnvs = ['development', 'test', 'production']
      expect(validEnvs).toContain(process.env.NODE_ENV)
    } finally {
      // 恢复原始环境变量
      process.env.NODE_ENV = originalEnv
    }
  })
  
  it('should fail due to async timing', async () => {
    // 模拟异步操作的时间问题
    const delay = Math.random() * 200 // 0-200ms的随机延迟
    
    const promise = new Promise(resolve => {
      setTimeout(() => resolve('done'), delay)
    })
    
    const startTime = Date.now()
    const result = await promise
    const endTime = Date.now()
    
    expect(result).toBe('done')
    
    // 这个断言可能因为随机延迟而失败
    const actualDelay = endTime - startTime
    expect(actualDelay).toBeLessThan(100) // 可能会随机失败
  })
})

describe('Flaky Utility Functions', () => {
  it('should test network simulation', async () => {
    // 模拟网络请求
    const simulateNetworkRequest = () => {
      return new Promise((resolve, reject) => {
        const delay = Math.random() * 100
        const shouldFail = Math.random() < 0.3 // 30%失败率
        
        setTimeout(() => {
          if (shouldFail) {
            reject(new Error('Network timeout'))
          } else {
            resolve({ data: 'success', delay })
          }
        }, delay)
      })
    }
    
    try {
      const result = await simulateNetworkRequest()
      expect(result.data).toBe('success')
      expect(result.delay).toBeGreaterThanOrEqual(0)
    } catch (error) {
      // 这个测试可能会因为模拟的网络错误而失败
      expect(error.message).toBe('Network timeout')
    }
  })
  
  it('should test random data generation', () => {
    // 生成随机数据
    const generateRandomData = () => {
      const data = []
      const count = Math.floor(Math.random() * 10) + 1
      
      for (let i = 0; i < count; i++) {
        data.push({
          id: i,
          value: Math.random() * 100,
          active: Math.random() > 0.5
        })
      }
      
      return data
    }
    
    const data = generateRandomData()
    expect(data).toBeInstanceOf(Array)
    expect(data.length).toBeGreaterThan(0)
    
    // 这个断言可能因为随机数据而失败
    const activeCount = data.filter(item => item.active).length
    const expectedActiveCount = Math.ceil(data.length / 2)
    
    // 添加一些容差，但仍然可能失败
    if (Math.random() < 0.2) { // 20%失败率
      expect(activeCount).toBe(expectedActiveCount) // 可能不匹配
    } else {
      expect(activeCount).toBeGreaterThanOrEqual(0)
    }
  })
  
  it('should be a stable utility test', () => {
    // 稳定的工具函数测试
    const utils = {
      add: (a, b) => a + b,
      multiply: (a, b) => a * b,
      isEven: (n) => n % 2 === 0
    }
    
    expect(utils.add(2, 3)).toBe(5)
    expect(utils.multiply(4, 5)).toBe(20)
    expect(utils.isEven(6)).toBe(true)
    expect(utils.isEven(7)).toBe(false)
  })
})

// 独立的测试用例
it('should be a standalone flaky test', () => {
  // 独立的flaky测试
  const randomValue = Math.random()
  
  // 这个测试有大约50%的成功率
  if (randomValue < 0.5) {
    expect(randomValue).toBeGreaterThan(0.5) // 故意错误的断言
  } else {
    expect(randomValue).toBeLessThanOrEqual(1)
  }
})

it('should be a standalone stable test', () => {
  // 独立的稳定测试
  expect(Math.PI).toBeCloseTo(3.14159, 4)
  expect(typeof 'string').toBe('string')
  expect(null).toBeNull()
})