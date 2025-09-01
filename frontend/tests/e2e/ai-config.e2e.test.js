import { test, expect } from '@playwright/test'

// 测试数据
const testData = {
  provider: {
    name: 'test_provider',
    provider_type: 'openai',
    display_name: 'Test Provider',
    base_url: 'https://api.test.com',
    api_version: 'v1'
  },
  apiKey: {
    key_name: 'test_key',
    provider: 1,
    api_key: 'sk-test123456789'
  },
  modelConfig: {
    name: 'test_config',
    model: 1,
    temperature: 0.7,
    max_tokens: 1000
  }
}

test.describe('AI配置页面E2E测试', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到AI配置页面
    await page.goto('/ai-config')
    
    // 等待页面加载完成
    await page.waitForSelector('.ai-config-container', { timeout: 10000 })
  })

  test('应该正确加载AI配置页面', async ({ page }) => {
    // 验证页面标题
    await expect(page.locator('h1')).toContainText('AI配置管理')
    
    // 验证标签页存在
    await expect(page.locator('.config-tabs')).toBeVisible()
    
    // 验证各个标签页
    await expect(page.locator('text=AI提供商')).toBeVisible()
    await expect(page.locator('text=API密钥')).toBeVisible()
    await expect(page.locator('text=AI模型')).toBeVisible()
    await expect(page.locator('text=模型配置')).toBeVisible()
    await expect(page.locator('text=统计信息')).toBeVisible()
  })

  test('应该能够管理AI提供商', async ({ page }) => {
    // 点击AI提供商标签页
    await page.click('text=AI提供商')
    await page.waitForSelector('.provider-list')
    
    // 验证提供商列表显示
    await expect(page.locator('.provider-list')).toBeVisible()
    
    // 点击添加提供商按钮
    await page.click('.add-provider-btn')
    await page.waitForSelector('.provider-dialog')
    
    // 填写提供商信息
    await page.fill('input[name="name"]', testData.provider.name)
    await page.selectOption('select[name="provider_type"]', testData.provider.provider_type)
    await page.fill('input[name="display_name"]', testData.provider.display_name)
    await page.fill('input[name="base_url"]', testData.provider.base_url)
    await page.fill('input[name="api_version"]', testData.provider.api_version)
    
    // 提交表单
    await page.click('.submit-btn')
    
    // 验证成功消息
    await expect(page.locator('.success-message')).toBeVisible()
    
    // 验证新提供商出现在列表中
    await expect(page.locator(`text=${testData.provider.display_name}`)).toBeVisible()
  })

  test('应该能够管理API密钥', async ({ page }) => {
    // 点击API密钥标签页
    await page.click('text=API密钥')
    await page.waitForSelector('.api-key-list')
    
    // 验证API密钥列表显示
    await expect(page.locator('.api-key-list')).toBeVisible()
    
    // 点击添加API密钥按钮
    await page.click('.add-api-key-btn')
    await page.waitForSelector('.api-key-dialog')
    
    // 填写API密钥信息
    await page.fill('input[name="key_name"]', testData.apiKey.key_name)
    await page.selectOption('select[name="provider"]', testData.apiKey.provider.toString())
    await page.fill('input[name="api_key"]', testData.apiKey.api_key)
    
    // 提交表单
    await page.click('.submit-btn')
    
    // 验证成功消息
    await expect(page.locator('.success-message')).toBeVisible()
    
    // 验证新API密钥出现在列表中
    await expect(page.locator(`text=${testData.apiKey.key_name}`)).toBeVisible()
  })

  test('应该能够管理AI模型', async ({ page }) => {
    // 点击AI模型标签页
    await page.click('text=AI模型')
    await page.waitForSelector('.model-list')
    
    // 验证模型列表显示
    await expect(page.locator('.model-list')).toBeVisible()
    
    // 验证模型信息显示
    await expect(page.locator('.model-item')).toHaveCount(2) // 至少应该有2个模型
    
    // 点击查看模型详情
    await page.click('.view-model-detail-btn:first-child')
    await page.waitForSelector('.model-detail-dialog')
    
    // 验证详情对话框显示
    await expect(page.locator('.model-detail-dialog')).toBeVisible()
    
    // 关闭详情对话框
    await page.click('.close-btn')
  })

  test('应该能够管理模型配置', async ({ page }) => {
    // 点击模型配置标签页
    await page.click('text=模型配置')
    await page.waitForSelector('.model-config-list')
    
    // 验证配置列表显示
    await expect(page.locator('.model-config-list')).toBeVisible()
    
    // 点击添加配置按钮
    await page.click('.add-config-btn')
    await page.waitForSelector('.config-dialog')
    
    // 填写配置信息
    await page.fill('input[name="name"]', testData.modelConfig.name)
    await page.selectOption('select[name="model"]', testData.modelConfig.model.toString())
    await page.fill('input[name="temperature"]', testData.modelConfig.temperature.toString())
    await page.fill('input[name="max_tokens"]', testData.modelConfig.max_tokens.toString())
    
    // 提交表单
    await page.click('.submit-btn')
    
    // 验证成功消息
    await expect(page.locator('.success-message')).toBeVisible()
    
    // 验证新配置出现在列表中
    await expect(page.locator(`text=${testData.modelConfig.name}`)).toBeVisible()
  })

  test('应该能够查看统计信息', async ({ page }) => {
    // 点击统计信息标签页
    await page.click('text=统计信息')
    await page.waitForSelector('.statistics-section')
    
    // 验证统计信息显示
    await expect(page.locator('.statistics-section')).toBeVisible()
    
    // 验证使用量统计
    await expect(page.locator('.usage-statistics')).toBeVisible()
    await expect(page.locator('.total-requests')).toBeVisible()
    await expect(page.locator('.total-tokens')).toBeVisible()
    await expect(page.locator('.total-cost')).toBeVisible()
    
    // 验证成本统计
    await expect(page.locator('.cost-statistics')).toBeVisible()
    
    // 验证提供商统计
    await expect(page.locator('.provider-statistics')).toBeVisible()
  })

  test('应该能够监控健康状态', async ({ page }) => {
    // 验证健康状态显示
    await expect(page.locator('.health-status')).toBeVisible()
    
    // 验证状态指示器
    const statusIndicators = page.locator('.status-indicator')
    await expect(statusIndicators).toHaveCount(2) // 至少应该有2个服务状态
    
    // 验证所有服务都是健康状态
    for (let i = 0; i < await statusIndicators.count(); i++) {
      const indicator = statusIndicators.nth(i)
      await expect(indicator).toHaveClass(/healthy/)
    }
  })

  test('应该能够刷新数据', async ({ page }) => {
    // 点击刷新按钮
    await page.click('.refresh-btn')
    
    // 验证加载状态
    await expect(page.locator('.loading-spinner')).toBeVisible()
    
    // 等待加载完成
    await page.waitForSelector('.loading-spinner', { state: 'hidden' })
    
    // 验证数据已刷新
    await expect(page.locator('.provider-list')).toBeVisible()
  })

  test('应该能够处理错误情况', async ({ page }) => {
    // 模拟网络错误（通过修改API响应）
    await page.route('/api/v1/ai/providers/', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      })
    })
    
    // 刷新页面触发错误
    await page.reload()
    
    // 验证错误消息显示
    await expect(page.locator('.error-message')).toBeVisible()
    await expect(page.locator('.error-message')).toContainText('加载失败')
  })

  test('应该能够编辑现有配置', async ({ page }) => {
    // 点击AI提供商标签页
    await page.click('text=AI提供商')
    await page.waitForSelector('.provider-list')
    
    // 点击编辑按钮
    await page.click('.edit-provider-btn:first-child')
    await page.waitForSelector('.provider-dialog')
    
    // 修改提供商信息
    await page.fill('input[name="display_name"]', 'Updated Provider Name')
    
    // 提交修改
    await page.click('.submit-btn')
    
    // 验证成功消息
    await expect(page.locator('.success-message')).toBeVisible()
    
    // 验证修改后的名称显示
    await expect(page.locator('text=Updated Provider Name')).toBeVisible()
  })

  test('应该能够删除配置', async ({ page }) => {
    // 点击AI提供商标签页
    await page.click('text=AI提供商')
    await page.waitForSelector('.provider-list')
    
    // 点击删除按钮
    await page.click('.delete-provider-btn:first-child')
    
    // 确认删除
    await page.click('.confirm-delete-btn')
    
    // 验证成功消息
    await expect(page.locator('.success-message')).toBeVisible()
    
    // 验证提供商已被删除
    await expect(page.locator('.provider-item')).toHaveCount(1) // 减少了一个
  })

  test('应该能够搜索和筛选', async ({ page }) => {
    // 点击AI提供商标签页
    await page.click('text=AI提供商')
    await page.waitForSelector('.provider-list')
    
    // 使用搜索功能
    await page.fill('.search-input', 'OpenAI')
    
    // 验证搜索结果
    await expect(page.locator('.provider-item')).toHaveCount(1)
    await expect(page.locator('text=OpenAI')).toBeVisible()
    
    // 清除搜索
    await page.fill('.search-input', '')
    
    // 验证所有提供商重新显示
    await expect(page.locator('.provider-item')).toHaveCount(2)
  })

  test('应该能够导出配置', async ({ page }) => {
    // 点击导出按钮
    await page.click('.export-btn')
    
    // 验证下载开始
    const downloadPromise = page.waitForEvent('download')
    await page.click('.confirm-export-btn')
    const download = await downloadPromise
    
    // 验证下载文件名
    expect(download.suggestedFilename()).toMatch(/ai-config-\d{4}-\d{2}-\d{2}\.json/)
  })

  test('应该能够导入配置', async ({ page }) => {
    // 点击导入按钮
    await page.click('.import-btn')
    await page.waitForSelector('.import-dialog')
    
    // 选择文件
    await page.setInputFiles('input[type="file"]', {
      name: 'test-config.json',
      mimeType: 'application/json',
      buffer: Buffer.from(JSON.stringify({
        providers: [testData.provider],
        api_keys: [testData.apiKey],
        model_configs: [testData.modelConfig]
      }))
    })
    
    // 确认导入
    await page.click('.confirm-import-btn')
    
    // 验证成功消息
    await expect(page.locator('.success-message')).toBeVisible()
  })
})
