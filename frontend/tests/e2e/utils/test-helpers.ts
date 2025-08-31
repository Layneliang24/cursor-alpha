import { Page, expect } from '@playwright/test'

/**
 * 测试工具类
 */
export class TestHelpers {
  constructor (private page: Page) {}

  /**
   * 等待Vue应用加载完成
   */
  async waitForVueApp () {
    await this.page.waitForSelector('#app', { state: 'visible' })
    await this.page.waitForLoadState('networkidle')
  }

  /**
   * 检查是否重定向到登录页面
   */
  async checkAuthRedirect (): Promise<boolean> {
    return this.page.url().includes('login')
  }

  /**
   * 模拟用户登录（如果需要）
   * 注意：这是一个占位符，实际实现需要根据具体的登录流程
   */
  async loginIfNeeded (username = 'test@example.com', password = 'testpass123') {
    if (await this.checkAuthRedirect()) {
      console.log('检测到需要登录，尝试自动登录...')
      
      // 填写登录表单
      const usernameInput = this.page.locator('input[type="text"], input[placeholder*="用户名"], input[placeholder*="邮箱"]').first()
      const passwordInput = this.page.locator('input[type="password"]')
      const loginButton = this.page.locator('button[type="submit"], button:has-text("登录")').first()
      
      if (await usernameInput.isVisible()) {
        await usernameInput.fill(username)
      }
      if (await passwordInput.isVisible()) {
        await passwordInput.fill(password)
      }
      if (await loginButton.isVisible()) {
        await loginButton.click()
      }
      
      // 等待登录完成
      await this.page.waitForTimeout(2000)
      
      return !await this.checkAuthRedirect()
    }
    return true // 已经登录
  }

  /**
   * 导航到指定页面并处理认证
   */
  async navigateWithAuth (path: string) {
    await this.page.goto(path)
    await this.waitForVueApp()
    
    const isLoggedIn = await this.loginIfNeeded()
    if (isLoggedIn && !this.page.url().includes(path)) {
      // 如果登录成功但不在目标页面，重新导航
      await this.page.goto(path)
      await this.waitForVueApp()
    }
    
    return isLoggedIn
  }

  /**
   * 检查页面是否有JavaScript错误
   */
  async checkForJSErrors (): Promise<string[]> {
    const errors: string[] = []
    
    this.page.on('pageerror', (error) => {
      errors.push(error.message)
    })
    
    this.page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
      }
    })
    
    return errors
  }

  /**
   * 等待元素出现并可见
   */
  async waitForElement (selector: string, timeout = 10000) {
    return await this.page.waitForSelector(selector, { 
      state: 'visible', 
      timeout, 
    })
  }

  /**
   * 检查页面加载性能
   */
  async checkPagePerformance () {
    const navigationTiming = await this.page.evaluate(() => {
      const timing = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
      return {
        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
        loadComplete: timing.loadEventEnd - timing.navigationStart,
        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
      }
    })
    
    return navigationTiming
  }

  /**
   * 截图并保存（用于调试）
   */
  async takeDebugScreenshot (name: string) {
    await this.page.screenshot({ 
      path: `test-results/debug-${name}-${Date.now()}.png`,
      fullPage: true, 
    })
  }

  /**
   * 检查响应式设计
   */
  async checkResponsiveDesign () {
    const viewports = [
      { width: 1920, height: 1080, name: 'Desktop' },
      { width: 768, height: 1024, name: 'Tablet' },
      { width: 375, height: 667, name: 'Mobile' },
    ]
    
    const results = []
    
    for (const viewport of viewports) {
      await this.page.setViewportSize({ width: viewport.width, height: viewport.height })
      await this.page.waitForTimeout(1000)
      
      const appElement = this.page.locator('#app')
      const isVisible = await appElement.isVisible()
      
      results.push({
        viewport: viewport.name,
        dimensions: `${viewport.width}x${viewport.height}`,
        appVisible: isVisible,
      })
    }
    
    return results
  }
}
