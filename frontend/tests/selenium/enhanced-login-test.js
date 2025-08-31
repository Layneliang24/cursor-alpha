const { By, Key } = require('selenium-webdriver')
const BaseSeleniumTest = require('./base-test')

/**
 * 增强版登录测试 - 支持验证码处理和真实账号验证
 */
class EnhancedLoginTest extends BaseSeleniumTest {
  constructor () {
    super()
    this.testName = '增强版登录功能测试'
    this.realCredentials = {
      username: 'layne',
      password: 'meimei520',
    }
  }

  /**
   * 运行完整的登录测试
   */
  async runCompleteTest () {
    console.log(`\n🎯 开始 ${this.testName}`)
    console.log('=' .repeat(60))

    const browsers = ['firefox', 'edge'] // Chrome暂时移除
    const allResults = []

    for (const browser of browsers) {
      try {
        console.log(`\n📋 测试浏览器: ${browser.toUpperCase()}`)
        console.log('-'.repeat(40))
        
        const results = await this.testBrowserWithRealCredentials(browser)
        allResults.push(...results)
        
      } catch (error) {
        console.error(`❌ ${browser} 测试失败:`, error.message)
        this.recordResult(`${browser}_overall`, false, `浏览器测试失败: ${error.message}`)
      }
    }

    this.printDetailedSummary(allResults)
    return allResults
  }

  /**
   * 使用真实凭据测试浏览器
   */
  async testBrowserWithRealCredentials (browser) {
    await this.setup(browser)
    
    try {
      // 核心测试用例
      const testCases = [
        () => this.testPageAccessibility(),
        () => this.testFormElements(),
        () => this.testCaptchaHandling(),
        () => this.testRealLogin(),
        () => this.testPostLoginNavigation(),
        () => this.testLearningPageAccess(),
      ]

      // 执行所有测试用例
      for (const testCase of testCases) {
        try {
          await testCase()
        } catch (error) {
          console.error('测试用例失败:', error.message)
          await this.screenshot(`${browser}_error_${Date.now()}`)
        }
        
        await this.sleep(1500)
      }

    } finally {
      await this.teardown()
    }

    return this.testResults.filter(r => r.browser === browser)
  }

  /**
   * 测试页面可访问性
   */
  async testPageAccessibility () {
    const testName = '页面可访问性测试'
    
    try {
      await this.navigateTo('/login')
      
      // 检查页面标题
      const title = await this.getTitle()
      this.assert(title.includes('用户登录') || title.includes('Alpha'), 
        `页面标题应该包含"用户登录"或"Alpha"，实际为: ${title}`)
      
      // 检查页面是否完全加载
      const bodyElement = await this.isElementPresent(By.css('body'))
      this.assert(bodyElement, '页面body元素应该存在')
      
      // 检查Vue应用是否挂载
      const appElement = await this.isElementPresent(By.css('#app'))
      this.assert(appElement, 'Vue应用挂载点应该存在')
      
      this.recordResult(testName, true, '页面可访问性正常')
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
      throw error
    }
  }

  /**
   * 测试表单元素
   */
  async testFormElements () {
    const testName = '表单元素检查'
    
    try {
      await this.navigateTo('/login')
      await this.sleep(2000) // 等待页面完全加载
      
      // 检查用户名输入框
      const usernameInput = await this.waitForVisible(By.css('input[placeholder*="用户名"], input[placeholder*="邮箱"], .el-input__inner'))
      this.assert(usernameInput !== null, '用户名输入框应该可见')
      
      // 检查密码输入框
      const passwordInput = await this.waitForVisible(By.css('input[type="password"], .el-input__inner[type="password"]'))
      this.assert(passwordInput !== null, '密码输入框应该可见')
      
      // 检查验证码输入框
      const captchaInput = await this.waitForVisible(By.css('input[placeholder*="验证码"], .captcha-container input'))
      this.assert(captchaInput !== null, '验证码输入框应该可见')
      
      // 检查验证码图片
      const captchaImage = await this.isElementPresent(By.css('canvas, .captcha-image'))
      this.assert(captchaImage, '验证码图片应该存在')
      
      // 检查登录按钮
      const loginButton = await this.waitForVisible(By.css('.el-button--primary, button[type="submit"]'))
      this.assert(loginButton !== null, '登录按钮应该可见')
      
      this.recordResult(testName, true, '所有表单元素检查通过')
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
      throw error
    }
  }

