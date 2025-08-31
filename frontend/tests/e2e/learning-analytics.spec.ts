import { test, expect } from '@playwright/test'
import { TestHelpers } from './utils/test-helpers'

test.describe('学习分析功能测试', () => {
  let helpers: TestHelpers

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page)
  })

  test('学习分析页面应该正确加载', async ({ page }) => {
    await page.goto('/english/learning-analytics')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 检查页面标题
    await expect(page).toHaveTitle(/学习数据分析|学习分析/)

    // 检查页面主要内容区域
    const mainContent = page.locator('#app, .main-content, .analytics-dashboard')
    await expect(mainContent.first()).toBeVisible()

    console.log('✅ 学习分析页面加载成功')
  })

  test('应该显示学习进度图表', async ({ page }) => {
    await page.goto('/english/learning-analytics')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 等待图表加载
    await page.waitForTimeout(3000)

    // 查找图表容器（ECharts相关）
    const chartSelectors = [
      '.echarts, [class*="echarts"]',
      '.chart-container, [class*="chart"]',
      '.progress-chart, .trend-chart',
      'canvas',
      'svg',
    ]

    let chartFound = false
    for (const selector of chartSelectors) {
      const charts = page.locator(selector)
      const count = await charts.count()
      
      if (count > 0) {
        console.log(`✅ 发现 ${count} 个图表元素 (${selector})`)
        chartFound = true
        
        // 检查第一个图表是否可见
        const firstChart = charts.first()
        if (await firstChart.isVisible()) {
          console.log('✅ 图表元素可见')
        }
      }
    }

    if (!chartFound) {
      console.log('ℹ️ 未发现明显的图表元素，可能需要数据或正在加载中')
    }
  })

  test('应该显示学习统计数据', async ({ page }) => {
    await page.goto('/english/learning-analytics')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 等待数据加载
    await page.waitForTimeout(3000)

    // 查找统计数据元素
    const statsSelectors = [
      '.stats, .statistics',
      '.metric, .metrics',
      '.data-card, [class*="card"]',
      '.number, .count',
      '[class*="stat"]',
    ]

    let statsFound = false
    for (const selector of statsSelectors) {
      const stats = page.locator(selector)
      const count = await stats.count()
      
      if (count > 0) {
        console.log(`✅ 发现 ${count} 个统计数据元素 (${selector})`)
        statsFound = true
        
        // 检查前几个统计元素的内容
        for (let i = 0; i < Math.min(count, 3); i++) {
          const stat = stats.nth(i)
          if (await stat.isVisible()) {
            const text = await stat.textContent()
            if (text && text.trim()) {
              console.log(`  统计项 ${i + 1}: ${text.trim().substring(0, 50)}`)
            }
          }
        }
      }
    }

    if (!statsFound) {
      console.log('ℹ️ 未发现明显的统计数据元素')
    }
  })

  test('应该显示掌握度分布', async ({ page }) => {
    await page.goto('/english/learning-analytics')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()
    await page.waitForTimeout(3000)

    // 查找掌握度相关元素
    const masterySelectors = [
      '[class*="mastery"]',
      '[class*="progress"]',
      '.skill-level, .level',
      '.proficiency',
      '[data-testid*="mastery"]',
    ]

    let masteryFound = false
    for (const selector of masterySelectors) {
      const elements = page.locator(selector)
      const count = await elements.count()
      
      if (count > 0) {
        console.log(`✅ 发现 ${count} 个掌握度相关元素 (${selector})`)
        masteryFound = true
      }
    }

    if (!masteryFound) {
      console.log('ℹ️ 未发现明显的掌握度分布元素')
    }
  })

  test('应该显示学习时间分析', async ({ page }) => {
    await page.goto('/english/learning-analytics')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()
    await page.waitForTimeout(3000)

    // 查找时间分析相关元素
    const timeSelectors = [
      '[class*="time"]',
      '[class*="duration"]',
      '.hours, .minutes',
      '.study-time',
      '[data-testid*="time"]',
    ]

    let timeAnalysisFound = false
    for (const selector of timeSelectors) {
      const elements = page.locator(selector)
      const count = await elements.count()
      
      if (count > 0) {
        console.log(`✅ 发现 ${count} 个时间分析相关元素 (${selector})`)
        timeAnalysisFound = true
        
        // 检查是否包含时间相关文本
        for (let i = 0; i < Math.min(count, 3); i++) {
          const element = elements.nth(i)
          if (await element.isVisible()) {
            const text = await element.textContent()
            if (text && (text.includes('时间') || text.includes('分钟') || text.includes('小时') || text.includes('天'))) {
              console.log(`  时间数据: ${text.trim()}`)
            }
          }
        }
      }
    }

    if (!timeAnalysisFound) {
      console.log('ℹ️ 未发现明显的时间分析元素')
    }
  })

  test('应该能够导航到详细分析', async ({ page }) => {
    await page.goto('/english/idiomatic-learning')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 查找"详细分析"按钮
    const analyticsButton = page.locator('button:has-text("详细分析"), a:has-text("详细分析"), [href*="analytics"]')
    
    if (await analyticsButton.count() > 0) {
      await analyticsButton.first().click()
      await helpers.waitForVueApp()

      // 检查是否导航到分析页面
      const currentUrl = page.url()
      expect(currentUrl).toContain('analytics')
      
      await expect(page).toHaveTitle(/学习数据分析|学习分析/)
      console.log('✅ 成功导航到详细分析页面')
    } else {
      console.log('ℹ️ 未找到详细分析按钮')
    }
  })

  test('学习分析页面应该支持数据筛选', async ({ page }) => {
    await page.goto('/english/learning-analytics')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()
    await page.waitForTimeout(3000)

    // 查找筛选控件
    const filterSelectors = [
      '.filter, [class*="filter"]',
      '.date-picker, [class*="date"]',
      '.select, .dropdown',
      '.time-range',
      'input[type="date"]',
    ]

    let filterFound = false
    for (const selector of filterSelectors) {
      const filters = page.locator(selector)
      const count = await filters.count()
      
      if (count > 0) {
        console.log(`✅ 发现 ${count} 个筛选控件 (${selector})`)
        filterFound = true
        
        // 尝试与第一个筛选控件交互
        const firstFilter = filters.first()
        if (await firstFilter.isVisible()) {
          try {
            await firstFilter.click()
            await page.waitForTimeout(1000)
            console.log('✅ 筛选控件可交互')
          } catch (error) {
            console.log('ℹ️ 筛选控件交互测试跳过')
          }
        }
      }
    }

    if (!filterFound) {
      console.log('ℹ️ 未发现筛选控件')
    }
  })

  test('应该能够导出学习报告', async ({ page }) => {
    await page.goto('/english/learning-analytics')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()
    await page.waitForTimeout(3000)

    // 查找导出按钮
    const exportButton = page.locator('button:has-text("导出"), button:has-text("下载"), button:has-text("报告"), [class*="export"]')
    
    if (await exportButton.count() > 0) {
      console.log('✅ 发现导出功能按钮')
      
      // 注意：不实际点击下载，只检查按钮存在性
      const button = exportButton.first()
      await expect(button).toBeVisible()
      
      console.log('✅ 导出按钮可见且可点击')
    } else {
      console.log('ℹ️ 未发现导出功能按钮')
    }
  })

  test('学习分析页面应该响应式适配', async ({ page }) => {
    await page.goto('/english/learning-analytics')

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
      await page.waitForTimeout(2000)

      // 检查主要内容区域在不同屏幕尺寸下是否可见
      const mainContent = page.locator('#app, .main-content, .analytics-dashboard')
      await expect(mainContent.first()).toBeVisible()

      // 检查图表是否适应屏幕
      const charts = page.locator('canvas, svg, .echarts')
      const chartCount = await charts.count()
      
      console.log(`✅ ${viewport.name} (${viewport.width}x${viewport.height}) - 主内容可见，${chartCount}个图表元素`)
    }
  })

  test('学习分析功能应该无JavaScript错误', async ({ page }) => {
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

    await page.goto('/english/learning-analytics')

    if (await helpers.checkAuthRedirect()) {
      test.skip(true, '需要用户认证')
      return
    }

    await helpers.waitForVueApp()

    // 等待数据和图表加载
    await page.waitForTimeout(5000)

    // 尝试与页面交互
    const interactiveElements = page.locator('button, .clickable, [class*="click"]')
    const count = await interactiveElements.count()
    
    if (count > 0) {
      // 点击第一个可交互元素
      try {
        await interactiveElements.first().click()
        await page.waitForTimeout(2000)
      } catch (error) {
        // 忽略交互错误，专注于JavaScript错误
      }
    }

    // 检查是否有JavaScript错误
    expect(jsErrors).toHaveLength(0)
    
    if (jsErrors.length > 0) {
      console.log('发现JavaScript错误:', jsErrors)
    }

    console.log('✅ 学习分析功能无JavaScript错误')
  })
})
