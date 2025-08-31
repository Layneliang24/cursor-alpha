/**
 * 简化的E2E测试认证设置
 * 专门为Playwright测试设计，避免验证码问题
 */

import { test as setup, expect } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

/**
 * 设置测试用户认证 - 简化版本
 */
setup('authenticate', async ({ page }) => {
  console.log('🚀 开始认证设置...');
  
  try {
    // 直接导航到主页
    await page.goto('/');
    
    // 执行登录API调用
    const loginResult = await page.evaluate(async () => {
      try {
        const response = await fetch('/api/v1/auth/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: 'test_learner',
            password: 'testpass123'
          })
        });
        
        if (!response.ok) {
          return { 
            success: false, 
            error: `HTTP ${response.status}: ${response.statusText}`,
            response: await response.text()
          };
        }
        
        const data = await response.json();
        
        if (data.tokens && data.user) {
          // 保存认证信息到localStorage
          localStorage.setItem('access_token', data.tokens.access);
          localStorage.setItem('refresh_token', data.tokens.refresh);
          localStorage.setItem('user', JSON.stringify(data.user));
          
          return { success: true, user: data.user };
        } else {
          return { success: false, error: 'Missing tokens or user data', data };
        }
      } catch (error: any) {
        return { success: false, error: error.message };
      }
    });
    
    if (loginResult.success) {
      console.log('✅ API登录成功，用户:', loginResult.user.username);
      
      // 验证登录状态 - 访问受保护页面
      await page.goto('/english/idiomatic-learning');
      await page.waitForTimeout(2000);
      
      const currentUrl = page.url();
      if (currentUrl.includes('/login')) {
        throw new Error('认证验证失败：仍被重定向到登录页面');
      }
      
      console.log('✅ 认证状态验证成功');
      
      // 保存认证状态到文件
      await page.context().storageState({ path: authFile });
      console.log('✅ 认证状态已保存到:', authFile);
      
    } else {
      console.error('❌ 登录失败:', loginResult.error);
      console.error('响应数据:', loginResult.response || loginResult.data);
      throw new Error(`登录失败: ${loginResult.error}`);
    }
    
  } catch (error: any) {
    console.error('❌ 认证设置失败:', error.message);
    
    // 创建一个空的认证状态文件作为后备
    console.log('⚠️ 创建空认证状态文件作为后备');
    await page.context().storageState({ path: authFile });
    
    // 重新抛出错误，让测试失败而不是静默通过
    throw error;
  }
});
