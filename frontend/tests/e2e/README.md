# Playwright E2E 测试

这个目录包含使用 Playwright 编写的端到端测试，用于验证地道表达学习平台的前端功能。

## 快速开始

### 安装依赖
```bash
npm install @playwright/test
npx playwright install
```

### 运行测试
```bash
# 运行所有测试
npm run test:e2e

# 运行特定测试文件
npx playwright test basic-navigation.spec.ts

# 使用可视化界面运行测试
npm run test:e2e:ui

# 调试模式运行测试
npm run test:e2e:debug

# 查看测试报告
npm run test:e2e:report
```

## 测试文件结构

- `basic-navigation.spec.ts` - 基础导航功能测试
- `idiomatic-expressions.spec.ts` - 地道表达学习功能测试
- `utils/test-helpers.ts` - 测试工具类

## 测试覆盖范围

### 基础功能测试
- ✅ 首页加载
- ✅ 页面导航
- ✅ 登录页面显示
- ✅ 路由守卫（认证重定向）

### 地道表达学习功能测试
- ✅ 地道表达列表页面
- ✅ 地道表达学习页面
- ✅ 学习模式切换
- ✅ AI助教聊天界面
- ✅ 学习分析页面

### 跨浏览器测试
支持以下浏览器和设备：
- Desktop Chrome
- Desktop Firefox  
- Desktop Safari (WebKit)
- Mobile Chrome
- Mobile Safari
- Microsoft Edge
- Google Chrome

## 配置说明

### playwright.config.ts
主要配置项：
- `baseURL`: 测试的基础URL (http://localhost:3000)
- `testDir`: 测试文件目录 (./tests/e2e)
- `webServer`: 自动启动开发服务器
- `reporter`: 测试报告格式（HTML、JSON、列表）
- `use`: 全局测试选项（截图、录屏、追踪等）

### 测试工具类
`utils/test-helpers.ts` 提供了以下工具方法：
- `waitForVueApp()` - 等待Vue应用加载
- `checkAuthRedirect()` - 检查认证重定向
- `loginIfNeeded()` - 自动登录（如果需要）
- `navigateWithAuth()` - 带认证处理的页面导航
- `checkForJSErrors()` - 检查JavaScript错误
- `checkPagePerformance()` - 页面性能检查
- `checkResponsiveDesign()` - 响应式设计检查

## 测试最佳实践

### 选择器策略
1. 优先使用 `data-testid` 属性
2. 使用语义化选择器（如 `getByRole`）
3. 避免依赖CSS类名和ID（除非稳定）
4. 使用 `.first()` 处理多个匹配元素

### 等待策略
```typescript
// 等待元素可见
await expect(element).toBeVisible();

// 等待网络空闲
await page.waitForLoadState('networkidle');

// 等待特定选择器
await page.waitForSelector('.some-element');
```

### 错误处理
```typescript
// 检查认证重定向
if (page.url().includes('login')) {
  console.log('需要登录，跳过测试');
  return;
}

// 处理多个可能的元素
const element = page.locator('.element').first();
```

## 调试技巧

### 可视化调试
```bash
# 有头模式运行
npx playwright test --headed

# 调试特定测试
npx playwright test basic-navigation.spec.ts --debug

# 使用UI模式
npm run test:e2e:ui
```

### 截图和录屏
测试失败时会自动生成：
- 截图：`test-results/[test-name]/test-failed-1.png`
- 录屏：`test-results/[test-name]/video.webm`
- 追踪：`test-results/[test-name]/trace.zip`

### 查看测试报告
```bash
# 生成并打开HTML报告
npm run test:e2e:report
```

## 持续集成

测试配置已优化用于CI环境：
- CI环境下重试失败的测试2次
- 使用单个worker避免资源冲突
- 自动启动和停止开发服务器

## 常见问题

### Q: 测试失败显示"strict mode violation"
A: 使用 `.first()` 或更具体的选择器来处理多个匹配元素

### Q: 测试超时
A: 增加等待时间或检查网络连接：
```typescript
await page.waitForSelector('.element', { timeout: 30000 });
```

### Q: 认证相关测试失败
A: 确保测试账户可用，或跳过需要认证的测试：
```typescript
if (page.url().includes('login')) {
  test.skip(true, '需要用户认证');
}
```

## 扩展测试

### 添加新测试
1. 在 `tests/e2e/` 目录创建 `.spec.ts` 文件
2. 使用 `test.describe()` 组织测试套件
3. 使用 `test()` 定义具体测试用例
4. 使用 `expect()` 进行断言

### 测试模板
```typescript
import { test, expect } from '@playwright/test';

test.describe('功能名称测试', () => {
  test('应该能够执行某个操作', async ({ page }) => {
    await page.goto('/some-page');
    
    // 测试逻辑
    const element = page.locator('.some-element');
    await expect(element).toBeVisible();
  });
});
```
