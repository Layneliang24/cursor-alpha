# 前端测试指南

## 概述

本项目使用 **Vitest** 作为前端测试框架，配合 **@vue/test-utils** 和 **@testing-library/vue** 进行组件测试。

## 测试结构

```
frontend/tests/
├── README.md                 # 本文件
├── setupTests.ts            # 测试环境配置
├── factories.ts             # 测试数据工厂
└── __tests__/               # 测试用例目录
    ├── components/          # 组件测试
    │   ├── App.spec.ts     # App组件测试
    │   ├── TopNavBar.spec.ts # 导航栏测试
    │   ├── FooterComponent.spec.ts # 页脚测试
    │   └── NavBar.spec.ts  # 导航栏测试
    └── utils/               # 工具函数测试
        └── soundResources.spec.ts # 声音资源测试
```

## 测试级别

### 1. 冒烟测试 (Smoke)
- **用途**: 快速验证核心功能
- **覆盖**: 主要组件渲染、基础交互
- **执行时间**: 1-2分钟
- **命令**: `npm run test:fe -- --run`

### 2. 快速测试 (Fast)
- **用途**: 验证主要功能逻辑
- **覆盖**: 组件功能、工具函数、用户交互
- **执行时间**: 3-5分钟
- **命令**: `npm run test:fe -- --run --max-threads=2`

### 3. 全量测试 (Full)
- **用途**: 全面验证所有功能
- **覆盖**: 所有测试用例、边界条件、异常处理
- **执行时间**: 8-12分钟
- **命令**: `npm run test:fe -- --run --coverage`

### 4. 性能测试 (Performance)
- **用途**: 评估组件性能
- **覆盖**: 渲染性能、内存使用、响应时间
- **执行时间**: 5-8分钟
- **命令**: `npm run test:fe -- --run --max-threads=1`

## 运行测试

### 本地开发
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 运行测试（监听模式）
npm run test:fe:watch

# 运行测试（单次执行）
npm run test:fe

# 运行测试（带覆盖率）
npm run test:fe -- --coverage
```

### 集成到项目测试体系
```bash
# 项目根目录
# 运行前端冒烟测试
python tests/test_runner_optimized.py --level frontend

# 运行前端全量测试
python tests/test_runner_optimized.py --level frontend --coverage

# 运行前端性能测试
python tests/test_runner_optimized.py --level frontend --verbose
```

## 测试数据工厂

使用 `tests/factories.ts` 中的工厂类生成测试数据：

```typescript
import { UserFactory, ArticleFactory, WordFactory } from './factories'

// 创建单个用户
const user = UserFactory.create({ username: 'testuser' })

// 创建多个文章
const articles = ArticleFactory.createMultiple(5, { category: '技术' })

// 创建不同难度的单词
const easyWords = WordFactory.createByDifficulty('easy', 10)
const hardWords = WordFactory.createByDifficulty('hard', 5)

// 创建完整数据集
const dataset = TestDataSetFactory.createCompleteDataset()
```

## 测试最佳实践

### 1. 组件测试
- 测试组件渲染
- 测试用户交互
- 测试props变化
- 测试事件触发
- 测试计算属性

### 2. 工具函数测试
- 测试正常输入
- 测试边界条件
- 测试异常情况
- 测试返回值类型

### 3. 集成测试
- 测试组件间通信
- 测试路由导航
- 测试状态管理
- 测试API调用

### 4. 测试隔离
- 每个测试用例独立
- 使用beforeEach清理状态
- Mock外部依赖
- 避免测试间数据污染

## 测试配置

### Vitest配置
```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    css: true,
    include: ['src/**/__tests__/**/*.{test,spec}.{js,ts,jsx,tsx}'],
    setupFiles: ['./tests/setupTests.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      reportsDirectory: './coverage'
    }
  }
})
```

### 测试环境设置
```typescript
// tests/setupTests.ts
import { config } from '@vue/test-utils'
import { vi } from 'vitest'

// 全局配置
config.global.stubs = {
  'router-link': true,
  'router-view': true
}

// Mock全局对象
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))
```

## 覆盖率报告

测试完成后，覆盖率报告保存在 `frontend/coverage/` 目录：

- **HTML报告**: `coverage/index.html`
- **文本报告**: 控制台输出
- **JSON数据**: `coverage/coverage-summary.json`

## 常见问题

### 1. 测试环境问题
```bash
# 清理缓存
rm -rf node_modules/.cache
rm -rf .vitest

# 重新安装依赖
npm install
```

### 2. 组件渲染问题
- 检查组件是否正确导入
- 确认测试环境配置
- 验证Mock组件设置

### 3. 异步测试问题
- 使用 `await wrapper.vm.$nextTick()`
- 等待路由就绪 `await router.isReady()`
- 处理异步操作 `await action()`

### 4. 覆盖率问题
- 检查测试文件命名规范
- 确认测试文件位置
- 验证覆盖率配置

## 持续集成

前端测试已集成到项目的CI/CD流程中：

- **GitHub Actions**: 自动运行前端测试
- **测试报告**: 生成HTML和JSON格式报告
- **质量门禁**: 覆盖率阈值检查
- **并行执行**: 支持多进程测试

## 贡献指南

### 添加新测试
1. 在对应目录创建测试文件
2. 使用描述性的测试名称
3. 遵循测试最佳实践
4. 确保测试覆盖率

### 修改现有测试
1. 保持向后兼容
2. 更新相关文档
3. 验证测试通过
4. 检查覆盖率变化

### 测试命名规范
- 测试文件: `ComponentName.spec.ts`
- 测试套件: `describe('ComponentName', ...)`
- 测试用例: `it('should do something', ...)`
- 测试数据: 使用工厂函数生成

## 相关资源

- [Vitest官方文档](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Testing Library Vue](https://testing-library.com/docs/vue-testing-library/intro/)
- [Vue 3测试指南](https://vuejs.org/guide/scaling-up/testing.html) 