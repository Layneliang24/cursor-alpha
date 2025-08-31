const { By } = require('selenium-webdriver')
const BaseSeleniumTest = require('./base-test')

/**
 * 跨浏览器登录功能测试
 */
class CrossBrowserLoginTest extends BaseSeleniumTest {
  constructor () {
    super()
    this.testName = '跨浏览器登录功能测试'
  }

  /**
   * 运行所有浏览器测试
   */
  async runAllBrowsers () {
    console.log(`\n🎯 开始 ${this.testName}`)
    console.log('=' .repeat(60))

    const browsers = ['chrome', 'firefox', 'edge']
    const allResults = []

    for (const browser of browsers) {
      try {
        console.log(`\n📋 测试浏览器: ${browser.toUpperCase()}`)
        console.log('-'.repeat(40))
        
        const results = await this.testBrowser(browser)
        allResults.push(...results)
        
      } catch (error) {
        console.error(`❌ ${browser} 测试失败:`, error.message)
        this.recordResult(`${browser}_overall`, false, `浏览器测试失败: ${error.message}`)
      }
    }

    this.printSummary(allResults)
    return allResults
  }

  /**
   * 测试单个浏览器
   * @param {string} browser 
   */
  async testBrowser (browser) {
    await this.setup(browser)
    
    try {
      // 测试用例列表
      const testCases = [
        () => this.testLoginPageElements(),
        () => this.testValidLogin(),
        () => this.testInvalidLogin(),
        () => this.testEmptyFields(),
        () => this.testResponsiveDesign(),
        () => this.testJavaScriptErrors(),
        () => this.testNavigationAfterLogin(),
      ]

      // 执行所有测试用例
      for (const testCase of testCases) {
        try {
          await testCase()
        } catch (error) {
          console.error('测试用例失败:', error.message)
          await this.screenshot(`${browser}_error_${Date.now()}`)
        }
        
        // 每个测试用例之间稍作停顿
        await this.sleep(1000)
      }

    } finally {
      await this.teardown()
    }

    return this.testResults.filter(r => r.browser === browser)
  }

  /**
   * 测试登录页面元素
   */
  async testLoginPageElements () {
    const testName = '登录页面元素检查'
    
    try {
      await this.navigateTo('/login')
      
      // 检查页面标题
      await this.assertTitle('用户登录')
      
      // 检查必要的表单元素
      await this.assertElementVisible(By.css('input[type="text"], .el-input__inner'), '用户名输入框应该可见')
      await this.assertElementVisible(By.css('input[type="password"], .el-input__inner[type="password"]'), '密码输入框应该可见')
      await this.assertElementVisible(By.css('.el-button--primary, button[type="submit"]'), '登录按钮应该可见')
      
      // 检查是否有记住我选项
      const rememberCheckbox = await this.isElementPresent(By.css('input[type="checkbox"]'))
      if (rememberCheckbox) {
        console.log('✅ 发现"记住我"选项')
      }

      this.recordResult(testName, true, '所有登录页面元素正常显示')
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
      throw error
    }
  }

