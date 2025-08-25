import { Page, Locator } from '@playwright/test';
import { TestHelpers } from '../utils/test-helpers';

/**
 * 登录页面对象模型
 */
export class LoginPage {
  private helpers: TestHelpers;

  // 页面元素定位器
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly registerLink: Locator;
  readonly errorMessage: Locator;
  readonly forgotPasswordLink: Locator;

  constructor(private page: Page) {
    this.helpers = new TestHelpers(page);
    
    // 初始化元素定位器
    this.usernameInput = page.locator('input[name="username"], input[type="email"]');
    this.passwordInput = page.locator('input[name="password"], input[type="password"]');
    this.loginButton = page.locator('button[type="submit"], button:has-text("登录"), button:has-text("Login")');
    this.registerLink = page.locator('a:has-text("注册"), a:has-text("Register")');
    this.errorMessage = page.locator('.error-message, .alert-danger, [data-testid="error-message"]');
    this.forgotPasswordLink = page.locator('a:has-text("忘记密码"), a:has-text("Forgot Password")');
  }

  /**
   * 导航到登录页面
   */
  async goto() {
    await this.page.goto('/login');
    await this.helpers.waitForPageLoad();
  }

  /**
   * 执行登录操作
   */
  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    
    // 等待登录请求完成
    const responsePromise = this.helpers.waitForApiResponse('/api/v1/auth/login/');
    await this.loginButton.click();
    await responsePromise;
    
    await this.helpers.waitForPageLoad();
  }

  /**
   * 快速登录（使用默认测试用户）
   */
  async quickLogin() {
    await this.login('testuser', 'testpass123');
  }

  /**
   * 验证登录成功
   */
  async verifyLoginSuccess() {
    // 验证跳转到主页或仪表板
    await this.helpers.verifyUrl('/(dashboard|home|main)');
    
    // 验证用户菜单或头像可见
    await this.helpers.verifyElementVisible('.user-menu, .user-avatar, [data-testid="user-menu"]');
  }

  /**
   * 验证登录失败
   */
  async verifyLoginFailure(expectedErrorMessage?: string) {
    await this.helpers.verifyElementVisible(this.errorMessage.first());
    
    if (expectedErrorMessage) {
      await this.helpers.verifyElementText(this.errorMessage.first(), expectedErrorMessage);
    }
  }

  /**
   * 点击注册链接
   */
  async clickRegisterLink() {
    await this.registerLink.click();
    await this.helpers.waitForPageLoad();
  }

  /**
   * 点击忘记密码链接
   */
  async clickForgotPasswordLink() {
    await this.forgotPasswordLink.click();
    await this.helpers.waitForPageLoad();
  }

  /**
   * 验证页面元素是否正确显示
   */
  async verifyPageElements() {
    await this.helpers.verifyElementVisible(this.usernameInput);
    await this.helpers.verifyElementVisible(this.passwordInput);
    await this.helpers.verifyElementVisible(this.loginButton);
    await this.helpers.verifyElementVisible(this.registerLink);
  }

  /**
   * 清空表单
   */
  async clearForm() {
    await this.usernameInput.clear();
    await this.passwordInput.clear();
  }

  /**
   * 验证表单验证错误
   */
  async verifyFormValidation() {
    // 尝试提交空表单
    await this.loginButton.click();
    
    // 验证浏览器原生验证或自定义验证消息
    const usernameValidation = await this.usernameInput.getAttribute('validationMessage');
    const passwordValidation = await this.passwordInput.getAttribute('validationMessage');
    
    return {
      username: usernameValidation,
      password: passwordValidation
    };
  }
}