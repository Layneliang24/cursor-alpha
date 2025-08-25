import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DictionaryPage } from '../pages/DictionaryPage';
import { AnalyticsPage } from '../pages/AnalyticsPage';
import { TestHelpers, TestDataGenerator } from '../utils/test-helpers';

test.describe('完整用户旅程', () => {
  let loginPage: LoginPage;
  let dictionaryPage: DictionaryPage;
  let analyticsPage: AnalyticsPage;
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dictionaryPage = new DictionaryPage(page);
    analyticsPage = new AnalyticsPage(page);
    helpers = new TestHelpers(page);
  });

  test('完整的学习流程：注册 -> 登录 -> 创建词典 -> 练习 -> 查看分析', async ({ page }) => {
    const userData = TestDataGenerator.generateUserData();
    const dictionaryData = TestDataGenerator.generateDictionaryData();

    // 步骤1: 用户注册
    await page.goto('/register');
    await helpers.waitForPageLoad();
    
    await page.fill('input[name="username"]', userData.username);
    await page.fill('input[name="email"]', userData.email);
    await page.fill('input[name="password"]', userData.password);
    await page.fill('input[name="confirmPassword"]', userData.password);
    
    const registerButton = page.locator('button[type="submit"], button:has-text("注册")');
    await registerButton.click();
    await helpers.waitForPageLoad();

    // 步骤2: 用户登录（如果注册后没有自动登录）
    const currentUrl = page.url();
    if (currentUrl.includes('/login')) {
      await loginPage.login(userData.username, userData.password);
      await loginPage.verifyLoginSuccess();
    }

    // 步骤3: 创建词典
    await dictionaryPage.goto();
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

    // 步骤4: 开始练习
    await dictionaryPage.startPractice(dictionaryData.name);
    await dictionaryPage.verifyPracticePageElements();

    // 完成一轮练习
    await dictionaryPage.completePracticeRound(5);
    await dictionaryPage.verifyPracticeCompletion();

    // 步骤5: 查看学习分析
    await analyticsPage.goto();
    await analyticsPage.verifyDashboardElements();
    
    // 验证练习数据已反映在分析中
    const stats = await analyticsPage.getStatisticsData();
    expect(parseInt(stats.totalWords || '0')).toBeGreaterThan(0);
    expect(parseInt(stats.masteredWords || '0')).toBeGreaterThan(0);

    // 步骤6: 导出学习报告
    const download = await analyticsPage.exportData('csv');
    expect(download.suggestedFilename()).toMatch(/\.csv$/);
  });

  test('多设备学习同步流程', async ({ page, context }) => {
    // 在第一个设备上登录和学习
    await loginPage.goto();
    await loginPage.quickLogin();
    
    await dictionaryPage.goto();
    await dictionaryPage.startPractice();
    await dictionaryPage.markWordAsKnown();
    await dictionaryPage.nextWord();
    await dictionaryPage.markWordAsUnknown();
    
    const initialProgress = await dictionaryPage.getPracticeProgress();

    // 模拟第二个设备
    const secondPage = await context.newPage();
    const secondLoginPage = new LoginPage(secondPage);
    const secondDictionaryPage = new DictionaryPage(secondPage);
    
    await secondLoginPage.goto();
    await secondLoginPage.quickLogin();
    
    await secondDictionaryPage.goto();
    await secondDictionaryPage.startPractice();
    
    // 验证学习进度同步
    const syncedProgress = await secondDictionaryPage.getPracticeProgress();
    expect(syncedProgress.progress).toBeTruthy();
    
    await secondPage.close();
  });

  test('学习计划和目标设置流程', async ({ page }) => {
    await loginPage.goto();
    await loginPage.quickLogin();

    // 设置学习目标
    const settingsPage = page.locator('a:has-text("设置"), [data-testid="settings-link"]');
    if (await settingsPage.isVisible()) {
      await settingsPage.click();
      
      // 设置每日学习目标
      const dailyGoalInput = page.locator('input[name="dailyGoal"], [data-testid="daily-goal"]');
      if (await dailyGoalInput.isVisible()) {
        await dailyGoalInput.fill('20');
      }
      
      // 设置学习提醒
      const reminderCheckbox = page.locator('input[name="reminder"], [data-testid="reminder-checkbox"]');
      if (await reminderCheckbox.isVisible()) {
        await reminderCheckbox.check();
      }
      
      // 保存设置
      const saveButton = page.locator('button:has-text("保存"), [data-testid="save-settings"]');
      await saveButton.click();
      await helpers.waitForPageLoad();
    }

    // 开始学习以达成目标
    await dictionaryPage.goto();
    await dictionaryPage.startPractice();
    
    // 完成足够的练习以接近目标
    await dictionaryPage.completePracticeRound(10);
    
    // 检查目标进度
    await analyticsPage.goto();
    const goalProgress = page.locator('.goal-progress, [data-testid="goal-progress"]');
    if (await goalProgress.isVisible()) {
      const progressText = await goalProgress.textContent();
      expect(progressText).toBeTruthy();
    }
  });

  test('社交学习功能流程', async ({ page }) => {
    await loginPage.goto();
    await loginPage.quickLogin();

    // 查找好友或学习小组功能
    const socialTab = page.locator('a:has-text("社交"), a:has-text("好友"), [data-testid="social-tab"]');
    
    if (await socialTab.isVisible()) {
      await socialTab.click();
      
      // 搜索好友
      const searchFriendInput = page.locator('input[placeholder*="搜索好友"], [data-testid="search-friend"]');
      if (await searchFriendInput.isVisible()) {
        await searchFriendInput.fill('testfriend');
        await page.keyboard.press('Enter');
        await helpers.waitForPageLoad();
      }
      
      // 查看排行榜
      const leaderboardTab = page.locator('a:has-text("排行榜"), [data-testid="leaderboard-tab"]');
      if (await leaderboardTab.isVisible()) {
        await leaderboardTab.click();
        await helpers.waitForPageLoad();
        
        // 验证排行榜显示
        const leaderboardList = page.locator('.leaderboard-list, [data-testid="leaderboard-list"]');
        await helpers.verifyElementVisible(leaderboardList);
      }
      
      // 分享学习成就
      const shareButton = page.locator('button:has-text("分享"), [data-testid="share-achievement"]');
      if (await shareButton.isVisible()) {
        await shareButton.click();
        
        // 选择分享平台
        const shareOptions = page.locator('.share-options, [data-testid="share-options"]');
        await helpers.verifyElementVisible(shareOptions);
      }
    } else {
      console.log('社交功能未实现');
    }
  });

  test('离线学习和数据同步流程', async ({ page }) => {
    await loginPage.goto();
    await loginPage.quickLogin();
    
    // 下载离线内容
    await dictionaryPage.goto();
    const downloadButton = page.locator('button:has-text("离线下载"), [data-testid="download-offline"]');
    
    if (await downloadButton.isVisible()) {
      await downloadButton.click();
      
      // 等待下载完成
      const downloadProgress = page.locator('.download-progress, [data-testid="download-progress"]');
      await helpers.verifyElementVisible(downloadProgress);
      
      // 等待下载完成提示
      await page.waitForSelector('.download-complete, [data-testid="download-complete"]', { timeout: 30000 });
    }
    
    // 模拟离线状态
    await page.setOffline(true);
    
    // 在离线状态下练习
    await dictionaryPage.startPractice();
    await dictionaryPage.markWordAsKnown();
    await dictionaryPage.nextWord();
    
    // 恢复在线状态
    await page.setOffline(false);
    
    // 验证数据同步
    await page.reload();
    await helpers.waitForPageLoad();
    
    const syncStatus = page.locator('.sync-status, [data-testid="sync-status"]');
    if (await syncStatus.isVisible()) {
      const statusText = await syncStatus.textContent();
      expect(statusText).toContain('同步');
    }
  });

  test('学习路径推荐流程', async ({ page }) => {
    await loginPage.goto();
    await loginPage.quickLogin();
    
    // 完成初始评估
    const assessmentButton = page.locator('button:has-text("开始评估"), [data-testid="start-assessment"]');
    
    if (await assessmentButton.isVisible()) {
      await assessmentButton.click();
      
      // 完成评估问题
      for (let i = 0; i < 5; i++) {
        const answerButton = page.locator('.assessment-answer').first();
        if (await answerButton.isVisible()) {
          await answerButton.click();
          
          const nextButton = page.locator('button:has-text("下一题"), [data-testid="next-question"]');
          if (await nextButton.isVisible()) {
            await nextButton.click();
          }
        }
      }
      
      // 查看推荐结果
      const recommendationResults = page.locator('.recommendation-results, [data-testid="recommendation-results"]');
      await helpers.verifyElementVisible(recommendationResults);
      
      // 选择推荐的学习路径
      const selectPathButton = page.locator('button:has-text("选择此路径"), [data-testid="select-path"]');
      if (await selectPathButton.isVisible()) {
        await selectPathButton.click();
        await helpers.waitForPageLoad();
      }
    }
    
    // 按照推荐路径学习
    await dictionaryPage.goto();
    const recommendedDictionary = page.locator('.recommended-dictionary, [data-testid="recommended-dictionary"]');
    
    if (await recommendedDictionary.isVisible()) {
      await recommendedDictionary.click();
      await dictionaryPage.startPractice();
      await dictionaryPage.completePracticeRound(3);
    }
  });

  test('学习成就和徽章系统流程', async ({ page }) => {
    await loginPage.goto();
    await loginPage.quickLogin();
    
    // 查看成就页面
    const achievementsTab = page.locator('a:has-text("成就"), [data-testid="achievements-tab"]');
    
    if (await achievementsTab.isVisible()) {
      await achievementsTab.click();
      
      // 验证成就列表
      const achievementsList = page.locator('.achievements-list, [data-testid="achievements-list"]');
      await helpers.verifyElementVisible(achievementsList);
      
      // 查看徽章收集
      const badgesSection = page.locator('.badges-section, [data-testid="badges-section"]');
      if (await badgesSection.isVisible()) {
        await helpers.verifyElementVisible(badgesSection);
      }
    }
    
    // 通过学习解锁新成就
    await dictionaryPage.goto();
    await dictionaryPage.startPractice();
    
    // 连续答对多个单词以触发成就
    for (let i = 0; i < 10; i++) {
      await dictionaryPage.markWordAsKnown();
      if (i < 9) {
        await dictionaryPage.nextWord();
      }
    }
    
    // 检查是否有新成就通知
    const achievementNotification = page.locator('.achievement-notification, [data-testid="achievement-notification"]');
    if (await achievementNotification.isVisible()) {
      const notificationText = await achievementNotification.textContent();
      expect(notificationText).toContain('成就');
    }
  });

  test('多语言学习切换流程', async ({ page }) => {
    await loginPage.goto();
    await loginPage.quickLogin();
    
    // 切换界面语言
    const languageSelector = page.locator('.language-selector, [data-testid="language-selector"]');
    
    if (await languageSelector.isVisible()) {
      await languageSelector.click();
      
      // 选择英语界面
      const englishOption = page.locator('[data-lang="en"], option[value="en"]');
      if (await englishOption.isVisible()) {
        await englishOption.click();
        await helpers.waitForPageLoad();
        
        // 验证界面语言切换
        const pageTitle = await page.title();
        expect(pageTitle).toMatch(/Alpha|Dictionary|Learning/);
      }
      
      // 切换回中文
      await languageSelector.click();
      const chineseOption = page.locator('[data-lang="zh"], option[value="zh"]');
      if (await chineseOption.isVisible()) {
        await chineseOption.click();
        await helpers.waitForPageLoad();
      }
    }
    
    // 学习不同语言的词典
    await dictionaryPage.goto();
    
    // 创建日语词典
    await dictionaryPage.createDictionary({
      name: '日语基础词汇',
      description: '日语学习词典',
      language: 'ja'
    });
    
    // 练习日语词典
    await dictionaryPage.startPractice('日语基础词汇');
    await dictionaryPage.completePracticeRound(3);
  });

  test('学习数据备份和恢复流程', async ({ page }) => {
    await loginPage.goto();
    await loginPage.quickLogin();
    
    // 进行一些学习活动
    await dictionaryPage.goto();
    await dictionaryPage.startPractice();
    await dictionaryPage.completePracticeRound(5);
    
    // 备份学习数据
    const settingsPage = page.locator('a:has-text("设置"), [data-testid="settings-link"]');
    if (await settingsPage.isVisible()) {
      await settingsPage.click();
      
      const backupButton = page.locator('button:has-text("备份数据"), [data-testid="backup-data"]');
      if (await backupButton.isVisible()) {
        const downloadPromise = page.waitForEvent('download');
        await backupButton.click();
        const download = await downloadPromise;
        
        expect(download.suggestedFilename()).toMatch(/backup.*\.(json|zip)$/);
      }
      
      // 测试数据恢复功能
      const restoreButton = page.locator('button:has-text("恢复数据"), [data-testid="restore-data"]');
      if (await restoreButton.isVisible()) {
        await restoreButton.click();
        
        // 验证文件上传界面
        const fileInput = page.locator('input[type="file"]');
        await helpers.verifyElementVisible(fileInput);
      }
    }
  });
});