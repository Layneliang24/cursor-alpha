import { test, expect } from '@playwright/test'

test.describe('地道表达模块 E2E 测试', () => {
  test('应用首页可以正常访问', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/Alpha/)
    
    // 检查页面是否加载完成
    await page.waitForSelector('#app', { timeout: 10000 })
  })
  
  test('后端API健康检查', async ({ page }) => {
    // 测试后端API是否可访问
    const response = await page.request.get('http://localhost:8000/api/health/')
    expect(response.status()).toBe(200)
  })
  
  test('地道表达API端点测试', async ({ page }) => {
    // 测试地道表达相关的API端点
    const response = await page.request.get('http://localhost:8000/api/v1/idiomatic-expressions/')
    // API可能返回401（未认证）或200（成功），都表示端点存在
    expect([200, 401, 403]).toContain(response.status())
  })
})
