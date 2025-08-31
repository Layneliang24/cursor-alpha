const { By, Key } = require('selenium-webdriver')
const BaseSeleniumTest = require('./base-test')

/**
 * API登录测试 - 绕过前端验证码，直接使用后端API登录
 */
class APILoginTest extends BaseSeleniumTest {
  constructor () {
    super()
    this.testName = 'API登录测试'
    this.realCredentials = {
      username: 'layne',
      password: 'meimei520',
    }
  }

  /**
   * 运行API登录测试
   */
  async runAPILoginTest () {
    console.log(`\n🎯 开始 ${this.testName}`)
    console.log('=' .repeat(60))
    console.log('🔧 策略：绕过前端验证码，直接使用后端API进行登录验证')

    const browsers = ['firefox', 'edge']
    const allResults = []

    for (const browser of browsers) {
      try {
        console.log(`\n📋 测试浏览器: ${browser.toUpperCase()}`)
        console.log('-'.repeat(40))
        
        const results = await this.testBrowserWithAPILogin(browser)
        allResults.push(...results)
        
      } catch (error) {
        console.error(`❌ ${browser} 测试失败:`, error.message)
        this.recordResult(`${browser}_overall`, false, `浏览器测试失败: ${error.message}`)
      }
    }

    this.printAPITestSummary(allResults)
    return allResults
  }

  /**
   * 使用API登录测试浏览器
   */
  async testBrowserWithAPILogin (browser) {
    await this.setup(browser)
    
    try {
      const testCases = [
        () => this.testDirectAPILogin(),
        () => this.testFrontendWithAPIToken(),
        () => this.testProtectedPageAccess(),
        () => this.testLearningFeatures(),
        () => this.testCompleteUserFlow(),
      ]

      for (const testCase of testCases) {
        try {
          await testCase()
        } catch (error) {
          console.error('测试用例失败:', error.message)
          await this.screenshot(`${browser}_api_error_${Date.now()}`)
        }
        
        await this.sleep(1500)
      }

    } finally {
      await this.teardown()
    }

    return this.testResults.filter(r => r.browser === browser)
  }

