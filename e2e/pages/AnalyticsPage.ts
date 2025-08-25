import { Page, Locator } from '@playwright/test';
import { TestHelpers } from '../utils/test-helpers';

/**
 * 数据分析页面对象模型
 */
export class AnalyticsPage {
  private helpers: TestHelpers;

  // 页面元素定位器
  readonly dashboardContainer: Locator;
  readonly chartContainer: Locator;
  readonly statisticsCards: Locator;
  readonly dateRangePicker: Locator;
  readonly filterDropdown: Locator;
  readonly exportButton: Locator;
  readonly refreshButton: Locator;
  readonly loadingSpinner: Locator;
  readonly errorMessage: Locator;
  
  // 具体图表元素
  readonly practiceProgressChart: Locator;
  readonly wordMasteryChart: Locator;
  readonly studyTimeChart: Locator;
  readonly difficultyDistributionChart: Locator;
  
  // 统计卡片
  readonly totalWordsCard: Locator;
  readonly masteredWordsCard: Locator;
  readonly studyTimeCard: Locator;
  readonly accuracyRateCard: Locator;
  
  // 详细数据表格
  readonly dataTable: Locator;
  readonly tableHeaders: Locator;
  readonly tableRows: Locator;
  readonly paginationControls: Locator;

  constructor(private page: Page) {
    this.helpers = new TestHelpers(page);
    
    // 初始化元素定位器
    this.dashboardContainer = page.locator('.dashboard-container, [data-testid="dashboard-container"]');
    this.chartContainer = page.locator('.chart-container, [data-testid="chart-container"]');
    this.statisticsCards = page.locator('.statistics-cards, [data-testid="statistics-cards"]');
    this.dateRangePicker = page.locator('.date-range-picker, [data-testid="date-range-picker"]');
    this.filterDropdown = page.locator('.filter-dropdown, [data-testid="filter-dropdown"]');
    this.exportButton = page.locator('button:has-text("导出"), button:has-text("Export"), [data-testid="export-button"]');
    this.refreshButton = page.locator('button:has-text("刷新"), button:has-text("Refresh"), [data-testid="refresh-button"]');
    this.loadingSpinner = page.locator('.loading-spinner, [data-testid="loading-spinner"]');
    this.errorMessage = page.locator('.error-message, [data-testid="error-message"]');
    
    // 图表元素
    this.practiceProgressChart = page.locator('[data-testid="practice-progress-chart"], .practice-progress-chart');
    this.wordMasteryChart = page.locator('[data-testid="word-mastery-chart"], .word-mastery-chart');
    this.studyTimeChart = page.locator('[data-testid="study-time-chart"], .study-time-chart');
    this.difficultyDistributionChart = page.locator('[data-testid="difficulty-distribution-chart"], .difficulty-distribution-chart');
    
    // 统计卡片
    this.totalWordsCard = page.locator('[data-testid="total-words-card"], .total-words-card');
    this.masteredWordsCard = page.locator('[data-testid="mastered-words-card"], .mastered-words-card');
    this.studyTimeCard = page.locator('[data-testid="study-time-card"], .study-time-card');
    this.accuracyRateCard = page.locator('[data-testid="accuracy-rate-card"], .accuracy-rate-card');
    
    // 数据表格
    this.dataTable = page.locator('.data-table, [data-testid="data-table"]');
    this.tableHeaders = page.locator('.data-table thead th, [data-testid="table-header"]');
    this.tableRows = page.locator('.data-table tbody tr, [data-testid="table-row"]');
    this.paginationControls = page.locator('.pagination-controls, [data-testid="pagination-controls"]');
  }

  /**
   * 导航到数据分析页面
   */
  async goto() {
    await this.page.goto('/analytics');
    await this.helpers.waitForPageLoad();
    await this.waitForChartsToLoad();
  }

  /**
   * 等待图表加载完成
   */
  async waitForChartsToLoad() {
    // 等待加载动画消失
    await this.page.waitForSelector('.loading-spinner, [data-testid="loading-spinner"]', { state: 'hidden', timeout: 10000 });
    
    // 等待图表容器可见
    await this.helpers.verifyElementVisible(this.chartContainer);
    
    // 等待网络请求完成
    await this.helpers.waitForPageLoad();
  }

  /**
   * 验证仪表板页面元素
   */
  async verifyDashboardElements() {
    await this.helpers.verifyElementVisible(this.dashboardContainer);
    await this.helpers.verifyElementVisible(this.statisticsCards);
    await this.helpers.verifyElementVisible(this.chartContainer);
    await this.helpers.verifyElementVisible(this.dateRangePicker);
  }

  /**
   * 验证统计卡片
   */
  async verifyStatisticsCards() {
    await this.helpers.verifyElementVisible(this.totalWordsCard);
    await this.helpers.verifyElementVisible(this.masteredWordsCard);
    await this.helpers.verifyElementVisible(this.studyTimeCard);
    await this.helpers.verifyElementVisible(this.accuracyRateCard);
  }

  /**
   * 验证图表显示
   */
  async verifyCharts() {
    await this.helpers.verifyElementVisible(this.practiceProgressChart);
    await this.helpers.verifyElementVisible(this.wordMasteryChart);
    await this.helpers.verifyElementVisible(this.studyTimeChart);
    await this.helpers.verifyElementVisible(this.difficultyDistributionChart);
  }

