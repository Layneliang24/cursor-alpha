const { Builder } = require('selenium-webdriver')
const chrome = require('selenium-webdriver/chrome')
const firefox = require('selenium-webdriver/firefox')
const edge = require('selenium-webdriver/edge')

/**
 * Selenium 测试配置
 */
class SeleniumConfig {
  constructor () {
    this.baseUrl = process.env.BASE_URL || 'http://localhost:3000'
    this.timeout = parseInt(process.env.SELENIUM_TIMEOUT) || 30000
    this.headless = process.env.HEADLESS !== 'false' // 默认无头模式
    this.browsers = ['firefox', 'edge'] // 暂时移除Chrome，直到WebDriver问题解决
  }

  /**
   * 创建WebDriver实例
   * @param {string} browserName - 浏览器名称 (chrome, firefox, edge)
   * @returns {Promise<WebDriver>}
   */
  async createDriver (browserName = 'chrome') {
    let driver
    
    try {
      switch (browserName.toLowerCase()) {
        case 'chrome':
          driver = await this.createChromeDriver()
          break
        case 'firefox':
          driver = await this.createFirefoxDriver()
          break
        case 'edge':
          driver = await this.createEdgeDriver()
          break
        default:
          throw new Error(`不支持的浏览器: ${browserName}`)
      }

      // 设置窗口大小
      await driver.manage().window().setRect({ width: 1920, height: 1080 })
      
      // 设置超时时间
      await driver.manage().setTimeouts({
        implicit: this.timeout,
        pageLoad: this.timeout,
        script: this.timeout,
      })

      console.log(`✅ ${browserName} WebDriver 创建成功`)
      return driver
    } catch (error) {
      console.error(`❌ 创建 ${browserName} WebDriver 失败:`, error.message)
      throw error
    }
  }

  /**
   * 创建Chrome WebDriver
   */
  async createChromeDriver () {
    const options = new chrome.Options()
    
    if (this.headless) {
      options.addArguments('--headless')
    }
    
    options.addArguments(
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--disable-extensions',
      '--disable-background-timer-throttling',
      '--disable-backgrounding-occluded-windows',
      '--disable-renderer-backgrounding',
      '--disable-features=TranslateUI',
      '--disable-web-security',
      '--allow-running-insecure-content',
    )

    return new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build()
  }

  /**
   * 创建Firefox WebDriver
   */
  async createFirefoxDriver () {
    const options = new firefox.Options()
    
    if (this.headless) {
      options.addArguments('--headless')
    }
    
    options.addArguments('--no-sandbox', '--disable-dev-shm-usage')

    return new Builder()
      .forBrowser('firefox')
      .setFirefoxOptions(options)
      .build()
  }

  /**
   * 创建Edge WebDriver
   */
  async createEdgeDriver () {
    const options = new edge.Options()
    
    if (this.headless) {
      options.addArguments('--headless')
    }
    
    options.addArguments(
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
    )

    return new Builder()
      .forBrowser('MicrosoftEdge')
      .setEdgeOptions(options)
      .build()
  }

  /**
   * 安全关闭WebDriver
   * @param {WebDriver} driver 
   */
  async closeDriver (driver) {
    if (driver) {
      try {
        await driver.quit()
        console.log('✅ WebDriver 已关闭')
      } catch (error) {
        console.error('❌ 关闭 WebDriver 时出错:', error.message)
      }
    }
  }

  /**
   * 等待页面完全加载
   * @param {WebDriver} driver 
   */
  async waitForPageLoad (driver) {
    await driver.wait(async () => {
      const readyState = await driver.executeScript('return document.readyState')
      return readyState === 'complete'
    }, this.timeout)

    // 等待Vue应用挂载
    try {
      await driver.wait(async () => {
        const vueApp = await driver.executeScript('return document.querySelector("#app").__vue_app__')
        return vueApp !== null
      }, 5000)
    } catch (error) {
      console.log('Vue应用检测超时，继续执行测试')
    }
  }

  /**
   * 检查控制台错误
   * @param {WebDriver} driver 
   * @returns {Promise<Array>}
   */
  async getConsoleErrors (driver) {
    try {
      const logs = await driver.manage().logs().get('browser')
      return logs.filter(log => log.level.name === 'SEVERE')
    } catch (error) {
      console.log('无法获取浏览器日志:', error.message)
      return []
    }
  }

  /**
   * 截图
   * @param {WebDriver} driver 
   * @param {string} filename 
   */
  async takeScreenshot (driver, filename) {
    try {
      const screenshot = await driver.takeScreenshot()
      const fs = require('fs')
      const path = require('path')
      
      const screenshotDir = path.join(__dirname, '../../test-results/selenium-screenshots')
      if (!fs.existsSync(screenshotDir)) {
        fs.mkdirSync(screenshotDir, { recursive: true })
      }
      
      const filepath = path.join(screenshotDir, `${filename}.png`)
      fs.writeFileSync(filepath, screenshot, 'base64')
      console.log(`📸 截图已保存: ${filepath}`)
      return filepath
    } catch (error) {
      console.error('截图失败:', error.message)
    }
  }
}

module.exports = SeleniumConfig
