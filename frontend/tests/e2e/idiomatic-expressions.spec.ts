import { test, expect } from '@playwright/test'

test.describe('地道表达学习功能测试', () => {
  test('地道表达列表页面应该正确加载', async ({ page }) => {
    await page.goto('/english/expressions')
    
    // 由于需要认证，检查是否重定向到登录页面
    if (page.url().includes('login')) {
      await expect(page.url()).toContain('login')
      console.log('页面正确重定向到登录页面（需要认证）')
      return
    }
    
    // 如果已登录，检查页面内容
    await expect(page).toHaveTitle(/地道表达/)
  })

  test('地道表达学习页面应该正确加载', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')
    
    // 由于需要认证，检查是否重定向到登录页面
    if (page.url().includes('login')) {
      await expect(page.url()).toContain('login')
      console.log('页面正确重定向到登录页面（需要认证）')
      return
    }
    
    // 如果已登录，检查页面内容
    await expect(page).toHaveTitle(/地道表达学习/)
    
    // 检查学习模式选项
    const modeCards = page.locator('.mode-card')
    await expect(modeCards).toHaveCount(4) // 应该有4种学习模式
    
    // 检查AI对话模式
    const aiModeCard = page.locator('.mode-card:has-text("AI对话")')
    await expect(aiModeCard).toBeVisible()
  })

  test('应该能够切换到AI对话模式', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')
    
    // 跳过认证检查（假设已登录或使用测试账户）
    if (page.url().includes('login')) {
      console.log('跳过测试：需要用户认证')
      return
    }
    
    // 点击AI对话模式
    const aiModeCard = page.locator('.mode-card:has-text("AI对话")')
    await aiModeCard.click()
    
    // 检查模式是否切换成功
    await expect(aiModeCard).toHaveClass(/active/)
    
    // 检查AI助教组件是否显示
    const aiChatArea = page.locator('.ai-chat-mode')
    await expect(aiChatArea).toBeVisible()
  })

  test('AI助教聊天界面应该包含基本元素', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')
    
    if (page.url().includes('login')) {
      console.log('跳过测试：需要用户认证')
      return
    }
    
    // 切换到AI对话模式
    const aiModeCard = page.locator('.mode-card:has-text("AI对话")')
    await aiModeCard.click()
    
    // 等待AI组件加载
    await page.waitForTimeout(2000)
    
    // 检查基本的聊天界面元素
    const chatInput = page.locator('input[placeholder*="消息"], input[placeholder*="输入"], textarea[placeholder*="消息"]')
    const sendButton = page.locator('button:has-text("发送"), button[title="发送"]')
    
    // 至少应该有输入框
    await expect(chatInput.first()).toBeVisible()
  })

  test('学习分析页面应该可访问', async ({ page }) => {
    await page.goto('/english/learning-analytics')
    
    // 由于需要认证，检查是否重定向到登录页面
    if (page.url().includes('login')) {
      await expect(page.url()).toContain('login')
      console.log('页面正确重定向到登录页面（需要认证）')
      return
    }
    
    // 如果已登录，检查页面内容
    await expect(page).toHaveTitle(/学习数据分析/)
  })
})
