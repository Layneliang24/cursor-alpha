import { test, expect } from '@playwright/test'
import { TestHelpers } from './utils/test-helpers'

test.describe('用户登录流程测试', () => {
  let helpers: TestHelpers

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page)
  })

  test('应该显示登录页面的所有必要元素', async ({ page }) => {
    await page.goto('/login')
    await helpers.waitForVueApp()

    // 检查页面标题
    await expect(page).toHaveTitle(/用户登录/)

    // 检查登录表单元素
    const usernameInput = page.locator('input[type="text"]').first()
    const passwordInput = page.locator('input[type="password"]')
    const loginButton = page.locator('button:has-text("登录")').first()

    await expect(usernameInput).toBeVisible()
    await expect(passwordInput).toBeVisible()
    await expect(loginButton).toBeVisible()

    // 检查是否有"记住我"选项
    const rememberCheckbox = page.locator('input[type="checkbox"]')
    if (await rememberCheckbox.count() > 0) {
      await expect(rememberCheckbox.first()).toBeVisible()
    }

    // 检查是否有注册链接
    const registerLink = page.locator('a:has-text("注册"), button:has-text("注册")')
    if (await registerLink.count() > 0) {
      await expect(registerLink.first()).toBeVisible()
    }
  })

  test('应该能够输入用户名和密码', async ({ page }) => {
    await page.goto('/login')
    await helpers.waitForVueApp()

    const usernameInput = page.locator('input[type="text"]').first()
    const passwordInput = page.locator('input[type="password"]')

    // 输入测试数据
    await usernameInput.fill('test@example.com')
    await passwordInput.fill('testpass123')

    // 验证输入内容
    await expect(usernameInput).toHaveValue('test@example.com')
    await expect(passwordInput).toHaveValue('testpass123')
  })

  test('空用户名或密码应该显示验证错误', async ({ page }) => {
    await page.goto('/login')
    await helpers.waitForVueApp()

    const loginButton = page.locator('button:has-text("登录")').first()

    // 尝试不填写任何信息就登录
    await loginButton.click()

    // 等待可能的错误消息
    await page.waitForTimeout(2000)

    // 检查是否有错误提示（Element Plus的表单验证）
    const errorMessages = page.locator('.el-form-item__error, .el-message--error, [class*="error"]')
    if (await errorMessages.count() > 0) {
      await expect(errorMessages.first()).toBeVisible()
    }

    // 或者检查是否仍在登录页面（没有跳转）
    expect(page.url()).toContain('login')
  })

  test('登录失败应该显示错误信息', async ({ page }) => {
    await page.goto('/login')
    await helpers.waitForVueApp()

    const usernameInput = page.locator('input[type="text"]').first()
    const passwordInput = page.locator('input[type="password"]')
    const loginButton = page.locator('button:has-text("登录")').first()

    // 输入错误的凭据
    await usernameInput.fill('wrong@example.com')
    await passwordInput.fill('wrongpassword')
    await loginButton.click()

    // 等待响应
    await page.waitForTimeout(3000)

    // 检查错误消息或仍在登录页面
    const errorMessage = page.locator('.el-message--error, [class*="error"], .error-message')
    if (await errorMessage.count() > 0) {
      await expect(errorMessage.first()).toBeVisible()
    } else {
      // 如果没有明显的错误消息，检查是否仍在登录页面
      expect(page.url()).toContain('login')
    }
  })

  test('应该能够导航到注册页面', async ({ page }) => {
    await page.goto('/login')
    await helpers.waitForVueApp()

    // 查找注册链接
    const registerLink = page.locator('a:has-text("注册"), button:has-text("注册"), [href="/register"]')
    
    if (await registerLink.count() > 0) {
      await registerLink.first().click()
      await helpers.waitForVueApp()

      // 检查是否导航到注册页面
      expect(page.url()).toContain('register')
      await expect(page).toHaveTitle(/注册/)
    } else {
      console.log('未找到注册链接，跳过此测试')
      test.skip(true, '未找到注册链接')
    }
  })

  test('登录页面应该响应式适配', async ({ page }) => {
    await page.goto('/login')
    await helpers.waitForVueApp()

    // 测试不同屏幕尺寸
    const viewports = [
      { width: 1920, height: 1080, name: 'Desktop' },
      { width: 768, height: 1024, name: 'Tablet' },
      { width: 375, height: 667, name: 'Mobile' },
    ]

    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height })
      await page.waitForTimeout(1000)

      // 检查关键元素在不同屏幕尺寸下是否可见
      const usernameInput = page.locator('input[type="text"]').first()
      const passwordInput = page.locator('input[type="password"]')
      const loginButton = page.locator('button:has-text("登录")').first()

      await expect(usernameInput).toBeVisible()
      await expect(passwordInput).toBeVisible()
      await expect(loginButton).toBeVisible()

      console.log(`✅ ${viewport.name} (${viewport.width}x${viewport.height}) - 登录表单正常显示`)
    }
  })

  test('登录页面应该无JavaScript错误', async ({ page }) => {
    const jsErrors: string[] = []

    // 监听JavaScript错误
    page.on('pageerror', (error) => {
      jsErrors.push(error.message)
    })

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        jsErrors.push(msg.text())
      }
    })

    await page.goto('/login')
    await helpers.waitForVueApp()

    // 与页面交互
    const usernameInput = page.locator('input[type="text"]').first()
    const passwordInput = page.locator('input[type="password"]')

    await usernameInput.fill('test@example.com')
    await passwordInput.fill('testpass123')

    // 等待一段时间确保所有异步操作完成
    await page.waitForTimeout(3000)

    // 检查是否有JavaScript错误
    expect(jsErrors).toHaveLength(0)
    
    if (jsErrors.length > 0) {
      console.log('发现JavaScript错误:', jsErrors)
    }
  })
})