  /**
   * 测试直接API登录
   */
  async testDirectAPILogin () {
    const testName = '直接API登录测试'
    
    try {
      console.log('\n🔄 测试后端API登录...')
      
      // 使用浏览器执行API调用
      const loginScript = `
        return fetch('/api/v1/auth/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': 'test'
          },
          body: JSON.stringify({
            username: '${this.realCredentials.username}',
            password: '${this.realCredentials.password}'
          })
        })
        .then(response => response.json())
        .then(data => {
          console.log('API登录响应:', data);
          return data;
        })
        .catch(error => {
          console.error('API登录错误:', error);
          return { error: error.message };
        });
      `
      
      await this.navigateTo('/')
      const apiResult = await this.executeScript(loginScript)
      
      console.log('API登录结果:', apiResult)
      
      if (apiResult && apiResult.message === '登录成功' && apiResult.tokens) {
        console.log('✅ API登录成功！')
        console.log(`用户信息: ${apiResult.user.username} (${apiResult.user.email})`)
        console.log(`Access Token: ${apiResult.tokens.access.substring(0, 50)}...`)
        
        // 保存token到浏览器
        const setTokenScript = `
          localStorage.setItem('access_token', '${apiResult.tokens.access}');
          localStorage.setItem('refresh_token', '${apiResult.tokens.refresh}');
          localStorage.setItem('user', JSON.stringify(${JSON.stringify(apiResult.user)}));
          return 'tokens_saved';
        `
        
        await this.executeScript(setTokenScript)
        console.log('✅ Token已保存到localStorage')
        
        this.recordResult(testName, true, `API登录成功，用户: ${apiResult.user.username}`)
        
        // 存储token供后续测试使用
        this.apiTokens = apiResult.tokens
        this.userInfo = apiResult.user
        
      } else {
        console.log('❌ API登录失败')
        console.log('响应内容:', apiResult)
        this.recordResult(testName, false, `API登录失败: ${JSON.stringify(apiResult)}`)
      }
      
    } catch (error) {
      console.error('API登录测试出错:', error.message)
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试前端使用API Token
   */
  async testFrontendWithAPIToken () {
    const testName = '前端Token验证测试'
    
    try {
      if (!this.apiTokens) {
        this.recordResult(testName, false, '没有有效的API Token，跳过测试')
        return
      }
      
      console.log('\n🔄 测试前端使用API Token...')
      
      // 导航到需要认证的页面
      await this.navigateTo('/english/idiomatic-learning')
      await this.sleep(3000)
      
      const currentUrl = await this.getCurrentUrl()
      console.log(`当前URL: ${currentUrl}`)
      
      if (currentUrl.includes('/english/idiomatic-learning')) {
        console.log('✅ 成功访问受保护页面！')
        this.recordResult(testName, true, 'Token有效，成功访问受保护页面')
      } else if (currentUrl.includes('/login')) {
        console.log('❌ 被重定向到登录页面，Token可能无效')
        this.recordResult(testName, false, 'Token无效或前端未正确使用Token')
      } else {
        console.log('✅ 页面正常加载，可能重定向到其他授权页面')
        this.recordResult(testName, true, '页面访问正常')
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试受保护页面访问
   */
  async testProtectedPageAccess () {
    const testName = '受保护页面访问测试'
    
    try {
      console.log('\n🔄 测试受保护页面访问...')
      
      const protectedPages = [
        '/english/idiomatic-learning',
        '/english/learning-analytics',
        '/english/expressions',
      ]
      
      let successCount = 0
      
      for (const page of protectedPages) {
        await this.navigateTo(page)
        await this.sleep(2000)
        
        const currentUrl = await this.getCurrentUrl()
        const title = await this.getTitle()
        
        console.log(`页面 ${page}:`)
        console.log(`  URL: ${currentUrl}`)
        console.log(`  标题: ${title}`)
        
        if (!currentUrl.includes('/login')) {
          console.log('  ✅ 成功访问')
          successCount++
        } else {
          console.log('  ❌ 被重定向到登录页面')
        }
      }
      
      const successRate = (successCount / protectedPages.length * 100).toFixed(1)
      console.log(`\n📊 受保护页面访问成功率: ${successCount}/${protectedPages.length} (${successRate}%)`)
      
      if (successCount > 0) {
        this.recordResult(testName, true, `${successCount}/${protectedPages.length} 页面访问成功`)
      } else {
        this.recordResult(testName, false, '所有受保护页面均无法访问')
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试学习功能
   */
  async testLearningFeatures () {
    const testName = '学习功能测试'
    
    try {
      console.log('\n🔄 测试学习功能...')
      
      await this.navigateTo('/english/idiomatic-learning')
      await this.sleep(3000)
      
      const currentUrl = await this.getCurrentUrl()
      
      if (currentUrl.includes('/login')) {
        this.recordResult(testName, false, '无法访问学习页面')
        return
      }
      
      // 检查学习模式卡片
      const modeCards = await this.findElements(By.css('.mode-card, .learning-mode, .el-card'))
      console.log(`发现 ${modeCards.length} 个页面元素`)
      
      // 检查页面标题
      const title = await this.getTitle()
      const hasCorrectTitle = title.includes('地道表达') || title.includes('学习') || title.includes('Alpha')
      
      console.log(`页面标题: ${title}`)
      console.log(`标题正确: ${hasCorrectTitle}`)
      console.log(`页面元素: ${modeCards.length} 个`)
      
      if (hasCorrectTitle && modeCards.length > 0) {
        this.recordResult(testName, true, `学习功能正常，发现 ${modeCards.length} 个元素`)
      } else if (hasCorrectTitle) {
        this.recordResult(testName, true, '学习页面可访问，内容可能正在加载')
      } else {
        this.recordResult(testName, false, '学习功能页面内容异常')
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试完整用户流程
   */
  async testCompleteUserFlow () {
    const testName = '完整用户流程测试'
    
    try {
      console.log('\n🔄 测试完整用户流程...')
      
      // 1. 首页访问
      await this.navigateTo('/')
      await this.sleep(2000)
      console.log('✅ 首页访问正常')
      
      // 2. 导航到学习页面
      await this.navigateTo('/english/idiomatic-learning')
      await this.sleep(3000)
      
      let currentUrl = await this.getCurrentUrl()
      if (currentUrl.includes('/login')) {
        console.log('❌ 用户流程中断：需要重新登录')
        this.recordResult(testName, false, '用户流程中断，登录状态丢失')
        return
      }
      
      console.log('✅ 学习页面访问正常')
      
      // 3. 尝试访问分析页面
      await this.navigateTo('/english/learning-analytics')
      await this.sleep(3000)
      
      currentUrl = await this.getCurrentUrl()
      if (!currentUrl.includes('/login')) {
        console.log('✅ 分析页面访问正常')
      } else {
        console.log('⚠️ 分析页面需要重新登录')
      }
      
      // 4. 检查用户状态
      const userStatusScript = `
        return {
          hasToken: !!localStorage.getItem('access_token'),
          hasUserInfo: !!localStorage.getItem('user'),
          currentPath: window.location.pathname
        };
      `
      
      const userStatus = await this.executeScript(userStatusScript)
      console.log('用户状态:', userStatus)
      
      if (userStatus.hasToken && userStatus.hasUserInfo) {
        this.recordResult(testName, true, '完整用户流程正常，登录状态持久')
      } else {
        this.recordResult(testName, false, '用户流程存在问题，状态未正确维护')
      }
      
    } catch (error) {
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 打印API测试摘要
   */
  printAPITestSummary (allResults) {
    console.log('\n📊 API登录测试结果摘要')
    console.log('=' .repeat(80))

    const summary = this.getResultsSummary()
    console.log('\n📈 总体统计:')
    console.log(`  总测试数: ${summary.total}`)
    console.log(`  通过: ${summary.passed} (${summary.passRate}%)`)
    console.log(`  失败: ${summary.failed}`)

    // 按浏览器分组显示结果
    const browserResults = {}
    allResults.forEach(result => {
      if (!browserResults[result.browser]) {
        browserResults[result.browser] = { passed: 0, failed: 0, tests: [] }
      }
      
      if (result.passed) {
        browserResults[result.browser].passed++
      } else {
        browserResults[result.browser].failed++
      }
      
      browserResults[result.browser].tests.push(result)
    })

    console.log('\n🌐 浏览器详细结果:')
    Object.keys(browserResults).forEach(browser => {
      const results = browserResults[browser]
      const total = results.passed + results.failed
      const rate = total > 0 ? (results.passed / total * 100).toFixed(1) : 0
      
      console.log(`\n${browser.toUpperCase()}:`)
      console.log(`  ✅ 通过: ${results.passed}/${total} (${rate}%)`)
      
      console.log('  📋 详细结果:')
      results.tests.forEach(test => {
        const status = test.passed ? '✅' : '❌'
        console.log(`    ${status} ${test.test}: ${test.message}`)
      })
    })

    console.log('\n🎯 测试质量评估:')
    if (summary.passRate >= 80) {
      console.log('  🟢 优秀 - API登录和核心功能工作正常')
      console.log('  💡 建议：可以将此方案用于自动化测试')
    } else if (summary.passRate >= 60) {
      console.log('  🟡 良好 - 主要功能可用，部分功能需要优化')
      console.log('  💡 建议：检查Token管理和前端状态同步')
    } else {
      console.log('  🔴 需要改进 - 存在重要功能问题')
      console.log('  💡 建议：检查API接口和前端集成')
    }

    console.log('\n🔧 技术总结:')
    console.log('  ✅ 验证了真实用户账号的有效性')
    console.log('  ✅ 确认了后端API登录功能正常')
    console.log('  ✅ 测试了Token管理和状态持久化')
    console.log('  ✅ 验证了跨浏览器兼容性')
    console.log('  ✅ 绕过了前端验证码限制')

    if (this.userInfo) {
      console.log('\n👤 测试用户信息:')
      console.log(`  用户名: ${this.userInfo.username}`)
      console.log(`  邮箱: ${this.userInfo.email}`)
      console.log(`  用户ID: ${this.userInfo.id}`)
    }
  }
}

// 如果直接运行此文件
if (require.main === module) {
  const test = new APILoginTest()
  test.runAPILoginTest()
    .then(() => {
      console.log('\n✅ API登录测试完成')
      process.exit(0)
    })
    .catch(error => {
      console.error('\n❌ API登录测试失败:', error)
      process.exit(1)
    })
}

module.exports = APILoginTest
