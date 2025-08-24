# 测试快速开始指南

## 🚀 快速开始

### 1. 运行现有测试
```bash
# 运行所有测试
npm run test:fe

# 运行测试并检查覆盖率
npm run test:fe -- --coverage

# 监听模式（开发时使用）
npm run test:fe:watch
```

### 2. 为新组件编写测试

#### 步骤1：复制测试模板
```bash
# 复制模板到你的组件目录
cp tests/templates/component-test-template.ts src/components/__tests__/YourComponent.spec.ts
```

#### 步骤2：修改模板
```typescript
// 1. 导入你的组件
import YourComponent from '../YourComponent.vue'

// 2. 修改测试套件名称
describe('YourComponent.vue Component', () => {

// 3. 取消注释并修改测试用例
it('应该正确渲染组件', () => {
  expect(wrapper.find('.your-component').exists()).toBe(true)
})
```

#### 步骤3：运行测试
```bash
# 运行特定组件的测试
npm run test:fe -- --run src/components/__tests__/YourComponent.spec.ts
```

### 3. 检查测试规范
```bash
# 检查所有测试文件是否符合规范
npm run test:check

# 运行完整测试（规范检查 + 功能测试）
npm run test:all
```

## 📋 测试检查清单

### 新功能开发
- [ ] 复制了测试模板
- [ ] 修改了组件导入和名称
- [ ] 编写了基础渲染测试
- [ ] 编写了用户交互测试
- [ ] 编写了API调用测试
- [ ] 编写了错误处理测试
- [ ] 编写了边界情况测试
- [ ] **编写了数据流测试** ⭐ 新增
- [ ] **编写了集成测试** ⭐ 新增
- [ ] 运行了测试规范检查
- [ ] 确保测试覆盖率达到80%以上
- [ ] 所有测试通过

### 代码提交前
- [ ] 运行了 `npm run test:check`
- [ ] 运行了 `npm run test:fe`
- [ ] 检查了覆盖率报告
- [ ] 确保没有破坏现有功能

## 🎯 常见测试模式

### 组件测试
```typescript
// 基础渲染
it('应该正确渲染组件', () => {
  expect(wrapper.find('.component').exists()).toBe(true)
})

// 属性验证
it('应该正确接收props', () => {
  expect(wrapper.props('title')).toBe('测试标题')
})

// 用户交互
it('点击按钮时应该触发事件', async () => {
  await wrapper.find('.btn').trigger('click')
  expect(wrapper.emitted('click')).toBeTruthy()
})
```

### API测试
```typescript
// API调用
it('应该调用API获取数据', () => {
  expect(mockApi.fetchData).toHaveBeenCalled()
})

// 成功响应
it('API成功时应该更新数据', async () => {
  mockApi.fetchData.mockResolvedValue(mockData)
  await wrapper.vm.loadData()
  expect(wrapper.vm.data).toEqual(mockData)
})

// 错误处理
it('API失败时应该显示错误', async () => {
  mockApi.fetchData.mockRejectedValue(new Error('API Error'))
  await wrapper.vm.loadData()
  expect(wrapper.text()).toContain('错误信息')
})
```

### 表单测试
```typescript
// 表单验证
it('应该验证必填字段', async () => {
  await wrapper.find('form').trigger('submit')
  expect(wrapper.text()).toContain('请填写必填字段')
})

// 表单提交
it('应该提交有效数据', async () => {
  await wrapper.find('[name="username"]').setValue('testuser')
  await wrapper.find('[name="password"]').setValue('password123')
  await wrapper.find('form').trigger('submit')
  expect(mockApi.submit).toHaveBeenCalledWith({
    username: 'testuser',
    password: 'password123'
  })
})
```

### 数据流测试 ⭐ 新增
```typescript
// 数据传递测试
it('应该正确传递数据到父组件', async () => {
  await wrapper.find('.input').setValue('test value')
  expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  expect(wrapper.emitted('update:modelValue')[0]).toEqual(['test value'])
})

// API参数验证
it('API调用应该包含正确的参数', async () => {
  await wrapper.vm.submitData()
  expect(mockApi.submit).toHaveBeenCalledWith(
    expect.objectContaining({
      mistakes: expect.any(Object),
      wrong_count: expect.any(Number)
    })
  )
})
```