  /**
   * 测试有效登录
   */
  async testValidLogin () {
    const testName = '有效登录测试'
    
    try {
      await this.navigateTo('/login')
      
      // 输入有效凭据（使用真实测试账号）
      const usernameField = By.css('input[type="text"], .el-input__inner')
      const passwordField = By.css('input[type="password"], .el-input__inner[type="password"]')
      const loginButton = By.css('.el-button--primary, button[type="submit"]')
      
      await this.sendKeys(usernameField, 'layne')
      await this.sendKeys(passwordField, 'meimei520')
      await this.click(loginButton)
      
      // 等待页面响应
      await this.sleep(3000)
      
      // 检查是否成功登录（这里检查URL变化或页面元素）
      const currentUrl = await this.getCurrentUrl()
      const isStillOnLogin = currentUrl.includes('/login')
      
      if (!isStillOnLogin) {
        this.recordResult(testName, true, '登录成功，已跳转到主页面')
      } else {
        // 检查是否有错误消息
        const hasError = await this.isElementPresent(By.css('.error, .el-message--error'))
        if (hasError) {
          const errorText = await this.getText(By.css('.error, .el-message--error'))
          this.recordResult(testName, false, `登录失败: ${errorText}`)
        } else {
          this.recordResult(testName, false, '登录后仍在登录页面，但无错误消息')
        }
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试无效登录
   */
  async testInvalidLogin () {
    const testName = '无效登录测试'
    
    try {
      await this.navigateTo('/login')
      
      const usernameField = By.css('input[type="text"], .el-input__inner')
      const passwordField = By.css('input[type="password"], .el-input__inner[type="password"]')
      const loginButton = By.css('.el-button--primary, button[type="submit"]')
      
      // 输入无效凭据
      await this.sendKeys(usernameField, 'wrong@example.com')
      await this.sendKeys(passwordField, 'wrongpassword')
      await this.click(loginButton)
      
      // 等待响应
      await this.sleep(3000)
      
      // 应该仍在登录页面
      const currentUrl = await this.getCurrentUrl()
      const stillOnLogin = currentUrl.includes('/login')
      
      if (stillOnLogin) {
        // 检查是否有错误消息
        const hasError = await this.isElementPresent(By.css('.error, .el-message--error, [class*="error"]'))
        if (hasError) {
          this.recordResult(testName, true, '无效登录正确显示错误消息')
        } else {
          this.recordResult(testName, true, '无效登录保持在登录页面（无明显错误消息）')
        }
      } else {
        this.recordResult(testName, false, '无效登录意外跳转到其他页面')
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试空字段验证
   */
  async testEmptyFields () {
    const testName = '空字段验证测试'
    
    try {
      await this.navigateTo('/login')
      
      const loginButton = By.css('.el-button--primary, button[type="submit"]')
      
      // 直接点击登录按钮（不输入任何信息）
      await this.click(loginButton)
      
      // 等待验证消息
      await this.sleep(2000)
      
      // 检查是否有验证错误
      const hasValidationError = await this.isElementPresent(By.css('.el-form-item__error, .error, [class*="error"]'))
      
      if (hasValidationError) {
        this.recordResult(testName, true, '空字段验证正常工作')
      } else {
        // 检查是否仍在登录页面
        const currentUrl = await this.getCurrentUrl()
        const stillOnLogin = currentUrl.includes('/login')
        
        if (stillOnLogin) {
          this.recordResult(testName, true, '空字段提交后保持在登录页面')
        } else {
          this.recordResult(testName, false, '空字段验证失败，意外跳转')
        }
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试响应式设计
   */
  async testResponsiveDesign () {
    const testName = '响应式设计测试'
    
    try {
      await this.navigateTo('/login')
      
      const viewports = [
        { width: 1920, height: 1080, name: 'Desktop' },
        { width: 768, height: 1024, name: 'Tablet' },
        { width: 375, height: 667, name: 'Mobile' },
      ]

      let allViewportsWork = true
      const results = []

      for (const viewport of viewports) {
        await this.setWindowSize(viewport.width, viewport.height)
        await this.sleep(1000)

        // 检查关键元素是否仍然可见
        const usernameVisible = await this.isElementVisible(By.css('input[type="text"], .el-input__inner'))
        const passwordVisible = await this.isElementVisible(By.css('input[type="password"], .el-input__inner[type="password"]'))
        const buttonVisible = await this.isElementVisible(By.css('.el-button--primary, button[type="submit"]'))

        const viewportWorks = usernameVisible && passwordVisible && buttonVisible
        results.push(`${viewport.name}: ${viewportWorks ? '✅' : '❌'}`)
        
        if (!viewportWorks) {
          allViewportsWork = false
        }
      }

      // 恢复默认窗口大小
      await this.setWindowSize(1920, 1080)

      this.recordResult(testName, allViewportsWork, results.join(', '))
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试JavaScript错误
   */
  async testJavaScriptErrors () {
    const testName = 'JavaScript错误检查'
    
    try {
      await this.navigateTo('/login')
      
      // 与页面交互
      const usernameField = By.css('input[type="text"], .el-input__inner')
      const passwordField = By.css('input[type="password"], .el-input__inner[type="password"]')
      
      await this.sendKeys(usernameField, 'test@example.com')
      await this.sendKeys(passwordField, 'password')
      
      // 等待一段时间让JavaScript执行
      await this.sleep(2000)
      
      // 检查控制台错误
      const errors = await this.checkConsoleErrors()
      
      if (errors.length === 0) {
        this.recordResult(testName, true, '无JavaScript错误')
      } else {
        this.recordResult(testName, false, `发现 ${errors.length} 个JavaScript错误`)
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试登录后导航
   */
  async testNavigationAfterLogin () {
    const testName = '登录后导航测试'
    
    try {
      await this.navigateTo('/login')
      
      // 尝试登录
      const usernameField = By.css('input[type="text"], .el-input__inner')
      const passwordField = By.css('input[type="password"], .el-input__inner[type="password"]')
      const loginButton = By.css('.el-button--primary, button[type="submit"]')
      
      await this.sendKeys(usernameField, 'layne')
      await this.sendKeys(passwordField, 'meimei520')
      await this.click(loginButton)
      
      // 等待跳转
      await this.sleep(3000)
      
      const currentUrl = await this.getCurrentUrl()
      
      if (!currentUrl.includes('/login')) {
        // 尝试访问需要认证的页面
        await this.navigateTo('/english/idiomatic-learning')
        await this.sleep(2000)
        
        const finalUrl = await this.getCurrentUrl()
        
        if (finalUrl.includes('/english/idiomatic-learning')) {
          this.recordResult(testName, true, '登录后可以访问受保护页面')
        } else if (finalUrl.includes('/login')) {
          this.recordResult(testName, false, '登录后仍被重定向到登录页面')
        } else {
          this.recordResult(testName, true, '登录后导航正常（可能重定向到其他授权页面）')
        }
      } else {
        this.recordResult(testName, false, '登录未成功，无法测试导航')
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 打印测试摘要
   */
  printSummary (allResults) {
    console.log('\n📊 测试结果摘要')
    console.log('=' .repeat(60))

    const summary = this.getResultsSummary()
    console.log(`总测试数: ${summary.total}`)
    console.log(`通过: ${summary.passed} (${summary.passRate}%)`)
    console.log(`失败: ${summary.failed}`)

    // 按浏览器分组显示结果
    const browserResults = {}
    allResults.forEach(result => {
      if (!browserResults[result.browser]) {
        browserResults[result.browser] = { passed: 0, failed: 0, tests: [] }
      }
      
      if (result.passed) {
        browserResults[result.browser].passed++
      } else {
        browserResults[result.browser].failed++
      }
      
      browserResults[result.browser].tests.push(result)
    })

    console.log('\n📋 各浏览器测试结果:')
    Object.keys(browserResults).forEach(browser => {
      const results = browserResults[browser]
      const total = results.passed + results.failed
      const rate = total > 0 ? (results.passed / total * 100).toFixed(1) : 0
      
      console.log(`\n${browser.toUpperCase()}:`)
      console.log(`  ✅ 通过: ${results.passed}/${total} (${rate}%)`)
      
      if (results.failed > 0) {
        console.log('  ❌ 失败的测试:')
        results.tests.filter(t => !t.passed).forEach(test => {
          console.log(`    - ${test.test}: ${test.message}`)
        })
      }
    })

    console.log('\n🎯 测试完成!')
  }
}

// 如果直接运行此文件
if (require.main === module) {
  const test = new CrossBrowserLoginTest()
  test.runAllBrowsers()
    .then(() => {
      console.log('所有测试完成')
      process.exit(0)
    })
    .catch(error => {
      console.error('测试运行失败:', error)
      process.exit(1)
    })
}

module.exports = CrossBrowserLoginTest
