import { describe, it, expect } from 'vitest'

describe('基础测试环境', () => {
  it('应该能够运行基础测试', () => {
    expect(true).toBe(true)
  })

  it('应该能够进行数学运算', () => {
    expect(1 + 1).toBe(2)
    expect(2 * 3).toBe(6)
    expect(10 / 2).toBe(5)
  })

  it('应该能够处理字符串', () => {
    expect('hello').toBe('hello')
    expect('hello' + ' world').toBe('hello world')
  })

  it('应该能够处理数组', () => {
    const arr = [1, 2, 3]
    expect(arr.length).toBe(3)
    expect(arr[0]).toBe(1)
    expect(arr.includes(2)).toBe(true)
  })

  it('应该能够处理对象', () => {
    const obj = { name: 'test', value: 123 }
    expect(obj.name).toBe('test')
    expect(obj.value).toBe(123)
    expect(Object.keys(obj)).toHaveLength(2)
  })
})