### 集成测试 ⭐ 新增
```typescript
// 组件协作测试
it('与其他组件的协作应该正常', async () => {
  await wrapper.vm.loadData()
  expect(wrapper.find('.child-component').exists()).toBe(true)
  expect(wrapper.find('.data-display').text()).toContain('加载的数据')
})

// 完整流程测试
it('完整业务流程应该正常工作', async () => {
  // 1. 用户操作
  await wrapper.find('.input').setValue('helo')
  
  // 2. 提交数据
  await wrapper.find('.submit').trigger('click')
  
  // 3. 验证数据传递
  expect(mockApi.submit).toHaveBeenCalledWith(
    expect.objectContaining({
      mistakes: { 'l': ['l'] }
    })
  )
  
  // 4. 验证界面更新
  expect(wrapper.text()).toContain('提交成功')
})
```

## 🔧 调试技巧

### 1. 查看测试输出
```bash
# 详细输出
npm run test:fe -- --reporter=verbose

# 只运行失败的测试
npm run test:fe -- --run --reporter=verbose | grep -A 10 -B 10 "FAIL"
```

### 2. 调试特定测试
```typescript
// 在测试中添加调试信息
it('调试测试', () => {
  console.log('组件HTML:', wrapper.html())
  console.log('组件数据:', wrapper.vm.$data)
  console.log('组件方法:', Object.keys(wrapper.vm))
})
```

### 3. 检查Mock状态
```typescript
// 检查Mock是否被调用
expect(mockApi.fetchData).toHaveBeenCalled()
expect(mockApi.fetchData).toHaveBeenCalledWith(expectedParams)

// 检查Mock调用次数
expect(mockApi.fetchData).toHaveBeenCalledTimes(1)
```

## 📊 覆盖率要求

### 最低覆盖率标准
- **组件测试**: 80% 语句覆盖率
- **API测试**: 90% 语句覆盖率
- **工具函数**: 95% 语句覆盖率
- **整体项目**: 70% 语句覆盖率

### 检查覆盖率
```bash
# 查看覆盖率报告
npm run test:fe -- --coverage --reporter=text

# 查看特定文件覆盖率
npm run test:fe -- --coverage --reporter=text | grep "YourComponent"
```

## 🚨 常见问题

### 1. 测试失败：找不到组件
```bash
# 检查组件路径是否正确
import YourComponent from '../YourComponent.vue'  # 路径要正确
```

### 2. 测试失败：Mock不工作
```typescript
// 确保Mock在测试前设置
beforeEach(() => {
  vi.clearAllMocks()  // 清理Mock状态
})

// 确保Mock函数被正确调用
expect(mockApi.fetchData).toHaveBeenCalled()
```

### 3. 测试失败：异步操作
```typescript
// 使用 async/await 处理异步
it('异步测试', async () => {
  await wrapper.vm.loadData()
  await nextTick()  // 等待DOM更新
  expect(wrapper.vm.data).toBeDefined()
})
```

### 4. 测试失败：组件未挂载
```typescript
// 确保组件正确挂载
beforeEach(() => {
  wrapper = mount(YourComponent, {
    props: { /* props */ },
    global: { /* 全局配置 */ }
  })
})
```

## 📚 更多资源

- [测试规范文档](./TESTING_STANDARDS.md) - 详细的测试编写规范
- [测试模板](../tests/templates/component-test-template.ts) - 完整的测试模板
- [Vitest文档](https://vitest.dev/) - 官方测试框架文档
- [Vue Test Utils文档](https://test-utils.vuejs.org/) - Vue测试工具文档

## 🎯 记住要点

1. **测试驱动开发** - 先写测试，再写代码
2. **测试隔离** - 每个测试都是独立的
3. **Mock外部依赖** - 避免测试依赖外部服务
4. **覆盖边界情况** - 测试异常和边界条件
5. **保持测试简单** - 一个测试只验证一个功能
6. **使用描述性名称** - 测试名称要清晰表达测试目的
7. **定期运行测试** - 确保代码变更不会破坏现有功能

**记住：好的测试是项目质量的保障！** 🛡️ 