const { By, until } = require('selenium-webdriver')
const SeleniumConfig = require('./selenium.config')

/**
 * Selenium 基础测试类
 */
class BaseSeleniumTest {
  constructor () {
    this.config = new SeleniumConfig()
    this.driver = null
    this.currentBrowser = 'chrome'
    this.testResults = []
  }

  /**
   * 设置测试环境
   * @param {string} browserName 
   */
  async setup (browserName = 'chrome') {
    this.currentBrowser = browserName
    this.driver = await this.config.createDriver(browserName)
    console.log(`🚀 开始 ${browserName} 测试`)
  }

  /**
   * 清理测试环境
   */
  async teardown () {
    if (this.driver) {
      await this.config.closeDriver(this.driver)
    }
  }

  /**
   * 导航到指定页面
   * @param {string} path 
   */
  async navigateTo (path = '/') {
    const url = `${this.config.baseUrl}${path}`
    await this.driver.get(url)
    await this.config.waitForPageLoad(this.driver)
    console.log(`📍 导航到: ${url}`)
  }

  /**
   * 查找元素
   * @param {By} locator 
   * @param {number} timeout 
   * @returns {Promise<WebElement>}
   */
  async findElement (locator, timeout = 10000) {
    try {
      const element = await this.driver.wait(until.elementLocated(locator), timeout)
      await this.driver.wait(until.elementIsVisible(element), timeout)
      return element
    } catch (error) {
      console.error(`❌ 未找到元素: ${locator.toString()}`)
      throw error
    }
  }

  /**
   * 查找多个元素
   * @param {By} locator 
   * @param {number} timeout 
   * @returns {Promise<Array<WebElement>>}
   */
  async findElements (locator, timeout = 10000) {
    try {
      await this.driver.wait(until.elementsLocated(locator), timeout)
      return await this.driver.findElements(locator)
    } catch (error) {
      console.error(`❌ 未找到元素: ${locator.toString()}`)
      return []
    }
  }

  /**
   * 等待元素可见
   * @param {By} locator 
   * @param {number} timeout 
   */
  async waitForVisible (locator, timeout = 10000) {
    const element = await this.driver.wait(until.elementLocated(locator), timeout)
    await this.driver.wait(until.elementIsVisible(element), timeout)
    return element
  }

  /**
   * 等待元素可点击
   * @param {By} locator 
   * @param {number} timeout 
   */
  async waitForClickable (locator, timeout = 10000) {
    const element = await this.driver.wait(until.elementLocated(locator), timeout)
    await this.driver.wait(until.elementIsEnabled(element), timeout)
    return element
  }

  /**
   * 点击元素
   * @param {By} locator 
   */
  async click (locator) {
    const element = await this.waitForClickable(locator)
    await element.click()
    console.log(`👆 点击: ${locator.toString()}`)
  }

  /**
   * 输入文本
   * @param {By} locator 
   * @param {string} text 
   */
  async sendKeys (locator, text) {
    const element = await this.findElement(locator)
    await element.clear()
    await element.sendKeys(text)
    console.log(`⌨️ 输入文本: ${text}`)
  }

  /**
   * 获取元素文本
   * @param {By} locator 
   * @returns {Promise<string>}
   */
  async getText (locator) {
    const element = await this.findElement(locator)
    return await element.getText()
  }

  /**
   * 获取页面标题
   * @returns {Promise<string>}
   */
  async getTitle () {
    return await this.driver.getTitle()
  }

  /**
   * 获取当前URL
   * @returns {Promise<string>}
   */
  async getCurrentUrl () {
    return await this.driver.getCurrentUrl()
  }

  /**
   * 执行JavaScript
   * @param {string} script 
   * @param {...any} args 
   * @returns {Promise<any>}
   */
  async executeScript (script, ...args) {
    return await this.driver.executeScript(script, ...args)
  }

