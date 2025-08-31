import { test, expect } from '@playwright/test'

test.describe('基础导航测试', () => {
  test('首页应该正确加载', async ({ page }) => {
    await page.goto('/')
    
    // 检查页面标题
    await expect(page).toHaveTitle(/Alpha 技术共享平台/)
    
    // 检查Vue应用是否挂载
    const appElement = page.locator('#app').first()
    await expect(appElement).toBeVisible()
  })

  test('应该能够导航到英语学习页面', async ({ page }) => {
    await page.goto('/')
    
    // 等待页面加载
    await page.waitForLoadState('networkidle')
    
    // 尝试导航到英语学习相关页面
    await page.goto('/english/expressions')
    
    // 由于已认证，应该能够访问页面而不被重定向
    await expect(page.url()).toContain('/english/expressions')
    
    // 检查页面是否正确加载
    await expect(page.locator('body')).toBeVisible()
  })

  test('登录页面应该正确显示', async ({ page }) => {
    await page.goto('/login')
    
    // 检查页面标题
    await expect(page).toHaveTitle(/用户登录/)
    
    // 检查登录表单元素
    const usernameInput = page.locator('input[type="text"], input[placeholder*="用户名"], input[placeholder*="邮箱"]').first()
    const passwordInput = page.locator('input[type="password"]')
    const loginButton = page.locator('button[type="submit"], button:has-text("登录")').first()
    
    await expect(usernameInput).toBeVisible()
    await expect(passwordInput).toBeVisible()
    await expect(loginButton).toBeVisible()
  })
})
