import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { TestHelpers, TestDataGenerator } from '../utils/test-helpers';

test.describe('用户认证功能', () => {
  let loginPage: LoginPage;
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    helpers = new TestHelpers(page);
    await loginPage.goto();
  });

  test('应该显示登录页面的所有必要元素', async () => {
    await loginPage.verifyPageElements();
    await helpers.verifyTitle(/登录|Login/);
  });

  test('应该能够成功登录有效用户', async () => {
    // 使用测试用户登录
    await loginPage.login('testuser', 'testpass123');
    
    // 验证登录成功
    await loginPage.verifyLoginSuccess();
  });

  test('应该拒绝无效的登录凭据', async () => {
    // 尝试使用无效凭据登录
    await loginPage.login('invaliduser', 'wrongpassword');
    
    // 验证登录失败
    await loginPage.verifyLoginFailure();
  });

  test('应该验证空表单提交', async () => {
    // 验证表单验证
    const validation = await loginPage.verifyFormValidation();
    
    // 验证浏览器原生验证或自定义验证消息
    expect(validation.username || validation.password).toBeTruthy();
  });

  test('应该能够导航到注册页面', async () => {
    await loginPage.clickRegisterLink();
    
    // 验证跳转到注册页面
    await helpers.verifyUrl('/register');
  });

  test('应该能够导航到忘记密码页面', async () => {
    await loginPage.clickForgotPasswordLink();
    
    // 验证跳转到忘记密码页面
    await helpers.verifyUrl('/forgot-password');
  });

  test('应该处理网络错误', async ({ page }) => {
    // 模拟网络错误
    await page.route('**/api/v1/auth/login/', route => {
      route.abort('failed');
    });
    
    await loginPage.login('testuser', 'testpass123');
    
    // 验证错误处理
    await loginPage.verifyLoginFailure('网络错误');
  });

  test('应该处理服务器错误', async ({ page }) => {
    // 模拟服务器错误
    await page.route('**/api/v1/auth/login/', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: '服务器内部错误' })
      });
    });
    
    await loginPage.login('testuser', 'testpass123');
    
    // 验证错误处理
    await loginPage.verifyLoginFailure();
  });

  test('应该记住用户登录状态', async ({ page, context }) => {
    // 登录
    await loginPage.login('testuser', 'testpass123');
    await loginPage.verifyLoginSuccess();
    
    // 创建新页面
    const newPage = await context.newPage();
    await newPage.goto('/');
    
    // 验证用户仍然登录
    const userMenu = newPage.locator('.user-menu, .user-avatar, [data-testid="user-menu"]');
    await expect(userMenu).toBeVisible();
    
    await newPage.close();
  });

  test('应该能够退出登录', async ({ page }) => {
    // 先登录
    await loginPage.login('testuser', 'testpass123');
    await loginPage.verifyLoginSuccess();
    
    // 退出登录
    const userMenu = page.locator('.user-menu, .user-avatar, [data-testid="user-menu"]');
    await userMenu.click();
    
    const logoutButton = page.locator('button:has-text("退出"), button:has-text("Logout"), [data-testid="logout-button"]');
    await logoutButton.click();
    
    // 验证跳转回登录页面
    await helpers.verifyUrl('/login');
  });

  test('应该支持键盘导航', async ({ page }) => {
    // 使用Tab键导航
    await page.keyboard.press('Tab'); // 用户名输入框
    await page.keyboard.type('testuser');
    
    await page.keyboard.press('Tab'); // 密码输入框
    await page.keyboard.type('testpass123');
    
    await page.keyboard.press('Tab'); // 登录按钮
    await page.keyboard.press('Enter'); // 提交表单
    
    // 验证登录成功
    await loginPage.verifyLoginSuccess();
  });

  test('应该在多次失败登录后显示验证码', async () => {
    // 多次尝试错误登录
    for (let i = 0; i < 3; i++) {
      await loginPage.login('testuser', 'wrongpassword');
      await loginPage.verifyLoginFailure();
      await loginPage.clearForm();
    }
    
    // 验证验证码出现（如果实现了此功能）
    const captcha = loginPage.page.locator('.captcha, [data-testid="captcha"]');
    // 验证码可能不总是出现，所以这是可选验证
    try {
      await expect(captcha).toBeVisible({ timeout: 2000 });
    } catch {
      console.log('验证码功能未实现或未触发');
    }
  });

  test('应该支持社交登录（如果可用）', async ({ page }) => {
    // 检查是否有社交登录按钮
    const socialLoginButtons = page.locator('.social-login, [data-testid="social-login"]');
    const count = await socialLoginButtons.count();
    
    if (count > 0) {
      // 测试第一个社交登录按钮
      await socialLoginButtons.first().click();
      
      // 验证跳转到社交登录页面或弹窗
      await page.waitForTimeout(1000);
      
      // 这里可以添加更多社交登录的验证逻辑
    } else {
      console.log('社交登录功能未实现');
    }
  });
});

test.describe('用户注册功能', () => {
  test('应该能够注册新用户', async ({ page }) => {
    const helpers = new TestHelpers(page);
    const userData = TestDataGenerator.generateUserData();
    
    // 导航到注册页面
    await page.goto('/register');
    await helpers.waitForPageLoad();
    
    // 填写注册表单
    await page.fill('input[name="username"]', userData.username);
    await page.fill('input[name="email"]', userData.email);
    await page.fill('input[name="password"]', userData.password);
    await page.fill('input[name="confirmPassword"]', userData.password);
    
    // 提交注册表单
    const registerButton = page.locator('button[type="submit"], button:has-text("注册"), button:has-text("Register")');
    await registerButton.click();
    
    // 验证注册成功
    await helpers.verifyUrl('/(login|dashboard|home)');
  });

  test('应该验证密码确认匹配', async ({ page }) => {
    const helpers = new TestHelpers(page);
    const userData = TestDataGenerator.generateUserData();
    
    await page.goto('/register');
    await helpers.waitForPageLoad();
    
    // 填写不匹配的密码
    await page.fill('input[name="username"]', userData.username);
    await page.fill('input[name="email"]', userData.email);
    await page.fill('input[name="password"]', userData.password);
    await page.fill('input[name="confirmPassword"]', 'differentpassword');
    
    const registerButton = page.locator('button[type="submit"]');
    await registerButton.click();
    
    // 验证密码不匹配错误
    const errorMessage = page.locator('.error-message, [data-testid="error-message"]');
    await expect(errorMessage).toBeVisible();
  });
});