  /**
   * 检查元素是否存在
   * @param {By} locator 
   * @returns {Promise<boolean>}
   */
  async isElementPresent (locator) {
    try {
      await this.driver.findElement(locator)
      return true
    } catch (error) {
      return false
    }
  }

  /**
   * 检查元素是否可见
   * @param {By} locator 
   * @returns {Promise<boolean>}
   */
  async isElementVisible (locator) {
    try {
      const element = await this.driver.findElement(locator)
      return await element.isDisplayed()
    } catch (error) {
      return false
    }
  }

  /**
   * 等待一段时间
   * @param {number} ms 
   */
  async sleep (ms) {
    await this.driver.sleep(ms)
  }

  /**
   * 设置窗口大小
   * @param {number} width 
   * @param {number} height 
   */
  async setWindowSize (width, height) {
    await this.driver.manage().window().setRect({ width, height })
    console.log(`📱 设置窗口大小: ${width}x${height}`)
  }

  /**
   * 刷新页面
   */
  async refresh () {
    await this.driver.navigate().refresh()
    await this.config.waitForPageLoad(this.driver)
    console.log('🔄 页面已刷新')
  }

  /**
   * 记录测试结果
   * @param {string} testName 
   * @param {boolean} passed 
   * @param {string} message 
   */
  recordResult (testName, passed, message = '') {
    const result = {
      browser: this.currentBrowser,
      test: testName,
      passed,
      message,
      timestamp: new Date().toISOString(),
    }
    
    this.testResults.push(result)
    
    const status = passed ? '✅' : '❌'
    console.log(`${status} [${this.currentBrowser}] ${testName}: ${message}`)
  }

  /**
   * 断言
   * @param {boolean} condition 
   * @param {string} message 
   */
  assert (condition, message) {
    if (!condition) {
      throw new Error(`断言失败: ${message}`)
    }
  }

  /**
   * 断言元素存在
   * @param {By} locator 
   * @param {string} message 
   */
  async assertElementExists (locator, message) {
    const exists = await this.isElementPresent(locator)
    this.assert(exists, message || `元素应该存在: ${locator.toString()}`)
  }

  /**
   * 断言元素可见
   * @param {By} locator 
   * @param {string} message 
   */
  async assertElementVisible (locator, message) {
    const visible = await this.isElementVisible(locator)
    this.assert(visible, message || `元素应该可见: ${locator.toString()}`)
  }

  /**
   * 断言页面标题
   * @param {string} expectedTitle 
   */
  async assertTitle (expectedTitle) {
    const actualTitle = await this.getTitle()
    this.assert(
      actualTitle.includes(expectedTitle), 
      `页面标题应该包含 "${expectedTitle}"，实际为 "${actualTitle}"`,
    )
  }

  /**
   * 断言URL包含
   * @param {string} expectedPath 
   */
  async assertUrlContains (expectedPath) {
    const currentUrl = await this.getCurrentUrl()
    this.assert(
      currentUrl.includes(expectedPath), 
      `URL应该包含 "${expectedPath}"，实际为 "${currentUrl}"`,
    )
  }

  /**
   * 检查控制台错误
   */
  async checkConsoleErrors () {
    const errors = await this.config.getConsoleErrors(this.driver)
    if (errors.length > 0) {
      console.warn(`⚠️ 发现 ${errors.length} 个控制台错误:`)
      errors.forEach(error => {
        console.warn(`  - ${error.message}`)
      })
    }
    return errors
  }

  /**
   * 截图
   * @param {string} filename 
   */
  async screenshot (filename) {
    return await this.config.takeScreenshot(this.driver, filename)
  }

  /**
   * 获取测试结果摘要
   */
  getResultsSummary () {
    const total = this.testResults.length
    const passed = this.testResults.filter(r => r.passed).length
    const failed = total - passed

    return {
      total,
      passed,
      failed,
      passRate: total > 0 ? (passed / total * 100).toFixed(2) : 0,
      results: this.testResults,
    }
  }
}

module.exports = BaseSeleniumTest