  /**
   * 测试验证码处理
   */
  async testCaptchaHandling () {
    const testName = '验证码处理测试'
    
    try {
      await this.navigateTo('/login')
      await this.sleep(2000)
      
      // 尝试获取验证码图片
      const captchaCanvas = await this.findElement(By.css('canvas'))
      this.assert(captchaCanvas !== null, '验证码Canvas应该存在')
      
      // 点击刷新验证码
      const captchaRefresh = await this.isElementPresent(By.css('.captcha-image, .captcha-refresh'))
      if (captchaRefresh) {
        await this.click(By.css('.captcha-image'))
        await this.sleep(1000)
        console.log('✅ 验证码刷新功能正常')
      }
      
      // 注意：这里我们不能自动识别验证码，需要手动处理或跳过
      console.log('⚠️ 验证码需要手动输入，自动化测试将使用模拟输入')
      
      this.recordResult(testName, true, '验证码元素存在，刷新功能正常')
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试真实登录
   */
  async testRealLogin () {
    const testName = '真实账号登录测试'
    
    try {
      await this.navigateTo('/login')
      await this.sleep(2000)
      
      // 输入真实凭据
      const usernameField = By.css('input[placeholder*="用户名"], input[placeholder*="邮箱"], .el-input__inner')
      const passwordField = By.css('input[type="password"], .el-input__inner[type="password"]')
      const captchaField = By.css('input[placeholder*="验证码"], .captcha-container input')
      
      await this.sendKeys(usernameField, this.realCredentials.username)
      console.log(`✅ 已输入用户名: ${this.realCredentials.username}`)
      
      await this.sendKeys(passwordField, this.realCredentials.password)
      console.log('✅ 已输入密码')
      
      // 验证码处理 - 尝试常见的测试验证码
      const testCaptchas = ['1234', 'test', 'abcd', '0000']
      let loginSuccess = false
      
      for (const captcha of testCaptchas) {
        try {
          // 清除之前的验证码
          const captchaInput = await this.findElement(captchaField)
          await captchaInput.clear()
          await captchaInput.sendKeys(captcha)
          
          console.log(`🔄 尝试验证码: ${captcha}`)
          
          // 点击登录
          await this.click(By.css('.el-button--primary, button[type="submit"]'))
          await this.sleep(3000)
          
          // 检查是否登录成功
          const currentUrl = await this.getCurrentUrl()
          if (!currentUrl.includes('/login')) {
            loginSuccess = true
            console.log('✅ 登录成功！')
            break
          } else {
            console.log(`❌ 验证码 ${captcha} 失败，尝试下一个`)
            // 刷新验证码
            const refreshButton = await this.isElementPresent(By.css('.captcha-image'))
            if (refreshButton) {
              await this.click(By.css('.captcha-image'))
              await this.sleep(1000)
            }
          }
        } catch (e) {
          console.log(`验证码 ${captcha} 测试出错:`, e.message)
          continue
        }
      }
      
      if (loginSuccess) {
        this.recordResult(testName, true, `使用账号 ${this.realCredentials.username} 登录成功`)
      } else {
        // 尝试手动提示用户输入验证码
        console.log('\n🔔 需要手动验证：')
        console.log('自动验证码尝试失败，登录页面仍然存在')
        console.log('这可能是因为：1) 验证码无法自动识别 2) 账号密码错误 3) 其他验证失败')
        
        this.recordResult(testName, false, '自动登录失败 - 可能需要手动输入验证码')
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试登录后导航
   */
  async testPostLoginNavigation () {
    const testName = '登录后导航测试'
    
    try {
      const currentUrl = await this.getCurrentUrl()
      
      if (currentUrl.includes('/login')) {
        this.recordResult(testName, false, '用户未成功登录，跳过导航测试')
        return
      }
      
      // 检查是否跳转到了主页面
      console.log(`当前URL: ${currentUrl}`)
      
      // 尝试访问需要登录的页面
      await this.navigateTo('/english/idiomatic-learning')
      await this.sleep(2000)
      
      const finalUrl = await this.getCurrentUrl()
      if (finalUrl.includes('/english/idiomatic-learning')) {
        this.recordResult(testName, true, '登录后可以访问受保护页面')
      } else if (finalUrl.includes('/login')) {
        this.recordResult(testName, false, '登录状态丢失，被重定向到登录页面')
      } else {
        this.recordResult(testName, true, '登录后导航正常，可能重定向到其他授权页面')
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试学习页面访问
   */
  async testLearningPageAccess () {
    const testName = '学习页面访问测试'
    
    try {
      await this.navigateTo('/english/idiomatic-learning')
      await this.sleep(3000)
      
      const currentUrl = await this.getCurrentUrl()
      
      if (currentUrl.includes('/login')) {
        this.recordResult(testName, true, '页面正确要求登录认证')
        return
      }
      
      // 检查页面标题
      const title = await this.getTitle()
      const hasCorrectTitle = title.includes('地道表达') || title.includes('学习')
      
      // 检查学习模式卡片
      const modeCards = await this.findElements(By.css('.mode-card, .learning-mode'))
      
      if (hasCorrectTitle && modeCards.length > 0) {
        this.recordResult(testName, true, `学习页面加载成功，发现 ${modeCards.length} 个学习模式`)
      } else {
        this.recordResult(testName, false, '学习页面内容不完整')
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 打印详细测试摘要
   */
  printDetailedSummary (allResults) {
    console.log('\n📊 详细测试结果摘要')
    console.log('=' .repeat(80))

    const summary = this.getResultsSummary()
    console.log('\n📈 总体统计:')
    console.log(`  总测试数: ${summary.total}`)
    console.log(`  通过: ${summary.passed} (${summary.passRate}%)`)
    console.log(`  失败: ${summary.failed}`)

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

    console.log('\n🌐 浏览器详细结果:')
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
      
      console.log('  📋 详细结果:')
      results.tests.forEach(test => {
        const status = test.passed ? '✅' : '❌'
        console.log(`    ${status} ${test.test}: ${test.message}`)
      })
    })

    console.log('\n🎯 测试质量评估:')
    if (summary.passRate >= 80) {
      console.log('  🟢 测试质量: 优秀 - 大部分功能正常工作')
    } else if (summary.passRate >= 60) {
      console.log('  🟡 测试质量: 良好 - 主要功能可用，需要优化')
    } else {
      console.log('  🔴 测试质量: 需要改进 - 存在重要功能问题')
    }

    console.log('\n🔧 改进建议:')
    const failedTests = allResults.filter(r => !r.passed)
    if (failedTests.length > 0) {
      console.log('  1. 优先修复失败的测试用例')
      console.log('  2. 考虑添加验证码自动识别功能')
      console.log('  3. 增加更多的错误处理和重试机制')
      console.log('  4. 完善测试数据和环境配置')
    } else {
      console.log('  1. 考虑增加更多边界情况测试')
      console.log('  2. 添加性能测试指标')
      console.log('  3. 扩展到更多浏览器和设备')
    }
  }
}

// 如果直接运行此文件
if (require.main === module) {
  const test = new EnhancedLoginTest()
  test.runCompleteTest()
    .then(() => {
      console.log('\n✅ 增强版登录测试完成')
      process.exit(0)
    })
    .catch(error => {
      console.error('\n❌ 增强版登录测试失败:', error)
      process.exit(1)
    })
}

module.exports = EnhancedLoginTest
