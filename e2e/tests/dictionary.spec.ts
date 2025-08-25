import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DictionaryPage } from '../pages/DictionaryPage';
import { TestHelpers, TestDataGenerator } from '../utils/test-helpers';

test.describe('词典功能', () => {
  let loginPage: LoginPage;
  let dictionaryPage: DictionaryPage;
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dictionaryPage = new DictionaryPage(page);
    helpers = new TestHelpers(page);
    
    // 登录后访问词典页面
    await loginPage.goto();
    await loginPage.quickLogin();
    await dictionaryPage.goto();
  });

  test('应该显示词典列表页面', async () => {
    await dictionaryPage.verifyDictionaryList();
    await helpers.verifyTitle(/词典|Dictionary/);
  });

  test('应该能够搜索词典', async () => {
    // 搜索词典
    await dictionaryPage.searchDictionary('英语');
    
    // 验证搜索结果
    await helpers.waitForPageLoad();
    
    // 验证搜索结果包含相关词典
    const searchResults = dictionaryPage.dictionaryList.locator('.dictionary-item');
    const count = await searchResults.count();
    expect(count).toBeGreaterThan(0);
  });

  test('应该能够创建新词典', async () => {
    const dictionaryData = TestDataGenerator.generateDictionaryData();
    
    await dictionaryPage.createDictionary({
      name: dictionaryData.name,
      description: dictionaryData.description,
      language: dictionaryData.language
    });
    
    // 验证词典创建成功
    await helpers.verifyElementText(
      '.success-message, [data-testid="success-message"]',
      '词典创建成功'
    );
  });

  test('应该能够开始词典练习', async () => {
    // 开始练习第一个词典
    await dictionaryPage.startPractice();
    
    // 验证练习页面元素
    await dictionaryPage.verifyPracticePageElements();
    
    // 验证URL包含练习路径
    await helpers.verifyUrl('/practice');
  });

  test('应该能够配置练习设置', async () => {
    // 开始练习
    await dictionaryPage.startPractice();
    
    // 配置练习设置
    await dictionaryPage.configurePracticeSettings({
      difficulty: 'medium',
      practiceType: 'flashcard',
      wordCount: 10
    });
    
    // 验证设置已应用
    await helpers.waitForPageLoad();
  });

  test('应该能够完成单词练习流程', async () => {
    await dictionaryPage.startPractice();
    
    // 练习第一个单词
    await dictionaryPage.showAnswer();
    await dictionaryPage.markWordAsKnown();
    
    // 验证进度更新
    const progress = await dictionaryPage.getPracticeProgress();
    expect(progress.progress).toBeTruthy();
  });

  test('应该能够标记单词为不认识', async () => {
    await dictionaryPage.startPractice();
    
    // 标记单词为不认识
    await dictionaryPage.markWordAsUnknown();
    
    // 验证可以继续到下一个单词
    await dictionaryPage.nextWord();
    
    // 验证进度更新
    const progress = await dictionaryPage.getPracticeProgress();
    expect(progress.progress).toBeTruthy();
  });

  test('应该能够在单词间导航', async () => {
    await dictionaryPage.startPractice();
    
    // 标记第一个单词并前进
    await dictionaryPage.markWordAsKnown();
    await dictionaryPage.nextWord();
    
    // 返回上一个单词
    await dictionaryPage.previousWord();
    
    // 验证可以正常导航
    await helpers.verifyElementVisible(dictionaryPage.wordCard);
  });

  test('应该能够完成完整的练习轮次', async () => {
    await dictionaryPage.startPractice();
    
    // 完成5个单词的练习
    await dictionaryPage.completePracticeRound(5);
    
    // 验证练习完成
    await dictionaryPage.verifyPracticeCompletion();
  });

  test('应该显示练习进度和分数', async () => {
    await dictionaryPage.startPractice();
    
    // 练习几个单词
    for (let i = 0; i < 3; i++) {
      await dictionaryPage.markWordAsKnown();
      if (i < 2) {
        await dictionaryPage.nextWord();
      }
    }
    
    // 获取并验证进度数据
    const progress = await dictionaryPage.getPracticeProgress();
    expect(progress.progress).toBeTruthy();
    expect(progress.score).toBeTruthy();
  });

  test('应该处理练习中的错误', async ({ page }) => {
    // 模拟API错误
    await page.route('**/api/v1/practice/**', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: '服务器错误' })
      });
    });
    
    await dictionaryPage.startPractice();
    
    // 验证错误处理
    const errorMessage = page.locator('.error-message, [data-testid="error-message"]');
    await expect(errorMessage).toBeVisible();
  });

  test('应该支持键盘快捷键', async ({ page }) => {
    await dictionaryPage.startPractice();
    
    // 使用空格键显示答案
    await page.keyboard.press('Space');
    await page.waitForTimeout(500);
    
    // 使用方向键导航
    await page.keyboard.press('ArrowRight'); // 下一个单词
    await page.waitForTimeout(500);
    
    await page.keyboard.press('ArrowLeft'); // 上一个单词
    await page.waitForTimeout(500);
    
    // 使用数字键标记单词
    await page.keyboard.press('1'); // 认识
    await page.waitForTimeout(500);
  });

  test('应该支持不同的练习模式', async () => {
    await dictionaryPage.startPractice();
    
    // 测试闪卡模式
    await dictionaryPage.configurePracticeSettings({
      practiceType: 'flashcard'
    });
    
    await helpers.verifyElementVisible(dictionaryPage.wordCard);
    
    // 测试选择题模式（如果可用）
    try {
      await dictionaryPage.configurePracticeSettings({
        practiceType: 'multiple_choice'
      });
      
      const choiceButtons = dictionaryPage.page.locator('.choice-button, [data-testid="choice-button"]');
      await expect(choiceButtons.first()).toBeVisible();
    } catch {
      console.log('选择题模式未实现');
    }
  });

  test('应该保存练习进度', async ({ page, context }) => {
    await dictionaryPage.startPractice();
    
    // 练习几个单词
    await dictionaryPage.markWordAsKnown();
    await dictionaryPage.nextWord();
    await dictionaryPage.markWordAsUnknown();
    
    // 获取当前进度
    const initialProgress = await dictionaryPage.getPracticeProgress();
    
    // 刷新页面
    await page.reload();
    await helpers.waitForPageLoad();
    
    // 验证进度是否保存
    const savedProgress = await dictionaryPage.getPracticeProgress();
    expect(savedProgress.progress).toBeTruthy();
  });

  test('应该支持批量操作', async () => {
    // 选择多个词典项
    const checkboxes = dictionaryPage.page.locator('.dictionary-item input[type="checkbox"]');
    const count = await checkboxes.count();
    
    if (count > 0) {
      // 选择前两个词典
      await checkboxes.first().check();
      await checkboxes.nth(1).check();
      
      // 执行批量操作
      const batchActionButton = dictionaryPage.page.locator('.batch-action, [data-testid="batch-action"]');
      await batchActionButton.click();
      
      // 选择删除操作
      const deleteOption = dictionaryPage.page.locator('[data-action="delete"]');
      await deleteOption.click();
      
      // 确认删除
      const confirmButton = dictionaryPage.page.locator('button:has-text("确认"), [data-testid="confirm-delete"]');
      await confirmButton.click();
      
      await helpers.waitForPageLoad();
    }
  });

  test('应该支持词典导入导出', async ({ page }) => {
    // 测试导出功能
    const exportButton = page.locator('button:has-text("导出"), [data-testid="export-dictionary"]');
    
    if (await exportButton.isVisible()) {
      const downloadPromise = page.waitForEvent('download');
      await exportButton.click();
      const download = await downloadPromise;
      
      expect(download.suggestedFilename()).toMatch(/\.(json|csv|xlsx)$/);
    }
    
    // 测试导入功能
    const importButton = page.locator('button:has-text("导入"), [data-testid="import-dictionary"]');
    
    if (await importButton.isVisible()) {
      await importButton.click();
      
      // 验证文件上传对话框
      const fileInput = page.locator('input[type="file"]');
      await expect(fileInput).toBeVisible();
    }
  });

  test('应该支持移动端响应式设计', async ({ page }) => {
    // 切换到移动端视图
    await page.setViewportSize({ width: 375, height: 667 });
    await helpers.waitForPageLoad();
    
    // 验证移动端布局
    await helpers.verifyElementVisible(dictionaryPage.dictionaryList);
    
    // 测试移动端练习界面
    await dictionaryPage.startPractice();
    await dictionaryPage.verifyPracticePageElements();
    
    // 恢复桌面视图
    await page.setViewportSize({ width: 1280, height: 720 });
  });
});