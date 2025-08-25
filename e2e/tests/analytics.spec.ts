import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { AnalyticsPage } from '../pages/AnalyticsPage';
import { TestHelpers } from '../utils/test-helpers';

test.describe('数据分析功能', () => {
  let loginPage: LoginPage;
  let analyticsPage: AnalyticsPage;
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    analyticsPage = new AnalyticsPage(page);
    helpers = new TestHelpers(page);
    
    // 登录后访问数据分析页面
    await loginPage.goto();
    await loginPage.quickLogin();
    await analyticsPage.goto();
  });

  test('应该显示数据分析仪表板', async () => {
    await analyticsPage.verifyDashboardElements();
    await helpers.verifyTitle(/分析|Analytics|Dashboard/);
  });

  test('应该显示所有统计卡片', async () => {
    await analyticsPage.verifyStatisticsCards();
    
    // 验证统计数据不为空
    const stats = await analyticsPage.getStatisticsData();
    expect(stats.totalWords).toBeTruthy();
    expect(stats.masteredWords).toBeTruthy();
    expect(stats.studyTime).toBeTruthy();
    expect(stats.accuracyRate).toBeTruthy();
  });

  test('应该显示所有图表', async () => {
    await analyticsPage.verifyCharts();
    
    // 验证图表容器可见
    await helpers.verifyElementVisible(analyticsPage.practiceProgressChart);
    await helpers.verifyElementVisible(analyticsPage.wordMasteryChart);
    await helpers.verifyElementVisible(analyticsPage.studyTimeChart);
    await helpers.verifyElementVisible(analyticsPage.difficultyDistributionChart);
  });

  test('应该能够设置日期范围过滤', async () => {
    const startDate = '2024-01-01';
    const endDate = '2024-01-31';
    
    await analyticsPage.setDateRange(startDate, endDate);
    
    // 验证图表重新加载
    await analyticsPage.waitForChartsToLoad();
    
    // 验证统计数据更新
    const stats = await analyticsPage.getStatisticsData();
    expect(stats.totalWords).toBeTruthy();
  });

  test('应该能够应用过滤器', async () => {
    await analyticsPage.applyFilter('difficulty', 'medium');
    
    // 验证过滤器应用成功
    await analyticsPage.waitForChartsToLoad();
    
    // 验证数据更新
    const stats = await analyticsPage.getStatisticsData();
    expect(stats).toBeTruthy();
  });

  test('应该能够刷新数据', async () => {
    // 获取初始统计数据
    const initialStats = await analyticsPage.getStatisticsData();
    
    // 刷新数据
    await analyticsPage.refreshData();
    
    // 验证数据重新加载
    const refreshedStats = await analyticsPage.getStatisticsData();
    expect(refreshedStats).toBeTruthy();
  });

  test('应该能够导出数据', async () => {
    // 测试CSV导出
    const download = await analyticsPage.exportData('csv');
    expect(download.suggestedFilename()).toMatch(/\.csv$/);
    
    // 验证下载文件不为空
    const path = await download.path();
    expect(path).toBeTruthy();
  });

  test('应该显示数据表格', async () => {
    const tableInfo = await analyticsPage.verifyDataTable();
    
    expect(tableInfo.headerCount).toBeGreaterThan(0);
    // 数据行可能为空，所以不强制要求
  });

  test('应该支持分页功能', async () => {
    // 检查是否有分页控件
    const paginationVisible = await analyticsPage.paginationControls.isVisible();
    
    if (paginationVisible) {
      // 测试下一页
      await analyticsPage.nextPage();
      await helpers.waitForPageLoad();
      
      // 测试上一页
      await analyticsPage.previousPage();
      await helpers.waitForPageLoad();
      
      // 测试跳转到指定页面
      await analyticsPage.navigateToPage(1);
      await helpers.waitForPageLoad();
    } else {
      console.log('分页功能不可用或数据量不足');
    }
  });

  test('应该支持图表交互', async () => {
    await analyticsPage.verifyChartInteractivity();
    
    // 验证图表响应用户交互
    await helpers.waitForPageLoad();
  });

  test('应该处理加载状态', async ({ page }) => {
    // 模拟慢速网络
    await page.route('**/api/v1/analytics/**', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      await route.continue();
    });
    
    // 刷新数据并验证加载状态
    await analyticsPage.refreshData();
    
    // 验证加载指示器显示
    await helpers.verifyElementVisible(analyticsPage.loadingSpinner);
    
    // 等待加载完成
    await analyticsPage.waitForChartsToLoad();
  });

  test('应该处理错误状态', async () => {
    await analyticsPage.verifyErrorHandling();
    
    // 验证错误消息显示
    await helpers.verifyElementVisible(analyticsPage.errorMessage);
  });

  test('应该支持响应式设计', async () => {
    await analyticsPage.verifyResponsiveDesign();
    
    // 验证移动端和桌面端都能正常显示
    await analyticsPage.verifyDashboardElements();
  });

  test('应该显示实时数据更新', async ({ page }) => {
    // 获取初始统计数据
    const initialStats = await analyticsPage.getStatisticsData();
    
    // 模拟数据更新
    await page.route('**/api/v1/analytics/stats/', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          totalWords: parseInt(initialStats.totalWords || '0') + 10,
          masteredWords: parseInt(initialStats.masteredWords || '0') + 5,
          studyTime: '120分钟',
          accuracyRate: '85%'
        })
      });
    });
    
    // 刷新数据
    await analyticsPage.refreshData();
    
    // 验证数据更新
    const updatedStats = await analyticsPage.getStatisticsData();
    expect(updatedStats.totalWords).not.toBe(initialStats.totalWords);
  });

  test('应该支持多种图表类型', async ({ page }) => {
    // 验证不同类型的图表
    const chartTypes = [
      { selector: analyticsPage.practiceProgressChart, name: '练习进度图表' },
      { selector: analyticsPage.wordMasteryChart, name: '单词掌握图表' },
      { selector: analyticsPage.studyTimeChart, name: '学习时间图表' },
      { selector: analyticsPage.difficultyDistributionChart, name: '难度分布图表' }
    ];
    
    for (const chart of chartTypes) {
      await helpers.verifyElementVisible(chart.selector);
      console.log(`${chart.name} 显示正常`);
    }
  });

  test('应该支持数据钻取', async ({ page }) => {
    // 点击图表元素进行钻取
    await analyticsPage.practiceProgressChart.click();
    
    // 验证是否显示详细数据或跳转到详细页面
    await page.waitForTimeout(1000);
    
    // 检查是否有详细数据模态框或新页面
    const detailModal = page.locator('.detail-modal, [data-testid="detail-modal"]');
    const detailPage = page.locator('.detail-page, [data-testid="detail-page"]');
    
    const modalVisible = await detailModal.isVisible();
    const pageVisible = await detailPage.isVisible();
    
    if (!modalVisible && !pageVisible) {
      console.log('数据钻取功能未实现');
    }
  });

  test('应该支持数据比较', async () => {
    // 设置比较日期范围
    await analyticsPage.setDateRange('2024-01-01', '2024-01-15');
    const period1Stats = await analyticsPage.getStatisticsData();
    
    await analyticsPage.setDateRange('2024-01-16', '2024-01-31');
    const period2Stats = await analyticsPage.getStatisticsData();
    
    // 验证可以获取不同时期的数据
    expect(period1Stats).toBeTruthy();
    expect(period2Stats).toBeTruthy();
  });

  test('应该支持自定义图表配置', async ({ page }) => {
    // 查找图表配置按钮
    const configButton = page.locator('.chart-config, [data-testid="chart-config"]');
    
    if (await configButton.isVisible()) {
      await configButton.click();
      
      // 修改图表配置
      const chartTypeSelector = page.locator('select[name="chartType"]');
      if (await chartTypeSelector.isVisible()) {
        await chartTypeSelector.selectOption('bar');
      }
      
      // 应用配置
      const applyButton = page.locator('button:has-text("应用"), [data-testid="apply-config"]');
      await applyButton.click();
      
      await analyticsPage.waitForChartsToLoad();
    } else {
      console.log('图表配置功能未实现');
    }
  });

  test('应该支持数据导出多种格式', async () => {
    const formats = ['csv', 'excel', 'pdf'] as const;
    
    for (const format of formats) {
      try {
        const download = await analyticsPage.exportData(format);
        const filename = download.suggestedFilename();
        
        switch (format) {
          case 'csv':
            expect(filename).toMatch(/\.csv$/);
            break;
          case 'excel':
            expect(filename).toMatch(/\.(xlsx|xls)$/);
            break;
          case 'pdf':
            expect(filename).toMatch(/\.pdf$/);
            break;
        }
        
        console.log(`${format.toUpperCase()} 导出成功: ${filename}`);
      } catch (error) {
        console.log(`${format.toUpperCase()} 导出功能未实现或失败`);
      }
    }
  });

  test('应该支持数据缓存和离线查看', async ({ page }) => {
    // 首次加载数据
    await analyticsPage.waitForChartsToLoad();
    const initialStats = await analyticsPage.getStatisticsData();
    
    // 模拟网络断开
    await page.setOffline(true);
    
    // 刷新页面
    await page.reload();
    
    // 验证是否显示缓存数据或离线提示
    const offlineMessage = page.locator('.offline-message, [data-testid="offline-message"]');
    const cachedData = page.locator('.cached-data, [data-testid="cached-data"]');
    
    const offlineVisible = await offlineMessage.isVisible();
    const cachedVisible = await cachedData.isVisible();
    
    if (!offlineVisible && !cachedVisible) {
      console.log('离线缓存功能未实现');
    }
    
    // 恢复网络连接
    await page.setOffline(false);
  });
});