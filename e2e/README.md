# E2E 测试文档

本项目使用 Playwright 进行端到端（E2E）测试，覆盖关键用户路径和业务流程。

## 📋 目录结构

```
e2e/
├── pages/              # 页面对象模型 (Page Object Model)
│   ├── LoginPage.ts    # 登录页面
│   ├── DictionaryPage.ts # 词典页面
│   └── AnalyticsPage.ts  # 数据分析页面
├── tests/              # 测试用例
│   ├── auth.spec.ts    # 认证功能测试
│   ├── dictionary.spec.ts # 词典功能测试
│   ├── analytics.spec.ts  # 数据分析测试
│   └── user-journey.spec.ts # 完整用户旅程测试
├── utils/              # 测试工具类
│   └── test-helpers.ts # 测试辅助函数
└── README.md          # 本文档
```

## 🚀 快速开始

### 安装依赖

```bash
# 安装 Playwright 和浏览器
npm install
npx playwright install

# 安装前端依赖
cd frontend
npm install

# 安装后端依赖
cd ../backend
pip install -r requirements.txt
```

### 运行测试

```bash
# 运行所有 E2E 测试
npm run test:e2e

# 运行特定浏览器的测试
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# 运行特定测试文件
npx playwright test auth.spec.ts
npx playwright test dictionary.spec.ts

# 以调试模式运行
npm run test:e2e:debug

# 以 UI 模式运行
npm run test:e2e:ui

# 运行测试并生成报告
npm run test:e2e:report
```

### 查看测试报告

```bash
# 查看 HTML 报告
npx playwright show-report

# 查看测试结果
open playwright-report/index.html
```

## 📝 测试覆盖范围

### 🔐 认证功能 (auth.spec.ts)
- 用户登录/注册
- 表单验证
- 错误处理
- 会话管理
- 社交登录（如果可用）

### 📚 词典功能 (dictionary.spec.ts)
- 词典列表和搜索
- 词典创建和管理
- 单词练习流程
- 练习设置配置
- 进度跟踪
- 批量操作
- 导入导出功能

### 📊 数据分析 (analytics.spec.ts)
- 仪表板显示
- 统计数据展示
- 图表交互
- 数据过滤和导出
- 响应式设计
- 错误处理

### 🛤️ 用户旅程 (user-journey.spec.ts)
- 完整学习流程
- 多设备同步
- 学习计划设置
- 社交功能
- 离线学习
- 成就系统

## 🏗️ 页面对象模型 (POM)

我们使用页面对象模型来组织测试代码，提高可维护性和复用性。

### 创建新的页面对象

```typescript
import { Page, Locator } from '@playwright/test';
import { TestHelpers } from '../utils/test-helpers';

export class NewPage {
  private helpers: TestHelpers;
  readonly someElement: Locator;

  constructor(private page: Page) {
    this.helpers = new TestHelpers(page);
    this.someElement = page.locator('[data-testid="some-element"]');
  }

  async goto() {
    await this.page.goto('/new-page');
    await this.helpers.waitForPageLoad();
  }

  async performAction() {
    await this.someElement.click();
    await this.helpers.waitForPageLoad();
  }
}
```

## 🛠️ 测试工具类

### TestHelpers
提供常用的测试辅助方法：
- 页面加载等待
- 元素验证
- 表单填写
- API 模拟
- 截图调试

### TestDataGenerator
生成测试数据：
- 随机用户数据
- 词典测试数据
- 随机字符串

## 📋 测试最佳实践

### 1. 元素定位策略

优先级顺序：
1. `data-testid` 属性
2. 语义化选择器（role, label）
3. 文本内容
4. CSS 选择器（最后选择）

```typescript
// 推荐
page.locator('[data-testid="login-button"]')
page.locator('button:has-text("登录")')
page.getByRole('button', { name: '登录' })

// 避免
page.locator('.btn.btn-primary')
page.locator('#login-form > button')
```

### 2. 等待策略

```typescript
// 等待元素可见
await page.waitForSelector('[data-testid="element"]', { state: 'visible' });

// 等待网络请求完成
await page.waitForLoadState('networkidle');

// 等待特定 API 响应
await page.waitForResponse(response => response.url().includes('/api/'));
```

### 3. 错误处理

```typescript
// 模拟网络错误
await page.route('**/api/**', route => {
  route.abort('failed');
});

// 模拟服务器错误
await page.route('**/api/**', route => {
  route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: '服务器错误' })
  });
});
```

### 4. 测试数据管理

```typescript
// 使用测试数据生成器
const userData = TestDataGenerator.generateUserData();
const dictionaryData = TestDataGenerator.generateDictionaryData();

// 清理测试数据
test.afterEach(async ({ page }) => {
  // 清理创建的测试数据
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
});
```

## 🔧 配置说明

### playwright.config.ts

