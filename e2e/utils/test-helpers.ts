import { Page, expect } from '@playwright/test';

/**
 * 测试辅助工具类
 */
export class TestHelpers {
  constructor(private page: Page) {}

  /**
   * 等待页面加载完成
   */
  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * 截图用于调试
   */
  async takeScreenshot(name: string) {
    await this.page.screenshot({ path: `test-results/screenshots/${name}.png` });
  }

  /**
   * 等待元素可见
   */
  async waitForElement(selector: string, timeout = 5000) {
    await this.page.waitForSelector(selector, { state: 'visible', timeout });
  }

  /**
   * 填写表单字段
   */
  async fillForm(fields: Record<string, string>) {
    for (const [selector, value] of Object.entries(fields)) {
      await this.page.fill(selector, value);
    }
  }

  /**
   * 验证页面标题
   */
  async verifyTitle(expectedTitle: string) {
    await expect(this.page).toHaveTitle(expectedTitle);
  }

  /**
   * 验证URL包含指定路径
   */
  async verifyUrl(expectedPath: string) {
    await expect(this.page).toHaveURL(new RegExp(expectedPath));
  }

  /**
   * 验证元素文本内容
   */
  async verifyElementText(selector: string, expectedText: string) {
    await expect(this.page.locator(selector)).toContainText(expectedText);
  }

  /**
   * 验证元素是否可见
   */
  async verifyElementVisible(selector: string) {
    await expect(this.page.locator(selector)).toBeVisible();
  }

  /**
   * 验证元素是否隐藏
   */
  async verifyElementHidden(selector: string) {
    await expect(this.page.locator(selector)).toBeHidden();
  }

  /**
   * 点击并等待导航
   */
  async clickAndWaitForNavigation(selector: string) {
    await Promise.all([
      this.page.waitForNavigation(),
      this.page.click(selector)
    ]);
  }

  /**
   * 模拟API响应
   */
  async mockApiResponse(url: string, response: any) {
    await this.page.route(url, route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(response)
      });
    });
  }

  /**
   * 等待API请求完成
   */
  async waitForApiRequest(url: string) {
    return this.page.waitForRequest(request => request.url().includes(url));
  }

  /**
   * 等待API响应
   */
  async waitForApiResponse(url: string) {
    return this.page.waitForResponse(response => response.url().includes(url));
  }
}

/**
 * 测试数据生成器
 */
export class TestDataGenerator {
  /**
   * 生成随机用户数据
   */
  static generateUserData() {
    const timestamp = Date.now();
    return {
      username: `testuser_${timestamp}`,
      email: `test_${timestamp}@example.com`,
      password: 'TestPassword123!',
      firstName: 'Test',
      lastName: 'User'
    };
  }

  /**
   * 生成随机字符串
   */
  static generateRandomString(length = 8) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  /**
   * 生成测试词典数据
   */
  static generateDictionaryData() {
    return {
      name: `Test Dictionary ${this.generateRandomString(6)}`,
      description: 'A test dictionary for E2E testing',
      language: 'en',
      words: [
        { word: 'test', translation: '测试', pronunciation: '/test/' },
        { word: 'example', translation: '例子', pronunciation: '/ɪɡˈzæmpəl/' },
        { word: 'practice', translation: '练习', pronunciation: '/ˈpræktɪs/' }
      ]
    };
  }
}