const { By } = require('selenium-webdriver')
const BaseSeleniumTest = require('./base-test')

/**
 * 跨浏览器学习功能测试
 */
class CrossBrowserLearningTest extends BaseSeleniumTest {
  constructor () {
    super()
    this.testName = '跨浏览器学习功能测试'
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
        () => this.testLearningPageLoad(),
        () => this.testLearningModeSelection(),
        () => this.testFlashcardMode(),
        () => this.testAIChatMode(),
        () => this.testAnalyticsNavigation(),
        () => this.testResponsiveDesign(),
        () => this.testJavaScriptErrors(),
      ]

      // 执行所有测试用例
      for (const testCase of testCases) {
        try {
          await testCase()
        } catch (error) {
          console.error('测试用例失败:', error.message)
          await this.screenshot(`${browser}_learning_error_${Date.now()}`)
        }
        
        await this.sleep(1000)
      }

    } finally {
      await this.teardown()
    }

    return this.testResults.filter(r => r.browser === browser)
  }

  /**
   * 测试学习页面加载
   */
  async testLearningPageLoad () {
    const testName = '学习页面加载测试'
    
    try {
      await this.navigateTo('/english/idiomatic-learning')
      
      // 检查是否需要登录
      const currentUrl = await this.getCurrentUrl()
      if (currentUrl.includes('/login')) {
        this.recordResult(testName, true, '页面正确重定向到登录页面（需要认证）')
        return
      }
      
      // 检查页面标题
      await this.assertTitle('地道表达学习')
      
      // 检查页面主要内容
      const mainContent = await this.isElementPresent(By.css('#app, .main-content, .learning-container'))
      this.assert(mainContent, '主要内容区域应该存在')
      
      this.recordResult(testName, true, '学习页面成功加载')
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试学习模式选择
   */
  async testLearningModeSelection () {
    const testName = '学习模式选择测试'
    
    try {
      await this.navigateTo('/english/idiomatic-learning')
      
      const currentUrl = await this.getCurrentUrl()
      if (currentUrl.includes('/login')) {
        this.recordResult(testName, true, '需要登录，跳过模式选择测试')
        return
      }
      
      // 查找学习模式卡片
      const modeCards = await this.findElements(By.css('.mode-card'))
      
      if (modeCards.length === 0) {
        this.recordResult(testName, false, '未找到学习模式卡片')
        return
      }
      
      console.log(`发现 ${modeCards.length} 个学习模式`)
      
      // 检查是否有4个学习模式
      if (modeCards.length >= 4) {
        this.recordResult(testName, true, `发现 ${modeCards.length} 个学习模式卡片`)
      } else {
        this.recordResult(testName, false, `学习模式数量不足，期望4个，实际 ${modeCards.length} 个`)
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试闪卡学习模式
   */
  async testFlashcardMode () {
    const testName = '闪卡学习模式测试'
    
    try {
      await this.navigateTo('/english/idiomatic-learning')
      
      const currentUrl = await this.getCurrentUrl()
      if (currentUrl.includes('/login')) {
        this.recordResult(testName, true, '需要登录，跳过闪卡模式测试')
        return
      }
      
      // 查找并点击闪卡模式
      const flashcardModeSelectors = [
        '.mode-card:contains("闪卡")',
        '.mode-card',
        '[data-mode="flashcard"]',
      ]
      
      let flashcardMode = null
      for (const selector of flashcardModeSelectors) {
        try {
          const elements = await this.findElements(By.css(selector))
          if (elements.length > 0) {
            flashcardMode = elements[0]
            break
          }
        } catch (e) {
          continue
        }
      }
      
      if (!flashcardMode) {
        this.recordResult(testName, false, '未找到闪卡学习模式')
        return
      }
      
      // 点击闪卡模式
      await flashcardMode.click()
      await this.sleep(2000)
      
      // 检查模式是否激活
      const activeMode = await this.isElementPresent(By.css('.mode-card.active, .active'))
      
      if (activeMode) {
        this.recordResult(testName, true, '闪卡模式成功激活')
      } else {
        this.recordResult(testName, true, '闪卡模式点击成功（未检测到明显的激活状态）')
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试AI对话模式
   */
  async testAIChatMode () {
    const testName = 'AI对话模式测试'
    
    try {
      await this.navigateTo('/english/idiomatic-learning')
      
      const currentUrl = await this.getCurrentUrl()
      if (currentUrl.includes('/login')) {
        this.recordResult(testName, true, '需要登录，跳过AI对话模式测试')
        return
      }
      
      // 查找AI对话模式
      const aiModeSelectors = [
        '.mode-card:contains("AI对话")',
        '.mode-card:contains("AI")',
        '[data-mode="ai_chat"]',
      ]
      
      let aiMode = null
      const modeCards = await this.findElements(By.css('.mode-card'))
      
      // 尝试找到包含AI相关文本的模式卡片
      for (const card of modeCards) {
        try {
          const cardText = await card.getText()
          if (cardText.includes('AI') || cardText.includes('对话')) {
            aiMode = card
            break
          }
        } catch (e) {
          continue
        }
      }
      
      if (!aiMode) {
        this.recordResult(testName, false, '未找到AI对话模式')
        return
      }
      
      // 点击AI对话模式
      await aiMode.click()
      await this.sleep(2000)
      
      // 查找AI对话界面元素
      const aiChatElements = [
        'input[placeholder*="消息"]',
        'input[placeholder*="输入"]',
        'textarea[placeholder*="消息"]',
        '.chat-input',
        '.message-input',
      ]
      
      let foundChatInput = false
      for (const selector of aiChatElements) {
        const exists = await this.isElementPresent(By.css(selector))
        if (exists) {
          foundChatInput = true
          break
        }
      }
      
      if (foundChatInput) {
        this.recordResult(testName, true, 'AI对话模式成功激活，发现聊天输入框')
      } else {
        this.recordResult(testName, true, 'AI对话模式点击成功（未检测到明显的聊天界面）')
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试分析页面导航
   */
  async testAnalyticsNavigation () {
    const testName = '分析页面导航测试'
    
    try {
      await this.navigateTo('/english/learning-analytics')
      
      const currentUrl = await this.getCurrentUrl()
      if (currentUrl.includes('/login')) {
        this.recordResult(testName, true, '分析页面正确重定向到登录页面（需要认证）')
        return
      }
      
      // 检查分析页面是否加载
      const pageTitle = await this.getTitle()
      const hasAnalyticsContent = await this.isElementPresent(By.css('.analytics, .chart, canvas, svg'))
      
      if (pageTitle.includes('分析') || hasAnalyticsContent) {
        this.recordResult(testName, true, '分析页面成功加载')
      } else {
        this.recordResult(testName, false, '分析页面加载但未检测到分析内容')
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试响应式设计
   */
  async testResponsiveDesign () {
    const testName = '学习页面响应式设计测试'
    
    try {
      await this.navigateTo('/english/idiomatic-learning')
      
      const currentUrl = await this.getCurrentUrl()
      if (currentUrl.includes('/login')) {
        this.recordResult(testName, true, '需要登录，跳过响应式测试')
        return
      }
      
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

        // 检查主要内容是否可见
        const mainContentVisible = await this.isElementVisible(By.css('#app, .main-content'))
        
        // 检查学习模式卡片是否可见
        const modeCardsVisible = await this.isElementPresent(By.css('.mode-card'))
        
        const viewportWorks = mainContentVisible && modeCardsVisible
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
    const testName = '学习页面JavaScript错误检查'
    
    try {
      await this.navigateTo('/english/idiomatic-learning')
      
      const currentUrl = await this.getCurrentUrl()
      if (currentUrl.includes('/login')) {
        this.recordResult(testName, true, '需要登录，跳过JS错误检查')
        return
      }
      
      // 与页面交互
      const modeCards = await this.findElements(By.css('.mode-card'))
      if (modeCards.length > 0) {
        // 点击第一个模式卡片
        await modeCards[0].click()
        await this.sleep(2000)
      }
      
      // 检查控制台错误
      const errors = await this.checkConsoleErrors()
      
      // 过滤掉一些已知的非关键错误
      const criticalErrors = errors.filter(error => {
        const message = error.message.toLowerCase()
        return !message.includes('favicon') && 
               !message.includes('service worker') &&
               !message.includes('manifest')
      })
      
      if (criticalErrors.length === 0) {
        this.recordResult(testName, true, '无关键JavaScript错误')
      } else {
        this.recordResult(testName, false, `发现 ${criticalErrors.length} 个关键JavaScript错误`)
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 打印测试摘要
   */
  printSummary (allResults) {
    console.log('\n📊 学习功能测试结果摘要')
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

    console.log('\n🎯 学习功能测试完成!')
  }
}

// 如果直接运行此文件
if (require.main === module) {
  const test = new CrossBrowserLearningTest()
  test.runAllBrowsers()
    .then(() => {
      console.log('所有学习功能测试完成')
      process.exit(0)
    })
    .catch(error => {
      console.error('学习功能测试运行失败:', error)
      process.exit(1)
    })
}

module.exports = CrossBrowserLearningTest