主要配置项：
- `testDir`: 测试文件目录
- `baseURL`: 应用基础 URL
- `projects`: 浏览器配置
- `webServer`: 本地服务器配置
- `use`: 全局测试选项

### 环境变量

```bash
# 测试环境配置
DATABASE_URL=postgresql://user:pass@localhost:5432/test_db
DJANGO_SETTINGS_MODULE=alpha.settings.test
CI=true  # CI 环境标识
```

## 🚀 CI/CD 集成

### GitHub Actions

E2E 测试在以下情况下运行：
- Push 到 main/develop 分支
- Pull Request
- 每日定时任务

### 测试分片

为了提高执行速度，测试被分为 4 个分片并行运行：

```bash
npx playwright test --shard=1/4
npx playwright test --shard=2/4
npx playwright test --shard=3/4
npx playwright test --shard=4/4
```

### 报告合并

所有分片的测试报告会自动合并并部署到 GitHub Pages。

## 🐛 调试指南

### 1. 本地调试

```bash
# 以调试模式运行特定测试
npx playwright test auth.spec.ts --debug

# 以 headed 模式运行（显示浏览器）
npx playwright test --headed

# 录制测试
npx playwright codegen http://localhost:5173
```

### 2. 查看失败截图和视频

测试失败时会自动生成：
- 截图：`test-results/screenshots/`
- 视频：`test-results/videos/`
- 跟踪文件：`test-results/traces/`

### 3. 跟踪查看器

```bash
# 查看跟踪文件
npx playwright show-trace test-results/trace.zip
```

## 📈 性能测试

### 标记性能测试

```typescript
test('页面加载性能 @performance', async ({ page }) => {
  const startTime = Date.now();
  await page.goto('/');
  const loadTime = Date.now() - startTime;
  
  expect(loadTime).toBeLessThan(3000); // 3秒内加载完成
});
```

### 运行性能测试

```bash
# 运行性能测试
npx playwright test --grep "@performance"

# 在 CI 中触发性能测试
git commit -m "feat: 新功能 [perf]"
```

## 🎨 视觉回归测试

### 创建视觉测试

```typescript
test('页面视觉回归 @visual', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page).toHaveScreenshot('dashboard.png');
});
```

### 更新基准截图

```bash
# 更新所有截图
npx playwright test --update-snapshots

# 更新特定测试的截图
npx playwright test dashboard.spec.ts --update-snapshots
```

## ♿ 可访问性测试

### 安装 axe-playwright

```bash
npm install --save-dev axe-playwright
```

### 创建可访问性测试

```typescript
import { injectAxe, checkA11y } from 'axe-playwright';

test('页面可访问性 @accessibility', async ({ page }) => {
  await page.goto('/login');
  await injectAxe(page);
  await checkA11y(page);
});
```

## 📊 测试指标

### 覆盖率目标
- 关键用户路径：100%
- 主要功能模块：≥90%
- 错误处理场景：≥80%

### 性能指标
- 页面加载时间：<3秒
- 交互响应时间：<500ms
- 测试执行时间：<30分钟

## 🔄 维护指南

### 定期维护任务

1. **每周**：
   - 检查失败的测试
   - 更新测试数据
   - 清理过期的测试报告

2. **每月**：
   - 更新 Playwright 版本
   - 审查测试覆盖率
   - 优化慢速测试

3. **每季度**：
   - 重构重复的测试代码
   - 更新页面对象模型
   - 评估测试策略

### 常见问题解决

#### 测试不稳定 (Flaky Tests)

```typescript
// 增加重试次数
test.describe.configure({ retries: 2 });

// 增加等待时间
await page.waitForTimeout(1000);

// 使用更可靠的等待策略
await page.waitForFunction(() => {
  return document.querySelector('[data-testid="element"]')?.textContent?.includes('期望文本');
});
```

#### 元素定位失败

```typescript
// 使用多个定位策略
const element = page.locator('[data-testid="button"]')
  .or(page.locator('button:has-text("提交")'))
  .or(page.locator('.submit-button'));
```

#### 测试超时

```typescript
// 增加测试超时时间
test.setTimeout(60000); // 60秒

// 针对特定操作增加超时
await page.waitForSelector('[data-testid="element"]', { timeout: 10000 });
```

## 📚 参考资源

- [Playwright 官方文档](https://playwright.dev/)
- [测试最佳实践](https://playwright.dev/docs/best-practices)
- [页面对象模型指南](https://playwright.dev/docs/pom)
- [CI/CD 集成指南](https://playwright.dev/docs/ci)

## 🤝 贡献指南

1. 创建新测试时，请遵循现有的命名约定
2. 使用页面对象模型组织代码
3. 添加适当的注释和文档
4. 确保测试在所有浏览器中通过
5. 提交前运行完整的测试套件

---

如有问题或建议，请创建 Issue 或联系测试团队。