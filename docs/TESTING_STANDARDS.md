# 前端测试规范

## 📋 目录
- [测试文件组织](#测试文件组织)
- [命名规范](#命名规范)
- [测试结构](#测试结构)
- [Mock策略](#mock策略)
- [覆盖率要求](#覆盖率要求)
- [最佳实践](#最佳实践)
- [常见模式](#常见模式)

## 📁 测试文件组织

### 目录结构
```
src/
├── components/
│   ├── ComponentName.vue
│   └── __tests__/
│       ├── ComponentName.spec.ts          # 真实组件测试
│       ├── ComponentName.behavior.spec.ts # 行为测试（Mock）
│       └── ComponentName.integration.spec.ts # 集成测试
├── views/
│   ├── ViewName.vue
│   └── __tests__/
│       ├── ViewName.spec.ts
│       └── ViewName.behavior.spec.ts
├── api/
│   ├── apiName.js
│   └── __tests__/
│       └── apiName.spec.ts
└── utils/
    ├── utilName.js
    └── __tests__/
        └── utilName.spec.ts
```

### 文件命名规范
- **组件测试**: `ComponentName.spec.ts`
- **行为测试**: `ComponentName.behavior.spec.ts`
- **集成测试**: `ComponentName.integration.spec.ts`
- **API测试**: `apiName.spec.ts`
- **工具函数测试**: `utilName.spec.ts`

## 🏷️ 命名规范

### 测试套件命名
```typescript
// ✅ 正确
describe('Login.vue Component', () => {
describe('UserArticles.vue Component', () => {
describe('auth.js API', () => {
describe('formatDate utility', () => {

// ❌ 错误
describe('Login', () => {
describe('test login', () => {
```

### 测试用例命名
```typescript
// ✅ 正确 - 使用中文描述，清晰表达测试目的
it('应该正确渲染登录表单', () => {
it('用户输入有效邮箱时应该通过验证', () => {
it('API调用失败时应该显示错误信息', () => {
it('空数据时应该显示默认状态', () => {

// ❌ 错误
it('should render form', () => {
it('test validation', () => {
it('works', () => {
```

## 🏗️ 测试结构

### 标准测试结构
```typescript
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import ComponentName from '../ComponentName.vue'

// Mock 外部依赖
vi.mock('@/api/auth', () => ({
  login: vi.fn()
}))

describe('ComponentName.vue Component', () => {
  let wrapper: any

  // 测试数据
  const mockProps = {
    // 定义测试用的props
  }

  beforeEach(() => {
    // 清理mock
    vi.clearAllMocks()
    
    // 创建组件实例
    wrapper = mount(ComponentName, {
      props: mockProps,
      global: {
        // 全局配置
      }
    })
  })

  afterEach(() => {
    // 清理资源
    if (wrapper) {
      wrapper.unmount()
    }
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('应该正确渲染组件容器', () => {
      expect(wrapper.find('.component-container').exists()).toBe(true)
    })

    it('应该显示正确的标题', () => {
      expect(wrapper.text()).toContain('期望的标题')
    })
  })

  describe('属性验证', () => {
    it('应该正确接收props', () => {
      expect(wrapper.props('propName')).toBe(expectedValue)
    })

    it('props变化时应该正确更新', async () => {
      await wrapper.setProps({ propName: 'newValue' })
      expect(wrapper.props('propName')).toBe('newValue')
    })
  })

  describe('用户交互', () => {
    it('点击按钮时应该触发事件', async () => {
      const button = wrapper.find('.action-button')
      await button.trigger('click')
      
      expect(wrapper.emitted('action')).toBeTruthy()
    })

    it('输入框变化时应该更新数据', async () => {
      const input = wrapper.find('.input-field')
      await input.setValue('test value')
      
      expect(wrapper.vm.inputValue).toBe('test value')
    })
  })

  describe('API调用', () => {
    it('组件挂载时应该调用API', () => {
      expect(mockApi.fetchData).toHaveBeenCalled()
    })

    it('API成功时应该更新数据', async () => {
      // 模拟API成功响应
      mockApi.fetchData.mockResolvedValue(mockData)
      
      await wrapper.vm.loadData()
      
      expect(wrapper.vm.data).toEqual(mockData)
    })

    it('API失败时应该显示错误', async () => {
      // 模拟API失败
      mockApi.fetchData.mockRejectedValue(new Error('API Error'))
      
      await wrapper.vm.loadData()
      
      expect(wrapper.text()).toContain('错误信息')
    })
  })

  describe('边界情况', () => {
    it('空数据时应该显示默认状态', () => {
      wrapper = mount(ComponentName, {
        props: { data: [] }
      })
      
      expect(wrapper.text()).toContain('暂无数据')
    })

    it('加载状态时应该显示loading', () => {
      wrapper.vm.loading = true
      
      expect(wrapper.text()).toContain('加载中')
    })
  })

  describe('响应式数据', () => {
    it('数据变化时应该正确更新', async () => {
      const newData = { id: 1, name: 'test' }
      wrapper.vm.data = newData
      
      await nextTick()
      
      expect(wrapper.vm.data).toEqual(newData)
    })
  })
})
```

## 🎭 Mock策略

### Mock组件测试（行为测试）
```typescript
// 用于测试组件的行为逻辑，不测试实际实现
const mockComponent = {
  template: `
    <div class="component">
      <button @click="handleClick">{{ buttonText }}</button>
    </div>
  `,
  data() {
    return {
      buttonText: '点击我'
    }
  },
  methods: {
    handleClick() {
      this.$emit('clicked')
    }
  }
}

describe('Component Behavior', () => {
  it('点击按钮时应该触发事件', async () => {
    const wrapper = mount(mockComponent)
    await wrapper.find('button').trigger('click')
    
    expect(wrapper.emitted('clicked')).toBeTruthy()
  })
})
```

### Mock外部依赖
```typescript
// Mock API
vi.mock('@/api/auth', () => ({
  login: vi.fn().mockResolvedValue({ token: 'mock-token' }),
  logout: vi.fn().mockResolvedValue({})
}))

// Mock Router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn()
}

// Mock Store
const mockStore = {
  state: { user: null },
  commit: vi.fn(),
  dispatch: vi.fn()
}
```

## 📊 覆盖率要求

### 最低覆盖率标准
- **组件测试**: 80% 语句覆盖率
- **API测试**: 90% 语句覆盖率
- **工具函数**: 95% 语句覆盖率
- **整体项目**: 70% 语句覆盖率

### 覆盖率检查
```bash
# 运行测试并检查覆盖率
npm run test:fe -- --coverage

# 检查特定文件的覆盖率
npm run test:fe -- --coverage --reporter=text | grep "ComponentName"
```

## ✅ 最佳实践

### 1. 测试隔离
```typescript
// ✅ 每个测试都是独立的
beforeEach(() => {
  vi.clearAllMocks() // 清理mock状态
})

afterEach(() => {
  wrapper?.unmount() // 清理组件实例
})
```

### 2. 测试数据管理
```typescript
// ✅ 使用工厂函数创建测试数据
const createMockUser = (overrides = {}) => ({
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  ...overrides
})

// 使用
const user = createMockUser({ username: 'custom' })
```

### 3. 异步测试
```typescript
// ✅ 正确处理异步操作
it('异步加载数据', async () => {
  await wrapper.vm.loadData()
  await nextTick()
  
  expect(wrapper.vm.data).toBeDefined()
})
```

### 4. 错误处理测试
```typescript
// ✅ 测试错误情况
it('API失败时应该处理错误', async () => {
  mockApi.fetchData.mockRejectedValue(new Error('Network Error'))
  
  await wrapper.vm.loadData()
  
  expect(wrapper.vm.error).toBe('Network Error')
})
```

## 🔄 常见模式

### 1. 数据流测试模式 ⭐ 新增
```typescript
describe('数据流测试', () => {
  it('前端数据应该正确传递到后端', async () => {
    // 1. 模拟前端操作
    await wrapper.vm.submitData()
    
    // 2. 验证API调用参数
    expect(mockAPI.submit).toHaveBeenCalledWith(
      expect.objectContaining({
        mistakes: expect.any(Object),
        wrong_count: expect.any(Number)
      })
    )
  })

  it('后端数据应该正确保存到数据库', async () => {
    // 1. 模拟API响应
    mockAPI.submit.mockResolvedValue({ success: true })
    
    // 2. 验证数据保存
    expect(mockDatabase.save).toHaveBeenCalledWith(
      expect.objectContaining({
        mistakes: { 'l': ['l', 'l'] }
      })
    )
  })

  it('数据库数据应该正确显示在前端', async () => {
    // 1. 模拟数据获取
    mockAPI.getData.mockResolvedValue({
      data: [{ name: 'l', value: 5 }]
    })
    
    // 2. 验证前端显示
    await wrapper.vm.loadData()
    expect(wrapper.text()).toContain('L键: 5次错误')
  })
})
```

### 2. 集成测试模式 ⭐ 新增
```typescript
describe('集成测试', () => {
  it('完整业务流程应该正常工作', async () => {
    // 1. 用户输入错误
    await wrapper.find('.input').setValue('helo')
    
    // 2. 提交练习结果
    await wrapper.find('.submit').trigger('click')
    
    // 3. 验证数据传递
    expect(mockAPI.submit).toHaveBeenCalledWith(
      expect.objectContaining({
        mistakes: { 'l': ['l'] }
      })
    )
    
    // 4. 验证热力图更新
    await wrapper.vm.refreshData()
    expect(wrapper.find('.error-count').text()).toContain('1')
  })
})
```

### 3. 表单测试模式
```typescript
describe('表单测试', () => {
  it('应该验证必填字段', async () => {
    const form = wrapper.find('form')
    await form.trigger('submit')
    
    expect(wrapper.text()).toContain('请填写必填字段')
  })

  it('应该提交有效数据', async () => {
    await wrapper.find('[name="username"]').setValue('testuser')
    await wrapper.find('[name="password"]').setValue('password123')
    
    const form = wrapper.find('form')
    await form.trigger('submit')
    
    expect(mockApi.submit).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password123'
    })
  })
})
```

### 2. 列表测试模式
```typescript
describe('列表测试', () => {
  it('应该渲染列表项', () => {
    const items = wrapper.findAll('.list-item')
    expect(items).toHaveLength(3)
  })

  it('应该处理空列表', () => {
    wrapper = mount(Component, { props: { items: [] } })
    
    expect(wrapper.text()).toContain('暂无数据')
  })

  it('应该支持分页', async () => {
    await wrapper.find('.next-page').trigger('click')
    
    expect(wrapper.vm.currentPage).toBe(2)
  })
})
```

### 3. 模态框测试模式
```typescript
describe('模态框测试', () => {
  it('应该显示模态框', async () => {
    await wrapper.find('.open-modal').trigger('click')
    
    expect(wrapper.find('.modal').isVisible()).toBe(true)
  })

  it('应该关闭模态框', async () => {
    await wrapper.find('.close-modal').trigger('click')
    
    expect(wrapper.find('.modal').isVisible()).toBe(false)
  })
})
```

## 🚀 测试执行规范

### 开发阶段
```bash
# 开发时运行相关测试
npm run test:fe -- --run src/components/__tests__/ComponentName.spec.ts

# 监听模式
npm run test:fe:watch
```

### 提交前检查
```bash
# 运行所有测试
npm run test:fe

# 检查覆盖率
npm run test:fe -- --coverage
```

### CI/CD集成
```yaml
# .github/workflows/test.yml
- name: Run Tests
  run: |
    cd frontend
    npm run test:fe -- --coverage --reporter=junit
```

## 📝 检查清单

### 新功能开发检查清单
- [ ] 编写了基础渲染测试
- [ ] 编写了用户交互测试
- [ ] 编写了API调用测试
- [ ] 编写了错误处理测试
- [ ] 编写了边界情况测试
- [ ] **编写了数据流测试** ⭐ 新增
- [ ] **编写了集成测试** ⭐ 新增
- [ ] 测试覆盖率达到要求
- [ ] 所有测试通过

### 代码审查检查清单
- [ ] 测试命名清晰明确
- [ ] 测试结构符合规范
- [ ] Mock使用合理
- [ ] 异步测试正确处理
- [ ] 错误情况有测试覆盖
- [ ] 测试数据管理良好
- [ ] **数据流测试覆盖完整** ⭐ 新增
- [ ] **集成测试覆盖完整** ⭐ 新增

## 🎯 总结

遵循这些测试规范可以确保：
1. **测试质量一致** - 所有测试都遵循相同标准
2. **维护成本低** - 测试代码易于理解和维护
3. **覆盖率达标** - 确保关键功能得到充分测试
4. **团队协作好** - 新成员可以快速上手
5. **项目质量高** - 减少bug，提高稳定性
6. **数据流完整** - 确保前后端数据传递正确 ⭐ 新增
7. **集成测试覆盖** - 验证完整业务流程 ⭐ 新增

## 🚨 重要提醒 ⭐ 新增

### 测试策略改进记录
**日期**: 2024年12月
**问题**: 按键错误热力图没有更新
**原因**: 前端没有正确发送按键错误信息到后端
**教训**: 仅测试组件渲染是不够的，必须测试数据流和集成场景

### 新增测试要求
1. **数据流测试**: 验证前端→后端→数据库→前端的完整数据传递
2. **集成测试**: 测试多个组件协作的完整业务流程
3. **用户场景测试**: 模拟真实用户操作场景
4. **数据一致性测试**: 确保前后端数据结构一致

### 自动遵循规则
- 每次编写测试时，必须包含数据流测试
- 每个功能模块必须包含集成测试
- 测试覆盖率必须包含数据传递验证
- 代码审查时必须检查数据流测试完整性

记住：**好的测试规范是项目质量的基石！** 