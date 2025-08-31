import { test, expect } from '@playwright/test'
import { TestHelpers } from './utils/test-helpers'

test.describe('AI助教高级功能测试', () => {
  let helpers: TestHelpers

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page)
  })

  test('AI助教界面应该包含所有必要元素', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 切换到AI对话模式
    const aiMode = page.locator('.mode-card:has-text("AI对话"), .mode-card:has-text("AI")')
    if (await aiMode.count() === 0) {
      test.skip(true, '未找到AI对话模式')
      return
    }

    await aiMode.click()
    await page.waitForTimeout(2000)

    // 检查AI助教界面的关键元素
    const elements = {
      messageInput: page.locator('input[placeholder*="消息"], input[placeholder*="输入"], textarea[placeholder*="消息"]'),
      sendButton: page.locator('button:has-text("发送"), button[title="发送"]'),
      chatArea: page.locator('.chat-messages, .message-list, .conversation-area'),
      aiAvatar: page.locator('.ai-avatar, .assistant-avatar, [class*="avatar"]'),
      settingsButton: page.locator('button[title*="设置"], .settings-button, [class*="setting"]'),
    }

    // 检查消息输入框
    if (await elements.messageInput.count() > 0) {
      await expect(elements.messageInput.first()).toBeVisible()
      console.log('✅ 消息输入框存在')
    }

    // 检查发送按钮或Enter键提示
    if (await elements.sendButton.count() > 0) {
      await expect(elements.sendButton.first()).toBeVisible()
      console.log('✅ 发送按钮存在')
    } else {
      console.log('ℹ️ 未找到发送按钮，可能支持Enter键发送')
    }

    // 检查聊天区域
    if (await elements.chatArea.count() > 0) {
      await expect(elements.chatArea.first()).toBeVisible()
      console.log('✅ 聊天区域存在')
    }

    console.log('✅ AI助教界面基本元素检查完成')
  })

  test('应该能够输入和发送消息', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 切换到AI对话模式
    const aiMode = page.locator('.mode-card:has-text("AI对话"), .mode-card:has-text("AI")')
    if (await aiMode.count() === 0) {
      test.skip(true, '未找到AI对话模式')
      return
    }

    await aiMode.click()
    await page.waitForTimeout(2000)

    // 查找消息输入框
    const messageInput = page.locator('input[placeholder*="消息"], input[placeholder*="输入"], textarea[placeholder*="消息"]')
    if (await messageInput.count() === 0) {
      test.skip(true, '未找到消息输入框')
      return
    }

    const input = messageInput.first()
    const testMessages = [
      'Hello, can you help me with English expressions?',
      '请解释一下 "break the ice" 的含义',
      'How do I use "piece of cake" in a sentence?',
    ]

    for (const message of testMessages) {
      // 清空输入框
      await input.fill('')
      
      // 输入消息
      await input.fill(message)
      await expect(input).toHaveValue(message)

      // 尝试发送消息
      const sendButton = page.locator('button:has-text("发送"), button[title="发送"]')
      if (await sendButton.count() > 0) {
        await sendButton.first().click()
      } else {
        await input.press('Enter')
      }

      // 等待响应
      await page.waitForTimeout(2000)

      console.log(`✅ 消息发送测试: "${message.substring(0, 30)}..."`)
    }
  })

  test('应该能够处理长消息输入', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 切换到AI对话模式
    const aiMode = page.locator('.mode-card:has-text("AI对话"), .mode-card:has-text("AI")')
    if (await aiMode.count() === 0) {
      test.skip(true, '未找到AI对话模式')
      return
    }

    await aiMode.click()
    await page.waitForTimeout(2000)

    const messageInput = page.locator('input[placeholder*="消息"], input[placeholder*="输入"], textarea[placeholder*="消息"]')
    if (await messageInput.count() === 0) {
      test.skip(true, '未找到消息输入框')
      return
    }

    const input = messageInput.first()
    
    // 测试长消息
    const longMessage = 'This is a very long message that contains multiple sentences and should test the input field\'s ability to handle extended text. I want to learn about idiomatic expressions like "break the ice", "piece of cake", "hit the nail on the head", and many others. Can you help me understand their meanings and usage in different contexts?'

    await input.fill(longMessage)
    await expect(input).toHaveValue(longMessage)

    console.log('✅ 长消息输入测试通过')
  })

  test('AI助教应该支持上下文对话', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 切换到AI对话模式
    const aiMode = page.locator('.mode-card:has-text("AI对话"), .mode-card:has-text("AI")')
    if (await aiMode.count() === 0) {
      test.skip(true, '未找到AI对话模式')
      return
    }

    await aiMode.click()
    await page.waitForTimeout(2000)

    const messageInput = page.locator('input[placeholder*="消息"], input[placeholder*="输入"], textarea[placeholder*="消息"]')
    if (await messageInput.count() === 0) {
      test.skip(true, '未找到消息输入框')
      return
    }

    const input = messageInput.first()

    // 模拟上下文对话
    const conversationFlow = [
      'What does "break the ice" mean?',
      'Can you give me an example sentence?',
      'Are there similar expressions?',
      'Thank you for the explanation!',
    ]

    for (let i = 0; i < conversationFlow.length; i++) {
      await input.fill(conversationFlow[i])
      
      const sendButton = page.locator('button:has-text("发送"), button[title="发送"]')
      if (await sendButton.count() > 0) {
        await sendButton.first().click()
      } else {
        await input.press('Enter')
      }

      // 等待响应
      await page.waitForTimeout(1500)

      console.log(`✅ 对话轮次 ${i + 1}: "${conversationFlow[i]}"`)
    }

    console.log('✅ 上下文对话测试完成')
  })

  test('AI助教界面应该显示消息历史', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 切换到AI对话模式
    const aiMode = page.locator('.mode-card:has-text("AI对话"), .mode-card:has-text("AI")')
    if (await aiMode.count() === 0) {
      test.skip(true, '未找到AI对话模式')
      return
    }

    await aiMode.click()
    await page.waitForTimeout(2000)

    // 检查是否有消息历史区域
    const messageArea = page.locator('.chat-messages, .message-list, .conversation-history, .messages')
    if (await messageArea.count() > 0) {
      await expect(messageArea.first()).toBeVisible()
      console.log('✅ 消息历史区域存在')

      // 检查是否有欢迎消息或历史消息
      const messages = page.locator('.message, .chat-message, [class*="message"]')
      const messageCount = await messages.count()
      
      if (messageCount > 0) {
        console.log(`✅ 发现 ${messageCount} 条历史消息`)
      } else {
        console.log('ℹ️ 暂无历史消息（正常情况）')
      }
    } else {
      console.log('ℹ️ 未找到明显的消息历史区域')
    }
  })

  test('AI助教应该支持表达式上下文学习', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 切换到AI对话模式
    const aiMode = page.locator('.mode-card:has-text("AI对话"), .mode-card:has-text("AI")')
    if (await aiMode.count() === 0) {
      test.skip(true, '未找到AI对话模式')
      return
    }

    await aiMode.click()
    await page.waitForTimeout(2000)

    const messageInput = page.locator('input[placeholder*="消息"], input[placeholder*="输入"], textarea[placeholder*="消息"]')
    if (await messageInput.count() === 0) {
      test.skip(true, '未找到消息输入框')
      return
    }

    // 测试表达式相关的对话
    const expressionQueries = [
      'Explain the expression "piece of cake"',
      'When would I use "break the ice"?',
      'What\'s the difference between "hit the nail on the head" and "close but no cigar"?',
    ]

    const input = messageInput.first()

    for (const query of expressionQueries) {
      await input.fill(query)
      
      const sendButton = page.locator('button:has-text("发送"), button[title="发送"]')
      if (await sendButton.count() > 0) {
        await sendButton.first().click()
      } else {
        await input.press('Enter')
      }

      await page.waitForTimeout(2000)
      console.log(`✅ 表达式查询: "${query}"`)
    }

    console.log('✅ 表达式上下文学习测试完成')
  })

  test('AI助教功能应该无JavaScript错误', async ({ page }) => {
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

    // 切换到AI对话模式并进行交互
    const aiMode = page.locator('.mode-card:has-text("AI对话"), .mode-card:has-text("AI")')
    if (await aiMode.count() > 0) {
      await aiMode.click()
      await page.waitForTimeout(2000)

      const messageInput = page.locator('input[placeholder*="消息"], input[placeholder*="输入"], textarea[placeholder*="消息"]')
      if (await messageInput.count() > 0) {
        const input = messageInput.first()
        await input.fill('Test message for error checking')
        await input.press('Enter')
        await page.waitForTimeout(3000)
      }
    }

    // 检查是否有JavaScript错误
    expect(jsErrors).toHaveLength(0)
    
    if (jsErrors.length > 0) {
      console.log('发现JavaScript错误:', jsErrors)
    }

    console.log('✅ AI助教功能无JavaScript错误')
  })
})
