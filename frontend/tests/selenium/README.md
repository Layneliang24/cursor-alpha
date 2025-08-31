# Selenium 跨浏览器测试

这个目录包含使用 Selenium WebDriver 进行跨浏览器兼容性测试的测试套件。

## 🎯 测试目标

- **跨浏览器兼容性**: 在 Chrome、Firefox、Edge 等主流浏览器中验证功能
- **真实用户场景**: 模拟用户的实际操作流程
- **JavaScript错误检测**: 捕获和报告浏览器控制台错误
- **响应式设计验证**: 测试不同屏幕尺寸下的显示效果

## 📁 文件结构

```
tests/selenium/
├── README.md                      # 本文档
├── selenium.config.js             # Selenium配置类
├── base-test.js                   # 基础测试类
├── cross-browser-login.test.js    # 登录功能跨浏览器测试
├── cross-browser-learning.test.js # 学习功能跨浏览器测试
└── run-all-tests.js              # 测试套件运行器
```

## 🚀 运行测试

### 前置条件

1. **安装浏览器驱动**:
   ```bash
   # Chrome
   npm install chromedriver --save-dev
   
   # Firefox  
   npm install geckodriver --save-dev
   
   # Edge
   npm install edgedriver --save-dev
   ```

2. **确保前端服务运行**:
   ```bash
   npm run dev  # 确保服务运行在 http://localhost:3000
   ```

### 运行命令

```bash
# 运行所有Selenium测试
npm run test:selenium

# 仅运行登录功能测试
npm run test:selenium:login

# 仅运行学习功能测试  
npm run test:selenium:learning

# 跨浏览器测试（别名）
npm run test:cross-browser
```

### 环境变量配置

可以通过环境变量自定义测试行为：

```bash
# 设置基础URL
BASE_URL=http://localhost:3000

# 设置超时时间（毫秒）
SELENIUM_TIMEOUT=30000

# 启用有头模式（显示浏览器窗口）
HEADLESS=false
```

示例：
```bash
BASE_URL=http://localhost:5000 HEADLESS=false npm run test:selenium
```

## 📊 测试报告

测试完成后会生成详细的报告：

### 控制台输出
- 实时测试进度
- 各浏览器测试结果
- 失败测试详情
- 总体统计信息

### 报告文件
报告保存在 `test-results/selenium-reports/` 目录：

- `selenium-test-report-[timestamp].json` - JSON格式详细报告
- `selenium-test-report-[timestamp].html` - HTML格式可视化报告
- `selenium-screenshots/` - 失败测试的截图

## 🧪 测试覆盖范围

### 登录功能测试
- ✅ 登录页面元素检查
- ✅ 有效登录测试
- ✅ 无效登录测试
- ✅ 空字段验证测试
- ✅ 响应式设计测试
- ✅ JavaScript错误检查
- ✅ 登录后导航测试

### 学习功能测试
- ✅ 学习页面加载测试
- ✅ 学习模式选择测试
- ✅ 闪卡学习模式测试
- ✅ AI对话模式测试
- ✅ 分析页面导航测试
- ✅ 响应式设计测试
- ✅ JavaScript错误检查

### 支持的浏览器
- 🌐 Google Chrome
- 🦊 Mozilla Firefox  
- 🔷 Microsoft Edge

### 测试屏幕尺寸
- 💻 Desktop: 1920x1080
- 📱 Tablet: 768x1024
- 📱 Mobile: 375x667

## 🔧 自定义测试

### 添加新的测试用例

1. **继承基础测试类**:
```javascript
const BaseSeleniumTest = require('./base-test');

class MyCustomTest extends BaseSeleniumTest {
  async testMyFeature() {
    const testName = '我的功能测试';
    try {
      await this.navigateTo('/my-page');
      await this.assertElementExists(By.css('.my-element'));
      this.recordResult(testName, true, '功能正常');
    } catch (error) {
      this.recordResult(testName, false, error.message);
    }
  }
}
```

2. **添加到测试套件**:
在 `run-all-tests.js` 中引入并运行你的测试类。

### 配置新的浏览器

在 `selenium.config.js` 中添加新的浏览器配置：

```javascript
async createSafariDriver() {
  return new Builder()
    .forBrowser('safari')
    .build();
}
```

## 📝 最佳实践

### 元素定位
- 优先使用 CSS 选择器
- 避免使用 XPath（除非必要）
- 使用语义化的选择器

### 等待策略
- 使用显式等待而不是固定延时
- 等待元素可见而不是仅仅存在
- 设置合理的超时时间

### 错误处理
- 每个测试用例都要有 try-catch
- 失败时截图保存现场
- 记录详细的错误信息

### 测试数据
- 使用专门的测试账号
- 避免依赖生产数据
- 每个测试保持独立性

## 🐛 故障排除

### 常见问题

**1. 浏览器驱动未找到**
```bash
Error: ChromeDriver not found
```
解决：安装对应的浏览器驱动
```bash
npm install chromedriver --save-dev
```

**2. 元素未找到**
```bash
NoSuchElementError: Unable to locate element
```
解决：
- 检查元素选择器是否正确
- 增加等待时间
- 确认页面已完全加载

**3. 端口占用**
```bash
Error: connect ECONNREFUSED 127.0.0.1:3000
```
解决：确保前端开发服务器正在运行
```bash
npm run dev
```

**4. 权限问题（Linux/Mac）**
```bash
Permission denied
```
解决：给予执行权限
```bash
chmod +x node_modules/.bin/chromedriver
```

### 调试技巧

1. **启用有头模式**:
   ```bash
   HEADLESS=false npm run test:selenium
   ```

2. **增加等待时间**:
   ```bash
   SELENIUM_TIMEOUT=60000 npm run test:selenium
   ```

3. **查看截图**:
   失败的测试会自动截图，查看 `test-results/selenium-screenshots/`

4. **查看详细日志**:
   测试过程中会输出详细的操作日志

## 🔗 相关链接

- [Selenium WebDriver 文档](https://selenium-webdriver.js.org/)
- [Playwright vs Selenium 对比](https://playwright.dev/docs/why-playwright)
- [Element Plus 组件库](https://element-plus.org/)
- [Vue.js 测试指南](https://vuejs.org/guide/scaling-up/testing.html)