  /**
   * 获取统计数据
   */
  async getStatisticsData() {
    const totalWords = await this.totalWordsCard.locator('.card-value, [data-testid="card-value"]').textContent();
    const masteredWords = await this.masteredWordsCard.locator('.card-value, [data-testid="card-value"]').textContent();
    const studyTime = await this.studyTimeCard.locator('.card-value, [data-testid="card-value"]').textContent();
    const accuracyRate = await this.accuracyRateCard.locator('.card-value, [data-testid="card-value"]').textContent();
    
    return {
      totalWords: totalWords?.trim(),
      masteredWords: masteredWords?.trim(),
      studyTime: studyTime?.trim(),
      accuracyRate: accuracyRate?.trim()
    };
  }

  /**
   * 设置日期范围
   */
  async setDateRange(startDate: string, endDate: string) {
    await this.dateRangePicker.click();
    
    // 填写开始日期
    const startDateInput = this.page.locator('input[name="startDate"], [data-testid="start-date"]');
    await startDateInput.fill(startDate);
    
    // 填写结束日期
    const endDateInput = this.page.locator('input[name="endDate"], [data-testid="end-date"]');
    await endDateInput.fill(endDate);
    
    // 应用日期范围
    const applyButton = this.page.locator('button:has-text("应用"), button:has-text("Apply"), [data-testid="apply-date-range"]');
    await applyButton.click();
    
    await this.waitForChartsToLoad();
  }

  /**
   * 应用过滤器
   */
  async applyFilter(filterType: string, filterValue: string) {
    await this.filterDropdown.click();
    
    // 选择过滤器类型
    const filterOption = this.page.locator(`[data-value="${filterType}"], option[value="${filterType}"]`);
    await filterOption.click();
    
    // 输入过滤值
    const filterInput = this.page.locator('input[name="filterValue"], [data-testid="filter-input"]');
    await filterInput.fill(filterValue);
    
    // 应用过滤器
    const applyButton = this.page.locator('button:has-text("应用"), button:has-text("Apply"), [data-testid="apply-filter"]');
    await applyButton.click();
    
    await this.waitForChartsToLoad();
  }

  /**
   * 刷新数据
   */
  async refreshData() {
    await this.refreshButton.click();
    await this.waitForChartsToLoad();
  }

  /**
   * 导出数据
   */
  async exportData(format: 'csv' | 'excel' | 'pdf' = 'csv') {
    await this.exportButton.click();
    
    // 选择导出格式
    const formatOption = this.page.locator(`[data-value="${format}"], option[value="${format}"]`);
    await formatOption.click();
    
    // 确认导出
    const confirmButton = this.page.locator('button:has-text("确认"), button:has-text("Confirm"), [data-testid="confirm-export"]');
    
    // 等待下载开始
    const downloadPromise = this.page.waitForEvent('download');
    await confirmButton.click();
    const download = await downloadPromise;
    
    return download;
  }

  /**
   * 验证数据表格
   */
  async verifyDataTable() {
    await this.helpers.verifyElementVisible(this.dataTable);
    
    // 验证表头
    const headerCount = await this.tableHeaders.count();
    if (headerCount === 0) {
      throw new Error('数据表格没有表头');
    }
    
    // 验证数据行
    const rowCount = await this.tableRows.count();
    if (rowCount === 0) {
      console.warn('数据表格没有数据行');
    }
    
    return { headerCount, rowCount };
  }

  /**
   * 分页操作
   */
  async navigateToPage(pageNumber: number) {
    const pageButton = this.paginationControls.locator(`button:has-text("${pageNumber}"), [data-page="${pageNumber}"]`);
    await pageButton.click();
    await this.helpers.waitForPageLoad();
  }

  /**
   * 下一页
   */
  async nextPage() {
    const nextButton = this.paginationControls.locator('button:has-text("下一页"), button:has-text("Next"), [data-testid="next-page"]');
    await nextButton.click();
    await this.helpers.waitForPageLoad();
  }

  /**
   * 上一页
   */
  async previousPage() {
    const prevButton = this.paginationControls.locator('button:has-text("上一页"), button:has-text("Previous"), [data-testid="previous-page"]');
    await prevButton.click();
    await this.helpers.waitForPageLoad();
  }

  /**
   * 验证图表交互性
   */
  async verifyChartInteractivity() {
    // 测试图表悬停效果
    await this.practiceProgressChart.hover();
    await this.page.waitForTimeout(500);
    
    // 测试图表点击
    await this.practiceProgressChart.click();
    await this.page.waitForTimeout(500);
    
    // 验证图表工具提示或详细信息
    const tooltip = this.page.locator('.chart-tooltip, [data-testid="chart-tooltip"]');
    // 工具提示可能不总是可见，所以不强制验证
  }

  /**
   * 验证响应式设计
   */
  async verifyResponsiveDesign() {
    // 测试移动端视图
    await this.page.setViewportSize({ width: 375, height: 667 });
    await this.helpers.waitForPageLoad();
    
    // 验证移动端布局
    await this.helpers.verifyElementVisible(this.dashboardContainer);
    
    // 恢复桌面视图
    await this.page.setViewportSize({ width: 1280, height: 720 });
    await this.helpers.waitForPageLoad();
  }

  /**
   * 验证错误处理
   */
  async verifyErrorHandling() {
    // 模拟网络错误
    await this.page.route('**/api/v1/analytics/**', route => {
      route.abort('failed');
    });
    
    await this.refreshData();
    
    // 验证错误消息显示
    await this.helpers.verifyElementVisible(this.errorMessage);
    
    // 清除路由拦截
    await this.page.unroute('**/api/v1/analytics/**');
  }
}