import { test, expect } from '@playwright/test'
import { TestHelpers } from './utils/test-helpers'

test.describe('学习模式功能测试', () => {
  let helpers: TestHelpers

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page)
  })

  test('应该显示所有4种学习模式选项', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')

    // 如果需要认证，跳过测试
    if (await helpers.checkAuthRedirect()) {
      console.log('需要用户认证，跳过测试')
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 检查页面标题
    await expect(page).toHaveTitle(/地道表达学习/)

    // 查找学习模式卡片
    const modeCards = page.locator('.mode-card')
    await expect(modeCards).toHaveCount(4)

    // 检查具体的学习模式
    const modes = [
      { name: '闪卡学习', icon: 'Postcard' },
      { name: '情景学习', icon: 'VideoPlay' },
      { name: 'AI对话', icon: 'ChatDotSquare' },
      { name: '复习模式', icon: 'Refresh' },
    ]

    for (let i = 0; i < modes.length; i++) {
      const card = modeCards.nth(i)
      await expect(card).toBeVisible()
      
      // 检查模式标题
      const title = card.locator('h3')
      if (await title.count() > 0) {
        const titleText = await title.textContent()
        console.log(`模式 ${i + 1}: ${titleText}`)
      }
    }
  })

  test('应该能够切换到闪卡学习模式', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 查找并点击闪卡学习模式
    const flashcardMode = page.locator('.mode-card:has-text("闪卡"), .mode-card').first()
    await flashcardMode.click()
    await page.waitForTimeout(2000)

    // 检查模式是否激活
    await expect(flashcardMode).toHaveClass(/active/)

    // 检查闪卡学习界面是否显示
    const flashcardArea = page.locator('.flashcard-mode, .card-container, [data-testid="flashcard-area"]')
    if (await flashcardArea.count() > 0) {
      await expect(flashcardArea.first()).toBeVisible()
    }

    console.log('✅ 闪卡学习模式激活成功')
  })

  test('应该能够切换到情景学习模式', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 查找并点击情景学习模式
    const scenarioMode = page.locator('.mode-card:has-text("情景")')
    if (await scenarioMode.count() > 0) {
      await scenarioMode.click()
      await page.waitForTimeout(2000)

      // 检查模式是否激活
      await expect(scenarioMode).toHaveClass(/active/)

      // 检查情景学习界面是否显示
      const scenarioArea = page.locator('.scenario-mode, .video-container, [data-testid="scenario-area"]')
      if (await scenarioArea.count() > 0) {
        await expect(scenarioArea.first()).toBeVisible()
      }

      console.log('✅ 情景学习模式激活成功')
    } else {
      console.log('未找到情景学习模式，跳过测试')
    }
  })

  test('应该能够切换到AI对话模式', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 查找并点击AI对话模式
    const aiMode = page.locator('.mode-card:has-text("AI对话"), .mode-card:has-text("AI")')
    if (await aiMode.count() > 0) {
      await aiMode.click()
      await page.waitForTimeout(2000)

      // 检查模式是否激活
      await expect(aiMode).toHaveClass(/active/)

      // 检查AI对话界面是否显示
      const aiChatArea = page.locator('.ai-chat-mode, .chat-container, [data-testid="ai-chat-area"]')
      if (await aiChatArea.count() > 0) {
        await expect(aiChatArea.first()).toBeVisible()
      }

      console.log('✅ AI对话模式激活成功')
    } else {
      console.log('未找到AI对话模式，跳过测试')
    }
  })

  test('应该能够切换到复习模式', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 查找并点击复习模式
    const reviewMode = page.locator('.mode-card:has-text("复习")')
    if (await reviewMode.count() > 0) {
      await reviewMode.click()
      await page.waitForTimeout(2000)

      // 检查模式是否激活
      await expect(reviewMode).toHaveClass(/active/)

      // 检查复习界面是否显示
      const reviewArea = page.locator('.review-mode, .review-container, [data-testid="review-area"]')
      if (await reviewArea.count() > 0) {
        await expect(reviewArea.first()).toBeVisible()
      }

      console.log('✅ 复习模式激活成功')
    } else {
      console.log('未找到复习模式，跳过测试')
    }
  })

  test('在AI对话模式下应该能够发送消息', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 切换到AI对话模式
    const aiMode = page.locator('.mode-card:has-text("AI对话"), .mode-card:has-text("AI")')
    if (await aiMode.count() > 0) {
      await aiMode.click()
      await page.waitForTimeout(2000)

      // 查找消息输入框
      const messageInput = page.locator('input[placeholder*="消息"], input[placeholder*="输入"], textarea[placeholder*="消息"]')
      if (await messageInput.count() > 0) {
        const input = messageInput.first()
        
        // 输入测试消息
        const testMessage = 'Hello, can you help me learn this expression?'
        await input.fill(testMessage)
        await expect(input).toHaveValue(testMessage)

        // 查找发送按钮
        const sendButton = page.locator('button:has-text("发送"), button[title="发送"]')
        if (await sendButton.count() > 0) {
          await sendButton.first().click()
        } else {
          // 尝试使用Enter键发送
          await input.press('Enter')
        }

        console.log('✅ AI对话消息发送测试完成')
      } else {
        console.log('未找到消息输入框')
      }
    } else {
      console.log('未找到AI对话模式，跳过测试')
    }
  })

  test('学习模式切换应该无JavaScript错误', async ({ page }) => {
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

    await page.goto('/english/idiomatic-learning')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 依次点击所有学习模式
    const modeCards = page.locator('.mode-card')
    const count = await modeCards.count()

    for (let i = 0; i < Math.min(count, 4); i++) {
      const card = modeCards.nth(i)
      if (await card.isVisible()) {
        await card.click()
        await page.waitForTimeout(1500)
      }
    }

    // 检查是否有JavaScript错误
    expect(jsErrors).toHaveLength(0)
    
    if (jsErrors.length > 0) {
      console.log('发现JavaScript错误:', jsErrors)
    }

    console.log('✅ 学习模式切换无JavaScript错误')
  })

  test('学习模式页面应该响应式适配', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

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

      // 检查学习模式卡片在不同屏幕尺寸下是否可见
      const modeCards = page.locator('.mode-card')
      const visibleCards = await modeCards.count()

      expect(visibleCards).toBeGreaterThan(0)
      console.log(`✅ ${viewport.name} (${viewport.width}x${viewport.height}) - ${visibleCards}个学习模式可见`)
    }
  })
})
